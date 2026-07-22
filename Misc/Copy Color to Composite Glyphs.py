# MenuTitle: Copy Color to Composite Glyphs
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs

font = Glyphs.font

if not font:
    print("No font open.")
else:
    selectedGlyphs = {layer.parent for layer in font.selectedLayers}
    count = 0

    for sourceGlyph in selectedGlyphs:

        color = sourceGlyph.color
        if color is None:
            continue

        sourceName = sourceGlyph.name

        for targetGlyph in font.glyphs:

            if targetGlyph == sourceGlyph:
                continue

            usesSource = False

            for layer in targetGlyph.layers:

                if not (layer.isMasterLayer or layer.isSpecialLayer):
                    continue

                for component in layer.components:
                    if component.componentName == sourceName:
                        usesSource = True
                        break

                if usesSource:
                    break

            if usesSource:
                targetGlyph.color = color
                count += 1
                print("%s → %s" % (sourceName, targetGlyph.name))

    print("\n%d glyphs updated." % count)