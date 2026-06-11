import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Dashboard Academia Vidrí-Novex",
    page_icon="img/cheque.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F7F8FA; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #2563EB;
        margin-bottom: 8px;
    }
    .metric-card.red  { border-left-color: #EF4444; }
    .metric-card.green{ border-left-color: #10B981; }
    .metric-card.orange{ border-left-color: #F59E0B; }
    .metric-label { font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
    .metric-value { font-size: 32px; font-weight: 800; color: #111827; line-height: 1.1; }
    .metric-sub   { font-size: 13px; color: #6B7280; margin-top: 4px; }
    .section-title { font-size: 18px; font-weight: 700; color: #111827; margin: 20px 0 10px 0; }
    .badge-green { background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    .badge-red   { background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    .badge-orange{ background:#FEF3C7; color:#92400E; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    div[data-testid="stSidebar"] { background: #1E3A5F; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stSelectbox label { color: #CBD5E1 !important; }
    h1 { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    xl = pd.ExcelFile("data/Reporte LMS.xlsx")
    fact = xl.parse("Fact_LMS")
    cc   = xl.parse("CC")
    emp  = xl.parse("Empleados")

    fact['Hora inicio'] = pd.to_numeric(fact['Hora inicio'], errors='coerce')
    fact['Hora fin'] = pd.to_numeric(fact['Hora fin'],    errors='coerce')
    fact['duracion_horas'] = (fact['Hora fin'] - fact['Hora inicio']).clip(lower=0)
    
    fact['Fecha comienzo'] = pd.to_datetime(fact['Fecha comienzo'], errors='coerce')
    fact['Fecha fin'] = pd.to_datetime(fact['Fecha fin'], errors='coerce')
    fact['velocidad'] = (fact['Fecha fin'] - fact['Fecha comienzo']).dt.total_seconds() / 3600

    cc_op = cc[cc['Tipo'] == 'Operativa'][['Centro de Trabajo', 'Distrito', 'CC']].copy()
    fact = fact.merge(cc_op, left_on='Sucursal', right_on='Centro de Trabajo', how='left')

    fact['cumple'] = fact['Estado Aprobación'] == 'Aprobado'
    fact['finalizo'] = fact['Estado curso'] == 'Finalizado a tiempo'

    return fact, cc_op, emp

fact, cc_op, emp = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("img/vidrinovex.png", width=250)
    st.markdown("### Dashboard Academia _Vidrí-Novex_")
    st.markdown("---")

    distritos = ["Todos"] + sorted(cc_op['Distrito'].dropna().unique().tolist())
    distrito_sel = st.selectbox("🗺️ Distrito", distritos)

    if distrito_sel != "Todos":
        sucursales_disponibles = cc_op[cc_op['Distrito'] == distrito_sel]['Centro de Trabajo'].tolist()
    else:
        sucursales_disponibles = sorted(fact['Sucursal'].dropna().unique().tolist())

    sucursales_disponibles = ["Todos"] + sucursales_disponibles
    sucursal_sel = st.selectbox("🏬 Centro de Trabajo", sucursales_disponibles)

    cursos_disponibles = ["Todos"] + sorted(fact['Curso'].dropna().unique().tolist())
    curso_sel = st.selectbox("📚 Curso", cursos_disponibles)

    #fechas_ordenadas = sorted(pd.to_datetime(fact['Fecha asignación'], errors='coerce').dropna().unique())
    #fecha_asign = ["Todos"] + [fecha.strftime('%d/%m/%Y') for fecha in fechas_ordenadas]
    #fecha_sel = st.selectbox("📅 Fecha de Asignación", fecha_asign)
    fechas_ordenadas = sorted(
        pd.to_datetime(
            fact['Fecha asignación'],
            errors='coerce'
        ).dropna().unique()
    )

    fecha_options = [None] + list(fechas_ordenadas)

    fecha_sel = st.selectbox(
        "📅 Fecha de Asignación",
        fecha_options,
        format_func=lambda x:
            "Todos" if x is None
            else pd.Timestamp(x).strftime("%d/%m/%Y")
    )

    st.markdown("---")
    st.markdown("**Última actualización:**")
    if 'Fecha asignación' in fact.columns:
        ultima = pd.to_datetime(fact['Fecha asignación'], errors='coerce').max()
        st.markdown(f"📅 _{ultima.strftime('%d/%m/%Y') if pd.notna(ultima) else 'N/D'}_")

# ── Filtros ────────────────────────────────────────────────────────────────────
df = fact.copy()
if distrito_sel != "Todos":
    df = df[df['Distrito'] == distrito_sel]
if sucursal_sel != "Todos":
    df = df[df['Sucursal'] == sucursal_sel]
if curso_sel != "Todos":
    df = df[df['Curso'] == curso_sel]
#if fecha_sel != "Todos":
#    fecha_filtro = pd.to_datetime(fecha_sel, format='%d/%m/%Y')
#    df = df[df['Fecha asignación'].dt.normalize == fecha_filtro.normalize()]
if fecha_sel is not None:
    df = df[
        df['Fecha asignación'].dt.normalize()
        ==
        pd.Timestamp(fecha_sel).normalize()
    ]

# ── Header ─────────────────────────────────────────────────────────────────────
titulo = f"Sucursal: {sucursal_sel}" if sucursal_sel != "Todos" else (f"Distrito: {distrito_sel}" if distrito_sel != "Todos" else "Vista General – Todas las Sucursales")
st.markdown(f"# {titulo}")
st.markdown(f"*{df['Código Empleado'].nunique():,} colaboradores · {df['Curso'].nunique()} cursos*")
st.markdown("---")

# ── KPIs principales ──────────────────────────────────────────────────────────
total = len(df)
aprobados = (df['Estado Aprobación'] == 'Aprobado').sum()
no_cumplen = (df['Estado curso'] != 'Finalizado a tiempo').sum()
desaprobados = (df['Estado Aprobación'] == 'Desaprobado').sum()
en_progreso = (df['Estado Aprobación'] == 'En progreso').sum()
pct_aprobados = round(aprobados / total * 100, 1) if total else 0
pct_incump = round(no_cumplen / total * 100, 1) if total else 0
nota_prom = df['Evaluación Final - Nota'].mean()
nota_prom = round(nota_prom, 1) if not np.isnan(nota_prom) else 0
delta_prom = df[df['Delta Puntaje'] != 0]['Delta Puntaje'].mean()
delta_prom = round(delta_prom, 1) if not np.isnan(delta_prom) else 0
finalizados = df['finalizo'].sum()
pct_cumplimiento = round(finalizados / total * 100, 1) if total else 0
velocidad_prom = df[df['velocidad'] > 0]['velocidad'].mean()
velocidad_prom = round(velocidad_prom, 1) if not np.isnan(velocidad_prom) else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

def kpi(col, label, value, sub, color="blue"):
    col.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(col1, "% Cumplimiento", f"{pct_cumplimiento}%", f"{finalizados:,} de {total:,} finalizaron", "green" if pct_cumplimiento >= 95 else "orange" if pct_cumplimiento >= 70 else "red")
kpi(col2, "No cumplen", f"{no_cumplen:,}", f"{pct_incump}% del total asignado", "red" if pct_incump > 30 else "orange")
kpi(col3, "% Aprobados", f"{pct_aprobados}%", f"{aprobados:,} de {total:,} aprobados", "green" if pct_aprobados >= 90 else "orange")
kpi(col4, "Nota Promedio", f"{nota_prom}", "Sobre 100 puntos", "green" if nota_prom >= 90 else "orange" if nota_prom >= 70 else "red")
kpi(col5, "Mejora (Delta)", f"+{delta_prom}" if delta_prom >= 0 else str(delta_prom), "Diagnóstica → Final", "green" if delta_prom >= 15 else "orange")
kpi(col6, "Velocidad Promedio", f"{velocidad_prom:.1f} hrs", "Tiempo promedio de finalización", "green" if velocidad_prom <= 1.5 else "orange" if velocidad_prom <= 2.5 else "red")

st.markdown("")

# ── Fila 2: Gráficas principales ──────────────────────────────────────────────
cola, colb = st.columns([1, 1])

with cola:
    st.markdown('<div class="section-title">📈 Cumplimiento por Centro de Trabajo</div>', unsafe_allow_html=True)

    grp = df.groupby('Sucursal').agg(
        total=('Código Empleado', 'count'),
        aprobados=('finalizo', 'sum')
    ).reset_index()
    grp['pct'] = (grp['aprobados'] / grp['total'] * 100).round(1)
    grp = grp.sort_values('pct', ascending=True)
    grp['color'] = grp['pct'].apply(lambda x: '#10B981' if x >= 85 else '#F59E0B' if x >= 65 else '#EF4444')
    fig = go.Figure(go.Bar(
        x=grp['pct'], y=grp['Sucursal'], orientation='h',
        marker_color=grp['color'],
        text=grp['pct'].apply(lambda x: f"{x}%"),
        textposition='outside',
        customdata=grp[['total', 'aprobados']],
        hovertemplate='<b>%{y}</b><br>Cumplimiento: %{x}%<br>Finalizados: %{customdata[1]} / %{customdata[0]}<extra></extra>'
    ))
    fig.add_vline(x=85, line_dash="dash", line_color="#6B7280", annotation_text="Meta 85%", annotation_position="top right")
    fig.update_layout(
        height=max(350, len(grp) * 28),
        margin=dict(l=0, r=60, t=10, b=10),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor='#F3F4F6'),
        yaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor='white', paper_bgcolor='white',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with colb:
    st.markdown('<div class="section-title">✅ Estado de Aprobaciones</div>', unsafe_allow_html=True)
    estados = df['Estado Aprobación'].value_counts().reset_index()
    estados.columns = ['Estado', 'Cantidad']
    color_map = {'Aprobado': '#10B981', 'Desaprobado': '#EF4444', 'En progreso': '#F59E0B'}
    fig2 = go.Figure(go.Pie(
        labels=estados['Estado'],
        values=estados['Cantidad'],
        hole=0.55,
        marker_colors=[color_map.get(e, '#9CA3AF') for e in estados['Estado']],
        textinfo='label+percent',
        textfont_size=13,
        hovertemplate='<b>%{label}</b><br>%{value:,} personas (%{percent})<extra></extra>'
    ))
    fig2.add_annotation(text=f"<b>{total:,}</b><br>registros", x=0.5, y=0.5,
                        font_size=16, showarrow=False, align='center')
    fig2.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='white', showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Estado de cursos
    st.markdown('<div class="section-title">🕒 Estado de Cursos</div>', unsafe_allow_html=True)
    ec = df['Estado curso'].value_counts().reset_index()
    ec.columns = ['Estado', 'Cantidad']
    cmap2 = {'Finalizado a tiempo': '#10B981', 'No finalizado': '#EF4444', 'Finalizado atrasado': '#F59E0B'}
    fig3 = px.bar(ec, x='Cantidad', y='Estado', orientation='h',
                  color='Estado', color_discrete_map=cmap2,
                  text='Cantidad')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(
        height=180, margin=dict(l=0, r=60, t=5, b=5),
        showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6'),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Fila 3: Tabla de colaboradores ────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">Detalle de Colaboradores</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📉 No cumplen", "📈 Aprobados"])

def tabla_colaboradores(data, estado_filter):
    sub = data[data['Estado curso'].isin(estado_filter)].copy()
    sub = sub[['Nombre y apellido', 'Sucursal', 'Curso', 'Estado Aprobación',
               'Estado curso', 'Evaluación Diagnóstica - Nota',
               'Evaluación Final - Nota', 'Delta Puntaje']].copy()
    sub.columns = ['Colaborador', 'Sucursal', 'Curso', 'Estado Aprobación',
                   'Estado Curso', 'Diagnóstica', 'Final', 'Δ Mejora']
    sub = sub.sort_values('Final')
    return sub

with tab1:
    t1 = tabla_colaboradores(df, ['No finalizado', 'Finalizado atrasado'])
    st.markdown(f"**{len(t1):,} colaboradores sin cumplir**")

    def badge_estado(val):
        if val == 'No finalizado' or val == 'Desaprobado':
            return 'background-color: #FEE2E2; color: #991B1B; border-radius: 4px; padding: 2px 6px;'
        elif val == 'Finalizado atrasado' or val == 'En progreso':
            return 'background-color: #FEF3C7; color: #92400E; border-radius: 4px; padding: 2px 6px;'
        elif val == 'Finalizado a tiempo' or val == 'Aprobado':
            return 'background-color: #D1FAE5; color: #065F46; border-radius: 4px; padding: 2px 6px;'
        return ''

    st.dataframe(
        t1.style.map(badge_estado, subset=['Estado Curso', 'Estado Aprobación'])
               .format({'Diagnóstica': '{:.0f}', 'Final': '{:.0f}', 'Δ Mejora': '{:+.0f}'}),
        use_container_width=True,
        height=350
    )

with tab2:
    t2 = tabla_colaboradores(df, ['Finalizado a tiempo'])
    st.markdown(f"**{len(t2):,} colaboradores aprobados**")
    st.dataframe(
        t2.style.map(badge_estado, subset=['Estado Curso', 'Estado Aprobación'])
            .format({'Diagnóstica': '{:.0f}', 'Final': '{:.0f}', 'Δ Mejora': '{:+.0f}'}),
            use_container_width=True,
            height=350
    )

# ── Fila 4: Notas y Delta ──────────────────────────────────────────────────────
st.markdown("---")
colc, cold = st.columns([1, 1])

with colc:
    st.markdown('<div class="section-title">📊 Nota Diagnóstica vs Final por Centro</div>', unsafe_allow_html=True)

    grp2 = df[df['Evaluación Diagnóstica - Nota'] > 0].groupby('Sucursal').agg(
        diag=('Evaluación Diagnóstica - Nota', 'mean'),
        final=('Evaluación Final - Nota', 'mean')
    ).reset_index().round(1)
    grp2 = grp2.sort_values('final', ascending=False).head(15)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name='Diagnóstica', x=grp2['Sucursal'], y=grp2['diag'],
                            marker_color='#93C5FD', text=grp2['diag'], textposition='outside'))
    fig4.add_trace(go.Bar(name='Final', x=grp2['Sucursal'], y=grp2['final'],
                            marker_color='#1D4ED8', text=grp2['final'], textposition='outside'))
    fig4.update_layout(
        barmode='group', height=320,
        margin=dict(l=0, r=0, t=10, b=80),
        plot_bgcolor='white', paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='top', y=1.12, xanchor='right', x=1),
        xaxis=dict(tickangle=-35, tickfont=dict(size=10)),
        yaxis=dict(range=[0, 115], showgrid=True, gridcolor='#F3F4F6')
    )
    st.plotly_chart(fig4, use_container_width=True)

with cold:
    st.markdown('<div class="section-title">🚀 Mejora de Conocimiento (Delta Promedio)</div>', unsafe_allow_html=True)
    grp3 = df[df['Delta Puntaje'] > 0].groupby('Sucursal')['Delta Puntaje'].mean().reset_index()
    grp3.columns = ['Grupo', 'Delta']
    grp3 = grp3.sort_values('Delta', ascending=False).round(1)
    grp3['color'] = grp3['Delta'].apply(lambda x: '#10B981' if x >= 20 else '#F59E0B' if x >= 10 else '#EF4444')
    fig5 = go.Figure(go.Bar(
        x=grp3['Grupo'], y=grp3['Delta'],
        marker_color=grp3['color'],
        text=grp3['Delta'].apply(lambda x: f"+{x}"),
        textposition='outside'
    ))
    fig5.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=80),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(tickangle=-35, tickfont=dict(size=10)),
        yaxis=dict(range=[0, grp3['Delta'].max() + 15 if len(grp3) else 50],
                   showgrid=True, gridcolor='#F3F4F6', title="Puntos de mejora")
    )
    st.plotly_chart(fig5, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#9CA3AF; font-size:14px; padding:8px 0;'>
    Almacenes Vidrí S.A. de C.V. - Actualización semanal - Desarrollado por Dereck Méndez (2026)
</div>
""", unsafe_allow_html=True)
