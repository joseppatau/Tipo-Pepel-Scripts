# MenuTitle: Create Shadows
# -*- coding: utf-8 -*-
# Description: Create Shadows
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
__doc__="""
Create Shadows"""




from GlyphsApp import *
from AppKit import NSAffineTransform
from Foundation import NSMutableArray
import objc
from vanilla import FloatingWindow, TextBox, EditText, Button

class ShadowPanel(object):
    def __init__(self):
        self.w = FloatingWindow((220, 120), "Shadow")
        self.w.tx = TextBox((15, 12, 40, 20), "ΔX:")
        self.w.ex = EditText((60, 10, 145, 24), "40")
        self.w.ty = TextBox((15, 42, 40, 20), "ΔY:")
        self.w.ey = EditText((60, 40, 145, 24), "-40")
        self.w.apply = Button((15, 74, 190, 28), "Apply to selection", callback=self.applyShadow)
        self.w.open()

    def applyShadow(self, sender):
        f = Glyphs.font
        if not f or not f.selectedLayers:
            Message("No glyph selected.", "Shadow"); return

        GSPathOperator = objc.lookUpClass("GSPathOperator")

        try:
            dx = float(self.w.ex.get())
            dy = float(self.w.ey.get())
        except:
            Message("Enter numeric values for ΔX and ΔY.", "Shadow"); return

        f.disableUpdateInterface()
        try:
            for selLayer in list(f.selectedLayers):
                g = selLayer.parent
                g.beginUndo()
                try:
                    # 1) Delete non-master layers (backups/special), keep masters
                    for L in list(g.layers):
                        if not L.isMasterLayer:
                            del g.layers[L.layerId]

                    # 2) Work on selected master (display)
                    mainLayer = g.layers[f.selectedFontMaster.id]
                    
                    mainLayer.decomposeComponents()
                    mainLayer.removeOverlap()

                    # 3) Clear existing background and create new one with original paths
                    if mainLayer.background:
                        mainLayer.background.clear()
                    
                    # Create backup copy of original shapes for the boolean operation
                    originalShapes = [shape.copy() for shape in mainLayer.shapes]
                    
                    # Create background layer
                    if mainLayer.background:
                        backgroundLayer = mainLayer.background
                    else:
                        backgroundLayer = GSLayer()
                    
                    # Clear any existing shapes in background and add copies of original shapes
                    backgroundLayer.shapes = []
                    for shape in originalShapes:
                        backgroundLayer.shapes.append(shape.copy())
                    
                    mainLayer.background = backgroundLayer

                    # 4) Offset the MAIN LAYER (visible)
                    mainLayer.applyTransform((1, 0, 0, 1, dx, dy))

                    # 5) Boolean: subtract the ORIGINAL (non-offset) shapes from the offset main layer
                    paths = NSMutableArray.array()
                    erasers = NSMutableArray.array()
                    
                    # Add offset paths from main layer
                    for shape in mainLayer.shapes:
                        if isinstance(shape, GSPath):
                            paths.addObject_(shape)
                    
                    # Add original (non-offset) shapes as erasers
                    for shape in originalShapes:
                        if isinstance(shape, GSPath):
                            erasers.addObject_(shape)

                    # Perform boolean subtraction
                    if paths.count() > 0 and erasers.count() > 0:
                        GSPathOperator.subtractPaths_from_error_(erasers, paths, None)

                    # 6) Write result to visible main layer
                    mainLayer.shapes = list(paths)
                    mainLayer.correctPathDirection()
                    mainLayer.removeOverlap()

                except Exception as e:
                    Message(f"Error: {str(e)}", "Shadow")
                finally:
                    g.endUndo()
        finally:
            f.enableUpdateInterface()

ShadowPanel()