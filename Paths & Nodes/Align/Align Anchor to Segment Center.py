# MenuTitle: Align Anchor to Segment Center (All Masters)
# -*- coding: utf-8 -*-
# Description: Aligns the selected anchor to the horizontal center of selected nodes across all masters, with optional italic compensation
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
import math


class AlignAnchorSegmentCenter(object):

    def __init__(self):

        self.w = FloatingWindow(
            (300, 140),
            "Align Anchor to Segment",
            autosaveName="align.anchor.segment.center"
        )

        self.w.text = TextBox(
            (20, 10, -20, 20),
            "Select anchor and nodes, then click:"
        )

        self.w.italics_checkbox = CheckBox(
            (20, 35, -20, 20),
            "Consider italic angle",
            value=True
        )

        self.w.run = Button(
            (20, 65, -20, 30),
            "Align Anchor to Selection",
            callback=self.run
        )

        self.w.open()

    # --------------------------------------------------

    def italicizeX(self, x, y, angle, baseline):
        """Convierte coordenada X al espacio vertical (sin cursiva)"""
        if angle == 0:
            return x
        return x - (y - baseline) * math.tan(math.radians(angle))

    def deItalicizeX(self, x, y, angle, baseline):
        """Devuelve coordenada X al espacio cursivo"""
        if angle == 0:
            return x
        return x + (y - baseline) * math.tan(math.radians(angle))

    # --------------------------------------------------

    def getSelectedNodes(self, layer):

        nodes = []

        for pIndex, path in enumerate(layer.paths):
            for nIndex, node in enumerate(path.nodes):
                if node.selected:
                    nodes.append((pIndex, nIndex))

        return nodes

    def getSelectedAnchor(self, layer):

        for a in layer.anchors:
            if a.selected:
                return a.name

        return None

    # --------------------------------------------------

    def run(self, sender):

        font = Glyphs.font
        if not font:
            Message("No Font Open", "Open a font first")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        anchorName = self.getSelectedAnchor(layer)
        selectedNodes = self.getSelectedNodes(layer)
        considerItalics = self.w.italics_checkbox.get()

        if not anchorName:
            Message("Select an anchor", "Please select an anchor.")
            return

        if not selectedNodes:
            Message("Select nodes", "Please select nodes.")
            return

        font.disableUpdateInterface()

        try:

            for master in font.masters:

                masterLayer = glyph.layers[master.id]
                if not masterLayer:
                    continue

                anchor = masterLayer.anchors[anchorName]
                if not anchor:
                    continue

                italicAngle = master.italicAngle if considerItalics else 0
                baseline = master.descender * 0  # baseline normalmente = 0

                nodeXs = []

                for pathIndex, nodeIndex in selectedNodes:

                    if pathIndex >= len(masterLayer.paths):
                        continue

                    path = masterLayer.paths[pathIndex]

                    if nodeIndex >= len(path.nodes):
                        continue

                    node = path.nodes[nodeIndex]

                    xNeutral = self.italicizeX(
                        node.x,
                        node.y,
                        italicAngle,
                        baseline
                    )

                    nodeXs.append(xNeutral)

                if not nodeXs:
                    continue

                centerNeutral = sum(nodeXs) / len(nodeXs)

                newX = self.deItalicizeX(
                    centerNeutral,
                    anchor.y,
                    italicAngle,
                    baseline
                )

                anchor.x = newX

        finally:

            font.enableUpdateInterface()


AlignAnchorSegmentCenter()