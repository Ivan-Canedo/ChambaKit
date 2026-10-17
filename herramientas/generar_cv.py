#!/usr/bin/env python3
"""Genera un CV (FODT, PDF, DOCX, PNG y TXT) a partir del Markdown de 03 o de una adaptación.

Uso:
  python3 -I generar_cv.py ENTRADA.md --idioma es|en --salida DIR/NOMBRE [--borrador]

ENTRADA puede ser 03_CV_BASE.md (se toma la sección CV-ES o CV-EN) o un archivo con
solo el CV adaptado, con el mismo formato: ### por sección, **negritas**, viñetas «- ».
Los marcadores [CV-E##] y los <> de correos y URL se retiran. Requiere LibreOffice (soffice) y poppler-utils.

El color de acento sale del primer bloque ```json de la sección CV-PLANTILLA de
09_GENERACION_DE_CV.md, en la raíz de la copia: {"color_acento": "#RRGGBB"}. Si 09 no se puede
leer, no tiene el bloque o el color no es #RRGGBB, termina con código 2 sin generar nada. Si el
texto extraído del PDF no coincide con el contenido, termina con código 1.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from html import escape

MODULO_09 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "09_GENERACION_DE_CV.md")
TEXTO = "#1A1A1A"
GRIS = "#4D4D4D"
FUENTE = "Carlito"

ENCABEZADO = {"encabezado", "header"}
EXPERIENCIA = {"experiencia profesional", "professional experience"}


def error(mensaje):
    print(mensaje, file=sys.stderr)
    sys.exit(2)


def leer_acento(ruta):
    """Color de acento del primer bloque JSON de la sección CV-PLANTILLA de 09."""
    try:
        with open(ruta, encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        error(f"{ruta}: no se pudo leer el módulo 09, de donde sale el color del CV ({e.strerror}).")
    seccion = re.search(r"^## CV-PLANTILLA\b.*?(?=^## |\Z)", md, re.M | re.S)
    bloque = seccion and re.search(r"^```json\n(.*?)^```", seccion.group(0), re.M | re.S)
    if not bloque:
        error(f"{ruta}: falta el bloque de configuración (```json) en la sección CV-PLANTILLA.")
    try:
        config = json.loads(bloque.group(1))
    except ValueError as e:
        error(f"{ruta}: el bloque de CV-PLANTILLA no es JSON válido ({e}); debe ser un objeto con color_acento.")
    acento = config.get("color_acento") if isinstance(config, dict) else None
    if not isinstance(acento, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", acento):
        error(f"{ruta}: color_acento, en el bloque de CV-PLANTILLA, debe ser un color #RRGGBB; dice {acento!r}.")
    return acento


def extraer_cv(md, idioma):
    """Devuelve las líneas del CV: la sección CV-ES/CV-EN de 03 o el archivo completo."""
    marca = f"## CV-{idioma.upper()}"
    if marca in md:
        inicio = md.index(marca)
        md = md[md.index("\n", inicio) + 1:]
        fin = re.search(r"^## ", md, re.M)
        md = md[: fin.start()] if fin else md
    return md.splitlines()


def limpiar(texto):
    texto = re.sub(r"<((?:https?://|mailto:)[^<>\s]+|[^<>\s@]+@[^<>\s]+)>", r"\1", texto)
    return re.sub(r"\s*\[CV-E[^\]]*\]", "", texto).rstrip()


def en_linea(texto):
    """Markdown en línea (**negrita**) a XML de ODF."""
    partes = re.split(r"(\*\*.+?\*\*)", texto)
    xml = []
    for p in partes:
        if p.startswith("**") and p.endswith("**"):
            xml.append(f'<text:span text:style-name="B">{escape(p[2:-2], quote=False)}</text:span>')
        else:
            xml.append(escape(p, quote=False))
    return "".join(xml)


def bloques(lineas):
    """Convierte las líneas en una lista de (estilo, texto) y viñetas (nivel, texto)."""
    salida, seccion, i = [], None, 0
    while i < len(lineas):
        crudo = lineas[i]
        linea = limpiar(crudo)
        i += 1
        if not linea.strip():
            continue
        if linea.startswith("### "):
            seccion = linea[4:].strip()
            if seccion.lower() not in ENCABEZADO:
                salida.append(("Seccion", seccion))
            continue
        m = re.match(r"^(\s*)- (.*)$", linea)
        if m:
            salida.append(("Vineta", (1 if len(m.group(1)) >= 2 else 0, m.group(2))))
            continue
        texto = linea.strip()
        solo_negrita = re.fullmatch(r"\*\*[^*]+\*\*", texto)
        if seccion and seccion.lower() in ENCABEZADO:
            n = sum(1 for e in salida if e[0] in ("Nombre", "Titulo"))
            estilo = ("Nombre", "Titulo")[n] if solo_negrita and n < 2 else "Contacto"
            salida.append((estilo, texto.strip("*") if solo_negrita else texto))
        elif seccion and seccion.lower() in EXPERIENCIA and solo_negrita:
            salida.append(("Puesto", texto.strip("*")))
        elif salida and salida[-1][0] == "Puesto":
            salida.append(("PuestoDatos", texto))
        else:
            salida.append(("Cuerpo", texto))
    return salida


def estilos(tam, acento):
    t = tam
    def p(nombre, extra_p="", extra_t="", padre="Base"):
        return (f'<style:style style:name="{nombre}" style:family="paragraph" style:parent-style-name="{padre}">'
                f'<style:paragraph-properties {extra_p}/><style:text-properties {extra_t}/></style:style>')
    return "".join([
        '<style:style style:name="Base" style:family="paragraph">'
        '<style:paragraph-properties fo:margin-top="0pt" fo:margin-bottom="0pt" fo:line-height="113%" '
        'fo:hyphenation-ladder-count="no-limit" fo:orphans="2" fo:widows="2"/>'
        f'<style:text-properties style:font-name="{FUENTE}" fo:font-size="{t}pt" fo:color="{TEXTO}" '
        'fo:language="es" fo:country="MX" fo:hyphenate="false"/></style:style>',
        p("Nombre", 'fo:margin-bottom="1pt" fo:line-height="100%"', f'fo:font-size="{t + 9}pt" fo:font-weight="bold"'),
        p("Titulo", 'fo:margin-bottom="2pt"', f'fo:font-size="{t + 1}pt" fo:font-weight="bold" fo:color="{GRIS}"'),
        p("Contacto", f'fo:padding-bottom="5pt" fo:border-bottom="0.75pt solid {acento}" fo:margin-bottom="2pt"',
          f'fo:font-size="{t - 0.5}pt" fo:color="{GRIS}"'),
        p("Seccion", 'fo:margin-top="9pt" fo:margin-bottom="3pt" fo:keep-with-next="always"',
          f'fo:font-size="{t}pt" fo:font-weight="bold" fo:color="{acento}" fo:text-transform="uppercase" fo:letter-spacing="0.02cm"'),
        p("Cuerpo", 'fo:margin-bottom="3pt"'),
        p("Puesto", 'fo:keep-with-next="always"', f'fo:font-size="{t + 0.5}pt" fo:font-weight="bold"'),
        p("PuestoDatos", 'fo:margin-bottom="3pt" fo:keep-with-next="always"', f'fo:font-size="{t - 0.5}pt" fo:color="{GRIS}"'),
        p("Vineta", 'fo:margin-bottom="2.5pt"'),
        p("Borrador", 'fo:margin-bottom="4pt"', f'fo:font-size="{t - 2}pt" fo:color="{GRIS}"'),
        '<style:style style:name="B" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>',
        '<text:list-style style:name="Lista">'
        '<text:list-level-style-bullet text:level="1" text:bullet-char="•">'
        '<style:list-level-properties text:list-level-position-and-space-mode="label-alignment">'
        '<style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.42cm" '
        'fo:text-indent="-0.38cm" fo:margin-left="0.42cm"/></style:list-level-properties>'
        f'<style:text-properties fo:color="{GRIS}"/></text:list-level-style-bullet>'
        '<text:list-level-style-bullet text:level="2" text:bullet-char="–">'
        '<style:list-level-properties text:list-level-position-and-space-mode="label-alignment">'
        '<style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.84cm" '
        'fo:text-indent="-0.38cm" fo:margin-left="0.84cm"/></style:list-level-properties>'
        f'<style:text-properties fo:color="{GRIS}"/></text:list-level-style-bullet>'
        '</text:list-style>',
    ])


def cuerpo(bl, borrador):
    xml = []
    if borrador:
        xml.append(f'<text:p text:style-name="Borrador">{escape(borrador, quote=False)}</text:p>')
    i = 0
    while i < len(bl):
        estilo, contenido = bl[i]
        if estilo != "Vineta":
            xml.append(f'<text:p text:style-name="{estilo}">{en_linea(contenido)}</text:p>')
            i += 1
            continue
        xml.append('<text:list text:style-name="Lista">')
        while i < len(bl) and bl[i][0] == "Vineta":
            nivel, texto = bl[i][1]
            item = f'<text:p text:style-name="Vineta">{en_linea(texto)}</text:p>'
            if nivel == 1:
                item = f'<text:list><text:list-item>{item}</text:list-item></text:list>'
                xml[-1] = xml[-1].replace("</text:list-item>", "") + item + "</text:list-item>"
            else:
                xml.append(f'<text:list-item>{item}</text:list-item>')
            i += 1
        xml.append("</text:list>")
    return "".join(xml)


def fodt(bl, tam, margen, borrador, acento):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
 xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
 office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.text">
<office:font-face-decls><style:font-face style:name="{FUENTE}" svg:font-family="{FUENTE}"/></office:font-face-decls>
<office:styles>{estilos(tam, acento)}</office:styles>
<office:automatic-styles><style:page-layout style:name="Pagina">
<style:page-layout-properties fo:page-width="21.59cm" fo:page-height="27.94cm" fo:margin-top="{margen[0]}cm"
 fo:margin-bottom="{margen[0]}cm" fo:margin-left="{margen[1]}cm" fo:margin-right="{margen[1]}cm"/>
</style:page-layout></office:automatic-styles>
<office:master-styles><style:master-page style:name="Standard" style:page-layout-name="Pagina"/></office:master-styles>
<office:body><office:text>{cuerpo(bl, borrador)}</office:text></office:body>
</office:document>
'''


def palabras(texto):
    return re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ’'+.#/-]+", texto)


def texto_plano(bl):
    out = []
    for estilo, c in bl:
        t = c[1] if estilo == "Vineta" else c
        out.append(t.replace("**", ""))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("--idioma", choices=["es", "en"], required=True)
    ap.add_argument("--salida", required=True, help="ruta sin extensión")
    ap.add_argument("--tam", type=float, default=10.5)
    ap.add_argument("--margen", type=float, nargs=2, default=[1.4, 1.7], metavar=("VERT", "HORIZ"))
    ap.add_argument("--borrador", default="", help="línea de aviso al inicio (muestras)")
    a = ap.parse_args()

    acento = leer_acento(MODULO_09)
    with open(a.entrada, encoding="utf-8") as f:
        bl = bloques(extraer_cv(f.read(), a.idioma))
    destino = os.path.abspath(a.salida)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base = os.path.basename(destino)
    with open(destino + ".fodt", "w", encoding="utf-8") as f:
        f.write(fodt(bl, a.tam, a.margen, a.borrador, acento))

    perfil = tempfile.mkdtemp(prefix="lo_")
    soffice = ["soffice", f"-env:UserInstallation=file://{perfil}", "--headless", "--convert-to"]
    for fmt in ("pdf", "docx:MS Word 2007 XML"):
        subprocess.run(soffice + [fmt, "--outdir", os.path.dirname(destino), destino + ".fodt"],
                       check=True, capture_output=True, timeout=180)
    subprocess.run(["pdftoppm", "-png", "-r", "80", destino + ".pdf", destino + "_p"], check=True)
    subprocess.run(["pdftotext", destino + ".pdf", destino + ".txt"], check=True)

    info = subprocess.run(["pdfinfo", destino + ".pdf"], capture_output=True, text=True).stdout
    paginas = re.search(r"Pages:\s+(\d+)", info).group(1)
    fuentes = subprocess.run(["pdffonts", destino + ".pdf"], capture_output=True, text=True).stdout
    crudo = subprocess.run(["pdftotext", "-raw", destino + ".pdf", "-"], capture_output=True, text=True).stdout
    # Un compuesto partido al final de línea («state-of-» / «the-art») puede unirse sin guion al extraerlo.
    partidos = re.findall(r"(\S+-)\n(\S+)", crudo)
    crudo = re.sub(r"(\S-)\n", r"\1", crudo)
    esperado = palabras(texto_plano(bl))
    obtenido = palabras(crudo)
    if a.borrador:
        obtenido = obtenido[len(palabras(a.borrador)):]
    iguales = [w.lower() for w in esperado] == [w.lower() for w in obtenido]
    print(f"{base}: {paginas} página(s), {len(esperado)} palabras")
    print("Fuentes incrustadas:", "sí" if all(l.split()[-5] == "yes" for l in fuentes.splitlines()[2:]) else "revisar")
    print("Texto extraído = contenido, en el mismo orden:", "sí" if iguales else "NO")
    for antes, despues in partidos:
        print(f"  revisar: compuesto partido al final de línea «{antes} {despues}»")
    if not iguales:
        for k, (x, y) in enumerate(zip(esperado, obtenido)):
            if x.lower() != y.lower():
                print(f"  primera diferencia en la palabra {k}: esperado {x!r}, extraído {y!r}")
                break
        else:
            print(f"  longitudes distintas: {len(esperado)} frente a {len(obtenido)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
