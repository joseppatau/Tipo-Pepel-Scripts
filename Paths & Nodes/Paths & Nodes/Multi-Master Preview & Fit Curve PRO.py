# MenuTitle: Multi-Master Fit Curve & Ductus PRO
# -*- coding: utf-8 -*-

from vanilla import *
from GlyphsApp import *
from AppKit import *
import objc
import traceback
import math
import json
import os

DEBUG = True

def log(msg):
    if DEBUG:
        print(f"[FitCurve] {msg}")

# --- CONFIGURACIÓN DE RUTAS ---
def get_prefs_path():
    try:
        folder = GSGlyphsInfo.applicationSupportPath()
    except:
        folder = os.path.expanduser("~/Library/Application Support/Glyphs 3")
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, "MultiMasterFitConfig.json")

SUPPORT_PATH = get_prefs_path()

# --- CLASE DE PREVISUALIZACIÓN (NSView) ---
try:
    SimpleGlyphPreviewView = objc.lookUpClass("SimpleGlyphPreviewView")
except:
    class SimpleGlyphPreviewView(NSView):
        def initWithFrame_(self, frame):
            self = objc.super(SimpleGlyphPreviewView, self).initWithFrame_(frame)
            if self is None: return None
            self.glyph_data = []
            self.zoom = 0.7
            self.is_dragging = False
            self.drag_start_x = 0
            self.drag_start_y = 0
            self.visible_masters = []
            return self

        def acceptsFirstResponder(self): return True

        def drawRect_(self, rect):
            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())
            
            if not self.glyph_data: return

            x_cursor = 50
            v_height = self.bounds().size.height
            
            for item in self.glyph_data:
                if self.visible_masters and item.get('master_id') not in self.visible_masters:
                    continue
                    
                path = item['path'].copy()
                scale = (400.0 / item['upm']) * self.zoom
                baseline = (v_height / 2.0) + (item['descender'] * scale)
                
                t = NSAffineTransform.transform()
                t.translateXBy_yBy_(x_cursor, baseline)
                t.scaleBy_(scale)
                path.transformUsingAffineTransform_(t)
                
                NSColor.blackColor().set()
                path.fill()
                
                x_cursor += (item['width'] * scale) + (80 * self.zoom)

        def mouseDown_(self, event):
            if event.modifierFlags() & (NSEventModifierFlagOption | NSEventModifierFlagCommand):
                self.is_dragging = True
                self.drag_start_x = event.locationInWindow().x
                self.drag_start_y = event.locationInWindow().y
                NSCursor.closedHandCursor().set()

        def mouseDragged_(self, event):
            if not self.is_dragging: return
            sv = self.enclosingScrollView()
            if not sv: return
            cur = event.locationInWindow()
            dx = self.drag_start_x - cur.x
            dy = cur.y - self.drag_start_y
            origin = sv.contentView().bounds().origin
            new_origin = NSMakePoint(origin.x + dx, origin.y + dy)
            sv.contentView().scrollToPoint_(new_origin)
            sv.reflectScrolledClipView_(sv.contentView())
            self.drag_start_x, self.drag_start_y = cur.x, cur.y

        def mouseUp_(self, event):
            self.is_dragging = False
            NSCursor.arrowCursor().set()

class NSViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, view):
        self._posSize, self._nsObject = posSize, view
    def getNSView(self): return self._nsObject

# --- CLASE PRINCIPAL UNIFICADA ---
class MultiMasterFitCurveDuctus(object):

    def __init__(self):
        if not Glyphs.font:
            return
        
        self.font = Glyphs.font
    
        # Cargar preferencias
        self.prefs = self.load_prefs()
    
        # Ventana principal
        self.w = Window(
            (self.prefs.get('w', 950), self.prefs.get('h', 700)),
            "Multi-Master Fit Curve & Ductus PRO",
            minSize=(800, 500)
        )
    
        # Crear tabs
        self.w.tabs = Tabs((10, 10, -10, -10), ["Fit Curve & Ductus", "Preview Config"])
    
        # ===== TAB 1: FIT CURVE & DUCTUS =====
        self.tab1 = self.w.tabs[0]
    
        # Panel de controles (ancho 150)
        self.control_panel = Group((0, 0, 150, -0))
    
        y = 10
    
        # SMOOTH %
        self.control_panel.t1 = TextBox((10, y, 60, 17), "Smooth %", sizeStyle='small')
        self.control_panel.sliderAbs = Slider((10, y+18, 100, 20), value=61, minValue=0, maxValue=100, callback=self.smooth_callback)
        self.control_panel.editAbs = EditText((115, y+16, 30, 22), "61", callback=self.smooth_edit_callback, sizeStyle='small')

        y += 50

        # DELTA %
        self.control_panel.t2 = TextBox((10, y, 60, 17), "Delta %", sizeStyle='small')
        self.control_panel.sliderRel = Slider((10, y+18, 100, 20), value=0, minValue=-50, maxValue=50, callback=self.smooth_callback)
        self.control_panel.editRel = EditText((115, y+16, 30, 22), "0", callback=self.smooth_edit_callback, sizeStyle='small')

        y += 50
        self.control_panel.line1 = HorizontalLine((10, y, 130, 1))

        y += 15

        # DUCTUS HORIZONTAL (X)
        self.control_panel.t3 = TextBox((10, y, 100, 17), "Ductus H (X)", sizeStyle='small')
        self.control_panel.sliderDuctusH = Slider((10, y+18, 100, 20), value=0, minValue=-100, maxValue=100, callback=self.ductus_callback)
        self.control_panel.editDuctusH = EditText((115, y+16, 30, 22), "0", callback=self.ductus_edit_callback, sizeStyle='small')

        y += 50

        # DUCTUS VERTICAL (Y)
        self.control_panel.t4 = TextBox((10, y, 100, 17), "Ductus V (Y)", sizeStyle='small')
        self.control_panel.sliderDuctusV = Slider((10, y+18, 100, 20), value=0, minValue=-100, maxValue=100, callback=self.ductus_callback)
        self.control_panel.editDuctusV = EditText((115, y+16, 30, 22), "0", callback=self.ductus_edit_callback, sizeStyle='small')

        y += 50
        self.control_panel.line2 = HorizontalLine((10, y, 130, 1))

        y += 15

        # DESPLAÇAMENT VERTICAL
        self.control_panel.t5 = TextBox((10, y, 100, 17), "Despl. Vertical", sizeStyle='small')
        self.control_panel.sliderVerticalSel = Slider((10, y+18, 100, 20), value=0, minValue=-100, maxValue=100, callback=self.vertical_sel_callback)
        self.control_panel.editVerticalSel = EditText((115, y+16, 30, 22), "0", callback=self.vertical_sel_edit_callback, sizeStyle='small')

        y += 50
        self.control_panel.line3 = HorizontalLine((10, y, 130, 1))

        y += 15

        # DESPLAÇAMENT HORIZONTAL
        self.control_panel.t6 = TextBox((10, y, 100, 17), "Despl. Horizontal", sizeStyle='small')
        self.control_panel.sliderHorizontalSel = Slider((10, y+18, 100, 20), value=0, minValue=-100, maxValue=100, callback=self.horizontal_sel_callback)
        self.control_panel.editHorizontalSel = EditText((115, y+16, 30, 22), "0", callback=self.horizontal_sel_edit_callback, sizeStyle='small')

        y += 50
        self.control_panel.line4 = HorizontalLine((10, y, 130, 1))

        y += 15

        # INFO TEXT
        self.control_panel.infoText = TextBox((10, y, 130, 80), "Detectant handles...", sizeStyle='small')

        y += 85

        # SYNC CHECKBOX
        self.control_panel.syncAll = CheckBox((10, y, 130, 20), "Sync all Masters", value=True, callback=self.sync_checkbox_callback)
    
        y += 25
        self.control_panel.debugBtn = Button((10, y, 130, 20), "Debug", callback=self.debug_show_status)
    
        y += 30
    
        # ZOOM CONTROLS
        self.control_panel.zoom_label = TextBox((10, y, 130, 17), "Preview Zoom", sizeStyle='small')
        y += 20
        self.control_panel.zoom_slider = Slider((10, y, 100, 20), value=self.prefs.get('zoom', 0.7), minValue=0.2, maxValue=2.0, callback=self.update_zoom)
        self.control_panel.zoom_minus = SquareButton((115, y-2, 15, 22), "-", callback=self.zoom_out)
        self.control_panel.zoom_plus = SquareButton((132, y-2, 15, 22), "+", callback=self.zoom_in)
    
        # Añadir control panel al tab1
        self.tab1.control_panel = self.control_panel
    
        # ===== PREVIEW en TAB1 =====
        # Scroll view para el preview
        scroll_frame = ((160, 0), (780, 680))
        self.scroll = NSScrollView.alloc().initWithFrame_(scroll_frame)
        self.scroll.setHasHorizontalScroller_(True)
        self.scroll.setHasVerticalScroller_(True)
        self.scroll.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
    
        self.view = SimpleGlyphPreviewView.alloc().initWithFrame_(((0, 0), (14800, 800)))
        self.view.zoom = self.prefs.get('zoom', 0.7)
        self.view.visible_masters = self.prefs.get('visible_masters', [])
    
        self.scroll.setDocumentView_(self.view)
    
        # Wrapper para el scroll view
        self.tab1.preview = NSViewWrapper((160, 0, -0, -0), self.scroll)
    
        # ===== TAB 2: PREVIEW CONFIG =====
        self.tab2 = self.w.tabs[1]
    
        # Configuración de ventana
        self.tab2.window_label = TextBox((20, 20, 150, 17), "Window Size:", sizeStyle='small')
        self.tab2.w_label = TextBox((20, 45, 40, 17), "Width:", sizeStyle='small')
        self.tab2.w_edit = EditText((60, 43, 60, 22), str(int(self.w.getPosSize()[2])), callback=self.save_window_size)
        self.tab2.h_label = TextBox((140, 45, 40, 17), "Height:", sizeStyle='small')
        self.tab2.h_edit = EditText((180, 43, 60, 22), str(int(self.w.getPosSize()[3])), callback=self.save_window_size)
        self.tab2.apply_btn = Button((260, 43, 80, 22), "Apply", callback=self.apply_window_size)
    
        # Separador
        self.tab2.line1 = HorizontalLine((20, 80, -20, 1))
    
        # Masters visibles
        self.tab2.masters_label = TextBox((20, 95, 200, 17), "Masters to display:", sizeStyle='small')
    
        self.master_checkboxes = []
        y_pos = 120
    
        # Crear un grupo simple para los checkboxes sin ScrollView
        self.master_list_group = Group((20, y_pos, 400, 350))
    
        y_list = 0
        saved_visible = self.prefs.get('visible_masters', [])
        self.visible_master_ids = saved_visible.copy()
    
        for master in self.font.masters:
            is_visible = master.id in saved_visible
            cb = CheckBox((10, y_list, 380, 20), master.name, value=is_visible, callback=self.update_visible_masters)
            setattr(self.master_list_group, f"cb_{master.id.replace('-', '_').replace('.', '_')}", cb)
            self.master_checkboxes.append((master.id, cb))
            y_list += 25
    
        self.tab2.master_list_group = self.master_list_group
    
        # Botones de selección
        btn_y = y_pos + 360
        self.tab2.select_all_btn = Button((20, btn_y, 100, 22), "Select All", callback=self.select_all_masters)
        self.tab2.select_none_btn = Button((130, btn_y, 100, 22), "Select None", callback=self.select_none_masters)
    
        # Variables de estado
        self.memory = {}
        self.nodes_horitzontals = []
        self.nodes_verticals = []
        self.memory_by_master = {}
        self.nodes_horitzontals_by_master = {}
        self.nodes_verticals_by_master = {}
    
        # Stem widths
        self.stem_widths_by_master = {}
        self.current_master_stem_width = None
    
        self.last_selection_signature = None
        self.vertical_memory = {}
        self.horizontal_memory = {}
        self.last_glyph_name = None
        self.last_master_name = None
        self.last_ductus_h = 0
        self.last_ductus_v = 0
    
        # Inicializar
        self.init_stem_widths()
        self.detectar_handles()

        self.update_preview_content()
        self.center_preview()
    
    
        # Callbacks
        log("Registering callbacks...")
        try:
            Glyphs.addCallback(self.glyph_changed_callback, "GSGlyphContentsDidChangeNotification")
            Glyphs.addCallback(self.current_glyph_changed_callback, "GSSelectionDidChangeNotification")
            log("Callbacks registered successfully")
        except Exception as e:
            log(f"Error registering callbacks: {e}")
            traceback.print_exc()
    
        # Configurar ventana y abrir
        self.w.bind("close", self.windowWillClose)
        self.w.open()
    
        # Actualizar contenido inicial
        self.update_preview_content()
    
        # Seleccionar primer tab
        self.w.tabs.set(0)

    def load_prefs(self):
        if os.path.exists(SUPPORT_PATH):
            try:
                with open(SUPPORT_PATH, "r") as f:
                    data = json.load(f)
                    # Asegurar que visible_masters existe
                    if 'visible_masters' not in data and Glyphs.font:
                        data['visible_masters'] = [m.id for m in Glyphs.font.masters]
                    return data
            except:
                pass
        # Si no hay preferencias, mostrar todos los masters
        all_masters = [m.id for m in Glyphs.font.masters] if Glyphs.font else []
        return {'w': 950, 'h': 700, 'zoom': 0.7, 'visible_masters': all_masters}

    def save_prefs(self):
        if hasattr(self, 'w') and hasattr(self, 'view'):
            data = {
                'w': self.w.getPosSize()[2],
                'h': self.w.getPosSize()[3],
                'zoom': self.view.zoom,
                'visible_masters': self.visible_master_ids
            }
            try:
                with open(SUPPORT_PATH, "w") as f:
                    json.dump(data, f)
            except:
                pass

    def save_window_size(self, sender):
        pass  # Solo guardamos al aplicar
    
    def apply_window_size(self, sender):
        try:
            new_w = int(self.tab2.w_edit.get())
            new_h = int(self.tab2.h_edit.get())
            self.w.setPosSize((self.w.getPosSize()[0], self.w.getPosSize()[1], new_w, new_h))
            self.save_prefs()
        except:
            pass

    def windowWillClose(self, sender):
        self.save_prefs()
        Glyphs.removeCallback(self.glyph_changed_callback, "GSGlyphContentsDidChangeNotification")
        Glyphs.removeCallback(self.current_glyph_changed_callback, "GSSelectionDidChangeNotification")

    # ===== MÉTODOS DE CONFIGURACIÓN DE MASTERS =====
    def update_visible_masters(self, sender):
        """Actualizar qué masters son visibles en el preview"""
        self.visible_master_ids = [mid for mid, cb in self.master_checkboxes if cb.get()]
        self.view.visible_masters = self.visible_master_ids
        self.view.setNeedsDisplay_(True)
        self.save_prefs()

    def select_all_masters(self, sender):
        for mid, cb in self.master_checkboxes:
            cb.set(True)
        self.update_visible_masters(None)

    def select_none_masters(self, sender):
        for mid, cb in self.master_checkboxes:
            cb.set(False)
        self.update_visible_masters(None)

    # ===== MÉTODOS DE ZOOM =====
    def update_zoom(self, sender):
        self.view.zoom = self.control_panel.zoom_slider.get()
        self.view.setNeedsDisplay_(True)
        self.update_preview_content()

    def zoom_in(self, sender):
        current = self.control_panel.zoom_slider.get()
        new_val = min(2.0, current + 0.1)
        self.control_panel.zoom_slider.set(new_val)
        self.update_zoom(None)

    def zoom_out(self, sender):
        current = self.control_panel.zoom_slider.get()
        new_val = max(0.2, current - 0.1)
        self.control_panel.zoom_slider.set(new_val)
        self.update_zoom(None)

    # ===== MÉTODOS DE PREVIEW =====
    def update_preview_content(self):
        f = Glyphs.font
        if not f or not f.selectedLayers:
            return
        
        glyph = f.selectedLayers[0].parent
        if not glyph:
            return
        
        new_data = []
        
        for m in f.masters:
            layer = glyph.layers[m.id]
            if layer:
                new_data.append({
                    'path': layer.completeBezierPath.copy(),
                    'width': layer.width,
                    'upm': f.upm if f.upm > 0 else 1000,
                    'descender': m.descender,
                    'master_id': m.id,
                    'master_name': m.name
                })
        
        self.view.glyph_data = new_data
        self.view.setNeedsDisplay_(True)
        
        
        
    def center_preview(self):
        if not self.view.glyph_data:
            return

        # calcular bounding box aproximat
        min_x, max_x = 99999, -99999
        min_y, max_y = 99999, -99999

        for item in self.view.glyph_data:
            path = item['path']
            bounds = path.bounds()

            min_x = min(min_x, bounds.origin.x)
            max_x = max(max_x, bounds.origin.x + bounds.size.width)
            min_y = min(min_y, bounds.origin.y)
            max_y = max(max_y, bounds.origin.y + bounds.size.height)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        clip = self.scroll.contentView()

        # ajust visual (trial & error perquè hi ha escala)
        scroll_point = NSMakePoint(center_x, center_y)

        clip.scrollToPoint_(scroll_point)
        self.scroll.reflectScrolledClipView_(clip)
        
        
        

    # ===== MÉTODOS DE STEM WIDTH =====
    def init_stem_widths(self):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            return
            
        stem_values = {
            "Black": 213.0,
            "Black Condensed": 213.0,
            "Black Contrast": 213.0,
            "Black Contrast Condensed": 213.0,
            "Fine": 63.0,
            "Fine Condensed": 63.0,
            "Fine contrast": 63.0,
            "Fine contrast Condensed": 63.0,
            "Hair": 8.0,
            "Hair Condensed": 8.0,
            "Hair2": 8.0,
            "Hair2 Condensed": 8.0,
        }
        
        current_layer = font.selectedLayers[0]
        if current_layer and current_layer.parent:
            for layer in current_layer.parent.layers:
                if layer and layer.master:
                    master_name = layer.master.name
                    master_id = layer.master.id
                    clean_name = master_name.strip()
                    
                    if clean_name in stem_values:
                        self.stem_widths_by_master[master_id] = stem_values[clean_name]
                    else:
                        found = False
                        for key in stem_values:
                            if key in clean_name or clean_name in key:
                                self.stem_widths_by_master[master_id] = stem_values[key]
                                found = True
                                break
                        if not found:
                            self.stem_widths_by_master[master_id] = 100.0
        
        current_master_id = current_layer.master.id
        self.current_master_stem_width = self.stem_widths_by_master.get(current_master_id, 100.0)

    def get_scaled_ductus_value(self, target_master_id, original_value):
        if not self.control_panel.syncAll.get():
            return original_value
        
        current_width = self.current_master_stem_width
        target_width = self.stem_widths_by_master.get(target_master_id, current_width)
        
        if current_width <= 0:
            return original_value
        
        scale_factor = target_width / current_width
        return original_value * scale_factor

    def get_layers_to_process(self):
        font = Glyphs.font
        if not font or not font.selectedLayers or len(font.selectedLayers) == 0:
            return []
        
        if self.control_panel.syncAll.get():
            layer = font.selectedLayers[0]
            if not layer or not layer.parent:
                return []
            glyph = layer.parent
            if glyph and hasattr(glyph, 'layers'):
                unique_layers = {}
                for l in glyph.layers:
                    if l and l.master:
                        unique_layers[l.master.id] = l
                return list(unique_layers.values())
            else:
                return []
        else:
            return font.selectedLayers

    # ===== MÉTODOS DE HANDLES =====
    def obtenir_handles_node(self, nodes, idx, es_path_tancat):
        handle_in = None
        handle_out = None
        num_nodes = len(nodes)
        
        if idx >= len(nodes) or nodes[idx].type != 'curve':
            return None, None
        
        if es_path_tancat and num_nodes >= 6:
            prev_idx = (idx - 1) % num_nodes
            prev2_idx = (idx - 2) % num_nodes
            next_idx = (idx + 1) % num_nodes
            next2_idx = (idx + 2) % num_nodes
            
            if prev2_idx < len(nodes) and nodes[prev_idx].type == 'offcurve' and nodes[prev2_idx].type == 'offcurve':
                offcurve = nodes[prev2_idx]
                dx = offcurve.x - nodes[idx].x
                dy = offcurve.y - nodes[idx].y
                if dx != 0 or dy != 0:
                    handle_in = (dx, dy)
            
            if next2_idx < len(nodes) and nodes[next_idx].type == 'offcurve' and nodes[next2_idx].type == 'offcurve':
                offcurve = nodes[next2_idx]
                dx = offcurve.x - nodes[idx].x
                dy = offcurve.y - nodes[idx].y
                if dx != 0 or dy != 0:
                    handle_out = (dx, dy)
        else:
            if idx >= 2:
                if nodes[idx-1].type == 'offcurve' and nodes[idx-2].type == 'offcurve':
                    offcurve = nodes[idx-2]
                    dx = offcurve.x - nodes[idx].x
                    dy = offcurve.y - nodes[idx].y
                    if dx != 0 or dy != 0:
                        handle_in = (dx, dy)
            
            if idx + 2 < num_nodes:
                if nodes[idx+1].type == 'offcurve' and nodes[idx+2].type == 'offcurve':
                    offcurve = nodes[idx+2]
                    dx = offcurve.x - nodes[idx].x
                    dy = offcurve.y - nodes[idx].y
                    if dx != 0 or dy != 0:
                        handle_out = (dx, dy)
        
        return handle_in, handle_out
        
    def get_selection_signature(self, layer):
        if not layer or not layer.paths:
            return None
        ids = []
        for path in layer.paths:
            for node in path.nodes:
                if node.selected:
                    ids.append(id(node))
        return (layer.parent.name if layer.parent else None, 
                layer.master.name if layer.master else None, 
                tuple(ids))

    def classificar_handle(self, dx, dy):
        if abs(dx) > abs(dy):
            return 'horitzontal'
        elif abs(dy) > abs(dx):
            return 'vertical'
        else:
            return 'diagonal'

    def detectar_handles(self):
        try:
            font = Glyphs.font
            if not font or not font.selectedLayers or len(font.selectedLayers) == 0:
                self.control_panel.infoText.set("Selecciona una lletra")
                return
        
            layers = self.get_layers_to_process()
            if not layers:
                self.control_panel.infoText.set("Selecciona una lletra")
                return
            
            self.nodes_horitzontals = []
            self.nodes_verticals = []
            
            for layer in layers:
                if not layer or not layer.master:
                    continue
                    
                master_id = layer.master.id
                master_name = layer.master.name
                
                if not layer.paths:
                    log(f"{master_name}: no paths")
                    self.nodes_horitzontals_by_master[master_id] = []
                    self.nodes_verticals_by_master[master_id] = []
                    continue
                
                nodes_hor = []
                nodes_ver = []
            
                for path in layer.paths:
                    nodes = path.nodes
                    es_tancat = path.closed
                
                    for i, node in enumerate(nodes):
                        if node.type != 'curve':
                            continue
                    
                        handle_in, handle_out = self.obtenir_handles_node(nodes, i, es_tancat)
                    
                        tipus_final = None
                        direccio = 0
                    
                        for handle in [handle_in, handle_out]:
                            if not handle:
                                continue
                        
                            dx, dy = handle
                            tipus = self.classificar_handle(dx, dy)

                            if tipus == 'horitzontal':
                                tipus_final = 'horitzontal'
                                direccio = 1 if dx > 0 else -1
                                break

                            elif tipus == 'vertical' and tipus_final != 'horitzontal':
                                tipus_final = 'vertical'
                                direccio = 1 if dy > 0 else -1
                    
                        if tipus_final == 'horitzontal':
                            nodes_hor.append({
                                'node': node,
                                'direccio': direccio,
                                'x_original': node.x,
                                'y_original': node.y
                            })

                        elif tipus_final == 'vertical':
                            nodes_ver.append({
                                'node': node,
                                'direccio': direccio,
                                'x_original': node.x,
                                'y_original': node.y
                            })
                
                self.nodes_horitzontals_by_master[master_id] = nodes_hor
                self.nodes_verticals_by_master[master_id] = nodes_ver
                log(f"{master_name}: H:{len(nodes_hor)} V:{len(nodes_ver)}")
                
                if layer == font.selectedLayers[0]:
                    self.nodes_horitzontals = nodes_hor
                    self.nodes_verticals = nodes_ver
        
            self.update_info_text()
        
        except Exception as e:
            self.control_panel.infoText.set(f"Error: {str(e)}")
            log(f"Error: {e}")
            traceback.print_exc()

    def update_info_text(self):
        stem_info = f"\nStem: {self.current_master_stem_width:.1f}" if self.current_master_stem_width else ""
        sync_status = f"Sync: {'ON' if self.control_panel.syncAll.get() else 'OFF'}"
        masters_count = len(self.stem_widths_by_master)
        
        self.control_panel.infoText.set(
            f"Handles hor: {len(self.nodes_horitzontals)}\n"
            f"Handles ver: {len(self.nodes_verticals)}\n"
            f"{sync_status}{stem_info}\n"
            f"Masters: {masters_count}"
        )

    def aplicar_desplacament_hor(self, valor_percent, master_id=None):
        if master_id:
            nodes_hor = self.nodes_horitzontals_by_master.get(master_id, [])
        else:
            nodes_hor = self.nodes_horitzontals
        
        for item in nodes_hor:
            node = item['node']
            direccio = item['direccio']
            node.x = item['x_original'] + (-direccio * valor_percent)

    def aplicar_desplacament_ver(self, valor_percent, master_id=None):
        if master_id:
            nodes_ver = self.nodes_verticals_by_master.get(master_id, [])
        else:
            nodes_ver = self.nodes_verticals
        
        for item in nodes_ver:
            node = item['node']
            direccio = item['direccio']
            node.y = item['y_original'] + (-direccio * valor_percent)

    def store(self, layer):
        if not layer:
            return
            
        master_id = layer.master.id if layer.master else "default"
        master_name = layer.master.name if layer.master else "Unknown"
        memory = {}

        for path in layer.paths:
            for node in path.nodes:
                if node.type != "offcurve" or not node.selected:
                    continue

                prev = node.prevNode
                next = node.nextNode

                if not prev or not next:
                    continue

                if prev.type != "offcurve":
                    owner = prev
                    target = next.nextNode if next.type == "offcurve" else next
                else:
                    owner = next
                    target = prev.prevNode if prev.type == "offcurve" else prev

                if not owner or not target:
                    continue

                axis = "y" if abs(node.y - owner.y) < 2 else "x"

                memory[id(node)] = {
                    "handle": node,
                    "owner": owner,
                    "target": target,
                    "axis": axis,
                    "ox": owner.x,
                    "oy": owner.y,
                    "tx": target.x,
                    "ty": target.y
                }
        
        if memory:
            self.memory_by_master[master_id] = memory
            log(f"Stored {len(memory)} handles for {master_name}")

    def apply(self, layer, ratio):
        if not layer:
            return
            
        master_id = layer.master.id if layer.master else "default"
        memory = self.memory_by_master.get(master_id, {})
        
        for data in memory.values():
            try:
                owner = data["owner"]
                target = data["target"]
                handle = data["handle"]

                if owner.parent is None or target.parent is None:
                    continue

                dx = target.x - owner.x
                dy = target.y - owner.y

                if data["axis"] == "y":
                    handle.x = owner.x + dx * ratio
                    handle.y = owner.y
                else:
                    handle.y = owner.y + dy * ratio
                    handle.x = owner.x

            except Exception as e:
                log(f"ERROR applying smooth: {e}")

    # ===== MÉTODOS DE CALLBACK =====
    def check_glyph_master_change(self):
        font = Glyphs.font
        if not font or not font.selectedLayers or len(font.selectedLayers) == 0:
            return False
        
        layer = font.selectedLayers[0]
        if not layer or not layer.parent or not layer.master:
            return False
            
        current_glyph_name = layer.parent.name
        current_master_name = layer.master.name
        
        if (current_glyph_name != self.last_glyph_name) or (current_master_name != self.last_master_name):
            self.last_glyph_name = current_glyph_name
            self.last_master_name = current_master_name
            
            current_master_id = layer.master.id
            self.current_master_stem_width = self.stem_widths_by_master.get(current_master_id, 100.0)
            
            self.reset_all_state()
            return True
        return False
        
    def glyph_changed_callback(self, notification):
        self.reset_all_state()
        self.update_preview_content()
        
    def current_glyph_changed_callback(self, notification):
        self.reset_all_state()
        self.update_preview_content()
        
    def reset_all_state(self):
        self.control_panel.sliderAbs.set(61)
        self.control_panel.editAbs.set("61")
        self.control_panel.sliderRel.set(0)
        self.control_panel.editRel.set("0")
        self.control_panel.sliderDuctusH.set(0)
        self.control_panel.editDuctusH.set("0")
        self.control_panel.sliderDuctusV.set(0)
        self.control_panel.editDuctusV.set("0")
        self.control_panel.sliderVerticalSel.set(0)
        self.control_panel.editVerticalSel.set("0")
        self.control_panel.sliderHorizontalSel.set(0)
        self.control_panel.editHorizontalSel.set("0")
        
        self.memory = {}
        self.memory_by_master = {}
        self.nodes_horitzontals = []
        self.nodes_verticals = []
        self.nodes_horitzontals_by_master = {}
        self.nodes_verticals_by_master = {}
        self.vertical_memory = {}
        self.horizontal_memory = {}
        self.last_selection_signature = None
        
        self.detectar_handles()
        self.update_info_text()
        
        font = Glyphs.font
        if font and font.selectedLayers and len(font.selectedLayers) > 0:
            font.disableUpdateInterface()
            s_abs = self.control_panel.sliderAbs.get()
            s_rel = self.control_panel.sliderRel.get()
            ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)
            
            layers = self.get_layers_to_process()
            for layer in layers:
                if layer:
                    self.store(layer)
                    self.apply(layer, ratio)
            font.enableUpdateInterface()
            Glyphs.redraw()

    def sync_checkbox_callback(self, sender):
        log(f"Sync all Masters changed to: {sender.get()}")
        self.reset_all_state()
        self.update_preview_content()

    # ===== MÉTODOS DE UI =====
    def smooth_edit_callback(self, sender):
        try:
            val = float(sender.get())
            if sender == self.control_panel.editAbs: 
                self.control_panel.sliderAbs.set(val)
            elif sender == self.control_panel.editRel: 
                self.control_panel.sliderRel.set(val)
            self.smooth_callback(None)
        except:
            pass

    def smooth_callback(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers or len(font.selectedLayers) == 0:
            return

        self.check_glyph_master_change()

        s_abs = self.control_panel.sliderAbs.get()
        s_rel = self.control_panel.sliderRel.get()
        
        self.control_panel.editAbs.set(f"{s_abs:g}")
        self.control_panel.editRel.set(f"{s_rel:g}")

        ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)

        font.disableUpdateInterface()

        layers = self.get_layers_to_process()
        if not layers:
            font.enableUpdateInterface()
            return
            
        current_layer = font.selectedLayers[0]
        current_master_id = current_layer.master.id
        
        for layer in layers:
            if not layer or not layer.master:
                continue
                
            master_id = layer.master.id
            
            dH = self.control_panel.sliderDuctusH.get()
            dV = self.control_panel.sliderDuctusV.get()
            
            if master_id == current_master_id or not self.control_panel.syncAll.get():
                scaled_dH = dH
                scaled_dV = dV
            else:
                scaled_dH = self.get_scaled_ductus_value(master_id, dH)
                scaled_dV = self.get_scaled_ductus_value(master_id, dV)
            
            self.aplicar_desplacament_hor(scaled_dH, master_id=master_id)
            self.aplicar_desplacament_ver(scaled_dV, master_id=master_id)
            self.apply(layer, ratio)

        font.enableUpdateInterface()
        Glyphs.redraw()
        self.update_preview_content()

    def ductus_edit_callback(self, sender):
        try:
            val = float(sender.get())
            if sender == self.control_panel.editDuctusH: 
                self.control_panel.sliderDuctusH.set(val)
            elif sender == self.control_panel.editDuctusV: 
                self.control_panel.sliderDuctusV.set(val)
            self.ductus_callback(None)
        except:
            pass

    def ductus_callback(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers or len(font.selectedLayers) == 0:
            return
        
        self.check_glyph_master_change()
        
        dH = self.control_panel.sliderDuctusH.get()
        dV = self.control_panel.sliderDuctusV.get()
        
        self.control_panel.editDuctusH.set(f"{dH:g}")
        self.control_panel.editDuctusV.set(f"{dV:g}")
        
        font.disableUpdateInterface()
        
        layers = self.get_layers_to_process()
        if not layers:
            font.enableUpdateInterface()
            return
            
        current_layer = font.selectedLayers[0]
        if not current_layer or not current_layer.master:
            font.enableUpdateInterface()
            return
            
        current_master_id = current_layer.master.id
        
        for layer in layers:
            if not layer or not layer.master:
                continue
                
            master_id = layer.master.id
            
            if master_id == current_master_id or not self.control_panel.syncAll.get():
                scaled_dH = dH
                scaled_dV = dV
            else:
                scaled_dH = self.get_scaled_ductus_value(master_id, dH)
                scaled_dV = self.get_scaled_ductus_value(master_id, dV)
            
            self.aplicar_desplacament_hor(scaled_dH, master_id=master_id)
            self.aplicar_desplacament_ver(scaled_dV, master_id=master_id)
            
            s_abs = self.control_panel.sliderAbs.get()
            s_rel = self.control_panel.sliderRel.get()
            ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)
            
            self.apply(layer, ratio)
        
        font.enableUpdateInterface()
        Glyphs.redraw()
        self.update_preview_content()
        
    def vertical_sel_edit_callback(self, sender):
        try:
            val = float(sender.get())
            self.control_panel.sliderVerticalSel.set(val)
            self.vertical_sel_callback(None)
        except:
            pass
        

        
    def vertical_sel_edit_callback(self, sender):
        try:
            val = float(sender.get())
            self.control_panel.sliderVerticalSel.set(val)
            self.vertical_sel_callback(None)
        except: pass
        
        

    def vertical_sel_callback(self, sender):
        if not self.nodes_verticals: 
            print("DEBUG V: No vertical handles")
            return

        val = self.control_panel.sliderVerticalSel.get()
        print(f"DEBUG V: slider={val}")

        font = Glyphs.font
        font.disableUpdateInterface()

        # INVERSO: slider positivo → mueve negativo
        delta = -val
        print(f"DEBUG V: delta inverso={delta}")

        for i, item in enumerate(self.nodes_verticals):
            orig = item['y_original']
            new_y = orig + delta
            item['node'].y = new_y

            if i < 5:
                print(f"DEBUG V nodo{i}: orig={orig} → new={new_y}")

        self.control_panel.editVerticalSel.set(f"{val:g}")

        font.enableUpdateInterface()
        Glyphs.redraw()
        self.update_preview_content()
    
    
    
    
    def horizontal_sel_callback(self, sender):
        if not self.nodes_horitzontals: 
            print("DEBUG H: No horizontal handles")
            return

        val = self.control_panel.sliderHorizontalSel.get()
        print(f"DEBUG H: slider={val}")

        font = Glyphs.font
        font.disableUpdateInterface()

        # INVERSO: slider positivo → mueve negativo
        delta = -val
        print(f"DEBUG H: delta inverso={delta}")

        for i, item in enumerate(self.nodes_horitzontals):
            orig = item['x_original']
            new_x = orig + delta
            item['node'].x = new_x

            if i < 5:
                print(f"DEBUG H nodo{i}: orig={orig} → new={new_x}")

        self.control_panel.editHorizontalSel.set(f"{val:g}")

        font.enableUpdateInterface()
        Glyphs.redraw()
        self.update_preview_content()        
        

    def horizontal_sel_edit_callback(self, sender):
        try:
            val = float(sender.get())
            self.control_panel.sliderHorizontalSel.set(val)
            self.horizontal_sel_callback(None)
        except: pass
        
        
        



        
        
        
        
        

    def debug_show_status(self, sender):
        print("\n" + "="*80)
        print("DEBUG: MASTER STATUS")
        print("="*80)
        
        font = Glyphs.font
        if not font:
            print("No font open")
            return
        
        if not font.selectedLayers or len(font.selectedLayers) == 0:
            print("No layer selected")
            return
        
        current_layer = font.selectedLayers[0]
        current_master_name = current_layer.master.name if current_layer.master else "Unknown"
        
        print(f"\n📌 CURRENT MASTER: {current_master_name}")
        print(f"   Stem width: {self.current_master_stem_width}")
        print(f"   Sync enabled: {self.control_panel.syncAll.get()}")
        
        print(f"\n📊 ALL MASTERS IN GLYPH:")
        print("-" * 70)
        print(f"{'Master Name':<35} {'Stem Width':<12} {'Handles H/V':<15}")
        print("-" * 70)
        
        if current_layer and current_layer.parent:
            for layer in current_layer.parent.layers:
                if layer and layer.master:
                    master_name = layer.master.name
                    stem = self.stem_widths_by_master.get(layer.master.id, "NOT SET")
                    hor_count = len(self.nodes_horitzontals_by_master.get(layer.master.id, []))
                    ver_count = len(self.nodes_verticals_by_master.get(layer.master.id, []))
                    print(f"{master_name:<35} {str(stem):<12} {hor_count}/{ver_count}")
        
        print("\n" + "="*80 + "\n")

# Ejecutar
MultiMasterFitCurveDuctus()