# MenuTitle:Copy Metrics to Multiple Masters
# -*- coding: utf-8 -*-
# Description: Copies selected metrics (LSB, RSB, width) from the active master to multiple target masters across selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Copia mètriques a masters seleccionats
# -*- coding: utf-8 -*-
# Description: Apply equidistant nodes and roughness effects to glyphs
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import FloatingWindow, Button, TextBox, CheckBox, PopUpButton, EditText, ScrollView, List, Group, TextEditor
import vanilla


class CopyMetricsToMasters(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("Error", "Obre un fitxer de font primer")
            return

        # Llistat de tots els masters
        self.all_masters = self.font.masters
        self.master_names = [master.name for master in self.all_masters]
        self.master_ids = [master.id for master in self.all_masters]
        
        # Master actiu (origen)
        self.active_master_index = None
        for i, master in enumerate(self.all_masters):
            if master.id == self.font.selectedFontMaster.id:
                self.active_master_index = i
                break
        
        # Estat dels checkboxes per als masters
        self.master_checkboxes = []
        self.master_checkbox_states = [i != self.active_master_index for i in range(len(self.all_masters))]
        
        # Àmbit d'aplicació: 
        # 0 = Current glyph, 1 = Selected glyphs, 2 = All glyphs
        self.scope_value = 1  # Per defecte: selected glyphs

        self.w = FloatingWindow((380, 780), "Copia mètriques")

        self.w.descText = TextBox(
            (10, 10, -10, 20),
            f"Master origen: {self.master_names[self.active_master_index]}"
        )

        # Llista de masters amb checkboxes utilitzant List
        self.w.mastersLabel = TextBox(
            (10, 40, -10, 20),
            "Masters destí:"
        )
        
        # Crear dades per la llista
        self.master_items = []
        for i, master_name in enumerate(self.master_names):
            if i == self.active_master_index:
                self.master_items.append({
                    "name": f"{master_name} (origen - no seleccionable)",
                    "selected": False,
                    "index": i
                })
            else:
                self.master_items.append({
                    "name": master_name,
                    "selected": self.master_checkbox_states[i],
                    "index": i
                })
        
        # Llista amb checkboxes
        self.w.mastersList = List(
            (10, 60, 360, 420),
            self.master_items,
            columnDescriptions=[
                {"title": "Selecciona", "key": "selected", "width": 70, "cell": vanilla.CheckBoxListCell()},
                {"title": "Master", "key": "name", "width": 270}
            ]
        )
        
        # Botons de Select All i Deselect All
        self.w.selectAllButton = Button(
            (10, 485, 120, 22),
            "Seleccionar tot",
            callback=self.selectAllCallback
        )
        
        self.w.deselectAllButton = Button(
            (140, 485, 150, 22),
            "Desseleccionar tot",
            callback=self.deselectAllCallback
        )
        
        # Separador
        self.w.scopeLabel = TextBox(
            (10, 520, -10, 20),
            "Àmbit d'aplicació:"
        )
        
        # Radio buttons per a l'àmbit (simulats amb CheckBox)
        self.w.currentGlyphRadio = CheckBox(
            (20, 540, 150, 20),
            "Current glyph",
            value=False,
            callback=self.scopeRadioCallback,
            sizeStyle="small"
        )
        
        self.w.selectedGlyphsRadio = CheckBox(
            (20, 560, 150, 20),
            "Selected glyphs",
            value=True,
            callback=self.scopeRadioCallback,
            sizeStyle="small"
        )
        
        self.w.allGlyphsRadio = CheckBox(
            (20, 580, 150, 20),
            "All glyphs",
            value=False,
            callback=self.scopeRadioCallback,
            sizeStyle="small"
        )
        
        # Opcions de mètriques
        self.w.metricsLabel = TextBox(
            (10, 610, -10, 20),
            "Mètriques a copiar:"
        )
        
        self.w.copyLSB = CheckBox((20, 630, 80, 20), "LSB", value=True, sizeStyle="small")
        self.w.copyRSB = CheckBox((110, 630, 80, 20), "RSB", value=True, sizeStyle="small")
        self.w.copyWidth = CheckBox((200, 630, 80, 20), "Width", value=True, sizeStyle="small")

        # Botó de còpia
        self.w.copyButton = Button(
            (10, 670, -10, 30),
            "Copia mètriques",
            callback=self.copyMetricsCallback
        )

        self.w.open()

    # -----------------------------------------------------
    
    def selectAllCallback(self, sender):
        """Seleccionar tots els masters destí"""
        items = self.w.mastersList.get()
        for i, item in enumerate(items):
            if i != self.active_master_index:  # No seleccionar el master origen
                item["selected"] = True
        self.w.mastersList.set(items)
    
    # -----------------------------------------------------
    
    def deselectAllCallback(self, sender):
        """Desseleccionar tots els masters destí"""
        items = self.w.mastersList.get()
        for i, item in enumerate(items):
            if i != self.active_master_index:  # No desseleccionar el master origen (ja ho està)
                item["selected"] = False
        self.w.mastersList.set(items)
    
    # -----------------------------------------------------
    
    def scopeRadioCallback(self, sender):
        """Gestionar els radio buttons de l'àmbit"""
        if sender == self.w.currentGlyphRadio and sender.get():
            self.scope_value = 0
            self.w.selectedGlyphsRadio.set(False)
            self.w.allGlyphsRadio.set(False)
        elif sender == self.w.selectedGlyphsRadio and sender.get():
            self.scope_value = 1
            self.w.currentGlyphRadio.set(False)
            self.w.allGlyphsRadio.set(False)
        elif sender == self.w.allGlyphsRadio and sender.get():
            self.scope_value = 2
            self.w.currentGlyphRadio.set(False)
            self.w.selectedGlyphsRadio.set(False)
    
    # -----------------------------------------------------

    def copyMetricsCallback(self, sender):
        font = Glyphs.font
        if not font:
            Message("Error", "Obre un fitxer de font primer")
            return

        # Master d'origen (el que està actiu)
        source_master_id = font.selectedFontMaster.id
        source_master_name = font.selectedFontMaster.name

        # Obtenir els masters seleccionats de la llista
        list_items = self.w.mastersList.get()
        selected_dest_ids = []
        selected_dest_names = []
        
        for i, item in enumerate(list_items):
            # El master origen no es pot seleccionar (el checkbox està deshabilitat visualment)
            if i != self.active_master_index and item["selected"]:
                # Netejar el nom si té el text "(origen - no seleccionable)"
                name = item["name"]
                if " (origen - no seleccionable)" in name:
                    name = name.replace(" (origen - no seleccionable)", "")
                
                selected_dest_ids.append(self.master_ids[i])
                selected_dest_names.append(name)

        if not selected_dest_ids:
            Message("Error", "Selecciona com a mínim un master de destí")
            return

        # Quines mètriques copiar?
        copyLSB = self.w.copyLSB.get()
        copyRSB = self.w.copyRSB.get()
        copyWidth = self.w.copyWidth.get()

        if not (copyLSB or copyRSB or copyWidth):
            Message("Error", "Selecciona quina mètrica copiar")
            return

        # Determinar quins glifos processar segons l'àmbit seleccionat
        glyphs_to_process = []
        
        if self.scope_value == 0:  # Current glyph
            selectedLayers = font.selectedLayers
            if not selectedLayers:
                Message("Error", "Selecciona un glif")
                return
            # Agafar el primer glif seleccionat (current glyph)
            if selectedLayers[0].parent:
                glyphs_to_process = [selectedLayers[0].parent.name]
            else:
                Message("Error", "No s'ha pogut identificar el glif actual")
                return
                
        elif self.scope_value == 1:  # Selected glyphs
            selectedLayers = font.selectedLayers
            if not selectedLayers:
                Message("Error", "Selecciona com a mínim un glif")
                return
            # Agafar tots els glifs seleccionats (únics)
            glyphs_to_process = list(set([layer.parent.name for layer in selectedLayers if layer.parent]))
            
        else:  # All glyphs
            glyphs_to_process = [glyph.name for glyph in font.glyphs]

        if not glyphs_to_process:
            Message("Error", "No s'han trobat glifs per processar")
            return

        # Per cada glif processar
        total_copies = 0
        processed_glyphs = 0
        
        font.disableUpdateInterface()
        
        for glyphName in glyphs_to_process:
            glyph = font.glyphs[glyphName]
            if not glyph:
                continue

            # Capa d'origen (master actiu)
            sourceLayer = glyph.layers[source_master_id]
            
            glyph.beginUndo()
            glyph_updated = False

            # Per cada master de destí seleccionat
            for dest_master_id in selected_dest_ids:
                # No copiar al mateix master
                if dest_master_id == source_master_id:
                    continue
                    
                targetLayer = glyph.layers[dest_master_id]

                # Copiar mètriques seleccionades
                if copyLSB:
                    targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
                    targetLayer.LSB = sourceLayer.LSB
                    glyph_updated = True
                
                if copyRSB:
                    targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
                    targetLayer.RSB = sourceLayer.RSB
                    glyph_updated = True
                
                if copyWidth:
                    targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey
                    targetLayer.width = sourceLayer.width
                    glyph_updated = True

            if glyph_updated:
                total_copies += len(selected_dest_ids)
                processed_glyphs += 1
            
            glyph.endUndo()

        font.enableUpdateInterface()

        # Actualitzar la vista
        if font.currentTab:
            font.currentTab.redraw()

        # Missatge de resum
        scope_names = ["glif actual", "glifs seleccionats", "tots els glifs"]
        scope_text = scope_names[self.scope_value]
        
        if len(selected_dest_names) <= 5:
            master_list = ", ".join(selected_dest_names)
        else:
            master_list = f"{', '.join(selected_dest_names[:5])} i {len(selected_dest_names)-5} més"
        
        Message("Fet!", 
                f"Origen: {source_master_name}\n"
                f"Àmbit: {scope_text}\n"
                f"Mètriques copiades a {len(selected_dest_names)} master(s):\n"
                f"{master_list}\n\n"
                f"Glifs processats: {processed_glyphs} de {len(glyphs_to_process)}\n"
                f"Total capes actualitzades: {total_copies}")


CopyMetricsToMasters()