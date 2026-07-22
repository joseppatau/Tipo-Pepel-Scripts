# MenuTitle: Open Corners in All Masters (Custom Length)
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, GSNode, GSOFFCURVE
from vanilla import FloatingWindow, Button, TextBox, EditText


class OpenCornersAllMasters:

    def __init__(self):
        self.w = FloatingWindow(
            (130, 100),
            "Open Corners All Masters"
        )

        self.w.lengthLabel = TextBox(
            (20, 20, 140, 20),
            "Lenght:"
        )

        self.w.lengthInput = EditText(
            (80, 18, 30, 24),
            "10"
        )

        self.w.applyButton = Button(
            (20, 50, 90, 30),
            "Apply",
            callback=self.apply
        )



        self.w.open()
        self.w._window.setLevel_(4)

    def log(self, msg):
        print(msg)
        self.w.info.set(msg)

    def get_selected_signature(self, layer):
        sig = []

        for obj in layer.selection:
            if not isinstance(obj, GSNode):
                continue

            if obj.type == GSOFFCURVE:
                continue

            found = False

            for p_idx, path in enumerate(layer.paths):
                for n_idx, node in enumerate(path.nodes):
                    if node == obj:
                        sig.append((p_idx, n_idx))
                        found = True
                        break
                if found:
                    break

        return sig

    def get_offset(self):
        try:
            value = float(self.w.lengthInput.get())
            if value <= 0:
                return 10.0
            return value
        except:
            return 10.0

    def apply(self, sender):
        font = Glyphs.font

        if not font:
            self.log("No hi ha font oberta.")
            return

        if not font.selectedLayers:
            self.log("No hi ha layer seleccionat.")
            return

        base_layer = font.selectedLayers[0]
        glyph = base_layer.parent

        selected = self.get_selected_signature(base_layer)

        if not selected:
            self.log("No hi ha nodes on-curve seleccionats.")
            return

        offset = self.get_offset()
        opened = 0

        glyph.beginUndo()
        font.disableUpdateInterface()

        try:
            for layer in glyph.layers:

                if not layer.paths:
                    continue

                for p_idx, n_idx in sorted(
                    selected,
                    key=lambda x: (x[0], x[1]),
                    reverse=True
                ):

                    if p_idx >= len(layer.paths):
                        continue

                    path = layer.paths[p_idx]

                    if n_idx >= len(path.nodes):
                        continue

                    node = path.nodes[n_idx]

                    if node.type == GSOFFCURVE:
                        continue

                    try:
                        layer.openCornerAtNode_offset_(node, offset)
                        opened += 1
                    except Exception as e:
                        print(f"Error a {layer.name}: {e}")

        finally:
            font.enableUpdateInterface()
            glyph.endUndo()

        self.log(f"Fet: {opened} corners oberts (offset {offset}).")


OpenCornersAllMasters()