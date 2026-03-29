from GlyphsApp.plugins import *
from GlyphsApp import Glyphs, OFFCURVE, CURVE
import traceback


class BackgroundMagneticHandles(SelectTool):

    def settings(self):
        self.name = "Background Magnetic Handles"
        self.keyboardShortcut = 'm'

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

            tolerance = 15.0  # Tolerancia intermedia

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