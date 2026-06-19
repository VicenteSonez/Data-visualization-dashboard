import nbformat as nbf

nb = nbf.v4.new_notebook()

markdown_intro = """
# Análisis del Crecimiento de la Brecha Salarial
Este análisis utiliza los datos de la encuesta Casen 2024 para visualizar cómo evoluciona la brecha salarial entre hombres y mujeres a lo largo del ciclo vital (edad). 

Se seleccionan las siguientes variables según el Libro de Códigos:
- `activ` == 1: Filtra solo a las personas **ocupadas**.
- `yoprcor`: Mide el **ingreso de la ocupación principal**, que refleja con mayor precisión la compensación directa por el trabajo.
- `edad`: Permite agrupar en rangos quinquenales para ver el **crecimiento o decrecimiento** temporal.
- `sexo`: Para comparar hombres y mujeres.

El gráfico utiliza un diseño interactivo moderno con sombreado dinámico para destacar el crecimiento de la brecha.
"""

code_cell = """
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Carga y preparación de los datos
df = pd.read_parquet('../Data/casen_2024.parquet')

# Filtramos personas ocupadas (activ == 1) con ingresos de ocupación principal mayores a 0
df_ocupados = df[(df['activ'] == 1.0) & (df['yoprcor'] > 0)].copy()

# Definimos rangos de edad quinquenales para observar la evolución a lo largo del ciclo de vida laboral
bins = list(range(20, 75, 5)) + [100]
labels = [f'{i}-{i+4}' for i in range(20, 70, 5)] + ['70+']
df_ocupados['rango_edad'] = pd.cut(df_ocupados['edad'], bins=bins, labels=labels, right=False)

# Calculamos el ingreso promedio por rango de edad y sexo
df_brecha = df_ocupados.groupby(['rango_edad', 'sexo'], observed=True)['yoprcor'].mean().unstack()
df_brecha.columns = ['Hombre', 'Mujer']
df_brecha = df_brecha.reset_index()

# Calculamos la brecha absoluta y porcentual
df_brecha['Brecha'] = df_brecha['Hombre'] - df_brecha['Mujer']
df_brecha['Brecha_Porcentaje'] = (df_brecha['Brecha'] / df_brecha['Hombre']) * 100

# 2. Configuración de diseño Premium (Aesthetics)
color_hombre = '#1A365D' # Azul marino profundo
color_mujer = '#E53E3E'  # Rojo vibrante
color_brecha = '#ED8936' # Naranja para la brecha
bg_color = '#F7FAFC'     # Fondo ligeramente gris-azulado claro

# 3. Creación del gráfico
# Usamos subplots para combinar las líneas de ingreso y un bar chart de la brecha porcentual
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.75, 0.25],
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        '<b>Evolución del Ingreso Promedio: Hombres vs Mujeres</b>', 
        '<b>Brecha Salarial (%) relativa al Hombre</b>'
    )
)

# --- PANEL SUPERIOR: Líneas de Ingreso ---
# Línea de Mujeres (Abajo, para que el área sombreada suba hasta la de hombres)
fig.add_trace(go.Scatter(
    x=df_brecha['rango_edad'],
    y=df_brecha['Mujer'],
    name='Mujeres',
    mode='lines+markers',
    line=dict(color=color_mujer, width=3.5, shape='spline'),
    marker=dict(size=8, symbol='circle', line=dict(color='white', width=1)),
    hovertemplate='<b>Rango:</b> %{x}<br><b>Ingreso:</b> $%{y:,.0f}<extra></extra>'
), row=1, col=1)

# Línea de Hombres con sombreado (fill='tonexty') hacia la línea de Mujeres
fig.add_trace(go.Scatter(
    x=df_brecha['rango_edad'],
    y=df_brecha['Hombre'],
    name='Hombres',
    mode='lines+markers',
    line=dict(color=color_hombre, width=3.5, shape='spline'),
    marker=dict(size=8, symbol='square', line=dict(color='white', width=1)),
    fill='tonexty', # Rellena el área entre la línea de mujeres y la de hombres
    fillcolor='rgba(229, 62, 62, 0.15)', # Rojo transparente para destacar la "pérdida" o brecha
    hovertemplate='<b>Rango:</b> %{x}<br><b>Ingreso:</b> $%{y:,.0f}<extra></extra>'
), row=1, col=1)


# --- PANEL INFERIOR: Barras de Brecha Porcentual ---
fig.add_trace(go.Bar(
    x=df_brecha['rango_edad'],
    y=df_brecha['Brecha_Porcentaje'],
    name='Brecha Salarial (%)',
    marker_color=color_brecha,
    marker_line=dict(width=0),
    hovertemplate='<b>Rango:</b> %{x}<br><b>Brecha:</b> %{y:.1f}%<extra></extra>'
), row=2, col=1)

# 4. Ajustes de Layout (Typography, Grids, Backgrounds)
fig.update_layout(
    title=dict(
        text='<b>Crecimiento de la Brecha Salarial por Ciclo Vital</b><br><span style="font-size: 14px; color: #718096">Análisis sobre el ingreso de la ocupación principal en personas empleadas (Casen 2024)</span>',
        font=dict(family='Inter, Roboto, sans-serif', size=24, color='#2D3748'),
        x=0.05,
        y=0.96
    ),
    plot_bgcolor='white',
    paper_bgcolor=bg_color,
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='right',
        x=0.95,
        font=dict(family='Inter', size=12),
        bgcolor='rgba(255, 255, 255, 0.8)'
    ),
    height=800,
    margin=dict(t=120, b=50, l=80, r=40)
)

# Ajustes específicos para los ejes
fig.update_xaxes(
    title_text='Rango de Edad', 
    row=2, col=1, 
    showgrid=False,
    tickfont=dict(family='Inter', size=12, color='#4A5568')
)
fig.update_xaxes(
    showgrid=False, 
    row=1, col=1,
    tickfont=dict(family='Inter', size=12, color='#4A5568')
)

fig.update_yaxes(
    title_text='Ingreso Promedio (CLP)', 
    tickformat='$,.0f', 
    gridcolor='#E2E8F0', 
    zerolinecolor='#CBD5E0',
    row=1, col=1,
    tickfont=dict(family='Inter', size=12, color='#4A5568')
)
fig.update_yaxes(
    title_text='Brecha (%)', 
    ticksuffix='%', 
    gridcolor='#E2E8F0', 
    zerolinecolor='#CBD5E0',
    row=2, col=1,
    tickfont=dict(family='Inter', size=12, color='#4A5568')
)

# Agregar anotación destacando el punto de mayor brecha
idx_max_gap = df_brecha['Brecha_Porcentaje'].idxmax()
rango_max = df_brecha.loc[idx_max_gap, 'rango_edad']
brecha_max = df_brecha.loc[idx_max_gap, 'Brecha_Porcentaje']

fig.add_annotation(
    x=rango_max,
    y=brecha_max,
    xref='x2', yref='y2',
    text=f"Máxima brecha: {brecha_max:.1f}%",
    showarrow=True,
    arrowhead=2,
    arrowcolor='#C05621',
    arrowsize=1.5,
    arrowwidth=2,
    ax=-40,
    ay=-40,
    font=dict(family='Inter', size=12, color='#C05621'),
    bgcolor='white',
    bordercolor='#C05621',
    borderwidth=1,
    borderpad=4
)

fig.show()
"""

nb.cells.append(nbf.v4.new_markdown_cell(markdown_intro))
nb.cells.append(nbf.v4.new_code_cell(code_cell))

with open('../Tarea_2/Grafico6.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook created successfully.")
