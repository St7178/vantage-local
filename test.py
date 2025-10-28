import pandas as pd

# Ruta de tu archivo Excel
archivo_excel = "backend/RVTools_export_all_2025COPY.xlsx"

# Cargar la hoja vInfo
df = pd.read_excel(archivo_excel, sheet_name="vInfo")

# Supongamos que la columna con el nombre de la VM es 'VM' y la del OS es 'Guest OS'
# Ajusta el nombre de las columnas según tu archivo
if 'VM' not in df.columns or 'OS according to the configuration file' not in df.columns:
    print("Verifica que las columnas 'VM' y 'Guest OS' existan en tu hoja vInfo")
else:
    # Contar la cantidad de VMs por sistema operativo
    resumen_os = df.groupby('OS according to the configuration file')['VM'].count().reset_index()
    resumen_os = resumen_os.rename(columns={'VM': 'Cantidad de VMs'})

    # Mostrar el resultado en pantalla
    print("Resumen de VMs por Sistema Operativo:")
    print(resumen_os.to_string(index=False))
