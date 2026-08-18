# 🌍 Mapa de Terremotos – España (IGN)

Mapa interactivo público que muestra los terremotos registrados por el
[Instituto Geográfico Nacional (IGN)](https://www.ign.es) en tiempo casi real.

**🌐 Ver mapa:** https://aalasan202.github.io/mapaterremotos/

---

## ¿Cómo funciona?

| Componente | Descripción |
|---|---|
| **Fuente de datos** | Feed RSS del IGN: `https://www.ign.es/ign/RssTools/sismologia.xml` |
| **Actualización** | GitHub Actions descarga el feed cada **10 minutos** y guarda `data/earthquakes.json` |
| **Mapa** | Página estática servida por **GitHub Pages** (Leaflet.js + OpenStreetMap/CARTO) |
| **Fallback** | Si el JSON no está disponible, el navegador descarga el RSS directamente vía proxy CORS |
| **Auto‑refresco** | La página se actualiza sola cada **5 minutos** |

## Configuración (solo la primera vez)

### 1. Activar GitHub Pages

1. Ve a **Settings → Pages** en este repositorio.
2. En *Source*, elige **Deploy from a branch**.
3. Selecciona la rama **main** y la carpeta **/ (root)**.
4. Guarda. En 1‑2 minutos el mapa estará en:
   `https://aalasan202.github.io/mapaterremotos/`

### 2. Activar GitHub Actions

Los workflows ya están en `.github/workflows/`. GitHub los detecta automáticamente.
Para forzar una primera ejecución:

1. Ve a la pestaña **Actions**.
2. Haz clic en *Actualizar datos de terremotos*.
3. Pulsa **Run workflow**.

### 3. Verificar

Después de la primera ejecución, el archivo `data/earthquakes.json` aparecerá
en el repositorio con los últimos terremotos.

---

## Escala de colores

| Color | Magnitud | Clasificación |
|---|---|---|
| 🔵 Azul | < 1.5 | Micro |
| 🟢 Verde | 1.5 – 2.5 | Menor |
| 🟡 Amarillo | 2.5 – 3.5 | Leve |
| 🟠 Naranja | 3.5 – 4.5 | Moderado |
| 🔴 Rojo | 4.5 – 5.5 | Fuerte |
| 🟣 Violeta | ≥ 5.5 | Mayor |

---

## Tecnologías

- [Leaflet.js](https://leafletjs.com/) — Mapa interactivo
- [CARTO Dark Matter](https://carto.com/basemaps/) — Tiles del mapa
- [GitHub Pages](https://pages.github.com/) — Hosting gratuito
- [GitHub Actions](https://github.com/features/actions) — Automatización de datos
