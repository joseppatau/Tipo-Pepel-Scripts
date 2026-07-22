# MenuTitle: Assign Metrics Keys to Small Caps
# -*- coding: utf-8 -*-
# Description: Assigns metrics keys from uppercase glyphs to selected small caps glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

__doc__ = """
Floating window to assign METRICS KEYS from uppercase glyphs to selected .sc glyphs.
Example: a.sc ← A, ae.sc ← AE, aeacute.sc ← AEacute
Only processes selected glyphs.
"""

from GlyphsApp import Glyphs
from vanilla import Window, Button, TextBox

class AssignMetricsSCWindow:
    
    # Special glyphs that should NOT be converted to uppercase
    SPECIAL_GLYPHS = [
        'endash', 'emdash', 'bullet', 'currency', 'multiply', 'divide', 'notequal',
        'greater', 'less', 'greaterequal', 'lessequal', 'plusminus',
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
        'exclam', 'exclamdown', 'question', 'questiondown', 'periodcentered', 'hyphen',
        'parenleft', 'parenright', 'braceleft', 'braceright', 'bracketleft', 'bracketright',
        'quotedblleft', 'quotedblright', 'quoteleft', 'quoteright',
        'guillemetleft', 'guillemetright', 'guilsinglleft', 'guilsinglright',
        'period', 'comma', 'colon', 'semicolon', 'ellipsis',
        'quotesinglbase', 'quotedblbase', 'asterisk', 'paragraph', 'section',
        'copyright', 'registered', 'trademark', 'degree', 'bar', 'brokenbar',
        'dagger', 'daggerdbl', 'cent', 'numbersign', 'approxequal', 'asciitilde',
        'logicalnot', 'asciicircum', 'slash', 'backslash', 'quotedbl', 'quotesingle',
        'yen', 'at', 'ampersand', 'dollar', 'euro', 'sterling', 'plus', 'minus',
        'equal', 'percent', 'perthousand'
    ]
    
    # Ligatures requiring special uppercase mapping
    LIGATURES_UPPERCASE = {
        'ae': 'AE',
        'aeacute': 'AEacute',
        'oe': 'OE',
        'oeacute': 'OEacute',
        'ij': 'IJ',
        'dz': 'DZ',
        'dzacute': 'DZacute',
        'dzcaron': 'DZcaron',
        'ff': 'FF',
        'ffi': 'FFI',
        'ffl': 'FFL',
        'fi': 'FI',
        'fl': 'FL',
        'st': 'ST',
        'ct': 'CT'
    }
    
    def is_smallcap(self, name):
        return name.endswith('.sc') or name.endswith('.SC')
    
    def remove_sc_suffix(self, name):
        if name.endswith('.sc') or name.endswith('.SC'):
            return name[:-3]
        return name
    
    def get_uppercase_name(self, base_name):
        if not base_name:
            return base_name
        
        if base_name in self.LIGATURES_UPPERCASE:
            return self.LIGATURES_UPPERCASE[base_name]
        
        if base_name.isupper():
            return base_name
        
        if len(base_name) == 1 and base_name.isalpha():
            return base_name.upper()
        
        if base_name[0].isalpha():
            return base_name[0].upper() + base_name[1:]
        
        return base_name
    
    def get_original_uppercase(self, sc_name):
        base_name = self.remove_sc_suffix(sc_name)
        
        if base_name in self.SPECIAL_GLYPHS:
            return base_name
        
        return self.get_uppercase_name(base_name)
    
    def count_selected(self):
        font = Glyphs.font
        if not font:
            return "No font open"
        
        selected = font.selectedLayers
        sc = [l.parent for l in selected if l.parent and self.is_smallcap(l.parent.name)]
        
        if sc:
            return f"✓ {len(sc)} .sc glyphs selected"
        else:
            return "✗ No .sc glyphs selected"
    
    def update_counter(self, sender):
        self.w.selectionText.set(self.count_selected())
    
    def apply(self, sender):
        font = Glyphs.font
        if not font:
            print("No font open.")
            return
        
        selected = font.selectedLayers
        sc_glyphs = [l.parent for l in selected if l.parent and self.is_smallcap(l.parent.name)]
        
        if not sc_glyphs:
            print("❌ No .sc glyphs selected.")
            return
        
        count = 0
        errors = []
        
        for g_sc in sc_glyphs:
            original_name = self.get_original_uppercase(g_sc.name)
            g_original = font.glyphs[original_name]
            
            print(f"🔍 Processing: {g_sc.name} → inherits from: '{original_name}'")
            
            if not g_original:
                errors.append(f"Missing '{original_name}' for '{g_sc.name}'")
                continue
            
            modified = False
            
            for layer in g_sc.layers:
                try:
                    layer.setLeftMetricsKey_(original_name)
                    layer.setRightMetricsKey_(original_name)
                    layer.setWidthMetricsKey_(original_name)
                    modified = True
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            if modified:
                count += 1
                print(f"✅ {g_sc.name} → now inherits from '{original_name}'")
        
        print(f"\n{'='*40}")
        print(f"Updated {count} small caps glyphs")
        if errors:
            print(f"{len(errors)} errors found")
        print(f"{'='*40}")
        
        Glyphs.redraw()
    
    def close(self, sender):
        self.w.close()
    
    def __init__(self):
        self.w = Window((340, 200), "Assign Metrics Keys to Small Caps")
        
        self.w.instructions = TextBox(
            (10, 10, -10, 60),
            "Assign metrics keys to selected .sc glyphs\n"
            "• Inherit from uppercase glyphs\n"
            "• ae.sc → AE, a.sc → A\n"
            "• Will display as '=A', '=AE', etc."
        )
        
        self.w.selectionText = TextBox((10, 75, -10, 20), "Loading...")
        
        self.w.applyButton = Button((10, 110, 150, 22), "Apply", callback=self.apply)
        self.w.closeButton = Button((170, 110, 150, 22), "Close", callback=self.close)
        
        self.w.open()
        self.update_counter(None)


AssignMetricsSCWindow()