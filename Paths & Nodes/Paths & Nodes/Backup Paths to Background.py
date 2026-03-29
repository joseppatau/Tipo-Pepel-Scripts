# MenuTitle: Backup Paths to Background
# -*- coding: utf-8 -*-
# Description: Copies current outlines to background layers for all glyphs and masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
import vanilla
from GlyphsApp import Glyphs

class CopyToBackgroundTool:

    def __init__(self):

        self.w = vanilla.FloatingWindow((260, 120), "Backup Paths to Background")

        self.w.button = vanilla.Button(
            (20, 30, -20, 30),
            "Copy ALL to background",
            callback=self.copyAll
        )

        self.w.status = vanilla.TextBox(
            (20, 70, -20, 20),
            "Idle"
        )

        self.w.open()

    # =========================

    def copyAll(self, sender):

        font = Glyphs.font
        if not font:
            self.w.status.set("No font open")
            return

        count = 0

        font.disableUpdateInterface()

        for glyph in font.glyphs:
            for master in font.masters:

                layer = glyph.layers[master.id]
                if not layer:
                    continue

                # 🔥 copia correcta
                bg = layer.copy()
                bg.setAssociatedMasterId_(master.id)
                layer.background = bg

                count += 1

        font.enableUpdateInterface()

        self.w.status.set(f"Done: {count} layers")
        print(f"✅ Copiados {count} layers al background")


CopyToBackgroundTool()