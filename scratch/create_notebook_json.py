import json

markdown_intro = """# Análisis del Crecimiento de la Brecha Salarial
Este análisis utiliza los datos de la encuesta Casen 2024 para visualizar cómo evoluciona la brecha salarial entre hombres y mujeres a lo largo del ciclo vital (edad). 

Se seleccionan las siguientes variables según el Libro de Códigos:
- `activ` == 1: Filtra solo a las personas **ocupadas**.
- `yoprcor`: Mide el **ingreso de la ocupación principal**, que refleja con mayor precisión la compensación directa por el trabajo.
- `edad`: Permite usar un valor continuo para visualizar el **crecimiento o decrecimiento** temporal en formato de línea.
- `sexo`: Para comparar hombres y mujeres.
"""

code_cell = """import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Carga y preparación de los datos
df = pd.read_parquet('../Data/casen_2024.parquet')

# Filtramos personas ocupadas (activ == 1.0) con ingresos de ocupación principal mayores a 0
# Además acotamos la edad a un rango laboral típico continuo (ej: 18 a 75 años)
df_ocupados = df[(df['activ'] == 1.0) & (df['yoprcor'] > 0) & (df['edad'] >= 18) & (df['edad'] <= 75)].copy()

# Calculamos el ingreso promedio exacto por edad y sexo
df_brecha = df_ocupados.groupby(['edad', 'sexo'], observed=True)['yoprcor'].mean().unstack()
df_brecha.columns = ['Hombre', 'Mujer']
df_brecha = df_brecha.reset_index()

# Suavizado de datos con media móvil para una curva más estética
df_brecha['Hombre_suave'] = df_brecha['Hombre'].rolling(window=3, center=True, min_periods=1).mean()
df_brecha['Mujer_suave'] = df_brecha['Mujer'].rolling(window=3, center=True, min_periods=1).mean()

# 2. Configuración de diseño Premium (Aesthetics)
color_hombre = '#2B5B84' # Azul elegante
color_mujer = '#C23B22'  # Rojo clásico sofisticado

# 3. Creación del gráfico
fig = go.Figure()

# Línea de Mujeres
fig.add_trace(go.Scatter(
    x=df_brecha['edad'],
    y=df_brecha['Mujer_suave'],
    name='Mujeres',
    mode='lines',
    line=dict(color=color_mujer, width=4.5, shape='spline', smoothing=1.3),
    hovertemplate='<b>Edad:</b> %{x} años<br><b>Ingreso Promedio:</b> $%{y:,.0f}<extra></extra>'
))

# Línea de Hombres con sombreado
fig.add_trace(go.Scatter(
    x=df_brecha['edad'],
    y=df_brecha['Hombre_suave'],
    name='Hombres',
    mode='lines',
    line=dict(color=color_hombre, width=4.5, shape='spline', smoothing=1.3),
    fill='tonexty', 
    fillcolor='rgba(194, 59, 34, 0.12)', # Sombreado rojo muy sutil y elegante
    hovertemplate='<b>Edad:</b> %{x} años<br><b>Ingreso Promedio:</b> $%{y:,.0f}<extra></extra>'
))

# 4. Ajustes de Layout (Typography, Grids, Backgrounds)
fig.update_layout(
    title=dict(
        text='<b>Crecimiento de la Brecha Salarial por Edad</b>',
        font=dict(family='Inter, Roboto, Arial, sans-serif', size=28, color='#1A202C'),
        x=0.02,
        y=0.96
    ),
    xaxis=dict(
        title='<b>Edad (Años)</b>',
        showgrid=False,
        showline=True,
        linecolor='rgba(0,0,0,0.3)',
        linewidth=2,
        tickfont=dict(family='Inter, Arial', size=15, color='#4A5568'),
        titlefont=dict(family='Inter, Arial', size=18, color='#2D3748'),
        dtick=5,
        range=[18, 75]
    ),
    yaxis=dict(
        title='<b>Ingreso Promedio (CLP)</b>',
        tickformat='$,.0f',
        gridcolor='rgba(0, 0, 0, 0.08)',
        gridwidth=1.5,
        griddash='dot', # Grilla punteada elegante
        zeroline=False,
        showline=False,
        tickfont=dict(family='Inter, Arial', size=15, color='#4A5568'),
        titlefont=dict(family='Inter, Arial', size=18, color='#2D3748')
    ),
    plot_bgcolor='rgba(0,0,0,0)',  # Fondo transparente (estilo PNG)
    paper_bgcolor='rgba(0,0,0,0)', # Fondo transparente (estilo PNG)
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='right',
        x=0.98,
        font=dict(family='Inter, Arial', size=16, color='#2D3748'),
        bgcolor='rgba(255, 255, 255, 0)', # Leyenda transparente
        itemwidth=40
    ),
    height=650,
    margin=dict(t=120, b=80, l=90, r=40),
    hoverlabel=dict(
        bgcolor="white",
        font_size=15,
        font_family="Inter"
    )
)

fig.show()
"""

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\\n" for line in markdown_intro.split('\\n')]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\\n" for line in code_cell.split('\\n')]
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('../Tarea_2/Grafico6.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)
