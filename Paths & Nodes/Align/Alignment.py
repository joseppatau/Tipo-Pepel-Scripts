# MenuTitle: Alignment PRO FINAL (Ultimate Clean + DEBUG)
# -*- coding: utf-8 -*-
# Description: Advanced alignment tool for Glyphs using an italic-aware projection method.  
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
from GlyphsApp import Glyphs, GSComponent

DEBUG = False  # Cambiado a False para modo silencioso

def log(msg):
    if DEBUG:
        print(msg)


class AlignTool(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow((240, 620), "Alignment PRO")

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
            ["— Presets —", 
             "Baseline", 
             "Baseline Overshoots",
             "x-height", 
             "x-height Overshoots",
             "Cap height", 
             "Cap height Overshoots",
             "Ascenders", 
             "Ascenders Overshoots",
             "Descenders",
             "Descenders Overshoots"],
            callback=self.applyYPreset
        )

        self.w.overshootValueLabel = vanilla.TextBox((15, 405, 100, 20), "Overshoot value:")
        self.w.overshootValue = vanilla.EditText((120, 402, 60, 22), "10")

        # Cargar el valor de overshoot desde el master actual
        self.loadOvershootFromMaster()
        self.detectOvershootFromO()

        self.w.open()

    # ========= ITALIC PROJECTION =========

    def italicX(self, x, y, angle):
        return x - y * math.tan(math.radians(angle))

    # ========= MULTI SAMPLE BOUNDS =========

    def getItalicBounds(self, items, layer):

        angle = layer.italicAngle or 0

        # si no hi ha italic → fallback normal
        if angle == 0:
            return self.getBoundsFallback(items, layer)

        ys = []
        segments = []

        # recollir segments
        for item in items:
            if hasattr(item, "nodes"):
                nodes = item.nodes
                for i in range(len(nodes)):
                    n1 = nodes[i]
                    n2 = nodes[(i + 1) % len(nodes)]

                    segments.append((n1.x, n1.y, n2.x, n2.y))
                    ys.append(n1.y)
                    ys.append(n2.y)

        if not ys:
            return self.getBoundsFallback(items, layer)

        minY = min(ys)
        maxY = max(ys)

        samples = 7
        xs = []

        for i in range(samples):
            y = minY + (maxY - minY) * (i / (samples - 1))

            intersections = []

            for x1, y1, x2, y2 in segments:

                if (y1 <= y <= y2) or (y2 <= y <= y1):
                    if y1 != y2:
                        t = (y - y1) / (y2 - y1)
                        x = x1 + t * (x2 - x1)

                        px = self.italicX(x, y, angle)
                        intersections.append(px)

            if intersections:
                xs.append(min(intersections))
                xs.append(max(intersections))

        if not xs:
            return self.getBoundsFallback(items, layer)

        return (min(xs), minY, max(xs), maxY)


    # ========= FALLBACK =========

    def getBoundsFallback(self, items, layer):
        xs, ys = [], []

        for item in items:
            if hasattr(item, "nodes"):
                for n in item.nodes:
                    xs.append(n.x)
                    ys.append(n.y)
            elif isinstance(item, GSComponent):
                b = self.getComponentBounds(item, layer)
                xs.extend([b[0], b[2]])
                ys.extend([b[1], b[3]])
            elif hasattr(item, "x"):
                xs.append(item.x)
                ys.append(item.y)

        if not xs:
            return None

        return (min(xs), min(ys), max(xs), max(ys))

        
        
    def detectOvershootFromO(self):

        font = Glyphs.font
        master = font.selectedFontMaster

        if "O" not in font.glyphs:
            log("Glyph 'O' not found")
            return

        glyph = font.glyphs["O"]
        layer = glyph.layers[master.id]

        if not layer:
            log("No layer for 'O'")
            return

        # bounds del glif sencer
        b = layer.bounds
        if not b:
            return

        minY = b.origin.y
        maxY = b.origin.y + b.size.height

        # calculem overshoots
        top_overshoot = maxY - master.capHeight
        bottom_overshoot = 0 - minY

        # agafem el més coherent (normalment iguals)
        overshoot = max(abs(top_overshoot), abs(bottom_overshoot))

        log(f"Overshoot from O: {overshoot}")

        # evitar valors absurds
        if overshoot > 0 and overshoot < 200:
            self.w.overshootValue.set(str(int(round(overshoot))))
        
    def loadOvershootFromMaster(self):
        """Lee el valor de overshoot de las blue zones del master actual"""
        try:
            master = Glyphs.font.selectedFontMaster
            if hasattr(master, 'blueZones'):
                for zone in master.blueZones:
                    # Buscar una blue zone con tamaño > 0 (overshoot)
                    if zone.size != 0:
                        overshoot_value = abs(zone.size)
                        self.w.overshootValue.set(str(overshoot_value))
                        log(f"Overshoot cargado desde master: {overshoot_value}")
                        return
            # Si no encuentra blue zones, usa valor por defecto
            self.w.overshootValue.set("10")
            log("No se encontraron blue zones, usando valor por defecto: 10")
        except Exception as e:
            log(f"Error cargando overshoot: {e}")
            self.w.overshootValue.set("10")

    # ========= SMART SELECTION =========

    def getSelectionSmart(self, layer):
        partial_nodes = []
        full_paths = []

        for p in layer.paths:
            selected_nodes = [n for n in p.nodes if n.selected]

            if not selected_nodes:
                continue

            if len(selected_nodes) == len(p.nodes):
                full_paths.append(p)
            else:
                partial_nodes.extend(selected_nodes)

        return partial_nodes, full_paths

    # ========= OVERSHOOT =========

    def getOvershootValue(self):
        try:
            return float(self.w.overshootValue.get())
        except:
            return 10

    # ========= COMPONENT BOUNDS =========

    def getComponentBounds(self, comp, layer):

        try:
            b = comp.bounds
            if b and b.size.width > 0 and b.size.height > 0:
                return (b.origin.x, b.origin.y,
                        b.origin.x + b.size.width,
                        b.origin.y + b.size.height)
        except:
            pass

        try:
            glyph = Glyphs.font.glyphs[comp.componentName]
            layer_orig = glyph.layers[layer.master.id]
            b = layer_orig.bounds

            if b and b.size.width > 0:
                t = comp.transform

                pts = [
                    (b.origin.x, b.origin.y),
                    (b.origin.x + b.size.width, b.origin.y),
                    (b.origin.x, b.origin.y + b.size.height),
                    (b.origin.x + b.size.width, b.origin.y + b.size.height),
             alignLayer   ]

                xs = [t.a*x + t.c*y + t.tx for x, y in pts]
                ys = [t.b*x + t.d*y + t.ty for x, y in pts]

                return (min(xs), min(ys), max(xs), max(ys))
        except:
            pass

        return (comp.transform.tx, comp.transform.ty,
                comp.transform.tx, comp.transform.ty)

    # ========= BOUNDS =========

    def getBounds(self, items, layer):
        return self.getItalicBounds(items, layer)
        xs, ys = [], []

        for item in items:
            if hasattr(item, "nodes"):
                for n in item.nodes:
                    xs.append(n.x)
                    ys.append(n.y)
            elif hasattr(item, "position"):
                xs.append(item.x)
                ys.append(item.y)
            elif isinstance(item, GSComponent):
                b = self.getComponentBounds(item, layer)
                xs.extend([b[0], b[2]])
                ys.extend([b[1], b[3]])
            elif hasattr(item, "x"):
                xs.append(item.x)
                ys.append(item.y)

        if not xs:
            return None

        return (min(xs), min(ys), max(xs), max(ys))

    # ========= MOVE =========

    def moveItems(self, items, dx, dy):
        if dx == 0 and dy == 0:
            return

        log(f"MOVE dx={dx}, dy={dy}")

        for item in items:
            if hasattr(item, "nodes"):
                for n in item.nodes:
                    n.x += dx
                    n.y += dy
            elif hasattr(item, "position"):
                item.x += dx
                item.y += dy
            elif hasattr(item, "x"):
                item.x += dx
                item.y += dy

    # ========= ALIGN =========

    def alignLayer(self, layer):

        nodes, fullPathsFromNodes = self.getSelectionSmart(layer)

        paths_selected = [p for p in layer.paths if p.selected]
        paths = []
        for p in paths_selected + fullPathsFromNodes:
            if p not in paths:
                paths.append(p)
        comps = [c for c in layer.components if c.selected]
        anchors = [a for a in layer.anchors if a.selected]

        option = self.w.options.get()

        # ===== DEBUG GLOBAL =====
        if DEBUG:
            log("\n====================")
            log("NEW ALIGN CALL")
            log(f"Nodes partial: {len(nodes)}")
            log(f"Full paths: {len(fullPathsFromNodes)}")
            log(f"Paths selected: {len(paths_selected)}")
            log(f"Paths FINAL: {len(paths)}")
            log(f"Components: {len(comps)}")
            log(f"Anchors: {len(anchors)}")
            log(f"pathsAsGroup: {self.w.pathsAsGroup.get()}")

        # NODE MODE
        
        # ===== NEW CASE: FULL PATH ↔ SEGMENT =====
        if nodes and fullPathsFromNodes:

            log("🧠 MODE: FULL PATH ↔ SEGMENT")

            # Segment (nodes parcials) = referencia
            bRef = self.getBounds(nodes, layer)
            if not bRef:
                return

            minXr, minYr, maxXr, maxYr = bRef
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2

            # Paths completos = elementos a mover
            for p in fullPathsFromNodes:

                b = self.getBounds([p], layer)
                if not b:
                    continue

                minX, minY, maxX, maxY = b
                cx = (minX + maxX) / 2
                cy = (minY + maxY) / 2

                if option == 0: dx, dy = 0, maxYr - maxY
                elif option == 1: dx, dy = 0, cyr - cy
                elif option == 2: dx, dy = 0, minYr - minY
                elif option == 3: dx, dy = minXr - minX, 0
                elif option == 4: dx, dy = cxr - cx, 0
                elif option == 5: dx, dy = maxXr - maxX, 0

                log(f"→ Move FULL PATH dx={dx}, dy={dy}")
                self.moveItems([p], dx, dy)

            return
        
        if nodes and not fullPathsFromNodes:
            log("MODE: NODE")
            b = self.getBounds(nodes, layer)
            log(f"Bounds NODE: {b}")
            minX, minY, maxX, maxY = b
            cx = (minX + maxX) / 2
            cy = (minY + maxY) / 2

            for n in nodes:
                if option == 0: dx, dy = 0, maxY - n.y
                elif option == 1: dx, dy = 0, cy - n.y
                elif option == 2: dx, dy = 0, minY - n.y
                elif option == 3: dx, dy = minX - n.x, 0
                elif option == 4: dx, dy = cx - n.x, 0
                elif option == 5: dx, dy = maxX - n.x, 0
                n.x += dx
                n.y += dy
            return

        # COMPONENT ↔ COMPONENT
        if len(comps) >= 2 and not paths and not anchors:
            log("MODE: COMPONENT ↔ COMPONENT")

            ref = comps[0]
            bRef = self.getComponentBounds(ref, layer)
            log(f"Ref bounds: {bRef}")

            minXr, minYr, maxXr, maxYr = bRef
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2

            for comp in comps[1:]:
                b = self.getComponentBounds(comp, layer)
                log(f"Comp bounds: {b}")

                minX, minY, maxX, maxY = b
                cx = (minX + maxX) / 2
                cy = (minY + maxY) / 2

                if option == 0: dx, dy = 0, maxYr - maxY
                elif option == 1: dx, dy = 0, cyr - cy
                elif option == 2: dx, dy = 0, minYr - minY
                elif option == 3: dx, dy = minXr - minX, 0
                elif option == 4: dx, dy = cxr - cx, 0
                elif option == 5: dx, dy = maxXr - maxX, 0

                log(f"→ Move component dx={dx}, dy={dy}")
                comp.x += dx
                comp.y += dy

            return

        # DEBUG CONDITION
        if DEBUG:
            log("CHECK PATH ↔ COMPONENT:")
            log(f"comps: {bool(comps)}")
            log(f"paths/anchors: {bool(paths or anchors)}")
            log(f"pathsAsGroup: {self.w.pathsAsGroup.get()}")

        # PATH ↔ COMPONENT
        if comps and (paths or anchors) and self.w.pathsAsGroup.get():

            log("🔥 ENTER PATH ↔ COMPONENT")

            moveItems = paths + anchors
            ref = comps[0]

            bMove = self.getBounds(moveItems, layer)
            bRef = self.getComponentBounds(ref, layer)

            log(f"Bounds MOVE: {bMove}")
            log(f"Bounds REF: {bRef}")

            minX, minY, maxX, maxY = bMove
            minXr, minYr, maxXr, maxYr = bRef

            cx = (minX + maxX) / 2
            cy = (minY + maxY) / 2
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2

            log(f"Center MOVE: {cx}, {cy}")
            log(f"Center REF: {cxr}, {cyr}")

            if option == 0: dx, dy = 0, maxYr - maxY
            elif option == 1: dx, dy = 0, cyr - cy
            elif option == 2: dx, dy = 0, minYr - minY
            elif option == 3: dx, dy = minXr - minX, 0
            elif option == 4: dx, dy = cxr - cx, 0
            elif option == 5: dx, dy = maxXr - maxX, 0

            log(f"RESULT dx={dx}, dy={dy}")

            self.moveItems(moveItems, dx, dy)
            return
        # ===== NEW CASE: MULTIPLE PATHS (SMART REFERENCE BY AREA) =====
        if not nodes and not comps and len(paths) >= 2:

            log("🧠 MODE: MULTI PATH SMART ALIGN")

            bounds_list = []

            for p in paths:
                b = self.getBounds([p], layer)
                if not b:
                    continue

                minX, minY, maxX, maxY = b
                area = (maxX - minX) * (maxY - minY)

                bounds_list.append((p, b, area))

            if len(bounds_list) < 2:
                return

            # ordenar per àrea (gran → petit)
            bounds_list.sort(key=lambda x: x[2], reverse=True)

            ref, bRef, _ = bounds_list[0]

            minXr, minYr, maxXr, maxYr = bRef
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2

            # tots els altres es mouen
            for p, b, _ in bounds_list[1:]:

                minX, minY, maxX, maxY = b
                cx = (minX + maxX) / 2
                cy = (minY + maxY) / 2

                if option == 0: dx, dy = 0, maxYr - maxY
                elif option == 1: dx, dy = 0, cyr - cy
                elif option == 2: dx, dy = 0, minYr - minY
                elif option == 3: dx, dy = minXr - minX, 0
                elif option == 4: dx, dy = cxr - cx, 0
                elif option == 5: dx, dy = maxXr - maxX, 0

                log(f"→ Move PATH dx={dx}, dy={dy}")
                self.moveItems([p], dx, dy)

            return
            
            
        # DEFAULT
        log("MODE: DEFAULT")

        all_items = paths + comps + anchors

        if len(all_items) < 2:
            return

        total = self.getBounds(all_items, layer)
        log(f"Bounds TOTAL: {total}")

        minX, minY, maxX, maxY = total
        cx = (minX + maxX) / 2
        cy = (minY + maxY) / 2

        for item in all_items:
            b = self.getBounds([item], layer)
            log(f"Item bounds: {b}")

            minXi, minYi, maxXi, maxYi = b
            cxi = (minXi + maxXi) / 2
            cyi = (minYi + maxYi) / 2

            if option == 0: dx, dy = 0, maxY - maxYi
            elif option == 1: dx, dy = 0, cy - cyi
            elif option == 2: dx, dy = 0, minY - minYi
            elif option == 3: dx, dy = minX - minXi, 0
            elif option == 4: dx, dy = cx - cxi, 0
            elif option == 5: dx, dy = maxX - maxXi, 0

            log(f"→ Move item dx={dx}, dy={dy}")
            self.moveItems([item], dx, dy)

    # ========= Y POSITION =========

    def applyYToLayer(self, layer, targetY, applyOvershoot=False, overshootDirection="north", forceAlignMode=None):
        """
        forceAlignMode: Puede ser "up", "down" o None (usa el modo de la UI)
        """
        items = list(layer.paths) + list(layer.components) + list(layer.anchors)
        items = [i for i in items if i.selected]

        if not items:
            return

        b = self.getBounds(items, layer)
        if not b:
            return

        minX, minY, maxX, maxY = b
        
        # Determinar modo de alineación
        if forceAlignMode == "up":
            mode = 0  # Up
        elif forceAlignMode == "down":
            mode = 2  # Down
        else:
            mode = self.w.yMode.get()  # Usar el modo de la UI
        
        overshoot = self.getOvershootValue() if applyOvershoot else 0

        if mode == 0:  # Up (align top)
            # Para norte: SUMAR overshoot
            # Para sur: RESTAR overshoot
            if applyOvershoot and overshootDirection == "north":
                targetY_adjusted = targetY + overshoot
            elif applyOvershoot and overshootDirection == "south":
                targetY_adjusted = targetY - overshoot
            else:
                targetY_adjusted = targetY
            dy = targetY_adjusted - maxY
        elif mode == 1:  # Center
            dy = targetY - ((minY + maxY) / 2)
        else:  # Down (align bottom)
            # Para sur: RESTAR overshoot
            # Para norte: SUMAR overshoot
            if applyOvershoot and overshootDirection == "south":
                targetY_adjusted = targetY - overshoot
            elif applyOvershoot and overshootDirection == "north":
                targetY_adjusted = targetY + overshoot
            else:
                targetY_adjusted = targetY
            dy = targetY_adjusted - minY

        log(f"Y MOVE: forceMode={forceAlignMode}, finalMode={mode}, targetY={targetY}, overshoot={overshoot}, direction={overshootDirection}, targetY_adjusted={targetY_adjusted}, dy={dy}")

        self.moveItems(items, 0, dy)

    def applyYPosition(self, sender):
        font = Glyphs.font

        try:
            y = float(self.w.yInput.get())
        except:
            log("Invalid Y input")
            return

        for layer in font.selectedLayers:
            if self.w.scope.get():
                for m in font.masters:
                    self.applyYToLayer(layer.parent.layers[m.id], y)
            else:
                self.applyYToLayer(layer, y)

        Glyphs.redraw()

    def applyYPreset(self, sender):
        master = Glyphs.font.selectedFontMaster
        preset_index = self.w.yPreset.get()
        
        if preset_index == 0:
            return
        
        # Define presets with their values, overshoot settings, and forced alignment mode
        # Baseline = 0 (cero)
        # Descenders = master.descender (valor negativo)
        presets = [
            ("Baseline", 0, False, None, "down"),
            ("Baseline Overshoots", 0, True, "south", "down"),
            ("x-height", master.xHeight, False, None, "up"),
            ("x-height Overshoots", master.xHeight, True, "north", "up"),
            ("Cap height", master.capHeight, False, None, "up"),
            ("Cap height Overshoots", master.capHeight, True, "north", "up"),
            ("Ascenders", master.ascender, False, None, "up"),
            ("Ascenders Overshoots", master.ascender, True, "north", "up"),
            ("Descenders", master.descender, False, None, "down"),
            ("Descenders Overshoots", master.descender, True, "south", "down")
        ]
        
        preset_name, value, apply_overshoot, direction, force_mode = presets[preset_index - 1]
        
        
        
        # ===== AUTO OVERSHOOT (MATCH EXACT METRIC ZONE) =====
        overshoot_value = 0

        try:
            zones = getattr(master, "alignmentZones", [])

            target = value  # baseline, xHeight, etc.

            for z in zones:
                # match exacte amb la mètrica
                if abs(z.position - target) < 1:  # tolerància mínima
                    overshoot_value = abs(z.size)
                    break

            # fallback
            if overshoot_value == 0:
                overshoot_value = float(self.w.overshootValue.get())

        except Exception as e:
            log(f"Overshoot error: {e}")
            overshoot_value = float(self.w.overshootValue.get())

        self.w.overshootValue.set(str(int(overshoot_value)))
        
        
        
        
        self.w.yInput.set(str(value))
        
        # Apply the Y position with overshoot if needed
        font = Glyphs.font
        for layer in font.selectedLayers:
            if self.w.scope.get():
                for m in font.masters:
                    self.applyYToLayer(layer.parent.layers[m.id], value, apply_overshoot, direction, force_mode)
            else:
                self.applyYToLayer(layer, value, apply_overshoot, direction, force_mode)
        
        Glyphs.redraw()

    # ========= RUN =========

    def align(self, sender):
        font = Glyphs.font
        for layer in font.selectedLayers:
            self.alignLayer(layer)
        Glyphs.redraw()
        
        


AlignTool()