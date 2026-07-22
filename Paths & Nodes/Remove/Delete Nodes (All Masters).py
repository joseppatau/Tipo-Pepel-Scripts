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
            (100, 60),
            "Nodes",
        )

        self.w.deleteButton = vanilla.Button(
            (15, 20, -15, 30),
            "DELETE",
            callback=self.deleteNodes
        )



        self.w.open()

    # -----------------------------------------------------
    # DELETE NODES
    # -----------------------------------------------------

    def deleteNodes(self, sender):

        font = Glyphs.font
        if not font or not font.selectedLayers:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        selectedIndexes = self.getSelectedNodeIndexes(layer)

        if not selectedIndexes:
            Glyphs.showNotification("Delete Nodes", "No nodes selected.")
            return

        masterLayers = [candidate for candidate in glyph.layers if candidate.isMasterLayer]
        incompatible = self.incompatibleLayers(layer, masterLayers, selectedIndexes)
        if incompatible:
            Glyphs.showNotification(
                "Delete Nodes",
                "Canceled: incompatible structure in %s." % ", ".join(incompatible)
            )
            return

        font.disableUpdateInterface()
        glyph.beginUndo()
        try:
            for masterLayer in masterLayers:
                for pathIndex, nodeIndex in sorted(selectedIndexes, reverse=True):
                    del masterLayer.paths[pathIndex].nodes[nodeIndex]
        finally:
            glyph.endUndo()
            font.enableUpdateInterface()

        Glyphs.showNotification("Delete Nodes", "Nodes deleted in all masters.")

    # -----------------------------------------------------
    # DELETE HANDLES (Glyphs 3 way)
    # -----------------------------------------------------

    def deleteHandles(self, sender):

        font = Glyphs.font
        if not font or not font.selectedLayers:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        selectedIndexes = self.getSelectedNodeIndexes(layer)

        if not selectedIndexes:
            Glyphs.showNotification("Delete Handles", "No nodes selected.")
            return

        masterLayers = [candidate for candidate in glyph.layers if candidate.isMasterLayer]
        incompatible = self.incompatibleLayers(layer, masterLayers, selectedIndexes)
        if incompatible:
            Glyphs.showNotification(
                "Delete Handles",
                "Canceled: incompatible structure in %s." % ", ".join(incompatible)
            )
            return

        font.disableUpdateInterface()
        glyph.beginUndo()
        try:
            for masterLayer in masterLayers:
                for pathIndex, nodeIndex in selectedIndexes:
                    path = masterLayer.paths[pathIndex]

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
        finally:
            glyph.endUndo()
            font.enableUpdateInterface()

        Glyphs.showNotification("Delete Handles", "Handles removed in all masters.")

    def incompatibleLayers(self, sourceLayer, layers, selectedIndexes):
        """Return master names whose path/node structure differs from the source."""
        incompatible = []
        for layer in layers:
            valid = len(layer.paths) == len(sourceLayer.paths)
            if valid:
                valid = all(
                    len(layer.paths[pathIndex].nodes)
                    == len(sourceLayer.paths[pathIndex].nodes)
                    for pathIndex, nodeIndex in selectedIndexes
                )
            if not valid:
                incompatible.append(layer.name)
        return incompatible

    # -----------------------------------------------------

    def getSelectedNodeIndexes(self, layer):

        indexes = []

        for pathIndex, path in enumerate(layer.paths):
            for nodeIndex, node in enumerate(path.nodes):
                if node.selected and node.type != GSOFFCURVE:
                    indexes.append((pathIndex, nodeIndex))

        return indexes


DeleteNodesAllMasters()
