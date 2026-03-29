# MenuTitle: Replace Outlines From Master
# -*- coding: utf-8 -*-
# Description: Replaces or copies glyph outlines from a source master to the active master only.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla
import copy

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
        
        # Obtener el master activo actual
        self.activeMaster = self.font.selectedFontMaster
        activeMasterIndex = self.font.masters.index(self.activeMaster) if self.activeMaster else 0

        self.w = vanilla.FloatingWindow(
            (350, 200),
            "Replace Outlines From Master",
            autosaveName="com.yournamespace.replaceFromMaster"
        )

        self.w.text = vanilla.TextBox(
            (15, 15, -15, 14),
            "Source master:"
        )

        self.w.masterPopup = vanilla.PopUpButton(
            (15, 35, -15, 22),
            masterNames
        )
        
        # Mostrar el master destino (activo)
        self.w.destText = vanilla.TextBox(
            (15, 65, -15, 14),
            f"Destination master: {self.activeMaster.name if self.activeMaster else 'Active master'}"
        )

        # Checkbox para elegir entre reemplazar o poner en background
        self.w.backgroundCheckbox = vanilla.CheckBox(
            (15, 95, -15, 20),
            "Put in background (instead of replace)",
            value=False
        )

        self.w.replaceButton = vanilla.Button(
            (15, 130, -15, 30),
            "PROCESS SELECTED GLYPHS",
            callback=self.replaceGlyphs
        )

        self.w.open()

    # -----------------------------------------------------

    def replaceGlyphs(self, sender):

        targetFont = self.font
        sourceMasterIndex = self.w.masterPopup.get()
        sourceMaster = targetFont.masters[sourceMasterIndex]
        
        # Obtener el master activo como destino
        destinationMaster = self.activeMaster
        if not destinationMaster:
            Glyphs.showNotification("Replace From Master", "No active master found.")
            return
            
        putInBackground = self.w.backgroundCheckbox.get()  # True si está marcado

        selectedLayers = targetFont.selectedLayers
        if not selectedLayers:
            Glyphs.showNotification("Replace From Master", "No glyphs selected.")
            return

        # Get unique glyphs from selected layers
        glyphsToProcess = {}
        for layer in selectedLayers:
            glyph = layer.parent
            if glyph.name not in glyphsToProcess:
                glyphsToProcess[glyph.name] = glyph

        processedCount = 0
        skippedCount = 0

        for glyphName, targetGlyph in glyphsToProcess.items():
            
            sourceGlyph = targetFont.glyphs[glyphName]
            
            if not sourceGlyph:
                skippedCount += 1
                continue

            # Verificar que el glifo fuente tenga el master seleccionado
            sourceLayer = sourceGlyph.layers[sourceMaster.id]
            if not sourceLayer or not sourceLayer.shapes:
                skippedCount += 1
                continue

            targetGlyph.beginUndo()
            targetFont.disableUpdateInterface()

            # Procesar solo el master activo (destino)
            targetLayer = targetGlyph.layers[destinationMaster.id]
            
            if not targetLayer:
                skippedCount += 1
                targetFont.enableUpdateInterface()
                targetGlyph.endUndo()
                continue

            if putInBackground:
                # Poner en background
                # Limpiar background existente
                targetLayer.background = None
                
                # Crear nueva capa de background y copiar formas
                targetLayer.background = GSBackgroundLayer()
                for shape in sourceLayer.shapes:
                    targetLayer.background.shapes.append(shape.copy())
                
                # Opcional: copiar ancho al background
                targetLayer.background.width = sourceLayer.width
            else:
                # Reemplazar contornos (comportamiento original)
                # Limpiar formas existentes
                targetLayer.shapes = []

                # Copiar formas del master fuente
                for shape in sourceLayer.shapes:
                    targetLayer.shapes.append(shape.copy())

                # Copiar ancho
                targetLayer.width = sourceLayer.width

            targetGlyph.endUndo()
            processedCount += 1

        targetFont.enableUpdateInterface()

        action = "background" if putInBackground else "outlines"
        message = f"Processed: {processedCount} glyphs ({action})\nDestination: {destinationMaster.name}"
        if skippedCount > 0:
            message += f"\nSkipped: {skippedCount} glyphs"

        Glyphs.showNotification(
            "Replace From Master",
            message
        )


ReplaceFromMaster()