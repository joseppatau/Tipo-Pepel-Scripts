# MenuTitle: Multi-Master Node Align
# -*- coding: utf-8 -*-
# Description: Aligns selected nodes to the extreme position (up, down, left, right) across current or all masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla


class AlignDirectionalPerMaster(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow(
            (220, 240),
            "Align Selected Nodes"
        )

        self.w.up = vanilla.Button((80, 20, 60, 30), "Up", callback=self.alignUp)
        self.w.left = vanilla.Button((20, 70, 60, 30), "Left", callback=self.alignLeft)
        self.w.right = vanilla.Button((140, 70, 60, 30), "Right", callback=self.alignRight)
        self.w.down = vanilla.Button((80, 120, 60, 30), "Down", callback=self.alignDown)

        self.w.scope = vanilla.RadioGroup(
            (20, 165, -20, 40),
            ["Current Master", "All Masters"],
            isVertical=True
        )
        self.w.scope.set(1)

        self.w.open()

    # -----------------------------------------------------

    def getSelectedNodes(self, layer):
        return [n for p in layer.paths for n in p.nodes if n.selected]

    # -----------------------------------------------------

    def align(self, direction):

        font = Glyphs.font
        if not font:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        if self.w.scope.get() == 0:
            layersToProcess = [layer]
        else:
            layersToProcess = [l for l in glyph.layers if l.isMasterLayer]

        glyph.beginUndo()
        font.disableUpdateInterface()

        for processLayer in layersToProcess:

            selectedNodes = self.getSelectedNodes(processLayer)

            if len(selectedNodes) < 2:
                continue

            # Determine master per layer
            if direction == "up":
                masterNode = max(selectedNodes, key=lambda n: n.y)
                axis = "y"
            elif direction == "down":
                masterNode = min(selectedNodes, key=lambda n: n.y)
                axis = "y"
            elif direction == "left":
                masterNode = min(selectedNodes, key=lambda n: n.x)
                axis = "x"
            elif direction == "right":
                masterNode = max(selectedNodes, key=lambda n: n.x)
                axis = "x"

            # Align others to master
            for node in selectedNodes:

                if node == masterNode:
                    continue

                if axis == "x":
                    node.x = masterNode.x
                else:
                    node.y = masterNode.y

        font.enableUpdateInterface()
        glyph.endUndo()

    # -----------------------------------------------------

    def alignUp(self, sender):
        self.align("up")

    def alignDown(self, sender):
        self.align("down")

    def alignLeft(self, sender):
        self.align("left")

    def alignRight(self, sender):
        self.align("right")


AlignDirectionalPerMaster()