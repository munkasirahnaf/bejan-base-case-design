# Optimization of CGAM Cogeneration System in IDAES
## Problem Statement
CGAM process simulation:
*A. Bejan, G. Tsatsaronis, M. Moran: Thermal Design and Optimization, Wiley,*
*New York, 1995.*
#### Base-case Design of the Cogeneration System

<figure>
  <img src="Files/bejan-book.png" alt="Cogeneration system">
</figure>

#### Parameter highlighting
- Specified input parameters: **`highlighted`**
- Results of simulation: normalfont

 #### Table: Mass flow rate, temperature, and pressure data for the cogeneration system
 |State|Substance|Mass Flow Rate (kg/s)|Temperature (K)|Pressure (bars)|
|:---|:---:|:---:|:---:|:---:|
|1|Air|91.2757|**`298.150`**|**`1.013`**|
|2|Air|91.2757|603.738|10.130|
|3|Air|91.2757|**`850.000`**|9.623|
|4|Combustion Products|92.9176|**`1520.000`**|9.142|
|5|Combustion Products|92.9176|1006.162|1.099|
|6|Combustion Products|92.9176|779.784|1.066|
|7|Combustion Products|92.9176|426.897|**`1.013`**|
|8|Water|**`14.0000`**|**`298.150`**|**`20.000`**|
|9|Water|14.0000|485.570|20.000|
|10|Methane|1.6419|**`298.150`**|**`12.000`**|

#### Table: Parameters and Decision Variables
|Parameter, decision variable|Symbol|Value|Unit|
|:---|:---:|:---:|:---:|
|**Ambient State**||||
|Temperature|$T_0$|298.15|K|
|Pressure|$p_0$|1.013|bar|
|**Overall process requirements**||||
|Net power output|$\dot{W}_{net}$|30|MW|
|Mass flow rate of steam|$\dot{m}_{steam}$|14|kg/s|
|Pressure of steam|$p_{steam}$|20|bar|
|Quality of steam|$x$|1||
|**Overall process decision variables**||||
|Pressure ratio of compression|$r_{p,AC}$|10||
|Isentropic efficiency of air compressor|$\eta_{s,AC}$|0.86||
|Isentropic efficiency of expander|$\eta_{s,EXP}$|0.86||
|Combustion chamber inlet temperature|$T_3$|850|K|
|Expander inlet temperature|$T_4$|1520|K|
|**Remaining flow- and component-based specifications**||||
|**Molar Analysis of Air**||||
|$N_2$ mole percent||77.48||
|$O_2$ mole percent||20.59||
|$CO_2$ mole percent||0.03||
|$H_2O$ mole percent||1.9||
|**Fuel**||||
|Temperature|$T_{10}$|298.15|K|
|Pressure|$p_{10}$|12|bar|
|Molar Analysis of $CH_4$||100||
|**Air Preheater (APH)**||||
|Pressure loss, air side|$\Delta{p}_{air,APH}$|5%||
|Pressure loss, flue gas side|$\Delta{p}_{fluegas,APH}$|3%||
|**Combustion Chamber**||||
|Thermal efficiency|$\eta_{CC}$|0.98||
|Pressure loss|$\Delta{p}_{CC}$|5%||
|**Heat Recovery Steam Generator**||||
|Pressure loss, flue gas side|$\Delta{p}_{fluegas,HRSG}$|5%||
|Pressure loss, water side|$\Delta{p}_{water,APH}$|0%||

#### Table: Dependent Variables
|Variable|Symbol|
|:---|:---:|
|Mass flow rate of air|$\dot{m}_{air}$|
|Mass flow rate of fuel|$\dot{m}_{fuel}$|
|Mass flow rate of flue gas|$\dot{m}_{fluegas}$|
|Molar analysis of flue gas||
|$N_2$ mole percent||
|$O_2$ mole percent||
|$CO_2$ mole percent||
|$H_2O$ mole percent||
|Pressures|$p_2$, $p_3$, $p_4$, $p_5$, $p_6$|
|Temperatures|$T_2$, $T_5$, $T_6$, $T_7$, $T_9$|
|Work rates||
|Work rate of Air Compressor|$\dot{W}_{AC}$|
|Work rate of Expander|$\dot{W}_{EXP}$|

## Results
#### Table: Validation of Combustion Chamber
|Variable|Symbol|Unit|Reference Value from Literature|Value from IDAES|
|:---|:-:|:-:|:-:|:-:|
|Mass flow rate of air|$\dot{m}_3$|kg/s|91.2757|91.1798|
|Mass flow rate of fuel|$\dot{m}_{10}$|kg/s|1.6419|1.6153|
|**Molar analysis of flue gas**|||||
|$N_2$ mole percent|||75.07|75.104|
|$O_2$ mole percent|||13.72|13.8254|
|$CO_2$ mole percent|||3.14|3.0957|
|$H_2O$ mole percent|||8.07|7.9749|

#### Table: Validation of CGAM Process, Reference Values, and Relative Deviations
|Dependent Variable $Y$|Symbol|Unit|Reference Value from Literature|Value from IDAES|$\Delta_{rel}=\left(\frac{Y}{Y_{ref}}-1\right)* 100\\%$|
|:---|:-:|:-:|:-:|:-:|:-:|
|Mass flow rate of air|$\dot{m}_{air}$|kg/s|91.2757|91.1798|0.105|
|Mass flow rate of fuel|$\dot{m}_{fuel}$|kg/s|1.6419|1.6153|1.6201|
|**Molar analysis of flue gas**|||||
|$N_2$ mole percent|||75.07|75.104|0.045|
|$O_2$ mole percent|||13.72|13.8254|0.768|
|$CO_2$ mole percent|||3.14|3.0957|1.411|
|$H_2O$ mole percent|||8.07|7.9749|1.178|
|**Temperatures of air/flue gas**||||||
|At the outlet of Air Compressor|$T_2$|K|603.738|613.2177|1.57|
|At the outlet of Expander|$T_5$|K|1006.162|1011.0889|0.4897|
|At the outlet of Air Preheater|$T_6$|K|779.784|795.5961|2.0278|
|At the outlet of HRSG|$T_7$|K|426.897|431.6191|1.1061|
|Temperature of steam|$T_9$|K|485.57|485.527|0.0089|
|**Pressures**||||||
||$p_2$|bar|10.130|10.13||
||$p_3$|bar|9.623|9.6235||
||$p_4$|bar|9.142|9.142325||
||$p_5$|bar|1.099|1.0993||
||$p_6$|bar|1.066|1.0663||
|**Work rates**||||||
|Work rate of the Air Compressor|$\dot{W}_{AC}$|MW|29.662|29.817|0.523|
|Work rate of the Air Compressor|$\dot{W}_{EXP}$|MW|59.662|59.817|0.260|

### Comparison with TESPy
Simulation results from TESPy is taken from
```bibtex
Thermal Engineering Systems in Python (TESPy): The implementation and validation of the chemical exergy
Hofmann, Mathias; Witte, Francesco; Shawky, Karim; Tuschy, Ilja; Tsatsaronis, George
DOI: https://doi.org/10.14279/depositonce-20664
```
#### Table: Reference Values, Values from TESPy, and Values from IDAES
|Dependent Variable|Symbol|Unit|Reference Value from Literature|Value from TESPy|Value from IDAES|
|:---|:-:|:-:|:-:|:-:|:-:|
|Mass flow rate of air|$\dot{m}_{air}$|kg/s|91.2757|90.939|91.1798|
|Mass flow rate of fuel|$\dot{m}_{fuel}$|kg/s|1.6419|1.647|1.6153|
|**Molar analysis of flue gas**|||||
|$N_2$ mole percent|||75.07|75.05|75.104|
|$O_2$ mole percent|||13.72|13.68|13.8254|
|$CO_2$ mole percent|||3.14|3.16|3.0957|
|$H_2O$ mole percent|||8.07|8.10|7.9749|
|**Temperatures of air/flue gas**||||||
|At the outlet of Air Compressor|$T_2$|K|603.738|611.55|613.2177|
|At the outlet of Expander|$T_5$|K|1006.162|1011.35|1011.0889|
|At the outlet of Air Preheater|$T_6$|K|779.784|794.85|795.5961|
|At the outlet of HRSG|$T_7$|K|426.897|430.45|431.6191|
|Temperature of steam|$T_9$|K|485.57|485.55|485.527|
|**Pressures**||||||
||$p_2$|bar|10.130|10.03|10.13|
||$p_3$|bar|9.623|9.6235|9.6235|
||$p_4$|bar|9.142|9.1423|9.142325|
||$p_5$|bar|1.099|1.0993|1.0993|
||$p_6$|bar|1.066|1.0663|1.0663|
|**Work rates**||||||
|Work rate of the Air Compressor|$\dot{W}_{AC}$|MW|29.662|29.695|29.817|
|Work rate of the Air Compressor|$\dot{W}_{EXP}$|MW|59.662|59.695|59.817|

## Process Flowsheet
```python
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

## Gas Turbine ##
@declare_process_block_class(
    "GasTurbineFlowsheet",
    doc=(
        "The gas turbine flowsheet"
    ),
)
class GasTurbineFlowsheetData(FlowsheetBlockData):
    def build(self):
        super().build()
        self._add_properties()
        self._add_models()
        self._add_constraints()
        self._add_arcs()
        self._set_initial_inputs()
        self._add_tags()
        self._set_scaling()

    def _add_properties(
        self,
        air_species={"CO2", "H2O", "O2", "N2"},
        cmb_species={"CH4", "O2", "H2O", "CO2", "N2"},
        flue_species={"O2", "H2O", "CO2", "N2"},
        rxns={
            "ch4_cmb": "CH4",
        },
    ):
        """Add property parameter blocks"""
        self.air_species = air_species
        self.cmb_species = cmb_species
        self.flue_species = flue_species
        self.rxns = rxns
        self.prop_water = iapws95.Iapws95ParameterBlock()
        self.air_prop_params = GenericParameterBlock(
            **get_prop(air_species, ["Vap"]),
            doc="Air property parameters",
        )
        self.cmb_prop_params = GenericParameterBlock(
            **get_prop(cmb_species, ["Vap"]),
            doc="Natural gas or Natural gas + Air property parameters",
        )
        self.flue_prop_params = GenericParameterBlock(
            **get_prop(flue_species, ["Vap"]),
            doc="Flue gas property parameters",
        )
        # Combustion reaction package
        self.gas_combustion = GenericReactionParameterBlock(
            **get_rxn(self.cmb_prop_params, self.rxns),
            doc="Reaction parameters package",
        )

    def _add_models(self):
        self.feed_air1 = um.Feed(
            doc="Air feed block",
            property_package=self.air_prop_params,
        )
        self.feed_fuel1 = um.Feed(
            doc="Fuel feed block",
            property_package=self.cmb_prop_params,
        ) 
        self.feed_water1 = um.Feed(
            doc="Feedwater block", 
            property_package=self.prop_water,
        )
        self.cmp1 = um.Compressor(
            doc="Gas turbine air compression section",
            property_package=self.air_prop_params,
            support_isentropic_performance_curves=False,
        )
        self.aph_shell = um.Heater(
            doc="Air preheater shell section",
            dynamic= False,
            property_package= self.flue_prop_params,
            has_pressure_change= True,
        )
        self.aph_tube = um.Heater(
            doc="Air preheater tube section",
            dynamic= False,
            property_package= self.air_prop_params,
            has_pressure_change= True,
        )
        self.inject_translator = um.Translator(
            doc="Translator for air to combustion mixture properties",
            inlet_property_package=self.air_prop_params,
            outlet_property_package=self.cmb_prop_params,
            outlet_state_defined=False,
        )
        self.inject1 = um.Mixer(
            doc="Fuel injection mixer (mix air and natural gas)",
            property_package=self.cmb_prop_params,
            inlet_list=["gas", "air"],
            momentum_mixing_type=um.MomentumMixingType.none,
        )
        self.cmb1 = um.StoichiometricReactor(
            doc="Combustor",
            property_package=self.cmb_prop_params,
            reaction_package=self.gas_combustion,
            has_pressure_change=True,
        )
        self.flue_translator = um.Translator(
            doc="Translate combustion mixture properties to flue gas",
            inlet_property_package=self.cmb_prop_params,
            outlet_property_package=self.flue_prop_params,
            outlet_state_defined=False,
        )
        self.gts1 = um.Turbine(
            doc="Gas turbine stage 1",
            property_package=self.flue_prop_params,
            support_isentropic_performance_curves=False,
        )
        self.evap = um.HeatExchanger(
            doc="HRSG Evaporator heat exchanger section",
            hot_side_name="shell",
            cold_side_name="tube",
            shell={"property_package": self.flue_prop_params,
                  "has_pressure_change": True,},
            tube={"property_package": self.prop_water},
            delta_temperature_callback=delta_temperature_lmtd_callback,
            flow_pattern=HeatExchangerFlowPattern.countercurrent,
            has_holdup=False,
        )
        self.exhaust1 = um.Product(
            doc="Air feed block",
            property_package=self.flue_prop_params,
        )
            
    def _add_constraints(self):
        # Complete combustion, use key components and 100% conversion (Make it 98%)
        @self.cmb1.Constraint(self.time, self.rxns.keys())
        def reaction_extent(b, t, r):
            key = self.rxns[r]
            prp = b.control_volume.properties_in[t]
            stc = self.gas_combustion.rate_reaction_stoichiometry[r, "Vap", key]
            extent = b.rate_reaction_extent[t, r]
            return extent == - prp.flow_mol * prp.mole_frac_comp[key] / stc
        # Pressure in the air-fuel mixer
        @self.inject1.Constraint(self.time)
        def mxpress_eqn(b, t):
            return b.mixed_state[t].pressure == b.air_state[t].pressure
        # The pressure drop in the combustor is 5%
        @self.cmb1.Constraint(self.time)
        def pressure_drop_eqn(b, t):
            return (
                0.95
                == b.control_volume.properties_out[t].pressure
                / b.control_volume.properties_in[t].pressure
            )
        # Pressure drop in the tube section of APH is 5%
        @self.aph_tube.Constraint(self.time)
        def pressure_drop_eqn(b, t):
            return (
                0.95
                == b.control_volume.properties_out[t].pressure
                / b.control_volume.properties_in[t].pressure
            )
        # Pressure drop in the shell section of APH is 3%
        @self.aph_shell.Constraint(self.time)
        def pressure_drop_eqn(b, t):
            return (
                0.97
                == b.control_volume.properties_out[t].pressure
                / b.control_volume.properties_in[t].pressure
            )
        # Pressure drop in the shell section of HRSG evaporator is 5%
        @self.evap.shell.Constraint(self.time)
        def pressure_drop_eqn(b, t):
            return (
                0.95
                == b.properties_out[t].pressure
                / b.properties_in[t].pressure
            )
        # Power
        @self.Expression(self.time)
        def gt_power_expr(b, t):
            return (
                self.cmp1.control_volume.work[t]
                + self.gts1.control_volume.work[t]
            )
        self.gt_power = pyo.Var(self.time, units=pyo.units.W)
        @self.Constraint(self.time)
        def gt_power_eqn(b, t):
            return b.gt_power[t] == b.gt_power_expr[t]
            
        # Evaporation
        @self.evap.Constraint(
            self.config.time, doc="Everything evaporates in evaporator"
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
            self.inject_translator,
            self.flue_translator,
        }
        for blk in translators:
            blk.temperature_eqn = pyo.Constraint(self.time, rule=rule_temperature)
            blk.pressure_eqn = pyo.Constraint(self.time, rule=rule_pressure)
            for t in self.config.time:
                iscale.constraint_scaling_transform(blk.temperature_eqn[t], 1e-2)
                iscale.constraint_scaling_transform(blk.pressure_eqn[t], 1e-6)
        self.inject_translator.flow_mole_comp_eqn = pyo.Constraint(
            self.time, self.air_species, rule=rule_flow_mol_comp
        )
        for i, c in self.inject_translator.flow_mole_comp_eqn.items():
            iscale.constraint_scaling_transform(c, 1e-3)
        self.inject_translator.zero_flow_eqn = pyo.Constraint(
            self.time, self.cmb_species - self.air_species, rule=rule_zero_flow
        )
        self.flue_translator.flow_mole_comp_eqn = pyo.Constraint(
            self.time, self.flue_species, rule=rule_flow_mol_comp
        )
        for i, c in self.flue_translator.flow_mole_comp_eqn.items():
            iscale.constraint_scaling_transform(c, 1e-3)

    def _add_arcs(self): 
        self.fuel01 = Arc(
            source=self.feed_fuel1.outlet,
            destination=self.inject1.gas,
        )
        self.air01 = Arc(
            source=self.feed_air1.outlet,
            destination=self.cmp1.inlet,
        )
        self.air02 = Arc(
            source=self.cmp1.outlet,
            destination=self.aph_tube.inlet,
        )
        self.air03a = Arc(
            source=self.aph_tube.outlet,
            destination=self.inject_translator.inlet,
        )
        self.air03b = Arc(
            source=self.inject_translator.outlet,
            destination=self.inject1.air,
        )
        self.g01 = Arc(source=self.inject1.outlet, destination=self.cmb1.inlet)
        self.g02a = Arc(source=self.cmb1.outlet, destination=self.flue_translator.inlet)
        self.g02b = Arc(source=self.flue_translator.outlet, destination=self.gts1.inlet)
        self.g03 = Arc(source=self.gts1.outlet, destination=self.aph_shell.inlet)
        self.g04 = Arc(source=self.aph_shell.outlet, destination=self.evap.shell_inlet)
        self.g05 = Arc(source=self.evap.shell_outlet, destination=self.exhaust1.inlet)
        self.liq01 = Arc(
            doc="Feedwater outlet to evaporator inlet",
            source=self.feed_water1.outlet,
            destination=self.evap.tube_inlet,
        )
        
        pyo.TransformationFactory("network.expand_arcs").apply_to(self)

    def _set_initial_inputs(self):
        # Feed air (Component: feed_air1)
        air_comp = {
            "CH4": 0.0,
            "O2": 0.2059,
            "H2O": 0.0190,
            "CO2": 0.0003,
            "N2": 0.7748,
        }
        self.feed_air1.temperature.fix(298.15)
        self.feed_air1.pressure.fix(101300)
        for i, v in air_comp.items():
            self.feed_air1.mole_frac_comp[:, i].fix(v)
        self.feed_air1.flow_mol[:] = 3200
        
        # Feed fuel (Component: feed_fuel1)
        ng_comp = {
            "CH4": 1.0,
            "O2": 0.0,
            "H2O": 0.0,
            "CO2": 0.0,
            "N2": 0.0,
        }
        self.feed_fuel1.temperature.fix(298.15)
        self.feed_fuel1.pressure.fix(1.2e6)
        self.feed_fuel1.flow_mol.fix(100)
        for i, v in ng_comp.items():
            self.feed_fuel1.mole_frac_comp[:, i].fix(v)
        # Feedwater
        self.feed_water1.outlet.flow_mol[0].fix(777.118091)
        self.feed_water1.outlet.pressure[0].fix(2e6)
        self.feed_water1.outlet.enth_mol[0].fix(
            iapws95.htpx(T=298.15 * pyo.units.K, P=2e6 * pyo.units.Pa)
        )
        # Compressor (Component: cmp1)
        self.cmp1.efficiency_isentropic.fix(0.86)
        self.cmp1.ratioP.fix(10)
        # Turbine
        self.gts1.ratioP.fix(0.2)
        self.gts1.efficiency_isentropic.fix(0.86)
        self.evap.area.fix(15000)
        

    def _add_tags(self):
        tag_stm = iutil.ModelTagGroup()
        tag_gas = iutil.ModelTagGroup()
        self.tags_steam_streams = tag_stm
        self.tags_flue_gas_streams = tag_gas
        stream_states = tables.stream_states_dict(
            tables.arcs_to_stream_dict(
                self,
                descend_into=False,
                additional={  # these are streams in or out without an arc
                    "g05": self.evap.shell_outlet,
                    "liq02": self.evap.tube_outlet,
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
            expr=100 * self.cmp1.efficiency_isentropic[0],
            format_string="{:.2f}",
            display_units="%",
        )
        tag_group["gts1_eff_isen"] = iutil.ModelTag(
            doc=f"Gas turbine stage 1 isentropic efficiency.",
            expr=100 * self.gts1.efficiency_isentropic[0],
            format_string="{:.2f}",
            display_units="%",
        )
        tag_group["cmp1_power"] = iutil.ModelTag(
            doc=f"Compressor power",
            expr=self.cmp1.control_volume.work[0],
            format_string="{:.2f}",
            display_units=pyo.units.MW,
        )
        tag_group["gts1_power"] = iutil.ModelTag(
            doc=f"GT stage 1 power",
            expr=self.gts1.control_volume.work[0],
            format_string="{:.2f}",
            display_units=pyo.units.MW,
        )
        tag_group["gt_total_power"] = iutil.ModelTag(
            doc=f"Total gas turbine power output",
            expr=-self.gt_power[0],
            format_string="{:.2f}",
            display_units=pyo.units.MW,
        )
        """
        tag_group["lhv_efficiency"] = iutil.ModelTag(
            doc=f"Overall LHV efficiency",
            expr=100 * self.lhv_efficiency[0],
            format_string="{:.2f}",
            display_units="%",
        )
        """
        tag_group["combustor_temperature"] = iutil.ModelTag(
            doc=f"Combustor Temperature",
            expr=self.cmb1.control_volume.properties_out[0].temperature,
            format_string="{:.2f}",
            display_units=pyo.units.K,
        )
        tag_group["fuel_flow"] = iutil.ModelTag(
            doc=f"Fuel mass flow",
            expr=self.feed_fuel1.properties[0].flow_mass,
            format_string="{:.3f}",
            display_units=pyo.units.kg / pyo.units.s,
        )

    def _set_scaling(self):
        prop_packages = {
            self.air_prop_params,
            self.cmb_prop_params,
            self.flue_prop_params,
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
        iscale.set_scaling_factor(self.cmp1.control_volume.work, 1e-8)
        iscale.set_scaling_factor(self.gts1.control_volume.work, 1e-8)
        iscale.set_scaling_factor(
            self.gts1.control_volume.properties_in[0].flow_mol, 1e-5
        )
        iscale.set_scaling_factor(
            self.gts1.control_volume.properties_out[0].flow_mol, 1e-5
        )
        for i, v in self.cmb1.control_volume.rate_reaction_extent.items():
            if i[1] == "ch4_cmb":
                iscale.set_scaling_factor(v, 1e-2)
            else:
                iscale.set_scaling_factor(v, 1)
        for i, c in self.cmb1.reaction_extent.items():
            iscale.constraint_scaling_transform(c, 1e-2)
        for i, v in self.cmb1.control_volume.rate_reaction_generation.items():
            if i[2] in ["O2", "CO2", "CH4", "H2O"]:
                iscale.set_scaling_factor(v, 0.001)
            else:
                iscale.set_scaling_factor(v, 0.1)
        for v in self.gt_power.values():
            iscale.set_scaling_factor(v, 1e-8)
        for c in self.gt_power_eqn.values():
            iscale.constraint_scaling_transform(c, 1e-8)
        for c in self.inject1.enthalpy_mixing_equations.values():
            iscale.constraint_scaling_transform(c, 1e-8)
        for c in self.inject1.mxpress_eqn.values():
            iscale.constraint_scaling_transform(c, 1e-5)
        for v in self.cmp1.deltaP.values():
            iscale.set_scaling_factor(v, 1e-6)
        for v in self.gts1.deltaP.values():
            iscale.set_scaling_factor(v, 1e-6)
        """ Heaters"""
        for v in self.aph_tube.deltaP.values():
            iscale.set_scaling_factor(v, 1e-6)
        for v in self.aph_shell.deltaP.values():
            iscale.set_scaling_factor(v, 1e-6)
        iscale.set_scaling_factor(self.aph_shell.control_volume.heat, 1e-5)
        iscale.set_scaling_factor(self.aph_tube.control_volume.heat, 1e-5)

        iscale.set_scaling_factor(self.evap.shell.heat, 1e-8)
        iscale.set_scaling_factor(self.evap.tube.heat, 1e-8)
        iscale.set_scaling_factor(self.evap.tube.heat, 1e-8)
        iscale.set_scaling_factor(self.evap.area, 1e-4)
        iscale.set_scaling_factor(self.evap.overall_heat_transfer_coefficient, 1e-2)
        for v in self.evap.shell.deltaP.values():
            iscale.set_scaling_factor(v, 1e-6)
        
    def initialize(
        self,
        outlvl=idaeslog.NOTSET,
        solver=None,
        optarg=None,
        load_from="gas_turbine_init.json.gz",
        save_to="gas_turbine_init.json.gz",
    ):
        
        init_log = idaeslog.getInitLogger(self.name, outlvl, tag="flowsheet")
        solve_log = idaeslog.getSolveLogger(self.name, outlvl, tag="flowsheet")

        if load_from is not None:
            if os.path.exists(load_from):
                init_log.info_high(f"GT load initial from {load_from}")
                # here suffix=False avoids loading scaling factors
                iutil.from_json(
                    self, fname=load_from, wts=iutil.StoreSpec(suffix=False)
                )
                return

        init_log.info_high("Gas Turbine Initialization Starting")
        solver_obj = get_solver(solver, optarg)

        # Feedwater outlet
        self.feed_water1.outlet.flow_mol[0].fix(777.118091)
        self.feed_water1.outlet.pressure[0].fix(2e6)
        self.feed_water1.outlet.enth_mol[0].fix(
            iapws95.htpx(T=298.15 * pyo.units.K, P=2e6 * pyo.units.Pa)
        )
        self.feed_water1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.liq01)
         # Evaporator Tube
        self.evap.initialize(solver=solver, outlvl=outlvl, optarg=optarg)
        self.evap.sat_vap_eqn.activate()
        
        # Feed air
        self.feed_air1.flow_mol.fix(3200)
        self.feed_air1.temperature.fix(298.15)
        self.feed_air1.pressure.fix(101300)
        self.feed_air1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.air01)
        
        self.feed_air1.flow_mol.unfix()
        
        # Feed fuel
        self.feed_fuel1.flow_mol.fix(100)
        self.feed_fuel1.temperature.fix(298.15)
        self.feed_fuel1.pressure.fix(1.2e6)
        self.feed_fuel1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.fuel01)
        
        self.feed_fuel1.flow_mol.unfix()
        
        # Compressor
        self.cmp1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.air02)
        
        # Air Preheater: Tube section
        self.con1 = pyo.Constraint(expr=self.aph_tube.control_volume.properties_out[0].temperature == 850.0)
        self.aph_tube.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.air03a)
        
        #Inject Translator
        self.inject_translator.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.air03b)

        # Air Fuel mixer
        self.inject1.mixed_state[0].pressure = pyo.value(self.inject1.air.pressure[0])
        self.inject1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.g01)

        # Combustor
        self.con2 = pyo.Constraint(expr=self.cmb1.control_volume.properties_out[0].temperature == 1520.0)
        self.cmb1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.g02a)
        
        # Flue Translator
        self.flue_translator.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.g02b)

        # Gas Turbine
        self.gts1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        propagate_state(self.g03)

        # APH Shell
        self.aph_shell.heat_duty[0].\
            fix(-pyo.value(self.aph_tube.heat_duty[0]))
        self.aph_shell.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        self.aph_shell.heat_duty[0].unfix()
        self.con3 = pyo.Constraint(expr=self.aph_tube.heat_duty[0] == -self.aph_shell.heat_duty[0])
        
        propagate_state(self.g04)
        propagate_state(self.g05)
        self.exhaust1.initialize(outlvl=outlvl, solver=solver, optarg=optarg)
        # GT power output
        self.gt_power[0].fix(-3e7)

        # Solve
        solver_obj.solve(self, tee=True)

        self.gts1.ratioP.unfix()
        self.exhaust1.pressure.fix(101300)
        solver_obj.solve(self, tee=True)
        
        if save_to is not None:
            iutil.to_json(self)
            if save_to is not None:
                iutil.to_json(self, fname=save_to)
                init_log.info_high(f"Initialization saved to {save_to}")
                
    @staticmethod
    def _stream_col_gen(tag_group):
        """Generate a stream table heading from a group of stream tags"""
        for tag in tag_group.values():
            spltstr = tag.doc.split(":")
            stream = spltstr[0].strip()
            col = f"{spltstr[1].strip()} ({tag.get_unit_str()})"
            yield tag, stream, col

    @staticmethod
    def _stream_table(tag_group):
        """Generate a stream table from a group of stream tags"""
        rows = set()
        cols = set()
        tags = []
        for tag, stream, col in GasTurbineFlowsheetData._stream_col_gen(tag_group):
            rows.add(stream)
            cols.add(col)
            tags.append((tag, stream, col))
        df = pd.DataFrame(index=sorted(rows), columns=sorted(cols))
        for tag, stream, col in tags:
            df.at[stream, col] = tag.get_display_value()
        return df
    
    def steam_streams_dataframe(self):
        """Get stream table for steam streams"""
        return self._stream_table(self.tags_steam_streams)

    def flue_gas_streams_dataframe(self):
        """Get stream table for flue gas streams"""
        return self._stream_table(self.tags_flue_gas_streams)

    pfd_file = "gt_template.svg"

    def write_pfd(self, fname=None):

        input_file = Path.cwd() / self.pfd_file
        with open(input_file, "r") as f:
            s = svg_tag(svg=f, tag_group=self.tags_steam_streams)
        s = svg_tag(svg=s, tag_group=self.tags_flue_gas_streams, outfile=fname)
        if fname is None:
            return s

    def check_scaling(self):
        jac, nlp = iscale.get_jacobian(self, scaled=True)
        print("Extreme Jacobian entries:")
        for i in iscale.extreme_jacobian_entries(jac=jac, nlp=nlp, large=100):
            print(f"    {i[0]:.2e}, [{i[1]}, {i[2]}]")
        print("Badly scaled variables:")
        for v, sv in iscale.badly_scaled_var_generator(
            m, large=1e2, small=1e-2, zero=1e-12
        ):
            print(f"    {v} -- {sv} -- {iscale.get_scaling_factor(v)}")
        print(f"Jacobian Condition Number: {iscale.jacobian_cond(jac=jac):.2e}")

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
m.fs = GasTurbineFlowsheet(dynamic=False)
iscale.calculate_scaling_factors(m) 
m.fs.initialize(
    load_from="gas_turbine_init.json.gz",
    save_to="gas_turbine_init.json.gz",
)
res = solver.solve(m, tee=True)
```

