# MenuTitle: Remove Handles (Selected Nodes)
# -*- coding: utf-8 -*-
# Description: Removes handles from selected nodes in the current or all master layers.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla

class RemoveHandlesUnified(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow(
            (260, 140),
            "Remove Handles"
        )

        self.w.scope = vanilla.RadioGroup(
            (15, 15, -15, 40),
            ["Current Master", "All Masters"],
            isVertical=True
        )
        self.w.scope.set(0)

        self.w.runButton = vanilla.Button(
            (15, 70, -15, 30),
            "Remove Handles",
            callback=self.run
        )

        self.w.status = vanilla.TextBox(
            (15, 105, -15, 20),
            "Idle",
            sizeStyle="small"
        )

        self.w.open()

    # --------------------------------------------

    def removeHandlesInLayer(self, layer):

        selected_nodes = []

        for path in layer.paths:
            for node in path.nodes:
                if node.selected and node.type != GSOFFCURVE:
                    selected_nodes.append(node)

        for node in selected_nodes:
            path = node.parent
            index = path.nodes.index(node)

            # remove previous handles
            if index > 0 and path.nodes[index - 1].type == GSOFFCURVE:
                path.removeNodeCheckKeepShape_(path.nodes[index - 1])
            if index > 1 and path.nodes[index - 1].type == GSOFFCURVE:
                path.removeNodeCheckKeepShape_(path.nodes[index - 1])

            # remove next handles
            if index < len(path.nodes) - 1 and path.nodes[index + 1].type == GSOFFCURVE:
                path.removeNodeCheckKeepShape_(path.nodes[index + 1])
            if index < len(path.nodes) - 2 and path.nodes[index + 1].type == GSOFFCURVE:
                path.removeNodeCheckKeepShape_(path.nodes[index + 1])

    # --------------------------------------------

    def run(self, sender):

        font = Glyphs.font
        if not font:
            self.w.status.set("No font open")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        font.disableUpdateInterface()
        glyph.beginUndo()

        if self.w.scope.get() == 0:
            # Current master
            self.removeHandlesInLayer(layer)
            self.w.status.set("Done (current master)")

        else:
            # All masters
            for l in glyph.layers:
                if l.isMasterLayer:
                    self.removeHandlesInLayer(l)
            self.w.status.set("Done (all masters)")

        glyph.endUndo()
        font.enableUpdateInterface()

        if font.currentTab:
            font.currentTab.redraw()


RemoveHandlesUnified()