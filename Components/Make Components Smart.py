# MenuTitle: Make Components Smart (Glyphs 3 Safe)
# -*- coding: utf-8 -*-
# Description: Converts components into smart components by creating axes and assigning interpolation values across masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
Glyphs.clearLog()

font = Glyphs.font

if not font:
    print("No font open.")
else:

    selectedLayers = font.selectedLayers

    if not selectedLayers:
        print("No glyphs selected.")
    else:

        batchProcess = len(selectedLayers) > 1
        processedGlyphs = set()

        for selectedLayer in selectedLayers:

            selectedGlyph = selectedLayer.parent
            print(f"Processing {selectedGlyph.name}...")

            for selectedComponent in selectedLayer.components:

                if not selectedComponent.selected and not batchProcess:
                    continue

                originalGlyph = font.glyphs[selectedComponent.name]

                if not originalGlyph:
                    continue

                # --------------------------------------------------
                # Create Smart Axes if they don't exist
                # --------------------------------------------------

                if not originalGlyph.smartComponentAxes:

                    for i, fontAxis in enumerate(font.axes):

                        axisValues = [m.axes[i] for m in font.masters]

                        newAxis = GSSmartComponentAxis()
                        newAxis.name = fontAxis.name
                        newAxis.bottomValue = min(axisValues)
                        newAxis.topValue = max(axisValues)

                        originalGlyph.smartComponentAxes.append(newAxis)

                        # Assign poles
                        for layer in originalGlyph.layers:
                            if not layer.isMasterLayer:
                                continue

                            master = layer.associatedFontMaster()
                            masterValue = master.axes[i]

                            if masterValue == newAxis.bottomValue:
                                layer.smartComponentPoleMapping[newAxis.id] = 1
                            elif masterValue == newAxis.topValue:
                                layer.smartComponentPoleMapping[newAxis.id] = 2

                # --------------------------------------------------
                # Assign interpolation values safely
                # --------------------------------------------------

                for layer in selectedGlyph.layers:

                    if not layer.isMasterLayer:
                        continue

                    master = layer.associatedFontMaster()

                    for component in layer.components:

                        if component.name != originalGlyph.name:
                            continue

                        for i, smartAxis in enumerate(originalGlyph.smartComponentAxes):

                            interpolationValue = master.axes[i]
                            component.smartComponentValues[smartAxis.id] = interpolationValue

                # Refresh selection to show smart UI
                if not batchProcess:
                    selectedComponent.selected = False
                    selectedComponent.selected = True

                processedGlyphs.add(originalGlyph.name)

        # ------------------------------------------------------

        if processedGlyphs:
            be = "are" if len(processedGlyphs) > 1 else "is"
            print(f'{", ".join(processedGlyphs)} {be} now smart.')
        else:
            print("No glyphs changed. Select at least one component.")