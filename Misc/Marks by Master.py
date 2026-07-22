# MenuTitle: Marks by Master
# -*- coding: utf-8 -*-
# Description: Lightweight color-marking tool for Glyphs App that allows assigning visual status markers to selected glyph layers using native Glyphs color labels.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import Glyphs
import vanilla


# -------------------------
# COLORS (Glyphs)
# -------------------------
GLYPHS_COLORS = [
    ("Red", 0),
    ("Orange", 1),
    ("Brown", 2),
    ("Yellow", 3),
    ("Light Green", 4),
    ("Green", 5),
    ("Light Blue", 6),
    ("Blue", 7),
    ("Purple", 8),
]


# -------------------------
# ROW
# -------------------------
class MarkRow(object):

    def __init__(self, parent, y, name, colorIndex, callback, index):

        self.callback = callback
        self.colorIndex = colorIndex

        # Label centrado
        label = vanilla.TextBox((10, y, 90, 18), name)
        label.getNSTextField().setAlignment_(1)
        setattr(parent, f"label_{index}", label)

        # Botón
        setattr(parent, f"btn_{index}",
            vanilla.Button((20, y+18, 80, 22), "Mark", callback=self.mark)
        )
        self.button = getattr(parent, f"btn_{index}")

    def mark(self, sender):
        self.callback(self.colorIndex)


# -------------------------
# MAIN UI
# -------------------------
class ReviewMarksUI(object):

    def __init__(self):
        self.rows = []
        self.buildUI()

    def buildUI(self):

        self.w = vanilla.FloatingWindow((120, 280), "Marks")

        for name, idx in GLYPHS_COLORS:
            self.addRow(name, idx)

        # 🔥 BOTÓN CLEAN
        self.w.cleanButton = vanilla.Button(
            (10, -80, -10, 22),
            "Clean",
            callback=self.cleanMarks
        )

        # 🔘 RADIO BUTTONS (VERTICAL)
        self.w.scopeRadio = vanilla.RadioGroup(
            (10, -50, -10, 40),
            ["This Master", "All Masters"],
            isVertical=True
        )
        self.w.scopeRadio.set(0)

        self.w.open()

    def addRow(self, name, idx):
        index = len(self.rows)
        y = 10 + index * 45

        row = MarkRow(self.w, y, name, idx, self.applyMark, index)
        self.rows.append(row)

        self.resizeWindow()

    def resizeWindow(self):
        x, y, w, h = self.w.getPosSize()
        newHeight = 100 + len(self.rows) * 45
        self.w.setPosSize((x, y, w, newHeight))

    # -------------------------
    # APPLY COLOR
    # -------------------------
    def applyMark(self, colorIndex):

        scope = self.w.scopeRadio.get()

        if scope == 0:
            for layer in Glyphs.font.selectedLayers:
                layer.color = colorIndex
        else:
            font = Glyphs.font
            selectedGlyphs = [layer.parent for layer in font.selectedLayers]

            for glyph in selectedGlyphs:
                for master in font.masters:
                    layer = glyph.layers[master.id]
                    if layer:
                        layer.color = colorIndex

        print(f"🎨 Applied Glyphs color {colorIndex}")

    # -------------------------
    # CLEAN COLORS
    # -------------------------
    def cleanMarks(self, sender):

        scope = self.w.scopeRadio.get()

        if scope == 0:
            for layer in Glyphs.font.selectedLayers:
                layer.color = None
        else:
            font = Glyphs.font
            selectedGlyphs = [layer.parent for layer in font.selectedLayers]

            for glyph in selectedGlyphs:
                for master in font.masters:
                    layer = glyph.layers[master.id]
                    if layer:
                        layer.color = None

        print("🧹 Colors cleared")


# RUN
ReviewMarksUI()