# MenuTitle: Alignment PRO FINAL (Transform Safe)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)


class AlignTool(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow((240, 520), "Alignment PRO")

        # ===== ALIGN =====
        self.w.label = vanilla.TextBox((15, 10, -15, 20), "X —   Y |")

        self.w.options = vanilla.RadioGroup(
            (15, 30, -15, 140),
            ["Up", "Center Y", "Down", "Left", "Center X", "Right"]
        )
        self.w.options.set(4)

        self.w.alignButton = vanilla.Button(
            (15, 170, -15, 30),
            "Align",
            callback=self.align
        )

        # ===== SCOPE =====
        self.w.scope = vanilla.RadioGroup(
            (15, 210, -15, 40),
            ["Current", "All masters"]
        )
        self.w.scope.set(0)

        self.w.pathsAsGroup = vanilla.CheckBox(
            (15, 260, -15, 20),
            "Paths as group",
            value=True
        )

        # ===== Y POSITION =====
        self.w.sep = vanilla.HorizontalLine((10, 290, -10, 1))

        self.w.yMode = vanilla.RadioGroup(
            (15, 300, 200, 40),
            ["Up", "Center", "Down"],
            isVertical=False
        )
        self.w.yMode.set(0)

        self.w.yLabel = vanilla.TextBox((15, 340, 80, 20), "Y position")

        self.w.yInput = vanilla.EditText((95, 337, 60, 22), "0")

        self.w.yApply = vanilla.Button(
            (160, 335, 30, 24),
            "▶",
            callback=self.applyYPosition
        )

        self.w.yPreset = vanilla.PopUpButton(
            (15, 370, -15, 25),
            ["— Presets —", "Baseline", "x-height", "Cap height", "Ascender", "Descender"],
            callback=self.applyYPreset
        )

        self.w.open()

    # ========= SELECTION =========

    def getSelection(self, layer):

        paths = [p for p in layer.paths if p.selected]
        comps = [c for c in layer.components if c.selected]
        anchors = [a for a in layer.anchors if a.selected]

        log(f"Paths: {len(paths)} | Comps: {len(comps)} | Anchors: {len(anchors)}")

        return paths, comps, anchors

    # ========= SAFE BOUNDS (FIX CLAU) =========

    def getBounds(self, items):

        if not items:
            return None

        xs, ys = [], []

        font = Glyphs.font
        masterID = font.selectedFontMaster.id

        for item in items:

            # ---- PATH ----
            if hasattr(item, "nodes"):
                for n in item.nodes:
                    xs.append(n.x)
                    ys.append(n.y)

            # ---- ANCHOR ----
            elif hasattr(item, "position"):
                xs.append(item.x)
                ys.append(item.y)

            # ---- COMPONENT (TRANSFORM SAFE) ----
            else:
                try:
                    baseLayer = item.component.layers[masterID]
                    tempLayer = baseLayer.copyDecomposedLayer()

                    tempLayer.applyTransform(item.transform)

                    b = tempLayer.bounds

                    xs += [b.origin.x, b.origin.x + b.size.width]
                    ys += [b.origin.y, b.origin.y + b.size.height]

                except Exception as e:
                    log(f"Component fallback: {e}")
                    xs.append(item.x)
                    ys.append(item.y)

        if not xs or not ys:
            return None

        return min(xs), min(ys), max(xs), max(ys)

    # ========= MOVE =========

    def moveItems(self, items, dx, dy):

        log(f"MOVE dx={dx}, dy={dy}")

        for item in items:

            if hasattr(item, "nodes"):
                for n in item.nodes:
                    n.x += dx
                    n.y += dy

            elif hasattr(item, "position"):  # anchor
                item.x += dx
                item.y += dy

            elif hasattr(item, "x") and hasattr(item, "y"):  # component
                item.x += dx
                item.y += dy

    # ========= ALIGN =========

    def alignLayer(self, layer):

        log("\n=== ALIGN LAYER ===")

        paths, comps, anchors = self.getSelection(layer)

        if not paths and not comps and not anchors:
            return

        # RELACIONAL
        if paths and comps:
            refItems = comps
            moveItems = paths + anchors
            log("MODE: PATHS → COMPONENT")

        elif comps:
            refItems = comps
            moveItems = comps
            log("MODE: COMPONENT")

        else:
            refItems = paths + anchors
            moveItems = paths + anchors
            log("MODE: GROUP")

        boundsMove = self.getBounds(moveItems)
        boundsRef = self.getBounds(refItems)

        log(f"Bounds MOVE: {boundsMove}")
        log(f"Bounds REF: {boundsRef}")

        if not boundsMove or not boundsRef:
            return

        minX, minY, maxX, maxY = boundsMove
        minXr, minYr, maxXr, maxYr = boundsRef

        cx = (minX + maxX) / 2
        cy = (minY + maxY) / 2

        option = self.w.options.get()

        if option == 0: dx, dy = 0, maxYr - maxY
        elif option == 1: dx, dy = 0, ((minYr+maxYr)/2) - cy
        elif option == 2: dx, dy = 0, minYr - minY
        elif option == 3: dx, dy = minXr - minX, 0
        elif option == 4: dx, dy = ((minXr+maxXr)/2) - cx, 0
        elif option == 5: dx, dy = maxXr - maxX, 0

        log(f"RESULT dx={dx}, dy={dy}")

        self.moveItems(moveItems, dx, dy)

    # ========= MOVE Y =========

    def applyYToLayer(self, layer, targetY):

        log("\n=== Y POSITION ===")

        paths, comps, anchors = self.getSelection(layer)

        moveItems = paths + comps + anchors

        if not moveItems:
            return

        bounds = self.getBounds(moveItems)

        log(f"Bounds: {bounds}")

        if not bounds:
            return

        minX, minY, maxX, maxY = bounds

        mode = self.w.yMode.get()

        if mode == 0:
            currentY = maxY
        elif mode == 1:
            currentY = (minY + maxY) / 2
        else:
            currentY = minY

        dy = targetY - currentY

        log(f"TARGET Y: {targetY}")
        log(f"CURRENT Y: {currentY}")
        log(f"RESULT dy={dy}")

        self.moveItems(moveItems, 0, dy)

    def applyYPosition(self, sender):

        font = Glyphs.font

        try:
            targetY = float(self.w.yInput.get())
        except:
            log("Invalid Y")
            return

        font.disableUpdateInterface()

        try:
            for layer in font.selectedLayers:

                glyph = layer.parent

                if self.w.scope.get():
                    for m in font.masters:
                        self.applyYToLayer(glyph.layers[m.id], targetY)
                else:
                    self.applyYToLayer(layer, targetY)

        finally:
            font.enableUpdateInterface()

        Glyphs.redraw()

    # ========= PRESETS =========

    def applyYPreset(self, sender):

        index = self.w.yPreset.get()

        if index == 0:
            return

        master = Glyphs.font.selectedFontMaster

        values = [
            0,
            master.xHeight,
            master.capHeight,
            master.ascender,
            master.descender
        ]

        y = values[index-1]

        log(f"Preset Y: {y}")

        self.w.yInput.set(str(y))
        self.applyYPosition(None)

    # ========= MAIN =========

    def align(self, sender):

        font = Glyphs.font

        font.disableUpdateInterface()

        try:
            for layer in font.selectedLayers:

                glyph = layer.parent

                if self.w.scope.get():
                    for m in font.masters:
                        self.alignLayer(glyph.layers[m.id])
                else:
                    self.alignLayer(layer)

        finally:
            font.enableUpdateInterface()

        Glyphs.redraw()


AlignTool()