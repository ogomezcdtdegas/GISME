import numpy as np
import math
from copy import deepcopy

def calcular_volumen(data):
    """
    Calcula el volumen neto estándar (NSV) a partir de la data de un medidor Coriolis.

    Parámetros:
        data (dict): Diccionario con los datos del medidor y del producto.

    Retorna:
        dict: Diccionario con el valor calculado de NSV.
    """
    # Extraer variables relevantes
    masa = data.get("Masa", 0)
    mf = data.get("MF", 1.0)
    densidad_base = data.get("dl", 1.0)
    tipo_met = data.get("tipoMet", "COR").upper()
    bbl_m3 = 6.289812  # Factor de conversión de barriles a metros cúbicos

    # Validar tipo de medidor
    if tipo_met != "COR":
        raise ValueError("Esta función está diseñada para medidores tipo COR (Coriolis).")

    # Verificaciones básicas
    if densidad_base <= 0:
        raise ValueError("La densidad base debe ser mayor que cero.")
    if masa <= 0:
        raise ValueError("La masa indicada debe ser mayor que cero.")

    # Calcular masa corregida y NSV
    masa_corregida = masa * mf
    nsv = masa_corregida*bbl_m3 / densidad_base

    # Retornar como diccionario
    return {"NSV": nsv,
            "Masa_Corregida": masa_corregida}


def calcular_uvisc(data):
    """
    Calcula el número de Reynolds según la fórmula del Excel ajustada
    para un medidor Coriolis u otro medidor másico.
    Mantiene la coherencia de unidades imperiales (in, cP, etc.).
    """

    # Extraer variables del diccionario
    Qm = data.get("Qm", 0)             # Flujo másico (kg/h)
    dl = data.get("dl", 0)             # Densidad (kg/m³)
    DN = data.get("DN", 0)             # Diámetro nominal (in)
    deltavis = data.get("deltavis", 1) # Rango de viscosidad dinámica (cP)
    vis = data.get("vis", 1)           # Viscosidad dinámica (cP)
    
    # Constantes del Excel
    bbl_m3 = 6.289812  # Barriles por m³
    factor_conv = 9702 # Factor de ajuste de unidades
    dens_conv = 1550   # kg/m³ → lb/ft³
    
    # === Fórmula según Excel corregida (sin convertir DN) ===
    Re = 0 if Qm == 0 else (
        ((((Qm * bbl_m3 / dl) * factor_conv) / 3600)
         / ((math.pi * (DN ** 2) / 4)))
        * DN
        / (deltavis / 1000 / dl * dens_conv)
    )

    Re_2 = 0 if Qm == 0 else (
        ((((Qm * bbl_m3 / dl) * factor_conv) / 3600)
         / ((math.pi * (DN ** 2) / 4)))
        * DN
        / (vis / 1000 / dl * dens_conv)
    )

    # evitar log(0) o valores negativos
    def safe_log(x):
        return math.log(x) if x > 0 else float("-inf")
    
    Re_solo = abs(0.1794 * safe_log(Re) - 2.0477) if Re > 0 else 0.0

    sum_re = Re + Re_2
    Re_combinado = abs(0.1794 * safe_log(sum_re) - 2.0477) if sum_re > 0 else 0.0     

    # === Cálculo de la incertidumbre por viscosidad ===
    if deltavis == 0:
        uvisc = 0
    else:
        if Re < 10000:  
            uvisc = Re_solo - Re_combinado
        else:
            uvisc = 0
    return uvisc

def combinar_incertidumbre_dict(componentes, grados_libertad):
    """
    Combina componentes de incertidumbre (u_i) mediante la raíz cuadrática
    y calcula los grados de libertad efectivos (v_eff) con la fórmula de Welch_Satterthwaite.

    Parámetros
    ----------
    componentes : dict
        Diccionario con los componentes de incertidumbre (ej. {'cal': ucal, 'der': uder, ...})
        Cada valor debe ser numérico (float).
    grados_libertad : dict
        Diccionario con los grados de libertad correspondientes a cada componente
        (ej. {'cal': 50, 'der': 30, ...}). Puede incluir math.inf para contribuciones tipo B.

    Retorna
    -------
    u_c : float
        Incertidumbre combinada (raíz cuadrática).
    v_eff : float
        Grados de libertad efectivos según Welch_Satterthwaite.
    """

    # --- 1. Cálculo de la incertidumbre combinada ---
    suma_cuadrados = sum(v**2 for v in componentes.values())
    u_c = math.sqrt(suma_cuadrados)

    # --- 2. Cálculo de los grados de libertad efectivos ---
    # Evitar división por cero en componentes con v_i = 0
    suma_v = 0
    for key, u_i in componentes.items():
        v_i = grados_libertad.get(key, math.inf)
        if v_i != 0 and v_i != math.inf:
            suma_v += (u_i**4) / v_i
        elif v_i == math.inf:
            suma_v += 0  # contribución tipo B no añade incertidumbre estadística
        else:
            raise ValueError(f"El componente '{key}' tiene grados de libertad = 0, no válido.")

    v_eff = math.inf if suma_v == 0 else (u_c**4) / suma_v

    return u_c, v_eff

def GUM_secundario(data):
    """
    Calcula incertidumbres estándar combinadas (uX)
    y los grados de libertad efectivos usando la fórmula de Welch_Satterthwaite.
    """
    # ======================================================
    # --- 0. Calculos Previos ---
    # ======================================================
    contribuciones_sub = {}
    Tl        = data.get("Tl", 0)
    Pl        = data.get("Pl", 0)
    dl        = data.get("dl", 0)
    product   = data.get("product", 'GLP')
    Qm        = data.get("Qm", 0)
    uvisc     = calcular_uvisc(data)

    # ======================================================
    # --- 1. MF ---
    # ======================================================
    Masa = data.get("Masa", 0)
    MF = data.get("MF", 1)
    DN = data.get("DN", 0)

    # --- MF ---
    ucalMet = data.get("ucalMet", 0)
    kcalMet = data.get("kcalMet", 2)
    esisMet = data.get("esisMet", 0)
    ucartaMet = data.get("ucartaMet", 0)
    zeroStab = data.get("zeroStab", 0)

    # Contribuciones individuales
    ucalMF = (ucalMet * MF / 100) / kcalMet
    uerrMF = (esisMet * MF / 100) / math.sqrt(3)
    ucartaMF = ucartaMet
    uzeroStab = (zeroStab/Qm) * (MF / 100) / math.sqrt(3)
    uTempMF = (0.001*(Tl-32)/1.8) * (MF / 100) / math.sqrt(3)
    uPresMF = (0.0005*Pl) * (MF / 100) / math.sqrt(3)
    uViscMF = uvisc * (MF / 100) / math.sqrt(3)

    componentes_MF = {
        'cal':        ucalMF,         # Calibración
        'err':        uerrMF,         # Error sistemático no corregido
        'carta':      ucartaMF,       # Carta de control
        'zero':       uzeroStab,      # Estabilidad en cero
        'Temp':       uTempMF,        # Efecto de temperatura
        'Pres':       uPresMF,        # Efecto de presión
        'Visc':       uViscMF         # Efecto de viscosidad
    }

    # Grados de libertad 
    grados_libertad_MF = {
        'cal':        200,      # Calibración
        'err':        50,       # Error sistemático no corregido
        'carta':      200,      # Carta de control
        'zero':       50,       # Estabilidad en cero
        'Temp':       50,       # Efecto de temperatura
        'Pres':       50,       # Efecto de presión
        'Visc':       50        # Efecto de viscosidad
    }
    # Combinación cuadrática y grados de libertad efectivos
    uMF, v_MF = combinar_incertidumbre_dict(componentes_MF, grados_libertad_MF)
    data["uMF"], data["v_MF"] = uMF,  v_MF

    if data.get("MF") == None: data["MF"] = 1
    
    # ======================================================
    # --- 2. DENSIDAD ---
    # ======================================================
    # Extracción
    metdl    = data.get("metdl", "Directa con Densímetros")
    tipdens  = data.get("tipdens", "Tipo Coriolis")
    desvdens = data.get("desvdens", 0)
    ucalDens = data.get("ucalDens", 0)
    kcalDens = data.get("kcalDens", 2)

    ucal_dl = (ucalDens) / kcalDens

    if metdl == "Directa con Densímetros":
        uvis_efec_dl = desvdens
        if tipdens == "Tipo Coriolis":
            uP_efec_dl = 0.0031 * Pl
            uT_efec_dl = 0.005 * Tl
        elif tipdens == "Tipo Tubo Vibrante":
            uP_efec_dl = 0.0065 * Pl
            uT_efec_dl = 0.09 * Tl
        elif tipdens == "Tipo Diente de horquilla de inserción":
            uP_efec_dl = 0.0
            uT_efec_dl = 0.18 * Tl
    else:
        uP_efec_dl   = 0
        uT_efec_dl   = 0
        uvis_efec_dl = 0

    uP_efec_dl   = uP_efec_dl / math.sqrt(3)
    uT_efec_dl   = uT_efec_dl / math.sqrt(3)
    uvis_efec_dl = uvis_efec_dl / math.sqrt(3)

    componentes_dl = {
        'cal_tip':     ucal_dl,          # calibración típica
        'P_efec':      uP_efec_dl,       # efecto de presión
        'T_efec':      uT_efec_dl,       # efecto de temperatura
        'vis_efec':    uvis_efec_dl,     # efecto de viscosidad
    }
 
    grados_libertad_dl = {
        'cal_tip':     50,               # calibración típica
        'P_efec':      50,               # efecto de presión
        'T_efec':      50,               # efecto de temperatura
        'vis_efec':    50,               # efecto de viscosidad
    }

    # Combinación cuadrática y grados de libertad efectivos
    data["udl"], data["v_dl"] = combinar_incertidumbre_dict(componentes_dl, grados_libertad_dl)        

    # ====================================================================
    # --- Asignación al diccionario final (Contribuciones individuales)---
    # ====================================================================
    ucaracteristicas_dl = uP_efec_dl + uT_efec_dl + uvis_efec_dl
    ucaracteristicas_MF = uTempMF + uPresMF + uViscMF

    contribuciones_sub.update({
    'Densidad': {'Calibración': ucal_dl, 'Presión': uP_efec_dl, 'Temperatura': uT_efec_dl, 'Viscosidad': uvis_efec_dl},
    'MF': {'Calibración': ucalMF, 'Error': uerrMF, 'Carta de Control': ucartaMF, 'Zero': uzeroStab, 'Temperatura': uTempMF, 'Presión': uPresMF, 'Viscosidad': uViscMF},
    }) #hasta aqui solo van las incertidumbres individuales, falta multiplicar por el coeficiente de sensibilidad. 

    return data, contribuciones_sub


# intento usar scipy si está disponible para obtener t-quantile exacto
try:
    from scipy.stats import t as t_dist
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

def _t_quantile(alpha, df):
    """
    Devuelve t_{1-alpha, df}. Si scipy está disponible usa scipy.stats.t.ppf,
    si no y df es grande usa aproximación normal (z) y si df es pequeño devuelve z.
    alpha: cola superior (ej. 0.975 para 95% conf.)
    df: grados de libertad (float, puede ser np.inf)
    """
    if df is None or (df == np.inf):
        # normal approx
        return _z_quantile(alpha)
    if SCIPY_AVAILABLE:
        return t_dist.ppf(alpha, df)
    else:
        # fallback: si df > 1000, usar normal; si df moderate usar normal como aproximación
        # aviso: aproximación para entornos sin scipy
        return _z_quantile(alpha)

def _z_quantile(alpha):
    """Cuantil de la Normal estándar (inversa CDF) para probabilidad alpha."""
    return math.sqrt(2) * math.erf_inv(2*alpha - 1) if hasattr(math, "erf_inv") else _approx_z(alpha)

def _approx_z(alpha):
    """Aproximación simple al cuantil normal usando math.erf inverso aproximado."""
    # Si math.erf_inv no está disponible, usar una aproximación muy simple via inverse erfinv series.
    # Para la mayoría de entornos modernos math.erf_inv está disponible; si no, usar 1.96 como fallback.
    # (Esto sólo ocurre en entornos muy limitados.)
    if alpha == 0.975:
        return 1.95996398454005
    if alpha == 0.995:
        return 2.57582930354890
    # fallback grosero:
    return 1.96

# Si math.erf_inv no existe (viejas versiones de python), intentar importarla:
if not hasattr(math, "erf_inv"):
    try:
        from math import erfinv as _erfinv
        math.erf_inv = _erfinv  # monkey-patch para usar en _z_quantile
    except Exception:
        pass


def GUM(data, variables=None, alpha=0.05):
    """
    GUM: cálculo de incertidumbre por propagación lineal, con cálculo de grados
    de libertad efectivos (Welch-Satterthwaite) y cálculo del factor k como
    t_{1-alpha/2, nu_eff}.

    Parámetros:
        data: dict con entradas necesarias por calcular_volumen y además:
              - para cada variable x que se incluya en 'variables' debe existir:
                u{x} -> incertidumbre estándar de x
                v{x} -> grados de libertad asociados (opcional)
        variables: lista de nombres de variables a considerar (por defecto ["MF","dl"])
        alpha: nivel de significancia (0.05 -> confianza 95%)

    Retorna:
        diccionario con:
            NSV_nominal, u_c, Uexp, k, k_df (nu_eff), sensitivities, contribuciones, info_warning
    """
    if variables is None:
        variables = ["MF", "dl"]

    info_warnings = []

    data, contribuciones_gum = GUM_secundario(data)

    # 1) modelo nominal
    y0_dict = calcular_volumen(data)    
    y0 = y0_dict.get("NSV", None)
    m0 = y0_dict.get("Masa_Corregida", 0)
    if y0 is None:
        raise ValueError("No se pudo obtener NSV del modelo base.")

    # 2) sensibilidades numéricas
    sensitivities = {}
    for var in variables:
        if var not in data:
            sensitivities[var] = 0.0
            continue

        x0 = data[var]
        uxi = data.get(f"u{var}", None)
        if uxi is None or uxi == 0:
            sensitivities[var] = 0.0
            continue

        delta = abs(uxi)
        data_plus = deepcopy(data)
        data_minus = deepcopy(data)
        data_plus[var] = x0 + delta
        data_minus[var] = x0 - delta

        y_plus = calcular_volumen(data_plus).get("NSV", 0.0)
        y_minus = calcular_volumen(data_minus).get("NSV", 0.0)

        ci = (y_plus - y_minus) / (2.0 * delta)
        sensitivities[var] = ci

    # 3) propagación lineal y contribuciones
    uc2 = 0.0
    contribs = {}
    for var in variables:
        uvar = data.get(f"u{var}", None)
        if uvar is None:
            continue
        ci = sensitivities.get(var, 0.0)
        term_sq = (ci * uvar) ** 2
        uc2 += term_sq

        # grados de libertad asociados a esta incertidumbre (si existen)
        v_var = data.get(f"v{var}", None)  # puede ser None (interpreta como infinito)
        contribs[var] = {
            "ci": ci,
            "uvar": uvar,
            "contrib_abs": math.sqrt(term_sq),
            "contrib_sq": term_sq,
            "v_var": v_var
        }

    uc = math.sqrt(uc2) if uc2 > 0 else 0.0

    # ➤ Añadir contribución porcentual (una vez se conoce uc2)
    for var, info in contribs.items():
        if uc2 > 0:
            info["contrib_%"] = (info["contrib_sq"] / uc2) * 100
        else:
            info["contrib_%"] = 0.0

    # 4) Welch-Satterthwaite para grados de libertad efectivos
    # nu_eff = (uc^4) / sum( ( (ci*u_i)^4 / v_i ) )
    denom = 0.0
    for var, info in contribs.items():
        v_i = info.get("v_var", None)
        term_sq = info.get("contrib_sq", 0.0)
        if term_sq == 0:
            continue
        if v_i is None or v_i == 0 or v_i == float("inf"):
            # si v_i es None o infinito, su contribución al denominador es 0
            continue
        # proteger v_i <= 0
        if v_i <= 0:
            info_warnings.append(f"v{var} tiene valor no positivo ({v_i}); se ignora en denom.")
            continue
        denom += (term_sq ** 2) / v_i  # (ci*u_i)^4 / v_i

    if denom == 0.0:
        nu_eff = float("inf")
    else:
        nu_eff = (uc2 ** 2) / denom  # (uc^4)/(sum ...)


    # 5) Contribuciones detalladas (subcomponentes)
    contribuciones_sub = contribuciones_gum

    # Coeficientes de sensibilidad (obtenidos en el paso 2)
    c_dens = sensitivities.get('dl', 0)
    c_MF = sensitivities.get('MF', 0)

    # Diccionarios para resultados
    contribuciones_net = {}
    contribuciones_rel = {}

    for grupo, subvars in contribuciones_sub.items():
        contribuciones_net[grupo] = {}
        contribuciones_rel[grupo] = {}

        for sub, u in subvars.items():
            # 1️⃣ Multiplicación por coeficiente de sensibilidad
            c = c_dens if grupo == 'Densidad' else c_MF
            u_net = c * u
            contribuciones_net[grupo][sub] = u_net

            # 2️⃣ Contribución relativa
            if uc2 != 0:
                contrib_rel = ((u_net) ** 2 / (uc2)) * 100
            else:
                contrib_rel = 0

            contribuciones_rel[grupo][sub] = contrib_rel


    # 6) calcular k como t_{1-alpha/2, nu_eff}
    alpha_tail = 1 - alpha / 2.0  # ejemplo: 0.975 para alpha=0.05
    if nu_eff == float("inf"):
        k = _t_quantile(alpha_tail, np.inf)
    else:
        k = _t_quantile(alpha_tail, nu_eff)

    # 7) incertidumbre expandida
    Uexp = k * uc
    Urel = Uexp/y0 *100

    # 8) gráfico de contribuciones (opcional)
          
    #main_sources = ['MF', 'Densidad']
    #subsources = contribuciones_rel
    #df_heatmap = generar_heatmap_incertidumbre(subsources, main_sources)
    
    # 9) Output de contribuciones principales

    uMF = data.get("uMF")      # U estándar combinada MF
    udl = data.get("udl")      # U estándar combinada dl, kg/m³

    cMF = uMF * c_MF           # contribución MF, bbl
    cdl = udl * c_dens         # contribución dl, bbl

    crMF = cMF**2 / uc2  *100     # contribución relativa MF, %
    crdl = cdl**2 / uc2  *100     # contribución relativa dl, %

    # 8) output
    return {
        "NSV": f"{y0:.2f}", 
        "masa": f"{m0:.2f}",
        "U":  f"{uc:.2f}",
        "Uexp": f"{Uexp:.2f}",
        "k":   f"{k:.2f}",
        "Urel": f"{Urel:.2f}",
        "uMF": f"{uMF:.6f}",
        "udl": f"{udl:.6f}",
        "cMF": f"{cMF:.6f}",
        "cdl": f"{cdl:.6f}",
        "crMF": f"{crMF:.6f}",
        "crdl": f"{crdl:.6f}"
    }
   