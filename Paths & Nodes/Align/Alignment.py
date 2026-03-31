# MenuTitle: Alignment (FINAL TRUE WIDTH PRO)
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
        self.w = vanilla.FloatingWindow((240, 360), "Alignment PRO")

        self.w.options = vanilla.RadioGroup(
            (45, 10, -15, 140),
            ["Up", "Center Y", "Down", "Left", "Center X", "Right"]
        )
        self.w.options.set(4)
        
        self.w.labelY = vanilla.TextBox((17, 80, -15, 20), "Y |")
        self.w.labelX = vanilla.TextBox((15, 10, -15, 20), "X —")
        self.w.options.set(0)

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

        self.w.open()

    # ========= ITALIC =========

    def getItalicAngle(self, layer):
        font = Glyphs.font
        master = font.masters[layer.associatedMasterId]
        angle = master.italicAngle or 0
        log(f"Italic angle: {angle}")
        return angle

    # ========= SELECTION =========

    def getItems(self, layer):
        paths = [p for p in layer.paths if p.selected]
        comps = [c for c in layer.components if c.selected]

        log(f"Paths selected: {len(paths)}")
        log(f"Components selected: {len(comps)}")

        items = paths + comps

        if not items:
            log("No selection → using all items")
            items = list(layer.paths) + list(layer.components)

        log(f"Total items used: {len(items)}")
        return items

    # ========= GET ALL NODES (KEY) =========

    def getAllNodes(self, layer):

        nodes = []

        # paths
        for p in layer.paths:
            nodes.extend(p.nodes)

        # components → descomponer
        bg = layer.background
        orig_paths = [p.copy() for p in bg.paths]
        orig_comps = [c.copy() for c in bg.components]

        for c in layer.components:
            bg.clear()
            bg.components.append(c.copy())
            bg.decomposeComponents()

            for p in bg.paths:
                nodes.extend(p.nodes)

        # restore
        bg.clear()
        for p in orig_paths:
            bg.paths.append(p)
        for c in orig_comps:
            bg.components.append(c)

        log(f"Total nodes collected: {len(nodes)}")
        return nodes

    # ========= BOUNDS (ITALIC-AWARE) =========

    def getBounds(self, layer, item):

        angle = self.getItalicAngle(layer)
        tan_angle = math.tan(math.radians(angle))

        xs, ys = [], []

        if hasattr(item, "nodes"):
            for n in item.nodes:
                xs.append(n.x - (n.y * tan_angle))
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
                    xs.append(n.x - (n.y * tan_angle))
                    ys.append(n.y)

            bg.clear()
            for p in orig_paths:
                bg.paths.append(p)
            for c in orig_comps:
                bg.components.append(c)

        if not xs:
            return 0, 0, 0, 0

        bounds = (min(xs), min(ys), max(xs), max(ys))
        log(f"Bounds: {bounds}")
        return bounds

    # ========= GLOBAL REFERENCE =========

    def getReference(self, layer, items, option):

        bounds_list = [self.getBounds(layer, i) for i in items]

        minX = min(b[0] for b in bounds_list)
        minY = min(b[1] for b in bounds_list)
        maxX = max(b[2] for b in bounds_list)
        maxY = max(b[3] for b in bounds_list)

        log(f"GLOBAL bounds: {(minX, minY, maxX, maxY)}")

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

        log(f"REFERENCE: {ref:.2f}")
        return ref

    # ========= MOVE =========

    def moveItem(self, layer, item, option, ref):

        minX, minY, maxX, maxY = self.getBounds(layer, item)

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

        log(f"MOVE → dx={dx:.2f}, dy={dy:.2f}")

        if hasattr(item, "nodes"):
            for n in item.nodes:
                n.x += dx
                n.y += dy
        else:
            item.applyTransform((1, 0, 0, 1, dx, dy))

    # ========= TRUE WIDTH (YOUR METHOD) =========

    def applyTrueWidth(self, layer):

        try:
            nodes = self.getAllNodes(layer)

            if not nodes:
                log("No nodes → abort")
                return

            angle = self.getItalicAngle(layer)
            tan_angle = math.tan(math.radians(angle))

            projected = [n.x - (n.y * tan_angle) for n in nodes]

            left = min(projected)
            right = max(projected)

            log(f"Projected left: {left:.2f}")
            log(f"Projected right: {right:.2f}")

            overflow_right = max(0, right - layer.width)

            log(f"Overflow right: {overflow_right:.2f}")

            path_width = (right - left) + overflow_right

            log(f"Path width: {path_width:.2f}")
            log(f"Glyph width: {layer.width}")

            margin = layer.width - path_width
            side = margin / 2

            new_lsb = side
            new_rsb = side

            log(f"New LSB: {new_lsb:.2f}")
            log(f"New RSB: {new_rsb:.2f}")

            layer.LSB = new_lsb
            layer.RSB = new_rsb

            log("✅ TRUE WIDTH CENTER APPLIED")

        except:
            traceback.print_exc()

    # ========= ALIGN =========

    def alignLayer(self, layer):

        log("\n========================")
        log(f"LAYER: {layer.name}")

        items = self.getItems(layer)
        option = self.w.options.get()

        log(f"OPTION: {option}")

        if self.w.trueWidth.get() and option == 4:
            log("MODE: TRUE WIDTH CENTER")
            self.applyTrueWidth(layer)
            return

        ref = self.getReference(layer, items, option)

        for item in items:
            self.moveItem(layer, item, option, ref)

    # ========= MAIN =========

    def align(self, sender):

        log("\n🟢 RUN ALIGN")

        font = Glyphs.font

        if not font.selectedLayers:
            log("No layers selected")
            return

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