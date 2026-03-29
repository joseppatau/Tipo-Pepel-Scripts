# MenuTitle:Auto Metrics Keys (First Letter)
# -*- coding: utf-8 -*-
# Description: Automatically assigns metrics keys based on the first letter of each glyph name.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Set Metrics Keys from First Letter

import GlyphsApp
from vanilla import *
from AppKit import NSAlert, NSAlertStyleInformational


class SetMetricsFromFirstLetter(object):
    
    def __init__(self):
        
        self.w = FloatingWindow(
            (360, 190),
            "Auto Metrics Keys (First Letter)"
        )
        
        self.w.text = TextBox(
            (15, 15, -15, 20),
            "Assign metrics key from first letter of glyph name"
        )
        
        self.w.leftCheck = CheckBox(
            (15, 45, -15, 20),
            "Apply to Left Metrics Key",
            value=True
        )
        
        self.w.rightCheck = CheckBox(
            (15, 70, -15, 20),
            "Apply to Right Metrics Key",
            value=True
        )
        
        self.w.widthCheck = CheckBox(
            (15, 95, -15, 20),
            "Apply to Width Metrics Key",
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
        
        changedCount = 0
        
        font.disableUpdateInterface()
        
        for glyph in selectedGlyphs:
            
            glyphName = glyph.name
            
            if not glyphName or len(glyphName) == 0:
                continue
            
            firstLetter = glyphName[0]
            
            # només si és lletra
            if not firstLetter.isalpha():
                continue
            
            metricKey = "=" + firstLetter
            
            if self.w.leftCheck.get():
                glyph.leftMetricsKey = metricKey
            
            if self.w.rightCheck.get():
                glyph.rightMetricsKey = metricKey
            
            if self.w.widthCheck.get():
                glyph.widthMetricsKey = metricKey
            
            changedCount += 1
        
        font.enableUpdateInterface()
        
        
        # Confirmation dialog
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Metrics assignment completed")
        alert.setInformativeText_(
            f"{changedCount} glyphs updated."
        )
        alert.setAlertStyle_(NSAlertStyleInformational)
        alert.runModal()


SetMetricsFromFirstLetter()