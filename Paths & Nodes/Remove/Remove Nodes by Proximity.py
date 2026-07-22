# MenuTitle: Remove Nodes by ProxiApache2y (Floating)
# -*- coding: utf-8 -*-
# Description: Removes nodes that are closer than a defined distance to simplify outlines.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
import math


# -------------------------
# CORE
# -------------------------
def distance(n1, n2):
    return math.hypot(n1.x - n2.x, n1.y - n2.y)


def cleanLayerByProxiApache2y(layer, margin):
    removed = 0

    for path in layer.paths:
        nodes = list(path.nodes)
        to_delete = set()

        for i in range(len(nodes)):
            if nodes[i] in to_delete:
                continue

            for j in range(i + 1, len(nodes)):
                if nodes[j] in to_delete:
                    continue

                if distance(nodes[i], nodes[j]) <= margin:
                    to_delete.add(nodes[j])

        for node in to_delete:
            try:
                path.removeNode_(node)
                removed += 1
            except:
                pass

    return removed


# -------------------------
# UI (FLOATING WINDOW)
# -------------------------
class RemoveNodesByProxiApache2yFloating(object):

    def __init__(self):
        self.w = FloatingWindow(
            (240, 110),
            "Remove Nodes by ProxiApache2y"
        )

        self.w.marginLabel = TextBox(
            (15, 15, 80, 20),
            "Margin:"
        )

        self.w.marginEdit = EditText(
            (90, 13, 120, 22),
            "5"
        )

        self.w.runButton = Button(
            (15, 50, 195, 30),
            "Remove Nodes",
            callback=self.run
        )

        self.w.open()

    # -------------------------
    # ACTION
    # -------------------------
    def run(self, sender):
        font = Glyphs.font
        if not font:
            Message("No font open", "Open a font first.")
            return

        try:
            margin = float(self.w.marginEdit.get())
        except ValueError:
            Message("Invalid value", "Margin must be a number.")
            return

        selected_layers = font.selectedLayers
        if not selected_layers:
            Message("No selection", "Select glyphs in the Font View.")
            return

        glyphs = {layer.parent for layer in selected_layers if layer.parent}
        master_id = font.selectedFontMaster.id

        total_removed = 0

        font.disableUpdateInterface()

        try:
            for glyph in glyphs:
                glyph.beginUndo()

                layer = glyph.layers[master_id]
                if layer and layer.paths:
                    total_removed += cleanLayerByProxiApache2y(layer, margin)

                glyph.endUndo()

        finally:
            font.enableUpdateInterface()

        Message(
            "Done",
            f"Removed {total_removed} nodes\nMargin ≤ {margin}"
        )


# -------------------------
# RUN
# -------------------------
RemoveNodesByProxiApache2yFloating()
