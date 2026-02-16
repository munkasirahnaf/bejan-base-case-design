import os
import re
from pathlib import Path
import csv
import pandas as pd
import numpy as np
import pytest
import logging
from IPython.core.display import SVG

import pyomo.environ as pyo
from pyomo.network import Arc, SequentialDecomposition
from pyomo.common.fileutils import this_file_dir

import idaes
import idaes.logger as idaeslog
import idaes.models.unit_models as um
import idaes.core.util as iutil
import idaes.core.util.scaling as iscale
import idaes.core.util.tables as tables
import idaes.core.util.initialization as iinit

from idaes.core import FlowsheetBlockData, UnitModelBlockData, declare_process_block_class
from idaes.core.solvers import get_solver
from idaes.core.solvers import use_idaes_solver_configuration_defaults
from idaes.core.util.initialization import propagate_state
from idaes.core.util.tags import svg_tag
from idaes.models.properties import iapws95
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock,
)
from idaes.models.properties.modular_properties.base.generic_reaction import (
    GenericReactionParameterBlock,
)

from idaes.models.unit_models import Mixer
from idaes.models.unit_models.heat_exchanger import (
    HeatExchanger,
    HeatExchangerFlowPattern,
    delta_temperature_lmtd_callback,
)
import idaes.models_extra.power_generation.unit_models.helm as helm
from idaes.models_extra.power_generation.properties.natural_gas_PR import (
    get_prop,
    get_rxn,
)
from idaes.models.unit_models.pressure_changer import ThermodynamicAssumption
from idaes.models_extra.power_generation.properties import FlueGasParameterBlock
from idaes.core.util.model_statistics import degrees_of_freedom

## Gas Turbine - Functional Approach ##

def add_properties(
    fs,
    air_species={"CO2", "H2O", "O2", "N2"},
    cmb_species={"CH4", "O2", "H2O", "CO2", "N2"},
    flue_species={"O2", "H2O", "CO2", "N2"},
    rxns={"ch4_cmb": "CH4"},
):
    """Add property parameter blocks to flowsheet"""
    fs.air_species = air_species
    fs.cmb_species = cmb_species
    fs.flue_species = flue_species
    fs.rxns = rxns
    fs.prop_water = iapws95.Iapws95ParameterBlock()
    fs.air_prop_params = GenericParameterBlock(
        **get_prop(air_species, ["Vap"]),
        doc="Air property parameters",
    )
    fs.cmb_prop_params = GenericParameterBlock(
        **get_prop(cmb_species, ["Vap"]),
        doc="Natural gas or Natural gas + Air property parameters",
    )
    fs.flue_prop_params = GenericParameterBlock(
        **get_prop(flue_species, ["Vap"]),
        doc="Flue gas property parameters",
    )
    # Combustion reaction package
    fs.gas_combustion = GenericReactionParameterBlock(
        **get_rxn(fs.cmb_prop_params, fs.rxns),
        doc="Reaction parameters package",
    )


def add_models(fs):
    """Add unit models to flowsheet"""
    fs.feed_air1 = um.Feed(
        doc="Air feed block",
        property_package=fs.air_prop_params,
    )
    fs.feed_fuel1 = um.Feed(
        doc="Fuel feed block",
        property_package=fs.cmb_prop_params,
    )
    fs.feed_water1 = um.Feed(
        doc="Feedwater block",
        property_package=fs.prop_water,
    )
    fs.cmp1 = um.Compressor(
        doc="Gas turbine air compression section",
        property_package=fs.air_prop_params,
        support_isentropic_performance_curves=False,
    )
    fs.aph_shell = um.Heater(
        doc="Air preheater shell section",
        dynamic=False,
        property_package=fs.flue_prop_params,
        has_pressure_change=True,
    )
    fs.aph_tube = um.Heater(
        doc="Air preheater tube section",
        dynamic=False,
        property_package=fs.air_prop_params,
        has_pressure_change=True,
    )
    fs.inject_translator = um.Translator(
        doc="Translator for air to combustion mixture properties",
        inlet_property_package=fs.air_prop_params,
        outlet_property_package=fs.cmb_prop_params,
        outlet_state_defined=False,
    )
    fs.inject1 = um.Mixer(
        doc="Fuel injection mixer (mix air and natural gas)",
        property_package=fs.cmb_prop_params,
        inlet_list=["gas", "air"],
        momentum_mixing_type=um.MomentumMixingType.none,
    )
    fs.cmb1 = um.StoichiometricReactor(
        doc="Combustor",
        property_package=fs.cmb_prop_params,
        reaction_package=fs.gas_combustion,
        has_pressure_change=True,
    )
    fs.flue_translator = um.Translator(
        doc="Translate combustion mixture properties to flue gas",
        inlet_property_package=fs.cmb_prop_params,
        outlet_property_package=fs.flue_prop_params,
        outlet_state_defined=False,
    )
    fs.gts1 = um.Turbine(
        doc="Gas turbine stage 1",
        property_package=fs.flue_prop_params,
        support_isentropic_performance_curves=False,
    )
    fs.evap = um.HeatExchanger(
        doc="HRSG Evaporator heat exchanger section",
        hot_side_name="shell",
        cold_side_name="tube",
        shell={"property_package": fs.flue_prop_params,
              "has_pressure_change": True,},
        tube={"property_package": fs.prop_water},
        delta_temperature_callback=delta_temperature_lmtd_callback,
        flow_pattern=HeatExchangerFlowPattern.countercurrent,
        has_holdup=False,
    )
    fs.exhaust1 = um.Product(
        doc="Air feed block",
        property_package=fs.flue_prop_params,
    )


def add_constraints(fs):
    """Add constraints to flowsheet"""
    # Complete combustion, use key components and 100% conversion (Make it 98%)
    @fs.cmb1.Constraint(fs.time, fs.rxns.keys())
    def reaction_extent(b, t, r):
        key = fs.rxns[r]
        prp = b.control_volume.properties_in[t]
        stc = fs.gas_combustion.rate_reaction_stoichiometry[r, "Vap", key]
        extent = b.rate_reaction_extent[t, r]
        return extent == - prp.flow_mol * prp.mole_frac_comp[key] / stc

    # Pressure in the air-fuel mixer
    @fs.inject1.Constraint(fs.time)
    def mxpress_eqn(b, t):
        return b.mixed_state[t].pressure == b.air_state[t].pressure

    # The pressure drop in the combustor is 5%
    @fs.cmb1.Constraint(fs.time)
    def pressure_drop_eqn(b, t):
        return (
            0.95
            == b.control_volume.properties_out[t].pressure
            / b.control_volume.properties_in[t].pressure
        )

    # Pressure drop in the tube section of APH is 5%
    @fs.aph_tube.Constraint(fs.time)
    def pressure_drop_eqn(b, t):
        return (
            0.95
            == b.control_volume.properties_out[t].pressure
            / b.control_volume.properties_in[t].pressure
        )

    # Pressure drop in the shell section of APH is 3%
    @fs.aph_shell.Constraint(fs.time)
    def pressure_drop_eqn(b, t):
        return (
            0.97
            == b.control_volume.properties_out[t].pressure
            / b.control_volume.properties_in[t].pressure
        )

    # Pressure drop in the shell section of HRSG evaporator is 5%
    @fs.evap.shell.Constraint(fs.time)
    def pressure_drop_eqn(b, t):
        return (
            0.95
            == b.properties_out[t].pressure
            / b.properties_in[t].pressure
        )

    # Power
    @fs.Expression(fs.time)
    def gt_power_expr(b, t):
        return (
            fs.cmp1.control_volume.work[t]
            + fs.gts1.control_volume.work[t]
        )
    fs.gt_power = pyo.Var(fs.time, units=pyo.units.W)
    @fs.Constraint(fs.time)
    def gt_power_eqn(b, t):
        return b.gt_power[t] == b.gt_power_expr[t]

    # Evaporation
    @fs.evap.Constraint(
        fs.config.time, doc="Everything evaporates in evaporator"
    )
    def sat_vap_eqn(b, t):
        return (
            b.tube.properties_out[t].enth_mol / 1e4
            == (b.tube.properties_out[t].enth_mol_sat_phase["Vap"]) / 1e4
        )

    # Rules for translator blocks (Do not change anything here)
    def rule_flow_mol_comp(blk, t, j):
        return (
            blk.properties_in[t].flow_mol_comp[j]
            == blk.properties_out[t].flow_mol_comp[j]
        )
    def rule_temperature(blk, t):
        return blk.properties_in[t].temperature == blk.properties_out[t].temperature
    def rule_pressure(blk, t):
        return blk.properties_in[t].pressure == blk.properties_out[t].pressure
    def rule_zero_flow(blk, t, j):
        return blk.properties_out[t].flow_mol_comp[j] == 0

    translators = {
        fs.inject_translator,
        fs.flue_translator,
    }
    for blk in translators:
        blk.temperature_eqn = pyo.Constraint(fs.time, rule=rule_temperature)
        blk.pressure_eqn = pyo.Constraint(fs.time, rule=rule_pressure)
        for t in fs.config.time:
            iscale.constraint_scaling_transform(blk.temperature_eqn[t], 1e-2)
            iscale.constraint_scaling_transform(blk.pressure_eqn[t], 1e-6)

    fs.inject_translator.flow_mole_comp_eqn = pyo.Constraint(
        fs.time, fs.air_species, rule=rule_flow_mol_comp
    )
    for i, c in fs.inject_translator.flow_mole_comp_eqn.items():
        iscale.constraint_scaling_transform(c, 1e-3)

    fs.inject_translator.zero_flow_eqn = pyo.Constraint(
        fs.time, fs.cmb_species - fs.air_species, rule=rule_zero_flow
    )

    fs.flue_translator.flow_mole_comp_eqn = pyo.Constraint(
        fs.time, fs.flue_species, rule=rule_flow_mol_comp
    )
    for i, c in fs.flue_translator.flow_mole_comp_eqn.items():
        iscale.constraint_scaling_transform(c, 1e-3)


def add_arcs(fs):
    """Add arcs (connections) between unit models"""
    fs.fuel01 = Arc(
        source=fs.feed_fuel1.outlet,
        destination=fs.inject1.gas,
    )
    fs.air01 = Arc(
        source=fs.feed_air1.outlet,
        destination=fs.cmp1.inlet,
    )
    fs.air02 = Arc(
        source=fs.cmp1.outlet,
        destination=fs.aph_tube.inlet,
    )
    fs.air03a = Arc(
        source=fs.aph_tube.outlet,
        destination=fs.inject_translator.inlet,
    )
    fs.air03b = Arc(
        source=fs.inject_translator.outlet,
        destination=fs.inject1.air,
    )
    fs.g01 = Arc(source=fs.inject1.outlet, destination=fs.cmb1.inlet)
    fs.g02a = Arc(source=fs.cmb1.outlet, destination=fs.flue_translator.inlet)
    fs.g02b = Arc(source=fs.flue_translator.outlet, destination=fs.gts1.inlet)
    fs.g03 = Arc(source=fs.gts1.outlet, destination=fs.aph_shell.inlet)
    fs.g04 = Arc(source=fs.aph_shell.outlet, destination=fs.evap.shell_inlet)
    fs.g05 = Arc(source=fs.evap.shell_outlet, destination=fs.exhaust1.inlet)
    fs.liq01 = Arc(
        doc="Feedwater outlet to evaporator inlet",
        source=fs.feed_water1.outlet,
        destination=fs.evap.tube_inlet,
    )

    pyo.TransformationFactory("network.expand_arcs").apply_to(fs)


def set_initial_inputs(fs):
    """Set initial inputs and boundary conditions"""
    # Feed air (Component: feed_air1)
    air_comp = {
        "CH4": 0.0,
        "O2": 0.2059,
        "H2O": 0.0190,
        "CO2": 0.0003,
        "N2": 0.7748,
    }
    fs.feed_air1.temperature.fix(298.15)
    fs.feed_air1.pressure.fix(101300)
    for i, v in air_comp.items():
        fs.feed_air1.mole_frac_comp[:, i].fix(v)
    fs.feed_air1.flow_mol[:] = 3200

    # Feed fuel (Component: feed_fuel1)
    ng_comp = {
        "CH4": 1.0,
        "O2": 0.0,
        "H2O": 0.0,
        "CO2": 0.0,
        "N2": 0.0,
    }
    fs.feed_fuel1.temperature.fix(298.15)
    fs.feed_fuel1.pressure.fix(1.2e6)
    fs.feed_fuel1.flow_mol.fix(100)
    for i, v in ng_comp.items():
        fs.feed_fuel1.mole_frac_comp[:, i].fix(v)

    # Feedwater
    fs.feed_water1.outlet.flow_mol[0].fix(777.118091)
    fs.feed_water1.outlet.pressure[0].fix(2e6)
    fs.feed_water1.outlet.enth_mol[0].fix(
        iapws95.htpx(T=298.15 * pyo.units.K, P=2e6 * pyo.units.Pa)
    )

    # Compressor (Component: cmp1)
    fs.cmp1.efficiency_isentropic.fix(0.86)
    fs.cmp1.ratioP.fix(10)

    # Turbine
    fs.gts1.ratioP.fix(0.2)
    fs.gts1.efficiency_isentropic.fix(0.86)
    fs.evap.area.fix(15000)


def add_tags(fs):
    """Add tags for stream table generation"""
    tag_stm = iutil.ModelTagGroup()
    tag_gas = iutil.ModelTagGroup()
    fs.tags_steam_streams = tag_stm
    fs.tags_flue_gas_streams = tag_gas
    stream_states = tables.stream_states_dict(
        tables.arcs_to_stream_dict(
            fs,
            descend_into=False,
            additional={  # these are streams in or out without an arc
                "g05": fs.evap.shell_outlet,
                "liq02": fs.evap.tube_outlet,
            },
        )
    )
    for i, s in stream_states.items():
        if isinstance(s, iapws95.Iapws95StateBlockData):
            tag_group = tag_stm
            is_steam = True
        else:
            tag_group = tag_gas
            is_steam = False
        tag_group[f"{i}_F"] = iutil.ModelTag(
            doc=f"{i}: mass flow",
            expr=s.flow_mass,
            format_string="{:.3f}",
            display_units=pyo.units.kg / pyo.units.s,
        )
        tag_group[f"{i}_Fmol"] = iutil.ModelTag(
            doc=f"{i}: mole flow",
            expr=s.flow_mol,
            format_string="{:.3f}",
            display_units=pyo.units.kmol / pyo.units.s,
        )
        tag_group[f"{i}_Fvol"] = iutil.ModelTag(
            doc=f"{i}: volumetric flow",
            expr=s.flow_vol,
            format_string="{:.3f}",
            display_units=pyo.units.m**3 / pyo.units.s,
        )
        tag_group[f"{i}_P"] = iutil.ModelTag(
            doc=f"{i}: pressure",
            expr=s.pressure,
            format_string="{:.3f}",
            display_units=pyo.units.bar,
        )
        tag_group[f"{i}_T"] = iutil.ModelTag(
            doc=f"{i}: temperature",
            expr=s.temperature,
            format_string="{:.2f}",
            display_units=pyo.units.K,
        )
        if is_steam:
            tag_group[f"{i}_X"] = iutil.ModelTag(
                doc=f"{i}: vapor fraction",
                expr=s.phase_frac["Vap"],
                format_string="{:.3f}",
                display_units=None,
            )
            tag_group[f"{i}_H"] = iutil.ModelTag(
                doc=f"{i}: molar enthalpy",
                expr=s.enth_mol,
                format_string="{:.3f}",
                display_units=pyo.units.kJ / pyo.units.mol,
            )
        else:
            for c in s.mole_frac_comp:
                tag_group[f"{i}_y{c}"] = iutil.ModelTag(
                    doc=f"{i}: mole percent {c}",
                    expr=s.mole_frac_comp[c] * 100,
                    format_string="{:.3f}",
                    display_units="%",
                )
    tag_group = iutil.ModelTagGroup()
    tag_group["cmp1_eff_isen"] = iutil.ModelTag(
        doc=f"Compressor isentropic efficiency.",
        expr=100 * fs.cmp1.efficiency_isentropic[0],
        format_string="{:.2f}",
        display_units="%",
    )
    tag_group["gts1_eff_isen"] = iutil.ModelTag(
        doc=f"Gas turbine stage 1 isentropic efficiency.",
        expr=100 * fs.gts1.efficiency_isentropic[0],
        format_string="{:.2f}",
        display_units="%",
    )
    tag_group["cmp1_power"] = iutil.ModelTag(
        doc=f"Compressor power",
        expr=fs.cmp1.control_volume.work[0],
        format_string="{:.2f}",
        display_units=pyo.units.MW,
    )
    tag_group["gts1_power"] = iutil.ModelTag(
        doc=f"GT stage 1 power",
        expr=fs.gts1.control_volume.work[0],
        format_string="{:.2f}",
        display_units=pyo.units.MW,
    )
    tag_group["gt_total_power"] = iutil.ModelTag(
        doc=f"Total gas turbine power output",
        expr=-fs.gt_power[0],
        format_string="{:.2f}",
        display_units=pyo.units.MW,
    )
    tag_group["combustor_temperature"] = iutil.ModelTag(
        doc=f"Combustor Temperature",
        expr=fs.cmb1.control_volume.properties_out[0].temperature,
        format_string="{:.2f}",
        display_units=pyo.units.K,
    )
    tag_group["fuel_flow"] = iutil.ModelTag(
        doc=f"Fuel mass flow",
        expr=fs.feed_fuel1.properties[0].flow_mass,
        format_string="{:.3f}",
        display_units=pyo.units.kg / pyo.units.s,
    )


def set_scaling(fs):
    """Set scaling factors for variables and constraints"""
    prop_packages = {
        fs.air_prop_params,
        fs.cmb_prop_params,
        fs.flue_prop_params,
    }
    _mf_scale = {
        "Ar": 100,
        "O2": 100,
        "H2S": 1000,
        "SO2": 1000,
        "H2": 1000,
        "CO": 1000,
        "C2H4": 1000,
        "C2H6": 1000,
        "C3H8": 1000,
        "C4H10": 1000,
        "CO2": 1000,
    }
    for pp in prop_packages:
        pp.set_default_scaling("mole_frac_comp", 10)
        pp.set_default_scaling("mole_frac_phase_comp", 10)
        for c, s in _mf_scale.items():
            if c in pp.component_list:
                pp.set_default_scaling("mole_frac_comp", s, index=c)
                pp.set_default_scaling("mole_frac_phase_comp", s, index=("Vap", c))
        pp.set_default_scaling("enth_mol_phase", 1e-3, index="Vap")
    iscale.set_scaling_factor(fs.cmp1.control_volume.work, 1e-8)
    iscale.set_scaling_factor(fs.gts1.control_volume.work, 1e-8)
    iscale.set_scaling_factor(
        fs.gts1.control_volume.properties_in[0].flow_mol, 1e-5
    )
    iscale.set_scaling_factor(
        fs.gts1.control_volume.properties_out[0].flow_mol, 1e-5
    )
    for i, v in fs.cmb1.control_volume.rate_reaction_extent.items():
        if i[1] == "ch4_cmb":
            iscale.set_scaling_factor(v, 1e-2)
        else:
            iscale.set_scaling_factor(v, 1)
    for i, c in fs.cmb1.reaction_extent.items():
        iscale.constraint_scaling_transform(c, 1e-2)
    for i, v in fs.cmb1.control_volume.rate_reaction_generation.items():
        if i[2] in ["O2", "CO2", "CH4", "H2O"]:
            iscale.set_scaling_factor(v, 0.001)
        else:
            iscale.set_scaling_factor(v, 0.1)
    for v in fs.gt_power.values():
        iscale.set_scaling_factor(v, 1e-8)
    for c in fs.gt_power_eqn.values():
        iscale.constraint_scaling_transform(c, 1e-8)
    for c in fs.inject1.enthalpy_mixing_equations.values():
        iscale.constraint_scaling_transform(c, 1e-8)
    for c in fs.inject1.mxpress_eqn.values():
        iscale.constraint_scaling_transform(c, 1e-5)
    for v in fs.cmp1.deltaP.values():
        iscale.set_scaling_factor(v, 1e-6)
    for v in fs.gts1.deltaP.values():
        iscale.set_scaling_factor(v, 1e-6)
    """ Heaters"""
    for v in fs.aph_tube.deltaP.values():
        iscale.set_scaling_factor(v, 1e-6)
    for v in fs.aph_shell.deltaP.values():
        iscale.set_scaling_factor(v, 1e-6)
    iscale.set_scaling_factor(fs.aph_shell.control_volume.heat, 1e-5)
    iscale.set_scaling_factor(fs.aph_tube.control_volume.heat, 1e-5)

    iscale.set_scaling_factor(fs.evap.shell.heat, 1e-8)
    iscale.set_scaling_factor(fs.evap.tube.heat, 1e-8)
    iscale.set_scaling_factor(fs.evap.tube.heat, 1e-8)
    iscale.set_scaling_factor(fs.evap.area, 1e-4)
    iscale.set_scaling_factor(fs.evap.overall_heat_transfer_coefficient, 1e-2)
    for v in fs.evap.shell.deltaP.values():
        iscale.set_scaling_factor(v, 1e-6)


def initialize_flowsheet(
    fs,
    outlvl=idaeslog.NOTSET,
    solver=None,
    optarg=None,
    load_from="gas_turbine_init.json.gz",
    save_to="gas_turbine_init.json.gz",
):
    """Initialize the gas turbine flowsheet"""
    init_log = idaeslog.getInitLogger(fs.name, outlvl, tag="flowsheet")
    solve_log = idaeslog.getSolveLogger(fs.name, outlvl, tag="flowsheet")

    if load_from is not None:
        if os.path.exists(load_from):
            init_log.info_high(f"GT load initial from {load_from}")
            # here suffix=False avoids loading scaling factors
            iutil.from_json(
                fs, fname=load_from, wts=iutil.StoreSpec(suffix=False)
            )
            return

    init_log.info_high("Gas Turbine Initialization Starting")
    solver_obj = get_solver(solver, optarg)

    # Feedwater outlet
    fs.feed_water1.outlet.flow_mol[0].fix(777.118091)
    fs.feed_water1.outlet.pressure[0].fix(2e6)
    fs.feed_water1.outlet.enth_mol[0].fix(
        iapws95.htpx(T=298.15 * pyo.units.K, P=2e6 * pyo.units.Pa)
    )
    fs.feed_water1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.liq01)
    # Evaporator Tube
    fs.evap.initialize(solver=solver, outlvl=outlvl, optarg=optarg)
    fs.evap.sat_vap_eqn.activate()

    # Feed air
    fs.feed_air1.flow_mol.fix(3200)
    fs.feed_air1.temperature.fix(298.15)
    fs.feed_air1.pressure.fix(101300)
    fs.feed_air1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.air01)

    fs.feed_air1.flow_mol.unfix()

    # Feed fuel
    fs.feed_fuel1.flow_mol.fix(100)
    fs.feed_fuel1.temperature.fix(298.15)
    fs.feed_fuel1.pressure.fix(1.2e6)
    fs.feed_fuel1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.fuel01)

    fs.feed_fuel1.flow_mol.unfix()

    # Compressor
    fs.cmp1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.air02)

    # Air Preheater: Tube section
    fs.con1 = pyo.Constraint(expr=fs.aph_tube.control_volume.properties_out[0].temperature == 850.0)
    fs.aph_tube.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.air03a)

    # Inject Translator
    fs.inject_translator.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.air03b)

    # Air Fuel mixer
    fs.inject1.mixed_state[0].pressure = pyo.value(fs.inject1.air.pressure[0])
    fs.inject1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.g01)

    # Combustor
    fs.con2 = pyo.Constraint(expr=fs.cmb1.control_volume.properties_out[0].temperature == 1520.0)
    fs.cmb1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.g02a)

    # Flue Translator
    fs.flue_translator.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.g02b)

    # Gas Turbine
    fs.gts1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    propagate_state(fs.g03)

    # APH Shell
    fs.aph_shell.heat_duty[0].\
        fix(-pyo.value(fs.aph_tube.heat_duty[0]))
    fs.aph_shell.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    fs.aph_shell.heat_duty[0].unfix()
    fs.con3 = pyo.Constraint(expr=fs.aph_tube.heat_duty[0] == -fs.aph_shell.heat_duty[0])

    propagate_state(fs.g04)
    propagate_state(fs.g05)
    fs.exhaust1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
    # GT power output
    fs.gt_power[0].fix(-3e7)

    # Solve
    solver_obj.solve(fs, tee=True)

    fs.gts1.ratioP.unfix()
    fs.exhaust1.pressure.fix(101300)
    solver_obj.solve(fs, tee=True)

    if save_to is not None:
        iutil.to_json(fs)
        if save_to is not None:
            iutil.to_json(fs, fname=save_to)
            init_log.info_high(f"Initialization saved to {save_to}")


def stream_col_gen(tag_group):
    """Generate a stream table heading from a group of stream tags"""
    for tag in tag_group.values():
        spltstr = tag.doc.split(":")
        stream = spltstr[0].strip()
        col = f"{spltstr[1].strip()} ({tag.get_unit_str()})"
        yield tag, stream, col


def stream_table(tag_group):
    """Generate a stream table from a group of stream tags"""
    rows = set()
    cols = set()
    tags = []
    for tag, stream, col in stream_col_gen(tag_group):
        rows.add(stream)
        cols.add(col)
        tags.append((tag, stream, col))
    df = pd.DataFrame(index=sorted(rows), columns=sorted(cols))
    for tag, stream, col in tags:
        df.at[stream, col] = tag.get_display_value()
    return df


def steam_streams_dataframe(fs):
    """Get stream table for steam streams"""
    return stream_table(fs.tags_steam_streams)


def flue_gas_streams_dataframe(fs):
    """Get stream table for flue gas streams"""
    return stream_table(fs.tags_flue_gas_streams)


def write_pfd(fs, fname=None):
    """Write process flow diagram"""
    pfd_file = "gt_template.svg"
    input_file = Path.cwd() / pfd_file
    with open(input_file, "r") as f:
        s = svg_tag(svg=f, tag_group=fs.tags_steam_streams)
    s = svg_tag(svg=s, tag_group=fs.tags_flue_gas_streams, outfile=fname)
    if fname is None:
        return s


def check_scaling(fs, m):
    """Check scaling of the flowsheet"""
    jac, nlp = iscale.get_jacobian(fs, scaled=True)
    print("Extreme Jacobian entries:")
    for i in iscale.extreme_jacobian_entries(jac=jac, nlp=nlp, large=100):
        print(f"    {i[0]:.2e}, [{i[1]}, {i[2]}]")
    print("Badly scaled variables:")
    for v, sv in iscale.badly_scaled_var_generator(
        m, large=1e2, small=1e-2, zero=1e-12
    ):
        print(f"    {v} -- {sv} -- {iscale.get_scaling_factor(v)}")
    print(f"Jacobian Condition Number: {iscale.jacobian_cond(jac=jac):.2e}")


def build_flowsheet(m):
    """Build the complete gas turbine flowsheet"""
    from idaes.core import FlowsheetBlock

    m.fs = FlowsheetBlock(dynamic=False)
    add_properties(m.fs)
    add_models(m.fs)
    add_constraints(m.fs)
    add_arcs(m.fs)
    set_initial_inputs(m.fs)
    add_tags(m.fs)
    set_scaling(m.fs)
    return m.fs


## Run Program ##
logging.getLogger("pyomo").setLevel(logging.ERROR)

def make_directory(path):
    """Make a directory if it doesn't exist"""
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

make_directory("data")
make_directory("data_pfds")
make_directory("data_tabulated")

use_idaes_solver_configuration_defaults()
idaes.cfg.ipopt.options.nlp_scaling_method = "user-scaling"
idaes.cfg.ipopt.options.linear_solver = "ma57"
idaes.cfg.ipopt.options.ma57_pivtol = 1e-5
idaes.cfg.ipopt.options.ma57_pivtolmax = 0.1
solver = pyo.SolverFactory("ipopt")

m = pyo.ConcreteModel()
build_flowsheet(m)
iscale.calculate_scaling_factors(m)
initialize_flowsheet(
    m.fs,
    load_from="gas_turbine_init.json.gz",
    save_to="gas_turbine_init.json.gz",
)
res = solver.solve(m, tee=True)

