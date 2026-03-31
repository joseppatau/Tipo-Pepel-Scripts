# MenuTitle: Alignment (FINAL clean background)
# -*- coding: utf-8 -*-
# Description: Aligns components horizontally using a true italic-aware projection method.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
from GlyphsApp import Glyphs
import math

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)


class AlignTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((160, 300), "Alignment")
        
        self.w.labelX = vanilla.TextBox((15, 10, -15, 20), "X —")
        self.w.options = vanilla.RadioGroup(
            (45, 10, -15, 150),
            ["Up", "Center", "Down", "Left", "Center", "Right"]
        )
        self.w.labelY = vanilla.TextBox((15, 70, -15, 20), "Y |")
        self.w.options.set(4)
        
        self.w.alignButton = vanilla.Button(
            (15, 180, -15, 25),
            "Align Paths",
            callback=self.align
        )
        
        self.w.scope = vanilla.RadioGroup(
            (15, 220, -15, 40),
            ["Current", "All masters"]
        )
        self.w.scope.set(0)

        self.w.open()

    # ========= ITALIC =========

    def deitalicize(self, x, y, angle):
        return x - y * math.tan(math.radians(angle)) if angle else x

    # ========= INTERSECTIONS =========

    def centerFromPaths(self, paths, angle, y_target):
        xs = []

        for path in paths:
            nodes = path.nodes
            if not nodes:
                continue

            for i in range(len(nodes)):
                n1 = nodes[i]
                n2 = nodes[(i + 1) % len(nodes)]

                if (n1.y <= y_target <= n2.y) or (n2.y <= y_target <= n1.y):
                    if n1.y == n2.y:
                        continue

                    t = (y_target - n1.y) / (n2.y - n1.y)
                    x = n1.x + t * (n2.x - n1.x)

                    xs.append(self.deitalicize(x, y_target, angle))

        log(f"  intersections @Y {y_target}: {len(xs)}")

        if len(xs) < 2:
            return None

        center = (min(xs) + max(xs)) / 2
        log(f"  center: {center}")
        return center

    # ========= GLOBAL FALLBACK =========

    def globalCenter(self, paths, angle):
        xs = []

        for p in paths:
            for n in p.nodes:
                xs.append(self.deitalicize(n.x, n.y, angle))

        if not xs:
            return None

        return (min(xs) + max(xs)) / 2

    # ========= GROUPS (SAFE BACKGROUND) =========

    def getGroups(self, layer):
        groups = []
        bg = layer.background

        # 🔥 guardar estat original
        original_paths = [p.copy() for p in bg.paths]
        original_components = [c.copy() for c in bg.components]

        for comp in layer.components:
            bg.clear()
            bg.components.append(comp.copy())
            bg.decomposeComponents()

            paths = list(bg.paths)

            log(f"component → {len(paths)} paths")

            if paths:
                groups.append((comp, paths))

        # 🔥 restaurar background
        bg.clear()
        for p in original_paths:
            bg.paths.append(p)
        for c in original_components:
            bg.components.append(c)

        return groups

    # ========= ALIGN =========

    def alignLayer(self, layer):
        angle = layer.master.italicAngle or 0

        log("\n========================")
        log(f"Layer: {layer.name} | angle: {angle}")

        groups = self.getGroups(layer)

        if len(groups) < 2:
            log("❌ not enough groups")
            return

        sized = []

        for comp, paths in groups:
            xs, ys = [], []

            for p in paths:
                if not p.nodes:
                    continue
                xs.extend([n.x for n in p.nodes])
                ys.extend([n.y for n in p.nodes])

            if not xs or not ys:
                continue

            size = (max(xs)-min(xs)) * (max(ys)-min(ys))
            sized.append((size, comp, paths))

        if len(sized) < 2:
            log("❌ not enough sized elements")
            return

        sized.sort(reverse=True, key=lambda x: x[0])

        ref_comp, ref_paths = sized[0][1], sized[0][2]
        target_comp, target_paths = sized[1][1], sized[1][2]

        log(f"REF size: {sized[0][0]}")
        log(f"TGT size: {sized[1][0]}")

        # ========= MULTI-SAMPLING =========

        ys = []
        for p in target_paths:
            ys.extend([n.y for n in p.nodes])

        if not ys:
            log("❌ no Y values")
            return

        y_values = [
            min(ys),
            (min(ys) + max(ys)) / 2,
            max(ys)
        ]

        ref_centers = []
        cur_centers = []

        for y in y_values:
            log(f"\nSampling Y = {y}")

            ref_c = self.centerFromPaths(ref_paths, angle, y)
            cur_c = self.centerFromPaths(target_paths, angle, y)

            if ref_c is not None and cur_c is not None:
                ref_centers.append(ref_c)
                cur_centers.append(cur_c)

        # ========= FALLBACK =========

        if not ref_centers:
            log("⚠️ using GLOBAL fallback")

            ref_center = self.globalCenter(ref_paths, angle)
            cur_center = self.globalCenter(target_paths, angle)

        else:
            ref_center = sum(ref_centers) / len(ref_centers)
            cur_center = sum(cur_centers) / len(cur_centers)

        dx = round(ref_center - cur_center, 2)
        log(f"DX: {dx}")

        if abs(dx) < 0.01:
            log("⚠️ dx too small")
            return

        before = target_comp.x
        target_comp.applyTransform((1, 0, 0, 1, dx, 0))
        after = target_comp.x

        log(f"Moved: {before} → {after}")

    # ========= MAIN =========

    def align(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            return

        font.disableUpdateInterface()

        for layer in font.selectedLayers:
            glyph = layer.parent

            if self.w.scope.get() == 0:
                self.alignLayer(layer)
            else:
                for l in glyph.layers:
                    if l.isMasterLayer or l.isSpecialLayer:
                        self.alignLayer(l)

        font.enableUpdateInterface()


AlignTool()