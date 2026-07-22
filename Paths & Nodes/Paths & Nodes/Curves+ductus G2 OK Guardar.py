# MenuTitle: Fit Curve & Ductus PRO (Slope Lock + Green Harmony G2)
# -*- coding: utf-8 -*-

from vanilla import FloatingWindow, TextBox, Slider, CheckBox, HorizontalLine, EditText, Button
import GlyphsApp
from GlyphsApp import Glyphs, GSNode, OFFCURVE, CURVE, GSSMOOTH, GSPath
from Foundation import NSPoint
import math

# --- FUNCIONS G2 GREEN HARMONY ---

def getIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    try:
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
        return px, py
    except:
        return None, None

def getDist(a, b):
    return math.sqrt((b.x - a.x)**2 + (b.y - a.y)**2)

def remap(oldValue, oldMin, oldMax, newMin, newMax):
    try:
        oldRange = (oldMax - oldMin)
        newRange = (newMax - newMin)
        newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
        return newValue
    except:
        return None

def harmonize_G2(layer, path_idx, node_idx):
    path = layer.paths[path_idx]
    node = path.nodes[node_idx]
    
    # Segons el teu script: N, P (handles), NN, PP (on-curves següents)
    N = node.nextNode
    P = node.prevNode
    NN = N.nextNode
    PP = P.prevNode

    if not (N.type == OFFCURVE and P.type == OFFCURVE):
        return

    # Trobar intersecció de les línies dels handles
    xInt, yInt = getIntersection(N.x, N.y, NN.x, NN.y, P.x, P.y, PP.x, PP.y)
    
    if xInt is not None:
        intersection = NSPoint(xInt, yInt)
        r0 = getDist(NN, N) / getDist(N, intersection)
        r1 = getDist(intersection, P) / getDist(P, PP)
        ratio = math.sqrt(r0 * r1)

        t = ratio / (ratio + 1)
        node.x = remap(t, 0, 1, N.x, P.x)
        node.y = remap(t, 0, 1, N.y, P.y)
        node.connection = GSSMOOTH

# --- CLASSE PRINCIPAL ---

class FitCurveDuctusG2Green:
    def __init__(self):
        self.w = FloatingWindow((175, 420), "Fit Curve & Ductus PRO + G2")
        
        y = 15
        self.w.t1 = TextBox((10, y, 80, 17), "Smooth %", sizeStyle='small')
        self.w.sliderAbs = Slider((10, 40, 150, 17), value=61, minValue=0, maxValue=100, callback=self.ui_callback)
        self.w.valAbs = EditText((130, y-4, 30, 22), "61", callback=self.edit_text_callback, sizeStyle='small')
        
        y += 30
        self.w.t2 = TextBox((10, 65, 80, 17), "Delta %", sizeStyle='small')
        self.w.sliderRel = Slider((10, 85, 150, 17), value=0, minValue=-50, maxValue=50, callback=self.ui_callback)
        self.w.valRel = EditText((130, 60, 30, 22), "0", callback=self.edit_text_callback, sizeStyle='small')

        y += 35
        self.w.line1 = HorizontalLine((10, 115, -10, 1))

        y += 15
        self.w.t3 = TextBox((10, 130, 100, 17), "Ductus H (X)", sizeStyle='small')
        self.w.sliderDuctusH = Slider((10, 150, 150, 17), value=0, minValue=-100, maxValue=100, callback=self.ui_callback)
        self.w.valDuctusH = EditText((130, 125, 30, 22), "0", callback=self.edit_text_callback, sizeStyle='small')
        
        y += 30
        self.w.t4 = TextBox((10, 180, 100, 17), "Ductus V (Y)", sizeStyle='small')
        self.w.sliderDuctusV = Slider((10, 200, 150, 17), value=0, minValue=-100, maxValue=100, callback=self.ui_callback)
        self.w.valDuctusV = EditText((130, 175, 30, 22), "0", callback=self.edit_text_callback, sizeStyle='small')

        y += 40
        self.w.line2 = HorizontalLine((10, 230, -10, 1))

        y += 15
        self.w.syncAll = CheckBox((10, 240, 120, 20), "Sync Masters", value=True, sizeStyle='small')
        self.w.btnRefresh = Button((10, 270, 150, 20), "TOTAL RESET", callback=self.manual_reset, sizeStyle='small')
        
        y += 35
        self.w.btnG2 = Button((10, 295, 150, 25), "APPLY G2", callback=self.apply_g2_logic)

        self.master_memories = {} 
        self.last_selection = None
        
        Glyphs.addCallback(self.auto_refresh, "GSUpdateInterface")
        self.refresh_references()
        self.w.bind("close", self.remove_callbacks)
        self.w.open()

    def remove_callbacks(self, sender):
        Glyphs.removeCallback(self.auto_refresh)

    def auto_refresh(self, sender):
        font = Glyphs.font
        if font and font.selectedLayers:
            layer = font.selectedLayers[0]
            current_sel_id = [n.index for n in layer.selection if isinstance(n, GSNode)]
            if current_sel_id != self.last_selection:
                self.last_selection = current_sel_id
                self.refresh_references()

    def refresh_references(self):
        font = Glyphs.font
        if not font or not font.selectedLayers: return
        active_layer = font.selectedLayers[0]
        self.master_memories = {}
        
        targets = []
        for p_idx, path in enumerate(active_layer.paths):
            for n_idx, node in enumerate(path.nodes):
                if node.selected:
                    if node.type == CURVE:
                        h_in, h_out = path.nodes[n_idx-1], path.nodes[(n_idx+1)%len(path.nodes)]
                        for h in [h_in, h_out]:
                            if h.type == OFFCURVE:
                                dx, dy = h.x - node.x, h.y - node.y
                                eix, dir = ('H', (1 if dx > 0 else -1)) if abs(dx) > abs(dy) else ('V', (1 if dy > 0 else -1))
                                targets.append({'type': 'ductus', 'p': p_idx, 'n': n_idx, 'eix': eix, 'dir': dir})
                                break
                    elif node.type == OFFCURVE:
                        owner = path.nodes[n_idx-1] if path.nodes[n_idx-1].type != OFFCURVE else path.nodes[(n_idx+1)%len(path.nodes)]
                        step = 1 if path.nodes[n_idx-1].type != OFFCURVE else -1
                        t_idx = None
                        for j in range(1,4):
                            idx = (n_idx + (j*step)) % len(path.nodes)
                            if path.nodes[idx].type != OFFCURVE:
                                t_idx = idx
                                break
                        targets.append({'type': 'fit', 'p': p_idx, 'n': n_idx, 'owner_idx': owner.index, 'target_idx': t_idx})

        for layer in active_layer.parent.layers:
            if layer.isMasterLayer or layer.isSpecialLayer:
                m_id = layer.layerId
                self.master_memories[m_id] = []
                for t in targets:
                    try:
                        node = layer.paths[t['p']].nodes[t['n']]
                        mem = t.copy()
                        mem['orig_x'], mem['orig_y'] = node.x, node.y
                        if t['type'] == 'fit':
                            owner = layer.paths[t['p']].nodes[t['owner_idx']]
                            mem['orig_rel_x'], mem['orig_rel_y'] = node.x - owner.x, node.y - owner.y
                        self.master_memories[m_id].append(mem)
                    except: pass

    def apply_to_layer(self, layer, ratio, dH, dV):
        m_id = layer.layerId
        if m_id not in self.master_memories: return
        for m in self.master_memories[m_id]:
            if m['type'] == 'ductus':
                node = layer.paths[m['p']].nodes[m['n']]
                if m['eix'] == 'H': node.x = m['orig_x'] + (-m['dir'] * dH)
                elif m['eix'] == 'V': node.y = m['orig_y'] + (-m['dir'] * dV)
        
        for m in self.master_memories[m_id]:
            if m['type'] == 'fit':
                path = layer.paths[m['p']]
                node, owner, target = path.nodes[m['n']], path.nodes[m['owner_idx']], path.nodes[m['target_idx']]
                dx_seg, dy_seg = target.x - owner.x, target.y - owner.y
                if abs(m['orig_rel_x']) > abs(m['orig_rel_y']):
                    node.x = owner.x + (dx_seg * ratio)
                    if abs(m['orig_rel_x']) > 0: node.y = owner.y + ((node.x - owner.x) * (m['orig_rel_y'] / m['orig_rel_x']))
                else:
                    node.y = owner.y + (dy_seg * ratio)
                    if abs(m['orig_rel_y']) > 0: node.x = owner.x + ((node.y - owner.y) * (m['orig_rel_x'] / m['orig_rel_y']))

    def apply_g2_logic(self, sender):
        font = Glyphs.font
        if not font: return
        font.disableUpdateInterface()
        for layer in font.selectedLayers:
            layers = [layer] if not self.w.syncAll.get() else [l for l in layer.parent.layers if l.isMasterLayer or l.isSpecialLayer]
            for l in layers:
                # Trobar quins nodes estan seleccionats per la seva posició/índex
                for p_idx, path in enumerate(l.paths):
                    for n_idx, node in enumerate(path.nodes):
                        if node.selected and node.type == CURVE:
                            harmonize_G2(l, p_idx, n_idx)
        font.enableUpdateInterface()
        Glyphs.redraw()

    def manual_reset(self, sender):
        self.w.sliderAbs.set(61); self.w.valAbs.set("61")
        self.w.sliderRel.set(0); self.w.valRel.set("0")
        self.w.sliderDuctusH.set(0); self.w.valDuctusH.set("0")
        self.w.sliderDuctusV.set(0); self.w.valDuctusV.set("0")
        self.refresh_references(); self.ui_callback(None)

    def edit_text_callback(self, sender):
        try:
            self.w.sliderAbs.set(float(self.w.valAbs.get()))
            self.w.sliderRel.set(float(self.w.valRel.get()))
            self.ui_callback(None)
        except: pass

    def ui_callback(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers: return
        if sender in [self.w.sliderAbs, self.w.sliderRel, self.w.sliderDuctusH, self.w.sliderDuctusV]:
            self.w.valAbs.set(str(int(self.w.sliderAbs.get())))
            self.w.valRel.set(str(int(self.w.sliderRel.get())))
            self.w.valDuctusH.set(str(int(self.w.sliderDuctusH.get())))
            self.w.valDuctusV.set(str(int(self.w.sliderDuctusV.get())))
        
        ratio = (self.w.sliderAbs.get() / 100.0) * (1.0 + (self.w.sliderRel.get() / 100.0))
        dH, dV = self.w.sliderDuctusH.get(), self.w.sliderDuctusV.get()
        
        font.disableUpdateInterface()
        for active_layer in font.selectedLayers:
            self.apply_to_layer(active_layer, ratio, dH, dV)
            if self.w.syncAll.get():
                for layer in active_layer.parent.layers:
                    if layer.layerId != active_layer.layerId and (layer.isMasterLayer or layer.isSpecialLayer):
                        self.apply_to_layer(layer, ratio, dH, dV)
        font.enableUpdateInterface()
        Glyphs.redraw()

FitCurveDuctusG2Green()