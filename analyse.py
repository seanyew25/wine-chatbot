import pandas as pd

df = pd.read_csv('wine_data_final.csv', delimiter=';')
unique_values = df['product_type'].unique()
print(unique_values)
