#!/usr/bin/env python3
"""ChambaKit: el archivo de registros de la copia (11/REG-LOCAL).

Uso, con el Python del entorno virtual de la copia (en Windows, .venv\\Scripts\\python.exe):
    .venv/bin/python -I herramientas/registros.py crear
    .venv/bin/python -I herramientas/registros.py agregar [FILAS.json]
    .venv/bin/python -I herramientas/registros.py actualizar [CAMBIOS.json]
    .venv/bin/python -I herramientas/registros.py leer PESTAÑA [--id ID ...] [--columna COLUMNA]
    .venv/bin/python -I herramientas/registros.py informe BUS-ID
    .venv/bin/python -I herramientas/registros.py instantanea

El archivo es <archivo.nombre>.xlsx en la raíz de la copia, con las pestañas del bloque de 11/REG-ESQUEMA y
sus columnas guardadas: las calculadas de informes no se guardan, las da la orden informe.

- crear: el archivo vacío, con los encabezados. No sobrescribe uno que ya exista.
- agregar: filas nuevas, {pestaña: [{columna: texto}]}, de varias pestañas a la vez. Las referencias se
  resuelven contra lo ya registrado más lo de la misma llamada, así que una vacante nueva y su primera
  observación van juntas.
- actualizar: columnas de filas ya registradas, {pestaña: [{columna_id: ID, columna: texto nuevo}]}. El
  ID no cambia; el texto vacío borra el valor.
- leer: las filas de una pestaña, o solo las que tienen esos IDs en la primera columna o en --columna.
- informe: la tabla resumen de una búsqueda (08/EVAL-INFORME), con las columnas calculadas de informes
  (11/REG-CAMPOS) a la fecha de hoy en la zona horaria de 04 y con el umbral de «antigua» de 08/EVAL-ACUERDOS.
- instantanea: regenera completa la instantánea que lee el canal Web (11/REG-INSTANTANEA), en instantanea/:
  informes.md, con las últimas 10 búsquedas y su tabla resumen, y vacantes.md, con una sección por vacante
  evaluada cuya última observación no es Cerrada. Agregar y actualizar la regeneran después de escribir. Si
  pasa de 300 KB, lo avisa en stderr sin fallar.

Agregar y actualizar comprueban cada fila que escriben contra el esquema: tipos, listas
(empresa_id, contra 06/CAT-EMPRESAS), obligatoriedad, IDs únicos y referencias. Con un solo error no
escriben nada: dicen todos en stderr y terminan con código 1. El JSON va a stdout. Si falta la
configuración, el archivo u openpyxl, o se pide una pestaña o búsqueda inexistente, termina con código 2
y dice qué falla.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULO_04 = os.path.join(RAIZ, "04_PREFERENCIAS_LABORALES.md")
MODULO_06 = os.path.join(RAIZ, "06_EMPRESAS_OBJETIVO.md")
MODULO_08 = os.path.join(RAIZ, "08_EVALUACION_DE_VACANTES.md")
MODULO_11 = os.path.join(RAIZ, "11_ESQUEMAS_DE_REGISTROS.md")
CARPETA_INSTANTANEA = "instantanea"
ULTIMAS_BUSQUEDAS = 10
AVISO_INSTANTANEA_KB = 300
UMBRAL_DE_ANTIGUA = 20


def error(mensaje):
    """Configuración, archivo o biblioteca que falta: termina con código 2 sin tocar el archivo."""
    print(mensaje, file=sys.stderr)
    sys.exit(2)


def leer_modulo(ruta, para):
    try:
        with open(ruta, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        error(f"{ruta}: no se pudo leer el módulo, de donde salen {para} ({e.strerror}).")


def seccion(md, titulo, nivel="##"):
    """Texto de la sección `<nivel> <titulo>` hasta la siguiente del mismo nivel o mayor."""
    m = re.search(rf"^{nivel} {re.escape(titulo)}(?![\w-]).*?(?=^#{{2,{len(nivel)}}} |\Z)", md, re.M | re.S)
    return m.group(0) if m else None


def bloque_json(texto):
    """Contenido del primer bloque ```json del texto, o None."""
    m = texto and re.search(r"^```json\n(.*?)^```", texto, re.M | re.S)
    return m.group(1) if m else None


def leer_esquema():
    """Bloque de 11/REG-ESQUEMA."""
    ruta = MODULO_11
    bloque = bloque_json(seccion(leer_modulo(ruta, "las pestañas y sus columnas"), "REG-ESQUEMA"))
    if bloque is None:
        error(f"{ruta}: falta el bloque del esquema (```json) en la sección REG-ESQUEMA.")
    try:
        esquema = json.loads(bloque)
    except ValueError as e:
        error(f"{ruta}: el bloque de REG-ESQUEMA no es JSON válido ({e}).")
    if not (isinstance(esquema, dict) and isinstance(esquema.get("archivo"), dict)
            and isinstance(esquema["archivo"].get("nombre"), str) and isinstance(esquema.get("pestanas"), list)):
        error(f"{ruta}, REG-ESQUEMA: el bloque debe ser un objeto con archivo.nombre y pestanas.")
    return esquema


def guardadas(pestana):
    """Las columnas que guarda el archivo: todas menos las calculadas, que son una vista."""
    return [c for c in pestana["columnas"] if c["tipo"] != "calculada"]


def encabezados(pestana):
    """Los nombres de las columnas guardadas, en orden: la fila 1 de la pestaña en el archivo."""
    return [c["nombre"] for c in guardadas(pestana)]


def clave(pestana):
    """La primera columna, la que identifica la fila: su ID, o en informes, su búsqueda."""
    return pestana["columnas"][0]

def pestana_del_esquema(esquema, nombre):
    for p in esquema["pestanas"]:
        if p["nombre"] == nombre:
            return p
    error(f"{nombre!r} no es una pestaña de 11/REG-ESQUEMA; opciones: "
          f"{', '.join(p['nombre'] for p in esquema['pestanas'])}.")


def biblioteca_xlsx():
    """openpyxl, o termina con código 2 si este Python no la tiene."""
    try:
        import openpyxl as biblioteca
    except ImportError:
        error("Falta openpyxl. Corre la herramienta con el Python del entorno virtual de la copia "
              "(.venv/bin/python; en Windows, .venv\\Scripts\\python.exe). Si no existe, lo instala "
              "`/configurar`, paso 8 (Registros).")
    return biblioteca


def ruta_archivo(esquema):
    return os.path.join(RAIZ, esquema["archivo"]["nombre"] + ".xlsx")


def crear(esquema):
    ruta = ruta_archivo(esquema)
    if os.path.exists(ruta):
        error(f"{ruta} ya existe; no se sobrescribe.")
    libro = biblioteca_xlsx().Workbook()
    libro.remove(libro.active)
    for p in esquema["pestanas"]:
        pestana = libro.create_sheet(p["nombre"])
        pestana.append(encabezados(p))
        pestana.freeze_panes = "A2"
    libro.save(ruta)
    return {"archivo": ruta, "pestanas": {p["nombre"]: encabezados(p)
                                          for p in esquema["pestanas"]}}


def abrir(esquema):
    """El libro y {pestaña: [fila como {columna: texto}]}, con los encabezados comprobados contra 11."""
    ruta = ruta_archivo(esquema)
    if not os.path.exists(ruta):
        error(f"{ruta}: no existe el archivo de registros; lo crea `/configurar`, paso 8 (Registros).")
    libro = biblioteca_xlsx().load_workbook(ruta)
    filas = {}
    for p in esquema["pestanas"]:
        columnas = encabezados(p)
        if p["nombre"] not in libro.sheetnames:
            error(f"{ruta}: falta la pestaña {p['nombre']} de 11/REG-ESQUEMA.")
        valores = libro[p["nombre"]].iter_rows(values_only=True)
        en_el_archivo = list(next(valores, ()))
        if en_el_archivo != columnas:
            error(f"{ruta}, pestaña {p['nombre']}: los encabezados {en_el_archivo} no coinciden con los de "
                  f"11/REG-ESQUEMA, {columnas} (11/REG-DECISIONES, «Encabezados»).")
        filas[p["nombre"]] = [dict(zip(columnas, ("" if v is None else str(v) for v in fila)))
                              for fila in valores if any(v not in (None, "") for v in fila)]
    return libro, filas


def escribir(celda, valor):
    """Un valor como texto. openpyxl tomaría por fórmula un texto que empieza con «=», como uno copiado de un
    anuncio, y una hoja de cálculo lo evaluaría al abrir el archivo."""
    celda.value, celda.number_format = valor or None, "@"
    if valor:
        celda.data_type = "s"


def guardar(libro, ruta):
    """Escribe el libro completo en un archivo temporal y lo pone en lugar del anterior: nunca queda a medias."""
    temporal = ruta + ".tmp"
    try:
        libro.save(temporal)
        os.replace(temporal, ruta)
    finally:
        if os.path.exists(temporal):
            os.remove(temporal)


def rechazar(errores):
    """Filas que no cumplen el esquema: las dice todas y termina con código 1 sin escribir ninguna."""
    for e in errores:
        print(e, file=sys.stderr)
    print("No se escribió ninguna fila.", file=sys.stderr)
    sys.exit(1)


def leer_entrada(archivo):
    """El JSON de las filas, de un archivo o de stdin ("-")."""
    try:
        if archivo == "-":
            return json.load(sys.stdin)
        with open(archivo, encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        rechazar([f"{archivo}: no se pudo leer ({e.strerror})."])
    except ValueError as e:
        rechazar([f"Las filas no son JSON válido ({e})."])


def filas_de_entrada(esquema, entrada):
    """{pestaña: [{columna: texto}]} de la entrada, con null como texto vacío, o la rechaza si no tiene esa
    forma o nombra pestañas o columnas que el archivo no guarda."""
    if not isinstance(entrada, dict):
        rechazar(["La entrada debe ser un objeto JSON {pestaña: [fila, ...]}."])
    pestanas = {p["nombre"]: p for p in esquema["pestanas"]}
    errores, filas = [], {}
    for nombre, nuevas in entrada.items():
        if nombre not in pestanas:
            errores.append(f"{nombre!r} no es una pestaña de 11/REG-ESQUEMA; opciones: {', '.join(pestanas)}.")
            continue
        if not (isinstance(nuevas, list) and all(isinstance(f, dict) for f in nuevas)):
            errores.append(f"{nombre}: las filas deben ser una lista de objetos {{columna: valor}}.")
            continue
        columnas = {c["nombre"]: c for c in pestanas[nombre]["columnas"]}
        filas[nombre] = []
        for n, fila in enumerate(nuevas, 1):
            for c, v in fila.items():
                if c not in columnas:
                    errores.append(f"{nombre}, fila {n}: {c!r} no es una columna de {nombre}.")
                elif columnas[c]["tipo"] == "calculada":
                    errores.append(f"{nombre}, fila {n}: {c} se calcula (orden informe); no se escribe.")
                elif not isinstance(v, (str, type(None))):
                    errores.append(f"{nombre}, fila {n}: {c} debe ser texto, entre comillas; dice {v!r}.")
            filas[nombre].append({c: v or "" for c, v in fila.items()})
    if errores:
        rechazar(errores)
    return filas


def leer_catalogo():
    """Los EMP-ID de 06/CAT-EMPRESAS."""
    ruta = MODULO_06
    catalogo = seccion(leer_modulo(ruta, "los IDs de empresa_id"), "CAT-EMPRESAS")
    if catalogo is None:
        error(f"{ruta}: falta la sección CAT-EMPRESAS, el catálogo de empresas.")
    return re.findall(r"^\|\s*(EMP-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*\|", catalogo, re.M)


def es_fecha(valor, con_hora):
    m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})( \d{2}:\d{2})?", valor)
    if not m or (m.group(2) and not con_hora):
        return False
    try:
        dt.datetime.strptime(valor, "%Y-%m-%d %H:%M" if m.group(2) else "%Y-%m-%d")
    except ValueError:
        return False
    return True


def comprobar(esquema, todas, revisar):
    """Errores de las filas de revisar [(pestaña, fila, etiqueta)] según 11/REG-ESQUEMA. Las referencias
    y la unicidad se resuelven contra todas: las ya registradas más las de esta llamada."""
    pestanas = {p["nombre"]: p for p in esquema["pestanas"]}
    por_id = {nombre: {} for nombre in todas}
    for nombre, filas in todas.items():
        primera = clave(pestanas[nombre])["nombre"]
        for f in filas:
            por_id[nombre].setdefault(f[primera], []).append(f)
    catalogo = []
    errores = []
    for nombre, fila, etiqueta in revisar:
        def mal(columna, mensaje):
            errores.append(f"{nombre}, {etiqueta}: {columna}: {mensaje}")

        for c in guardadas(pestanas[nombre]):
            col, v = c["nombre"], fila[c["nombre"]]
            if v == "":
                if c.get("oblig") == "si" and not (c.get("vacia_con") and fila[c["vacia_con"]]):
                    mal(col, "es obligatoria y está vacía.")
                continue
            tipo = c["tipo"]
            if tipo in ("id", "ref") and not re.fullmatch(f"(PRUEBA-)?{c['patron']}", v):
                mal(col, f"«{v}» no tiene la forma {c['patron']}.")
            elif tipo == "id":
                if sum(f[col] == v for f in todas[nombre]) > 1:
                    mal(col, f"«{v}» se repite en {nombre}; los IDs no se reutilizan.")
            elif tipo == "ref":
                citadas = por_id[c["en"]].get(v, [])
                if not citadas:
                    mal(col, f"«{v}» no existe en {c['en']}.")
                elif c.get("misma_vacante") and not any(f["vacante_id"] == fila["vacante_id"] for f in citadas):
                    mal(col, f"«{v}» es de otra vacante, no de {fila['vacante_id']}.")
                if c.get("unica_con") and sum(f[col] == v and f[c["unica_con"]] == fila[c["unica_con"]]
                                              for f in todas[nombre]) > 1:
                    mal(col, f"la pareja {c['unica_con']} «{fila[c['unica_con']]}» + «{v}» se repite en {nombre}.")
                if c.get("distinta_de") and v == fila[c["distinta_de"]]:
                    mal(col, f"no puede ser igual a {c['distinta_de']}.")
            elif tipo == "fecha" and not es_fecha(v, c.get("hora")):
                forma = "AAAA-MM-DD o AAAA-MM-DD HH:MM" if c.get("hora") else "AAAA-MM-DD, sin hora"
                mal(col, f"«{v}» no es una fecha real con la forma {forma}.")
            elif tipo == "url" and not re.fullmatch(r"https?://\S+", v):
                mal(col, f"«{v}» no es una URL que empiece con http:// o https:// y sin espacios.")
            elif tipo == "patron" and not re.fullmatch(c["patron"], v):
                mal(col, f"«{v}» no tiene la forma {c['patron']}.")
            elif tipo == "lista":
                if "valores_de" in c:
                    if c["valores_de"] != "06/CAT-EMPRESAS":
                        error(f"{MODULO_11}, REG-ESQUEMA: valores_de {c['valores_de']!r} desconocido.")
                    catalogo = catalogo or leer_catalogo()
                    if v not in catalogo:
                        mal(col, f"«{v}» no está en el catálogo de 06 (CAT-EMPRESAS); dala de alta ahí primero.")
                elif v not in c["valores"]:
                    mal(col, f"«{v}» no es uno de: {' / '.join(c['valores'])}.")
    return errores


def agregar(esquema, entrada):
    columnas = {p["nombre"]: encabezados(p) for p in esquema["pestanas"]}
    nuevas = {nombre: [{c: f.get(c, "") for c in columnas[nombre]} for f in filas]
              for nombre, filas in filas_de_entrada(esquema, entrada).items()}
    libro, registradas = abrir(esquema)
    todas = {nombre: filas + nuevas.get(nombre, []) for nombre, filas in registradas.items()}
    revisar = [(nombre, fila, f"fila {n}")
               for nombre, filas in nuevas.items() for n, fila in enumerate(filas, 1)]
    errores = comprobar(esquema, todas, revisar)
    if errores:
        rechazar(errores)
    vistas = instantanea(esquema, todas)
    for nombre, filas in nuevas.items():
        pestana = libro[nombre]
        for fila in filas:
            numero = pestana.max_row + 1
            for i, valor in enumerate(fila.values(), 1):
                escribir(pestana.cell(numero, i), valor)
    guardar(libro, ruta_archivo(esquema))
    guardar_instantanea(vistas)
    return {"agregadas": {nombre: len(filas) for nombre, filas in nuevas.items()}}


def actualizar(esquema, entrada):
    """Cambia las columnas dadas de filas ya registradas, cada una identificada por su ID (la primera columna).
    Las filas cambiadas se comprueban completas, como al agregarlas."""
    cambios = filas_de_entrada(esquema, entrada)
    libro, registradas = abrir(esquema)
    todas = {nombre: [dict(f) for f in filas] for nombre, filas in registradas.items()}
    errores, revisar = [], []
    for nombre, filas in cambios.items():
        id_ = clave(pestana_del_esquema(esquema, nombre))
        if id_["tipo"] != "id":
            errores.append(f"{nombre}: sus filas no tienen ID propio y no se actualizan.")
            continue
        for n, cambio in enumerate(filas, 1):
            valor = cambio.get(id_["nombre"])
            fila = next((f for f in todas[nombre] if valor and f[id_["nombre"]] == valor), None)
            if fila is None:
                errores.append(f"{nombre}, fila {n}: {id_['nombre']} «{valor or ''}» no está registrado; cada "
                               f"cambio lleva el ID de una fila de {nombre}.")
                continue
            fila.update(cambio)
            revisar.append((nombre, fila, valor))
    errores += comprobar(esquema, todas, revisar)
    if errores:
        rechazar(errores)
    vistas = instantanea(esquema, todas)
    for nombre, filas in cambios.items():
        pestana = libro[nombre]
        columnas = encabezados(pestana_del_esquema(esquema, nombre))
        for cambio in filas:
            numero = next(celda.row for celda in pestana["A"] if celda.value == cambio[columnas[0]])
            for columna, valor in cambio.items():
                escribir(pestana.cell(numero, columnas.index(columna) + 1), valor)
    guardar(libro, ruta_archivo(esquema))
    guardar_instantanea(vistas)
    return {"actualizadas": {nombre: len(filas) for nombre, filas in cambios.items()}}


def leer_zona_horaria():
    """La zona_horaria del bloque de 04/PREF-UBICACION, con la que se cuenta la antigüedad."""
    ruta = MODULO_04
    bloque = bloque_json(seccion(leer_modulo(ruta, "la zona horaria"), "PREF-UBICACION"))
    try:
        zona = json.loads(bloque or "null")["zona_horaria"]
    except (ValueError, TypeError, KeyError):
        zona = None
    if not isinstance(zona, str):
        error(f"{ruta}, PREF-UBICACION: falta la zona_horaria del bloque; llénala con `/configurar`, paso 4 "
              "(Preferencias).")
    try:
        return ZoneInfo(zona)
    except (ValueError, KeyError):
        error(f"{ruta}, PREF-UBICACION: zona_horaria no es una zona IANA conocida: {zona!r}. Si el nombre es "
              "correcto, al entorno virtual le falta la base de zonas horarias (en Windows: "
              "`.venv\\Scripts\\python.exe -m pip install tzdata`).")


def umbral_de_antigua():
    """Los días de la marca «antigua», de su línea en 08/EVAL-ACUERDOS; sin esa línea, los 20 por defecto."""
    ruta = MODULO_08
    acuerdos = seccion(leer_modulo(ruta, "el umbral de «antigua»"), "EVAL-ACUERDOS") or ""
    linea = re.search(r"^- \*\*Marca «antigua»:\*\*.*$", acuerdos, re.M)
    if linea is None:
        return UMBRAL_DE_ANTIGUA
    dias = re.search(r"a partir de \**(\d+)\**\s+días?\b", linea.group(0))
    if dias is None:
        error(f"{ruta}, EVAL-ACUERDOS: la línea «Marca «antigua»» debe decir «a partir de N días», con N en "
              "cifras; dice: " + linea.group(0))
    return int(dias.group(1))


def antiguedad(vacante, hoy, umbral):
    """08/EVAL-ANTIGUEDAD: «N d» desde la más antigua entre fecha_publicacion y
    primera_deteccion; «≥ N d» si solo hay primera_deteccion; «—» si además se detectó hoy."""
    publicada, detectada = vacante["fecha_publicacion"], vacante["primera_deteccion"]
    try:
        n = max((hoy - dt.datetime.strptime(f, "%Y-%m-%d").date()).days
                for f in ((detectada,) if publicada == "" else (publicada, detectada)))
    except ValueError:
        return "#VALUE!"
    if publicada == "" and n <= 0:
        return "—"
    return ("≥ " if publicada == "" else "") + f"{n} d" + (" · antigua" if n >= umbral else "")


def encaje(evaluacion):
    if evaluacion["condiciones"] == "Excluida":
        return "—"
    return evaluacion["encaje"] + (" · " + evaluacion["cobertura"] if evaluacion["cobertura"] else "")


def alertas(evaluacion):
    """Si está excluida, su detalle; si no, los núcleos insuficientes y académicos y los pendientes poco
    habituales (08/EVAL-INFORME)."""
    detalle = evaluacion["condiciones_detalle"]
    if evaluacion["condiciones"] == "Excluida":
        return "Excluida: " + detalle.replace(" | ", "; ")
    nucleos = [n for n in evaluacion["nucleos"].split(" | ") if n]

    def de_categoria(categoria):
        return "; ".join(n for n in nucleos if n.endswith(categoria)).replace(categoria, "")

    insuficientes = de_categoria(": Insuficiente")
    academicas = de_categoria(": Académica/formativa")
    habituales = ("Sueldo", "Duración", "Relación", "Horario", "Ninguno")
    pendientes = ", ".join(p for p in detalle.split(" | ") if p and p not in habituales).lower()
    partes = [titulo + texto for titulo, texto in (("Insuficiente: ", insuficientes), ("Académica: ", academicas),
                                                   ("Pendiente: ", pendientes)) if texto]
    return " · ".join(partes) or "—"


def calculadas(vacante, evaluacion, hoy, umbral):
    """Las columnas calculadas de una fila de informes, como las describe 11/REG-CAMPOS, con #N/A si su vacante
    o su evaluación no existen."""
    if vacante is None:
        de_la_vacante = dict.fromkeys(("empresa", "vacante", "antiguedad", "url_oficial"), "#N/A")
    else:
        job_id = vacante["job_id"]
        de_la_vacante = {
            "empresa": vacante["empresa_id"].replace("EMP-", ""),
            # «No publicado» sin distinguir mayúsculas.
            "vacante": ("sin Job ID" if job_id.casefold() in ("", "no publicado") else job_id) + " — "
                       + vacante["titulo"],
            "antiguedad": antiguedad(vacante, hoy, umbral),
            "url_oficial": vacante["url_oficial"]}
    if evaluacion is None:
        de_la_evaluacion = dict.fromkeys(("encaje", "alertas"), "#N/A")
    else:
        de_la_evaluacion = {"encaje": encaje(evaluacion), "alertas": alertas(evaluacion)}
    return de_la_vacante | de_la_evaluacion


def primeras(filas, columna):
    """{ID: fila}, con la primera fila de cada ID."""
    por_id = {}
    for f in filas:
        por_id.setdefault(f[columna], f)
    return por_id


def tabla_resumen(esquema, filas, busqueda_id, hoy, umbral):
    """Las filas de informes de una búsqueda, en su orden, con sus columnas calculadas a la fecha hoy."""
    vacantes = primeras(filas["vacantes"], "vacante_id")
    evaluaciones = primeras(filas["evaluaciones"], "evaluacion_id")
    columnas = [c["nombre"] for c in pestana_del_esquema(esquema, "informes")["columnas"]]
    tabla = []
    for f in filas["informes"]:
        if f["busqueda_id"] == busqueda_id:
            fila = f | calculadas(vacantes.get(f["vacante_id"]), evaluaciones.get(f["evaluacion_id"]), hoy, umbral)
            tabla.append({c: fila[c] for c in columnas})
    return tabla


def informe(esquema, busqueda_id):
    """La tabla resumen de una búsqueda (08/EVAL-INFORME): sus filas de informes, en su orden, con las
    columnas calculadas a la fecha de hoy."""
    filas = abrir(esquema)[1]
    if not any(f["busqueda_id"] == busqueda_id for f in filas["busquedas"]):
        error(f"{busqueda_id} no existe en busquedas.")
    hoy = dt.datetime.now(leer_zona_horaria()).date()
    return tabla_resumen(esquema, filas, busqueda_id, hoy, umbral_de_antigua())


def codificar(url, signos):
    """La URL con esos signos como %XX, para que no corten una liga ni una celda de tabla."""
    return re.sub(f"[{re.escape(signos)}]", lambda m: f"%{ord(m.group()):02X}", url)


def md(valor):
    """Un valor de los registros como texto de la instantánea: en una línea, con los signos de Markdown escapados
    y cada URL como autoliga, para que se lea literal y pase markdownlint. La puntuación que sigue a una URL
    queda fuera de la liga."""
    texto = []
    for i, parte in enumerate(re.split(r"(https?://\S+?)(?=[.,;:!?)»]*(?:\s|$))", " ".join(valor.split()))):
        if i % 2:
            texto.append(f"<{codificar(parte, '<>|')}>")
        else:
            texto.append(re.sub(r"([\\`*_\[\]<>|#~])", r"\\\1", parte))
    return "".join(texto)


def liga(texto, url):
    """[texto](url), o solo el texto si no hay URL."""
    if not url.startswith(("http://", "https://")):
        return md(texto)
    return f"[{md(texto)}]({codificar(url, '()<>| ')})"


def campos(fila, sin=()):
    """Las columnas con valor de una fila, una por renglón de lista."""
    return [f"- **{c}:** {md(v)}" for c, v in fila.items() if v and c not in sin]


def vista_informes(esquema, filas, encabezado, hoy, umbral):
    """informes.md: las últimas búsquedas, la más reciente primero, con su fila de busquedas y su tabla resumen."""
    busquedas = sorted(filas["busquedas"], key=lambda b: (b["fecha_hora"], b["busqueda_id"]), reverse=True)
    ultimas = busquedas[:ULTIMAS_BUSQUEDAS]
    lineas = ["# Instantánea: informes", "", encabezado, "",
              f"Búsquedas: las últimas {len(ultimas)} de {len(busquedas)}, la más reciente primero, cada una con su "
              "fila de `busquedas` y su tabla resumen (08/EVAL-INFORME)."]
    for b in ultimas:
        lineas += ["", f"## {b['busqueda_id']} · {md(b['fecha_hora'])}", ""]
        lineas += campos({c: b[c] for c in ("solicitud_alcance", "cobertura_limitaciones", "no_revisado_pendientes",
                                             "comparacion_anterior")})
        tabla = tabla_resumen(esquema, filas, b["busqueda_id"], hoy, umbral)
        if not tabla:
            lineas += ["", "Sin vacantes evaluadas en `informes`."]
            continue
        lineas += ["", "| Vacante | Encaje | Antigüedad | Alertas |", "| --- | --- | --- | --- |"]
        lineas += [f"| {liga(f['vacante'], f['url_oficial'])} | {md(f['encaje'])} | {md(f['antiguedad'])} "
                   f"| {md(f['alertas'])} |" for f in tabla]
    return "\n".join(lineas) + "\n"


def vista_vacantes(filas, encabezado, hoy, umbral):
    """vacantes.md: una sección autocontenida por vacante evaluada cuya última observación no es Cerrada."""
    observaciones = primeras(filas["observaciones"], "observacion_id")
    ultima_evaluacion = {e["vacante_id"]: e for e in filas["evaluaciones"]}
    requisitos = {}
    for r in filas["habilidades_vacante"]:
        requisitos.setdefault(r["observacion_id"], []).append(r)
    secciones = []
    for v in filas["vacantes"]:
        evaluacion = ultima_evaluacion.get(v["vacante_id"])
        observacion = observaciones.get(v["ultima_observacion_id"])
        if evaluacion is None or v["duplicado_de"] or (observacion and observacion["estado_vigencia"] == "Cerrada"):
            continue
        job_id = "sin Job ID" if v["job_id"].casefold() in ("", "no publicado") else v["job_id"]
        seccion = [f"## {v['vacante_id']} · {md(job_id)} · {v['empresa_id']} · «{md(v['titulo'])}»", ""]
        seccion += campos(v, sin=("vacante_id",)) + [f"- **antigüedad:** {md(antiguedad(v, hoy, umbral))}"]
        if observacion:
            seccion += ["", f"### Última observación: {observacion['observacion_id']}", ""]
            seccion += campos(observacion, sin=("observacion_id", "vacante_id"))
        seccion += ["", f"### Última evaluación: {evaluacion['evaluacion_id']}", ""]
        seccion += campos(evaluacion, sin=("evaluacion_id", "vacante_id"))
        # Una fila por frase literal: «Python or R» junta sus dos términos y conserva la alternativa.
        grupos = {}
        for r in requisitos.get(evaluacion["observacion_id"], []):
            normalizados, tipos = grupos.setdefault(r["habilidad_literal"], ([], []))
            for lista, valor in ((normalizados, r["habilidad_normalizada"]), (tipos, r["tipo_requisito"])):
                if valor and valor not in lista:
                    lista.append(valor)
        seccion += ["", f"### Requisitos de {evaluacion['observacion_id']}", ""]
        if grupos:
            seccion += ["| Frase literal | Normalizados | Tipo |", "| --- | --- | --- |"]
            seccion += [f"| {md(literal)} | {md('; '.join(normalizados)) or '—'} | {md('; '.join(tipos))} |"
                        for literal, (normalizados, tipos) in grupos.items()]
        else:
            seccion.append("Sin requisitos registrados.")
        secciones.append("\n".join(seccion))
    lineas = ["# Instantánea: vacantes evaluadas", "", encabezado, "",
              f"Vacantes: {len(secciones)}, con evaluación y cuya última observación no es `Cerrada`. Cada una trae sus "
              "campos de `vacantes`, su última observación, su última evaluación y los requisitos de la observación "
              "evaluada, agrupados por frase literal. No están las vacantes sin evaluación, el historial de "
              "observaciones ni `documentos`."]
    return "\n\n".join(["\n".join(lineas)] + secciones) + "\n"


def instantanea(esquema, filas):
    """Las dos vistas de la instantánea (11/REG-INSTANTANEA), {archivo: texto}, desde todas las filas. Se arman
    antes de guardar el archivo de registros: si falta lo que piden, como la zona horaria de 04, no se escribe nada."""
    ahora = dt.datetime.now(leer_zona_horaria())
    umbral = umbral_de_antigua()
    encabezado = (f"**Exportada:** {ahora:%Y-%m-%d %H:%M} ({ahora.tzinfo.key}), desde "
                  f"`{esquema['archivo']['nombre']}.xlsx`. La antigüedad está calculada a esa fecha; las demás fechas "
                  "son las de los registros. Se regenera completa con cada escritura y no se edita a mano "
                  "(11/REG-INSTANTANEA).")
    return {"informes.md": vista_informes(esquema, filas, encabezado, ahora.date(), umbral),
            "vacantes.md": vista_vacantes(filas, encabezado, ahora.date(), umbral)}


def guardar_instantanea(vistas):
    """Escribe cada vista completa en instantanea/ y avisa en stderr, sin fallar, si juntas pasan del límite."""
    carpeta = os.path.join(RAIZ, CARPETA_INSTANTANEA)
    os.makedirs(carpeta, exist_ok=True)
    tamanos = {}
    for nombre, texto in vistas.items():
        ruta = os.path.join(carpeta, nombre)
        temporal = ruta + ".tmp"
        try:
            with open(temporal, "w", encoding="utf-8", newline="\n") as f:
                f.write(texto)
            os.replace(temporal, ruta)
        finally:
            if os.path.exists(temporal):
                os.remove(temporal)
        tamanos[f"{CARPETA_INSTANTANEA}/{nombre}"] = os.path.getsize(ruta)
    total = sum(tamanos.values())
    if total > AVISO_INSTANTANEA_KB * 1024:
        print(f"Aviso: la instantánea pesa {total / 1024:.0f} KB, más de {AVISO_INSTANTANEA_KB} KB; el canal Web puede no leerla "
              "completa (11/REG-INSTANTANEA).", file=sys.stderr)
    return {"archivos": tamanos}


def leer(esquema, nombre, ids, columna):
    p = pestana_del_esquema(esquema, nombre)
    columna = columna or clave(p)["nombre"]
    if columna not in encabezados(p):
        error(f"{columna!r} no es una columna guardada de {nombre}.")
    filas = abrir(esquema)[1][nombre]
    return [f for f in filas if f[columna] in ids] if ids else filas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ordenes = ap.add_subparsers(dest="orden", required=True)
    ordenes.add_parser("crear", help="crea el archivo desde 11/REG-ESQUEMA")
    o = ordenes.add_parser("agregar", help="agrega filas, comprobadas contra 11/REG-ESQUEMA")
    o.add_argument("filas", nargs="?", default="-", metavar="ARCHIVO.json",
                   help="{pestaña: [fila, ...]}; por defecto, de stdin")
    o = ordenes.add_parser("actualizar", help="cambia columnas de filas registradas, por su ID")
    o.add_argument("filas", nargs="?", default="-", metavar="ARCHIVO.json",
                   help="{pestaña: [{columna_id: ID, columna: valor nuevo, ...}]}; por defecto, de stdin")
    o = ordenes.add_parser("informe", help="la tabla resumen de una búsqueda, con las columnas calculadas")
    o.add_argument("busqueda_id", metavar="BUS-ID")
    o = ordenes.add_parser("leer", help="filas de una pestaña")
    o.add_argument("pestana", metavar="PESTAÑA")
    o.add_argument("--id", nargs="+", default=[], help="solo las filas con alguno de estos IDs")
    o.add_argument("--columna", help="columna donde se buscan los IDs (por defecto, la primera)")
    ordenes.add_parser("instantanea", help="regenera la instantánea completa que lee el canal Web")
    a = ap.parse_args()
    esquema = leer_esquema()
    if a.orden == "crear":
        res = crear(esquema)
    elif a.orden == "agregar":
        res = agregar(esquema, leer_entrada(a.filas))
    elif a.orden == "actualizar":
        res = actualizar(esquema, leer_entrada(a.filas))
    elif a.orden == "informe":
        res = informe(esquema, a.busqueda_id)
    elif a.orden == "instantanea":
        res = guardar_instantanea(instantanea(esquema, abrir(esquema)[1]))
    else:
        res = leer(esquema, a.pestana, a.id, a.columna)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
