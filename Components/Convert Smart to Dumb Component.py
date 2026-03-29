# MenuTitle: Convert Smart to Dumb Component (via temp glyph)
# -*- coding: utf-8 -*-
# Description: Utility script that converts smart components into regular (dumb) components by replacing them with static outlines via a temporary glyph.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2


font = Glyphs.font

font.disableUpdateInterface()

try:
    for layer in font.selectedLayers:
        comps = list(layer.components)

        for comp in comps:
            base = font.glyphs[comp.componentName]

            if base and base.smartComponentAxes:

                # crear glyph temporal
                tempName = "_temp_" + comp.componentName
                if not font.glyphs[tempName]:
                    tempGlyph = GSGlyph(tempName)
                    font.glyphs.append(tempGlyph)

                    # copiar outlines del master
                    tempLayer = tempGlyph.layers[font.selectedFontMaster.id]
                    sourceLayer = base.layers[font.selectedFontMaster.id]
                    tempLayer.shapes = [s.copy() for s in sourceLayer.shapes]

                # substituir component
                newComp = GSComponent(tempName)
                newComp.position = comp.position
                newComp.scale = comp.scale

                layer.components.append(newComp)
                layer.removeShape_(comp)

                print("Desmartitzat:", layer.parent.name)

finally:
    font.enableUpdateInterface()

Glyphs.showNotification("Fet", "Components ja NO són smart")