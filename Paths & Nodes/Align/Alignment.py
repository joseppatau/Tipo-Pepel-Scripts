# MenuTitle: Alignment (PRO FINAL)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs
import math
import traceback

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)


class AlignTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((240, 420), "Alignment PRO")

        self.w.options = vanilla.RadioGroup(
            (45, 10, -15, 140),
            ["Up", "Center Y", "Down", "Left", "Center X", "Right"]
        )
        self.w.options.set(4)

        # Labels
        self.w.labelY = vanilla.TextBox((15, 80, -15, 20), "Y |")
        self.w.labelX = vanilla.TextBox((15, 10, -15, 20), "X —")

        self.w.alignButton = vanilla.Button(
            (15, 170, -15, 30),
            "Align",
            callback=self.align
        )

        self.w.trueWidth = vanilla.CheckBox(
            (15, 210, -15, 20),
            "Align to width",
            value=False
        )

        self.w.scope = vanilla.RadioGroup(
            (15, 240, -15, 40),
            ["Current", "All masters"]
        )
        self.w.scope.set(0)

        self.w.pathsAsGroup = vanilla.CheckBox(
            (15, 290, -15, 20),
            "Paths as group",
            value=True
        )

        self.w.open()

    # ========= ITALIC =========

    def getItalicAngle(self, layer):
        font = Glyphs.font
        return font.masters[layer.associatedMasterId].italicAngle or 0

    # ========= SELECTION =========

    def getSelection(self, layer):
        paths = [p for p in layer.paths if p.selected]
        comps = [c for c in layer.components if c.selected]

        if not paths and not comps:
            paths = list(layer.paths)
            comps = list(layer.components)

        log(f"Selected paths: {len(paths)}")
        log(f"Selected components: {len(comps)}")

        return paths, comps

    # ========= ALL NODES (ORIGINAL SAFE) =========

    def getAllNodes(self, layer):

        nodes = []

        for p in layer.paths:
            nodes.extend(p.nodes)

        bg = layer.background
        orig_paths = [p.copy() for p in bg.paths]
        orig_comps = [c.copy() for c in bg.components]

        for c in layer.components:
            bg.clear()
            bg.components.append(c.copy())
            bg.decomposeComponents()

            for p in bg.paths:
                nodes.extend(p.nodes)

        bg.clear()
        for p in orig_paths:
            bg.paths.append(p)
        for c in orig_comps:
            bg.components.append(c)

        return nodes

    # ========= BOUNDS (SAFE VERSION) =========

    def getBounds(self, layer, item):

        angle = self.getItalicAngle(layer)
        tan = math.tan(math.radians(angle))

        xs, ys = [], []

        if hasattr(item, "nodes"):
            for n in item.nodes:
                xs.append(n.x - n.y * tan)
                ys.append(n.y)
        else:
            bg = layer.background

            orig_paths = [p.copy() for p in bg.paths]
            orig_comps = [c.copy() for c in bg.components]

            bg.clear()
            bg.components.append(item.copy())
            bg.decomposeComponents()

            for p in bg.paths:
                for n in p.nodes:
                    xs.append(n.x - n.y * tan)
                    ys.append(n.y)

            bg.clear()
            for p in orig_paths:
                bg.paths.append(p)
            for c in orig_comps:
                bg.components.append(c)

        return min(xs), min(ys), max(xs), max(ys)

    def getGroupBounds(self, layer, items):

        log("=== GROUP BOUNDS ===")

        bounds = [self.getBounds(layer, i) for i in items]

        minX = min(b[0] for b in bounds)
        minY = min(b[1] for b in bounds)
        maxX = max(b[2] for b in bounds)
        maxY = max(b[3] for b in bounds)

        log(f"Group bounds: {(minX, minY, maxX, maxY)}")

        return minX, minY, maxX, maxY

    # ========= TRUE WIDTH =========

    def applyTrueWidth(self, layer):

        try:
            nodes = self.getAllNodes(layer)

            if not nodes:
                return

            angle = self.getItalicAngle(layer)
            tan = math.tan(math.radians(angle))

            projected = [n.x - n.y * tan for n in nodes]

            left = min(projected)
            right = max(projected)

            overflow = max(0, right - layer.width)
            width = (right - left) + overflow

            margin = layer.width - width
            side = margin / 2

            layer.LSB = side
            layer.RSB = side

            log("TRUE WIDTH applied")

        except:
            traceback.print_exc()

    # ========= ALIGN =========

    def alignLayer(self, layer):

        log("\n====== ALIGN LAYER ======")

        paths, comps = self.getSelection(layer)
        option = self.w.options.get()

        # TRUE WIDTH
        if self.w.trueWidth.get() and option == 4:
            log("TRUE WIDTH MODE")
            self.applyTrueWidth(layer)
            return

        # 🔥 GROUP LOGIC CORRECTA
        if self.w.pathsAsGroup.get() and comps:
            log("🔥 GROUP MODE (paths → component)")
            refItems = comps
            moveItems = paths
        else:
            refItems = paths + comps
            moveItems = paths + comps

        log(f"Reference items: {len(refItems)}")
        log(f"Move items: {len(moveItems)}")

        # reference
        minX, minY, maxX, maxY = self.getGroupBounds(layer, refItems)

        if option == 0:
            ref = maxY
        elif option == 1:
            ref = (minY + maxY) / 2
        elif option == 2:
            ref = minY
        elif option == 3:
            ref = minX
        elif option == 4:
            ref = (minX + maxX) / 2
        elif option == 5:
            ref = maxX

        log(f"REFERENCE: {ref}")

        # group
        minX, minY, maxX, maxY = self.getGroupBounds(layer, moveItems)

        dx = dy = 0

        if option == 0:
            dy = ref - maxY
        elif option == 1:
            dy = ref - ((minY + maxY) / 2)
        elif option == 2:
            dy = ref - minY
        elif option == 3:
            dx = ref - minX
        elif option == 4:
            dx = ref - ((minX + maxX) / 2)
        elif option == 5:
            dx = ref - maxX

        log(f"GROUP MOVE dx={dx}, dy={dy}")

        for item in moveItems:
            log(f"Moving item: {item}")

            if hasattr(item, "nodes"):
                for n in item.nodes:
                    n.x += dx
                    n.y += dy
            else:
                item.applyTransform((1, 0, 0, 1, dx, dy))

    # ========= MAIN =========

    def align(self, sender):

        font = Glyphs.font

        font.disableUpdateInterface()

        try:
            for layer in font.selectedLayers:
                glyph = layer.parent

                if self.w.scope.get() == 0:
                    self.alignLayer(layer)
                else:
                    for l in glyph.layers:
                        if l.isMasterLayer or l.isSpecialLayer:
                            self.alignLayer(l)

        finally:
            font.enableUpdateInterface()


AlignTool()