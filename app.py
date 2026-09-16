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
    initial_sidebar_state="auto"  # Open on desktop, collapsed on mobile
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
# INTERACTIVE USER GUIDE MODAL / DIALOG FUNCTION
# ---------------------------------------------------------
def render_guide_content():
    st.markdown("""
    ### 📖 Guía de Uso e Interpretación de Funciones

    Bienvenido a **DataLens BI Dashboard**. Esta plataforma combina inteligencia de negocios interactiva con algoritmos estadísticos y de Machine Learning aplicados.

    ---

    #### 📊 1. Dashboard Ejecutivo & Analítica Avanzada
    - **Tarjetas KPI e Interpretación Automática**: Muestran el volumen de datos, acumulados, promedios y máximos con explicaciones generadas en tiempo real.
    - **Relojes de Rendimiento (Gauges)**: Miden la eficiencia y el índice de salud operativa de tus métricas.
    - **Tendencia Temporal con Media Móvil**: Filtra la volatilidad mediante curvas suavizadas.
    - **Treemap Jerárquico**: Representa la proporción y volumen de las categorías principales.
    - **🤖 Clustering K-Means & PCA 2D**: Agrupa observaciones similares en clústeres y las proyecta en un plano 2D explicativo.
    - **⚠️ Detección de Anomalías (Isolation Forest)**: Detecta desviaciones atípicas o valores extremos que requieren atención.
    - **🔮 Regresión Lineal OLS**: Evalúa la tendencia matemática de crecimiento y su grado de certidumbre ($R^2$).
    - **📈 Matriz de Correlación & Gráfico de Violín (Density)**: Mide la relación entre variables y evalúa los cuartiles y la densidad de distribución de los datos.

    ---

    #### 📋 2. Explorador de Datos
    - Incluye **buscador interactivo (lupita)** para encontrar registros específicos en tiempo real.
    - Exportación limpia a **CSV** y **Excel (.xlsx)**.
    """)

if hasattr(st, "dialog"):
    @st.dialog("📖 Guía Completa de Uso e Interpretación BI", width="large")
    def show_guide_dialog():
        render_guide_content()
else:
    def show_guide_dialog():
        with st.expander("📖 Guía Completa de Uso e Interpretación BI", expanded=True):
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

# Initialize session state for user dataset selection
if 'use_demo_data' not in st.session_state:
    st.session_state['use_demo_data'] = False

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & UPLOAD
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 📂 DataLens BI Control")
    uploaded_files = st.file_uploader(
        "Sube tus datos aquí (CSV, Excel, JSON)",
        type=["csv", "xlsx", "xls", "json", "tsv"],
        accept_multiple_files=True
    )
    
    st.divider()
    
    st.markdown("### 🎨 Tema Visual & Paleta")
    plotly_template = st.selectbox(
        "Plantilla Plotly",
        ["plotly_white", "plotly_dark", "seaborn", "ggplot2", "presentation"],
        index=0  # Default Light Mode
    )
    color_palette = st.selectbox(
        "Esquema de Colores",
        ["Indigo / Violet", "Teal / Emerald", "Sunset / Orange", "Deep Sea Blue"],
        index=0
    )
    
    palette_colors = {
        "Indigo / Violet": ["#4f46e5", "#818cf8", "#c084fc", "#a855f7", "#6366f1"],
        "Teal / Emerald": ["#0d9488", "#14b8a6", "#34d399", "#10b981", "#059669"],
        "Sunset / Orange": ["#f97316", "#fb923c", "#facc15", "#ef4444", "#dc2626"],
        "Deep Sea Blue": ["#0284c7", "#38bdf8", "#0284c7", "#1e3a8a", "#0f172a"]
    }[color_palette]

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
        <p class="ds-subtitle">Plataforma de Inteligencia de Negocios, Machine Learning y Análisis Estadístico</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">📁</div>
        <h2 style="color: #0f172a; font-weight: 800; margin-bottom: 0.5rem;">Sube tus datos aquí</h2>
        <p style="color: #64748b; font-size: 0.95rem; max-width: 550px; margin: 0 auto 1.5rem auto;">
            Carga tus archivos <b>CSV, Excel (.xlsx) o JSON</b> desplegando el menú lateral o utiliza el botón inferior para comenzar la experiencia.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_w1, col_w2, col_w3 = st.columns([1, 2, 1])
    with col_w2:
        if st.button("🧪 Explorar con Dataset de Demostración (ejemplo.csv)", use_container_width=True, type="primary"):
            st.session_state['use_demo_data'] = True
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📖 Abrir Guía de Uso & Manual BI", use_container_width=True):
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
    st.markdown("### 🎛️ Filtros & Slicers")
    df_filtered = df_raw.copy()
    
    # Date filter
    date_cols = [c for c in df_filtered.columns if pd.api.types.is_datetime64_any_dtype(df_filtered[c])]
    if date_cols:
        d_col = date_cols[0]
        min_d, max_d = df_filtered[d_col].min().date(), df_filtered[d_col].max().date()
        if min_d < max_d:
            dates = st.date_input(f"Rango: {d_col}", value=(min_d, max_d), min_value=min_d, max_value=max_d)
            if isinstance(dates, tuple) and len(dates) == 2:
                df_filtered = df_filtered[(df_filtered[d_col].dt.date >= dates[0]) & (df_filtered[d_col].dt.date <= dates[1])]
                
    # Categorical filters
    cat_cols = [c for c in df_filtered.columns if df_filtered[c].dtype == 'object' or df_filtered[c].nunique() < 12]
    for c in cat_cols:
        if c in date_cols: continue
        vals = list(df_filtered[c].dropna().unique())
        if len(vals) > 1:
            sel = st.multiselect(f"Filtrar {c}", vals, default=[])
            if sel:
                df_filtered = df_filtered[df_filtered[c].isin(sel)]

num_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
str_cols = [c for c in df_filtered.columns if c not in num_cols and c not in date_cols]

# ---------------------------------------------------------
# CLEAN HEADER SECTION (PERFECTLY ALIGNED)
# ---------------------------------------------------------
st.markdown('<div class="ds-header-container">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1.3])

with col_h1:
    st.markdown(f"""
    <h1 class="ds-title">DataLens BI Dashboard</h1>
    <p class="ds-subtitle">Análisis Estadístico, Machine Learning e Indicadores Clave • {active_file}</p>
    """, unsafe_allow_html=True)

with col_h2:
    if st.button("📖 Guía de Uso & Manual BI", use_container_width=True, help="Abrir manual interactivo"):
        show_guide_dialog()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2 CONSOLIDATED TABS (Analítica Completa vs Explorador)
# ---------------------------------------------------------
tab_full_dashboard, tab_explorer = st.tabs([
    "📊 Dashboard Ejecutivo & Analítica Avanzada",
    "📋 Explorador de Datos"
])

# =========================================================
# TAB 1: CONSOLIDATED DASHBOARD & ADVANCED ANALYTICS
# =========================================================
with tab_full_dashboard:
    # --- SECTION A: EXECUTIVE OVERVIEW & KPIS ---
    st.markdown("### 📌 1. Indicadores Clave & Rendimiento General")
    
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns([1, 1, 1, 1])
    
    with c_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">
                <span class="metric-title">Volumen de Datos</span>
                <span class="metric-delta delta-neutral">Dataset</span>
            </div>
            <div class="metric-value">{len(df_filtered):,}</div>
            <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Registros filtrados analizados</div>
        </div>
        """, unsafe_allow_html=True)
        
    if num_cols:
        main_metric = num_cols[0]
        val_sum = df_filtered[main_metric].sum()
        val_avg = df_filtered[main_metric].mean()
        val_max = df_filtered[main_metric].max()
        val_min = df_filtered[main_metric].min()
        
        with c_kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Total {main_metric}</span>
                    <span class="metric-delta delta-positive">Suma</span>
                </div>
                <div class="metric-value">{val_sum:,.2f}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Acumulado global del conjunto</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_kpi3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Promedio ({main_metric})</span>
                    <span class="metric-delta delta-neutral">Media</span>
                </div>
                <div class="metric-value">{val_avg:,.2f}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Valor medio por observación</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_kpi4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Pico Máximo</span>
                    <span class="metric-delta delta-warning">Max</span>
                </div>
                <div class="metric-value">{val_max:,.2f}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Pico máximo registrado</div>
            </div>
            """, unsafe_allow_html=True)

    # Dynamic Insight Box for KPIs
    if num_cols:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">💡 Lectura e Interpretación del Negocio (KPIs)</div>
            <div class="insight-body">
                Se están analizando <b>{len(df_filtered):,} observaciones</b>. La variable principal <b>{main_metric}</b> presenta un promedio de <b>{val_avg:,.2f}</b> por registro, alcanzando un valor acumulado total de <b>{val_sum:,.2f}</b>. El valor máximo registrado llega a <b>{val_max:,.2f}</b>, lo que permite evaluar el techo operacional de tu conjunto de datos.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Executive Gauges Row
    if num_cols and len(num_cols) >= 2:
        g_col1, g_col2, g_col3 = st.columns([1, 1, 1])
        with g_col1:
            fig_g1 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(val_avg),
                title={'text': f"Rendimiento Medio ({num_cols[0]})", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, max(float(val_max), 1.0)]},
                    'bar': {'color': palette_colors[0]},
                    'steps': [
                        {'range': [0, float(val_max)*0.5], 'color': "#f1f5f9"},
                        {'range': [float(val_max)*0.5, float(val_max)], 'color': "#e2e8f0"}
                    ]
                }
            ))
            fig_g1.update_layout(height=240, margin=dict(l=25, r=25, t=55, b=25), template=plotly_template)
            st.plotly_chart(fig_g1, use_container_width=True)
            
        with g_col2:
            sec_col = num_cols[1]
            sec_val = df_filtered[sec_col].mean()
            sec_max = df_filtered[sec_col].max()
            fig_g2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(sec_val),
                title={'text': f"Ratio Promedio ({sec_col})", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, max(float(sec_max), 1.0)]},
                    'bar': {'color': palette_colors[1]},
                    'steps': [
                        {'range': [0, float(sec_max)*0.5], 'color': "#f1f5f9"},
                        {'range': [float(sec_max)*0.5, float(sec_max)], 'color': "#e2e8f0"}
                    ]
                }
            ))
            fig_g2.update_layout(height=240, margin=dict(l=25, r=25, t=55, b=25), template=plotly_template)
            st.plotly_chart(fig_g2, use_container_width=True)

        with g_col3:
            health_score = min(100.0, max(0.0, float((val_avg / (val_max + 1e-9)) * 100 * 1.5)))
            fig_g3 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health_score,
                number={'suffix': '%'},
                title={'text': "Índice de Salud Operativa", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': palette_colors[2]},
                    'steps': [
                        {'range': [0, 40], 'color': "#fee2e2"},
                        {'range': [40, 75], 'color': "#fef3c7"},
                        {'range': [75, 100], 'color': "#dcfce7"}
                    ]
                }
            ))
            fig_g3.update_layout(height=240, margin=dict(l=25, r=25, t=55, b=25), template=plotly_template)
            st.plotly_chart(fig_g3, use_container_width=True)

    # Main Visualizations Grid (Native Streamlit Containers - No Empty White Boxes)
    row1_c1, row1_c2 = st.columns([6, 6])
    
    with row1_c1:
        with st.container(border=True):
            if date_cols and num_cols:
                d_col = date_cols[0]
                metric_col = num_cols[0]
                df_time = df_filtered.groupby(d_col)[metric_col].sum().reset_index()
                df_time['Moving_Avg'] = df_time[metric_col].rolling(window=3, min_periods=1).mean()
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=df_time[d_col], y=df_time[metric_col],
                    mode='lines+markers', name=metric_col,
                    line=dict(color=palette_colors[0], width=2.5),
                    marker=dict(size=6)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_time[d_col], y=df_time['Moving_Avg'],
                    mode='lines', name='Media Móvil (Suavizada)',
                    line=dict(color=palette_colors[2], width=2, dash='dash')
                ))
                fig_trend.update_layout(
                    title=f"📈 Tendencia Temporal & Suavizado de {metric_col}",
                    template=plotly_template,
                    height=310,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">💡 ¿Qué nos dice la tendencia temporal?</div>
                    <div class="insight-body">
                        La curva azul muestra los valores de <b>{metric_col}</b> a lo largo del tiempo ({d_col}). La media móvil verde suaviza la curva para identificar si la tendencia estructural es de crecimiento constante o contracción.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            elif len(num_cols) >= 2:
                fig_scat = px.scatter(
                    df_filtered, x=num_cols[0], y=num_cols[1],
                    color=str_cols[0] if str_cols else None,
                    title=f"🎯 Dispersión: {num_cols[0]} vs {num_cols[1]}",
                    template=plotly_template,
                    color_discrete_sequence=palette_colors
                )
                fig_scat.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_scat, use_container_width=True)
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">💡 Análisis de Dispersión</div>
                    <div class="insight-body">
                        Evalúa la relación entre <b>{num_cols[0]}</b> e <b>{num_cols[1]}</b>. Observa la concentración de puntos para detectar agrupaciones naturales.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                fig_hist = px.histogram(
                    df_filtered, x=num_cols[0] if num_cols else df_filtered.columns[0],
                    title="📊 Distribución General de Datos",
                    template=plotly_template,
                    color_discrete_sequence=palette_colors
                )
                fig_hist.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_hist, use_container_width=True)
        
    with row1_c2:
        with st.container(border=True):
            if str_cols and num_cols:
                cat_c = str_cols[0]
                val_c = num_cols[0]
                df_cat = df_filtered.groupby(cat_c)[val_c].sum().reset_index().sort_values(by=val_c, ascending=False).head(10)
                
                fig_bar = px.bar(
                    df_cat, y=cat_c, x=val_c,
                    orientation='h',
                    title=f"🏆 Top {cat_c} por {val_c}",
                    template=plotly_template,
                    color=val_c,
                    color_continuous_scale="Viridis"
                )
                fig_bar.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_bar, use_container_width=True)
                
                top_category_name = df_cat.iloc[0][cat_c]
                top_category_val = df_cat.iloc[0][val_c]
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">💡 Interpretación por Categorías</div>
                    <div class="insight-body">
                        La entidad líder es <b>{top_category_name}</b> con un acumulado de <b>{top_category_val:,.2f}</b> ({val_c}), representando el volumen dominante del negocio en esta dimensión.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                fig_hist = px.histogram(
                    df_filtered, x=num_cols[0] if num_cols else df_filtered.columns[0],
                    title="📊 Distribución General de Datos",
                    template=plotly_template,
                    color_discrete_sequence=palette_colors
                )
                fig_hist.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_hist, use_container_width=True)

    # ROW 2: ADVANCED RESOURCE (TREEMAP HIERARCHICAL BREAKDOWN)
    if str_cols and num_cols:
        row2_c1, row2_c2 = st.columns([6, 6])
        with row2_c1:
            with st.container(border=True):
                cat_c = str_cols[0]
                val_c = num_cols[0]
                df_tree = df_filtered.groupby(cat_c)[val_c].sum().reset_index()
                
                fig_tree = px.treemap(
                    df_tree, path=[cat_c], values=val_c,
                    title=f"🌳 Treemap Jerárquico de Proporción por {cat_c}",
                    template=plotly_template,
                    color=val_c,
                    color_continuous_scale="Teal"
                )
                fig_tree.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_tree, use_container_width=True)
                
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">💡 Proporción Visual Treemap</div>
                    <div class="insight-body">
                        El tamaño de cada rectángulo es proporcional a la contribución de <b>{cat_c}</b> en <b>{val_c}</b>. Permite identificar de un vistazo las entidades que más pesan en el total.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        with row2_c2:
            with st.container(border=True):
                if len(num_cols) >= 2:
                    sec_c = num_cols[1]
                    df_scat2 = px.scatter(
                        df_filtered, x=num_cols[0], y=sec_c,
                        color=str_cols[0] if str_cols else None,
                        size=num_cols[0],
                        title=f"🫧 Análisis de Burbujas: {num_cols[0]} vs {sec_c}",
                        template=plotly_template
                    )
                    df_scat2.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(df_scat2, use_container_width=True)
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-title">💡 Gráfico de Burbujas Multivariable</div>
                        <div class="insight-body">
                            Relaciona la magnitud de <b>{num_cols[0]}</b> con <b>{sec_c}</b>. El tamaño de cada burbuja es proporcional al peso relativo del registro.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    fig_box = px.box(
                        df_filtered, y=num_cols[0],
                        title=f"📦 Diagrama de Caja (Boxplot) de {num_cols[0]}",
                        template=plotly_template
                    )
                    fig_box.update_layout(height=310, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # --- SECTION B: DATA SCIENCE & MACHINE LEARNING ---
    st.markdown("### 🧪 2. Modelos de Data Science & Machine Learning Aplicados")
    st.markdown("Algoritmos automáticos de segmentación (K-Means), detección de anomalías (Isolation Forest) y regresión lineal.")
    
    ds_subtab1, ds_subtab2, ds_subtab3 = st.tabs([
        "🤖 Clustering (K-Means & PCA)",
        "⚠️ Detección de Anomalías (Outliers)",
        "🔮 Regresión & Proyección de Tendencias"
    ])
    
    # --- SUBTAB 1: K-MEANS CLUSTERING ---
    with ds_subtab1:
        if len(num_cols) >= 2:
            with st.container(border=True):
                col_ml1, col_ml2 = st.columns([1, 3])
                
                with col_ml1:
                    st.markdown("#### Configuración del Modelo")
                    selected_features = st.multiselect("Variables Numéricas", num_cols, default=num_cols[:min(4, len(num_cols))])
                    n_clusters = st.slider("Número de Clusters (K)", min_value=2, max_value=min(6, max(2, len(df_filtered))), value=3)
                    
                with col_ml2:
                    if len(selected_features) >= 2 and len(df_filtered) >= n_clusters:
                        try:
                            df_cluster = df_filtered[selected_features].dropna()
                            if len(df_cluster) >= n_clusters:
                                scaler = StandardScaler()
                                scaled_data = scaler.fit_transform(df_cluster)
                                
                                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                                clusters = kmeans.fit_predict(scaled_data)
                                df_cluster['Cluster'] = [f"Cluster {c+1}" for c in clusters]
                                
                                pca = PCA(n_components=2)
                                pca_coords = pca.fit_transform(scaled_data)
                                df_cluster['PCA1'] = pca_coords[:, 0]
                                df_cluster['PCA2'] = pca_coords[:, 1]
                                
                                var_exp = pca.explained_variance_ratio_.sum() * 100
                                
                                fig_pca = px.scatter(
                                    df_cluster, x='PCA1', y='PCA2', color='Cluster',
                                    hover_data=selected_features,
                                    title=f"🌌 Proyección de Clusters en 2D (PCA - Varianza Explicada: {var_exp:.1f}%)",
                                    template=plotly_template,
                                    color_discrete_sequence=palette_colors
                                )
                                fig_pca.update_traces(marker=dict(size=9, opacity=0.8, line=dict(width=1, color='white')))
                                fig_pca.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                                st.plotly_chart(fig_pca, use_container_width=True)
                                
                                cluster_counts = df_cluster['Cluster'].value_counts()
                                dominant_cluster = cluster_counts.index[0]
                                st.markdown(f"""
                                <div class="insight-card">
                                    <div class="insight-title">💡 ¿Qué significan estos Clusters?</div>
                                    <div class="insight-body">
                                        El algoritmo <b>K-Means</b> dividió tus datos en <b>{n_clusters} grupos homogéneos</b>. El grupo más grande es <b>{dominant_cluster}</b> con <b>{cluster_counts.iloc[0]} observaciones ({cluster_counts.iloc[0]/len(df_cluster)*100:.1f}%)</b>. La proyección PCA 2D explica el <b>{var_exp:.1f}% de la varianza total</b>.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.warning("No hay suficientes datos limpios para formar el número de clusters seleccionado.")
                        except Exception as e:
                            st.error(f"Error procesando Clustering: {e}")
                    else:
                        st.info("Selecciona al menos 2 variables numéricas para el análisis de Clustering.")
        else:
            st.warning("Se requieren al menos 2 columnas numéricas en el dataset para ejecutar K-Means.")

    # --- SUBTAB 2: ANOMALY / OUTLIER DETECTION ---
    with ds_subtab2:
        if len(num_cols) >= 1:
            with st.container(border=True):
                col_anom1, col_anom2 = st.columns([1, 3])
                
                with col_anom1:
                    st.markdown("#### Parámetros de Anomalía")
                    anom_feature = st.selectbox("Variable Objetivo", num_cols, index=0)
                    contamination = st.slider("Porcentaje Estimado de Anomalías (%)", 1, 15, 5) / 100.0
                    
                with col_anom2:
                    values = df_filtered[[anom_feature]].dropna()
                    if len(values) >= 5:
                        try:
                            iso_forest = IsolationForest(contamination=contamination, random_state=42)
                            preds = iso_forest.fit_predict(values)
                            values['Anomaly'] = np.where(preds == -1, 'Anomalía Detectada', 'Normal')
                            
                            fig_anom = px.strip(
                                values, x='Anomaly', y=anom_feature, color='Anomaly',
                                color_discrete_map={'Normal': '#6366f1', 'Anomalía Detectada': '#ef4444'},
                                title=f"🚨 Detección de Anomalías (Isolation Forest) sobre {anom_feature}",
                                template=plotly_template
                            )
                            fig_anom.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                            st.plotly_chart(fig_anom, use_container_width=True)
                            
                            n_anom = (preds == -1).sum()
                            st.markdown(f"""
                            <div class="insight-card">
                                <div class="insight-title">💡 ¿Qué representan los puntos rojos de Anomalía?</div>
                                <div class="insight-body">
                                    <b>Isolation Forest</b> identificó <b>{n_anom} observaciones anómalas</b> en la variable <b>{anom_feature}</b>. Estos puntos rojos son valores extremos inusuales que requieren revisión operativa o control de calidad.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"No se pudo ejecutar la detección de anomalías: {e}")
                    else:
                        st.info("Se necesitan al menos 5 registros para evaluar anomalías.")

    # --- SUBTAB 3: REGRESSION & PREDICTION ---
    with ds_subtab3:
        if len(num_cols) >= 2:
            with st.container(border=True):
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    x_reg = st.selectbox("Variable X (Predictora)", num_cols, index=0)
                with r_col2:
                    y_reg = st.selectbox("Variable Y (Objetivo)", num_cols, index=min(1, len(num_cols)-1))
                    
                df_reg = df_filtered[[x_reg, y_reg]].dropna()
                is_constant_x = (df_reg[x_reg].nunique() <= 1) or (df_reg[x_reg].std() == 0)
                
                if is_constant_x:
                    fig_reg = px.scatter(
                        df_reg, x=x_reg, y=y_reg,
                        title=f"📈 Dispersión de {x_reg} vs {y_reg}",
                        template=plotly_template,
                        color_discrete_sequence=[palette_colors[0]]
                    )
                    fig_reg.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig_reg, use_container_width=True)
                    st.warning(f"⚠️ No es posible calcular la regresión lineal porque todos los valores de la variable predictora '{x_reg}' son idénticos o no presentan variación.")
                else:
                    try:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(df_reg[x_reg], df_reg[y_reg])
                        r_sq = r_value**2
                        
                        fig_reg = px.scatter(
                            df_reg, x=x_reg, y=y_reg, trendline="ols",
                            title=f"📈 Modelo Regresión Lineal: R² = {r_sq:.4f} (p-val: {p_value:.3e})",
                            template=plotly_template,
                            color_discrete_sequence=[palette_colors[0]]
                        )
                        fig_reg.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                        st.plotly_chart(fig_reg, use_container_width=True)
                        
                        trend_dir = "creciente (positiva)" if slope > 0 else "decreciente (negativa)"
                        st.markdown(f"""
                        <div class="insight-card">
                            <div class="insight-title">💡 Interpretación del Modelo de Regresión</div>
                            <div class="insight-body">
                                Existe una relación <b>{trend_dir}</b> entre <b>{x_reg}</b> e <b>{y_reg}</b> con ecuación: <b><code>{y_reg} = {slope:.4f} * {x_reg} + ({intercept:.4f})</code></b>.<br>
                                El coeficiente de determinación <b>R² es {r_sq:.4f}</b> (el <b>{r_sq*100:.1f}% de la variabilidad en {y_reg} es explicado matemáticamente por {x_reg}</b>).
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        fig_reg = px.scatter(
                            df_reg, x=x_reg, y=y_reg,
                            title=f"📈 Dispersión de {x_reg} vs {y_reg}",
                            template=plotly_template,
                            color_discrete_sequence=[palette_colors[0]]
                        )
                        fig_reg.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                        st.plotly_chart(fig_reg, use_container_width=True)
                        st.warning(f"⚠️ No se pudo calcular el ajuste lineal: {e}")

    st.divider()

    # --- SECTION C: STATISTICAL ANALYSIS & DISTRIBUTIONS ---
    st.markdown("### 📈 3. Perfilado Estadístico & Correlaciones")
    
    st_col1, st_col2 = st.columns([6, 6])
    
    with st_col1:
        with st.container(border=True):
            if len(num_cols) >= 2:
                corr_matrix = df_filtered[num_cols].corr()
                fig_corr = px.imshow(
                    corr_matrix, text_auto=".2f",
                    color_continuous_scale="Blues",
                    title="🔥 Matriz de Correlación de Pearson",
                    template=plotly_template
                )
                fig_corr.update_layout(height=365, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_corr, use_container_width=True)
                
                try:
                    corr_abs = corr_matrix.abs()
                    corr_vals = corr_abs.to_numpy(copy=True)
                    np.fill_diagonal(corr_vals, 0)
                    corr_abs_df = pd.DataFrame(corr_vals, index=corr_abs.index, columns=corr_abs.columns)
                    max_pair = corr_abs_df.unstack().idxmax()
                    max_corr_val = corr_matrix.loc[max_pair[0], max_pair[1]]
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-title">💡 Interpretación de Correlaciones</div>
                        <div class="insight-body">
                            La asociación más fuerte ocurre entre <b>{max_pair[0]}</b> y <b>{max_pair[1]}</b> (r = <b>{max_corr_val:.2f}</b>).
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    st.caption("💡 Matriz de correlación calculada exitosamente.")
            else:
                st.info("Se necesitan al menos 2 variables numéricas para calcular correlaciones.")
        
    with st_col2:
        with st.container(border=True):
            if num_cols:
                selected_stat_col = st.selectbox("Seleccionar Variable para Violín & Densidad", num_cols)
                
                fig_violin = px.violin(
                    df_filtered, y=selected_stat_col, box=True, points="all",
                    title=f"🎻 Distribución Violín & Cuartiles de {selected_stat_col}",
                    template=plotly_template,
                    color_discrete_sequence=[palette_colors[1]]
                )
                fig_violin.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_violin, use_container_width=True)
                
                skew_val = df_filtered[selected_stat_col].skew()
                skew_desc = "sesgada a la derecha" if skew_val > 0.5 else ("sesgada a la izquierda" if skew_val < -0.5 else "aproximadamente simétrica")
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">💡 Forma y Densidad del Violín</div>
                    <div class="insight-body">
                        Muestra la densidad completa y los cuartiles de <b>{selected_stat_col}</b> con sesgo <b>{skew_desc}</b> (Skewness = <b>{skew_val:.2f}</b>).
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Statistical Summary Table
    if num_cols:
        with st.container(border=True):
            st.markdown("#### 📐 Tabla Completa de Métricas Estadísticas Descriptivas")
            
            stat_df = df_filtered[num_cols].describe().T
            stat_df['Skewness'] = df_filtered[num_cols].skew()
            stat_df['Kurtosis'] = df_filtered[num_cols].kurt()
            stat_df['IQR'] = stat_df['75%'] - stat_df['25%']
            
            st.dataframe(stat_df[['count', 'mean', 'std', 'min', '50%', 'max', 'IQR', 'Skewness', 'Kurtosis']].style.format("{:.2f}"), use_container_width=True)

# =========================================================
# TAB 2: DATA EXPLORER WITH LIVE SEARCH BAR
# =========================================================
with tab_explorer:
    st.markdown("### 📋 Explorador Interactivo de Datos con Buscador")
    
    with st.container(border=True):
        search_query = st.text_input("🔍 Buscar término en el dataset (Filtro en tiempo real):", "", placeholder="Escribe cualquier palabra o número, ej. 'Tres Arroyos', '2015', 'Buenos Aires'...")
        
        df_search_result = df_filtered.copy()
        if search_query:
            mask = np.column_stack([df_search_result[col].astype(str).str.contains(search_query, case=False, na=False) for col in df_search_result.columns])
            df_search_result = df_search_result[mask.any(axis=1)]
            st.caption(f"🔎 Se encontraron **{len(df_search_result):,} filas** que contienen el término '{search_query}'.")
        
        st.dataframe(df_search_result, use_container_width=True, height=420)
        
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            csv_data = df_search_result.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar CSV Filtrado",
                data=csv_data,
                file_name="datalens_export.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with e_col2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                df_search_result.to_excel(writer, index=False, sheet_name='DataLens_BI')
            st.download_button(
                "📊 Descargar Excel Filtrado",
                data=buf.getvalue(),
                file_name="datalens_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.markdown("<br><hr><center><small>DataLens BI Dashboard • Potenciado con Streamlit, Plotly & Scikit-Learn</small></center>", unsafe_allow_html=True)
