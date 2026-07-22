# MenuTitle: Replace Outlines From Master (with Corners)
# -*- coding: utf-8 -*-
# Description: Replaces glyph outlines and corner components from a source master to the CURRENT master.
# Author: Designed by Josep Patau Bellart, updated for Dynamic Master support.

import GlyphsApp
from GlyphsApp import GSBackgroundLayer, GSHint, CORNER
import vanilla

class ReplaceFromMaster(object):

    def __init__(self):
        self.font = Glyphs.font

        if not self.font:
            Glyphs.showNotification("Replace From Master", "No font open.")
            return

        if len(self.font.masters) < 2:
            Glyphs.showNotification("Replace From Master", "Font needs at least 2 masters.")
            return

        masterNames = [m.name for m in self.font.masters]
        
        self.w = vanilla.FloatingWindow(
            (350, 220),
            "Replace Outlines & Corners",
            autosaveName="com.pepel.replaceFromMasterCorners"
        )

        self.w.text = vanilla.TextBox((15, 15, -15, 14), "Source master:")
        self.w.masterPopup = vanilla.PopUpButton((15, 35, -15, 22), masterNames)
        
        self.w.destText = vanilla.TextBox(
            (15, 65, -15, 14), 
            "Destination: (Current Active Master)"
        )

        self.w.backgroundCheckbox = vanilla.CheckBox(
            (15, 95, -15, 20),
            "Put in background (instead of replace)",
            value=False
        )

        self.w.replaceButton = vanilla.Button(
            (15, 140, -15, 30),
            "PROCESS SELECTED GLYPHS",
            callback=self.replaceGlyphs
        )

        self.w.open()

    def copyCorners(self, sourceLayer, targetLayer):
        """Copia els corners i neteja els antics."""
        # Netejar corners previs
        for i in range(len(targetLayer.hints) - 1, -1, -1):
            if targetLayer.hints[i].type == CORNER:
                del targetLayer.hints[i]

        # Copiar corners nous
        for sourceHint in sourceLayer.hints:
            if sourceHint.type == CORNER:
                newCorner = sourceHint.copy()
                targetLayer.hints.append(newCorner)

    def replaceGlyphs(self, sender):
        # DINÀMIC: Obtenir el master actiu just en el moment del clic
        targetFont = Glyphs.font
        destinationMaster = targetFont.selectedFontMaster
        
        sourceMasterIndex = self.w.masterPopup.get()
        sourceMaster = targetFont.masters[sourceMasterIndex]
        
        if sourceMaster.id == destinationMaster.id:
            Glyphs.showNotification("Replace From Master", "Source and Destination are the same master.")
            return
            
        putInBackground = self.w.backgroundCheckbox.get()
        selectedLayers = targetFont.selectedLayers
        
        if not selectedLayers:
            Glyphs.showNotification("Replace From Master", "No glyphs selected.")
            return

        # Glifs únics de la selecció
        glyphsToProcess = {layer.parent.name: layer.parent for layer in selectedLayers}

        processedCount = 0
        targetFont.disableUpdateInterface()

        for glyphName, targetGlyph in glyphsToProcess.items():
            sourceLayer = targetGlyph.layers[sourceMaster.id]
            
            if not sourceLayer:
                continue

            targetGlyph.beginUndo()
            targetLayer = targetGlyph.layers[destinationMaster.id]
            
            if not targetLayer:
                targetGlyph.endUndo()
                continue

            if putInBackground:
                # Copiar al Background
                targetLayer.background = GSBackgroundLayer()
                for shape in sourceLayer.shapes:
                    targetLayer.background.shapes.append(shape.copy())
                self.copyCorners(sourceLayer, targetLayer.background)
                targetLayer.background.width = sourceLayer.width
            else:
                # Reemplaçar contorns principals
                targetLayer.shapes = []
                for shape in sourceLayer.shapes:
                    targetLayer.shapes.append(shape.copy())
                self.copyCorners(sourceLayer, targetLayer)
                targetLayer.width = sourceLayer.width

            targetGlyph.endUndo()
            processedCount += 1

        targetFont.enableUpdateInterface()

        # Feedback final
        action = "background" if putInBackground else "outlines + corners"
        print(f"Replace Master: {sourceMaster.name} -> {destinationMaster.name} ({processedCount} glyphs)")
        
        Glyphs.showNotification(
            "Replace From Master", 
            f"Copied to {destinationMaster.name}: {processedCount} glyphs"
        )

ReplaceFromMaster()