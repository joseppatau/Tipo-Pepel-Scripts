# MenuTitle: Move elements in masters
# -*- coding: utf-8 -*-

from GlyphsApp import *
from vanilla import *
from AppKit import NSModalPanelWindowLevel


class MoveElementsClean(object):

    def __init__(self):

        self.font = Glyphs.font
        self.w = Window((320, 820), "Move elements")

        # PM / NM
        self.w.prevMaster = Button((-60, 5, 25, 14), "PM", callback=self.prevMaster)
        self.w.nextMaster = Button((-30, 5, 25, 14), "NM", callback=self.nextMaster)

        # Arrows
        self.w.up = Button((140, 10, 40, 24), "↑", callback=lambda s: self.move(0, 1))
        self.w.down = Button((140, 80, 40, 24), "↓", callback=lambda s: self.move(0, -1))
        self.w.left = Button((80, 45, 40, 24), "←", callback=lambda s: self.move(-1, 0))
        self.w.right = Button((200, 45, 40, 24), "→", callback=lambda s: self.move(1, 0))

        self.w.value = EditText((134, 48, 50, 22), "10")

        # WHAT
        self.w.what = RadioGroup(
            (15, 120, 150, 60),
            ["Paths (Nodes)", "Components", "Both"],
            isVertical=True
        )
        self.w.what.set(0)

        # WHERE
        self.w.where = RadioGroup(
            (170, 120, 140, 40),
            ["Current Master Only", "Selected Masters"],
            isVertical=True
        )
        self.w.where.set(1)

        # MASTER CHECKBOXES
        self.masterChecks = []
        yStart = 190

        for i, master in enumerate(self.font.masters):
            cb = CheckBox((15, yStart + i * 20, -10, 20), master.name, value=True)
            setattr(self.w, f"master_{i}", cb)
            self.masterChecks.append(cb)

        # Toggle button
        self.w.toggleAll = Button(
            (15, yStart + len(self.font.masters) * 20 + 15, 120, 18),
            "Deselect All",
            callback=self.toggleMasters
        )

        # Debug button
        self.w.debug = Button(
            (150, yStart + len(self.font.masters) * 20 + 15, 80, 18),
            "Debug",
            callback=self.debugSelection
        )

        # Status label for selected glyphs
        self.w.status = TextBox((15, yStart + len(self.font.masters) * 20 + 45, -10, 20), "")
        self.updateStatus()

        # Debug output area
        self.w.debugOutput = TextEditor(
            (15, yStart + len(self.font.masters) * 20 + 70, -10, 150),
            "",
            readOnly=True
        )

        # Always on top
        self.w.getNSWindow().setLevel_(NSModalPanelWindowLevel)

        self.w.open()
        self.w.makeKey()

    def updateStatus(self):
        """Update status label with number of selected glyphs"""
        font = Glyphs.font
        if font and font.selectedLayers:
            count = len(set(layer.parent for layer in font.selectedLayers))
            if count == 1:
                self.w.status.set("1 glyph selected")
            else:
                self.w.status.set(f"{count} glyphs selected")
        else:
            self.w.status.set("No glyphs selected")

    def debugSelection(self, sender):
        """Debug function to analyze current selection"""
        font = Glyphs.font
        debugText = []
        
        debugText.append("=" * 50)
        debugText.append("DEBUG INFORMATION")
        debugText.append("=" * 50)
        
        if not font:
            debugText.append("ERROR: No font open!")
            self.w.debugOutput.set("\n".join(debugText))
            return
        
        debugText.append(f"Font: {font.familyName} {font.styleName}")
        debugText.append(f"Total masters: {len(font.masters)}")
        debugText.append("")
        
        # Selected layers
        debugText.append("SELECTED LAYERS:")
        debugText.append(f"Count: {len(font.selectedLayers)}")
        
        if len(font.selectedLayers) == 0:
            debugText.append("⚠️ No layers selected!")
            debugText.append("Please select some glyphs in the font window or edit view.")
        else:
            total_selected_nodes = 0
            total_selected_paths = 0
            total_selected_components = 0
            total_selected_anchors = 0
            
            for i, layer in enumerate(font.selectedLayers):
                glyph = layer.parent
                debugText.append(f"  {i+1}. Glyph: {glyph.name} (Layer: {layer.name})")
                debugText.append(f"     - Paths: {len(layer.paths)}")
                debugText.append(f"     - Components: {len(layer.components)}")
                debugText.append(f"     - Anchors: {len(layer.anchors)}")
                
                # Check what's selected
                selectedPaths = 0
                selectedNodes = 0
                
                # Check selected paths/nodes
                for path in layer.paths:
                    if path.selected:
                        selectedPaths += 1
                    for node in path.nodes:
                        if node.selected:
                            selectedNodes += 1
                
                # Check selected components
                selectedComponents = 0
                for comp in layer.components:
                    if comp.selected:
                        selectedComponents += 1
                
                # Check selected anchors
                selectedAnchors = 0
                for anchor in layer.anchors:
                    if anchor.selected:
                        selectedAnchors += 1
                
                debugText.append(f"     - Selected whole paths: {selectedPaths}")
                debugText.append(f"     - Selected nodes: {selectedNodes}")
                debugText.append(f"     - Selected components: {selectedComponents}")
                debugText.append(f"     - Selected anchors: {selectedAnchors}")
                
                total_selected_nodes += selectedNodes
                total_selected_paths += selectedPaths
                total_selected_components += selectedComponents
                total_selected_anchors += selectedAnchors
                debugText.append("")
            
            debugText.append("TOTAL SELECTED ELEMENTS:")
            debugText.append(f"  - Nodes: {total_selected_nodes}")
            debugText.append(f"  - Whole paths: {total_selected_paths}")
            debugText.append(f"  - Components: {total_selected_components}")
            debugText.append(f"  - Anchors: {total_selected_anchors}")
        
        # Current mode
        debugText.append("")
        debugText.append("MODE SETTINGS:")
        mode = self.w.what.get()
        mode_names = ["Paths (Nodes)", "Components", "Both"]
        debugText.append(f"  What to move: {mode_names[mode]}")
        
        where = self.w.where.get()
        where_names = ["Current Master Only", "Selected Masters"]
        debugText.append(f"  Where to move: {where_names[where]}")
        
        if where == 1:
            debugText.append("  Selected masters:")
            selected_masters = [m for i, m in enumerate(self.font.masters) if self.masterChecks[i].get()]
            for m in selected_masters:
                debugText.append(f"    - {m.name}")
        
        debugText.append("")
        debugText.append("VALUE:")
        debugText.append(f"  Move amount: {self.w.value.get()}")
        
        debugText.append("")
        debugText.append("BEHAVIOR:")
        debugText.append("  - If nodes/paths/components/anchors are selected → move only selected")
        debugText.append("  - If nothing selected → move entire glyph")
        
        self.w.debugOutput.set("\n".join(debugText))

    # -------------------------
    # MASTER NAVIGATION
    # -------------------------
    def nextMaster(self, sender):
        font = Glyphs.font
        if not font or not font.currentTab:
            return
        tab = font.currentTab
        tab.masterIndex = (tab.masterIndex + 1) % len(font.masters)

    def prevMaster(self, sender):
        font = Glyphs.font
        if not font or not font.currentTab:
            return
        tab = font.currentTab
        tab.masterIndex = (tab.masterIndex - 1) % len(font.masters)

    # -------------------------
    # TOGGLE ALL
    # -------------------------
    def toggleMasters(self, sender):

        allSelected = all(cb.get() for cb in self.masterChecks)
        newState = not allSelected

        for cb in self.masterChecks:
            cb.set(newState)

        if newState:
            self.w.toggleAll.setTitle("Deselect All")
        else:
            self.w.toggleAll.setTitle("Select All")

    # -------------------------
    # TARGET LAYERS
    # -------------------------
    def getTargetLayers(self, glyph, currentLayer):

        if self.w.where.get() == 0:
            return [currentLayer]

        selectedMasters = [
            m for i, m in enumerate(self.font.masters)
            if self.masterChecks[i].get()
        ]

        layers = []
        for m in selectedMasters:
            layer = glyph.layers[m.id]
            if layer:
                layers.append(layer)

        return layers

    def hasAnySelection(self, layer, mode):
        """Check if there are any selected elements in the layer for the given mode"""
        if mode in (0, 2):  # Paths or Both
            for path in layer.paths:
                if path.selected:
                    return True
                for node in path.nodes:
                    if node.selected:
                        return True
        
        if mode in (1, 2):  # Components or Both
            for comp in layer.components:
                if comp.selected:
                    return True
        
        if mode == 2:  # Anchors (only in Both mode)
            for anchor in layer.anchors:
                if anchor.selected:
                    return True
        
        return False

    # -------------------------
    # MOVE - SMART BEHAVIOR
    # -------------------------
    def move(self, xDir, yDir):

        font = Glyphs.font
        if not font:
            Message("No font", "Please open a font first.")
            return

        # Check if there are selected layers
        if not font.selectedLayers:
            Message("No selection", "Please select some glyphs in the font window or edit view.")
            return

        try:
            value = float(self.w.value.get())
        except:
            Message("Invalid value", "Enter a numeric value.")
            return

        dx = xDir * value
        dy = yDir * value

        mode = self.w.what.get()
        mode_names = ["Paths (Nodes)", "Components", "Both"]
        
        # Debug info for move operation
        debug_info = []
        debug_info.append(f"Moving: {dx}, {dy}")
        debug_info.append(f"Mode: {mode_names[mode]}")
        debug_info.append("")

        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()
        font.disableUpdateInterface()

        moved = False
        glyphsProcessed = set()
        
        total_paths_moved = 0
        total_components_moved = 0
        total_anchors_moved = 0
        total_glyphs_moved = 0

        for layer in font.selectedLayers:
            glyph = layer.parent
            
            # Skip if we already processed this glyph
            if glyph in glyphsProcessed:
                continue
            glyphsProcessed.add(glyph)
            
            targetLayers = self.getTargetLayers(glyph, layer)
            
            # Check if we should move entire glyph or only selected elements
            has_selection = self.hasAnySelection(layer, mode)
            move_entire_glyph = not has_selection  # Si no hay selección, mover glifo completo
            
            debug_info.append(f"Glyph: {glyph.name}")
            debug_info.append(f"  Source layer: {layer.name}")
            debug_info.append(f"  Target layers: {len(targetLayers)}")
            debug_info.append(f"  Has selection: {has_selection}")
            debug_info.append(f"  Move entire glyph: {move_entire_glyph}")
            
            # ===== MOVE ENTIRE GLYPH (all paths, components, anchors) =====
            if move_entire_glyph:
                for target in targetLayers:
                    # Move all paths
                    for path in target.paths:
                        for node in path.nodes:
                            node.x += dx
                            node.y += dy
                            moved = True
                            total_paths_moved += 1
                    
                    # Move all components
                    for comp in target.components:
                        comp.x += dx
                        comp.y += dy
                        moved = True
                        total_components_moved += 1
                    
                    # Move all anchors
                    for anchor in target.anchors:
                        anchor.x += dx
                        anchor.y += dy
                        moved = True
                        total_anchors_moved += 1
                    
                    total_glyphs_moved += 1
                
                debug_info.append(f"  → Moved entire glyph to {len(targetLayers)} masters")
            
            # ===== MOVE SELECTED ELEMENTS ONLY =====
            else:
                # ===== PATHS =====
                if mode in (0, 2):
                    paths_moved = 0
                    for pIndex, path in enumerate(layer.paths):

                        moveWholePath = path.selected
                        selectedNodeIndexes = [i for i, n in enumerate(path.nodes) if n.selected]

                        if not moveWholePath and not selectedNodeIndexes:
                            continue
                        
                        if moveWholePath:
                            debug_info.append(f"  Path {pIndex}: Whole path selected")
                        elif selectedNodeIndexes:
                            debug_info.append(f"  Path {pIndex}: {len(selectedNodeIndexes)} nodes selected")

                        for target in targetLayers:
                            if pIndex >= len(target.paths):
                                continue
                            
                            tPath = target.paths[pIndex]
                            nodes = tPath.nodes

                            if moveWholePath:
                                for n in nodes:
                                    n.x += dx
                                    n.y += dy
                                    moved = True
                                    paths_moved += 1
                                continue

                            nodesToMove = set()

                            for i in selectedNodeIndexes:
                                if i >= len(nodes):
                                    continue

                                node = nodes[i]
                                nodesToMove.add(node)

                                if node.type != OFFCURVE:

                                    j = i - 1
                                    while j >= 0 and nodes[j].type == OFFCURVE:
                                        nodesToMove.add(nodes[j])
                                        j -= 1

                                    j = i + 1
                                    while j < len(nodes) and nodes[j].type == OFFCURVE:
                                        nodesToMove.add(nodes[j])
                                        j += 1

                            for n in nodesToMove:
                                n.x += dx
                                n.y += dy
                                moved = True
                                paths_moved += 1
                    
                    if paths_moved > 0:
                        total_paths_moved += paths_moved
                        debug_info.append(f"  → Moved {paths_moved} path elements")

                # ===== COMPONENTS =====
                if mode in (1, 2):
                    components_moved = 0
                    for cIndex, comp in enumerate(layer.components):

                        if not comp.selected:
                            continue

                        for target in targetLayers:
                            if cIndex >= len(target.components):
                                continue
                            
                            tComp = target.components[cIndex]
                            tComp.x += dx
                            tComp.y += dy
                            moved = True
                            components_moved += 1
                    
                    if components_moved > 0:
                        total_components_moved += components_moved
                        debug_info.append(f"  → Moved {components_moved} components")

                # ===== ANCHORS =====
                if mode == 2:
                    anchors_moved = 0
                    for aIndex, anchor in enumerate(layer.anchors):

                        if not anchor.selected:
                            continue

                        for target in targetLayers:
                            if aIndex >= len(target.anchors):
                                continue
                            
                            tAnchor = target.anchors[aIndex]
                            tAnchor.x += dx
                            tAnchor.y += dy
                            moved = True
                            anchors_moved += 1
                    
                    if anchors_moved > 0:
                        total_anchors_moved += anchors_moved
                        debug_info.append(f"  → Moved {anchors_moved} anchors")
            
            debug_info.append("")

        font.enableUpdateInterface()
        undoManager.endUndoGrouping()
        
        # Show debug info in the output area
        debug_output = "\n".join(debug_info)
        if not moved:
            debug_output += "\n" + "=" * 50 + "\n"
            debug_output += "NO ELEMENTS MOVED!\n"
            debug_output += "Possible reasons:\n"
            if mode == 0:
                debug_output += "1. No nodes or paths selected, and 'Paths' mode is active\n"
            elif mode == 1:
                debug_output += "1. No components selected, and 'Components' mode is active\n"
            else:
                debug_output += "1. No elements selected, and 'Both' mode is active\n"
            debug_output += "2. Target masters may not have matching paths/components\n"
            debug_output += "3. Click 'Debug' button for detailed selection information"
            self.w.debugOutput.set(debug_output)
            Message("Nothing moved", "No elements found to move.\n\nCheck the debug output for details.")
        else:
            self.w.debugOutput.set(debug_output)
            if total_glyphs_moved > 0:
                summary = f"Moved ENTIRE GLYPHS:\n- {total_glyphs_moved} glyphs processed\n- {total_paths_moved} paths\n- {total_components_moved} components\n- {total_anchors_moved} anchors"
            else:
                summary = f"Moved SELECTED ELEMENTS:\n- Path elements: {total_paths_moved}\n- Components: {total_components_moved}\n- Anchors: {total_anchors_moved}"
            Message("Success", summary)
        
        # Update status after operation
        self.updateStatus()


MoveElementsClean()