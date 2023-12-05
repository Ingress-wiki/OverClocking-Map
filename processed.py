import pandas as pd

file_path = 'POIsLightshipDevPortal.csv'
df = pd.read_csv(file_path)

columns_to_remove = ['id', 'img_uri', 'address', 'localizability']
df = df.drop(columns=columns_to_remove, errors='ignore')

df.to_csv('new_file.csv', index=False)