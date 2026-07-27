"""
Interfaz web simple (Streamlit) para interactuar con el agente de
Mercado Central 24h.

Ejecutar con:
    streamlit run src/app.py
"""
import streamlit as st

from src.agent import preguntar

st.set_page_config(page_title="Asistente Mercado Central 24h", page_icon="🛒")
st.title("🛒 Asistente Inteligente — Mercado Central 24h")
st.caption(
    "Pregúntame sobre políticas de la empresa (devoluciones, reglamento, "
    "proveedores) o sobre el inventario de productos (stock, precio, ubicación)."
)

if "historial" not in st.session_state:
    st.session_state.historial = []

for rol, mensaje in st.session_state.historial:
    with st.chat_message(rol):
        st.markdown(mensaje)

pregunta = st.chat_input("Escribe tu pregunta...")
if pregunta:
    st.session_state.historial.append(("user", pregunta))
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            respuesta = preguntar(pregunta)
        st.markdown(respuesta)
    st.session_state.historial.append(("assistant", respuesta))
