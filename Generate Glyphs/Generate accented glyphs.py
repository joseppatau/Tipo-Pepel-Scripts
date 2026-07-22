#MenuTitle: Genera accents dels glifs seleccionats (DEBUG)
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, GSGlyph

font = Glyphs.font

REBUILD_EXISTING = False
DEBUG = True

targets = {
	"A": ["Aacute","Abreve","Acircumflex","Adieresis","Agrave","Amacron","Aogonek","Aring","Atilde"],
	"C": ["Cacute","Ccaron","Ccedilla","Cdotaccent"],
	"D": ["Dcaron","Dcroat","Eth"],
	"E": ["Eacute","Ecaron","Ecircumflex","Edieresis","Edotaccent","Egrave","Emacron","Eogonek","Etilde"],
	"G": ["Gbreve","Gcommaaccent","Gdotaccent","Gmacron"],
	"H": ["Hbar"],
	"I": ["Iacute","Icircumflex","Idieresis","Idotaccent","Igrave","Imacron","Iogonek","Itilde"],
	"J": ["Jacute"],
	"K": ["Kcommaaccent"],
	"L": ["Lacute","Lcaron","Lcommaaccent","Lslash"],
	"N": ["Nacute","Ncaron","Ncommaaccent","Ntilde"],
	"O": ["Oacute","Ocircumflex","Odieresis","Ograve","Ohungarumlaut","Omacron","Oslash","Otilde"],
	"R": ["Racute","Rcaron","Rcommaaccent"],
	"S": ["Sacute","Scaron","Scedilla","Scommaaccent"],
	"T": ["Tcaron","Tcedilla","Tcommaaccent"],
	"U": ["Uacute","Ucircumflex","Udieresis","Ugrave","Uhungarumlaut","Umacron","Uogonek","Uring","Utilde"],
	"W": ["Wacute","Wcircumflex","Wdieresis","Wgrave"],
	"Y": ["Yacute","Ycircumflex","Ydieresis","Ygrave","Ytilde"],
	"Z": ["Zacute","Zcaron","Zdotaccent"],

	"a": ["aacute","abreve","acircumflex","adieresis","agrave","amacron","aogonek","aring","atilde"],
	"c": ["cacute","ccaron","ccedilla","cdotaccent"],
	"d": ["dcaron","dcroat","eth"],
	"e": ["eacute","ecaron","ecircumflex","edieresis","edotaccent","egrave","emacron","eogonek","etilde"],
	"g": ["gbreve","gcommaaccent","gdotaccent","gmacron"],
	"h": ["hbar"],
	"i": ["iacute","icircumflex","idieresis","idotaccent","igrave","imacron","iogonek","itilde"],
	"j": ["jacute"],
	"k": ["kcommaaccent"],
	"l": ["lacute","lcaron","lcommaaccent","lslash"],
	"n": ["nacute","ncaron","ncommaaccent","ntilde"],
	"o": ["oacute","ocircumflex","odieresis","ograve","ohungarumlaut","omacron","oslash","otilde"],
	"r": ["racute","rcaron","rcommaaccent"],
	"s": ["sacute","scaron","scedilla","scommaaccent"],
	"t": ["tcaron","tcedilla","tcommaaccent"],
	"u": ["uacute","ucircumflex","udieresis","ugrave","uhungarumlaut","umacron","uogonek","uring","utilde"],
	"w": ["wacute","wcircumflex","wdieresis","wgrave"],
	"y": ["yacute","ycircumflex","ydieresis","ygrave","ytilde"],
	"z": ["zacute","zcaron","zdotaccent"],

	"Lcommaaccent": ["Lcommaaccent.loclMAH"],
	"Ncommaaccent": ["Ncommaaccent.loclMAH"],
	"lcommaaccent": ["lcommaaccent.loclMAH"],
	"ncommaaccent": ["ncommaaccent.loclMAH"],
}

created = []
rebuilt = []
skipped = []
problems = []

selectedGlyphs = set(layer.parent.name for layer in font.selectedLayers)

Glyphs.clearLog()
print("=" * 60)
print("GENERACIÓ DE COMPOSTOS")
print("=" * 60)
print("Seleccionats:", ", ".join(sorted(selectedGlyphs)))

font.disableUpdateInterface()

try:

	for baseName in selectedGlyphs:

		if baseName not in targets:
			if DEBUG:
				print("\n⚠️ No hi ha definicions per:", baseName)
			continue

		for glyphName in targets[baseName]:

			if DEBUG:
				print("\n" + "-" * 50)
				print("Base:", baseName)
				print("Objectiu:", glyphName)

			glyph = font.glyphs[glyphName]

			if glyph:

				if not REBUILD_EXISTING:
					skipped.append(glyphName)

					if DEBUG:
						print("Ja existeix -> saltat")

					continue

				rebuilt.append(glyphName)

				if DEBUG:
					print("Reconstruint glif existent")

			else:
				glyph = GSGlyph(glyphName)
				font.glyphs.append(glyph)
				glyph.updateGlyphInfo()

				created.append(glyphName)

				if DEBUG:
					print("Creat glif nou")

			if glyph.glyphInfo is None:
				msg = "GlyphInfo absent: %s" % glyphName
				problems.append(msg)
				print("⚠️", msg)

			for layer in glyph.layers:

				layer.clear()
				layer.makeComponents()

				componentNames = [c.componentName for c in layer.components]

				if DEBUG:
					print("  Capa:", layer.name)
					print("  Components:", componentNames)
					print("  Shapes:", len(layer.shapes))
					print("  Width:", layer.width)

				if len(componentNames) == 0:
					msg = "%s -> capa '%s' sense components" % (
						glyphName,
						layer.name
					)
					problems.append(msg)

					print("⚠️", msg)

finally:
	font.enableUpdateInterface()

print("\n")
print("=" * 60)
print("RESUM")
print("=" * 60)

print("Creats:", len(created))
print("Reconstruïts:", len(rebuilt))
print("Saltats:", len(skipped))
print("Problemes:", len(problems))

if created:
	print("\nCREATS")
	print(", ".join(created))

if rebuilt:
	print("\nRECONSTRUÏTS")
	print(", ".join(rebuilt))

if problems:
	print("\nPROBLEMES DETECTATS")
	for p in problems:
		print("•", p)

print("\nFi.")