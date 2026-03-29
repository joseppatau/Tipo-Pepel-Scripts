# MenuTitle: Segment Angle Tool
# -*- coding: utf-8 -*-
# Description: Adjusts segment angles between nodes using directional and axis-based geometric constraints.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
import vanilla
import math
from GlyphsApp import Glyphs, GSOFFCURVE

DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)

class SegmentAngleViewer:

    def __init__(self):
        self.w = vanilla.FloatingWindow((170, 470), "Segment Angle")
        self.selected_segment = None
        
        self.w.text = vanilla.TextBox((10, 10, -10, 20), "Angle: —")
        
        self.w.input = vanilla.EditText((10, 40, 40, 22), "80")
        self.w.button = vanilla.Button((60, 40, 30, 22), "▶", callback=self.applyAngle)
        
        self.w.dirRadio = vanilla.RadioGroup((10, 65, 70, 30), ["/", "\\"], isVertical=False)
        self.w.dirRadio.set(0)
        
        self.w.axisRadio = vanilla.RadioGroup((10, 90, 70, 30), ["X", "Y"], isVertical=False)
        self.w.axisRadio.set(0)
        
        self.w.autoAxis = vanilla.CheckBox((10, 125, 120, 20), "Auto axis", value=True)
        self.w.noHandles = vanilla.CheckBox((10, 150, 120, 20), "No handles", value=True)
        
        self.w.sep = vanilla.HorizontalLine((10, 180, -10, 1))
        self.w.rangeLabel = vanilla.TextBox((10, 190, -10, 20), "Apply in range")
        
        self.w.rangeAxis = vanilla.RadioGroup((10, 210, 100, 20), ["X", "Y"], isVertical=False)
        self.w.rangeAxis.set(1)
        
        self.w.start = vanilla.EditText((10, 235, 50, 22), "450")
        self.w.end = vanilla.EditText((70, 235, 50, 22), "520")
        
        self.w.scope = vanilla.RadioGroup(
            (10, 265, 120, 60),
            ["Current", "Selected", "Entire font"],
            isVertical=True
        )
        self.w.scope.set(0)
        
        self.w.applyRangeBtn = vanilla.Button((10, 330, 120, 25), "Apply Range", callback=self.applyRange)
        
        # Botón de refresco manual
        self.w.refreshButton = vanilla.Button((10, 365, 120, 25), "Refresh Angle", callback=self.updateAngle)
        
        self.w.open()
        
        # Registrar callback para cambios en la selección
        Glyphs.addCallback(self.selectionChanged, "GSSelectionChanged")
        
        # Actualizar ángulo inicial
        self.updateAngle(None)

    # =========================
    
    def selectionChanged(self, notification):
        """Callback cuando cambia la selección en Glyphs"""
        self.updateAngle(None)
    
    def updateAngle(self, sender):
        """Actualiza el ángulo mostrado basado en la selección actual"""
        try:
            font = Glyphs.font
            if not font:
                self.w.text.set("Angle: —")
                return
            
            if not font.selectedLayers:
                self.w.text.set("Angle: —")
                return
            
            layer = font.selectedLayers[0]
            if not layer:
                self.w.text.set("Angle: —")
                return
            
            # Buscar segmentos seleccionados
            selected_segment = self.getSelectedSegment(layer)
            
            if selected_segment:
                self.selected_segment = selected_segment
                angle = self.calculateSegmentAngle(selected_segment[0], selected_segment[1])
                self.w.text.set(f"Angle: {angle:.1f}°")
            else:
                self.w.text.set("Angle: —")
                self.selected_segment = None
                
        except Exception as e:
            log(f"Error updating angle: {e}")
            self.w.text.set("Angle: —")

    # =========================
    
    def getSelectedSegment(self, layer):
        """Obtiene el segmento seleccionado (dos nodos consecutivos)"""
        if not hasattr(layer, 'selection') or not layer.selection:
            return None
        
        selected_nodes = []
        for item in layer.selection:
            # Verificar si es un nodo (no un componente)
            if hasattr(item, 'type') and item.type != GSOFFCURVE:
                selected_nodes.append(item)
        
        # Si hay exactamente dos nodos seleccionados, verificar si son consecutivos
        if len(selected_nodes) == 2:
            n1, n2 = selected_nodes[0], selected_nodes[1]
            
            # Verificar si son consecutivos en algún path
            for path in layer.paths:
                nodes = path.nodes
                for i in range(len(nodes)):
                    # Nodos consecutivos (considerando el ciclo cerrado)
                    next_idx = (i + 1) % len(nodes)
                    if (nodes[i] == n1 and nodes[next_idx] == n2) or \
                       (nodes[i] == n2 and nodes[next_idx] == n1):
                        return (n1, n2)
        
        return None
    
    def calculateSegmentAngle(self, node1, node2):
        """Calcula el ángulo entre dos nodos"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    # =========================

    def refresh(self):
        """Refresca la vista actual"""
        if Glyphs.font and Glyphs.font.currentTab:
            Glyphs.font.currentTab.redraw()
        # También actualizar el ángulo después del refresco
        self.updateAngle(None)

    # =========================

    def hasHandles(self, node):
        if node.prevNode and node.prevNode.type == GSOFFCURVE:
            return True
        if node.nextNode and node.nextNode.type == GSOFFCURVE:
            return True
        return False

    # =========================

    def applyAngle(self, sender):
        """Aplica el ángulo al segmento seleccionado"""
        if not self.selected_segment:
            log("No segment selected")
            return
        
        try:
            angle = float(self.w.input.get())
        except:
            log("Invalid angle value")
            return
        
        n1, n2 = self.selected_segment
        
        # Verificar que los nodos aún existen
        font = Glyphs.font
        if not font:
            return
        
        if not font.selectedLayers:
            return
        
        layer = font.selectedLayers[0]
        if not layer:
            return
        
        # Deshabilitar actualización de interfaz para mejor rendimiento
        font.disableUpdateInterface()
        
        try:
            # Aplicar el ángulo
            self.applyAngleToPair(n1, n2, angle)
            
            # Actualizar la selección para reflejar los cambios
            # Forzar la actualización de la capa
            layer.parent.beginUndo()
            layer.parent.endUndo()
            
        finally:
            font.enableUpdateInterface()
        
        # Refrescar la vista
        self.refresh()
        
        # Actualizar el ángulo mostrado
        self.updateAngle(None)
        
        log(f"Applied angle {angle}° to selected segment")

    # =========================

    def applyAngleToPair(self, p1, p2, angle):
        """Aplica el ángulo a un par de nodos"""
        
        log(f"→ APPLY PAIR: ({p1.x:.1f},{p1.y:.1f}) → ({p2.x:.1f},{p2.y:.1f})")
        
        # Obtener la dirección
        if self.w.dirRadio.get() == 1:
            angle = -angle
        
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        
        log(f"   Original dx:{dx:.2f} dy:{dy:.2f}")
        
        if abs(dx) < 1 and abs(dy) < 1:
            log("   ✖ segmento demasiado pequeño")
            return
        
        rad = math.radians(angle)
        
        # Determinar el eje
        if self.w.autoAxis.get():
            axis = 1 if abs(dx) > abs(dy) else 0
        else:
            axis = self.w.axisRadio.get()
        
        log(f"   axis: {'Y' if axis else 'X'}")
        
        # Guardar posición original
        before = (p2.x, p2.y)
        
        # Aplicar la transformación
        if axis == 0:  # Eje X (mantener Y constante)
            if abs(math.tan(rad)) > 1e-6:
                new_x = p1.x + dy / math.tan(rad)
                # Verificar que el nuevo valor sea razonable
                if abs(new_x) < 10000:
                    p2.x = new_x
                    log(f"   Y fixed: {p1.y} → {p2.y}, X changed: {before[0]} → {p2.x}")
                else:
                    log("   ✖ resultado X fuera de rango")
        
        elif axis == 1:  # Eje Y (mantener X constante)
            new_y = p1.y + math.tan(rad) * dx
            if abs(new_y) < 10000:
                p2.y = new_y
                log(f"   X fixed: {p1.x} → {p2.x}, Y changed: {before[1]} → {p2.y}")
            else:
                log("   ✖ resultado Y fuera de rango")
        
        after = (p2.x, p2.y)
        
        # Calcular el nuevo ángulo
        new_dx = p2.x - p1.x
        new_dy = p2.y - p1.y
        new_angle = math.degrees(math.atan2(new_dy, new_dx))
        
        log(f"   before: {before} → after: {after}")
        log(f"   new angle: {new_angle:.1f}° (target: {angle}°)")

    # =========================

    def applyRange(self, sender):
        
        log("\n=== APPLY RANGE ===")
        
        try:
            start = float(self.w.start.get())
            end = float(self.w.end.get())
        except:
            log("✖ rango inválido")
            return
        
        if start > end:
            start, end = end, start
        
        log(f"range: {start} → {end}")
        
        if not Glyphs.font.selectedLayers:
            return
        
        font = Glyphs.font
        font.disableUpdateInterface()
        
        try:
            layer = font.selectedLayers[0]
            self.processLayer(layer, start, end)
        finally:
            font.enableUpdateInterface()
        
        self.refresh()

    # =========================

    def processLayer(self, layer, start, end):
        
        axis = self.w.rangeAxis.get()
        nodesInRange = []
        
        for path in layer.paths:
            for n in path.nodes:
                
                if n.type == GSOFFCURVE:
                    continue
                
                if self.w.noHandles.get() and self.hasHandles(n):
                    continue
                
                if axis == 1:
                    if start <= n.y <= end:
                        log(f"✔ nodo en rango Y: ({n.x:.1f},{n.y:.1f})")
                        nodesInRange.append(n)
                else:
                    if start <= n.x <= end:
                        nodesInRange.append(n)
        
        log(f"total nodos: {len(nodesInRange)}")
        
        #########  DISTANCIA QUE APLICA LA RECTA  ################### 
        
        threshold = 80
        
        ############################ 
        
        angle_value = float(self.w.input.get())
        
        for i in range(len(nodesInRange)):
            n1 = nodesInRange[i]
            
            for j in range(i + 1, len(nodesInRange)):
                n2 = nodesInRange[j]
                
                dx = n2.x - n1.x
                dy = n2.y - n1.y
                
                angle = abs(math.degrees(math.atan2(dy, dx)))
                
                log(f"→ test pair angle:{angle:.2f}")
                
                if axis == 1 and angle < 5:
                    log("   ✖ descartado horizontal")
                    continue
                
                dist = math.hypot(dx, dy)
                
                log(f"   dist:{dist:.2f}")
                
                if dist < threshold:
                    log("   ✔ MATCH → aplicar")
                    self.applyAngleToPair(n1, n2, angle_value)
                    break


# Ejecutar
SegmentAngleViewer()