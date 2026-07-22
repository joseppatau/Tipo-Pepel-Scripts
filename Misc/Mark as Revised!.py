# MenuTitle: Mark as Revised!
# Josep Patau Bellart / ChatGPT
# Alineació basada en la mètrica. Neteja el background abans d'actuar.

from GlyphsApp import Glyphs
from vanilla import FloatingWindow, Button

class RevisedTool(object):
    def __init__(self):
        self.w = FloatingWindow((150, 60), "Revised!")
        self.w.btn = Button((10, 10, -10, -10), "Revised! ✅", callback=self.markAsRevised)
        self.w.open()

    def markAsRevised(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            return

        stamp_name = "check" # El teu glif de referència
        
        if not font.glyphs[stamp_name]:
            Glyphs.showNotification("Revised Tool", f"Error: No s'ha trobat el glif '{stamp_name}'.")
            return
        
        font.disableUpdateInterface()
        
        try:
            for current_layer in font.selectedLayers:
                master_id = current_layer.associatedMasterId
                
                # 1. Obtenir la capa del segell
                stamp_layer = font.glyphs[stamp_name].layers[master_id]
                if not stamp_layer: continue

                # 2. NETEJAR BACKGROUND (Evita que s'acumulin paths amagats)
                current_layer.background.clear()

                # 3. CÀLCUL DE L'OFFSET X
                offset_x = (current_layer.width - stamp_layer.width) / 2.0

                # 4. Copiar i moure camins
                for path in stamp_layer.paths:
                    new_path = path.copy()
                    for node in new_path.nodes:
                        node.x += offset_x
                    current_layer.background.paths.append(new_path)
                
                # 5. Copiar i moure components
                for component in stamp_layer.components:
                    new_comp = component.copy()
                    new_comp.x += offset_x
                    current_layer.background.components.append(new_comp)
                
            print(f"✅ Revised! Background actualitzat i centrat (sense color).")
            
        except Exception as e:
            print(f"Error: {e}")
        
        font.enableUpdateInterface()
        
        # Refrescar la vista
        if hasattr(Glyphs, "redraw"):
            Glyphs.redraw()

RevisedTool()