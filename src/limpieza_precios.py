import pandas as pd
import os

def limpiar_datos():
    print("=== Iniciando Proceso de Limpieza y guardado en PARQUET ===")
    
    # Leemos el archivo csv
    carpeta_src = os.path.dirname(__file__)
    archivo_sucio = os.path.join(carpeta_src, "..", "data", "cripto_precios_SUCIO.csv")    
    archivo_parquet = os.path.join(carpeta_src, "..", "data", "cripto_precios_OPTIMIZADO.parquet")
    if not os.path.exists(archivo_sucio):
        print(f"[ERROR] No se encontró el archivo {archivo_sucio}")
        return

    df = pd.read_csv(archivo_sucio, dtype=str, encoding="utf-8-sig")
    print(f"Datos cargados: {df.shape[0]} filas.")

    # Limpiamos los datos
    # Utilizamos regex para buscar números y un punto decimal, ignora cualquier otro simbolo
    regex_limpieza = r'[^0-9.]'

    columnas_a_limpiar = ['precio_usd', 'cambio_24h', 'volumen_24h', 'cap_mercado']

    for col in columnas_a_limpiar:
            if col in df.columns:
                # Aseguramos que sea string, eliminamos las comas 
                df[col] = (df[col]
                        .str.replace(',', '', regex=False)
                        .str.replace(regex_limpieza, '', regex=True)
                        .str.strip())
                #por si quedan vacíos
                df[col] = df[col].replace('', '0')
                
    # Transformamos las columnas a formato numérico
    for col in columnas_a_limpiar:
        if col in df.columns:
          df[col] = pd.to_numeric(df[col], errors='coerce')

    print("Limpieza y transformación completada.")

    # Guardamos en PARQUET    
    try:
        df.to_parquet(archivo_parquet, index=False)
        print(f"[OK] Archivo PARQUET guardado: {archivo_parquet}")
    except ImportError:
        print("[ERROR] Es necesario instalar pyarrow, usa el comando: pip install pyarrow")

    # Resultado Final
    print("\nResumen de datos limpios:")
    print(df.head(5).to_string())
    print("\nTipos de datos finales:")
    print(df.dtypes)

if __name__ == "__main__":
    limpiar_datos()