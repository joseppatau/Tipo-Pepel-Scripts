# MenuTitle: Enable/disable components in All Masters
# -*- coding: utf-8 -*-
# Description: Enables or disables automatic alignment of components across all masters for selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# License: Apache2

from __future__ import division, print_function, unicode_literals
from GlyphsApp import *
import vanilla


class ToggleAlignmentAllMasters(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Open a font first.")
            return

        self.w = vanilla.FloatingWindow(
            (280, 180),
            "Toggle Alignment",
            closable=True
        )

        self.w.title = vanilla.TextBox(
            (10, 10, -10, 22),
            "Toggle alignment for selected glyphs:",
            sizeStyle="small"
        )

        self.w.enableButton = vanilla.Button(
            (20, 40, -20, 24),
            "Enable Alignment in All Masters",
            callback=self.enableAlignment
        )

        self.w.disableButton = vanilla.Button(
            (20, 70, -20, 24),
            "Disable Alignment in All Masters",
            callback=self.disableAlignment
        )

        self.w.optionsText = vanilla.TextBox(
            (10, 105, -10, 22),
            "Apply to:",
            sizeStyle="small"
        )

        self.w.selectedOnly = vanilla.CheckBox(
            (20, 125, -20, 20),
            "Selected components only",
            value=True,
            sizeStyle="small",
            callback=self.toggleComponentOptions
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
        if sender == self.w.allComponents and sender.get():
            self.w.selectedOnly.set(False)
        elif sender == self.w.selectedOnly and sender.get():
            self.w.allComponents.set(False)

        if not self.w.selectedOnly.get() and not self.w.allComponents.get():
            self.w.selectedOnly.set(True)

    def selectedGlyphs(self):
        glyphs = []
        seen = set()

        for layer in self.font.selectedLayers or []:
            glyph = layer.parent
            if glyph and glyph.name not in seen:
                glyphs.append(glyph)
                seen.add(glyph.name)

        if glyphs:
            return glyphs

        for glyph in self.font.glyphs:
            if glyph.selected and glyph.name not in seen:
                glyphs.append(glyph)
                seen.add(glyph.name)

        return glyphs

    def selectedComponentIndexesForGlyph(self, glyph):
        indexes = set()

        for layer in self.font.selectedLayers or []:
            if layer.parent != glyph:
                continue

            for index, component in enumerate(layer.components):
                if component.selected:
                    indexes.add(index)

        return indexes

    def targetLayersForGlyph(self, glyph):
        layers = []
        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                layers.append(layer)
        return layers

    def setComponentAlignment(self, component, enable):
        component.automaticAlignment = bool(enable)

    def toggleAlignmentForGlyph(self, glyph, enable=True, selectedOnly=True):
        changed = 0
        selectedIndexes = self.selectedComponentIndexesForGlyph(glyph) if selectedOnly else None

        if selectedOnly and not selectedIndexes:
            # In Font View / grid selection there are selected glyphs, but no
            # selected components. In that context, fall back to all components.
            selectedOnly = False

        for layer in self.targetLayersForGlyph(glyph):
            components = list(layer.components)

            if selectedOnly:
                targetComponents = [
                    components[index]
                    for index in sorted(selectedIndexes)
                    if index < len(components)
                ]
            else:
                targetComponents = components

            for component in targetComponents:
                self.setComponentAlignment(component, enable)
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

        glyphs = self.selectedGlyphs()
        if not glyphs:
            Message("No glyphs selected", "Please select at least one glyph.")
            return

        font.disableUpdateInterface()
        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()

        try:
            totalChanged = 0

            for glyph in glyphs:
                totalChanged += self.toggleAlignmentForGlyph(
                    glyph,
                    enable=enable,
                    selectedOnly=selectedOnly
                )

            action = "Enabled" if enable else "Disabled"

            if selectedOnly and totalChanged == 0:
                Glyphs.showNotification(
                    "No selected components",
                    "Select at least one component, or choose All components in glyph."
                )
            else:
                Glyphs.showNotification(
                    "Alignment %s" % action,
                    "%s alignment for %d glyph(s)\nModified %d component(s)" % (
                        action,
                        len(glyphs),
                        totalChanged
                    )
                )

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            Glyphs.showNotification("Error", "An error occurred: %s" % str(e))

        finally:
            undoManager.endUndoGrouping()
            font.enableUpdateInterface()


ToggleAlignmentAllMasters()
