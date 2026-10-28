"""Pruebas de la herramienta del archivo de registros, por su línea de comandos y sin red.

Uso, con el Python de un entorno virtual que tiene openpyxl (CONTRIBUTING, «Pruebas»):
    .venv/bin/python -I -B -m unittest discover -s herramientas/pruebas

Sin openpyxl, se saltan. Cada prueba arma una copia ficticia con el script, el 08 y el 11 de la plantilla,
un 04 con la zona horaria y un 06 con empresas ficticias. Los datos son sintéticos.
"""
import datetime as dt
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "herramientas" / "registros.py"
SIN_OPENPYXL = importlib.util.find_spec("openpyxl") is None

PESTANAS = ["vacantes", "observaciones", "habilidades_vacante", "documentos", "busquedas", "evaluaciones",
            "informes"]


def modulo_04(zona_horaria="UTC"):
    bloque = {"paises": {}, "localidades": [], "remoto": {"alcance": "cualquiera", "paises": []},
              "zona_horaria": zona_horaria, "moneda": "XTS"}
    return ("# 04 — Preferencias laborales\n\n## PREF-UBICACION — Región\n\nRegión.\n\n```json\n"
            + json.dumps(bloque, indent=2) + "\n```\n")


def modulo_06(ids):
    filas = "".join(f"| {eid} | Empresa ficticia | Objetivo | 0.1 | 2026-10-16 |\n" for eid in ids)
    return ("# 06 — Empresas objetivo y fichas\n\n## CAT-EMPRESAS — Catálogo\n\n"
            "| ID | Empresa | Estado | Versión de ficha | Fecha de comprobación |\n"
            "| --- | --- | --- | --- | --- |\n" + filas + "\n## CAT-REGLAS — Mantenimiento\n\n- Reglas.\n")


def busqueda_ficticia():
    """Lo que registra una búsqueda ficticia, en todas las pestañas. VAC-0001 y OBS-0001 se citan entre sí."""
    return {
        "busquedas": [{"busqueda_id": "BUS-0001", "fecha_hora": "2026-03-02 09:30",
                       "solicitud_alcance": "Búsqueda ficticia", "recursos_versiones": "07 v1.0 | 11 v1.0",
                       "fuentes_consultas_filtros": "herramientas/buscar.py v1.0 | portal ficticio",
                       "cobertura_limitaciones": "2 únicos de 2, completa", "no_revisado_pendientes": "Ninguno",
                       "comparacion_anterior": "Sin búsqueda comparable"}],
        "vacantes": [
            {"vacante_id": "VAC-0001", "empresa_id": "EMP-XA", "job_id": "000123", "titulo": "Puesto ficticio",
             "url_oficial": "https://example.com/empleo/000123", "ubicacion_literal": "Ciudad A1, País A",
             "modalidad_literal": "Hybrid", "region_relacionada": "Dentro", "fecha_publicacion": "2026-02-20",
             "primera_deteccion": "2026-03-02", "ultima_observacion_id": "OBS-0001"},
            {"vacante_id": "VAC-0002", "empresa_id": "EMP-XA", "job_id": "No publicado", "titulo": "Otro puesto",
             "ubicacion_literal": "No publicado", "modalidad_literal": "No publicado",
             "region_relacionada": "Indeterminada", "primera_deteccion": "2026-03-02",
             "ultima_observacion_id": "OBS-0002"}],
        "observaciones": [
            {"observacion_id": "OBS-0001", "vacante_id": "VAC-0001", "busqueda_id": "BUS-0001",
             "fecha_verificacion": "2026-03-02", "estado_vigencia": "Confirmada abierta",
             "motivo": "En listado oficial; detalle no consultado", "url_fuente": "https://example.com/empleo/000123",
             "tipo_fuente": "Oficial"},
            {"observacion_id": "OBS-0002", "vacante_id": "VAC-0002", "busqueda_id": "BUS-0001",
             "fecha_verificacion": "2026-03-02 10:05", "estado_vigencia": "No verificable", "motivo": "error 404",
             "tipo_fuente": "Oficial"}],
        "habilidades_vacante": [
            {"habilidad_observacion_id": "HV-00001", "vacante_id": "VAC-0001", "observacion_id": "OBS-0001",
             "habilidad_literal": "Experience with Python", "habilidad_normalizada": "Python",
             "tipo_requisito": "Obligatorio"}],
        "documentos": [
            {"documento_id": "DOC-0001", "vacante_id": "VAC-0001", "fecha_generacion": "2026-03-03",
             "version_perfil": "1.10", "version_cv_base": "1.0", "idioma": "ES", "formato": "PDF",
             "archivo": "CV_ficticio.pdf", "revision_visual": "Satisfactoria", "texto_extraible": "Satisfactoria"}],
        "evaluaciones": [
            {"evaluacion_id": "EVA-0001", "vacante_id": "VAC-0001", "observacion_id": "OBS-0001",
             "fecha_evaluacion": "2026-03-02", "version_perfil": "1.10", "version_evaluacion": "1.0",
             "condiciones": "Sin exclusiones", "condiciones_detalle": "Sueldo | Remoto", "encaje": "★★★☆☆",
             "cobertura": "3/4", "nucleos": "Núcleo A: Directa"}],
        "informes": [{"busqueda_id": "BUS-0001", "vacante_id": "VAC-0001", "evaluacion_id": "EVA-0001"}],
    }


@unittest.skipIf(SIN_OPENPYXL, "falta openpyxl: corre las pruebas con el Python del entorno virtual")
class CopiaFicticia(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)
        (self.dir / "herramientas").mkdir()
        shutil.copy(SCRIPT, self.dir / "herramientas")
        shutil.copy(RAIZ / "11_ESQUEMAS_DE_REGISTROS.md", self.dir)
        shutil.copy(RAIZ / "08_EVALUACION_DE_VACANTES.md", self.dir)
        (self.dir / "04_PREFERENCIAS_LABORALES.md").write_text(modulo_04(), encoding="utf-8")
        (self.dir / "06_EMPRESAS_OBJETIVO.md").write_text(modulo_06(["EMP-XA", "EMP-PRUEBA"]), encoding="utf-8")
        self.archivo = self.dir / "ChambaKit_Registros.xlsx"

    def tearDown(self):
        self._tmp.cleanup()

    def correr(self, *argumentos, entrada=None):
        """El script de la copia por su línea de comandos; entrada, el JSON que recibe por stdin."""
        return subprocess.run([sys.executable, "-I", "-B", str(self.dir / "herramientas" / "registros.py"),
                               *argumentos], input=None if entrada is None else json.dumps(entrada),
                              capture_output=True, text=True, timeout=60)

    def ok(self, *argumentos, entrada=None):
        r = self.correr(*argumentos, entrada=entrada)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def leer(self, pestana, *argumentos):
        return self.ok("leer", pestana, *argumentos)

    def assertRechazaSinEscribir(self, orden, entrada, *textos):
        antes = self.archivo.read_bytes()
        r = self.correr(orden, entrada=entrada)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        for t in textos:
            self.assertIn(t, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(r.stdout, "")
        self.assertEqual(self.archivo.read_bytes(), antes)


class Crear(CopiaFicticia):
    def test_crea_el_archivo_con_las_pestanas_del_esquema_vacias(self):
        creado = self.ok("crear")
        self.assertTrue(self.archivo.is_file())
        self.assertEqual(list(creado["pestanas"]), PESTANAS)
        self.assertEqual(creado["pestanas"]["busquedas"][0], "busqueda_id")
        # informes guarda solo los IDs; las columnas calculadas las da el comando informe.
        self.assertEqual(creado["pestanas"]["informes"], ["busqueda_id", "vacante_id", "evaluacion_id"])
        for pestana in PESTANAS:
            with self.subTest(pestana=pestana):
                self.assertEqual(self.leer(pestana), [])

    def test_no_sobrescribe_un_archivo_que_ya_existe(self):
        self.ok("crear")
        self.ok("agregar", entrada={"busquedas": busqueda_ficticia()["busquedas"]})
        r = self.correr("crear")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("ya existe", r.stderr)
        self.assertEqual(len(self.leer("busquedas")), 1)

    def test_si_11_cambia_una_columna_avisa_que_el_archivo_no_coincide(self):
        self.ok("crear")
        modulo = self.dir / "11_ESQUEMAS_DE_REGISTROS.md"
        texto = modulo.read_text(encoding="utf-8")
        modulo.write_text(texto.replace('{"nombre": "comparacion_anterior",', '{"nombre": "comparacion_nueva",'), encoding="utf-8")
        r = self.correr("leer", "busquedas")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("comparacion_nueva", r.stderr)
        self.assertIn("Encabezados", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


class Agregar(CopiaFicticia):
    def setUp(self):
        super().setUp()
        self.columnas = self.ok("crear")["pestanas"]

    def test_agrega_las_filas_de_todas_las_pestanas_y_se_leen_tal_como_se_escribieron(self):
        busqueda = busqueda_ficticia()
        agregadas = self.ok("agregar", entrada=busqueda)
        self.assertEqual(agregadas["agregadas"], {p: len(filas) for p, filas in busqueda.items()})
        for pestana, filas in busqueda.items():
            with self.subTest(pestana=pestana):
                # Las columnas que la fila no trae se leen vacías; «000123» y «1.10» siguen siendo texto.
                esperadas = [{c: f.get(c, "") for c in self.columnas[pestana]} for f in filas]
                self.assertEqual(self.leer(pestana), esperadas)

    def test_un_texto_que_empieza_con_igual_se_guarda_como_texto_y_no_como_formula(self):
        import openpyxl
        busqueda = busqueda_ficticia()
        busqueda["habilidades_vacante"][0]["habilidad_literal"] = '=HYPERLINK("https://example.com","Python")'
        self.ok("agregar", entrada=busqueda)
        self.ok("actualizar", entrada={"observaciones": [{"observacion_id": "OBS-0002", "motivo": "=1+1"}]})
        libro = openpyxl.load_workbook(self.archivo)
        for pestana, celda in (("habilidades_vacante", "D2"), ("observaciones", "F3")):
            with self.subTest(pestana=pestana):
                self.assertEqual(libro[pestana][celda].data_type, "s")
        self.assertEqual(self.leer("observaciones", "--id", "OBS-0002")[0]["motivo"], "=1+1")

    def test_rechaza_las_filas_que_no_cumplen_el_esquema_y_no_escribe_ninguna(self):
        def con(pestana, cambios, indice=0):
            busqueda = busqueda_ficticia()
            busqueda[pestana][indice].update(cambios)
            return busqueda

        def sin(pestana, columna):
            busqueda = busqueda_ficticia()
            del busqueda[pestana][0][columna]
            return busqueda

        repetida = busqueda_ficticia()
        repetida["habilidades_vacante"].append(dict(repetida["habilidades_vacante"][0], habilidad_literal="Python"))
        informe_doble = busqueda_ficticia()
        informe_doble["informes"].append(dict(informe_doble["informes"][0]))
        casos = {
            "fecha irreal": (con("vacantes", {"fecha_publicacion": "2026-13-45"}), "fecha_publicacion"),
            "hora donde no se admite": (con("evaluaciones", {"fecha_evaluacion": "2026-03-02 10:00"}),
                                        "fecha_evaluacion"),
            "hora irreal": (con("observaciones", {"fecha_verificacion": "2026-03-02 25:00"}, 1),
                            "fecha_verificacion"),
            "URL sin protocolo": (con("vacantes", {"url_oficial": "example.com/empleo/000123"}), "url_oficial"),
            "valor fuera de la lista": (con("vacantes", {"region_relacionada": "Cerca"}), "region_relacionada"),
            "empresa fuera de 06": (con("vacantes", {"empresa_id": "EMP-ZZ"}), "empresa_id", "06"),
            "ID mal formado": (con("documentos", {"documento_id": "DOC-1"}), "documento_id"),
            "ID repetido": (repetida, "habilidad_observacion_id", "HV-00001"),
            "obligatoria vacía": (sin("vacantes", "titulo"), "titulo"),
            "obligatoria vacía sin duplicado_de": (con("vacantes", {"ultima_observacion_id": ""}),
                                                   "ultima_observacion_id"),
            "referencia inexistente": (con("observaciones", {"busqueda_id": "BUS-0099"}), "busqueda_id", "BUS-0099"),
            "observación de otra vacante": (con("evaluaciones", {"observacion_id": "OBS-0002"}), "observacion_id"),
            "duplicada de sí misma": (con("vacantes", {"duplicado_de": "VAC-0001"}), "duplicado_de"),
            "pareja repetida en informes": (informe_doble, "vacante_id"),
            "patrón": (con("documentos", {"version_perfil": "1"}), "version_perfil"),
            "columna desconocida": (con("vacantes", {"salario": "1000"}), "salario"),
            "columna calculada": (con("informes", {"encaje": "★★★☆☆"}), "encaje"),
            "valor que no es texto": (con("vacantes", {"job_id": 123}), "job_id"),
            "pestaña desconocida": ({"postulaciones": [{"vacante_id": "VAC-0001"}]}, "postulaciones"),
            "filas que no son lista": ({"vacantes": {"vacante_id": "VAC-0001"}}, "vacantes"),
            "entrada que no es objeto": ([busqueda_ficticia()], "objeto"),
        }
        for caso, (entrada, *textos) in casos.items():
            with self.subTest(caso):
                self.assertRechazaSinEscribir("agregar", entrada, *textos)

    def test_una_fila_que_repite_un_id_ya_registrado_se_rechaza(self):
        self.ok("agregar", entrada=busqueda_ficticia())
        self.assertRechazaSinEscribir("agregar", {"busquedas": busqueda_ficticia()["busquedas"]}, "busqueda_id",
                                      "BUS-0001")

    def test_las_referencias_se_resuelven_con_las_filas_ya_registradas(self):
        busqueda = busqueda_ficticia()
        self.ok("agregar", entrada={p: busqueda[p] for p in ("busquedas", "vacantes", "observaciones")})
        self.ok("agregar", entrada={p: busqueda[p] for p in ("evaluaciones", "informes")})
        self.assertEqual([f["evaluacion_id"] for f in self.leer("informes")], ["EVA-0001"])


class Actualizar(CopiaFicticia):
    def setUp(self):
        super().setUp()
        self.ok("crear")
        self.ok("agregar", entrada=busqueda_ficticia())

    def test_cambia_solo_las_columnas_dadas_de_la_fila_con_ese_id(self):
        antes = self.leer("vacantes")
        segunda = busqueda_ficticia()["busquedas"][0] | {"busqueda_id": "BUS-0002"}
        observacion = busqueda_ficticia()["observaciones"][0] | {"observacion_id": "OBS-0003", "busqueda_id": "BUS-0002"}
        self.ok("agregar", entrada={"busquedas": [segunda], "observaciones": [observacion]})
        cambio = {"vacante_id": "VAC-0001", "titulo": "Puesto ficticio (nuevo título)", "ultima_observacion_id": "OBS-0003"}
        self.assertEqual(self.ok("actualizar", entrada={"vacantes": [cambio]}), {"actualizadas": {"vacantes": 1}})
        self.assertEqual(self.leer("vacantes"), [antes[0] | cambio, antes[1]])

    def test_una_fila_absorbida_puede_quedar_sin_ultima_observacion(self):
        cambio = {"vacante_id": "VAC-0002", "duplicado_de": "VAC-0001", "ultima_observacion_id": ""}
        self.ok("actualizar", entrada={"vacantes": [cambio]})
        self.assertEqual(self.leer("vacantes", "--id", "VAC-0002")[0]["duplicado_de"], "VAC-0001")

    def test_rechaza_los_cambios_invalidos_y_no_escribe_ninguno(self):
        casos = {
            "ID inexistente": ({"vacantes": [{"vacante_id": "VAC-0099", "titulo": "x"}]}, "VAC-0099"),
            "valor inválido": ({"vacantes": [{"vacante_id": "VAC-0001", "titulo": "x"},
                                             {"vacante_id": "VAC-0002", "fecha_publicacion": "2026-02-30"}]},
                               "VAC-0002", "fecha_publicacion"),
            "sin el ID de la fila": ({"vacantes": [{"titulo": "x"}]}, "vacante_id"),
            "pestaña sin ID propio": ({"informes": [{"busqueda_id": "BUS-0001", "evaluacion_id": "EVA-0001"}]},
                                      "informes"),
        }
        for caso, (entrada, *textos) in casos.items():
            with self.subTest(caso):
                self.assertRechazaSinEscribir("actualizar", entrada, *textos)


class Leer(CopiaFicticia):
    def test_filtra_por_id_en_la_primera_columna_o_en_la_que_se_pida(self):
        self.ok("crear")
        self.ok("agregar", entrada=busqueda_ficticia())
        self.assertEqual([f["vacante_id"] for f in self.leer("vacantes", "--id", "VAC-0002", "VAC-0099")], ["VAC-0002"])
        self.assertEqual([f["observacion_id"] for f in self.leer("observaciones", "--columna", "vacante_id",
                                                                 "--id", "VAC-0001")], ["OBS-0001"])

    def test_sin_el_archivo_dice_que_lo_crea_configurar(self):
        r = self.correr("leer", "vacantes")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("/configurar", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


def hoy():
    """La fecha de hoy en la zona horaria del 04 ficticio (UTC), la que usa el comando informe."""
    return dt.datetime.now(dt.timezone.utc).date()


def hace(dias):
    return (hoy() - dt.timedelta(days=dias)).isoformat()


class Informe(CopiaFicticia):
    def setUp(self):
        super().setUp()
        self.ok("crear")

    def test_la_tabla_de_una_busqueda_calcula_las_columnas_de_informes(self):
        def vacante(n, job_id, publicada, detectada, url=""):
            return {"vacante_id": f"VAC-000{n}", "empresa_id": "EMP-XA", "job_id": job_id, "titulo": f"Puesto {n}",
                    "url_oficial": url, "region_relacionada": "Dentro", "fecha_publicacion": publicada,
                    "primera_deteccion": detectada, "ultima_observacion_id": f"OBS-000{n}"}

        def observacion(n):
            return {"observacion_id": f"OBS-000{n}", "vacante_id": f"VAC-000{n}", "busqueda_id": "BUS-0002",
                    "fecha_verificacion": hace(0), "estado_vigencia": "Confirmada abierta", "motivo": "En listado",
                    "tipo_fuente": "Oficial"}

        def evaluacion(n, condiciones, detalle, encaje="", cobertura="", nucleos=""):
            return {"evaluacion_id": f"EVA-000{n}", "vacante_id": f"VAC-000{n}", "observacion_id": f"OBS-000{n}",
                    "fecha_evaluacion": hace(0), "version_perfil": "1.0", "version_evaluacion": "1.0",
                    "condiciones": condiciones, "condiciones_detalle": detalle, "encaje": encaje,
                    "cobertura": cobertura, "nucleos": nucleos}

        busqueda = busqueda_ficticia()
        busqueda["busquedas"].append(dict(busqueda["busquedas"][0], busqueda_id="BUS-0002", fecha_hora=hace(0)))
        busqueda["vacantes"] += [
            vacante(3, "R-3", hace(25), hace(3), "https://example.com/empleo/R-3"),
            # Sin distinguir mayúsculas: también es «sin Job ID».
            vacante(4, "no publicado", "", hace(3)),
            vacante(5, "", "", hace(0)),
            vacante(6, "R-6", hace(20), hace(0)),
            vacante(7, "R-7", hace(19), hace(25)),
            vacante(8, "R-8", hace(0), hace(0))]
        busqueda["observaciones"] += [observacion(n) for n in range(3, 9)]
        busqueda["evaluaciones"] += [
            evaluacion(3, "Sin exclusiones", "Sueldo | Duración | Relación | Horario", "★★★★☆", "4/4",
                       "Núcleo A: Directa | Núcleo B: Transferible"),
            evaluacion(4, "Excluida", "Duración: «6-month contract» | Relación: «Freelance»"),
            evaluacion(5, "Sin exclusiones", "Ninguno", "★★☆☆☆", "", "Núcleo A: Insuficiente | Núcleo B: Insuficiente"),
            evaluacion(6, "Sin exclusiones", "Sueldo | Modalidad | Viajes", "★★★☆☆", "2/3, 1 solo académico",
                       "Núcleo C: Académica/formativa"),
            evaluacion(7, "Sin exclusiones", "Ubicación", "★☆☆☆☆", "1/4", "Núcleo A: Insuficiente"),
            evaluacion(8, "Sin exclusiones", "Ninguno", "☆☆☆☆☆", "0/2")]
        busqueda["informes"] += [{"busqueda_id": "BUS-0002", "vacante_id": f"VAC-000{n}", "evaluacion_id": f"EVA-000{n}"}
                                 for n in (3, 4, 5, 6, 7, 8)]
        self.ok("agregar", entrada=busqueda)
        tabla = self.ok("informe", "BUS-0002")
        self.assertEqual([[f[c] for c in ("empresa", "vacante", "encaje", "antiguedad", "alertas", "url_oficial")]
                          for f in tabla], [
            ["XA", "R-3 — Puesto 3", "★★★★☆ · 4/4", "25 d · antigua", "—", "https://example.com/empleo/R-3"],
            ["XA", "sin Job ID — Puesto 4", "—", "≥ 3 d", "Excluida: Duración: «6-month contract»; Relación: «Freelance»",
             ""],
            ["XA", "sin Job ID — Puesto 5", "★★☆☆☆", "—", "Insuficiente: Núcleo A; Núcleo B", ""],
            ["XA", "R-6 — Puesto 6", "★★★☆☆ · 2/3, 1 solo académico", "20 d · antigua",
             "Académica: Núcleo C · Pendiente: modalidad, viajes", ""],
            # Detectada antes de su fecha de publicación: cuenta desde la más antigua de las dos.
            ["XA", "R-7 — Puesto 7", "★☆☆☆☆ · 1/4", "25 d · antigua", "Insuficiente: Núcleo A · Pendiente: ubicación",
             ""],
            ["XA", "R-8 — Puesto 8", "☆☆☆☆☆ · 0/2", "0 d", "—", ""]])
        self.assertEqual([(f["busqueda_id"], f["vacante_id"], f["evaluacion_id"]) for f in tabla],
                         [("BUS-0002", f"VAC-000{n}", f"EVA-000{n}") for n in (3, 4, 5, 6, 7, 8)])
        self.assertEqual(len(self.ok("informe", "BUS-0001")), 1)

    def test_una_busqueda_inexistente_falla_con_un_mensaje_claro(self):
        r = self.correr("informe", "BUS-0099")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("BUS-0099", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_sin_una_zona_horaria_usable_en_04_dice_que_falta(self):
        self.ok("agregar", entrada={"busquedas": busqueda_ficticia()["busquedas"]})
        for zona, textos in ((None, ("zona_horaria", "/configurar", "paso 4")),
                             ("Region/Inexistente", ("Region/Inexistente", "tzdata"))):
            with self.subTest(zona=zona):
                (self.dir / "04_PREFERENCIAS_LABORALES.md").write_text(modulo_04(zona), encoding="utf-8")
                r = self.correr("informe", "BUS-0001")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                for t in textos:
                    self.assertIn(t, r.stderr)
                self.assertNotIn("Traceback", r.stderr)

    def test_el_umbral_de_antigua_sale_de_eval_acuerdos_en_08(self):
        modulo = self.dir / "08_EVALUACION_DE_VACANTES.md"
        texto = modulo.read_text(encoding="utf-8")
        linea = "- **Marca «antigua»:** a partir de 20 días publicada"
        self.assertEqual(texto.count(linea), 1)
        busqueda = busqueda_ficticia()
        busqueda["vacantes"][0].update(fecha_publicacion=hace(25), primera_deteccion=hace(0))
        self.ok("agregar", entrada=busqueda)
        self.assertEqual(self.ok("informe", "BUS-0001")[0]["antiguedad"], "25 d · antigua")
        # En cifras, con negritas o sin ellas.
        for nueva in ("a partir de 30 días", "a partir de **30 días**"):
            with self.subTest(nueva=nueva):
                modulo.write_text(texto.replace(linea, linea.replace("a partir de 20 días", nueva)), encoding="utf-8")
                self.assertEqual(self.ok("informe", "BUS-0001")[0]["antiguedad"], "25 d")
        self.ok("instantanea")
        self.assertIn("- **antigüedad:** 25 d\n", (self.dir / "instantanea" / "vacantes.md").read_text(encoding="utf-8"))

    def test_sin_acuerdo_en_08_el_umbral_es_de_20_dias(self):
        modulo = self.dir / "08_EVALUACION_DE_VACANTES.md"
        texto = modulo.read_text(encoding="utf-8")
        modulo.write_text(re.sub(r"^- \*\*Marca «antigua»:\*\*.*\n", "", texto, count=1, flags=re.M), encoding="utf-8")
        busqueda = busqueda_ficticia()
        busqueda["vacantes"][0].update(fecha_publicacion=hace(20), primera_deteccion=hace(0))
        self.ok("agregar", entrada=busqueda)
        self.assertEqual(self.ok("informe", "BUS-0001")[0]["antiguedad"], "20 d · antigua")

    def test_un_umbral_sin_numero_en_08_dice_donde_corregirlo(self):
        self.ok("agregar", entrada={"busquedas": busqueda_ficticia()["busquedas"]})
        modulo = self.dir / "08_EVALUACION_DE_VACANTES.md"
        texto = modulo.read_text(encoding="utf-8")
        modulo.write_text(texto.replace("a partir de 20 días publicada", "a partir de veinte días publicada", 1),
                          encoding="utf-8")
        # Las escrituras también la necesitan, para la instantánea: no escriben nada.
        otra = {"busquedas": [dict(busqueda_ficticia()["busquedas"][0], busqueda_id="BUS-0002")]}
        for argumentos, entrada in ((("informe", "BUS-0001"), None), (("agregar",), otra)):
            with self.subTest(orden=argumentos[0]):
                antes = self.archivo.read_bytes()
                r = self.correr(*argumentos, entrada=entrada)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                for t in ("08_EVALUACION_DE_VACANTES.md", "EVAL-ACUERDOS", "Marca «antigua»"):
                    self.assertIn(t, r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                self.assertEqual(self.archivo.read_bytes(), antes)


class Instantanea(CopiaFicticia):
    """La instantánea que lee el canal Web (11/REG-INSTANTANEA): informes.md y vacantes.md en instantanea/."""

    def setUp(self):
        super().setUp()
        self.ok("crear")
        self.carpeta = self.dir / "instantanea"

    def vista(self, nombre):
        return (self.carpeta / nombre).read_text(encoding="utf-8")

    def seccion(self, texto, encabezado):
        """La sección `## ...` que empieza con encabezado, hasta la siguiente."""
        m = re.search(rf"^## {re.escape(encabezado)}.*?(?=^## |\Z)", texto, re.M | re.S)
        self.assertIsNotNone(m, f"falta la sección «## {encabezado}»")
        return m.group(0)

    def test_agregar_y_actualizar_la_regeneran_y_un_rechazo_no_la_toca(self):
        self.assertFalse(self.carpeta.exists())
        self.ok("agregar", entrada=busqueda_ficticia())
        self.assertIn("«Puesto ficticio»", self.vista("vacantes.md"))
        self.ok("actualizar", entrada={"vacantes": [{"vacante_id": "VAC-0001", "titulo": "Título nuevo"}]})
        self.assertIn("«Título nuevo»", self.vista("vacantes.md"))
        self.assertNotIn("«Puesto ficticio»", self.vista("vacantes.md"))
        antes = {n: self.vista(n) for n in ("informes.md", "vacantes.md")}
        self.assertRechazaSinEscribir("agregar", {"vacantes": [{"vacante_id": "VAC-1"}]}, "vacante_id")
        self.assertRechazaSinEscribir("actualizar", {"vacantes": [{"vacante_id": "VAC-0099", "titulo": "x"}]},
                                      "VAC-0099")
        self.assertEqual({n: self.vista(n) for n in antes}, antes)

    def test_la_orden_instantanea_la_regenera_si_se_borro_o_se_edito(self):
        self.ok("agregar", entrada=busqueda_ficticia())
        original = self.vista("vacantes.md")
        (self.carpeta / "vacantes.md").write_text("editada a mano\n", encoding="utf-8")
        (self.carpeta / "informes.md").unlink()
        res = self.ok("instantanea")
        self.assertEqual(sorted(res["archivos"]), ["instantanea/informes.md", "instantanea/vacantes.md"])
        self.assertEqual(self.vista("vacantes.md").split("\n", 3)[3], original.split("\n", 3)[3])
        self.assertIn("BUS-0001", self.vista("informes.md"))

    def test_sin_zona_horaria_en_04_no_escribe_ni_el_archivo_ni_la_instantanea(self):
        (self.dir / "04_PREFERENCIAS_LABORALES.md").write_text(modulo_04(None), encoding="utf-8")
        antes = self.archivo.read_bytes()
        r = self.correr("agregar", entrada=busqueda_ficticia())
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("zona_horaria", r.stderr)
        self.assertEqual(self.archivo.read_bytes(), antes)
        self.assertFalse(self.carpeta.exists())

    def test_las_dos_vistas_llevan_la_fecha_de_exportacion(self):
        self.ok("agregar", entrada=busqueda_ficticia())
        for nombre in ("informes.md", "vacantes.md"):
            with self.subTest(nombre):
                encabezado = self.vista(nombre).split("\n## ", 1)[0]
                self.assertRegex(encabezado, rf"Exportada:\*\* {hoy().isoformat()} \d\d:\d\d \(UTC\)")
                self.assertIn("antigüedad está calculada a esa fecha", encabezado)
                self.assertIn("no se edita a mano", encabezado)

    def test_informes_trae_las_ultimas_10_busquedas_con_su_fila_y_su_tabla(self):
        busqueda = busqueda_ficticia()
        base = busqueda["busquedas"][0]
        busqueda["busquedas"] = [dict(base, busqueda_id=f"BUS-{n:04}", fecha_hora=f"2026-03-{n:02} 09:30",
                                      solicitud_alcance=f"Alcance {n}", cobertura_limitaciones=f"Cobertura {n}",
                                      no_revisado_pendientes=f"Pendientes {n}", comparacion_anterior=f"Comparación {n}")
                                 for n in range(1, 13)]
        busqueda["vacantes"][0].update(fecha_publicacion=hace(25), primera_deteccion=hace(0))
        busqueda["evaluaciones"].append(dict(busqueda["evaluaciones"][0], evaluacion_id="EVA-0002",
                                             vacante_id="VAC-0002", observacion_id="OBS-0002",
                                             condiciones="Excluida", condiciones_detalle="Duración: «6-month contract»",
                                             encaje="", cobertura="", nucleos=""))
        busqueda["informes"] = [{"busqueda_id": "BUS-0012", "vacante_id": "VAC-0001", "evaluacion_id": "EVA-0001"},
                                {"busqueda_id": "BUS-0012", "vacante_id": "VAC-0002", "evaluacion_id": "EVA-0002"}]
        self.ok("agregar", entrada=busqueda)
        texto = self.vista("informes.md")
        self.assertEqual(re.findall(r"^## (BUS-\d+)", texto, re.M), [f"BUS-{n:04}" for n in range(12, 2, -1)])
        ultima = self.seccion(texto, "BUS-0012")
        self.assertIn("2026-03-12 09:30", ultima.splitlines()[0])
        for valor in ("Alcance 12", "Cobertura 12", "Pendientes 12", "Comparación 12"):
            self.assertIn(valor, ultima)
        filas = [linea for linea in ultima.splitlines() if linea.startswith("|")]
        self.assertEqual(filas, [
            "| Vacante | Encaje | Antigüedad | Alertas |",
            "| --- | --- | --- | --- |",
            "| [000123 — Puesto ficticio](https://example.com/empleo/000123) | ★★★☆☆ · 3/4 | 25 d · antigua "
            "| Pendiente: remoto |",
            f"| sin Job ID — Otro puesto | — | ≥ {(hoy() - dt.date(2026, 3, 2)).days} d · antigua "
            "| Excluida: Duración: «6-month contract» |"])
        sin_informes = self.seccion(texto, "BUS-0011")
        self.assertFalse([linea for linea in sin_informes.splitlines() if linea.startswith("|")])
        self.assertIn("Sin vacantes evaluadas", sin_informes)

    def test_vacantes_trae_solo_las_evaluadas_no_cerradas_con_su_ultima_observacion_y_evaluacion(self):
        busqueda = busqueda_ficticia()
        busqueda["busquedas"].append(dict(busqueda["busquedas"][0], busqueda_id="BUS-0002"))
        busqueda["vacantes"].append(dict(busqueda["vacantes"][0], vacante_id="VAC-0003", job_id="000999",
                                         titulo="Puesto cerrado", ultima_observacion_id="OBS-0003"))
        busqueda["observaciones"] += [
            dict(busqueda["observaciones"][0], observacion_id="OBS-0003", vacante_id="VAC-0003",
                 estado_vigencia="Cerrada", motivo="«No longer accepting applications»"),
            dict(busqueda["observaciones"][0], observacion_id="OBS-0004", busqueda_id="BUS-0002",
                 fecha_verificacion="2026-03-09", motivo="Sigue en el listado")]
        busqueda["vacantes"][0]["ultima_observacion_id"] = "OBS-0004"
        busqueda["evaluaciones"] += [
            dict(busqueda["evaluaciones"][0], evaluacion_id="EVA-0002", vacante_id="VAC-0003",
                 observacion_id="OBS-0003"),
            dict(busqueda["evaluaciones"][0], evaluacion_id="EVA-0003", fecha_evaluacion="2026-03-09",
                 encaje="★★★★☆", cobertura="4/4")]
        # Los requisitos de otra observación de la misma vacante no son los de la evaluada.
        busqueda["observaciones"].append(dict(busqueda["observaciones"][0], observacion_id="OBS-0005",
                                              motivo="Otra lectura"))
        busqueda["habilidades_vacante"].append(dict(busqueda["habilidades_vacante"][0],
                                                    habilidad_observacion_id="HV-00009", observacion_id="OBS-0005",
                                                    habilidad_literal="Requisito de otra observación"))
        self.ok("agregar", entrada=busqueda)
        texto = self.vista("vacantes.md")
        # VAC-0002 no tiene evaluación y VAC-0003 está cerrada.
        self.assertEqual(re.findall(r"^## (.*)", texto, re.M), ["VAC-0001 · 000123 · EMP-XA · «Puesto ficticio»"])
        seccion = self.seccion(texto, "VAC-0001")
        for valor in ("<https://example.com/empleo/000123>", "Ciudad A1, País A", "Hybrid", "Dentro", "2026-02-20",
                      "2026-03-02", "### Última observación: OBS-0004", "2026-03-09", "Sigue en el listado",
                      "### Última evaluación: EVA-0003", "★★★★☆", "4/4", "Núcleo A: Directa",
                      "### Requisitos de OBS-0001", "Experience with Python"):
            self.assertIn(valor, seccion)
        # Ni el historial de observaciones, ni las evaluaciones anteriores, ni documentos.
        for ausente in ("En listado oficial", "EVA-0001", "Requisito de otra observación", "CV_ficticio.pdf",
                        "DOC-0001"):
            self.assertNotIn(ausente, texto)

    def test_los_requisitos_van_agrupados_por_frase_literal(self):
        busqueda = busqueda_ficticia()
        hv = busqueda["habilidades_vacante"][0]
        busqueda["habilidades_vacante"] = [
            dict(hv, habilidad_observacion_id="HV-00001", habilidad_literal="Python or R", habilidad_normalizada="Python"),
            dict(hv, habilidad_observacion_id="HV-00002", habilidad_literal="Excel | Sheets", habilidad_normalizada="Excel",
                 tipo_requisito="Deseable"),
            dict(hv, habilidad_observacion_id="HV-00003", habilidad_literal="Python or R", habilidad_normalizada="R"),
            dict(hv, habilidad_observacion_id="HV-00004", habilidad_literal="Strong *communication*",
                 habilidad_normalizada="", tipo_requisito="Ambiguo")]
        self.ok("agregar", entrada=busqueda)
        seccion = self.seccion(self.vista("vacantes.md"), "VAC-0001")
        self.assertIn("### Requisitos de OBS-0001", seccion)
        filas = [linea for linea in seccion.splitlines() if linea.startswith("|")]
        self.assertEqual(filas, [
            "| Frase literal | Normalizados | Tipo |",
            "| --- | --- | --- |",
            "| Python or R | Python; R | Obligatorio |",
            r"| Excel \| Sheets | Excel | Deseable |",
            r"| Strong \*communication\* | — | Ambiguo |"])

    def test_avisa_en_stderr_si_pasa_de_300_kb_sin_fallar(self):
        busqueda = busqueda_ficticia()
        hv = busqueda["habilidades_vacante"][0]
        busqueda["habilidades_vacante"] = [dict(hv, habilidad_observacion_id=f"HV-{n:05}",
                                                habilidad_literal=f"Requisito {n} " + "x" * 400) for n in range(1, 801)]
        r = self.correr("agregar", entrada=busqueda)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("300 KB", r.stderr)
        self.assertGreater(sum(f.stat().st_size for f in self.carpeta.iterdir()), 300 * 1024)
        self.ok("actualizar", entrada={"habilidades_vacante": [{"habilidad_observacion_id": f"HV-{n:05}",
                                                                "habilidad_literal": f"Requisito {n}"}
                                                               for n in range(1, 801)]})
        self.assertNotIn("300 KB", self.correr("instantanea").stderr)

    @unittest.skipIf(shutil.which("markdownlint-cli2") is None, "falta markdownlint-cli2")
    def test_pasa_markdownlint_sin_advertencias(self):
        busqueda = busqueda_ficticia()
        # Textos con Markdown, URLs sueltas y barras, como los que trae un anuncio.
        busqueda["vacantes"][0]["titulo"] = "Analyst [Remote] <EMEA> | #1 *team*:"
        busqueda["observaciones"][0]["motivo"] = "Visto en https://example.com/a_b_c y en `código`\nsegunda línea"
        busqueda["habilidades_vacante"][0]["habilidad_literal"] = "_SQL_ or ~~Excel~~ | > 3 years"
        self.ok("agregar", entrada=busqueda)
        shutil.copy(RAIZ / ".markdownlint-cli2.jsonc", self.dir)
        r = subprocess.run(["markdownlint-cli2", "--no-globs", "instantanea/informes.md", "instantanea/vacantes.md"],
                           cwd=self.dir, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
