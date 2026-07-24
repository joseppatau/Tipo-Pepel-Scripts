import objc
from GlyphsApp.plugins import *
from GlyphsApp.plugins import pathForResource
from GlyphsApp import Glyphs, OFFCURVE, CURVE
from AppKit import NSImage, NSMakeRect, NSMenuItem, NSSlider, NSTextField, NSView
import traceback


class BackgroundMagneticHandles(SelectTool):

    DEFAULT_TOLERANCE = 15.0
    DEFAULTS_KEY = "com.tipopepel.BackgroundMagneticHandles.tolerance"

    @objc.python_method
    def settings(self):
        self.name = "Background Magnetic Handles"
        self.keyboardShortcut = 'm'
        self._toolBarIcon = self.loadToolbarIcon()
        self._toleranceLabel = None

    @objc.python_method
    def loadToolbarIcon(self):
        iconPath = pathForResource("toolbar", "pdf", __file__)
        if not iconPath:
            return None
        icon = NSImage.alloc().initWithContentsOfFile_(iconPath)
        if icon:
            icon.setTemplate_(True)
        return icon

    def toolBarIcon(self):
        return self._toolBarIcon

    def toolbarIcon(self):
        return self.toolBarIcon()

    @objc.python_method
    def tolerance(self):
        try:
            value = Glyphs.defaults[self.DEFAULTS_KEY]
            return float(value)
        except Exception:
            return self.DEFAULT_TOLERANCE

    @objc.python_method
    def setTolerance(self, value):
        value = max(1.0, min(80.0, float(value)))
        Glyphs.defaults[self.DEFAULTS_KEY] = value
        if self._toleranceLabel:
            self._toleranceLabel.setStringValue_("Tolerance: %.0f units" % value)

    def toleranceSliderChanged_(self, sender):
        self.setTolerance(sender.floatValue())

    def addMenuItemsForEvent_toMenu_(self, event, menu):
        menu.addItem_(NSMenuItem.separatorItem())

        titleItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Background Magnetic Handles", None, ""
        )
        titleItem.setEnabled_(False)
        menu.addItem_(titleItem)

        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("", None, "")
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 220, 46))

        label = NSTextField.alloc().initWithFrame_(NSMakeRect(12, 24, 196, 18))
        label.setEditable_(False)
        label.setBordered_(False)
        label.setDrawsBackground_(False)
        label.setStringValue_("Tolerance: %.0f units" % self.tolerance())
        view.addSubview_(label)
        self._toleranceLabel = label

        slider = NSSlider.alloc().initWithFrame_(NSMakeRect(12, 4, 196, 20))
        slider.setMinValue_(1.0)
        slider.setMaxValue_(80.0)
        slider.setFloatValue_(self.tolerance())
        slider.setTarget_(self)
        slider.setAction_("toleranceSliderChanged:")
        view.addSubview_(slider)

        item.setView_(view)
        menu.addItem_(item)

    def mouseDragged_(self, event):

        try:
            # comportamiento normal de la herramienta
            SelectTool.mouseDragged_(self, event)

            font = Glyphs.font
            if not font:
                return

            layer = font.selectedLayers[0]
            bg = layer.background

            if not bg:
                return

            tolerance = self.tolerance()

            # Recopilar todos los nodos seleccionados
            selected_nodes = []
            for path in layer.paths:
                for node in path.nodes:
                    if node.selected and node.type != OFFCURVE:
                        selected_nodes.append(node)

            if not selected_nodes:
                return

            # Procesar cada nodo seleccionado
            for selected_node in selected_nodes:
                nodo_encontrado = None
                
                # Buscar coincidencia en background
                for bgPath in bg.paths:       
                    for bgNode in bgPath.nodes:
                        if bgNode.type != OFFCURVE:
                            # Calcular distancia
                            distancia_x = abs(selected_node.x - bgNode.x)
                            distancia_y = abs(selected_node.y - bgNode.y)

                            # Si está dentro de la tolerancia en ambos ejes
                            if distancia_x < tolerance and distancia_y < tolerance:
                                nodo_encontrado = bgNode
                                break
                    if nodo_encontrado:
                        break
                
                # Si encontramos una coincidencia
                if nodo_encontrado:
                    # Guardar referencias a los handles actuales
                    current_prev = selected_node.prevNode
                    current_next = selected_node.nextNode
                    
                    # Mover el nodo principal
                    selected_node.x = nodo_encontrado.x
                    selected_node.y = nodo_encontrado.y
                    
                    # Mover los handles si existen
                    if current_prev and nodo_encontrado.prevNode and current_prev.type == OFFCURVE:
                        current_prev.x = nodo_encontrado.prevNode.x
                        current_prev.y = nodo_encontrado.prevNode.y
                    
                    if current_next and nodo_encontrado.nextNode and current_next.type == OFFCURVE:
                        current_next.x = nodo_encontrado.nextNode.x
                        current_next.y = nodo_encontrado.nextNode.y

        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
