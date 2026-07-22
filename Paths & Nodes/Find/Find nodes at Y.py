# MenuTitle: Find nodes at Y
# -*- coding: utf-8 -*-
# Description: Find and snap selected glyph nodes to a given Y position.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# License: Apache2

from GlyphsApp import Glyphs
from vanilla import FloatingWindow, TextBox, EditText, Button, CheckBox
from Foundation import NSUserDefaults


PREF_PREFIX = "FindNodesAtY."


class FindNodesAtY(object):

    def __init__(self):
        self.loadSettings()

        self.w = FloatingWindow((390, 178), "Find nodes at Y", minSize=(370, 178))

        y = 14
        self.w.yLabel = TextBox((14, y + 3, 70, 20), "Y value")
        self.w.yField = EditText((90, y, 90, 24), str(self.yValue))

        self.w.toleranceLabel = TextBox((195, y + 3, 70, 20), "Tolerance")
        self.w.toleranceField = EditText((270, y, 60, 24), str(self.tolerance))

        y += 34
        self.w.currentMasterCheck = CheckBox(
            (14, y, 180, 22),
            "Current master only",
            value=self.currentMasterOnly,
        )

        y += 34
        self.w.snapCheck = CheckBox(
            (14, y, 220, 22),
            "Snap found nodes to Y value",
            value=self.snapNodes,
        )

        y += 34
        self.w.scanButton = Button((14, y, 100, 26), "Rastrejar", callback=self.scanCallback)
        self.w.status = TextBox((126, y + 4, -14, 20), "")

        self.w.open()

    def prefKey(self, name):
        return PREF_PREFIX + name

    def loadSettings(self):
        d = NSUserDefaults.standardUserDefaults()
        self.yValue = d.stringForKey_(self.prefKey("yValue")) or "0"
        self.tolerance = d.stringForKey_(self.prefKey("tolerance")) or "0"
        self.currentMasterOnly = True
        if d.objectForKey_(self.prefKey("currentMasterOnly")) is not None:
            self.currentMasterOnly = bool(d.boolForKey_(self.prefKey("currentMasterOnly")))
        self.snapNodes = True
        if d.objectForKey_(self.prefKey("snapNodes")) is not None:
            self.snapNodes = bool(d.boolForKey_(self.prefKey("snapNodes")))

    def saveSettings(self):
        d = NSUserDefaults.standardUserDefaults()
        d.setObject_forKey_(self.w.yField.get(), self.prefKey("yValue"))
        d.setObject_forKey_(self.w.toleranceField.get(), self.prefKey("tolerance"))
        d.setBool_forKey_(bool(self.w.currentMasterCheck.get()), self.prefKey("currentMasterOnly"))
        d.setBool_forKey_(bool(self.w.snapCheck.get()), self.prefKey("snapNodes"))

    def scanCallback(self, sender):
        font = Glyphs.font
        if not font:
            self.setStatus("No font open.")
            return

        try:
            yValue = float(self.w.yField.get().replace(",", "."))
            tolerance = abs(float(self.w.toleranceField.get().replace(",", ".")))
        except Exception:
            self.setStatus("Y/tolerance invalid.")
            return

        self.saveSettings()

        masterIDs = self.masterIDs(font)
        selectedGlyphs = self.selectedGlyphs(font)
        if not selectedGlyphs:
            self.setStatus("No selected glyphs.")
            return

        matches = []
        changedNodes = 0
        snapNodes = bool(self.w.snapCheck.get())

        if snapNodes:
            try:
                font.disableUpdateInterface()
            except Exception:
                pass

        for glyph in selectedGlyphs:
            if not glyph:
                continue
            found, changed = self.processGlyph(glyph, masterIDs, yValue, tolerance, snapNodes)
            if found:
                matches.append(glyph.name)
                changedNodes += changed

        if snapNodes:
            try:
                font.enableUpdateInterface()
            except Exception:
                pass

        if matches:
            font.newTab("/" + "/".join(matches))
            if snapNodes:
                self.setStatus("%s glyphs, %s nodes snapped." % (len(matches), changedNodes))
            else:
                self.setStatus("%s glyphs found." % len(matches))
        else:
            self.setStatus("No matches.")

    def selectedGlyphs(self, font):
        glyphs = []
        seen = set()

        try:
            for layer in font.selectedLayers:
                glyph = getattr(layer, "parent", None)
                if glyph and glyph.name not in seen:
                    glyphs.append(glyph)
                    seen.add(glyph.name)
        except Exception:
            pass

        if glyphs:
            return glyphs

        try:
            tab = font.currentTab
            for layer in tab.layers:
                glyph = getattr(layer, "parent", None)
                if glyph and glyph.name not in seen:
                    glyphs.append(glyph)
                    seen.add(glyph.name)
        except Exception:
            pass

        return glyphs

    def masterIDs(self, font):
        if bool(self.w.currentMasterCheck.get()):
            try:
                return [font.selectedFontMaster.id]
            except Exception:
                return []
        ids = []
        try:
            for master in font.masters:
                ids.append(master.id)
        except Exception:
            pass
        return ids

    def processGlyph(self, glyph, masterIDs, yValue, tolerance, snapNodes):
        found = False
        changed = 0
        for masterID in masterIDs:
            try:
                layer = glyph.layers[masterID]
            except Exception:
                continue
            layerFound, layerChanged = self.processLayer(layer, yValue, tolerance, snapNodes)
            if layerFound:
                found = True
                changed += layerChanged
        return found, changed

    def processLayer(self, layer, yValue, tolerance, snapNodes):
        found = False
        changed = 0
        try:
            paths = layer.paths
        except Exception:
            return False, 0

        for path in paths:
            try:
                nodes = path.nodes
            except Exception:
                continue
            for node in nodes:
                try:
                    if abs(float(node.y) - yValue) <= tolerance:
                        found = True
                        if snapNodes and float(node.y) != yValue:
                            node.y = yValue
                            changed += 1
                except Exception:
                    pass
        return found, changed

    def setStatus(self, message):
        try:
            self.w.status.set(message)
        except Exception:
            print(message)


if "findNodesAtYWindow" in globals():
    try:
        findNodesAtYWindow.w.close()
    except Exception:
        pass

findNodesAtYWindow = FindNodesAtY()
