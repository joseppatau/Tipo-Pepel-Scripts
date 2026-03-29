# MenuTitle: Alignment (FIXED EDGES - PATHS)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs
from AppKit import NSAffineTransform
import traceback


class AlignTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((150, 260), "Alignment")
        
        self.w.labelX = vanilla.TextBox((15, 10, -15, 20), "X —")
        self.w.options = vanilla.RadioGroup(
            (45, 10, -15, 150),
            ["Up", "Center", "Down", "Left", "Center", "Right"]
        )
        self.w.labelY = vanilla.TextBox((15, 70, -15, 20), "Y |")
        self.w.options.set(0)
        
        self.w.alignButton = vanilla.Button(
            (15, 170, -15, 25),
            "Align Paths",
            callback=self.align
        )
        
        self.w.scope = vanilla.RadioGroup(
            (15, 205, -15, 40),
            ["Current", "All masters"]
        )
        self.w.scope.set(0)
        self.w.divider = vanilla.HorizontalLine((15, 195, -15, 1))
        self.w.open()

    def getSelectedPaths(self, layer):
        """Obtener paths seleccionados"""
        paths = []
        try:
            for path in layer.paths:
                if path.selected:
                    paths.append(path)
        except:
            pass
        return paths

    def getPathBounds(self, path):
        """Obtener bounds de un path de forma segura"""
        try:
            if hasattr(path, 'bounds'):
                b = path.bounds
                minX = float(b.origin.x)
                minY = float(b.origin.y)
                maxX = float(b.origin.x + b.size.width)
                maxY = float(b.origin.y + b.size.height)
                return (minX, minY, maxX, maxY)
        except:
            pass
        
        # Fallback: calcular bounds desde los nodos
        minX = minY = float('inf')
        maxX = maxY = float('-inf')
        
        try:
            for node in path.nodes:
                x = float(node.x)
                y = float(node.y)
                minX = min(minX, x)
                minY = min(minY, y)
                maxX = max(maxX, x)
                maxY = max(maxY, y)
        except:
            pass
        
        if minX == float('inf'):
            return (0, 0, 0, 0)
        
        return (minX, minY, maxX, maxY)

    def getReference(self, paths, option):
        """Calcular el valor de referencia para alinear"""
        values = []
        
        for path in paths:
            try:
                minX, minY, maxX, maxY = self.getPathBounds(path)
                
                if option == 0:  # Up (superior)
                    values.append(maxY)
                elif option == 1:  # Center Y (centro vertical)
                    values.append((minY + maxY) / 2)
                elif option == 2:  # Down (inferior)
                    values.append(minY)
                elif option == 3:  # Left (izquierda)
                    values.append(minX)
                elif option == 4:  # Center X (centro horizontal)
                    values.append((minX + maxX) / 2)
                elif option == 5:  # Right (derecha)
                    values.append(maxX)
            except:
                continue
        
        if not values:
            return None
        
        if option in [0, 5]:
            return max(values)
        elif option in [2, 3]:
            return min(values)
        else:
            return sum(values) / len(values)

    def movePath(self, path, option, ref):
        """Mover un path al valor de referencia"""
        try:
            minX, minY, maxX, maxY = self.getPathBounds(path)
            dx = dy = 0
            
            if option == 0:  # Up
                dy = ref - maxY
            elif option == 1:  # Center Y
                dy = ref - ((minY + maxY) / 2)
            elif option == 2:  # Down
                dy = ref - minY
            elif option == 3:  # Left
                dx = ref - minX
            elif option == 4:  # Center X
                dx = ref - ((minX + maxX) / 2)
            elif option == 5:  # Right
                dx = ref - maxX
            
            if dx != 0 or dy != 0:
                # Mover todos los nodos del path
                for node in path.nodes:
                    node.x += dx
                    node.y += dy
        except:
            pass

    def alignLayer(self, layer):
        """Alinear los paths seleccionados en una capa"""
        try:
            # Obtener paths seleccionados
            paths = self.getSelectedPaths(layer)
            
            # Si no hay paths seleccionados, usar todos los paths
            if not paths:
                paths = list(layer.paths)
            
            if not paths:
                return
            
            option = self.w.options.get()
            ref = self.getReference(paths, option)
            
            if ref is not None:
                for path in paths:
                    self.movePath(path, option, ref)
        except:
            traceback.print_exc()

    def align(self, sender):
        """Callback del botón align"""
        try:
            font = Glyphs.font
            if not font.selectedLayers:
                return
            
            font.disableUpdateInterface()
            
            try:
                for layer in font.selectedLayers:
                    glyph = layer.parent
                    
                    if self.w.scope.get() == 0:
                        self.alignLayer(layer)
                    else:
                        for l in glyph.layers:
                            if l.isMasterLayer or l.isSpecialLayer:
                                self.alignLayer(l)
            finally:
                font.enableUpdateInterface()
        except:
            traceback.print_exc()


# Ejecutar el script
AlignTool()