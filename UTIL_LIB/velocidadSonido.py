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

def calcular_velSonido_gas(request_data):
    P = unit_converters.psi_to_bar(float(request_data.get("pressure", 1.0)))
    T = unit_converters.fahrenheit_to_celsius(float(request_data.get("temperature", 15.0)))

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
    
    print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    print(P,T)

    # Propiedades físicas
    gerg = pvtlib.AGA8("GERG-2008")
    gas_properties = gerg.calculate_from_PT(composition=composition, pressure=P, temperature=T)
    print(f"Gas properties: {gas_properties}")

    detail = pvtlib.AGA8("DETAIL")
    gas_properties_detail = detail.calculate_from_PT(composition=composition, pressure=P, temperature=T)

    return {
        "Velocidad_sonido": f"{gas_properties_detail['w']:.6f} m/s",
    }