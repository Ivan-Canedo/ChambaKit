"""Pruebas del hook de la nube, sin red.

Uso:
    python3 -I -B -m unittest discover -s herramientas/pruebas

El hook SessionStart de .claude/settings.json corre herramientas/preparar_nube.sh, que en Code en
la nube instala las herramientas y crea .venv. La instalación real necesita root y red, así que no se
prueba aquí. Lo que se prueba es que en Code local no hace nada: el comando, tal como lo lee de la
configuración del proyecto, corre con bash en una copia ficticia sin CLAUDE_CODE_REMOTE, sale con 0,
no imprime nada y no crea ningún archivo. El camino de la nube corre con comandos falsos en el PATH
(apt-get, npm, python3…) que anotan sus llamadas, para ver qué se instala, qué se salta y qué avisa.
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CONFIGURACION = RAIZ / ".claude" / "settings.json"
SCRIPT = RAIZ / "herramientas" / "preparar_nube.sh"


def comandos_del_hook():
    """Comandos de los hooks SessionStart de la configuración del proyecto."""
    configuracion = json.loads(CONFIGURACION.read_text(encoding="utf-8"))
    return [hook["command"]
            for grupo in configuracion["hooks"]["SessionStart"]
            for hook in grupo["hooks"]]


def archivos(carpeta):
    """Rutas relativas de todo lo que hay bajo carpeta."""
    return sorted(str(p.relative_to(carpeta)) for p in pathlib.Path(carpeta).rglob("*"))


def copia_ficticia(prueba):
    """Carpeta temporal con solo herramientas/preparar_nube.sh; se borra al terminar la prueba."""
    copia = pathlib.Path(tempfile.mkdtemp())
    prueba.addCleanup(shutil.rmtree, copia)
    (copia / "herramientas").mkdir()
    shutil.copy(SCRIPT, copia / "herramientas")
    return copia


class HookFueraDeLaNube(unittest.TestCase):
    def setUp(self):
        self.copia = str(copia_ficticia(self))
        self.antes = archivos(self.copia)

    def correr(self, comando, **variables):
        entorno = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_REMOTE"}
        entorno.update(CLAUDE_PROJECT_DIR=self.copia, **variables)
        return subprocess.run(["bash", "-c", comando], cwd=self.copia, env=entorno,
                              capture_output=True, text=True, timeout=60)

    def test_hay_un_hook_sessionstart(self):
        self.assertTrue(comandos_del_hook())

    def test_el_comando_no_lleva_rutas_de_la_maquina(self):
        for comando in comandos_del_hook():
            with self.subTest(comando=comando):
                self.assertIn("$CLAUDE_PROJECT_DIR", comando)
                self.assertNotIn(str(RAIZ), comando)

    def test_sin_la_variable_no_hace_nada(self):
        for comando in comandos_del_hook():
            with self.subTest(comando=comando):
                resultado = self.correr(comando)
                self.assertEqual(resultado.returncode, 0)
                self.assertEqual(resultado.stdout + resultado.stderr, "")
                self.assertEqual(archivos(self.copia), self.antes)

    def test_con_otro_valor_de_la_variable_no_hace_nada(self):
        for comando in comandos_del_hook():
            with self.subTest(comando=comando):
                resultado = self.correr(comando, CLAUDE_CODE_REMOTE="false")
                self.assertEqual(resultado.returncode, 0)
                self.assertEqual(resultado.stdout + resultado.stderr, "")
                self.assertEqual(archivos(self.copia), self.antes)

    def test_el_script_solo_tampoco_hace_nada_sin_la_variable(self):
        resultado = self.correr('bash "$CLAUDE_PROJECT_DIR/herramientas/preparar_nube.sh"')
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout + resultado.stderr, "")
        self.assertEqual(archivos(self.copia), self.antes)


# Comandos falsos para el camino de la nube: anotan cada llamada en $LLAMADAS y se comportan según
# las variables de la prueba. Así se ve qué intenta instalar el script sin root ni red.
FALSOS = {
    "id": 'echo 0',
    "dpkg": '[ -n "$INSTALADO" ]',
    "apt-get": 'echo "apt-get $*" >> "$LLAMADAS"; [ -z "$FALLA_APT" ] || { echo "E: sin red"; exit 100; }',
    "npm": 'echo "npm $*" >> "$LLAMADAS"',
    "markdownlint-cli2": '[ -z "$INSTALADO" ] || echo "markdownlint-cli2 v0 (falso)"',
    "python3": ('echo "python3 $*" >> "$LLAMADAS"; mkdir -p .venv/bin; '
                'printf "#!/bin/sh\\n[ \\"\\$1\\" = -I ] || echo pip >> \\"$LLAMADAS\\"\\n" > .venv/bin/python; '
                'chmod +x .venv/bin/python'),
}


class HookEnLaNube(unittest.TestCase):
    """Camino de la nube con comandos falsos; la instalación real se comprueba a mano en la nube."""

    def setUp(self):
        self.copia = copia_ficticia(self)
        self.bin = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.bin)
        for nombre, cuerpo in FALSOS.items():
            falso = self.bin / nombre
            falso.write_text(f"#!/bin/sh\n{cuerpo}\n", encoding="utf-8")
            falso.chmod(0o755)
        self.llamadas = self.bin / "llamadas.txt"
        self.llamadas.touch()

    def correr(self, **variables):
        # Los falsos van primero, pero /usr/bin y /bin se quedan: en Fedora, bash puede cargar
        # /etc/bashrc, cuyo command_not_found_handle llama a gettext; si un comando falta y gettext
        # tampoco está en el PATH, el manejador se llama a sí mismo y bifurca bash sin fin.
        entorno = {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "CLAUDE_CODE_REMOTE": "true",
            "CLAUDE_PROJECT_DIR": str(self.copia),
            "LLAMADAS": str(self.llamadas),
            **variables,
        }
        comando = comandos_del_hook()[0]
        resultado = subprocess.run(["bash", "-c", comando], cwd=self.copia, env=entorno,
                                   capture_output=True, text=True, timeout=60)
        return resultado, self.llamadas.read_text(encoding="utf-8")

    def test_en_una_maquina_limpia_instala_todo_y_crea_venv(self):
        resultado, llamadas = self.correr()
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("listos", resultado.stdout)
        for paquete in ("poppler-utils", "fonts-crosextra-carlito", "libreoffice-writer-nogui"):
            self.assertIn(paquete, llamadas)
        self.assertIn("npm install -g markdownlint-cli2", llamadas)
        self.assertIn("python3 -m venv .venv", llamadas)
        self.assertIn("pip", llamadas)

    def test_se_salta_lo_ya_instalado_y_un_venv_con_openpyxl(self):
        (self.copia / ".venv" / "bin").mkdir(parents=True)
        python = self.copia / ".venv" / "bin" / "python"
        python.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        python.chmod(0o755)
        resultado, llamadas = self.correr(INSTALADO="1")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("listos", resultado.stdout)
        self.assertEqual(llamadas, "")

    def test_si_una_parte_falla_avisa_que_fallo_sigue_y_sale_con_0(self):
        resultado, llamadas = self.correr(FALLA_APT="1")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("apt no instaló", resultado.stdout)
        self.assertIn("E: sin red", resultado.stdout)
        self.assertNotIn("listos", resultado.stdout)
        self.assertIn("npm install -g markdownlint-cli2", llamadas)
        self.assertIn("python3 -m venv .venv", llamadas)


if __name__ == "__main__":
    unittest.main()
