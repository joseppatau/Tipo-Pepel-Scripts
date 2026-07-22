# MenuTitle: Fit Curve & Ductus PRO (DEBUG STABLE UI)
# -*- coding: utf-8 -*-

from vanilla import *
import GlyphsApp

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)

class FitCurveLiveSync:

    def __init__(self):
        self.w = FloatingWindow((280, 540), "Fit Curve & Ductus PRO")

        y = 15

        # SMOOTH %
        self.w.t1 = TextBox((10, y, 120, 17), "Smooth %", sizeStyle='small')
        self.w.sliderAbs = Slider((10, y+18, -60, 20), value=61, minValue=0, maxValue=100, callback=self.ui_callback)
        self.w.editAbs = EditText((-50, y+16, 40, 22), "61", callback=self.ui_edit_callback, sizeStyle='small')

        y += 50

        # DELTA %
        self.w.t2 = TextBox((10, y, 120, 17), "Delta %", sizeStyle='small')
        self.w.sliderRel = Slider((10, y+18, -60, 20), value=0, minValue=-50, maxValue=50, callback=self.ui_callback)
        self.w.editRel = EditText((-50, y+16, 40, 22), "0", callback=self.ui_edit_callback, sizeStyle='small')

        y += 50
        self.w.line1 = HorizontalLine((10, y, -10, 1))

        y += 15

        # DUCTUS HORITZONTAL (Nodes amb handles horitzontals)
        self.w.t3 = TextBox((10, y, -10, 17), "Ductus Horitzontal (X)", sizeStyle='small')
        self.w.sliderDuctusH = Slider((10, y+18, -60, 20), value=0, minValue=-100, maxValue=100, callback=self.ductus_callback)
        self.w.editDuctusH = EditText((-50, y+16, 40, 22), "0", callback=self.ductus_edit_callback, sizeStyle='small')

        y += 50

        # DUCTUS VERTICAL (Nodes amb handles verticals)
        self.w.t4 = TextBox((10, y, -10, 17), "Ductus Vertical (Y)", sizeStyle='small')
        self.w.sliderDuctusV = Slider((10, y+18, -60, 20), value=0, minValue=-100, maxValue=100, callback=self.ductus_callback)
        self.w.editDuctusV = EditText((-50, y+16, 40, 22), "0", callback=self.ductus_edit_callback, sizeStyle='small')

        y += 50
        self.w.line2 = HorizontalLine((10, y, -10, 1))

        y += 15

        # DESPLAÇAMENT ADJACENT HORITZONTAL (Moviment en Y)
        self.w.t5 = TextBox((10, y, -10, 17), "Desplaçament Adjacent (Y)", sizeStyle='small')
        self.w.sliderAdjacent = Slider((10, y+18, -60, 20), value=0, minValue=-100, maxValue=100, callback=self.adjacent_callback)
        self.w.editAdjacent = EditText((-50, y+16, 40, 22), "0", callback=self.adjacent_edit_callback, sizeStyle='small')

        y += 50
        self.w.line3 = HorizontalLine((10, y, -10, 1))

        y += 15

        # INFO TEXT (automatic)
        self.w.infoText = TextBox((10, y, -10, 50), "Detectant handles...", sizeStyle='small')

        y += 65

        # SYNC
        self.w.syncAll = CheckBox((10, y, -10, 20), "Sync all Masters", value=True, callback=self.reset_memory)

        self.w.open()

        self.memory = {}
        self.nodes_horitzontals = []
        self.nodes_verticals = []
        self.nodes_adjacents = []  # Guardar parells de nodes adjacents
        
        # Deteccio inicial
        self.detectar_handles()

    # -------------------------
    # DETECCIO D'HANDLES (AUTOMATICA)
    # -------------------------
    def obtenir_handles_node(self, nodes, idx, es_path_tancat):
        """Obté els 2 handles d'un node"""
        handle_in = None
        handle_out = None
        num_nodes = len(nodes)
        
        if nodes[idx].type != 'curve':
            return None, None
        
        if es_path_tancat and num_nodes >= 6:
            prev_idx = (idx - 1) % num_nodes
            prev2_idx = (idx - 2) % num_nodes
            next_idx = (idx + 1) % num_nodes
            next2_idx = (idx + 2) % num_nodes
            
            if nodes[prev_idx].type == 'offcurve' and nodes[prev2_idx].type == 'offcurve':
                offcurve = nodes[prev2_idx]
                dx = offcurve.x - nodes[idx].x
                dy = offcurve.y - nodes[idx].y
                if dx != 0 or dy != 0:
                    handle_in = (dx, dy)
            
            if nodes[next_idx].type == 'offcurve' and nodes[next2_idx].type == 'offcurve':
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

    def classificar_handle(self, dx, dy):
        if abs(dx) > abs(dy):
            return 'horitzontal'
        elif abs(dy) > abs(dx):
            return 'vertical'
        else:
            return 'diagonal'

    def detectar_nodes_adjacents(self, layer):
        """Detecta parells de nodes adjacents per al desplaçament en Y"""
        adjacents = []
        
        for path in layer.paths:
            nodes = path.nodes
            num_nodes = len(nodes)
            es_tancat = path.closed
            
            # Buscar nodes curve i els seus veïns
            for i, node in enumerate(nodes):
                if node.type != 'curve':
                    continue
                
                # Trobar els nodes curve anterior i següent
                prev_node = None
                next_node = None
                
                # Cercar cap enrere
                j = i - 1
                while j >= 0 and prev_node is None:
                    if nodes[j].type == 'curve':
                        prev_node = nodes[j]
                    j -= 1
                
                # Si es tancat i no hem trobat, buscar al final
                if es_tancat and prev_node is None:
                    j = num_nodes - 1
                    while j > i and prev_node is None:
                        if nodes[j].type == 'curve':
                            prev_node = nodes[j]
                        j -= 1
                
                # Cercar cap endavant
                j = i + 1
                while j < num_nodes and next_node is None:
                    if nodes[j].type == 'curve':
                        next_node = nodes[j]
                    j += 1
                
                # Si es tancat i no hem trobat, buscar al principi
                if es_tancat and next_node is None:
                    j = 0
                    while j < i and next_node is None:
                        if nodes[j].type == 'curve':
                            next_node = nodes[j]
                        j += 1
                
                if prev_node and next_node:
                    adjacents.append({
                        'node_central': node,
                        'node_prev': prev_node,
                        'node_next': next_node,
                        'pos_original_prev': (prev_node.x, prev_node.y),
                        'pos_original_next': (next_node.x, next_node.y),
                        'pos_original_central': (node.x, node.y)
                    })
        
        return adjacents

    def detectar_handles(self):
        """Detecta automaticament els nodes amb handles horitzontals i verticals"""
        try:
            font = Glyphs.font
            if not font or not font.selectedLayers:
                self.w.infoText.set("Selecciona una lletra")
                return
            
            layer = font.selectedLayers[0]
            
            if not layer.paths:
                self.w.infoText.set("La capa no conté paths")
                return
            
            self.nodes_horitzontals = []
            self.nodes_verticals = []
            count_hor = 0
            count_ver = 0
            
            for path in layer.paths:
                nodes = path.nodes
                es_tancat = path.closed
                
                for i, node in enumerate(nodes):
                    if node.type != 'curve':
                        continue
                    
                    handle_in, handle_out = self.obtenir_handles_node(nodes, i, es_tancat)
                    
                    te_horitzontal = False
                    te_vertical = False
                    direccio_hor = 0
                    direccio_ver = 0
                    
                    if handle_in:
                        dx, dy = handle_in
                        tipus = self.classificar_handle(dx, dy)
                        if tipus == 'horitzontal':
                            te_horitzontal = True
                            count_hor += 1
                            direccio_hor = 1 if dx > 0 else -1
                        elif tipus == 'vertical':
                            te_vertical = True
                            count_ver += 1
                            direccio_ver = 1 if dy > 0 else -1
                    
                    if handle_out:
                        dx, dy = handle_out
                        tipus = self.classificar_handle(dx, dy)
                        if tipus == 'horitzontal':
                            te_horitzontal = True
                            count_hor += 1
                            direccio_hor = 1 if dx > 0 else -1
                        elif tipus == 'vertical':
                            te_vertical = True
                            count_ver += 1
                            direccio_ver = 1 if dy > 0 else -1
                    
                    if te_horitzontal:
                        self.nodes_horitzontals.append({
                            'node': node,
                            'direccio': direccio_hor,
                            'x_original': node.x,
                            'y_original': node.y
                        })
                    
                    if te_vertical:
                        self.nodes_verticals.append({
                            'node': node,
                            'direccio': direccio_ver,
                            'x_original': node.x,
                            'y_original': node.y
                        })
            
            # Detectar nodes adjacents
            self.nodes_adjacents = self.detectar_nodes_adjacents(layer)
            
            self.w.infoText.set(f"H hor: {count_hor} ({len(self.nodes_horitzontals)} nodes)\n"
                               f"H ver: {count_ver} ({len(self.nodes_verticals)} nodes)\n"
                               f"Adjacents: {len(self.nodes_adjacents)} parells")
            log(f"Detectats: {len(self.nodes_horitzontals)} hor, {len(self.nodes_verticals)} ver, {len(self.nodes_adjacents)} adj")
            
        except Exception as e:
            self.w.infoText.set(f"Error: {str(e)}")
            log(f"Error detectant: {e}")

    def aplicar_desplacament_hor(self, valor_percent):
        """Aplica desplaçament horitzontal en temps real"""
        if not self.nodes_horitzontals:
            return
        
        desplacament = valor_percent
        
        for item in self.nodes_horitzontals:
            node = item['node']
            direccio = item['direccio']
            desplacament_x = -direccio * desplacament
            node.x = item['x_original'] + desplacament_x

    def aplicar_desplacament_ver(self, valor_percent):
        """Aplica desplaçament vertical en temps real"""
        if not self.nodes_verticals:
            return
        
        desplacament = valor_percent
        
        for item in self.nodes_verticals:
            node = item['node']
            direccio = item['direccio']
            desplacament_y = -direccio * desplacament
            node.y = item['y_original'] + desplacament_y

    def aplicar_desplacament_adjacent(self, valor_percent):
        """Aplica desplaçament VERTICAL als nodes adjacents (prev, central, next)"""
        if not self.nodes_adjacents:
            return
        
        desplacament = valor_percent
        
        for item in self.nodes_adjacents:
            node_prev = item['node_prev']
            node_next = item['node_next']
            node_central = item['node_central']
            
            # Moure TOTS ELS NODES (prev, central, next) en Y
            node_prev.y = item['pos_original_prev'][1] + desplacament
            node_next.y = item['pos_original_next'][1] + desplacament
            node_central.y = item['pos_original_central'][1] + desplacament

    def reset_posicions(self):
        """Restaura les posicions originals dels nodes"""
        for item in self.nodes_horitzontals:
            node = item['node']
            node.x = item['x_original']
            node.y = item['y_original']
        
        for item in self.nodes_verticals:
            node = item['node']
            node.x = item['x_original']
            node.y = item['y_original']
        
        for item in self.nodes_adjacents:
            item['node_prev'].x, item['node_prev'].y = item['pos_original_prev']
            item['node_next'].x, item['node_next'].y = item['pos_original_next']
            item['node_central'].x, item['node_central'].y = item['pos_original_central']

    def store(self, layer):
        """Guarda l'estat inicial dels handles seleccionats"""
        log("---- STORE ----")
        self.memory = {}

        for path in layer.paths:
            for node in path.nodes:
                # Només ens interessen handles (offcurve) seleccionats
                if node.type != "offcurve" or not node.selected:
                    continue

                prev = node.prevNode
                next = node.nextNode
                if not prev or not next:
                    continue

                # Identifiquem el node on "penja" el handle (owner)
                if prev.type != "offcurve":
                    owner = prev
                    target = next.nextNode if next.type == "offcurve" else next
                else:
                    owner = next
                    target = prev.prevNode if prev.type == "offcurve" else prev

                if not owner or not target:
                    continue

                # --- FILTRE PER CORNER NODES ---
                # Només processem si el node owner és SMOOTH (connexió verda)
                # En Glyphs, owner.connection == 100 significa "Smooth"
                if owner.connection != 100:
                    continue

                # Determinar si el handle és principalment horitzontal o vertical
                axis = "y" if abs(node.y - owner.y) < 2 else "x"

                self.memory[id(node)] = {
                    "handle": node,
                    "owner": owner,
                    "target": target,
                    "axis": axis,
                    "ox": owner.x,
                    "oy": owner.y,
                    "tx": target.x,
                    "ty": target.y
                }
    # -------------------------
    # APPLY (original)
    # -------------------------
    def apply(self, layer, ratio):
        """Aplica el càlcul de Fit Curve basat en la memòria"""
        log("---- APPLY ----")
        for data in self.memory.values():
            try:
                owner = data["owner"]
                target = data["target"]
                handle = data["handle"]

                if owner.parent is None: continue

                dx = target.x - owner.x
                dy = target.y - owner.y

                if data["axis"] == "y":
                    handle.x = owner.x + dx * ratio
                    handle.y = owner.y
                else:
                    handle.y = owner.y + dy * ratio
                    handle.x = owner.x
            except Exception as e:
                log(f"ERROR apply: {e}")
                
                
                
    # -------------------------
    # UI CALLBACKS
    # -------------------------
    def ui_edit_callback(self, sender):
        try:
            val = float(sender.get())
            if sender == self.w.editAbs: 
                self.w.sliderAbs.set(val)
            elif sender == self.w.editRel: 
                self.w.sliderRel.set(val)
            self.ui_callback(None)
        except:
            pass

    def ductus_edit_callback(self, sender):
        try:
            val = float(sender.get())
            if sender == self.w.editDuctusH: 
                self.w.sliderDuctusH.set(val)
                self.aplicar_desplacament_hor(val)
            elif sender == self.w.editDuctusV: 
                self.w.sliderDuctusV.set(val)
                self.aplicar_desplacament_ver(val)
            
            self.ductus_callback(None)
        except:
            pass

    def adjacent_edit_callback(self, sender):
        try:
            val = float(sender.get())
            self.w.sliderAdjacent.set(val)
            self.aplicar_desplacament_adjacent(val)
            self.adjacent_callback(None)
        except:
            pass

    def ductus_callback(self, sender):
        """Callback per als sliders de ductus (live preview)"""
        font = Glyphs.font
        if not font:
            return
        
        dH = self.w.sliderDuctusH.get()
        dV = self.w.sliderDuctusV.get()
        
        self.w.editDuctusH.set(f"{dH:g}")
        self.w.editDuctusV.set(f"{dV:g}")
        
        font.disableUpdateInterface()
        
        self.aplicar_desplacament_hor(dH)
        self.aplicar_desplacament_ver(dV)
        
        # Re-aplicar Smooth
        s_abs = self.w.sliderAbs.get()
        s_rel = self.w.sliderRel.get()
        ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)
        
        for layer in font.selectedLayers:
            if not self.memory:
                self.store(layer)
            self.apply(layer, ratio)
        
        font.enableUpdateInterface()
        Glyphs.redraw()

    def adjacent_callback(self, sender):
        """Callback per al slider de desplaçament adjacent (live preview)"""
        font = Glyphs.font
        if not font:
            return
        
        adj = self.w.sliderAdjacent.get()
        self.w.editAdjacent.set(f"{adj:g}")
        
        font.disableUpdateInterface()
        
        self.aplicar_desplacament_adjacent(adj)
        
        # Re-aplicar Smooth i ductus
        s_abs = self.w.sliderAbs.get()
        s_rel = self.w.sliderRel.get()
        ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)
        dH = self.w.sliderDuctusH.get()
        dV = self.w.sliderDuctusV.get()
        
        self.aplicar_desplacament_hor(dH)
        self.aplicar_desplacament_ver(dV)
        
        for layer in font.selectedLayers:
            if not self.memory:
                self.store(layer)
            self.apply(layer, ratio)
        
        font.enableUpdateInterface()
        Glyphs.redraw()

    def ui_callback(self, sender):
        """Callback per als sliders de Smooth (live preview)"""
        font = Glyphs.font
        if not font:
            return

        s_abs = self.w.sliderAbs.get()
        s_rel = self.w.sliderRel.get()
        
        self.w.editAbs.set(f"{s_abs:g}")
        self.w.editRel.set(f"{s_rel:g}")

        ratio = (s_abs / 100.0) * (1 + s_rel / 100.0)

        font.disableUpdateInterface()

        for layer in font.selectedLayers:
            if not self.memory:
                self.store(layer)
            self.apply(layer, ratio)

        font.enableUpdateInterface()
        Glyphs.redraw()

    def reset_memory(self, sender):
        log("Memory reset")
        self.memory = {}
        self.detectar_handles()

# Executar
FitCurveLiveSync()