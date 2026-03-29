# MenuTitle:Delimit Zones
# -*- coding: utf-8 -*-
# Description: Creates and manages horizontal zones with visual overlays and node-edge highlighting for precise vertical control.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

from GlyphsApp import *
from AppKit import *
import objc
import json
import traceback
import random
import string
import math

# =====================================================
# ACOTE ZONES MANAGER
# =====================================================

# Generar un ID simple de letras y números
def generate_simple_id(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

session_id = generate_simple_id()
class_name = f"AcoteZonesManager{session_id}"

print(f"Creando clase: {class_name}")

# Definir la clase dinámicamente
AcoteZonesManagerClass = type(class_name, (NSObject,), {
    '__objc_name__': class_name,
    
    'init': lambda self: self._init(),
    '_init': None,  # Será definido después
})

# Ahora definimos los métodos de la clase
def init_method(self):
    self = objc.super(self.__class__, self).init()
    if self is None:
        return None
    
    self.zones = []
    self.callback_id = None
    self.glyph_callback_id = None  # Nuevo callback para nodos
    self.panel = None
    self.zones_table = None
    self.table_ds = None
    self._session_id = session_id
    self.highlight_nodes = True  # Controlar si se resaltan nodos
    self.node_circle_size = 15  # Tamaño del círculo (radio de 15 unidades)
    self.window_delegate = None  # Guardar referencia al delegado
    
    self.create_panel()
    
    # Crear zona diacritics automáticamente al iniciar
    self.create_diacritics_zone_auto()
    
    return self

# Asignar el método de inicialización
AcoteZonesManagerClass._init = init_method

# -------------------------------------------------
# ZONE CLASS (clase interna)
# -------------------------------------------------

class Zone:
    def __init__(self, y_min=500, y_max=600, color_hex="FFF4D0", visible=True, name="New Zone"):
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        self.color_hex = color_hex.upper().replace("#", "")
        self.visible = bool(visible)
        self.name = str(name)
    
    def nsColor(self):
        h = self.color_hex
        if len(h) != 6:
            h = "FFF4D0"
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 0.4)
    
    def contains_y(self, y, tolerance=0.5):
        """Verifica si un punto Y está dentro de la zona (incluyendo bordes)"""
        return self.y_min - tolerance <= y <= self.y_max + tolerance
    
    def is_on_edge(self, y, tolerance=0.5):
        """Verifica si un punto Y está exactamente en el borde de la zona"""
        return (abs(y - self.y_min) <= tolerance or 
                abs(y - self.y_max) <= tolerance)

# -------------------------------------------------
# DRAW CALLBACKS
# -------------------------------------------------

def draw_all_zones(self, layer, info):
    try:
        # Dibujar las zonas primero
        for z in self.zones:
            if not z.visible:
                continue
            z.nsColor().setFill()
            p = NSBezierPath.bezierPath()
            p.appendBezierPathWithRect_(
                NSMakeRect(-10000, z.y_min, 20000, z.y_max - z.y_min)
            )
            p.fill()
    except Exception:
        traceback.print_exc()

def draw_highlighted_nodes(self, layer, info):
    """Callback para resaltar nodos en los bordes de las zonas"""
    try:
        if not self.highlight_nodes:
            return
        
        # Buscar todos los nodos en el layer actual
        for path in layer.paths:
            for node in path.nodes:
                node_y = node.position.y
                
                # Verificar si el nodo está en el borde de alguna zona visible
                for zone in self.zones:
                    if zone.visible and zone.is_on_edge(node_y, tolerance=0.5):
                        # Dibujar un círculo rojo alrededor del nodo (más grande)
                        NSColor.redColor().setStroke()
                        NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 0.2).setFill()
                        
                        # Tamaño del círculo basado en self.node_circle_size
                        circle_size = self.node_circle_size
                        circle_rect = NSMakeRect(
                            node.position.x - circle_size,  # Radio de circle_size unidades
                            node_y - circle_size,
                            circle_size * 2,  # Diámetro
                            circle_size * 2
                        )
                        
                        circle = NSBezierPath.bezierPathWithOvalInRect_(circle_rect)
                        circle.fill()
                        
                        # Borde más grueso
                        circle.setLineWidth_(1.5)
                        NSColor.redColor().setStroke()
                        circle.stroke()
                        
                        # También dibujar un punto rojo más pequeño en el centro
                        NSColor.redColor().setFill()
                        center_circle = NSBezierPath.bezierPathWithOvalInRect_(
                            NSMakeRect(
                                node.position.x - 2,
                                node_y - 2,
                                4,
                                4
                            )
                        )
                        center_circle.fill()
                        
                        break
                        
    except Exception:
        traceback.print_exc()

AcoteZonesManagerClass.draw_all_zones = draw_all_zones
AcoteZonesManagerClass.draw_highlighted_nodes = draw_highlighted_nodes

# -------------------------------------------------
# UI METHODS
# -------------------------------------------------

def create_panel(self):
    w, h = 520, 480  # Aumentado para controles adicionales
    
    self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(0, 0, w, h),
        NSTitledWindowMask | NSClosableWindowMask,
        NSBackingStoreBuffered,
        False,
    )
    self.panel.setTitle_("Acote Zones")
    self.panel.center()
    
    # -------- Buttons (top)
    
    def button(x, y, title, action):
        b = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, 140, 24))
        b.setTitle_(title)
        b.setTarget_(self)
        b.setAction_(action)
        self.panel.contentView().addSubview_(b)
    
    button(20, 420, "Acote from selection", "acoteSelectedZone:")
    button(170, 420, "Add new zone", "addNewZone:")
    button(320, 420, "Delete selected", "deleteSelectedZone:")
    
    # -------- Controles para nodos
    node_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 385, 120, 22))
    node_label.setStringValue_("Node circle size:")
    node_label.setBezeled_(False)
    node_label.setDrawsBackground_(False)
    node_label.setEditable_(False)
    node_label.setSelectable_(False)
    self.panel.contentView().addSubview_(node_label)
    
    # Slider para tamaño del círculo
    self.node_size_slider = NSSlider.alloc().initWithFrame_(NSMakeRect(140, 385, 120, 22))
    self.node_size_slider.setMinValue_(5)
    self.node_size_slider.setMaxValue_(30)
    self.node_size_slider.setFloatValue_(self.node_circle_size)
    self.node_size_slider.setTarget_(self)
    self.node_size_slider.setAction_("nodeSizeChanged:")
    self.panel.contentView().addSubview_(self.node_size_slider)
    
    # Label para valor del slider
    self.node_size_label = NSTextField.alloc().initWithFrame_(NSMakeRect(270, 385, 40, 22))
    self.node_size_label.setStringValue_(str(int(self.node_circle_size)))
    self.node_size_label.setBezeled_(True)
    self.node_size_label.setEditable_(False)
    self.node_size_label.setSelectable_(False)
    self.node_size_label.setAlignment_(NSCenterTextAlignment)
    self.panel.contentView().addSubview_(self.node_size_label)
    
    # Checkbox para resaltar nodos
    highlight_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(320, 385, 180, 22))
    highlight_checkbox.setButtonType_(NSSwitchButton)
    highlight_checkbox.setTitle_("Highlight nodes on edges")
    highlight_checkbox.setState_(1 if self.highlight_nodes else 0)
    highlight_checkbox.setTarget_(self)
    highlight_checkbox.setAction_("toggleHighlightNodes:")
    self.panel.contentView().addSubview_(highlight_checkbox)
    
    # -------- Table
    
    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 90, 480, 280))
    scroll.setHasVerticalScroller_(True)
    
    self.zones_table = NSTableView.alloc().initWithFrame_(scroll.bounds())
    
    titles = ["Name", "Y Min", "Y Max", "Color", "Visible"]
    widths = [120, 60, 60, 80, 50]
    
    for i, t in enumerate(titles):
        col = NSTableColumn.alloc().initWithIdentifier_(str(i))
        col.setWidth_(widths[i])
        col.headerCell().setStringValue_(t)
        
        # Configurar celda especial para la columna "Visible" (checkbox)
        if i == 4:  # Columna "Visible"
            # Crear una celda de checkbox
            checkbox_cell = NSButtonCell.alloc().init()
            checkbox_cell.setButtonType_(NSSwitchButton)
            checkbox_cell.setTitle_("")
            checkbox_cell.setControlSize_(NSSmallControlSize)
            checkbox_cell.setRefusesFirstResponder_(True)
            col.setDataCell_(checkbox_cell)
        else:
            # Para otras columnas, usar celda de texto normal
            text_cell = NSTextFieldCell.alloc().init()
            text_cell.setEditable_(True)
            if i == 1 or i == 2:  # Columnas Y Min y Y Max
                # Formateador para números
                formatter = NSNumberFormatter.alloc().init()
                formatter.setNumberStyle_(NSNumberFormatterDecimalStyle)
                formatter.setMinimumFractionDigits_(0)
                formatter.setMaximumFractionDigits_(0)
                text_cell.setFormatter_(formatter)
            col.setDataCell_(text_cell)
        
        self.zones_table.addTableColumn_(col)
    
    # Hacer que todas las columnas excepto Visible sean editables
    for i in [0, 1, 2, 3]:  # Name, Y Min, Y Max, Color
        col = self.zones_table.tableColumns()[i]
        cell = col.dataCell()
        cell.setEditable_(True)
    
    # Crear clase de datos de tabla con nombre único
    table_ds_class_name = f"TableDataSource{session_id}"
    
    # Definir la clase de datos de tabla dinámicamente
    TableDataSourceClass = type(table_ds_class_name, (NSObject,), {
        '__objc_name__': table_ds_class_name,
        
        'initWithManager_': lambda self, manager: self._initWithManager_(manager),
        '_initWithManager_': None,
    })
    
    def init_with_manager(self, manager):
        self = objc.super(self.__class__, self).init()
        if self:
            self.manager = manager
        return self
    
    TableDataSourceClass._initWithManager_ = init_with_manager
    
    def number_of_rows(self, tv):
        return len(self.manager.zones)
    
    def object_value_for_table_column(self, tv, col, row):
        z = self.manager.zones[row]
        c = int(col.identifier())
        if c == 0:
            return z.name
        elif c == 1:
            return z.y_min
        elif c == 2:
            return z.y_max
        elif c == 3:
            return z.color_hex
        elif c == 4:
            return z.visible
        return ""
    
    def set_object_value_for_table_column(self, tv, value, col, row):
        z = self.manager.zones[row]
        c = int(col.identifier())
        if c == 0:
            z.name = str(value)
        elif c == 1:
            try:
                z.y_min = float(value)
            except:
                pass
        elif c == 2:
            try:
                z.y_max = float(value)
            except:
                pass
        elif c == 3:
            z.color_hex = str(value).upper().replace("#", "")
        elif c == 4:
            # Cambiar el estado de visibilidad
            z.visible = bool(value)
        # Redibujar la vista para reflejar los cambios
        Glyphs.redraw()
        self.manager.zones_table.reloadData()
    
    TableDataSourceClass.numberOfRowsInTableView_ = number_of_rows
    TableDataSourceClass.tableView_objectValueForTableColumn_row_ = object_value_for_table_column
    TableDataSourceClass.tableView_setObjectValue_forTableColumn_row_ = set_object_value_for_table_column
    
    self.table_ds = TableDataSourceClass.alloc().initWithManager_(self)
    self.zones_table.setDataSource_(self.table_ds)
    self.zones_table.setDelegate_(self.table_ds)
    
    scroll.setDocumentView_(self.zones_table)
    self.panel.contentView().addSubview_(scroll)
    
    # -------- Bottom buttons
    
    button(20, 30, "Save zones", "saveZones:")
    button(180, 30, "Load zones", "loadZones:")
    button(340, 30, "Refresh All", "refreshAll:")
    
    # -------- Inicializar sin zonas por defecto
    self.zones = []  # Lista vacía, sin zonas predeterminadas
    
    self.zones_table.reloadData()
    self.panel.orderFront_(None)
    
    self.activateDrawing()

AcoteZonesManagerClass.create_panel = create_panel

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------

def find_circumflexcomb_glyph(self):
    """Buscar el glifo 'circumflexcomb' en la fuente"""
    font = Glyphs.font
    if not font:
        print("No hay fuente abierta")
        return None
    
    # Buscar el glifo por nombre
    glyph = font.glyphs["circumflexcomb"]
    if not glyph:
        print("No se encontró el glifo 'circumflexcomb'")
        # Intentar buscar con nombre alternativo
        glyph = font.glyphs["circumflexcomb.case"]
        if not glyph:
            print("Tampoco se encontró 'circumflexcomb.case'")
            return None
    
    print(f"Glifo 'circumflexcomb' encontrado: {glyph.name}")
    return glyph

def get_glyph_bounds(self, glyph, master_id=None):
    """Obtener los límites de un glifo en un master específico"""
    try:
        if not glyph:
            return None
        
        font = Glyphs.font
        if not font:
            return None
        
        # Si no se especifica master_id, usar el master actual
        if master_id is None:
            current_layer = font.selectedLayers[0] if font.selectedLayers else None
            if current_layer:
                master_id = current_layer.associatedMasterId
            else:
                master_id = font.masters[0].id
        
        # Buscar el layer del glifo para este master
        target_layer = None
        for layer in glyph.layers:
            if layer.associatedMasterId == master_id:
                target_layer = layer
                break
        
        if not target_layer:
            print(f"No se encontró layer para master {master_id}, usando el primero")
            target_layer = glyph.layers[0]
        
        # Obtener los límites del trazado
        bounds = target_layer.bounds
        print(f"Bounds del glifo {glyph.name}: y={bounds.origin.y}, height={bounds.size.height}")
        
        if bounds.size.width == 0 or bounds.size.height == 0:
            print(f"Bounds vacíos para el glifo {glyph.name}")
            return None
        
        return bounds
        
    except Exception as e:
        print(f"Error obteniendo bounds del glifo: {e}")
        traceback.print_exc()
        return None

def create_diacritics_zone_auto(self):
    """Crear zona diacritics automáticamente al iniciar basada en circumflexcomb"""
    print(f"\n=== Creando zona diacritics automática ===")
    
    # Buscar el glifo circumflexcomb
    glyph = self.find_circumflexcomb_glyph()
    if not glyph:
        print("No se encontró circumflexcomb, no se creará zona diacritics automática")
        return
    
    # Obtener los límites del glifo
    bounds = self.get_glyph_bounds(glyph)
    if not bounds:
        print("No se pudieron obtener límites de circumflexcomb")
        return
    
    y_min = bounds.origin.y
    y_max = bounds.origin.y + bounds.size.height
    
    print(f"Límites del circumflexcomb: min_y={y_min}, max_y={y_max}")
    
    # Crear la zona diacritics
    self.zones.append(
        Zone(y_min, y_max, "FFB6C1", True, "Diacritics")
    )
    
    print(f"Zona diacritics creada automáticamente")
    
    # Actualizar la tabla si ya existe
    if hasattr(self, 'zones_table') and self.zones_table:
        self.zones_table.reloadData()
        Glyphs.redraw()

def get_selected_nodes_bounds(self, layer):
    """Obtener los límites Y de los nodos seleccionados"""
    min_y = None
    max_y = None
    
    print(f"Analizando selección en layer: {layer.parent.name}")
    print(f"Total elementos seleccionados: {len(layer.selection)}")
    
    for item in layer.selection:
        if isinstance(item, GSNode):
            y = item.position.y
            print(f"Nodo seleccionado: y={y}")
            if min_y is None or y < min_y:
                min_y = y
            if max_y is None or y > max_y:
                max_y = y
        
        elif isinstance(item, GSPath):
            print(f"Path seleccionado, tiene {len(item.nodes)} nodos")
            for node in item.nodes:
                y = node.position.y
                if min_y is None or y < min_y:
                    min_y = y
                if max_y is None or y > max_y:
                    max_y = y
        
        elif isinstance(item, GSComponent):
            print(f"Componente seleccionado: {item.componentName}")
            # Obtener bounds del componente
            bounds = self.get_component_bounds(item)
            if bounds:
                comp_min_y = bounds.origin.y
                comp_max_y = bounds.origin.y + bounds.size.height
                print(f"Bounds del componente: min_y={comp_min_y}, max_y={comp_max_y}")
                if min_y is None or comp_min_y < min_y:
                    min_y = comp_min_y
                if max_y is None or comp_max_y > max_y:
                    max_y = comp_max_y
    
    return min_y, max_y

def get_component_bounds(self, component):
    """Obtener los límites de un componente en el contexto actual"""
    try:
        # Obtener el glifo maestro
        master_glyph = component.component
        if not master_glyph:
            return None
        
        # Obtener el layer actual
        font = Glyphs.font
        current_layer = font.selectedLayers[0] if font.selectedLayers else None
        if not current_layer:
            return None
        
        # Obtener los bounds del glifo maestro
        master_bounds = master_glyph.layers[current_layer.associatedMasterId].bounds
        
        # Aplicar transformación del componente
        transform = component.transform
        
        # Transformar los puntos de los bounds
        x1 = master_bounds.origin.x
        y1 = master_bounds.origin.y
        x2 = x1 + master_bounds.size.width
        y2 = y1 + master_bounds.size.height
        
        # Aplicar transformación
        tx1 = x1 * transform[0] + y1 * transform[1] + transform[4]
        ty1 = x1 * transform[2] + y1 * transform[3] + transform[5]
        tx2 = x2 * transform[0] + y2 * transform[1] + transform[4]
        ty2 = x2 * transform[2] + y2 * transform[3] + transform[5]
        
        min_x = min(tx1, tx2)
        max_x = max(tx1, tx2)
        min_y = min(ty1, ty2)
        max_y = max(ty1, ty2)
        
        return NSRect(min_x, min_y, max_x - min_x, max_y - min_y)
        
    except Exception as e:
        print(f"Error obteniendo bounds del componente: {e}")
        traceback.print_exc()
        return None

# -------------------------------------------------
# ACTION METHODS
# -------------------------------------------------

def acote_selected_zone(self, sender):
    """Crear zona basada en la selección actual"""
    font = Glyphs.font
    if not font or not font.selectedLayers:
        print("No hay fuente o layer seleccionado")
        return
    
    layer = font.selectedLayers[0]
    print(f"\n=== ACOTE FROM SELECTION ===")
    print(f"Glifo: {layer.parent.name}")
    print(f"Master: {layer.associatedMasterId}")
    
    if not layer.selection:
        print("No hay elementos seleccionados en el layer")
        return
    
    # Obtener límites Y de los elementos seleccionados
    min_y, max_y = self.get_selected_nodes_bounds(layer)
    
    if min_y is None or max_y is None:
        print("No se pudieron determinar los límites de la selección")
        return
    
    print(f"Límites encontrados: min_y={min_y}, max_y={max_y}")
    
    # Contar zonas existentes con nombre "Selected"
    selected_count = sum(1 for z in self.zones if z.name.startswith("Selected"))
    zone_name = f"Selected {selected_count + 1}" if selected_count > 0 else "Selected"
    
    # Crear la nueva zona
    self.zones.append(
        Zone(min_y, max_y, "FF9999", True, zone_name)
    )
    
    print(f"Zona creada: {zone_name} ({min_y} - {max_y})")
    
    # Actualizar UI
    self.zones_table.reloadData()
    Glyphs.redraw()

def add_new_zone(self, sender):
    """Añadir una nueva zona vacía"""
    new_count = sum(1 for z in self.zones if z.name.startswith("New Zone"))
    zone_name = f"New Zone {new_count + 1}" if new_count > 0 else "New Zone"
    
    self.zones.append(Zone(visible=True, name=zone_name))
    self.zones_table.reloadData()
    Glyphs.redraw()
    print(f"Nueva zona añadida: {zone_name}")

def delete_selected_zone(self, sender):
    r = self.zones_table.selectedRow()
    if r >= 0:
        zone_name = self.zones[r].name
        del self.zones[r]
        print(f"Zona eliminada: {zone_name}")
        self.zones_table.reloadData()
        Glyphs.redraw()

def save_zones(self, sender):
    p = NSSavePanel.savePanel()
    p.setAllowedFileTypes_(["json"])
    if p.runModal() == 1:
        with open(p.URL().path(), "w") as f:
            # Guardar todos los atributos de las zonas
            zones_data = []
            for z in self.zones:
                zones_data.append({
                    'name': z.name,
                    'y_min': z.y_min,
                    'y_max': z.y_max,
                    'color_hex': z.color_hex,
                    'visible': z.visible
                })
            json.dump(zones_data, f, indent=2)
        print(f"Zonas guardadas en: {p.URL().path()}")

def load_zones(self, sender):
    p = NSOpenPanel.openPanel()
    p.setAllowedFileTypes_(["json"])
    if p.runModal() == 1:
        with open(p.URL().path(), "r") as f:
            data = json.load(f)
        self.zones = [Zone(**d) for d in data]
        self.zones_table.reloadData()
        Glyphs.redraw()
        print(f"Zonas cargadas desde: {p.URL().path()}")

def toggle_highlight_nodes(self, sender):
    """Alternar la visualización de nodos resaltados"""
    self.highlight_nodes = bool(sender.state())
    print(f"Highlight nodes: {self.highlight_nodes}")
    Glyphs.redraw()

def node_size_changed(self, sender):
    """Cambiar el tamaño del círculo de nodos"""
    self.node_circle_size = sender.floatValue()
    self.node_size_label.setStringValue_(str(int(self.node_circle_size)))
    print(f"Tamaño de círculo cambiado a: {self.node_circle_size}")
    Glyphs.redraw()

def refresh_all(self, sender):
    """Refrescar todas las vistas"""
    print("Refrescando todas las vistas")
    self.zones_table.reloadData()
    Glyphs.redraw()

# Asignar métodos de acción
AcoteZonesManagerClass.acoteSelectedZone_ = acote_selected_zone
AcoteZonesManagerClass.addNewZone_ = add_new_zone
AcoteZonesManagerClass.deleteSelectedZone_ = delete_selected_zone
AcoteZonesManagerClass.saveZones_ = save_zones
AcoteZonesManagerClass.loadZones_ = load_zones
AcoteZonesManagerClass.toggleHighlightNodes_ = toggle_highlight_nodes
AcoteZonesManagerClass.nodeSizeChanged_ = node_size_changed
AcoteZonesManagerClass.refreshAll_ = refresh_all
AcoteZonesManagerClass.find_circumflexcomb_glyph = find_circumflexcomb_glyph
AcoteZonesManagerClass.get_glyph_bounds = get_glyph_bounds
AcoteZonesManagerClass.create_diacritics_zone_auto = create_diacritics_zone_auto
AcoteZonesManagerClass.get_selected_nodes_bounds = get_selected_nodes_bounds
AcoteZonesManagerClass.get_component_bounds = get_component_bounds

# -------------------------------------------------
# CALLBACK METHODS
# -------------------------------------------------

def activate_drawing(self):
    """Activar todos los callbacks de dibujo"""
    if self.callback_id is None:
        self.callback_id = Glyphs.addCallback(
            self.draw_all_zones, DRAWBACKGROUND
        )
        print("Callback de zonas activado")
    
    # Añadir callback para resaltar nodos (en primer plano)
    if self.glyph_callback_id is None:
        self.glyph_callback_id = Glyphs.addCallback(
            self.draw_highlighted_nodes, DRAWFOREGROUND
        )
        print("Callback de nodos activado")

def deactivate_drawing(self):
    """Desactivar callbacks cuando se cierra la ventana"""
    if self.callback_id is not None:
        try:
            Glyphs.removeCallback(self.callback_id)
            self.callback_id = None
            print("Callback de zonas desactivado")
        except:
            pass
    
    if self.glyph_callback_id is not None:
        try:
            Glyphs.removeCallback(self.glyph_callback_id)
            self.glyph_callback_id = None
            print("Callback de nodos desactivado")
        except:
            pass

AcoteZonesManagerClass.activateDrawing = activate_drawing
AcoteZonesManagerClass.deactivateDrawing = deactivate_drawing

# -------------------------------------------------
# WINDOW DELEGATE METHODS
# -------------------------------------------------

def window_will_close(self, notification):
    """Manejar el cierre de la ventana - llamar al manager para desactivar callbacks"""
    print("Cerrando ventana, desactivando callbacks...")
    # Obtener el manager desde el objeto window
    window = notification.object()
    if window and hasattr(window, 'manager'):
        window.manager.deactivateDrawing()

# Crear una clase delegada para la ventana
WindowDelegateClass = type(f"WindowDelegate{session_id}", (NSObject,), {
    '__objc_name__': f"WindowDelegate{session_id}",
    
    'initWithManager_': lambda self, manager: self._initWithManager_(manager),
    '_initWithManager_': None,
    'windowWillClose_': window_will_close,
})

def init_window_delegate(self, manager):
    """Inicializar el delegado con referencia al manager"""
    self = objc.super(self.__class__, self).init()
    if self:
        self.manager = manager
    return self

WindowDelegateClass._initWithManager_ = init_window_delegate

# =====================================================
# RUN (safe re-exec)
# =====================================================

try:
    # Cerrar ventana anterior si existe
    if 'manager' in globals():
        try:
            if hasattr(manager, 'deactivateDrawing'):
                manager.deactivateDrawing()
            if hasattr(manager, 'panel') and manager.panel:
                manager.panel.close()
        except:
            pass
    
    # Crear nueva instancia
    manager = AcoteZonesManagerClass.alloc().init()
    if manager:
        # Crear delegado con referencia al manager
        window_delegate = WindowDelegateClass.alloc().initWithManager_(manager)
        manager.panel.setDelegate_(window_delegate)
        
        # Guardar referencia al delegado en el manager para mantenerlo vivo
        manager.window_delegate = window_delegate
        
        manager.retain()  # Mantener la referencia al manager
        print(f"Manager creado exitosamente con ID: {session_id}")
    else:
        print("Error: No se pudo crear la instancia del manager")
        
except Exception as e:
    print(f"Error ejecutando script: {e}")
    traceback.print_exc()