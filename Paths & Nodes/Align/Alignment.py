# MenuTitle: Alignment (FINAL mapping fix)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs
import math


class AlignTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((160, 270), "Alignment")
        
        self.w.labelX = vanilla.TextBox((15, 10, -15, 20), "X —")
        self.w.options = vanilla.RadioGroup(
            (45, 10, -15, 150),
            ["Up", "Center", "Down", "Left", "Center", "Right"]
        )
        self.w.labelY = vanilla.TextBox((15, 70, -15, 20), "Y |")
        self.w.options.set(4)
        
        self.w.alignButton = vanilla.Button(
            (15, 180, -15, 25),
            "Align",
            callback=self.align
        )
        
        self.w.open()

    # ========= ITALIC =========

    def deitalicize(self, x, y, angle):
        return x - y * math.tan(math.radians(angle)) if angle else x

    # ========= INTERSECTIONS =========

    def centerFromIntersections(self, path, angle, y_target):
        xs = []
        nodes = path.nodes

        for i in range(len(nodes)):
            n1 = nodes[i]
            n2 = nodes[(i + 1) % len(nodes)]

            if (n1.y <= y_target <= n2.y) or (n2.y <= y_target <= n1.y):
                if n1.y == n2.y:
                    continue

                t = (y_target - n1.y) / (n2.y - n1.y)
                x = n1.x + t * (n2.x - n1.x)

                xs.append(self.deitalicize(x, y_target, angle))

        if len(xs) < 2:
            return None

        return (min(xs) + max(xs)) / 2

    # ========= TEMP =========

    def getTemp(self, layer):
        bg = layer.background
        bg.clear()

        for c in layer.components:
            bg.components.append(c.copy())

        bg.decomposeComponents()

        return list(bg.paths), list(layer.components)

    # ========= ALIGN =========

    def alignLayer(self, layer):
        angle = layer.master.italicAngle or 0

        temp_paths, comps = self.getTemp(layer)

        if len(temp_paths) < 2:
            return

        pairs = list(zip(comps, temp_paths))

        sized = []
        for comp, path in pairs:
            xs = [n.x for n in path.nodes]
            ys = [n.y for n in path.nodes]
            size = (max(xs)-min(xs)) * (max(ys)-min(ys))
            sized.append((size, comp, path))

        sized.sort(reverse=True, key=lambda x: x[0])

        ref_comp, ref_path = sized[0][1], sized[0][2]
        target_comp, target_path = sized[1][1], sized[1][2]

        ys = [n.y for n in target_path.nodes]
        y = (min(ys) + max(ys)) / 2

        ref_center = self.centerFromIntersections(ref_path, angle, y)
        cur_center = self.centerFromIntersections(target_path, angle, y)

        if ref_center is None or cur_center is None:
            return

        dx = round(ref_center - cur_center, 2)

        target_comp.applyTransform((1, 0, 0, 1, dx, 0))

    def align(self, sender):
        font = Glyphs.font
        font.disableUpdateInterface()

        for layer in font.selectedLayers:
            self.alignLayer(layer)

        font.enableUpdateInterface()


AlignTool()