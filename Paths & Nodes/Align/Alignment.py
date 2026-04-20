# MenuTitle: Alignment PRO FINAL (All Masters FIXED)
# -*- coding: utf-8 -*-
# Description: Advanced alignment tool for Glyphs using an italic-aware projection method.  
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
import math
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
            # Intentar con alignmentZones (nueva API)
            if hasattr(master, 'alignmentZones'):
                for zone in master.alignmentZones:
                    try:
                        # Verificar si zone tiene atributo size
                        if hasattr(zone, 'size') and zone.size != 0:
                            overshoot_value = abs(zone.size)
                            self.w.overshootValue.set(str(overshoot_value))
                            log(f"Overshoot cargado desde alignmentZones: {overshoot_value}")
                            return
                    except:
                        continue
            
            # Fallback: intentar con blueZones (API antigua)
            if hasattr(master, 'blueZones'):
                for zone in master.blueZones:
                    try:
                        # En Glyphs 3, blueZones puede devolver selectors
                        if hasattr(zone, 'size') and zone.size != 0:
                            overshoot_value = abs(zone.size)
                            self.w.overshootValue.set(str(overshoot_value))
                            log(f"Overshoot cargado desde blueZones: {overshoot_value}")
                            return
                        elif isinstance(zone, (list, tuple)) and len(zone) > 1:
                            # Si zone es una tupla/lista, el segundo elemento podría ser el tamaño
                            if zone[1] != 0:
                                overshoot_value = abs(zone[1])
                                self.w.overshootValue.set(str(overshoot_value))
                                log(f"Overshoot cargado desde blueZones tupla: {overshoot_value}")
                                return
                    except:
                        continue
            
            # Si no encuentra, usar valor por defecto
            self.w.overshootValue.set("10")
            log("No se encontraron zonas de overshoot, usando valor por defecto: 10")
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
                ]

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

    # ========= ALIGN LAYER =========

    def alignLayer(self, layer, ref_bounds=None, ref_component=None):
        """
        Alinea un layer específico.
        Si se proporciona ref_bounds, se usa como referencia.
        Si se proporciona ref_component, se usa ese componente como referencia fija.
        """
        nodes, fullPathsFromNodes = self.getSelectionSmart(layer)
        paths_selected = [p for p in layer.paths if p.selected]
        paths = []
        for p in paths_selected + fullPathsFromNodes:
            if p not in paths:
                paths.append(p)
        comps = [c for c in layer.components if c.selected]
        anchors = [a for a in layer.anchors if a.selected]

        # NODE MODE
        if nodes and not fullPathsFromNodes:
            b = self.getBounds(nodes, layer)
            if not b:
                return
            
            minX, minY, maxX, maxY = b
            cx = (minX + maxX) / 2
            cy = (minY + maxY) / 2
            option = self.w.options.get()

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

        # MODO ESPECIAL: Componente como referencia fija vs Paths
        if ref_component is not None and (paths or anchors):
            log("🔥 MODO: Componente como referencia (fijo) vs Paths")
            
            # El componente de referencia NO se mueve
            # Calculamos sus bounds
            bRef = self.getComponentBounds(ref_component, layer)
            if not bRef:
                return
            
            minXr, minYr, maxXr, maxYr = bRef
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2
            
            # Movemos los paths y anchors seleccionados
            moveItems = paths + anchors
            
            for item in moveItems:
                b = self.getBounds([item], layer)
                if not b:
                    continue
                
                minXi, minYi, maxXi, maxYi = b
                cxi = (minXi + maxXi) / 2
                cyi = (minYi + maxYi) / 2
                option = self.w.options.get()

                if option == 0: dx, dy = 0, maxYr - maxYi
                elif option == 1: dx, dy = 0, cyr - cyi
                elif option == 2: dx, dy = 0, minYr - minYi
                elif option == 3: dx, dy = minXr - minXi, 0
                elif option == 4: dx, dy = cxr - cxi, 0
                elif option == 5: dx, dy = maxXr - maxXi, 0

                self.moveItems([item], dx, dy)
            return

        # Si tenemos ref_bounds (modo multi-master)
        if ref_bounds:
            minXr, minYr, maxXr, maxYr = ref_bounds
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2
        else:
            # Modo normal: calcular bounds de todos los items seleccionados
            all_items = paths + comps + anchors
            if len(all_items) < 2:
                return
            total = self.getBounds(all_items, layer)
            if not total:
                return
            minXr, minYr, maxXr, maxYr = total
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2

        # Mover cada item individualmente
        for item in paths + comps + anchors:
            b = self.getBounds([item], layer)
            if not b:
                continue
            
            minXi, minYi, maxXi, maxYi = b
            cxi = (minXi + maxXi) / 2
            cyi = (minYi + maxYi) / 2
            option = self.w.options.get()

            if option == 0: dx, dy = 0, maxYr - maxYi
            elif option == 1: dx, dy = 0, cyr - cyi
            elif option == 2: dx, dy = 0, minYr - minYi
            elif option == 3: dx, dy = minXr - minXi, 0
            elif option == 4: dx, dy = cxr - cxi, 0
            elif option == 5: dx, dy = maxXr - maxXi, 0

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

        # Obtener el glifo actual
        if not font.selectedLayers:
            return
        
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        
        if self.w.scope.get() == 1:  # All masters
            # Aplicar a todos los masters del glifo actual
            for master in font.masters:
                target_layer = glyph.layers[master.id]
                if target_layer:
                    self.applyYToLayer(target_layer, y)
        else:  # Current master
            self.applyYToLayer(current_layer, y)

        Glyphs.redraw()

    def applyYPreset(self, sender):
        master = Glyphs.font.selectedFontMaster
        preset_index = self.w.yPreset.get()
        
        if preset_index == 0:
            return
        
        # Define presets with their values, overshoot settings, and forced alignment mode
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
            # Intentar con alignmentZones (API más nueva)
            zones = []
            if hasattr(master, 'alignmentZones'):
                zones = master.alignmentZones
            elif hasattr(master, 'blueZones'):
                zones = master.blueZones

            target = value  # baseline, xHeight, etc.

            for z in zones:
                try:
                    # Manejar diferentes tipos de objetos zone
                    if hasattr(z, 'position') and hasattr(z, 'size'):
                        if abs(z.position - target) < 1:
                            overshoot_value = abs(z.size)
                            break
                    elif isinstance(z, (list, tuple)) and len(z) >= 2:
                        if abs(z[0] - target) < 1:
                            overshoot_value = abs(z[1])
                            break
                except:
                    continue

            # fallback
            if overshoot_value == 0:
                overshoot_value = float(self.w.overshootValue.get())

        except Exception as e:
            log(f"Overshoot error: {e}")
            overshoot_value = float(self.w.overshootValue.get())

        self.w.overshootValue.set(str(int(overshoot_value)))
        
        self.w.yInput.set(str(value))
        
        # Obtener el glifo actual
        font = Glyphs.font
        if not font.selectedLayers:
            return
        
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        
        if self.w.scope.get() == 1:  # All masters
            # Aplicar a todos los masters del glifo actual
            for master in font.masters:
                target_layer = glyph.layers[master.id]
                if target_layer:
                    self.applyYToLayer(target_layer, value, apply_overshoot, direction, force_mode)
        else:  # Current master
            self.applyYToLayer(current_layer, value, apply_overshoot, direction, force_mode)
        
        Glyphs.redraw()

    # ========= RUN ALIGN =========

    def align(self, sender):
        font = Glyphs.font
        
        if not font.selectedLayers:
            return
        
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        
        if self.w.scope.get() == 1:  # "All masters" mode
            log("=== ALL MASTERS MODE ===")
            
            # Detectar qué tipo de selección tenemos en el layer actual
            ref_nodes, ref_fullPaths = self.getSelectionSmart(current_layer)
            ref_paths_selected = [p for p in current_layer.paths if p.selected]
            ref_paths = []
            for p in ref_paths_selected + ref_fullPaths:
                if p not in ref_paths:
                    ref_paths.append(p)
            ref_comps = [c for c in current_layer.components if c.selected]
            ref_anchors = [a for a in current_layer.anchors if a.selected]
            
            # MODO 1: Componente como referencia (para alinear paths contra componente)
            if ref_comps and (ref_paths or ref_anchors) and self.w.pathsAsGroup.get():
                log("🔥 ALL MASTERS: Componente como referencia fija")
                # Tomamos el primer componente como referencia
                ref_comp = ref_comps[0]
                
                # Para cada master
                for master in font.masters:
                    target_layer = glyph.layers[master.id]
                    if target_layer:
                        # Encontrar el componente correspondiente en este master
                        target_comp = None
                        for comp in target_layer.components:
                            if comp.componentName == ref_comp.componentName:
                                target_comp = comp
                                break
                        
                        if target_comp:
                            # Alinear paths y anchors contra este componente
                            self.alignLayer(target_layer, ref_component=target_comp)
                        else:
                            log(f"No se encontró componente {ref_comp.componentName} en master {master.name}")
                
                Glyphs.redraw()
                return
            
            # MODO 2: Nodos seleccionados
            if ref_nodes and not ref_fullPaths:
                log("ALL MASTERS: Modo Nodos")
                # Calcular bounds de referencia UNA VEZ
                b_ref = self.getBounds(ref_nodes, current_layer)
                if not b_ref:
                    return
                
                # Para cada master, encontrar los nodos correspondientes
                for master in font.masters:
                    target_layer = glyph.layers[master.id]
                    if target_layer:
                        # Encontrar nodos correspondientes en este master
                        target_nodes = []
                        source_paths = list(current_layer.paths)
                        target_paths = list(target_layer.paths)
                        
                        for source_node in ref_nodes:
                            # Encontrar índice del path y del nodo
                            for path_idx, path in enumerate(source_paths):
                                for node_idx, node in enumerate(path.nodes):
                                    if node is source_node:
                                        if path_idx < len(target_paths):
                                            target_path = target_paths[path_idx]
                                            if node_idx < len(target_path.nodes):
                                                target_nodes.append(target_path.nodes[node_idx])
                                        break
                                else:
                                    continue
                                break
                        
                        # Crear un layer virtual con solo esos nodos para alinear
                        if target_nodes:
                            # Guardar posiciones originales
                            original_positions = [(n.x, n.y) for n in target_nodes]
                            
                            # Aplicar alineación usando los bounds de referencia
                            # Calculamos bounds de los nodos en el target
                            target_bounds = self.getBounds(target_nodes, target_layer)
                            if target_bounds:
                                minXt, minYt, maxXt, maxYt = target_bounds
                                minXr, minYr, maxXr, maxYr = b_ref
                                cxr = (minXr + maxXr) / 2
                                cyr = (minYr + maxYr) / 2
                                cxt = (minXt + maxXt) / 2
                                cyt = (minYt + maxYt) / 2
                                option = self.w.options.get()
                                
                                for n in target_nodes:
                                    if option == 0: dx, dy = 0, maxYr - maxYt
                                    elif option == 1: dx, dy = 0, cyr - cyt
                                    elif option == 2: dx, dy = 0, minYr - minYt
                                    elif option == 3: dx, dy = minXr - minXt, 0
                                    elif option == 4: dx, dy = cxr - cxt, 0
                                    elif option == 5: dx, dy = maxXr - maxXt, 0
                                    n.x += dx
                                    n.y += dy
                
                # También mover los nodos en el layer actual
                self.alignLayer(current_layer, ref_bounds=b_ref)
                Glyphs.redraw()
                return
            
            # MODO 3: Paths, componentes o anchors normales
            ref_items = ref_paths + ref_comps + ref_anchors
            if len(ref_items) < 2:
                log("ALL MASTERS: No hay suficientes items seleccionados para alinear")
                return
            
            ref_bounds = self.getBounds(ref_items, current_layer)
            if not ref_bounds:
                return
            
            # Aplicar a todos los masters del glifo
            for master in font.masters:
                target_layer = glyph.layers[master.id]
                if target_layer:
                    self.alignLayer(target_layer, ref_bounds=ref_bounds)
        
        else:  # "Current" mode
            log("=== CURRENT MASTER MODE ===")
            for layer in font.selectedLayers:
                self.alignLayer(layer)
        
        Glyphs.redraw()


# Iniciar la herramienta
AlignTool()