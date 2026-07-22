# MenuTitle: Assign Metrics to Small Caps in all masters
# -*- coding: utf-8 -*-
from GlyphsApp import *
from GlyphsApp.UI import *
from vanilla import *

class AssignMetricsToSC(object):
    def __init__(self):
        self.w = FloatingWindow((350, 170), "Assign Metrics Keys to .sc")
        
        self.w.text_desc = TextBox((15, 12, 320, 40), 
            "Copies LSB and RSB from base glyphs to selected .sc glyphs.\n"
            "Base: a → A, aacute → Aacute, ae → AE, oe → OE, zero → zero", sizeStyle='small')
        
        self.w.apply_all_masters = CheckBox((15, 55, 200, 20), 
            "Apply to all masters", 
            value=True,
            callback=self.toggle_masters)
        
        self.w.run_btn = Button((15, 90, 320, 30), "Apply to Selected Glyphs", 
            callback=self.apply_to_selected)
        
        self.w.setDefaultButton(self.w.run_btn)
        self.w.center()
        self.w.open()
    
    def toggle_masters(self, sender):
        pass
    
    def get_base_glyph_name(self, sc_name):
        """Converteix nom .sc a nom base"""
        if not sc_name.endswith('.sc'):
            return None
        
        base = sc_name[:-3]  # Treu .sc
        
        # Excepcions especials
        if base == 'ae':
            return 'AE', base
        elif base == 'oe':
            return 'OE', base
        
        # Per la resta: prova amb capitalize
        capitalized = base.capitalize()
        return capitalized, base
    
    def apply_to_selected(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No font open")
            return
        
        selected_glyphs = [layer.parent for layer in font.selectedLayers]
        if not selected_glyphs:
            print("❌ No glyphs selected")
            return
        
        sc_glyphs = [g for g in selected_glyphs if g.name.endswith('.sc')]
        if not sc_glyphs:
            print("❌ No .sc glyphs in selection")
            return
        
        apply_to_all = self.w.apply_all_masters.get()
        copied_count = 0
        skipped_count = 0
        
        font.disableUpdateInterface()
        
        for sc_glyph in sc_glyphs:
            sc_name = sc_glyph.name
            capitalized, original = self.get_base_glyph_name(sc_name)
            
            # Buscar glif base
            base_glyph = None
            base_name_used = None
            
            if capitalized in font.glyphs:
                base_glyph = font.glyphs[capitalized]
                base_name_used = capitalized
            elif original in font.glyphs:
                base_glyph = font.glyphs[original]
                base_name_used = original
            
            if base_glyph:
                if apply_to_all:
                    # Aplicar a tots els masters
                    for master in font.masters:
                        sc_layer = sc_glyph.layers[master.id]
                        base_layer = base_glyph.layers[master.id]
                        if sc_layer and base_layer:
                            sc_layer.LSB = base_layer.LSB
                            sc_layer.RSB = base_layer.RSB
                    print(f"✅ {sc_name} ← {base_name_used} (applied to {len(font.masters)} masters)")
                else:
                    # Aplicar només al master actiu
                    current_master = font.selectedFontMaster
                    sc_layer = sc_glyph.layers[current_master.id]
                    base_layer = base_glyph.layers[current_master.id]
                    if sc_layer and base_layer:
                        sc_layer.LSB = base_layer.LSB
                        sc_layer.RSB = base_layer.RSB
                    print(f"✅ {sc_name} ← {base_name_used} (current master only: {current_master.name})")
                
                copied_count += 1
            else:
                print(f"⚠️ {sc_name}: base glyph not found (tried: {capitalized}, {original})")
                skipped_count += 1
        
        font.enableUpdateInterface()
        
        # Missatge final
        mode = "all masters" if apply_to_all else "current master only"
        message = f"Done!\nCopied metrics keys to: {copied_count} glyphs\nSkipped: {skipped_count} glyphs\nMode: {mode}"
        print(message)
        
        # Alert amb NSAlert
        alert = NSAlert.alloc().init()
        alert.setMessageText_(message)
        alert.addButtonWithTitle_("OK")
        alert.runModal()
        
        self.w.close()

# Executar
if __name__ == "__main__":
    AssignMetricsToSC()