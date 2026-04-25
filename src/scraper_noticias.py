import requests
from bs4 import BeautifulSoup
import pandas as pd
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    return sesion


# ── SCRAPER DE NOTICIAS ───────────────────────────────────────
def obtener_noticias(sesion):
    url = "https://cointelegraph.com/tags/bitcoin"

    print(f"Conectando a CoinTelegraph...")

    try:
        respuesta = sesion.get(url, timeout=15)
        respuesta.raise_for_status()

        soup = BeautifulSoup(respuesta.text, "lxml")
        noticias = []

        # Selector principal de CoinTelegraph
        articulos = soup.select("article.post-card")

        if not articulos:
            print("[WARN] Selector 'article.post-card' no encontró nada — probando alternativo...")
            articulos = soup.select("li.posts-listing__item")

        if not articulos:
            print("[WARN] Probando tercer selector...")
            articulos = soup.find_all("article")

        if not articulos:
            print("[ERROR] El HTML de CoinTelegraph cambió — no se encontraron artículos")
            return []

        print(f"[OK] Se encontraron {len(articulos)} artículos")

        for articulo in articulos[:10]:
            try:
                # Buscar título
                titulo_tag = (
                    articulo.find("span", class_=lambda c: c and "title" in c.lower()) or
                    articulo.find("h1") or
                    articulo.find("h2") or
                    articulo.find("h3") or
                    articulo.find("h4")
                )

                if titulo_tag is None:
                    raise AttributeError("No se encontró tag de título en este artículo")

                # Buscar fecha
                fecha_tag = articulo.find("time")

                # Buscar link
                link_tag = articulo.find("a", href=True)

                noticia = {
                    "titulo" : f"  {titulo_tag.get_text(strip=False)}  ",
                    "fecha"  : fecha_tag.get("datetime") if fecha_tag else "  Sin fecha  ",
                    "fuente" : "  CoinTelegraph  ",
                    "url"    : f"  https://cointelegraph.com{link_tag['href']}  " if link_tag else "N/A",
                }
                noticias.append(noticia)

            except AttributeError as e:
                # El elemento HTML no existe o cambió de nombre
                print(f"[WARN] Elemento HTML no encontrado: {e}")
                continue

        return noticias

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR HTTP {respuesta.status_code}] CoinTelegraph respondió con error: {e}")
        return []

    except requests.exceptions.ConnectionError:
        print("[ERROR] Sin conexión — verifica tu internet")
        return []

    except requests.exceptions.Timeout:
        print("[ERROR] Timeout — CoinTelegraph tardó más de 15 segundos")
        return []


# ── GUARDAR CSV SUCIO ─────────────────────────────────────────
def guardar_csv(noticias):
    if not noticias:
        print("[WARN] No hay noticias para guardar")
        return

    df = pd.DataFrame(noticias)
    nombre_archivo = "cripto_noticias_SUCIO.csv"
    df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")

    print(f"\n[OK] CSV guardado: {nombre_archivo}")
    print(f"[OK] Total de noticias: {len(noticias)}")
    print("\nPrimeras 3 noticias del CSV sucio:")
    print(df.head(3).to_string())


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Observatorio de Criptoactivos — Noticias ===")
    sesion   = crear_sesion()
    noticias = obtener_noticias(sesion)
    guardar_csv(noticias)
    print("\n=== Scraping de noticias completado ===")