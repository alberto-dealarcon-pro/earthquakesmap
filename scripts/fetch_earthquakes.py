#!/usr/bin/env python3
"""
Descarga el feed RSS de sismología del IGN y genera data/earthquakes.json.
Este script lo ejecuta GitHub Actions cada 10 minutos.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import re
import os
from datetime import datetime, timezone

FEED_URL    = "https://www.ign.es/ign/RssTools/sismologia.xml"
OUTPUT_FILE = "data/earthquakes.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; earthquake-map/1.0; +https://github.com)"
}


def fetch_feed():
    req = urllib.request.Request(FEED_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse_feed(content: bytes) -> list:
    root = ET.fromstring(content)
    ns   = {"geo": "http://www.w3.org/2003/01/geo/wgs84_pos#"}

    earthquakes = []
    for item in root.findall(".//item"):
        try:
            title       = (item.findtext("title") or "").strip()
            description = (item.findtext("description") or "").strip()
            link        = (item.findtext("link") or item.findtext("guid") or "").strip()

            lat_el = item.find("geo:lat",  ns)
            lon_el = item.find("geo:long", ns)
            if lat_el is None or lon_el is None:
                continue

            lat = float(lat_el.text.strip())
            lon = float(lon_el.text.strip())

            # Magnitud: "terremoto de magnitud 2.8 en …"
            mag_m = re.search(r"magnitud[e]?\s+([\d.]+)", description, re.IGNORECASE)
            magnitude = float(mag_m.group(1)) if mag_m else 0.0

            # Localización: "magnitud X.X en LUGAR en la fecha"
            loc_m = re.search(
                r"magnitud[e]?\s+[\d.]+\s+en\s+(.+?)\s+en\s+la\s+fecha",
                description, re.IGNORECASE
            )
            location = loc_m.group(1).strip() if loc_m else ""

            # Fecha: "DD/MM/YYYY H:MM:SS"
            date_m = re.search(
                r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})",
                title + " " + description
            )
            date_str = date_m.group(1) if date_m else ""

            # ID de evento
            evid_m = re.search(r"evid=([^&\"]+)", link)
            event_id = evid_m.group(1) if evid_m else ""

            earthquakes.append({
                "id":          event_id,
                "lat":         lat,
                "lon":         lon,
                "magnitude":   magnitude,
                "location":    location,
                "date":        date_str,
                "description": description,
                "link":        link,
            })
        except (ValueError, AttributeError) as exc:
            print(f"  ⚠ Saltando ítem: {exc}")
            continue

    return earthquakes


def main():
    print(f"Descargando {FEED_URL} …")
    content = fetch_feed()
    print(f"Recibidos {len(content):,} bytes")

    eqs = parse_feed(content)
    print(f"Procesados {len(eqs)} terremotos")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    data = {
        "updated":     datetime.now(timezone.utc).isoformat(),
        "count":       len(eqs),
        "source":      FEED_URL,
        "earthquakes": eqs,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
