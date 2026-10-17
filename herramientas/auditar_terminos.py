#!/usr/bin/env python3
"""Auditoría de términos: busca una lista de términos en archivos y reporta cada coincidencia.

Uso:
    python3 -I herramientas/auditar_terminos.py TERMINOS RUTA [RUTA ...] [--excluir RUTA] [--conteo]

TERMINOS es un archivo de texto con un término por línea; el script no lleva términos dentro.
Las líneas vacías y las que empiezan con # se ignoran. Las que empiezan con ! son excepciones:
una frase literal permitida (solo sin distinguir mayúsculas), cuyas coincidencias no se reportan.

Los términos se buscan sin distinguir mayúsculas ni acentos, como palabras completas; sus partes
pueden ir juntas o separadas por signos (ver `patron`). Las carpetas se recorren sin entrar en
.git, y la propia lista no se revisa. Los binarios no se revisan: se avisan en stderr para
revisar sus metadatos aparte.

Cada coincidencia sale en stdout como `ruta:línea:columna: término «texto»`; con --conteo, una
línea por término con su número de coincidencias, incluso cero.
Termina con 0 si no hay coincidencias, 1 si las hay y 2 si hubo un error (ruta inexistente,
archivo ilegible o término sin letras ni números). Solo biblioteca estándar.
"""
import argparse
import os
import re
import sys
import unicodedata

LETRA_O_DIGITO = r"[^\W_]"


def normalizar(texto):
    """Sin acentos y en minúsculas. Devuelve el texto y, por cada carácter, su posición original."""
    salida, posiciones = [], []
    for i, c in enumerate(texto):
        for d in unicodedata.normalize("NFKD", c).casefold():
            if not unicodedata.combining(d):
                salida.append(d)
                posiciones.append(i)
    return "".join(salida), posiciones


def partes(termino):
    """Tramos de letras o de dígitos del término normalizado."""
    return re.findall(r"[^\W\d_]+|\d+", normalizar(termino)[0])


def patron(termino):
    """El término como palabra completa. Sus partes pueden ir juntas o separadas por signos,
    espacios o guiones bajos: «José Peña» encuentra `JosePena` y `jose_pena`, y «ID12345»
    encuentra `ID-12345`."""
    cuerpo = r"[\W_]*".join(map(re.escape, partes(termino)))
    return re.compile(f"(?<!{LETRA_O_DIGITO}){cuerpo}(?!{LETRA_O_DIGITO})")


def leer_lista(ruta):
    """Devuelve (términos, excepciones) del archivo de la lista."""
    with open(ruta, encoding="utf-8") as f:
        lineas = [linea.strip() for linea in f]
    lineas = [linea for linea in dict.fromkeys(lineas) if linea and not linea.startswith("#")]
    return ([linea for linea in lineas if not linea.startswith("!")],
            [linea[1:].strip() for linea in lineas if linea.startswith("!")])


def coincidencias(contenido, terminos, excepciones):
    """(término, inicio, fin) de cada coincidencia en el texto original, salvo las que caen
    dentro de una excepción. `terminos` son pares (término, patrón)."""
    normal, posiciones = normalizar(contenido)
    permitidos = [m.span() for e in excepciones
                  for m in re.finditer(re.escape(e), contenido, re.IGNORECASE)]
    for termino, regex in terminos:
        for m in regex.finditer(normal):
            inicio, fin = posiciones[m.start()], posiciones[m.end() - 1] + 1
            if not any(a <= inicio and fin <= b for a, b in permitidos):
                yield termino, inicio, fin


def archivos(rutas, excluidas):
    """Los archivos de las rutas, recorriendo carpetas. Omite .git y las rutas excluidas."""
    fuera = {os.path.realpath(e) for e in excluidas}

    def excluida(ruta):
        return os.path.realpath(ruta) in fuera

    for ruta in rutas:
        if excluida(ruta):
            continue
        if not os.path.isdir(ruta):
            yield os.path.normpath(ruta)
            continue
        for base, carpetas, nombres in os.walk(ruta):
            carpetas[:] = sorted(c for c in carpetas
                                 if c != ".git" and not excluida(os.path.join(base, c)))
            for nombre in sorted(nombres):
                if not excluida(os.path.join(base, nombre)):
                    yield os.path.normpath(os.path.join(base, nombre))


def main():
    ap = argparse.ArgumentParser(description="Busca una lista de términos en archivos.")
    ap.add_argument("lista", help="archivo con un término por línea")
    ap.add_argument("rutas", nargs="+", help="archivos o carpetas que se revisan")
    ap.add_argument("--excluir", action="append", default=[], metavar="RUTA",
                    help="archivo o carpeta que no se revisa (se puede repetir)")
    ap.add_argument("--conteo", action="store_true",
                    help="en lugar de cada coincidencia, cuántas tiene cada término (incluso cero)")
    args = ap.parse_args()

    faltantes = [r for r in [args.lista] + args.rutas if not os.path.exists(r)]
    if faltantes:
        ap.error("no existe: " + ", ".join(faltantes))
    textos, excepciones = leer_lista(args.lista)
    vacios = [t for t in textos if not partes(t)]
    if vacios:
        ap.error("términos sin letras ni números: " + ", ".join(f"«{t}»" for t in vacios))
    terminos = [(t, patron(t)) for t in textos]

    conteo = dict.fromkeys(textos, 0)
    errores = 0
    for ruta in archivos(args.rutas, args.excluir + [args.lista]):
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = f.read()
        except UnicodeDecodeError:
            print(f"{ruta}: binario, no revisado; revisar sus metadatos aparte", file=sys.stderr)
            continue
        except OSError as e:
            print(f"{ruta}: no se pudo leer ({e.strerror})", file=sys.stderr)
            errores += 1
            continue
        for termino, inicio, fin in coincidencias(contenido, terminos, excepciones):
            conteo[termino] += 1
            if not args.conteo:
                linea = contenido.count("\n", 0, inicio) + 1
                columna = inicio - contenido.rfind("\n", 0, inicio)
                print(f"{ruta}:{linea}:{columna}: {termino} «{contenido[inicio:fin]}»")
    if args.conteo:
        for termino, n in conteo.items():
            print(f"{n}\t{termino}")
    if errores:
        return 2
    return 1 if any(conteo.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
