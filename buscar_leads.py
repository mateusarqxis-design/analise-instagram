"""
buscar_leads.py — Busca leads via Google Places API para profissionais de
                  estetica e saude em Maringa-PR.

Categorias buscadas:
  - Medico Esteta
  - Dermatologista
  - Clinica de Estetica
  - Clinica Medica
  - Cirurgiao Plastico

Fluxo:
  1. Places Text Search  -> lista de place_id por categoria
  2. Place Details       -> nome, telefone, site
  3. Scraping do site    -> perfil do Instagram

Saida: saida/leads_maringá.csv
Colunas: tipo, nome, site, telefone, instagram, maps_url, avaliacao, total_avaliacoes

Uso:
  # Passar a chave pela variavel de ambiente (recomendado)
  set GOOGLE_PLACES_KEY=SUA_CHAVE
  python buscar_leads.py

  # Ou digitar quando solicitado
  python buscar_leads.py
"""

import csv
import os
import re
import sys
import time
import random
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Forca UTF-8 no terminal Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Configuracao ──────────────────────────────────────────────────────────────

PASTA_SAIDA  = Path(__file__).parent / "saida"
ARQUIVO_SAIDA = PASTA_SAIDA / "leads_maringá.csv"

# Cada entrada: (label_csv, query_places)
CATEGORIAS = [
    ("Medico Esteta",       "medico esteta Maringa PR"),
    ("Dermatologista",      "dermatologista Maringa PR"),
    ("Clinica de Estetica", "clinica de estetica Maringa PR"),
    ("Clinica Medica",      "clinica medica Maringa PR"),
    ("Cirurgiao Plastico",  "cirurgiao plastico Maringa PR"),
]

MAX_PAGINAS = 3          # Places API permite ate 3 paginas (60 resultados)
TIMEOUT_HTTP = 10        # segundos para requests de site

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

REGEX_INSTAGRAM = re.compile(r"instagram\.com/([A-Za-z0-9_.]{2,30})")
INSTAGRAM_IGNORADOS = {
    "", "accounts", "explore", "reel", "reels", "p", "stories",
    "tv", "share", "sharer", "developer", "about", "legal",
    "help", "press", "api", "ar",
}

# ── Google Places API (New / v1) ──────────────────────────────────────────────
# Documentacao: https://developers.google.com/maps/documentation/places/web-service/text-search

BASE_TEXT_SEARCH = "https://places.googleapis.com/v1/places:searchText"

FIELDS_TEXT_SEARCH = ",".join([
    "places.id",
    "places.displayName",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.googleMapsUri",
    "places.rating",
    "places.userRatingCount",
    "nextPageToken",
])


def text_search(query: str, api_key: str) -> list[dict]:
    """
    Executa Places Text Search (API nova) com paginacao.
    Retorna lista de dicts com os campos ja extraidos.
    """
    lugares = []
    ids_vistos: set[str] = set()
    page_token = None
    pagina = 0

    while pagina < MAX_PAGINAS:
        body: dict = {"textQuery": query, "languageCode": "pt-BR"}
        if page_token:
            body["pageToken"] = page_token

        headers = {
            "Content-Type":    "application/json",
            "X-Goog-Api-Key":  api_key,
            "X-Goog-FieldMask": FIELDS_TEXT_SEARCH,
        }

        try:
            resp = requests.post(BASE_TEXT_SEARCH, json=body, headers=headers, timeout=TIMEOUT_HTTP)
        except requests.RequestException as e:
            print(f"  [ERRO Places] {e}")
            break

        if resp.status_code == 403:
            data = resp.json()
            msg = data.get("error", {}).get("message", resp.text)
            print(f"  [ERRO] Chave invalida ou sem permissao: {msg}")
            sys.exit(1)

        if resp.status_code != 200:
            print(f"  [AVISO] Status HTTP {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        results = data.get("places", [])

        for r in results:
            pid = r.get("id", "")
            if not pid or pid in ids_vistos:
                continue
            ids_vistos.add(pid)
            lugares.append({
                "nome":             r.get("displayName", {}).get("text", ""),
                "telefone":         r.get("nationalPhoneNumber", ""),
                "site":             r.get("websiteUri", ""),
                "maps_url":         r.get("googleMapsUri", ""),
                "avaliacao":        r.get("rating", ""),
                "total_avaliacoes": r.get("userRatingCount", ""),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        pagina += 1
        time.sleep(2.5)  # exigido pela API antes de usar o nextPageToken

    return lugares


# ── Scraping do site para Instagram ──────────────────────────────────────────

def _headers_site():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }


def extrair_instagram(url: str) -> str:
    """Visita o site e tenta capturar o handle do Instagram."""
    if not url:
        return ""
    try:
        resp = requests.get(
            url, headers=_headers_site(), timeout=TIMEOUT_HTTP, allow_redirects=True
        )
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        texto = soup.get_text(" ", strip=True)
    except requests.RequestException:
        return ""

    # 1) Links href -> instagram.com/handle
    for a in soup.find_all("a", href=True):
        m = REGEX_INSTAGRAM.search(a["href"])
        if m and m.group(1).lower() not in INSTAGRAM_IGNORADOS:
            return f"instagram.com/{m.group(1)}"

    # 2) Texto da pagina
    for m in REGEX_INSTAGRAM.finditer(texto):
        if m.group(1).lower() not in INSTAGRAM_IGNORADOS:
            return f"instagram.com/{m.group(1)}"

    return ""


# ── Principal ─────────────────────────────────────────────────────────────────

def obter_api_key() -> str:
    key = os.environ.get("GOOGLE_PLACES_KEY", "").strip()
    if not key:
        print("\nChave da Google Places API nao encontrada.")
        print("Obtenha a sua em: https://console.cloud.google.com/")
        print("Habilite 'Places API' no projeto.\n")
        key = input("Cole sua API Key aqui: ").strip()
    if not key:
        print("[ERRO] Nenhuma chave informada. Encerrando.")
        sys.exit(1)
    return key


def buscar_leads():
    api_key = obter_api_key()

    todos_leads  = []
    ids_vistos   = set()
    sites_vistos = set()

    print("\n" + "=" * 58)
    print("  Buscador de Leads | Google Places | Maringa PR")
    print("=" * 58)

    for tipo, query in CATEGORIAS:
        print(f"\n{'-' * 58}")
        print(f"  Categoria : {tipo}")
        print(f"  Query     : \"{query}\"")

        lugares = text_search(query, api_key)
        print(f"  Places    : {len(lugares)} locais encontrados\n")

        for lugar in lugares:
            nome      = lugar["nome"]
            telefone  = lugar["telefone"]
            site      = lugar["site"]
            maps_url  = lugar["maps_url"]
            avaliacao = lugar["avaliacao"]
            total_av  = lugar["total_avaliacoes"]

            # Deduplica por nome+telefone entre categorias
            chave = (nome.lower().strip(), telefone)
            if chave in ids_vistos:
                continue
            ids_vistos.add(chave)

            print(f"  >> {nome[:52]}")
            print(f"     Tel : {telefone or '-'}")
            print(f"     Site: {(site or '-')[:65]}")

            # Scraping do Instagram no site
            instagram = ""
            if site and site not in sites_vistos:
                sites_vistos.add(site)
                instagram = extrair_instagram(site)
                time.sleep(random.uniform(1.0, 2.0))

            print(f"     IG  : {instagram or '-'}\n")

            todos_leads.append({
                "tipo":              tipo,
                "nome":              nome,
                "site":              site,
                "telefone":          telefone,
                "instagram":         instagram,
                "maps_url":          maps_url,
                "avaliacao":         avaliacao,
                "total_avaliacoes":  total_av,
            })

    # ── Salvar CSV ────────────────────────────────────────────────────────────
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    campos = ["tipo", "nome", "site", "telefone", "instagram",
              "maps_url", "avaliacao", "total_avaliacoes"]

    with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(todos_leads)

    # ── Resumo final ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 58}")
    print("  Resumo por categoria:")
    print(f"  {'-' * 50}")
    for tipo, _ in CATEGORIAS:
        grupo     = [l for l in todos_leads if l["tipo"] == tipo]
        com_fone  = sum(1 for l in grupo if l["telefone"])
        com_site  = sum(1 for l in grupo if l["site"])
        com_ig    = sum(1 for l in grupo if l["instagram"])
        print(f"  {tipo:<22} {len(grupo):>2} leads | "
              f"tel:{com_fone} site:{com_site} ig:{com_ig}")

    print(f"  {'-' * 50}")
    print(f"  TOTAL: {len(todos_leads)} leads")
    print(f"\n  Salvo em: {ARQUIVO_SAIDA}")
    print("=" * 58)


if __name__ == "__main__":
    buscar_leads()
