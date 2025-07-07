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
    "H2S": {"HHV": 637.1, "LHV": 0},
    "H2O": {"HHV": 50.312, "LHV": 0},
    # Otros gases sin poder calorífico quedan fuera del cálculo
    "O2": {"HHV": 0, "LHV": 0},
    "N2": {"HHV": 0, "LHV": 0},
    "Ar": {"HHV": 0, "LHV": 0},
    "He": {"HHV": 0, "LHV": 0},
    "CO2": {"HHV": 0, "LHV": 0}
}

# Presión crítica (psia)
P = [667, 492.8, 1070, 707.8, 615, 3200.1, 1300, 187.5, 506.8, 731.4,
     527.9, 548.8, 490.4, 488.1, 436.9, 396.8, 360.7, 330.7, 304.6, 32.99, 706.9]
#         CH4,   N2,   CO2,  C2H6, C3H8,  H2O,   H2S,   H2,   CO,   O2,
#       iC4H10, nC4H10, iC5H12, nC5H12, nC6H14, nC7H16, nC8H18, nC9H20, nC10H22, He,   Ar

# Temperatura crítica (°R)
T = [343.01, 227.19, 547.4, 549.74, 665.6, 1164.77, 672.07, 59.37, 239.16, 278.27,
     734.07, 765.19, 828.63, 845.37, 913.47, 972.47, 1023.82, 1070.39, 1111.77, 9.36, 271.47]
#         CH4,   N2,   CO2,  C2H6, C3H8,  H2O,   H2S,   H2,   CO,   O2,
#       iC4H10, nC4H10, iC5H12, nC5H12, nC6H14, nC7H16, nC8H18, nC9H20, nC10H22, He,   Ar

# Factor Z crítico (adimensional)
Z = [0.288, 0.29, 0.274, 0.285, 0.281, 0.229, 0.284, 0.305, 0.295, 0.288,
     0.283, 0.274, 0.271, 0.262, 0.26, 0.263, 0.259, 0.26, 0.247, 0.301, 0.291]
#         CH4,   N2,   CO2,  C2H6, C3H8,  H2O,   H2S,   H2,   CO,   O2,
#       iC4H10, nC4H10, iC5H12, nC5H12, nC6H14, nC7H16, nC8H18, nC9H20, nC10H22, He,   Ar

# Masa molar (g/mol)
M = [16.043, 28.0135, 44.01, 30.07, 44.097, 18.0153, 34.082, 2.0159, 28.01, 31.9988,
     58.123, 58.123, 72.15, 72.15, 86.177, 100.204, 114.231, 128.258, 142.285, 4.0026, 39.948]
#         CH4,   N2,   CO2,  C2H6, C3H8,  H2O,   H2S,   H2,   CO,   O2,
#       iC4H10, nC4H10, iC5H12, nC5H12, nC6H14, nC7H16, nC8H18, nC9H20, nC10H22, He,   Ar

COMPONENT_KEYS = [
    "C1", "N2", "CO2", "C2", "C3",
    "H2O", "H2S", "H2", "CO", "O2",
    "iC4", "nC4", "iC5", "nC5", "nC6",
    "nC7", "nC8", "nC9", "nC10", "He", "Ar"
]

P_dict = dict(zip(COMPONENT_KEYS, P))  # Presión crítica
T_dict = dict(zip(COMPONENT_KEYS, T))  # Temperatura crítica
Z_dict = dict(zip(COMPONENT_KEYS, Z))  # Factor Z
M_dict = dict(zip(COMPONENT_KEYS, M))  # Masa molar

# Constantes base
T_BASE_K = 288.5556      # 15 °C
P_BASE_BAR = 1.01325353
Z_BASE = 1
DENS_AIRE = 1.2192452 # kg/m3
kg_per_m3_to_lb_per_ft3 = 0.06242796
R_ConstanteGas = 8.314472  # J/(mol·K)
Masa_Molar_AireSeco = 0.0289635  # kg/mol

def calcular_propiedades_gas(request_data):
    Pb = round(unit_converters.psi_to_bar(float(request_data.get("presBs", 1.0))),6)
    Tb = round(unit_converters.fahrenheit_to_celsius(float(request_data.get("tempBs", 15.0))),4)
    P = round(unit_converters.psi_to_bar(float(request_data.get("pressure", 1.0))),6)
    T = round(unit_converters.fahrenheit_to_celsius(float(request_data.get("temperature", 15.0))),4)
    
    Tk = (float(request_data.get("temperature", 60)) - 32) * 5/9 + 273.15
    Tkb = (float(request_data.get("tempBs", 60)) - 32) * 5/9 + 273.15
    Ppasb = float(request_data.get("presBs", 14.695)) * 6894.76

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

    # ----------- ajuste a condiciones reales (opcional) ----------
    Z_real = gas_properties_detailBas["z"]
    HHV_Calc = ((((HHV_base/round(Z_real,6)) * float(request_data.get("presBs", 14.696)))/14.696))

    #----------------------------------------------------------------------------------------------------------------------------------
    '''----------------------------------------- Cálculo de densidad relativa Gr ------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------
    # Cálculo de densidad relativa Gr
    '''Densidad del Gas'''
    DensGas = (Ppasb * (round(gas_properties_detailBas['mm'], 6) / 1000)) / (round(gas_properties_detailBas['z'],6) * R_ConstanteGas * Tkb) # kg/m3

    '''Densidad del Aire'''
    DensAire = (Ppasb * Masa_Molar_AireSeco) / (1.0 * R_ConstanteGas * Tkb) # kg/m3

    '''Densidad Relativa Gr'''
    DensGr = DensGas / DensAire # Adimensional
    #----------------------------------------------------------------------------------------------------------------------------------
    '''-----------------------------------------------------------------------------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------------
    '''--------------------------------------------------------Indice de Woobe------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------
    Iw = (HHV_Calc / math.sqrt(DensGr))  # Btu/ft3
    #----------------------------------------------------------------------------------------------------------------------------------
    '''-----------------------------------------------------------------------------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------------
    '''-------------------------------------------------Cálculo de Viscocidad PVTLib------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------
    from pvtlib import thermodynamics
    gas_thermodynamics_detail = thermodynamics.natural_gas_viscosity_Lee_et_al(
        T, gas_properties_detail["mm"], gas_properties_detail["rho"]
    )

    rho = round(gas_properties_detail["rho"], 6)
    #----------------------------------------------------------------------------------------------------------------------------------
    '''-----------------------------------------------------------------------------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------------
    '''------------------------------------La viscosidad de un gas natural con la correlación de Carr-------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------
    # Cálculo de Viscosidad
    Mwair = 28.963
    Ppc = sum(xi * P_dict[g] for g, xi in composition_frac.items())         # psia
    Tpc = sum(xi * T_dict[g] for g, xi in composition_frac.items())         # °R
    Zpc = sum(xi * Z_dict[g] for g, xi in composition_frac.items())         # adim
    Mwg = sum(xi * M_dict[g] for g, xi in composition_frac.items())         # g/mol

    # G = Peso molecular relativo
    G = Mwg / Mwair
    dpc = 2.698825 * ((G * Ppc) / (Zpc * Tpc)) # lb/ft³
    dpr = (gas_properties_detail["rho"] * kg_per_m3_to_lb_per_ft3)/ dpc

    # Factor A
    A = ((1.023) + (0.23364 * dpr) + (0.58533 * dpr**2) -
        (0.40758 * dpr**3) + (0.093324 * dpr**4)) ** 4

    # Factor B
    Pcatm = Ppc / 14.696
    Tkc = Tpc / 1.8
    B = ((Tkc ** (1 / 6)) / ((Mwg ** 0.5) * (Pcatm ** (2 / 3))))

    T_Rankine = Tk * 9 / 5
    ulc = ((1.709e-5) - (2.062e-6) * G) * (T_Rankine - 460) + 0.008188 - 0.00615 * math.log10(G)

    CO2 = composition_frac.get("CO2", 0) * 1e-3 * ((9.08 * math.log10(G) + 6.24))
    N2  = composition_frac.get("N2", 0)  * 1e-3 * ((8.48 * math.log10(G) + 9.59))
    H2S = composition_frac.get("H2S", 0) * 1e-3 * ((8.49 * math.log10(G) + 3.73))

    ul = ulc + CO2 + N2 + H2S
    viscosidad = ul + (((A - 1) * 1e-4) / B)
    #----------------------------------------------------------------------------------------------------------------------------------
    '''-----------------------------------------------------------------------------------------------------------------------------'''
    #----------------------------------------------------------------------------------------------------------------------------------

    return {
        "rho_gerg": f"{gas_properties['rho'] * kg_per_m3_to_lb_per_ft3:.6f}",
        "rho_detailRelative": f"{DensGr:.6f}",
        "rho_detail": f"{rho * kg_per_m3_to_lb_per_ft3:.6f}",
        "z_gerg": f"{gas_properties_detail['z']:.6f}",
        "z_gergBas": f"{gas_properties_detailBas['z']:.6f}",
        "z_detail": f"{gas_properties_detail['z']:.6f}",
        "cps": f"{gas_properties_detail['cp']:.6f} J/(mol·K)",
        "mm": f"{gas_properties_detail['mm']:.6f}",
        "mu": f"{viscosidad:.6f}",
        "d": f"{gas_properties_detail['d']:.6f}",
        # ---- poder calorífico -----
        "HHV_BTU_ft3_real": f"{HHV_Calc:.6f}",
        "indice_Wobbe": f"{Iw:.6f}",
        "Velocidad_sonido": f"{gas_properties_detail['w']:.6f} m/s",
    }