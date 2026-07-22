# MenuTitle: Copy Selected Glyphs to Other Masters
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs
from vanilla import FloatingWindow, Button, TextBox
import copy


class CopyToMastersUI(object):

    def __init__(self):
        self.w = FloatingWindow(
            (440, 135),
            "Copy Selected Glyphs to Other Masters"
        )

        self.w.info = TextBox(
            (15, 15, -15, 55),
            "Copies the current master layer content, width and Metrics Keys\n"
            "of the selected glyphs to all other masters, replacing their\n"
            "existing content."
        )

        self.w.applyButton = Button(
            (160, 90, 120, 30),
            "Apply",
            callback=self.copyLayers
        )

        self.w.open()

    def copyLayers(self, sender):
        font = Glyphs.font

        if not font:
            print("No font open.")
            return

        selectedLayers = font.selectedLayers

        if not selectedLayers:
            print("No glyphs selected.")
            return

        currentMaster = font.selectedFontMaster
        currentMasterID = currentMaster.id

        Glyphs.clearLog()
        print("=== Copy Selected Glyphs to Other Masters ===")
        print("Source master: %s" % currentMaster.name)

        font.disableUpdateInterface()

        try:
            for selectedLayer in selectedLayers:
                glyph = selectedLayer.parent
                sourceLayer = glyph.layers[currentMasterID]

                if not sourceLayer:
                    print("\n⚠️ Missing source layer: %s" % glyph.name)
                    continue

                print("\nProcessing %s" % glyph.name)

                for master in font.masters:
                    if master.id == currentMasterID:
                        continue

                    targetLayer = glyph.layers[master.id]

                    if not targetLayer:
                        print("  ⚠️ Missing target layer: %s" % master.name)
                        continue

                    # Remove existing target content
                    targetLayer.shapes = []
                    targetLayer.anchors = []
                    targetLayer.guides = []

                    # Copy layer width
                    targetLayer.width = sourceLayer.width

                    # Copy layer-specific Metrics Keys
                    targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
                    targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
                    targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey

                    # Copy shapes
                    for shape in sourceLayer.shapes:
                        targetLayer.shapes.append(copy.copy(shape))

                    # Copy anchors
                    for anchor in sourceLayer.anchors:
                        targetLayer.anchors.append(copy.copy(anchor))

                    # Copy guides
                    for guide in sourceLayer.guides:
                        targetLayer.guides.append(copy.copy(guide))

                    # Recalculate metrics when Metrics Keys are present
                    if (
                        targetLayer.leftMetricsKey
                        or targetLayer.rightMetricsKey
                        or targetLayer.widthMetricsKey
                    ):
                        try:
                            targetLayer.syncMetrics()
                        except Exception as error:
                            print(
                                "  ⚠️ Could not sync metrics in %s: %s"
                                % (master.name, error)
                            )

                    print(
                        "  → copied to %s | L: %s | R: %s | W: %s"
                        % (
                            master.name,
                            targetLayer.leftMetricsKey or "—",
                            targetLayer.rightMetricsKey or "—",
                            targetLayer.widthMetricsKey or "—",
                        )
                    )

        except Exception:
            import traceback
            print("\nERROR:")
            print(traceback.format_exc())

        finally:
            font.enableUpdateInterface()

        print("\nDONE.")


CopyToMastersUI()