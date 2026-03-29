# MenuTitle: Duplicate components in all masters (improved)
# -*- coding: utf-8 -*-
# Description: Duplicates selected or all components from the active layer into all masters for selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT


from GlyphsApp import *
from vanilla import FloatingWindow, CheckBox, Button, TextBox

__doc__ = """
Duplicate components in all masters.
If 'Apply to all selected glyphs' is checked,
all components are duplicated without needing selection.
"""


class DuplicateComponentsUI(object):

    def __init__(self):
        self.font = Glyphs.font

        self.w = FloatingWindow(
            (380, 150),
            "Duplicate components in all masters"
        )

        self.w.text = TextBox(
            (15, 15, -15, 40),
            "Duplicate components from the active layer\ninto all masters."
        )

        self.w.allGlyphsCheck = CheckBox(
            (15, 60, -15, 20),
            "Apply to all selected glyphs (duplicate ALL components)",
            value=False
        )

        self.w.runButton = Button(
            (15, 100, -15, 30),
            "Duplicate",
            callback=self.run
        )

        self.w.open()

    def run(self, sender):
        font = self.font
        selectedLayers = font.selectedLayers

        if not selectedLayers:
            Message(
                "No glyph selected",
                "Select at least one glyph before running this script.",
                OKButton="OK"
            )
            return

        applyToAllGlyphs = self.w.allGlyphsCheck.get()

        if applyToAllGlyphs:
            glyphs = list({layer.parent for layer in selectedLayers})
        else:
            glyphs = [selectedLayers[0].parent]

        totalComponents = 0

        for glyph in glyphs:
            activeLayer = glyph.layers[font.selectedFontMaster.id]

            if applyToAllGlyphs:
                sourceComponents = list(activeLayer.components)
            else:
                sourceComponents = [c for c in activeLayer.components if c.selected]
                if not sourceComponents:
                    Message(
                        "No component selected",
                        "Select at least one component, or enable\n'Apply to all selected glyphs'.",
                        OKButton="OK"
                    )
                    return

            for master in font.masters:
                targetLayer = glyph.layers[master.id]
                if targetLayer == activeLayer:
                    continue

                for sourceComponent in sourceComponents:
                    newComponent = GSComponent(sourceComponent.componentName)
                    newComponent.transform = sourceComponent.transform
                    targetLayer.components.append(newComponent)
                    totalComponents += 1

        Glyphs.showNotification(
            "Duplicate components",
            f"Duplicated {totalComponents} components into all masters."
        )

        # La ventana ya no se cierra aquí
        # self.w.close()  # <--- Eliminado


DuplicateComponentsUI()