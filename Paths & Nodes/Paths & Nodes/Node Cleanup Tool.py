# MenuTitle: Node Cleanup Tool
# -*- coding: utf-8 -*-
# Description: Removes handles from selected nodes and optionally redistributes them into evenly spaced line segments.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import FloatingWindow, Button

DISTANCIA = 10  # unitats de dispersió


class RemoveHandlesTool(object):

    def __init__(self):
        self.w = FloatingWindow((260, 100), "Nodes seleccionats")

        self.w.cleanButton = Button(
            (10, 10, -10, 30),
            "Neteja corbes",
            callback=self.removeHandlesCallback
        )

        self.w.disperseButton = Button(
            (10, 50, -10, 30),
            "Dispersa nodes (+10)",
            callback=self.disperseNodesCallback
        )

        self.w.open()

    # -------------------------------------------------
    # BOTÓ 1 — eliminar manejadors només dels nodes seleccionats
    # -------------------------------------------------
    def removeHandlesCallback(self, sender):
        font = Glyphs.font
        if not font:
            return

        for layer in font.selectedLayers:
            for path in layer.paths:
                nodes = path.nodes
                for i, node in enumerate(nodes):
                    if not node.selected:
                        continue

                    if node.type in (GSLINE, GSCURVE):
                        prevNode = nodes[i - 1]
                        nextNode = nodes[(i + 1) % len(nodes)]

                        if prevNode.type == GSOFFCURVE:
                            prevNode.type = GSLINE
                            prevNode.smooth = False

                        if nextNode.type == GSOFFCURVE:
                            nextNode.type = GSLINE
                            nextNode.smooth = False

                        node.type = GSLINE
                        node.smooth = False

        font.currentTab.redraw()

    # -------------------------------------------------
    # BOTÓ 2 — dispersar nodes seleccionats
    #          eliminar manejadors existents
    #          i eliminar els dos centrals si n'hi ha 4
    # -------------------------------------------------
    def disperseNodesCallback(self, sender):
        font = Glyphs.font
        if not font:
            return

        for layer in font.selectedLayers:
            for path in layer.paths:

                # ABANS DE DISPERSAR: eliminar manejadors dels nodes seleccionats
                nodes = path.nodes
                for i, node in enumerate(nodes):
                    if not node.selected:
                        continue
                    
                    if node.type in (GSLINE, GSCURVE):
                        prevNode = nodes[i - 1]
                        nextNode = nodes[(i + 1) % len(nodes)]

                        if prevNode.type == GSOFFCURVE:
                            prevNode.type = GSLINE
                            prevNode.smooth = False

                        if nextNode.type == GSOFFCURVE:
                            nextNode.type = GSLINE
                            nextNode.smooth = False

                        node.type = GSLINE
                        node.smooth = False

                # ARA SÍ: dispersar
                selectedNodes = [n for n in path.nodes if n.selected]

                if len(selectedNodes) < 2:
                    continue

                # ordenar per X (comportament predictible)
                selectedNodes.sort(key=lambda n: n.x)

                baseX = selectedNodes[0].x
                baseY = selectedNodes[0].y

                # dispersar
                for i, node in enumerate(selectedNodes):
                    node.x = baseX + (i * DISTANCIA)
                    node.y = baseY

                # si n'hi ha 4, eliminar els dos centrals
                if len(selectedNodes) == 4:
                    for node in selectedNodes[1:3]:
                        path.removeNode_(node)

        font.currentTab.redraw()


RemoveHandlesTool()