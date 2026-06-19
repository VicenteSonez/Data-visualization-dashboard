import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# 1. Cargar los datos (solo las columnas necesarias para no saturar la memoria)
# Si ya tenías el df cargado, puedes saltar esta línea y usar tu df
df = pd.read_parquet('Data/casen_2024.parquet', columns=['educc', 'qaut', 'activ'])
import plotly.graph_objects as go
# 1. Filtrar: Excluir 'No sabe' en educación Y dejar solo a los 'Ocupados' (activ == 1)
df_alluvial = df[(df['educc'] != -88) & (df['activ'] == 1)].copy()

# 2. Mapeos de categorías
educc_map = {
    0: 'Educación media incompleta o inferior',
    1: 'Educación media incompleta o inferior',
    2: 'Educación media incompleta o inferior',
    3: 'Educación media incompleta o inferior',
    4: 'Educación media completa / sup. incompleta',
    5: 'Educación media completa / sup. incompleta',
    6: 'Educación superior completa'
}

qaut_map = {
    1: 'Quintil 1',
    2: 'Quintil 2',
    3: 'Quintil 3',
    4: 'Quintil 4',
    5: 'Quintil 5'
}

df_alluvial['educc_label'] = df_alluvial['educc'].map(educc_map)
df_alluvial['qaut_label'] = df_alluvial['qaut'].map(qaut_map)
df_alluvial = df_alluvial.dropna(subset=['educc_label', 'qaut_label'])

# 3. Agrupar flujos
flujos = df_alluvial.groupby(['educc_label', 'qaut_label']).size().reset_index(name='cantidad')

# 4. DEFINICIÓN DE COLORES
# Colores semitransparentes para los flujos (basados en origen)
color_flujos_dict = {
    'Educación media incompleta o inferior': 'rgba(214, 39, 40, 0.5)',   # Rojo
    'Educación media completa / sup. incompleta': 'rgba(218, 165, 32, 0.5)',   # Dorado
    'Educación superior completa': 'rgba(31, 119, 180, 0.5)'    # Azul
}

# Colores sólidos para los nodos
color_nodos_dict = {
    'Quintil 1': 'rgba(120, 120, 120, 0.8)',
    'Quintil 2': 'rgba(120, 120, 120, 0.8)',
    'Quintil 3': 'rgba(120, 120, 120, 0.8)',
    'Quintil 4': 'rgba(120, 120, 120, 0.8)',
    'Quintil 5': 'rgba(120, 120, 120, 0.8)',
    # Colores primarios para los nodos de origen
    'Educación media incompleta o inferior': 'rgba(214, 39, 40, 0.8)',
    'Educación media completa / sup. incompleta': 'rgba(218, 165, 32, 0.8)',
    'Educación superior completa': 'rgba(31, 119, 180, 0.8)'
}

# Asignar color a los flujos
colores_enlaces = flujos['educc_label'].map(color_flujos_dict).tolist()

# 5. Preparar Nodos
nodos_origen = [
    'Educación media incompleta o inferior',
    'Educación media completa / sup. incompleta',
    'Educación superior completa'
]
nodos_destino = [qaut_map[i] for i in range(1, 6)]
todos_los_nodos = nodos_origen + nodos_destino

# Agregamos etiquetas HTML <b> para que todo el texto aparezca en Negrita y contraste mejor
etiquetas_en_negrita = [f"<b>{nodo}</b>" for nodo in todos_los_nodos]

indice_nodos = {nodo: i for i, nodo in enumerate(todos_los_nodos)}
colores_nodos_lista = [color_nodos_dict[nodo] for nodo in todos_los_nodos]

# 6. Preparar Enlaces
indices_origen = flujos['educc_label'].map(indice_nodos).tolist()
indices_destino = flujos['qaut_label'].map(indice_nodos).tolist()
valores = flujos['cantidad'].tolist()

# 7. Generar Gráfico
fig = go.Figure(data=[go.Sankey(
    textfont=dict(size=14), # Aumentamos el tamaño y dejamos que Plotly elija el color según el modo (claro/oscuro)
    node = dict(
      pad = 25,
      thickness = 30,
      line = dict(color = "black", width = 0.5),
      label = etiquetas_en_negrita, # Usamos las etiquetas con negrita
      color = colores_nodos_lista 
    ),
    link = dict(
      source = indices_origen,
      target = indices_destino,
      value = valores,
      color = colores_enlaces 
    )
)])

fig.update_layout(
    title_text="<b>Flujo de escolaridad hacia quintil de ingresos (solo personas ocupadas)</b>",
    font_size=13,
    height=600,
    margin=dict(t=50, l=50, r=50, b=50)
)

fig.show()
