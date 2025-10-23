# -- coding: utf-8 --
# Cálculo de densidad a 15 °C (API MPMS 11.2.4) a partir de ρ_obs y T_obs
# Vía resolución de γ60 con T24 (Tabla 24E, base 60°F) y conversión 60°F -> 15°C (≈59°F).

# API MPMS 11.2.4 - Densidad de líquidos hidrocarburos por medidores Coriolis. Table 2 Reference Fluids Parameters página 12

import math

# ==== Parámetros de referencia (API MPMS 11.2.4, Tabla 2) ====
# (name, gamma60, Tc[K], Zc, rhoc[kmol/m3], k1, k2, k3, k4)
REF = [
    ("EE(68/32)", 0.325022, 298.11, 0.27998, 6.250,  2.54616855327, -0.058244177754,  0.803398090807, -0.745720314137),
    ("Ethane",     0.355994, 305.33, 0.28220, 6.870,  1.89113042610, -0.370305782347, -0.544867288720,  0.337876634952),
    ("EP(65/35)",  0.429277, 333.67, 0.28060, 5.615,  2.20970078464, -0.294253708172, -0.405754420098,  0.319443433421),
    ("EP(35/65)",  0.470381, 352.46, 0.27930, 5.110,  2.25341981320, -0.266542138024, -0.372756711655,  0.384734185665),
    ("Propane",    0.507025, 369.78, 0.27626, 5.000,  1.96568366933, -0.327662435541, -0.417979702538,  0.303271602831),
    ("i-Butane",   0.562827, 407.85, 0.28326, 3.860,  2.04748034410, -0.289734363425, -0.330345036434,  0.291757103132),
    ("n-Butane",   0.584127, 425.16, 0.27536, 3.920,  2.03734743118, -0.299059145695, -0.418883095671,  0.380367738748),
    ("i-Pentane",  0.624285, 460.44, 0.27026, 3.247,  2.06541640707, -0.238366208840, -0.161440492247,  0.258681568613),
    ("n-Pentane",  0.631054, 469.65, 0.27235, 3.200,  2.11263474494, -0.261269413560, -0.291923445075,  0.308344290017),
    ("i-Hexane",   0.657167, 498.05, 0.26706, 2.727,  2.02382197871, -0.423550090067, -1.152810982570,  0.950139001678),
    ("n-Hexane",   0.664064, 507.35, 0.26762, 2.704,  2.17134547773, -0.232997313405, -0.267019794036,  0.378629524102),
    ("n-Heptane",  0.688039, 540.15, 0.26312, 2.315,  2.19773533433, -0.275056764147, -0.447144095029,  0.493770995799),
]

# ==== Constantes y rangos ====
RHO_W_60F = 999.016  # kg/m3, agua a 60°F (símbolo ρw60 en la norma)
T_MIN_C, T_MAX_C = -46.0, 93.0       # alcance de 11.2.4
GAMMA_MIN, GAMMA_MAX = 0.3500, 0.6880  # alcance de 11.2.4 (base 60°F)
TB_15C_K = 288.15
T_59F_K = (59.0 - 32.0) / 1.8 + 273.15  # 59°F ≈ 15°C exactos

# ==== Utilidades ====
def _rho_sat_reduced(k1, k2, k3, k4, Tr):
    tau = 1.0 - Tr
    # Ecuación de densidad de saturación reducida (T24/10)
    return 1.0 + (k1 * tau**0.35) / (1.0 + k2 * tau**0.65) + k3 * tau**2 + k4 * tau**3

def _pick_refs(gamma60):
    # elige dos fluidos contiguos que encierren gamma60; si está fuera, pega a extremos
    if gamma60 <= REF[0][1]:
        return REF[0], REF[1]
    if gamma60 >= REF[-1][1]:
        return REF[-2], REF[-1]
    for i in range(len(REF)-1):
        g1, g2 = REF[i][1], REF[i+1][1]
        if g1 <= gamma60 <= g2:
            return REF[i], REF[i+1]
    return REF[0], REF[1]

def ctl_24E(gamma60, T_obs_C):
    """
    CTL(T) = V60 / V_T  (Tabla 24E, base 60°F)  = F(T) / F(60°F)
    """
    if T_obs_C < T_MIN_C or T_obs_C > T_MAX_C:
        raise ValueError("Temperatura fuera del alcance de 11.2.4 (-46 a 93 °C).")

    # Limita gamma al dominio (sin abortar)
    gamma60 = max(min(gamma60, GAMMA_MAX - 1e-12), GAMMA_MIN + 1e-12)

    # Temperaturas en K
    Tx = T_obs_C + 273.15
    T60_K = (60.0 - 32.0) / 1.8 + 273.15

    # Selección de fluidos de referencia por gamma60
    f1, f2 = _pick_refs(gamma60)
    _, g1, Tc1, Zc1, rc1, k11, k21, k31, k41 = f1
    _, g2, Tc2, Zc2, rc2, k12, k22, k32, k42 = f2

    delta = (gamma60 - g1) / (g2 - g1)
    Tc = Tc1 + delta * (Tc2 - Tc1)
    Zc = Zc1 + delta * (Zc2 - Zc1)
    rc = rc1 + delta * (rc2 - rc1)
    h2 = (Zc * rc) / (Zc1 * rc1)

    # Temperaturas reducidas
    Tr_obs = Tx / Tc
    if Tr_obs >= 1.0:
        Tr_obs = 1.0 - 1e-12
    Tr60 = T60_K / Tc

    # Densidades reducidas de saturación
    rho60_r1 = _rho_sat_reduced(k11, k21, k31, k41, Tr60)
    rho60_r2 = _rho_sat_reduced(k12, k22, k32, k42, Tr60)
    rhoT_r1  = _rho_sat_reduced(k11, k21, k31, k41, Tr_obs)
    rhoT_r2  = _rho_sat_reduced(k12, k22, k32, k42, Tr_obs)

    # Función F(T) y F(60°F)
    F_T  = (rhoT_r1  * (1.0 + delta)) / ((rhoT_r1  * h2 / rhoT_r2 ) - (1.0 - delta))
    F_60 = (rho60_r1 * (1.0 + delta)) / ((rho60_r1 * h2 / rho60_r2) - (1.0 - delta))

    CTL = F_T / F_60  # V60 / V_T
    return round(CTL, 5)


# ==== Resolución de gamma60 desde ρ_obs y T_obs, y cálculo de ρ15 ====
def rho15_from_rhoobs_api1124(rho_obs, T_obs_C, max_iter=30, tol=1e-8):
    """
    Entrada:
      - rho_obs [kg/m3]: densidad Coriolis a T_obs (asumida a presión de saturación; ver nota)
      - T_obs_C [°C]
    Salida:
      - rho15 [kg/m3] (≈ densidad a 15°C)
      - gamma60 (relativa 60/60°F)
    """
    if T_obs_C < T_MIN_C or T_obs_C > T_MAX_C:
        raise ValueError("Temperatura fuera del alcance de 11.2.4 (-46 a 93 °C).")

    # Conjetura inicial de gamma60 usando CTL≈1 en primera pasada:
    gamma = max(min(rho_obs / RHO_W_60F, GAMMA_MAX - 1e-6), GAMMA_MIN + 1e-6)

    for _ in range(max_iter):
        ctl_obs = ctl_24E(gamma, T_obs_C)  # V60/Vobs
        # Predicción de rho_obs a partir de gamma actual:
        rho_obs_pred = (gamma * RHO_W_60F) * ctl_obs   # rho_obs = rho60 / CTL
        # Punto fijo: actualizar gamma para hacer coincidir rho_obs
        # => gamma_new = rho_obs * ctl_obs / RHO_W_60F
        gamma_new = rho_obs / (RHO_W_60F * ctl_obs)
        # Acotar al rango permitido (no abortar)
        gamma_new = max(min(gamma_new, GAMMA_MAX - 1e-12), GAMMA_MIN + 1e-12)

        if abs(gamma_new - gamma) < tol * max(1.0, abs(gamma)):
            gamma = gamma_new
            break
        gamma = gamma_new

    # Con gamma final, calcular rho60 y rho15 (usando 59°F como 15°C exacto)
    rho60 = gamma * RHO_W_60F
    # CTL a 59°F: V60 / V_59F
    ctl_59F = ctl_24E(gamma, (59.0 - 32.0) / 1.8)  # temperatura en °C
    # rho_59F = rho60 / CTL(59°F)
    rho15 = rho60 / ctl_59F
    return rho15, gamma

'''
# ==== Ejemplo directo ====
if __name__ == "__main__":
    # Ajusta a tus datos reales:
    rho_obs = 449.59  # kg/m3
    T_obs_C = 93     # °C

    rho15, gamma60 = rho15_from_rhoobs_api1124(rho_obs, T_obs_C)
    # Validación “suave” del ámbito nominal de densidades a 15°C en la Sección 2:
    if rho15 < 351.7 or rho15 > 687.8:
        print("ADVERTENCIA: ρ15 fuera del ámbito nominal de 11.2.4 (351.7–687.8 kg/m3 a 15°C).")
    print(f"γ60 (resuelto): {gamma60:.6f}")
    print(f"Densidad a 15°C (≈59°F): {rho15:.3f} kg/m³")
'''