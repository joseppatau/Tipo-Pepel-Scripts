# MenuTitle: Stem Width/Height by Side
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs
from vanilla import *
import json


class StemTransformBySide(object):

    def __init__(self):
        self.prefPrefix = "com.tipopepel.StemTransformBySide."
        self.rowHeight = 28
        self.sectionGap = 34
        self.rows = {
            "left": [],
            "right": [],
            "top": [],
            "bottom": [],
        }

        self.w = FloatingWindow(
            (326, 270),
            "Transform",
            minSize=(326, 270),
            maxSize=(900, 900)
        )

        self.w.leftTitle = TextBox((24, 12, 120, 17), "Left Side", alignment="center", sizeStyle="small")
        self.w.rightTitle = TextBox((188, 12, 120, 17), "Right Side", alignment="center", sizeStyle="small")
        self.w.vDivider = VerticalLine((163, 2, 1, -2))

        self.w.leftArrowOut = TextBox((6, 39, 18, 17), u"← %", sizeStyle="small")
        self.w.leftOut = EditText((47, 35, 34, 22), self.pref("leftOut", "60"), sizeStyle="small")
        self.w.leftMark = TextBox((84, 39, 18, 17), u"○", alignment="center", sizeStyle="small")
        self.w.leftIn = EditText((103, 35, 34, 22), self.pref("leftIn", "40"), sizeStyle="small")
        self.w.leftArrowIn = TextBox((141, 39, 18, 17), u"% →", sizeStyle="small")

        self.w.rightArrowIn = TextBox((170, 39, 18, 17), u"← %", sizeStyle="small")
        self.w.rightIn = EditText((211, 35, 34, 22), self.pref("rightIn", "60"), sizeStyle="small")
        self.w.rightMark = TextBox((248, 39, 18, 17), u"○", alignment="center", sizeStyle="small")
        self.w.rightOut = EditText((267, 35, 34, 22), self.pref("rightOut", "40"), sizeStyle="small")
        self.w.rightArrowOut = TextBox((305, 39, 18, 17), u"% →", sizeStyle="small")

        self.w.hDivider = HorizontalLine((0, 150, -0, 1))
        self.w.topTitle = TextBox((24, 168, 120, 17), "Top Side", alignment="center", sizeStyle="small")
        self.w.bottomTitle = TextBox((188, 168, 120, 17), "Bottom Side", alignment="center", sizeStyle="small")

        self.w.topArrowOut = TextBox((6, 195, 18, 17), u"↑ %", sizeStyle="small")
        self.w.topOut = EditText((47, 191, 34, 22), self.pref("topOut", "60"), sizeStyle="small")
        self.w.topMark = TextBox((84, 195, 18, 17), u"○", alignment="center", sizeStyle="small")
        self.w.topIn = EditText((103, 191, 34, 22), self.pref("topIn", "40"), sizeStyle="small")
        self.w.topArrowIn = TextBox((141, 195, 18, 17), u"% ↓", sizeStyle="small")

        self.w.bottomArrowIn = TextBox((170, 195, 18, 17), u"↑ %", sizeStyle="small")
        self.w.bottomIn = EditText((211, 191, 34, 22), self.pref("bottomIn", "60"), sizeStyle="small")
        self.w.bottomMark = TextBox((248, 195, 18, 17), u"○", alignment="center", sizeStyle="small")
        self.w.bottomOut = EditText((267, 191, 34, 22), self.pref("bottomOut", "40"), sizeStyle="small")
        self.w.bottomArrowOut = TextBox((305, 195, 18, 17), u"% ↓", sizeStyle="small")

        self.loadRows()
        self.relayout()

        try:
            self.w.bind("close", self.windowClose)
        except:
            pass

        self.w.open()

    def pref(self, key, fallback=""):
        try:
            value = Glyphs.defaults[self.prefPrefix + key]
            if value is not None:
                return str(value)
        except:
            pass
        return fallback

    def setPref(self, key, value):
        try:
            Glyphs.defaults[self.prefPrefix + key] = str(value)
        except:
            pass

    def windowClose(self, sender):
        self.savePrefs()

    def rowsToData(self):
        data = {}
        for side, rows in self.rows.items():
            data[side] = [row["value"].get() for row in rows]
        return data

    def loadRows(self):
        fallback = {
            "left": ["125", "138"],
            "right": [""],
            "top": [""],
            "bottom": [""],
        }

        data = fallback
        raw = self.pref("rows", "")
        if raw:
            try:
                loaded = json.loads(raw)
                if isinstance(loaded, dict):
                    data = loaded
            except:
                data = fallback

        for side, label in [("left", "W"), ("right", "W"), ("top", "H"), ("bottom", "H")]:
            values = data.get(side, fallback.get(side, [""]))
            if not values:
                values = [""]
            for value in values[:12]:
                self.addRow(side, label, value, save=False)

    def savePrefs(self):
        for key in [
            "leftOut", "leftIn", "rightIn", "rightOut",
            "topOut", "topIn", "bottomIn", "bottomOut",
        ]:
            try:
                self.setPref(key, getattr(self.w, key).get())
            except:
                pass

        self.setPref("rows", json.dumps(self.rowsToData()))

    def floatValue(self, text, fallback=None):
        text = text.strip()
        if not text:
            return fallback
        try:
            return float(text)
        except:
            return fallback

    def isOffCurve(self, node):
        try:
            return "offcurve" in str(node.type).lower()
        except:
            return False

    def rowX(self, side):
        return 20 if side in ("left", "top") else 184

    def addRow(self, side, labelText, value="", save=True):
        index = len(self.rows[side])
        x = self.rowX(side)
        prefix = "%sRow%d_" % (side, index)

        label = TextBox((x, 0, 18, 17), labelText, sizeStyle="small")
        valueBox = EditText((x + 27, 0, 58, 22), value, sizeStyle="small")
        applyButton = SquareButton((x + 91, 0, 16, 22), u"▸", callback=self.applyValue)
        addButton = None
        removeButton = None

        if index == 0:
            addButton = SquareButton((x + 113, 0, 18, 22), "+", callback=self.addRowCallback)
            addButton._stemSide = side
            addButton._stemLabel = labelText
        else:
            removeButton = SquareButton((x + 113, 0, 18, 22), "-", callback=self.removeRowCallback)
            removeButton._stemSide = side

        row = {
            "side": side,
            "labelText": labelText,
            "label": label,
            "value": valueBox,
            "apply": applyButton,
            "add": addButton,
            "remove": removeButton,
        }

        applyButton._stemRow = row
        if removeButton is not None:
            removeButton._stemRow = row

        setattr(self.w, prefix + "label", label)
        setattr(self.w, prefix + "value", valueBox)
        setattr(self.w, prefix + "apply", applyButton)
        if addButton is not None:
            setattr(self.w, prefix + "add", addButton)
        if removeButton is not None:
            setattr(self.w, prefix + "remove", removeButton)

        self.rows[side].append(row)
        if save:
            self.relayout()
            self.savePrefs()

    def addRowCallback(self, sender):
        self.addRow(
            getattr(sender, "_stemSide", "left"),
            getattr(sender, "_stemLabel", "W"),
            ""
        )

    def removeRowCallback(self, sender):
        row = getattr(sender, "_stemRow", None)
        if row is None:
            return

        side = row["side"]
        if row not in self.rows[side]:
            return
        if len(self.rows[side]) <= 1:
            return

        self.rows[side].remove(row)
        for key in ["label", "value", "apply", "add", "remove"]:
            widget = row.get(key)
            if widget is not None:
                widget.show(False)

        self.relayout()
        self.savePrefs()

    def setRowPos(self, row, y):
        x = self.rowX(row["side"])
        row["label"].setPosSize((x, y + 4, 18, 17))
        row["value"].setPosSize((x + 27, y, 58, 22))
        row["apply"].setPosSize((x + 91, y, 16, 22))
        if row["add"] is not None:
            row["add"].setPosSize((x + 113, y, 18, 22))
        if row["remove"] is not None:
            row["remove"].setPosSize((x + 113, y, 18, 22))

    def relayout(self):
        widthRows = max(len(self.rows["left"]), len(self.rows["right"]), 1)
        heightSectionY = 76 + widthRows * self.rowHeight + self.sectionGap
        heightRows = max(len(self.rows["top"]), len(self.rows["bottom"]), 1)
        windowHeight = heightSectionY + 64 + heightRows * self.rowHeight

        for index, row in enumerate(self.rows["left"]):
            self.setRowPos(row, 76 + index * self.rowHeight)
        for index, row in enumerate(self.rows["right"]):
            self.setRowPos(row, 76 + index * self.rowHeight)

        self.w.hDivider.setPosSize((0, heightSectionY - 16, -0, 1))
        self.w.topTitle.setPosSize((24, heightSectionY + 2, 120, 17))
        self.w.bottomTitle.setPosSize((188, heightSectionY + 2, 120, 17))

        percentY = heightSectionY + 29
        self.w.topArrowOut.setPosSize((6, percentY + 4, 18, 17))
        self.w.topOut.setPosSize((47, percentY, 34, 22))
        self.w.topMark.setPosSize((84, percentY + 4, 18, 17))
        self.w.topIn.setPosSize((103, percentY, 34, 22))
        self.w.topArrowIn.setPosSize((141, percentY + 4, 18, 17))

        self.w.bottomArrowIn.setPosSize((170, percentY + 4, 18, 17))
        self.w.bottomIn.setPosSize((211, percentY, 34, 22))
        self.w.bottomMark.setPosSize((248, percentY + 4, 18, 17))
        self.w.bottomOut.setPosSize((267, percentY, 34, 22))
        self.w.bottomArrowOut.setPosSize((305, percentY + 4, 18, 17))

        rowY = heightSectionY + 70
        for index, row in enumerate(self.rows["top"]):
            self.setRowPos(row, rowY + index * self.rowHeight)
        for index, row in enumerate(self.rows["bottom"]):
            self.setRowPos(row, rowY + index * self.rowHeight)

        self.w.resize(326, windowHeight)

    def selectedOnCurveMap(self, layer):
        selected = set()
        for pIndex, path in enumerate(layer.paths):
            for nIndex, node in enumerate(path.nodes):
                if node.selected and not self.isOffCurve(node):
                    selected.add((pIndex, nIndex))
        return selected

    def nodesFromMap(self, layer, nodeMap):
        nodes = []
        for pIndex, nIndex in nodeMap:
            try:
                nodes.append(layer.paths[pIndex].nodes[nIndex])
            except:
                pass
        return nodes

    def bounds(self, nodes):
        xs = [n.position.x for n in nodes]
        ys = [n.position.y for n in nodes]
        return min(xs), min(ys), max(xs), max(ys)

    def edgeMaps(self, layer, onCurveMap, tolerance=4):
        nodes = self.nodesFromMap(layer, onCurveMap)
        xMin, yMin, xMax, yMax = self.bounds(nodes)
        maps = {
            "left": set(),
            "right": set(),
            "bottom": set(),
            "top": set(),
        }

        for item in onCurveMap:
            node = layer.paths[item[0]].nodes[item[1]]
            if abs(node.position.x - xMin) <= tolerance:
                maps["left"].add(item)
            if abs(node.position.x - xMax) <= tolerance:
                maps["right"].add(item)
            if abs(node.position.y - yMin) <= tolerance:
                maps["bottom"].add(item)
            if abs(node.position.y - yMax) <= tolerance:
                maps["top"].add(item)

        return maps, (xMin, yMin, xMax, yMax)

    def addMove(self, moves, item, dx, dy):
        oldDx, oldDy = moves.get(item, (0, 0))
        moves[item] = (oldDx + dx, oldDy + dy)

    def setMove(self, moves, item, dx, dy):
        if item not in moves:
            moves[item] = (dx, dy)

    def attachHandleMoves(self, layer, onCurveMap, moves):
        for item in onCurveMap:
            if item not in moves:
                continue

            pIndex, nIndex = item
            path = layer.paths[pIndex]
            count = len(path.nodes)
            closed = bool(getattr(path, "closed", False))
            dx, dy = moves[item]

            for direction in (-1, 1):
                handleIndexes = []
                nextIndex = nIndex + direction

                while True:
                    if closed:
                        nextIndex %= count
                        if nextIndex == nIndex:
                            break
                    elif nextIndex < 0 or nextIndex >= count:
                        break

                    nextNode = path.nodes[nextIndex]
                    if not self.isOffCurve(nextNode):
                        break
                    handleIndexes.append(nextIndex)
                    nextIndex += direction

                if handleIndexes:
                    closestHandle = (pIndex, handleIndexes[0])
                    self.setMove(moves, closestHandle, dx, dy)

    def applyTargetToLayer(self, layer, side, targetValue):
        onCurveMap = self.selectedOnCurveMap(layer)
        if len(onCurveMap) < 2:
            print("Select at least two on-curve nodes.")
            return

        maps, bounds = self.edgeMaps(layer, onCurveMap)
        xMin, yMin, xMax, yMax = bounds
        currentWidth = xMax - xMin
        currentHeight = yMax - yMin
        moves = {}

        if side in ("left", "right"):
            delta = targetValue - currentWidth
            if delta == 0:
                return

            if side == "left":
                outPct = self.floatValue(self.w.leftOut.get(), 0) / 100.0
                inPct = self.floatValue(self.w.leftIn.get(), 0) / 100.0
                outMove = -delta * outPct
                inMove = delta * inPct
            else:
                inPct = self.floatValue(self.w.rightIn.get(), 0) / 100.0
                outPct = self.floatValue(self.w.rightOut.get(), 0) / 100.0
                inMove = -delta * inPct
                outMove = delta * outPct

            for item in maps["left"]:
                self.addMove(moves, item, outMove if side == "left" else inMove, 0)
            for item in maps["right"]:
                self.addMove(moves, item, inMove if side == "left" else outMove, 0)

        else:
            delta = targetValue - currentHeight
            if delta == 0:
                return

            if side == "top":
                outPct = self.floatValue(self.w.topOut.get(), 0) / 100.0
                inPct = self.floatValue(self.w.topIn.get(), 0) / 100.0
                outMove = delta * outPct
                inMove = -delta * inPct
            else:
                inPct = self.floatValue(self.w.bottomIn.get(), 0) / 100.0
                outPct = self.floatValue(self.w.bottomOut.get(), 0) / 100.0
                inMove = delta * inPct
                outMove = -delta * outPct

            for item in maps["top"]:
                self.addMove(moves, item, 0, outMove if side == "top" else inMove)
            for item in maps["bottom"]:
                self.addMove(moves, item, 0, inMove if side == "top" else outMove)

        self.attachHandleMoves(layer, onCurveMap, moves)

        for item, (dx, dy) in moves.items():
            try:
                node = layer.paths[item[0]].nodes[item[1]]
                node.position = (node.position.x + dx, node.position.y + dy)
            except:
                pass

    def applyValue(self, sender):
        row = getattr(sender, "_stemRow", None)
        if row is None:
            return

        targetValue = self.floatValue(row["value"].get(), None)
        if targetValue is None:
            return

        font = Glyphs.font
        if not font or not font.selectedLayers:
            return

        layer = font.selectedLayers[0]
        font.disableUpdateInterface()
        try:
            self.applyTargetToLayer(layer, row["side"], targetValue)
            self.savePrefs()
        finally:
            font.enableUpdateInterface()
            Glyphs.redraw()


StemTransformBySide()
