# MenuTitle: Delete Glyph Content (Smart)
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, Message
import vanilla


class ClearGlyphContentUI(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow(
            (280, 170),
            "Clear Glyph Content"
        )

        self.w.info = vanilla.TextBox(
            (15, 15, -15, 40),
            "Deletes ALL content or only selection\n(paths, components, anchors...).",
            sizeStyle="small"
        )

        self.w.allMasters = vanilla.CheckBox(
            (15, 60, -15, 20),
            "Apply to ALL masters",
            value=False,
            sizeStyle="small"
        )

        self.w.runButton = vanilla.Button(
            (15, 90, -15, 30),
            "Apply",
            callback=self.run
        )

        self.w.status = vanilla.TextBox(
            (15, 130, -15, 20),
            "Idle",
            sizeStyle="small"
        )

        self.w.open()

    # --------------------------------------------

    def getTargetGlyphs(self, font):
        layers = font.selectedLayers
        if layers:
            return list(set([l.parent for l in layers]))
        return []

    # --------------------------------------------

    def clearLayer(self, layer):
        """Delete everything"""
        layer.shapes = []
        layer.anchors = []
        layer.guides = []
        layer.hints = []

    # --------------------------------------------

    def clearSelection(self, layer):
        """Delete only selected elements"""

        # Shapes (paths + components)
        for shape in list(layer.shapes):
            if shape.selected:
                layer.shapes.remove(shape)

        # Anchors
        for anchor in list(layer.anchors):
            if anchor.selected:
                layer.anchors.remove(anchor)

        # Guides
        for guide in list(layer.guides):
            if guide.selected:
                layer.guides.remove(guide)

    # --------------------------------------------

    def layerHasSelection(self, layer):
        """Check if something is selected"""

        for shape in layer.shapes:
            if shape.selected:
                return True

        for anchor in layer.anchors:
            if anchor.selected:
                return True

        for guide in layer.guides:
            if guide.selected:
                return True

        return False

    # --------------------------------------------

    def run(self, sender):

        font = Glyphs.font
        if not font:
            self.w.status.set("No font open")
            return

        glyphs = self.getTargetGlyphs(font)

        if not glyphs:
            Message("Error", "Select glyph(s) or layers.", OKButton="OK")
            return

        allMasters = self.w.allMasters.get()

        font.disableUpdateInterface()

        try:
            for glyph in glyphs:
                glyph.beginUndo()

                if allMasters:
                    layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
                else:
                    layers = [l for l in font.selectedLayers if l.parent == glyph]

                for layer in layers:
                    if self.layerHasSelection(layer):
                        self.clearSelection(layer)
                    else:
                        self.clearLayer(layer)

                glyph.endUndo()

        finally:
            font.enableUpdateInterface()

        self.w.status.set(f"Done: {len(glyphs)} glyph(s) processed")

        if font.currentTab:
            font.currentTab.redraw()


ClearGlyphContentUI()