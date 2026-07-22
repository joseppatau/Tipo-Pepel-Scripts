# MenuTitle: Adjust Metrics by Kerning Group (Pro Final)
# -*- coding: utf-8 -*-
# Description: Adjusts LSB and RSB values for glyphs based on kerning group membership across selected masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
import GlyphsApp
from vanilla import *
from AppKit import NSAlert, NSAlertStyleInformational


class AdjustMetricsByGroup(object):

    def __init__(self):

        font = Glyphs.font
        if not font:
            return

        self.w = FloatingWindow(
            (520, 460),
            "Adjust Metrics by Kerning Group"
        )

        # Group name
        self.w.groupLabel = TextBox((15, 20, 150, 20), "Kerning group name:")
        self.w.groupName = EditText((170, 18, 220, 24), "")

        # LSB
        self.w.lsbLabel = TextBox((15, 60, 100, 20), "LSB:")
        self.w.lsbValue = EditText((110, 58, 80, 24), "10")
        self.w.lsbMode = PopUpButton(
            (200, 58, 150, 24),
            ["Increase", "Decrease", "Exact value"]
        )

        # RSB
        self.w.rsbLabel = TextBox((15, 95, 100, 20), "RSB:")
        self.w.rsbValue = EditText((110, 93, 80, 24), "10")
        self.w.rsbMode = PopUpButton(
            (200, 93, 150, 24),
            ["Increase", "Decrease", "Exact value"]
        )

        # Masters label
        self.w.masterLabel = TextBox(
            (15, 135, -15, 20),
            "Apply to masters:"
        )

        # Prepare master data
        self.masterData = []
        for master in font.masters:
            self.masterData.append({
                "apply": True,
                "name": master.name,
                "id": master.id
            })

        # Scrollable List
        self.w.masterList = List(
            (15, 160, -15, 220),
            self.masterData,
            columnDescriptions=[
                {"title": "Apply", "key": "apply", "width": 60, "cell": CheckBoxListCell()},
                {"title": "Master", "key": "name"}
            ],
            showColumnTitles=True,
            allowsMultipleSelection=False
        )

        # Run button
        self.w.runButton = Button(
            (-120, -40, -15, -15),
            "Run",
            callback=self.run
        )

        self.w.open()


    def applyValue(self, currentValue, amount, mode):
        if mode == 0:      # Increase
            return currentValue + amount
        elif mode == 1:    # Decrease
            return currentValue - amount
        elif mode == 2:    # Exact value
            return amount


    def run(self, sender):

        font = Glyphs.font
        if not font:
            return

        groupName = self.w.groupName.get().strip()
        if not groupName:
            return

        try:
            lsbValue = float(self.w.lsbValue.get())
        except:
            lsbValue = 0

        try:
            rsbValue = float(self.w.rsbValue.get())
        except:
            rsbValue = 0

        lsbMode = self.w.lsbMode.get()
        rsbMode = self.w.rsbMode.get()

        selectedMasterIDs = [
            item["id"]
            for item in self.w.masterList.get()
            if item["apply"]
        ]

        if not selectedMasterIDs:
            return

        affectedGlyphs = 0
        totalLayersChanged = 0

        font.disableUpdateInterface()

        for glyph in font.glyphs:

            affectsLeftSide = glyph.leftKerningGroup == groupName
            affectsRightSide = glyph.rightKerningGroup == groupName

            if not affectsLeftSide and not affectsRightSide:
                continue

            glyph.beginUndo()

            affectedGlyphs += 1

            for masterID in selectedMasterIDs:

                layer = glyph.layers[masterID]
                if not layer:
                    continue

                # LSB
                if affectsLeftSide:
                    layer.LSB = self.applyValue(layer.LSB, lsbValue, lsbMode)

                # RSB
                if affectsRightSide:
                    layer.RSB = self.applyValue(layer.RSB, rsbValue, rsbMode)

                totalLayersChanged += 1

            glyph.endUndo()

        font.enableUpdateInterface()

        alert = NSAlert.alloc().init()
        alert.setMessageText_("Metrics adjustment completed")
        alert.setInformativeText_(
            f"Group: {groupName}\n"
            f"{affectedGlyphs} glyphs affected\n"
            f"{totalLayersChanged} layers modified.\n\n"
            f"Undo available with ⌘Z"
        )
        alert.setAlertStyle_(NSAlertStyleInformational)
        alert.runModal()


AdjustMetricsByGroup()