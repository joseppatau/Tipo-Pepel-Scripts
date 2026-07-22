# MenuTitle: PRO – Find & Fix Diacritics Alignment
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

class DiacriticsProTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((420, 220), "Diacritics PRO Tool")

        self.w.text = vanilla.TextBox(
            (15, 15, -15, 20),
            "Find & Fix diacritics with Automatic Alignment OFF"
        )

        self.w.onlyCurrentMaster = vanilla.CheckBox(
            (15, 45, -15, 20),
            "Only current master",
            value=True
        )

        self.w.onlyMarks = vanilla.CheckBox(
            (15, 70, -15, 20),
            "Only mark components (anchors-based)",
            value=False
        )

        self.w.scanButton = vanilla.Button(
            (15, 110, -15, 30),
            "Scan",
            callback=self.scan
        )

        self.w.fixButton = vanilla.Button(
            (15, 150, -15, 30),
            "Fix All",
            callback=self.fix
        )

        self.w.status = vanilla.TextBox(
            (15, 185, -15, 20),
            ""
        )

        self.w.open()

    # -------------------------
    # CORE LOGIC
    # -------------------------

    def getLayers(self, glyph, font):
        if self.w.onlyCurrentMaster.get():
            return [glyph.layers[font.selectedFontMaster.id]]
        return glyph.layers

    def isMarkComponent(self, component, font):
        baseGlyph = font.glyphs[component.componentName]
        if not baseGlyph:
            return False

        # mira si té anchors típics de marks
        for layer in baseGlyph.layers:
            for anchor in layer.anchors:
                if anchor.name.startswith("_"):
                    return True
        return False

    def findIssues(self, font):
        issues = []
        affectedGlyphs = []

        for glyph in font.glyphs:
            for layer in self.getLayers(glyph, font):

                for component in layer.components:
                    compName = component.componentName

                    if compName not in DIACRITICS:
                        continue

                    if self.w.onlyMarks.get():
                        if not self.isMarkComponent(component, font):
                            continue

                    if not component.automaticAlignment:
                        issues.append((glyph.name, compName))
                        affectedGlyphs.append(glyph.name)
                        break

        return issues, sorted(list(set(affectedGlyphs)))

    # -------------------------
    # ACTIONS
    # -------------------------

    def scan(self, sender):
        font = Glyphs.font
        if not font:
            return

        issues, glyphs = self.findIssues(font)

        print("\n--- DIACRITICS REPORT ---")
        for g, c in issues:
            print(f"{g} → {c}")

        if glyphs:
            tabString = "/" + "/".join(glyphs)
            font.newTab(tabString)

        self.w.status.set(f"Found {len(issues)} issues in {len(glyphs)} glyphs")

    def fix(self, sender):
        font = Glyphs.font
        if not font:
            return

        issues, glyphs = self.findIssues(font)
        fixed = 0

        for glyph in font.glyphs:
            for layer in self.getLayers(glyph, font):

                for component in layer.components:
                    compName = component.componentName

                    if compName not in DIACRITICS:
                        continue

                    if self.w.onlyMarks.get():
                        if not self.isMarkComponent(component, font):
                            continue

                    if not component.automaticAlignment:
                        component.automaticAlignment = True
                        fixed += 1

        Glyphs.showNotification(
            "Diacritics Fixed",
            f"{fixed} components updated"
        )

        self.w.status.set(f"Fixed {fixed} components")

# RUN
DiacriticsProTool()