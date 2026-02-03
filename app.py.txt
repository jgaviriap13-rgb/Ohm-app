import streamlit as st
import math

st.set_page_config(page_title="OHM – Asistente Eléctrico", layout="wide")

# ======================
# DATOS NORMATIVOS
# ======================
CONDUCTOR_DATA = [
    {"awg": "14", "amp_60": 20, "amp_75": 20, "r": 10.17, "x": 0.190},
    {"awg": "12", "amp_60": 25, "amp_75": 25, "r": 6.56, "x": 0.177},
    {"awg": "10", "amp_60": 30, "amp_75": 35, "r": 3.94, "x": 0.164},
    {"awg": "8",  "amp_60": 40, "amp_75": 50, "r": 2.56, "x": 0.171},
    {"awg": "6",  "amp_60": 55, "amp_75": 65, "r": 1.61, "x": 0.167},
    {"awg": "4",  "amp_60": 70, "amp_75": 85, "r": 1.02, "x": 0.157},
]

# ======================
# FUNCIONES
# ======================
def hp_to_kw(hp):
    return hp * 0.7457

def calcular_regulacion(I, L_m, conductor, tipo):
    cosphi = 0.9
    sinphi = math.sin(math.acos(cosphi))
    L_km = L_m / 1000
    Z = conductor["r"] * cosphi + conductor["x"] * sinphi

    if tipo == "Monofásica":
        delta_v = 2 * L_km * I * Z
        v_base = 120
    else:
        delta_v = math.sqrt(3) * L_km * I * Z
        v_base = 208

    return (delta_v / v_base) * 100

# ======================
# SIDEBAR
# ======================
st.sidebar.title("⚡ OHM")
menu = st.sidebar.radio(
    "Herramientas",
    ["Asistente", "Motores", "Acometidas", "Ductos"]
)

# ======================
# MOTORES
# ======================
if menu == "Motores":
    st.header("🔁 Conversión HP → kW")

    hp = st.number_input("Potencia del motor (HP)", min_value=0.0, step=0.5)
    if st.button("Calcular"):
        st.success(f"{hp_to_kw(hp):.3f} kW")

# ======================
# ACOMETIDAS
# ======================
if menu == "Acometidas":
    st.header("🏠 Cálculo de Acometidas (NTC 2050 / CHEC)")

    corriente = st.number_input("Corriente estimada (A)", min_value=1.0)
    longitud = st.number_input("Longitud de acometida (m)", min_value=1.0)
    tipo = st.selectbox("Tipo de red", ["Monofásica", "Trifásica"])

    if st.button("Dimensionar"):
        temp_col = "amp_60" if corriente < 100 else "amp_75"

        for c in CONDUCTOR_DATA:
            if c[temp_col] >= corriente:
                reg = calcular_regulacion(corriente, longitud, c, tipo)
                if reg <= 3:
                    st.success(f"""
                    ✔ Conductor: {c['awg']} AWG  
                    ✔ Regulación: {reg:.2f}%  
                    ✔ Cumple RETIE
                    """)
                    break
        else:
            st.error("❌ No cumple regulación con calibres estándar")

# ======================
# DUCTOS
# ======================
if menu == "Ductos":
    st.header("📦 Ocupación de Ductos (40%)")

    awg = st.selectbox("Calibre", ["14", "12", "10", "8", "6", "4"])
    cantidad = st.number_input("Cantidad de conductores", min_value=1)

    diam = {"14":3.4,"12":3.9,"10":4.5,"8":5.9,"6":7.6,"4":8.8}
    area = math.pi * (diam[awg]/2)**2 * cantidad

    ductos = {"1/2\"":150,"3/4\"":270,"1\"":450}

    for d, a in ductos.items():
        if area <= a * 0.4:
            st.success(f"Ducto recomendado: {d}")
            break
