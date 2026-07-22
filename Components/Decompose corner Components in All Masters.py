# MenuTitle: Decompose corner Components in All Masters
# -*- coding: utf-8 -*-
# Description: Descompon tots els corner components a tots els mestres.
# Author: Gemini & Josep Patau



font = Glyphs.font

print("Descomponen corner components de tots els masters...\n")

glyphCount = 0
layerCount = 0

for glyph in font.glyphs:
    if len(font.selectedLayers) == 0 or glyph.layers[0] in font.selectedLayers:
        glyphCount += 1
        for layer in glyph.layers:
            # Comprova si la capa té contingut (paths o components)
            if len(layer.paths) == 0 and len(layer.components) == 0:
                continue  # Salta capes buides
            
            layerCount += 1
            layer.decomposeCorners()  # Descompon només corner/cap components
            print(f"✓ {glyph.name} / {layer.name}")

print(f"\nProcessats {glyphCount} glyphs i {layerCount} capes amb contingut. Fet!")