"""Scraping por consulta de texto — descubrimiento + cosecha en un solo paso.

Busca en TODO YouTube (canal oficial de la institucion O terceros: vloggers,
noticias, testimonios, comparativas) videos que hablen de la oferta de una
institucion especifica. Descarga video + comentarios directamente.

IMPORTANTE (protocolo de equipo):
- Usa esto para una institución que TE FUE ASIGNADA. No busques instituciones
  de otros países/personas: revisa el registro compartido antes de correr.
- Después de cada corrida, REVISA cada video antes de subir el registro al
  Sheet: marca en la columna Tipo_Fuente si es "Oficial" (canal de la propia
  institución) o "Tercero" (cualquier otro canal). El script no puede saberlo
  solo -> queda en blanco a propósito para que tú lo confirmes.
- Corre esto varias veces por institución, una por cada BLOQUE_ACTUAL, para
  cubrir las 12 etiquetas de la guía de anotación (ver tabla más abajo).
"""
from scraper_yt import buscar_videos, procesar_corrida, top_por_comentarios

# --- Configuración de quién corre esto (para el registro de equipo) ---
PERSONA = "Frank_Figueroa"        # reemplaza con tu nombre, tal como en el Sheet
PAIS = "Argentina"                      # país asignado
INSTITUCION = "Universidad de Buenos Aires"  # nombre oficial para el registro

# Nombres con los que la gente busca esta universidad en YouTube.
# El script buscará con CADA uno de estos nombres por separado y combinará
# los resultados. También se usan como filtro: un video que no mencione
# ninguno de estos nombres (en título, canal o descripción) se descarta.
NOMBRES_BUSQUEDA = ["Universidad de Buenos Aires", "UBA"]

# Mapeo de país a código ISO 3166-1 alpha-2 (lo que usa la API de YouTube)
CODIGOS_PAIS = {
    "Peru": "PE", "Colombia": "CO", "Chile": "CL", "Argentina": "AR",
    "Mexico": "MX", "España": "ES", "Ecuador": "EC", "Bolivia": "BO",
}

# --- Bloques de búsqueda: cubren las 12 etiquetas de la guía en 6 corridas ---
# Cambia BLOQUE_ACTUAL y vuelve a correr el script para cada bloque.
BLOQUES = {
    "Ingreso":     ("matricula admision inscripcion", "Matricula, Admision"),
    "Dinero":      ("pension beca costo", "Costo, Beca"),
    "Programas":   ("carreras maestria posgrado", "Carrera, Postgrado"),
    "Calidad":     ("acreditacion docentes", "CalidadAcademica, Docente"),
    "Vida_Campus": ("campus laboratorios vida universitaria", "Infraestructura, VidaUniversitaria"),
    "Experiencia": ("modalidad virtual experiencia estudiante", "Modalidad, Testimonio"),
}
BLOQUE_ACTUAL = "Ingreso"  # <- cambia esto en cada corrida: Ingreso / Dinero / Programas / Calidad / Vida_Campus / Experiencia

# Valores reducidos para la PRIMERA PRUEBA (barato en cuota).
# Cuando confirmes que todo funciona, puedes subir estos números.
MAX_VIDEOS = 50
TOP_N = 10

if __name__ == "__main__":
    terminos, etiquetas_cubiertas = BLOQUES[BLOQUE_ACTUAL]
    region = CODIGOS_PAIS.get(PAIS, "PE")

    print(f"Bloque: {BLOQUE_ACTUAL} (cubre etiquetas: {etiquetas_cubiertas})")
    print(f"Región de búsqueda: {PAIS} ({region})")
    print(f"Nombres de búsqueda: {NOMBRES_BUSQUEDA}")

    # Buscar con cada nombre/alias por separado y combinar resultados sin duplicados.
    # Esto imita lo que harías tú buscando "UBA admision" y luego
    # "Universidad de Buenos Aires admision" manualmente en YouTube.
    todos_los_ids = []
    vistos = set()
    for nombre in NOMBRES_BUSQUEDA:
        consulta = f"{nombre} {terminos}"
        print(f"\n--- Buscando: '{consulta}' ---")
        ids = buscar_videos(query=consulta, max_videos=MAX_VIDEOS, region_code=region)
        nuevos = 0
        for vid_id in ids:
            if vid_id not in vistos:
                vistos.add(vid_id)
                todos_los_ids.append(vid_id)
                nuevos += 1
        print(f"  -> {nuevos} videos nuevos (no duplicados)")

    print(f"\n>>> Total: {len(todos_los_ids)} videos únicos encontrados.")

    if not todos_los_ids:
        raise SystemExit("Sin IDs válidos para explorar.")

    top_videos = top_por_comentarios(todos_los_ids, TOP_N, palabras_clave=NOMBRES_BUSQUEDA)
    if not top_videos:
        raise SystemExit("No se pudieron obtener estadísticas.")

    procesar_corrida(f"{INSTITUCION}_{BLOQUE_ACTUAL}", top_videos,
                     persona=PERSONA, pais=PAIS, institucion=INSTITUCION,
                     bloque_busqueda=BLOQUE_ACTUAL)
