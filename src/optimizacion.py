import pandas as pd
import os
import time

def optimizar_a_parquet():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "master_PROCESADO.csv"))
    OUTPUT_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "master_FINAL.parquet"))

    print("\n=== FASE 3: OPTIMIZACIÓN DE ALMACENAMIENTO (PARQUET) ===")
    
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Error: No se encuentra el archivo {INPUT_PATH}")
        return

    # 1. Cargamos el csv procesado
    df = pd.read_csv(INPUT_PATH)
    
    # 2. Medimos los pesos
    peso_csv = os.path.getsize(INPUT_PATH) / 1024  # KB
    
    # 3. Exportamos a Parquet (Optimización)
    start_time = time.time()
    df.to_parquet(OUTPUT_PATH, engine='pyarrow', compression='snappy')
    end_time = time.time()
    
    peso_parquet = os.path.getsize(OUTPUT_PATH) / 1024  # KB
    ahorro = 100 - (peso_parquet / peso_csv * 100)

    print(f"✔ Archivo convertido a Parquet exitosamente.")
    print(f"📊 Peso Original (CSV): {peso_csv:.2f} KB")
    print(f"📊 Peso Optimizado (Parquet): {peso_parquet:.2f} KB")
    print(f"📉 Ahorro de espacio: {ahorro:.2f}%")
    print(f"⏱ Tiempo de ejecución: {(end_time - start_time):.4f} segundos")

if __name__ == "__main__":
    optimizar_a_parquet()