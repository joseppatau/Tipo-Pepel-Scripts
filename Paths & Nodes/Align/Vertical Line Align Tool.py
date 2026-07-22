#MenuTitle: Vertical Line Align Tool
# -*- coding: utf-8 -*-
# Description: Detects and aligns semi-vertical node groups based on proxiApache2y and length criteria.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from GlyphsApp import Glyphs, GSNode, Message
import vanilla


class SemiVerticalDetector(object):

    def __init__(self):
        self.w = vanilla.Window((380, 200), "Vertical Line Align Tool")
        
        # Margin input
        self.w.text1 = vanilla.TextBox((15, 15, 100, 20), "Margin:")
        self.w.margin = vanilla.EditText((120, 12, 60, 22), "4")
        
        # Alignment radio buttons
        self.w.text2 = vanilla.TextBox((15, 45, 100, 20), "Align to:")
        self.w.alignment = vanilla.RadioGroup(
            (120, 42, 200, 30),
            ["Left", "Center", "Right"],
            isVertical=False
        )
        self.w.alignment.set(1)  # Center by default
        
        # Minimum length
        self.w.text3 = vanilla.TextBox((15, 75, 120, 20), "Min length:")
        self.w.minLength = vanilla.EditText((140, 72, 60, 22), "20")
        
        # Apply button
        self.w.applyButton = vanilla.Button(
            (120, 115, 140, 28),
            "Apply",
            callback=self.applyCorrection
        )
        
        self.w.open()
    
    def showMessage(self, title, message):
        """Show a message using Glyphs Message function"""
        Message(title, message)
    
    def getSelectedLayers(self):
        """Get selected layers from active master"""
        font = Glyphs.font
        if not font:
            return []
        
        layers = []
        for layer in font.selectedLayers:
            if layer:
                layers.append(layer)
        
        return layers
    
    def findNodesToAlign(self, layer, margin, min_length):
        """
        Find nodes that should be vertically aligned
        Groups nodes by X proxiApache2y
        """
        # Group nodes by X proxiApache2y
        x_groups = {}
        
        for path in layer.paths:
            for node in path.nodes:
                x = node.x
                y = node.y
                
                # Find which group this node belongs to
                found_group = False
                for group_x in list(x_groups.keys()):
                    if abs(x - group_x) <= margin:
                        x_groups[group_x].append({
                            'node': node,
                            'x': x,
                            'y': y
                        })
                        found_group = True
                        break
                
                if not found_group:
                    x_groups[x] = [{
                        'node': node,
                        'x': x,
                        'y': y
                    }]
        
        # Analyze each group
        nodes_to_align = []
        
        for group_x, nodes in x_groups.items():
            if len(nodes) < 2:
                continue
            
            # Sort by Y
            nodes.sort(key=lambda n: n['y'])
            
            # Check vertical span
            y_min = nodes[0]['y']
            y_max = nodes[-1]['y']
            y_span = y_max - y_min
            
            if y_span >= min_length:
                # This is a vertical line candidate
                nodes_to_align.append({
                    'group_x': group_x,
                    'nodes': nodes,
                    'y_span': y_span,
                    'x_values': [n['x'] for n in nodes]
                })
        
        return nodes_to_align
    
    def calculateTargetX(self, x_values, alignment):
        """Calculate target X based on alignment choice"""
        if alignment == 0:  # Left
            return min(x_values)
        elif alignment == 1:  # Center
            return sum(x_values) / len(x_values)
        else:  # Right
            return max(x_values)
    
    def applyCorrection(self, sender):
        """Apply correction to selected layers"""
        font = Glyphs.font
        if not font:
            self.showMessage("Error", "No font open")
            return
        
        # Read values
        try:
            margin = float(self.w.margin.get())
            min_length = float(self.w.minLength.get())
        except:
            self.showMessage("Error", "Please enter valid numbers")
            return
        
        alignment = self.w.alignment.get()
        alignment_names = ["Left", "Center", "Right"]
        
        # Get selected layers
        layers = self.getSelectedLayers()
        if not layers:
            self.showMessage("Error", "No layers selected")
            return
        
        # Analyze all layers
        all_candidates = []
        total_candidates = 0
        
        for layer in layers:
            candidates = self.findNodesToAlign(layer, margin, min_length)
            if candidates:
                all_candidates.append({
                    'layer': layer,
                    'candidates': candidates
                })
                total_candidates += len(candidates)
        
        if total_candidates == 0:
            self.showMessage(
                "No changes",
                f"No vertical lines found with:\n"
                f"Margin = {margin}, Min length = {min_length}"
            )
            return
        
        # Apply corrections
        changes = []
        total_corrections = 0
        
        font.disableUpdateInterface()
        
        try:
            for item in all_candidates:
                layer = item['layer']
                candidates = item['candidates']
                
                glyph_name = layer.parent.name
                layer_changes = []
                
                # Start undo for this glyph
                layer.parent.beginUndo()
                
                for candidate in candidates:
                    nodes = candidate['nodes']
                    x_values = candidate['x_values']
                    
                    # Calculate target X
                    target_x = self.calculateTargetX(x_values, alignment)
                    
                    # Apply to all nodes in this group
                    corrected_nodes = 0
                    for node_info in nodes:
                        node = node_info['node']
                        
                        if abs(node.x - target_x) > 0.01:
                            node.x = target_x
                            corrected_nodes += 1
                    
                    if corrected_nodes > 0:
                        layer_changes.append({
                            'group_x': candidate['group_x'],
                            'target_x': target_x,
                            'node_count': len(nodes),
                            'y_span': candidate['y_span']
                        })
                
                if layer_changes:
                    changes.append({
                        'glyph': glyph_name,
                        'corrections': layer_changes
                    })
                    total_corrections += len(layer_changes)
                
                # End undo for this glyph
                layer.parent.endUndo()
        
        except Exception as e:
            self.showMessage("Error", f"An error occurred: {str(e)}")
        
        finally:
            font.enableUpdateInterface()
        
        # Show results
        if total_corrections == 0:
            self.showMessage(
                "No changes",
                f"Found {total_candidates} candidates but no changes were needed"
            )
        else:
            msg = f"✅ Applied corrections to {total_corrections} vertical line(s)\n"
            msg += f"📏 Margin: {margin}, Min length: {min_length}, Alignment: {alignment_names[alignment]}\n\n"
            msg += "📋 Affected glyphs:\n"
            
            for change in changes:
                msg += f"• /{change['glyph']}: {len(change['corrections'])} line(s)\n"
                
                for corr in change['corrections'][:3]:  # Show first 3
                    msg += f"  · X≈{corr['group_x']:.1f} → {corr['target_x']:.1f} "
                    msg += f"({corr['node_count']} nodes, span={corr['y_span']:.0f})\n"
                
                if len(change['corrections']) > 3:
                    msg += f"  · ... and {len(change['corrections'])-3} more\n"
            
            self.showMessage("✅ Corrections applied", msg)


# Run the script
SemiVerticalDetector()