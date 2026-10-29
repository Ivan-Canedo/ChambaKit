"""Pruebas del script de búsqueda, sin red.

Uso:
    python3 -I -B -m unittest discover -s herramientas/pruebas

Cada prueba arma una copia ficticia con el script, un 04 y un 06. La configuración que falta se
prueba por la línea de comandos, porque el script se detiene antes de cualquier petición. La
clasificación de ubicaciones y cada adaptador se prueban corriendo main() con un portal falso de su
plataforma (Workday, Eightfold, Workable, SmartRecruiters u Oracle Recruiting Cloud) en lugar de la
red: los anuncios y los lugares son ficticios, con los códigos XA, XB, XC y XD, que la norma ISO
reserva y no son países.
"""
import contextlib
import datetime as dt
import html
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest import mock

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "herramientas" / "buscar.py"

PAISES = {"XA": ["País A", "Country A"], "XB": ["País B", "Country B"], "XC": ["País C", "Country C"]}


def preferencias(localidades, alcance="ninguno", paises_remoto=(), **cambios):
    """Bloque de 04/PREF-UBICACION lleno, con los cambios que pida la prueba."""
    bloque = {"paises": PAISES, "localidades": localidades,
              "remoto": {"alcance": alcance, "paises": list(paises_remoto)},
              "zona_horaria": "UTC", "moneda": "XTS"}
    bloque.update(cambios)
    return bloque


def grupo(pais, divisiones=(), nombres=()):
    return {"pais": pais, "divisiones": list(divisiones), "zona": None, "nombres": list(nombres)}


def modulo_04(bloque):
    texto = bloque if isinstance(bloque, str) else json.dumps(bloque, ensure_ascii=False, indent=2)
    return f"# 04 — Preferencias laborales\n\n## PREF-UBICACION — Región\n\nRegión.\n\n```json\n{texto}\n```\n"


def ficha(eid, configuracion):
    texto = configuracion if isinstance(configuracion, str) else json.dumps(configuracion, indent=2)
    return f"## {eid} — Empresa ficticia\n\n### Configuración\n\n```json\n{texto}\n```\n\n### Identidad\n\n- Ficticia.\n"


def modulo_06(fichas):
    filas = "".join(f"| {eid} | Empresa ficticia | Objetivo | 0.1 | 2026-10-16 |\n" for eid in fichas)
    return ("# 06 — Empresas objetivo y fichas\n\n## CAT-EMPRESAS — Catálogo\n\n"
            "| ID | Empresa | Estado | Versión de ficha | Fecha de comprobación |\n"
            "| --- | --- | --- | --- | --- |\n" + filas + "\n## CAT-REGLAS — Mantenimiento\n\n- Reglas.\n\n"
            + "\n".join(fichas.values()))


class CopiaFicticia(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)
        (self.dir / "herramientas").mkdir()
        shutil.copy(SCRIPT, self.dir / "herramientas")

    def tearDown(self):
        self._tmp.cleanup()

    def escribir(self, modulo_04_texto=None, modulo_06_texto=None):
        if modulo_04_texto is not None:
            (self.dir / "04_PREFERENCIAS_LABORALES.md").write_text(modulo_04_texto, encoding="utf-8")
        if modulo_06_texto is not None:
            (self.dir / "06_EMPRESAS_OBJETIVO.md").write_text(modulo_06_texto, encoding="utf-8")

    def correr(self, *argumentos):
        """El script de la copia por su línea de comandos."""
        return subprocess.run([sys.executable, "-I", "-B", str(self.dir / "herramientas" / "buscar.py"), *argumentos],
                              capture_output=True, text=True, timeout=60)


class ConfiguracionFaltante(CopiaFicticia):
    def assertFallaSinBuscar(self, r, *textos):
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        for t in textos:
            self.assertIn(t, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_sin_04_falla_con_un_mensaje_claro(self):
        self.escribir(None, modulo_06({}))
        self.assertFallaSinBuscar(self.correr(), "04_PREFERENCIAS_LABORALES.md")

    def test_con_el_bloque_de_04_sin_llenar_pide_configurarlo(self):
        plantilla = {"paises": {}, "localidades": [], "remoto": {"alcance": None, "paises": []},
                     "zona_horaria": None, "moneda": None}
        self.escribir(modulo_04(plantilla), modulo_06({}))
        self.assertFallaSinBuscar(self.correr(), "PREF-UBICACION", "/configurar", "paso 4")

    def test_un_bloque_de_04_que_no_cumple_sus_reglas_falla_con_un_mensaje_claro(self):
        en_xa = [grupo("XA", nombres=["Ciudad A1"])]
        casos = {
            "sin bloque": ("# 04\n\n## PREF-UBICACION — Región\n\nSin bloque.\n", "```json"),
            "JSON inválido": (modulo_04('{"paises": {},}'), "JSON"),
            "país sin nombres": (modulo_04(preferencias([grupo("XD", nombres=["Ciudad D1"])])), "XD"),
            "alcance desconocido": (modulo_04(preferencias(en_xa, alcance="mundo")), "remoto.alcance"),
            "remoto por países sin países": (modulo_04(preferencias(en_xa, alcance="paises")), "remoto.paises"),
            "nada que buscar": (modulo_04(preferencias([], alcance="ninguno")), "localidades"),
            "zona horaria inexistente": (modulo_04(preferencias(en_xa, zona_horaria="Region/Inexistente")),
                                         "zona_horaria"),
            "localidad sin lista": (modulo_04(preferencias([{"pais": "XA", "nombres": "Ciudad A1"}])), "localidades"),
        }
        for caso, (texto, campo) in casos.items():
            with self.subTest(caso):
                self.escribir(texto, modulo_06({}))
                self.assertFallaSinBuscar(self.correr(), "PREF-UBICACION", campo)

    def test_sin_06_falla_con_un_mensaje_claro(self):
        self.escribir(modulo_04(preferencias([grupo("XA", nombres=["Ciudad A1"])])), None)
        self.assertFallaSinBuscar(self.correr(), "06_EMPRESAS_OBJETIVO.md")

    def test_con_el_catalogo_vacio_pide_agregar_empresas(self):
        self.escribir(modulo_04(preferencias([grupo("XA", nombres=["Ciudad A1"])])), modulo_06({}))
        self.assertFallaSinBuscar(self.correr(), "CAT-EMPRESAS", "/configurar", "paso 7")

    def test_una_empresa_que_no_esta_en_el_catalogo_falla_y_nombra_las_que_hay(self):
        self.escribir(modulo_04(preferencias([grupo("XA", nombres=["Ciudad A1"])])),
                      modulo_06({"EMP-ACME": ficha("EMP-ACME", {"plataforma": "workday", "portal": "https://x"})}))
        self.assertFallaSinBuscar(self.correr("EMP-OTRA"), "EMP-OTRA", "EMP-ACME")

    def test_una_ficha_sin_configuracion_usable_sale_como_fallo_sin_detener_las_demas(self):
        sin_bloque = "## EMP-SINBLOQUE — Empresa ficticia\n\n### Configuración\n\n«pendiente»\n"
        fichas = {
            "EMP-SINBLOQUE": sin_bloque,
            "EMP-ROTA": ficha("EMP-ROTA", '{"plataforma": "workday",}'),
            "EMP-SINPORTAL": ficha("EMP-SINPORTAL", {"plataforma": "workday"}),
            "EMP-OTRAPLATAFORMA": ficha("EMP-OTRAPLATAFORMA", {"plataforma": "inexistente", "portal": "https://x"}),
            "EMP-SINFICHA": "",
        }
        self.escribir(modulo_04(preferencias([grupo("XA", nombres=["Ciudad A1"])])), modulo_06(fichas))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        errores = {e["empresa_id"]: e["error"] for e in json.loads(r.stdout)["empresas"]}
        self.assertEqual(list(errores), list(fichas))
        for eid, texto in (("EMP-SINBLOQUE", "```json"), ("EMP-ROTA", "JSON"), ("EMP-SINPORTAL", "portal"),
                           ("EMP-OTRAPLATAFORMA", "workday"), ("EMP-SINFICHA", "## EMP-SINFICHA")):
            with self.subTest(eid):
                self.assertIn(f"[FALLO] {eid}: ", r.stderr)
                self.assertIn(texto, errores[eid])

    def test_solo_remoto_con_sin_remotas_falla_porque_no_habria_nada_que_buscar(self):
        self.escribir(modulo_04(preferencias([], alcance="cualquiera")),
                      modulo_06({"EMP-ACME": ficha("EMP-ACME", {"plataforma": "workday", "portal": "https://x"})}))
        self.assertFallaSinBuscar(self.correr("--sin-remotas"), "--sin-remotas", "remoto")


class WorkdayFalso:
    """La API de Workday de un sitio ficticio: robots.txt, facetas y listado por facetas (POST) y detalle (GET).

    Cada anuncio es un dict con id, ubicaciones (la primera es la principal), pais y, si no es
    presencial, modalidad. Como en Workday, los valores de faceta solo existen si algún anuncio los
    tiene, y parámetros distintos se combinan con «y»."""

    PLATAFORMA = "workday"
    HOST = "https://acme.wd1.myworkdayjobs.com"
    PORTAL = HOST + "/Acme"
    API = HOST + "/wday/cxs/acme/Acme"

    def __init__(self, anuncios, faceta_de_pais=True, faceta_de_remoto=True, extra_en_total=0,
                 robots="User-agent: *\nDisallow: /refreshFacet/\n"):
        self.anuncios = {f"/job/Lugar/Puesto_{a['id']}": a for a in anuncios}
        self.faceta_de_pais, self.faceta_de_remoto = faceta_de_pais, faceta_de_remoto
        self.extra_en_total, self.robots = extra_en_total, robots
        self.listados = []

    def valores(self, a):
        """{parámetro: descriptor} de las facetas de un anuncio."""
        v = {"locations": a["ubicaciones"][0]}
        if self.faceta_de_pais:
            v["Location_Country"] = a["pais"]
        if self.faceta_de_remoto:
            v["remoteType"] = a.get("modalidad", "On-site")
        return v

    def facetas(self):
        por_parametro = {}
        for a in self.anuncios.values():
            for p, d in self.valores(a).items():
                por_parametro.setdefault(p, {})[f"{p}:{d}"] = d

        def faceta(p):
            return {"facetParameter": p, "values": [{"descriptor": d, "id": i, "count": 1}
                                                    for i, d in por_parametro.get(p, {}).items()]}

        # Como en algunos sitios, «locations» viene anidada dentro de «locationMainGroup»
        return [faceta(p) for p in ("Location_Country", "remoteType") if p in por_parametro] + [
            {"facetParameter": "locationMainGroup", "values": [faceta("locations")]}]

    def __call__(self, url, cuerpo=None, intentos=3, como_json=True, extra=None):
        if url == self.HOST + "/robots.txt":
            return self.robots
        if url == self.API + "/jobs":
            aplicadas = cuerpo["appliedFacets"]
            if cuerpo["offset"] == 0 and cuerpo["limit"] > 1:
                self.listados.append(aplicadas)
            elegidos = [(ruta, a) for ruta, a in self.anuncios.items()
                        if all(f"{p}:{self.valores(a).get(p)}" in ids for p, ids in aplicadas.items())]
            pagina = elegidos[cuerpo["offset"]:cuerpo["offset"] + cuerpo["limit"]]
            return {"total": len(elegidos) + self.extra_en_total, "facets": self.facetas(), "jobPostings": [
                {"title": f"Puesto {a['id']}", "externalPath": ruta, "locationsText": a["ubicaciones"][0]}
                for ruta, a in pagina]}
        ruta = url.removeprefix(self.API)
        if ruta in self.anuncios:
            a = self.anuncios[ruta]
            return {"jobPostingInfo": {
                "jobReqId": a["id"], "title": f"Puesto {a['id']}", "location": a["ubicaciones"][0],
                "additionalLocations": a["ubicaciones"][1:], "remoteType": a.get("modalidad"),
                "startDate": "2026-10-01", "canApply": True, "externalUrl": self.PORTAL + ruta,
                "jobDescription": "<p>Descripción ficticia.</p>"}}
        raise AssertionError(f"petición inesperada: {url}")


OCTUBRE_1 = int(dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc).timestamp())  # 00:00 UTC


class EightfoldFalso:
    """La API pcsx de Eightfold de un sitio ficticio: robots.txt, listado (GET, 10 por página) y detalle (GET).

    Cada anuncio es un dict con id, ubicaciones, normalizadas (como standardizedLocations, que terminan en el
    código del país) y, si no es presencial, modalidad (workLocationOption). Como el buscador real, location
    busca por país solo con los nombres que reconoce, y ahí también trae las remotas abiertas a otros países
    (en_todas); «Remote» trae las remotas, y cualquier otro lugar, las que lo nombran, con un radio
    (distance). El filtro de modalidad solo existe si el sitio lo tiene."""

    PLATAFORMA = "eightfold"
    HOST = "https://empleos.acme.example"
    PORTAL = HOST + "/careers?domain=acme.example"
    # La forma de los sitios reales: todo prohibido salvo el buscador y su API
    ROBOTS = "User-agent: *\nDisallow: /\nAllow: /$\nAllow: /careers\nAllow: /api/pcsx\n"

    def __init__(self, anuncios, reconocidos=None, filtro_de_modalidad=True, extra_en_total=0, robots=ROBOTS,
                 orden="timestamp", sin_pcsx=False):
        self.anuncios = {9000 + i: a for i, a in enumerate(anuncios)}
        self.reconocidos = reconocidos if reconocidos is not None else {
            n: c for c, nombres in PAISES.items() for n in nombres}
        self.filtro_de_modalidad, self.extra_en_total, self.robots = filtro_de_modalidad, extra_en_total, robots
        self.orden, self.sin_pcsx = orden, sin_pcsx
        self.listados, self.detalles = [], []

    @staticmethod
    def codigos(a):
        return {s.rsplit(",", 1)[-1].strip() for s in a.get("normalizadas", [])}

    def elegir(self, q):
        """(IDs de los anuncios que trae la búsqueda, appliedFilters)."""
        elegidos, aplicados = list(self.anuncios), {}
        lugar = q.get("location", [None])[0]
        if lugar:
            aplicados = {"includeRemote": ["0"], "includeRelocation": ["0"]}
            if lugar in self.reconocidos:
                elegidos = [i for i in elegidos if self.reconocidos[lugar] in self.codigos(self.anuncios[i])
                            or self.anuncios[i].get("en_todas")]
            elif lugar == "Remote":
                aplicados["includeRemote"] = ["1"]
                elegidos = [i for i in elegidos if self.anuncios[i].get("modalidad") == "remote_local"]
            else:
                aplicados["distance"] = ["80"]
                elegidos = [i for i in elegidos
                            if any(lugar.lower() in u.lower() for u in self.anuncios[i]["ubicaciones"])]
        for p, valores in q.items():
            if p == "filter_work_location_option" and self.filtro_de_modalidad:
                elegidos = [i for i in elegidos if self.anuncios[i].get("modalidad", "onsite") in valores]
            elif p == "filter_job_family":
                elegidos = [i for i in elegidos if self.anuncios[i].get("familia", "").lower() in valores]
            elif p == "query":
                elegidos = [i for i in elegidos if valores[0].lower() in self.anuncios[i].get("titulo", "").lower()]
            elif p != "location":
                raise AssertionError(f"parámetro inesperado: {p}")
        return elegidos, aplicados

    def filtros(self):
        familias = sorted({a["familia"] for a in self.anuncios.values() if "familia" in a})
        filtros = [{"filterName": "job_family", "options": [{"label": f, "value": f.lower()} for f in familias]}]
        if self.filtro_de_modalidad:
            filtros.append({"filterName": "work_location_option", "options": [
                {"label": "On-site", "value": "onsite"}, {"label": "Hybrid", "value": "hybrid"},
                {"label": "Virtual", "value": "remote_local"}]})
        return filtros

    def posicion(self, i):
        a = self.anuncios[i]
        return {"id": i, "displayJobId": a["id"], "name": a.get("titulo", f"Puesto {a['id']}"),
                "locations": a["ubicaciones"], "standardizedLocations": a.get("normalizadas", []),
                "postedTs": a.get("ts", OCTUBRE_1), "department": a.get("familia"),
                "workLocationOption": a.get("modalidad", "onsite"), "locationFlexibility": None,
                "positionUrl": f"/careers/job/{i}"}

    def __call__(self, url, cuerpo=None, intentos=3, como_json=True, extra=None):
        if url == self.HOST + "/robots.txt":
            return self.robots
        ruta, _, consulta = url.partition("?")
        q = urllib.parse.parse_qs(consulta)
        if q.pop("domain", None) != ["acme.example"]:
            raise AssertionError(f"petición sin el dominio de la ficha: {url}")
        if ruta == self.HOST + "/api/pcsx/search":
            if self.sin_pcsx:
                raise self.script.Fallo(f"HTTP 403 en {url}", 403)
            if q.pop("sort_by", None) != ["timestamp"]:
                raise AssertionError(f"listado sin orden estable: {url}")
            inicio = int(q.pop("start")[0])
            if inicio == 0:
                self.listados.append(q)
            elegidos, aplicados = self.elegir(q)
            return {"status": 200, "data": {
                "positions": [self.posicion(i) for i in elegidos[inicio:inicio + 10]],
                "count": len(elegidos) + self.extra_en_total, "sortBy": self.orden, "appliedFilters": aplicados,
                "filterDef": {"allFilters": self.filtros()}}}
        if ruta == self.HOST + "/api/pcsx/position_details":
            i = int(q["position_id"][0])
            self.detalles.append(i)
            a = self.anuncios[i]
            return {"status": 200, "data": {
                "id": a.get("id_en_detalle", i), "jobDescription": "<p>Descripción ficticia.</p>",
                "positionUserActions": {"applyAction": {"status": a.get("estado", "allowed")}}}}
        raise AssertionError(f"petición inesperada: {url}")


class WorkableFalso:
    """La API de Workable de una cuenta ficticia: listado v3 (POST, 10 por página, con token) y detalle v2 (GET).

    Cada anuncio es un dict con id (shortcode), lugares [(ciudad, región, país, código)] y, si no es
    presencial, modalidad (workplace); remota (el booleano remote) sigue a la modalidad salvo que se dé. Como
    la API real, location filtra por código de país, y por ciudad o región si se dan, pero también trae las
    remotas abiertas a cualquier país (en_todas)."""

    PLATAFORMA = "workable"
    SITIO = "https://apply.workable.com"
    PORTAL = SITIO + "/acme/"
    LISTADO = SITIO + "/api/v3/accounts/acme/jobs"
    DETALLE = SITIO + "/api/v2/accounts/acme/jobs/"
    ROBOTS = "User-agent: *\nContent-Signal: search=yes, ai-input=yes, ai-train=no\nDisallow:\n"

    def __init__(self, anuncios, extra_en_total=0, robots=ROBOTS):
        self.anuncios = {a["id"]: a for a in anuncios}
        self.extra_en_total, self.robots = extra_en_total, robots
        self.listados, self.detalles = [], []

    @staticmethod
    def lugares(a):
        return [{"city": c, "region": r, "country": p, "countryCode": cc} for c, r, p, cc in a["lugares"]]

    @staticmethod
    def remota(a):
        return a.get("remota", a.get("modalidad") == "remote")

    def pasa(self, a, cuerpo):
        if cuerpo["remote"] and not self.remota(a):
            return False
        if cuerpo["location"] and not a.get("en_todas") and not any(
                all(lugar.get(k) == v for k, v in filtro.items())
                for filtro in cuerpo["location"] for lugar in self.lugares(a)):
            return False
        return cuerpo["query"].lower() in f"puesto {a['id']}".lower()

    def __call__(self, url, cuerpo=None, intentos=3, como_json=True, extra=None):
        if url == self.SITIO + "/robots.txt":
            return self.robots
        if url == self.LISTADO:
            if "token" not in cuerpo:
                self.listados.append({k: v for k, v in cuerpo.items() if v})
            elegidos = [a for a in self.anuncios.values() if self.pasa(a, cuerpo)]
            inicio = int(cuerpo.get("token", 0))
            pagina = elegidos[inicio:inicio + 10]
            # Como la API real, trae nextPage con cada página llena, aunque la siguiente salga vacía
            return {"total": len(elegidos) + self.extra_en_total, "results": [
                {"shortcode": a["id"], "title": f"Puesto {a['id']}", "locations": self.lugares(a),
                 "workplace": a.get("modalidad", "on_site"), "remote": self.remota(a),
                 "published": a.get("publicada", "2026-10-01T00:00:00.000Z")} for a in pagina],
                **({"nextPage": str(inicio + 10)} if len(pagina) == 10 else {})}
        if url.startswith(self.DETALLE):
            sc = url.removeprefix(self.DETALLE)
            self.detalles.append(sc)
            a = self.anuncios[sc]
            return {"shortcode": a.get("id_en_detalle", sc), "state": a.get("estado", "published"),
                    "department": ["Ingeniería"], "description": "<p>Descripción ficticia.</p>",
                    "requirements": "<p>Requisitos ficticios.</p>", "benefits": "<p></p>"}
        raise AssertionError(f"petición inesperada: {url}")


class SmartRecruitersFalso:
    """El sitio de carreras de SmartRecruiters de una empresa ficticia: robots.txt de sus tres hosts, listado
    agrupado (GET, HTML), «Show more» de cada grupo y página de cada publicación (GET, HTML).

    Cada publicación es un dict con id, lugar (como lo escribe el listado), los microdatos del detalle
    (detalle: localidad, región y país), modalidad (workplaceType), ref (la del listado) y ref_detalle (la
    jobRefCode de la página). Como el sitio real: agrupa por ubicación o por departamento; sin filtros, da tres
    grupos por página, y con un filtro, todos en cada página; un grupo de más de 10 muestra 9 y su «Show more»;
    el texto bajo el título es el lugar si el sitio no agrupa por ubicación, y el tipo de empleo si agrupa."""

    PLATAFORMA = "smartrecruiters"
    CARRERAS = "https://careers.smartrecruiters.com"
    PUBLICACIONES = "https://jobs.smartrecruiters.com"
    WWW = "https://www.smartrecruiters.com"
    PORTAL = CARRERAS + "/Acme"
    ROBOTS_WWW = "User-agent: *\nDisallow: /search/\nDisallow: /OtraEmpresa/*\n"

    def __init__(self, publicaciones, agrupar="location", extra_en_total=0, robots_www=ROBOTS_WWW):
        self.publicaciones = {p["id"]: p for p in publicaciones}
        self.agrupar, self.extra_en_total, self.robots_www = agrupar, extra_en_total, robots_www
        self.listados, self.completados, self.detalles = [], [], []

    def pasa(self, p, q):
        modalidad = p.get("modalidad", "on_site").replace("_", "").upper()
        texto = q.get("search", [""])[0].lower()
        return (q.get("locationType", [modalidad])[0] == modalidad
                and (texto in p["lugar"].lower() or texto in f"puesto {p['id']}".lower()))

    def grupos(self, q):
        """[(nombre, valor del «Show more», publicaciones)], en orden de nombre."""
        grupos = {}
        for p in self.publicaciones.values():
            if self.pasa(p, q):
                grupos.setdefault(p["lugar"] if self.agrupar == "location" else p["departamento"], []).append(p)
        return [(nombre, f"{nombre}, XX" if self.agrupar == "location" else str(i), pubs)
                for i, (nombre, pubs) in enumerate(sorted(grupos.items()))]

    def li(self, p):
        desc = "Full-time" if self.agrupar == "location" else p["lugar"]
        return (f'<li class="opening-job job column wide-7of16 medium-1of2"><a href="{self.PUBLICACIONES}/Acme/'
                f'{p["id"]}-puesto-{p["id"]}" aria-label="Puesto {p["id"]} - {p.get("ref") or "undefined"}" '
                f'class="link--block details js-job-ad-link"><h4 class="details-title job-title">Puesto {p["id"]}</h4>'
                f'<p class="details-desc job-desc"><span class="margin--right--s">{html.escape(desc)}</span></p>'
                "</a></li>")

    def seccion(self, i, nombre, valor, pubs):
        total = len(pubs) + (self.extra_en_total if i == 0 else 0)
        mas = (f'<li class="opening-job job column js-more-container"><ul class="list--dotted"><li><a data-page="0" '
               f'data-value="{urllib.parse.quote(valor)}" data-type="{self.agrupar}" data-more="/Acme/api/more" '
               f'href="?search=&amp;page=0" class="link details-desc js-more">Show more jobs</a></li></ul></li>')
        return (f'<section data-qty="{total}" class="openings-section opening opening--grouped js-group"><header '
                f'class="opening-header"><ul class="list--dotted title-list"><li><h3 class="opening-title title">'
                f'{html.escape(nombre)}</h3></li><li><span class="title">{total} jobs</span></li></ul></header><ul '
                f'class="opening-jobs js-group-list">' + "".join(self.li(p) for p in (pubs[:9] if total > 10 else pubs))
                + (mas if total > 10 else "") + "</ul></section>")

    def detalle(self, p):
        localidad, region, pais = p["detalle"]
        ref = f"\n  'jobRefCode': '{p['ref_detalle']}'," if p.get("ref_detalle") else ""
        return (f'<html><head><link href="{self.PUBLICACIONES}/Acme/{p.get("id_en_detalle", p["id"])}-puesto" '
                f"rel=\"canonical\"><script>gtmDataLayer.push({{\n  'postingId': '{p['id']}',{ref}\n}});</script>"
                "</head>"
                f'<body><span itemprop="addressLocality" content="{localidad}"></span><span itemprop="addressRegion" '
                f'content="{region}"></span><span itemprop="addressCountry" content="{pais}"></span><meta '
                f'itemprop="datePosted" content="{p.get("publicada", "2026-10-01T00:00:00.000Z")}"><spl-job-location '
                f'formattedAddress="{localidad}, {pais}" workplaceDescription="" '
                f'workplaceType="{p.get("modalidad", "on_site")}"></spl-job-location>'
                f'<li class="job-detail">Department: Ingeniería</li><section class="job-section" '
                f'id="st-companyDescription"><p>Empresa ficticia.</p></section><section class="job-section" '
                f'id="st-jobDescription"><p>Descripción ficticia.</p></section><section class="job-section" '
                f'id="st-qualifications"><p>Requisitos ficticios.</p></section>'
                + ('<button data-sr-track="apply">I\'m interested</button>' if p.get("abierta", True) else "")
                + "</body></html>")

    def __call__(self, url, cuerpo=None, intentos=3, como_json=True, extra=None):
        if url == self.CARRERAS + "/robots.txt":
            # Como el real: redirige a una página que no es un robots.txt
            return "<!DOCTYPE html>\n<html><head><title>Job Search</title></head><body>Busca empleo</body></html>"
        if url == self.PUBLICACIONES + "/robots.txt":
            raise self.script.Fallo(f"HTTP 404 en {url}", 404)
        if url == self.WWW + "/robots.txt":
            return self.robots_www
        ruta, _, consulta = url.partition("?")
        q = urllib.parse.parse_qs(consulta)
        pagina = int(q.pop("page", ["0"])[0])
        if ruta == self.CARRERAS + "/Acme/api/groups":
            if pagina == 0:
                self.listados.append(q)
            grupos = list(enumerate(self.grupos(q)))
            # Sin filtros, el sitio reparte los grupos en páginas; con un filtro, los repite todos en cada página
            return "".join(self.seccion(i, *g) for i, g in (grupos if q else grupos[3 * pagina:3 * pagina + 3]))
        if ruta == self.CARRERAS + "/Acme/api/more":
            tipo, valor = q.pop("type")[0], q.pop("value")[0]
            if pagina == 0:
                self.completados.append(valor)
            pubs = next(g[2] for g in self.grupos(q) if g[1] == valor and tipo == self.agrupar)
            # La página 0 repite las 9 que ya muestra el grupo; las siguientes traen 10
            inicio = 0 if pagina == 0 else 9 + 10 * (pagina - 1)
            return "".join(self.li(p) for p in pubs[inicio:9 if pagina == 0 else inicio + 10])
        if ruta.startswith(self.PUBLICACIONES + "/Acme/"):
            pid = ruta.rsplit("/", 1)[1].split("-")[0]
            self.detalles.append(pid)
            return self.detalle(self.publicaciones[pid])
        raise AssertionError(f"petición inesperada: {url}")


class OracleFalso:
    """La API REST de Oracle Recruiting Cloud de un sitio ficticio: robots.txt, listado con el finder findReqs (GET,
    25 por página) y detalle con ById (GET).

    Cada requisición es un dict con id, lugares [(nombre, código)] (el primero es el principal), modalidad
    (WorkplaceType; Onsite si no se da) y familia. Como la API real, location filtra por país solo con los nombres
    que reconoce, y con otro no filtra; un país cuenta también por sus ubicaciones secundarias. Las facetas solo
    traen los valores que tiene alguna requisición del resultado. extra_en_total: requisiciones que el total y la
    faceta de ubicaciones cuentan, pero que el listado no trae."""

    PLATAFORMA = "oraclerecruitingcloud"
    HOST = "https://acme.fa.xx1.oraclecloud.com"
    PORTAL = HOST + "/hcmUI/CandidateExperience/en/sites/CX_1"
    API = HOST + "/hcmRestApi/resources/latest"
    MODALIDADES = {"Onsite": "ORA_ON_SITE", "Hybrid": "ORA_HYBRID", "Remote": "ORA_REMOTE"}

    def __init__(self, requisiciones, reconocidos=None, extra_en_total=0, robots=None):
        self.requisiciones = {r["id"]: r for r in requisiciones}
        self.reconocidos = reconocidos if reconocidos is not None else {PAISES[c][1]: c for c in PAISES}
        self.extra_en_total, self.robots = extra_en_total, robots
        self.listados, self.detalles = [], []

    @staticmethod
    def finder(url):
        """{parámetro: valor} del finder de la URL, con su nombre en «finder»."""
        nombre, _, parametros = url.split("finder=", 1)[1].partition(";")
        return {"finder": nombre, **{k: urllib.parse.unquote(v) for k, _, v in
                                     (p.partition("=") for p in parametros.split(","))}}

    def elegir(self, f):
        elegidas = list(self.requisiciones.values())
        codigo = self.reconocidos.get(f.get("location"))
        if codigo:
            elegidas = [r for r in elegidas if codigo in {c for _, c in r["lugares"]}]
        if "selectedWorkplaceTypesFacet" in f:
            pedidas = f["selectedWorkplaceTypesFacet"].split(";")
            elegidas = [r for r in elegidas if self.MODALIDADES[r.get("modalidad", "Onsite")] in pedidas]
        if "selectedCategoriesFacet" in f:
            elegidas = [r for r in elegidas if f"CAT-{r.get('familia')}" in f["selectedCategoriesFacet"].split(";")]
        if "keyword" in f:
            elegidas = [r for r in elegidas if f["keyword"].lower() in f"puesto {r['id']}".lower()]
        return elegidas

    def facetas(self, elegidas):
        nombres = {c: n for n, c in self.reconocidos.items()}

        def cuenta(valores, extra=0):
            return [{"Id": i, "Name": n, "TotalCount": valores.count((i, n)) + extra}
                    for i, n in dict.fromkeys(valores)]

        return {"locationsFacet": cuenta([(f"LOC-{c}", nombres.get(c, c)) for r in elegidas for c in
                                          dict.fromkeys(c for _, c in r["lugares"])], self.extra_en_total),
                "workplaceTypesFacet": cuenta([(self.MODALIDADES[m], m) for m in
                                               (r.get("modalidad", "Onsite") for r in elegidas)]),
                "categoriesFacet": cuenta([(f"CAT-{r['familia']}", r["familia"]) for r in elegidas if "familia" in r])}

    def requisicion(self, r):
        (principal, codigo), secundarias = r["lugares"][0], r["lugares"][1:]
        return {"Id": r["id"], "Title": f"Puesto {r['id']}", "PostedDate": "2026-10-01", "PrimaryLocation": principal,
                "PrimaryLocationCountry": codigo, "WorkplaceType": r.get("modalidad", "Onsite"),
                "WorkplaceTypeCode": self.MODALIDADES[r.get("modalidad", "Onsite")], "JobFunction": r.get("familia"),
                "secondaryLocations": [{"Name": n, "CountryCode": c} for n, c in secundarias]}

    def __call__(self, url, cuerpo=None, intentos=3, como_json=True, extra=None):
        if url == self.HOST + "/robots.txt":
            if self.robots is None:
                raise self.script.Fallo(f"HTTP 404 en {url}", 404)
            return self.robots
        if url.startswith(self.API + "/recruitingCEJobRequisitions?"):
            f = self.finder(url)
            if (f["finder"], f["siteNumber"], f["sortBy"]) != ("findReqs", "CX_1", "POSTING_DATES_DESC"):
                raise AssertionError(f"listado sin el sitio o el orden de la ficha: {url}")
            inicio, limite = int(f.pop("offset")), int(f["limit"])
            if inicio == 0:
                self.listados.append({k: v for k, v in f.items()
                                      if k not in ("finder", "siteNumber", "sortBy", "limit", "facetsList")})
            elegidas = self.elegir(f)
            return {"items": [{"TotalJobsCount": len(elegidas) + self.extra_en_total,
                               "requisitionList": [self.requisicion(r) for r in elegidas[inicio:inicio + limite]],
                               **self.facetas(elegidas)}]}
        if url.startswith(self.API + "/recruitingCEJobRequisitionDetails?"):
            f = self.finder(url)
            rid = f["Id"].strip('"')
            self.detalles.append(rid)
            r = self.requisiciones[rid]
            return {"items": [{"Id": r.get("id_en_detalle", rid), "Title": f"Puesto {rid}",
                               "ExternalPostedStartDate": r.get("publicada", "2026-10-01T00:00:00+00:00"),
                               "ExternalPostedEndDate": r.get("cierre"), "WorkplaceType": r.get("modalidad", "Onsite"),
                               "JobFunction": r.get("familia"),
                               "ExternalDescriptionStr": "<p>Descripción ficticia.</p>",
                               "ExternalResponsibilitiesStr": "<ul><li>Responsabilidad ficticia.</li></ul>",
                               "ExternalQualificationsStr": None}]}
        raise AssertionError(f"petición inesperada: {url}")


CAMPOS_DE_VACANTES_Y_OBSERVACIONES = {"empresa_id", "job_id", "titulo", "url_oficial", "ubicacion_literal",
                                      "modalidad_literal", "region_relacionada", "fecha_publicacion",
                                      "estado_vigencia", "motivo", "url_fuente"}


class ConPortalFalso(CopiaFicticia):
    def buscar(self, bloque_04, portal, *argumentos, consulta=None, codigo_esperado=0, red=None, nube=False):
        """Corre main() del script de la copia con el portal falso en lugar de la red. Con red, el portal solo da la
        configuración: la red falsa reemplaza urllib.request.urlopen, las esperas entre intentos se anotan en
        self.esperas sin esperar, y se ejercita el pedir() real. nube: corre como Code en la nube
        (CLAUDE_CODE_REMOTE=true); si no, sin la variable."""
        configuracion = {"plataforma": portal.PLATAFORMA, "portal": portal.PORTAL, "consulta": consulta}
        self.escribir(modulo_04(bloque_04), modulo_06({"EMP-ACME": ficha("EMP-ACME", configuracion)}))
        especificacion = importlib.util.spec_from_file_location("buscar_copia", self.dir / "herramientas" / "buscar.py")
        script = importlib.util.module_from_spec(especificacion)
        especificacion.loader.exec_module(script)
        self.esperas = []
        if red is None:
            script.pedir = portal
            portal.script = script  # para que el portal falso responda con los errores del script
            sustituir = contextlib.nullcontext()
        else:
            sustituir = contextlib.ExitStack()
            sustituir.enter_context(mock.patch.object(script.urllib.request, "urlopen", red))
            sustituir.enter_context(mock.patch.object(script.time, "sleep", self.esperas.append))
        entorno = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_REMOTE"}
        if nube:
            entorno["CLAUDE_CODE_REMOTE"] = "true"
        salida, errores, codigo = io.StringIO(), io.StringIO(), 0
        with mock.patch.object(sys, "argv", ["buscar.py", *argumentos]), sustituir, \
                mock.patch.dict(os.environ, entorno, clear=True), \
                contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            try:
                script.main()
            except SystemExit as e:
                codigo = e.code
        self.assertEqual(codigo, codigo_esperado, errores.getvalue())
        self.assertNotIn("Traceback", errores.getvalue())
        return json.loads(salida.getvalue())["empresas"][0], errores.getvalue()

    def regiones(self, r, lista="vacantes"):
        return {v["job_id"]: v["region_relacionada"] for v in r[lista]}

    def listados(self, portal):
        """Las facetas de cada listado que pidió el script, con los IDs ordenados."""
        return [{p: sorted(ids) for p, ids in aplicadas.items()} for aplicadas in portal.listados]


class ClasificacionDeUbicaciones(ConPortalFalso):
    def test_varias_ciudades_de_una_zona_metropolitana(self):
        bloque = preferencias([grupo("XA", ["Estado A", "Edo. A"], ["Ciudad A", "Municipio A2", "Municipio A3"])])
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A, Estado A, País A"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Municipio A3"]},
            {"id": "R-3", "pais": "País A", "ubicaciones": ["MUNICIPIO A2, estado a"]},
            {"id": "R-4", "pais": "País A", "ubicaciones": ["Municipio A9, Edo. A, País A"]},
            {"id": "R-5", "pais": "País A", "ubicaciones": ["Ciudad A, Estado A, País A", "Ciudad B1, País B"]},
            {"id": "R-6", "pais": "País A", "ubicaciones": ["Ciudad Alta, Estado A5, País A"]},
            {"id": "R-7", "pais": "País B", "ubicaciones": ["Ciudad B1, País B"]},
        ])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(portal.listados, [{"Location_Country": ["Location_Country:País A"]}])
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (6, 6, True))
        self.assertEqual(self.regiones(r), {"R-1": "Dentro", "R-2": "Dentro", "R-3": "Dentro",
                                            "R-4": "Indeterminada", "R-5": "Incluye"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad Alta, Estado A5, País A"])
        revisar = {v["job_id"]: v["ubicaciones_por_revisar"] for v in r["vacantes"]}
        self.assertEqual(revisar["R-4"], ["Municipio A9, Edo. A, País A"])
        for v in r["vacantes"]:
            self.assertLessEqual(CAMPOS_DE_VACANTES_Y_OBSERVACIONES, set(v))
            self.assertEqual(v["estado_vigencia"], "Confirmada abierta")
        self.assertIn("[OK] EMP-ACME: 6/6 únicos; 4 en la región", errores)
        self.assertIn("revisar ubicación: R-4 Municipio A9, Edo. A, País A", errores)

    def test_una_ubicacion_que_solo_nombra_el_pais_queda_por_revisar(self):
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"]), grupo("XB", divisiones=["Provincia B1"])])
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["País A"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Ciudad A1, País A", "Country A"]},
            {"id": "R-3", "pais": "País A", "ubicaciones": ["Multiple Locations"]},
            {"id": "R-4", "pais": "País B", "ubicaciones": ["Country B"]},
            {"id": "R-5", "pais": "País B", "ubicaciones": ["Ciudad B9, Provincia B1, País B"]},
            {"id": "R-6", "pais": "País B", "ubicaciones": ["Ciudad B9, Provincia B2, País B"]},
        ])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(self.regiones(r), {"R-1": "Indeterminada", "R-2": "Incluye", "R-3": "Indeterminada",
                                            "R-4": "Indeterminada", "R-5": "Dentro"})
        revisar = {v["job_id"]: v["ubicaciones_por_revisar"] for v in r["vacantes"]}
        self.assertEqual(revisar, {"R-1": ["País A"], "R-2": ["Country A"], "R-3": ["Multiple Locations"],
                                   "R-4": ["Country B"], "R-5": []})
        self.assertEqual(r["fuera_de_region"], ["Ciudad B9, Provincia B2, País B"])
        for job_id in ("R-1", "R-2", "R-3", "R-4"):
            self.assertIn(f"revisar ubicación: {job_id} ", errores)
        self.assertNotIn("revisar ubicación: R-5", errores)

    def test_varios_paises_con_remoto_desde_algunos(self):
        bloque = preferencias([grupo("XA"), grupo("XB", divisiones=["Provincia B1"])],
                              alcance="paises", paises_remoto=["XA", "XC"])
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A7, País A"]},
            {"id": "R-2", "pais": "País B", "ubicaciones": ["Ciudad B9, Provincia B1, País B"]},
            {"id": "R-3", "pais": "País B", "ubicaciones": ["Ciudad B9, Provincia B2, País B"]},
            {"id": "R-4", "pais": "País C", "ubicaciones": ["Ciudad C1, País C"], "modalidad": "Remote"},
            {"id": "R-5", "pais": "País C", "ubicaciones": ["Ciudad C2, País C"]},
            {"id": "R-6", "pais": "País D", "ubicaciones": ["Ciudad D1, País D"], "modalidad": "Remote"},
            {"id": "R-7", "pais": "País A", "ubicaciones": ["Ciudad A8, País A"], "modalidad": "Remote"},
            {"id": "R-8", "pais": "País B", "ubicaciones": ["Ciudad B8, Provincia B3, País B"], "modalidad": "Remote"},
            # Otro lugar que contiene el nombre del país completo
            {"id": "R-9", "pais": "País A", "ubicaciones": ["Nuevo País A - Ciudad N1"]},
        ])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(self.listados(portal), [
            {"Location_Country": ["Location_Country:País A", "Location_Country:País B"]},
            {"remoteType": ["remoteType:Remote"], "Location_Country": ["Location_Country:País A",
                                                                       "Location_Country:País C"]},
        ])
        self.assertEqual(self.regiones(r), {"R-1": "Dentro", "R-2": "Dentro", "R-7": "Dentro"})
        self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), {"R-4": "Fuera"})
        # R-8 es remota, pero de un país que 04 no acepta para el remoto
        self.assertEqual(sorted(r["fuera_de_region"]), ["Ciudad B8, Provincia B3, País B",
                                                        "Ciudad B9, Provincia B2, País B", "Nuevo País A - Ciudad N1"])
        # R-7 sale en los dos listados y cuenta una vez
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (7, 7, True))
        self.assertIn("remoteType", r["remotas_revision"])
        self.assertIn("[OK] EMP-ACME: 7/7 únicos; 3 en la región; remotas fuera de la región: 1", errores)

    def test_solo_remoto_desde_cualquier_pais_lista_solo_las_remotas(self):
        anuncios = [
            {"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A1, País A"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Remote - Ciudad A2, País A"], "modalidad": "Remote"},
            {"id": "R-3", "pais": "País D", "ubicaciones": ["Remote"], "modalidad": "Remote"},
            {"id": "R-4", "pais": "País D", "ubicaciones": ["Ciudad D1, País D"], "modalidad": "Hybrid"},
        ]
        filtros = {
            "faceta de remoto": (True, [{"remoteType": ["remoteType:Remote"]}]),
            # Sin faceta de remoto, el portal marca las remotas en sus ubicaciones «Remote …»
            "ubicaciones «Remote»": (False, [{"locations": ["locations:Remote",
                                                            "locations:Remote - Ciudad A2, País A"]}]),
        }
        for caso, (faceta_de_remoto, esperados) in filtros.items():
            with self.subTest(caso):
                portal = WorkdayFalso(anuncios, faceta_de_remoto=faceta_de_remoto)
                r, errores = self.buscar(preferencias([], alcance="cualquiera"), portal)
                self.assertEqual(self.listados(portal), esperados)
                self.assertEqual(self.regiones(r), {"R-3": "Indeterminada"})
                self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), {"R-2": "Fuera"})
                self.assertIn("[OK] EMP-ACME: 2/2 únicos; 0 en la región; remotas fuera de la región: 1", errores)

    def test_una_ciudad_homonima_en_otro_pais_de_04_queda_fuera(self):
        bloque = preferencias([grupo("XA", ["Provincia A1"], ["Ciudad A1"]), grupo("XB", ["Provincia B1"])])
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A1, País A"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Ciudad A1, País C"]},
            {"id": "R-3", "pais": "País B", "ubicaciones": ["Ciudad B1, Provincia A1, País B"]},
            {"id": "R-4", "pais": "País B", "ubicaciones": ["Ciudad B2, Provincia B1"]},
        ])
        r, _ = self.buscar(bloque, portal)
        self.assertEqual(self.regiones(r), {"R-1": "Dentro", "R-4": "Dentro"})
        self.assertEqual(sorted(r["fuera_de_region"]), ["Ciudad A1, País C", "Ciudad B1, Provincia A1, País B"])

    def test_avisa_por_cada_pais_de_la_region_que_el_portal_no_ofrece(self):
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"]), grupo("XB", nombres=["Ciudad B1"])])
        portal = WorkdayFalso([{"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A1, País A"]}])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(self.listados(portal), [{"Location_Country": ["Location_Country:País A"]}])
        self.assertEqual(self.regiones(r), {"R-1": "Dentro"})
        self.assertIn("revisar: el portal no ofrece XB", errores)
        self.assertNotIn("no ofrece XA", errores)

    def test_sin_faceta_de_pais_se_lista_por_las_ubicaciones_que_nombran_el_pais_como_una_parte(self):
        # Los portales escriben «País - Ciudad», «Ciudad, País (Edificio)» o «Remote - País»; «Nuevo País A»
        # es otro lugar aunque contenga «País A».
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["País A - Ciudad A1"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Ciudad A9, País A (Edificio 1)"]},
            {"id": "R-3", "pais": "País A", "ubicaciones": ["País A - Remote"], "modalidad": "Remote"},
            {"id": "R-4", "pais": "País A", "ubicaciones": ["Remote - País A"], "modalidad": "Remote"},
            {"id": "R-5", "pais": "País N", "ubicaciones": ["Nuevo País A - Remote"], "modalidad": "Remote"},
            {"id": "R-6", "pais": "País N", "ubicaciones": ["Nuevo País A - Ciudad N1"]},
        ], faceta_de_pais=False, faceta_de_remoto=False)
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"])], alcance="paises", paises_remoto=["XA"])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(self.listados(portal), [
            {"locations": ["locations:Ciudad A9, País A (Edificio 1)", "locations:País A - Ciudad A1",
                           "locations:País A - Remote", "locations:Remote - País A"]},
            {"locations": ["locations:País A - Remote", "locations:Remote - País A"]},
        ])
        self.assertEqual(self.regiones(r), {"R-1": "Dentro", "R-3": "Indeterminada", "R-4": "Indeterminada"})


class ConsultaDeLaFicha(ConPortalFalso):
    def test_la_consulta_de_la_ficha_reemplaza_el_listado_por_paises(self):
        bloque = preferencias([grupo("XA", nombres=["Ciudad A"])])
        portal = WorkdayFalso([
            {"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A, País A"]},
            {"id": "R-2", "pais": "País A", "ubicaciones": ["Ciudad A9, País A"]},
        ])
        consulta = {"facetas": {"locations": ["ciudad a, pais a", "Ciudad Inexistente"]}, "texto": ""}
        r, errores = self.buscar(bloque, portal, consulta=consulta)
        self.assertEqual(portal.listados, [{"locations": ["locations:Ciudad A, País A"]}])
        self.assertEqual(self.regiones(r), {"R-1": "Dentro"})
        self.assertIn("revisar: la faceta locations no ofrece «Ciudad Inexistente»", errores)

    def test_una_consulta_sin_valores_que_el_portal_ofrezca_no_lista_nada(self):
        portal = WorkdayFalso([{"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A, País A"]}])
        consulta = {"facetas": {"locations": ["Ciudad Inexistente"]}}
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A"])]), portal, consulta=consulta)
        self.assertEqual(portal.listados, [])
        self.assertEqual((r["total_reportado"], r["vacantes"]), (0, []))
        self.assertIn("revisar: la faceta locations no ofrece «Ciudad Inexistente»", errores)

    def test_una_consulta_mal_formada_sale_como_fallo(self):
        portal = WorkdayFalso([{"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A, País A"]}])
        for consulta in ({}, {"facetas": {"locations": "Ciudad A"}}, {"texto": 5}, {"filtro": "x"}):
            with self.subTest(consulta=consulta):
                r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A"])]), portal,
                                         consulta=consulta, codigo_esperado=1)
                self.assertIn("consulta", r["error"])
                self.assertIn("06/CAT-PLATAFORMAS", r["error"])
        self.assertEqual(portal.listados, [])


class ComprobacionesDeWorkday(ConPortalFalso):
    EN_XA = [{"id": "R-1", "pais": "País A", "ubicaciones": ["Ciudad A, País A"]}]

    def test_si_los_ids_unicos_no_igualan_el_total_la_busqueda_queda_incompleta(self):
        portal = WorkdayFalso(self.EN_XA, extra_en_total=1)
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A"])]), portal)
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (2, 1, False))
        self.assertIn("[INCOMPLETA] EMP-ACME: 1/2 únicos", errores)

    def test_si_robots_txt_prohibe_la_api_no_se_usa(self):
        portal = WorkdayFalso(self.EN_XA, robots="User-agent: *\nDisallow: /wday/\n")
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A"])]), portal, codigo_esperado=1)
        self.assertIn("[FALLO] EMP-ACME: ", errores)
        self.assertIn("robots.txt", r["error"])
        self.assertEqual(portal.listados, [])

    def test_un_portal_que_no_es_de_workday_sale_como_fallo(self):
        self.escribir(modulo_04(preferencias([grupo("XA", nombres=["Ciudad A"])])), modulo_06({"EMP-ACME": ficha(
            "EMP-ACME", {"plataforma": "workday", "portal": "https://empleos.example.com/Acme", "consulta": None})}))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("[FALLO] EMP-ACME: ", r.stderr)
        self.assertIn("myworkdayjobs.com", r.stderr)


class RedSinSalida:
    """La red de un entorno que no deja salir la petición: urlopen lanza el URLError que da urllib ante ese error de
    conexión. Anota cada URL que se pidió."""

    def __init__(self, error):
        self.error, self.pedidas = error, []

    def __call__(self, req, timeout=None):
        self.pedidas.append(req.full_url)
        raise urllib.error.URLError(self.error)


class HostBloqueadoPorLaLista(ConPortalFalso):
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A"])])

    def test_el_proxy_de_la_nube_nombra_el_host_y_donde_agregarlo_tras_un_solo_intento(self):
        # El proxy de Code en la nube responde 403 al CONNECT de un host fuera de la lista de dominios
        red = RedSinSalida(OSError("Tunnel connection failed: 403 Forbidden"))
        r, errores = self.buscar(self.BLOQUE, WorkdayFalso([]), codigo_esperado=1, red=red)
        self.assertEqual(red.pedidas, [WorkdayFalso.HOST + "/robots.txt"])
        fallo = next(linea for linea in errores.splitlines() if linea.startswith("[FALLO] EMP-ACME: "))
        self.assertTrue(fallo.endswith(": acme.wd1.myworkdayjobs.com"), fallo)
        self.assertIn("lista de dominios del entorno de la nube", fallo)
        self.assertIn("claude.ai/code (entorno → red → Custom)", fallo)
        self.assertNotIn("no se pudo leer", r["error"])

    def test_sin_red_por_otra_causa_conserva_el_mensaje_del_robots_txt(self):
        red = RedSinSalida(OSError("[Errno -3] Temporary failure in name resolution"))
        r, _ = self.buscar(self.BLOQUE, WorkdayFalso([]), codigo_esperado=1, red=red)
        self.assertEqual(len(red.pedidas), 3)
        self.assertIn(f"no se pudo leer {WorkdayFalso.HOST}/robots.txt", r["error"])
        self.assertNotIn("lista de dominios", r["error"])


class RedConLimite:
    """La red de un sitio que responde HTTP 429 a todo, con ese cuerpo y Retry-After. Anota cada URL que se
    pidió."""

    def __init__(self, cuerpo, retry_after="7"):
        self.cuerpo, self.retry_after, self.pedidas = cuerpo, retry_after, []

    def __call__(self, req, timeout=None):
        self.pedidas.append(req.full_url)
        raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {"Retry-After": self.retry_after},
                                     io.BytesIO(self.cuerpo))


class WorkableEnLaNube(ConPortalFalso):
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A"])])
    # Lo que responde Cloudflare cuando Workable bloquea las IP de la nube
    BLOQUEO = b"error code: 1015"

    def test_en_la_nube_el_bloqueo_de_cloudflare_manda_a_code_local_tras_un_solo_intento(self):
        red = RedConLimite(self.BLOQUEO)
        r, errores = self.buscar(self.BLOQUE, WorkableFalso([]), codigo_esperado=1, red=red, nube=True)
        self.assertEqual(red.pedidas, [WorkableFalso.SITIO + "/robots.txt"])
        self.assertEqual(self.esperas, [])
        fallo = next(linea for linea in errores.splitlines() if linea.startswith("[FALLO] EMP-ACME: "))
        self.assertIn("apply.workable.com bloquea las IP de Code en la nube", fallo)
        self.assertIn("busca esta empresa en Code local", fallo)
        self.assertNotIn("no se pudo leer", r["error"])

    def test_en_code_local_el_mismo_429_se_reintenta_con_retry_after(self):
        red = RedConLimite(self.BLOQUEO)
        r, _ = self.buscar(self.BLOQUE, WorkableFalso([]), codigo_esperado=1, red=red)
        self.assertEqual(len(red.pedidas), 3)
        self.assertEqual(self.esperas, [7, 7])
        self.assertIn(f"no se pudo leer {WorkableFalso.SITIO}/robots.txt (HTTP 429", r["error"])
        self.assertNotIn("Code local", r["error"])

    def test_en_la_nube_un_429_con_otro_cuerpo_se_reintenta_con_retry_after(self):
        red = RedConLimite(b"Too Many Requests")
        r, _ = self.buscar(self.BLOQUE, WorkableFalso([]), codigo_esperado=1, red=red, nube=True)
        self.assertEqual(len(red.pedidas), 3)
        self.assertEqual(self.esperas, [7, 7])
        self.assertNotIn("Code local", r["error"])


class AdaptadorDeEightfold(ConPortalFalso):
    def test_lista_cada_pais_de_la_region_con_el_primer_nombre_que_el_buscador_reconoce(self):
        bloque = preferencias([grupo("XA", ["Estado A"], ["Ciudad A1"]), grupo("XB", nombres=["Ciudad B1"])],
                              zona_horaria="Etc/GMT+12")
        portal = EightfoldFalso([
            {"id": "E-1", "ubicaciones": ["Ciudad A1, Estado A, País A"], "normalizadas": ["Ciudad A1, EA, XA"],
             "estado": "log_in"},
            # Publicada el 2 de octubre a las 03:00 UTC: en UTC−12 todavía es el 1
            {"id": "E-2", "ubicaciones": ["Ciudad A9, Estado A, País A"], "normalizadas": ["Ciudad A9, EA, XA"],
             "ts": OCTUBRE_1 + 27 * 3600},
            {"id": "E-3", "ubicaciones": ["Ciudad A7, Estado A7, País A"], "normalizadas": ["Ciudad A7, E7, XA"]},
            {"id": "E-4", "ubicaciones": ["Ciudad B1, País B"], "normalizadas": ["Ciudad B1, PB, XB"],
             "estado": "closed"},
            {"id": "E-5", "ubicaciones": ["Ciudad C1, País C"], "normalizadas": ["Ciudad C1, PC, XC"]},
        ], reconocidos={"Country A": "XA", "País B": "XB"})
        r, errores = self.buscar(bloque, portal)
        # La primera página sin filtros da los filtros del buscador; «País A» no es un país para el buscador
        self.assertEqual(portal.listados, [{}, {"location": ["País A"]}, {"location": ["Country A"]},
                                           {"location": ["País B"]}])
        self.assertEqual(self.regiones(r), {"E-1": "Dentro", "E-2": "Indeterminada", "E-4": "Dentro"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad A7, Estado A7, País A"])
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (4, 4, True))
        # Solo se lee el detalle de las que se entregan
        self.assertEqual(sorted(portal.detalles), [9000, 9001, 9003])
        vacantes = {v["job_id"]: v for v in r["vacantes"]}
        for v in vacantes.values():
            self.assertLessEqual(CAMPOS_DE_VACANTES_Y_OBSERVACIONES, set(v))
            self.assertEqual(v["descripcion"], "Descripción ficticia.")
        # 07/BUS-FECHAS: a las 00:00 UTC queda la fecha UTC; con hora real, la de la zona de 04
        self.assertEqual({j: v["fecha_publicacion"] for j, v in vacantes.items()},
                         {"E-1": "2026-10-01", "E-2": "2026-10-01", "E-4": "2026-10-01"})
        self.assertEqual({j: v["estado_vigencia"] for j, v in vacantes.items()},
                         {"E-1": "Confirmada abierta", "E-2": "Confirmada abierta", "E-4": "Revisar"})
        self.assertEqual(vacantes["E-1"]["url_oficial"], EightfoldFalso.HOST + "/careers/job/9000")
        self.assertIn("[OK] EMP-ACME: 4/4 únicos; 2 en la región", errores)
        self.assertIn("revisar vigencia: E-4 ", errores)

    def test_avisa_si_el_buscador_no_reconoce_ningun_nombre_de_un_pais(self):
        portal = EightfoldFalso([{"id": "E-1", "ubicaciones": ["Ciudad A1, País A"], "normalizadas": ["XA"]}],
                                reconocidos={})
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal)
        self.assertEqual(portal.listados, [{}, {"location": ["País A"]}, {"location": ["Country A"]}])
        self.assertEqual((r["total_reportado"], r["vacantes"]), (0, []))
        self.assertIn("revisar: el buscador no reconoce como país ningún nombre de XA", errores)

    def test_las_remotas_salen_del_filtro_de_modalidad_acotado_a_los_paises_del_remoto(self):
        bloque = preferencias([grupo("XB", nombres=["Ciudad B1"])], alcance="paises", paises_remoto=["XA", "XC"])
        portal = EightfoldFalso([
            {"id": "E-1", "ubicaciones": ["Ciudad B1, País B"], "normalizadas": ["Ciudad B1, PB, XB"]},
            {"id": "E-2", "ubicaciones": ["País A (Virtual)"], "normalizadas": ["XA"], "modalidad": "remote_local"},
            {"id": "E-3", "ubicaciones": ["Ciudad C1, País C"], "normalizadas": ["Ciudad C1, PC, XC"],
             "modalidad": "remote_local"},
            {"id": "E-4", "ubicaciones": ["Ciudad D1, País D"], "normalizadas": ["Ciudad D1, PD, XD"],
             "modalidad": "remote_local"},
            {"id": "E-5", "ubicaciones": ["Ciudad B2, País B"], "normalizadas": ["Ciudad B2, PB, XB"],
             "modalidad": "remote_local"},
            {"id": "E-6", "ubicaciones": ["Ciudad C2, País C"], "normalizadas": ["Ciudad C2, PC, XC"],
             "modalidad": "hybrid"},
        ])
        r, errores = self.buscar(bloque, portal)
        remoto = {"filter_work_location_option": ["remote_local"]}
        self.assertEqual(portal.listados, [{}, {"location": ["País B"]}, {"location": ["País A"], **remoto},
                                           {"location": ["País C"], **remoto}])
        self.assertEqual(self.regiones(r), {"E-1": "Dentro"})
        self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), {"E-2": "Fuera", "E-3": "Fuera"})
        # E-5 es remota, pero de un país que 04 no acepta para el remoto
        self.assertEqual(r["fuera_de_region"], ["Ciudad B2, País B"])
        self.assertIn("work_location_option", r["remotas_revision"])
        self.assertIn("[OK] EMP-ACME: 4/4 únicos; 1 en la región; remotas fuera de la región: 2", errores)

    def test_con_el_filtro_de_modalidad_por_pais_el_alcance_se_decide_por_codigo_de_pais(self):
        portal = EightfoldFalso([
            {"id": "E-1", "ubicaciones": ["Ciudad A1, País A"], "normalizadas": ["Ciudad A1, PA, XA"],
             "modalidad": "remote_local"},
            # Una remota de otro país que la búsqueda por país también trae
            {"id": "E-2", "ubicaciones": ["Ciudad D1, País D"], "normalizadas": ["Ciudad D1, PD, XD"],
             "modalidad": "remote_local", "en_todas": True},
        ])
        r, _ = self.buscar(preferencias([], alcance="paises", paises_remoto=["XA"]), portal)
        self.assertEqual(portal.listados, [{}, {"location": ["País A"],
                                                "filter_work_location_option": ["remote_local"]}])
        self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), {"E-1": "Fuera"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad D1, País D"])

    def test_sin_filtro_de_modalidad_las_remotas_salen_de_la_busqueda_remote_con_su_alcance_por_codigo(self):
        anuncios = [
            {"id": "E-1", "ubicaciones": ["Remote", "Ciudad A1, País A"],
             "normalizadas": ["Remote", "Ciudad A1, PA, XA"], "modalidad": "remote_local"},
            {"id": "E-2", "ubicaciones": ["Ciudad A2, País A"], "normalizadas": ["PA,XA"], "modalidad": "remote_local"},
            # Un país que 04 no nombra: por el nombre, podría estar en el alcance; por el código, no
            {"id": "E-3", "ubicaciones": ["Ciudad D1, País D"], "normalizadas": ["Ciudad D1, PD, XD"],
             "modalidad": "remote_local"},
            {"id": "E-4", "ubicaciones": ["Ciudad A3, País A"], "normalizadas": ["Ciudad A3, PA, XA"]},
        ]
        casos = {"paises": (["XA"], {"E-2": "Fuera"}, ["Ciudad D1, País D"]),
                 "cualquiera": ([], {"E-2": "Fuera", "E-3": "Fuera"}, [])}
        for alcance, (paises_remoto, remotas, fuera) in casos.items():
            with self.subTest(alcance):
                portal = EightfoldFalso(anuncios, filtro_de_modalidad=False)
                r, _ = self.buscar(preferencias([], alcance=alcance, paises_remoto=paises_remoto), portal)
                self.assertEqual(portal.listados, [{}, {"location": ["Remote"]}])
                self.assertEqual(self.regiones(r), {"E-1": "Indeterminada"})
                self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), remotas)
                self.assertEqual(r["fuera_de_region"], fuera)
                self.assertIn("«Remote»", r["remotas_revision"])

    def test_la_consulta_de_la_ficha_reemplaza_el_listado_por_paises(self):
        portal = EightfoldFalso([
            {"id": "E-1", "ubicaciones": ["Ciudad A1, País A"], "familia": "Ingeniería", "titulo": "Analista de datos"},
            {"id": "E-2", "ubicaciones": ["Ciudad A1, País A"], "familia": "Finanzas", "titulo": "Analista de datos"},
            {"id": "E-3", "ubicaciones": ["Ciudad A2, País A"], "familia": "Ingeniería", "titulo": "Analista de datos"},
            {"id": "E-4", "ubicaciones": ["Ciudad A1, País A"], "familia": "Ingeniería", "titulo": "Contador"},
        ])
        consulta = {"ubicaciones": ["Ciudad A1"], "filtros": {"job_family": ["ingenieria", "Inexistente"]},
                    "texto": "datos"}
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta)
        self.assertEqual(portal.listados, [{}, {"location": ["Ciudad A1"], "filter_job_family": ["ingeniería"],
                                                "query": ["datos"]}])
        self.assertEqual(self.regiones(r), {"E-1": "Dentro"})
        self.assertIn("revisar: el filtro job_family no ofrece «Inexistente»", errores)

    def test_una_consulta_mal_formada_sale_como_fallo(self):
        portal = EightfoldFalso([{"id": "E-1", "ubicaciones": ["Ciudad A1, País A"]}])
        for consulta in ({}, {"ubicaciones": "Ciudad A1"}, {"filtros": {"job_family": "x"}}, {"texto": 5},
                         {"facetas": {"locations": ["Ciudad A1"]}}):
            with self.subTest(consulta=consulta):
                r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta,
                                   codigo_esperado=1)
                self.assertIn("consulta", r["error"])
                self.assertIn("06/CAT-PLATAFORMAS", r["error"])
        self.assertEqual(portal.listados, [])


class ComprobacionesDeEightfold(ConPortalFalso):
    EN_XA = [{"id": "E-1", "ubicaciones": ["Ciudad A1, País A"], "normalizadas": ["Ciudad A1, PA, XA"]}]
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A1"])])

    def test_si_los_ids_unicos_no_igualan_el_total_la_busqueda_queda_incompleta(self):
        r, errores = self.buscar(self.BLOQUE, EightfoldFalso(self.EN_XA, extra_en_total=1))
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (2, 1, False))
        self.assertIn("[INCOMPLETA] EMP-ACME: 1/2 únicos", errores)

    def test_un_listado_sin_el_orden_estable_sale_como_fallo(self):
        r, _ = self.buscar(self.BLOQUE, EightfoldFalso(self.EN_XA, orden="distance"), codigo_esperado=1)
        self.assertIn("timestamp", r["error"])

    def test_un_detalle_con_otro_id_deja_la_vacante_con_la_evidencia_del_listado(self):
        portal = EightfoldFalso([{**self.EN_XA[0], "id_en_detalle": 1}])
        r, errores = self.buscar(self.BLOQUE, portal)
        v = r["vacantes"][0]
        self.assertEqual(v["estado_vigencia"], "Confirmada abierta")
        self.assertIn("detalle no consultado", v["motivo"])
        self.assertIn("otro ID", v["motivo"])
        self.assertIn("revisar vigencia: E-1 ", errores)

    def test_un_portal_sin_la_api_pcsx_sale_como_fallo(self):
        r, errores = self.buscar(self.BLOQUE, EightfoldFalso(self.EN_XA, sin_pcsx=True), codigo_esperado=1)
        self.assertIn("[FALLO] EMP-ACME: ", errores)
        self.assertIn("pcsx", r["error"])

    def test_un_portal_sin_el_dominio_de_la_empresa_sale_como_fallo(self):
        self.escribir(modulo_04(self.BLOQUE), modulo_06({"EMP-ACME": ficha("EMP-ACME", {
            "plataforma": "eightfold", "portal": EightfoldFalso.HOST + "/careers", "consulta": None})}))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("[FALLO] EMP-ACME: ", r.stderr)
        self.assertIn("?domain=<dominio>", r.stderr)


class ReglasDeRobotsTxt(ConPortalFalso):
    def test_gana_la_regla_mas_larga_del_grupo_del_agente_igual_en_cualquier_python(self):
        # Hasta Python 3.12, urllib.robotparser aplicaba la primera regla que coincide, no la más larga (RFC 9309)
        casos = {
            "Disallow: / antes de un Allow más largo": ("User-agent: *\nDisallow: /\nAllow: /api/pcsx\n", True),
            "ruta prohibida": ("User-agent: *\nDisallow: /api/\n", False),
            "consultas prohibidas con comodín": ("User-agent: *\nDisallow: /*?\n", False),
            "Disallow vacío": ("User-agent: *\nDisallow:\n", True),
            "grupo de otro agente": ("User-agent: OtroBot\nDisallow: /\n", True),
            "grupo propio antes que el de *": ("User-agent: Mozilla\nDisallow: /api/\n\nUser-agent: *\nAllow: /\n",
                                               False),
            "empate entre Allow y Disallow": ("User-agent: *\nDisallow: /api/pcsx\nAllow: /api/pcsx\n", True),
            "fin de ruta con $": ("User-agent: *\nDisallow: /api/pcsx/search$\n", True),
        }
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"])])
        for caso, (robots, permitido) in casos.items():
            with self.subTest(caso):
                portal = EightfoldFalso([{"id": "E-1", "ubicaciones": ["Ciudad A1, País A"]}], robots=robots)
                r, _ = self.buscar(bloque, portal, codigo_esperado=0 if permitido else 1)
                if permitido:
                    self.assertNotIn("error", r)
                else:
                    self.assertIn("robots.txt", r["error"])
                    self.assertEqual(portal.listados, [])


class AdaptadorDeWorkable(ConPortalFalso):
    def test_lista_por_los_codigos_de_pais_de_la_region_en_paginas_de_diez(self):
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"]), grupo("XB", divisiones=["Provincia B1"])],
                              zona_horaria="Etc/GMT+12")
        portal = WorkableFalso([{"id": f"WA{i:02}", "lugares": [("Ciudad A1", "Provincia A1", "País A", "XA")]}
                                for i in range(17)] + [
            # Publicada el 2 de octubre a las 03:00 UTC: en UTC−12 todavía es el 1
            {"id": "WB1", "lugares": [("Ciudad B1", "Provincia B1", "País B", "XB")],
             "publicada": "2026-10-02T03:00:00.000Z"},
            {"id": "WB2", "lugares": [("Ciudad B2", "Provincia B2", "País B", "XB")]},
            {"id": "WC1", "lugares": [("Ciudad C1", None, "País C", "XC")]},
            # Una remota abierta a cualquier país, que el filtro de país también trae
            {"id": "WD1", "lugares": [("", None, "País D", "XD")], "modalidad": "remote", "en_todas": True},
        ])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(portal.listados, [{"location": [{"countryCode": "XA"}, {"countryCode": "XB"}]}])
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (20, 20, True))
        self.assertEqual(set(self.regiones(r).values()), {"Dentro"})
        self.assertEqual(len(r["vacantes"]), 18)
        self.assertEqual(r["fuera_de_region"], ["Ciudad B2, Provincia B2, País B", "País D"])
        self.assertEqual(sorted(portal.detalles), sorted(v["job_id"] for v in r["vacantes"]))
        vacantes = {v["job_id"]: v for v in r["vacantes"]}
        self.assertLessEqual(CAMPOS_DE_VACANTES_Y_OBSERVACIONES, set(vacantes["WB1"]))
        self.assertEqual({vacantes[j]["fecha_publicacion"] for j in ("WA00", "WB1")}, {"2026-10-01"})
        self.assertEqual(vacantes["WA00"]["url_oficial"], "https://apply.workable.com/acme/j/WA00/")
        self.assertEqual(vacantes["WA00"]["ubicacion_literal"], "Ciudad A1, Provincia A1, País A")
        self.assertEqual(vacantes["WA00"]["departamento"], "Ingeniería")
        self.assertEqual(vacantes["WA00"]["descripcion"], "Descripción ficticia.\n\nRequisitos ficticios.")
        self.assertEqual(vacantes["WA00"]["estado_vigencia"], "Confirmada abierta")
        self.assertIn("[OK] EMP-ACME: 20/20 únicos; 18 en la región", errores)

    def test_las_remotas_salen_del_filtro_de_remoto_con_su_alcance_por_codigo_de_pais(self):
        anuncios = [
            {"id": "W1", "lugares": [("Ciudad A1", None, "País A", "XA")]},
            {"id": "W2", "lugares": [("Ciudad A2", None, "País A", "XA")], "modalidad": "remote"},
            {"id": "W3", "lugares": [("", None, "País D", "XD")], "modalidad": "remote", "en_todas": True},
            {"id": "W4", "lugares": [("Ciudad C1", None, "País C", "XC")], "modalidad": "remote"},
            # Remota por el booleano remote, aunque workplace diga otra cosa
            {"id": "W5", "lugares": [("Ciudad A3", None, "País A", "XA")], "modalidad": "hybrid", "remota": True},
        ]
        casos = {
            "paises": (["XA"], [{"remote": [True], "location": [{"countryCode": "XA"}]}],
                       {"W2": "Fuera", "W5": "Fuera"}, ["País D"]),
            "cualquiera": ([], [{"remote": [True]}], {"W2": "Fuera", "W3": "Fuera", "W4": "Fuera", "W5": "Fuera"}, []),
        }
        for alcance, (paises_remoto, listados, remotas, fuera) in casos.items():
            with self.subTest(alcance):
                portal = WorkableFalso(anuncios)
                r, _ = self.buscar(preferencias([], alcance=alcance, paises_remoto=paises_remoto), portal)
                self.assertEqual(portal.listados, listados)
                self.assertEqual(r["vacantes"], [])
                self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), remotas)
                self.assertEqual(r["fuera_de_region"], fuera)
                self.assertIn("remote", r["remotas_revision"])

    def test_la_consulta_de_la_ficha_reemplaza_el_listado_por_paises(self):
        portal = WorkableFalso([{"id": "W1", "lugares": [("Ciudad A1", None, "País A", "XA")]},
                                {"id": "W2", "lugares": [("Ciudad A1", None, "País A", "XA")]},
                                {"id": "W3", "lugares": [("Ciudad A2", None, "País A", "XA")]}])
        consulta = {"ubicaciones": [{"countryCode": "XA", "city": "Ciudad A1"}], "texto": "W1"}
        r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta)
        self.assertEqual(portal.listados, [{"location": [{"countryCode": "XA", "city": "Ciudad A1"}], "query": "W1"}])
        self.assertEqual(self.regiones(r), {"W1": "Dentro"})

    def test_una_consulta_mal_formada_sale_como_fallo(self):
        portal = WorkableFalso([{"id": "W1", "lugares": [("Ciudad A1", None, "País A", "XA")]}])
        for consulta in ({}, {"ubicaciones": ["Ciudad A1"]}, {"ubicaciones": [{"pais": "XA"}]}, {"texto": 5},
                         {"ubicaciones": [{}]}):
            with self.subTest(consulta=consulta):
                r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta,
                                   codigo_esperado=1)
                self.assertIn("consulta", r["error"])
                self.assertIn("06/CAT-PLATAFORMAS", r["error"])
        self.assertEqual(portal.listados, [])


class ComprobacionesDeWorkable(ConPortalFalso):
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A1"])])

    def test_vigencia_e_id_del_detalle_y_total_del_listado(self):
        portal = WorkableFalso([
            {"id": "W1", "lugares": [("Ciudad A1", None, "País A", "XA")], "estado": "closed"},
            {"id": "W2", "lugares": [("Ciudad A1", None, "País A", "XA")], "id_en_detalle": "OTRO"},
        ], extra_en_total=1)
        r, errores = self.buscar(self.BLOQUE, portal)
        vacantes = {v["job_id"]: v for v in r["vacantes"]}
        self.assertEqual(vacantes["W1"]["estado_vigencia"], "Revisar")
        self.assertIn("detalle no consultado", vacantes["W2"]["motivo"])
        self.assertIn("[INCOMPLETA] EMP-ACME: 2/3 únicos", errores)
        self.assertIn("revisar vigencia: W1 ", errores)

    def test_un_portal_que_no_es_de_workable_sale_como_fallo(self):
        self.escribir(modulo_04(self.BLOQUE), modulo_06({"EMP-ACME": ficha("EMP-ACME", {
            "plataforma": "workable", "portal": "https://empleos.acme.example/jobs", "consulta": None})}))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("[FALLO] EMP-ACME: ", r.stderr)
        self.assertIn("apply.workable.com/<cuenta>", r.stderr)


def publicacion(pid, lugar, **cambios):
    """Una publicación de SmartRecruitersFalso, con su ref en el listado y un detalle «Ciudad, Región, País»."""
    ciudad, _, pais = lugar.rpartition(", ")
    return {"id": pid, "lugar": lugar, "ref": f"R{pid}", "detalle": (ciudad, "Región X", pais), **cambios}


class AdaptadorDeSmartRecruiters(ConPortalFalso):
    def test_agrupado_por_ubicacion_completa_solo_los_grupos_que_pueden_ser_de_la_region(self):
        bloque = preferencias([grupo("XA", ["Estado A"], ["Ciudad A1"])], zona_horaria="Etc/GMT+12")
        en_a1 = [publicacion(f"1{i:02}", "Ciudad A1, País A") for i in range(12)]
        en_a1[0].update(ref_detalle="REQ-100", detalle=("Ciudad A1", "Estado A", "País A"))
        en_a1[1].update(ref=None, publicada="2026-10-02T03:00:00.000Z")  # en UTC−12 todavía es el 1
        en_a1[2]["abierta"] = False
        portal = SmartRecruitersFalso(en_a1 + [
            # Grupos que solo nombran el país o una localidad no aceptada de un país de la región: decide su página
            publicacion("200", "País A", detalle=("Ciudad A7", "Estado A", "País A")),
            publicacion("300", "Ciudad A9, País A", detalle=("Ciudad A9", "Estado A", "País A")),
        ] + [publicacion(f"4{i:02}", "Ciudad C1, País C") for i in range(11)])
        r, errores = self.buscar(bloque, portal)
        self.assertEqual(portal.listados, [{}])
        # Solo el grupo de Ciudad A1 tiene más de las que muestra; el de Ciudad C1 no se completa
        self.assertEqual(portal.completados, ["Ciudad A1, País A, XX"])
        self.assertEqual(sorted(portal.detalles), sorted([p["id"] for p in en_a1] + ["200", "300"]))
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (14, 14, True))
        vacantes = {v["url_oficial"].rsplit("/", 1)[1].split("-")[0]: v for v in r["vacantes"]}
        self.assertEqual({p: v["region_relacionada"] for p, v in vacantes.items()},
                         {**{p["id"]: "Dentro" for p in en_a1}, "200": "Indeterminada", "300": "Indeterminada"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad C1, País C"])
        self.assertEqual({p: vacantes[p]["job_id"] for p in ("100", "101", "102")},
                         {"100": "REQ-100", "101": None, "102": "R102"})
        v = vacantes["100"]
        self.assertLessEqual(CAMPOS_DE_VACANTES_Y_OBSERVACIONES, set(v))
        url = SmartRecruitersFalso.PUBLICACIONES + "/Acme/100-puesto-100"
        self.assertEqual((v["url_oficial"], v["url_fuente"]), (url, url))
        self.assertEqual((v["ubicacion_literal"], v["modalidad_literal"]), ("Ciudad A1, Estado A, País A", "on_site"))
        self.assertEqual((v["departamento"], v["descripcion"]),
                         ("Ingeniería", "Descripción ficticia.\n\nRequisitos ficticios."))
        self.assertEqual({vacantes[p]["fecha_publicacion"] for p in ("100", "101")}, {"2026-10-01"})
        self.assertEqual({p: vacantes[p]["estado_vigencia"] for p in ("100", "102")},
                         {"100": "Confirmada abierta", "102": "Revisar"})
        self.assertIn("[OK] EMP-ACME: 14/14 únicos; 12 en la región", errores)
        self.assertIn("revisar ubicación: R200 Ciudad A7, Estado A, País A", errores)
        self.assertIn("revisar vigencia: R102 ", errores)

    def test_un_grupo_que_no_nombra_un_pais_de_04_se_decide_por_la_pagina_de_su_primera_publicacion(self):
        # Como «Ciudad, Estado» en los sitios de algunos países: el nombre del grupo no dice el país
        en_z1 = [publicacion(f"1{i:02}", "Ciudad Z1, EZ", detalle=("Ciudad Z1", "EZ", "País A")) for i in range(11)]
        portal = SmartRecruitersFalso(en_z1 + [
            publicacion("200", "Ciudad Z2, EZ", detalle=("Ciudad Z2", "EZ", "País C")),
            publicacion("201", "Ciudad Z2, EZ", detalle=("Ciudad Z2", "EZ", "País C")),
            publicacion("300", "Ciudad C1, País C"),
        ])
        r, _ = self.buscar(preferencias([grupo("XA")]), portal)
        self.assertEqual(portal.completados, ["Ciudad Z1, EZ, XX"])
        # Una página por grupo sin país de 04, que no se vuelve a pedir; el grupo de País C no se lee
        self.assertEqual(sorted(portal.detalles), sorted([p["id"] for p in en_z1] + ["200"]))
        self.assertEqual(self.regiones(r), {p["ref"]: "Dentro" for p in en_z1})
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (11, 11, True))
        self.assertEqual(r["fuera_de_region"], ["Ciudad C1, País C", "Ciudad Z2, EZ"])

    def test_un_lugar_bajo_el_titulo_que_no_nombra_un_pais_de_04_se_decide_por_una_pagina_con_ese_lugar(self):
        portal = SmartRecruitersFalso([
            publicacion(f"1{i:02}", "Ciudad Z1, EZ", departamento="Ingeniería", detalle=("Ciudad Z1", "EZ", "País A"))
            for i in range(11)] + [
            publicacion("200", "Ciudad Z2, EZ", departamento="Ingeniería", detalle=("Ciudad Z2", "EZ", "País C")),
            publicacion("201", "Ciudad Z2, EZ", departamento="Finanzas", detalle=("Ciudad Z2", "EZ", "País C")),
        ], agrupar="department")
        r, _ = self.buscar(preferencias([grupo("XA")]), portal)
        # Una página por lugar sin país de 04: la de Ciudad Z1 se aprovecha; la de Ciudad Z2 decide que no
        self.assertEqual(sorted(portal.detalles), [f"1{i:02}" for i in range(11)] + ["201"])
        self.assertEqual(set(self.regiones(r).values()), {"Dentro"})
        self.assertEqual(len(r["vacantes"]), 11)
        self.assertEqual(r["fuera_de_region"], ["Ciudad Z2, EZ"])

    def test_avisa_de_las_publicaciones_de_una_misma_requisicion(self):
        portal = SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A", ref_detalle="REQ-1"),
                                       publicacion("2", "Ciudad A2, País A", ref_detalle="REQ-1"),
                                       publicacion("3", "Ciudad A1, País A")])
        r, errores = self.buscar(preferencias([grupo("XA")]), portal)
        self.assertEqual(sorted(v["job_id"] for v in r["vacantes"]), ["R3", "REQ-1", "REQ-1"])
        self.assertEqual(errores.count("revisar: REQ-1 requisición con 2 publicaciones en esta búsqueda"), 2)
        self.assertNotIn("revisar: R3 requisición", errores)

    def test_agrupado_por_departamento_completa_todos_los_grupos_y_toma_el_lugar_de_cada_publicacion(self):
        ingenieria = [publicacion(f"1{i:02}", "Ciudad A1, País A" if i % 4 == 0 else "Ciudad C1, País C",
                                  departamento="Ingeniería") for i in range(12)]
        portal = SmartRecruitersFalso(ingenieria + [
            publicacion("201", "Ciudad A1, País A", departamento="Finanzas"),
            publicacion("202", "Ciudad D1, País D", departamento="Finanzas"),
        ], agrupar="department")
        r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal)
        self.assertEqual(portal.completados, ["1"])
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (14, 14, True))
        # 202 nombra un país que 04 no tiene: su página lo decide
        self.assertEqual(sorted(portal.detalles), ["100", "104", "108", "201", "202"])
        self.assertEqual(set(self.regiones(r).values()), {"Dentro"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad D1, País D", "Ciudad C1, País C"])

    def test_si_ningun_grupo_dice_como_agrupa_prueba_el_nombre_del_grupo_y_el_texto_de_la_publicacion(self):
        publicaciones = [publicacion("1", "Ciudad A1, País A", departamento="Ingeniería"),
                         publicacion("2", "Ciudad C1, País C", departamento="Ingeniería")]
        casos = {"location": "Ciudad C1, País C | Full-time", "department": "Ingeniería | Ciudad C1, País C"}
        for agrupar, fuera in casos.items():
            with self.subTest(agrupar):
                portal = SmartRecruitersFalso(publicaciones, agrupar=agrupar)
                r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal)
                self.assertEqual(self.regiones(r), {"R1": "Dentro"})
                self.assertEqual(portal.detalles, ["1"])
                self.assertEqual(r["fuera_de_region"], [fuera])

    def test_las_remotas_salen_del_filtro_locationtype_con_su_alcance(self):
        publicaciones = [
            publicacion("1", "Ciudad A1, País A"),
            publicacion("2", "Ciudad A2, País A", modalidad="remote"),
            publicacion("3", "Ciudad C1, País C", modalidad="remote"),
            # Un país que 04 no nombra: por el nombre, puede estar en el alcance
            publicacion("4", "Ciudad D1, País D", modalidad="remote"),
            publicacion("5", "Ciudad B1, País B", modalidad="hybrid"),
        ]
        casos = {"paises": (["XA"], ["2", "4"], {"R2": "Fuera", "R4": "Fuera"},
                            ["Ciudad C1, País C | Full-time", "Ciudad A1, País A | Full-time"]),
                 "cualquiera": ([], ["2", "3", "4"], {"R2": "Fuera", "R3": "Fuera", "R4": "Fuera"},
                                ["Ciudad A1, País A | Full-time"])}
        for alcance, (paises_remoto, detalles, remotas, fuera) in casos.items():
            with self.subTest(alcance):
                portal = SmartRecruitersFalso(publicaciones)
                bloque = preferencias([grupo("XB", nombres=["Ciudad B1"])], alcance=alcance,
                                      paises_remoto=paises_remoto)
                r, errores = self.buscar(bloque, portal)
                # Las remotas primero: el listado de la región no dice la modalidad
                self.assertEqual(portal.listados, [{"locationType": ["REMOTE"]}, {}])
                self.assertEqual(sorted(portal.detalles), detalles + ["5"])
                self.assertEqual(self.regiones(r), {"R5": "Dentro"})
                self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), remotas)
                self.assertEqual(r["fuera_de_region"], fuera)
                self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (5, 5, True))
                self.assertIn("locationType=REMOTE", r["remotas_revision"])

    def test_la_consulta_de_la_ficha_elige_grupos_y_busca_texto(self):
        portal = SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A"), publicacion("2", "Ciudad A2, País A"),
                                       publicacion("3", "Ciudad A1, País A")])
        consulta = {"grupos": ["ciudad a1, pais a", "Ciudad Inexistente"], "texto": "puesto 1"}
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta)
        self.assertEqual(portal.listados, [{"search": ["puesto 1"]}])
        self.assertEqual(self.regiones(r), {"R1": "Dentro"})
        self.assertIn("revisar: el sitio no tiene el grupo «Ciudad Inexistente»", errores)

    def test_una_consulta_mal_formada_sale_como_fallo(self):
        portal = SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A")])
        for consulta in ({}, {"grupos": "Ciudad A1"}, {"grupos": []}, {"texto": 5}, {"facetas": {"x": ["y"]}}):
            with self.subTest(consulta=consulta):
                r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta,
                                   codigo_esperado=1)
                self.assertIn("consulta", r["error"])
                self.assertIn("06/CAT-PLATAFORMAS", r["error"])
        self.assertEqual(portal.listados, [])


class ComprobacionesDeSmartRecruiters(ConPortalFalso):
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A1"])])

    def test_si_un_grupo_trae_menos_publicaciones_que_su_conteo_la_busqueda_queda_incompleta(self):
        r, errores = self.buscar(self.BLOQUE, SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A")],
                                                                   extra_en_total=1))
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (2, 1, False))
        self.assertIn("[INCOMPLETA] EMP-ACME: 1/2 únicos", errores)

    def test_un_detalle_con_otro_id_deja_la_vacante_con_la_evidencia_del_listado(self):
        r, errores = self.buscar(self.BLOQUE, SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A",
                                                                                id_en_detalle="9")]))
        v = r["vacantes"][0]
        self.assertEqual((v["job_id"], v["estado_vigencia"]), ("R1", "Confirmada abierta"))
        self.assertIn("otro ID", v["motivo"])
        self.assertIn("revisar vigencia: R1 ", errores)

    def test_si_el_robots_txt_de_smartrecruiters_prohibe_la_empresa_no_se_usa(self):
        portal = SmartRecruitersFalso([publicacion("1", "Ciudad A1, País A")],
                                      robots_www="User-agent: *\nDisallow: /search/\nDisallow: /Acme/*\n")
        r, errores = self.buscar(self.BLOQUE, portal, codigo_esperado=1)
        self.assertIn("[FALLO] EMP-ACME: ", errores)
        self.assertIn("robots.txt", r["error"])
        self.assertEqual(portal.listados, [])

    def test_un_portal_que_no_es_de_smartrecruiters_sale_como_fallo(self):
        self.escribir(modulo_04(self.BLOQUE), modulo_06({"EMP-ACME": ficha("EMP-ACME", {
            "plataforma": "smartrecruiters", "portal": "https://api.smartrecruiters.com/v1/companies/Acme",
            "consulta": None})}))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("[FALLO] EMP-ACME: ", r.stderr)
        self.assertIn("careers.smartrecruiters.com/<empresa>", r.stderr)


class AdaptadorDeOracle(ConPortalFalso):
    def test_lista_cada_pais_de_la_region_con_el_primer_nombre_que_la_api_reconoce(self):
        bloque = preferencias([grupo("XA", ["Estado A"], ["Ciudad A1"]), grupo("XB", nombres=["Ciudad B1"])],
                              zona_horaria="Etc/GMT+12")
        en_a1 = [{"id": f"1{i:02}", "lugares": [("Ciudad A1, Estado A, País A", "XA")]} for i in range(27)]
        portal = OracleFalso(en_a1 + [
            # Publicada el 2 de octubre a las 03:00 UTC: en UTC−12 todavía es el 1
            {"id": "201", "lugares": [("Ciudad C1, País C", "XC"), ("Ciudad A1, Estado A, País A", "XA")],
             "publicada": "2026-10-02T03:00:00+00:00", "familia": "Ingeniería"},
            {"id": "202", "lugares": [("Ciudad A7, Estado A7, País A", "XA")]},
            {"id": "203", "lugares": [("Ciudad B1, País B", "XB")], "cierre": "2026-01-01T00:00:00+00:00"},
            {"id": "204", "lugares": [("Ciudad C2, País C", "XC")]},
        ], reconocidos={"Country A": "XA", "País B": "XB"})
        r, errores = self.buscar(bloque, portal)
        # La primera página sin filtros da las facetas; «País A» no lo reconoce, y entonces no filtra
        self.assertEqual(portal.listados,
                         [{}, {"location": "País A"}, {"location": "Country A"}, {"location": "País B"}])
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (30, 30, True))
        self.assertEqual(self.regiones(r), {**{a["id"]: "Dentro" for a in en_a1}, "201": "Incluye", "203": "Dentro"})
        self.assertEqual(r["fuera_de_region"], ["Ciudad A7, Estado A7, País A"])
        # Solo se lee el detalle de las que se entregan
        self.assertEqual(sorted(portal.detalles), sorted([f"1{i:02}" for i in range(27)] + ["201", "203"]))
        vacantes = {v["job_id"]: v for v in r["vacantes"]}
        v = vacantes["201"]
        self.assertLessEqual(CAMPOS_DE_VACANTES_Y_OBSERVACIONES, set(v))
        self.assertEqual(v["url_oficial"], OracleFalso.PORTAL + "/job/201")
        self.assertEqual(v["ubicacion_literal"], "Ciudad C1, País C | Ciudad A1, Estado A, País A")
        self.assertEqual((v["modalidad_literal"], v["departamento"]), ("Onsite", "Ingeniería"))
        self.assertEqual(v["descripcion"], "Descripción ficticia.\n\n- Responsabilidad ficticia.")
        self.assertIn("recruitingCEJobRequisitionDetails", v["url_fuente"])
        self.assertEqual({vacantes[j]["fecha_publicacion"] for j in ("100", "201")}, {"2026-10-01"})
        self.assertEqual({j: vacantes[j]["estado_vigencia"] for j in ("100", "203")},
                         {"100": "Confirmada abierta", "203": "Revisar"})
        self.assertIn("ExternalPostedEndDate", vacantes["203"]["motivo"])
        self.assertIn("[OK] EMP-ACME: 30/30 únicos; 29 en la región", errores)
        self.assertIn("revisar vigencia: 203 ", errores)

    def test_un_nombre_que_la_api_no_reconoce_no_filtra_aunque_su_faceta_lo_traiga_con_otros_acentos(self):
        # «Country Á» no lo reconoce y trae todo el sitio, cuya faceta de ubicaciones trae «Country A»
        bloque = preferencias([grupo("XA", nombres=["Ciudad A1"])], paises={"XA": ["Country Á", "Country A"]})
        portal = OracleFalso([{"id": "1", "lugares": [("Ciudad A1, País A", "XA")]},
                              {"id": "2", "lugares": [("Ciudad C1, País C", "XC")]}])
        r, _ = self.buscar(bloque, portal)
        self.assertEqual(portal.listados, [{}, {"location": "Country Á"}, {"location": "Country A"}])
        self.assertEqual((r["total_reportado"], r["unicos"]), (1, 1))
        self.assertEqual(r["fuera_de_region"], [])

    def test_avisa_si_la_api_no_reconoce_ningun_nombre_de_un_pais(self):
        portal = OracleFalso([{"id": "1", "lugares": [("Ciudad A1, País A", "XA")]}], reconocidos={})
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal)
        self.assertEqual(portal.listados, [{}, {"location": "País A"}, {"location": "Country A"}])
        self.assertEqual((r["total_reportado"], r["vacantes"]), (0, []))
        self.assertIn("revisar: la API no reconoce como país ningún nombre de XA", errores)

    def test_las_remotas_salen_de_la_faceta_de_modalidad_con_su_alcance_por_codigo_de_pais(self):
        requisiciones = [
            {"id": "1", "lugares": [("Ciudad A1, País A", "XA")]},
            {"id": "2", "lugares": [("Ciudad A2, País A", "XA")], "modalidad": "Remote"},
            # Remota de otro país con una ubicación secundaria en XA: la búsqueda por XA también la trae
            {"id": "3", "lugares": [("Ciudad D1, País D", "XD"), ("Ciudad A3, País A", "XA")], "modalidad": "Remote"},
            {"id": "4", "lugares": [("Ciudad C1, País C", "XC")], "modalidad": "Remote"},
            {"id": "5", "lugares": [("Ciudad A4, País A", "XA")], "modalidad": "Hybrid"},
        ]
        remoto = {"selectedWorkplaceTypesFacet": "ORA_REMOTE"}
        casos = {"paises": (["XA"], [{}, {"location": "País A", **remoto}, {"location": "Country A", **remoto}],
                            {"2": "Fuera", "3": "Fuera"}),
                 "cualquiera": ([], [{}, remoto], {"2": "Fuera", "3": "Fuera", "4": "Fuera"})}
        for alcance, (paises_remoto, listados, remotas) in casos.items():
            with self.subTest(alcance):
                portal = OracleFalso(requisiciones)
                r, _ = self.buscar(preferencias([], alcance=alcance, paises_remoto=paises_remoto), portal)
                self.assertEqual(portal.listados, listados)
                self.assertEqual(r["vacantes"], [])
                self.assertEqual(self.regiones(r, "remotas_fuera_de_region"), remotas)
                self.assertIn("selectedWorkplaceTypesFacet", r["remotas_revision"])

    def test_sin_valor_remoto_en_la_faceta_de_modalidad_avisa(self):
        portal = OracleFalso([{"id": "1", "lugares": [("Ciudad A1, País A", "XA")]}])
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])], alcance="cualquiera"), portal)
        self.assertEqual(self.regiones(r), {"1": "Dentro"})
        self.assertIn("No disponible", r["remotas_revision"])
        self.assertIn("revisar: sin filtro de remoto en el portal", errores)

    def test_la_consulta_de_la_ficha_reemplaza_el_listado_por_paises(self):
        portal = OracleFalso([{"id": "1", "lugares": [("Ciudad A1, País A", "XA")], "familia": "Ingeniería"},
                              {"id": "2", "lugares": [("Ciudad A1, País A", "XA")], "familia": "Finanzas"},
                              {"id": "3", "lugares": [("Ciudad A1, País A", "XA")], "familia": "Ingeniería"}])
        consulta = {"facetas": {"CATEGORIES": ["ingenieria", "Inexistente"]}, "texto": "puesto 1"}
        r, errores = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta)
        self.assertEqual(portal.listados, [{}, {"selectedCategoriesFacet": "CAT-Ingeniería", "keyword": "puesto 1"}])
        self.assertEqual(self.regiones(r), {"1": "Dentro"})
        self.assertIn("revisar: la faceta CATEGORIES no ofrece «Inexistente»", errores)

    def test_una_consulta_mal_formada_sale_como_fallo(self):
        portal = OracleFalso([{"id": "1", "lugares": [("Ciudad A1, País A", "XA")]}])
        for consulta in ({}, {"facetas": {"CATEGORIES": "x"}}, {"facetas": {"OTRA": ["x"]}}, {"texto": 5},
                         {"ubicaciones": ["Ciudad A1"]}):
            with self.subTest(consulta=consulta):
                r, _ = self.buscar(preferencias([grupo("XA", nombres=["Ciudad A1"])]), portal, consulta=consulta,
                                   codigo_esperado=1)
                self.assertIn("consulta", r["error"])
                self.assertIn("06/CAT-PLATAFORMAS", r["error"])
        self.assertEqual(portal.listados, [])


class ComprobacionesDeOracle(ConPortalFalso):
    BLOQUE = preferencias([grupo("XA", nombres=["Ciudad A1"])])
    EN_XA = [{"id": "1", "lugares": [("Ciudad A1, País A", "XA")]}]

    def test_si_los_ids_unicos_no_igualan_el_total_la_busqueda_queda_incompleta(self):
        r, errores = self.buscar(self.BLOQUE, OracleFalso(self.EN_XA, extra_en_total=1))
        self.assertEqual((r["total_reportado"], r["unicos"], r["completa"]), (2, 1, False))
        self.assertIn("[INCOMPLETA] EMP-ACME: 1/2 únicos", errores)

    def test_un_detalle_con_otro_id_deja_la_vacante_con_la_evidencia_del_listado(self):
        r, errores = self.buscar(self.BLOQUE, OracleFalso([{**self.EN_XA[0], "id_en_detalle": "9"}]))
        v = r["vacantes"][0]
        self.assertEqual(v["estado_vigencia"], "Confirmada abierta")
        self.assertIn("otro ID", v["motivo"])
        self.assertIn("revisar vigencia: 1 ", errores)

    def test_si_robots_txt_prohibe_la_api_no_se_usa(self):
        portal = OracleFalso(self.EN_XA, robots="User-agent: *\nDisallow: /hcmRestApi/\n")
        r, errores = self.buscar(self.BLOQUE, portal, codigo_esperado=1)
        self.assertIn("robots.txt", r["error"])
        self.assertEqual(portal.listados, [])

    def test_un_portal_que_no_es_de_oraclerecruitingcloud_sale_como_fallo(self):
        self.escribir(modulo_04(self.BLOQUE), modulo_06({"EMP-ACME": ficha("EMP-ACME", {
            "plataforma": "oraclerecruitingcloud", "portal": "https://empleos.acme.example/jobs", "consulta": None})}))
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("[FALLO] EMP-ACME: ", r.stderr)
        self.assertIn("/hcmUI/CandidateExperience/", r.stderr)


if __name__ == "__main__":
    unittest.main()
