"""Pruebas del generador de CV, por su línea de comandos y sin red.

Uso:
    python3 -I -B -m unittest discover -s herramientas/pruebas

Las que generan el CV se saltan si faltan LibreOffice o poppler.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "herramientas" / "generar_cv.py"
HERRAMIENTAS_CV = ("soffice", "pdftoppm", "pdftotext", "pdfinfo", "pdffonts")
FALTAN_HERRAMIENTAS = not all(shutil.which(h) for h in HERRAMIENTAS_CV)

CV_MINIMO = """### Encabezado

**Nombre Apellido**
**Título descriptivo**
Ciudad, País · <nombre@example.com>

### Experiencia profesional

**Empresa — Cargo**
Ciudad, País · 2020–actualidad

- Responsabilidad con su resultado.
"""


def modulo_09(bloque):
    return f"# 09 — Generación de CV\n\n## CV-PLANTILLA — Presentación\n\nDiseño.\n\n{bloque}\n"


class GeneradorDeCV(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def copia(self, contenido_09):
        """Una copia ficticia con el script, un CV mínimo y, si hay contenido, un 09 con él."""
        (self.dir / "herramientas").mkdir(exist_ok=True)
        shutil.copy(SCRIPT, self.dir / "herramientas")
        if contenido_09 is not None:
            (self.dir / "09_GENERACION_DE_CV.md").write_text(contenido_09, encoding="utf-8")
        (self.dir / "cv.md").write_text(CV_MINIMO, encoding="utf-8")

    def generar_en_la_copia(self):
        return self.generar(self.dir / "herramientas" / "generar_cv.py", self.dir / "cv.md")

    def generar(self, script, entrada, idioma="es"):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(script), str(entrada), "--idioma", idioma,
             "--salida", str(self.dir / "salida" / f"cv_{idioma}")],
            capture_output=True, text=True, timeout=300,
        )

    @unittest.skipIf(FALTAN_HERRAMIENTAS, "faltan LibreOffice o poppler")
    def test_el_esqueleto_de_03_genera_pdf_y_docx_y_pasa_los_controles(self):
        for idioma in ("es", "en"):
            with self.subTest(idioma=idioma):
                r = self.generar(SCRIPT, RAIZ / "03_CV_BASE.md", idioma)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("Fuentes incrustadas: sí", r.stdout)
                self.assertIn("Texto extraído = contenido, en el mismo orden: sí", r.stdout)
                for extension in ("pdf", "docx"):
                    self.assertTrue((self.dir / "salida" / f"cv_{idioma}.{extension}").is_file())

    @unittest.skipIf(FALTAN_HERRAMIENTAS, "faltan LibreOffice o poppler")
    def test_el_cv_usa_el_color_de_09(self):
        self.copia(modulo_09('```json\n{\n  "color_acento": "#123456"\n}\n```'))
        r = self.generar_en_la_copia()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        estilos = zipfile.ZipFile(self.dir / "salida" / "cv_es.docx").read("word/styles.xml").decode()
        colores = re.findall(r'w:color(?: w:val)?="(\w{6})"', estilos)
        # El acento va en dos lugares: los títulos de sección y la línea bajo el contacto.
        self.assertEqual(colores.count("123456"), 2, colores)

    def test_sin_el_bloque_de_09_falla_con_un_mensaje_claro_y_no_genera_nada(self):
        self.copia(modulo_09("El titular todavía no elige color."))
        r = self.generar_en_la_copia()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("09_GENERACION_DE_CV.md", r.stderr)
        self.assertIn("CV-PLANTILLA", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((self.dir / "salida").exists())

    def test_sin_09_falla_con_un_mensaje_claro(self):
        self.copia(None)
        r = self.generar_en_la_copia()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("09_GENERACION_DE_CV.md", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_un_color_que_no_es_rrggbb_falla_con_un_mensaje_claro(self):
        for bloque in ('{"color_acento": "rojo"}', '{"color": "#123456"}', '["#123456"]',
                       '{"color_acento": "#123456",}'):
            with self.subTest(bloque=bloque):
                self.copia(modulo_09(f"```json\n{bloque}\n```"))
                r = self.generar_en_la_copia()
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("CV-PLANTILLA", r.stderr)
                self.assertIn("color_acento", r.stderr)
                self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
