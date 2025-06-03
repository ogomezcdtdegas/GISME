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

RANKING = 459.67  # Conversión de Fahrenheit a Rankine

def calcular_volBaseML(request_data):
    Pb = unit_converters.psi_to_bar(float(request_data.get("presBs", 1.0)))
    Tb = unit_converters.fahrenheit_to_celsius(float(request_data.get("tempBs", 15.0)))
    P = unit_converters.psi_to_bar(float(request_data.get("pressure", 1.0)))
    T = unit_converters.fahrenheit_to_celsius(float(request_data.get("temperature", 15.0)))
    volMedido = float(request_data.get("volMedido", 0.0))

    tbk = float(request_data.get("tempBs", 15.0)) + RANKING
    tfk = float(request_data.get("temperature", 15.0)) + RANKING

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

    # Propiedades físicas
    detail = pvtlib.AGA8("DETAIL")
    gas_properties_detail = detail.calculate_from_PT(composition=composition, pressure=P, temperature=T)
    gas_properties_detailBas = detail.calculate_from_PT(composition=composition, pressure=Pb, temperature=Tb)

    print(f"Gas properties: {gas_properties_detail}")

    zf = gas_properties_detail["z"]
    zb = gas_properties_detailBas["z"]

    vb = volMedido * (abs(P)/abs(Pb)) * (tbk/tfk) * (zb/zf) 

    desv =(abs(volMedido - ( vb )) / ( vb )) * 100
    print(f"Volumen base calculado: {vb}, Desviación: {desv}")

    return {
        "volBase": f"{vb:.6f}",
        "Desviación": f"{desv:.6f}",
        "zf": f"{zf:.6f}",
        "zb": f"{zb:.6f}",
    }