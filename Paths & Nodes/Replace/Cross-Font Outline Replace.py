# MenuTitle: Cross-Font Outline Replace
# -*- coding: utf-8 -*-
# Description: Replaces glyph outlines and data from another open font, supporting current or all masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla
import copy

class ReplaceOutlines(object):

    def __init__(self):

        self.font = Glyphs.font

        if not self.font:
            Glyphs.showNotification("Replace Outlines", "No font open.")
            return

        self.otherFonts = [f for f in Glyphs.fonts if f != self.font]

        if not self.otherFonts:
            Glyphs.showNotification("Replace Outlines", "No second font open.")
            return

        fontNames = [f.familyName for f in self.otherFonts]

        self.w = vanilla.FloatingWindow(
            (350, 200),
            "Replace Glyph Outlines",
            autosaveName="com.yournamespace.replaceOutlines"
        )

        self.w.text = vanilla.TextBox(
            (15, 15, -15, 14),
            "Source font:"
        )

        self.w.fontPopup = vanilla.PopUpButton(
            (15, 35, -15, 22),
            fontNames
        )

        # Radio buttons for master selection
        self.w.masterText = vanilla.TextBox(
            (15, 65, -15, 14),
            "Apply to:"
        )

        self.w.currentMasterRadio = vanilla.RadioButton(
            (15, 85, 120, 18),
            "Current Master",
            value=True,
            callback=self.radioCallback
        )

        self.w.allMastersRadio = vanilla.RadioButton(
            (140, 85, 100, 18),
            "All Masters",
            value=False,
            callback=self.radioCallback
        )

        self.w.replaceButton = vanilla.Button(
            (15, 120, -15, 30),
            "REPLACE SELECTED GLYPHS",
            callback=self.replaceGlyphs
        )

        self.w.open()
        
        # Store the current selection mode
        self.applyToAllMasters = False

    # -----------------------------------------------------
    
    def radioCallback(self, sender):
        """Update the apply mode based on radio button selection"""
        if sender == self.w.currentMasterRadio:
            self.applyToAllMasters = not self.w.currentMasterRadio.get()
        elif sender == self.w.allMastersRadio:
            self.applyToAllMasters = self.w.allMastersRadio.get()

    # -----------------------------------------------------

    def replaceGlyphs(self, sender):

        targetFont = self.font
        sourceFont = self.otherFonts[self.w.fontPopup.get()]

        selectedLayers = targetFont.selectedLayers
        if not selectedLayers:
            Glyphs.showNotification("Replace Outlines", "No glyphs selected.")
            return

        # Get unique glyph names from selected layers
        glyphNames = list(set([layer.parent.name for layer in selectedLayers]))
        
        # Check if all glyphs exist in source font
        missingGlyphs = []
        for glyphName in glyphNames:
            if not sourceFont.glyphs[glyphName]:
                missingGlyphs.append(glyphName)
        
        if missingGlyphs:
            missingList = ", ".join(missingGlyphs[:5])  # Show first 5 missing glyphs
            if len(missingGlyphs) > 5:
                missingList += f" and {len(missingGlyphs) - 5} more"
            
            Glyphs.showNotification(
                "Replace Outlines",
                f"Glyphs not found in source: {missingList}"
            )
            return

        # Check master count only if applying to all masters
        if self.applyToAllMasters and len(targetFont.masters) != len(sourceFont.masters):
            Glyphs.showNotification(
                "Replace Outlines",
                "Number of masters does not match. Use 'Current Master' mode."
            )
            return

        # Process each glyph
        successCount = 0
        failedGlyphs = []

        for glyphName in glyphNames:
            try:
                targetGlyph = targetFont.glyphs[glyphName]
                sourceGlyph = sourceFont.glyphs[glyphName]

                if self.applyToAllMasters:
                    # Replace outlines in all masters
                    targetGlyph.beginUndo()
                    for i, targetMaster in enumerate(targetFont.masters):
                        self.replaceLayer(
                            targetGlyph, 
                            sourceGlyph, 
                            targetMaster.id, 
                            sourceFont.masters[i].id
                        )
                    targetGlyph.endUndo()
                    
                else:
                    # Replace only in current master for each selected layer
                    # Group selected layers by glyph
                    layersForGlyph = [layer for layer in selectedLayers if layer.parent.name == glyphName]
                    
                    targetGlyph.beginUndo()
                    for layer in layersForGlyph:
                        currentMasterId = layer.master.id
                        
                        # Find corresponding master in source font by index
                        masterIndex = targetFont.masters.index(layer.master)
                        sourceMasterId = sourceFont.masters[masterIndex].id
                        
                        self.replaceLayer(
                            targetGlyph, 
                            sourceGlyph, 
                            currentMasterId, 
                            sourceMasterId
                        )
                    targetGlyph.endUndo()
                
                successCount += 1
                
            except Exception as e:
                failedGlyphs.append(glyphName)
                print(f"Error processing {glyphName}: {str(e)}")

        targetFont.enableUpdateInterface()

        # Show summary notification
        masterMode = "all masters" if self.applyToAllMasters else "current master(s)"
        
        if failedGlyphs:
            failedList = ", ".join(failedGlyphs[:5])
            if len(failedGlyphs) > 5:
                failedList += f" and {len(failedGlyphs) - 5} more"
            
            Glyphs.showNotification(
                "Replace Outlines - Partial Success",
                f"Replaced {successCount} glyphs in {masterMode}. Failed: {failedList}"
            )
        else:
            Glyphs.showNotification(
                "Replace Outlines - Complete",
                f"Successfully replaced {successCount} glyphs in {masterMode}."
            )
        
    # -----------------------------------------------------
    
    def replaceLayer(self, targetGlyph, sourceGlyph, targetMasterId, sourceMasterId):
        """Replace outlines, components, and anchors in a specific layer"""
        
        targetLayer = targetGlyph.layers[targetMasterId]
        sourceLayer = sourceGlyph.layers[sourceMasterId]
        
        if not sourceLayer:
            return
        
        # Clear existing shapes (paths and components)
        targetLayer.shapes = []
        
        # Deep copy shapes (paths and components)
        for shape in sourceLayer.shapes:
            newShape = shape.copy()
            targetLayer.shapes.append(newShape)
        
        # Copy anchors
        targetLayer.anchors = []
        for anchor in sourceLayer.anchors:
            newAnchor = anchor.copy()
            targetLayer.anchors.append(newAnchor)
        
        # Copy metrics
        targetLayer.width = sourceLayer.width
        targetLayer.LSB = sourceLayer.LSB  # Left side bearing
        targetLayer.RSB = sourceLayer.RSB  # Right side bearing
        
        # Copy layer color if present
        if sourceLayer.color:
            targetLayer.color = sourceLayer.color
        
        # Copy background image if present
        if sourceLayer.backgroundImage:
            targetLayer.backgroundImage = sourceLayer.backgroundImage.copy()


ReplaceOutlines()