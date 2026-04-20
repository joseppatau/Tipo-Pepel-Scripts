# MenuTitle: Multi-Master Preview PRO (Full & ⌘ Drag)
# -*- coding: utf-8 -*-

from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc
import os
import json

# Import explícit per a la gestió de ratolí i teclat
from AppKit import NSEvent, NSEventModifierFlagCommand, NSCursor

def log(msg):
    print(f"DEBUG: {msg}")

# --- Preferències ---
def get_prefs_path():
    try:
        folder = GSGlyphsInfo.applicationSupportPath()
    except:
        folder = os.path.expanduser("~/Library/Application Support/Glyphs 3")
    if not os.path.exists(folder): os.makedirs(folder)
    return os.path.join(folder, "MultiMasterPreviewConfig.json")

SUPPORT_PATH = get_prefs_path()

# 1. CLASSE DE PREVISUALITZACIÓ
try:
    DraggablePreviewView = objc.lookUpClass("DraggablePreviewView")
except:
    class DraggablePreviewView(NSView):
        def initWithFrame_(self, frame):
            self = objc.super(DraggablePreviewView, self).initWithFrame_(frame)
            if self is None: return None
            self.glyph_data = []
            self.zoom = 0.7
            self.vertical_offset = 300
            self.is_dragging = False
            self.drag_start = None
            return self

        def acceptsFirstResponder(self): return True
        def acceptsFirstMouse_(self, event): return True

        def drawRect_(self, rect):
            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())
            if not self.glyph_data: return
            
            x_cursor = 50
            v_base = self.vertical_offset 
            for item in self.glyph_data:
                if item['path']:
                    p = item['path'].copy()
                    scale = (400.0 / item['upm']) * self.zoom
                    baseline = v_base + (item['descender'] * scale)
                    t = NSAffineTransform.transform()
                    t.translateXBy_yBy_(x_cursor, baseline)
                    t.scaleBy_(scale)
                    p.transformUsingAffineTransform_(t)
                    NSColor.blackColor().set()
                    p.fill()
                    x_cursor += (item['width'] * scale) + (80 * self.zoom)

        def mouseDown_(self, event):
            if event.modifierFlags() & NSEventModifierFlagCommand:
                self.is_dragging = True
                self.drag_start = event.locationInWindow()
                NSCursor.closedHandCursor().set()
            else:
                self.is_dragging = False

        def mouseDragged_(self, event):
            if not self.is_dragging or self.drag_start is None: return
            sv = self.enclosingScrollView()
            if not sv: return
            current_pos = event.locationInWindow()
            dx = self.drag_start.x - current_pos.x
            dy = current_pos.y - self.drag_start.y
            origin = sv.contentView().bounds().origin
            new_origin = NSMakePoint(origin.x + dx, origin.y + dy)
            sv.contentView().scrollToPoint_(new_origin)
            sv.reflectScrolledClipView_(sv.contentView())
            self.drag_start = current_pos

        def mouseUp_(self, event):
            self.is_dragging = False
            NSCursor.arrowCursor().set()

class NSViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, view):
        self._posSize, self._nsObject = posSize, view
    def getNSView(self): return self._nsObject

# 2. FINESTRA PRINCIPAL
class MultiMasterPreviewPanel(object):
    def __init__(self):
        if not Glyphs.font: return
        self.font = Glyphs.font
        self.prefs = self.load_prefs()
        
        # Mida recuperada de prefs
        w_size = self.prefs.get('w', 1100)
        h_size = self.prefs.get('h', 600)
        
        self.w = Window((w_size, h_size), "Multi-Master Preview PRO", minSize=(800, 500))
        self.w.tabs = Tabs((10, 10, -10, -10), ["Preview", "Config"])
        
        # --- TAB PREVIEW ---
        tp = self.w.tabs[0]
        tp.zoom_txt = TextBox((15, 12, 45, 17), "Zoom:", sizeStyle='small')
        tp.zoom = Slider((60, 10, 100, 20), value=0.7, minValue=0.1, maxValue=2.0, callback=self.updateUI)
        
        # BOTONS ZOOM RECUPERATS
        tp.btn_minus = SquareButton((165, 8, 25, 23), "-", callback=self.zoomOut)
        tp.btn_plus = SquareButton((190, 8, 25, 23), "+", callback=self.zoomIn)
        
        tp.vert_txt = TextBox((235, 12, 60, 17), "Vertical:", sizeStyle='small')
        tp.verticalPos = Slider((295, 10, 150, 20), value=300, minValue=-500, maxValue=1500, callback=self.updateUI)
        
        tp.reset = Button((465, 8, 80, 23), "Reset", callback=self.resetView)

        self.scroll = NSScrollView.alloc().initWithFrame_(((0, 0), (1100, 500)))
        self.scroll.setHasHorizontalScroller_(True)
        self.scroll.setHasVerticalScroller_(True)
        self.view = DraggablePreviewView.alloc().initWithFrame_(((0, 0), (10000, 3000)))
        self.scroll.setDocumentView_(self.view)
        tp.preview = NSViewWrapper((0, 45, -0, -0), self.scroll)

        # --- TAB CONFIG ---
        tc = self.w.tabs[1]
        # Personalització de mida de finestra
        tc.lbl_w = TextBox((20, 20, 60, 17), "Width:")
        tc.edit_w = EditText((80, 18, 60, 22), str(int(w_size)))
        tc.lbl_h = TextBox((160, 20, 60, 17), "Height:")
        tc.edit_h = EditText((220, 18, 60, 22), str(int(h_size)))
        tc.apply_btn = Button((300, 18, 120, 22), "Apply & Save", callback=self.save_window_prefs)
        
        tc.line = HorizontalLine((20, 55, -20, 1))
        tc.lbl_m = TextBox((20, 65, 200, 17), "Visible Masters:")
        
        tc.masterList = ScrollView((15, 85, -15, -45), None, hasHorizontalScroller=False)
        self.master_items = []
        y_pos = 5
        saved_masters = self.prefs.get('visible_masters', [m.id for m in self.font.masters])
        
        for master in self.font.masters:
            is_on = master.id in saved_masters
            cb = CheckBox((15, y_pos, -20, 20), master.name, value=is_on, callback=self.updateContent)
            setattr(tc.masterList, f"cb_{master.id.replace('-','_')}", cb)
            self.master_items.append((master.id, cb))
            y_pos += 25
            
        tc.selectAll = Button((15, -35, 100, 20), "Select All", sizeStyle='small', callback=self.allAction)
        tc.deselectAll = Button((120, -35, 100, 20), "Deselect All", sizeStyle='small', callback=self.allAction)

        Glyphs.addCallback(self.updateContent, UPDATEINTERFACE)
        self.updateContent()
        self.updateUI(None)
        self.w.open()
        self.w.makeKey()

    def load_prefs(self):
        if os.path.exists(SUPPORT_PATH):
            try:
                with open(SUPPORT_PATH, "r") as f: return json.load(f)
            except: pass
        return {'w': 1100, 'h': 600, 'visible_masters': [m.id for m in self.font.masters]}

    def save_window_prefs(self, sender=None):
        try:
            new_w = int(self.w.tabs[1].edit_w.get())
            new_h = int(self.w.tabs[1].edit_h.get())
            self.w.setPosSize((self.w.getPosSize()[0], self.w.getPosSize()[1], new_w, new_h))
            self.save_all_prefs()
        except: pass

    def save_all_prefs(self):
        visible = [m_id for m_id, cb in self.master_items if cb.get()]
        curr = self.w.getPosSize()
        data = {'w': curr[2], 'h': curr[3], 'visible_masters': visible}
        with open(SUPPORT_PATH, "w") as f: json.dump(data, f)

    def allAction(self, sender):
        state = sender == self.w.tabs[1].selectAll
        for m_id, cb in self.master_items: cb.set(state)
        self.updateContent()

    def updateUI(self, sender):
        self.view.zoom = self.w.tabs[0].zoom.get()
        self.view.vertical_offset = self.w.tabs[0].verticalPos.get()
        self.view.setNeedsDisplay_(True)

    def zoomIn(self, sender):
        self.w.tabs[0].zoom.set(min(2.0, self.w.tabs[0].zoom.get() + 0.1))
        self.updateUI(None)

    def zoomOut(self, sender):
        self.w.tabs[0].zoom.set(max(0.1, self.w.tabs[0].zoom.get() - 0.1))
        self.updateUI(None)

    def resetView(self, sender):
        self.w.tabs[0].zoom.set(0.7)
        self.w.tabs[0].verticalPos.set(300)
        self.updateUI(None)
        self.scroll.contentView().scrollToPoint_(NSMakePoint(0, 50))

    def updateContent(self, sender=None):
        f = Glyphs.font
        if not f or not f.selectedLayers: return
        glyph = f.selectedLayers[0].parent
        new_data = []
        visible_ids = [m_id for m_id, cb in self.master_items if cb.get()]
        for m in f.masters:
            if m.id in visible_ids:
                l = glyph.layers[m.id]
                if l:
                    new_data.append({
                        'path': l.completeBezierPath.copy(),
                        'width': l.width,
                        'upm': f.upm if f.upm > 0 else 1000,
                        'descender': m.descender
                    })
        self.view.glyph_data = new_data
        self.view.setNeedsDisplay_(True)
        self.save_all_prefs()

    def windowWillClose(self, sender):
        Glyphs.removeCallback(self.updateContent, UPDATEINTERFACE)

MultiMasterPreviewPanel()