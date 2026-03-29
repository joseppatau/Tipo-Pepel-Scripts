# MenuTitle: Random Node Movement
# -*- coding: utf-8 -*-
# Description: Randomly offsets selected nodes based on local geometry and user-defined intensity.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

import GlyphsApp
import random, math
from vanilla import FloatingWindow, Slider, TextBox, Button

# -------------------------------------------------
# Utils
# -------------------------------------------------

def distance(n1, n2):
    return math.hypot(n2.x - n1.x, n2.y - n1.y)

def groupNodesByPosition(nodes, precision=0.001):
    groups = {}
    for n in nodes:
        key = (round(n.x / precision), round(n.y / precision))
        groups.setdefault(key, []).append(n)
    return groups

# -------------------------------------------------
# UI
# -------------------------------------------------

class RandomizeNodesUI(object):
    def __init__(self):
        self.w = FloatingWindow((360, 140), "Randomize Selected Nodes")
        
        self.w.text = TextBox(
            (15, 15, -15, 20),
            "Intensitat (% distància als nodes veïns):"
        )
        self.w.slider = Slider(
            (15, 40, -15, 20),
            minValue=0,
            maxValue=100,
            value=20
        )
        self.w.button = Button(
            (130, 80, 100, 30),
            "Aplicar",
            callback=self.applyRandomize
        )
        
        self.w.open()
        self.w.makeKey()

    # -------------------------------------------------
    # Core logic
    # -------------------------------------------------

    def applyRandomize(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            print("⚠️ Cap capa seleccionada.")
            return
        
        percent = self.w.slider.get() / 100.0
        total = 0
        epsilon = 0.01
        
        for layer in font.selectedLayers:
            glyph = layer.parent
            glyph.beginUndo()
            
            for path in layer.paths:
                nodes = path.nodes
                groups = groupNodesByPosition(nodes)

                for group in groups.values():
                    if not any(n.selected for n in group):
                        continue

                    # Distància efectiva (real o sintètica)
                    dists = []
                    for n in group:
                        i = nodes.index(n)
                        dists.append(distance(n, nodes[i - 1]))
                        dists.append(distance(n, nodes[(i + 1) % len(nodes)]))

                    localDist = max(max(dists), 50.0)
                    maxOffset = localDist * percent

                    dx = random.uniform(-maxOffset, maxOffset)
                    dy = random.uniform(-maxOffset, maxOffset)

                    for idx, n in enumerate(group):
                        n.x += dx + idx * epsilon
                        n.y += dy + idx * epsilon
                        total += 1
            
            glyph.endUndo()
        
        font.currentTab.redraw()
        print(
            f"✅ {total} nodes randomitzats "
            f"(desplaçament amplificat, intensitat {percent*100:.0f}%)."
        )

# -------------------------------------------------
# Run
# -------------------------------------------------

RandomizeNodesUI()
