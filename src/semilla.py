import pandas as pd
import os
from datetime import datetime, timedelta
import random

def generar_semilla():
    print("=== Generando Archivo Semilla para el Equipo ===")
    
    # 1. Definimos las columnas del "Contrato"
    columnas = [
        'id_transaccion', 'fecha_hora', 'activo', 'precio_usd', 
        'volumen_24h', 'market_cap', 'nivel_impacto', 
        'tipo_evento', 'procedencia'
    ]
    
    # 2. Creamos datos de ejemplo (10 filas) para que el archivo no esté vacío
    datos = []
    fecha_base = datetime.now()
    eventos = ['Regulacion', 'Adopcion', 'Hackeo', 'Twitter', 'Ballenas']
    fuentes = ['CoinTelegraph', 'Binance', 'Twitter', 'API']
    activos = ['BTC', 'ETH', 'SOL']

    for i in range(10):
        datos.append({
            'id_transaccion': f"TX-{1000 + i}",
            'fecha_hora': (fecha_base - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
            'activo': random.choice(activos),
            'precio_usd': round(random.uniform(3000, 65000), 2),
            'volumen_24h': round(random.uniform(1000000, 50000000), 2),
            'market_cap': round(random.uniform(100000000, 1000000000), 2),
            'nivel_impacto': random.randint(1, 10),
            'tipo_evento': random.choice(eventos),
            'procedencia': random.choice(fuentes)
        })

    df = pd.DataFrame(datos, columns=columnas)

    # 3. Guardamos en la carpeta data
    carpeta_src = os.path.dirname(__file__)
    ruta_salida = os.path.join(carpeta_src, "..", "data", "master_SUCIO.csv")
    
    # Aseguramos que la carpeta data exista
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    
    print(f"\n[OK] Archivo creado: {ruta_salida}")
    print("Manda este archivo al repositorio para que el Integrante 2 lo use de base.")

if __name__ == "__main__":
    generar_semilla()