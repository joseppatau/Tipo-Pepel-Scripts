# MenuTitle: Marks by Master
# -*- coding: utf-8 -*-

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

        # Nom centrat
        label = vanilla.TextBox((10, y, 90, 18), name)
        label.getNSTextField().setAlignment_(1)
        setattr(parent, f"label_{index}", label)

        # Botó
        setattr(parent, f"btn_{index}",
            vanilla.Button((10, y+18, 80, 22), "Mark", callback=self.mark)
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

        self.w = vanilla.FloatingWindow((100, 220), "Marks")

        for name, idx in GLYPHS_COLORS:
            self.addRow(name, idx)

        # 🔥 BOTÓ CLEAN
        self.w.cleanButton = vanilla.Button(
            (10, -30, -10, 22),
            "Clean",
            callback=self.cleanMarks
        )

        self.w.open()

    def addRow(self, name, idx):
        index = len(self.rows)
        y = 10 + index * 45

        row = MarkRow(self.w, y, name, idx, self.applyMark, index)
        self.rows.append(row)

        self.resizeWindow()

    def resizeWindow(self):
        x, y, w, h = self.w.getPosSize()
        newHeight = 40 + len(self.rows) * 45
        self.w.setPosSize((x, y, w, newHeight))

    # -------------------------
    # APPLY COLOR
    # -------------------------
    def applyMark(self, colorIndex):
        for layer in Glyphs.font.selectedLayers:
            layer.color = colorIndex

        print(f"🎨 Applied Glyphs color {colorIndex}")

    # -------------------------
    # CLEAN COLORS
    # -------------------------
    def cleanMarks(self, sender):
        for layer in Glyphs.font.selectedLayers:
            layer.color = None

        print("🧹 Colors cleared")


# RUN
ReviewMarksUI()