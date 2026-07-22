# MenuTitle: Reset Handles Tool - ( 1 & 2 keys)

from GlyphsApp import *
from vanilla import *
from AppKit import NSEvent
import traceback

NSEventMaskKeyDown = 1 << 10

class ResetHandlesAlignmentTool(object):

    def __init__(self):
        self.w = Window((430, 240), "Reset Handles Alignment Tool")

        self.w.enabledBtn = Button((15, 15, 400, 45), "🔴 DESACTIVADO - Click para activar", callback=self.toggleEnabled)
        self.w.enabledBtn.getNSButton().setBezelStyle_(1)

        self.w.debugMode = CheckBox((15, 70, 150, 20), "Modo DEBUG", value=True, callback=self.toggleDebug)

        self.w.legend = TextBox(
            (15, 95, 400, 100),
            "1 → Alinear handles seleccionados\n2 → Alinear TODOS los handles\n\nModo manual: primero X, luego Y, según el lado del handle respecto al nodo.",
            sizeStyle='small'
        )

        self.enabled = False
        self.monitor = None
        self.debug = True
        self.w.open()

        print("🚀 Reset Handles Alignment Tool iniciado")

    def toggleDebug(self, sender):
        self.debug = self.w.debugMode.get()
        print(f"🔍 DEBUG: {'ON' if self.debug else 'OFF'}")

    def toggleEnabled(self, sender):
        self.enabled = not self.enabled
        if self.enabled:
            self.w.enabledBtn.setTitle("🟢 ACTIVADO - Click para desactivar")
            self.monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
                NSEventMaskKeyDown, self.handleKeyEvent
            )
            print("✅ ACTIVADO")
        else:
            self.w.enabledBtn.setTitle("🔴 DESACTIVADO - Click para activar")
            if self.monitor:
                NSEvent.removeMonitor_(self.monitor)
                self.monitor = None
            print("❌ DESACTIVADO")

    def handleKeyEvent(self, event):
        if not self.enabled:
            return event
        try:
            key = event.characters().lower()
            if key == '1':
                self.alignSelectedHandles()
                return None
            elif key == '2':
                self.alignAllHandles()
                return None
        except Exception as e:
            print("Error en evento:", e)
            traceback.print_exc()
        return event

    def log(self, msg):
        if self.debug:
            print(f"🔍 {msg}")

    def alignHandleToNode(self, handle, node):
        hx = handle.position.x
        hy = handle.position.y
        nx = node.position.x
        ny = node.position.y

        changed = False

        # Alinear en X según esté a izquierda o derecha
        if hx != nx:
            handle.position = (nx, hy)
            changed = True

        # Alinear en Y según esté arriba o abajo
        if hy != ny:
            handle.position = (handle.position.x, ny)
            changed = True

        return changed

    def getAssociatedNode(self, nodes, handle_index):
        """
        Busca el nodo on-curve asociado al handle.
        Prioriza el CURVE/LINE/QCURVE más cercano estructuralmente.
        """
        left = None
        right = None

        for i in range(handle_index - 1, -1, -1):
            if nodes[i].type in (CURVE, QCURVE, LINE):
                left = nodes[i]
                break

        for i in range(handle_index + 1, len(nodes)):
            if nodes[i].type in (CURVE, QCURVE, LINE):
                right = nodes[i]
                break

        if left and right:
            dl = abs(left.position.x - nodes[handle_index].position.x) + abs(left.position.y - nodes[handle_index].position.y)
            dr = abs(right.position.x - nodes[handle_index].position.x) + abs(right.position.y - nodes[handle_index].position.y)
            return left if dl <= dr else right

        return left or right

    def alignAllHandles(self):
        print("=" * 60)
        print("🔧 Alineando TODOS los handles...")

        font = Glyphs.font
        if not font or not font.selectedLayers:
            print("❌ No hay capa seleccionada")
            return

        layer = font.selectedLayers[0]
        total = 0

        for pathIndex, path in enumerate(layer.paths):
            nodes = path.nodes

            for i, node in enumerate(nodes):
                if node.type != OFFCURVE:
                    continue

                target = self.getAssociatedNode(nodes, i)
                if target:
                    if self.alignHandleToNode(node, target):
                        total += 1
                        self.log(f"Path {pathIndex}: handle {i} alineado con nodo {target.type}")

        if total > 0:
            Glyphs.redraw()
            print(f"✅ {total} handles alineados")
            Glyphs.showNotification("Reset Handles", f"✅ {total} handles alineados")
        else:
            print("ℹ️ No hay handles para alinear")

        print("=" * 60)

    def alignSelectedHandles(self):
        print("=" * 60)
        print("🔧 Alineando handles seleccionados...")

        font = Glyphs.font
        if not font or not font.selectedLayers:
            print("❌ No hay capa seleccionada")
            return

        layer = font.selectedLayers[0]
        total = 0

        for pathIndex, path in enumerate(layer.paths):
            nodes = path.nodes

            for i, node in enumerate(nodes):
                if not node.selected:
                    continue

                if node.type == OFFCURVE:
                    target = self.getAssociatedNode(nodes, i)
                    if target:
                        if self.alignHandleToNode(node, target):
                            total += 1
                            self.log(f"Path {pathIndex}: selected handle {i} alineado")

                elif node.type in (CURVE, QCURVE, LINE):
                    x = node.position.x
                    y = node.position.y

                    for j in (i - 1, i - 2, i + 1, i + 2):
                        if 0 <= j < len(nodes) and nodes[j].type == OFFCURVE and nodes[j].selected:
                            if self.alignHandleToNode(nodes[j], node):
                                total += 1
                                self.log(f"Path {pathIndex}: selected handle {j} alineado con nodo {i}")

        if total > 0:
            Glyphs.redraw()
            print(f"✅ {total} handles seleccionados alineados")
            Glyphs.showNotification("Reset Handles", f"✅ {total} handles seleccionados")
        else:
            print("ℹ️ No hay handles seleccionados")

        print("=" * 60)

    def windowWillClose(self, sender):
        if self.monitor:
            NSEvent.removeMonitor_(self.monitor)
        print("👋 Tool cerrado")

ResetHandlesAlignmentTool()