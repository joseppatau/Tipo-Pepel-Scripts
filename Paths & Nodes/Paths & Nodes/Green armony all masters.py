# MenuTitle: green armony all masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import vanilla
from GlyphsApp import Glyphs, GSPath, CURVE, OFFCURVE
from math import sqrt
from Foundation import NSPoint

# ------------------ Funciones auxiliares ------------------
def getIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    return px, py

def getDist(a, b):
    return sqrt((b.x - a.x)**2 + (b.y - a.y)**2)

def remap(oldValue, oldMin, oldMax, newMin, newMax):
    try:
        oldRange = (oldMax - oldMin)
        newRange = (newMax - newMin)
        return (((oldValue - oldMin) * newRange) / oldRange) + newMin
    except:
        return None

def harmonize(layer, shapeIndex, nodeIndex):
    """Aplica la armonización a un nodo CURVE smooth con offcurves delante y detrás."""
    node = layer.shapes[shapeIndex].nodes[nodeIndex]
    N = node.nextNode
    P = node.prevNode
    NN = node.nextNode.nextNode
    PP = node.prevNode.prevNode

    # Intersección de las rectas prolongadas de los offcurves
    xIntersect, yIntersect = getIntersection(
        N.x, N.y, NN.x, NN.y,
        P.x, P.y, PP.x, PP.y,
    )
    intersection = NSPoint(xIntersect, yIntersect)

    # Ratios
    r0 = getDist(NN, N) / getDist(N, intersection)
    r1 = getDist(intersection, P) / getDist(P, PP)
    ratio = sqrt(r0 * r1)

    # Nueva posición del nodo oncurve
    t = ratio / (ratio + 1)
    node.x = remap(t, 0, 1, N.x, P.x)
    node.y = remap(t, 0, 1, N.y, P.y)

# ------------------ Ventana flotante ------------------
class GreenHarmonyWindow(object):
    def __init__(self):
        self.w = vanilla.FloatingWindow((100, 80), "🌱 Armonía Verde", minSize=(250, 80), maxSize=(400, 100))
        self.w.applyOnlySelected = vanilla.CheckBox((10, 10, -10, 20), "Only selected", value=False)
        self.w.applyButton = vanilla.Button((10, 40, -10, 30), "Apply", callback=self.applyToAllMasters)
        self.w.setDefaultButton(self.w.applyButton)
        self.w.center()
        self.w.open()

    def applyToAllMasters(self, sender):
        """Recorre todas las capas del glifo actual y aplica la armonía."""
        doc = Glyphs.currentDocument
        if not doc:
            print("No hay documento abierto.")
            return

        glyph = doc.selectedLayers()[0].parent
        if not glyph:
            print("No hay glifo seleccionado.")
            return

        onlySelected = self.w.applyOnlySelected.get()

        # Recorremos todas las capas (masters y capas especiales)
        for layer in glyph.layers:
            # Puedes cambiar la condición si quieres solo masters:
            # if not layer.isMasterLayer: continue
            print(f"Procesando capa: {layer.name}")
            self.processLayer(layer, onlySelected)

        # Redibujar la interfaz
        Glyphs.redraw()

    def processLayer(self, layer, onlySelected):
        """Aplica harmonize a cada nodo que cumpla las condiciones."""
        if not layer.shapes:
            return
        selection = set(layer.selection) if onlySelected else None
        for i, shape in enumerate(layer.shapes):
            if not isinstance(shape, GSPath):
                continue
            for j, node in enumerate(shape.nodes):
                if onlySelected and node not in selection:
                    continue
                if node.type == CURVE and node.smooth:
                    N = node.nextNode
                    P = node.prevNode
                    if N and P and N.type == OFFCURVE and P.type == OFFCURVE:
                        harmonize(layer, i, j)

# ------------------ Lanzar la ventana ------------------
if __name__ == "__main__":
    import time
    time.sleep(0.1)
    GreenHarmonyWindow()