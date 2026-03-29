#MenuTitle: Character Tuner
# -*- coding: utf-8 -*-
# Description: Detects and corrects line alignment and stem widths using geometric grouping and node pairing.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from GlyphsApp import Glyphs, GSNode, Message
import vanilla
import math


class CharacterTuner(object):
    
    def __init__(self):
        self.font = Glyphs.font

        if not self.font:
            Glyphs.showNotification("Character Tuner", "No font open.")
            return

        if len(self.font.masters) < 1:
            Glyphs.showNotification("Character Tuner", "Font needs at least 1 master.")
            return

        masterNames = [m.name for m in self.font.masters]

        self.w = vanilla.FloatingWindow(
            (420, 520),
            "Character Tuner",
            autosaveName="com.charactertuner.main"
        )

        # ---- MASTER SELECTOR ----
        self.w.masterText = vanilla.TextBox(
            (15, 15, -15, 14),
            "Master to process:"
        )

        self.w.masterPopup = vanilla.PopUpButton(
            (15, 35, -15, 22),
            masterNames
        )
        
        # Mostrar el master seleccionado actualmente
        self.w.currentMasterText = vanilla.TextBox(
            (15, 65, -15, 14),
            f"Current: {self.font.masters[0].name}"
        )
        
        # Actualizar cuando cambie la selección
        self.w.masterPopup._setCallback(self.masterChanged)
        
        # Separator
        self.w.separator0 = vanilla.HorizontalLine((10, 90, -10, 1))
        
        # ---- LINE DETECTOR SECTION ----
        self.w.lineDetectorTitle = vanilla.TextBox((10, 100, 200, 16), "Non rect line detector")
        
        # Horizontal/Vertical radio
        self.w.lineOrientation = vanilla.RadioGroup(
            (20, 120, 150, 20),
            ["Horizontal", "Vertical"],
            isVertical=False
        )
        self.w.lineOrientation.set(1)  # Vertical by default
        
        # Margin
        self.w.marginText = vanilla.TextBox((20, 145, 80, 20), "Margin:")
        self.w.margin = vanilla.EditText((100, 142, 50, 22), "3")
        
        # Min length
        self.w.minLengthText = vanilla.TextBox((180, 145, 80, 20), "Min length:")
        self.w.minLength = vanilla.EditText((260, 142, 50, 22), "20")
        
        # Align to (dynamic based on orientation)
        self.w.alignText = vanilla.TextBox((20, 175, 80, 20), "Align to:")
        self.w.alignment = vanilla.RadioGroup(
            (100, 172, 200, 20),
            ["Left", "Center", "Right"],
            isVertical=False
        )
        self.w.alignment.set(1)  # Center by default
        
        # Apply line detector button
        self.w.applyLineBtn = vanilla.Button(
            (280, 200, 120, 24),
            "Apply Lines",
            callback=self.applyLineCorrection
        )
        
        # Separator
        self.w.separator1 = vanilla.HorizontalLine((10, 230, -10, 1))
        
        # ---- STEM WIDTH CHANGE SECTION ----
        self.w.stemTitle = vanilla.TextBox((10, 240, 200, 16), "Stem width Change")
        
        # X/Y radio
        self.w.stemAxis = vanilla.RadioGroup(
            (20, 260, 100, 20),
            ["X", "Y"],
            isVertical=False
        )
        self.w.stemAxis.set(1)  # Y by default
        
        # RECT section
        self.w.rectTitle = vanilla.TextBox((20, 290, 100, 16), "Rect:")
        
        self.w.rectMinText = vanilla.TextBox((40, 315, 80, 20), "Width min:")
        self.w.rectMin = vanilla.EditText((120, 312, 50, 22), "97")
        
        self.w.rectMaxText = vanilla.TextBox((190, 315, 80, 20), "Width max:")
        self.w.rectMax = vanilla.EditText((270, 312, 50, 22), "102")
        
        self.w.rectNewText = vanilla.TextBox((40, 345, 80, 20), "New width:")
        self.w.rectNew = vanilla.EditText((120, 342, 50, 22), "99")
        
        # CURVE section
        self.w.curveTitle = vanilla.TextBox((20, 380, 100, 16), "Curve (handles only):")
        
        self.w.curveMinText = vanilla.TextBox((40, 405, 80, 20), "Width min:")
        self.w.curveMin = vanilla.EditText((120, 402, 50, 22), "62")
        
        self.w.curveMaxText = vanilla.TextBox((190, 405, 80, 20), "Width max:")
        self.w.curveMax = vanilla.EditText((270, 402, 50, 22), "64")
        
        self.w.curveNewText = vanilla.TextBox((40, 435, 120, 20), "New width:")
        self.w.curveNew = vanilla.EditText((160, 432, 50, 22), "65")
        
        # Direction info
        self.w.directionText = vanilla.TextBox((20, 470, 300, 16), "Direction: Second node only (fixed)")
        
        # Apply stem button
        self.w.applyStemBtn = vanilla.Button(
            (280, 490, 120, 24),
            "Apply Stem",
            callback=self.applyStemCorrection
        )
        
        self.w.open()
        self.w.makeKey()
        
        # Bind orientation change to update alignment labels
        self.w.lineOrientation._setCallback(self.orientationChanged)
    
    def masterChanged(self, sender):
        """Update current master text when selection changes"""
        master_index = self.w.masterPopup.get()
        master = self.font.masters[master_index]
        self.w.currentMasterText.set(f"Current: {master.name}")
    
    def orientationChanged(self, sender):
        """Update alignment labels based on orientation"""
        if sender.get() == 0:  # Horizontal
            self.w.alignment.setItems(["Bottom", "Center", "Top"])
        else:  # Vertical
            self.w.alignment.setItems(["Left", "Center", "Right"])
    
    def showMessage(self, title, message):
        """Show a message using Glyphs Message function"""
        Message(title, message)
    
    def debugPrint(self, message):
        """Print debug message to console"""
        print("🔍 DEBUG: " + str(message))
    
    def getCurrentLayer(self):
        """Get active layer from current glyph"""
        font = Glyphs.font
        if not font:
            return None
        
        if not font.selectedLayers:
            return None
        
        return font.selectedLayers[0]
    
    def getFloatValue(self, field, default=20.0):
        """Safely get float value from edit text field"""
        try:
            value = field.get().strip()
            if value == "":
                return default
            return float(value)
        except:
            return default
    
    def hasHandles(self, node):
        """Check if a node has Bezier handles."""
        node_type = getattr(node, 'type', None)
        
        # Convertir a string si es necesario
        if node_type is not None:
            node_type_str = str(node_type).lower()
        else:
            node_type_str = ""
        
        # Los nodos de tipo "curve" siempre tienen manejadores
        if node_type_str == "curve":
            return True
        
        return False
    
    def getNodeTypeDescription(self, node):
        """Get a description of the node type for debugging"""
        node_type = getattr(node, 'type', 'unknown')
        
        # Convertir a string para comparar
        node_type_str = str(node_type).lower() if node_type is not None else "unknown"
        
        if node_type_str == "line":
            return "LINE (corner)"
        elif node_type_str == "curve":
            return "CURVE (has handles)"
        elif node_type_str == "offcurve":
            return "OFFCURVE (off-curve point)"
        else:
            return f"type={node_type_str} (unknown)"
    
    def isNodeSelected(self, node):
        """Check if a node is selected"""
        return hasattr(node, 'selected') and node.selected
    
    # ==================== LINE DETECTOR METHODS ====================
    
    def findNodesToAlign(self, layer, margin, min_length, is_horizontal):
        """Find nodes that should be aligned"""
        groups = {}
        
        for path in layer.paths:
            for node in path.nodes:
                pos = node.y if is_horizontal else node.x
                other_pos = node.x if is_horizontal else node.y
                
                found_group = False
                for group_pos in list(groups.keys()):
                    if abs(pos - group_pos) <= margin:
                        groups[group_pos].append({
                            'node': node,
                            'pos': pos,
                            'other_pos': other_pos
                        })
                        found_group = True
                        break
                
                if not found_group:
                    groups[pos] = [{
                        'node': node,
                        'pos': pos,
                        'other_pos': other_pos
                    }]
        
        nodes_to_align = []
        
        for group_pos, nodes in groups.items():
            if len(nodes) < 2:
                continue
            
            nodes.sort(key=lambda n: n['other_pos'])
            other_min = nodes[0]['other_pos']
            other_max = nodes[-1]['other_pos']
            span = other_max - other_min
            
            if span >= min_length:
                nodes_to_align.append({
                    'group_pos': group_pos,
                    'nodes': nodes,
                    'span': span,
                    'pos_values': [n['pos'] for n in nodes]
                })
        
        return nodes_to_align
    
    def calculateTargetPos(self, pos_values, alignment, is_horizontal):
        """Calculate target position based on alignment choice"""
        if is_horizontal:
            if alignment == 0:  # Bottom
                return min(pos_values)
            elif alignment == 1:  # Center
                return sum(pos_values) / len(pos_values)
            else:  # Top
                return max(pos_values)
        else:
            if alignment == 0:  # Left
                return min(pos_values)
            elif alignment == 1:  # Center
                return sum(pos_values) / len(pos_values)
            else:  # Right
                return max(pos_values)
    
    def applyLineCorrection(self, sender):
        """Apply line detector correction to current glyph using selected master"""
        font = Glyphs.font
        if not font:
            return
        
        selected_layers = font.selectedLayers
        if not selected_layers:
            return
        
        # Obtener el master seleccionado en el popup
        master_index = self.w.masterPopup.get()
        target_master = font.masters[master_index]
        
        # Get unique glyphs from selected layers
        glyphs_to_process = {}
        for layer in selected_layers:
            glyph = layer.parent
            if glyph.name not in glyphs_to_process:
                glyphs_to_process[glyph.name] = glyph
        
        # Read values with defaults
        margin = self.getFloatValue(self.w.margin, 3.0)
        min_length = self.getFloatValue(self.w.minLength, 20.0)
        
        orientation = self.w.lineOrientation.get()
        is_horizontal = (orientation == 0)
        alignment = self.w.alignment.get()
        
        font.disableUpdateInterface()
        
        for glyph_name, glyph in glyphs_to_process.items():
            layer = glyph.layers[target_master.id]
            
            if not layer:
                continue
            
            # Find candidates
            candidates = self.findNodesToAlign(layer, margin, min_length, is_horizontal)
            
            if not candidates:
                continue
            
            glyph.beginUndo()
            
            for candidate in candidates:
                nodes = candidate['nodes']
                pos_values = candidate['pos_values']
                target_pos = self.calculateTargetPos(pos_values, alignment, is_horizontal)
                
                for node_info in nodes:
                    node = node_info['node']
                    if is_horizontal:
                        node.y = target_pos
                    else:
                        node.x = target_pos
            
            glyph.endUndo()
        
        font.enableUpdateInterface()
    
    # ==================== STEM WIDTH METHODS ====================
    
    def findUniqueNodePairs(self, layer, axis, min_width, max_width, require_handles=False, debug=False):
        """
        Find unique pairs of nodes where each node is used only once
        require_handles: if True, only include nodes with Bezier handles
        debug: if True, show detailed information
        """
        all_nodes = []
        nodes_with_handles = 0
        nodes_without_handles = 0
        
        if debug:
            self.debugPrint(f"--- Scanning nodes (require_handles={require_handles}) ---")
        
        for path in layer.paths:
            for node in path.nodes:
                node_desc = self.getNodeTypeDescription(node)
                
                if require_handles:
                    has_handles = self.hasHandles(node)
                    
                    if has_handles:
                        nodes_with_handles += 1
                        if debug:
                            self.debugPrint(f"  ✓ INCLUDED: {node_desc} at ({round(node.x,1)}, {round(node.y,1)})")
                        all_nodes.append(node)
                    else:
                        nodes_without_handles += 1
                        if debug:
                            self.debugPrint(f"  ✗ SKIPPED: {node_desc} at ({round(node.x,1)}, {round(node.y,1)}) - no handles")
                else:
                    if debug:
                        self.debugPrint(f"  • INCLUDED: {node_desc} at ({round(node.x,1)}, {round(node.y,1)})")
                    all_nodes.append(node)
        
        if require_handles and debug:
            self.debugPrint(f"\nSummary: {nodes_with_handles} with handles, {nodes_without_handles} without handles")
        
        if debug:
            self.debugPrint(f"Total nodes: {len(all_nodes)}")
        
        if len(all_nodes) < 2:
            if debug:
                self.debugPrint("Not enough nodes")
            return []
        
        # Sort by axis value
        if axis == 0:
            all_nodes.sort(key=lambda n: n.x)
            if debug:
                self.debugPrint(f"Sorted X values: {[(round(n.x,1), round(n.y,1)) for n in all_nodes]}")
        else:
            all_nodes.sort(key=lambda n: n.y)
            if debug:
                self.debugPrint(f"Sorted Y values: {[(round(n.y,1), round(n.x,1)) for n in all_nodes]}")
        
        # Find unique pairs
        used_nodes = set()
        unique_pairs = []
        
        if debug:
            self.debugPrint(f"\n--- Checking pairs with range {min_width} to {max_width} ---")
        
        for i in range(len(all_nodes)):
            node1 = all_nodes[i]
            if id(node1) in used_nodes:
                continue
                
            for j in range(i + 1, len(all_nodes)):
                node2 = all_nodes[j]
                if id(node2) in used_nodes:
                    continue
                
                if axis == 0:
                    distance = abs(node2.x - node1.x)
                    coord1 = node1.x
                    coord2 = node2.x
                else:
                    distance = abs(node2.y - node1.y)
                    coord1 = node1.y
                    coord2 = node2.y
                
                if debug:
                    self.debugPrint(f"  Checking pair: {round(coord1,1)} - {round(coord2,1)} = {round(distance,1)}")
                    self.debugPrint(f"    Range: {min_width} <= {round(distance,1)} <= {max_width}? {min_width <= distance <= max_width}")
                
                if min_width <= distance <= max_width:
                    unique_pairs.append((node1, node2, distance))
                    used_nodes.add(id(node1))
                    used_nodes.add(id(node2))
                    if debug:
                        self.debugPrint(f"    ✓ PAIR ACCEPTED")
                    break
                else:
                    if debug:
                        self.debugPrint(f"    ✗ PAIR REJECTED (outside range)")
        
        if debug:
            self.debugPrint(f"\nFound {len(unique_pairs)} unique pairs")
        
        return unique_pairs
    
    def adjustNodePair(self, node1, node2, current_distance, new_distance, axis):
        """Adjust a pair of nodes - Second node only, moving handles as well"""
        self.debugPrint(f"Adjusting: {round(current_distance,1)} -> {round(new_distance,1)}")
    
        if axis == 0:  # X axis
            # Ensure node1 is left, node2 is right
            if node1.x > node2.x:
                node1, node2 = node2, node1
        
            adjustment = new_distance - current_distance
            old_x = node2.x
        
            # Move the node
            node2.x += adjustment
        
            # Move connected offcurve nodes (handles)
            offcurves = self.getConnectedOffcurves(node2)
            for offcurve in offcurves:
                offcurve.x += adjustment
                self.debugPrint(f"  Moved offcurve at ({round(offcurve.x,1)}, {round(offcurve.y,1)})")
        
            self.debugPrint(f"X: left={round(node1.x,1)}, right {round(old_x,1)} → {round(node2.x,1)}")
            
        else:  # Y axis
            # In Glyphs, Y increases downward, so top has smaller Y, bottom has larger Y
            if node1.y > node2.y:
                node1, node2 = node2, node1
        
            adjustment = new_distance - current_distance
            old_y = node2.y
        
            # Move the node
            node2.y += adjustment
        
            # Move connected offcurve nodes (handles)
            offcurves = self.getConnectedOffcurves(node2)
            for offcurve in offcurves:
                offcurve.y += adjustment
                self.debugPrint(f"  Moved offcurve at ({round(offcurve.x,1)}, {round(offcurve.y,1)})")
        
            self.debugPrint(f"Y: top={round(node1.y,1)}, bottom {round(old_y,1)} → {round(node2.y,1)}")
    
    


    def getConnectedOffcurves(self, node):
        """Get all offcurve nodes connected to this curve node"""
        connected = []
    
        if not hasattr(node, 'parent'):
            return connected
    
        path = node.parent
        if not path:
            return connected
    
        nodes = path.nodes
        node_index = None
    
        for i, n in enumerate(nodes):
            if n is node:
                node_index = i
                break
    
        if node_index is None:
            return connected
    
        # Check previous node
        prev_index = (node_index - 1) % len(nodes)
        prev_node = nodes[prev_index]
        prev_type = str(getattr(prev_node, 'type', '')).lower()
        if prev_type == "offcurve":
            connected.append(prev_node)
    
        # Check next node
        next_index = (node_index + 1) % len(nodes)
        next_node = nodes[next_index]
        next_type = str(getattr(next_node, 'type', '')).lower()
        if next_type == "offcurve":
            connected.append(next_node)
    
        return connected
    
    
    
    def moveConnectedHandles(self, node, adjustment, axis):
        """Move all handles (offcurve nodes) connected to this curve node"""
        if not hasattr(node, 'parent'):
            return
    
        path = node.parent
        if not path:
            return
    
        # Find all nodes in the path
        nodes = path.nodes
        node_index = None
    
        # Find the index of this node
        for i, n in enumerate(nodes):
            if n is node:
                node_index = i
                break
    
        if node_index is None:
            return
    
        # Check previous node (if it's an offcurve connected to this curve)
        prev_index = (node_index - 1) % len(nodes)
        prev_node = nodes[prev_index]
    
        # Check if previous node is offcurve
        prev_type = str(getattr(prev_node, 'type', '')).lower()
        if prev_type == "offcurve":
            if axis == 0:
                prev_node.x += adjustment
            else:
                prev_node.y += adjustment
            self.debugPrint(f"  Moved previous offcurve: ({round(prev_node.x,1)}, {round(prev_node.y,1)})")
    
        # Check next node (if it's an offcurve connected to this curve)
        next_index = (node_index + 1) % len(nodes)
        next_node = nodes[next_index]
    
        next_type = str(getattr(next_node, 'type', '')).lower()
        if next_type == "offcurve":
            if axis == 0:
                next_node.x += adjustment
            else:
                next_node.y += adjustment
            self.debugPrint(f"  Moved next offcurve: ({round(next_node.x,1)}, {round(next_node.y,1)})")
    
    
    def applyStemCorrection(self, sender):
        """Apply stem width correction to selected glyphs using selected master"""
        font = Glyphs.font
        if not font:
            self.debugPrint("ERROR: No font open")
            return
        
        selected_layers = font.selectedLayers
        if not selected_layers:
            self.debugPrint("ERROR: No glyphs selected")
            return
        
        # Obtener el master seleccionado en el popup
        master_index = self.w.masterPopup.get()
        target_master = font.masters[master_index]
        
        self.debugPrint("="*50)
        self.debugPrint("STEM WIDTH CORRECTION STARTED")
        self.debugPrint(f"Processing master: {target_master.name}")
        
        # Get unique glyphs from selected layers
        glyphs_to_process = {}
        for layer in selected_layers:
            glyph = layer.parent
            if glyph.name not in glyphs_to_process:
                glyphs_to_process[glyph.name] = glyph
        
        self.debugPrint(f"Processing {len(glyphs_to_process)} glyphs")
        
        # Read values
        rect_min = self.getFloatValue(self.w.rectMin, 20.0)
        rect_max = self.getFloatValue(self.w.rectMax, 20.0)
        rect_new = self.getFloatValue(self.w.rectNew, 20.0)
        
        curve_min = self.getFloatValue(self.w.curveMin, 20.0)
        curve_max = self.getFloatValue(self.w.curveMax, 20.0)
        curve_new = self.getFloatValue(self.w.curveNew, 20.0)
        
        self.debugPrint(f"Rect: min={rect_min}, max={rect_max}, new={rect_new}")
        self.debugPrint(f"Curve: min={curve_min}, max={curve_max}, new={curve_new}")
        
        axis = self.w.stemAxis.get()
        axis_name = "X" if axis == 0 else "Y"
        self.debugPrint(f"Axis: {axis_name}")
        
        total_rect_pairs = 0
        total_curve_pairs = 0
        
        font.disableUpdateInterface()
        
        for glyph_name, glyph in glyphs_to_process.items():
            is_debug_glyph = (glyph_name == "a")
            
            if is_debug_glyph:
                self.debugPrint(f"\n{'='*40}")
                self.debugPrint(f"🔍 DETAILED DEBUG for glyph: {glyph_name}")
            else:
                self.debugPrint(f"\n--- Processing glyph: {glyph_name} ---")
            
            # Obtener la capa del master seleccionado
            layer = glyph.layers[target_master.id]
            
            if not layer:
                self.debugPrint(f"  No layer found for {glyph_name} in master {target_master.name}")
                continue
            
            if is_debug_glyph:
                self.debugPrint(f"\n--- RECT SECTION ---")
                self.debugPrint(f"Looking for distances between {rect_min} and {rect_max}")
            
            rect_pairs = self.findUniqueNodePairs(layer, axis, rect_min, rect_max, require_handles=False, debug=is_debug_glyph)
            
            if is_debug_glyph:
                self.debugPrint(f"\n--- CURVE SECTION ---")
                self.debugPrint(f"Looking for distances between {curve_min} and {curve_max}")
            
            curve_pairs = self.findUniqueNodePairs(layer, axis, curve_min, curve_max, require_handles=True, debug=is_debug_glyph)
            
            if not rect_pairs and not curve_pairs:
                if is_debug_glyph:
                    self.debugPrint(f"  No pairs found in {glyph_name}")
                continue
            
            glyph.beginUndo()
            
            # Adjust rect pairs
            for node1, node2, distance in rect_pairs:
                if is_debug_glyph:
                    self.debugPrint(f"\nAdjusting RECT pair: distance={round(distance,1)} -> {rect_new}")
                self.adjustNodePair(node1, node2, distance, rect_new, axis)
                total_rect_pairs += 1
            
            # Adjust curve pairs
            for node1, node2, distance in curve_pairs:
                if is_debug_glyph:
                    self.debugPrint(f"\nAdjusting CURVE pair: distance={round(distance,1)} -> {curve_new}")
                self.adjustNodePair(node1, node2, distance, curve_new, axis)
                total_curve_pairs += 1
            
            glyph.endUndo()
            
            if is_debug_glyph:
                self.debugPrint(f"\n  ✓ {glyph_name}: Rect={len(rect_pairs)} pairs, Curve={len(curve_pairs)} pairs")
            else:
                self.debugPrint(f"  ✓ {glyph_name}: Rect={len(rect_pairs)}, Curve={len(curve_pairs)}")
        
        font.enableUpdateInterface()
        
        self.debugPrint("\n" + "="*50)
        self.debugPrint(f"✅ STEM WIDTH CORRECTION COMPLETED")
        self.debugPrint(f"   • Master: {target_master.name}")
        self.debugPrint(f"   • Rect: {total_rect_pairs} pairs adjusted to {rect_new}")
        self.debugPrint(f"   • Curve: {total_curve_pairs} pairs adjusted to {curve_new}")
        self.debugPrint(f"   • Processed {len(glyphs_to_process)} glyphs")
        self.debugPrint("="*50)


# Run the script
CharacterTuner()