# MenuTitle: Move Anchors to Metrics Lines
# -*- coding: utf-8 -*-

from GlyphsApp import *
from vanilla import *

class MoveAnchors(object):

    def __init__(self):
        if not Glyphs.font:
            Message("Error", "No font open")
            return

        self.font = Glyphs.font

        self.w = Window((340, 190), "Move Anchors")

        # --- Anchor list (ALL font anchors) ---
        self.w.txt_anchor = TextBox((15, 15, 120, 20), "Anchor:")
        self.w.anchorList = PopUpButton((140, 15, 180, 20), self.getAllAnchors())

        # --- Metric lines ---
        self.w.txt_line = TextBox((15, 50, 120, 20), "Align to:")
        self.w.lineList = PopUpButton((140, 50, 180, 20), [
            "baseline",
            "x-height",
            "cap height",
            "ascender"
        ])

        # --- Scope ---
        self.w.scope = RadioGroup((15, 85, 200, 40),
            ["This master", "All masters"],
            isVertical=True
        )
        self.w.scope.set(0)

        # --- Run ---
        self.w.runButton = Button((15, 140, -15, 20), "Move Anchors", callback=self.run)

        self.w.open()

    # --- GET ALL ANCHORS FROM FONT ---
    def getAllAnchors(self):
        anchors = set()

        for g in self.font.glyphs:
            for layer in g.layers:
                for a in layer.anchors:
                    anchors.add(a.name)

        return sorted(list(anchors))

    # --- GET Y POSITION FROM METRICS ---
    def getMetricValue(self, master, metricName):
        if metricName == "baseline":
            return 0
        elif metricName == "x-height":
            return master.xHeight
        elif metricName == "cap height":
            return master.capHeight
        elif metricName == "ascender":
            return master.ascender
        return 0

    # --- MAIN ---
    def run(self, sender):

        selectedAnchor = self.w.anchorList.getItem()
        selectedLine = self.w.lineList.getItem()
        scope = self.w.scope.get()

        font = Glyphs.font
        selectedLayers = font.selectedLayers

        if not selectedLayers:
            Message("Error", "No glyphs selected")
            return

        for layer in selectedLayers:

            glyph = layer.parent

            # --- WHICH MASTERS ---
            if scope == 0:
                layersToProcess = [layer]
            else:
                layersToProcess = [l for l in glyph.layers if l.isMasterLayer]

            for l in layersToProcess:
                master = font.masters[l.associatedMasterId]
                targetY = self.getMetricValue(master, selectedLine)

                for anchor in l.anchors:
                    if anchor.name == selectedAnchor:
                        anchor.y = targetY

        Glyphs.redraw()

MoveAnchors()