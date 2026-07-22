# MenuTitle: Duplicate Selected Paths to Masters

import vanilla
import traceback
from GlyphsApp import Glyphs, Message
from AppKit import NSFont, NSAttributedString, NSFontAttributeName


class DuplicatePathsToMasters:
    
    def __init__(self):
        self.setupUI()
    
    def setupUI(self):
        self.w = vanilla.FloatingWindow((380, 240), "Duplicate Selected Paths to Masters")
        
        y = 10
        
        self.w.infoText = vanilla.TextBox(
            (15, y, -10, 40),
            "Select nodes or paths in Edit view,\nthen duplicate ONLY those paths to all masters.",
            sizeStyle="small"
        )
        y += 50
        
        self.w.replaceCheck = vanilla.CheckBox(
            (15, y, -10, 20),
            "Replace existing paths in target masters (⚠️ careful)",
            value=False
        )
        y += 30
        
        self.w.copyMetricsCheck = vanilla.CheckBox(
            (15, y, -10, 20),
            "Copy metrics (LSB, RSB, width)",
            value=False
        )
        y += 30
        
        self.w.duplicateButton = vanilla.Button(
            (15, y, -15, 30),
            "Duplicate Selected Paths",
            callback=self.duplicatePaths
        )
        
        try:
            button_title = NSAttributedString.alloc().initWithString_attributes_(
                "Duplicate Selected Paths",
                {NSFontAttributeName: NSFont.boldSystemFontOfSize_(NSFont.systemFontSize())}
            )
            self.w.duplicateButton.getNSButton().setAttributedTitle_(button_title)
        except:
            pass
        
        y += 45
        
        self.w.statusText = vanilla.TextBox(
            (15, y, -10, 40),
            "Ready",
            sizeStyle="small"
        )
        
        self.w.open()
    
    def duplicatePaths(self, sender):
        font = Glyphs.font
        
        if not font:
            Message("Error", "No font open.", OKButton="OK")
            return
        
        selected_layers = font.selectedLayers
        
        if not selected_layers:
            Message("Info", "Select at least one glyph.", OKButton="OK")
            return
        
        masters = font.masters
        
        replace = self.w.replaceCheck.get()
        copy_metrics = self.w.copyMetricsCheck.get()
        
        font.disableUpdateInterface()
        
        try:
            for layer in selected_layers:
                glyph = layer.parent
                if not glyph:
                    continue
                
                source_layer = layer
                source_master_id = layer.associatedMasterId
                
                # 🔥 DETECTAR PATHS SELECCIONATS (robust)
                source_paths = []
                
                for path in source_layer.paths:
                    
                    if path.selected:
                        source_paths.append(path)
                        continue
                    
                    for node in path.nodes:
                        if node.selected:
                            source_paths.append(path)
                            break
                
                if not source_paths:
                    print(f"⚠️ No selected paths in '{glyph.name}'")
                    continue
                
                print(f"✔ {glyph.name}: {len(source_paths)} selected paths")
                
                # Mètriques
                source_lsb = source_layer.LSB
                source_rsb = source_layer.RSB
                source_width = source_layer.width
                
                for master in masters:
                    
                    if master.id == source_master_id:
                        continue
                    
                    target_layer = glyph.layers[master.id]
                    
                    try:
                        # ⚠️ Replace (perillós amb selecció parcial)
                        if replace:
                            print(f"⚠️ Replacing ALL paths in {glyph.name} / {master.name}")
                            for p in list(target_layer.paths):
                                target_layer.removePath_(p)
                        
                        # Copiar paths seleccionats
                        for path in source_paths:
                            new_path = path.copy()
                            target_layer.paths.append(new_path)
                        
                        # Mètriques
                        if copy_metrics:
                            target_layer.LSB = source_lsb
                            target_layer.RSB = source_rsb
                            target_layer.width = source_width
                    
                    except Exception as e:
                        print(f"❌ Error in {glyph.name} / {master.name}: {e}")
                        traceback.print_exc()
            
            self.w.statusText.set("✅ Done")
            print("=== DONE ===")
        
        finally:
            font.enableUpdateInterface()


DuplicatePathsToMasters()