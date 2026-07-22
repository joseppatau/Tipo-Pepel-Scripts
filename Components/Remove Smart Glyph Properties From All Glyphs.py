# MenuTitle: Remove Smart Glyph Properties From All Glyphs
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs

font = Glyphs.font
if not font:
    raise Exception("No hi ha cap font oberta.")

Glyphs.clearLog()
print("Eliminant smart properties de tots els glifs...\n")

totalGlyphs = 0
changedGlyphs = 0

for glyph in font.glyphs:
    totalGlyphs += 1
    
    try:
        props = glyph.partsSettings()
    except Exception:
        props = None

    if props and len(props):
        try:
            glyph.setPartsSettings_([])
            changedGlyphs += 1
            print("✓ %s: smart properties eliminades" % glyph.name)
        except Exception as e:
            print("✗ %s: no s'han pogut eliminar (%s)" % (glyph.name, e))

print("\nFet. %d glifs processats, %d glifs modificats." % (totalGlyphs, changedGlyphs))