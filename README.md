# Proyecto: Scraper de videos y comentarios de YouTube

Este proyecto descarga videos de YouTube (según canal o búsqueda de texto) junto con
sus comentarios, para análisis posterior (anotación, NER, clasificación NPS, etc.).

## ¿Qué hace cada archivo?

| Archivo | Función |
| :---- | :---- |
| `scraper_yt.py` | Módulo núcleo: búsqueda, ranking por comentarios, extracción de comentarios, descarga de video. No se ejecuta directo. |
| `scraper_consulta.py` | Runner: busca videos por texto libre (ej. "mejores universidades de lima"). |
| `scraper_canales.py` | Runner: busca videos dentro de canales institucionales específicos. |

Ambos runners solo cambian **qué buscar**; toda la lógica pesada vive en `scraper_yt.py`.

---

## Paso 1: Requisitos previos

- Python 3.9 o superior instalado.
- `ffmpeg` instalado (necesario para fusionar video+audio en calidad completa):
  - Windows: `winget install Gyan.FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- Una cuenta de Google (no requiere tarjeta de crédito ni facturación).

---

## Paso 2: Obtener tu propia API Key de YouTube

**Cada persona del equipo debe generar SU PROPIA key.** No compartan una sola key entre
varios colaboradores: la cuota diaria es por proyecto de Google Cloud, y si la comparten
se agota más rápido y no sabrán quién la usó.

1. Ve a [console.cloud.google.com](https://console.cloud.google.com) e inicia sesión.
2. Arriba, clic en el selector de proyecto → **New Project** → ponle un nombre (ej. `scraper-yt`) → **Create**.
3. Verifica que el proyecto recién creado quede **seleccionado** en el selector de arriba.
4. Menú ☰ → **APIs & Services** → **Library**.
5. Busca `YouTube Data API v3`, ábrela, clic en **Enable**.
6. Menú ☰ → **APIs & Services** → **Credentials** → **+ Create Credentials** → **API key**.
7. Copia la key que aparece (empieza con `AIza...`).
8. (Recomendado) Antes de cerrar el diálogo: sección **API restrictions** → **Restrict key** →
   selecciona solo `YouTube Data API v3` → **Save**. Esto evita que la key, si se filtra,
   pueda usarse para otra cosa.

No se necesita facturación habilitada para nada de esto. La cuota gratuita por defecto
alcanza para pruebas normales de este proyecto.

---

## Paso 3: Instalar el proyecto

```bash
# Clona o descarga esta carpeta, luego entra a ella
cd proyecto-scraper-yt

# (Recomendado) crea un entorno virtual
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Instala dependencias
pip install -r requirements.txt
```

## Paso 4: Configurar tu API key

1. Copia el archivo `.env.example` y renómbralo a `.env`.
2. Ábrelo y reemplaza el texto de ejemplo por tu key real:

```
YOUTUBE_API_KEY=AIzaSy...tu_key_real...
```

3. Guarda el archivo. **Nunca subas `.env` a un repositorio compartido** — el `.gitignore`
   ya está configurado para ignorarlo automáticamente, pero verifica antes de hacer `git push`.

El script carga esta variable automáticamente gracias a `python-dotenv`; no hace falta
hacer `export` manual en la terminal cada vez.

---

## Paso 5: Correr una prueba pequeña primero

`scraper_consulta.py` ya viene configurado con valores reducidos para la primera prueba
(`MAX_VIDEOS = 5`, `TOP_N = 2`) para no gastar mucha cuota ni esperar mucho:

```bash
python scraper_consulta.py
```

Deberías ver en consola:
1. Cuántos videos encontró la búsqueda.
2. El ranking de los 2 con más comentarios.
3. El proceso de descarga y extracción de comentarios de cada uno.

Al terminar, revisa la carpeta `videosYT/` — debería tener una subcarpeta por video con
`video.mkv` + `comentarios.csv`, y un `comentarios_masivos_yt.csv` general.

---

## Paso 6: Correr el proyecto real

Cuando la prueba funcionó, edita los parámetros según tu necesidad:

**Para búsqueda libre** (`scraper_consulta.py`):
```python
CONSULTA = "tu búsqueda aquí"
MAX_VIDEOS = 50   # cuántos candidatos explorar
TOP_N = 25        # cuántos se procesan al final (los de más comentarios)
```

**Para canales específicos** (`scraper_canales.py`):
```python
CANALES = [("@handle_del_canal", "nombre_para_la_carpeta"), ...]
```

Luego corre el que corresponda:
```bash
python scraper_consulta.py
python scraper_canales.py
```

---

## Notas de cuota y buenas prácticas

- Cada búsqueda (`search.list`) cuesta más cuota que otras llamadas — evita subir
  `MAX_VIDEOS` innecesariamente alto en pruebas.
- Hay un límite de **2 GB de descarga de video por corrida** (`LIMITE_DESCARGA_BYTES`
  en `scraper_yt.py`). Al alcanzarlo, el script sigue extrayendo comentarios pero deja
  de descargar video.
- Si la API responde error de cuota agotada, hay que esperar al reinicio diario
  (medianoche hora del Pacífico) o revisar el consumo en Google Cloud Console →
  APIs & Services → tu API → pestaña Quotas.
- No compartan su archivo `.env` ni peguen su key en chats, tickets o repositorios públicos.

---

## Problemas comunes

| Síntoma | Causa probable | Solución |
| :---- | :---- | :---- |
| `SystemExit: Falta la variable de entorno YOUTUBE_API_KEY` | No creaste `.env` o le falta la key | Revisa el Paso 4 |
| Descarga de video en baja calidad | Falta `ffmpeg` en el sistema | Instálalo (ver Paso 1) |
| Error 403 con "quotaExceeded" | Se agotó la cuota diaria de tu proyecto | Espera al reinicio diario o baja `MAX_VIDEOS` |
| `commentsDisabled` en consola | El video tiene comentarios deshabilitados | Es normal, el script lo omite y sigue |
