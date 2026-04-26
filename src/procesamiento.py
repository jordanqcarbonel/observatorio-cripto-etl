"""
procesamiento.py
================
Script de limpieza y preparación de datos del observatorio cripto.

Acciones:
  1. Carga de datos desde data/master_SUCIO.csv
  2. Detección de Outliers (método IQR) → columna 'es_outlier'
  3. Imputación de nulos (mediana para numéricos, moda para texto)
  4. Normalización MinMax [0, 1] → columnas '_norm'
  5. Exporta data/master_PROCESADO.csv

Autor : Int. 2 - Procesamiento Estadístico
Fecha : 2026-04-26
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ─────────────────────────────────────────────
# 0. RUTAS
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV  = os.path.join(BASE_DIR, "data", "master_SUCIO.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "master_PROCESADO.csv")

print("=" * 60)
print("  OBSERVATORIO CRIPTO — PROCESAMIENTO ESTADÍSTICO")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. CARGA DE DATOS
# ─────────────────────────────────────────────
print("\n[1/4] Cargando datos...")

df = pd.read_csv(INPUT_CSV)

# Convertir fecha_hora a datetime
df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")

print(f"  ✔ Filas cargadas     : {len(df)}")
print(f"  ✔ Columnas           : {list(df.columns)}")
print(f"\n  Nulos por columna:\n{df.isnull().sum().to_string()}")

# ─────────────────────────────────────────────
# 2. IMPUTACIÓN DE NULOS
# ─────────────────────────────────────────────
print("\n[2/4] Imputando nulos...")

COLS_NUMERICAS = ["precio_usd", "volumen_24h", "market_cap", "nivel_impacto"]
COLS_TEXTO     = ["activo", "tipo_evento", "procedencia"]

nulos_antes = df.isnull().sum().sum()

# Numéricos → mediana (robusta ante outliers)
for col in COLS_NUMERICAS:
    if df[col].isnull().any():
        mediana = df[col].median()
        df[col].fillna(mediana, inplace=True)
        print(f"  ✔ '{col}' → imputado con mediana ({mediana:.4f})")
    else:
        print(f"  — '{col}' → sin nulos")

# Texto → moda (valor más frecuente)
for col in COLS_TEXTO:
    if df[col].isnull().any():
        moda = df[col].mode()[0]
        df[col].fillna(moda, inplace=True)
        print(f"  ✔ '{col}' → imputado con moda ('{moda}')")
    else:
        print(f"  — '{col}' → sin nulos")

# fecha_hora → si hay nulos, se eliminan (no se puede imputar una fecha)
nulos_fecha = df["fecha_hora"].isnull().sum()
if nulos_fecha > 0:
    df.dropna(subset=["fecha_hora"], inplace=True)
    print(f"  ⚠ '{fecha_hora}' → {nulos_fecha} filas eliminadas (fecha inválida)")

nulos_despues = df.isnull().sum().sum()
print(f"\n  Nulos antes: {nulos_antes}  →  Nulos después: {nulos_despues}")

# ─────────────────────────────────────────────
# 3. DETECCIÓN DE OUTLIERS (método IQR)
# ─────────────────────────────────────────────
print("\n[3/4] Detectando outliers (método IQR)...")

"""
Método IQR:
  Q1 = percentil 25
  Q3 = percentil 75
  IQR = Q3 - Q1
  Límite inferior = Q1 - 1.5 * IQR
  Límite superior = Q3 + 1.5 * IQR
  Outlier si valor < lim_inf  OR  valor > lim_sup
"""

df["es_outlier"] = False  # bandera general
outlier_detalle  = {}     # para el reporte

for col in COLS_NUMERICAS:
    Q1  = df[col].quantile(0.25)
    Q3  = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    mascara = (df[col] < lim_inf) | (df[col] > lim_sup)
    df[f"outlier_{col}"] = mascara          # columna individual por variable
    df["es_outlier"] = df["es_outlier"] | mascara  # bandera global

    n_outliers = mascara.sum()
    outlier_detalle[col] = {
        "Q1": Q1, "Q3": Q3, "IQR": IQR,
        "lim_inf": lim_inf, "lim_sup": lim_sup,
        "n_outliers": n_outliers
    }
    print(f"  '{col}' → lim:[{lim_inf:.2f}, {lim_sup:.2f}]  |  outliers: {n_outliers}")

total_outliers = df["es_outlier"].sum()
print(f"\n  Total de filas con al menos un outlier: {total_outliers} / {len(df)}")
print("  ⚠ Los outliers NO se eliminaron (solo se marcaron).")

# ─────────────────────────────────────────────
# 4. NORMALIZACIÓN MinMax [0, 1]
# ─────────────────────────────────────────────
print("\n[4/4] Normalizando columnas numéricas principales...")

COLS_NORMALIZAR = ["precio_usd", "volumen_24h", "market_cap"]

scaler = MinMaxScaler()
valores_norm = scaler.fit_transform(df[COLS_NORMALIZAR])

for i, col in enumerate(COLS_NORMALIZAR):
    nueva_col = f"{col}_norm"
    df[nueva_col] = valores_norm[:, i]
    print(f"  ✔ '{nueva_col}' → rango [{df[nueva_col].min():.4f}, {df[nueva_col].max():.4f}]")

# nivel_impacto también normalizado 
df["nivel_impacto_norm"] = (df["nivel_impacto"] - df["nivel_impacto"].min()) / \
                           (df["nivel_impacto"].max() - df["nivel_impacto"].min())
print(f"  ✔ 'nivel_impacto_norm' → rango [{df['nivel_impacto_norm'].min():.4f}, {df['nivel_impacto_norm'].max():.4f}]")

# ─────────────────────────────────────────────
# 5. EXPORTAR
# ─────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("\n" + "=" * 60)
print("  RESUMEN FINAL")
print("=" * 60)
print(f"  Filas procesadas     : {len(df)}")
print(f"  Outliers detectados  : {total_outliers}")
print(f"  Nulos imputados      : {nulos_antes}")
print(f"  Columnas generadas   : es_outlier, outlier_*, *_norm")
print(f"\n  ✅ Archivo exportado → {OUTPUT_CSV}")
print("=" * 60)
