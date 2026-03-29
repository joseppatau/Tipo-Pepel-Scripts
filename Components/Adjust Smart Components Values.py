# MenuTitle: Adjust Smart Components Values (.sc) Final
# -*- coding: utf-8 -*-
# Description: Adjusts smart component axis values for selected glyphs in the current master.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *


class AdjustSmartSC:

    def __init__(self):

        font = Glyphs.font
        if not font:
            Message("Error", "Open a font first.", OKButton="OK")
            return

        # Verificar que haya glifos seleccionados
        if not font.selectedLayers:
            Message("Info", "Select at least one glyph in the font view.", OKButton="OK")
            return

        self.smartAxes = self.detectSmartAxes()

        if not self.smartAxes:
            Message("Info", "No smart components found in selected glyphs.", OKButton="OK")
            return

        height = max(200, 120 + 35 * len(self.smartAxes))
        self.w = FloatingWindow((380, height), "Adjust Smart SC")

        self.w.info = TextBox((15, 15, -15, 20), "Smart Component Axes:")

        self.axisInputs = []
        y = 50

        for i, axis in enumerate(self.smartAxes):

            self.w.__setattr__(
                f"label_{i}",
                TextBox((15, y + 3, 160, 20), axis.name)
            )

            self.w.__setattr__(
                f"input_{i}",
                EditText((190, y, 120, 22), "0")
            )

            self.axisInputs.append(
                (axis, getattr(self.w, f"input_{i}"))
            )

            y += 35

        self.w.applyButton = Button(
            (15, y + 10, -15, 30),
            "Apply",
            callback=self.apply
        )

        self.w.open()

    # -----------------------------------------------------

    def detectSmartAxes(self):

        font = Glyphs.font
        selected_layers = font.selectedLayers

        # Asegurarse de que selected_layers no sea None
        if not selected_layers:
            return []

        for layer in selected_layers:
            if not layer:
                continue

            # Verificar que la capa tenga componentes
            if not hasattr(layer, 'components') or not layer.components:
                continue

            for comp in layer.components:
                if not comp:
                    continue

                # Obtener el glifo base del componente
                baseGlyph = font.glyphs[comp.componentName]
                if baseGlyph and hasattr(baseGlyph, 'smartComponentAxes') and baseGlyph.smartComponentAxes:
                    return baseGlyph.smartComponentAxes

        return []

    # -----------------------------------------------------

    def apply(self, sender):

        font = Glyphs.font
        master = font.selectedFontMaster
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return

        masterID = master.id

        values = {}

        for axis, inputField in self.axisInputs:
            try:
                values[axis.id] = float(inputField.get())
            except:
                values[axis.id] = 0.0

        font.disableUpdateInterface()

        try:
            selected_layers = font.selectedLayers

            # Asegurarse de que selected_layers no sea None
            if not selected_layers:
                Message("Info", "No glyphs selected.", OKButton="OK")
                return

            for layer in selected_layers:
                if not layer:
                    continue

                glyph = layer.parent
                if not glyph:
                    continue

                targetLayer = glyph.layers[masterID]
                if not targetLayer:
                    continue

                # Verificar que la capa tenga componentes
                if not hasattr(targetLayer, 'components') or not targetLayer.components:
                    continue

                for comp in targetLayer.components:
                    if not comp:
                        continue

                    baseGlyph = font.glyphs[comp.componentName]
                    if not baseGlyph:
                        continue

                    if not hasattr(baseGlyph, 'smartComponentAxes') or not baseGlyph.smartComponentAxes:
                        continue

                    # Actualizar valores del componente inteligente
                    for axis in baseGlyph.smartComponentAxes:
                        if axis.id in values:
                            # Asegurarse de que smartComponentValues existe
                            if not hasattr(comp, 'smartComponentValues'):
                                continue
                            comp.smartComponentValues[axis.id] = values[axis.id]

        except Exception as e:
            print(f"Error applying values: {e}")
            import traceback
            traceback.print_exc()
            Message("Error", f"An error occurred: {e}", OKButton="OK")

        finally:
            font.enableUpdateInterface()

        Message("Done", "Smart values updated.", OKButton="OK")


# Ejecutar el script
AdjustSmartSC()