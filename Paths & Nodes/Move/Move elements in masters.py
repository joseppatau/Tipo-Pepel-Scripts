# MenuTitle: Move elements in masters
# -*- coding: utf-8 -*-
# Description: Moves nodes, components, or both across current or all masters using a directional UI.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
from AppKit import NSModalPanelWindowLevel

class MoveElementsClean(object):

    def __init__(self):

        self.w = Window((300, 200), "Move elements")

        # Arrows
        self.w.up = Button((130, 10, 40, 24), "↑", callback=lambda s: self.move(0, 1))
        self.w.down = Button((130, 80, 40, 24), "↓", callback=lambda s: self.move(0, -1))
        self.w.left = Button((70, 45, 40, 24), "←", callback=lambda s: self.move(-1, 0))
        self.w.right = Button((186, 45, 40, 24), "→", callback=lambda s: self.move(1, 0))

        self.w.value = EditText((124, 48, 50, 22), "10")


        # WHAT
        self.w.what = RadioGroup(
            (15, 120, 220, 60),
            ["Paths (Nodes)",
             "Components",
             "Both"],
            isVertical=True
        )
        self.w.what.set(0)

        # WHERE
        self.w.where = RadioGroup(
            (135, 120, 220, 40),
            ["Current Master Only",
             "All Masters"],
            isVertical=True
        )
        self.w.where.set(1)

        # Make window float above Glyphs main window
        self.w.getNSWindow().setLevel_(NSModalPanelWindowLevel)
        
        self.w.open()

    # -------------------------------------------------

    def move(self, xDir, yDir):

        font = Glyphs.font
        if not font:
            return

        try:
            value = float(self.w.value.get())
        except:
            Message("Invalid value", "Enter a numeric value.")
            return

        dx = xDir * value
        dy = yDir * value

        mode = self.w.what.get()
        affectAll = self.w.where.get() == 1

        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()
        font.disableUpdateInterface()

        for layer in font.selectedLayers:
            glyph = layer.parent

            # Layers to affect
            if affectAll:
                targetLayers = [glyph.layers[m.id] for m in font.masters]
            else:
                targetLayers = [layer]

            # =========================
            # MOVE PATHS (nodes)
            # =========================
            if mode in (0, 2):

                for pIndex, path in enumerate(layer.paths):

                    moveWholePath = path.selected
                    selectedNodeIndexes = [
                        nIndex for nIndex, n in enumerate(path.nodes)
                        if n.selected
                    ]

                    if not moveWholePath and not selectedNodeIndexes:
                        continue

                    for target in targetLayers:
                        try:
                            targetPath = target.paths[pIndex]
                        except IndexError:
                            continue

                        # Move whole path
                        if moveWholePath:
                            for node in targetPath.nodes:
                                node.x += dx
                                node.y += dy

                        # Move individual nodes
                        else:
                            for nIndex in selectedNodeIndexes:
                                try:
                                    node = targetPath.nodes[nIndex]
                                    node.x += dx
                                    node.y += dy
                                except IndexError:
                                    continue

            # =========================
            # MOVE COMPONENTS
            # =========================
            if mode in (1, 2):

                for cIndex, component in enumerate(layer.components):

                    if not component.selected:
                        continue

                    for target in targetLayers:
                        try:
                            masterComponent = target.components[cIndex]
                            masterComponent.x += dx
                            masterComponent.y += dy
                        except IndexError:
                            continue

        font.enableUpdateInterface()
        undoManager.endUndoGrouping()


MoveElementsClean()