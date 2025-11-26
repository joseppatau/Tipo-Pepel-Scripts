# MenuTitle: Duplicate components in all masters (improved)
# -*- coding: utf-8 -*-
# Description: Duplicate components in all masters
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

__doc__ = """
Duplicate components in all masters
"""

font = Glyphs.font
selectedLayers = font.selectedLayers

if not selectedLayers:
    Message("No glyph selected", "Select a glyph before running this script.", OKButton="OK")
else:
    layer = selectedLayers[0]
    glyph = layer.parent

    # Selected components
    selectedComponents = [c for c in layer.components if c.selected]
    if not selectedComponents:
        Message("No component selected", "Select at least one component in the active layer.", OKButton="OK")
    else:
        for master in font.masters:
            targetLayer = glyph.layers[master.id]
            if targetLayer != layer:
                for sourceComponent in selectedComponents:
                    # Create new copy
                    newComponent = GSComponent(sourceComponent.componentName)
                    newComponent.transform = sourceComponent.transform
                    targetLayer.components.append(newComponent)

        print(f"Duplicated {len(selectedComponents)} components (including smart components) into all masters of {glyph.name}.")
