# MenuTitle: Enable/disable components in All Masters
# -*- coding: utf-8 -*-
# Description: Enables or disables automatic alignment of components across all masters for selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# License: MIT

from __future__ import division, print_function, unicode_literals
from GlyphsApp import *
import vanilla

class ToggleAlignmentAllMasters(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Open a font first.")
            return

        # Ventana
        self.w = vanilla.FloatingWindow(
            (280, 180),
            "Toggle Alignment",
            closable=True
        )

        # Título
        self.w.title = vanilla.TextBox(
            (10, 10, -10, 22),
            "Toggle alignment for selected glyphs:",
            sizeStyle="small"
        )

        # Botones
        self.w.enableButton = vanilla.Button(
            (20, 40, -20, 24),
            "✅ Enable Alignment in All Masters",
            callback=self.enableAlignment
        )

        self.w.disableButton = vanilla.Button(
            (20, 70, -20, 24),
            "❌ Disable Alignment in All Masters",
            callback=self.disableAlignment
        )

        # Opciones de componentes
        self.w.optionsText = vanilla.TextBox(
            (10, 105, -10, 22),
            "Apply to:",
            sizeStyle="small"
        )

        self.w.selectedOnly = vanilla.CheckBox(
            (20, 125, -20, 20),
            "Selected components only",
            value=True,
            sizeStyle="small"
        )

        self.w.allComponents = vanilla.CheckBox(
            (20, 145, -20, 20),
            "All components in glyph",
            value=False,
            sizeStyle="small",
            callback=self.toggleComponentOptions
        )

        self.w.open()

    def toggleComponentOptions(self, sender):
        # Si marcas "All components", desmarca "Selected components", y viceversa
        if sender == self.w.allComponents and sender.get():
            self.w.selectedOnly.set(False)
        elif sender == self.w.selectedOnly and sender.get():
            self.w.allComponents.set(False)

    def toggleAlignmentForGlyph(self, glyph, enable=True, selectedOnly=True):
        """Activa o desactiva la alineación para un glifo en todos los masters"""
        changed = 0

        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                if selectedOnly:
                    components = [c for c in layer.components if c.selected]
                else:
                    components = list(layer.components)

                for component in components:
                    component.automaticAlignment = bool(enable)
                    changed += 1

        return changed

    def enableAlignment(self, sender):
        self.toggleAlignment(enable=True)

    def disableAlignment(self, sender):
        self.toggleAlignment(enable=False)

    def toggleAlignment(self, enable=True):
        font = self.font
        if not font:
            return

        selectedOnly = self.w.selectedOnly.get()
        if self.w.allComponents.get():
            selectedOnly = False

        # 1) Glifos seleccionados en el panel de glifos
        selectedGlyphs = [g for g in font.selectedLayers and {l.parent for l in font.selectedLayers}]

        # Si no hay glifos a partir de las capas seleccionadas, usar selección de panel
        if not selectedGlyphs:
            selectedGlyphs = [g for g in font.glyphs if g.selected]

        if not selectedGlyphs:
            Message("No glyphs selected", "Please select at least one glyph.")
            return

        font.disableUpdateInterface()
        undo_manager = font.undoManager()
        undo_manager.beginUndoGrouping()

        try:
            total_changed = 0

            for glyph in selectedGlyphs:
                if not glyph:
                    continue
                total_changed += self.toggleAlignmentForGlyph(
                    glyph,
                    enable=enable,
                    selectedOnly=selectedOnly
                )

            action = "Enabled" if enable else "Disabled"
            Glyphs.showNotification(
                f"Alignment {action}",
                f"{action} alignment for {len(selectedGlyphs)} glyph(s)\n"
                f"Modified {total_changed} component(s)"
            )

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            Glyphs.showNotification(
                "Error",
                f"An error occurred: {str(e)}"
            )

        finally:
            undo_manager.endUndoGrouping()
            font.enableUpdateInterface()

# Ejecutar
ToggleAlignmentAllMasters()
