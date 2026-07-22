#MenuTitle: Move Noder Engine
# -*- coding: utf-8 -*-
# Description: Moves and adjusts node positions and distances using axis-based constraints and multi-glyph scope control.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla
from math import fabs

class MoveNodesUI(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow(
            (320, 500),
            "Move Noder Engine",
            autosaveName="com.yournamespace.nodemover"
        )
        
        # Create tab group
        self.w.tabs = vanilla.Tabs((10, 10, -10, 430), ["One Node", "Multiple Nodes"])
        
        # --- TAB 1: ONE NODE (Actualitzat amb el codi de Move Nodes By Axis checkbox) ---
        self.w.tabs[0].axisText = vanilla.TextBox((10, 10, -10, 14), "Select Axis")
        self.w.tabs[0].axis = vanilla.RadioGroup(
            (10, 30, -10, 20),
            ["X", "Y"],
            isVertical=False
        )
        self.w.tabs[0].axis.set(0)

        self.w.tabs[0].actualText = vanilla.TextBox((10, 60, -10, 14), "Actual position")
        self.w.tabs[0].actualPos = vanilla.EditText((10, 78, -10, 20), "12")

        self.w.tabs[0].newText = vanilla.TextBox((10, 108, -10, 14), "New position")
        self.w.tabs[0].newPos = vanilla.EditText((10, 126, -10, 20), "18")

        self.w.tabs[0].toleranceText = vanilla.TextBox((10, 156, -10, 14), "Margin tolerance")
        self.w.tabs[0].tolerance = vanilla.EditText((10, 174, -10, 20), "3")
        
        # ---- SCOPE CHECKBOXES (del primer script) ----
        self.w.tabs[0].scopeText = vanilla.TextBox((10, 205, -10, 14), "Apply to:")

        self.w.tabs[0].currentGlyph = vanilla.CheckBox(
            (20, 225, -10, 20),
            "Current Glyph",
            value=True,
            callback=self.scopeChanged
        )

        self.w.tabs[0].selectedGlyphs = vanilla.CheckBox(
            (20, 250, -10, 20),
            "Selected Characters",
            callback=self.scopeChanged
        )

        self.w.tabs[0].tabGlyphs = vanilla.CheckBox(
            (20, 275, -10, 20),
            "Tab Characters",
            callback=self.scopeChanged
        )

        self.w.tabs[0].entireMaster = vanilla.CheckBox(
            (20, 300, -10, 20),
            "Entire Master",
            callback=self.scopeChanged
        )
        
        # --- TAB 2: MULTIPLE NODES (sense canvis) ---
        self.w.tabs[1].axisText = vanilla.TextBox((10, 10, -10, 14), "Select Axis")
        self.w.tabs[1].axis = vanilla.RadioGroup(
            (10, 30, -10, 20),
            ["X", "Y"],
            isVertical=False
        )
        self.w.tabs[1].axis.set(0)

        self.w.tabs[1].distanceText = vanilla.TextBox((10, 60, -10, 14), "Distance Between")
        self.w.tabs[1].distance = vanilla.EditText((10, 78, -10, 20), "12")

        self.w.tabs[1].newDistanceText = vanilla.TextBox((10, 108, -10, 14), "New distance")
        self.w.tabs[1].newDistance = vanilla.EditText((10, 126, -10, 20), "18")

        self.w.tabs[1].toleranceText = vanilla.TextBox((10, 156, -10, 14), "Margin tolerance")
        self.w.tabs[1].tolerance = vanilla.EditText((10, 174, -10, 20), "3")

        self.w.tabs[1].directionText = vanilla.TextBox((10, 204, -10, 14), "Expand/contract direction")
        self.w.tabs[1].direction = vanilla.RadioGroup(
            (10, 224, -10, 80),
            ["Both sides", "First node only", "From center", "Second node only"],
            isVertical=True
        )
        self.w.tabs[1].direction.set(0)
        
        # LiApache2 to masters checkbox
        self.w.tabs[1].liApache2ToMasters = vanilla.CheckBox(
            (10, 310, -10, 20),
            "LiApache2 expansion to master lines",
            value=False,
            callback=self.liApache2ToMastersChanged
        )
        
        self.w.tabs[1].excludeText = vanilla.TextBox((10, 340, -10, 14), "Exclude (if within 3 units):")
        self.w.tabs[1].excludeBaseline = vanilla.CheckBox((20, 360, -10, 20), "Baseline")
        self.w.tabs[1].excludeXHeight = vanilla.CheckBox((20, 385, -10, 20), "x-height")
        self.w.tabs[1].excludeCaps = vanilla.CheckBox((20, 410, -10, 20), "Caps")

        # Apply button
        self.w.applyButton = vanilla.Button(
            (10, -40, -10, 30),
            "APPLY",
            callback=self.apply
        )

        self.w.open()
    
    # -----------------------------------------------------
    # Scope logic (mutually exclusive) - del primer script
    # -----------------------------------------------------
    
    def scopeChanged(self, sender):
        for cb in [self.w.tabs[0].currentGlyph,
                   self.w.tabs[0].selectedGlyphs,
                   self.w.tabs[0].tabGlyphs,
                   self.w.tabs[0].entireMaster]:
            if cb != sender:
                cb.set(False)

        sender.set(True)
    
    # -----------------------------------------------------
    # Get glyphs according to scope (del primer script)
    # -----------------------------------------------------
    
    def getGlyphsByScope(self, font, tabIndex=0):
        """Get glyphs based on selected scope for specified tab"""
        
        if tabIndex == 0:  # One Node tab
            if self.w.tabs[0].currentGlyph.get():
                layer = font.selectedLayers[0] if font.selectedLayers else None
                return [layer.parent] if layer else []

            elif self.w.tabs[0].selectedGlyphs.get():
                return list({l.parent for l in font.selectedLayers})

            elif self.w.tabs[0].tabGlyphs.get():
                if font.currentTab:
                    return [l.parent for l in font.currentTab.layers if l.parent]
                return []

            elif self.w.tabs[0].entireMaster.get():
                return list(font.glyphs)
        else:  # Multiple Nodes tab (mantenim funcionalitat original)
            return list(font.glyphs)

        return []
    
    def liApache2ToMastersChanged(self, sender):
        """Enable/disable exclude checkboxes based on liApache2ToMasters"""
        enabled = not self.w.tabs[1].liApache2ToMasters.get()
        self.w.tabs[1].excludeBaseline.enable(enabled)
        self.w.tabs[1].excludeXHeight.enable(enabled)
        self.w.tabs[1].excludeCaps.enable(enabled)

    def isNearReferenceLine(self, nodeY, master, excludeList):
        """Check if a node is near reference lines to exclude"""
        if not excludeList:
            return False
            
        # Get reference line positions from master
        baseline = 0  # Baseline is always 0 in Glyphs
        xHeight = master.xHeight
        capHeight = master.capHeight
        
        for line in excludeList:
            if line == "Baseline" and fabs(nodeY - baseline) <= 3:
                return True
            elif line == "x-height" and fabs(nodeY - xHeight) <= 3:
                return True
            elif line == "Caps" and fabs(nodeY - capHeight) <= 3:
                return True
        
        return False
    
    def getMovementLiApache2s(self, node1, node2, useY, master, direction):
        """Calculate movement liApache2s based on master lines"""
        if not useY:  # Para eje X no hay líApache2es de líneas maestras
            return None, None, None, None
        
        # Obtener posiciones de líneas maestras
        baseline = 0
        xHeight = master.xHeight
        capHeight = master.capHeight
        
        # Determinar qué nodo es superior y cuál inferior
        if node1.y > node2.y:  # En tipografía, Y mayor = más abajo
            top_node, bottom_node = node2, node1
        else:
            top_node, bottom_node = node1, node2
        
        # Calcular líApache2es
        # El nodo inferior no puede pasar la baseline
        bottom_liApache2 = baseline
        
        # El nodo superior tiene líApache2e según tipo de letra
        # Si está cerca de x-height, liApache2ar a x-height
        # Si está cerca de cap height, liApache2ar a cap height
        top_liApache2 = None
        
        if fabs(top_node.y - xHeight) < 10:  # Si está cerca de x-height
            top_liApache2 = xHeight
        elif fabs(top_node.y - capHeight) < 10:  # Si está cerca de cap height
            top_liApache2 = capHeight
        
        return top_node, bottom_node, top_liApache2, bottom_liApache2
    
    def adjustWithLiApache2s(self, node1, node2, newDistance, direction, useY, master, liApache2ToMasters):
        """Adjust nodes with optional liApache2s"""
        if not useY or not liApache2ToMasters:
            # Sin líApache2es, usar función original
            if useY:
                self.adjustNodesY(node1, node2, newDistance, direction)
            else:
                self.adjustNodesX(node1, node2, newDistance, direction)
            return True
        
        # Con líApache2es, calcular primero
        top_node, bottom_node, top_liApache2, bottom_liApache2 = self.getMovementLiApache2s(
            node1, node2, useY, master, direction
        )
        
        # Calcular movimiento deseado
        currentDistance = top_node.y - bottom_node.y
        desiredAdjustment = newDistance - currentDistance
        
        # Calcular movimiento máximo perApache2ido
        maxAdjustment = desiredAdjustment
        
        if direction == 0:  # Both sides
            # Ambos se mueven Apache2ad cada uno
            top_allowed = float('inf') if top_liApache2 is None else top_node.y - top_liApache2
            bottom_allowed = float('inf') if bottom_liApache2 is None else bottom_node.y - bottom_liApache2
            
            # El ajuste máximo es 2 veces el menor de los líApache2es (Apache2ad para cada lado)
            maxAdjustment = min(maxAdjustment, 2 * top_allowed, 2 * bottom_allowed)
            
        elif direction == 1:  # First node only (top/superior)
            if top_liApache2 is not None:
                maxAdjustment = min(maxAdjustment, top_node.y - top_liApache2)
                
        elif direction == 2:  # From center
            # Similar a both sides pero manteniendo centro
            top_allowed = float('inf') if top_liApache2 is None else top_node.y - top_liApache2
            bottom_allowed = float('inf') if bottom_liApache2 is None else bottom_node.y - bottom_liApache2
            
            maxAdjustment = min(maxAdjustment, 2 * top_allowed, 2 * bottom_allowed)
            
        elif direction == 3:  # Second node only (bottom/inferior)
            if bottom_liApache2 is not None:
                maxAdjustment = min(maxAdjustment, bottom_node.y - bottom_liApache2)
        
        # Si no hay ajuste posible, devolver False
        if maxAdjustment <= 0:
            return False
        
        # Aplicar ajuste liApache2ado
        if maxAdjustment != desiredAdjustment:
            # Ajustar con distancia liApache2ada
            liApache2edDistance = currentDistance + maxAdjustment
            if useY:
                self.adjustNodesY(node1, node2, liApache2edDistance, direction)
            else:
                self.adjustNodesX(node1, node2, liApache2edDistance, direction)
            return True
        else:
            # Aplicar ajuste completo
            if useY:
                self.adjustNodesY(node1, node2, newDistance, direction)
            else:
                self.adjustNodesX(node1, node2, newDistance, direction)
            return True

    def apply(self, sender):
        font = Glyphs.font
        if not font:
            return

        master = font.selectedFontMaster
        masterID = master.id
        
        currentTab = self.w.tabs.get()
        
        if currentTab == 0:  # One Node Tab (actualitzat)
            self.applyOneNode(font, master)
        else:  # Multiple Nodes Tab
            self.applyMultipleNodes(font, master)

    def applyOneNode(self, font, master):
        """Updated with scope functionality from first script"""
        
        try:
            actual = float(self.w.tabs[0].actualPos.get())
            new = float(self.w.tabs[0].newPos.get())
            tolerance = float(self.w.tabs[0].tolerance.get())
        except ValueError:
            Glyphs.showNotification("Node mover", "Invalid numeric values.")
            return

        useY = (self.w.tabs[0].axis.get() == 1)
        minVal = actual - tolerance
        maxVal = actual + tolerance

        masterID = master.id
        glyphs = self.getGlyphsByScope(font, 0)

        if not glyphs:
            Glyphs.showNotification("Node mover", "No glyphs found for selected scope.")
            return

        moved = 0
        font.disableUpdateInterface()

        for glyph in glyphs:
            layer = glyph.layers[masterID]
            if not layer:
                continue

            for shape in layer.shapes:
                if hasattr(shape, "nodes"):
                    for node in shape.nodes:
                        value = node.y if useY else node.x

                        if minVal <= value <= maxVal:
                            if useY:
                                node.y = new
                            else:
                                node.x = new
                            moved += 1

        font.enableUpdateInterface()

        Glyphs.showNotification(
            "Node mover",
            f"Moved {moved} nodes on {'Y' if useY else 'X'} axis"
        )

    def applyMultipleNodes(self, font, master):
        """New functionality - adjust distance between multiple nodes"""
        masterID = master.id
        
        try:
            targetDistance = float(self.w.tabs[1].distance.get())
            newDistance = float(self.w.tabs[1].newDistance.get())
            tolerance = float(self.w.tabs[1].tolerance.get())
        except ValueError:
            Glyphs.showNotification(
                "Node mover",
                "Please enter valid numeric values."
            )
            return

        useY = (self.w.tabs[1].axis.get() == 1)
        direction = self.w.tabs[1].direction.get()
        liApache2ToMasters = self.w.tabs[1].liApache2ToMasters.get()
        
        # Get exclude options (solo si liApache2ToMasters no está activado)
        excludeList = []
        if not liApache2ToMasters:
            if self.w.tabs[1].excludeBaseline.get():
                excludeList.append("Baseline")
            if self.w.tabs[1].excludeXHeight.get():
                excludeList.append("x-height")
            if self.w.tabs[1].excludeCaps.get():
                excludeList.append("Caps")
        
        pairsAdjusted = 0
        nodesMoved = set()
        liApache2edPairs = 0  # Contador para pares liApache2ados
        
        font.disableUpdateInterface()

        for glyph in font.glyphs:
            layer = glyph.layers[masterID]
            if not layer:
                continue
            
            allNodes = []
            for shape in layer.shapes:
                if hasattr(shape, "nodes"):
                    for node in shape.nodes:
                        if useY and not liApache2ToMasters and self.isNearReferenceLine(node.y, master, excludeList):
                            continue
                        allNodes.append(node)
            
            if useY:
                allNodes.sort(key=lambda n: n.y)
            else:
                allNodes.sort(key=lambda n: n.x)
            
            processedPairs = set()
            
            for i in range(len(allNodes)):
                node1 = allNodes[i]
                node1_id = id(node1)
                
                for j in range(i + 1, len(allNodes)):
                    node2 = allNodes[j]
                    node2_id = id(node2)
                    
                    pair_id = tuple(sorted((node1_id, node2_id)))
                    
                    if pair_id in processedPairs:
                        continue
                    
                    if useY:
                        distance = fabs(node2.y - node1.y)
                    else:
                        distance = fabs(node2.x - node1.x)
                    
                    if fabs(distance - targetDistance) <= tolerance:
                        # Ajustar con/sin líApache2es
                        adjusted = self.adjustWithLiApache2s(
                            node1, node2, newDistance, direction, useY, master, liApache2ToMasters
                        )
                        
                        if adjusted:
                            processedPairs.add(pair_id)
                            pairsAdjusted += 1
                            nodesMoved.add(node1_id)
                            nodesMoved.add(node2_id)
                            
                            # Verificar si fue liApache2ado
                            if useY and liApache2ToMasters:
                                currentDistance = fabs(node2.y - node1.y) if useY else fabs(node2.x - node1.x)
                                if fabs(currentDistance - newDistance) > 0.1:  # Si no alcanzó la distancia deseada
                                    liApache2edPairs += 1

            processedPairs.clear()

        font.enableUpdateInterface()

        message = f"Adjusted {pairsAdjusted} pairs ({len(nodesMoved)} unique nodes) on {'Y' if useY else 'X'} axis"
        if liApache2edPairs > 0:
            message += f"\n{liApache2edPairs} pairs liApache2ed by master lines"
        
        Glyphs.showNotification("Node mover", message)

    def adjustNodesY(self, node1, node2, newDistance, direction):
        """Adjust vertical positions of two nodes"""
        if node1.y < node2.y:
            node1, node2 = node2, node1
        
        currentDistance = node1.y - node2.y
        adjustment = newDistance - currentDistance
        
        if direction == 0:  # Both sides
            node1.y += adjustment / 2
            node2.y -= adjustment / 2
        elif direction == 1:  # First node only (top)
            node1.y += adjustment
        elif direction == 2:  # From center
            midpoint = (node1.y + node2.y) / 2
            node1.y = midpoint + newDistance / 2
            node2.y = midpoint - newDistance / 2
        elif direction == 3:  # Second node only (bottom)
            node2.y -= adjustment

    def adjustNodesX(self, node1, node2, newDistance, direction):
        """Adjust horizontal positions of two nodes"""
        if node1.x > node2.x:
            node1, node2 = node2, node1
        
        currentDistance = node2.x - node1.x
        adjustment = newDistance - currentDistance
        
        if direction == 0:  # Both sides
            node1.x -= adjustment / 2
            node2.x += adjustment / 2
        elif direction == 1:  # First node only (left)
            node1.x -= adjustment
        elif direction == 2:  # From center
            midpoint = (node1.x + node2.x) / 2
            node1.x = midpoint - newDistance / 2
            node2.x = midpoint + newDistance / 2
        elif direction == 3:  # Second node only (right)
            node2.x += adjustment


MoveNodesUI()