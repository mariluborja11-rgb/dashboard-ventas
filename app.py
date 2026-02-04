import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Dashboard Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== ESTILOS ====================
st.markdown("""
<style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    h1 {
        color: #0d0d0d;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    h2 {
        color: #0d0d0d;
        font-size: 20px;
        font-weight: 600;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        border-color: #10a37f;
        box-shadow: 0 4px 12px rgba(16,163,127,0.1);
    }
    
    .metric-label {
        font-size: 12px;
        color: #565869;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0d0d0d;
        margin: 5px 0;
    }
    
    .metric-delta {
        font-size: 12px;
        color: #10a37f;
        font-weight: 500;
        margin-top: 5px;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background: #e5e7eb;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #10a37f 0%, #0d8c70 100%);
        border-radius: 999px;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background: #ecfdf5;
        color: #065f46;
    }
    
    .badge-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .badge-danger {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 30px 0;
    }
    
    .info-box {
        background: #f0fdf4;
        border-left: 4px solid #10a37f;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 13px;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GENERAR DATOS ====================
@st.cache_data
def generar_datos():
    np.random.seed(42)
    vendedores = ['Juan García', 'María López', 'Carlos Rodríguez', 'Ana Martínez', 'Pablo Sánchez']
    
    datos = []
    fecha_inicio = datetime(2026, 2, 1)
    dia_actual = datetime.now()
    
    for vendedor in vendedores:
        for i in range((dia_actual - fecha_inicio).days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            tickets = np.random.randint(8, 18)
            ticket_promedio = np.random.uniform(150, 250)
            venta = tickets * ticket_promedio
            unidades = tickets * np.random.uniform(2.0, 3.5)
            costo = venta * np.random.uniform(0.55, 0.65)
            
            datos.append({
                'Fecha': fecha,
                'Vendedor': vendedor,
                'Venta': round(venta, 2),
                'Tickets': tickets,
                'Unidades': round(unidades),
                'Costo': round(costo, 2)
            })
    
    return pd.DataFrame(datos)

# ==================== FUNCIONES ====================
def calcular_kpis(df, vendedor=None):
    if vendedor:
        df = df[df['Vendedor'] == vendedor]
    
    if df.empty:
        return {k: 0 for k in ['venta', 'tickets', 'unidades', 'margen', 'margen_pct', 'ticket_prom', 'upt']}
    
    venta = df['Venta'].sum()
    tickets = df['Tickets'].sum()
    unidades = df['Unidades'].sum()
    costo = df['Costo'].sum()
    
    return {
        'venta': venta,
        'tickets': tickets,
        'unidades': unidades,
        'margen': venta - costo,
        'margen_pct': (venta - costo) / venta * 100 if venta > 0 else 0,
        'ticket_prom': venta / tickets if tickets > 0 else 0,
        'upt': unidades / tickets if tickets > 0 else 0
    }

def get_badge(pct):
    if pct >= 100:
        return '<span class="badge badge-success">✓ Cumplido</span>'
    elif pct >= 95:
        return '<span class="badge badge-warning">⚠ Alerta</span>'
    else:
        return '<span class="badge badge-danger">✗ Crítico</span>'

# ==================== CARGAR DATOS ====================
df_ventas = generar_datos()
df_ventas = df_ventas[df_ventas['Fecha'] <= datetime.now()]

META_MENSUAL = 50000
FECHA_INICIO = datetime(2026, 2, 1)
FECHA_FIN = datetime(2026, 2, 28)
DIA_ACTUAL = datetime.now()
DIAS_TRANSCURRIDOS = max(1, (DIA_ACTUAL - FECHA_INICIO).days + 1)
DIAS_RESTANTES = max(1, (FECHA_FIN - DIA_ACTUAL).days + 1)

vendedores_lista = sorted(df_ventas['Vendedor'].unique().tolist())

# ==================== HEADER ====================
st.title("📊 Dashboard de Ventas")
st.markdown(f"**Febrero 2026** • Día {DIAS_TRANSCURRIDOS} de 28")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    meta_input = st.number_input("Meta Mensual ($)", value=META_MENSUAL, step=1000)
    ticket_meta = st.number_input("Ticket Promedio Meta ($)", value=200, step=10)
    upt_meta = st.number_input("UPT Meta", value=2.5, step=0.1)
    margen_meta = st.number_input("Margen % Meta", value=40, step=1)

# ==================== CÁLCULOS ====================
kpis = calcular_kpis(df_ventas)
venta_total = kpis['venta']
pct_cumpl = (venta_total / meta_input * 100)
falta = meta_input - venta_total
venta_diaria_req = falta / DIAS_RESTANTES
venta_diaria_prom = venta_total / DIAS_TRANSCURRIDOS
proyeccion = venta_total + (venta_diaria_prom * DIAS_RESTANTES)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==================== SECCIÓN 1: MÉTRICAS ====================
st.markdown("### 🎯 Estado de Meta")

col1, col2, col3, col4 = st.columns(4)

with col1:
    progress_pct = min(pct_cumpl, 100)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Venta Actual</div>
        <div class="metric-value">${venta_total:,.0f}</div>
        <div class="metric-delta">{pct_cumpl:.1f}% de meta</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Meta Mensual</div>
        <div class="metric-value">${meta_input:,.0f}</div>
        <div class="metric-delta">Faltan ${max(0, falta):,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color = "✓" if proyeccion >= meta_input else "✗"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Proyección Final</div>
        <div class="metric-value">${proyeccion:,.0f}</div>
        <div class="metric-delta">{color} vs Meta</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Venta Diaria Requerida</div>
        <div class="metric-value">${venta_diaria_req:,.0f}</div>
        <div class="metric-delta">Próximos {DIAS_RESTANTES} días</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==================== SECCIÓN 2: KPIs ====================
st.markdown("### 📈 Indicadores Clave")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ticket Promedio</div>
        <div class="metric-value">${kpis['ticket_prom']:.2f}</div>
        <div class="metric-delta">Meta: ${ticket_meta}</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">UPT</div>
        <div class="metric-value">{kpis['upt']:.2f}</div>
        <div class="metric-delta">Meta: {upt_meta}</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Margen %</div>
        <div class="metric-value">{kpis['margen_pct']:.1f}%</div>
        <div class="metric-delta">Meta: {margen_meta}%</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Clientes</div>
        <div class="metric-value">{kpis['tickets']:.0f}</div>
        <div class="metric-delta">Promedio {kpis['tickets']/DIAS_TRANSCURRIDOS:.0f}/día</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==================== SECCIÓN 3: GRÁFICAS ====================
st.markdown("### 📊 Análisis Visual")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### Progreso de Meta")
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=min(pct_cumpl, 150),
        title={'text': "% Cumplimiento"},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': "#10a37f"},
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 85], 'color': "#fef3c7"},
                {'range': [85, 100], 'color': "#ecfdf5"},
                {'range': [100, 150], 'color': "#dcfce7"}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig_gauge.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

with col_chart2:
    st.markdown("#### Ventas Acumuladas")
    
    df_acum = df_ventas.groupby('Fecha')['Venta'].sum().reset_index()
    df_acum['Venta_Acum'] = df_acum['Venta'].cumsum()
    
    meta_diaria = meta_input / 28
    df_acum['Meta_Esperada'] = meta_diaria * (np.arange(len(df_acum)) + 1)
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_acum['Fecha'],
        y=df_acum['Venta_Acum'],
        mode='lines',
        name='Venta Acumulada',
        line=dict(color='#10a37f', width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 163, 127, 0.1)'
    ))
    fig_line.add_trace(go.Scatter(
        x=df_acum['Fecha'],
        y=df_acum['Meta_Esperada'],
        mode='lines',
        name='Meta Esperada',
        line=dict(color='#ef4444', width=2, dash='dash')
    ))
    fig_line.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10), hovermode='x unified')
    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==================== SECCIÓN 4: RANKING ====================
st.markdown("### 🏆 Ranking de Vendedores")

ranking_data = []
meta_per_vend = meta_input / len(vendedores_lista)

for vendedor in vendedores_lista:
    kpi = calcular_kpis(df_ventas, vendedor)
    pct = (kpi['venta'] / meta_per_vend * 100)
    
    ranking_data.append({
        'Vendedor': vendedor,
        'Venta': kpi['venta'],
        'Meta': meta_per_vend,
        '%': pct,
        'Tickets': kpi['tickets'],
        'Ticket Prom': kpi['ticket_prom'],
        'UPT': kpi['upt'],
        'Margen %': kpi['margen_pct']
    })

df_rank = pd.DataFrame(ranking_data).sort_values('%', ascending=False)

col_rank1, col_rank2 = st.columns([2, 1])

with col_rank1:
    st.markdown("#### Desempeño por Vendedor")
    
    rank_display = df_rank.copy()
    rank_display['Venta'] = rank_display['Venta'].apply(lambda x: f"${x:,.0f}")
    rank_display['Meta'] = rank_display['Meta'].apply(lambda x: f"${x:,.0f}")
    rank_display['%'] = rank_display['%'].apply(lambda x: f"{x:.1f}%")
    rank_display['Ticket Prom'] = rank_display['Ticket Prom'].apply(lambda x: f"${x:.2f}")
    rank_display['UPT'] = rank_display['UPT'].apply(lambda x: f"{x:.2f}")
    rank_display['Margen %'] = rank_display['Margen %'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(rank_display, use_container_width=True, hide_index=True)

with col_rank2:
    st.markdown("#### Distribución")
    
    fig_dist = px.bar(
        df_rank.sort_values('%'),
        y='Vendedor',
        x='%',
        orientation='h',
        color='%',
        color_continuous_scale=['#fee2e2', '#fef3c7', '#ecfdf5', '#dcfce7'],
        labels={'%': '% Cumpl'}
    )
    fig_dist.add_vline(x=100, line_dash="dash", line_color="#ef4444")
    fig_dist.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div class='divider'></div>", unsafe_before_content=True)

# ==================== SECCIÓN 5: ANÁLISIS ====================
st.markdown("### 📋 Análisis Detallado")

tab1, tab2 = st.tabs(["Por Vendedor", "Tendencias"])

with tab1:
    vend_select = st.selectbox("Selecciona vendedor", vendedores_lista)
    
    df_vend = df_ventas[df_ventas['Vendedor'] == vend_select]
    kpi_vend = calcular_kpis(df_vend)
    pct_vend = (kpi_vend['venta'] / meta_per_vend * 100)
    
    col_det1, col_det2, col_det3, col_det4 = st.columns(4)
    
    with col_det1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Venta Total</div>
            <div class="metric-value">${kpi_vend['venta']:,.0f}</div>
            <div class="metric-delta">{pct_vend:.1f}% de meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_det2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tickets</div>
            <div class="metric-value">{kpi_vend['tickets']:.0f}</div>
            <div class="metric-delta">${kpi_vend['ticket_prom']:.2f} c/u</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_det3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">UPT</div>
            <div class="metric-value">{kpi_vend['upt']:.2f}</div>
            <div class="metric-delta">Unidades/ticket</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_det4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Margen %</div>
            <div class="metric-value">{kpi_vend['margen_pct']:.1f}%</div>
            <div class="metric-delta">${kpi_vend['margen']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("#### Tendencias Diarias")
    
    tendencia = df_ventas.groupby('Fecha').agg({
        'Venta': 'sum',
        'Tickets': 'sum',
        'Unidades': 'sum'
    }).reset_index()
    
    metrica = st.selectbox("Métrica", ['Venta', 'Tickets', 'Unidades'])
    
    fig_tend = px.area(
        tendencia,
        x='Fecha',
        y=metrica,
        title=f"Tendencia: {metrica}",
        labels={'Fecha': '', metrica: metrica}
    )
    fig_tend.update_traces(fillcolor='rgba(16, 163, 127, 0.3)', line_color='#10a37f')
    st.plotly_chart(fig_tend, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #999; font-size: 12px;'>📊 Dashboard de Ventas Interactivo | Actualizado automáticamente</div>", unsafe_allow_html=True)
