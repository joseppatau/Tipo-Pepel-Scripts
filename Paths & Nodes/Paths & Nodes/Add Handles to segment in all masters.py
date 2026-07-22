# MenuTitle: Add Handles to SELECTED SEGMENT (DEBUG)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import *  # Per GSLINE, GSCORNER, etc.

class AddHandlesToSegment:
    def __init__(self):
        self.w = vanilla.FloatingWindow((250, 100), "Nanses a Segment (Debug)")
        self.w.runButton = vanilla.Button((10, 10, 120, 20), "Afegeix Nanses", callback=self.add_handles_callback)
        self.w.debugButton = vanilla.Button((140, 10, 100, 20), "Debug Info", callback=self.debug_callback)
        self.w.text = vanilla.TextBox((10, 40, -10, 50), "Selecciona AMB nodes del segment", sizeStyle='small')
        self.w.open()

    def debug_callback(self, sender):
        font = Font
        if not font or not font.selectedLayers:
            print("❌ No font/layer seleccionat")
            return
            
        layer = font.selectedLayers[0]
        print(f"\n🔍 DEBUG - Layer: {layer.name}")
        print("Nodes seleccionats:")
        
        for p_idx, path in enumerate(layer.paths):
            for n_idx, node in enumerate(path.nodes):
                if node.selected:
                    node_type = node.type
                    prev_type = node.prevNode.type if node.prevNode else "None"
                    next_type = node.nextNode.type if node.nextNode else "None"
                    print(f"  Path {p_idx}, Node {n_idx}: type='{node_type}' (prev='{prev_type}', next='{next_type}')")
        
        print("---")

    def add_handles_callback(self, sender):
        font = Font
        if font is None or not font.selectedLayers:
            return

        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent

        # TROBA SEGMENT(S) amb DEBUG
        selected_segments = []
        print("\n🔍 Analitzant paths:")
        
        for p_idx, path in enumerate(current_layer.paths):
            print(f"Path {p_idx}: {len(path.nodes)} nodes")
            nodes = path.nodes
            for i in range(len(nodes) - 1):
                node1, node2 = nodes[i], nodes[i + 1]
                print(f"  [{i}-{i+1}] sel={node1.selected and node2.selected}, types='{node1.type}:{node2.type}'")
                
                # RELAXAT: tant oncurve + oncurve, independent de tipus exacte
                if node1.selected and node2.selected and node1.type != "offcurve" and node2.type != "offcurve":
                    selected_segments.append((p_idx, i))
                    print(f"     → ✅ Segment detectat!")

        if not selected_segments:
            print("❌ Cap segment vàlid trobat.")
            self.debug_callback(None)  # Auto-debug
            return

        print(f"\n🎯 Processant {len(selected_segments)} segments...")

        # Aplicació als masters
        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                for p_idx, n1_idx in selected_segments:
                    try:
                        if p_idx >= len(layer.paths):
                            continue
                        path = layer.paths[p_idx]
                        if n1_idx + 1 >= len(path.nodes):
                            continue
                            
                        node1 = path.nodes[n1_idx]
                        node2 = path.nodes[n1_idx + 1]
                        
                        if node2.type != "offcurve":
                            p1 = node1.position
                            p2 = node2.position
                            
                            bcp1_pos = (p1.x + (p2.x - p1.x) / 3.0, p1.y + (p2.y - p1.y) / 3.0)
                            bcp2_pos = (p1.x + (p2.x - p1.x) * 2.0 / 3.0, p1.y + (p2.y - p1.y) * 2.0 / 3.0)
                            
                            bcp1 = GSNode(bcp1_pos, type="offcurve")
                            bcp2 = GSNode(bcp2_pos, type="offcurve")
                            
                            path.nodes.insert(n1_idx + 1, bcp1)
                            path.nodes.insert(n1_idx + 2, bcp2)
                            
                            node2.type = "curve"
                            node2.connection = GSCORNER
                            
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        continue
        
        if font.currentTab:
            font.currentTab.redraw()
            
        print(f"✅ Nanses afegides a {len(selected_segments)} segments!")

AddHandlesToSegment()