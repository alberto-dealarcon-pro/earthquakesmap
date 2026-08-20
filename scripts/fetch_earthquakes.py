#!/usr/bin/env python3
"""
Scraper de terremotos recientes del IGN.
Fuente: https://www.ign.es/web/ign/portal/ultimos-terremotos
"""

import json
import time
import http.cookiejar
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
DIAS   = 10
OUTPUT = "data/earthquakes.json"
BASE   = "https://www.ign.es/web/ign/portal/ultimos-terremotos"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

def data_url():
    ts = int(time.time() * 1000)
    p  = "_IGNGFSSismoSismicidadReciente_WAR_IGNGFSSismoSismicidadRecienteportlet"
    return (
        f"{BASE}/-/ultimos-terremotos/get10dias"
        f"?{p}_formDate={ts}&{p}_dias={DIAS}"
    )


# ── PARSER HTML ───────────────────────────────────────────────────────────────
class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table     = False
        self.in_row       = False
        self.in_cell      = False
        self.rows         = []
        self.current_row  = []
        self.current_cell = ""
        self.current_link = ""
        self._tdepth      = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self._tdepth += 1
            self.in_table = True
        if self.in_table:
            if tag == "tr":
                self.in_row = True
                self.current_row  = []
                self.current_link = ""
            elif tag in ("td", "th") and self.in_row:
                self.in_cell      = True
                self.current_cell = ""
            elif tag == "a" and self.in_cell:
                href = attrs.get("href", "")
                if href:
                    self.current_link = href

    def handle_endtag(self, tag):
        if tag == "table":
            self._tdepth -= 1
            if self._tdepth == 0:
                self.in_table = False
        if self.in_table:
            if tag in ("td", "th") and self.in_cell:
                self.in_cell = False
                self.current_row.append((self.current_cell.strip(), self.current_link))
                self.current_link = ""
            elif tag == "tr" and self.in_row:
                self.in_row = False
                if self.current_row:
                    self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data


# ── RED ───────────────────────────────────────────────────────────────────────
def make_opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(opener, url, referer=None):
    headers = dict(HEADERS)
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with opener.open(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── PARSEO ────────────────────────────────────────────────────────────────────
def parse_float(s):
    try:
        return float(str(s).replace(",", ".").strip())
    except (ValueError, AttributeError):
        return None

SKIP = {"Evento", "Fecha", "Hora", "Hora UTC", "Hora Local", "Latitud",
        "Longitud", "Profundidad", "Magnitud", "Localización", "Más Info", ""}

def parse_row(cells):
    """
    Columnas IGN (0-indexed):
      0  Evento        5  Longitud
      1  Fecha         6  Profundidad (km)
      2  Hora UTC      7  Magnitud
      3  Hora Local    8  Tipo Mag.
      4  Latitud       9  Int. max.   10  Localización   11  Más Info
    """
    if len(cells) < 8:
        return None
    texts = [c[0] for c in cells]
    link  = next((c[1] for c in cells if c[1]), "")
    try:
        lat       = parse_float(texts[4])
        lon       = parse_float(texts[5])
        magnitude = parse_float(texts[7])
        if lat is None or lon is None or magnitude is None:
            return None
        return {
            "event_id":  texts[0],
            "date":      f"{texts[1]} {texts[2]}",   # "DD/MM/YYYY HH:MM:SS" UTC
            "lat":       lat,
            "lon":       lon,
            "depth":     parse_float(texts[6]),
            "magnitude": magnitude,
            "mag_type":  texts[8]  if len(texts) > 8  else "",
            "intensity": texts[9]  if len(texts) > 9  else "",
            "location":  texts[10].strip() if len(texts) > 10 else "",
            "link":      link,
        }
    except Exception as e:
        print(f"  ⚠ fila ignorada: {e}")
        return None


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    opener = make_opener()

    # 1. Página principal → cookies de sesión Liferay
    print("Obteniendo cookies de sesión…")
    try:
        fetch(opener, BASE)
    except Exception as e:
        print(f"  ⚠ cookies no obtenidas: {e}")

    # 2. Datos
    url = data_url()
    print(f"Descargando datos ({DIAS} días)…")
    html = fetch(opener, url, referer=BASE)
    print(f"  HTML: {len(html):,} bytes")

    # 3. Parsear tabla
    parser = TableParser()
    parser.feed(html)

    earthquakes = []
    for row in parser.rows:
        if row and row[0][0].strip() in SKIP:
            continue
        eq = parse_row(row)
        if eq:
            earthquakes.append(eq)

    print(f"  Terremotos: {len(earthquakes)}")

    result = {
        "updated":     datetime.now(timezone.utc).isoformat(),
        "source":      "IGN – últimos terremotos",
        "count":       len(earthquakes),
        "earthquakes": earthquakes,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ {OUTPUT} actualizado ({len(earthquakes)} eventos)")


if __name__ == "__main__":
    main()
