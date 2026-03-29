# MenuTitle: Clear Metrics Keys
# -*- coding: utf-8 -*-
# Description: Removes metrics keys from selected glyphs, either selectively or completely.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Clear Metrics Keys (Advanced)

import GlyphsApp
from vanilla import *
from AppKit import NSAlert, NSAlertStyleInformational


class ClearMetricsKeys(object):
    
    def __init__(self):
        
        self.w = FloatingWindow(
            (380, 170),
            "Clear Metrics Keys"
        )
        
        self.w.text = TextBox(
            (15, 15, -15, 20),
            "Glyph references to remove (comma separated):"
        )
        
        self.w.input = EditText(
            (15, 40, -15, 24),
            "H,O"
        )
        
        self.w.removeAll = CheckBox(
            (15, 75, -15, 20),
            "Remove ALL metrics keys from selected glyphs",
            value=False
        )
        
        self.w.runButton = Button(
            (-110, -35, -15, -10),
            "Run",
            callback=self.run
        )
        
        self.w.open()
    
    
    def run(self, sender):
        
        font = Glyphs.font
        if not font:
            return
        
        selectedGlyphs = list(set([layer.parent for layer in font.selectedLayers]))
        if not selectedGlyphs:
            return
        
        inputText = self.w.input.get()
        targets = [x.strip() for x in inputText.split(",") if x.strip()]
        
        removedCount = 0
        
        font.disableUpdateInterface()
        
        for glyph in selectedGlyphs:
            
            for keyName in ["leftMetricsKey", "rightMetricsKey", "widthMetricsKey"]:
                
                keyValue = getattr(glyph, keyName)
                if not keyValue:
                    continue
                
                # Remove all keys option
                if self.w.removeAll.get():
                    setattr(glyph, keyName, None)
                    removedCount += 1
                    continue
                
                # Selective removal
                for target in targets:
                    if target in keyValue:
                        setattr(glyph, keyName, None)
                        removedCount += 1
                        break
        
        font.enableUpdateInterface()
        
        
        # Confirmation dialog
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Metrics cleanup completed")
        alert.setInformativeText_(
            f"{removedCount} metrics keys removed\n"
            f"{len(selectedGlyphs)} glyphs processed."
        )
        alert.setAlertStyle_(NSAlertStyleInformational)
        alert.runModal()


ClearMetricsKeys()