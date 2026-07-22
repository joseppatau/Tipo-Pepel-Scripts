# MenuTitle: Import LSB/RSB from Another Font All masters
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, Message
from vanilla import FloatingWindow, PopUpButton, Button, TextBox, RadioGroup


class ImportLSBRSB:

    def __init__(self):
        self.target_font = Glyphs.font
        
        # Obtener lista de fuentes abiertas
        self.open_fonts = Glyphs.fonts
        
        if len(self.open_fonts) < 2:
            Message("Necesitas tener al menos dos fuentes abiertas.")
            return
        
        # Construir lista de nombres
        self.font_names = []
        self.font_indices = []
        for i, font in enumerate(self.open_fonts):
            if font.masters:
                name = font.masters[0].name
            else:
                name = f"Font {i+1}"
            
            if font == self.target_font:
                name += " [DESTINO]"
            self.font_names.append(name)
            self.font_indices.append(i)
        
        # Ventana
        self.w = FloatingWindow((320, 180), "Import LSB/RSB")
        
        self.w.sourceLabel = TextBox((20, 20, 150, 20), "Font source (from):")
        self.w.fontPopup = PopUpButton((170, 18, 130, 22), self.font_names)
        
        self.w.scopeLabel = TextBox((20, 55, 150, 20), "Apply to:")
        self.w.scopeRadio = RadioGroup(
            (170, 52, 130, 50),
            ["Current glyph only", "All glyphs"]
        )
        self.w.scopeRadio.set(0)  # Seleccionar "Current glyph only" por defecto
        
        self.w.applyButton = Button((20, 120, 130, 30), "Apply", callback=self.apply)
        self.w.cancelButton = Button((170, 120, 130, 30), "Cancel", callback=self.close)
        
        self.w.open()
        self.w._window.setLevel_(4)
    
    def close(self, sender):
        self.w.close()
    
    def show_message(self, msg, is_error=False):
        """Muestra mensaje al usuario"""
        if is_error:
            Message(f"⚠️ Error\n\n{msg}")
        else:
            Message(f"✅ Completado\n\n{msg}")
    
    def import_metrics_for_glyph(self, source_glyph, target_glyph, master_ids):
        """Importa LSB y RSB de un glifo origen a uno destino"""
        success = True
        for master_id in master_ids:
            source_layer = source_glyph.layers[master_id]
            target_layer = target_glyph.layers[master_id]
            
            if source_layer and target_layer:
                target_layer.LSB = source_layer.LSB
                target_layer.RSB = source_layer.RSB
            else:
                success = False
        return success
    
    def apply(self, sender):
        # Obtener fuentes
        selected_idx = self.font_indices[self.w.fontPopup.get()]
        source_font = self.open_fonts[selected_idx]
        target_font = self.target_font
        
        # Verificar
        if source_font == target_font:
            self.show_message("No puedes importar de la misma fuente.", is_error=True)
            return
        
        # Verificar número de masters
        if len(source_font.masters) != len(target_font.masters):
            self.show_message(
                f"Las fuentes no tienen el mismo número de masters.\n\n"
                f"Origen: {len(source_font.masters)} masters\n"
                f"Destino: {len(target_font.masters)} masters",
                is_error=True
            )
            return
        
        # Obtener IDs de masters
        master_ids = [master.id for master in target_font.masters]
        
        # Determinar alcance
        scope = self.w.scopeRadio.get()
        
        if scope == 0:  # Current glyph only
            # Obtener glifo actual
            if not target_font.selectedLayers:
                self.show_message("No hay ningún glifo seleccionado.", is_error=True)
                return
            
            target_glyph = target_font.selectedLayers[0].parent
            source_glyph = source_font.glyphs[target_glyph.name]
            
            if not source_glyph:
                self.show_message(
                    f"El glifo '{target_glyph.name}' no existe en la fuente origen.",
                    is_error=True
                )
                return
            
            # Importar métricas
            target_glyph.beginUndo()
            try:
                if self.import_metrics_for_glyph(source_glyph, target_glyph, master_ids):
                    target_glyph.endUndo()
                    self.show_message(
                        f"LSB y RSB importados para '{target_glyph.name}'.\n\n"
                        f"{len(master_ids)} master(s) actualizados."
                    )
                else:
                    target_glyph.endUndo()
                    self.show_message(
                        f"Error parcial en '{target_glyph.name}'. Algunos masters no se actualizaron.",
                        is_error=True
                    )
            except Exception as e:
                target_glyph.endUndo()
                self.show_message(f"Error: {str(e)}", is_error=True)
        
        else:  # All glyphs
            # Encontrar glifos comunes
            target_glyph_names = set(target_font.glyphs.keys())
            source_glyph_names = set(source_font.glyphs.keys())
            common_glyphs = target_glyph_names.intersection(source_glyph_names)
            
            if not common_glyphs:
                self.show_message("No hay glifos comunes entre las dos fuentes.", is_error=True)
                return
            
            # Importar para todos los glifos comunes
            imported_count = 0
            failed_count = 0
            
            for glyph_name in common_glyphs:
                source_glyph = source_font.glyphs[glyph_name]
                target_glyph = target_font.glyphs[glyph_name]
                
                if source_glyph and target_glyph:
                    target_glyph.beginUndo()
                    try:
                        if self.import_metrics_for_glyph(source_glyph, target_glyph, master_ids):
                            imported_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        failed_count += 1
                        print(f"Error en '{glyph_name}': {e}")
                    finally:
                        target_glyph.endUndo()
            
            self.show_message(
                f"Importación completada.\n\n"
                f"✓ Correctos: {imported_count} glifos\n"
                f"✗ Fallos: {failed_count} glifos\n\n"
                f"{len(master_ids)} master(s) actualizados por glifo."
            )


# Ejecutar script
ImportLSBRSB()