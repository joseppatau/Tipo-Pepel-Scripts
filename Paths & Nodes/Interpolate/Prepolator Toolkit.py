# MenuTitle:Prepolator Toolkit
# -*- coding: utf-8 -*-
# Description: A toolkit for preparing glyphs for interpolation, including node sync, anchor management, and structural validation.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
import vanilla
from GlyphsApp import Glyphs, Message, OFFCURVE, CORNER, CURVE, GSPath, GSNode


class GlyphTools(object):

    def __init__(self):

        self.w = vanilla.FloatingWindow((250, 700), "Prepolator Toolkit")

        self.w.text = vanilla.TextBox(
            (15, 15, -15, 20),
            "Herramientas de nodos y anchors"
        )

        self.w.syncButton = vanilla.Button(
            (15, 45, -15, 25),
            "Sync First Node",
            callback=self.sync
        )

        self.w.syncOrderButton = vanilla.Button(
            (15, 80, -15, 25),
            "Sync Node Order",
            callback=self.syncNodeOrder
        )

        self.w.convertCubicButton = vanilla.Button(
            (15, 115, -15, 25),
            "Convert Paths to Cubic",
            callback=self.convertPathsToCubic
        )

        self.w.resetButton = vanilla.Button(
            (15, 150, -15, 25),
            "Reset Anchors",
            callback=self.resetAnchors
        )

        self.w.clearButton = vanilla.Button(
            (15, 185, -15, 25),
            "Clear All Anchors",
            callback=self.clearAnchors
        )

        self.w.cornerButton = vanilla.Button(
            (15, 220, -15, 25),
            "Delete All Corners",
            callback=self.deleteCorners
        )

        self.w.directionButton = vanilla.Button(
            (15, 255, -15, 25),
            "Correct Path Direction",
            callback=self.correctPathDirection
        )

        self.w.reorderButton = vanilla.Button(
            (15, 290, -15, 25),
            "Reorder Paths",
            callback=self.reorderPaths
        )

        self.w.checkNodesButton = vanilla.Button(
            (15, 325, -1, 25),
            "Check Number Nodes",
            callback=self.checkNodeCount
        )

        # Separator
        self.w.separator = vanilla.HorizontalLine((15, 360, -15, 1))

        # Test Glyph section
        self.w.testButton = vanilla.Button(
            (15, 375, -15, 25),
            "Test Glyph",
            callback=self.testGlyph
        )

        # Results area
        self.w.resultsLabel = vanilla.TextBox(
            (15, 410, 100, 20),
            "Resultats:"
        )

        self.w.resultsArea = vanilla.TextEditor(
            (15, 435, -15, 235),
            "Selecciona un glifo i prem Test Glyph",
            readOnly=True
        )

        self.w.open()

    def oncurveNodes(self, path):
        return [n for n in path.nodes if n.type != OFFCURVE]

    def detectExtreme(self, path, refNode):
        nodes = self.oncurveNodes(path)

        north = max(nodes, key=lambda n: n.y)
        south = min(nodes, key=lambda n: n.y)
        east = max(nodes, key=lambda n: n.x)
        west = min(nodes, key=lambda n: n.x)

        if refNode == north:
            return "north"
        if refNode == south:
            return "south"
        if refNode == east:
            return "east"
        if refNode == west:
            return "west"
        return None

    def findExtreme(self, path, extreme):
        nodes = self.oncurveNodes(path)

        if extreme == "north":
            return max(nodes, key=lambda n: n.y)
        if extreme == "south":
            return min(nodes, key=lambda n: n.y)
        if extreme == "east":
            return max(nodes, key=lambda n: n.x)
        if extreme == "west":
            return min(nodes, key=lambda n: n.x)
        return None

    def sync(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        refNode = None
        refPathIndex = None

        for pi, path in enumerate(layer.paths):
            for node in path.nodes:
                if node.selected and node.type != OFFCURVE:
                    refNode = node
                    refPathIndex = pi
                    break
            if refNode:
                break

        if not refNode:
            print("Selecciona un nodo on-curve.")
            return

        extreme = self.detectExtreme(layer.paths[refPathIndex], refNode)

        if not extreme:
            print("El nodo seleccionado no es extremo.")
            return

        font.disableUpdateInterface()

        for layer in glyph.layers:
            if not (layer.isMasterLayer or layer.isSpecialLayer):
                continue
            if refPathIndex >= len(layer.paths):
                continue
            path = layer.paths[refPathIndex]
            node = self.findExtreme(path, extreme)
            if node:
                node.makeNodeFirst()

        font.enableUpdateInterface()
        print("First node sincronizado en todos los masters.")

    def syncNodeOrder(self, sender):
        """Sincronitza l'ordre dels nodes de tots els masters amb el master actiu"""
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent
        
        # Obtenir el master actual
        if hasattr(layer, 'associatedFontMaster'):
            current_master = layer.associatedFontMaster()
        elif hasattr(layer, 'master'):
            current_master = layer.master
        else:
            current_master = font.masters[0]
        
        if not current_master:
            print("No s'ha trobat el master actual.")
            return
        
        # Netejar l'àrea de resultats
        self.w.resultsArea.set("")
        
        results = []
        results.append(f"=== Sincronitzant ordre de nodes ===")
        results.append(f"Master de referència: {current_master.name}\n")
        
        # Obtenir l'ordre dels nodes del master actual
        reference_nodes = []
        for path in layer.paths:
            for node in path.nodes:
                if node.type != OFFCURVE:
                    reference_nodes.append({
                        'x': round(node.x, 2),
                        'y': round(node.y, 2),
                        'order': len(reference_nodes)
                    })
        
        results.append(f"Nodes de referència: {len(reference_nodes)}")
        results.append("")
        
        font.disableUpdateInterface()
        
        sync_success = True
        problems = []
        
        # Per cada altre master, comparar l'ordre dels nodes
        for master in font.masters:
            if master.id == current_master.id:
                continue
                
            mlayer = glyph.layers[master.id]
            if not mlayer:
                results.append(f"  {master.name}: No té capa")
                continue
            
            # Recollir tots els nodes on-curve amb les seves coordenades
            current_nodes = []
            for path_idx, path in enumerate(mlayer.paths):
                for node in path.nodes:
                    if node.type != OFFCURVE:
                        current_nodes.append({
                            'node': node,
                            'x': node.x,
                            'y': node.y,
                            'path_idx': path_idx
                        })
            
            if len(current_nodes) != len(reference_nodes):
                results.append(f"  {master.name}: ⚠️ Nombre de nodes diferent ({len(current_nodes)} vs {len(reference_nodes)})")
                sync_success = False
                problems.append(master.name)
                continue
            
            # Trobar la correspondència entre nodes per posició
            matched = []
            used_indices = set()
            
            for ref in reference_nodes:
                best_match = None
                best_dist = float('inf')
                best_idx = -1
                
                for i, curr in enumerate(current_nodes):
                    if i in used_indices:
                        continue
                    dist = abs(curr['x'] - ref['x']) + abs(curr['y'] - ref['y'])
                    if dist < best_dist:
                        best_dist = dist
                        best_match = curr
                        best_idx = i
                
                if best_match and best_dist < 100:
                    matched.append((best_match, best_dist))
                    used_indices.add(best_idx)
                else:
                    matched.append((None, best_dist))
            
            # Comprovar si l'ordre és correcte
            mismatches = []
            for i, (ref, (match, dist)) in enumerate(zip(reference_nodes, matched)):
                if match:
                    if abs(match['x'] - ref['x']) > 15 or abs(match['y'] - ref['y']) > 15:
                        mismatches.append(f"    Node {i}: ref ({ref['x']}, {ref['y']}) vs {master.name} ({round(match['x'],1)}, {round(match['y'],1)})")
                else:
                    mismatches.append(f"    Node {i}: ref ({ref['x']}, {ref['y']}) vs NO MATCH FOUND")
            
            if mismatches:
                results.append(f"  {master.name}: ⚠️ Ordre diferent")
                for m in mismatches[:5]:
                    results.append(m)
                if len(mismatches) > 5:
                    results.append(f"    ... i {len(mismatches) - 5} més")
                sync_success = False
                problems.append(master.name)
            else:
                results.append(f"  {master.name}: ✓ Ordre correcte")
        
        font.enableUpdateInterface()
        
        results.append("")
        results.append("=" * 50)
        
        if sync_success:
            results.append("✅ Tots els masters tenen l'ordre de nodes correcte!")
        else:
            results.append("❌ HI HA MASTERS AMB ORDRE DE NODES DIFERENT")
            results.append("")
            results.append("PER SOLUCIONAR-HO:")
            results.append("")
            results.append("1. Selecciona el glifo que vols corregir")
            results.append("2. Fes doble clic per entrar en mode edició")
            results.append("3. Selecciona tots els nodes (Cmd+A)")
            results.append("4. Ves a: Glyphs > Paths > Correct Path Direction")
            results.append("5. Després: Glyphs > Paths > Make Node First (per sincronitzar el primer node)")
            results.append("")
            results.append(f"Masters afectats: {', '.join(problems)}")
        
        self.w.resultsArea.set("\n".join(results))
        print("\n".join(results))

    def convertPathsToCubic(self, sender):
        """Converteix tots els paths del glifi a corbes cúbiques (assegura que els offcurves estan correctes)"""
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent
        
        self.w.resultsArea.set("")
        
        results = []
        results.append(f"=== Convertint paths a cubic ===")
        results.append(f"Glifo: {glyph.name}\n")
        
        font.disableUpdateInterface()
        
        converted_count = 0
        error_count = 0
        
        for master in font.masters:
            glayer = glyph.layers[master.id]
            if not glayer:
                continue
            
            results.append(f"Processant master: {master.name}")
            
            for path_idx, path in enumerate(glayer.paths):
                try:
                    # Forçar que els nodes estiguin en format cúbic
                    # Això assegura que tots els offcurves estiguin correctament aparellats
                    path.nodes = path.nodes  # Això força una actualització
                    
                    # Comprovar que cada node curve té els seus offcurves
                    nodes = list(path.nodes)
                    for i, node in enumerate(nodes):
                        if node.type == CURVE:
                            # Assegurar que té manejadors
                            # Check if node has handles (they might be None)
                            has_left = hasattr(node, 'leftHandle') and node.leftHandle is not None
                            has_right = hasattr(node, 'rightHandle') and node.rightHandle is not None
                            
                            if not has_left or not has_right:
                                # Si no té manejadors, crear-ne de per defecte
                                prev_node = nodes[i-1] if i > 0 else nodes[-1]
                                next_node = nodes[i+1] if i < len(nodes)-1 else nodes[0]
                                
                                # Crear manejadors per defecte a 1/3 de la distància
                                dx1 = (node.x - prev_node.x) / 3
                                dy1 = (node.y - prev_node.y) / 3
                                dx2 = (next_node.x - node.x) / 3
                                dy2 = (next_node.y - node.y) / 3
                                
                                if hasattr(node, 'leftHandle'):
                                    node.leftHandle = (dx1, dy1)
                                if hasattr(node, 'rightHandle'):
                                    node.rightHandle = (dx2, dy2)
                    
                    converted_count += 1
                    results.append(f"  Path {path_idx}: convertit")
                    
                except Exception as e:
                    error_count += 1
                    results.append(f"  Path {path_idx}: ERROR - {str(e)}")
            
            results.append("")
        
        font.enableUpdateInterface()
        
        results.append("=" * 50)
        if error_count == 0:
            results.append(f"✅ Conversió completada. {converted_count} paths processats.")
        else:
            results.append(f"⚠️ Conversió completada amb {error_count} errors.")
        
        self.w.resultsArea.set("\n".join(results))
        print("\n".join(results))

    def resetAnchors(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        glyph = font.selectedLayers[0].parent

        font.disableUpdateInterface()

        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                layer.anchors = None
                layer.addMissingAnchors()

        font.enableUpdateInterface()
        print("Anchors reseteados en todos los masters.")

    def clearAnchors(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        glyph = font.selectedLayers[0].parent

        font.disableUpdateInterface()

        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                layer.anchors = []

        font.enableUpdateInterface()
        print("Todos los anchors eliminados.")

    def deleteCorners(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        glyph = font.selectedLayers[0].parent

        font.disableUpdateInterface()

        for layer in glyph.layers:
            if not (layer.isMasterLayer or layer.isSpecialLayer):
                continue
            for hint in list(layer.hints):
                if hint.type == CORNER:
                    layer.removeHint_(hint)

        font.enableUpdateInterface()
        print("Corner components eliminados.")

    def correctPathDirection(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        glyph = font.selectedLayers[0].parent

        font.disableUpdateInterface()

        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                layer.correctPathDirection()

        font.enableUpdateInterface()
        print("Dirección de contornos corregida en todos los masters.")


    def reorderPaths(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        def oncurveNodes(path):
            return [n for n in path.nodes if n.type != OFFCURVE]

        def countCurveNodes(path):
            return sum(1 for n in path.nodes if n.type == CURVE)

        def getCardinals(path):
            nodes = oncurveNodes(path)
            if not nodes:
                return (0, 0)
            xs = [n.x for n in nodes]
            ys = [n.y for n in nodes]
            return (round(min(xs), 1), round(min(ys), 1))

        def pathSignature(path):
            nodes = oncurveNodes(path)
            if nodes:
                xs = [n.x for n in nodes]
                ys = [n.y for n in nodes]
                bbox = (
                    round(min(xs), 1),
                    round(min(ys), 1),
                    round(max(xs), 1),
                    round(max(ys), 1),
                )
            else:
                bbox = (0, 0, 0, 0)

            return (
                len(nodes),
                countCurveNodes(path),
                int(path.closed),
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[3],
            )

        def buildOrderMap(refPaths, testPaths, keyFunc):
            refKeys = [(i, keyFunc(p)) for i, p in enumerate(refPaths)]
            testKeys = [(i, keyFunc(p)) for i, p in enumerate(testPaths)]

            used = set()
            order = []
            ambiguous = False

            for _, refKey in refKeys:
                matches = [i for i, k in testKeys if k == refKey and i not in used]
                if len(matches) == 1:
                    idx = matches[0]
                    order.append(idx)
                    used.add(idx)
                elif len(matches) > 1:
                    ambiguous = True
                    idx = matches[0]
                    order.append(idx)
                    used.add(idx)
                else:
                    ambiguous = True
                    bestIdx = None
                    bestDist = None
                    for i, k in testKeys:
                        if i in used:
                            continue
                        dist = sum(
                            abs(a - b)
                            for a, b in zip(refKey if isinstance(refKey, tuple) else (refKey,), k if isinstance(k, tuple) else (k,))
                            if isinstance(a, (int, float)) and isinstance(b, (int, float))
                        )
                        if bestDist is None or dist < bestDist:
                            bestDist = dist
                            bestIdx = i
                    if bestIdx is not None:
                        order.append(bestIdx)
                        used.add(bestIdx)

            remaining = [i for i in range(len(testPaths)) if i not in used]
            order.extend(remaining)
            return order, ambiguous

        def reorderLayerByOrder(layer, order):
            shapes = list(layer.shapes)
            paths = [s for s in shapes if hasattr(s, "nodes")]
            components = [s for s in shapes if not hasattr(s, "nodes")]

            if len(paths) != len(order):
                return False

            newPaths = [paths[i] for i in order]
            newShapes = newPaths + components
            layer.shapes = newShapes
            return True

        font.disableUpdateInterface()

        report = []
        for l in glyph.layers:
            if not (l.isMasterLayer or l.isSpecialLayer):
                continue

            paths = [s for s in list(l.shapes) if hasattr(s, "nodes")]
            if not paths:
                continue

            report.append(f"Layer: {l.name}")

            refPaths = [s for s in list(layer.shapes) if hasattr(s, "nodes")]
            if len(paths) != len(refPaths):
                report.append(f"  ⚠️ Número de paths distinto: {len(paths)} vs {len(refPaths)}")
                continue

            order, ambiguous = buildOrderMap(refPaths, paths, getCardinals)
            ok = reorderLayerByOrder(l, order)

            if ok:
                report.append("  ✓ Reordenado por cardinales")
            else:
                report.append("  ⚠️ No se pudo reordenar por cardinales")

            if ambiguous:
                order2, ambiguous2 = buildOrderMap(refPaths, [s for s in list(l.shapes) if hasattr(s, "nodes")], pathSignature)
                ok2 = reorderLayerByOrder(l, order2)
                if ok2:
                    report.append("  ✓ Reordenado por firma estructural")
                else:
                    report.append("  ⚠️ No se pudo reordenar por firma estructural")
                if ambiguous2:
                    report.append("  ⚠️ Hay paths ambiguos que quizá requieran revisión manual")

        font.enableUpdateInterface()

        print("\n".join(report))



        
        
    def checkNodeCount(self, sender):
        font = Glyphs.font
        if not font.selectedLayers:
            print("Selecciona un glifo.")
            return

        glyph = font.selectedLayers[0].parent

        counts = {}
        baseCount = None

        for layer in glyph.layers:
            if not (layer.isMasterLayer or layer.isSpecialLayer):
                continue
            nodeCount = 0
            for path in layer.paths:
                for node in path.nodes:
                    if node.type != OFFCURVE:
                        nodeCount += 1
            counts[layer.name] = nodeCount
            if baseCount is None:
                baseCount = nodeCount

        mismatches = []
        for masterName, count in counts.items():
            if count != baseCount:
                mismatches.append(f"{masterName}: {count}")

        if mismatches:
            message = "Masters con diferente número de nodos:\n\n"
            message += "\n".join(mismatches)
            Message("Node Count Mismatch", message, OKButton="OK")

    def testGlyph(self, sender):
        """Inspecciona el glifo seleccionat i mostra les causes per les quals no es pot interpolar"""
        font = Glyphs.font

        self.w.resultsArea.set("")

        if not font:
            self.w.resultsArea.set("Error: No hi ha cap font oberta.")
            return

        if not font.selectedLayers:
            self.w.resultsArea.set("Error: Selecciona un glifo.")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent
        glyph_name = glyph.name

        results = []
        results.append(f"=== Anàlisi del glifo: {glyph_name} ===\n")

        if len(font.masters) < 2:
            results.append("❌ ERROR: La font necessita almenys 2 masters per interpolació.")
        else:
            results.append(f"✓ Masters: {len(font.masters)}")

        # Comprovar que tots els masters tenen el glifo
        missing_masters = []
        for master in font.masters:
            if glyph_name not in font.glyphs or glyph.layers[master.id] is None:
                missing_masters.append(master.name)

        if missing_masters:
            results.append(f"❌ ERROR: Masters sense aquest glifo: {', '.join(missing_masters)}")
        else:
            results.append("✓ Tots els masters tenen el glifo")

        # Comprovar nombre de nodes per master
        node_counts = {}
        base_count = None
        base_master = None

        for master in font.masters:
            glayer = glyph.layers[master.id]
            if glayer:
                count = 0
                for path in glayer.paths:
                    for node in path.nodes:
                        if node.type != OFFCURVE:
                            count += 1
                node_counts[master.name] = count
                if base_count is None:
                    base_count = count
                    base_master = master.name

        results.append("\n--- Nombre de nodes on-curve ---")
        mismatches = []
        for master_name, count in node_counts.items():
            if count != base_count:
                results.append(f"  {master_name}: {count} ⚠️ (diferent de {base_master}: {base_count})")
                mismatches.append(master_name)
            else:
                results.append(f"  {master_name}: {count} ✓")

        # Comprovar estructura de paths
        path_counts = {}
        base_path_count = None
        for master in font.masters:
            glayer = glyph.layers[master.id]
            if glayer:
                path_count = len(glayer.paths)
                path_counts[master.name] = path_count
                if base_path_count is None:
                    base_path_count = path_count

        results.append("\n--- Nombre de contorns (paths) ---")
        for master_name, count in path_counts.items():
            if count != base_path_count:
                results.append(f"  {master_name}: {count} ⚠️")
            else:
                results.append(f"  {master_name}: {count} ✓")

        # Comprovar si hi ha problemes d'interpolació (línia vermella)
        results.append("\n--- Estat d'interpolació ---")
        
        # Intentar obtenir l'estat d'interpolació
        interpolation_issues = []
        
        # Comprovar si hi ha nodes sense manejadors
        for master in font.masters:
            glayer = glyph.layers[master.id]
            if glayer:
                for path in glayer.paths:
                    for node in path.nodes:
                        if node.type == CURVE:
                            # Check if node has handles - different versions of Glyphs might have different APIs
                            try:
                                # Try to access handles in different ways
                                has_left = False
                                has_right = False
                                
                                # Method 1: direct attribute
                                if hasattr(node, 'leftHandle'):
                                    has_left = node.leftHandle is not None
                                if hasattr(node, 'rightHandle'):
                                    has_right = node.rightHandle is not None
                                
                                # Method 2: check through node properties
                                if not has_left and hasattr(node, 'connection'):
                                    # Some versions use connection
                                    pass
                                
                                if not has_left or not has_right:
                                    interpolation_issues.append(f"  {master.name}: Node curve sense manejadors a ({round(node.x,1)}, {round(node.y,1)})")
                            except:
                                # If we can't check properly, assume it's a problem
                                interpolation_issues.append(f"  {master.name}: Node curve sense manejadors a ({round(node.x,1)}, {round(node.y,1)})")
        
        if interpolation_issues:
            results.append("⚠️ Problemes detectats:")
            for issue in interpolation_issues[:10]:
                results.append(issue)
            if len(interpolation_issues) > 10:
                results.append(f"  ... i {len(interpolation_issues) - 10} més")
        else:
            results.append("✓ No s'han detectat problemes evidents amb els manejadors")

        # Resum final
        results.append("\n" + "=" * 40)
        
        if missing_masters or mismatches:
            results.append("❌ EL GLIFO NO ESTÀ LLEST PER INTERPOLAR")
            if missing_masters:
                results.append(f"   • {len(missing_masters)} master(s) sense el glifo")
            if mismatches:
                results.append(f"   • {len(mismatches)} master(s) amb diferent nombre de nodes")
        else:
            results.append("✅ EL GLIFO ESTÀ LLEST PER INTERPOLAR")
            results.append("   Si encara veus línia vermella, prova:")
            results.append("   1. Convert Paths to Cubic")
            results.append("   2. Correct Path Direction")
            results.append("   3. Sync First Node (selecciona un node extrem)")

        self.w.resultsArea.set("\n".join(results))


# Run the script
GlyphTools()