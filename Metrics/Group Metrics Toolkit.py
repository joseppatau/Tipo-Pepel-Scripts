# MenuTitle:Group Metrics Toolkit
# -*- coding: utf-8 -*-
# Description: Manage kerning groups: update metrics, inspect group members, and analyze metric key dependencies.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Kern Group Update metrics

import GlyphsApp
from vanilla import FloatingWindow, EditText, TextBox, RadioGroup, Button, Tabs

font = Glyphs.font


class KernGroupTools(object):

    def __init__(self):

        self.w = FloatingWindow((460, 380),
                                "Kern & Metrics Tools")

        self.w.tabs = Tabs((10, 10, -10, -10),
                           ["Update @ metrics",
                            "View @ Members",
                            "Metric Keys"])

        # =====================================================
        # TAB 1 — UPDATE @ METRICS
        # =====================================================

        tab1 = self.w.tabs[0]

        tab1.textGroup = TextBox((15, 15, 120, 20), "Kern Group:")
        tab1.inputGroup = EditText((140, 12, 270, 22), "")

        tab1.textLSB = TextBox((15, 55, 120, 20), "LSB value:")
        tab1.inputLSB = EditText((140, 52, 270, 22), "")

        tab1.textRSB = TextBox((15, 85, 120, 20), "RSB value:")
        tab1.inputRSB = EditText((140, 82, 270, 22), "")

        tab1.radio = RadioGroup(
            (15, 115, -15, 60),
            ["Increase", "Decrease", "Equal to"],
            isVertical=True
        )
        tab1.radio.set(0)

        tab1.runButton = Button((15, 200, -15, 30),
                                "Apply",
                                callback=self.updateMetrics)

        # =====================================================
        # TAB 2 — VIEW @ MEMBERS
        # =====================================================

        tab2 = self.w.tabs[1]

        tab2.textGroup = TextBox((15, 15, 120, 20), "Kern Group:")
        tab2.inputGroup = EditText((140, 12, 270, 22), "")

        tab2.viewButton = Button((15, 50, -15, 30),
                                 "Open Tab",
                                 callback=self.viewMembers)

        # =====================================================
        # TAB 3 — METRIC KEYS
        # =====================================================

        tab3 = self.w.tabs[2]

        tab3.textGlyph = TextBox((15, 15, 200, 20),
                                 "Glyph name (metric key):")
        tab3.inputGlyph = EditText((15, 40, -15, 22), "")

        tab3.searchButton = Button((15, 75, -15, 30),
                                   "Search Linked Glyphs",
                                   callback=self.searchMetricKeys)

        self.w.open()
        self.w.makeKey()

    # =====================================================
    # TAB 1 — UPDATE METRICS
    # =====================================================

    def updateMetrics(self, sender):

        master = font.selectedFontMaster
        tab = self.w.tabs[0]

        groupInput = tab.inputGroup.get().strip()
        if not groupInput:
            return

        mode = tab.radio.get()

        try:
            lsbValue = float(tab.inputLSB.get()) if tab.inputLSB.get() else None
        except:
            lsbValue = None

        try:
            rsbValue = float(tab.inputRSB.get()) if tab.inputRSB.get() else None
        except:
            rsbValue = None

        groupName = groupInput.replace("@MMK_L_", "") \
                              .replace("@MMK_R_", "") \
                              .replace("@", "")

        # =====================================================
        # 🔥 SI NO HI HA VALORS → USAR EL GLIF AMB AQUEST NOM
        # =====================================================

        if lsbValue is None and rsbValue is None:

            referenceGlyph = font.glyphs[groupName]

            if not referenceGlyph:
                print("Reference glyph not found:", groupName)
                return

            refLayer = referenceGlyph.layers[master.id]

            lsbValue = refLayer.LSB
            rsbValue = refLayer.RSB
            mode = 2  # Equal to

            print("Using reference glyph '%s' values: LSB=%s RSB=%s"
                  % (groupName, lsbValue, rsbValue))

        # =====================================================

        font.disableUpdateInterface()

        for g in font.glyphs:

            layer = g.layers[master.id]
            if not layer:
                continue

            changed = False

            if lsbValue is not None and g.leftKerningGroup == groupName:
                g.beginUndo()
                if mode == 0:
                    layer.LSB += lsbValue
                elif mode == 1:
                    layer.LSB -= lsbValue
                elif mode == 2:
                    layer.LSB = lsbValue
                changed = True

            if rsbValue is not None and g.rightKerningGroup == groupName:
                if not changed:
                    g.beginUndo()
                if mode == 0:
                    layer.RSB += rsbValue
                elif mode == 1:
                    layer.RSB -= rsbValue
                elif mode == 2:
                    layer.RSB = rsbValue
                changed = True

            if changed:
                g.endUndo()

        font.enableUpdateInterface()

    # =====================================================
    # TAB 2 — VIEW MEMBERS
    # =====================================================

    def viewMembers(self, sender):

        tab = self.w.tabs[1]
        groupInput = tab.inputGroup.get().strip()
        if not groupInput:
            return

        groupName = groupInput.replace("@MMK_L_", "") \
                              .replace("@MMK_R_", "") \
                              .replace("@", "")

        leftMembers = []
        rightMembers = []

        for g in font.glyphs:

            if g.leftKerningGroup == groupName and g.string:
                leftMembers.append(g.string)

            if g.rightKerningGroup == groupName and g.string:
                rightMembers.append(g.string)

        text = ""

        if leftMembers:
            text += "@%s – LSB\n%s\n\n" % (
                groupName, "".join(leftMembers))

        if rightMembers:
            text += "@%s – RSB\n%s" % (
                groupName, "".join(rightMembers))

        if text:
            font.newTab(text)

    # =====================================================
    # TAB 3 — METRIC KEYS
    # =====================================================

    def searchMetricKeys(self, sender):

        tab = self.w.tabs[2]
        baseGlyphName = tab.inputGlyph.get().strip()

        if not baseGlyphName:
            return

        leftLinked = []
        rightLinked = []

        for g in font.glyphs:

            # IMPORTANT: en G3 sovint està al glyph
            leftKey = g.leftMetricsKey
            rightKey = g.rightMetricsKey

            # fallback layer
            if not leftKey or not rightKey:
                layer = g.layers[font.selectedFontMaster.id]
                if not leftKey:
                    leftKey = layer.leftMetricsKey
                if not rightKey:
                    rightKey = layer.rightMetricsKey

            if leftKey and baseGlyphName in leftKey:
                leftLinked.append("/" + g.name)

            if rightKey and baseGlyphName in rightKey:
                rightLinked.append("/" + g.name)

        if not leftLinked and not rightLinked:
            print("No linked glyphs found.")
            return

        text = ""

        if leftLinked:
            text += "@%s – Used in LSB\n%s\n\n" % (
                baseGlyphName, " ".join(leftLinked))

        if rightLinked:
            text += "@%s – Used in RSB\n%s" % (
                baseGlyphName, " ".join(rightLinked))

        font.newTab(text)


KernGroupTools()