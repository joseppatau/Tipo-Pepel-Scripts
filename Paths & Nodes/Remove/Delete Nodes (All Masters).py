# MenuTitle: Delete Nodes (All Masters)
# -*- coding: utf-8 -*-
# Description: Removes handles from selected nodes in the current or all master layers.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla

class DeleteNodesAllMasters(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow(
            (320, 180),
            "Delete Nodes (All Masters)",
        )

        self.w.infoText = vanilla.TextBox(
            (15, 15, -15, 40),
            "Delete selected nodes or only their handles\nin ALL master layers.",
            sizeStyle="small"
        )

        self.w.deleteButton = vanilla.Button(
            (15, 80, -15, 30),
            "DELETE SELECTED NODES",
            callback=self.deleteNodes
        )

        self.w.handleButton = vanilla.Button(
            (15, 120, -15, 30),
            "DELETE HANDLES ONLY",
            callback=self.deleteHandles
        )

        self.w.open()

    # -----------------------------------------------------
    # DELETE NODES
    # -----------------------------------------------------

    def deleteNodes(self, sender):

        font = Glyphs.font
        if not font:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        selectedIndexes = self.getSelectedNodeIndexes(layer)

        if not selectedIndexes:
            Glyphs.showNotification("Delete Nodes", "No nodes selected.")
            return

        font.disableUpdateInterface()
        glyph.beginUndo()

        for masterLayer in glyph.layers:
            if not masterLayer.isMasterLayer:
                continue

            for pathIndex, nodeIndex in sorted(selectedIndexes, reverse=True):
                if pathIndex < len(masterLayer.paths):
                    path = masterLayer.paths[pathIndex]
                    if nodeIndex < len(path.nodes):
                        del path.nodes[nodeIndex]

        glyph.endUndo()
        font.enableUpdateInterface()

        Glyphs.showNotification("Delete Nodes", "Nodes deleted in all masters.")

    # -----------------------------------------------------
    # DELETE HANDLES (Glyphs 3 way)
    # -----------------------------------------------------

    def deleteHandles(self, sender):

        font = Glyphs.font
        if not font:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        selectedIndexes = self.getSelectedNodeIndexes(layer)

        if not selectedIndexes:
            Glyphs.showNotification("Delete Handles", "No nodes selected.")
            return

        font.disableUpdateInterface()
        glyph.beginUndo()

        for masterLayer in glyph.layers:
            if not masterLayer.isMasterLayer:
                continue

            for pathIndex, nodeIndex in selectedIndexes:
                if pathIndex >= len(masterLayer.paths):
                    continue

                path = masterLayer.paths[pathIndex]
                if nodeIndex >= len(path.nodes):
                    continue

                node = path.nodes[nodeIndex]

                # Only curve nodes can have handles
                if node.type != GSCURVE:
                    continue

                nodes = path.nodes
                count = len(nodes)

                prevIndex = (nodeIndex - 1) % count
                nextIndex = (nodeIndex + 1) % count

                toDelete = []

                # Previous off-curve
                if nodes[prevIndex].type == GSOFFCURVE:
                    toDelete.append(prevIndex)

                # Next off-curve
                if nodes[nextIndex].type == GSOFFCURVE:
                    toDelete.append(nextIndex)

                # Delete in reverse order
                for i in sorted(toDelete, reverse=True):
                    del path.nodes[i]

        glyph.endUndo()
        font.enableUpdateInterface()

        Glyphs.showNotification("Delete Handles", "Handles removed in all masters.")

    # -----------------------------------------------------

    def getSelectedNodeIndexes(self, layer):

        indexes = []

        for pathIndex, path in enumerate(layer.paths):
            for nodeIndex, node in enumerate(path.nodes):
                if node.selected and node.type != GSOFFCURVE:
                    indexes.append((pathIndex, nodeIndex))

        return indexes


DeleteNodesAllMasters()