# MenuTitle: Duplicate Paths to Masters
# -*- coding: utf-8 -*-

import vanilla
import traceback
from GlyphsApp import Glyphs, Message
from AppKit import NSFont, NSAttributedString, NSFontAttributeName


class DuplicatePathsToMasters:
    
    def __init__(self):
        self.setupUI()
    
    def setupUI(self):
        self.w = vanilla.FloatingWindow((380, 240), "Duplicate Paths to Masters")
        
        y = 10
        
        # Instrucciones
        self.w.infoText = vanilla.TextBox(
            (15, y, -10, 40),
            "Select glyphs in the font view,\nthen click the button to duplicate their paths to all masters.",
            sizeStyle="small"
        )
        y += 50
        
        # Opción: Eliminar paths existentes en los masters destino
        self.w.replaceCheck = vanilla.CheckBox(
            (15, y, -10, 20),
            "Replace existing paths in target masters",
            value=True
        )
        y += 30
        
        # Opción: Copiar métricas a los masters destino
        self.w.copyMetricsCheck = vanilla.CheckBox(
            (15, y, -10, 20),
            "Copy metrics (LSB, RSB, width) to target masters",
            value=True
        )
        y += 30
        
        # Botón principal
        self.w.duplicateButton = vanilla.Button(
            (15, y, -15, 30),
            "Duplicate Paths",
            callback=self.duplicatePaths
        )
        
        # Estilo del botón en negrita
        try:
            button_title = NSAttributedString.alloc().initWithString_attributes_(
                "Duplicate Paths",
                {NSFontAttributeName: NSFont.boldSystemFontOfSize_(NSFont.systemFontSize())}
            )
            self.w.duplicateButton.getNSButton().setAttributedTitle_(button_title)
        except:
            pass
        
        y += 45
        
        # Estado
        self.w.statusText = vanilla.TextBox(
            (15, y, -10, 40),
            "Ready",
            sizeStyle="small"
        )
        
        self.w.open()
    
    def duplicatePaths(self, sender):
        """Duplica los paths de los glifos seleccionados a todos los masters"""
        font = Glyphs.font
        
        if not font:
            Message("Error", "No font open.", OKButton="OK")
            self.w.statusText.set("❌ No font open")
            return
        
        # Obtener glifos seleccionados
        selected_layers = font.selectedLayers
        
        if not selected_layers:
            Message("Info", "Select at least one glyph in the font view.", OKButton="OK")
            self.w.statusText.set("❌ No glyphs selected")
            return
        
        # Obtener la lista de masters
        masters = font.masters
        master_count = len(masters)
        
        if master_count <= 1:
            Message("Info", "Need at least 2 masters to duplicate paths.", OKButton="OK")
            self.w.statusText.set("❌ Only one master found")
            return
        
        # Opciones
        replace = self.w.replaceCheck.get()
        copy_metrics = self.w.copyMetricsCheck.get()
        
        processed = 0
        errors = 0
        glyphs_processed = 0
        
        font.disableUpdateInterface()
        
        try:
            for layer in selected_layers:
                glyph = layer.parent
                if not glyph:
                    continue
                
                glyphs_processed += 1
                
                # Obtener el ID del master actual
                source_master_id = layer.associatedMasterId
                
                # Obtener los paths de la capa seleccionada
                source_layer = glyph.layers[source_master_id]
                
                # Verificar que la capa tenga paths
                if not source_layer.paths:
                    print(f"⚠️ Glyph '{glyph.name}' has no paths in source master")
                    continue
                
                # Copiar los paths de origen
                source_paths = source_layer.paths
                
                # Obtener métricas del origen
                source_lsb = source_layer.LSB
                source_rsb = source_layer.RSB
                source_width = source_layer.width
                
                # Para cada master
                for master in masters:
                    target_master_id = master.id
                    
                    # Saltar el master de origen
                    if target_master_id == source_master_id:
                        continue
                    
                    # Obtener la capa destino
                    target_layer = glyph.layers[target_master_id]
                    
                    try:
                        # Copiar métricas si se solicita
                        if copy_metrics:
                            target_layer.LSB = source_lsb
                            target_layer.RSB = source_rsb
                            target_layer.width = source_width
                        
                        # Eliminar paths existentes si se solicita
                        if replace and target_layer.paths:
                            # Método correcto: eliminar cada path individualmente
                            # Creamos una copia de la lista para evitar problemas durante la iteración
                            paths_to_remove = list(target_layer.paths)
                            for path in paths_to_remove:
                                target_layer.removePath_(path)
                        
                        # Duplicar paths de la capa origen
                        for path in source_paths:
                            # Crear copia del path
                            new_path = path.copy()
                            target_layer.paths.append(new_path)
                        
                        processed += 1
                        
                    except Exception as e:
                        errors += 1
                        print(f"❌ Error duplicating to '{glyph.name}' master '{master.name}': {e}")
                        traceback.print_exc()
                
                print(f"✅ Duplicated paths for '{glyph.name}' to {master_count - 1} masters")
                if copy_metrics:
                    print(f"   Metrics copied: LSB={source_lsb}, RSB={source_rsb}, Width={source_width}")
            
        except Exception as e:
            Message("Error", f"An error occurred: {e}", OKButton="OK")
            self.w.statusText.set(f"❌ Error: {str(e)[:50]}")
            traceback.print_exc()
            
        finally:
            font.enableUpdateInterface()
        
        # Mostrar resultado
        if errors == 0:
            metrics_msg = " with metrics" if copy_metrics else ""
            self.w.statusText.set(f"✅ Processed {glyphs_processed} glyphs to {master_count - 1} masters{metrics_msg}")
            Message("Success", f"Duplicated paths for {glyphs_processed} glyphs\nto {master_count - 1} masters{metrics_msg}.", OKButton="OK")
        else:
            self.w.statusText.set(f"⚠️ Glyphs: {glyphs_processed}, Masters: {processed}, Errors: {errors}")
            Message("Completed with errors", f"Glyphs processed: {glyphs_processed}\nMasters updated: {processed}\nErrors: {errors}\nCheck console for details.", OKButton="OK")


# Ejecutar
DuplicatePathsToMasters()