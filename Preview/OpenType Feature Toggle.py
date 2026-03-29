# MenuTitle: OpenType Feature Toggle
# -*- coding: utf-8 -*-
# Description: Enables toggling OpenType features in the current tab for real-time testing.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
from GlyphsApp import Glyphs
from AppKit import NSView

class OTFeatureToggler(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            print("No font open.")
            return

        self.featureNames = [f.name for f in self.font.features]

        self.w = vanilla.Window((125, 500), "OT Features")

        contentHeight = len(self.featureNames) * 24 + 20
        self.documentView = NSView.alloc().initWithFrame_(((0, 0), (320, contentHeight)))

        self.checkboxes = {}
        y = 10

        for name in self.featureNames:
            cb = vanilla.CheckBox(
                (10, y, 300, 20),
                name,
                value=False
            )
            self.documentView.addSubview_(cb._nsObject)
            self.checkboxes[name] = cb
            y += 24

        self.w.scroll = vanilla.ScrollView(
            (10, 10, -10, -50),
            self.documentView,
            hasHorizontalScroller=False
        )

        self.w.applyButton = vanilla.Button(
            (10, -35, -10, 25),
            "Apply to Tab",
            callback=self.applyToTab
        )

        self.w.open()

    def applyToTab(self, sender):
        tab = Glyphs.font.currentTab
        if not tab:
            print("No active tab.")
            return

        selected = [
            name for name, cb in self.checkboxes.items()
            if cb.get()
        ]

        print("Applying features:", selected)

        # 🔥 USE LIST (not string)
        tab.features = selected

        print("Tab now has:", tab.features)


OTFeatureToggler()