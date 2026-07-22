# MenuTitle: Copy instance name to Style Linking and append Italic
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs

font = Glyphs.font
if not font:
    raise Exception("No hay fuente abierta.")

for instance in font.instances:
    if not instance.active:
        continue

    original_name = instance.name or ""

    # Copia el nombre al campo Style Linking
    instance.linkStyle = original_name

    # Añade Italic al nombre si no lo tiene
    if "Italic" not in original_name.split():
        instance.name = original_name + " Italic"

    # Marca el checkbox de Italic
    instance.isItalic = True

print("Hecho.")