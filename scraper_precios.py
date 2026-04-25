import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── CONEXIÓN ESTABLE ──────────────────────────────────────────
def crear_sesion():
    sesion = requests.Session()

    reintentos = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    sesion.mount("https://", HTTPAdapter(max_retries=reintentos))

    sesion.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Accept": "application/json"
    })
    return sesion


# ── SCRAPER PRINCIPAL ─────────────────────────────────────────
def obtener_precios(sesion):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order":       "market_cap_desc",
        "per_page":    20,
        "page":        1
    }

    print("Conectando a CoinGecko...")

    try:
        respuesta = sesion.get(url, params=params, timeout=10)
        respuesta.raise_for_status()   # dispara error si hay 404 o 500

        datos = respuesta.json()
        registros = []

        for moneda in datos:
            try:
                registro = {
                    "nombre"     : moneda["name"],
                    "simbolo"    : moneda["symbol"],
                    "precio_usd" : f"$ {moneda['current_price']} ",   # sucio
                    "volumen_24h": f"  {moneda['total_volume']}  ",   # sucio
                    "cambio_24h" : f"{moneda['price_change_percentage_24h']} %",
                    "cap_mercado": moneda.get("market_cap", "N/A"),
                }
                registros.append(registro)

            except KeyError as e:
                print(f"[WARN] Campo faltante: {e} — se omite esta moneda")
                continue

        return registros

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR 404/500] El servidor respondió con error: {e}")
        return []

    except requests.exceptions.ConnectionError:
        print("[ERROR] Sin conexión — verifica tu internet")
        return []

    except requests.exceptions.Timeout:
        print("[ERROR] Timeout — el servidor tardó más de 10 segundos")
        return []


# ── GUARDAR CSV SUCIO ─────────────────────────────────────────
def guardar_csv(registros):
    if not registros:
        print("[WARN] No hay datos para guardar")
        return

    df = pd.DataFrame(registros)
    nombre_archivo = "cripto_precios_SUCIO.csv"
    df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")

    print(f"\n[OK] CSV guardado: {nombre_archivo}")
    print(f"[OK] Total de monedas: {len(registros)}")
    print("\nPrimeras 3 filas del CSV sucio:")
    print(df.head(3).to_string())


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Observatorio de Criptoactivos ===")
    sesion   = crear_sesion()
    precios  = obtener_precios(sesion)
    time.sleep(2)
    guardar_csv(precios)
    print("\n=== Conexión estable lograda ===")