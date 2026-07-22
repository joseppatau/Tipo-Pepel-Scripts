# MenuTitle: Move Nodes & components (All Masters)
# -*- coding: utf-8 -*-
# Description: Moves selected nodes, anchors, and components across all master layers simultaneously.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
import vanilla

DEFAULT_KEY = "com.tunombre.movenodesallmasters.value"


class MoveNodesAllMastersFloating(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Open a font first.")
            return

        self.qIsDown = False

        self.w = vanilla.FloatingWindow(
            (200, 150),
            "Move Nodes (All Masters)",
            closable=True
        )

        self.w.valueText = vanilla.TextBox(
            (10, 10, -10, 17),
            "Move (pt):"
        )

        savedValue = Glyphs.defaults.get(DEFAULT_KEY, 30)

        self.w.value = vanilla.EditText(
            (10, 30, -10, 22),
            str(savedValue)
        )

        # Botones
        self.w.up = vanilla.Button(
            (80, 60, 40, 20),
            "↑",
            callback=lambda s: self._debugMove("UP", 0, 1)
        )
        self.w.down = vanilla.Button(
            (80, 85, 40, 20),
            "↓",
            callback=lambda s: self._debugMove("DOWN", 0, -1)
        )
        self.w.left = vanilla.Button(
            (35, 72, 40, 20),
            "←",
            callback=lambda s: self._debugMove("LEFT", -1, 0)
        )
        self.w.right = vanilla.Button(
            (125, 72, 40, 20),
            "→",
            callback=lambda s: self._debugMove("RIGHT", 1, 0)
        )

        self.w.bind("close", self.windowClosed)
        self.w.open()

        print("DEBUG: Window opened")
        Glyphs.addCallback(self.keyDown, "keyDown")

    def windowClosed(self, sender):
        print("DEBUG: Window closed")
        Glyphs.removeCallback(self.keyDown, "keyDown")
        global moveNodesWindow
        moveNodesWindow = None

    # -------------------------------------------------
    # KEYBOARD DEBUG
    # -------------------------------------------------
    def keyDown(self, event):
        try:
            keyCode = event.keyCode()
            charsIgnore = event.charactersIgnoringModifiers()
        except Exception as e:
            print("DEBUG: event error", e)
            return False

        # Q pressed
        if charsIgnore in ("q", "Q"):
            self.qIsDown = True
            print("DEBUG: Q DOWN")
            return False

        # Q + arrows
        if self.qIsDown:
            if keyCode == 123:
                self.move(-1, 0)
                return True
            elif keyCode == 124:
                self.move(1, 0)
                return True
            elif keyCode == 125:
                self.move(0, -1)
                return True
            elif keyCode == 126:
                self.move(0, 1)
                return True

        return False

    # -------------------------------------------------
    # MOVE (with debug)
    # -------------------------------------------------
    def _debugMove(self, label, x, y):
        print(f"DEBUG: BUTTON {label}")
        self.move(x, y)

    def move(self, xDir, yDir):

        font = Glyphs.font
        if not font:
            print("DEBUG: No font")
            return

        try:
            value = float(self.w.value.get())
        except:
            print("DEBUG: Invalid value")
            return

        Glyphs.defaults[DEFAULT_KEY] = value

        dx = xDir * value
        dy = yDir * value

        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()
        font.disableUpdateInterface()

        movedNodes = 0
        movedAnchors = 0
        movedComponents = 0

        for layer in font.selectedLayers:

            glyph = layer.parent

            # -----------------------------
            # NODES
            # -----------------------------
            for pIndex, path in enumerate(layer.paths):

                for nIndex, node in enumerate(path.nodes):

                    if node.selected:

                        for master in font.masters:

                            masterLayer = glyph.layers[master.id]

                            if not masterLayer:
                                continue

                            try:
                                masterNode = masterLayer.paths[pIndex].nodes[nIndex]
                            except IndexError:
                                continue

                            masterNode.x += dx
                            masterNode.y += dy
                            movedNodes += 1

            # -----------------------------
            # ANCHORS
            # -----------------------------
            for anchor in layer.anchors:

                if anchor.selected:

                    anchorName = anchor.name

                    for master in font.masters:

                        masterLayer = glyph.layers[master.id]

                        if not masterLayer:
                            continue

                        if anchorName in masterLayer.anchors:
                            masterAnchor = masterLayer.anchors[anchorName]
                            masterAnchor.x += dx
                            masterAnchor.y += dy
                            movedAnchors += 1

            # -----------------------------
            # COMPONENTS
            # -----------------------------
            # Obtener componentes de la capa actual
            components = []
            if hasattr(layer, 'components'):
                components = layer.components
            elif hasattr(layer, 'shapes'):
                components = [s for s in layer.shapes if isinstance(s, GSComponent)]

            for comp_idx, component in enumerate(components):

                if component.selected:

                    for master in font.masters:

                        masterLayer = glyph.layers[master.id]

                        if not masterLayer:
                            continue

                        # Obtener componentes en la capa master
                        masterComponents = []
                        if hasattr(masterLayer, 'components'):
                            masterComponents = masterLayer.components
                        elif hasattr(masterLayer, 'shapes'):
                            masterComponents = [s for s in masterLayer.shapes if isinstance(s, GSComponent)]

                        # Buscar el componente correspondiente
                        if comp_idx < len(masterComponents):
                            masterComponent = masterComponents[comp_idx]
                            
                            # Verificar que sea el mismo componente (por nombre)
                            comp_name = component.name if hasattr(component, 'name') else component.componentName if hasattr(component, 'componentName') else None
                            master_comp_name = masterComponent.name if hasattr(masterComponent, 'name') else masterComponent.componentName if hasattr(masterComponent, 'componentName') else None
                            
                            if comp_name == master_comp_name:
                                # Mover el componente modificando su transformación
                                t = masterComponent.transform
                                if t:
                                    # Actualizar la posición en la matriz de transformación
                                    masterComponent.transform = (t[0], t[1], t[2], t[3], t[4] + dx, t[5] + dy)
                                    movedComponents += 1

        font.enableUpdateInterface()
        undoManager.endUndoGrouping()

        print(f"DEBUG: Nodes moved: {movedNodes}")
        print(f"DEBUG: Anchors moved: {movedAnchors}")
        print(f"DEBUG: Components moved: {movedComponents}")


# Inicialización segura
if "moveNodesWindow" in globals() and moveNodesWindow is not None:
    moveNodesWindow.w.show()
else:
    moveNodesWindow = MoveNodesAllMastersFloating()