# MenuTitle: Create accented alternates from selected stylistic glyphs
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, GSGlyph, GSComponent
import copy

font = Glyphs.font
selectedLayers = list(font.selectedLayers) if font else []

if not selectedLayers:
    print("No glyphs selected.")
else:
    created = []
    skipped = []

    sourceGlyphs = list(font.glyphs)
    selectedGlyphs = []
    seenGlyphNames = set()
    for selectedLayer in selectedLayers:
        selectedGlyph = selectedLayer.parent
        if selectedGlyph.name not in seenGlyphNames:
            selectedGlyphs.append(selectedGlyph)
            seenGlyphNames.add(selectedGlyph.name)

    font.disableUpdateInterface()
    try:
        for selectedGlyph in selectedGlyphs:
            glyphName = selectedGlyph.name

            if "." not in glyphName:
                print(f"Skipping {glyphName}: no suffix found.")
                continue

            baseName, suffixPart = glyphName.split(".", 1)
            suffix = "." + suffixPart

            print(f"\nProcessing {glyphName}")
            print(f"Base: {baseName}")
            print(f"Suffix: {suffix}")

            baseGlyph = font.glyphs[baseName]
            if not baseGlyph:
                print(f"Base glyph {baseName} not found.")
                continue

            for glyph in sourceGlyphs:
                if glyph == selectedGlyph:
                    continue

                usesBase = False

                for layer in glyph.layers:
                    for shape in layer.shapes:
                        if isinstance(shape, GSComponent):
                            if shape.componentName == baseName:
                                usesBase = True
                                break
                    if usesBase:
                        break

                if usesBase:
                    newGlyphName = glyph.name + suffix

                    if font.glyphs[newGlyphName]:
                        skipped.append(newGlyphName)
                        print(f"SKIP: {newGlyphName} already exists")
                        continue

                    newGlyph = GSGlyph(newGlyphName)
                    newGlyph.export = True
                    newGlyph.unicode = None

                    font.glyphs.append(newGlyph)

                    for master in font.masters:
                        sourceLayer = glyph.layers[master.id]
                        targetLayer = newGlyph.layers[master.id]

                        targetLayer.width = sourceLayer.width
                        targetLayer.shapes = []
                        targetLayer.anchors = []

                        # copy shapes
                        for shape in sourceLayer.shapes:
                            newShape = copy.copy(shape)

                            if isinstance(newShape, GSComponent):
                                if newShape.componentName == baseName:
                                    newShape.componentName = glyphName

                            targetLayer.shapes.append(newShape)

                        # copy anchors
                        for anchor in sourceLayer.anchors:
                            targetLayer.anchors.append(copy.copy(anchor))

                    created.append(newGlyphName)
                    print(f"CREATED: {newGlyphName}")
    finally:
        font.enableUpdateInterface()

    print("\n=== DONE ===")
    print(f"Created: {len(created)}")
    for g in created:
        print(f" + {g}")

    print(f"\nSkipped: {len(skipped)}")
    for g in skipped:
        print(f" - {g}")
