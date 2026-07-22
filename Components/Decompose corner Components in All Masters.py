# MenuTitle: Decompose corner Components in All Masters
# -*- coding: utf-8 -*-
# Description: Descompon tots els corner components a tots els mestres.
# Author: Gemini & Josep Patau



font = Glyphs.font

if not font:
    raise RuntimeError("No hi ha cap font oberta.")

selectedGlyphs = {layer.parent for layer in font.selectedLayers}
if not selectedGlyphs:
    raise RuntimeError("Selecciona almenys un glif abans d'executar l'script.")

print("Descomponen corner components de tots els masters...\n")

glyphCount = 0
layerCount = 0

for glyph in selectedGlyphs:
    glyphCount += 1
    glyph.beginUndo()
    try:
        for layer in glyph.layers:
            # Comprova si la capa té contingut (paths o components)
            if len(layer.paths) == 0 and len(layer.components) == 0:
                continue  # Salta capes buides

            layerCount += 1
            layer.decomposeCorners()  # Descompon només corner/cap components
            print(f"✓ {glyph.name} / {layer.name}")
    finally:
        glyph.endUndo()

print(f"\nProcessats {glyphCount} glyphs i {layerCount} capes amb contingut. Fet!")
