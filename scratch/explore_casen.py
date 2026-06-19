import pandas as pd
import numpy as np

df = pd.read_parquet('../Data/casen_2024.parquet')
df_ocup = df[(df['activ'] == 1.0) & (df['yoprcor'] > 0)].copy()

# Bins for age
bins = [15, 24, 34, 44, 54, 64, 100]
labels = ['15-24', '25-34', '35-44', '45-54', '55-64', '65+']
df_ocup['edad_cat'] = pd.cut(df_ocup['edad'], bins=bins, labels=labels, right=True)

gap_df = df_ocup.groupby(['edad_cat', 'sexo'], observed=True)['yoprcor'].mean().unstack()
gap_df.columns = ['Hombre', 'Mujer']
gap_df['Brecha'] = gap_df['Hombre'] - gap_df['Mujer']
gap_df['Brecha %'] = gap_df['Brecha'] / gap_df['Hombre'] * 100

print("Brecha por edad:")
print(gap_df)

# Check by education level
# Is there 'esc' variable?
if 'esc' in df.columns:
    df_ocup['esc_cat'] = pd.cut(df_ocup['esc'], bins=[0, 8, 12, 16, 22], labels=['Basica', 'Media', 'Superior Incompleta', 'Superior Completa o mas'])
    gap_esc = df_ocup.groupby(['esc_cat', 'sexo'], observed=True)['yoprcor'].mean().unstack()
    gap_esc.columns = ['Hombre', 'Mujer']
    gap_esc['Brecha'] = gap_esc['Hombre'] - gap_esc['Mujer']
    gap_esc['Brecha %'] = gap_esc['Brecha'] / gap_esc['Hombre'] * 100
    print("\nBrecha por escolaridad:")
    print(gap_esc)

