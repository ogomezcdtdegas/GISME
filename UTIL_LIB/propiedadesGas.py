import pvtlib
from pvtlib import unit_converters
import math

# Opciones de gases
GASES_OPCIONES = {
    "C1": "Methane", "N2": "Nitrogen", "CO2": "Carbon Dioxide", "C2": "Ethane",
    "C3": "Propane", "iC4": "Isobutane", "nC4": "n-Butane", "iC5": "Isopentane",
    "nC5": "n-Pentane", "nC6": "Hexane", "nC7": "Heptane", "nC8": "Octane",
    "nC9": "Nonane", "nC10": "Decane", "H2": "Hydrogen", "O2": "Oxygen",
    "CO": "Carbon Monoxide", "H2O": "Water", "H2S": "Hydrogen Sulfide",
    "He": "Helium", "Ar": "Argon"
}

# Poder calorífico en Btu/ft3 ASTM D3588-98
HEATING_VALUES = {
    "C1": {"HHV": 1010.0, "LHV": 909.0},
    "C2": {"HHV": 1769.7, "LHV": 1618.7},
    "C3": {"HHV": 2516.1, "LHV": 2314.9},
    "iC4": {"HHV": 3251.9, "LHV": 3004.0},
    "nC4": {"HHV": 3262.3, "LHV": 3010.8},
    "iC5": {"HHV": 4000.9, "LHV": 3699.0},
    "nC5": {"HHV": 4008.9, "LHV": 3703.9},
    "nC6": {"HHV": 4755.9, "LHV": 4403.9},
    "nC7": {"HHV": 5502.5, "LHV": 5100.3},
    "nC8": {"HHV": 6248.9, "LHV": 5796.2},
    "nC9": {"HHV": 6996.5, "LHV": 6493.6},
    "nC10": {"HHV": 7742.9, "LHV": 7189.9},
    "H2": {"HHV": 324.2, "LHV": 273.93},
    "CO": {"HHV": 320.5, "LHV": 320.5},
    # Otros gases sin poder calorífico quedan fuera del cálculo
}

# Constantes base
T_BASE_K = 288.5556      # 15 °C
P_BASE_BAR = 1.01325353
Z_BASE = 1
DENS_AIRE = 1.2192452 # kg/m3
kg_per_m3_to_lb_per_ft3 = 0.062428

def calcular_propiedades_gas(request_data):
    Pb = unit_converters.psi_to_bar(float(request_data.get("presBs", 1.0)))
    Tb = unit_converters.fahrenheit_to_celsius(float(request_data.get("tempBs", 15.0)))
    P = unit_converters.psi_to_bar(float(request_data.get("pressure", 1.0)))
    T = unit_converters.fahrenheit_to_celsius(float(request_data.get("temperature", 15.0)))
    T_K = T + 273.15
    T_Kb = Tb + 273.15

    composition = {}
    total_percentage = 0

    for gas_key, value in request_data.items():
        if gas_key.startswith("gas_"):
            gas_id = gas_key.replace("gas_", "")
            value = float(value)
            if value > 0:
                composition[gas_id] = value
                total_percentage += value

    if total_percentage == 0:
        return {"error": "La composición del gas no puede ser 0%."}

    # Normalizar composición
    composition_frac = {k: v / total_percentage for k, v in composition.items()}

    # Propiedades físicas
    gerg = pvtlib.AGA8("GERG-2008")
    gas_properties = gerg.calculate_from_PT(composition=composition, pressure=P, temperature=T)
    print(f"Gas properties: {gas_properties}")
    gas_propertiesBas = gerg.calculate_from_PT(composition=composition, pressure=Pb, temperature=Tb)

    detail = pvtlib.AGA8("DETAIL")
    gas_properties_detail = detail.calculate_from_PT(composition=composition, pressure=P, temperature=T)
    gas_properties_detailBas = detail.calculate_from_PT(composition=composition, pressure=Pb, temperature=Tb)

    # ----------- HHV/LHV base -------------
    HHV_base = sum(xi * HEATING_VALUES[g]["HHV"] for g, xi in composition_frac.items() if g in HEATING_VALUES)
    LHV_base = sum(xi * HEATING_VALUES[g]["LHV"] for g, xi in composition_frac.items() if g in HEATING_VALUES)

    # ----------- ajuste a condiciones reales (opcional) ----------
    Z_real = gas_propertiesBas["z"]
    factor = (Pb / P_BASE_BAR) * (Z_BASE / Z_real) * (T_BASE_K / T_Kb)
    HHV_real = HHV_base * factor
    LHV_real = LHV_base * factor

    from pvtlib import thermodynamics
    gas_thermodynamics_detail = thermodynamics.natural_gas_viscosity_Lee_et_al(
        T, gas_properties["mm"], gas_properties["rho"]
    )

    return {
        "rho_gerg": f"{gas_properties['rho'] * kg_per_m3_to_lb_per_ft3:.6f}",
        "rho_gergRelative": f"{gas_propertiesBas['rho'] / DENS_AIRE:.6f}",
        "rho_detail": f"{gas_properties_detail['rho'] * kg_per_m3_to_lb_per_ft3:.6f}",
        "z_gerg": f"{gas_properties['z']:.6f}",
        "z_gergBas": f"{gas_propertiesBas['z']:.6f}",
        "z_detail": f"{gas_properties_detail['z']:.6f}",
        "cps": f"{gas_properties_detail['cp']:.6f} J/(mol·K)",
        "mm": f"{gas_properties_detail['mm']:.6f}",
        "mu": f"{gas_thermodynamics_detail:.6f}",
        "d": f"{gas_properties_detail['d']:.6f}",
        # ---- poder calorífico -----
        "HHV_BTU_ft3_base": f"{HHV_base:.2f} BTU/ft³ (base 60 °F,14.696 psia)",
        "LHV_BTU_ft3_base": f"{LHV_base:.2f} BTU/ft³ (base 60 °F,14.696 psia)",
        "HHV_BTU_ft3_real": f"{HHV_real:.2f}",
        "LHV_BTU_ft3_real": f"{LHV_real:.2f}",
        "indice_Wobbe": f"{(HHV_real / math.sqrt(gas_propertiesBas['rho']/ DENS_AIRE)):.6f}",
    }