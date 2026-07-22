# MenuTitle: Find diacritics with disabled auto alignment (fixed)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs

DIACRITICS = [
    "dieresiscomb", "dotaccentcomb", "gravecomb", "acutecomb",
    "hungarumlautcomb", "caroncomb.alt", "circumflexcomb",
    "caroncomb", "brevecomb", "ringcomb", "tildecomb",
    "macroncomb", "commaturnedabovecomb", "commaaccentcomb",
    "cedillacomb", "ogonekcomb", "slashlongcomb",
    "dieresiscomb.case", "gravecomb.case", "acutecomb.case",
    "hungarumlautcomb.case", "circumflexcomb.case",
    "caroncomb.case", "brevecomb.case", "tildecomb.case",
    "macroncomb.case",
    "dieresis", "dotaccent", "grave", "acute",
    "hungarumlaut", "circumflex", "caron", "breve",
    "ring", "tilde", "macron", "cedilla", "ogonek",
    "dotaccent.case"
]

class FindDiacritics(object):
    def __init__(self):
        self.w = vanilla.FloatingWindow((360, 120), "Find Diacritics (Fixed)")
        self.w.text = vanilla.TextBox((15, 15, -15, 20),
                                     "Find diacritics used without Automatic Alignment")
        self.w.runButton = vanilla.Button((15, 50, -15, 30),
                                          "Run", callback=self.run)
        self.w.open()

    def run(self, sender):
        font = Glyphs.font
        if not font:
            print("No font open")
            return

        affectedGlyphs = []

        for glyph in font.glyphs:
            for layer in glyph.layers:
                for component in layer.components:
                    compName = component.componentName

                    if compName in DIACRITICS:
                        if not component.automaticAlignment:
                            affectedGlyphs.append(glyph.name)
                            break
                else:
                    continue
                break

        affectedGlyphs = sorted(list(set(affectedGlyphs)))

        if affectedGlyphs:
            tabString = "/" + "/".join(affectedGlyphs)
            font.newTab(tabString)
            print(f"Found {len(affectedGlyphs)} glyphs with issues.")
        else:
            print("All diacritics are correctly aligned.")

FindDiacritics()