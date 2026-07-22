# MenuTitle: Corner Tool Pro (SMART SYNC FIX)
import GlyphsApp
from GlyphsApp import GSNode, GSHint, CORNER
from vanilla import FloatingWindow, List, Button, TextBox, CheckBox, EditText
from AppKit import NSTimer

font = Glyphs.font

def getAllCornerComponents(font):
    return sorted([g.name for g in font.glyphs if g.name.startswith("_corner.")])

def extractNodeRefs(layer):
    if not layer: return []
    shapes = getattr(layer, 'shapes', layer.paths)
    refs = []
    for sIndex, shape in enumerate(shapes):
        if hasattr(shape, 'nodes'):
            for nIndex, node in enumerate(shape.nodes):
                if node.selected:
                    refs.append((sIndex, nIndex))
    return refs

class CornerTool(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            raise RuntimeError("No font open.")
        self.corners = getAllCornerComponents(self.font)
        self.cachedSelection = [] 
        
        self.w = FloatingWindow((360, 680), "Corner Tool Pro 🔥")
        self.w.status = TextBox((10, 10, -10, 20), "Ready")
        
        self.w.autoRefresh = CheckBox((10, 35, 100, 18), "Auto Select", value=True, sizeStyle='small')
        self.w.conserveScale = CheckBox((110, 35, 110, 18), "Conserve Scale", value=True, sizeStyle='small')
        self.w.allMasters = CheckBox((225, 35, 120, 18), "Apply All Masters", value=False, sizeStyle='small')
        
        self.w.debugLog = CheckBox((10, 55, 90, 18), "Debug Log", value=False, sizeStyle='small')
        self.w.refreshBtn = Button((250, 55, 90, 22), "🔄 Force", callback=self.manualRefresh)
        
        self.w.nodesInfo = TextBox((10, 80, -10, 18), "Nodes: 0")

        self.w.list = List((10, 105, -10, -240), self.corners, allowsMultipleSelection=True, doubleClickCallback=self.apply)

        y_off = -230
        self.w.customScale = CheckBox((10, y_off, 100, 18), "Apply Scale:", value=True, sizeStyle='small')
        self.w.txt_h = TextBox((110, y_off, 20, 17), "↔")
        self.w.scale_x = EditText((130, y_off-2, 45, 20), "100", sizeStyle='small')
        self.w.txt_v = TextBox((185, y_off, 20, 17), "↕")
        self.w.scale_y = EditText((205, y_off-2, 45, 20), "100", sizeStyle='small')
        self.w.percent = TextBox((255, y_off, 20, 17), "%")

        self.w.applyBtn = Button((10, -205, -10, 30), "Apply Corner", callback=self.apply)
        self.w.deleteBtn = Button((10, -170, -10, 25), "🗑️ Delete All Corners", callback=self.deleteAll)
        self.w.flipH = Button((10, -140, 165, 25), "Flip H", callback=self.flipH)
        self.w.flipV = Button((185, -140, -10, 25), "Flip V", callback=self.flipV)
        self.w.alignLeft = Button((10, -105, 100, 25), "← LEFT (0)", callback=self.alignLeft)
        self.w.alignCenter = Button((120, -105, 100, 25), "| CENTER (2)", callback=self.alignCenter)
        self.w.alignRight = Button((230, -105, 100, 25), "→ RIGHT (1)", callback=self.alignRight)

        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.5, self, "updateSelection:", None, True)
        self.w.bind("close", self.windowWillClose)
        self.w.open()

    def getTargetLayers(self, base_layer):
        if self.w.allMasters.get():
            return [base_layer.parent.layers[m.id] for m in self.font.masters if base_layer.parent.layers[m.id]]
        return [base_layer]

    def find_ref(self, glyph, pIdx, nIdx):
        for master in self.font.masters:
            l = glyph.layers[master.id]
            node = self.nodeForRef(l, pIdx, nIdx)
            if node is not None:
                for h in l.hints:
                    if h.type == CORNER and h.originNode == node:
                        return h.scale.x, h.scale.y, h.options
        return None

    def nodeForRef(self, layer, shapeIndex, nodeIndex):
        shapes = getattr(layer, 'shapes', layer.paths)
        if shapeIndex >= len(shapes):
            return None
        shape = shapes[shapeIndex]
        if not hasattr(shape, "nodes") or nodeIndex >= len(shape.nodes):
            return None
        return shape.nodes[nodeIndex]

    def apply(self, sender):
        if not self.font.selectedLayers:
            self.w.status.set("Select a layer and one or more nodes.")
            return
        layer = self.font.selectedLayers[0]
        nodeRefs = extractNodeRefs(layer)
        if not nodeRefs or not self.w.list.getSelection(): return
        selected_names = [self.corners[i] for i in self.w.list.getSelection()]

        try:
            ui_x = abs(float(self.w.scale_x.get()) / 100.0)
            ui_y = abs(float(self.w.scale_y.get()) / 100.0)
        except: ui_x, ui_y = 1.0, 1.0

        targetLayers = self.getTargetLayers(layer)
        if any(
            self.nodeForRef(curr_layer, pIdx, nIdx) is None
            for curr_layer in targetLayers
            for pIdx, nIdx in nodeRefs
        ):
            self.w.status.set("Canceled: masters have incompatible structures.")
            return

        self.font.disableUpdateInterface()
        try:
            for curr_layer in targetLayers:
                for (pIdx, nIdx) in nodeRefs:
                    node = self.nodeForRef(curr_layer, pIdx, nIdx)
                
                # Buscar info prèvia
                    ref_info = self.find_ref(layer.parent, pIdx, nIdx)
                
                # Netejar vells
                    for h in [h for h in list(curr_layer.hints) if h.type == CORNER and h.originNode == node]:
                        curr_layer.removeHint_(h)

                    for name in selected_names:
                        new_h = GSHint()
                        new_h.type = CORNER
                        new_h.setName_(name)
                        new_h.originNode = node
                    
                    # LÒGICA DE PRIORITATS:
                    # 1. Si tenim referència d'altre master, heretem el signe (FLIP) i les opcions (DIRECCIÓ)
                        sig_x, sig_y, opts = (1, 1, 0)
                        if ref_info:
                            sig_x = -1 if ref_info[0] < 0 else 1
                            sig_y = -1 if ref_info[1] < 0 else 1
                            opts = ref_info[2]
                    
                    # 2. Determinar mida numèrica (Scale)
                        val_x, val_y = (ui_x, ui_y) if self.w.customScale.get() else (1.0, 1.0)
                    
                        new_h.scale = (val_x * sig_x, val_y * sig_y)
                        new_h.options = opts
                        curr_layer.addHint_(new_h)
            self.w.status.set("Applied successfully.")
        finally:
            self.font.enableUpdateInterface()

    # --- Resta de mètodes (Delete, Flip, Align, etc.) es mantenen igual ---
    def manualRefresh(self, sender): self.cachedSelection = []; self.updateSelection_(None)
    def windowWillClose(self, sender): self.timer.invalidate() if self.timer else None
    def deleteAll(self, sender):
        self.font.disableUpdateInterface()
        for l in self.getTargetLayers(self.font.selectedLayers[0]):
            for h in [h for h in list(l.hints) if h.type == CORNER]: l.removeHint_(h)
        self.font.enableUpdateInterface()
    def flipH(self, sender): self.flip("x")
    def flipV(self, sender): self.flip("y")
    def flip(self, axis):
        self.font.disableUpdateInterface()
        for l in self.getTargetLayers(self.font.selectedLayers[0]):
            shapes = getattr(l, 'shapes', l.paths)
            for (pIdx, nIdx) in extractNodeRefs(l):
                node = shapes[pIdx].nodes[nIdx]
                for h in [h for h in l.hints if h.type == CORNER and h.originNode == node]:
                    h.scale = (h.scale.x * (-1 if axis == "x" else 1), h.scale.y * (-1 if axis == "y" else 1))
        self.font.enableUpdateInterface()
    def align(self, val):
        self.font.disableUpdateInterface()
        for l in self.getTargetLayers(self.font.selectedLayers[0]):
            shapes = getattr(l, 'shapes', l.paths)
            for (pIdx, nIdx) in extractNodeRefs(l):
                node = shapes[pIdx].nodes[nIdx]
                for h in [h for h in l.hints if h.type == CORNER and h.originNode == node]: h.options = val
        self.font.enableUpdateInterface()
    def alignLeft(self, s): self.align(0)
    def alignCenter(self, s): self.align(2)
    def alignRight(self, s): self.align(1)
    def updateSelection_(self, t):
        try:
            l = self.font.selectedLayers[0]
            sel = extractNodeRefs(l)
            if sel != self.cachedSelection and self.w.autoRefresh.get():
                self.cachedSelection = sel; self.w.nodesInfo.set(f"Nodes: {len(sel)}")
                if sel:
                    node = getattr(l, 'shapes', l.paths)[sel[0][0]].nodes[sel[0][1]]
                    h = next((h for h in l.hints if h.type == CORNER and h.originNode == node), None)
                    if h:
                        if h.name in self.corners: self.w.list.setSelection([self.corners.index(h.name)])
                        self.w.scale_x.set(str(int(round(abs(h.scale.x) * 100))))
                        self.w.scale_y.set(str(int(round(abs(h.scale.y) * 100))))
        except: pass

CornerTool()
