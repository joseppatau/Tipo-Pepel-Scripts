#MenuTitle: Kerning Groups from Name
# -*- coding: utf-8 -*-
# Description: Assigns left and right kerning groups based on glyph names across selected glyphs or the entire font.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from GlyphsApp import *
from vanilla import *
from AppKit import NSFloatingWindowLevel
import traceback

class SetKerningGroupsFromProductionNames(object):
    
    def __init__(self):
        print("=" * 50)
        print("INITIALIZING SCRIPT")
        print("=" * 50)
        
        self.w = Window((280, 120), "Kerning Groups from Name", minSize=(250, 100))
        self.w._window.setLevel_(NSFloatingWindowLevel)
        
        self.w.text = TextBox((10, 10, -10, 20), "Apply to:")
        
        self.w.radio = RadioGroup(
            (10, 30, -10, 40), 
            ["Selected Characters", "Entire Font"],
            isVertical=False,
            sizeStyle='regular'
        )
        self.w.radio.set(0)  # Default to Selected Characters
        
        self.w.applyButton = Button(
            (10, 80, -10, 24),
            "Apply Kerning Groups",
            callback=self.applyKerningGroups
        )
        
        self.w.open()
        self.w.makeKey()
        print("Window opened")
    
    def getGlyphName(self, glyph):
        """
        Devuelve el nombre que se usará como grupo de kern.
        Ahora mismo usa glyph.name, si quieres usar production
        podemos cambiar esta función.
        """
        name = glyph.name
        print(f"  Glyph name (for groups): {name}")
        return name
    
    def setKerningGroup(self, glyph, groupName, side):
        """Set kerning group on the glyph object (left/right)."""
        try:
            print(f"    Attempting to set {side} group to: {groupName}")
            
            if side == 'left':
                glyph.leftKerningGroup = groupName
                print(f"    ✓ Set left group to: {groupName}")
            elif side == 'right':
                glyph.rightKerningGroup = groupName
                print(f"    ✓ Set right group to: {groupName}")
            
            return True
            
        except Exception as e:
            print(f"    ✗ Error setting {side} group: {e}")
            traceback.print_exc()
            return False
    
    def getCurrentKerningGroups(self, glyph):
        """Get current kerning groups from the glyph."""
        try:
            left = glyph.leftKerningGroup
            right = glyph.rightKerningGroup
            return left, right
        except Exception as e:
            print(f"    ✗ Error getting current groups: {e}")
            return None, None
    
    def debug_layer_info(self, layer, layer_index):
        """Solo info de depuración de la layer."""
        print(f"    Layer {layer_index}:")
        print(f"      Type: {type(layer)}")
        print(f"      Name: {getattr(layer, 'name', 'N/A')}")
        print(f"      LayerId: {getattr(layer, 'layerId', 'N/A')}")
        print(f"      Has parent: {hasattr(layer, 'parent') and bool(layer.parent)}")
    
    def applyKerningGroups(self, sender):
        """Main function to apply kerning groups"""
        print("\n" + "=" * 50)
        print("APPLY KERNING GROUPS CALLED")
        print("=" * 50)
        
        font = Glyphs.font
        if not font:
            print("ERROR: No font open")
            Message("No font open", "Please open a font first.")
            return
        
        print(f"Font: {font.familyName}")
        
        # Get selected option
        applyToEntireFont = self.w.radio.get() == 1
        print(f"Apply to entire font: {applyToEntireFont}")
        
        # Collect glyphs to process
        glyphsToProcess = []
        
        if applyToEntireFont:
            glyphsToProcess = [glyph for glyph in font.glyphs]
            print(f"Processing entire font: {len(glyphsToProcess)} glyphs")
        else:
            selectedLayers = font.selectedLayers
            print(f"SELECTED LAYERS: {len(selectedLayers)}")
            
            for i, layer in enumerate(selectedLayers):
                print(f"\n  Selected layer {i}:")
                print(f"    Layer object: {layer}")
                print(f"    Layer type: {type(layer)}")
                print(f"    Has parent: {hasattr(layer, 'parent')}")
                
                if hasattr(layer, 'parent') and layer.parent:
                    glyph = layer.parent
                    print(f"    Parent glyph: {glyph.name}")
                    
                    if glyph not in glyphsToProcess:
                        glyphsToProcess.append(glyph)
                        print(f"    ✓ Added glyph to process list")
                    else:
                        print(f"    - Glyph already in list")
                else:
                    print(f"    ✗ No parent glyph found")
        
        print(f"\nGlyphs to process: {len(glyphsToProcess)}")
        for g in glyphsToProcess:
            print(f"  - {g.name}")
        
        if not glyphsToProcess:
            print("ERROR: No glyphs to process")
            Message("No glyphs selected", "Please select at least one glyph or choose 'Entire Font'.")
            return
        
        modifiedCount = 0
        
        for glyph_index, glyph in enumerate(glyphsToProcess):
            print("\n" + "-" * 40)
            print(f"Processing glyph {glyph_index + 1}/{len(glyphsToProcess)}: {glyph.name}")
            print("-" * 40)
            
            glyphName = self.getGlyphName(glyph)
            glyphModified = False
            
            print(f"  Layers count: {len(glyph.layers)}")
            for layer_index, layer in enumerate(glyph.layers):
                print(f"\n  --- Layer {layer_index} ---")
                self.debug_layer_info(layer, layer_index)
            
            # Grupos actuales (en el glyph, no en la layer)
            current_left, current_right = self.getCurrentKerningGroups(glyph)
            print(f"  Current left group: {current_left}")
            print(f"  Current right group: {current_right}")
            
            # Set left kerning group if different
            if current_left != glyphName:
                print(f"  Setting left group from '{current_left}' to '{glyphName}'")
                if self.setKerningGroup(glyph, glyphName, 'left'):
                    glyphModified = True
            else:
                print(f"  Left group already correct: '{current_left}'")
            
            # Set right kerning group if different
            if current_right != glyphName:
                print(f"  Setting right group from '{current_right}' to '{glyphName}'")
                if self.setKerningGroup(glyph, glyphName, 'right'):
                    glyphModified = True
            else:
                print(f"  Right group already correct: '{current_right}'")
            
            if glyphModified:
                modifiedCount += 1
                print(f"\n  ✓ Glyph {glyph.name} modified")
            else:
                print(f"\n  - No changes made to {glyph.name}")
        
        scope = "entire font" if applyToEntireFont else "selected glyphs"
        result_message = f"Applied glyph names to kerning groups for {modifiedCount} glyphs in {scope}."
        
        print("\n" + "=" * 50)
        print(f"RESULT: {result_message}")
        print("=" * 50)
        
        Message("Kerning Groups Updated", result_message)
        
        self.w.close()

# Run the script
print("\n" + "=" * 50)
print("STARTING SCRIPT")
print("=" * 50)
SetKerningGroupsFromProductionNames()
