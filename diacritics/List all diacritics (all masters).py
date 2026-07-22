# MenuTitle:List all diacritics (all masters)
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import Glyphs

DIACRITICS = [
    "dieresiscomb","dotaccentcomb","gravecomb","acutecomb",
    "hungarumlautcomb","circumflexcomb","caroncomb","brevecomb",
    "ringcomb","tildecomb","macroncomb","dblgravecomb",
    "commaturnedabovecomb","dotbelowcomb","commaaccentcomb",
    "cedillacomb","ogonekcomb","slashlongcomb",
    "dblgravecomb.case","dieresiscomb.case","dotaccentcomb.case",
    "gravecomb.case","acutecomb.case","hungarumlautcomb.case",
    "circumflexcomb.case","caroncomb.case","brevecomb.case",
    "ringcomb.case","tildecomb.case","macroncomb.case",
    "commaaccentcomb.case","strokeshortcomb.case",
    "slashshortcomb.case","slashlongcomb.case",
    "invertedbrevecomb","invertedbrevecomb.case"
]

SPACE = "/space"

class TurboTool(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((360, 110), "Diacritics TURBO")
        self.w.runButton = vanilla.Button((15, 40, -15, 30), "Run", callback=self.run)
        self.w.open()

    # -------------------------

    def isLower(self, name):
        return "." not in name and name.islower()

    def isSmallCap(self, glyph):
        p = glyph.productionName or glyph.name
        return ".sc" in p

    # -------------------------

    def run(self, sender):

        font = Glyphs.font
        if not font:
            return

        # ⚡ precompute: glyph → components per master
        for master in font.masters:

            layers = {g.name: g.layers[master.id] for g in font.glyphs}

            lines = []

            # -------- LOWERCASE --------
            lines.append("@LOWERCASE")

            for d in DIACRITICS:
                if ".case" in d:
                    continue

                used = []

                for g in font.glyphs:
                    if not self.isLower(g.name):
                        continue

                    for c in layers[g.name].components:
                        if c.componentName == d:
                            used.append(g.name)
                            break

                used = sorted(set(used))
                parts = [f"/{d}"] + [f"/{u}" for u in used]
                lines.append(SPACE.join(parts))

            # -------- SMALL CAPS --------
            lines.append("")
            lines.append("@SMALL CAPS")

            for d in DIACRITICS:
                if ".case" in d:
                    continue

                used = []

                for g in font.glyphs:
                    if not self.isSmallCap(g):
                        continue

                    for c in layers[g.name].components:
                        if c.componentName == d:
                            used.append(g.name)
                            break

                used = sorted(set(used))
                parts = [f"/{d}"] + [f"/{u}" for u in used]
                lines.append(SPACE.join(parts))

            # -------- CASE --------
            lines.append("")
            lines.append("@CASE")

            for d in DIACRITICS:
                if ".case" not in d:
                    continue

                used = []

                for g in font.glyphs:
                    for c in layers[g.name].components:
                        if c.componentName == d:
                            used.append(g.name)
                            break

                used = sorted(set(used))
                parts = [f"/{d}"] + [f"/{u}" for u in used]
                lines.append(SPACE.join(parts))

            font.newTab("\n".join(lines))

# RUN
TurboTool()