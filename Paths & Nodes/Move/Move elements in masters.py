# MenuTitle: Move elements in masters
# -*- coding: utf-8 -*-

from GlyphsApp import *
from vanilla import *
from AppKit import NSModalPanelWindowLevel


class MoveElementsClean(object):

    def __init__(self):

        self.font = Glyphs.font
        self.w = Window((320, 740), "Move elements")

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

        # Always on top
        self.w.getNSWindow().setLevel_(NSModalPanelWindowLevel)

        self.w.open()
        self.w.makeKey()

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

    # -------------------------
    # MOVE (FINAL FIX)
    # -------------------------
    def move(self, xDir, yDir):

        font = Glyphs.font
        if not font:
            return

        try:
            value = float(self.w.value.get())
        except:
            Message("Invalid value", "Enter a numeric value.")
            return

        dx = xDir * value
        dy = yDir * value

        mode = self.w.what.get()

        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()
        font.disableUpdateInterface()

        for layer in font.selectedLayers:
            glyph = layer.parent
            targetLayers = self.getTargetLayers(glyph, layer)

            # ===== PATHS =====
            if mode in (0, 2):

                for pIndex, path in enumerate(layer.paths):

                    moveWholePath = path.selected
                    selectedNodeIndexes = [i for i, n in enumerate(path.nodes) if n.selected]

                    if not moveWholePath and not selectedNodeIndexes:
                        continue

                    for target in targetLayers:
                        try:
                            tPath = target.paths[pIndex]
                        except:
                            continue

                        nodes = tPath.nodes

                        if moveWholePath:
                            for n in nodes:
                                n.x += dx
                                n.y += dy
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

            # ===== COMPONENTS =====
            if mode in (1, 2):

                for cIndex, comp in enumerate(layer.components):

                    if not comp.selected:
                        continue

                    for target in targetLayers:
                        try:
                            tComp = target.components[cIndex]
                            tComp.x += dx
                            tComp.y += dy
                        except:
                            continue

            # ===== ANCHORS =====
            if mode == 2:

                for aIndex, anchor in enumerate(layer.anchors):

                    if not anchor.selected:
                        continue

                    for target in targetLayers:
                        try:
                            tAnchor = target.anchors[aIndex]
                            tAnchor.x += dx
                            tAnchor.y += dy
                        except:
                            continue

        font.enableUpdateInterface()
        undoManager.endUndoGrouping()


MoveElementsClean()