import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Cripto App - Final Project", layout="wide")

# 2. Función optimizada para cargar datos
@st.cache_data
def load_data():
    path = "data/master_FINAL.parquet"
    return pd.read_parquet(path)

# Intentar cargar los datos
try:
    df = load_data()
    
    # --- BARRA LATERAL PARA FILTROS ---
    st.sidebar.header("🔍 Filtros de Exploración")

    # 1. Filtro por Rango de Fechas
    df['solo_fecha'] = pd.to_datetime(df['fecha_hora']).dt.date
    min_fecha = df['solo_fecha'].min()
    max_fecha = df['solo_fecha'].max()

    st.sidebar.subheader("Calendario")
    rango_fechas = st.sidebar.date_input(
        "Selecciona un rango:",
        value=(min_fecha, max_fecha),
        min_value=min_fecha,
        max_value=max_fecha
    )


    # 2. Filtro por Activo
    activos_disponibles = df['activo'].unique()
    seleccion_activos = st.sidebar.multiselect(
        "Selecciona Criptoactivos:",
        options=activos_disponibles,
        default=activos_disponibles
    )

    # 3. Filtro por Procedencia
    origenes = df['procedencia'].unique()
    seleccion_origen = st.sidebar.multiselect(
        "Fuente de los datos:",
        options=origenes,
        default=origenes
    )

    # 4. Filtro por Nivel de Impacto
    impacto_minimo = st.sidebar.slider(
        "Nivel de Impacto Mínimo:",
        min_value=int(df['nivel_impacto'].min()),
        max_value=int(df['nivel_impacto'].max()),
        value=int(df['nivel_impacto'].min())
    )

    # --- APLICACIÓN DE LA LÓGICA DE FILTRADO  ---
    # Primero filtramos por fecha
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        inicio, fin = rango_fechas
        mask_fecha = (df['solo_fecha'] >= inicio) & (df['solo_fecha'] <= fin)
    else:
        mask_fecha = True

    # Aplicamos todos los filtros al mismo tiempo sobre el DF original
    df_filtrado = df[
        mask_fecha & 
        (df['activo'].isin(seleccion_activos)) & 
        (df['procedencia'].isin(seleccion_origen)) &
        (df['nivel_impacto'] >= impacto_minimo)
    ].copy()

    # 3. Encabezado de la App
    st.title("📊 Observatorio Cripto: Análisis de Datos")
    st.markdown("""
    Esta aplicación permite visualizar el impacto de las noticias en los precios de criptoactivos, 
    utilizando datos procesados y optimizados en formato Parquet.
    """)

    # 4. Mostrar métricas rápidas (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registros", f"{len(df_filtrado):,}")
    with col2:
        st.metric("Criptoactivos", df_filtrado['activo'].nunique() if not df_filtrado.empty else 0)
    with col3:
        if len(df_filtrado) > 0:
            outliers_pct = (df_filtrado['es_outlier'].sum() / len(df_filtrado)) * 100
        else:
            outliers_pct = 0
        st.metric("Anomalías en Selección", f"{outliers_pct:.2f}%")

    # 5. Vista previa de los datos
    with st.expander("Ver tabla de datos maestros"):
        st.dataframe(df_filtrado.head(100), use_container_width=True)

    # 6. Organización por Secciones (Pestañas)
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📈 Tendencias Temporales", "📊 Distribuciones", "🔍 Análisis de Impacto"])

    with tab1:
        st.subheader("Evolución de Precios y Volumen")
        fig_linea = px.line(
            df_filtrado, 
            x='fecha_hora', 
            y='precio_usd', 
            color='activo',
            hover_data=['tipo_evento', 'procedencia'],
            title="Precio USD en el Tiempo",
            template="plotly_dark"
        )
        st.plotly_chart(fig_linea, use_container_width=True)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Distribución de Precios")
            fig_hist = px.histogram(
                df_filtrado,
                x="precio_usd",
                color="activo",
                marginal="box", # Añade un diagrama de caja arriba
                title="Frecuencia de Precios por Activo",
                template="plotly_dark"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_b:
            st.subheader("Anomalías de Volumen")
            fig_scatter = px.scatter(
                df_filtrado, 
                x='precio_usd_norm', 
                y='volumen_24h_norm', 
                color='es_outlier',
                symbol='activo',
                title="Dispersión: Precio vs Volumen (Normalizado)",
                template="plotly_dark"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        st.subheader("Impacto de Noticias por Activo")
        # Calculamos el promedio de impacto por activo para este gráfico
        df_impacto = df_filtrado.groupby('activo')['nivel_impacto'].mean().reset_index()
        
        fig_bar = px.bar(
            df_impacto,
            x='activo',
            y='nivel_impacto',
            color='activo',
            title="Promedio de Nivel de Impacto por Criptoactivo",
            labels={'nivel_impacto': 'Impacto Promedio'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Treemap para ver la proporción de datos por procedencia
        st.subheader("Composición por Fuente de Datos")
        fig_tree = px.treemap(
            df_filtrado, 
            path=['procedencia', 'activo'], 
            values='precio_usd',
            title="Jerarquía: Procedencia -> Activo",
            template="plotly_dark"
        )
        st.plotly_chart(fig_tree, use_container_width=True)

except Exception as e:
    st.error(f"Error en la aplicación: {e}")
    st.info("Revisa que el archivo Parquet esté en la carpeta 'data'.")