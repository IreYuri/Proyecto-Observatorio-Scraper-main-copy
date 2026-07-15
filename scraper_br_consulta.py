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
PERSONA = "Steffi_Yurivilca"        # reemplaza con tu nombre, tal como en el Sheet
PAIS = "Brasil"                      # país asignado
INSTITUCION = "Universidade Estadual de Campinas"  # nombre oficial para el registro

# Nombres con los que la gente busca esta universidad en YouTube.
# El script buscará con CADA uno de estos nombres por separado y combinará
# los resultados. También se usan como filtro: un video que no mencione
# ninguno de estos nombres (en título, canal o descripción) se descarta.
NOMBRES_BUSQUEDA = ["Universidade Estadual de Campinas", "UNICAMP"]

# Mapeo de país a código ISO 3166-1 alpha-2 (lo que usa la API de YouTube)
CODIGOS_PAIS = {
    "Peru": "PE", "Colombia": "CO", "Chile": "CL", "Argentina": "AR",
    "Mexico": "MX", "España": "ES", "Ecuador": "EC", "Bolivia": "BO",
    "Uruguay":"UR", "Brasil": "BR",
}

# --- Bloques de búsqueda: cubren las 12 etiquetas de la guía en 6 corridas ---
# Cada bloque tiene una LISTA de búsquedas cortas (1-2 palabras cada una).
# El script buscará cada término POR SEPARADO con cada nombre de NOMBRES_BUSQUEDA.
# Ejemplo: ["beca", "costo"] con ["UBA", "Univ..."] genera 4 búsquedas independientes.
BLOQUES = {
    "Ingreso":     (["vestibular", "ingresso","processo seletivo","inscrição vestibular","como entrar na UNICAMP","como ingressar na UNICAMP","prova UNICAMP","enem UNICAMP","candidato UNICAMP","resultado vestibular" ], "Matricula, Admision"),
    "Dinero":      (["bolsas","bolsa de estudos","auxílio financeiro","assistência estudantil","benefícios estudantis","custo de vida","quanto custa estudar na UNICAMP", "mensalidade UNICAMP","taxa de matrícula","financiamento estudantil"], "Costo, Beca"),
    "Programas":   (["cursos UNICAMP","graduação","curso de graduação","bacharelado","licenciatura","engenharia UNICAMP","medicina UNICAMP","pós-graduação","mestrado","doutorado","especialização"], "Carrera, Postgrado"),
    "Calidad":     (["ranking UNICAMP","melhor universidade","qualidade acadêmica","excelência acadêmica","pesquisa científica","inovação","produção científica","reconhecimento internacional","avaliação universitária","universidade pública de excelência"], "CalidadAcademica, Docente"),
    "Vida_Campus": (["campus UNICAMP","vida universitária","moradia estudantil","biblioteca UNICAMP","laboratórios UNICAMP","infraestrutura UNICAMP","cidade universitária","intercâmbio UNICAMP","estudantes UNICAMP","rotina universitária"], "Infraestructura, VidaUniversitaria"),
    "Experiencia": (["minha experiência na UNICAMP","estudar na UNICAMP","como é estudar na UNICAMP","vlog UNICAMP","dia de estudante UNICAMP","depoimento aluno UNICAMP","experiência universitária","calouro UNICAMP","minha rotina UNICAMP"], "Modalidad, Testimonio"),
}
BLOQUE_ACTUAL = "Experiencia"  # <- cambia esto en cada corrida: Ingreso / Dinero / Programas / Calidad / Vida_Campus / Experiencia

# Cuántos videos traer POR CADA sub-consulta y cuántos descargar al final.
MAX_VIDEOS = 80
TOP_N = 10
MIN_COMENTARIOS = 75  # Límite estricto del proyecto

if __name__ == "__main__":
    terminos_lista, etiquetas_cubiertas = BLOQUES[BLOQUE_ACTUAL]
    region = CODIGOS_PAIS.get(PAIS, "BR")

    print(f"Bloque: {BLOQUE_ACTUAL} (cubre etiquetas: {etiquetas_cubiertas})")
    print(f"Región de búsqueda: {PAIS} ({region})")
    print(f"Nombres de búsqueda: {NOMBRES_BUSQUEDA}")
    print(f"Términos del bloque: {terminos_lista}")

    # Buscar con cada combinación de nombre × término por separado.
    # Esto imita lo que harías tú buscando "UBA beca", luego "UBA costo",
    # luego "Universidad de Buenos Aires beca", etc.
    todos_los_ids = []
    vistos = set()
    for nombre in NOMBRES_BUSQUEDA:
        for terminos in terminos_lista:
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

    top_videos = top_por_comentarios(todos_los_ids, TOP_N, palabras_clave=NOMBRES_BUSQUEDA,
                                     min_comentarios=MIN_COMENTARIOS, palabras_tema=terminos_lista)
    if not top_videos:
        raise SystemExit("No se pudieron obtener estadísticas.")

    procesar_corrida(f"{INSTITUCION}_{BLOQUE_ACTUAL}", top_videos,
                     persona=PERSONA, pais=PAIS, institucion=INSTITUCION,
                     bloque_busqueda=BLOQUE_ACTUAL)
