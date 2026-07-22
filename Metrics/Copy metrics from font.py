# MenuTitle: Copy metrics from font
# -*- coding: utf-8 -*-
# Description: Removes metrics keys from selected glyphs, either selectively or completely.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Clear Metrics Keys (Advanced)

import vanilla
from GlyphsApp import Glyphs, Message

PREF_KEY = "com.copyMetricsPro.sourceFont"

class CopyMetricsWindow(object):

    def __init__(self):
        self.font = Glyphs.font
        self.otherFonts = [f for f in Glyphs.fonts if f != self.font]

        if not self.otherFonts:
            Message("Error", "No hi ha cap altra font oberta.")
            return

        self.w = vanilla.FloatingWindow((340, 460), "Copy Metrics PRO")

        # FONT SELECTOR
        self.w.fontText = vanilla.TextBox((10, 10, -10, 20), "Source font:")

        fontNames = [f.familyName for f in self.otherFonts]

        savedIndex = Glyphs.defaults.get(PREF_KEY, 0)
        if savedIndex >= len(fontNames):
            savedIndex = 0

        self.w.fontPopUp = vanilla.PopUpButton(
            (10, 30, -10, 25),
            fontNames,
            callback=self.updateMasters
        )
        self.w.fontPopUp.set(savedIndex)

        # SCROLL CONTENT (IMPORTANT)
        self.w.scrollContent = vanilla.Group((0, 0, 300, 0))

        # SCROLL VIEW (AMB NSView)
        self.w.mastersText = vanilla.TextBox((10, 65, -10, 20), "Masters:")
        self.w.scroll = vanilla.ScrollView(
            (10, 85, -10, 160),
            self.w.scrollContent.getNSView(),
            hasHorizontalScroller=False
        )

        self.masterChecks = []

        # OPTIONS
        self.w.metricsText = vanilla.TextBox((10, 255, -10, 20), "Metrics:")
        self.w.copyLSB = vanilla.CheckBox((10, 275, -10, 20), "LSB", value=True)
        self.w.copyRSB = vanilla.CheckBox((10, 300, -10, 20), "RSB", value=True)
        self.w.copyWidth = vanilla.CheckBox((10, 325, -10, 20), "Width", value=True)

        self.w.selectedOnly = vanilla.CheckBox(
            (10, 350, -10, 20),
            "Only selected Glyphs",
            value=False
        )

        # BUTTON
        self.w.applyButton = vanilla.Button(
            (10, 390, -10, 30),
            "Apply",
            callback=self.copyMetrics
        )

        self.updateMasters(None)
        self.w.open()

    def updateMasters(self, sender):
        # guardar preferència
        Glyphs.defaults[PREF_KEY] = self.w.fontPopUp.get()

        # netejar UI antiga
        for attr in list(vars(self.w.scrollContent).keys()):
            if attr.startswith("cb_"):
                delattr(self.w.scrollContent, attr)

        self.masterChecks = []

        otherFont = self.otherFonts[self.w.fontPopUp.get()]

        y = 0
        for i, master in enumerate(otherFont.masters):
            cb = vanilla.CheckBox(
                (10, y, -10, 20),
                master.name,
                value=True
            )
            setattr(self.w.scrollContent, f"cb_{i}", cb)
            self.masterChecks.append((cb, master))
            y += 25

        # ajustar mida del contingut (IMPORTANT pel scroll)
        self.w.scrollContent.setPosSize((0, 0, 300, y))
        self.w.scrollContent.getNSView().setFrame_(((0, 0), (300, y)))

    def getSourceMaster(self, targetMaster, sourceFont):
        # 1. match per ID
        for sm in sourceFont.masters:
            if sm.id == targetMaster.id:
                return sm

        # 2. fallback per nom
        for sm in sourceFont.masters:
            if sm.name == targetMaster.name:
                return sm

        return None

    def copyMetrics(self, sender):
        targetFont = self.font
        sourceFont = self.otherFonts[self.w.fontPopUp.get()]

        selectedMasters = [
            m.name for (cb, m) in self.masterChecks if cb.get()
        ]

        copyLSB = self.w.copyLSB.get()
        copyRSB = self.w.copyRSB.get()
        copyWidth = self.w.copyWidth.get()

        if self.w.selectedOnly.get():
            glyphs = [l.parent for l in targetFont.selectedLayers]
        else:
            glyphs = targetFont.glyphs

        count = 0

        for glyph in glyphs:
            sourceGlyph = sourceFont.glyphs[glyph.name]
            if not sourceGlyph:
                continue

            for master in targetFont.masters:
                if master.name not in selectedMasters:
                    continue

                sourceMaster = self.getSourceMaster(master, sourceFont)
                if not sourceMaster:
                    continue

                targetLayer = glyph.layers[master.id]
                sourceLayer = sourceGlyph.layers[sourceMaster.id]

                if copyLSB:
                    targetLayer.LSB = sourceLayer.LSB
                if copyRSB:
                    targetLayer.RSB = sourceLayer.RSB
                if copyWidth:
                    targetLayer.width = sourceLayer.width

                count += 1

        Glyphs.showNotification(
            "Copy Metrics PRO",
            f"{count} layers actualitzades"
        )


CopyMetricsWindow()