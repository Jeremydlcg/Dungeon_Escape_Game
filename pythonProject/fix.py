import pandas as pd
import numpy as np

# Cargar el archivo
level_data = pd.read_csv("levels/level1_data.csv")

# Crear una nueva fila de -1 y añadirla al final si el archivo tiene 149 filas
if level_data.shape[0] == 149:
    new_row = pd.DataFrame(np.full((1, 150), -1), columns=level_data.columns)
    level_data = pd.concat([level_data, new_row], ignore_index=True)

# Guardar el archivo corregido
level_data.to_csv("level1_data_corrected.csv", index=False)
