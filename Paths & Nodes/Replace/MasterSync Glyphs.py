# MenuTitle: MasterSync Glyphs
# -*- coding: utf-8 -*-
# Description: Copies shapes, metrics, and spacing from a source master to the current master for selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import Glyphs
import vanilla
import traceback

class CopyMastersWindow(object):
    
    def __init__(self):
        # Crear la ventana
        self.w = vanilla.FloatingWindow(
            (280, 160),
            "Copy Masters Characters",
            autosaveName="CopyMastersWindow"
        )
        
        # Etiqueta para el desplegable
        self.w.masterLabel = vanilla.TextBox(
            (15, 15, 100, 20),
            "Source Master:",
            sizeStyle='small'
        )
        
        # Desplegable de masters
        self.w.masterPopUp = vanilla.PopUpButton(
            (120, 15, 145, 20),
            self.get_master_names(),
            sizeStyle='small',
            callback=self.masterChanged
        )
        
        # Línea separadora
        self.w.separator = vanilla.HorizontalLine(
            (15, 50, -15, 1)
        )
        
        # Información
        self.w.selectionInfo = vanilla.TextBox(
            (15, 65, -15, 40),
            "Selected glyphs will be copied from\nthe source master to the current master.",
            sizeStyle='small'
        )
        
        # Botón de aplicar
        self.w.applyButton = vanilla.Button(
            (15, 115, -15, 30),
            "Apply Copy",
            callback=self.applyCopy
        )
        
        # Variable para el master seleccionado
        self.selected_master_index = 0
        
        # Mostrar ventana
        self.w.open()
    
    def get_master_names(self):
        """Obtiene los nombres de los masters de la fuente actual"""
        font = Glyphs.font
        if not font:
            return ["No font open"]
        return [master.name for master in font.masters] or ["No masters found"]
    
    def masterChanged(self, sender):
        """Callback cuando cambia la selección del desplegable"""
        self.selected_master_index = sender.get()
    
    def applyCopy(self, sender):
        """Función principal que copia los caracteres"""
        try:
            font = Glyphs.font
            if not font:
                print("No font open")
                return
                
            if not font.masters:
                print("No masters in font")
                return
            
            # Obtener el master origen
            source_master = font.masters[self.selected_master_index]
            
            # Obtener el master activo actual (desde la capa seleccionada)
            selected_layers = font.selectedLayers
            if not selected_layers:
                print("No layers selected")
                return
            
            # El master actual es el de la primera capa seleccionada
            current_layer = selected_layers[0]
            
            # IMPORTANTE: En Glyphs, la capa seleccionada ya tiene la referencia al master
            # a través de .associatedMasterId
            current_master_id = current_layer.associatedMasterId
            
            if not current_master_id:
                print("Could not determine current master")
                return
            
            current_master = font.masters[current_master_id]
            
            # Obtener glifos seleccionados (a través de sus capas)
            selected_glyphs = []
            for layer in selected_layers:
                if layer.parent:  # Cada capa pertenece a un glifo
                    selected_glyphs.append(layer.parent)
            
            if not selected_glyphs:
                print("No glyphs selected")
                return
            
            print(f"\n📋 Copying from master: {source_master.name}")
            print(f"➡️ To current master: {current_master.name}")
            print(f"Selected glyphs: {[g.name for g in selected_glyphs]}\n")
            
            # Contador para feedback
            copied_count = 0
            
            # Para cada glifo seleccionado
            for glyph in selected_glyphs:
                # Obtener la capa del master origen
                source_layer = glyph.layers[source_master.id]
                
                # Obtener la capa del master destino (actual)
                target_layer = glyph.layers[current_master_id]
                
                if source_layer and target_layer:
                    # Copiar el contenido
                    target_layer.shapes = [shape.copy() for shape in source_layer.shapes]
                    target_layer.width = source_layer.width
                    
                    # Opcional: copiar también métricas si existen
                    if hasattr(source_layer, 'LSB'):
                        target_layer.LSB = source_layer.LSB
                    if hasattr(source_layer, 'RSB'):
                        target_layer.RSB = source_layer.RSB
                    
                    # Copiar keys de métricas
                    target_layer.leftMetricsKey = source_layer.leftMetricsKey
                    target_layer.rightMetricsKey = source_layer.rightMetricsKey
                    
                    copied_count += 1
                    print(f"  ✅ Copied: {glyph.name}")
            
            # Actualizar la vista
            Glyphs.redraw()
            
            # Feedback final
            print(f"\n✨ Successfully copied {copied_count} glyph(s) from {source_master.name}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            traceback.print_exc()

# Ejecutar el script
CopyMastersWindow()