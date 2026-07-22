# MenuTitle: Selected Glyphs to components with extension
# -*- coding: utf-8 -*-

from vanilla import *
from GlyphsApp import *
from AppKit import NSAlert, NSAlertFirstButtonReturn


class CreateComponentAlternates(object):

    def __init__(self):

        self.w = FloatingWindow(
            (260, 90),
            "Create Component Alternates"
        )

        self.w.label = TextBox(
            (10, 12, 70, 20),
            "Extension"
        )

        self.w.extension = EditText(
            (80, 10, 80, 22),
            ".ss02"
        )

        self.w.runButton = Button(
            (10, 50, -10, 22),
            "CREATE",
            callback=self.createGlyphs
        )

        self.w.open()
        self.w.makeKey()

    def askOverwrite(self, glyphNames):

        alert = NSAlert.alloc().init()
        alert.setMessageText_("Some glyphs already exist")
        alert.setInformativeText_(
            "Overwrite existing glyphs?\n\n%s" % ", ".join(glyphNames[:20])
        )

        alert.addButtonWithTitle_("Overwrite")
        alert.addButtonWithTitle_("Cancel")

        return alert.runModal() == NSAlertFirstButtonReturn

    def clearMasterLayer(self, layer):

        while len(layer.paths):
            del layer.paths[-1]

        while len(layer.components):
            del layer.components[-1]

        while len(layer.anchors):
            del layer.anchors[-1]

    def createGlyphs(self, sender):

        font = Glyphs.font

        if not font:
            return

        extension = self.w.extension.get().strip()

        if not extension:
            Message("Error", "Please enter an extension.")
            return

        selectedGlyphs = []
        processed = set()

        for layer in font.selectedLayers:
            glyph = layer.parent

            if glyph.name not in processed:
                processed.add(glyph.name)
                selectedGlyphs.append(glyph)

        existingGlyphs = []

        for glyph in selectedGlyphs:

            newName = glyph.name + extension

            if font.glyphs[newName]:
                existingGlyphs.append(newName)

        if existingGlyphs:

            if not self.askOverwrite(existingGlyphs):
                return

        createdCount = 0

        font.disableUpdateInterface()

        try:

            for sourceGlyph in selectedGlyphs:

                newName = sourceGlyph.name + extension

                targetGlyph = font.glyphs[newName]

                if not targetGlyph:

                    targetGlyph = GSGlyph(newName)
                    font.glyphs.append(targetGlyph)

                targetGlyph.export = sourceGlyph.export
                targetGlyph.category = sourceGlyph.category
                targetGlyph.subCategory = sourceGlyph.subCategory

                try:
                    targetGlyph.leftKerningGroup = sourceGlyph.leftKerningGroup
                except:
                    pass

                try:
                    targetGlyph.rightKerningGroup = sourceGlyph.rightKerningGroup
                except:
                    pass

                for master in font.masters:

                    sourceLayer = sourceGlyph.layers[master.id]
                    targetLayer = targetGlyph.layers[master.id]

                    self.clearMasterLayer(targetLayer)

                    targetLayer.width = sourceLayer.width

                    component = GSComponent(sourceGlyph.name)
                    targetLayer.components.append(component)

                    for anchor in sourceLayer.anchors:

                        newAnchor = GSAnchor()
                        newAnchor.name = anchor.name
                        newAnchor.position = anchor.position

                        targetLayer.anchors.append(newAnchor)

                createdCount += 1

        finally:
            font.enableUpdateInterface()

        Glyphs.showNotification(
            "Create Component Alternates",
            "%i glyph(s) created." % createdCount
        )


CreateComponentAlternates()