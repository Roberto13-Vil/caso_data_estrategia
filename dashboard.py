import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_parquet('Data/cleaned.parquet')

# ========== Configuracion ============

st.set_page_config(page_title='Dashboard', layout='wide', page_icon="📊")
st.title('Dashboard de Caso y Estrategia')
st.markdown("""
Este dashboard presenta un analisis de los datos relacionados con el caso Data y Estrategia.
            """)

# ========== Estilos ============

page_bg = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #e9d8a6;
    color: #001219;
    font-family: 'Segoe UI', sans-serif;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ========== Cargar datos ============

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']
df = load_data()
df['Mes'] = pd.Categorical(
    df['Mes'],
    categories=meses,
    ordered=True
)

# ========== Filtro de Análisis ============

analisis = ['Análisis de ventas por categoría', 'Análisis de Asesores', 'Análisis de cliente vs publicidad']
st.sidebar.title('🧭 Menú de análisis')
section = st.sidebar.radio('Selecciona:', analisis)

# Paletas de color
colores_capacitacion = {
    'Sí': '#31572c',
    'No': '#90a955',
    'Desconocido': '#ecf39e'
}
colores_base = ['#31572c', '#4f772d', '#90a955', '#ecf39e', '#fefae0']

# ===================== 1️⃣ Análisis de ventas =====================
if section == 'Análisis de ventas por categoría':
    zonas_disponibles = sorted(df['Zona'].unique())
    zonas_select = st.multiselect('🏙️ Selecciona Zonas:', zonas_disponibles, default=zonas_disponibles)
    df_filtrado = df[df['Zona'].isin(zonas_select)]

    st.subheader("📌 Vista Global: Zonas vs Canales")
    df_radar = df_filtrado.groupby(['Zona', 'Canal'], as_index=False)['Monto de Venta'].sum()

    fig_radar = px.line_polar(
        df_radar, r='Monto de Venta', theta='Zona', color='Canal', line_close=True,
        template="plotly_dark", color_discrete_sequence=colores_base
    )
    st.plotly_chart(fig_radar)

    st.subheader("📦 Evolución de ventas por producto")
    col1, col2 = st.columns(2)
    zona_select = col1.selectbox("Zona:", sorted(df_filtrado['Zona'].unique()))
    canal_select = col2.selectbox("Canal:", sorted(df_filtrado['Canal'].unique()))

    df_linea = df_filtrado[(df_filtrado['Zona'] == zona_select) & (df_filtrado['Canal'] == canal_select)]
    df_linea = df_linea.groupby(['Mes', 'Producto'], as_index=False)['Monto de Venta'].sum()

    fig_linea = px.line(
        df_linea, x='Mes', y='Monto de Venta', color='Producto', markers=True,
        title=f"Evolución de ventas ({zona_select} - {canal_select})"
    )
    st.plotly_chart(fig_linea)

# ===================== 2️⃣ Análisis de Asesores =====================
elif section == 'Análisis de Asesores':
    st.subheader("🏆 Top 10 Asesores por Monto de Venta")
    df_top = (df.groupby('Asesor')['Monto de Venta']
              .sum()
              .reset_index()
              .sort_values('Monto de Venta', ascending=False)
              .head(10))

    fig1 = px.bar(
        df_top, x='Monto de Venta', y='Asesor', orientation='h',
        text='Monto de Venta', color_discrete_sequence=[colores_base[0]]
    )
    fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig1)

    st.subheader("📚 Comparación ventas: Capacitados vs No Capacitados")
    df_capacitado = df.groupby('¿Capacitado?')['Monto de Venta'].sum().reset_index()
    fig2 = px.bar(
        df_capacitado, x='¿Capacitado?', y='Monto de Venta',
        color='¿Capacitado?', color_discrete_map=colores_capacitacion
    )
    st.plotly_chart(fig2)

    df_filtrado = df[df['Monto de Venta'] >= 0]

    st.subheader("📈 Antigüedad vs Cumplimiento de Objetivos")
    fig3 = px.scatter(
        df_filtrado, x='Antigüedad del Asesor (meses)', y='% Cumplimiento Objetivo',
        color='¿Capacitado?', color_discrete_map=colores_capacitacion,
        size='Monto de Venta', hover_name='Asesor'
    )
    st.plotly_chart(fig3)

# ===================== 3️⃣ Cliente vs Publicidad =====================
elif section == 'Análisis de cliente vs publicidad':
    st.subheader("🎯 % Clientes Nuevos vs Inversión en Publicidad")

    df_filtrado = df[df['Monto de Venta'] >= 0]
    fig1 = px.scatter(
        df_filtrado, x="Inversión en Publicidad", y="% Clientes Nuevos",
        color="Participación en Campañas", size="Monto de Venta",
        hover_data=["Edad del Cliente", "Producto"],
        color_discrete_sequence=colores_base
    )
    st.plotly_chart(fig1)

    st.subheader("👥 Edad del Cliente vs Monto de Venta")
    fig2 = px.scatter(
        df, x="Edad del Cliente", y="Monto de Venta",
        color="Producto", size="% Clientes Nuevos",
        hover_data=["Inversión en Publicidad", "Participación en Campañas"],
        color_discrete_sequence=colores_base
    )
    st.plotly_chart(fig2)