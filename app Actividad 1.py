import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard Producción Industrial",
    layout="wide"
)

st.title("Dashboard de Producción Industrial")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("produccion_planta.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

produccion = cargar_datos()

st.sidebar.header("Filtros")

lineas = st.sidebar.multiselect(
    "Seleccione línea(s)",
    options=produccion["linea"].unique(),
    default=produccion["linea"].unique()
)

turnos = st.sidebar.multiselect(
    "Seleccione turno(s)",
    options=produccion["turno"].unique(),
    default=produccion["turno"].unique()
)

# Aplicar filtros
filtro = produccion[
    (produccion["linea"].isin(lineas)) &
    (produccion["turno"].isin(turnos))
]

produccion_total = filtro["unidades_producidas"].sum()

tasa_defectos = (
    filtro["unidades_defectuosas"].sum() /
    filtro["unidades_producidas"].sum()
) * 100

tiempo_promedio = filtro["tiempo_operacion_min"].mean()

productividad = (
    filtro["unidades_producidas"].sum() /
    filtro["tiempo_operacion_min"].sum()
)

st.subheader("Indicadores principales")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Producción Total",
    f"{int(produccion_total)} unidades"
)

col2.metric(
    "Tasa de Defectos",
    f"{tasa_defectos:.2f}%"
)

col3.metric(
    "Tiempo Promedio",
    f"{tiempo_promedio:.2f} min"
)

col4.metric(
    "Productividad/min",
    f"{productividad:.2f}"
)

st.subheader("Producción a través del tiempo")

produccion_fecha = (
    filtro.groupby("fecha")["unidades_producidas"]
    .sum()
    .reset_index()
)

fig = px.line(
    produccion_fecha,
    x="fecha",
    y="unidades_producidas",
    markers=True,
    title="Unidades producidas por fecha"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Tasa de defectos por línea")

defectos_linea = (
    filtro.groupby("linea")[[
        "unidades_producidas",
        "unidades_defectuosas"
    ]]
    .sum()
)

defectos_linea["tasa_defectos"] = (
    defectos_linea["unidades_defectuosas"] /
    defectos_linea["unidades_producidas"]
) * 100

fig2, ax = plt.subplots(figsize=(8, 4))

ax.bar(
    defectos_linea.index,
    defectos_linea["tasa_defectos"]
)

ax.set_title("Tasa de defectos por línea")
ax.set_ylabel("Porcentaje (%)")
ax.set_xlabel("Línea")

st.pyplot(fig2)

st.subheader("Datos filtrados")

st.dataframe(filtro)