# MenuTitle: Enter to All Masters
# -*- coding: utf-8 -*-
# Description: Change type node in all masters
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2


from GlyphsApp import *
import vanilla

class ApplyEnterAllMastersFixed(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((240, 100), "Apply ENTER (Real)")

        self.w.button = vanilla.Button((20, 20, -20, 30), "Apply ENTER", callback=self.run)

        self.w.open()

    def run(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No font")
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        print("\n=== ENTER FIX DEBUG ===")
        print("Glyph:", glyph.name)

        selectedIndexes = []

        # Detectar nodes seleccionats
        for pIndex, path in enumerate(layer.paths):
            for nIndex, node in enumerate(path.nodes):
                if node.selected:
                    selectedIndexes.append((pIndex, nIndex))
                    print(f"✔ Selected → Path {pIndex}, Node {nIndex}, Connection {node.connection}")

        if not selectedIndexes:
            print("⚠️ No selection")
            return

        # Aplicar a tots els masters
        for masterLayer in glyph.layers:
            if not masterLayer.isMasterLayer:
                continue

            print(f"\n--- Master: {masterLayer.name} ---")

            for pIndex, nIndex in selectedIndexes:
                try:
                    node = masterLayer.paths[pIndex].nodes[nIndex]

                    print(f"Before: {node.connection}")

                    # 👉 AIXÒ ÉS EL REAL "ENTER"
                    if node.connection == GSSHARP:
                        node.connection = GSSMOOTH
                        print("   SHARP → SMOOTH (square → round)")
                    else:
                        node.connection = GSSHARP
                        print("   SMOOTH → SHARP (round → square)")

                except Exception as e:
                    print("❌ Error:", e)

        print("\n=== DONE ===")

ApplyEnterAllMastersFixed()