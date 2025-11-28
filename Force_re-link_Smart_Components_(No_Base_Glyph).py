# -*- coding: utf-8 -*-
# MenuTitle: Force re-link Smart Components (No Base Glyph)
# Description: Script for Glyphs App that fixes disconnected smart components.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

__doc__ = """
Script for Glyphs App that fixes disconnected smart components.
"""

from GlyphsApp import *

font = Glyphs.font
if not font:
    print("Open a font first")
else:
    fixed = 0
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if not layer.isMasterLayer: 
                continue
            
            shapes = layer.shapes
            for i in range(len(shapes) - 1, -1, -1):
                shape = shapes[i]
                if (shape.__class__.__name__ == "GSComponent" and 
                    hasattr(shape, "smartComponentValues") and 
                    shape.smartComponentValues):
                    
                    # Recreate component
                    newComp = GSComponent(shape.componentName)
                    newComp.position = shape.position
                    newComp.scale = shape.scale
                    newComp.rotation = shape.rotation
                    
                    del shapes[i]
                    shapes.append(newComp)
                    fixed += 1
    
    if font.currentTab:
        font.currentTab.redraw()
    print(f"✅ {fixed} smart components re-linked")
