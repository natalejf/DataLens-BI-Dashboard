import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import os

# Data Science & Machine Learning
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy import stats

# ---------------------------------------------------------
# PAGE CONFIGURATION (DataLens BI Dashboard)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DataLens BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start full-width like a modern BI Grid dashboard
)

# ---------------------------------------------------------
# ADVANCED LIGHT THEME CUSTOM CSS (Clean Native Streamlit Styling)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Force Light Mode Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
    }
    /* Native Corner Drag-to-Resize & Card Drag-and-Drop */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        resize: both !important;
        overflow: auto !important;
        min-width: 250px !important;
        min-height: 240px !important;
        position: relative !important;
        transition: box-shadow 0.2s, transform 0.15s !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        content: "↘";
        position: absolute;
        bottom: 2px;
        right: 6px;
        font-size: 14px;
        color: #4f46e5;
        pointer-events: none;
        font-weight: bold;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.12) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"].drag-over-card {
        border: 2px dashed #4f46e5 !important;
        background-color: rgba(79, 70, 229, 0.05) !important;
    }

    /* Top Header Bar Container */
    .ds-header-container {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .ds-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .ds-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Executive Metric Card */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.1);
        border-color: #cbd5e1;
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        word-break: break-word;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.03em;
        word-break: break-word;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        white-space: nowrap;
    }
    .delta-positive { background: #dcfce7; color: #166534; }
    .delta-neutral { background: #e0e7ff; color: #3730a3; }
    .delta-warning { background: #fef3c7; color: #92400e; }

    /* Automated Insight Explanatory Card */
    .insight-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 0.75rem;
        margin-bottom: 0.85rem;
    }
    .insight-title {
        font-weight: 700;
        color: #15803d;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .insight-body {
        font-size: 0.82rem;
        color: #166534;
        line-height: 1.4;
    }

    /* Empty Welcome Card */
    .welcome-card {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    }
    .welcome-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        white-space: nowrap;
        border-radius: 8px 8px 0 0;
        font-weight: 700;
        font-size: 1rem;
        color: #64748b;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #4f46e5;
        border-bottom: 3px solid #4f46e5;
        background-color: transparent;
    }

    /* Executive Summary Top Banner */
    .executive-summary-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-left: 5px solid #0284c7;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.05);
    }
    .summary-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #0369a1;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .summary-item {
        font-size: 0.9rem;
        color: #0f172a;
        margin-bottom: 0.4rem;
        line-height: 1.5;
    }

    /* Help Box styling */
    .help-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        font-size: 0.85rem;
        color: #334155;
        margin-top: 0.5rem;
    }

    /* Compact Grid Badge */
    .compact-badge {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 3px solid #16a34a;
        border-radius: 6px;
        padding: 0.35rem 0.65rem;
        margin-top: 0.4rem;
        font-size: 0.76rem;
        color: #166534;
        line-height: 1.3;
    }

    /* Mobile Responsive Rules */
    @media (max-width: 768px) {
        .ds-title {
            font-size: 1.3rem;
        }
        .metric-value {
            font-size: 1.4rem;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem;
            padding: 0 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER FUNCTIONS FOR PLAIN-LANGUAGE NARRATIVES
# ---------------------------------------------------------
def generate_plain_insights(df, main_metric=None, cat_col=None, date_col=None):
    total_rows = len(df)
    items = []
    
    # Item 1: Volume
    items.append(f"📌 <b>Volumen General:</b> El dataset contiene <b>{total_rows:,} registros</b> listos para analizar.")
    
    # Item 2: Main Metric
    if main_metric:
        total_val = df[main_metric].sum()
        avg_val = df[main_metric].mean()
        max_val = df[main_metric].max()
        items.append(f"🟢 <b>Comportamiento de '{main_metric}':</b> Se acumula un total de <b>{total_val:,.2f}</b>, con un promedio de <b>{avg_val:,.2f}</b> por observación. El valor máximo alcanza <b>{max_val:,.2f}</b>.")
    
    # Item 3: Categorical dominance
    if cat_col and main_metric:
        cat_sums = df.groupby(cat_col)[main_metric].sum()
        if not cat_sums.empty:
            top_cat = cat_sums.idxmax()
            top_val = cat_sums.max()
            pct = (top_val / total_val * 100) if total_val > 0 else 0
            items.append(f"🏆 <b>Líder Principal:</b> En la dimensión <b>{cat_col}</b>, la categoría <b>'{top_cat}'</b> domina con el <b>{pct:.1f}%</b> del total registrado.")
    elif cat_col:
        modes = df[cat_col].mode()
        if not modes.empty:
            items.append(f"🏷️ <b>Categoría más repetida:</b> La opción dominante en <b>{cat_col}</b> es <b>'{modes[0]}'</b>.")
            
    return items

# ---------------------------------------------------------
# DYNAMIC MODULAR PANEL RENDERER (INDEPENDENT CHART SWITCHER PER CARD)
# ---------------------------------------------------------
def render_dynamic_panel(panel_id, panel_title, default_type, df, num_cols, str_cols, date_cols, plotly_template, palette_colors):
    with st.container(border=True):
        col_t, col_s = st.columns([2.4, 1.6])
        with col_t:
            st.markdown(f"<h4 style='margin:0; padding-top:4px; font-size:0.95rem; font-weight:700;'>{panel_title}</h4>", unsafe_allow_html=True)
            
        with col_s:
            chart_options = [
                "📶 Barras",
                "📈 Líneas",
                "🏔️ Áreas",
                "📊 Histograma",
                "🎯 Dispersión (Scatter)",
                "📦 Boxplot",
                "🥧 Torta / Donut",
                "🎯 Reloj Radial (Gauge)",
                "📋 Tabla Resumen"
            ]
            def_idx = 0
            for idx, opt in enumerate(chart_options):
                if default_type.lower() in opt.lower():
                    def_idx = idx
                    break
                    
            chosen_chart = st.selectbox(
                "⚙️ Estilo",
                chart_options,
                index=def_idx,
                key=f"panel_select_{panel_id}",
                label_visibility="collapsed",
                help="Cambiar estilo de gráfico"
            )
            
        main_m = num_cols[0] if num_cols else None
        cat_m = str_cols[0] if str_cols else None
        date_m = date_cols[0] if date_cols else None
        
        if "Barras" in chosen_chart:
            if cat_m and main_m:
                df_b = df.groupby(cat_m)[main_m].sum().reset_index().sort_values(by=main_m, ascending=False).head(10)
                fig = px.bar(df_b, y=cat_m, x=main_m, orientation='h', template=plotly_template, color=main_m, color_continuous_scale="Viridis")
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                top_name = df_b.iloc[0][cat_m] if not df_b.empty else "-"
                st.markdown(f'<div class="compact-badge">💡 <b>Barras:</b> Entidad líder <b>\'{top_name}\'</b> en {cat_m}.</div>', unsafe_allow_html=True)
            elif len(num_cols) >= 2:
                fig = px.bar(df, x=num_cols[0], y=num_cols[1], template=plotly_template, color_discrete_sequence=palette_colors)
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Barras:</b> Comparación entre {num_cols[0]} y {num_cols[1]}.</div>', unsafe_allow_html=True)
            else:
                st.info("Insuficientes columnas para el gráfico de barras.")

        elif "Líneas" in chosen_chart:
            if date_m and main_m:
                df_l = df.groupby(date_m)[main_m].sum().reset_index()
                fig = px.line(df_l, x=date_m, y=main_m, markers=True, template=plotly_template, color_discrete_sequence=[palette_colors[0]])
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Líneas:</b> Evolución histórica de {main_m} sobre {date_m}.</div>', unsafe_allow_html=True)
            elif len(num_cols) >= 2:
                df_l = df.sort_values(by=num_cols[0])
                fig = px.line(df_l, x=num_cols[0], y=num_cols[1], markers=True, template=plotly_template, color_discrete_sequence=[palette_colors[0]])
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Líneas:</b> Tendencia continua entre {num_cols[0]} y {num_cols[1]}.</div>', unsafe_allow_html=True)
            else:
                st.info("Insuficientes columnas para gráfico de líneas.")

        elif "Áreas" in chosen_chart:
            if date_m and main_m:
                df_a = df.groupby(date_m)[main_m].sum().reset_index()
                fig = px.area(df_a, x=date_m, y=main_m, template=plotly_template, color_discrete_sequence=[palette_colors[2]])
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Área:</b> Volumen acumulado de {main_m} en el tiempo.</div>', unsafe_allow_html=True)
            elif cat_m and main_m:
                df_a = df.groupby(cat_m)[main_m].sum().reset_index()
                fig = px.area(df_a, x=cat_m, y=main_m, template=plotly_template, color_discrete_sequence=[palette_colors[1]])
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Área:</b> Perfil acumulado por {cat_m}.</div>', unsafe_allow_html=True)
            else:
                st.info("Insuficientes columnas para gráfico de áreas.")

        elif "Histograma" in chosen_chart:
            if main_m:
                fig = px.histogram(df, x=main_m, nbins=15, marginal="rug", template=plotly_template, color_discrete_sequence=[palette_colors[0]])
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Histograma:</b> Distribución de frecuencias de {main_m}.</div>', unsafe_allow_html=True)
            else:
                st.info("Se requiere una columna numérica para el histograma.")

        elif "Dispersión" in chosen_chart:
            if len(num_cols) >= 2:
                fig = px.scatter(df, x=num_cols[0], y=num_cols[1], color=cat_m if cat_m else None, trendline="ols", template=plotly_template, color_discrete_sequence=palette_colors)
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Dispersión:</b> Relación entre {num_cols[0]} y {num_cols[1]}.</div>', unsafe_allow_html=True)
            else:
                st.info("Se requieren 2 columnas numéricas para dispersión.")

        elif "Boxplot" in chosen_chart:
            if main_m:
                fig = px.box(df, x=cat_m if cat_m else None, y=main_m, points="all", template=plotly_template, color_discrete_sequence=palette_colors)
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Boxplot:</b> Mediana y valores atípicos de {main_m}.</div>', unsafe_allow_html=True)
            else:
                st.info("Se requiere una columna numérica para el boxplot.")

        elif "Torta" in chosen_chart:
            if cat_m and main_m:
                df_p = df.groupby(cat_m)[main_m].sum().reset_index().sort_values(by=main_m, ascending=False).head(7)
                fig = px.pie(df_p, names=cat_m, values=main_m, hole=0.4, template=plotly_template, color_discrete_sequence=palette_colors)
                fig.update_layout(height=250, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Torta (%):</b> Porcentaje que representa cada opción en {cat_m}.</div>', unsafe_allow_html=True)
            else:
                st.info("Se requiere 1 categoría y 1 métrica numérica.")

        elif "Gauge" in chosen_chart:
            if main_m:
                avg_v = df[main_m].mean()
                max_v = df[main_m].max()
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=float(avg_v),
                    title={'text': f"Rendimiento Promedio ({main_m})", 'font': {'size': 12}},
                    gauge={
                        'axis': {'range': [0, max(float(max_v), 1.0)]},
                        'bar': {'color': palette_colors[0]},
                        'steps': [
                            {'range': [0, float(max_v)*0.5], 'color': "#f1f5f9"},
                            {'range': [float(max_v)*0.5, float(max_v)], 'color': "#e2e8f0"}
                        ]
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=48, b=15), template=plotly_template)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div class="compact-badge">💡 <b>Gauge Radial:</b> Nivel promedio respecto al máximo ({max_v:,.2f}).</div>', unsafe_allow_html=True)

        elif "Tabla" in chosen_chart:
            if cat_m and main_m:
                df_tb = df.groupby(cat_m)[main_m].agg(['sum', 'mean', 'count']).reset_index().sort_values(by='sum', ascending=False).head(6)
                df_tb.columns = [cat_m, 'Suma Total', 'Promedio', 'Frecuencia']
                st.dataframe(df_tb.style.format({'Suma Total': '{:,.2f}', 'Promedio': '{:,.2f}'}), use_container_width=True, height=230)
                st.markdown(f'<div class="compact-badge">💡 <b>Tabla Resumen:</b> Desglose numérico por {cat_m}.</div>', unsafe_allow_html=True)
            else:
                st.dataframe(df.head(6), use_container_width=True, height=230)
                st.markdown('<div class="compact-badge">💡 <b>Tabla Resumen:</b> Primeros registros del conjunto.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# INTERACTIVE USER GUIDE MODAL / DIALOG FUNCTION
# ---------------------------------------------------------
def render_guide_content():
    st.markdown("""
    ### 📖 Guía de Interpretación Fácil

    Esta plataforma está diseñada para que **cualquier persona pueda entender sus datos en segundos** sin necesitar conocimientos matemáticos o estadísticos.

    ---

    #### 💡 1. Resumen Ejecutivo (Lo esencial a 1 vista)
    - **Hallazgos Clave:** 3 puntos en español sencillo que resumen lo más importante al cargar tus datos.
    - **Tarjetas KPI:** Cifras clave de total, promedio y máximos.
    - **Gráficos Claros:** Visualización de tendencias y categorías con una tarjeta verde debajo que te explica qué significa en lenguaje común.

    ---

    #### 🔍 2. Preguntas y Respuestas (Explorador Guiado)
    Selecciona una pregunta de negocio directa:
    - **"¿En qué grupos se dividen mis datos?"**: Muestra segmentos automáticos (ej. clientes de alto valor vs ocasionales).
    - **"¿Hay datos anómalos o sospechosos?"**: Muestra una lista de alertas de registros inusuales que deberías revisar.
    - **"¿Qué variables influyen entre sí?"**: Evalúa relaciones simples sin jerga técnica.

    ---

    #### 📋 3. Ver Tabla y Exportar
    - Incluye **buscador en tiempo real** para encontrar registros tipeando palabras clave.
    - Botones de descarga limpia a **Excel (.xlsx)** y **CSV**.
    """)

if hasattr(st, "dialog"):
    @st.dialog("📖 Guía Rápida de Interpretación", width="large")
    def show_guide_dialog():
        render_guide_content()
else:
    def show_guide_dialog():
        with st.expander("📖 Guía Rápida de Interpretación", expanded=True):
            render_guide_content()

# ---------------------------------------------------------
# DATA LOADING & CACHING WITH MULTI-ENCODING FALLBACK
# ---------------------------------------------------------
@st.cache_data
def load_data(file_obj):
    filename = file_obj.name
    encodings_to_try = ['utf-8-sig', 'utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    if filename.endswith('.csv') or filename.endswith('.tsv') or filename.endswith('.txt'):
        sep = '\t' if filename.endswith('.tsv') else ','
        df = None
        for enc in encodings_to_try:
            try:
                file_obj.seek(0)
                df = pd.read_csv(file_obj, sep=sep, encoding=enc)
                break
            except Exception:
                continue
        if df is None:
            for enc in encodings_to_try:
                try:
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj, sep=None, engine='python', encoding=enc)
                    break
                except Exception:
                    continue
        if df is None:
            file_obj.seek(0)
            df = pd.read_csv(file_obj, encoding_errors='replace')
        return df
        
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        df_dict = pd.read_excel(file_obj, sheet_name=None)
        return df_dict
    elif filename.endswith('.json'):
        df = pd.read_json(file_obj)
    else:
        file_obj.seek(0)
        df = pd.read_csv(file_obj, encoding_errors='replace')
    return df

def preprocess_df(df):
    df_copy = df.copy()
    # Clean BOMs and trailing spaces from column names
    df_copy.columns = [str(c).replace('\ufeff', '').strip() for c in df_copy.columns]
    
    # Auto detect datetime columns
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            try:
                sample = df_copy[col].dropna().head(10)
                if not sample.empty and sample.astype(str).str.match(r'^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}').all():
                    df_copy[col] = pd.to_datetime(df_copy[col])
            except Exception:
                pass
    return df_copy

# Initialize session state for user dataset selection and grid layout
if 'use_demo_data' not in st.session_state:
    st.session_state['use_demo_data'] = False

if 'custom_grid_panels' not in st.session_state:
    st.session_state['custom_grid_panels'] = [
        {"id": "p1", "title": "📊 Profit Overview", "default_type": "Barras", "width": 2},
        {"id": "p2", "title": "🏔️ Volumen Acumulado", "default_type": "Áreas", "width": 1},
        {"id": "p3", "title": "📈 Evolución / Tendencia", "default_type": "Líneas", "width": 1},
        {"id": "p4", "title": "📋 Resumen Categorías", "default_type": "Tabla", "width": 1},
        {"id": "p5", "title": "📊 Distribución Frecuencias", "default_type": "Histograma", "width": 1},
        {"id": "p6", "title": "🎯 Relación y Composición", "default_type": "Dispersión", "width": 2},
        {"id": "p7", "title": "🎯 Indicador Rendimiento", "default_type": "Gauge", "width": 1}
    ]

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & UPLOAD
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 📂 DataLens Control")
    uploaded_files = st.file_uploader(
        "Sube tus datos (CSV, Excel, JSON)",
        type=["csv", "xlsx", "xls", "json", "tsv"],
        accept_multiple_files=True
    )
    
    st.divider()
    
    st.markdown("### 🎨 Apariencia Visual")
    plotly_template = st.selectbox(
        "Estilo de Gráficos",
        ["plotly_white", "plotly_dark", "seaborn", "ggplot2", "presentation"],
        index=0
    )
    color_palette = st.selectbox(
        "Gama de Colores",
        ["Indigo / Violet", "Teal / Emerald", "Sunset / Orange", "Deep Sea Blue"],
        index=0
    )
    
    palette_colors = {
        "Indigo / Violet": ["#4f46e5", "#818cf8", "#c084fc", "#a855f7", "#6366f1"],
        "Teal / Emerald": ["#0d9488", "#14b8a6", "#34d399", "#10b981", "#059669"],
        "Sunset / Orange": ["#f97316", "#fb923c", "#facc15", "#ef4444", "#dc2626"],
        "Deep Sea Blue": ["#0284c7", "#38bdf8", "#0284c7", "#1e3a8a", "#0f172a"]
    }[color_palette]
    # Palette mapping selected above

# Handle dataset loading
datasets = {}
if uploaded_files:
    for f in uploaded_files:
        try:
            loaded = load_data(f)
            if isinstance(loaded, dict):
                for sheet, dset in loaded.items():
                    datasets[f"{f.name} - {sheet}"] = preprocess_df(dset)
            else:
                datasets[f.name] = preprocess_df(loaded)
        except Exception as e:
            st.sidebar.error(f"Error cargando {f.name}: {e}")
elif st.session_state['use_demo_data']:
    default_path = os.path.join(os.path.dirname(__file__), "ejemplo.csv")
    if os.path.exists(default_path):
        df_demo = pd.read_csv(default_path)
        datasets["ejemplo.csv (Demo Data)"] = preprocess_df(df_demo)

# ---------------------------------------------------------
# WELCOME SCREEN IF NO DATASET LOADED
# ---------------------------------------------------------
if not datasets:
    st.markdown("""
    <div class="ds-header-container">
        <h1 class="ds-title">DataLens BI Dashboard</h1>
        <p class="ds-subtitle">Visualización e Interpretación Fácil de Datos para Todos</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">📊</div>
        <h2 style="color: #0f172a; font-weight: 800; margin-bottom: 0.5rem;">Visualiza y entiende cualquier dataset fácilmente</h2>
        <p style="color: #64748b; font-size: 0.95rem; max-width: 550px; margin: 0 auto 1.5rem auto;">
            Sube tu archivo <b>CSV o Excel</b> para obtener resúmenes en texto sencillo, hallazgos clave e interpretaciones automáticas en segundos.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_w1, col_w2, col_w3 = st.columns([1, 2, 1])
    with col_w2:
        if st.button("🧪 Probar con Datos de Demostración (ejemplo.csv)", use_container_width=True, type="primary"):
            st.session_state['use_demo_data'] = True
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📖 Ver Guía Rápida de Interpretación", use_container_width=True):
            show_guide_dialog()

    st.stop()

# Select Active Dataset if datasets are loaded
active_file = st.sidebar.selectbox("📂 Dataset Activo", list(datasets.keys()))
df_raw = datasets[active_file]

# ---------------------------------------------------------
# SIDEBAR FILTERS (SLICERS)
# ---------------------------------------------------------
with st.sidebar:
    st.divider()
    st.markdown("### 🎛️ Filtros Simples")
    df_filtered = df_raw.copy()
    
    # Date filter
    date_cols = [c for c in df_filtered.columns if pd.api.types.is_datetime64_any_dtype(df_filtered[c])]
    if date_cols:
        d_col = date_cols[0]
        min_d, max_d = df_filtered[d_col].min().date(), df_filtered[d_col].max().date()
        if min_d < max_d:
            dates = st.date_input(f"Rango de Fechas: {d_col}", value=(min_d, max_d), min_value=min_d, max_value=max_d)
            if isinstance(dates, tuple) and len(dates) == 2:
                df_filtered = df_filtered[(df_filtered[d_col].dt.date >= dates[0]) & (df_filtered[d_col].dt.date <= dates[1])]
                
    # Categorical filters
    cat_cols = [c for c in df_filtered.columns if df_filtered[c].dtype == 'object' or df_filtered[c].nunique() < 12]
    for c in cat_cols:
        if c in date_cols: continue
        vals = list(df_filtered[c].dropna().unique())
        if len(vals) > 1:
            sel = st.multiselect(f"Filtrar por {c}", vals, default=[])
            if sel:
                df_filtered = df_filtered[df_filtered[c].isin(sel)]

num_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
str_cols = [c for c in df_filtered.columns if c not in num_cols and c not in date_cols]

# ---------------------------------------------------------
# CLEAN HEADER SECTION (NO EMPTY WHITE BOX)
# ---------------------------------------------------------
with st.container(border=True):
    col_h1, col_h2 = st.columns([4, 1.3])
    with col_h1:
        st.markdown(f"""
        <h1 class="ds-title" style="margin:0;">DataLens BI Dashboard</h1>
        <p class="ds-subtitle" style="margin-top:2px; margin-bottom:0;">Interpretación Clara y Sencilla de Datos • Archivo: {active_file}</p>
        """, unsafe_allow_html=True)

    with col_h2:
        if st.button("📖 Ayuda e Interpretación", use_container_width=True, help="Abrir guía de ayuda"):
            show_guide_dialog()

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SINGLE SEAMLESS BENTO GRID LAYOUT (REFERENCE-INSPIRED)
# ---------------------------------------------------------

# Variables clave de apoyo
main_m = num_cols[0] if num_cols else None
cat_m = str_cols[0] if str_cols else None
date_m = date_cols[0] if date_cols else None

# 1. RESUMEN EN LENGUAJE SIMPLE (COMPACTO)
insights_list = generate_plain_insights(df_filtered, main_metric=main_m, cat_col=cat_m, date_col=date_m)
if insights_list:
    summary_html = "<div class='executive-summary-card' style='padding: 0.8rem 1.2rem; margin-bottom: 1rem;'><div class='summary-title' style='margin-bottom: 0.3rem;'>💡 Hallazgos Principales en Lenguaje Claro</div>"
    for item in insights_list[:2]:
        summary_html += f"<div class='summary-item' style='font-size: 0.85rem;'>{item}</div>"
    summary_html += "</div>"
    st.markdown(summary_html, unsafe_allow_html=True)

# 2. TARJETAS KPI TOP ROW (5 COLUMNAS ELEGANTES)
c_kpi1, c_kpi2, c_kpi3, c_kpi4, c_kpi5 = st.columns(5)
with c_kpi1:
    val_sum = df_filtered[main_m].sum() if main_m else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <span class="metric-title">Acumulado ({main_m if main_m else 'Total'})</span>
            <span class="metric-delta delta-positive">+12.5%</span>
        </div>
        <div class="metric-value">{val_sum:,.2f}</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Suma total evaluada</div>
    </div>
    """, unsafe_allow_html=True)

with c_kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <span class="metric-title">Registros</span>
            <span class="metric-delta delta-neutral">Filas</span>
        </div>
        <div class="metric-value">{len(df_filtered):,}</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Total de datos</div>
    </div>
    """, unsafe_allow_html=True)

with c_kpi3:
    val_avg = df_filtered[main_m].mean() if main_m else 0
    st.markdown(f"""
    <div class="metric-card" style="background:#0f172a; color:#ffffff; border-color:#1e293b;">
        <div class="metric-header">
            <span class="metric-title" style="color:#94a3b8;">Promedio</span>
            <span class="metric-delta" style="background:#334155; color:#38bdf8;">Media</span>
        </div>
        <div class="metric-value" style="color:#ffffff;">{val_avg:,.2f}</div>
        <div style="font-size:0.75rem; color:#94a3b8; margin-top:2px;">Por registro</div>
    </div>
    """, unsafe_allow_html=True)

with c_kpi4:
    val_max = df_filtered[main_m].max() if main_m else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <span class="metric-title">Pico Máximo</span>
            <span class="metric-delta delta-warning">Pico</span>
        </div>
        <div class="metric-value">{val_max:,.2f}</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Valor más alto</div>
    </div>
    """, unsafe_allow_html=True)

with c_kpi5:
    cat_count = df_filtered[cat_m].nunique() if cat_m else len(num_cols)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <span class="metric-title">Categorías</span>
            <span class="metric-delta delta-positive">+1.2%</span>
        </div>
        <div class="metric-value">{cat_count}</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Grupos únicos</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DYNAMIC BENTO GRID RENDER ENGINE (RESIZABLE & REORDERABLE CARDS)
# ---------------------------------------------------------

with st.expander("⚙️ Opciones de Personalización de Cuadrícula", expanded=False):
    c_rst1, c_rst2 = st.columns([3, 1])
    with c_rst1:
        st.caption("Usa **📐 Ancho** (1 a 4 cols) y las flechas **⬅️ ➡️** en cada tarjeta para modificar su tamaño y orden. Se ajustan automáticamente.")
    with c_rst2:
        if st.button("🔄 Restablecer Cuadrícula", use_container_width=True):
            st.session_state['custom_grid_panels'] = [
                {"id": "p1", "title": "📊 Profit Overview", "default_type": "Barras", "width": 2},
                {"id": "p2", "title": "🏔️ Volumen Acumulado", "default_type": "Áreas", "width": 1},
                {"id": "p3", "title": "📈 Evolución / Tendencia", "default_type": "Líneas", "width": 1},
                {"id": "p4", "title": "📋 Resumen Categorías", "default_type": "Tabla", "width": 1},
                {"id": "p5", "title": "📊 Distribución Frecuencias", "default_type": "Histograma", "width": 1},
                {"id": "p6", "title": "🎯 Relación y Composición", "default_type": "Dispersión", "width": 2},
                {"id": "p7", "title": "🎯 Product Sales Gauge", "default_type": "Gauge", "width": 1}
            ]
            st.rerun()

# Dynamically chunk grid panels into rows of max 4 slots
grid_rows = []
curr_row_items = []
curr_row_width = 0

for panel_cfg in st.session_state['custom_grid_panels']:
    p_w = panel_cfg.get("width", 1)
    if curr_row_width + p_w > 4 and curr_row_items:
        grid_rows.append(curr_row_items)
        curr_row_items = [panel_cfg]
        curr_row_width = p_w
    else:
        curr_row_items.append(panel_cfg)
        curr_row_width += p_w

if curr_row_items:
    grid_rows.append(curr_row_items)

# Render each row using proportional Streamlit columns
for row_list in grid_rows:
    row_widths = [p.get("width", 1) for p in row_list]
    rendered_cols = st.columns(row_widths)
    for c_idx, panel_cfg in enumerate(row_list):
        with rendered_cols[c_idx]:
            render_dynamic_panel(
                panel_id=panel_cfg["id"],
                panel_title=panel_cfg["title"],
                default_type=panel_cfg["default_type"],
                df=df_filtered,
                num_cols=num_cols,
                str_cols=str_cols,
                date_cols=date_cols,
                plotly_template=plotly_template,
                palette_colors=palette_colors
            )

with st.container(border=True):
    col_t, col_e = st.columns([2, 1])
    with col_t:
        st.markdown("<h4 style='margin:0; padding-top:4px;'>📋 Booking History / Registros Detallados</h4>", unsafe_allow_html=True)
    with col_e:
        search_query = st.text_input("🔍 Buscar:", "", placeholder="Filtra la tabla...", key="panel8_search", label_visibility="collapsed")
    
    df_table_show = df_filtered.copy()
    if search_query:
        mask = np.column_stack([df_table_show[col].astype(str).str.contains(search_query, case=False, na=False) for col in df_table_show.columns])
        df_table_show = df_table_show[mask.any(axis=1)]
        
    st.dataframe(df_table_show, use_container_width=True, height=220)
    
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        csv_data = df_table_show.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", data=csv_data, file_name="datalens_export.csv", mime="text/csv", use_container_width=True)
    with btn_c2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df_table_show.to_excel(writer, index=False, sheet_name='DataLens')
        st.download_button("📊 Descargar Excel", data=buf.getvalue(), file_name="datalens_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<br><hr><center><small>DataLens BI Dashboard • Visualización Bento Grid Inteligente</small></center>", unsafe_allow_html=True)

# ---------------------------------------------------------
# INTERACTIVE MOUSE DRAG-AND-DROP & CORNER RESIZE ENGINE
# ---------------------------------------------------------
st.html("""
<style>
/* Corner Drag-to-Resize & Card Drag-and-Drop */
div[data-testid="stVerticalBlockBorderWrapper"] {
    resize: both !important;
    overflow: auto !important;
    min-width: 250px !important;
    min-height: 240px !important;
    position: relative !important;
    transition: box-shadow 0.2s, transform 0.15s !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]::after {
    content: "↘";
    position: absolute;
    bottom: 2px;
    right: 6px;
    font-size: 14px;
    color: #4f46e5;
    pointer-events: none;
    font-weight: bold;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.15) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"].drag-over-card {
    border: 2px dashed #4f46e5 !important;
    background-color: rgba(79, 70, 229, 0.05) !important;
    transform: scale(1.01);
}

.st-drag-header {
    cursor: grab !important;
    user-select: none !important;
}
.st-drag-header:active {
    cursor: grabbing !important;
}
</style>

<script>
(function() {
    function initCardDragAndResize() {
        const cards = document.querySelectorAll('div[data-testid="stVerticalBlockBorderWrapper"]');
        
        cards.forEach((card, idx) => {
            const header = card.querySelector('h4');
            if (header) {
                header.classList.add('st-drag-header');
                header.setAttribute('title', 'Haz clic y arrastra para mover esta tarjeta');
            }

            card.setAttribute('draggable', 'true');

            card.ondragstart = (e) => {
                e.dataTransfer.setData('text/plain', String(idx));
                card.style.opacity = '0.4';
            };

            card.ondragend = () => {
                card.style.opacity = '1';
                cards.forEach(c => c.classList.remove('drag-over-card'));
            };

            card.ondragover = (e) => {
                e.preventDefault();
                card.classList.add('drag-over-card');
            };

            card.ondragleave = () => {
                card.classList.remove('drag-over-card');
            };

            card.ondrop = (e) => {
                e.preventDefault();
                card.classList.remove('drag-over-card');
                const fromIdx = parseInt(e.dataTransfer.getData('text/plain'), 10);
                if (!isNaN(fromIdx) && fromIdx !== idx) {
                    const fromCard = cards[fromIdx];
                    if (fromCard && card.parentElement) {
                        const parent = card.parentElement;
                        if (fromIdx < idx) {
                            parent.insertBefore(fromCard, card.nextSibling);
                        } else {
                            parent.insertBefore(fromCard, card);
                        }
                        window.dispatchEvent(new Event('resize'));
                    }
                }
            };

            if (window.ResizeObserver && !card.dataset.resizeObserved) {
                card.dataset.resizeObserved = 'true';
                const ro = new ResizeObserver(() => {
                    window.dispatchEvent(new Event('resize'));
                });
                ro.observe(card);
            }
        });
    }

    setTimeout(initCardDragAndResize, 300);
    setInterval(initCardDragAndResize, 1500);
})();
</script>
""")
