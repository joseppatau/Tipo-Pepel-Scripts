# MenuTitle: Smart Interpolation Engine
# -*- coding: utf-8 -*-
# Description: Adjusts node distances intelligently while preserving typographic constraints such as master lines and blue zones.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla
from math import fabs

class SmartNodeMoverUI(object):

    def __init__(self):
        # Ventana con selector de eje
        self.w = vanilla.FloatingWindow(
            (320, 440),
            "Smart Interpolation Engine",
            autosaveName="com.yournamespace.smartnodemover"
        )
        
        # Selector de eje (X/Y)
        self.w.axisText = vanilla.TextBox((10, 15, -10, 14), "Select Axis")
        self.w.axis = vanilla.RadioGroup(
            (10, 35, -10, 20),
            ["X", "Y"],
            isVertical=False
        )
        self.w.axis.set(1)  # Por defecto Y (vertical)
        
        # Campos de distancia
        self.w.distanceText = vanilla.TextBox((10, 65, -10, 14), "Current Distance Between Nodes")
        self.w.distance = vanilla.EditText((10, 85, -10, 22), "85")
        
        self.w.newDistanceText = vanilla.TextBox((10, 115, -10, 14), "New Distance")
        self.w.newDistance = vanilla.EditText((10, 135, -10, 22), "120")
        
        self.w.toleranceText = vanilla.TextBox((10, 165, -10, 14), "Tolerance")
        self.w.tolerance = vanilla.EditText((10, 185, -10, 22), "5")
        
        # Separador
        self.w.separator1 = vanilla.HorizontalLine((10, 220, -10, 1))
        
        # Título para checkboxes
        self.w.filterText = vanilla.TextBox((10, 230, -10, 14), "Apply to:")
        
        # Checkboxes para filtrar caracteres
        self.w.uppercaseCheckbox = vanilla.CheckBox(
            (10, 250, 100, 20),
            "Uppercase",
            value=True
        )
        
        self.w.lowercaseCheckbox = vanilla.CheckBox(
            (120, 250, 100, 20),
            "Lowercase",
            value=True
        )
        
        self.w.numbersCheckbox = vanilla.CheckBox(
            (10, 275, 100, 20),
            "Numbers",
            value=True
        )
        
        self.w.symbolsCheckbox = vanilla.CheckBox(
            (120, 275, 100, 20),
            "Symbols",
            value=True
        )
        
        self.w.punctuationCheckbox = vanilla.CheckBox(
            (10, 300, 100, 20),
            "Punctuation",
            value=True
        )
        
        # Botón para seleccionar/deseleccionar todos
        self.w.selectAllButton = vanilla.Button(
            (10, 325, 95, 22),
            "Select All",
            callback=self.selectAllCategories
        )
        
        self.w.deselectAllButton = vanilla.Button(
            (115, 325, 95, 22),
            "Deselect All",
            callback=self.deselectAllCategories
        )
        
        # Separador
        self.w.separator2 = vanilla.HorizontalLine((10, 355, -10, 1))
        
        # Checkbox para debug
        self.w.debugCheckbox = vanilla.CheckBox(
            (10, 365, -10, 20),
            "Debug Mode",
            value=False
        )
        
        # Botón principal
        self.w.applyButton = vanilla.Button(
            (10, -40, -10, 30),
            "SMART ADJUST",
            callback=self.applySmartAdjustment
        )
        
        self.w.open()
    
    def selectAllCategories(self, sender):
        """Selecciona todos los checkboxes"""
        self.w.uppercaseCheckbox.set(True)
        self.w.lowercaseCheckbox.set(True)
        self.w.numbersCheckbox.set(True)
        self.w.symbolsCheckbox.set(True)
        self.w.punctuationCheckbox.set(True)
    
    def deselectAllCategories(self, sender):
        """Deselecciona todos los checkboxes"""
        self.w.uppercaseCheckbox.set(False)
        self.w.lowercaseCheckbox.set(False)
        self.w.numbersCheckbox.set(False)
        self.w.symbolsCheckbox.set(False)
        self.w.punctuationCheckbox.set(False)
    
    def getSelectedCategories(self):
        """Obtiene las categorías seleccionadas"""
        categories = []
        if self.w.uppercaseCheckbox.get():
            categories.append("uppercase")
        if self.w.lowercaseCheckbox.get():
            categories.append("lowercase")
        if self.w.numbersCheckbox.get():
            categories.append("numbers")
        if self.w.symbolsCheckbox.get():
            categories.append("symbols")
        if self.w.punctuationCheckbox.get():
            categories.append("punctuation")
        return categories
    
    def shouldProcessGlyph(self, glyph_name, categories):
        """Determina si un glifo debe ser procesado basado en las categorías seleccionadas"""
        if not categories:  # Si no hay categorías seleccionadas, no procesar nada
            return False
        
        # Si todas las categorías están seleccionadas, procesar todo
        if len(categories) == 5:
            return True
        
        # Convertir el nombre del glifo a minúsculas para comparación
        glyph_lower = glyph_name.lower()
        
        # Verificar cada categoría
        for category in categories:
            if category == "uppercase":
                # Verificar si es una letra mayúscula (A-Z)
                if len(glyph_name) == 1 and glyph_name.isalpha() and glyph_name.isupper():
                    return True
                # También verificar glifos con nombres específicos de mayúsculas
                elif any(glyph_lower.startswith(prefix) for prefix in 
                        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                         'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']):
                    # Verificar que no sea una letra minúscula
                    if not (len(glyph_name) == 1 and glyph_name.isalpha() and glyph_name.islower()):
                        # Verificar si tiene variant selector o similar
                        if '.sc' not in glyph_lower and '.smcp' not in glyph_lower:
                            return True
            
            elif category == "lowercase":
                # Verificar si es una letra minúscula (a-z)
                if len(glyph_name) == 1 and glyph_name.isalpha() and glyph_name.islower():
                    return True
                # También verificar glifos con nombres específicos de minúsculas
                elif any(glyph_lower.startswith(prefix) for prefix in 
                        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                         'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']):
                    return True
                # Verificar small caps
                elif '.sc' in glyph_lower or '.smcp' in glyph_lower:
                    return True
            
            elif category == "numbers":
                # Verificar números (0-9)
                if len(glyph_name) == 1 and glyph_name.isdigit():
                    return True
                # También verificar nombres que comienzan con números
                elif any(glyph_lower.startswith(str(i)) for i in range(10)):
                    return True
            
            elif category == "symbols":
                # Lista de símbolos comunes
                symbols = ['exclam', 'at', 'numbersign', 'dollar', 'percent', 'ampersand',
                          'asterisk', 'parenleft', 'parenright', 'plus', 'comma', 'hyphen',
                          'period', 'slash', 'colon', 'semicolon', 'less', 'equal', 'greater',
                          'question', 'bracketleft', 'backslash', 'bracketright',
                          'asciicircum', 'underscore', 'grave', 'braceleft', 'bar',
                          'braceright', 'asciitilde', 'bullet', 'degree', 'currency',
                          'copyright', 'registered', 'trademark', 'section', 'paragraph',
                          'dagger', 'daggerdbl', 'lozenge', 'circle']
                
                for symbol in symbols:
                    if symbol in glyph_lower:
                        return True
            
            elif category == "punctuation":
                # Lista de puntuación
                punctuation = ['comma', 'period', 'colon', 'semicolon', 'exclam',
                              'question', 'quoteleft', 'quoteright', 'quotedblleft',
                              'quotedblright', 'quotesingle', 'quotedbl', 'apostrophe',
                              'hyphen', 'endash', 'emdash', 'underscore', 'ellipsis',
                              'bullet', 'periodcentered', 'guillemotleft', 'guillemotright',
                              'guilsinglleft', 'guilsinglright']
                
                for punct in punctuation:
                    if punct in glyph_lower:
                        return True
        
        return False
    
    def getMasterLinePositions(self, font, master):
        """Obtiene todas las posiciones de líneas maestras con sus blue zones"""
        positions = {}
        
        # Baseline
        positions['baseline'] = 0
        
        # x-Height
        positions['x-height'] = master.xHeight
        
        # Cap Height
        positions['cap-height'] = master.capHeight
        
        # Ascender
        positions['ascender'] = master.ascender
        
        # Descender
        positions['descender'] = master.descender
        
        # Blue zones (overshoots) - valores por defecto
        baseline_overshoot = 12
        xheight_overshoot = 12
        capheight_overshoot = 12
        ascender_overshoot = 12
        descender_overshoot = 12
        
        # Intentar obtener blue zones reales
        try:
            # Glyphs 2
            if hasattr(master, 'customParameters'):
                for param in master.customParameters:
                    if param.name == 'BlueScale':
                        blue_scale = float(param.value)
                        # Calcular overshoots
                        baseline_overshoot = round(master.xHeight * blue_scale)
                        xheight_overshoot = round(master.xHeight * blue_scale)
                        capheight_overshoot = round(master.xHeight * blue_scale)
            
            # Glyphs 3
            if hasattr(master, 'metrics'):
                for metric in master.metrics:
                    if hasattr(metric, 'size'):
                        if metric.type == 0:  # baseline
                            baseline_overshoot = metric.size
                        elif metric.type == 1:  # x-height
                            xheight_overshoot = metric.size
                        elif metric.type == 2:  # cap-height
                            capheight_overshoot = metric.size
        except:
            pass
        
        # Guardar overshoots
        positions['baseline_overshoot'] = baseline_overshoot
        positions['x-height_overshoot'] = xheight_overshoot
        positions['cap-height_overshoot'] = capheight_overshoot
        positions['ascender_overshoot'] = ascender_overshoot
        positions['descender_overshoot'] = descender_overshoot
        
        # Calcular posiciones de los extremos de las blue zones
        positions['baseline_extreme'] = 0 - baseline_overshoot
        positions['x-height_extreme'] = master.xHeight + xheight_overshoot
        positions['cap-height_extreme'] = master.capHeight + capheight_overshoot
        positions['ascender_extreme'] = master.ascender - ascender_overshoot
        positions['descender_extreme'] = master.descender - descender_overshoot
        
        return positions
    
    def getNodeBlueZoneExtreme(self, node_y, master_positions):
        """Determina en qué extremo de blue zone está un nodo y devuelve esa posición"""
        tolerance = 2
        
        # Baseline extreme (negativo)
        if fabs(node_y - master_positions['baseline_extreme']) <= tolerance:
            return master_positions['baseline_extreme'], "baseline_extreme"
        
        # Baseline (exacta)
        if fabs(node_y - master_positions['baseline']) <= tolerance:
            return master_positions['baseline'], "baseline"
        
        # x-Height extreme (positivo)
        if fabs(node_y - master_positions['x-height_extreme']) <= tolerance:
            return master_positions['x-height_extreme'], "x-height_extreme"
        
        # x-Height (exacta)
        if fabs(node_y - master_positions['x-height']) <= tolerance:
            return master_positions['x-height'], "x-height"
        
        # Cap-height extreme (positivo)
        if fabs(node_y - master_positions['cap-height_extreme']) <= tolerance:
            return master_positions['cap-height_extreme'], "cap-height_extreme"
        
        # Cap-height (exacta)
        if fabs(node_y - master_positions['cap-height']) <= tolerance:
            return master_positions['cap-height'], "cap-height"
        
        # Ascender extreme (negativo desde el ascender)
        if fabs(node_y - master_positions['ascender_extreme']) <= tolerance:
            return master_positions['ascender_extreme'], "ascender_extreme"
        
        # Ascender (exacta)
        if fabs(node_y - master_positions['ascender']) <= tolerance:
            return master_positions['ascender'], "ascender"
        
        # Descender extreme (más negativo)
        if fabs(node_y - master_positions['descender_extreme']) <= tolerance:
            return master_positions['descender_extreme'], "descender_extreme"
        
        # Descender (exacta)
        if fabs(node_y - master_positions['descender']) <= tolerance:
            return master_positions['descender'], "descender"
        
        return None, None
    
    def isNodeOnMasterLine(self, node, master_positions):
        """Verifica si un nodo está en una línea maestra o en su blue zone"""
        tolerance = 2
        
        # Baseline y su blue zone
        baseline = master_positions['baseline']
        baseline_extreme = master_positions['baseline_extreme']
        if fabs(node.y - baseline) <= tolerance or fabs(node.y - baseline_extreme) <= tolerance:
            if fabs(node.y - baseline_extreme) <= tolerance:
                return True, baseline_extreme, "baseline_extreme"
            else:
                return True, baseline, "baseline"
        
        # x-Height y su blue zone
        x_height = master_positions['x-height']
        x_height_extreme = master_positions['x-height_extreme']
        if fabs(node.y - x_height) <= tolerance or fabs(node.y - x_height_extreme) <= tolerance:
            if fabs(node.y - x_height_extreme) <= tolerance:
                return True, x_height_extreme, "x-height_extreme"
            else:
                return True, x_height, "x-height"
        
        # Cap-height y su blue zone
        cap_height = master_positions['cap-height']
        cap_height_extreme = master_positions['cap-height_extreme']
        if fabs(node.y - cap_height) <= tolerance or fabs(node.y - cap_height_extreme) <= tolerance:
            if fabs(node.y - cap_height_extreme) <= tolerance:
                return True, cap_height_extreme, "cap-height_extreme"
            else:
                return True, cap_height, "cap-height"
        
        # Ascender y su blue zone
        ascender = master_positions['ascender']
        ascender_extreme = master_positions['ascender_extreme']
        if fabs(node.y - ascender) <= tolerance or fabs(node.y - ascender_extreme) <= tolerance:
            if fabs(node.y - ascender_extreme) <= tolerance:
                return True, ascender_extreme, "ascender_extreme"
            else:
                return True, ascender, "ascender"
        
        # Descender y su blue zone
        descender = master_positions['descender']
        descender_extreme = master_positions['descender_extreme']
        if fabs(node.y - descender) <= tolerance or fabs(node.y - descender_extreme) <= tolerance:
            if fabs(node.y - descender_extreme) <= tolerance:
                return True, descender_extreme, "descender_extreme"
            else:
                return True, descender, "descender"
        
        return False, None, None
    
    def applySmartAdjustment(self, sender):
        """Aplicar ajuste inteligente"""
        font = Glyphs.font
        if not font:
            return
        
        # Verificar que al menos una categoría esté seleccionada
        categories = self.getSelectedCategories()
        if not categories:
            Glyphs.showNotification(
                "Smart Node Mover",
                "Please select at least one character category."
            )
            return
        
        master = font.selectedFontMaster
        useY = (self.w.axis.get() == 1)  # 0 = X, 1 = Y
        
        try:
            targetDistance = float(self.w.distance.get())
            newDistance = float(self.w.newDistance.get())
            tolerance = float(self.w.tolerance.get())
        except ValueError:
            Glyphs.showNotification(
                "Smart Node Mover",
                "Please enter valid numeric values."
            )
            return
        
        debug_mode = self.w.debugCheckbox.get()
        
        # Obtener posiciones de líneas maestras
        master_positions = self.getMasterLinePositions(font, master)
        
        if debug_mode:
            Glyphs.clearLog()
            Glyphs.showMacroWindow()
            print("=== SMART NODE MOVER DEBUG ===")
            print(f"Target distance: {targetDistance}")
            print(f"New distance: {newDistance}")
            print(f"Tolerance: {tolerance}")
            print(f"Axis: {'Y' if useY else 'X'}")
            print(f"Categories: {categories}")
            print(f"\nMaster positions and extremes:")
            print(f"  Baseline: {master_positions['baseline']} (extreme: {master_positions['baseline_extreme']})")
            print(f"  x-Height: {master_positions['x-height']} (extreme: {master_positions['x-height_extreme']})")
            print(f"  Cap-height: {master_positions['cap-height']} (extreme: {master_positions['cap-height_extreme']})")
            print(f"  Ascender: {master_positions['ascender']} (extreme: {master_positions['ascender_extreme']})")
            print(f"  Descender: {master_positions['descender']} (extreme: {master_positions['descender_extreme']})")
            print()
        
        masterID = master.id
        segmentsAdjusted = 0
        nodesMoved = 0
        nodesLocked = 0
        
        font.disableUpdateInterface()
        
        try:
            for glyph in font.glyphs:
                # Filtrar por categorías seleccionadas
                if not self.shouldProcessGlyph(glyph.name, categories):
                    continue
                
                if debug_mode:
                    print(f"\n=== Processing: {glyph.name} ===")
                
                layer = glyph.layers[masterID]
                if not layer or not layer.paths:
                    continue
                
                # PASO 1: Recolectar todos los nodos
                all_nodes = []
                for path in layer.paths:
                    for node in path.nodes:
                        all_nodes.append(node)
                
                if debug_mode:
                    print(f"Total nodes: {len(all_nodes)}")
                
                # PASO 2: Identificar nodos en líneas maestras
                master_line_nodes = {}
                
                for node in all_nodes:
                    is_master, master_line_pos, master_type = self.isNodeOnMasterLine(node, master_positions)
                    if is_master:
                        # Determinar si es un extremo de blue zone o línea exacta
                        blue_zone_extreme, extreme_type = self.getNodeBlueZoneExtreme(node.y, master_positions)
                        
                        # Usar el extremo de blue zone si existe
                        if blue_zone_extreme is not None and "extreme" in extreme_type:
                            target_position = blue_zone_extreme
                            position_type = extreme_type
                        else:
                            target_position = master_line_pos
                            position_type = master_type
                        
                        # Guardar información del nodo maestro
                        master_line_nodes[node] = {
                            'original_pos': (node.x, node.y),
                            'target_position': target_position,
                            'position_type': position_type,
                            'is_extreme': "extreme" in position_type
                        }
                        
                        if debug_mode:
                            node_type = "EXTREME" if "extreme" in position_type else "LINE"
                            print(f"📍 Master {node_type} node: ({node.x:.1f}, {node.y:.1f}) - {position_type}")
                
                # PASO 3: Ordenar nodos por el eje seleccionado
                if useY:
                    sorted_nodes = sorted(all_nodes, key=lambda n: n.y)
                else:
                    sorted_nodes = sorted(all_nodes, key=lambda n: n.x)
                
                # PASO 4: Procesar pares de nodos con la distancia objetivo
                processed_pairs = set()
                
                for i in range(len(sorted_nodes)):
                    for j in range(i + 1, len(sorted_nodes)):
                        node1 = sorted_nodes[i]
                        node2 = sorted_nodes[j]
                        
                        # Crear un ID único para este par
                        pair_id = (id(node1), id(node2))
                        if pair_id in processed_pairs:
                            continue
                        
                        # Calcular distancia en el eje seleccionado
                        if useY:
                            distance = fabs(node2.y - node1.y)
                        else:
                            distance = fabs(node2.x - node1.x)
                        
                        # Verificar si la distancia está dentro del rango objetivo
                        if fabs(distance - targetDistance) <= tolerance:
                            # Debug: mostrar información del par
                            if debug_mode:
                                node1_is_master = node1 in master_line_nodes
                                node2_is_master = node2 in master_line_nodes
                                node1_info = f"[{master_line_nodes[node1]['position_type']}]" if node1_is_master else ""
                                node2_info = f"[{master_line_nodes[node2]['position_type']}]" if node2_is_master else ""
                                print(f"\n🎯 Pair found: distance = {distance:.1f}")
                                print(f"  Node1: ({node1.x:.1f}, {node1.y:.1f}) {node1_info}")
                                print(f"  Node2: ({node2.x:.1f}, {node2.y:.1f}) {node2_info}")
                            
                            # Determinar qué nodo es primero (menor valor en el eje)
                            if useY:
                                if node1.y < node2.y:
                                    first_node, second_node = node1, node2
                                    first_pos, second_pos = node1.y, node2.y
                                else:
                                    first_node, second_node = node2, node1
                                    first_pos, second_pos = node2.y, node1.y
                            else:
                                if node1.x < node2.x:
                                    first_node, second_node = node1, node2
                                    first_pos, second_pos = node1.x, node2.x
                                else:
                                    first_node, second_node = node2, node1
                                    first_pos, second_pos = node2.x, node1.x
                            
                            # Verificar si los nodos están en líneas maestras
                            first_is_master = first_node in master_line_nodes
                            second_is_master = second_node in master_line_nodes
                            
                            # Calcular ajuste necesario
                            adjustment = newDistance - distance
                            
                            # Guardar posiciones originales para debug
                            if debug_mode:
                                first_original_pos = (first_node.x, first_node.y)
                                second_original_pos = (second_node.x, second_node.y)
                            
                            # NUEVA LÓGICA: MOVER AMBOS NODOS PERO MANTENER EL MAESTRO EN SU LÍNEA
                            if first_is_master and not second_is_master:
                                # Nodo 1 está en línea maestra, nodo 2 no
                                # Calcular nueva posición del nodo 2 para mantener la nueva distancia
                                if useY:
                                    # Para eje Y: nodo 2 se mueve para estar a nueva distancia del nodo 1
                                    second_node.y = first_node.y + newDistance
                                else:
                                    # Para eje X
                                    second_node.x = first_node.x + newDistance
                                
                                if debug_mode:
                                    print(f"  → Both nodes moved (first on master line)")
                                    print(f"    First node (master): ({first_original_pos[0]:.1f}, {first_original_pos[1]:.1f}) → ({first_node.x:.1f}, {first_node.y:.1f})")
                                    print(f"    Second node: ({second_original_pos[0]:.1f}, {second_original_pos[1]:.1f}) → ({second_node.x:.1f}, {second_node.y:.1f})")
                                
                                nodesMoved += 2  # Ambos nodos se han "movido" conceptualmente
                                segmentsAdjusted += 1
                            
                            elif not first_is_master and second_is_master:
                                # Nodo 2 está en línea maestra, nodo 1 no
                                # Calcular nueva posición del nodo 1 para mantener la nueva distancia
                                if useY:
                                    # Para eje Y: nodo 1 se mueve para estar a nueva distancia del nodo 2
                                    first_node.y = second_node.y - newDistance
                                else:
                                    # Para eje X
                                    first_node.x = second_node.x - newDistance
                                
                                if debug_mode:
                                    print(f"  → Both nodes moved (second on master line)")
                                    print(f"    First node: ({first_original_pos[0]:.1f}, {first_original_pos[1]:.1f}) → ({first_node.x:.1f}, {first_node.y:.1f})")
                                    print(f"    Second node (master): ({second_original_pos[0]:.1f}, {second_original_pos[1]:.1f}) → ({second_node.x:.1f}, {second_node.y:.1f})")
                                
                                nodesMoved += 2
                                segmentsAdjusted += 1
                            
                            elif first_is_master and second_is_master:
                                # Ambos nodos están en líneas maestras
                                if debug_mode:
                                    print(f"  → Both nodes on master lines - NO MOVEMENT")
                                
                                nodesLocked += 2
                            
                            else:
                                # Ninguno está en línea maestra
                                # Mover ambos nodos proporcionalmente
                                if useY:
                                    first_node.y -= adjustment / 2
                                    second_node.y += adjustment / 2
                                else:
                                    first_node.x -= adjustment / 2
                                    second_node.x += adjustment / 2
                                
                                if debug_mode:
                                    print(f"  → Moved both nodes proportionally")
                                    print(f"    First node: ({first_original_pos[0]:.1f}, {first_original_pos[1]:.1f}) → ({first_node.x:.1f}, {first_node.y:.1f})")
                                    print(f"    Second node: ({second_original_pos[0]:.1f}, {second_original_pos[1]:.1f}) → ({second_node.x:.1f}, {second_node.y:.1f})")
                                
                                nodesMoved += 2
                                segmentsAdjusted += 1
                            
                            # Marcar este par como procesado
                            processed_pairs.add(pair_id)
                
                # PASO 5: RESTAURAR nodos en líneas maestras a su POSICIÓN TARGET después de todos los movimientos
                restoration_count = 0
                for node, info in master_line_nodes.items():
                    target_position = info['target_position']
                    position_type = info['position_type']
                    original_pos = info['original_pos']
                    
                    # Solo restaurar en el eje Y (líneas maestras son horizontales)
                    if useY:
                        # El nodo maestro podría haberse movido ligeramente durante el ajuste proporcional
                        # o necesitamos restaurarlo a su posición target
                        current_y = node.y
                        
                        # Verificar si el nodo está donde debería estar
                        if fabs(current_y - target_position) > 0.1:
                            node.y = target_position
                            if debug_mode:
                                node_type = "EXTREME" if "extreme" in position_type else "LINE"
                                print(f"🔧 Restored {node_type} {position_type} node Y: {current_y:.1f} → {target_position:.1f}")
                            restoration_count += 1
                    
                    # Mantener la coordenada X original si es posible
                    original_x = original_pos[0]
                    if fabs(node.x - original_x) > 0.1:
                        # Solo ajustar X si no afecta la distancia con compañeros
                        # Buscar si hay un compañero vertical
                        has_vertical_partner = False
                        for other_node in all_nodes:
                            if other_node != node and fabs(other_node.x - node.x) < 5:
                                has_vertical_partner = True
                                break
                        
                        if not has_vertical_partner:
                            node.x = original_x
                            if debug_mode:
                                print(f"🔧 Restored X coordinate to original: {node.x:.1f}")
                
                if debug_mode and restoration_count > 0:
                    print(f"  → Restored {restoration_count} master line nodes to target positions")
        
        except Exception as e:
            if debug_mode:
                print(f"\n❌ ERROR: {str(e)}")
            font.enableUpdateInterface()
            raise
        
        font.enableUpdateInterface()
        
        # Mostrar resultados
        axis_name = "Y" if useY else "X"
        
        if debug_mode:
            print(f"\n=== FINAL RESULTS ===")
            print(f"Segments adjusted: {segmentsAdjusted}")
            print(f"Nodes moved: {nodesMoved}")
            print(f"Nodes locked on master lines: {nodesLocked}")
        
        # Mostrar notificación
        if segmentsAdjusted > 0:
            message = f"✅ Adjusted {segmentsAdjusted} segments on {axis_name} axis\n"
            message += f"📊 {nodesMoved} nodes moved intelligently\n"
            message += f"🔒 {nodesLocked} nodes preserved on master lines"
        else:
            message = f"❌ No segments found on {axis_name} axis\n"
            message += "Check distance and tolerance values"
        
        Glyphs.showNotification(f"Smart Node Mover ({axis_name})", message)


# Ejecutar la interfaz
SmartNodeMoverUI()