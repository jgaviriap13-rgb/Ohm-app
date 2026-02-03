import streamlit as st
import math
from datetime import datetime

st.set_page_config(
    page_title="Ohm – Asistente Técnico",
    layout="wide"
)

# =========================================================
# DATOS (extraídos del código Gemini Canvas)
# =========================================================

DMD_TABLE = [
    {"users": 1, "e1_2": 1.35, "e3": 1.31, "e4": 1.46, "e5_6": 2.21, "rural": 0.96},
    {"users": 2, "e1_2": 1.19, "e3": 1.14, "e4": 1.30, "e5_6": 1.58, "rural": 0.87},
    {"users": 3, "e1_2": 1.09, "e3": 0.99, "e4": 1.15, "e5_6": 1.17, "rural": 0.80},
    {"users": 4, "e1_2": 1.02, "e3": 0.87, "e4": 1.02, "e5_6": 0.96, "rural": 0.77},
    {"users": 5, "e1_2": 0.97, "e3": 0.76, "e4": 0.91, "e5_6": 0.83, "rural": 0.74},
    {"users": 6, "e1_2": 0.92, "e3": 0.69, "e4": 0.82, "e5_6": 0.75, "rural": 0.72},
    {"users": 7, "e1_2": 0.89, "e3": 0.63, "e4": 0.75, "e5_6": 0.69, "rural": 0.71},
    {"users": 8, "e1_2": 0.86, "e3": 0.59, "e4": 0.69, "e5_6": 0.65, "rural": 0.69},
    {"users": 9, "e1_2": 0.83, "e3": 0.55, "e4": 0.65, "e5_6": 0.61, "rural": 0.67},
    {"users": 10, "e1_2": 0.81, "e3": 0.52, "e4": 0.62, "e5_6": 0.58, "rural": 0.66},
]

CONDUCTOR_AMPACITY = [
    {"gauge": "14", "amp60": 20, "amp75": 20},
    {"gauge": "12", "amp60": 25, "amp75": 25},
    {"gauge": "10", "amp60": 30, "amp75": 35},
    {"gauge": "8",  "amp60": 40, "amp75": 50},
    {"gauge": "6",  "amp60": 55, "amp75": 65},
    {"gauge": "4",  "amp60": 70, "amp75": 85},
    {"gauge": "2",  "amp60": 95, "amp75": 115},
    {"gauge": "1/0","amp60": 125,"amp75": 150},
    {"gauge": "2/0","amp60": 145,"amp75": 175},
    {"gauge": "3/0","amp60": 165,"amp75": 200},
    {"gauge": "4/0","amp60": 195,"amp75": 230},
    {"gauge": "250","amp60": 215,"amp75": 255},
]

CONDUCTOR_IMPEDANCE = {
    "14": {"r": 10.17, "x": 0.190},
    "12": {"r": 6.56,  "x": 0.177},
    "10": {"r": 3.94,  "x": 0.164},
    "8":  {"r": 2.56,  "x": 0.171},
    "6":  {"r": 1.61,  "x": 0.167},
    "4":  {"r": 1.02,  "x": 0.157},
    "2":  {"r": 0.656, "x": 0.148},
    "1/0":{"r": 0.427, "x": 0.144},
    "2/0":{"r": 0.328, "x": 0.141},
    "3/0":{"r": 0.253, "x": 0.138},
    "4/0":{"r": 0.206, "x": 0.135},
    "250":{"r": 0.160, "x": 0.130},
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚡ OHM")
view = st.sidebar.radio(
    "Módulo",
    ["Inicio", "Chat Normativo", "Acometidas", "HP → kW", "Nodos CHEC"]
)

# =========================================================
# INICIO
# =========================================================

if view == "Inicio":
    st.title("Bienvenido a OHM")
    st.write("""
    Asistente técnico para normativa eléctrica colombiana:
    **RETIE – NTC 2050 – CHEC**
    """)
    st.info("Esta herramienta apoya cálculos técnicos, no reemplaza un diseñador eléctrico.")

# =========================================================
# HP → KW
# =========================================================

if view == "HP → kW":
    st.header("Conversión de Potencia")
    hp = st.number_input("Potencia del motor (HP)", min_value=0.0, step=0.5)
    if st.button("Calcular"):
        st.success(f"{hp * 0.7457:.4f} kW")

# =========================================================
# NODOS CHEC
# =========================================================

if view == "Nodos CHEC":
    st.header("Codificación de Nodos – CHEC")
    tipo = st.radio("Tipo de red", ["Aérea", "Subterránea"])

    if tipo == "Aérea":
        material = st.selectbox("Material", ["T", "M", "P", "V"])
        longitud = st.text_input("Longitud (m)")
        resistencia = st.text_input("Resistencia (kg)")
        codigo = f"A{material}{longitud or '00'}{resistencia or '000'}"
    else:
        tension = st.selectbox("Nivel de tensión", ["1", "2", "3"])
        conexion = st.selectbox("Tipo de conexión", ["O", "T", "C", "N"])
        fases = st.selectbox("Fases", ["1", "2", "3"])
        codigo = f"ES{tension}{conexion}{'1' if fases=='3' else '0'}{fases}"

    st.success(f"Código generado: **{codigo}**")

# =========================================================
# ACOMETIDAS
# =========================================================

if view == "Acometidas":
    st.header("Cálculo de Acometidas Residenciales")

    usuarios = st.number_input("Número de usuarios", min_value=1, step=1)
    estrato = st.selectbox("Estrato", ["1-2", "3", "4", "5-6", "Rural"])
    red = st.selectbox("Tipo de red", ["Monofásica", "Trifásica"])
    longitud = st.number_input("Longitud (m)", min_value=1.0)

    if st.button("Calcular acometida"):
        key = "rural" if estrato == "Rural" else \
              "e1_2" if estrato == "1-2" else \
              "e3" if estrato == "3" else \
              "e4" if estrato == "4" else "e5_6"

        fila = next((f for f in DMD_TABLE if f["users"] == min(usuarios, 10)), DMD_TABLE[-1])
        kva_total = fila[key] * usuarios

        if red == "Trifásica":
            corriente = (kva_total * 1000) / 360.24
            k = math.sqrt(3)
            vbase = 208
        else:
            corriente = (kva_total * 1000) / 120
            k = 2
            vbase = 120

        conductor_final = None
        regulacion = 100

        for c in CONDUCTOR_AMPACITY:
            imp = CONDUCTOR_IMPEDANCE[c["gauge"]]
            dv = k * corriente * (imp["r"] * 0.9 + imp["x"] * 0.4359) * (longitud / 1000)
            regulacion = (dv / vbase) * 100
            if c["amp60"] >= corriente and regulacion <= 3:
                conductor_final = c["gauge"]
                break

        if conductor_final:
            st.success("Cumple normativa")
            st.write(f"**Carga total:** {kva_total:.2f} kVA")
            st.write(f"**Corriente:** {corriente:.2f} A")
            st.write(f"**Conductor:** {conductor_final}")
            st.write(f"**Regulación:** {regulacion:.2f}%")
        else:
            st.error("No cumple con calibres estándar")

# =========================================================
# CHAT SIMULADO
# =========================================================

if view == "Chat Normativo":
    st.header("Asistente Normativo")

    if "chat" not in st.session_state:
        st.session_state.chat = [
            ("Ohm", "Hola, puedo ayudarte con RETIE, NTC 2050 y CHEC.")
        ]

    pregunta = st.text_input("Escribe tu consulta")

    if st.button("Enviar"):
        st.session_state.chat.append(("Tú", pregunta.lower()))

        if "tierra" in pregunta.lower():
            respuesta = "RETIE Art. 15: el sistema de puesta a tierra es obligatorio."
        elif "color" in pregunta.lower():
            respuesta = "Fases: amarillo, azul, rojo. Neutro: blanco. Tierra: verde."
        elif "baño" in pregunta.lower():
            respuesta = "NTC 2050 exige GFCI en tomacorrientes de baño."
        else:
            respuesta = "Consulta recibida. Sé más específica para aplicar normativa."

        st.session_state.chat.append(("Ohm", respuesta))

    for autor, msg in st.session_state.chat:
        st.write(f"**{autor}:** {msg}")
