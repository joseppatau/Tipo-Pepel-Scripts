#MenuTitle: Glyph Fill Engine
# -*- coding: utf-8 -*-
# Description: Fills glyph shapes with circles or custom glyphs using an adaptive multi-pass distribution algorithm.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
from __future__ import division, print_function
from GlyphsApp import *
from vanilla import Window, TextBox, EditText, Button, PopUpButton, CheckBox, List
from AppKit import NSFloatingWindowLevel
import math

KAPPA = 0.5522847498

# Función para mostrar mensajes de ayuda con ventana Vanilla flotante
def show_help(message, title="Help"):
    from vanilla import Window, TextBox, Button
    
    help_window = Window((400, 300), title)
    help_window._window.setLevel_(NSFloatingWindowLevel)  # Esto la hace flotante
    help_window.text = TextBox((10, 10, 380, 220), message)
    
    def close_window(sender):
        help_window.close()
    
    help_window.closeButton = Button((150, 240, 100, 30), "OK", callback=close_window)
    help_window.open()


class FillCirclesTurbo(object):

    def __init__(self):
        print("[Fill TURBO] UI init")

        self.w = Window((450, 560), "Fill with Glyphs TURBO")
        self.w._window.setLevel_(NSFloatingWindowLevel)

        # Variables para almacenar la lista de glifos
        self.glyph_list = ["circle"]  # Lista por defecto
        
        y = 12
        
        # === MODO DE APLICACIÓN ===
        self.w.modeText = TextBox((10, y, 120, 17), "Apply to:")
        self.w.modePopup = PopUpButton((140, y, 150, 22), 
                                      ["current glyph", "selected glyphs", "entire font"])
        y += 30
        
        # === MASTER ===
        self.w.masterText = TextBox((10, y, 120, 17), "Master:")
        self.w.masterPopup = PopUpButton((140, y, 150, 22), self.get_master_names())
        y += 30

        # === PARÁMETROS CON BOTONES DE AYUDA ===
        # Min diameter
        self.w.minText = TextBox((10, y, 120, 17), "Min diameter")
        self.w.minDia = EditText((140, y, 100, 22), "8")
        self.w.minHelp = Button((250, y, 22, 22), "?", callback=self.show_min_help)
        y += 30

        # Max diameter
        self.w.maxText = TextBox((10, y, 120, 17), "Max diameter")
        self.w.maxDia = EditText((140, y, 100, 22), "120")
        self.w.maxHelp = Button((250, y, 22, 22), "?", callback=self.show_max_help)
        y += 30

        # Safe area
        self.w.safeText = TextBox((10, y, 120, 17), "Safe area")
        self.w.safeArea = EditText((140, y, 100, 22), "10")
        self.w.safeHelp = Button((250, y, 22, 22), "?", callback=self.show_safe_help)
        y += 30
        
        # Step size
        self.w.stepText = TextBox((10, y, 120, 17), "Step size")
        self.w.stepSize = EditText((140, y, 100, 22), "8")
        self.w.stepHelp = Button((250, y, 22, 22), "?", callback=self.show_step_help)
        y += 30
        
        # Size drop
        self.w.dropText = TextBox((10, y, 120, 17), "Size drop")
        self.w.sizeDrop = EditText((140, y, 100, 22), "20")
        self.w.dropHelp = Button((250, y, 22, 22), "?", callback=self.show_drop_help)
        y += 30
        
        # Structure passes
        self.w.passesText = TextBox((10, y, 120, 17), "Structure passes")
        self.w.structurePasses = EditText((140, y, 100, 22), "3")
        self.w.passesHelp = Button((250, y, 22, 22), "?", callback=self.show_passes_help)
        y += 30
        
        # Max per size
        self.w.maxPerSizeText = TextBox((10, y, 120, 17), "Max per size")
        self.w.maxPerSize = EditText((140, y, 100, 22), "4")
        self.w.maxPerSizeHelp = Button((250, y, 22, 22), "?", callback=self.show_maxpersize_help)
        y += 40

        # === CHECKBOX PRINCIPAL ===
        self.w.useGlyphsCheck = CheckBox((10, y, 150, 22), "Use multiple glyphs")
        y += 30
        
        # === GESTIÓN DE GLIFOS ===
        # Grupo para la gestión de glifos
        glyph_group_y = y
        
        self.w.glyphLabel = TextBox((10, glyph_group_y, 150, 17), "Glyph to add:")
        self.w.newGlyphName = EditText((10, glyph_group_y + 20, 150, 22), "circle")
        self.w.addGlyphButton = Button((170, glyph_group_y + 20, 80, 22), "Add Glyph", callback=self.add_glyph)
        
        # Lista de glifos
        self.w.glyphListLabel = TextBox((10, glyph_group_y + 50, 200, 17), "Glyphs list (click to select):")
        
        # Scroll area con lista
        self.w.glyphList = List(
            (10, glyph_group_y + 70, 280, 120),
            self.glyph_list
        )
        
        # Botones para gestionar la lista
        self.w.removeSelectedButton = Button((300, glyph_group_y + 70, 80, 22), "Remove", callback=self.remove_selected_glyph)
        self.w.clearAllButton = Button((300, glyph_group_y + 100, 80, 22), "Clear All", callback=self.clear_all_glyphs)
        
        y = glyph_group_y + 200

        # === BOTONES PRINCIPALES ===
        button_y = 460
        self.w.previewButton = Button((10, 520, 180, 30), "PREVIEW", callback=self.preview)
        self.w.applyButton = Button((200, 520, 180, 30), "APPLY", callback=self.apply)

        self.w.open()
        print("[Fill TURBO] UI opened")
    
    # === FUNCIONES DE AYUDA ===
    def show_min_help(self, sender):
        show_help(
            "Minimum diameter of shapes to place.\n\n"
            "Smaller values allow more detailed filling.\n"
            "Default: 8",
            "Min diameter Help"
        )
    
    def show_max_help(self, sender):
        show_help(
            "Maximum diameter of shapes to place.\n\n"
            "Larger values create bigger focal points.\n"
            "Default: 120",
            "Max diameter Help"
        )
    
    def show_safe_help(self, sender):
        show_help(
            "Safe area around each shape.\n\n"
            "Minimum distance between shapes to avoid overlap.\n"
            "Higher values create more spacing.\n"
            "Default: 10",
            "Safe area Help"
        )
    
    def show_step_help(self, sender):
        show_help(
            "STEP SIZE - Distance between placement attempts.\n\n"
            "• Low (4-6): Denser filling, more shapes\n"
            "• High (12-16): Airier filling, fewer shapes\n"
            "Default: 8\n\n"
            "Like grid resolution - small step = fine mesh",
            "Step size Help"
        )
    
    def show_drop_help(self, sender):
        show_help(
            "SIZE DROP - How much size decreases each pass.\n\n"
            "• Low (10-15): Smooth size transition, more variety\n"
            "• High (25-30): Abrupt changes, less variety\n"
            "Default: 20\n\n"
            "Like stair steps - small steps = subtle changes",
            "Size drop Help"
        )
    
    def show_passes_help(self, sender):
        show_help(
            "STRUCTURE PASSES - Strategic large shape placement.\n\n"
            "• Low (1): Fewer large shapes, homogeneous fill\n"
            "• High (5): More large shapes, hierarchical structure\n"
            "Default: 3\n\n"
            "Like placing big furniture before filling with small items",
            "Structure passes Help"
        )
    
    def show_maxpersize_help(self, sender):
        show_help(
            "MAX PER SIZE - Limit of same-size shapes per row.\n\n"
            "• Low (2-3): Dispersed distribution, avoids clustering\n"
            "• High (6-8): Allows more repetition, denser fill\n"
            "Default: 4\n\n"
            "Prevents repetitive patterns of same-sized shapes",
            "Max per size Help"
        )
        
    def get_master_names(self):
        """Obtiene los nombres de todos los masters de la fuente"""
        font = Glyphs.font
        if not font or not font.masters:
            return ["No masters found"]
        
        return [master.name for master in font.masters]
    
    def get_selected_master(self):
        """Obtiene el índice del master seleccionado"""
        font = Glyphs.font
        if not font or not font.masters:
            return 0
            
        master_index = self.w.masterPopup.get()
        if master_index >= len(font.masters):
            return 0
            
        return master_index
    
    def has_only_components(self, glyph):
        """Verifica si un glifo solo tiene componentes (sin paths)"""
        if not glyph or not glyph.layers:
            return False
            
        master_index = self.get_selected_master()
        if master_index >= len(glyph.layers):
            return False
            
        layer = glyph.layers[master_index]
        has_paths = len(layer.paths) > 0
        
        return not has_paths and len(layer.components) > 0

    def get_glyph_layer(self, glyph_name):
        """Obtiene la capa del glifo especificado en el master seleccionado"""
        font = Glyphs.font
        if not font:
            return None
            
        glyph = font.glyphs[glyph_name]
        if not glyph:
            return None
            
        master_index = self.get_selected_master()
        if master_index >= len(glyph.layers):
            return None
            
        return glyph.layers[master_index]

    # === GESTIÓN DE LA LISTA DE GLIFOS ===
    
    def add_glyph(self, sender):
        """Añade un nuevo glifo a la lista"""
        new_glyph = self.w.newGlyphName.get().strip()
        if new_glyph and new_glyph not in self.glyph_list:
            self.glyph_list.append(new_glyph)
            self.update_list_ui()
            print(f"[Fill TURBO] Añadido glifo: {new_glyph}")
    
    def remove_selected_glyph(self, sender):
        """Elimina el glifo seleccionado de la lista"""
        selection = self.w.glyphList.getSelection()
        if selection:
            # Eliminar en orden inverso para no afectar los índices
            for index in sorted(selection, reverse=True):
                removed = self.glyph_list.pop(index)
                print(f"[Fill TURBO] Eliminado glifo: {removed}")
            self.update_list_ui()
    
    def clear_all_glyphs(self, sender):
        """Limpia toda la lista de glifos"""
        self.glyph_list = []
        self.update_list_ui()
        print("[Fill TURBO] Lista de glifos vaciada")
    
    def update_list_ui(self):
        """Actualiza la interfaz de la lista"""
        self.w.glyphList.set(self.glyph_list)
    
    def get_glyph_layers(self):
        """Obtiene todas las capas de glifos válidas de la lista"""
        if not self.w.useGlyphsCheck.get():
            return []
            
        glyph_layers = []
        for glyph_name in self.glyph_list:
            layer = self.get_glyph_layer(glyph_name)
            if layer and layer.paths:
                glyph_layers.append((glyph_name, layer))
            else:
                print(f"[Fill TURBO] ¡ATENCIÓN! Glifo no válido: {glyph_name}")
        
        return glyph_layers

    # =====================
    def get_target_layers(self):
        """Obtiene las capas según el modo seleccionado y el master elegido"""
        font = Glyphs.font
        if not font:
            return []
            
        mode = self.w.modePopup.getItems()[self.w.modePopup.get()]
        master_index = self.get_selected_master()
        
        layers = []
        skipped_glyphs = 0
        
        if mode == "current glyph":
            current_layer = font.selectedLayers[0]
            if current_layer:
                glyph = current_layer.parent
                if master_index < len(glyph.layers):
                    layer = glyph.layers[master_index]
                    layers.append(layer)
                    print(f"[Fill TURBO] Modo: glifo actual - {glyph.name}")
            
        elif mode == "selected glyphs":
            for layer in font.selectedLayers:
                if layer:
                    glyph = layer.parent
                    if master_index < len(glyph.layers):
                        target_layer = glyph.layers[master_index]
                        
                        if self.has_only_components(glyph):
                            skipped_glyphs += 1
                            print(f"[Fill TURBO] Saltando {glyph.name} - solo componentes")
                            continue
                            
                        layers.append(target_layer)
            
            print(f"[Fill TURBO] Modo: {len(layers)} glifos seleccionados")
            
        elif mode == "entire font":
            for glyph in font.glyphs:
                if master_index < len(glyph.layers):
                    if self.has_only_components(glyph):
                        skipped_glyphs += 1
                        continue
                        
                    layers.append(glyph.layers[master_index])
            
            print(f"[Fill TURBO] Modo: toda la fuente - {len(layers)} glifos")
            
        return layers

    def get_glyph_bounds(self, glyph_layer):
        """Obtiene los bounds del glifo"""
        if not glyph_layer or not glyph_layer.paths:
            return None
            
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for path in glyph_layer.paths:
            for node in path.nodes:
                x, y = node.position
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        
        width = max_x - min_x
        height = max_y - min_y
        
        return (min_x, min_y, width, height)

    # =====================
    def run_on_layer(self, layer, preview=True, minD=None, maxD=None, safe=None):
        """Ejecuta el algoritmo en una capa específica"""
        if not layer:
            return 0

        # Obtener parámetros
        STEP = float(self.w.stepSize.get())
        SIZE_DROP = float(self.w.sizeDrop.get())
        STRUCTURE_PASSES = int(self.w.structurePasses.get())
        MAX_PER_SIZE = int(self.w.maxPerSize.get())

        bounds = layer.bounds
        existing = []

        if preview:
            target = layer.copy()
            target.name = "● Fill TURBO Preview"
        else:
            target = layer

        # Obtener glifos a utilizar
        use_glyphs = self.w.useGlyphsCheck.get()
        glyph_data = self.get_glyph_layers() if use_glyphs else []
        
        if use_glyphs and not glyph_data:
            print("[Fill TURBO] No hay glifos válidos en la lista. Usando círculos.")
            use_glyphs = False

        # TESTS GEOMÉTRICOS
        insidePath = layer.completeBezierPath
        
        def overlaps(cx, cy, r):
            for ox, oy, orr, _ in existing:
                if math.hypot(cx - ox, cy - oy) < (r + orr + safe):
                    return True
            return False

        def respectsOutline(cx, cy, r):
            testR = r + safe
            STEPS = 64

            for i in range(STEPS):
                a = 2 * math.pi * i / STEPS
                px = cx + math.cos(a) * testR
                py = cy + math.sin(a) * testR

                if not insidePath.containsPoint_((px, py)):
                    return False
            return True

        def drawCircle(cx, cy, r, glyph_index=0):
            if use_glyphs and glyph_data:
                # Seleccionar glifo de la lista (cíclicamente)
                glyph_name, glyph_layer = glyph_data[glyph_index % len(glyph_data)]
                bounds_data = self.get_glyph_bounds(glyph_layer)
                
                if bounds_data:
                    min_x, min_y, width, height = bounds_data
                    target_size = r * 2
                    glyph_max_dim = max(width, height)
                    
                    if glyph_max_dim > 0:
                        scale = target_size / glyph_max_dim
                        
                        component = GSComponent(glyph_layer.parent)
                        component.position = (cx - min_x * scale, cy - min_y * scale)
                        component.scale = (scale, scale)
                        target.components.append(component)
            else:
                # Dibujar círculo normal
                h = r * KAPPA
                p = GSPath()
                p.closed = True
                p.nodes = [
                    GSNode((cx, cy + r), GSCURVE),
                    GSNode((cx + h, cy + r), GSOFFCURVE),
                    GSNode((cx + r, cy + h), GSOFFCURVE),
                    GSNode((cx + r, cy), GSCURVE),
                    GSNode((cx + r, cy - h), GSOFFCURVE),
                    GSNode((cx + h, cy - r), GSOFFCURVE),
                    GSNode((cx, cy - r), GSCURVE),
                    GSNode((cx - h, cy - r), GSOFFCURVE),
                    GSNode((cx - r, cy - h), GSOFFCURVE),
                    GSNode((cx - r, cy), GSCURVE),
                    GSNode((cx - r, cy + h), GSOFFCURVE),
                    GSNode((cx - h, cy + r), GSOFFCURVE),
                ]
                target.paths.append(p)

        glyph_counter = 0
        
        # PASS 1 — STRUCTURE
        for _ in range(STRUCTURE_PASSES):
            d = maxD
            sizeIndex = 0

            while d >= minD:
                r = d / 2
                placed = 0
                leftToRight = (sizeIndex % 2 == 0)

                y = bounds.origin.y
                while y < bounds.origin.y + bounds.size.height and placed < MAX_PER_SIZE:

                    if leftToRight:
                        x = bounds.origin.x
                        x_end = bounds.origin.x + bounds.size.width
                        x_step = STEP
                    else:
                        x = bounds.origin.x + bounds.size.width
                        x_end = bounds.origin.x
                        x_step = -STEP

                    while (x_step > 0 and x < x_end) or (x_step < 0 and x > x_end):
                        cx = x + r
                        cy = y + r

                        if (
                            respectsOutline(cx, cy, r)
                            and not overlaps(cx, cy, r)
                        ):
                            drawCircle(cx, cy, r, glyph_counter)
                            existing.append((cx, cy, r, glyph_counter))
                            placed += 1
                            glyph_counter += 1
                            if placed >= MAX_PER_SIZE:
                                break

                        x += x_step

                    y += STEP

                d -= SIZE_DROP
                sizeIndex += 1

        # PASS 2 — ADAPTIVE MAX-FIT
        d = maxD
        sizeIndex = 0

        while d >= minD:
            r = d / 2
            leftToRight = (sizeIndex % 2 == 0)

            y = bounds.origin.y
            while y < bounds.origin.y + bounds.size.height:

                if leftToRight:
                    x = bounds.origin.x
                    x_end = bounds.origin.x + bounds.size.width
                    x_step = STEP
                else:
                    x = bounds.origin.x + bounds.size.width
                    x_end = bounds.origin.x
                    x_step = -STEP

                while (x_step > 0 and x < x_end) or (x_step < 0 and x > x_end):
                    cx = x
                    cy = y

                    if (
                        respectsOutline(cx, cy, r)
                        and not overlaps(cx, cy, r)
                    ):
                        drawCircle(cx, cy, r, glyph_counter)
                        existing.append((cx, cy, r, glyph_counter))
                        glyph_counter += 1

                    x += x_step

                y += STEP

            d -= SIZE_DROP
            sizeIndex += 1

        if preview:
            layer.parent.layers.append(target)

        return len(existing)

    # =====================
    def run(self, preview=True):
        """Ejecuta el algoritmo en todas las capas según el modo seleccionado"""
        layers = self.get_target_layers()
        if not layers:
            print("[Fill TURBO] No hay capas para procesar")
            return

        minD = float(self.w.minDia.get())
        maxD = float(self.w.maxDia.get())
        safe = float(self.w.safeArea.get())

        total_elements = 0
        processed_layers = 0
        
        for layer in layers:
            if layer:
                elements = self.run_on_layer(layer, preview, minD, maxD, safe)
                total_elements += elements
                processed_layers += 1

        mode = self.w.modePopup.getItems()[self.w.modePopup.get()]
        master_name = "Unknown"
        font = Glyphs.font
        if font and font.masters:
            master_index = self.get_selected_master()
            if master_index < len(font.masters):
                master_name = font.masters[master_index].name
                
        glyph_info = ""
        if self.w.useGlyphsCheck.get():
            glyph_info = f", Usando {len(self.glyph_list)} glifos: {', '.join(self.glyph_list)}"
                
        print(f"[Fill TURBO] COMPLETADO - Modo: {mode}, Master: {master_name}{glyph_info}, Capas: {processed_layers}, Elementos totales: {total_elements}")

    # =====================
    def preview(self, sender):
        self.cleanup()
        self.run(preview=True)

    def apply(self, sender):
        self.cleanup()
        self.run(preview=False)

    def cleanup(self):
        """Limpia todas las capas de preview"""
        font = Glyphs.font
        if not font:
            return
            
        for glyph in font.glyphs:
            for layer in list(glyph.layers):
                if layer.name == "● Fill TURBO Preview":
                    glyph.layers.remove(layer)


# Ejecutar el script
FillCirclesTurbo()