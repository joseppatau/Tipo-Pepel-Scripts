# MenuTitle: Remove Overlapping Nodes
# -*- coding: utf-8 -*-
# Description: Removes duplicate nodes with identical positions
# Author: Josep Patau Bellart (with AI assistance)
# License: Apache2

from GlyphsApp import Glyphs
import vanilla


class RemoveOverlappingNodesUI(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow(
            (260, 150),
            "Remove Overlapping Nodes"
        )

        self.w.scopeText = vanilla.TextBox(
            (15, 15, -15, 20),
            "Apply to:",
            sizeStyle="small"
        )

        self.w.scope = vanilla.RadioGroup(
            (15, 35, -15, 40),
            ["Current Master", "All Masters"],
            isVertical=True
        )
        self.w.scope.set(1)  # default All Masters

        self.w.runButton = vanilla.Button(
            (15, 80, -15, 30),
            "Apply",
            callback=self.run
        )

        self.w.status = vanilla.TextBox(
            (15, 115, -15, 20),
            "Idle",
            sizeStyle="small"
        )

        self.w.open()

    # --------------------------------------------

    def cleanLayer(self, layer):
        removed = 0

        for path in layer.paths:
            nodesToDelete = []
            positions = {}

            for node in path.nodes:
                pos = (round(node.x, 4), round(node.y, 4))

                if pos in positions:
                    nodesToDelete.append(node)
                else:
                    positions[pos] = node

            for node in reversed(nodesToDelete):
                path.nodes.remove(node)
                removed += 1

        return removed

    # --------------------------------------------

    def run(self, sender):

        font = Glyphs.font
        if not font:
            self.w.status.set("No font open")
            return

        totalRemoved = 0
        scope = self.w.scope.get()

        font.disableUpdateInterface()

        try:
            for layer in font.selectedLayers:
                glyph = layer.parent
                glyph.beginUndo()

                if scope == 0:
                    # Current master only
                    totalRemoved += self.cleanLayer(layer)

                else:
                    # All masters
                    for l in glyph.layers:
                        if l.isMasterLayer:
                            totalRemoved += self.cleanLayer(l)

                glyph.endUndo()

        finally:
            font.enableUpdateInterface()

        self.w.status.set(f"Removed {totalRemoved} nodes")

        if font.currentTab:
            font.currentTab.redraw()


RemoveOverlappingNodesUI()