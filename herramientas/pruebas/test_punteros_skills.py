"""Pruebas de los punteros de las skills, sin red.

Uso:
    python3 -I -B -m unittest discover -s herramientas/pruebas

El texto completo de cada skill vive en .claude/skills/<nombre>/SKILL.md, que solo carga Claude Code.
Otros agentes (Antigravity, Gemini CLI) leen .agents/skills/, donde cada skill tiene un puntero con el
mismo name y la misma description, que remite a la skill completa. A diferencia de las demás pruebas,
esta no llama a un script: lee la estructura del repo, para que las dos ubicaciones no se
desincronicen en silencio.
"""
import pathlib
import unittest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
COMPLETAS = RAIZ / ".claude" / "skills"
PUNTEROS = RAIZ / ".agents" / "skills"


def skills(carpeta):
    """Nombres de las carpetas de carpeta que tienen un SKILL.md."""
    return sorted(d.name for d in carpeta.iterdir() if (d / "SKILL.md").is_file()) if carpeta.is_dir() else []


def leer_skill(archivo):
    """Frontmatter (como diccionario de líneas «clave: valor») y cuerpo de un SKILL.md."""
    texto = archivo.read_text(encoding="utf-8").replace("\r\n", "\n")
    _, frontmatter, cuerpo = texto.split("---\n", 2)
    campos = dict(linea.split(": ", 1) for linea in frontmatter.splitlines() if ": " in linea)
    return campos, cuerpo


class PunterosDeSkills(unittest.TestCase):
    def test_hay_skills_completas(self):
        self.assertTrue(skills(COMPLETAS))

    def test_cada_skill_completa_tiene_su_puntero(self):
        faltan = sorted(set(skills(COMPLETAS)) - set(skills(PUNTEROS)))
        self.assertEqual(faltan, [], "skills de .claude/skills/ sin puntero en .agents/skills/")

    def test_no_hay_punteros_sin_skill_completa(self):
        sobran = sorted(set(skills(PUNTEROS)) - set(skills(COMPLETAS)))
        self.assertEqual(sobran, [], "punteros de .agents/skills/ sin skill en .claude/skills/")

    def test_name_y_description_coinciden(self):
        for nombre in sorted(set(skills(COMPLETAS)) & set(skills(PUNTEROS))):
            with self.subTest(skill=nombre):
                completa, _ = leer_skill(COMPLETAS / nombre / "SKILL.md")
                puntero, _ = leer_skill(PUNTEROS / nombre / "SKILL.md")
                for campo in ("name", "description"):
                    self.assertIn(campo, completa)
                    self.assertEqual(puntero.get(campo), completa[campo], f"{campo} distinto")

    def test_el_puntero_cita_la_ruta_de_la_skill_completa(self):
        for nombre in skills(PUNTEROS):
            with self.subTest(skill=nombre):
                _, cuerpo = leer_skill(PUNTEROS / nombre / "SKILL.md")
                self.assertIn(f".claude/skills/{nombre}/SKILL.md", cuerpo)


if __name__ == "__main__":
    unittest.main()
