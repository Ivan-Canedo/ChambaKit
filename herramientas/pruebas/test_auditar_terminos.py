"""Pruebas de la auditoría de términos, por su línea de comandos y sin red.

Uso:
    python3 -I -B -m unittest discover -s herramientas/pruebas
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "auditar_terminos.py"


class AuditoriaDeTerminos(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def escribir(self, ruta, contenido):
        archivo = self.dir / ruta
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(contenido, encoding="utf-8")
        return archivo

    def auditar(self, terminos, *argumentos):
        lista = self.escribir("terminos.txt", terminos)
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(lista), *argumentos],
            capture_output=True, text=True, cwd=self.dir,
        )

    def test_reporta_la_ruta_y_la_linea_de_cada_coincidencia(self):
        self.escribir("modulo.md", "# Perfil\n\nTrabaja en Zeta Norte desde 2020.\n")
        r = self.auditar("Zeta Norte\n", "modulo.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("modulo.md:3:", r.stdout)
        self.assertIn("Zeta Norte", r.stdout)

    def test_sin_coincidencias_termina_sin_error_y_sin_salida(self):
        self.escribir("limpio.md", "# Plantilla\n\nSin datos de nadie.\n")
        r = self.auditar("Zeta Norte\n", "limpio.md")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_no_distingue_mayusculas_ni_acentos_y_reporta_el_texto_original(self):
        self.escribir("cv.md", "**JOSÉ PEÑA**\nArchivo: jose_pena_cv.pdf\n")
        r = self.auditar("José Peña\n", "cv.md")
        self.assertIn("cv.md:1:3: José Peña «JOSÉ PEÑA»", r.stdout)
        self.assertIn("cv.md:2:10: José Peña «jose_pena»", r.stdout)

    def test_encuentra_variantes_juntas_o_con_separador_entre_letras_y_numeros(self):
        self.escribir("a.md", "Usuario JosePena\nVacante ID-12345\nOtra id 12345\n")
        r = self.auditar("José Peña\nID12345\n", "a.md")
        self.assertIn("a.md:1:9: José Peña «JosePena»", r.stdout)
        self.assertIn("a.md:2:9: ID12345 «ID-12345»", r.stdout)
        self.assertIn("a.md:3:6: ID12345 «id 12345»", r.stdout)

    def test_busca_palabras_completas(self):
        self.escribir("metodo.md", "Un reporte corto desde Portugal.\n")
        r = self.auditar("ORT\n", "metodo.md")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_encuentra_el_termino_dentro_de_urls_e_identificadores(self):
        self.escribir("ficha.md", "<https://ort.com/jobs> y `ID-ORT` y Portal_ORT_2\n")
        r = self.auditar("ORT\n", "ficha.md")
        self.assertEqual(r.stdout.count("«ort»") + r.stdout.count("«ORT»"), 3, r.stdout)

    def test_ignora_comentarios_y_lineas_vacias_de_la_lista(self):
        self.escribir("nota.md", "## Empresas del catálogo\n")
        r = self.auditar("# Empresas del catálogo\n\nZeta Norte\n", "nota.md")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_recorre_carpetas_y_omite_las_excluidas_y_git(self):
        self.escribir("docs/adr/0001.md", "Zeta Norte\n")
        self.escribir(".scratch/originales/02.md", "Zeta Norte\n")
        self.escribir(".git/config", "Zeta Norte\n")
        r = self.auditar("Zeta Norte\n", ".", "--excluir", ".scratch")
        self.assertEqual(r.returncode, 1)
        self.assertIn("docs/adr/0001.md:1:1:", r.stdout)
        self.assertNotIn(".scratch", r.stdout)
        self.assertNotIn(".git", r.stdout)

    def test_una_excepcion_permite_solo_su_frase_literal(self):
        self.escribir("LICENSE", "Copyright (c) 2026 Jose-Pena\n")
        self.escribir("README.md", "Plantilla de José Peña, en github.com/jose-pena\n")
        r = self.auditar("Peña\n!Jose-Pena\n", "LICENSE", "README.md")
        self.assertNotIn("LICENSE", r.stdout)
        self.assertIn("README.md:1:19: Peña «Peña»", r.stdout)
        self.assertNotIn("«pena»", r.stdout)

    def test_avisa_de_los_binarios_que_no_puede_revisar(self):
        (self.dir / "registros.xlsx").write_bytes(b"PK\x03\x04\x14\x00\xff\xfe Zeta Norte")
        self.escribir("limpio.md", "Sin datos.\n")
        r = self.auditar("Zeta Norte\n", ".")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("registros.xlsx", r.stderr)
        self.assertIn("binario", r.stderr)

    def test_el_conteo_da_las_coincidencias_de_cada_termino_incluso_cero(self):
        self.escribir("a.md", "Zeta Norte y ZETA NORTE.\n")
        self.escribir("b.md", "zeta_norte\n")
        r = self.auditar("Zeta Norte\nFulano\n", "a.md", "b.md", "--conteo")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "3\tZeta Norte\n0\tFulano\n")

    def test_una_ruta_inexistente_es_un_error_y_no_una_coincidencia(self):
        r = self.auditar("Zeta Norte\n", "no_existe.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no_existe.md", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_rechaza_un_termino_sin_letras_ni_numeros(self):
        self.escribir("a.md", "R&D\n")
        r = self.auditar("&\n", "a.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("«&»", r.stderr)


if __name__ == "__main__":
    unittest.main()
