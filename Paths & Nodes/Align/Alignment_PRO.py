# MenuTitle: Alignment PRO FIXED (Italic X)
# -*- coding: utf-8 -*-

import vanilla
import math
from GlyphsApp import Glyphs, GSComponent

DEBUG = True

def log(msg):
    if DEBUG:
        print(f"🔍 {msg}")


class AlignTool(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow((140, 550), "Alignment PRO")

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

        self.w.useItalicProjection = vanilla.CheckBox(
            (15, 285, -15, 20),
            "Italic X",
            value=False
        )

        # ===== Y POSITION =====
        self.w.sep = vanilla.HorizontalLine((10, 315, -10, 1))

        # Y Mode - 3 files verticals
        self.w.yModeUp = vanilla.RadioButton((15, 325, 60, 20), "Up", value=True, callback=self.yModeChanged)
        self.w.yModeCen = vanilla.RadioButton((15, 350, 60, 20), "Center", value=False, callback=self.yModeChanged)
        self.w.yModeDown = vanilla.RadioButton((15, 375, 60, 20), "Down", value=False, callback=self.yModeChanged)

        self.w.yLabel = vanilla.TextBox((15, 405, 80, 20), "Y pos")

        self.w.yInput = vanilla.EditText((55, 402, 40, 22), "0")

        self.w.yApply = vanilla.Button(
            (100, 400, 24, 24),
            "▶",
            callback=self.applyYPosition
        )

        self.w.yPreset = vanilla.PopUpButton(
            (15, 435, -15, 25),
            ["— Presets —", 
             "Baseline", 
             "Baseline Overshoots",
             "x-height", 
             "X Height center",
             "x-height Overshoots",
             "Cap height", 
             "Cap height Overshoots",
             "Ascenders", 
             "Ascenders Overshoots",
             "Descenders",
             "Descenders Overshoots"],
            callback=self.applyYPreset
        )

        self.w.overshootValueLabel = vanilla.TextBox((15, 470, 100, 20), "Overshoot value:")
        self.w.overshootValue = vanilla.EditText((15, 493, 40, 22), "10")

        if not self.loadOvershootFromMaster():
            self.detectOvershootFromO()

        self.w.open()
        log("=== Alignment PRO iniciado ===")
        
        
    # ========= ITALIC PROJECTION =========
    def yModeChanged(self, sender):
        """Gestiona el canvi dels RadioButtons Up/Cen/Down"""
        self.w.yModeUp.set(sender == self.w.yModeUp)
        self.w.yModeCen.set(sender == self.w.yModeCen)
        self.w.yModeDown.set(sender == self.w.yModeDown)
        
    def italicX(self, x, y, angle):
        return x - y * math.tan(math.radians(angle))

    def useItalicProjection(self):
        try:
            return bool(self.w.useItalicProjection.get())
        except:
            return False

    def getItalicAngle(self, layer):
        try:
            return float(layer.master.italicAngle or 0)
        except:
            try:
                return float(Glyphs.font.selectedFontMaster.italicAngle or 0)
            except:
                return 0

    def projectX(self, x, y, layer):
        if not self.useItalicProjection():
            return x
        return self.italicX(x, y, self.getItalicAngle(layer))

    def boundsFromPoints(self, points, layer):
        points = list(points)
        xs = [self.projectX(x, y, layer) for x, y in points]
        ys = [y for x, y in points]
        return (min(xs), min(ys), max(xs), max(ys))

    def offsetForBounds(self, ref_bounds, item_bounds, option):
        minXr, minYr, maxXr, maxYr = ref_bounds
        minXi, minYi, maxXi, maxYi = item_bounds
        cxr = (minXr + maxXr) / 2
        cyr = (minYr + maxYr) / 2
        cxi = (minXi + maxXi) / 2
        cyi = (minYi + maxYi) / 2

        if option == 0:
            return (0, maxYr - maxYi)
        if option == 1:
            return (0, cyr - cyi)
        if option == 2:
            return (0, minYr - minYi)
        if option == 3:
            return (minXr - minXi, 0)
        if option == 4:
            return (cxr - cxi, 0)
        if option == 5:
            return (maxXr - maxXi, 0)
        return (0, 0)

    # ========= GET BOUNDS DIRECTLY =========

    def getRealBounds(self, items, layer):
        """
        Bounds robustos para:
        - nodos (GSNode)
        - paths
        - componentes
        - anchors
        """

        if not items:
            return None

        xs = []
        ys = []

        for item in items:

            # ===== NODOS =====
            if hasattr(item, "x") and hasattr(item, "y"):
                xs.append(self.projectX(item.x, item.y, layer))
                ys.append(item.y)
                log(f"    Node: ({item.x:.1f}, {item.y:.1f})")
                continue

            # ===== ITEMS CON BOUNDS (paths, comps, anchors) =====
            if hasattr(item, "bounds"):
                try:
                    b = item.bounds
                    if b:
                        minX = b.origin.x
                        minY = b.origin.y
                        maxX = b.origin.x + b.size.width
                        maxY = b.origin.y + b.size.height

                        projected = self.boundsFromPoints(
                            [
                                (minX, minY),
                                (maxX, minY),
                                (minX, maxY),
                                (maxX, maxY),
                            ],
                            layer
                        )
                        minX, minY, maxX, maxY = projected

                        xs.extend([minX, maxX])
                        ys.extend([minY, maxY])

                        log(f"    Bounds: ({minX:.1f}, {minY:.1f}, {maxX:.1f}, {maxY:.1f})")
                        continue
                except:
                    pass

            # ===== FALLBACK (por seguridad) =====
            if hasattr(item, "nodes"):
                try:
                    for n in item.nodes:
                        xs.append(self.projectX(n.x, n.y, layer))
                        ys.append(n.y)
                except:
                    pass

        if not xs or not ys:
            log("    ⚠️ No se pudieron extraer coordenadas")
            return None

        minX = min(xs)
        minY = min(ys)
        maxX = max(xs)
        maxY = max(ys)

        log(f"    FINAL BOUNDS: ({minX:.1f}, {minY:.1f}, {maxX:.1f}, {maxY:.1f})")

        return (minX, minY, maxX, maxY)
            
                
    def getComponentRealBounds(self, comp, layer):
        """Obtiene bounds reales de un componente"""
        try:
            b = comp.bounds
            if b and b.size.width > 0:
                minX = b.origin.x
                minY = b.origin.y
                maxX = b.origin.x + b.size.width
                maxY = b.origin.y + b.size.height
                return self.boundsFromPoints(
                    [(minX, minY), (maxX, minY), (minX, maxY), (maxX, maxY)],
                    layer
                )
        except:
            pass
        
        # Fallback
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
                return self.boundsFromPoints(zip(xs, ys), layer)
        except:
            pass
        
        return None

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

        b = layer.bounds
        if not b:
            return

        minY = b.origin.y
        maxY = b.origin.y + b.size.height

        top_overshoot = maxY - master.capHeight
        bottom_overshoot = 0 - minY

        overshoot = max(abs(top_overshoot), abs(bottom_overshoot))

        log(f"Overshoot from O: {overshoot}")

        if overshoot > 0 and overshoot < 200:
            self.w.overshootValue.set(str(int(round(overshoot))))

    def formatNumber(self, value):
        try:
            if float(value).is_integer():
                return str(int(value))
        except:
            pass
        return str(value)

    def zonePositionAndSize(self, zone):
        position = None
        size = None

        try:
            if hasattr(zone, "position"):
                position = float(zone.position)
        except:
            position = None

        try:
            if hasattr(zone, "size"):
                size = float(zone.size)
        except:
            size = None

        if isinstance(zone, (list, tuple)):
            try:
                if len(zone) > 0:
                    position = float(zone[0])
                if len(zone) > 1:
                    size = float(zone[1])
            except:
                pass

        return position, size

    def metricPositionAndOvershoot(self, metric_value):
        position = None
        overshoot = None

        for attr in ("position", "pos", "value"):
            try:
                if hasattr(metric_value, attr):
                    position = float(getattr(metric_value, attr))
                    break
            except:
                pass

        try:
            if hasattr(metric_value, "overshoot"):
                overshoot = float(metric_value.overshoot)
        except:
            overshoot = None

        if isinstance(metric_value, (list, tuple)):
            try:
                if len(metric_value) > 0:
                    position = float(metric_value[0])
                if len(metric_value) > 1:
                    overshoot = float(metric_value[1])
            except:
                pass

        return position, overshoot

    def masterMetricValues(self, master):
        values = []

        try:
            metrics = master.metrics
        except:
            return values

        try:
            if hasattr(metrics, "values"):
                values.extend(list(metrics.values()))
                return values
        except:
            pass

        try:
            if hasattr(metrics, "allValues"):
                values.extend(list(metrics.allValues()))
                return values
        except:
            pass

        try:
            values.extend(list(metrics))
        except:
            pass

        return values

    def bestOvershootCandidate(self, entries, targetY=None, direction=None):
        candidates = []
        fallback = None
        saw_position = False

        for position, size in entries:
            if size is None or size == 0:
                continue

            overshoot_value = abs(size)
            if fallback is None:
                fallback = overshoot_value

            if targetY is not None and position is not None:
                saw_position = True
                distance = abs(position - targetY)
                if distance <= 1:
                    direction_match = True
                    if direction == "north":
                        direction_match = size > 0
                    elif direction == "south":
                        direction_match = size < 0
                    candidates.append((0 if direction_match else 1, distance, overshoot_value))

        if candidates:
            candidates.sort(key=lambda item: (item[0], item[1]))
            return candidates[0][2]

        if targetY is None or not saw_position:
            return fallback

        return None

    def getMasterOvershootValue(self, master, targetY=None, direction=None):
        """
        Llegeix l'overshoot definit a Font Info > Masters > Metrics.
        Per presets concrets es busca la zona situada a la mateixa mètrica.
        """
        metric_entries = []
        for metric_value in self.masterMetricValues(master):
            metric_entries.append(self.metricPositionAndOvershoot(metric_value))

        overshoot_value = self.bestOvershootCandidate(metric_entries, targetY, direction)
        if overshoot_value is not None:
            log(f"Overshoot leído desde Metrics/Master '{master.name}': {overshoot_value}")
            return overshoot_value

        zones = []

        try:
            if hasattr(master, "alignmentZones"):
                zones.extend(list(master.alignmentZones))
        except:
            pass

        try:
            if hasattr(master, "blueZones"):
                zones.extend(list(master.blueZones))
        except:
            pass

        zone_entries = []

        for zone in zones:
            zone_entries.append(self.zonePositionAndSize(zone))

        overshoot_value = self.bestOvershootCandidate(zone_entries, targetY, direction)
        if overshoot_value is not None:
            log(f"Overshoot leído desde Zones/Master '{master.name}': {overshoot_value}")
            return overshoot_value

        return None
        
    def loadOvershootFromMaster(self):
        try:
            master = Glyphs.font.selectedFontMaster
            overshoot_value = self.getMasterOvershootValue(master)
            if overshoot_value is not None:
                self.w.overshootValue.set(self.formatNumber(overshoot_value))
                return True

            self.w.overshootValue.set("10")
            log("No se encontraron zonas de overshoot, usando valor por defecto: 10")
            return False
        except Exception as e:
            log(f"Error cargando overshoot: {e}")
            self.w.overshootValue.set("10")
            return False

    # ========= SMART SELECTION =========

    def getSelectionReference(self, layer):
        """
        Guarda la selecció del màster actiu com a índexs estructurals.
        Això permet reconstruir els mateixos nodes/items en altres màsters,
        on Glyphs no conserva necessàriament el flag selected.
        """
        ref = {
            "nodes": [],
            "full_paths": [],
            "paths": [],
            "components": [],
            "anchors": [],
        }

        for path_index, path in enumerate(layer.paths):
            selected_nodes = [n for n in path.nodes if n.selected]

            if selected_nodes:
                if len(selected_nodes) == len(path.nodes):
                    ref["full_paths"].append(path_index)
                else:
                    for node_index, node in enumerate(path.nodes):
                        if node.selected:
                            ref["nodes"].append((path_index, node_index))

            if path.selected:
                ref["paths"].append(path_index)

        for component_index, component in enumerate(layer.components):
            if component.selected:
                ref["components"].append((component_index, component.componentName))

        for anchor_index, anchor in enumerate(layer.anchors):
            if anchor.selected:
                ref["anchors"].append((anchor_index, anchor.name))

        return ref

    def selectionReferenceHasItems(self, selection_ref):
        if not selection_ref:
            return False
        return any(selection_ref.get(key) for key in ("nodes", "full_paths", "paths", "components", "anchors"))

    def itemNotInList(self, item, items):
        return all(existing is not item for existing in items)

    def getSelectionSmart(self, layer, selection_ref=None):
        partial_nodes = []
        full_paths = []

        if selection_ref is not None:
            for path_index, node_index in selection_ref.get("nodes", []):
                try:
                    partial_nodes.append(layer.paths[path_index].nodes[node_index])
                except Exception as e:
                    log(f"  ⚠️ No se pudo reconstruir nodo path={path_index}, node={node_index}: {e}")

            for path_index in selection_ref.get("full_paths", []):
                try:
                    full_paths.append(layer.paths[path_index])
                except Exception as e:
                    log(f"  ⚠️ No se pudo reconstruir path completo index={path_index}: {e}")

            return partial_nodes, full_paths

        for p in layer.paths:
            selected_nodes = [n for n in p.nodes if n.selected]

            if not selected_nodes:
                continue

            if len(selected_nodes) == len(p.nodes):
                full_paths.append(p)
            else:
                partial_nodes.extend(selected_nodes)

        return partial_nodes, full_paths

    def getLayerSelection(self, layer, selection_ref=None, use_all_items=False):
        if use_all_items:
            return [], [], list(layer.paths), list(layer.components), list(layer.anchors)

        nodes, fullPathsFromNodes = self.getSelectionSmart(layer, selection_ref)

        if selection_ref is None:
            paths_selected = [p for p in layer.paths if p.selected]
            comps = [c for c in layer.components if c.selected]
            anchors = [a for a in layer.anchors if a.selected]
        else:
            paths_selected = []
            for path_index in selection_ref.get("paths", []):
                try:
                    paths_selected.append(layer.paths[path_index])
                except Exception as e:
                    log(f"  ⚠️ No se pudo reconstruir path index={path_index}: {e}")

            comps = []
            for component_index, component_name in selection_ref.get("components", []):
                target_comp = None
                try:
                    candidate = layer.components[component_index]
                    if candidate.componentName == component_name:
                        target_comp = candidate
                except:
                    pass

                if target_comp is None:
                    for component in layer.components:
                        if component.componentName == component_name:
                            target_comp = component
                            break

                if target_comp is not None:
                    comps.append(target_comp)
                else:
                    log(f"  ⚠️ No se pudo reconstruir componente '{component_name}'")

            anchors = []
            for anchor_index, anchor_name in selection_ref.get("anchors", []):
                target_anchor = None
                try:
                    candidate = layer.anchors[anchor_index]
                    if candidate.name == anchor_name:
                        target_anchor = candidate
                except:
                    pass

                if target_anchor is None:
                    for anchor in layer.anchors:
                        if anchor.name == anchor_name:
                            target_anchor = anchor
                            break

                if target_anchor is not None:
                    anchors.append(target_anchor)
                else:
                    log(f"  ⚠️ No se pudo reconstruir anchor '{anchor_name}'")

        paths = []
        for path in paths_selected + fullPathsFromNodes:
            if self.itemNotInList(path, paths):
                paths.append(path)

        return nodes, fullPathsFromNodes, paths, comps, anchors

    # ========= OVERSHOOT =========

    def getOvershootValue(self):
        try:
            return float(self.w.overshootValue.get())
        except:
            return 10

    # ========= MOVE =========

    def moveItems(self, items, dx, dy):
        if dx == 0 and dy == 0:
            return

        log(f"  MOVE dx={dx:.1f}, dy={dy:.1f}")

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

    def isOffCurveNode(self, node):
        try:
            return "offcurve" in str(node.type).lower()
        except:
            return False

    def moveNodeWithHandles(self, node, dx, dy, moved=None, selected_oncurves=None):
        if dx == 0 and dy == 0:
            return
        if moved is None:
            moved = set()
        if selected_oncurves is None:
            selected_oncurves = set()

        nodes_to_move = [node]

        if not self.isOffCurveNode(node):
            try:
                path_nodes = list(node.parent.nodes)
                index = path_nodes.index(node)
                count = len(path_nodes)
                closed = bool(getattr(node.parent, "closed", False))

                for direction in (-1, 1):
                    handle_indexes = []
                    next_index = index + direction

                    while True:
                        if closed:
                            next_index %= count
                            if next_index == index:
                                break
                        elif next_index < 0 or next_index >= count:
                            break

                        next_node = path_nodes[next_index]
                        if not self.isOffCurveNode(next_node):
                            break

                        handle_indexes.append(next_index)
                        next_index += direction

                    opposite_oncurve = None
                    if handle_indexes:
                        if closed:
                            next_index %= count
                            if next_index != index:
                                candidate = path_nodes[next_index]
                                if not self.isOffCurveNode(candidate):
                                    opposite_oncurve = candidate
                        elif 0 <= next_index < count:
                            candidate = path_nodes[next_index]
                            if not self.isOffCurveNode(candidate):
                                opposite_oncurve = candidate

                    opposite_selected = (
                        opposite_oncurve is not None
                        and id(opposite_oncurve) in selected_oncurves
                    )

                    for handle_index in handle_indexes:
                        handle = path_nodes[handle_index]
                        if getattr(handle, "selected", False) or opposite_selected:
                            nodes_to_move.append(handle)
            except Exception as e:
                log(f"  ⚠️ No se pudieron arrastrar handles: {e}")

        for item in nodes_to_move:
            ident = id(item)
            if ident in moved:
                continue
            item.x += dx
            item.y += dy
            moved.add(ident)

    # ========= CALCULATE ALIGNMENT OFFSET FOR NODES VS ANCHOR =========
    
    def calculateAnchorOffsetFromNodes(self, layer, anchor, nodes, option):
        """
        Calcula el offset necesario para alinear un anchor respecto a unos nodos.
        Retorna (dx, dy) o None.
        """
        log(f"    === calculateAnchorOffsetFromNodes ===")
        
        b_nodes = self.getRealBounds(nodes, layer)
        if not b_nodes:
            log(f"    ❌ No se pudieron obtener bounds de los nodos")
            return None
        
        minX_n, minY_n, maxX_n, maxY_n = b_nodes
        cx_n = (minX_n + maxX_n) / 2
        cy_n = (minY_n + maxY_n) / 2
        
        log(f"    📊 NODOS REFERENCIA:")
        log(f"       - minX: {minX_n:.2f}, minY: {minY_n:.2f}")
        log(f"       - maxX: {maxX_n:.2f}, maxY: {maxY_n:.2f}")
        log(f"       - center X: {cx_n:.2f}, center Y: {cy_n:.2f}")
        log(f"    📍 ANCHOR (antes de mover):")
        log(f"       - nombre: {anchor.name if hasattr(anchor, 'name') else 'sin nombre'}")
        log(f"       - posición: ({anchor.x:.2f}, {anchor.y:.2f})")
        anchor_x = self.projectX(anchor.x, anchor.y, layer)
        
        option_names = ["Up", "Center Y", "Down", "Left", "Center X", "Right"]
        log(f"    🎯 Opción de alineación: {option_names[option]}")
        
        if option == 0:  # Up
            dx, dy = 0, maxY_n - anchor.y
            log(f"    📐 Cálculo: dy = maxY_n ({maxY_n:.2f}) - anchor.y ({anchor.y:.2f}) = {dy:.2f}")
        elif option == 1:  # Center Y
            dx, dy = 0, cy_n - anchor.y
            log(f"    📐 Cálculo: dy = cy_n ({cy_n:.2f}) - anchor.y ({anchor.y:.2f}) = {dy:.2f}")
        elif option == 2:  # Down
            dx, dy = 0, minY_n - anchor.y
            log(f"    📐 Cálculo: dy = minY_n ({minY_n:.2f}) - anchor.y ({anchor.y:.2f}) = {dy:.2f}")
        elif option == 3:  # Left
            dx, dy = minX_n - anchor_x, 0
            log(f"    📐 Cálculo: dx = minX_n ({minX_n:.2f}) - anchor.x ({anchor_x:.2f}) = {dx:.2f}")
        elif option == 4:  # Center X
            dx, dy = cx_n - anchor_x, 0
            log(f"    📐 Cálculo: dx = cx_n ({cx_n:.2f}) - anchor.x ({anchor_x:.2f}) = {dx:.2f}")
        elif option == 5:  # Right
            dx, dy = maxX_n - anchor_x, 0
            log(f"    📐 Cálculo: dx = maxX_n ({maxX_n:.2f}) - anchor.x ({anchor_x:.2f}) = {dx:.2f}")
        else:
            return None
        
        # Posición final del anchor después del movimiento
        final_x = anchor.x + dx
        final_y = anchor.y + dy
        log(f"    📍 ANCHOR (después de mover):")
        log(f"       - nueva posición: ({final_x:.2f}, {final_y:.2f})")
        
        return (dx, dy)

    # ========= CALCULATE ALIGNMENT OFFSET =========

    def calculateAlignmentOffset(self, layer, ref_component=None, move_paths_as_group=False, selection_ref=None):
        """
        Calcula el desplazamiento (dx, dy) necesario para alinear los items seleccionados.
        """
        log("=== calculateAlignmentOffset ===")
        
        nodes, fullPathsFromNodes, paths, comps, anchors = self.getLayerSelection(layer, selection_ref)
        
        log(f"  Nodos: {len(nodes)}")
        log(f"  Paths: {len(paths)}")
        log(f"  Componentes: {len(comps)}")
        log(f"  Anchors: {len(anchors)}")
        log(f"  Option: {self.w.options.get()} ({['Up', 'Center Y', 'Down', 'Left', 'Center X', 'Right'][self.w.options.get()]})")

        # ===== NUEVO MODO: NODOS + ANCHOR (el anchor se alinea a los nodos) =====
        if nodes and anchors and not fullPathsFromNodes:
            log("  🔥 Modo especial: NODOS + ANCHOR")
            log("     El anchor se alineará respecto a los nodos (los nodos NO se mueven)")
            
            option = self.w.options.get()
            anchor = anchors[0]
            
            offset = self.calculateAnchorOffsetFromNodes(layer, anchor, nodes, option)
            if offset:
                dx, dy = offset
                log(f"  Offset calculado: dx={dx:.1f}, dy={dy:.1f}")
                return (dx, dy, anchor.name if hasattr(anchor, 'name') else None, "anchor_only")
            return None

        # NODE MODE (solo nodos, sin anchors)
        if nodes and not fullPathsFromNodes and not anchors:
            log("  Modo: NODOS SOLO")
            b = self.getRealBounds(nodes, layer)
            if not b:
                log("  No bounds")
                return None
            
            minX, minY, maxX, maxY = b
            cx = (minX + maxX) / 2
            cy = (minY + maxY) / 2
            option = self.w.options.get()
            log(f"  Bounds: minX={minX:.1f}, minY={minY:.1f}, maxX={maxX:.1f}, maxY={maxY:.1f}, cx={cx:.1f}, cy={cy:.1f}")

            if nodes:
                n = nodes[0]
                nx = self.projectX(n.x, n.y, layer)
                if option == 0: dx, dy = 0, maxY - n.y
                elif option == 1: dx, dy = 0, cy - n.y
                elif option == 2: dx, dy = 0, minY - n.y
                elif option == 3: dx, dy = minX - nx, 0
                elif option == 4: dx, dy = cx - nx, 0
                elif option == 5: dx, dy = maxX - nx, 0
                log(f"  Offset: dx={dx:.1f}, dy={dy:.1f}")
                return (dx, dy, None, "nodes_only")
            return None

        # MODO: Componente como referencia vs Paths
        if ref_component is not None and (paths or anchors):
            log("  Modo: Componente vs Paths/Anchors")
            bRef = self.getComponentRealBounds(ref_component, layer)
            if not bRef:
                log("  No bounds del componente")
                return None
            
            minXr, minYr, maxXr, maxYr = bRef
            cxr = (minXr + maxXr) / 2
            cyr = (minYr + maxYr) / 2
            option = self.w.options.get()
            log(f"  Component bounds: minX={minXr:.1f}, minY={minYr:.1f}, maxX={maxXr:.1f}, maxY={maxYr:.1f}, cx={cxr:.1f}, cy={cyr:.1f}")
            
            if move_paths_as_group and paths:
                log("  Moviendo paths como grupo")
                b_paths = self.getRealBounds(paths, layer)
                if b_paths:
                    minXp, minYp, maxXp, maxYp = b_paths
                    cxp = (minXp + maxXp) / 2
                    cyp = (minYp + maxYp) / 2
                    log(f"  Paths group bounds: minX={minXp:.1f}, minY={minYp:.1f}, maxX={maxXp:.1f}, maxY={maxYp:.1f}, cx={cxp:.1f}, cy={cyp:.1f}")
                    
                    if option == 0: dx, dy = 0, maxYr - maxYp
                    elif option == 1: dx, dy = 0, cyr - cyp
                    elif option == 2: dx, dy = 0, minYr - minYp
                    elif option == 3: dx, dy = minXr - minXp, 0
                    elif option == 4: dx, dy = cxr - cxp, 0
                    elif option == 5: dx, dy = maxXr - maxXp, 0
                    log(f"  Offset calculado: dx={dx:.1f}, dy={dy:.1f}")
                    return (dx, dy, None, "group")
                return None
            else:
                move_items = paths + anchors
                if move_items:
                    b = self.getRealBounds([move_items[0]], layer)
                    if b:
                        minXi, minYi, maxXi, maxYi = b
                        cxi = (minXi + maxXi) / 2
                        cyi = (minYi + maxYi) / 2
                        
                        if option == 0: dx, dy = 0, maxYr - maxYi
                        elif option == 1: dx, dy = 0, cyr - cyi
                        elif option == 2: dx, dy = 0, minYr - minYi
                        elif option == 3: dx, dy = minXr - minXi, 0
                        elif option == 4: dx, dy = cxr - cxi, 0
                        elif option == 5: dx, dy = maxXr - maxXi, 0
                        log(f"  Offset (primer item): dx={dx:.1f}, dy={dy:.1f}")
                        return (dx, dy, None, "single")
                return None

        # MODO NORMAL
        all_items = paths + comps + anchors
        if len(all_items) < 2:
            log("  Modo NORMAL: menos de 2 items")
            return None
        
        log("  Modo NORMAL")
        total = self.getRealBounds(all_items, layer)
        if not total:
            log("  No bounds totales")
            return None
        
        minXr, minYr, maxXr, maxYr = total
        cxr = (minXr + maxXr) / 2
        cyr = (minYr + maxYr) / 2
        option = self.w.options.get()
        log(f"  Total bounds: minX={minXr:.1f}, minY={minYr:.1f}, maxX={maxXr:.1f}, maxY={maxYr:.1f}, cx={cxr:.1f}, cy={cyr:.1f}")
        
        if all_items:
            b = self.getRealBounds([all_items[0]], layer)
            if b:
                minXi, minYi, maxXi, maxYi = b
                cxi = (minXi + maxXi) / 2
                cyi = (minYi + maxYi) / 2
                
                if option == 0: dx, dy = 0, maxYr - maxYi
                elif option == 1: dx, dy = 0, cyr - cyi
                elif option == 2: dx, dy = 0, minYr - minYi
                elif option == 3: dx, dy = minXr - minXi, 0
                elif option == 4: dx, dy = cxr - cxi, 0
                elif option == 5: dx, dy = maxXr - maxXi, 0
                log(f"  Offset: dx={dx:.1f}, dy={dy:.1f}")
                return (dx, dy, None, "normal")
        
        return None

    # ========= ALIGN LAYER WITH OFFSET =========
    
    def alignLayerWithOffset(self, layer, offset, ref_component=None, move_paths_as_group=False, selection_ref=None):
        """
        Aplica un desplazamiento (dx, dy) a los elementos seleccionados de una capa
        """
        # Extraer componentes del offset (puede ser tupla de 4 elementos)
        if len(offset) == 4:
            dx, dy, anchor_name, mode_flag = offset
        elif len(offset) == 3:
            dx, dy, mode_flag = offset
            anchor_name = None
        else:
            dx, dy = offset
            anchor_name = None
            mode_flag = None
        
        if dx == 0 and dy == 0:
            log("  Offset es 0, nada que mover")
            return
        
        log(f"\n  --- alignLayerWithOffset para master: {layer.master.name if layer.master else 'Unknown'} ---")
        log(f"  Offset: dx={dx:.1f}, dy={dy:.1f}")
        if mode_flag:
            log(f"  Modo flag: {mode_flag}")
        
        # ===== MODO ESPECIAL: NODOS + ANCHOR (solo mover el anchor) =====
        if mode_flag == "anchor_only":
            # Buscar el anchor específico en esta capa
            if anchor_name:
                target_anchor = None
                for a in layer.anchors:
                    if a.name == anchor_name:
                        target_anchor = a
                        break
                if target_anchor:
                    log(f"  🔥 Modo especial: Moviendo SOLO el anchor '{anchor_name}'")
                    log(f"     Posición ANTES: ({target_anchor.x:.2f}, {target_anchor.y:.2f})")
                    self.moveItems([target_anchor], dx, dy)
                    log(f"     Posición DESPUÉS: ({target_anchor.x:.2f}, {target_anchor.y:.2f})")
                    log(f"  ✅ Anchor movido")
                else:
                    log(f"  ⚠️ Anchor '{anchor_name}' no encontrado en este master")
            else:
                # Fallback: mover todos los anchors seleccionados
                anchors = [a for a in layer.anchors if a.selected]
                if anchors:
                    log(f"  🔥 Modo especial: Moviendo SOLO los anchors seleccionados")
                    for a in anchors:
                        log(f"     Anchor '{a.name}' ANTES: ({a.x:.2f}, {a.y:.2f})")
                    self.moveItems(anchors, dx, dy)
                    for a in anchors:
                        log(f"     Anchor '{a.name}' DESPUÉS: ({a.x:.2f}, {a.y:.2f})")
                else:
                    log(f"  ⚠️ No hay anchors seleccionados para mover")
            return

        # ===== SMART SELECTION =====
        nodes, fullPathsFromNodes, paths, comps, anchors = self.getLayerSelection(layer, selection_ref)

        # ===== PRIORIDAD: NODOS SOLO =====
        if mode_flag == "nodes_only" or (nodes and not fullPathsFromNodes and not anchors):
            items = nodes
            log(f"  Modo: NODOS ({len(nodes)})")
        else:
            # Si hay un componente de referencia y estamos en modo grupo, 
            # excluir ese componente de los items a mover
            if ref_component is not None and move_paths_as_group:
                items = paths + anchors
                log(f"  Modo: PATHS+ANCHORS (excluyendo componente ref)")
            else:
                items = paths + comps + anchors
                log(f"  Modo: ITEMS ({len(items)})")

        if not items:
            log("  ⚠️ No hay elementos para mover en este master")
            return

        option = self.w.options.get()

        # Nodes-only mode should align each selected node, not move the whole
        # node selection by the offset calculated from the first node.
        if mode_flag == "nodes_only":
            ref_bounds = self.getRealBounds(nodes, layer)
            if not ref_bounds:
                log("  ⚠️ No hay bounds de referencia para nodos")
                return
            moved = set()
            selected_oncurves = set(id(n) for n in nodes if not self.isOffCurveNode(n))
            for node in nodes:
                item_bounds = self.getRealBounds([node], layer)
                if not item_bounds:
                    continue
                node_dx, node_dy = self.offsetForBounds(ref_bounds, item_bounds, option)
                self.moveNodeWithHandles(node, node_dx, node_dy, moved, selected_oncurves)
            log(f"  ✅ Nodos alineados individualmente")
            return

        # Component reference, individual mode: the component stays still and
        # every selected path/anchor is aligned separately to its bounds.
        if ref_component is not None and not move_paths_as_group:
            ref_bounds = self.getComponentRealBounds(ref_component, layer)
            if not ref_bounds:
                log("  ⚠️ No hay bounds del componente de referencia")
                return
            ref_items = paths + anchors
            for item in ref_items:
                item_bounds = self.getRealBounds([item], layer)
                if not item_bounds:
                    continue
                item_dx, item_dy = self.offsetForBounds(ref_bounds, item_bounds, option)
                self.moveItems([item], item_dx, item_dy)
            log(f"  ✅ Items alineados individualmente al componente")
            return

        # Normal multi-item mode: align each item to the total selection bounds.
        if mode_flag == "normal":
            ref_bounds = self.getRealBounds(items, layer)
            if not ref_bounds:
                log("  ⚠️ No hay bounds totales para alinear")
                return
            for item in items:
                item_bounds = self.getRealBounds([item], layer)
                if not item_bounds:
                    continue
                item_dx, item_dy = self.offsetForBounds(ref_bounds, item_bounds, option)
                self.moveItems([item], item_dx, item_dy)
            log(f"  ✅ Items alineados individualmente")
            return

        # ===== APPLY MOVE =====
        self.moveItems(items, dx, dy)
        log(f"  ✅ Movimiento aplicado")

    # ========= ALIGN =========

    def align(self, sender):
        log("\n=== ALIGN BUTTON PRESSED ===")
        font = Glyphs.font
    
        if not font.selectedLayers:
            log("No hay capas seleccionadas")
            return
    
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        paths_as_group = self.w.pathsAsGroup.get()
        option = self.w.options.get()
    
        log(f"Glifo: {glyph.name}")
        log(f"Paths as group: {paths_as_group}")
        log(f"Opción seleccionada: {option} ({['Up', 'Center Y', 'Down', 'Left', 'Center X', 'Right'][option]})")
    
        # ===== GET REFERENCE SELECTION (FROM CURRENT MASTER) =====
        selection_ref = self.getSelectionReference(current_layer)
        ref_nodes, ref_fullPaths, ref_paths, ref_comps, ref_anchors = self.getLayerSelection(
            current_layer,
            selection_ref
        )
    
        log(f"Selección: nodos={len(ref_nodes)}, paths={len(ref_paths)}, comps={len(ref_comps)}, anchors={len(ref_anchors)}")
    
        # =========================================================
        # ================= ALL MASTERS MODE ======================
        # =========================================================
    
        if self.w.scope.get() == 1:
            log("=== ALL MASTERS MODE ===")
        
            # -------- MODE: NODES + ANCHOR (CORREGIDO CON DEBUG) --------
            if ref_nodes and ref_anchors and not ref_fullPaths:
                log("🔥 Modo Especial: Nodos + Anchor (All Masters)")
                log("   Procesando master a master con sus propios nodos de referencia...")
                log("=" * 80)
                
                # Obtener el nombre del anchor seleccionado
                anchor_name = ref_anchors[0].name if hasattr(ref_anchors[0], 'name') else None
                log(f"📌 Anchor seleccionado: '{anchor_name}'")
                
                # Obtener información de los nodos en el master actual (referencia)
                log(f"\n📊 MASTER ACTUAL (REFERENCIA): {current_layer.master.name}")
                log(f"   Nodos seleccionados en master actual:")
                for i, node in enumerate(ref_nodes):
                    log(f"      Nodo {i+1}: ({node.x:.2f}, {node.y:.2f})")
                
                # Procesar cada master individualmente
                for master in font.masters:
                    log(f"\n{'─' * 60}")
                    log(f"📐 PROCESANDO MASTER: {master.name}")
                    log(f"{'─' * 60}")
                    
                    target_layer = glyph.layers[master.id]
                    if not target_layer:
                        log(f"  ⚠️ No se encontró layer para master {master.name}")
                        continue
                    
                    # Obtener los nodos seleccionados en ESTE master
                    target_nodes, target_fullPaths = self.getSelectionSmart(target_layer, selection_ref)
                    
                    log(f"  📊 Nodos seleccionados en este master: {len(target_nodes)}")
                    if target_nodes:
                        for i, node in enumerate(target_nodes):
                            log(f"      Nodo {i+1}: ({node.x:.2f}, {node.y:.2f})")
                    else:
                        log(f"      ❌ No hay nodos seleccionados!")
                        continue
                    
                    # Buscar el anchor con el mismo nombre en este master
                    target_anchor = None
                    for a in target_layer.anchors:
                        if a.name == anchor_name:
                            target_anchor = a
                            break
                    
                    if not target_anchor:
                        log(f"  ❌ Anchor '{anchor_name}' no encontrado en master {master.name}")
                        continue
                    
                    log(f"  📍 Anchor '{anchor_name}' encontrado:")
                    log(f"      Posición ANTES de mover: ({target_anchor.x:.2f}, {target_anchor.y:.2f})")
                    
                    # Calcular offset específico para este master usando sus propios nodos
                    log(f"\n  🎯 Calculando offset para este master...")
                    offset = self.calculateAnchorOffsetFromNodes(
                        target_layer, 
                        target_anchor, 
                        target_nodes, 
                        option
                    )
                    
                    if offset:
                        dx, dy = offset
                        log(f"\n  ✅ Offset calculado: dx={dx:.2f}, dy={dy:.2f}")
                        log(f"  🎯 Aplicando movimiento al anchor...")
                        
                        # Mover solo el anchor
                        self.moveItems([target_anchor], dx, dy)
                        
                        log(f"  📍 Anchor '{anchor_name}' después de mover:")
                        log(f"      Posición FINAL: ({target_anchor.x:.2f}, {target_anchor.y:.2f})")
                        log(f"  ✅ Master '{master.name}' procesado correctamente")
                    else:
                        log(f"  ❌ No se pudo calcular offset para master {master.name}")
                
                log(f"\n{'=' * 80}")
                log("✅ Todos los masters procesados")
                Glyphs.redraw()
                return
        
            # -------- MODE 1: COMPONENT AS REFERENCE --------
            if ref_comps and (ref_paths or ref_anchors):
                log("🔥 Modo: Componente como referencia")
                ref_comp = ref_comps[0]
            
                for master in font.masters:
                    target_layer = glyph.layers[master.id]
                    if not target_layer:
                        continue
                
                    # Buscar el mismo componente en este master
                    target_comp = None
                    for comp in target_layer.components:
                        if comp.componentName == ref_comp.componentName:
                            target_comp = comp
                            break
                
                    if not target_comp:
                        log(f"No se encontró componente en master {master.name}")
                        continue
                
                    # Calcular offset por master
                    offset = self.calculateAlignmentOffset(
                        target_layer,
                        ref_component=target_comp,
                        move_paths_as_group=paths_as_group,
                        selection_ref=selection_ref
                    )
                
                    if offset:
                        log(f"Alineando master: {master.name} → dx={offset[0]:.1f}, dy={offset[1]:.1f}")
                        self.alignLayerWithOffset(
                            target_layer,
                            offset,
                            ref_component=target_comp,
                            move_paths_as_group=paths_as_group,
                            selection_ref=selection_ref
                        )
            
                Glyphs.redraw()
                return
        
            # -------- MODE 2: NODES ONLY --------
            if ref_nodes and not ref_fullPaths and not ref_anchors:
                log("🔥 Modo: Nodos solamente")
            
                for master in font.masters:
                    target_layer = glyph.layers[master.id]
                    if not target_layer:
                        continue
                
                    offset = self.calculateAlignmentOffset(
                        target_layer,
                        move_paths_as_group=paths_as_group,
                        selection_ref=selection_ref
                    )
                
                    if offset:
                        log(f"Alineando master: {master.name} → dx={offset[0]:.1f}, dy={offset[1]:.1f}")
                        self.alignLayerWithOffset(
                            target_layer,
                            offset,
                            move_paths_as_group=paths_as_group,
                            selection_ref=selection_ref
                        )
            
                Glyphs.redraw()
                return
        
            # -------- MODE 3: NORMAL ITEMS --------
            ref_items = ref_paths + ref_comps + ref_anchors
            if len(ref_items) < 2:
                log("No hay suficientes items seleccionados")
                return
        
            log("🔥 Modo: Items normales")
        
            for master in font.masters:
                target_layer = glyph.layers[master.id]
                if not target_layer:
                    continue
            
                offset = self.calculateAlignmentOffset(
                    target_layer,
                    move_paths_as_group=paths_as_group,
                    selection_ref=selection_ref
                )
            
                if offset:
                    log(f"Alineando master: {master.name} → dx={offset[0]:.1f}, dy={offset[1]:.1f}")
                    self.alignLayerWithOffset(
                        target_layer,
                        offset,
                        move_paths_as_group=paths_as_group,
                        selection_ref=selection_ref
                    )
    
        # =========================================================
        # ================= CURRENT MASTER MODE ====================
        # =========================================================
    
        else:
            log("=== CURRENT MASTER MODE ===")

            if ref_comps and (ref_paths or ref_anchors):
                log("🔥 Modo: Componente como referencia (Current)")
                ref_comp = ref_comps[0]

                for layer in [current_layer]:
                    target_comp = None
                    for comp in layer.components:
                        if comp.componentName == ref_comp.componentName and comp.selected:
                            target_comp = comp
                            break
                    if target_comp is None:
                        for comp in layer.components:
                            if comp.componentName == ref_comp.componentName:
                                target_comp = comp
                                break
                    if target_comp is None:
                        log(f"No se encontró componente de referencia en {layer.parent.name}")
                        continue

                    offset = self.calculateAlignmentOffset(
                        layer,
                        ref_component=target_comp,
                        move_paths_as_group=paths_as_group
                    )

                    if offset:
                        self.alignLayerWithOffset(
                            layer,
                            offset,
                            ref_component=target_comp,
                            move_paths_as_group=paths_as_group
                        )

                Glyphs.redraw()
                log("=== ALIGN COMPLETED ===\n")
                return
        
            for layer in [current_layer]:
                offset = self.calculateAlignmentOffset(
                    layer,
                    move_paths_as_group=paths_as_group
                )
            
                if offset:
                    self.alignLayerWithOffset(
                        layer,
                        offset,
                        move_paths_as_group=paths_as_group
                    )
    
        Glyphs.redraw()
        log("=== ALIGN COMPLETED ===\n")
        
    def applyYPosition(self, sender):
        log("=== applyYPosition ===")
        font = Glyphs.font

        try:
            y = float(self.w.yInput.get())
        except:
            log("Invalid Y input")
            return

        if not font.selectedLayers:
            log("No hay capas seleccionadas")
            return
        
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        selection_ref = self.getSelectionReference(current_layer)
        has_edit_selection = self.selectionReferenceHasItems(selection_ref)
        
        if self.w.scope.get() == 1:
            log("Modo ALL MASTERS")
            for master in font.masters:
                target_layer = glyph.layers[master.id]
                if target_layer:
                    self.applyYToLayer(
                        target_layer,
                        y,
                        selection_ref=selection_ref if has_edit_selection else None
                    )
        else:
            log("Modo CURRENT MASTER")
            for layer in [current_layer]:
                self.applyYToLayer(layer, y)

        Glyphs.redraw()

    def applyYPreset(self, sender):
        log("\n=== applyYPreset ===")
        font = Glyphs.font
    
        if not font.selectedLayers:
            log("No hay capas seleccionadas")
            return
    
        active_master = font.selectedFontMaster
        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        selection_ref = self.getSelectionReference(current_layer)
        has_edit_selection = self.selectionReferenceHasItems(selection_ref)
        grid_glyphs = [] if has_edit_selection else [glyph]
    
        # DEBUG: Mostrar información de todos los masters
        log("=" * 60)
        log("DEBUG: MASTERS INFORMATION")
        log("=" * 60)
        for master in font.masters:
            log(f"Master: {master.name}")
            log(f"  - ID: {master.id}")
            log(f"  - xHeight: {master.xHeight}")
            log(f"  - capHeight: {master.capHeight}")
            log(f"  - ascender: {master.ascender}")
            log(f"  - descender: {master.descender}")
            log(f"  - baseline: 0")
        log("=" * 60)
    
        preset_index = self.w.yPreset.get()
        if preset_index == 0:
            return
    
        active_preset = self.getYPresetSettings(preset_index, active_master)
        if active_preset:
            active_target, active_apply_overshoot, active_direction, _active_force_mode = active_preset
            if active_apply_overshoot:
                overshoot_value = self.getMasterOvershootValue(active_master, active_target, active_direction)
                if overshoot_value is not None:
                    self.w.overshootValue.set(self.formatNumber(overshoot_value))
    
        # =========================================================
        # APLICAR A CADA MASTER CON SUS PROPIAS MÉTRICAS
        # =========================================================
    
        if self.w.scope.get() == 1:
            # Modo ALL MASTERS: cada master usa su propia métrica
            log("\n🚀 Modo ALL MASTERS - cada master usa su propia métrica")
            log("=" * 60)

            target_glyphs = grid_glyphs if grid_glyphs else [glyph]

            for target_glyph in target_glyphs:
                log(f"\n🔤 Procesando glifo: {target_glyph.name}")
                target_selection_ref = selection_ref if has_edit_selection and target_glyph == glyph else None

                for master in font.masters:
                    target_layer = target_glyph.layers[master.id]
                    if not target_layer:
                        log(f"⚠️ No se encontró layer para master {master.name}")
                        continue
            
                    # Obtener el valor de la métrica para ESTE master
                    preset = self.getYPresetSettings(preset_index, master)
                    if not preset:
                        continue

                    target_value, apply_overshoot, direction, force_mode = preset
                    master_overshoot = None
                    if apply_overshoot:
                        master_overshoot = self.getMasterOvershootValue(master, target_value, direction)
            
                    log(f"\n📐 Procesando master: {master.name}")
                    log(f"   - Usando target_value: {target_value}")
                    log(f"   - apply_overshoot: {apply_overshoot}")
                    log(f"   - overshoot master: {master_overshoot if master_overshoot is not None else self.getOvershootValue()}")
                    log(f"   - force_mode: {force_mode}")
            
                    self.applyYToLayer(
                        target_layer,
                        targetY=target_value,
                        applyOvershoot=apply_overshoot,
                        overshootDirection=direction,
                        overshootValue=master_overshoot,
                        forceAlignMode=force_mode,
                        use_all_items=bool(grid_glyphs),
                        selection_ref=target_selection_ref
                    )
    
        else:
            # Modo CURRENT MASTER: usar el master activo
            log("\n🎯 Modo CURRENT MASTER")

            preset = self.getYPresetSettings(preset_index, active_master)
            if not preset:
                return

            target_value, apply_overshoot, direction, force_mode = preset
            master_overshoot = None
            if apply_overshoot:
                master_overshoot = self.getMasterOvershootValue(active_master, target_value, direction)
                if master_overshoot is not None:
                    self.w.overshootValue.set(self.formatNumber(master_overshoot))
        
            self.w.yInput.set(str(target_value))

            if grid_glyphs:
                for target_glyph in grid_glyphs:
                    target_layer = target_glyph.layers[active_master.id]
                    if target_layer:
                        self.applyYToLayer(
                            target_layer,
                            targetY=target_value,
                            applyOvershoot=apply_overshoot,
                            overshootDirection=direction,
                            overshootValue=master_overshoot,
                            forceAlignMode=force_mode,
                            use_all_items=True
                        )
            else:
                self.applyYToLayer(
                    current_layer,
                    targetY=target_value,
                    applyOvershoot=apply_overshoot,
                    overshootDirection=direction,
                    overshootValue=master_overshoot,
                    forceAlignMode=force_mode,
                    selection_ref=selection_ref if has_edit_selection else None
                )
    
        Glyphs.redraw()
        log("=== applyYPreset completado ===\n")

    def getYPresetSettings(self, preset_index, master):
        if preset_index == 1:  # Baseline
            return (0, False, None, "down")
        elif preset_index == 2:  # Baseline Overshoots
            return (0, True, "south", "down")
        elif preset_index == 3:  # x-height
            return (master.xHeight, False, None, "up")
        elif preset_index == 4:  # X Height center
            return (master.xHeight / 2, False, None, "center")
        elif preset_index == 5:  # x-height Overshoots
            return (master.xHeight, True, "north", "up")
        elif preset_index == 6:  # Cap height
            return (master.capHeight, False, None, "up")
        elif preset_index == 7:  # Cap height Overshoots
            return (master.capHeight, True, "north", "up")
        elif preset_index == 8:  # Ascenders
            return (master.ascender, False, None, "up")
        elif preset_index == 9:  # Ascenders Overshoots
            return (master.ascender, True, "north", "up")
        elif preset_index == 10:  # Descenders
            return (master.descender, False, None, "down")
        elif preset_index == 11:  # Descenders Overshoots
            return (master.descender, True, "south", "down")
        return None
        
    def applyYToLayer(self, layer, targetY=None, applyOvershoot=False, 
                      overshootDirection="north", overshootValue=None, forceAlignMode=None,
                      use_dy_reference=False, dy_reference=0,
                      use_all_items=False, selection_ref=None):
        """
        Aplica posición Y a los elementos seleccionados
        """
        log(f"\n  --- applyYToLayer para master: {layer.master.name if layer.master else 'Unknown'} ---")
        
        # ===== SMART SELECTION =====
        nodes, fullPathsFromNodes, paths, comps, anchors = self.getLayerSelection(
            layer,
            selection_ref=selection_ref,
            use_all_items=use_all_items
        )

        # ===== PRIORIDAD: NODOS =====
        if nodes and not fullPathsFromNodes:
            items = nodes
            log(f"  Modo: NODOS ({len(nodes)})")
        else:
            items = paths + comps + anchors
            log(f"  Modo: ITEMS ({len(items)})")

        if not items:
            log("  ⚠️ No hay selección en este master")
            return

        # ===== MODO: USAR DY REFERENCIA (PARA ALL MASTERS) =====
        if use_dy_reference:
            log(f"  🔄 Usando dy_reference precalculado: {dy_reference:.1f}")
            if nodes and not fullPathsFromNodes:
                moved = set()
                selected_oncurves = set(id(n) for n in nodes if not self.isOffCurveNode(n))
                for node in nodes:
                    self.moveNodeWithHandles(node, 0, dy_reference, moved, selected_oncurves)
            else:
                self.moveItems(items, 0, dy_reference)
            log(f"  ✅ Movimiento aplicado")
            return

        # ===== MODO NORMAL: CALCULAR DY =====
        if targetY is None:
            log("  Error: targetY no especificado")
            return

        # ===== BOUNDS CORRECTOS =====
        b = self.getRealBounds(items, layer)
        if not b:
            log("  No bounds")
            return

        minX, minY, maxX, maxY = b
        log(f"  Bounds: minY={minY:.1f}, maxY={maxY:.1f}")

        # ===== ALIGN MODE =====
        if forceAlignMode == "up":
            mode = 0
        elif forceAlignMode == "center":
            mode = 1
        elif forceAlignMode == "down":
            mode = 2
        else:
            if self.w.yModeUp.get():
                mode = 0
            elif self.w.yModeCen.get():
                mode = 1
            else:
                mode = 2

        overshoot = (overshootValue if overshootValue is not None else self.getOvershootValue()) if applyOvershoot else 0
        log(f"  Mode: {mode} ({['up','center','down'][mode]})")
        log(f"  applyOvershoot: {applyOvershoot}, overshoot: {overshoot}, direction: {overshootDirection}")

        # ===== CALC DY =====
        if mode == 0:  # UP
            if applyOvershoot and overshootDirection == "north":
                targetY_adjusted = targetY + overshoot
            elif applyOvershoot and overshootDirection == "south":
                targetY_adjusted = targetY - overshoot
            else:
                targetY_adjusted = targetY

            dy = targetY_adjusted - maxY
            log(f"  UP mode: maxY={maxY:.1f}, target={targetY:.1f}, adjusted={targetY_adjusted:.1f}, dy={dy:.1f}")

        elif mode == 1:  # CENTER
            targetY_adjusted = targetY
            center_y = (minY + maxY) / 2
            dy = targetY - center_y
            log(f"  CENTER mode: centerY={center_y:.1f}, target={targetY:.1f}, dy={dy:.1f}")

        else:  # DOWN (mode == 2)
            if applyOvershoot and overshootDirection == "south":
                targetY_adjusted = targetY - overshoot
            elif applyOvershoot and overshootDirection == "north":
                targetY_adjusted = targetY + overshoot
            else:
                targetY_adjusted = targetY

            dy = targetY_adjusted - minY
            log(f"  DOWN mode: minY={minY:.1f}, target={targetY:.1f}, adjusted={targetY_adjusted:.1f}, dy={dy:.1f}")

        # ===== APPLY MOVE =====
        if nodes and not fullPathsFromNodes:
            moved = set()
            selected_oncurves = set(id(n) for n in nodes if not self.isOffCurveNode(n))
            for node in nodes:
                self.moveNodeWithHandles(node, 0, dy, moved, selected_oncurves)
        else:
            self.moveItems(items, 0, dy)
        log(f"  ✅ Movimiento aplicado: dy={dy:.1f}")
        
    def getSelectedItems(self, layer):
        """
        Devuelve selección unificada
        """
        nodes, fullPathsFromNodes = self.getSelectionSmart(layer)

        paths_selected = [p for p in layer.paths if p.selected]
        paths = []
        for p in paths_selected + fullPathsFromNodes:
            if p not in paths:
                paths.append(p)

        comps = [c for c in layer.components if c.selected]
        anchors = [a for a in layer.anchors if a.selected]

        if nodes and not fullPathsFromNodes:
            return nodes, "nodes"

        return paths + comps + anchors, "items"
                      

AlignTool()
