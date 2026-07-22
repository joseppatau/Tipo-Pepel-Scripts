#MenuTitle: Copy Sidebearings Between Masters
# -*- coding: utf-8 -*-

import GlyphsApp
from vanilla import FloatingWindow, PopUpButton, TextBox, Button, RadioGroup

font = Glyphs.font


class CopySidebearingsBetweenMasters(object):
    def __init__(self):
        if not font:
            print("No font open.")
            return

        self.w = FloatingWindow((420, 190), "Copy Sidebearings Between Masters")

        self.w.title = TextBox((15, 15, -15, 20), "Select source master:")
        self.w.sourceMaster = PopUpButton((15, 40, -15, 25), [m.name for m in font.masters])

        self.w.scopeTitle = TextBox((15, 75, -15, 20), "Apply to:")
        self.w.scope = RadioGroup((15, 95, -15, 34), ["Selected glyphs", "All glyphs"], isVertical=False)
        self.w.scope.set(0)

        self.w.go = Button((15, 145, -15, 28), "Copy Sidebearings", callback=self.copySidebearings)

        self.w.open()
        self.w.makeKey()

    def _selectedGlyphs(self):
        glyphs = []
        seen = set()
        for layer in font.selectedLayers:
            g = layer.parent
            if g and g.name not in seen:
                seen.add(g.name)
                glyphs.append(g)
        return glyphs

    def _log(self, tag, g, layer):
        print(
            "%s %s | %s | LSB=%s RSB=%s | LMK=%s RMK=%s"
            % (
                tag,
                g.name,
                layer.name,
                layer.LSB,
                layer.RSB,
                layer.leftMetricsKey,
                layer.rightMetricsKey,
            )
        )

    def copySidebearings(self, sender):
        sourceMaster = font.masters[self.w.sourceMaster.get()]
        targetMaster = font.selectedFontMaster

        if not targetMaster:
            print("No target master selected.")
            return
        if sourceMaster.id == targetMaster.id:
            print("Source and target master are the same.")
            return

        glyphs = self._selectedGlyphs() if self.w.scope.get() == 0 else list(font.glyphs)

        print("---- START ----")
        print("Source:", sourceMaster.name, "| Target:", targetMaster.name, "| Glyphs:", len(glyphs))

        font.disableUpdateInterface()
        try:
            for g in glyphs:
                sourceLayer = g.layers[sourceMaster.id]
                targetLayer = g.layers[targetMaster.id]

                if not sourceLayer or not targetLayer:
                    print("SKIP", g.name)
                    continue

                print("----")
                self._log("SOURCE BEFORE", g, sourceLayer)
                self._log("TARGET BEFORE", g, targetLayer)

                g.beginUndo()
                try:
                    targetLayer.leftMetricsKey = None
                    targetLayer.rightMetricsKey = None

                    targetLayer.LSB = sourceLayer.LSB
                    targetLayer.RSB = sourceLayer.RSB

                    self._log("TARGET WRITTEN", g, targetLayer)
                finally:
                    g.endUndo()

                self._log("TARGET AFTER", g, targetLayer)

        finally:
            font.enableUpdateInterface()

        print("---- DONE ----")


CopySidebearingsBetweenMasters()