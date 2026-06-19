import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
df = pd.read_parquet('data/casen_2024.parquet')
df.head()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 1. Load data
df = pd.read_parquet('data/casen_2024.parquet')

# 2. Filter data: Superior completa, Ocupados, Con ingresos
df_filtered = df[(df['educc'] == 6) & (df['activ'] == 1) & (df['ytrabajocor'] > 0)].copy()

# 3. Map categories (sentence case)
area_map = {
    1.0: 'Educación',
    2.0: 'Artes y humanidades',
    3.0: 'Ciencias soc., periodismo e inf.',
    4.0: 'Admin. de empresas y derecho',
    5.0: 'Ciencias nat., mat. y estadística',
    6.0: 'TIC',
    7.0: 'Ing., industria y construcción',
    8.0: 'Agr., silv., pesca y vet.',
    9.0: 'Salud y bienestar',
    10.0: 'Servicios'
}
sexo_map = {
    1: 'Hombre',
    2: 'Mujer'
}

df_filtered['area_nombre'] = df_filtered['cinef13_area'].map(area_map)
df_filtered['sexo_nombre'] = df_filtered['sexo'].map(sexo_map)

# Remove NaNs
df_filtered = df_filtered.dropna(subset=['area_nombre'])

# Set style
sns.set_theme(style="whitegrid")

# Calculate medians for sorting
medians = df_filtered.groupby('area_nombre')['ytrabajocor'].median().sort_values(ascending=False)
ordered_areas = medians.index

# ==================================================
# GRAFICO: Ingreso mediano por área segmentado por género
# ==================================================
plt.figure(figsize=(12, 7))

ax = sns.barplot(
    x='ytrabajocor', 
    y='area_nombre', 
    hue='sexo_nombre', 
    data=df_filtered, 
    estimator=np.median, 
    order=ordered_areas, 
    errorbar=None, 
    palette='Set2'
)

# Centered and highlighted title
plt.title(
    'Ingreso principal mediano por área de estudio y género', 
    fontsize=18, 
    fontweight='bold',
    pad=25,
    loc='center'
)

plt.xlabel('Ingreso mediano (CLP)', fontsize=12)
plt.ylabel('Área de estudio', fontsize=12)
plt.legend(title='Género')

# Number formatting
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(',', '.')))

plt.tight_layout()
plt.show()
plt.close()


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Filtros base
df_filtered = df[(df['educc'] == 6) & (df['activ'] == 1)].copy()
# Filtrar solo respuestas válidas de contrato (0: No, 1: Sí)
df_filtered = df_filtered[df_filtered['contrato'].isin([0, 1])]

# Mapeos
area_map = {
    1.0: 'Educación', 2.0: 'Artes y hum.', 3.0: 'Cs. sociales',
    4.0: 'Admin. y derecho', 5.0: 'Cs. naturales', 6.0: 'TIC',
    7.0: 'Ing. y constr.', 8.0: 'Agricultura', 9.0: 'Salud', 10.0: 'Servicios'
}
sexo_map = {1: 'Hombre', 2: 'Mujer'}

df_filtered['area_nombre'] = df_filtered['cinef13_area'].map(area_map)
df_filtered['sexo_nombre'] = df_filtered['sexo'].map(sexo_map)
df_filtered = df_filtered.dropna(subset=['area_nombre'])

# Calcular porcentajes
grouped = df_filtered.groupby(['area_nombre', 'sexo_nombre', 'contrato']).size().unstack(fill_value=0)
grouped.columns = ['Sin contrato', 'Con contrato']
grouped_pct = grouped.div(grouped.sum(axis=1), axis=0) * 100

# Ordenar áreas según porcentaje de hombres con contrato
order = grouped_pct.xs('Hombre', level='sexo_nombre')['Con contrato'].sort_values(ascending=False).index

plt.figure(figsize=(14, 8))
plt.style.use('seaborn-v0_8-whitegrid')

areas = order.tolist()
x = np.arange(len(areas))
width = 0.35

# Separar datos
h_con = [grouped_pct.loc[(area, 'Hombre'), 'Con contrato'] if (area, 'Hombre') in grouped_pct.index else 0 for area in areas]
h_sin = [grouped_pct.loc[(area, 'Hombre'), 'Sin contrato'] if (area, 'Hombre') in grouped_pct.index else 0 for area in areas]
m_con = [grouped_pct.loc[(area, 'Mujer'), 'Con contrato'] if (area, 'Mujer') in grouped_pct.index else 0 for area in areas]
m_sin = [grouped_pct.loc[(area, 'Mujer'), 'Sin contrato'] if (area, 'Mujer') in grouped_pct.index else 0 for area in areas]

# Colores cualitativos suaves (Set2 inspirados)
color_con = '#66c2a5' # Verde suave (Con contrato)
color_sin = '#fc8d62' # Naranja suave (Sin contrato)

# Barras Hombres (Izquierda)
plt.bar(x - width/2, h_con, width, label='Con contrato (H)', color=color_con, edgecolor='white')
plt.bar(x - width/2, h_sin, width, bottom=h_con, label='Sin contrato (H)', color=color_sin, edgecolor='white', hatch='//')

# Barras Mujeres (Derecha, con transparencia)
plt.bar(x + width/2, m_con, width, label='Con contrato (M)', color=color_con, edgecolor='white', alpha=0.7)
plt.bar(x + width/2, m_sin, width, bottom=m_con, label='Sin contrato (M)', color=color_sin, edgecolor='white', hatch='//', alpha=0.7)

# Detalles de diseño
plt.title('Brecha de formalidad laboral: porcentaje de trabajadores con contrato por área y género', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Porcentaje (%)', fontsize=12)
plt.xticks(x, areas, rotation=45, ha='right', fontsize=11)
plt.ylim(0, 105)

# Textos sobre las barras
for i in range(len(areas)):
    plt.text(x[i] - width/2, h_con[i]/2, f'{h_con[i]:.0f}%', ha='center', va='center', color='black', fontsize=9)
    plt.text(x[i] + width/2, m_con[i]/2, f'{m_con[i]:.0f}%', ha='center', va='center', color='black', fontsize=9)

# Leyenda unificada
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=color_con, edgecolor='white', label='Con contrato'),
    Patch(facecolor=color_sin, hatch='//', edgecolor='white', label='Sin contrato'),
    Patch(facecolor='gray', edgecolor='white', label='Columna Izq: Hombres'),
    Patch(facecolor='gray', edgecolor='white', alpha=0.5, label='Columna Der: Mujeres')
]
plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.show()

import pandas as pd
import plotly.express as px

# 1. Carga de datos
df = pd.read_parquet('data/casen_2024.parquet')

# Filtramos: Considerar solo a personas ocupadas o con ingresos
df = df[(df['activ'] == 1) | (df['ytotcor'] > 0)].copy()

# 2. Transformaciones y agrupaciones necesarias
df['I_1.5'] = (df['y1'] > 1500000).astype(int)

def agrupar_nse(nse):
    if pd.isna(nse): return None
    val = int(nse)
    if val in [1, 4]: return '1. Vulnerabilidad Alta'
    elif val in [2, 6]: return '2. Vulnerabilidad Media'
    elif val in [3, 7]: return '3. Vulnerabilidad Baja'
    else: return None
    
df['Nivel Vulnerabilidad'] = df['nse'].apply(agrupar_nse)

# Limpiamos nulos en las variables a utilizar
df_bar = df.dropna(subset=['Nivel Vulnerabilidad', 'y1']).copy()
df_bar['Status Ingreso'] = df_bar['I_1.5'].map({1: 'Gana > $1.5M', 0: 'Gana <= $1.5M'})

# 3. Cálculo de cantidades y porcentajes (usando el factor de expansión 'expr')
agg_df = df_bar.groupby(['Nivel Vulnerabilidad', 'Status Ingreso'])['expr'].sum().reset_index()
agg_df.rename(columns={'expr': 'Población'}, inplace=True)

# Porcentaje por columna
agg_df['Porcentaje_Num'] = agg_df.groupby('Nivel Vulnerabilidad')['Población'].transform(lambda x: (x / x.sum()) * 100)

# Referencia para ordenar de menor a mayor éxito
order_ref = agg_df[agg_df['Status Ingreso'] == 'Gana > $1.5M'].sort_values('Porcentaje_Num')['Nivel Vulnerabilidad'].tolist()

# Paleta Set2
color_palette = px.colors.qualitative.Set2

# 4. Generación del gráfico
fig6 = px.bar(agg_df, 
              x="Nivel Vulnerabilidad", 
              y="Porcentaje_Num", 
              color="Status Ingreso",
              text=agg_df['Porcentaje_Num'].apply(lambda x: f'{x:.1f}%'), # <--- Mostramos texto siempre
              orientation='v',
              category_orders={"Nivel Vulnerabilidad": order_ref, 
                               "Status Ingreso": ['Gana <= $1.5M', 'Gana > $1.5M']},
              color_discrete_map={'Gana > $1.5M': color_palette[1], 'Gana <= $1.5M': color_palette[2]}, 
              hover_data={'Porcentaje_Num': ':.1f', 'Población': ':,.0f'})

# Ajustes visuales de las trazas
fig6.update_traces(
    textposition='inside', 
    textfont=dict(size=13, color='black'),
    marker_line_color='white',
    marker_line_width=1
)

# Ajustes del layout del gráfico
fig6.update_layout(
    height=700, # <--- Gráfico más alto
    title="Distribución de Ingresos > $1.5M según Nivel de Vulnerabilidad",
    yaxis_title="Distribución Porcentual (%)",
    xaxis_title="Nivel de Vulnerabilidad",
    legend_title="Estado de Ingresos",
    yaxis=dict(ticksuffix="%", range=[0, 100]),
    uniformtext_minsize=10 # <--- uniformtext_mode='hide' removido
)

# Mostrar en el Notebook
fig6.show()


import pandas as pd
import matplotlib.pyplot as plt

# 1. Carga de datos y filtrado
df = pd.read_parquet('data/casen_2024.parquet')
df = df[(df['activ'] == 1) | (df['ytotcor'] > 0)].copy()

df['I_1.5'] = (df['y1'] > 1500000).astype(int)

# 2. Agrupación y mapeo de NSE
def agrupar_nse(nse):
    if pd.isna(nse): return None
    val = int(nse)
    map_nse = {
        1: 'Alto',
        2: 'Medio',
        3: 'Bajo',
        4: 'Medio-Alto',
        5: 'Bajo-Alto',
        6: 'Bajo-Medio-Alto',
        7: 'Bajo-Medio'
    }
    label = map_nse.get(val)
    if label == 'Bajo-Alto': return None  # Filtramos explícitamente el nivel Bajo-Alto
    return label
    
df['Nivel Vulnerabilidad'] = df['nse'].apply(agrupar_nse)

# Nos quedamos con los datos válidos
df_bar = df.dropna(subset=['Nivel Vulnerabilidad', 'y1']).copy()
df_bar['Status Ingreso'] = df_bar['I_1.5'].map({1: 'Gana > $1.5M', 0: 'Gana <= $1.5M'})

# 3. Cálculo de Porcentajes Ponderados
agg_df = df_bar.groupby(['Nivel Vulnerabilidad', 'Status Ingreso'])['expr'].sum().reset_index()

# Pivotamos la tabla para que sea más fácil graficar con Matplotlib
pivot_df = agg_df.pivot(index='Nivel Vulnerabilidad', columns='Status Ingreso', values='expr').fillna(0)

# Convertimos a porcentajes (cada fila sumará 100%)
pivot_pct = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

# Ordenamos por los que más ganan sobre 1.5M
pivot_pct = pivot_pct.sort_values(by='Gana > $1.5M')

# Aseguramos el orden de las columnas para el apilado
pivot_pct = pivot_pct[['Gana <= $1.5M', 'Gana > $1.5M']]

# 4. Generación del gráfico estático
fig, ax = plt.subplots(figsize=(10, 8))

# Colores (Gris y Verde oscuro)
colors = ['#EF959D', '#C0F8D1'] 

# Dibujar las barras apiladas
pivot_pct.plot(kind='bar', stacked=True, color=colors, ax=ax, edgecolor='white', width=0.7)

# Añadir etiquetas de porcentaje dentro de cada bloque de las barras
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    if height > 0: # Evitar poner texto en barras vacías
        # Elegir color de fuente dependiendo de qué segmento sea para mantener legibilidad
        text_color = 'black'
        
        ax.text(x + width/2, 
                y + height/2, 
                f'{height:.1f}%', 
                ha='center', 
                va='center', 
                color=text_color, 
                fontsize=11,
                fontweight='bold')

# Configuración estética del gráfico
ax.set_title("Niveles de ingresos por vulnerabilidad del sector de vivienda", fontsize=15, pad=20)
ax.set_xlabel("Índice de vulnerabilidad", fontsize=12, labelpad=10)
ax.set_ylabel("Distribución Porcentual (%)", fontsize=12, labelpad=10)
ax.set_ylim(0, 100)

# Rotar el texto del eje X para que no se superponga
plt.xticks(rotation=45, ha='right', fontsize=11)

# Posicionar la leyenda fuera del gráfico
ax.legend(title='Estado de Ingresos', bbox_to_anchor=(1.02, 1), loc='upper left')

# Evitar recortes
plt.tight_layout()

# Mostrar
plt.show()
