import pandas as pd
import os
import random

# --- CONFIG ---
carpeta_src = os.path.dirname(__file__)
INPUT_FILE  = os.path.join(carpeta_src, "..", "data", "cripto_precios_SUCIO.csv")
OUTPUT_FILE = os.path.join(carpeta_src, "..", "data", "cripto_precios_SUCIO.csv")
COLUMNA     = "cap_mercado"
SEED        = 42

random.seed(SEED)

# --- POOL DE SUCIEDAD ---
prefijos = ["$ ", "$", "USD ", "~ ", "≈ ", " "]
sufijos  = [" USD", " $", " ,00", "%", " ", "  "]

def ensuciar(valor: str) -> str:
    prefijo = random.choice(prefijos)
    sufijo  = random.choice(sufijos)
    espacios_extra = " " * random.randint(0, 3)
    return f"{prefijo}{espacios_extra}{valor}{sufijo}"

# --- PROCESO ---
df = pd.read_csv(INPUT_FILE, dtype=str, encoding="utf-8-sig")
df[COLUMNA] = df[COLUMNA].apply(ensuciar)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("✓ Listo. Columna ensuciada:")
print(df[["nombre", COLUMNA]].to_string(index=False))