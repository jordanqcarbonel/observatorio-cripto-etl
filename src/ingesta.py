import pandas as pd
import os
from datetime import datetime
import random

# ─────────────────────────────
# RUTAS
# ─────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "..", "data")

PRECIOS_FILE  = os.path.join(DATA_DIR, "cripto_precios_SUCIO.csv")
NOTICIAS_FILE = os.path.join(DATA_DIR, "cripto_noticias_SUCIO.csv")
OUTPUT_FILE   = os.path.join(DATA_DIR, "master_SUCIO.csv")

# ─────────────────────────────
# 1. CARGA DE DATOS
# ─────────────────────────────
def cargar_datos():
    df_precios = pd.read_csv(PRECIOS_FILE)
    df_noticias = pd.read_csv(NOTICIAS_FILE)

    print(f"✔ Precios: {df_precios.shape}")
    print(f"✔ Noticias: {df_noticias.shape}")

    return df_precios, df_noticias


# ─────────────────────────────
# 2. GENERAR DATOS SINTÉTICOS
# ─────────────────────────────
def generar_sinteticos(n=20):
    data = []
    activos = ["BTC", "ETH", "SOL"]

    for i in range(n):
        data.append({
            "id_transaccion": f"SYN-{i}",
            "fecha_hora": datetime.now(),
            "activo": random.choice(activos),
            "precio_usd": random.uniform(1000, 60000),
            "volumen_24h": random.uniform(1e6, 5e7),
            "market_cap": random.uniform(1e8, 1e9),
            "tipo_evento": "Sintetico",
            "procedencia": "Generado"
        })

    return pd.DataFrame(data)


# ─────────────────────────────
# 3. UNIFICAR DATOS
# ─────────────────────────────
def unificar(df_precios, df_noticias, df_sintetico):
    
    # Adaptar precios a esquema master
    df_precios["fecha_hora"] = datetime.now()
    df_precios["tipo_evento"] = "precio"
    df_precios["procedencia"] = "CoinGecko"
    df_precios["id_transaccion"] = range(len(df_precios))

    # Adaptar noticias
    df_noticias["precio_usd"] = None
    df_noticias["volumen_24h"] = None
    df_noticias["market_cap"] = None
    df_noticias["tipo_evento"] = "noticia"
    df_noticias["procedencia"] = df_noticias["fuente"]
    df_noticias["id_transaccion"] = range(len(df_noticias))

    # Columnas finales
    columnas = [
        "id_transaccion", "fecha_hora", "activo",
        "precio_usd", "volumen_24h", "market_cap",
        "tipo_evento", "procedencia"
    ]

def unificar(df_precios, df_noticias, df_sintetico):

    # ── PRECIOS ──
    df_precios = df_precios.copy()
    df_precios["activo"] = df_precios.get("simbolo", "UNK")
    df_precios["market_cap"] = df_precios.get("cap_mercado", None)
    df_precios["fecha_hora"] = datetime.now()
    df_precios["tipo_evento"] = "precio"
    df_precios["procedencia"] = "CoinGecko"
    df_precios["id_transaccion"] = range(len(df_precios))

    # ── NOTICIAS ──
    df_noticias = df_noticias.copy()

    # evitar error si viene vacío
    if df_noticias.empty:
        df_noticias = pd.DataFrame(columns=["fecha", "fuente"])

    df_noticias["activo"] = "BTC"
    df_noticias["precio_usd"] = None
    df_noticias["volumen_24h"] = None
    df_noticias["market_cap"] = None

    # 🔥 FIX CLAVE (tu error actual)
    if "fecha" in df_noticias.columns:
        df_noticias["fecha_hora"] = pd.to_datetime(df_noticias["fecha"], errors="coerce")
    else:
        df_noticias["fecha_hora"] = pd.NaT

    df_noticias["tipo_evento"] = "noticia"
    df_noticias["procedencia"] = df_noticias.get("fuente", "web")
    df_noticias["id_transaccion"] = range(len(df_noticias))

    # ── COLUMNAS FINALES ──
    columnas = [
        "id_transaccion", "fecha_hora", "activo",
        "precio_usd", "volumen_24h", "market_cap",
        "tipo_evento", "procedencia"
    ]

    df_final = pd.concat([
        df_precios[columnas],
        df_noticias[columnas],
        df_sintetico[columnas]
    ], ignore_index=True)

    return df_final



# ─────────────────────────────
# 4. MÉTRICAS DE CALIDAD
# ─────────────────────────────
def metricas_calidad(df):
    print("\n=== MÉTRICAS DE CALIDAD ===")

    total = len(df)
    total_celdas = df.size

    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()

    print(f"Total registros: {total}")
    print(f"Total columnas: {df.shape[1]}")

    print(f"% Nulos: {(nulos / total_celdas) * 100:.2f}%")
    print(f"% Duplicados: {(duplicados / total) * 100:.2f}%")
    print(f"% Completitud: {100 - ((nulos / total_celdas) * 100):.2f}%")

    print("\nDistribución por tipo_evento:")
    print(df["tipo_evento"].value_counts())



# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    print("=== INGESTA DE DATOS ===")

    df_precios, df_noticias = cargar_datos()

    df_sintetico = generar_sinteticos(200)

    df_final = unificar(df_precios, df_noticias, df_sintetico)

    #VALIDACIONES AUTOMATIZADAS
    assert "precio_usd" in df_final.columns, "Falta columna precio_usd"
    assert "fecha_hora" in df_final.columns, "Falta columna fecha_hora"
    assert df_final.isnull().sum().sum() < df_final.size, "Demasiados nulos"
    assert df_final.shape[0] > 0, "Dataset vacío"
    assert df_final.shape[0] > 50, "Muy pocos datos generados"
    assert df_final["fecha_hora"].notnull().any(), "Todas las fechas son nulas"



    # Guardar


    os.makedirs(DATA_DIR, exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✔ Archivo generado: {OUTPUT_FILE}")
    print(f"✔ Total registros: {len(df_final)}")

    metricas_calidad(df_final)


if __name__ == "__main__":
    main()

print("[INFO] Scraping completado")
print("[INFO] Datos unificados correctamente")
print("\n=== INGESTA COMPLETADA ===")
