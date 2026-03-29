#MenuTitle: Transform (All Masters) - TURBO
# -*- coding: utf-8 -*-
# Description: Applies Glyphs-style transformations (translate, scale, slant) across current or all masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import Glyphs
import vanilla
import math

class TransformationTool(object):
    
    def __init__(self):
        # Obtener la fuente actual para listar los masters
        self.font = Glyphs.font
        self.master_checkboxes = {}
        self.master_controls_created = False
        self.masters_visible = False
        
        # Prefijos para guardar valores
        self.prefix = "com.transform.tool."
        
        # Altura base de la ventana (sin la lista de masters)
        self.base_height = 380
        self.current_height = self.base_height
        
        # Crear la ventana
        self.w = vanilla.FloatingWindow(
            (300, self.base_height),
            "Transform (All Masters) - TURBO"
        )
        
        # Recuperar valores guardados o usar defaults
        translate_x = Glyphs.defaults.get(self.prefix + "translate_x", "0")
        translate_y = Glyphs.defaults.get(self.prefix + "translate_y", "0")
        scale1 = Glyphs.defaults.get(self.prefix + "scale1", "95")
        scale2 = Glyphs.defaults.get(self.prefix + "scale2", "100")
        slant = Glyphs.defaults.get(self.prefix + "slant", "10")
        scope = Glyphs.defaults.get(self.prefix + "scope", 0)
        selected_master = Glyphs.defaults.get(self.prefix + "selected_master", False)
        
        # Translate X
        self.w.translateXLabel = vanilla.TextBox(
            (15, 15, 60, 20),
            "Translate X",
            sizeStyle='small'
        )
        self.w.translateX = vanilla.EditText(
            (80, 15, 50, 20),
            translate_x,
            sizeStyle='small'
        )
        
        # Translate Y
        self.w.translateYLabel = vanilla.TextBox(
            (140, 15, 20, 20),
            "Y",
            sizeStyle='small'
        )
        self.w.translateY = vanilla.EditText(
            (165, 15, 50, 20),
            translate_y,
            sizeStyle='small'
        )
        
        # Separador visual
        self.w.separator1 = vanilla.HorizontalLine((15, 45, -15, 1))
        
        # Scale
        self.w.scaleLabel = vanilla.TextBox(
            (15, 55, 60, 20),
            "Scale",
            sizeStyle='small'
        )
        self.w.scale = vanilla.EditText(
            (80, 55, 50, 20),
            scale1,
            sizeStyle='small'
        )
        self.w.scalePercent = vanilla.TextBox(
            (135, 55, 30, 20),
            "%",
            sizeStyle='small'
        )
        
        # Flecha hacia abajo y segundo scale
        self.w.scaleArrow = vanilla.TextBox(
            (15, 80, 20, 20),
            "↓",
            sizeStyle='small'
        )
        self.w.scale2 = vanilla.EditText(
            (80, 80, 50, 20),
            scale2,
            sizeStyle='small'
        )
        self.w.scale2Percent = vanilla.TextBox(
            (135, 80, 30, 20),
            "%",
            sizeStyle='small'
        )
        
        # Separador visual
        self.w.separator2 = vanilla.HorizontalLine((15, 110, -15, 1))
        
        # Slant
        self.w.slantLabel = vanilla.TextBox(
            (15, 120, 60, 20),
            "Slant",
            sizeStyle='small'
        )
        self.w.slant = vanilla.EditText(
            (80, 120, 50, 20),
            slant,
            sizeStyle='small'
        )
        self.w.slantDegrees = vanilla.TextBox(
            (135, 120, 30, 20),
            "°",
            sizeStyle='small'
        )
        
        # Separador visual
        self.w.separator3 = vanilla.HorizontalLine((15, 150, -15, 1))
        
        # Radio buttons para ámbito
        self.w.scopeLabel = vanilla.TextBox(
            (15, 160, 100, 20),
            "Apply to:",
            sizeStyle='small'
        )
        self.w.scope = vanilla.RadioGroup(
            (15, 180, -15, 40),
            ["Current Master", "All Masters"],
            sizeStyle='small'
        )
        self.w.scope.set(scope)
        
        # Nuevo checkbox para Selected Master
        self.w.selectedMasterCheckbox = vanilla.CheckBox(
            (15, 220, 150, 20),
            "Selected Master",
            callback=self.toggle_selected_master,
            sizeStyle='small'
        )
        self.w.selectedMasterCheckbox.set(selected_master)
        
        # Botones principales
        self.w.cancelButton = vanilla.Button(
            (15, self.base_height - 45, 90, 20),
            "Cancel",
            callback=self.cancel,
            sizeStyle='small'
        )
        self.w.okButton = vanilla.Button(
            (135, self.base_height - 45, 90, 20),
            "OK",
            callback=self.apply,
            sizeStyle='small'
        )
        self.w.closeButton = vanilla.Button(
            (225, self.base_height - 45, 60, 20),
            "Close",
            callback=self.close_window,
            sizeStyle='small'
        )
        
        # Mensaje de estado
        self.w.statusMessage = vanilla.TextBox(
            (15, self.base_height - 70, 270, 20),
            "Ready",
            sizeStyle='small'
        )
        
        # Inicialmente no hay controles de masters
        self.master_controls = []
        
        # Crear los controles de masters
        self.create_master_controls()
        
        # Mostrar ventana
        self.w.open()
    
    def save_values(self):
        """Guardar los valores actuales"""
        Glyphs.defaults[self.prefix + "translate_x"] = self.w.translateX.get()
        Glyphs.defaults[self.prefix + "translate_y"] = self.w.translateY.get()
        Glyphs.defaults[self.prefix + "scale1"] = self.w.scale.get()
        Glyphs.defaults[self.prefix + "scale2"] = self.w.scale2.get()
        Glyphs.defaults[self.prefix + "slant"] = self.w.slant.get()
        Glyphs.defaults[self.prefix + "scope"] = self.w.scope.get()
        Glyphs.defaults[self.prefix + "selected_master"] = self.w.selectedMasterCheckbox.get()
        
        # Guardar selección de masters
        if self.master_checkboxes:
            for master in self.font.masters:
                key = self.prefix + f"master_{master.id}"
                Glyphs.defaults[key] = self.master_checkboxes.get(master.id, False).get()
    
    def load_master_selections(self):
        """Cargar la selección previa de masters"""
        if not self.master_checkboxes:
            return
        
        for master in self.font.masters:
            key = self.prefix + f"master_{master.id}"
            saved_value = Glyphs.defaults.get(key, None)
            if saved_value is not None:
                checkbox = self.master_checkboxes.get(master.id)
                if checkbox:
                    checkbox.set(saved_value)
    
    def set_status(self, message):
        """Actualizar el mensaje de estado"""
        self.w.statusMessage.set(message)
    
    def create_master_controls(self):
        """Crear los checkboxes de masters y el botón Select All"""
        if self.master_controls_created:
            return
        
        num_masters = len(self.font.masters) if self.font else 0
        if num_masters == 0:
            return
        
        # Posición Y donde comenzarán los controles
        start_y = 245
        y_pos = start_y
        
        # Crear checkboxes para cada master
        for i, master in enumerate(self.font.masters):
            checkbox = vanilla.CheckBox(
                (25, y_pos, 250, 20),
                master.name,
                sizeStyle='small',
                callback=self.master_selection_changed
            )
            # Por defecto, seleccionar el master actual
            current_layer = self.font.selectedLayers[0] if self.font.selectedLayers else None
            if current_layer and current_layer.master == master:
                checkbox.set(True)
            
            self.master_checkboxes[master.id] = checkbox
            self.master_controls.append(checkbox)
            setattr(self.w, f"master_checkbox_{i}", checkbox)
            y_pos += 22
        
        # Cargar selecciones previas
        self.load_master_selections()
        
        # Crear botón Select All / Deselect All (debajo del listado)
        button_y = y_pos + 5
        self.select_all_button = vanilla.Button(
            (25, button_y, 110, 20),
            "Select All",
            callback=self.toggle_select_all,
            sizeStyle='small'
        )
        self.master_controls.append(self.select_all_button)
        
        # Guardar la altura total de los controles de masters
        self.masters_total_height = (num_masters * 22) + 35
        self.master_controls_start_y = start_y
        
        # Inicialmente, si el checkbox no está marcado, movemos los controles fuera
        if not self.w.selectedMasterCheckbox.get():
            self.set_masters_position(offset_y=500)
        else:
            self.set_masters_position(offset_y=0)
            self.masters_visible = True
            self.resize_window()
        
        self.master_controls_created = True
    
    def set_masters_position(self, offset_y=0):
        """Mover los controles de masters a una posición específica"""
        if not self.master_controls:
            return
        
        # Mover checkboxes
        y_pos = self.master_controls_start_y
        for i, master in enumerate(self.font.masters):
            if i < len(self.master_controls):
                try:
                    new_y = y_pos + offset_y
                    self.master_controls[i].setPosSize((25, new_y, 250, 20))
                except:
                    pass
            y_pos += 22
        
        # Mover botón Select All (debajo del listado)
        try:
            new_y = y_pos + 5 + offset_y
            self.select_all_button.setPosSize((25, new_y, 110, 20))
        except:
            pass
    
    def show_master_controls(self):
        """Mostrar los controles de masters"""
        if self.master_controls_created:
            self.set_masters_position(offset_y=0)
            self.masters_visible = True
            self.resize_window()
        else:
            self.create_master_controls()
            self.set_masters_position(offset_y=0)
            self.masters_visible = True
            self.resize_window()
    
    def hide_master_controls(self):
        """Ocultar los controles de masters moviéndolos fuera de la vista"""
        if self.master_controls_created:
            self.set_masters_position(offset_y=500)
            self.masters_visible = False
            self.resize_window()
    
    def toggle_selected_master(self, sender):
        """Mostrar u ocultar la lista de masters según el checkbox"""
        is_checked = self.w.selectedMasterCheckbox.get()
        
        if is_checked:
            self.show_master_controls()
            self.w.scope.enable(False)
        else:
            self.hide_master_controls()
            self.w.scope.enable(True)
    
    def toggle_select_all(self, sender):
        """Alternar entre seleccionar todos y deseleccionar todos los masters"""
        if not self.master_checkboxes:
            return
            
        all_checked = all(checkbox.get() for checkbox in self.master_checkboxes.values())
        
        if all_checked:
            # Deseleccionar todos
            for checkbox in self.master_checkboxes.values():
                checkbox.set(False)
            self.select_all_button.setTitle("Select All")
        else:
            # Seleccionar todos
            for checkbox in self.master_checkboxes.values():
                checkbox.set(True)
            self.select_all_button.setTitle("Deselect All")
    
    def master_selection_changed(self, sender):
        """Actualizar el texto del botón según el estado de selección"""
        if not self.master_checkboxes or not self.select_all_button:
            return
            
        all_checked = all(checkbox.get() for checkbox in self.master_checkboxes.values())
        none_checked = not any(checkbox.get() for checkbox in self.master_checkboxes.values())
        
        if all_checked:
            self.select_all_button.setTitle("Deselect All")
        elif none_checked:
            self.select_all_button.setTitle("Select All")
    
    def resize_window(self):
        """Redimensionar la ventana según si la lista de masters está visible"""
        if self.masters_visible:
            new_height = self.master_controls_start_y + self.masters_total_height + 80
        else:
            new_height = self.base_height
        
        if new_height != self.current_height:
            self.current_height = new_height
            self.w.resize(300, new_height)
            
            # Recolocar botones principales
            button_y = new_height - 45
            self.w.cancelButton.setPosSize((15, button_y, 90, 20))
            self.w.okButton.setPosSize((135, button_y, 90, 20))
            self.w.closeButton.setPosSize((225, button_y, 60, 20))
            
            # Recolocar mensaje de estado
            self.w.statusMessage.setPosSize((15, button_y - 25, 270, 20))
    
    def get_selected_masters(self):
        """Obtener los masters seleccionados en la lista"""
        if not self.w.selectedMasterCheckbox.get():
            return None
        
        selected_masters = []
        for master in self.font.masters:
            checkbox = self.master_checkboxes.get(master.id)
            if checkbox and checkbox.get():
                selected_masters.append(master)
        
        return selected_masters if selected_masters else None
    
    def cancel(self, sender):
        """Cerrar ventana sin aplicar cambios"""
        self.w.close()
    
    def close_window(self, sender):
        """Cerrar la ventana"""
        self.w.close()
    
    def get_transform_values(self):
        """Obtiene los valores de transformación de los campos"""
        try:
            translate_x = float(self.w.translateX.get() or "0")
            translate_y = float(self.w.translateY.get() or "0")
            scale1 = float(self.w.scale.get() or "100") / 100.0
            scale2 = float(self.w.scale2.get() or "100") / 100.0
            slant = float(self.w.slant.get() or "0")
            
            return {
                'translate': (translate_x, translate_y),
                'scale': (scale1, scale2),
                'slant': slant
            }
        except ValueError:
            return None
    
    def transform_point(self, x, y, values):
        """Aplica las transformaciones a un punto (x, y)"""
        # 1. Traslación
        x += values['translate'][0]
        y += values['translate'][1]
        
        # 2. Escalado
        x *= values['scale'][0]
        y *= values['scale'][1]
        
        # 3. Slant (inclinación)
        if values['slant'] != 0:
            slant_rad = math.radians(values['slant'])
            x = x + (y * math.tan(slant_rad))
        
        return (x, y)
    
    def apply_transform_to_layer(self, layer, values):
        """Aplica las transformaciones a una capa (paths y anchors) - VERSIÓN TURBO"""
        if not layer or not values:
            return
        
        # Transformar paths - versión optimizada
        for path in layer.paths:
            nodes = path.nodes
            if nodes:
                for node in nodes:
                    new_x, new_y = self.transform_point(node.x, node.y, values)
                    node.x = new_x
                    node.y = new_y
        
        # Transformar anchors - versión optimizada
        if hasattr(layer, 'anchors') and layer.anchors:
            for anchor in layer.anchors:
                if hasattr(anchor, 'position'):
                    new_x, new_y = self.transform_point(anchor.position.x, anchor.position.y, values)
                    anchor.position = (new_x, new_y)
    
    def apply(self, sender):
        """Aplica las transformaciones - VERSIÓN TURBO"""
        
        # Guardar valores actuales
        self.save_values()
        
        # Obtener valores
        values = self.get_transform_values()
        if not values:
            self.set_status("Error: Invalid values")
            return
        
        font = Glyphs.font
        if not font:
            self.set_status("Error: No font open")
            return
        
        # Verificar si se está usando la selección de masters
        use_selected_masters = self.w.selectedMasterCheckbox.get()
        selected_masters = self.get_selected_masters() if use_selected_masters else None
        
        if use_selected_masters and not selected_masters:
            self.set_status("Error: No master selected")
            return
        
        # Obtener capas seleccionadas
        selected_layers = font.selectedLayers
        if not selected_layers:
            # Si no hay selección, aplicar a todos los glifos
            self.set_status("Applying to all glyphs...")
            all_glyphs = font.glyphs
            selected_layers = []
            for glyph in all_glyphs:
                if glyph.layers:
                    selected_layers.append(glyph.layers[0])
        
        # Deshabilitar actualización de interfaz
        font.disableUpdateInterface()
        
        try:
            transformed_glyphs = 0
            transformed_layers = 0
            
            # Pre-cache para mejorar rendimiento
            if use_selected_masters:
                selected_master_ids = [master.id for master in selected_masters]
            
            # Procesar glifos
            for layer in selected_layers:
                glyph = layer.parent
                if not glyph:
                    continue
                
                glyph_transformed = False
                
                if use_selected_masters:
                    # Procesar solo los masters seleccionados
                    for l in glyph.layers:
                        if l.isMasterLayer or l.isSpecialLayer:
                            if hasattr(l, 'associatedMasterId'):
                                master_id = l.associatedMasterId
                                if master_id in selected_master_ids:
                                    self.apply_transform_to_layer(l, values)
                                    transformed_layers += 1
                                    glyph_transformed = True
                            elif hasattr(l, 'masterId'):
                                master_id = l.masterId
                                if master_id in selected_master_ids:
                                    self.apply_transform_to_layer(l, values)
                                    transformed_layers += 1
                                    glyph_transformed = True
                else:
                    scope = self.w.scope.get()
                    
                    if scope == 0:  # Current Master
                        self.apply_transform_to_layer(layer, values)
                        transformed_layers += 1
                        glyph_transformed = True
                    else:  # All Masters
                        for l in glyph.layers:
                            if l.isMasterLayer or l.isSpecialLayer:
                                self.apply_transform_to_layer(l, values)
                                transformed_layers += 1
                        glyph_transformed = True
                
                if glyph_transformed:
                    transformed_glyphs += 1
            
            Glyphs.redraw()
            self.set_status(f"✓ Done: {transformed_glyphs} glyphs, {transformed_layers} layers")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)[:50]}")
            import traceback
            traceback.print_exc()
            
        finally:
            font.enableUpdateInterface()

# Ejecutar el script
TransformationTool()