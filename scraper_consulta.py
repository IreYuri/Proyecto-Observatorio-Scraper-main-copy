"""Scraping por consulta de texto — Fase 1 del protocolo: descubrimiento.

Top N videos con más comentarios para la búsqueda -> carpeta nombrada según
la consulta con subcarpeta por video (video.mkv + comentarios.csv)
+ CSV general. Descarga limitada a 2 GB por corrida.

IMPORTANTE (protocolo de equipo): usa esto para descubrir/explorar candidatos
de una institución que TE FUE ASIGNADA. No busques instituciones de otros
países/personas: revisa el registro compartido antes de correr.
"""
from scraper_yt import buscar_videos, procesar_corrida, top_por_comentarios

# --- Configuración de quién corre esto (para el registro de equipo) ---
PERSONA = "Nombre_Apellido"        # reemplaza con tu nombre, tal como en el Sheet
PAIS = "Peru"                      # país asignado
INSTITUCION = "Nombre_Institucion"  # institución asignada que estás explorando

# Valores reducidos para la PRIMERA PRUEBA (barato en cuota).
# Cuando confirmes que todo funciona, puedes subir estos números.
CONSULTA = f"{INSTITUCION} matrícula admisión"
MAX_VIDEOS = 5
TOP_N = 2

if __name__ == "__main__":
    videos = buscar_videos(query=CONSULTA, max_videos=MAX_VIDEOS)
    if not videos:
        raise SystemExit("Sin IDs válidos para explorar.")

    top_videos = top_por_comentarios(videos, TOP_N)
    if not top_videos:
        raise SystemExit("No se pudieron obtener estadísticas.")

    procesar_corrida(CONSULTA, top_videos,
                     persona=PERSONA, pais=PAIS, institucion=INSTITUCION)
