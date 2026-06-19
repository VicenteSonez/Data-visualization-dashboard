import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import plotly.express as px
import os

os.makedirs('figures', exist_ok=True)

print("Cargando datos...")
df_full = pd.read_parquet('../Data/casen_2024.parquet')

# ==========================================
# PLOT 1: Alluvial / Sankey (Grafico1)
# ==========================================
print("Generando Plot 1 (Sankey)...")
df_alluvial = df_full[['educc', 'qaut', 'activ']].copy()
df_alluvial = df_alluvial[(df_alluvial['educc'] != -88) & (df_alluvial['activ'] == 1)].copy()

educc_map = {
    0: 'Educ. Media Inc. o inferior', 1: 'Educ. Media Inc. o inferior',
    2: 'Educ. Media Inc. o inferior', 3: 'Educ. Media Inc. o inferior',
    4: 'Educ. Media Comp. / Sup. Inc.', 5: 'Educ. Media Comp. / Sup. Inc.',
    6: 'Educ. Superior Completa'
}
qaut_map = {1: 'Quintil 1', 2: 'Quintil 2', 3: 'Quintil 3', 4: 'Quintil 4', 5: 'Quintil 5'}

df_alluvial['educc_label'] = df_alluvial['educc'].map(educc_map)
df_alluvial['qaut_label'] = df_alluvial['qaut'].map(qaut_map)
df_alluvial = df_alluvial.dropna(subset=['educc_label', 'qaut_label'])

flujos = df_alluvial.groupby(['educc_label', 'qaut_label']).size().reset_index(name='cantidad')

# Paleta Cálida para los Flujos y Nodos
color_flujos_dict = {
    'Educ. Media Inc. o inferior': 'rgba(186, 45, 50, 0.45)',     # Terracota/Rojo cálido
    'Educ. Media Comp. / Sup. Inc.': 'rgba(244, 162, 97, 0.45)',   # Naranja cálido
    'Educ. Superior Completa': 'rgba(233, 196, 106, 0.45)'         # Dorado/Amarillo
}

color_nodos_dict = {
    'Quintil 1': 'rgba(165, 140, 125, 0.8)',
    'Quintil 2': 'rgba(165, 140, 125, 0.8)',
    'Quintil 3': 'rgba(165, 140, 125, 0.8)',
    'Quintil 4': 'rgba(165, 140, 125, 0.8)',
    'Quintil 5': 'rgba(165, 140, 125, 0.8)',
    'Educ. Media Inc. o inferior': 'rgba(186, 45, 50, 0.8)',
    'Educ. Media Comp. / Sup. Inc.': 'rgba(244, 162, 97, 0.8)',
    'Educ. Superior Completa': 'rgba(233, 196, 106, 0.8)'
}

colores_enlaces = flujos['educc_label'].map(color_flujos_dict).tolist()

nodos_origen = ['Educ. Media Inc. o inferior', 'Educ. Media Comp. / Sup. Inc.', 'Educ. Superior Completa']
nodos_destino = [qaut_map[i] for i in range(1, 6)]
todos_los_nodos = nodos_origen + nodos_destino

indice_nodos = {nodo: i for i, nodo in enumerate(todos_los_nodos)}
colores_nodos_lista = [color_nodos_dict[nodo] for nodo in todos_los_nodos]

fig1 = go.Figure(data=[go.Sankey(
    textfont=dict(size=12, family="Inter, Roboto, Arial, sans-serif"),
    node = dict(pad=20, thickness=25, line=dict(color="black", width=0.5), label=todos_los_nodos, color=colores_nodos_lista),
    link = dict(
        source=flujos['educc_label'].map(indice_nodos).tolist(),
        target=flujos['qaut_label'].map(indice_nodos).tolist(),
        value=flujos['cantidad'].tolist(),
        color=colores_enlaces
    )
)])
fig1.update_layout(
    title=dict(
        text="<b>1. Flujo educativo a quintiles</b>",
        x=0.5,
        xanchor='center',
        font=dict(size=15, family="Arial", color='#2c3e50')
    ),
    width=900,
    height=550,
    margin=dict(t=60, l=40, r=40, b=40)
)
fig1.write_image("figures/plot1.png", scale=2)


# ==========================================
# PLOT 2: Dumbbell Plot (Grafico2)
# ==========================================
print("Generando Plot 2 (Dumbbell)...")
df2 = df_full[['cinef13_area', 'sexo', 'ytrabajocor']].copy()
df2 = df2.dropna()
df2 = df2[df2['cinef13_area'] >= 0]
df2 = df2[df2['sexo'].isin([1, 2])]

cine_map = {
    1.0: 'Salud y Bienestar', 2.0: 'Ingeniería y Const.', 3.0: 'Educación', 4.0: 'Servicios',
    5.0: 'Admin. y Derecho', 6.0: 'Ciencias Sociales', 7.0: 'Ciencias Naturales',
    8.0: 'Agric. y Veterinaria', 9.0: 'Informática (TIC)', 10.0: 'Artes y Humanidades', 11.0: 'Cs. Básicas (Doc.)'
}
df2['area_label'] = df2['cinef13_area'].map(cine_map)
df2['genero_label'] = df2['sexo'].map({1: 'Hombre', 2: 'Mujer'})
df2 = df2.dropna(subset=['area_label'])

stats = df2.groupby(['area_label', 'genero_label'], as_index=False)['ytrabajocor'].agg(promedio='mean', tamano='count')
area_order = df2.groupby('area_label')['ytrabajocor'].mean().sort_values(ascending=True).index
stats['area_label'] = pd.Categorical(stats['area_label'], categories=area_order, ordered=True)
stats = stats.sort_values('area_label')

sns.set_theme(style="white")
fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.grid(False)
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)
ax.xaxis.grid(False)

# Dibujar las líneas de conexión en tonos cálidos neutros
for area in area_order:
    area_data = stats[stats['area_label'] == area]
    if len(area_data) == 2:
        val_h = area_data[area_data['genero_label'] == 'Hombre']['promedio'].values[0]
        val_m = area_data[area_data['genero_label'] == 'Mujer']['promedio'].values[0]
        ax.plot([val_m, val_h], [area, area], color='#C8B19F', zorder=1, alpha=0.6, linestyle='--', linewidth=2)

size_factor = 1500 / stats['tamano'].max()
# Paleta cálida para Hombre (Bronce) y Mujer (Carmesí/Rojo)
colores = {'Hombre': '#D97706', 'Mujer': '#C23B22'}

for genero, color in colores.items():
    g_data = stats[stats['genero_label'] == genero]
    ax.scatter(g_data['promedio'], g_data['area_label'], s=g_data['tamano']*size_factor+60, color=color, label=genero, alpha=0.9, zorder=3, edgecolors='white', linewidth=1, clip_on=False)

ax.set_ylim(-0.8, len(area_order) - 0.2)

ax.set_title('2. Sueldo por área y género\n(El tamaño del punto indica el tamaño de la muestra)', fontname='Arial', fontsize=13, fontweight='bold', color='#2c3e50', pad=15)
ax.set_xlabel('Sueldo Promedio (CLP)', fontsize=10)
ax.set_ylabel('')
sns.despine(left=True, bottom=True)
formatter = ticker.FuncFormatter(lambda x, pos: f'${x/1000:,.0f}K'.replace(',', '.'))
ax.xaxis.set_major_formatter(formatter)
legend_elements = [
    mpatches.Patch(color='#D97706', label='Hombre'),
    mpatches.Patch(color='#C23B22', label='Mujer')
]
ax.legend(handles=legend_elements, title='Género', loc='lower right', frameon=True, facecolor='white', edgecolor='lightgray')
fig.subplots_adjust(left=0.20, right=0.94, top=0.83, bottom=0.20)
plt.savefig('figures/plot2.png', dpi=300)
plt.close()


# ==========================================
# PLOT 3: Heatmap (Grafico3)
# ==========================================
print("Generando Plot 3 (Heatmap)...")
df3 = df_full.dropna(subset=['region', 'sexo', 'yoprcor']).copy()
macrozona_mapping = {
    1: 'Z. Norte', 2: 'Z. Norte', 3: 'Z. Centro Norte', 4: 'Z. Centro Norte',
    5: 'Z. Centro', 6: 'Z. Centro', 7: 'Z. Centro Sur', 8: 'Z. Centro Sur',
    9: 'Z. Sur', 10: 'Z. Sur', 11: 'Z. Sur', 12: 'Z. Sur',
    13: 'Z. Centro', 14: 'Z. Sur', 15: 'Z. Norte', 16: 'Z. Centro Sur'
}
df3['Macrozona'] = df3['region'].map(macrozona_mapping)
macrozona_order = ['Z. Norte', 'Z. Centro Norte', 'Z. Centro', 'Z. Centro Sur', 'Z. Sur']
df3['Macrozona'] = pd.Categorical(df3['Macrozona'], categories=macrozona_order, ordered=True)
df3['Genero'] = df3['sexo'].map({1: 'Hombre', 2: 'Mujer'})
map_qaut = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4', 5: 'Q5'}
df3['qaut_label'] = df3['qaut'].map(map_qaut)
df3 = df3.dropna(subset=['qaut_label'])

pivot = df3.pivot_table(values='yoprcor', index='Macrozona', columns=['qaut_label', 'Genero'], aggfunc='mean', observed=False)
gap_df = pd.DataFrame(index=macrozona_order)
for cat in pivot.columns.levels[0]:
    try:
        gap_df[cat] = ((pivot[cat]['Hombre'] - pivot[cat]['Mujer']) / pivot[cat]['Hombre']) * 100
    except: pass
gap_df = gap_df.dropna(how='all', axis=1).T

fig, ax = plt.subplots(figsize=(9, 5.5))
# Heatmap con paleta cálida YlOrRd
sns.heatmap(gap_df, annot=True, fmt=".1f", cmap="YlOrRd", vmin=0, vmax=35, cbar_kws={'label': 'Brecha (%)'}, annot_kws={"weight": "bold"}, ax=ax)
ax.set_title('3. Brecha por macrozona y quintil', fontname='Arial', fontsize=13, fontweight='bold', color='#2c3e50', pad=15)
ax.set_xlabel('Macro-Zona')
ax.set_ylabel('Quintil')
fig.subplots_adjust(left=0.12, right=0.88, top=0.83, bottom=0.20)
plt.savefig('figures/plot3.png', dpi=300)
plt.close()


# ==========================================
# PLOT 4: Stacked Bar (Grafico4)
# ==========================================
print("Generando Plot 4 (Stacked Bar)...")
df4 = df_full[(df_full['activ'] == 1) | (df_full['ytotcor'] > 0)].copy()
df4['I_1.5'] = (df4['y1'] > 1500000).astype(int)

def agrupar_nse(nse):
    if pd.isna(nse): return None
    val = int(nse)
    map_nse = {1: 'Alto', 2: 'Medio', 3: 'Bajo', 4: 'Medio-Alto', 5: 'Bajo-Alto', 6: 'Bajo-Medio-Alto', 7: 'Bajo-Medio'}
    label = map_nse.get(val)
    if label == 'Bajo-Alto': return None
    return label

df4['Nivel Vulnerabilidad'] = df4['nse'].apply(agrupar_nse)
df_bar = df4.dropna(subset=['Nivel Vulnerabilidad', 'y1']).copy()
df_bar['Status'] = df_bar['I_1.5'].map({1: '> $1.5M', 0: '<= $1.5M'})

agg_df = df_bar.groupby(['Nivel Vulnerabilidad', 'Status'])['expr'].sum().reset_index()
pivot_df = agg_df.pivot(index='Nivel Vulnerabilidad', columns='Status', values='expr').fillna(0)
pivot_pct = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
pivot_pct = pivot_pct.sort_values(by='> $1.5M')
pivot_pct = pivot_pct[['<= $1.5M', '> $1.5M']]

fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.grid(False)

# Reemplazar verde por durazno/amarillo cálido
pivot_pct.plot(kind='bar', stacked=True, color=['#F3C68F', '#C23B22'], ax=ax, edgecolor='white', width=0.7)
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)
ax.xaxis.grid(False)

for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy()
    if height > 4:
        ax.text(x+width/2, y+height/2, f'{height:.1f}%', ha='center', va='center', color='black', fontsize=9, fontweight='bold')

ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])

ax.set_title("4. Ingresos por vulnerabilidad", fontname='Arial', fontsize=13, fontweight='bold', color='#2c3e50', pad=28)
ax.set_xlabel("Vulnerabilidad del Sector", fontsize=10)
ax.set_ylabel("Distribución (%)", fontsize=10)
plt.xticks(rotation=30, ha='right')
sns.despine(left=True, bottom=True)
ax.legend(title='Ingresos', bbox_to_anchor=(1.0, 1.02), loc='lower right', ncol=2, frameon=False, fontsize=8.5, title_fontsize=8.5)
fig.subplots_adjust(left=0.20, right=0.94, top=0.83, bottom=0.20)
plt.savefig('figures/plot4.png', dpi=300)
plt.close()


# ==========================================
# PLOT 5: Treemap (Grafico5 de Tarea_2)
# ==========================================
print("Generando Plot 5 (Treemap)...")
educc_map = {
    0: 'Sin Educ.<br>Formal', 1: 'Básica<br>Incom.', 2: 'Básica<br>Comp.',
    3: 'Media<br>Incom.', 4: 'Media<br>Comp.', 5: 'Sup.<br>Incom.', 6: 'Sup.<br>Comp.'
}
zona_map = {1: 'Urbano', 2: 'Rural'}

df_educ = df_full[(df_full['educc'] >= 0) & (df_full['area'].isin([1, 2]))].copy()
df_educ['Nivel Educacional'] = df_educ['educc'].map(educc_map)
df_educ['Zona'] = df_educ['area'].map(zona_map)

educ_zona_counts = df_educ.groupby(['Zona', 'Nivel Educacional']).size().reset_index(name='Cantidad')

# TreeMap con escala cálida 'Oranges'
fig5 = px.treemap(
    educ_zona_counts,
    path=['Zona', 'Nivel Educacional'],
    values='Cantidad',
    title='<b>5. Educación por zona</b>',
    color='Cantidad',
    color_continuous_scale='Oranges'
)

max_val = educ_zona_counts['Cantidad'].max()
step = 10000
tickvals = np.arange(0, max_val + step, step)
ticktext = [f"{int(v/1000)} mil" if v > 0 else "0" for v in tickvals]

fig5.update_layout(
    width=900,
    height=550,
    title=dict(
        text='<b>5. Educación por zona</b>',
        x=0.5,
        xanchor='center',
        font=dict(size=15, family='Arial', color='#2c3e50')
    ),
    font=dict(size=12, family="Arial", color='#2c3e50'),
    margin=dict(t=60, l=40, r=40, b=40),
    coloraxis_colorbar=dict(
        title="Cantidad",
        tickvals=tickvals,
        ticktext=ticktext,
        thickness=15
    )
)
fig5.update_traces(textfont=dict(size=14), hoverlabel=dict(font_size=12))
fig5.write_image("figures/plot5.png", scale=2)


# ==========================================
# PLOT 6: Line Chart (Grafico6 de Tarea_2)
# ==========================================
print("Generando Plot 6 (Línea de Crecimiento de Brecha)...")
df_ocupados = df_full[(df_full['activ'] == 1.0) & (df_full['yoprcor'] > 0) & (df_full['edad'] >= 18) & (df_full['edad'] <= 75)].copy()

df_brecha = df_ocupados.groupby(['edad', 'sexo'], observed=True)['yoprcor'].mean().unstack()
df_brecha.columns = ['Hombre', 'Mujer']
df_brecha = df_brecha.reset_index()

df_brecha['Hombre_suave'] = df_brecha['Hombre'].rolling(window=3, center=True, min_periods=1).mean()
df_brecha['Mujer_suave'] = df_brecha['Mujer'].rolling(window=3, center=True, min_periods=1).mean()

# Colores Cálidos: Bronce para Hombres, Rojo para Mujeres
color_hombre = '#D97706'
color_mujer = '#C23B22'

fig6 = go.Figure()

# Línea de Mujeres
fig6.add_trace(go.Scatter(
    x=df_brecha['edad'],
    y=df_brecha['Mujer_suave'],
    name='Mujeres',
    mode='lines',
    line=dict(color=color_mujer, width=3.5, shape='spline', smoothing=1.3)
))

# Línea de Hombres con sombreado cálido sutil
fig6.add_trace(go.Scatter(
    x=df_brecha['edad'],
    y=df_brecha['Hombre_suave'],
    name='Hombres',
    mode='lines',
    line=dict(color=color_hombre, width=3.5, shape='spline', smoothing=1.3),
    fill='tonexty',
    fillcolor='rgba(244, 162, 97, 0.12)' # Sombreado naranja suave
))

fig6.update_layout(
    title=dict(
        text='<b>6. Brecha salarial por edad</b>',
        font=dict(family='Arial', size=15, color='#2c3e50'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(
            text='<b>Edad (Años)</b>',
            font=dict(family='Arial', size=12, color='#2D3748')
        ),
        showgrid=False,
        showline=True,
        linecolor='rgba(0,0,0,0.3)',
        linewidth=1.5,
        tickfont=dict(family='Arial', size=11, color='#4A5568'),
        dtick=10,
        range=[18, 75]
    ),
    yaxis=dict(
        title=dict(
            text='<b>Ingreso Promedio (CLP)</b>',
            font=dict(family='Arial', size=12, color='#2D3748')
        ),
        tickformat='$,.0f',
        showgrid=True,
        gridcolor='rgba(0, 0, 0, 0.08)',
        gridwidth=1,
        griddash='dot',
        zeroline=False,
        showline=False,
        tickfont=dict(family='Arial', size=11, color='#4A5568')
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=0.98,
        font=dict(family='Arial', size=11, color='#2D3748'),
        bgcolor='rgba(255, 255, 255, 0)'
    ),
    width=900,
    height=550,
    margin=dict(t=60, l=40, r=40, b=40)
)
fig6.write_image("figures/plot6.png", scale=2)

print("Proceso completado exitosamente.")
