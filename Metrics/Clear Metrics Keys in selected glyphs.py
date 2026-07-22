# MenuTitle: Clear Metrics Keys in selected glyphs
# -*- coding: utf-8 -*-
# Description: Removes metrics keys from selected glyphs and/or their master layers.
# Author: Designed by Josep Patau Bellart & Gemini

import GlyphsApp
from vanilla import *
from AppKit import NSAlert, NSAlertStyleInformational

class ClearMetricsKeys(object):
    
    def __init__(self):
        self.w = FloatingWindow((380, 210), "Clear Metrics Keys")
        
        self.w.text = TextBox((15, 15, -15, 20), "Glyph references to remove (comma separated):")
        self.w.input = EditText((15, 40, -15, 24), "H, O")
        
        self.w.removeAll = CheckBox((15, 75, -15, 20), "Remove ALL metrics keys", value=False)
        
        # Nou Checkbox per aplicar a tots els mestres
        self.w.allMasters = CheckBox((15, 100, -15, 20), "Apply to all masters (Layers)", value=True)
        
        self.w.runButton = Button((-110, -45, -15, -10), "Run", callback=self.run)
        
        self.w.open()
    
    def removeKeyFromObject(self, obj, targets, removeAll):
        """Funció interna per netejar claus d'un objecte (glif o capa)."""
        removed = 0
        for keyName in ["leftMetricsKey", "rightMetricsKey", "widthMetricsKey"]:
            keyValue = getattr(obj, keyName)
            if not keyValue:
                continue
            
            shouldRemove = False
            if removeAll:
                shouldRemove = True
            else:
                for target in targets:
                    if target in str(keyValue):
                        shouldRemove = True
                        break
            
            if shouldRemove:
                setattr(obj, keyName, None)
                removed += 1
        return removed

    def run(self, sender):
        font = Glyphs.font
        if not font:
            return
        
        selectedGlyphs = list(set([layer.parent for layer in font.selectedLayers]))
        if not selectedGlyphs:
            return
        
        inputText = self.w.input.get()
        targets = [x.strip() for x in inputText.split(",") if x.strip()]
        removeAll = self.w.removeAll.get()
        allMasters = self.w.allMasters.get()
        
        removedCount = 0
        font.disableUpdateInterface()
        
        try:
            for glyph in selectedGlyphs:
                # 1. Esborrar del Glif (Global)
                removedCount += self.removeKeyFromObject(glyph, targets, removeAll)
                
                # 2. Esborrar de les Capes (Mestres) si està activat
                if allMasters:
                    for layer in glyph.layers:
                        # Només actuem sobre capes de mestre o especials
                        if layer.isMasterLayer or layer.isSpecialLayer:
                            removedCount += self.removeKeyFromObject(layer, targets, removeAll)
        finally:
            font.enableUpdateInterface()
        
        # Diàleg de confirmació
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Metrics cleanup completed")
        alert.setInformativeText_(
            f"S'han eliminat {removedCount} claus de mètrica.\n"
            f"{len(selectedGlyphs)} glifs processats."
        )
        alert.setAlertStyle_(NSAlertStyleInformational)
        alert.runModal()

ClearMetricsKeys()