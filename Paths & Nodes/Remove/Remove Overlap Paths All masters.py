# MenuTitle: Remove Overlap Paths All masters
# -*- coding: utf-8 -*-

import vanilla

class RemoveOverlapSelectedOnly:
    def __init__(self):
        self.w = vanilla.FloatingWindow((250, 85), "Overlap Segments")
        self.w.runButton = vanilla.Button((10, 10, -10, 25), "Remove Overlap Selecció", callback=self.remove_overlap_callback)
        self.w.text = vanilla.TextBox((10, 45, -10, 35), "Processa només els segments seleccionats a cada màster.", sizeStyle='small')
        self.w.open()

    def remove_overlap_callback(self, sender):
        font = Font
        if font is None or not font.selectedLayers:
            return

        current_layer = font.selectedLayers[0]
        glyph = current_layer.parent
        
        # Guardem quins segments estan seleccionats (per índex de node)
        selected_nodes_map = []
        for p_idx, path in enumerate(current_layer.paths):
            for n_idx, node in enumerate(path.nodes):
                if node.selected:
                    selected_nodes_map.append((p_idx, n_idx))
        
        if not selected_nodes_map:
            print("Error: No has seleccionat cap segment.")
            return

        glyph.beginUndo()

        for layer in glyph.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                # Per a cada màster, seleccionem els mateixos nodes 
                # abans d'executar l'operador de camins
                layer.selection = None # Netejem selecció prèvia al màster
                
                for p_idx, n_idx in selected_nodes_map:
                    try:
                        layer.paths[p_idx].nodes[n_idx].selected = True
                    except:
                        pass
                
                # Usem l'operació específica de selecció
                # GSPathOperator.removeOverlap_fromLayer_error_(selectionOnly, layer, error)
                try:
                    # En Glyphs 3, el mètode removeOverlap té un paràmetre booleà
                    # per indicar si es vol fer només a la selecció.
                    layer.removeOverlap(True) 
                except Exception as e:
                    print(f"Error al màster {layer.name}: {e}")

        glyph.endUndo()
        
        if font.currentTab:
            font.currentTab.redraw()
            
        print("Fet! Overlap corregit només en la selecció a tots els màsters.")

RemoveOverlapSelectedOnly()