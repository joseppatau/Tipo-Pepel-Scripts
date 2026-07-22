# MenuTitle: Center Shapes in Width
# -*- coding: utf-8 -*-

from vanilla import *
from GlyphsApp import *


class CenterShapes(object):

    def __init__(self):

        self.w = FloatingWindow(
            (220, 80),
            "Center Shapes"
        )

        self.w.allMasters = CheckBox(
            (10, 12, -10, 20),
            "All masters",
            value=True
        )

        self.w.runButton = Button(
            (10, 40, -10, 22),
            "APPLY",
            callback=self.apply
        )

        self.w.open()
        self.w.makeKey()

    def centerLayer(self, layer):

        if len(layer.shapes) == 0:
            return False

        bounds = layer.bounds

        drawingCenter = bounds.origin.x + bounds.size.width / 2.0
        widthCenter = layer.width / 2.0

        shiftX = widthCenter - drawingCenter

        if abs(shiftX) < 0.01:
            return False

        # Paths
        for path in layer.paths:
            for node in path.nodes:
                node.x += shiftX

        # Components
        for component in layer.components:
            component.x += shiftX

        # Anchors
        for anchor in layer.anchors:
            anchor.x += shiftX

        return True

    def apply(self, sender):

        font = Glyphs.font

        if not font:
            return

        applyToAllMasters = self.w.allMasters.get()

        processedGlyphs = set()
        changedLayers = 0

        font.disableUpdateInterface()

        try:

            for selectedLayer in font.selectedLayers:

                glyph = selectedLayer.parent

                if applyToAllMasters:

                    if glyph.name in processedGlyphs:
                        continue

                    processedGlyphs.add(glyph.name)

                    for master in font.masters:

                        layer = glyph.layers[master.id]

                        if self.centerLayer(layer):
                            changedLayers += 1

                else:

                    if self.centerLayer(selectedLayer):
                        changedLayers += 1

        finally:
            font.enableUpdateInterface()

        Glyphs.showNotification(
            "Center Shapes",
            "%i layer(s) processed." % changedLayers
        )


CenterShapes()