# MenuTitle: Change Diacritics Components
# -*- coding: utf-8 -*-

from vanilla import *
from GlyphsApp import *
from AppKit import NSAlert

DIACRITIC_NAMES = [
    "acute",
    "acutecomb",
    "grave",
    "gravecomb",
    "circumflex",
    "circumflexcomb",
    "caron",
    "caroncomb",
    "breve",
    "brevecomb",
    "dieresis",
    "dieresiscomb",
    "tilde",
    "tildecomb",
    "macron",
    "macroncomb",
    "ring",
    "ringcomb",
    "hungarumlaut",
    "hungarumlautcomb",
    "cedilla",
    "cedillacomb",
    "ogonek",
    "ogonekcomb",
    "dotaccent",
    "dotaccentcomb",
    "commaaccent",
    "commaaccentcomb",
]


class ChangeDiacritics(object):

    def __init__(self):

        self.w = FloatingWindow(
            (230, 180),
            "Change Diacritics"
        )

        self.w.t1 = TextBox(
            (10, 10, -10, 17),
            "Current selected glyphs"
        )

        self.w.mode = RadioGroup(
            (10, 30, 120, 45),
            ["Regular names", "Extension"],
            isVertical=True,
            callback=self.updateUI
        )
        self.w.mode.set(0)

        self.w.currentExt = EditText(
            (120, 52, 80, 20),
            ".case"
        )

        self.w.t2 = TextBox(
            (10, 90, -10, 17),
            "Change/prepend"
        )

        self.w.t3 = TextBox(
            (10, 115, 60, 17),
            "Extension"
        )

        self.w.newExt = EditText(
            (80, 112, 80, 20),
            ".orn"
        )

        self.w.runButton = Button(
            (10, 145, -10, 22),
            "APPLY",
            callback=self.apply
        )

        self.updateUI(None)

        self.w.open()
        self.w.makeKey()

    def updateUI(self, sender):
        self.w.currentExt.enable(self.w.mode.get() == 1)

    def isDiacritic(self, componentName):

        for item in DIACRITIC_NAMES:
            if (
                componentName == item
                or componentName.startswith(item + ".")
            ):
                return True

        return False

    def apply(self, sender):

        font = Glyphs.font

        if not font:
            return

        mode = self.w.mode.get()
        currentExt = self.w.currentExt.get().strip()
        newExt = self.w.newExt.get().strip()

        changedCount = 0
        missingGlyphs = set()

        processedGlyphs = set()

        font.disableUpdateInterface()

        try:

            for selectedLayer in font.selectedLayers:

                glyph = selectedLayer.parent

                if glyph.name in processedGlyphs:
                    continue

                processedGlyphs.add(glyph.name)

                for master in font.masters:

                    layer = glyph.layers[master.id]

                    for component in layer.components:

                        oldName = component.componentName
                        newName = None

                        if mode == 0:

                            if oldName in DIACRITIC_NAMES:
                                newName = oldName + newExt

                        else:

                            if oldName.endswith(currentExt):

                                baseName = oldName[:-len(currentExt)]

                                if self.isDiacritic(baseName):
                                    newName = baseName + newExt

                        if not newName:
                            continue

                        if font.glyphs[newName]:

                            try:
                                component.componentName = newName

                                if component.componentName != newName:
                                    try:
                                        component.setComponentName_(newName)
                                    except:
                                        pass

                                changedCount += 1

                            except:
                                pass

                        else:
                            missingGlyphs.add(newName)

        finally:
            font.enableUpdateInterface()

        message = "%d component(s) modified." % changedCount

        if missingGlyphs:
            message += "\n\nMissing glyphs:\n"
            message += "\n".join(sorted(missingGlyphs))

        alert = NSAlert.alloc().init()
        alert.setMessageText_("Change Diacritics")
        alert.setInformativeText_(message)
        alert.runModal()


ChangeDiacritics()