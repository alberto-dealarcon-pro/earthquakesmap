# 🌍 Mapa de Terremotos – España (IGN)

Mapa interactivo público que muestra los terremotos registrados por el
[Instituto Geográfico Nacional (IGN)](https://www.ign.es) en tiempo casi real.

**🌐 Ver mapa:** https://alberto-dealarcon-pro.github.io/earthquakesmap/

---

## ¿Cómo funciona?

| Componente | Descripción |
|---|---|
| **Fuente de datos** | Web scraping de la página de últimos terremotos del IGN |
| **Actualización** | GitHub Actions ejecuta el scraper cada **~1 minuto** y guarda `data/earthquakes.json` |
| **Mapa** | Página estática servida por **GitHub Pages** (Leaflet.js + OpenStreetMap) |
| **Auto‑refresco** | La página consulta el JSON actualizado cada **60 segundos** |
| **Cobertura** | Últimos **10 días** de actividad sísmica en España y alrededores |

## Funcionalidades

- **Marcadores coloreados** por magnitud, con tamaño proporcional
- **Animación de pulso** sobre el terremoto más reciente
- **Filtro de período** — últimas 24 h, 3 días, 7 días o todos
- **Filtro de magnitud** — todos, ≥1.5, ≥2.5, ≥3.5
- **Popup** con magnitud, localización, hora en horario español y enlace directo a la ficha del IGN
- **Panel lateral** con listado ordenado por fecha, también con enlace al IGN
- **Centrado automático** en el terremoto más reciente cercano a Granada al cargar la página
- **Diseño responsive** adaptado a móvil

## Configuración (solo la primera vez)

### 1. Activar GitHub Pages

1. Ve a **Settings → Pages** en este repositorio.
2. En *Source*, elige **Deploy from a branch**.
3. Selecciona la rama **main** y la carpeta **/ (root)**.
4. Guarda. En 1‑2 minutos el mapa estará disponible.

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
- [OpenStreetMap](https://www.openstreetmap.org/) — Tiles del mapa
- [GitHub Pages](https://pages.github.com/) — Hosting gratuito
- [GitHub Actions](https://github.com/features/actions) — Automatización de datos
- Python (stdlib) — Scraper sin dependencias externas
