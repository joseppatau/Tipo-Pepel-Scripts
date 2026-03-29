# MenuTitle: Copy Metrics Between Masters
# -*- coding: utf-8 -*-
# Description: Copies LSB, RSB, width, and metrics keys from a source master to the current master.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Copy Metrics From Master

import GlyphsApp
from vanilla import FloatingWindow, PopUpButton, TextBox, Button

font = Glyphs.font


class CopyMetricsTool(object):

    def __init__(self):

        self.w = FloatingWindow((360, 140),
                                "Copy Metrics From Master")

        self.masterNames = [m.name for m in font.masters]

        self.w.text = TextBox((15, 15, -15, 20),
                              "Select source master:")

        self.w.popup = PopUpButton((15, 40, -15, 25),
                                   self.masterNames)

        self.w.copyButton = Button((15, 75, -15, 30),
                                   "Copy Metrics to Current Master",
                                   callback=self.copyMetrics)

        self.w.open()
        self.w.makeKey()

    def copyMetrics(self, sender):

        sourceIndex = self.w.popup.get()
        sourceMaster = font.masters[sourceIndex]
        targetMaster = font.selectedFontMaster

        if sourceMaster.id == targetMaster.id:
            print("Source and target master are the same.")
            return

        print("Copying metrics from:",
              sourceMaster.name,
              "→",
              targetMaster.name)

        font.disableUpdateInterface()

        for g in font.glyphs:

            sourceLayer = g.layers[sourceMaster.id]
            targetLayer = g.layers[targetMaster.id]

            if not sourceLayer or not targetLayer:
                continue

            g.beginUndo()

            # Copy numeric metrics
            targetLayer.LSB = sourceLayer.LSB
            targetLayer.RSB = sourceLayer.RSB
            targetLayer.width = sourceLayer.width

            # Copy metric keys
            targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
            targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
            targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey

            g.endUndo()

        font.enableUpdateInterface()

        print("Done.")


CopyMetricsTool()