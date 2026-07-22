# MenuTitle: Segment Angle Tool
# -*- coding: utf-8 -*-

import vanilla
import math
from GlyphsApp import Glyphs, GSOFFCURVE

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)


class SegmentAngleViewer:

    def __init__(self):

        self.w = vanilla.FloatingWindow((190, 560), "Segment Angle")
        self.selected_segment = None

        self.w.text = vanilla.TextBox((10, 10, -10, 20), "Angle: —")

        self.w.input = vanilla.EditText((10, 40, 50, 22), "80")
        self.w.button = vanilla.Button((70, 40, 30, 22), "▶", callback=self.applyAngle)

        self.w.dirRadio = vanilla.RadioGroup((10, 65, 90, 30), ["/", "\\"], isVertical=False)
        self.w.dirRadio.set(0)

        self.w.axisRadio = vanilla.RadioGroup((10, 90, 90, 30), ["X", "Y"], isVertical=False)
        self.w.axisRadio.set(0)

        self.w.autoAxis = vanilla.CheckBox((10, 125, 150, 20), "Auto axis", value=True)
        self.w.noHandles = vanilla.CheckBox((10, 150, 150, 20), "No handles", value=True)

        self.w.allMasters = vanilla.CheckBox((10, 175, 150, 20), "All masters", value=False)

        self.w.sep = vanilla.HorizontalLine((10, 205, -10, 1))
        self.w.rangeLabel = vanilla.TextBox((10, 215, -10, 20), "Apply in range")

        self.w.rangeAxis = vanilla.RadioGroup((10, 235, 100, 20), ["X", "Y"], isVertical=False)
        self.w.rangeAxis.set(1)

        self.w.start = vanilla.EditText((10, 260, 60, 22), "450")
        self.w.end = vanilla.EditText((80, 260, 60, 22), "520")

        self.w.rangeModeLabel = vanilla.TextBox((10, 290, -10, 20), "Range scope")

        self.w.rangeMode = vanilla.RadioGroup(
            (10, 310, 170, 60),
            [
                "Current master",
                "All masters (same nodes)",
                "All masters (by coordinates)"
            ],
            isVertical=True
        )

        self.w.rangeMode.set(0)

        self.w.applyRangeBtn = vanilla.Button((10, 380, 140, 25), "Apply Range", callback=self.applyRange)
        self.w.refreshButton = vanilla.Button((10, 415, 140, 25), "Refresh Angle", callback=self.updateAngle)

        self.w.open()

        Glyphs.addCallback(self.selectionChanged, "GSSelectionChanged")
        self.updateAngle(None)

    # ----------------------------------------------

    def selectionChanged(self, notification):
        self.updateAngle(None)

    # ----------------------------------------------

    def getSelectedSegment(self, layer):

        if not layer.selection:
            return None

        selected_nodes = [n for n in layer.selection if n.type != GSOFFCURVE]

        if len(selected_nodes) != 2:
            return None

        n1, n2 = selected_nodes

        for p_index, path in enumerate(layer.paths):

            nodes = path.nodes

            for i in range(len(nodes)):
                next_idx = (i + 1) % len(nodes)

                if (nodes[i] == n1 and nodes[next_idx] == n2) or \
                   (nodes[i] == n2 and nodes[next_idx] == n1):

                    return {
                        "p_index": p_index,
                        "n1_index": i,
                        "n2_index": next_idx
                    }

        return None

    # ----------------------------------------------

    def calculateSegmentAngle(self, node1, node2):
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        return math.degrees(math.atan2(dy, dx))

    # ----------------------------------------------

    def updateAngle(self, sender):

        try:
            font = Glyphs.font
            if not font or not font.selectedLayers:
                self.w.text.set("Angle: —")
                return

            layer = font.selectedLayers[0]
            seg = self.getSelectedSegment(layer)

            if seg:
                self.selected_segment = seg

                path = list(layer.paths)[seg["p_index"]]
                n1 = path.nodes[seg["n1_index"]]
                n2 = path.nodes[seg["n2_index"]]

                angle = self.calculateSegmentAngle(n1, n2)
                self.w.text.set(f"Angle: {angle:.1f}°")

            else:
                self.w.text.set("Angle: —")
                self.selected_segment = None

        except Exception as e:
            log(f"Error updating angle: {e}")
            self.w.text.set("Angle: —")

    # ----------------------------------------------

    def refresh(self):
        if Glyphs.font and Glyphs.font.currentTab:
            Glyphs.font.currentTab.redraw()
        self.updateAngle(None)

    # ----------------------------------------------

    def applyAngle(self, sender):

        if not self.selected_segment:
            log("No segment selected")
            return

        try:
            angle = float(self.w.input.get())
        except:
            log("Invalid angle")
            return

        font = Glyphs.font
        layer = font.selectedLayers[0]
        seg = self.selected_segment

        font.disableUpdateInterface()

        try:

            if self.w.allMasters.get():

                glyph = layer.parent

                for master in font.masters:

                    mlayer = glyph.layers[master.id]
                    paths = list(mlayer.paths)

                    if seg["p_index"] >= len(paths):
                        continue

                    path = paths[seg["p_index"]]
                    nodes = path.nodes

                    if seg["n1_index"] >= len(nodes) or seg["n2_index"] >= len(nodes):
                        continue

                    p1 = nodes[seg["n1_index"]]
                    p2 = nodes[seg["n2_index"]]

                    self.applyAngleToPair(p1, p2, angle)

            else:

                paths = list(layer.paths)

                if seg["p_index"] >= len(paths):
                    return

                path = paths[seg["p_index"]]
                nodes = path.nodes

                p1 = nodes[seg["n1_index"]]
                p2 = nodes[seg["n2_index"]]

                self.applyAngleToPair(p1, p2, angle)

            layer.parent.beginUndo()
            layer.parent.endUndo()

        finally:
            font.enableUpdateInterface()

        self.refresh()

    # ----------------------------------------------

    def applyAngleToPair(self, p1, p2, angle):

        if self.w.dirRadio.get() == 1:
            angle = -angle

        dx = p2.x - p1.x
        dy = p2.y - p1.y

        if abs(dx) < 1 and abs(dy) < 1:
            return

        rad = math.radians(angle)

        if self.w.autoAxis.get():
            axis = 1 if abs(dx) > abs(dy) else 0
        else:
            axis = self.w.axisRadio.get()

        if axis == 0:
            if abs(math.tan(rad)) > 1e-6:
                p2.x = p1.x + dy / math.tan(rad)
        else:
            p2.y = p1.y + math.tan(rad) * dx

    # ----------------------------------------------

    def applyRange(self, sender):

        try:
            start = float(self.w.start.get())
            end = float(self.w.end.get())
        except:
            log("invalid range")
            return

        if start > end:
            start, end = end, start

        font = Glyphs.font
        layer = font.selectedLayers[0]

        font.disableUpdateInterface()

        try:
            mode = self.w.rangeMode.get()

            if mode == 0:
                self.processLayer(layer, start, end)

            elif mode == 1:
                nodes = self.collectNodes(layer, start, end)
                glyph = layer.parent

                for master in font.masters:
                    mlayer = glyph.layers[master.id]

                    for p_index, n_index in nodes:
                        paths = list(mlayer.paths)

                        if p_index >= len(paths):
                            continue

                        path = paths[p_index]
                        nodesList = path.nodes

                        if n_index >= len(nodesList) - 1:
                            continue

                        n1 = nodesList[n_index]
                        n2 = nodesList[n_index + 1]

                        self.applyAngleToPair(n1, n2, float(self.w.input.get()))

            elif mode == 2:
                glyph = layer.parent
                for master in font.masters:
                    mlayer = glyph.layers[master.id]
                    self.processLayer(mlayer, start, end)

        finally:
            font.enableUpdateInterface()

        self.refresh()

    # ----------------------------------------------

    def collectNodes(self, layer, start, end):

        axis = self.w.rangeAxis.get()
        nodes = []

        for p_index, path in enumerate(layer.paths):
            for n_index, n in enumerate(path.nodes):

                if n.type == GSOFFCURVE:
                    continue

                if axis == 1:
                    if start <= n.y <= end:
                        nodes.append((p_index, n_index))
                else:
                    if start <= n.x <= end:
                        nodes.append((p_index, n_index))

        return nodes

    # ----------------------------------------------

    def processLayer(self, layer, start, end):

        axis = self.w.rangeAxis.get()
        nodesInRange = []

        for path in layer.paths:
            for n in path.nodes:

                if n.type == GSOFFCURVE:
                    continue

                if axis == 1:
                    if start <= n.y <= end:
                        nodesInRange.append(n)
                else:
                    if start <= n.x <= end:
                        nodesInRange.append(n)

        threshold = 80
        angle_value = float(self.w.input.get())

        for i in range(len(nodesInRange)):
            n1 = nodesInRange[i]

            for j in range(i + 1, len(nodesInRange)):
                n2 = nodesInRange[j]

                if math.hypot(n2.x - n1.x, n2.y - n1.y) < threshold:
                    self.applyAngleToPair(n1, n2, angle_value)
                    break


SegmentAngleViewer()