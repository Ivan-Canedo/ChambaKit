#!/usr/bin/env python3
"""ChambaKit: listado y detalle de vacantes por empresa (canal Code, 07/BUS-ACCESO-CODE).

Uso:
    python3 -I herramientas/buscar.py [EMP-ID ...] [--salida archivo.json] [--sin-remotas]

Las empresas se nombran por su ID de 06; por defecto, todas las del catálogo (CAT-EMPRESAS). La región,
el alcance del remoto y la zona horaria salen del bloque de 04/PREF-UBICACION; la plataforma, el portal
y la consulta de cada empresa, del bloque de «### Configuración» de su ficha en 06.

Si el bloque de 04 falta o no cumple sus reglas, el catálogo está vacío, un EMP-ID no está en él o
--sin-remotas dejaría vacía la búsqueda de un titular que solo acepta remoto, termina con código 2 sin
buscar nada. Una empresa sin configuración usable, con una plataforma sin adaptador o cuyo portal falla
sale como [FALLO] y las demás siguen; entonces termina con código 1.

Cada adaptador lista las vacantes de los países de la región, o las de la consulta de la ficha, y las
remotas con el filtro de su plataforma según el alcance del remoto; lee el detalle de cada una con
comprobación de ID y solo usa rutas que permite el robots.txt del sitio. El JSON va a --salida o a
stdout; el resumen y las líneas «revisar», a stderr. El script no evalúa ni escribe en los registros:
entrega los datos para los pasos 4-9 de 07/BUS-PASOS. Solo biblioteca estándar.
"""
import argparse
import datetime as dt
import html
import http.client
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

VERSION = "1.0"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULO_04 = os.path.join(RAIZ, "04_PREFERENCIAS_LABORALES.md")
MODULO_06 = os.path.join(RAIZ, "06_EMPRESAS_OBJETIVO.md")


class Fallo(Exception):
    """Lo que impide buscar en una empresa: su configuración o su portal. Sale como [FALLO] y las demás
    siguen. codigo: el estado HTTP, si lo hubo."""

    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.codigo = codigo


class HostBloqueado(Fallo):
    """El proxy de Code en la nube no dejó salir la petición: el host no está en la lista de dominios del entorno
    (07/BUS-ACCESO-CODE). No se reintenta ni lo oculta el mensaje del robots.txt."""

    def __init__(self, host):
        super().__init__(f"el host no está en la lista de dominios del entorno de la nube; agrégalo en claude.ai/code "
                         f"(entorno → red → Custom) y vuelve a buscar: {host}")
        self.host = host


def error(mensaje):
    """Configuración que falta o no sirve: termina con código 2 sin buscar nada."""
    print(mensaje, file=sys.stderr)
    sys.exit(2)


def leer(ruta, para):
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


def lista_de_textos(x):
    return isinstance(x, list) and all(isinstance(t, str) and t.strip() for t in x)


def leer_preferencias(ruta):
    """Bloque de 04/PREF-UBICACION, comprobado con sus «Reglas del bloque»."""
    bloque = bloque_json(seccion(leer(ruta, "la región, el remoto y la zona horaria"), "PREF-UBICACION"))
    if bloque is None:
        error(f"{ruta}: falta el bloque de configuración (```json) en la sección PREF-UBICACION.")
    try:
        p = json.loads(bloque)
    except ValueError as e:
        error(f"{ruta}: el bloque de PREF-UBICACION no es JSON válido ({e}).")

    def mal(mensaje):
        error(f"{ruta}, PREF-UBICACION: {mensaje}")

    if not isinstance(p, dict) or not isinstance(p.get("remoto"), dict):
        mal("el bloque debe ser un objeto con paises, localidades, remoto, zona_horaria y moneda.")
    remoto = p["remoto"]
    vacios = [c for c, v in (("remoto.alcance", remoto.get("alcance")), ("zona_horaria", p.get("zona_horaria")),
                              ("moneda", p.get("moneda"))) if v is None]
    if vacios:
        mal(f"el bloque está sin llenar ({', '.join(vacios)} en null); llénalo con `/configurar`, paso 4 "
            "(Preferencias).")
    paises = p.get("paises")
    if not isinstance(paises, dict) or not all(re.fullmatch(r"[A-Z]{2}", c) and lista_de_textos(n) and n
                                               for c, n in paises.items()):
        mal("paises debe ser un objeto: código ISO de dos letras mayúsculas → lista de nombres.")
    localidades = p.get("localidades")
    if not isinstance(localidades, list) or not all(
            isinstance(g, dict) and isinstance(g.get("pais"), str) and lista_de_textos(g.get("divisiones"))
            and lista_de_textos(g.get("nombres")) and isinstance(g.get("zona", None), (str, type(None)))
            for g in localidades):
        mal("localidades debe ser una lista de grupos con pais, divisiones, zona y nombres.")
    sin_pais = [g["pais"] for g in localidades if g["pais"] not in paises]
    if remoto["alcance"] not in ("ninguno", "paises", "cualquiera"):
        mal(f"remoto.alcance debe ser \"ninguno\", \"paises\" o \"cualquiera\"; dice {remoto['alcance']!r}.")
    if not lista_de_textos(remoto.get("paises")) or bool(remoto["paises"]) != (remoto["alcance"] == "paises"):
        mal("remoto.paises lleva los países del remoto solo con el alcance \"paises\"; con los otros, va vacía.")
    sin_pais += [c for c in remoto["paises"] if c not in paises]
    if sin_pais:
        mal(f"{', '.join(sin_pais)} no está en paises.")
    if not localidades and remoto["alcance"] == "ninguno":
        mal("localidades está vacía y el remoto es \"ninguno\": no habría nada que buscar.")
    try:
        p["tz"] = ZoneInfo(p["zona_horaria"])
    except (ValueError, KeyError, TypeError):
        mal(f"zona_horaria no es una zona IANA conocida: {p['zona_horaria']!r}. Si el nombre es correcto, al "
            "sistema le falta la base de zonas horarias (en Windows: `py -3 -m pip install tzdata`).")
    if not (isinstance(p["moneda"], str) and re.fullmatch(r"[A-Z]{3}", p["moneda"])):
        mal(f"moneda debe ser un código ISO 4217 de tres letras mayúsculas; dice {p['moneda']!r}.")
    return p


def leer_catalogo(ruta):
    """{EMP-ID: texto de su ficha, o None si falta} en el orden de CAT-EMPRESAS."""
    md = leer(ruta, "las empresas")
    catalogo = seccion(md, "CAT-EMPRESAS")
    if catalogo is None:
        error(f"{ruta}: falta la sección CAT-EMPRESAS, el catálogo de empresas.")
    ids = re.findall(r"^\|\s*(EMP-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*\|", catalogo, re.M)
    if not ids:
        error(f"{ruta}: el catálogo (CAT-EMPRESAS) no tiene empresas; agrégalas con `/configurar`, paso 7 "
              "(Empresas).")
    return {eid: seccion(md, eid) for eid in dict.fromkeys(ids)}


def leer_ficha(eid, ficha):
    """Bloque de «### Configuración» de la ficha (06/FICHA-PLANTILLA). Sin él, la empresa sale como [FALLO]."""
    if ficha is None:
        raise Fallo(f"falta su ficha en 06, la sección «## {eid} — <nombre>»")
    bloque = bloque_json(seccion(ficha, "Configuración", "###"))
    if bloque is None:
        raise Fallo("su ficha no tiene el bloque ```json de «### Configuración» (06/FICHA-PLANTILLA)")
    try:
        conf = json.loads(bloque)
    except ValueError as e:
        raise Fallo(f"el bloque de «### Configuración» de su ficha no es JSON válido ({e})") from e
    if not isinstance(conf, dict) or not isinstance(conf.get("plataforma"), str):
        raise Fallo("el bloque de «### Configuración» debe ser un objeto con plataforma, portal y consulta")
    if not (isinstance(conf.get("portal"), str) and re.match(r"https?://", conf["portal"])):
        raise Fallo(f"el portal de su ficha debe ser una URL http(s); dice {conf.get('portal')!r}")
    if conf.get("consulta") is not None and not isinstance(conf["consulta"], dict):
        raise Fallo("la consulta de su ficha debe ser null o un objeto (06/CAT-PLATAFORMAS)")
    return conf


# --- Acceso a los portales ---------------------------------------------------

def pedir(url, cuerpo=None, intentos=3, como_json=True, extra=None):
    """GET (o POST con cuerpo JSON) que devuelve JSON, o texto si como_json=False.
    extra: cabeceras adicionales que pida un adaptador. Reintenta errores transitorios, también HTTP 429."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    # Algunas plataformas responden JSON en lugar de la página solo si se pide application/json
    cabeceras = {"User-Agent": UA, "Accept": "application/json" if como_json else "text/html,application/xhtml+xml"}
    if datos is not None:
        cabeceras["Content-Type"] = "application/json"
    cabeceras.update(extra or {})
    for i in range(intentos):
        espera = 2 * (i + 1)
        try:
            req = urllib.request.Request(url, data=datos, headers=cabeceras,
                                         method="POST" if datos is not None else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r) if como_json else r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if (e.code < 500 and e.code != 429) or i == intentos - 1:
                raise Fallo(f"HTTP {e.code} en {url}", e.code) from e
            if e.code == 429:
                # El sitio pide bajar el ritmo: se espera lo que diga Retry-After, hasta un minuto
                pedida = (e.headers.get("Retry-After") if e.headers else None) or ""
                espera = min(int(pedida), 60) if pedida.isdigit() else 5 * espera
        # OSError: también el timeout de lectura, que en Python 3.9 todavía no es TimeoutError
        except (OSError, http.client.HTTPException, json.JSONDecodeError) as e:
            # El proxy de la nube responde 403 al CONNECT de un host fuera de la lista; urllib lo da como URLError
            if isinstance(e, urllib.error.URLError) and "Tunnel connection failed: 403" in str(e.reason):
                raise HostBloqueado(urllib.parse.urlsplit(url).hostname) from e
            if i == intentos - 1:
                raise Fallo(f"{type(e).__name__}: {e} en {url}") from e
        time.sleep(espera)


def robots_permite(reglas, url):
    """Si el robots.txt (su texto) permite la URL a este script, según RFC 9309: se aplican las reglas del grupo de su
    agente, o las de «*», y gana la que coincide con más caracteres de la ruta; en empate, Allow. Se evalúa aquí y
    no con urllib.robotparser porque, hasta Python 3.12, ese aplica la primera regla que coincide, y así un
    «Disallow: /» antes de un «Allow: /api/» lo prohíbe todo."""
    grupos, nuevo = [], True
    for linea in reglas.splitlines():
        clave, _, valor = linea.split("#", 1)[0].partition(":")
        clave, valor = clave.strip().lower(), valor.strip()
        if clave == "user-agent":
            if nuevo:  # varias líneas User-agent seguidas comparten grupo
                grupos.append((set(), []))
                nuevo = False
            grupos[-1][0].add(valor.lower())
        elif clave:
            nuevo = True
            if clave in ("allow", "disallow") and grupos and valor:  # «Disallow:» vacío no prohíbe nada
                grupos[-1][1].append((valor, clave == "allow"))
    agente = UA.split("/")[0].lower()
    aplican = [g for g in grupos if agente in g[0]] or [g for g in grupos if "*" in g[0]]
    u = urllib.parse.urlsplit(url)
    ruta = (u.path or "/") + (f"?{u.query}" if u.query else "")
    largo, permite = -1, True
    for _, reglas_grupo in aplican:
        for patron, allow in reglas_grupo:
            # «*» es cualquier texto y un «$» final ancla el fin de la ruta
            regex = ".*".join(map(re.escape, patron.rstrip("$").split("*"))) + ("$" if patron.endswith("$") else "")
            if re.match(regex, ruta) and (len(patron) > largo or (len(patron) == largo and allow)):
                largo, permite = len(patron), allow
    return permite


def comprobar_robots(sitio, urls):
    """Falla si el robots.txt del sitio prohíbe alguna de las URL que usa el adaptador (07/BUS-CANALES). Las URL
    llevan una consulta (?…) si el adaptador la usa, porque hay sitios que prohíben las rutas con consulta."""
    url = f"{sitio}/robots.txt"
    try:
        reglas = pedir(url, como_json=False)
    except HostBloqueado:
        raise
    except Fallo as e:
        if e.codigo in (404, 410):
            return  # sin robots.txt, el sitio no prohíbe nada
        raise Fallo(f"no se pudo leer {url} ({e}); sin él no se sabe qué rutas permite") from e
    prohibidas = [u for u in urls if not robots_permite(reglas, u)]
    if prohibidas:
        raise Fallo(f"{url} prohíbe {', '.join(prohibidas)}: no se usa; busca otra ruta del sitio oficial "
                    "(07/BUS-CANALES)")


def campo(d, *ruta):
    """Lee un campo obligatorio; si la API cambió de forma, falla con un mensaje claro."""
    for k in ruta:
        if not isinstance(d, dict) or k not in d:
            raise Fallo(f"Falta el campo {'.'.join(ruta)}: la API pudo haber cambiado")
        d = d[k]
    return d


def texto(h):
    """HTML a texto plano conservando párrafos y viñetas."""
    if not h:
        return ""
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h\d>|</ul>|</ol>", "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", "\n- ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h).replace("\xa0", " ")
    lineas = [" ".join(l.split()) for l in h.splitlines()]
    return "\n".join(l for l in lineas if l)


def atributos(etiqueta):
    """{nombre: valor} de los atributos de una etiqueta HTML."""
    return {k: html.unescape(v) for k, v in re.findall(r'([\w:-]+)="([^"]*)"', etiqueta)}


# --- Región de 04 -------------------------------------------------------------

# Palabras que no nombran un lugar. Una ubicación hecha solo de ellas y de los países de la región
# es demasiado general, como «Remote» o «Multiple Locations» (11, «Indeterminada»).
GENERALES = frozenset("""remote remoto remota teletrabajo hybrid hibrido hibrida home office anywhere virtual
multiple locations location ubicaciones ubicacion varias various in en de from desde and y or o""".split())


def normalizar(s):
    """Minúsculas, sin acentos y con un solo espacio, para comparar lugares (04, «Cómo se lee un grupo»)."""
    s = unicodedata.normalize("NFKD", s.casefold())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def palabra(nombre):
    """Patrón del nombre normalizado como palabra o frase completa."""
    return rf"(?<![^\W_]){re.escape(normalizar(nombre))}(?![^\W_])"


def nombra(s, nombres):
    """La ubicación normalizada s contiene alguno de los nombres como palabra o frase completa."""
    return any(re.search(palabra(n), s) for n in nombres if n.strip())


def sin_generales(texto):
    return " ".join(p for p in normalizar(texto).split() if p not in GENERALES)


def nombra_pais(literal, nombres):
    """La ubicación nombra uno de esos países como una de sus partes, separadas por comas, guiones con espacios
    o paréntesis, sin contar las palabras generales: «Ciudad, País», «País - Ciudad», «Remote - País». Así
    otro lugar que contiene el nombre del país («Nuevo País A») no lo nombra."""
    buscados = {sin_generales(n) for n in nombres}
    return any(sin_generales(parte) in buscados for parte in re.split(r"\s+[-–]\s+|[,|/()]", literal))


def paises_nombrados(literal, pref):
    return {c for c, nombres in pref["paises"].items() if nombra_pais(literal, nombres)}


def paises_region(pref):
    """Los países de localidades, en su orden."""
    return list(dict.fromkeys(g["pais"] for g in pref["localidades"]))


def demasiado_general(s, pref):
    """La ubicación normalizada s no nombra ningún lugar fuera de los países de la región: puede estar dentro."""
    for c in paises_region(pref):
        for n in sorted(pref["paises"][c], key=len, reverse=True):
            s = re.sub(palabra(n), " ", s)
    return all(p in GENERALES for p in re.findall(r"[^\W\d_]+", s))


def clasificar_ubicacion(literal, pref):
    """«dentro», «revisar» o «fuera»: una ubicación literal contra los grupos de 04/PREF-UBICACION."""
    s = normalizar(literal)
    revisar = demasiado_general(s, pref)
    # Una ubicación que nombra otro país de 04, y no el del grupo, no es de ese grupo: hay ciudades y
    # divisiones homónimas entre países
    nombrados = paises_nombrados(literal, pref)
    for g in pref["localidades"]:
        if nombrados and g["pais"] not in nombrados:
            continue
        if g["nombres"]:
            if nombra(s, g["nombres"]):
                return "dentro"
            # Nombra su división sin una localidad aceptada: puede estar dentro
            revisar = revisar or nombra(s, g["divisiones"])
        elif g["divisiones"]:
            if nombra(s, g["divisiones"]):
                return "dentro"
        elif g["pais"] in nombrados:
            return "dentro"
    return "revisar" if revisar else "fuera"


def region(literales, pref):
    """region_relacionada de 11 y las ubicaciones que pueden estar dentro sin nombrar una localidad aceptada."""
    if not literales:
        return "Indeterminada", []
    clases = [clasificar_ubicacion(l, pref) for l in literales]
    revisar = [l for l, c in zip(literales, clases) if c == "revisar"]
    if all(c == "dentro" for c in clases):
        return "Dentro", revisar
    if "dentro" in clases:
        return "Incluye", revisar
    if revisar:
        return "Indeterminada", revisar
    return "Fuera", revisar


def es_remota(modalidad):
    return bool(modalidad) and re.search(r"(?<![^\W_])(?:remot[eoa]s?|teletrabajo)(?![^\W_])",
                                         normalizar(modalidad)) is not None


def en_alcance_remoto(literal, pref, paises=None):
    """Una remota está en el alcance del remoto de 04, o puede estarlo porque no nombra ningún país de 04.
    paises: los códigos ISO de sus ubicaciones, si la plataforma los publica; deciden mejor que los nombres,
    porque también reconocen los países que 04 no nombra."""
    alcance = pref["remoto"]["alcance"]
    if alcance != "paises":
        return alcance == "cualquiera"
    nombrados = set(paises or ()) or paises_nombrados(literal or "", pref)
    return not nombrados or bool(nombrados & set(pref["remoto"]["paises"]))


def sin_remotas(pref, remotas):
    """Por qué no se listan remotas en esta búsqueda, o None si sí se listan."""
    if pref["remoto"]["alcance"] == "ninguno":
        return "No aplica: 04 no acepta remoto"
    if not remotas:
        return "Omitida (--sin-remotas)"
    return None


def aviso_sin_filtro_de_remoto(r):
    """La línea «revisar» de un portal sin filtro de remoto: sus remotas solo salen del listado de la región."""
    r["revisar"].append("sin filtro de remoto en el portal: solo se revisaron las remotas del listado de la región; "
                        "anotarlo en no_revisado_pendientes")


# --- Resultado de cada empresa -------------------------------------------------

def vigencia(indicador, valor, abiertos):
    """Estado sugerido según 07/BUS-VIGENCIA. Solo los valores positivos observados (abiertos) se mapean.
    El motivo lleva el prefijo «Detalle oficial: », como se registra."""
    motivo = f"Detalle oficial: {indicador}: {json.dumps(valor, ensure_ascii=False)}"
    if valor in abiertos:
        return "Confirmada abierta", motivo
    return "Revisar", motivo + " (valor no observado antes: decidir con 07/BUS-VIGENCIA)"


def fecha(instante, pref):
    """fecha_publicacion de un instante con zona (07/BUS-FECHAS): a las 00:00 UTC es una fecha sin hora y queda como
    fecha UTC; con hora real, pasa a la zona horaria de 04."""
    utc = instante.astimezone(dt.timezone.utc)
    return (utc if utc.time() == dt.time() else instante.astimezone(pref["tz"])).date().isoformat()


def instante_iso(s):
    """Una marca de tiempo ISO 8601 de una API («…Z» incluida) como datetime con zona (UTC si no trae), o None."""
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def fecha_iso(s, pref):
    """fecha() de una marca de tiempo ISO 8601, o None si no lo es."""
    t = instante_iso(s)
    return fecha(t, pref) if t else None


def vacante(pref, empresa_id, job_id, titulo, url_oficial, ubicaciones, modalidad, fecha_pub,
            estado, motivo, url_fuente, departamento, descripcion):
    """Los campos de `vacantes` y `observaciones` (11), con la región de 04."""
    ubicaciones = [u for u in ubicaciones if u]
    reg, revisar = region(ubicaciones, pref)
    return {
        "empresa_id": empresa_id,
        "job_id": job_id,
        "titulo": titulo,
        "url_oficial": url_oficial,
        "ubicacion_literal": " | ".join(ubicaciones) if ubicaciones else None,
        "modalidad_literal": modalidad,
        "region_relacionada": reg,
        "ubicaciones_por_revisar": revisar,
        "fecha_publicacion": fecha_pub,
        "estado_vigencia": estado,
        "motivo": motivo,
        "url_fuente": url_fuente,
        "departamento": departamento,
        "descripcion": descripcion,
    }


def sin_detalle(base, fallo):
    """Vacante del listado cuyo detalle falló: 07 admite el listado como evidencia."""
    base["estado_vigencia"] = "Confirmada abierta"
    base["motivo"] = f"En listado oficial; detalle no consultado ({fallo})"
    base["descripcion"] = None
    return base


def resultado(eid, acceso):
    """Lo que entrega cada adaptador; lo llenan listado() y repartir()."""
    return {"empresa_id": eid, "acceso": acceso, "consultas": [], "total_reportado": 0, "unicos": 0,
            "completa": True, "vacantes": [], "remotas_fuera_de_region": [], "fuera_de_region": [],
            "remotas_revision": None, "revisar": []}


def listado(r, consulta, total, ids, vistas=frozenset()):
    """Suma un listado al resultado, con sus IDs únicos contra el total que reporta (07/BUS-COBERTURA).
    total = None: la fuente no lo publica. Las vacantes que ya trajo un listado anterior (vistas) se
    descuentan de los únicos y del total, para que el resultado cuente vacantes distintas."""
    r["consultas"].append(f"{consulta} ({len(ids)} únicos de {total})" if total is not None
                          else f"{consulta} ({len(ids)} únicos, sin total publicado)")
    repetidas = len(ids & vistas)
    r["unicos"] += len(ids) - repetidas
    if total is None or r["total_reportado"] is None:
        r["total_reportado"] = r["completa"] = None
    else:
        r["total_reportado"] += total - repetidas
        r["completa"] = r["completa"] and len(ids) == total


def repartir(r, v, pref, de_remotas=False, paises=None):
    """Las de la región van a vacantes; las remotas de fuera, si las trajo un filtro de remoto ya acotado al alcance
    de 04 (de_remotas) o están en ese alcance, a remotas_fuera_de_region; las demás solo dejan su ubicación en
    fuera_de_region. paises: los códigos ISO de sus ubicaciones, si la plataforma los publica (en_alcance_remoto).
    Devuelve si la vacante se entrega, para leer el detalle solo de esas."""
    if v["region_relacionada"] != "Fuera":
        r["vacantes"].append(v)
    elif de_remotas or (es_remota(v["modalidad_literal"]) and en_alcance_remoto(v["ubicacion_literal"], pref, paises)):
        r["remotas_fuera_de_region"].append(v)
    else:
        anotar_fuera(r, v["ubicacion_literal"])
        return False
    return True


def por_desplazamiento(pagina, total_de, filas_de, id_de, primera=None):
    """(filas sin repetir, total) de un listado que pagina por desplazamiento: pagina(inicio) pide la página que
    empieza en inicio, y primera es la de inicio 0, si ya se pidió. Termina al llegar al total o con una página sin
    filas nuevas."""
    d = primera or pagina(0)
    filas, ids, inicio, total = [], set(), 0, total_de(d)
    while True:
        lista = filas_de(d)
        nuevas = [f for f in lista if id_de(f) not in ids]
        if not nuevas:
            return filas, total
        ids.update(id_de(f) for f in nuevas)
        filas += nuevas
        inicio += len(lista)
        if inicio >= total:
            return filas, total
        d = pagina(inicio)


def anotar_fuera(r, ubicacion):
    """Anota una vez en fuera_de_region la ubicación de una vacante que no se entrega."""
    if (ubicacion or "") not in r["fuera_de_region"]:
        r["fuera_de_region"].append(ubicacion or "")


# --- Consulta de la ficha ---------------------------------------------------------

def es_texto(x):
    return isinstance(x, str)


def listas_por_nombre(x):
    """Un objeto: nombre → lista no vacía de textos, como las facetas o los filtros de una consulta."""
    return isinstance(x, dict) and all(lista_de_textos(v) and v for v in x.values())


def leer_consulta(conf, campos, forma):
    """La consulta de la ficha, comprobada antes de pedir nada, o None si no trae. campos: {campo: comprobación}
    de su plataforma, y forma, cómo se escribe (06/CAT-PLATAFORMAS). Debe traer al menos un campo no vacío, para
    no listar todo el portal."""
    consulta = conf.get("consulta")
    if consulta is None:
        return None
    if (set(consulta) - set(campos) or not all(campos[k](v) for k, v in consulta.items())
            or not any(v.strip() if isinstance(v, str) else v for v in consulta.values())):
        raise Fallo(f"la consulta de su ficha debe ser {forma}, con al menos uno de sus campos (06/CAT-PLATAFORMAS)")
    return consulta


def resolver(pedidas, ofrecidos, r, parametro):
    """{parámetro: [valores]} con los de la consulta que el portal ofrece hoy, buscados por su nombre sin mayúsculas
    ni acentos (ofrecidos: {parámetro: {nombre normalizado: valor}}); None si a algún parámetro no le queda ninguno,
    porque el listado saldría vacío. parametro: cómo llama la plataforma a los suyos («la faceta»), para el aviso."""
    aplicados = {}
    for p, nombres in pedidas.items():
        hay = ofrecidos.get(p, {})
        for n in nombres:
            if normalizar(n) not in hay:
                r["revisar"].append(f"{parametro} {p} no ofrece «{n}»: no hay vacantes con ese valor hoy, o el nombre "
                                    "cambió (consulta de la ficha)")
        aplicados[p] = [hay[normalizar(n)] for n in nombres if normalizar(n) in hay]
    return None if any(not v for v in aplicados.values()) else aplicados


# --- Workday --------------------------------------------------------------------
# Portal: https://<empresa>.wd<N>.myworkdayjobs.com/<sitio>. API: POST para listar, GET para el detalle.

WD_POR_PAGINA = 20  # máximo que acepta la API


def wd_api(portal):
    """(sitio, base de la API) desde la URL del portal de la ficha."""
    u = urllib.parse.urlsplit(portal)
    host = u.hostname or ""
    partes = [p for p in u.path.split("/") if p]
    if partes and re.fullmatch(r"[a-z]{2}(?:-[A-Za-z]{2})?", partes[0]):
        partes = partes[1:]  # idioma de la página, como /en-US/
    if u.scheme != "https" or not host.endswith(".myworkdayjobs.com") or not partes:
        raise Fallo(f"el portal {portal} no es de Workday: debe ser https://<empresa>.wd<N>.myworkdayjobs.com/<sitio> "
                    "(06/CAT-PLATAFORMAS)")
    return f"https://{host}", f"https://{host}/wday/cxs/{host.split('.')[0]}/{partes[0]}"


def wd_listar(base, facetas, busqueda=""):
    filas, inicio, total = [], 0, None
    while total is None or inicio < total:
        d = pedir(f"{base}/jobs", {"appliedFacets": facetas, "limit": WD_POR_PAGINA, "offset": inicio,
                                   "searchText": busqueda})
        if total is None:
            total = campo(d, "total")  # las páginas siguientes pueden traer 0
        pagina = campo(d, "jobPostings")
        if not pagina:
            break
        filas += pagina
        inicio += WD_POR_PAGINA
    return filas, total


def wd_facetas(base):
    """(parámetro, nombre, id) de cada valor de faceta, también de las anidadas (locationMainGroup → locations).
    Un valor solo aparece si alguna vacante lo tiene."""
    d = pedir(f"{base}/jobs", {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""})
    valores = []

    def recorrer(facetas):
        for f in facetas:
            for v in f.get("values", []):
                if "facetParameter" in v:
                    recorrer([v])
                else:
                    valores.append((f.get("facetParameter"), v.get("descriptor") or "", v.get("id")))

    recorrer(campo(d, "facets"))
    return valores


def wd_elegir(facetas, es_parametro, es_valor):
    """(parámetro, [(nombre, id)]) del parámetro que más valores aceptados ofrece, o None. Se aplica uno solo
    porque Workday combina parámetros distintos con «y»."""
    por_parametro = {}
    for p, nombre, i in facetas:
        if p and es_parametro(p) and es_valor(nombre):
            por_parametro.setdefault(p, []).append((nombre, i))
    if not por_parametro:
        return None
    p = max(por_parametro, key=lambda k: len(por_parametro[k]))
    return p, por_parametro[p]


def wd_es_pais(p):
    return "country" in p.lower()


def wd_es_ubicacion(p):
    return "location" in p.lower() and not wd_es_pais(p)


def wd_paises(facetas, pref, codigos, con_localidades):
    """(faceta, códigos sin valor): la faceta que acota el listado a esos países y los que no ofrece. Es la
    de país, si el portal la tiene; si no, las ubicaciones que nombran uno de ellos o, con con_localidades,
    una localidad aceptada de 04. Un valor solo existe si alguna vacante lo tiene."""
    def de_pais(c):
        iguales = {normalizar(n) for n in pref["paises"][c]}
        return lambda d: normalizar(d) in iguales

    def de_ubicacion(c):
        del_pais = {**pref, "localidades": [g for g in pref["localidades"] if g["pais"] == c]}
        return lambda d: nombra_pais(d, pref["paises"][c]) or (
            con_localidades and clasificar_ubicacion(d, del_pais) == "dentro")

    if any(wd_es_pais(p) for p, _, _ in facetas if p):
        es_parametro, prueba = wd_es_pais, de_pais
    else:
        es_parametro, prueba = wd_es_ubicacion, de_ubicacion
    pruebas = {c: prueba(c) for c in codigos}
    elegida = wd_elegir(facetas, es_parametro, lambda d: any(ofrece(d) for ofrece in pruebas.values()))
    faltan = [c for c, ofrece in pruebas.items() if not elegida or not any(ofrece(n) for n, _ in elegida[1])]
    return elegida, faltan


def wd_aviso_pais(r, codigos):
    for c in codigos:
        r["revisar"].append(f"el portal no ofrece {c} en su faceta de país ni en la de ubicación: la empresa no "
                            "tiene vacantes ahí hoy, o el portal escribe el país de otra forma (paises de 04)")


def wd_vacante(pref, eid, base, f):
    """Detalle de una vacante del listado, con comprobación de ID por la ruta."""
    url_det = base + f["externalPath"]
    v = vacante(pref, eid, None, f["title"], None, [f.get("locationsText")], None, None, None, None, url_det,
                None, None)
    try:
        det = campo(pedir(url_det), "jobPostingInfo")
        ubic = [campo(det, "location")] + list(det.get("additionalLocations") or [])
        v = vacante(pref, eid, campo(det, "jobReqId"), campo(det, "title"), det.get("externalUrl"), ubic,
                    det.get("remoteType"), det.get("startDate"), *vigencia("canApply", det.get("canApply"), (True,)),
                    url_det, det.get("jobFamily") or None, texto(det.get("jobDescription")))
        # La ruta termina en _<jobReqId>, a veces con un sufijo -1 (republicación)
        if not re.search(rf"_{re.escape(v['job_id'])}(-\d+)?$", f["externalPath"]):
            raise Fallo(f"devolvió otro ID ({v['job_id']})")
    except Fallo as e:
        sin_detalle(v, e)
    return v


WD_CONSULTA = ({"facetas": listas_por_nombre, "texto": es_texto},
               '{"facetas": {"<parámetro>": ["<nombre visible>"]}, "texto": "<búsqueda>"}')


def wd_recorrer(r, pref, eid, base, aplicadas, nombre, vistas, de_remotas=False, busqueda=""):
    """Lista con las facetas elegidas ({parámetro: [(nombre, id)]}) y el texto, lee el detalle de cada vacante
    que no se había visto y la reparte. Devuelve la descripción del listado."""
    filas, total = wd_listar(base, {p: [i for _, i in valores] for p, valores in aplicadas.items()}, busqueda)
    ids = {f["externalPath"] for f in filas}
    filtro = "; ".join([f"{p} = {', '.join(n for n, _ in valores)}" for p, valores in aplicadas.items()]
                       + ([f"searchText = {busqueda}"] if busqueda else []))
    listado(r, f"{nombre}: POST {base}/jobs, {filtro}", total, ids, vistas)
    for f in filas:
        if f["externalPath"] not in vistas:
            vistas.add(f["externalPath"])
            repartir(r, wd_vacante(pref, eid, base, f), pref, de_remotas)
    return f"{filtro}: {len(ids)} únicos de {total}"


def wd_remotas(r, pref, eid, base, facetas, vistas):
    """Las remotas, con el filtro de remoto del portal según el alcance de 04: la faceta de remoto (acotada a los
    países del remoto) o, si no la tiene, sus ubicaciones «Remote …». Devuelve cómo se revisaron."""
    alcance, codigos = pref["remoto"]["alcance"], pref["remoto"]["paises"]
    remoto = wd_elegir(facetas, lambda p: "remote" in p.lower(), es_remota)
    if remoto:
        aplicadas = dict([remoto])
        if alcance == "paises":
            pais, faltan = wd_paises(facetas, pref, codigos, False)
            wd_aviso_pais(r, faltan)
            if not pais:
                return f"Faceta {remoto[0]}, sin listado: el portal no ofrece {', '.join(codigos)}"
            aplicadas[pais[0]] = pais[1]
    else:
        nombres = [n for c in codigos for n in pref["paises"][c]]
        ubicaciones = wd_elegir(facetas, wd_es_ubicacion, lambda d: es_remota(d) and (
            alcance == "cualquiera" or nombra_pais(d, nombres)))
        if not ubicaciones:
            aviso_sin_filtro_de_remoto(r)
            return "No disponible: el portal no tiene faceta de remoto ni ubicaciones «Remote»"
        aplicadas = dict([ubicaciones])
    return "Filtro de remoto del portal, " + wd_recorrer(r, pref, eid, base, aplicadas, "Remotas", vistas,
                                                         de_remotas=True)


def workday(eid, conf, pref, remotas):
    """Adaptador de Workday (06/CAT-PLATAFORMAS)."""
    sitio, base = wd_api(conf["portal"])
    consulta = leer_consulta(conf, *WD_CONSULTA)
    comprobar_robots(sitio, [f"{base}/jobs", f"{base}/job/"])
    facetas = wd_facetas(base)
    r = resultado(eid, "API de Workday (POST para listar, GET para el detalle)")
    vistas = set()
    if consulta:
        ofrecidos = {}
        for p, nombre, i in facetas:
            ofrecidos.setdefault(p, {})[normalizar(nombre)] = (nombre, i)
        aplicadas = resolver(consulta.get("facetas", {}), ofrecidos, r, "la faceta")
        if aplicadas is not None:
            wd_recorrer(r, pref, eid, base, aplicadas, "Consulta de la ficha", vistas,
                        busqueda=consulta.get("texto", ""))
    elif pref["localidades"]:
        faceta, faltan = wd_paises(facetas, pref, paises_region(pref), True)
        wd_aviso_pais(r, faltan)
        if faceta:
            wd_recorrer(r, pref, eid, base, dict([faceta]), "Países de la región", vistas)
    r["remotas_revision"] = sin_remotas(pref, remotas) or wd_remotas(r, pref, eid, base, facetas, vistas)
    return r


# --- Eightfold ------------------------------------------------------------------
# Portal: https://<sitio>/careers?domain=<dominio>, en <empresa>.eightfold.ai o en un dominio de la empresa. API pcsx
# del buscador: GET para listar, 10 por página, y GET para el detalle.

EF_ABIERTOS = ("allowed", "log_in")  # applyAction.status: postulación directa o tras iniciar sesión
EF_CONSULTA = ({"ubicaciones": lista_de_textos, "filtros": listas_por_nombre, "texto": es_texto},
               '{"ubicaciones": ["<lugar>"], "filtros": {"<filtro>": ["<nombre visible>"]}, "texto": "<búsqueda>"}')


def ef_api(portal):
    """(sitio, dominio) desde la URL del portal de la ficha."""
    u = urllib.parse.urlsplit(portal)
    dominio = urllib.parse.parse_qs(u.query).get("domain", [""])[0].strip()
    if u.scheme != "https" or not u.hostname or not dominio:
        raise Fallo(f"el portal {portal} no sirve para Eightfold: debe ser https://<sitio>/careers?domain=<dominio> "
                    "(06/CAT-PLATAFORMAS)")
    return f"https://{u.hostname}", dominio


def ef_pagina(sitio, dominio, parametros):
    """Una página del listado (start va en parametros), en el único orden estable: con el de por defecto, por
    distancia, las páginas se traslapan."""
    consulta = urllib.parse.urlencode({"domain": dominio, "sort_by": "timestamp", **parametros}, doseq=True)
    d = campo(pedir(f"{sitio}/api/pcsx/search?{consulta}"), "data")
    if campo(d, "sortBy") != "timestamp":
        raise Fallo(f"la página start={parametros['start']} no vino ordenada por timestamp")
    return d


def ef_filtros(sitio, dominio):
    """{filterName: [opciones]} de los filtros del buscador, desde su primera página sin filtros. Un sitio con el
    buscador anterior de Eightfold, sin la API pcsx, responde HTTP 403."""
    try:
        d = ef_pagina(sitio, dominio, {"start": 0})
    except Fallo as e:
        if e.codigo == 403:
            raise Fallo(f"{sitio} respondió HTTP 403 a la API pcsx: puede usar el buscador anterior de Eightfold, que "
                        "este adaptador no lee, o bloquear el acceso (06/CAT-PLATAFORMAS)") from e
        raise
    return {f.get("filterName"): f.get("options") or [] for f in (d.get("filterDef") or {}).get("allFilters") or []
            if isinstance(f, dict)}


def ef_ofrecidos(filtros):
    """{filtro: {nombre normalizado: valor}} de sus opciones, por su valor o por su nombre visible (resolver)."""
    ofrecidos = {}
    for nombre, opciones in filtros.items():
        for o in opciones:
            if isinstance(o, dict) and isinstance(o.get("value"), str):
                for k in ("value", "label"):
                    if isinstance(o.get(k), str):
                        ofrecidos.setdefault(nombre, {})[normalizar(o[k])] = o["value"]
    return ofrecidos


def ef_listar(sitio, dominio, parametros, primera=None):
    """(posiciones sin repetir, total) de todas las páginas. primera: la página start=0, si ya se pidió."""
    return por_desplazamiento(lambda inicio: ef_pagina(sitio, dominio, {**parametros, "start": inicio}),
                              lambda d: campo(d, "count"), lambda d: campo(d, "positions"),
                              lambda p: campo(p, "id"), primera)


def ef_pais(sitio, dominio, parametros, pref, c):
    """(nombre, página start=0) del primer nombre de c en 04 que el buscador busca como país; (None, None) si
    ninguno. A una ciudad, o a un lugar que no reconoce, le aplica un radio (distance en appliedFilters)."""
    for nombre in pref["paises"][c]:
        d = ef_pagina(sitio, dominio, {**parametros, "location": nombre, "start": 0})
        if "distance" not in campo(d, "appliedFilters"):
            return nombre, d
    return None, None


def ef_aviso_pais(r, c):
    r["revisar"].append(f"el buscador no reconoce como país ningún nombre de {c} en 04 (le aplica un radio): agrega "
                        "a paises de 04 el nombre que usa el portal")


def ef_codigos(p):
    """Los códigos ISO de país de sus ubicaciones normalizadas: «Ciudad, ST, XA», «ST,XA» o «XA»."""
    finales = (s.rsplit(",", 1)[-1].strip() for s in p.get("standardizedLocations") or [] if isinstance(s, str))
    return {c for c in finales if re.fullmatch(r"[A-Z]{2}", c)}


def ef_vacante(pref, eid, sitio, dominio, p):
    """Vacante desde el listado, que ya trae ubicaciones, modalidad y fecha; el detalle se lee aparte."""
    try:
        publicada = fecha(dt.datetime.fromtimestamp(p.get("postedTs"), dt.timezone.utc), pref)
    except (TypeError, ValueError, OverflowError, OSError):  # sin fecha, o no en segundos
        publicada = None
    modalidad = " | ".join(str(m) for m in (p.get("workLocationOption"), p.get("locationFlexibility")) if m) or None
    url_det = f"{sitio}/api/pcsx/position_details?" + urllib.parse.urlencode(
        {"position_id": p["id"], "domain": dominio, "hl": "en"})
    return vacante(pref, eid, p.get("displayJobId"), p.get("name"),
                   sitio + p["positionUrl"] if p.get("positionUrl") else None, p.get("locations") or [], modalidad,
                   publicada, None, None, url_det, p.get("department"), None)


def ef_detalle(v, pid):
    """Vigencia y descripción desde el detalle, con comprobación de ID."""
    try:
        det = campo(pedir(v["url_fuente"]), "data")
        if det.get("id") != pid:
            raise Fallo(f"devolvió otro ID ({det.get('id')})")
        v["estado_vigencia"], v["motivo"] = vigencia(
            "applyAction.status", campo(det, "positionUserActions", "applyAction", "status"), EF_ABIERTOS)
        v["descripcion"] = texto(det.get("jobDescription"))
    except Fallo as e:
        sin_detalle(v, e)


def ef_recorrer(r, pref, eid, sitio, dominio, parametros, nombre, vistas, de_remotas=False, primera=None):
    """Lista con esos parámetros, reparte las vacantes que no se habían visto y lee el detalle de las que se
    entregan. Devuelve la descripción del listado."""
    filas, total = ef_listar(sitio, dominio, parametros, primera)
    ids = {p["id"] for p in filas}
    filtro = "; ".join(f"{k} = {', '.join(v) if isinstance(v, list) else v}" for k, v in parametros.items())
    listado(r, f"{nombre}: GET {sitio}/api/pcsx/search, {filtro}", total, ids, vistas)
    for p in filas:
        if p["id"] not in vistas:
            vistas.add(p["id"])
            v = ef_vacante(pref, eid, sitio, dominio, p)
            if repartir(r, v, pref, de_remotas, ef_codigos(p)):
                ef_detalle(v, p["id"])
    return f"{filtro}: {len(ids)} únicos de {total}"


def ef_remotas(r, pref, eid, sitio, dominio, filtros, vistas):
    """Las remotas según el alcance de 04: con el filtro de modalidad del buscador (work_location_option), por país
    si el alcance es "paises", o, si no lo tiene, con su búsqueda «Remote», que trae las de todos los países. Como
    la búsqueda por país también puede traer remotas abiertas a otros países, con el alcance "paises" lo decide el
    código de país de cada vacante. Devuelve cómo se revisaron."""
    alcance, codigos = pref["remoto"]["alcance"], pref["remoto"]["paises"]
    remotos = [o["value"] for o in filtros.get("work_location_option", []) if isinstance(o, dict)
               and isinstance(o.get("value"), str) and (es_remota(o["value"]) or es_remota(o.get("label")))]
    if remotos:
        parametros = {"filter_work_location_option": remotos}
        if alcance == "cualquiera":
            return "Filtro de remoto del portal, " + ef_recorrer(r, pref, eid, sitio, dominio, parametros, "Remotas",
                                                                 vistas, de_remotas=True)
        revisadas = []
        for c in codigos:
            nombre, primera = ef_pais(sitio, dominio, parametros, pref, c)
            if nombre:
                revisadas.append(ef_recorrer(r, pref, eid, sitio, dominio, {"location": nombre, **parametros},
                                             "Remotas", vistas, primera=primera))
            else:
                ef_aviso_pais(r, c)
        return "Filtro de remoto del portal, " + ("; ".join(revisadas) or f"sin listado: el buscador no reconoce "
                                                                          f"{', '.join(codigos)} como país")
    d = ef_pagina(sitio, dominio, {"location": "Remote", "start": 0})
    if campo(d, "appliedFilters").get("includeRemote") != ["1"]:
        aviso_sin_filtro_de_remoto(r)
        return "No disponible: el buscador no tiene filtro de modalidad ni búsqueda «Remote»"
    return "Búsqueda «Remote» del portal, " + ef_recorrer(r, pref, eid, sitio, dominio, {"location": "Remote"},
                                                          "Remotas", vistas, alcance == "cualquiera", d)


def eightfold(eid, conf, pref, remotas):
    """Adaptador de Eightfold, para los buscadores con la API pcsx (06/CAT-PLATAFORMAS)."""
    sitio, dominio = ef_api(conf["portal"])
    consulta = leer_consulta(conf, *EF_CONSULTA)
    # Con todos los parámetros que se mandan, por si el robots.txt prohíbe alguno
    busqueda = urllib.parse.urlencode({"domain": dominio, "sort_by": "timestamp", "location": "x", "query": "x",
                                       "filter_work_location_option": "x", "start": 0})
    detalle = urllib.parse.urlencode({"position_id": 0, "domain": dominio, "hl": "en"})
    comprobar_robots(sitio, [f"{sitio}/api/pcsx/search?{busqueda}", f"{sitio}/api/pcsx/position_details?{detalle}"])
    filtros = ef_filtros(sitio, dominio)
    r = resultado(eid, "API pcsx de Eightfold (GET para listar y para el detalle)")
    vistas = set()
    if consulta:
        aplicados = resolver(consulta.get("filtros", {}), ef_ofrecidos(filtros), r, "el filtro")
        if aplicados is not None:
            parametros = {f"filter_{k}": v for k, v in aplicados.items()}
            if consulta.get("texto", "").strip():
                parametros["query"] = consulta["texto"]
            for lugar in consulta.get("ubicaciones") or [None]:
                ef_recorrer(r, pref, eid, sitio, dominio, {**({"location": lugar} if lugar else {}), **parametros},
                            "Consulta de la ficha", vistas)
    elif pref["localidades"]:
        for c in paises_region(pref):
            nombre, primera = ef_pais(sitio, dominio, {}, pref, c)
            if nombre:
                ef_recorrer(r, pref, eid, sitio, dominio, {"location": nombre}, "Países de la región", vistas,
                            primera=primera)
            else:
                ef_aviso_pais(r, c)
    r["remotas_revision"] = sin_remotas(pref, remotas) or ef_remotas(r, pref, eid, sitio, dominio, filtros, vistas)
    return r


# --- Workable -------------------------------------------------------------------
# Portal: https://apply.workable.com/<cuenta>/. API: POST para listar (v3, 10 por página, con token) y GET para el
# detalle (v2).

WK_SITIO = "https://apply.workable.com"


def wk_ubicaciones(u):
    """Las ubicaciones de una consulta: objetos con countryCode, region o city, como las da el listado."""
    return isinstance(u, list) and all(isinstance(l, dict) and l and set(l) <= {"countryCode", "region", "city"}
                                       and all(isinstance(x, str) and x.strip() for x in l.values()) for l in u)


WK_CONSULTA = ({"ubicaciones": wk_ubicaciones, "texto": es_texto},
               '{"ubicaciones": [{"countryCode": "<código>", "region": "<región>", "city": "<ciudad>"}], '
               '"texto": "<búsqueda>"}')


def wk_cuenta(portal):
    """La cuenta de la empresa desde la URL del portal de la ficha."""
    u = urllib.parse.urlsplit(portal)
    partes = [p for p in u.path.split("/") if p]
    if u.scheme != "https" or u.hostname != "apply.workable.com" or not partes or partes[0] in ("j", "api"):
        raise Fallo(f"el portal {portal} no es de Workable: debe ser {WK_SITIO}/<cuenta>/ (06/CAT-PLATAFORMAS)")
    return partes[0]


def wk_listar(base, filtros):
    """(vacantes sin repetir, total) de todas las páginas, con esos campos del cuerpo. Una página llena trae
    nextPage aunque la siguiente salga vacía."""
    cuerpo = {"query": "", "location": [], "department": [], "worktype": [], "remote": [], **filtros}
    filas, ids, total = [], set(), None
    while True:
        d = pedir(f"{base}/jobs", cuerpo)
        if total is None:
            total = campo(d, "total")
        nuevas = [f for f in campo(d, "results") if campo(f, "shortcode") not in ids]
        ids.update(f["shortcode"] for f in nuevas)
        filas += nuevas
        if not nuevas or not d.get("nextPage"):
            return filas, total
        cuerpo = {**cuerpo, "token": d["nextPage"]}


def wk_vacante(pref, eid, cuenta, f):
    """Vacante desde el listado, que ya trae ubicaciones, modalidad y fecha; el detalle se lee aparte."""
    sc = f["shortcode"]
    lugares = [", ".join(x for x in (l.get("city"), l.get("region"), l.get("country")) if x)
               for l in f.get("locations") or []]
    return vacante(pref, eid, sc, f.get("title"), f"{WK_SITIO}/{cuenta}/j/{sc}/", lugares, f.get("workplace"),
                   fecha_iso(f.get("published"), pref), None, None, f"{WK_SITIO}/api/v2/accounts/{cuenta}/jobs/{sc}",
                   None, None)


def wk_codigos(f):
    """Los códigos ISO de país de sus ubicaciones."""
    return {l.get("countryCode") for l in f.get("locations") or []} - {None, ""}


def wk_detalle(v, sc):
    """Vigencia, departamento y descripción desde el detalle, con comprobación de ID."""
    try:
        det = pedir(v["url_fuente"])
        if campo(det, "shortcode") != sc:
            raise Fallo(f"devolvió otro ID ({det['shortcode']})")
        v["estado_vigencia"], v["motivo"] = vigencia("state", det.get("state"), ("published",))
        departamento = det.get("department")
        v["departamento"] = (" / ".join(departamento) if isinstance(departamento, list) else departamento) or None
        secciones = (texto(det.get(k)) for k in ("description", "requirements", "benefits"))
        v["descripcion"] = "\n\n".join(s for s in secciones if s)
    except Fallo as e:
        sin_detalle(v, e)


def wk_recorrer(r, pref, eid, cuenta, filtros, nombre, vistas, de_remotas=False):
    """Lista con esos campos del cuerpo, reparte las vacantes que no se habían visto y lee el detalle de las que se
    entregan. Una vacante es remota por workplace o por el booleano remote, aunque workplace diga otra cosa.
    Devuelve la descripción del listado."""
    base = f"{WK_SITIO}/api/v3/accounts/{cuenta}"
    filas, total = wk_listar(base, filtros)
    ids = {f["shortcode"] for f in filas}
    filtro = "; ".join(f"{k} = {json.dumps(v, ensure_ascii=False)}" for k, v in filtros.items())
    listado(r, f"{nombre}: POST {base}/jobs, {filtro}", total, ids, vistas)
    for f in filas:
        if f["shortcode"] not in vistas:
            vistas.add(f["shortcode"])
            v = wk_vacante(pref, eid, cuenta, f)
            codigos = wk_codigos(f)
            remota = f.get("remote") is True and en_alcance_remoto(v["ubicacion_literal"], pref, codigos)
            if repartir(r, v, pref, de_remotas or remota, codigos):
                wk_detalle(v, f["shortcode"])
    return f"{filtro}: {len(ids)} únicos de {total}"


def wk_remotas(r, pref, eid, cuenta, vistas):
    """Las remotas, con el filtro de remoto de la API, acotado a los países del remoto si el alcance es "paises".
    Ese filtro de país también trae las remotas abiertas a cualquier país, así que ahí el alcance se decide por los
    códigos de país de cada vacante. Devuelve cómo se revisaron."""
    filtros = {"remote": [True]}
    if pref["remoto"]["alcance"] == "paises":
        filtros["location"] = [{"countryCode": c} for c in pref["remoto"]["paises"]]
    return "Filtro de remoto del portal, " + wk_recorrer(r, pref, eid, cuenta, filtros, "Remotas", vistas,
                                                         de_remotas=pref["remoto"]["alcance"] == "cualquiera")


def workable(eid, conf, pref, remotas):
    """Adaptador de Workable (06/CAT-PLATAFORMAS)."""
    cuenta = wk_cuenta(conf["portal"])
    consulta = leer_consulta(conf, *WK_CONSULTA)
    comprobar_robots(WK_SITIO, [f"{WK_SITIO}/api/v3/accounts/{cuenta}/jobs",
                                f"{WK_SITIO}/api/v2/accounts/{cuenta}/jobs/"])
    r = resultado(eid, "API de Workable: listado v3 (POST) y detalle v2 (GET)")
    vistas = set()
    if consulta:
        filtros = {"location": consulta.get("ubicaciones"), "query": consulta.get("texto", "").strip()}
        wk_recorrer(r, pref, eid, cuenta, {k: v for k, v in filtros.items() if v}, "Consulta de la ficha", vistas)
    elif pref["localidades"]:
        wk_recorrer(r, pref, eid, cuenta, {"location": [{"countryCode": c} for c in paises_region(pref)]},
                    "Países de la región", vistas)
    r["remotas_revision"] = sin_remotas(pref, remotas) or wk_remotas(r, pref, eid, cuenta, vistas)
    return r


# --- SmartRecruiters ------------------------------------------------------------
# Portal: el sitio de carreras, https://careers.smartrecruiters.com/<empresa>. Listado agrupado en HTML (GET), con el
# «Show more» de cada grupo, y página de cada publicación en jobs.smartrecruiters.com (GET, HTML). La API de
# api.smartrecruiters.com no se usa: su robots.txt la prohíbe.

SR_CARRERAS = "https://careers.smartrecruiters.com"
SR_PUBLICACIONES = "https://jobs.smartrecruiters.com"
SR_WWW = "https://www.smartrecruiters.com"
SR_PAGINAS = 200  # tope de páginas de grupos; si se alcanza, la paginación cambió
SR_POR_PAGINA = 10  # publicaciones por página del «Show more» de un grupo
SR_SECCIONES = ("jobDescription", "qualifications", "additionalInformation")
SR_CONSULTA = ({"grupos": lista_de_textos, "texto": es_texto},
               '{"grupos": ["<nombre visible del grupo>"], "texto": "<búsqueda>"}')


def sr_empresa(portal):
    """El identificador de la empresa desde la URL del portal de la ficha."""
    u = urllib.parse.urlsplit(portal)
    partes = [p for p in u.path.split("/") if p]
    if (u.scheme != "https" or u.hostname not in ("careers.smartrecruiters.com", "jobs.smartrecruiters.com")
            or not partes or partes[0] == "sr-jobs"):
        raise Fallo(f"el portal {portal} no es de SmartRecruiters: debe ser {SR_CARRERAS}/<empresa> "
                    "(06/CAT-PLATAFORMAS)")
    return partes[0]


def sr_url(empresa, recurso, filtros, **parametros):
    """URL del listado del sitio de carreras: «groups» (los grupos) o «more» (el «Show more» de uno)."""
    return f"{SR_CARRERAS}/{empresa}/api/{recurso}?" + urllib.parse.urlencode({**filtros, **parametros},
                                                                               quote_via=urllib.parse.quote)


def sr_publicaciones(h):
    """Las publicaciones de un fragmento del listado: id, url, título, ref (o None) y los textos bajo el título."""
    pubs = []
    for enlace, cuerpo in re.findall(r"<a\s([^>]*\bjs-job-ad-link\b[^>]*)>(.*?)</a>", h, re.S):
        a = atributos(enlace)
        url = a.get("href", "").split("?")[0]
        m = re.match(rf"{re.escape(SR_PUBLICACIONES)}/[^/]+/(\d+)", url)
        titulo = re.search(r"<h4[^>]*>(.*?)</h4>", cuerpo, re.S)
        if not (m and titulo):
            raise Fallo("el listado del sitio de carreras cambió de forma (una publicación sin ID o sin título)")
        # aria-label: «<título> - <ref>»; sin ref, «undefined»
        aria = a.get("aria-label", "")
        ref = aria.rpartition(" - ")[2].strip() if " - " in aria else ""
        desc = re.search(r'<p class="details-desc job-desc">(.*?)</p>', cuerpo, re.S)
        textos = [texto(s) for s in re.findall(r"<span[^>]*>(.*?)</span>", desc.group(1), re.S)] if desc else []
        pubs.append({"id": m.group(1), "url": url, "titulo": texto(titulo.group(1)),
                     "ref": None if ref in ("", "undefined") else ref, "textos": [t for t in textos if t]})
    return pubs


def sr_grupos_de_pagina(h):
    """Los grupos de una página: nombre, total (data-qty), las publicaciones que muestra y su «Show more»."""
    grupos = []
    for total, s in re.findall(r'<section data-qty="(\d+)"[^>]*>(.*?)</section>', h, re.S):
        nombre = re.search(r"<h3[^>]*>(.*?)</h3>", s, re.S)
        mas = re.search(r"<a\s([^>]*\bjs-more\b[^>]*)>", s)
        a = atributos(mas.group(1)) if mas else {}
        if not nombre or (mas and not (a.get("data-type") and a.get("data-value"))):
            raise Fallo("el listado del sitio de carreras cambió de forma (un grupo sin nombre o con otro «Show more»)")
        grupos.append({"nombre": texto(nombre.group(1)), "total": int(total), "publicaciones": sr_publicaciones(s),
                       "mas": (a["data-type"], urllib.parse.unquote(a["data-value"])) if mas else None})
    if len(re.findall(r"\bjs-job-ad-link\b", h)) != sum(len(g["publicaciones"]) for g in grupos):
        raise Fallo("el listado del sitio de carreras cambió de forma (publicaciones fuera de un grupo)")
    return grupos


def sr_grupos(empresa, filtros):
    """Los grupos de todas las páginas del listado. Sin filtros, el sitio los reparte en páginas; con un filtro, los
    repite todos en cada una: se para en la primera página que no trae un grupo nuevo."""
    grupos, vistos = [], set()
    for p in range(SR_PAGINAS):
        nuevos = []
        for g in sr_grupos_de_pagina(pedir(sr_url(empresa, "groups", filtros, page=p), como_json=False)):
            clave = (g["nombre"], g["total"], tuple(x["id"] for x in g["publicaciones"]))
            if clave not in vistos:
                vistos.add(clave)
                nuevos.append(g)
        if not nuevos:
            return grupos
        grupos += nuevos
    raise Fallo("el listado de grupos no termina: la paginación del sitio pudo haber cambiado")


def sr_completar(empresa, filtros, g):
    """Las publicaciones del grupo, también las que esconde su «Show more»: sus páginas, hasta una vacía. La página 0
    repite las que muestra el grupo."""
    pubs = {x["id"]: x for x in g["publicaciones"]}
    if g["mas"]:
        tipo, valor = g["mas"]
        for k in range(g["total"] // SR_POR_PAGINA + 2):  # más la página 0 y la vacía del final
            pagina = sr_publicaciones(pedir(sr_url(empresa, "more", filtros, type=tipo, value=valor, page=k),
                                            como_json=False))
            if not pagina:
                break
            for x in pagina:
                pubs.setdefault(x["id"], x)
    return list(pubs.values())


def sr_pagina(x):
    """Los campos de la página de una publicación, con comprobación de ID."""
    h = pedir(x["url"], como_json=False)
    canonica = re.search(r'<link\s[^>]*\brel="canonical"[^>]*>', h)
    devuelto = re.search(r"/(\d+)[^/]*$", atributos(canonica.group(0)).get("href", "")) if canonica else None
    if not devuelto:
        raise Fallo("la página no trae su ID (link canonical)")
    if devuelto.group(1) != x["id"]:
        raise Fallo(f"devolvió otro ID ({devuelto.group(1)})")
    micro = dict(re.findall(r'itemprop="(address(?:Locality|Region|Country))"[^>]*\bcontent="([^"]*)"', h))
    partes = [html.unescape(micro[k]).strip() for k in ("addressLocality", "addressRegion", "addressCountry")
              if micro.get(k, "").strip()]
    ubicacion = re.search(r"<spl-job-location\s[^>]*>", h)
    a = atributos(ubicacion.group(0)) if ubicacion else {}
    publicada = re.search(r'itemprop="datePosted"[^>]*\bcontent="([^"]*)"', h)
    ref = re.search(r"'jobRefCode': '([^']+)'", h)
    departamento = re.search(r'<li class="job-detail">\s*Department:\s*(.*?)</li>', h, re.S)
    secciones = dict(re.findall(r'<section class="job-section" id="st-(\w+)"[^>]*>(.*?)</section>', h, re.S))
    return {"lugar": ", ".join({normalizar(p): p for p in partes}.values()),  # sin partes repetidas («Canada, CANADA»)
            "modalidad": " | ".join(m for m in (a.get("workplaceType"), a.get("workplaceDescription")) if m) or None,
            "publicada": publicada.group(1) if publicada else None, "ref": ref.group(1) if ref else None,
            "departamento": (texto(departamento.group(1)) or None) if departamento else None,
            "abierta": 'data-sr-track="apply"' in h,
            "descripcion": "\n\n".join(texto(secciones[k]) for k in SR_SECCIONES if k in secciones)}


def sr_vacante(pref, eid, x, lugares, modalidad, pagina=None):
    """Vacante de una publicación con su página (pagina: la ya leída); si la página falla, queda con lo del listado.
    modalidad: la del filtro que la trajo, si la dice."""
    v = vacante(pref, eid, x["ref"], x["titulo"], x["url"], lugares, modalidad, None, None, None, x["url"], None, None)
    try:
        p = pagina or sr_pagina(x)
    except Fallo as e:
        return sin_detalle(v, e)
    return vacante(pref, eid, p["ref"] or x["ref"], x["titulo"], x["url"], [p["lugar"]] if p["lugar"] else lugares,
                   p["modalidad"] or modalidad, fecha_iso(p["publicada"], pref),
                   *vigencia('botón de postulación (data-sr-track="apply")', p["abierta"], (True,)), x["url"],
                   p["departamento"], p["descripcion"])


def sr_recorrer(r, pref, eid, empresa, filtros, nombre, vistas, puede_estar, de_remotas=False, modalidad=None,
                elegidos=None):
    """Lista los grupos con esos filtros, completa los que pueden traer vacantes buscadas, lee la página de cada
    publicación que puede serlo (puede_estar: si puede serlo, por sus lugares del listado) y la reparte. elegidos:
    los grupos de la consulta. Devuelve la descripción del listado.

    Un sitio agrupa por ubicación o por otro campo, como el departamento, y el «Show more» de un grupo grande dice
    cuál. Por ubicación, el lugar de una publicación es el nombre de su grupo, y un grupo que no puede estar no se
    completa; por otro campo, es el texto bajo su título; si ningún grupo lo dice, se prueban los dos. Un lugar que no
    nombra un país de 04, como «Ciudad, Estado», lo decide la página de la primera publicación con ese lugar."""
    grupos = sr_grupos(empresa, filtros)
    tipos = {g["mas"][0] for g in grupos if g["mas"]}
    por_ubicacion = "location" in tipos
    leidas, decididos = {}, {}  # páginas ya leídas, que no se vuelven a pedir, y lo que decidieron por lugar

    def lugares_de(g, x):
        return [g["nombre"]] if por_ubicacion else x["textos"] if tipos else [g["nombre"], *x["textos"]]

    def se_lee(lugares, x):
        if not lugares or puede_estar(lugares):
            return True
        clave = " | ".join(lugares)
        if paises_nombrados(clave, pref):
            return False
        if clave not in decididos:
            try:
                leidas[x["id"]] = sr_pagina(x)
                decididos[clave] = puede_estar([leidas[x["id"]]["lugar"] or clave])
            except Fallo:
                decididos[clave] = True  # sin la página no se sabe: se leen, y quedan con lo del listado
        return decididos[clave]

    if elegidos is not None:
        pedidos = {normalizar(n) for n in elegidos}
        hay = {normalizar(g["nombre"]) for g in grupos}
        for n in elegidos:
            if normalizar(n) not in hay:
                r["revisar"].append(f"el sitio no tiene el grupo «{n}»: no hay vacantes en él hoy, o el nombre cambió "
                                    "(consulta de la ficha)")
        grupos = [g for g in grupos if normalizar(g["nombre"]) in pedidos]
    completos, total = [], 0
    for g in grupos:
        if (elegidos is None and por_ubicacion and g["publicaciones"]
                and not se_lee([g["nombre"]], g["publicaciones"][0])):
            if any(x["id"] not in vistas for x in g["publicaciones"]) or len(g["publicaciones"]) < g["total"]:
                anotar_fuera(r, g["nombre"])
            continue
        completos.append((g, sr_completar(empresa, filtros, g)))
        total += g["total"]
    ids = {x["id"] for _, pubs in completos for x in pubs}
    filtro = "; ".join(f"{k} = {v}" for k, v in filtros.items()) or "sin filtros"
    listado(r, f"{nombre}: GET {SR_CARRERAS}/{empresa}/api/groups y api/more, {filtro}", total, ids, vistas)
    for g, pubs in completos:
        for x in pubs:
            if x["id"] not in vistas:
                vistas.add(x["id"])
                lugares = lugares_de(g, x)
                if se_lee(lugares, x):
                    repartir(r, sr_vacante(pref, eid, x, lugares, modalidad, leidas.get(x["id"])), pref, de_remotas)
                else:
                    anotar_fuera(r, " | ".join(lugares))
    return f"{filtro}: {len(completos)} de {len(grupos)} grupos, {len(ids)} únicos de {total}"


def sr_en_la_region(lugares, pref):
    """Una publicación puede estar en la región por sus lugares del listado: alguno puede estarlo según 04, o nombran
    uno de sus países, y entonces su página dice la localidad."""
    return (any(clasificar_ubicacion(l, pref) != "fuera" for l in lugares)
            or bool(paises_nombrados(" | ".join(lugares), pref) & set(paises_region(pref))))


def sr_remotas(r, pref, eid, empresa, vistas):
    """Las remotas, con el filtro locationType=REMOTE del sitio, que trae las de todos los países: con el alcance
    "paises", lo decide el lugar de cada una. Devuelve cómo se revisaron."""
    def puede_estar(lugares):
        # El alcance, con los lugares juntos: si el sitio no dice cómo agrupa, uno puede no ser un lugar («Full-time»)
        return sr_en_la_region(lugares, pref) or en_alcance_remoto(" | ".join(lugares), pref)

    return "Filtro locationType=REMOTE del sitio, " + sr_recorrer(
        r, pref, eid, empresa, {"locationType": "REMOTE"}, "Remotas", vistas, puede_estar,
        de_remotas=pref["remoto"]["alcance"] == "cualquiera", modalidad="REMOTE")


def sr_requisiciones(r):
    """Señala las publicaciones entregadas que comparten requisición (job_id): son una sola vacante."""
    por_id = {}
    for v in r["vacantes"] + r["remotas_fuera_de_region"]:
        if v["job_id"]:
            por_id.setdefault(v["job_id"], []).append(v)
    for mismas in por_id.values():
        if len(mismas) > 1:
            urls = ", ".join(v["url_oficial"] for v in mismas)
            for v in mismas:
                v.setdefault("revisar", []).append(
                    f"requisición con {len(mismas)} publicaciones en esta búsqueda ({urls}): es una sola vacante, con "
                    "todas sus ubicaciones y la relación regional de todas (11/REG-IDENTIDAD)")


def smartrecruiters(eid, conf, pref, remotas):
    """Adaptador del sitio de carreras de SmartRecruiters (06/CAT-PLATAFORMAS)."""
    empresa = sr_empresa(conf["portal"])
    consulta = leer_consulta(conf, *SR_CONSULTA)
    filtros = {"locationType": "REMOTE", "search": "x"}
    comprobar_robots(SR_CARRERAS, [sr_url(empresa, "groups", filtros, page=0),
                                   sr_url(empresa, "more", filtros, type="location", value="x", page=0)])
    comprobar_robots(SR_PUBLICACIONES, [f"{SR_PUBLICACIONES}/{empresa}/0"])
    # El robots.txt de www.smartrecruiters.com prohíbe las páginas de algunas empresas: esas no se leen en ningún host
    comprobar_robots(SR_WWW, [f"{SR_WWW}/{empresa}/"])
    r = resultado(eid, "Sitio de carreras de SmartRecruiters (GET, HTML): listado agrupado, «Show more» de cada "
                       "grupo y página de cada publicación")
    vistas = set()
    # Las remotas van primero: el listado no dice la modalidad, y una remota de fuera de la región que ya trajo el
    # listado de la región no se volvería a ver
    revision = sin_remotas(pref, remotas) or sr_remotas(r, pref, eid, empresa, vistas)
    if consulta:
        busqueda = consulta.get("texto", "").strip()
        sr_recorrer(r, pref, eid, empresa, {"search": busqueda} if busqueda else {}, "Consulta de la ficha", vistas,
                    lambda lugares: sr_en_la_region(lugares, pref), elegidos=consulta.get("grupos") or None)
    elif pref["localidades"]:
        sr_recorrer(r, pref, eid, empresa, {}, "Grupos de la región", vistas,
                    lambda lugares: sr_en_la_region(lugares, pref))
    r["remotas_revision"] = revision
    sr_requisiciones(r)
    return r


# --- Oracle Recruiting Cloud ----------------------------------------------------
# Portal: https://<host>/hcmUI/CandidateExperience/<idioma>/sites/<sitio>. API REST del mismo host: GET para listar
# (finder findReqs, 25 por página) y GET para el detalle (finder ById).

OR_POR_PAGINA = 25
# Las facetas: su nombre en facetsList → (su lista en la respuesta, el parámetro que filtra por ella)
OR_FACETAS = {"LOCATIONS": ("locationsFacet", "selectedLocationsFacet"),
              "WORKPLACE_TYPES": ("workplaceTypesFacet", "selectedWorkplaceTypesFacet"),
              "CATEGORIES": ("categoriesFacet", "selectedCategoriesFacet"),
              "ORGANIZATIONS": ("organizationsFacet", "selectedOrganizationsFacet"),
              "TITLES": ("titlesFacet", "selectedTitlesFacet")}
OR_CONSULTA = ({"facetas": lambda x: listas_por_nombre(x) and set(x) <= set(OR_FACETAS), "texto": es_texto},
               '{"facetas": {"<faceta>": ["<nombre visible>"]}, "texto": "<búsqueda>"}')
OR_DESCRIPCION = ("ExternalDescriptionStr", "ExternalResponsibilitiesStr", "ExternalQualificationsStr")


def or_api(portal):
    """(sitio, portal, base de la API, número de sitio) desde la URL del portal de la ficha."""
    u = urllib.parse.urlsplit(portal)
    m = re.fullmatch(r"(/hcmUI/CandidateExperience/[^/]+/sites/([^/]+))(?:/requisitions)?/?", u.path)
    if u.scheme != "https" or not u.hostname or not m:
        raise Fallo(f"el portal {portal} no es de Oracle Recruiting Cloud: debe ser "
                    "https://<host>/hcmUI/CandidateExperience/<idioma>/sites/<sitio> (06/CAT-PLATAFORMAS)")
    sitio = f"https://{u.hostname}"
    return sitio, sitio + m.group(1), f"{sitio}/hcmRestApi/resources/latest", m.group(2)


def or_finder(nombre, parametros):
    """El parámetro finder de la API, «finder=<nombre>;k=v,k=v», con cada valor codificado."""
    return f"finder={nombre};" + ",".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in parametros.items())


def or_url(api, numero, parametros, inicio):
    """URL de una página del listado, de la publicación más reciente a la más antigua."""
    return (f"{api}/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations&"
            + or_finder("findReqs", {"siteNumber": numero, "facetsList": ";".join(OR_FACETAS), "limit": OR_POR_PAGINA,
                                     "offset": inicio, "sortBy": "POSTING_DATES_DESC", **parametros}))


def or_pagina(api, numero, parametros, inicio):
    """items[0] de una página del listado: total, requisiciones y facetas."""
    items = campo(pedir(or_url(api, numero, parametros, inicio)), "items")
    if not (isinstance(items, list) and items):
        raise Fallo("el listado no trajo items: la API pudo haber cambiado")
    return items[0]


def or_listar(api, numero, parametros, primera=None):
    """(requisiciones sin repetir, total) de todas las páginas. primera: la página offset=0, si ya se pidió."""
    return por_desplazamiento(lambda inicio: or_pagina(api, numero, parametros, inicio),
                              lambda it: campo(it, "TotalJobsCount"), lambda it: campo(it, "requisitionList"),
                              lambda x: str(campo(x, "Id")), primera)


def or_pais(api, numero, parametros, pref, c):
    """(nombre, página offset=0) del primer nombre de c en 04 que la API reconoce; (None, None) si ninguno. Con un
    nombre que no reconoce, location no filtra y trae todo el sitio. Lo reconoce si no hay ninguna requisición o si
    su faceta de ubicaciones trae ese nombre con el total del resultado: la del sitio completo también puede traer
    el país con otro conteo, y con otros acentos («Canadá» frente a «Canada»)."""
    for nombre in pref["paises"][c]:
        it = or_pagina(api, numero, {**parametros, "location": nombre}, 0)
        total = campo(it, "TotalJobsCount")
        if total == 0 or any(isinstance(f, dict) and normalizar(str(f.get("Name"))) == normalizar(nombre)
                             and f.get("TotalCount") == total for f in it.get("locationsFacet") or []):
            return nombre, it
    return None, None


def or_aviso_pais(r, c):
    r["revisar"].append(f"la API no reconoce como país ningún nombre de {c} en 04: agrega a paises de 04 el nombre que "
                        "usa la faceta de ubicaciones del portal, en su idioma")


def or_codigos(x):
    """Los códigos ISO de país de sus ubicaciones, la principal y las secundarias."""
    return ({x.get("PrimaryLocationCountry")} | {s.get("CountryCode") for s in x.get("secondaryLocations") or []
                                                 if isinstance(s, dict)}) - {None, ""}


def or_vacante(pref, eid, portal, api, numero, x):
    """Vacante desde el listado, que ya trae ubicaciones, modalidad y fecha; el detalle se lee aparte."""
    rid = str(x["Id"])
    lugares = [x.get("PrimaryLocation")] + [s.get("Name") for s in x.get("secondaryLocations") or []
                                            if isinstance(s, dict)]
    url_det = (f"{api}/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&"
               + or_finder("ById", {"Id": f'"{rid}"', "siteNumber": numero}))
    return vacante(pref, eid, rid, x.get("Title"), f"{portal}/job/{rid}", lugares, x.get("WorkplaceType") or None,
                   x.get("PostedDate"), None, None, url_det, x.get("JobFunction"), None)


def or_detalle(v, rid, pref):
    """Vigencia, fecha, modalidad, función y descripción desde el detalle, con comprobación de ID. La API no trae un
    indicador de postulación: la vacante está en el listado y vale mientras su fecha de cierre no haya pasado."""
    try:
        items = campo(pedir(v["url_fuente"]), "items")
        det = items[0] if isinstance(items, list) and items else None
        if str(campo(det, "Id")) != rid:
            raise Fallo(f"devolvió otro ID ({det['Id']})")
        fin = det.get("ExternalPostedEndDate")
        cierre = instante_iso(fin)
        vigente = fin is None or (cierre is not None and cierre > dt.datetime.now(dt.timezone.utc))
        v["estado_vigencia"] = "Confirmada abierta" if vigente else "Revisar"
        v["motivo"] = f"En listado oficial; ExternalPostedEndDate: {json.dumps(fin)}" + (
            "" if vigente else " (fecha de cierre pasada o ilegible: decidir con 07/BUS-VIGENCIA)")
        v["fecha_publicacion"] = fecha_iso(det.get("ExternalPostedStartDate"), pref) or v["fecha_publicacion"]
        v["modalidad_literal"] = det.get("WorkplaceType") or v["modalidad_literal"]
        v["departamento"] = det.get("JobFunction") or det.get("Category") or v["departamento"]
        v["descripcion"] = "\n\n".join(texto(det[k]) for k in OR_DESCRIPCION if det.get(k))
    except Fallo as e:
        sin_detalle(v, e)


def or_recorrer(r, pref, eid, portal, api, numero, parametros, nombre, vistas, de_remotas=False, primera=None):
    """Lista con esos parámetros del finder, reparte las requisiciones que no se habían visto y lee el detalle de las
    que se entregan. Devuelve la descripción del listado."""
    filas, total = or_listar(api, numero, parametros, primera)
    ids = {str(x["Id"]) for x in filas}
    filtro = "; ".join(f"{k} = {v}" for k, v in parametros.items())
    listado(r, f"{nombre}: GET {api}/recruitingCEJobRequisitions, {filtro}", total, ids, vistas)
    for x in filas:
        rid = str(x["Id"])
        if rid not in vistas:
            vistas.add(rid)
            v = or_vacante(pref, eid, portal, api, numero, x)
            if repartir(r, v, pref, de_remotas, or_codigos(x)):
                or_detalle(v, rid, pref)
    return f"{filtro}: {len(ids)} únicos de {total}"


def or_remotas(r, pref, eid, portal, api, numero, facetas, vistas):
    """Las remotas, con el valor remoto de la faceta de modalidad, un listado por país del remoto si el alcance es
    "paises". Una búsqueda por país también trae las requisiciones que lo tienen como ubicación secundaria: el alcance
    lo deciden los códigos de país de cada una. Devuelve cómo se revisaron."""
    alcance, codigos = pref["remoto"]["alcance"], pref["remoto"]["paises"]
    remotos = [str(f["Id"]) for f in facetas.get("workplaceTypesFacet") or [] if isinstance(f, dict)
               and f.get("Id") is not None and (es_remota(str(f.get("Name"))) or es_remota(str(f["Id"])))]
    if not remotos:
        aviso_sin_filtro_de_remoto(r)
        return "No disponible: la faceta de modalidad del sitio no ofrece un valor remoto"
    parametros = {"selectedWorkplaceTypesFacet": ";".join(remotos)}
    if alcance == "cualquiera":
        return "Faceta de modalidad del sitio, " + or_recorrer(r, pref, eid, portal, api, numero, parametros, "Remotas",
                                                               vistas, de_remotas=True)
    revisadas = []
    for c in codigos:
        nombre, primera = or_pais(api, numero, parametros, pref, c)
        if nombre:
            revisadas.append(or_recorrer(r, pref, eid, portal, api, numero, {"location": nombre, **parametros},
                                         "Remotas", vistas, primera=primera))
        else:
            or_aviso_pais(r, c)
    return "Faceta de modalidad del sitio, " + ("; ".join(revisadas) or f"sin listado: la API no reconoce "
                                                                        f"{', '.join(codigos)} como país")


def oraclerecruitingcloud(eid, conf, pref, remotas):
    """Adaptador de Oracle Recruiting Cloud (06/CAT-PLATAFORMAS)."""
    sitio, portal, api, numero = or_api(conf["portal"])
    consulta = leer_consulta(conf, *OR_CONSULTA)
    # Con todos los parámetros que se mandan, por si el robots.txt prohíbe alguno
    todos = {"location": "x", "keyword": "x", **{p: "x" for _, p in OR_FACETAS.values()}}
    comprobar_robots(sitio, [or_url(api, numero, todos, 0), f"{api}/recruitingCEJobRequisitionDetails?expand=all&"
                             f"onlyData=true&" + or_finder("ById", {"Id": '"0"', "siteNumber": numero})])
    facetas = or_pagina(api, numero, {}, 0)
    r = resultado(eid, "API REST de Oracle Recruiting Cloud (GET para listar y para el detalle)")
    vistas = set()
    if consulta:
        ofrecidos = {nombre: {normalizar(str(f.get("Name"))): str(f["Id"]) for f in facetas.get(clave) or []
                              if isinstance(f, dict) and f.get("Id") is not None}
                     for nombre, (clave, _) in OR_FACETAS.items()}
        aplicadas = resolver(consulta.get("facetas", {}), ofrecidos, r, "la faceta")
        if aplicadas is not None:
            parametros = {OR_FACETAS[k][1]: ";".join(v) for k, v in aplicadas.items()}
            if consulta.get("texto", "").strip():
                parametros["keyword"] = consulta["texto"].strip()
            or_recorrer(r, pref, eid, portal, api, numero, parametros, "Consulta de la ficha", vistas)
    elif pref["localidades"]:
        for c in paises_region(pref):
            nombre, primera = or_pais(api, numero, {}, pref, c)
            if nombre:
                or_recorrer(r, pref, eid, portal, api, numero, {"location": nombre}, "Países de la región", vistas,
                            primera=primera)
            else:
                or_aviso_pais(r, c)
    r["remotas_revision"] = sin_remotas(pref, remotas) or or_remotas(r, pref, eid, portal, api, numero, facetas, vistas)
    return r


# --- Principal --------------------------------------------------------------

# Un adaptador por plataforma de reclutamiento (06/CAT-PLATAFORMAS). Uno nuevo es una función
# (eid, conf, pref, remotas) que devuelve resultado(), llenado con listado(), repartir() y anotar_fuera(), y que
# antes de pedir nada pasa por comprobar_robots(); se registra aquí con el nombre que lleva la ficha en «plataforma».
ADAPTADORES = {"workday": workday, "eightfold": eightfold, "workable": workable, "smartrecruiters": smartrecruiters,
               "oraclerecruitingcloud": oraclerecruitingcloud}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=f"Plataformas con adaptador: {', '.join(ADAPTADORES)}.")
    ap.add_argument("empresas", nargs="*", metavar="EMP-ID", help="IDs de 06 (por defecto, todo el catálogo)")
    ap.add_argument("--salida", help="archivo JSON de salida (por defecto, stdout)")
    ap.add_argument("--sin-remotas", action="store_true", help="omitir el listado de vacantes remotas")
    a = ap.parse_args()
    pref = leer_preferencias(MODULO_04)
    catalogo = leer_catalogo(MODULO_06)
    pedidas = [e.upper() for e in a.empresas] or list(catalogo)
    desconocidas = [e for e in pedidas if e not in catalogo]
    if desconocidas:
        ap.error(f"{', '.join(desconocidas)} no está en el catálogo de 06; opciones: {', '.join(catalogo)}")
    if a.sin_remotas and not pref["localidades"]:
        ap.error("04 solo acepta remoto (localidades vacía): con --sin-remotas no habría nada que buscar")
    ahora = dt.datetime.now(pref["tz"])
    res = {"script": f"herramientas/buscar.py v{VERSION}", "fecha_hora": ahora.strftime("%Y-%m-%d %H:%M"),
           "zona_horaria": pref["zona_horaria"], "empresas": []}
    fallos = 0
    for eid in pedidas:
        try:
            conf = leer_ficha(eid, catalogo[eid])
            adaptador = ADAPTADORES.get(conf["plataforma"].strip().lower())
            if adaptador is None:
                raise Fallo(f"la plataforma {conf['plataforma']!r} no tiene adaptador en el script (hay: "
                            f"{', '.join(ADAPTADORES)}); para agregar uno, 06/CAT-REGLAS")
            r = adaptador(eid, conf, pref, not a.sin_remotas)
        except Fallo as e:
            fallos += 1
            r = {"empresa_id": eid, "error": str(e)}
        res["empresas"].append(r)
        if "error" in r:
            print(f"[FALLO] {eid}: {r['error']}", file=sys.stderr)
            continue
        en_region = sum(v["region_relacionada"] in ("Dentro", "Incluye") for v in r["vacantes"])
        # completa = None: la fuente no publica total (07/BUS-COBERTURA); se declara con su verificación
        estado = "OK" if r["completa"] else "SIN TOTAL" if r["completa"] is None else "INCOMPLETA"
        cuenta = (f"{r['unicos']}/{r['total_reportado']}" if r["total_reportado"] is not None
                  else f"{r['unicos']} (sin total publicado)")
        print(f"[{estado}] {eid}: {cuenta} únicos; {en_region} en la región; remotas fuera de la región: "
              f"{len(r['remotas_fuera_de_region'])} ({r['remotas_revision']})", file=sys.stderr)
        if r.get("verificacion_cobertura"):
            print(f"    cobertura: {r['verificacion_cobertura']}", file=sys.stderr)
        for nota in r["revisar"]:
            print(f"    revisar: {nota}", file=sys.stderr)
        for v in r["vacantes"] + r["remotas_fuera_de_region"]:
            # Sin Job ID publicado (11/REG-IDENTIDAD), la vacante se nombra por su URL
            ident = v["job_id"] if v["job_id"] not in (None, "No publicado") else v["url_oficial"] or v["url_fuente"]
            if v["ubicaciones_por_revisar"] or v["region_relacionada"] == "Indeterminada":
                print(f"    revisar ubicación: {ident} {v['ubicacion_literal']}", file=sys.stderr)
            if v["estado_vigencia"] != "Confirmada abierta" or "detalle no consultado" in (v["motivo"] or ""):
                print(f"    revisar vigencia: {ident} {v['motivo']}", file=sys.stderr)
            for nota in v.get("revisar", []):
                print(f"    revisar: {ident} {nota}", file=sys.stderr)
    salida = json.dumps(res, ensure_ascii=False, indent=1)
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(salida + "\n")
    else:
        print(salida)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
