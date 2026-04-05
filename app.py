import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Calculadora Didáctica de Bonos", layout="wide")

st.title("🎓 Calculadora Didáctica de Bonos y Renta Fija")
st.markdown("""
Esta herramienta permite entender la relación entre el **Precio**, la **TIR (YTM)** y el **Cupón**. 
*Modifica los parámetros en la barra lateral y observa cómo cambian los flujos y el valor presente.*
""")

# --- BARRA LATERAL (INPUTS EDITABLES) ---
st.sidebar.header("⚙️ Parámetros del Bono")
face_value = st.sidebar.number_input("Valor Nominal ($)", value=1000.0, step=100.0)
coupon_rate = st.sidebar.slider("Tasa de Cupón Anual (%)", 0.0, 20.0, 5.0, 0.5) / 100
years = st.sidebar.slider("Años al Vencimiento", 1, 30, 5)
ytm = st.sidebar.slider("TIR / YTM Buscada (%)", 0.1, 20.0, 6.0, 0.1) / 100
frequency = st.sidebar.selectbox("Frecuencia de Pago", ["Anual", "Semestral", "Trimestral"])

freq_map = {"Anual": 1, "Semestral": 2, "Trimestral": 4}
n_periods = years * freq_map[frequency]
coupon_payment = (face_value * coupon_rate) / freq_map[frequency]
period_rate = ytm / freq_map[frequency]

# --- MOTOR DE CÁLCULO PASO A PASO ---
st.subheader("1. Desglose de Flujos de Fondos (Cash Flow)")
st.write("Aquí vemos cuánto dinero recibes en cada periodo y cuánto vale ese dinero *hoy* (Valor Presente).")

cash_flows = []
for t in range(1, n_periods + 1):
    payment = coupon_payment
    if t == n_periods:
        payment += face_value
    
    # Cálculo del Valor Presente (VP)
    pv = payment / ((1 + period_rate) ** t)
    cash_flows.append({"Periodo": t, "Flujo Nominal": payment, "Valor Presente": pv})

df_flows = pd.DataFrame(cash_flows)
st.table(df_flows.style.format({"Flujo Nominal": "${:.2f}", "Valor Presente": "${:.2f}"}))

# --- CÁLCULO DEL PRECIO FINAL ---
bond_price = df_flows["Valor Presente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Precio Teórico del Bono", f"${bond_price:.2f}")
col2.metric("Estado", "Sobre la Par" if bond_price > face_value else "Bajo la Par" if bond_price < face_value else "A la Par")
col3.metric("TIR Actual", f"{ytm*100:.2f}%")

# --- ANÁLISIS DIDÁCTICO (SENSIBILIDAD) ---
st.subheader("2. Análisis de Sensibilidad (Precio vs TIR)")
st.write("Observa cómo el precio cae cuando la TIR sube. Esta es la relación inversa fundamental de los bonos.")

# Generar datos para la curva
ytm_range = np.linspace(0.01, 0.20, 50)
prices = []

for r in ytm_range:
    p = sum([(coupon_payment + (face_value if t == n_periods else 0)) / ((1 + r/freq_map[frequency])**t) for t in range(1, n_periods + 1)])
    prices.append(p)

fig = go.Figure()
fig.add_trace(go.Scatter(x=ytm_range*100, y=prices, mode='lines', name='Curva de Precio', line=dict(color='royalblue', width=3)))
fig.add_trace(go.Scatter(x=[ytm*100], y=[bond_price], mode='markers', name='Tu Punto Actual', marker=dict(color='red', size=12)))

fig.update_layout(
    xaxis_title="TIR (%)",
    yaxis_title="Precio del Bono ($)",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 **Lección rápida:** Si el mercado empieza a exigir una TIR más alta que el {ytm*100:.2f}%, el precio de tu bono bajará para compensar el rendimiento.")
