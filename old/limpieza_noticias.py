import pandas as pd
import os

def limpiar_datos():
    print("=== Iniciando Proceso de Limpieza y guardado en PARQUET ===")
    
    # Leemos el archivo csv
    carpeta_src = os.path.dirname(__file__)
    archivo_sucio = os.path.join(carpeta_src, "..", "data", "cripto_noticias_SUCIO.csv")    
    archivo_parquet = os.path.join(carpeta_src, "..", "data", "cripto_noticias_OPTIMIZADO.parquet")
    if not os.path.exists(archivo_sucio):
        print(f"[ERROR] No se encontró el archivo {archivo_sucio}")
        return

    df = pd.DataFrame(pd.read_csv(archivo_sucio))
    print(f"Datos cargados: {df.shape[0]} filas.")

    # Limpiamos los datos
    if 'titulo' in df.columns:
        df['titulo'] = df['titulo'].astype(str).str.strip()

    if 'fuente' in df.columns:
        df['fuente'] = df['fuente'].astype(str).str.strip()

    if 'url' in df.columns:
        df['url'] = df['url'].astype(str).str.strip()

    if 'fecha' in df.columns:
        df['fecha'] = df['fecha'].astype(str).str.strip()
        # También lo convertimos a formato fecha real
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.date

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