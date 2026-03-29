# MenuTitle: Sync Paths with Background
# -*- coding: utf-8 -*-
# Description: Syncs foreground paths with background layer geometry, optionally copying node types and applying across masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2


from GlyphsApp import *
import vanilla

class SyncBackgroundDialog(object):
    
    def __init__(self):
        self.w = vanilla.FloatingWindow((320, 140), "Sync Paths with Background", minSize=(320, 140))
        
        # Controls
        self.w.copyTypes = vanilla.CheckBox(
            (15, 15, 250, 20),
            "Copy node type (LINE/CURVE)",
            value=False
        )
        
        self.w.onlySelectedPaths = vanilla.CheckBox(
            (15, 40, 250, 20),
            "Selected paths only",
            value=False
        )
        
        self.w.applyAllMasters = vanilla.CheckBox(
            (15, 65, 250, 20),
            "Apply to all masters",
            value=False
        )
        
        self.w.executeButton = vanilla.Button(
            (-120, 65, 100, 25),
            "Apply",
            callback=self.execute
        )
        
        self.w.closeButton = vanilla.Button(
            (-120, 40, 100, 25),
            "Cancel",
            callback=self.w.close
        )
        
        self.w.open()
    
    def execute(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            self.showAlert("Error", "Open a font and select a glyph.")
            return
        
        layer = font.selectedLayers[0]
        bg = layer.background
        
        if not bg.paths:
            self.showAlert("Error", "No paths found in background.")
            return
        
        copy_types = self.w.copyTypes.get()
        only_selected_paths = self.w.onlySelectedPaths.get()
        all_masters = self.w.applyAllMasters.get()
        
        total_paths = 0
        total_nodes = 0
        
        # Determine layers to process
        if all_masters:
            glyph = layer.parent
            layers_to_process = [glyph.layers[master.id] for master in font.masters]
        else:
            layers_to_process = [layer]
        
        for target_layer in layers_to_process:
            bg_target = target_layer.background
            if not bg_target or not bg_target.paths:
                continue
            
            # Determine path indices
            if only_selected_paths:
                path_indices = [
                    i for i, path in enumerate(target_layer.paths) if path.selected
                ]
            else:
                path_indices = range(
                    min(len(target_layer.paths), len(bg_target.paths))
                )
            
            paths_sync = 0
            
            for path_idx in path_indices:
                if path_idx >= len(bg_target.paths):
                    continue
                
                path = target_layer.paths[path_idx]
                bg_path = bg_target.paths[path_idx]
                
                min_nodes = min(len(path.nodes), len(bg_path.nodes))
                nodes_copied = 0
                
                for node_idx in range(min_nodes):
                    node = path.nodes[node_idx]
                    bg_node = bg_path.nodes[node_idx]
                    
                    node.position = bg_node.position
                    nodes_copied += 1
                    
                    # Copy node type if enabled
                    if copy_types:
                        try:
                            node.type = bg_node.type
                        except:
                            pass
                
                total_nodes += nodes_copied
                paths_sync += 1
            
            total_paths += paths_sync
        
        # Result message
        master_text = "all masters" if all_masters else "current master"
        
        self.showAlert(
            "Completed",
            f"Synchronized {total_paths} paths and {total_nodes} nodes in {master_text}."
        )
        
        font.parent.redraw()
        self.w.close()
    
    def showAlert(self, title, message):
        alert = vanilla.Alert(title, message, vanilla.OK)
        alert.show()


# Run dialog
SyncBackgroundDialog()