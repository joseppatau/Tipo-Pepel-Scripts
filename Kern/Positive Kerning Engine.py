# MenuTitle: Positive Kerning Engine
# -*- coding: utf-8 -*-
# Description: Detects collisions and applies positive kerning adjustments to maintain minimum spacing between glyph pairs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import math
import re
import json
import time
from GlyphsApp import *
from vanilla import *
from AppKit import *
from AppKit import NSAlert, NSAlertStyleInformational, NSAlertFirstButtonReturn
from AppKit import NSAlert, NSInformationalAlertStyle
from GlyphsApp import Glyphs


# ===================================================
# CONTEXT NORMALIZATION (GLOBAL, OBLIGATORI)
# ===================================================

# ===================================================
# KERN PAIR FORMATTERS (GLOBALS, OBLIGATORIS)
# ===================================================

def normalize_context(context):
	if context is None:
		return ""
	if isinstance(context, list):
		return "/" + "/".join(context)
	if isinstance(context, str):
		return context.strip()
	return ""


def format_kern_pair_core(prefix, left, right, suffix):
	"""
	FORMAT ÚNIC PER A COLUMNES
	ASCII PUR, AMPLADA ESTABLE
	"""
	prefix = normalize_context(prefix)
	suffix = normalize_context(suffix)
	return f"{prefix}/{left}/{right}{suffix}"


def format_kern_pair_block(prefix, left, right, suffix, pad=5):
	"""
	Formatter amb espais inicials.
	NO usar dins layout en columnes.
	"""
	core = format_kern_pair_core(prefix, left, right, suffix)

	if not isinstance(pad, int):
		print("⚠️ pad incorrect:", repr(pad))
		pad = 5

	return (" " * pad) + core



def format_context(context_str, glyph_name):
	"""
	Rep NOMÉS STRING (ja normalitzat).
	Retorna /x/y
	"""
	context_str = normalize_context(context_str)

	if not context_str:
		if '.sc' in glyph_name.lower():
			return "/h.sc/h.sc"
		elif glyph_name and glyph_name[0].islower():
			return "/h/h"
		else:
			return "/H/H"

	if context_str.startswith("/") and context_str.count("/") >= 2:
		return context_str

	if len(context_str) >= 2:
		return f"/{context_str[0]}/{context_str[1]}"

	return f"/{context_str[0]}/{context_str[0]}"


def format_kern_pair_block(prefix, left, right, suffix, pad=5):
	"""
	ÚNICA funció autoritzada a afegir espais.
	"""
	prefix = normalize_context(prefix)
	suffix = normalize_context(suffix)

	if not isinstance(pad, int):
		print("⚠️ pad incorrect:", repr(pad))
		pad = 5

	spaces = " " * pad
	return f"{spaces}{prefix}/{left}/{right}{suffix}"


# ===== helpers de geometria =====

def distance(p1, p2):
	return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def minDistanceBetweenSegments(a1, a2, b1, b2):
	def clamp(x, a, b):
		return max(a, min(b, x))

	A = (a1.x, a1.y); B = (a2.x, a2.y)
	C = (b1.x, b1.y); D = (b2.x, b2.y)

	def closestPoint(P, Q, R):
		vx, vy = Q[0]-P[0], Q[1]-P[1]
		denom = vx*vx + vy*vy
		if denom == 0:
			return P
		t = ((R[0]-P[0])*vx + (R[1]-P[1])*vy) / denom
		t = clamp(t, 0, 1)
		return (P[0] + t*vx, P[1] + t*vy)

	dmin = float("inf")
	for p in (A, B):
		q = closestPoint(C, D, p)
		dmin = min(dmin, distance(p, q))
	for p in (C, D):
		q = closestPoint(A, B, p)
		dmin = min(dmin, distance(p, q))

	return dmin

def getSegments(layer):
	segs = []
	for p in layer.paths:
		nodes = p.nodes
		if not nodes:
			continue
		count = len(nodes)
		for i in range(count):
			n1 = nodes[i]
			if p.closed:
				n2 = nodes[(i+1) % count]
			elif i+1 < count:
				n2 = nodes[i+1]
			else:
				continue
			segs.append((n1, n2))
	return segs

def minDistanceBetweenLayers(layer1, layer2, dx, liApache2=10000):
	segs1 = getSegments(layer1)
	segs2 = getSegments(layer2)
	if not segs1 or not segs2:
		return liApache2

	shifted = []
	for n1, n2 in segs2:
		shifted.append((
			type("P", (), {"x": n1.x + dx, "y": n1.y}),
			type("P", (), {"x": n2.x + dx, "y": n2.y})
		))

	dmin = liApache2
	for s1 in segs1:
		for s2 in shifted:
			d = minDistanceBetweenSegments(s1[0], s1[1], s2[0], s2[1])
			if d < dmin:
				dmin = d
			if dmin <= 0:
				return 0.0
	return dmin

# ===== CONSTANTS DE VISUALITZACIÓ DETECTOR DE COL·LISIONS =====
ZOOM_LEVEL = 15.0  # Escala al 15%
BASELINE_OFFSET = -30  # Baixar línia base
GLYPH_COLOR = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.2, 0.2, 1.0)	# Gris fosc
BACKGROUND_COLOR = NSColor.whiteColor()

# ===== LLISTES DE GLIFS (DEL SCRIPT FUNCIONAL) =====

# Llistes bàsiques
LATIN_LOWERCASE = [
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

LATIN_UPPERCASE = [
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
	'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

CYRILLIC_UPPERCASE = [
	'Acy', 'Becy', 'Vecy', 'Gecy', 'Gjecy', 'Djecy', 'Decy', 'Iecy', 
	'Iocy', 'Zhecy', 'Zecy', 'Iicy', 'Iishortcy', 'Kacy', 'Elcy', 
	'Emcy', 'Ency', 'Ocy', 'Pecy', 'Ercy', 'Escy', 'Tecy', 'Ucy', 
	'Efcy', 'Khacy', 'Tsecy', 'Checy', 'Shacy', 'Shchacy', 'Hardsigncy',
	'Yericy', 'Softsigncy', 'Ereversedcy', 'IUcy', 'IAcy', 'Yatcy',
	'uni0410', 'uni0411', 'uni0412', 'uni0413', 'uni0403', 'uni0490', 'uni0414', 
	'uni0415', 'uni0400', 'uni0401', 'uni0416', 'uni0417', 'uni0418', 'uni0419', 
	'uni040D', 'uni041K', 'uni040C', 'uni041B', 'uni041C', 'uni041D', 'uni041E', 
	'uni041F', 'uni0420', 'uni0421', 'uni0422', 'uni0423', 'uni0424', 'uni0425', 
	'uni0426', 'uni0427', 'uni0428', 'uni0429', 'uni040F', 'uni042C', 'uni042B', 
	'uni042A', 'uni0409', 'uni040A', 'uni0405', 'uni0404', 'uni042D', 'uni0406', 
	'uni0407', 'uni0408', 'uni040B', 'uni042E', 'uni042F', 'uni0402'
]

CYRILLIC_LOWERCASE = [
	'acy', 'becy', 'vecy', 'gecy', 'gjecy', 'djecy', 'decy', 'iecy', 
	'iocy', 'zhecy', 'zecy', 'iicy', 'iishortcy', 'kacy', 'elcy', 
	'emcy', 'ency', 'ocy', 'pecy', 'ercy', 'escy', 'tecy', 'ucy', 
	'efcy', 'khacy', 'tsecy', 'checy', 'shacy', 'shchacy', 'hardsigncy',
	'yericy', 'softsigncy', 'ereversedcy', 'iucy', 'iacy', 'yatcy',
	'uni0430', 'uni0431', 'uni0432', 'uni0433', 'uni0453', 'uni0491', 'uni0434', 
	'uni0435', 'uni0450', 'uni0451', 'uni0436', 'uni0437', 'uni0438', 'uni0439', 
	'uni043A', 'uni045C', 'uni043B', 'uni043C', 'uni043D', 'uni043E', 'uni043F', 
	'uni0440', 'uni0441', 'uni0442', 'uni0443', 'uni0444', 'uni0445', 'uni0446', 
	'uni0447', 'uni0448', 'uni0449', 'uni045F', 'uni044C', 'uni044B', 'uni044A', 
	'uni0459', 'uni045A', 'uni0455', 'uni0454', 'uni044D', 'uni0456', 'uni0457', 
	'uni0458', 'uni045B', 'uni044E', 'uni044F', 'uni0452',
	'iishort-cy.loclBGR', 'iigrave-cy.loclBGR', 'be-cy.loclSRB'
]

BASIC_NUMBERS = [
	'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

PUNCTUATION_GLYPHS = [
	'period', 'comma', 'colon', 'semicolon', 'ellipsis', 'exclam', 'exclamdown', 
	'question', 'questiondown', 'periodcentered', 'bullet', 'asterisk', 'numbersign', 
	'slash', 'backslash', 'hyphen', 'endash', 'emdash', 'underscore', 'parenleft', 
	'parenright', 'braceleft', 'braceright', 'bracketleft', 'bracketright', 
	'quotesinglbase', 'quotedblbase', 'quotedblleft', 'quotedblright', 'quoteleft', 
	'quoteright', 'guillemetleft', 'guillemetright', 'guilsinglleft', 'guilsinglright', 
	'quotedbl', 'quotesingle'
]

SYMBOLS_GLYPHS = [
	'baht', 'at', 'ampersand', 'paragraph', 'section', 'copyright', 'registered', 
	'trademark', 'degree', 'bar', 'brokenbar', 'dagger', 'daggerdbl', 'cent', 
	'currency', 'dollar', 'euro', 'sterling', 'yen', 'plus', 'minus', 'multiply', 
	'divide', 'equal', 'notequal', 'greater', 'less', 'greaterequal', 'lessequal', 
	'plusminus', 'logicalnot', 'asciicircum', 'partialdiff', 'percent', 'perthousand', 
	'upArrow', 'northEastArrow', 'rightArrow', 'southEastArrow', 'downArrow', 
	'southWestArrow', 'leftArrow', 'northWestArrow', 'leftRightArrow', 'upDownArrow', 
	'lozenge'
]

# ===== FUNCIONS AUXILIARS DEL SCRIPT FUNCIONAL =====






def glyph_to_char_or_name(glyph):
	"""Converteix glif a caràcter o nom per a visualització"""
	if not glyph: return ""
	if glyph.unicode:
		try: 
			char = chr(int(glyph.unicode, 16))
			if ord(char) < 32 or char.isspace():
				return f"/{glyph.name}"
			return char
		except: 
			return f"/{glyph.name}"
	return f"/{glyph.name}"

	
def filter_unique_by_groups(font, glyph_names, position="both"):
	"""Filtra glifs duplicats per grups de kerning"""
	seen_groups = set()
	result = []
	
	for name in glyph_names:
		if name not in font.glyphs:
			continue
			
		g = font.glyphs[name]
	
		if position == "left":
			group_to_check = g.rightKerningGroup
			if not group_to_check:
				group_to_check = f"NO_RIGHT_GROUP_{name}"
		elif position == "right":
			group_to_check = g.leftKerningGroup
			if not group_to_check:
				group_to_check = f"NO_LEFT_GROUP_{name}"
		else:
			left_group = g.leftKerningGroup or f"NO_LEFT_GROUP_{name}"
			right_group = g.rightKerningGroup or f"NO_RIGHT_GROUP_{name}"
			group_to_check = f"{left_group}|{right_group}"
	
		if group_to_check in seen_groups:
			continue
		
		seen_groups.add(group_to_check)
		result.append(name)
	
	return result

	
def format_kern_pair_block(prefix, left, right, suffix, pad=5):
	prefix = normalize_context(prefix)
	suffix = normalize_context(suffix)

	if not isinstance(pad, int):
		print("⚠️ pad incorrect:", repr(pad))
		pad = 5

	spaces = " " * pad
	return f"{spaces}{prefix}/{left}/{right}{suffix}"


	
	
	
	
# ===== CLASS PRINCIPAL ====
class KernMarginSlider(object):


			# ... código existente ...
	


	# ===================================================
	# MÉTODOS TURBO PARA EL LISTADOR DE PARES (INTEGRADO)
	# ===================================================

	def resolveKeyTurbo(self, key):
		"""TURBO: Fast key resolution with caching"""
		font = Glyphs.font
		if not font:
			return str(key)

		if not isinstance(key, str):
			return str(key)

		# TURBO: Cache for frequently resolved keys
		if key in self._keyCacheTurbo:
			return self._keyCacheTurbo[key]

		result = key
	
		# TURBO: Fast pattern matching
		if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
			result = key.split("_", 2)[-1]
		elif key.startswith("@") and "_" not in key:
			result = key[1:]
		elif len(key) == 36 and key.count("-") == 4:  # UUID
			g = font.glyphForId_(key)
			if g:
				result = g.name

		# TURBO: Cache result
		self._keyCacheTurbo[key] = result
	
		return result

	def charToProductionNameTurbo(self, char_or_name):
		"""TURBO: Fast character to production name conversion"""
		font = Glyphs.font
		if not font:
			return char_or_name
		
		# TURBO: Cache for production names
		if char_or_name in self._productionCacheTurbo:
			return self._productionCacheTurbo[char_or_name]
		
		result = char_or_name
	
		# TURBO: Quick font glyph check
		if char_or_name in font.glyphs:
			result = char_or_name
		else:
			# TURBO: Fast unicode lookup
			for glyph in font.glyphs:
				if glyph.unicode:
					try:
						if chr(int(glyph.unicode, 16)) == char_or_name:
							result = glyph.name
							break
					except:
						continue
		
			# TURBO: Common character mapping
			char_map = {
				'7': 'seven', '@': 'at', '&': 'ampersand', '#': 'numbersign',
				'$': 'dollar', '%': 'percent', '*': 'asterisk', '+': 'plus',
				'-': 'hyphen', '=': 'equal', '<': 'less', '>': 'greater',
				'?': 'question', '!': 'exclam', '"': 'quotedbl', "'": 'quotesingle',
				'(': 'parenleft', ')': 'parenright', '[': 'bracketleft',
				']': 'bracketright', '{': 'braceleft', '}': 'braceright',
				'/': 'slash', '\\': 'backslash', '|': 'bar', ':': 'colon',
				';': 'semicolon', ',': 'comma', '.': 'period'
			}
			result = char_map.get(char_or_name, result)

		# TURBO: Cache result
		self._productionCacheTurbo[char_or_name] = result
	
		return result

	def nameToGraphicalRepresentationTurbo(self, name):
		"""TURBO: Convert production name to graphical character for display"""
		font = Glyphs.font
		if not font:
			return name
		
		# TURBO: Cache for graphical representations
		if name in self._graphicalCacheTurbo:
			return self._graphicalCacheTurbo[name]
		
		result = name
	
		# TURBO: Check if it's a production name that should be shown as character
		production_to_char = {
			'seven': '7', 'at': '@', 'ampersand': '&', 'numbersign': '#',
			'dollar': '$', 'percent': '%', 'asterisk': '*', 'plus': '+',
			'hyphen': '-', 'equal': '=', 'less': '<', 'greater': '>',
			'question': '?', 'exclam': '!', 'quotedbl': '"', 'quotesingle': "'",
			'parenleft': '(', 'parenright': ')', 'bracketleft': '[',
			'bracketright': ']', 'braceleft': '{', 'braceright': '}',
			'slash': '/', 'backslash': '\\', 'bar': '|', 'colon': ':',
			'semicolon': ';', 'comma': ',', 'period': '.'
		}
	
		# TURBO: Convert production name to character if possible
		if name in production_to_char:
			result = production_to_char[name]
		else:
			# TURBO: Try to get unicode character for other glyphs
			if name in font.glyphs:
				g = font.glyphs[name]
				if g.unicode:
					try:
						result = chr(int(g.unicode, 16))
					except:
						pass

		# TURBO: Cache result
		self._graphicalCacheTurbo[name] = result
	
		return result

	def scriptOrderTurbo(self, ch):
		"""TURBO: Fast script-based ordering"""
		if not ch:
			return (9, ch)
	
		try:
			cp = ord(ch[0])
		except:
			return (9, ch)

		# TURBO: Quick unicode range checks
		if 0x0041 <= cp <= 0x024F: return (0, ch)  # Latin
		if 0x0370 <= cp <= 0x03FF: return (1, ch)  # Greek	
		if 0x0400 <= cp <= 0x052F: return (2, ch)  # Cyrillic
		return (3, ch)	# Other

	def contextualDisplayTurbo(self, L, R, val):
		"""Compact display: H◂B◂î◂H 1064 - mapeo dinámico completo"""
		if isinstance(L, str): L = L.strip()
		if isinstance(R, str): R = R.strip()
	
		Lprod = self.charToProductionNameTurbo(L)
		Rprod = self.charToProductionNameTurbo(R)
	
		# Mapeo dinámico COMPLETO para cualquier glyph name
		def glyph_to_compact(name):
			if not name:
				return "?"
			name = str(name).strip()
		
			# Si tiene unicode, usar carácter unicode
			try:
				g = Glyphs.font.glyphs[name]
				if g.unicode:
					return chr(int(g.unicode, 16))
			except:
				pass
		
			# Fallback: primera letra(s) + diacrítico detectado
			base = name[0].upper()
			if any(x in name.lower() for x in ['grave', 'acute', 'circ', 'caron', 'breve', 'tilde', 'dier']):
				if 'grave' in name.lower(): return chr(0x00EC)	# ì
				if 'circ' in name.lower(): return chr(0x00EE)	# î
				if 'dier' in name.lower(): return chr(0x00EF)	# ï
				if 'caron' in name.lower(): return chr(0x01D1)	# í (háček)
				if 'breve' in name.lower(): return chr(0x012D)	# ĩ
				if 'tilde' in name.lower(): return chr(0x0129)	# ĩ
			elif len(name) > 1:
				return name[:2].capitalize()
			return base
	
		Lshort = glyph_to_compact(Lprod)
		Rshort = glyph_to_compact(Rprod)
	
		result = f"H◂{Lshort}◂{Rshort}◂H {val}"
		print(f"🧪 DEBUG: '{result}'")
		return result


	def refreshPairsList(self, sender=None):
		"""TURBO: High-performance list refresh - SHOWS GRAPHICAL REPRESENTATION"""
		font = Glyphs.font
		if not font:
			return
		
		tab = self.w.tabs[1]
		mid = font.selectedFontMaster.id
	
		# TURBO: Cache kerning data
		if mid in self._kerningCacheTurbo:
			kerning = self._kerningCacheTurbo[mid]
		else:
			kerning = font.kerning.get(mid, {})
			self._kerningCacheTurbo[mid] = kerning

		rows = []
		seen = set()

		# TURBO: Optimized kerning processing
		for LK, rightDict in kerning.items():
			for RK, val in rightDict.items():
				try:
					val_int = int(val)
				except (TypeError, ValueError):
					continue

				# TURBO: Fast key resolution
				L0 = self.resolveKeyTurbo(LK)
				R0 = self.resolveKeyTurbo(RK)

				# TURBO: Convert to production names for internal processing
				L_prod = self.charToProductionNameTurbo(L0)
				R_prod = self.charToProductionNameTurbo(R0)

				# TURBO: Convert to graphical representation for DISPLAY
				L_display = self.nameToGraphicalRepresentationTurbo(L_prod)
				R_display = self.nameToGraphicalRepresentationTurbo(R_prod)

				uniq = (L_prod, R_prod, val_int)  # Use production names for uniqueness
				if uniq in seen:
					continue
				seen.add(uniq)

				rows.append({
					"Left": L_display,	# SHOW GRAPHICAL CHARACTER
					"Right": R_display, # SHOW GRAPHICAL CHARACTER
					"Value": val_int,
					"_display": self.contextualDisplayTurbo(L0, R0, val_int),  # Uses production names for tab
					"_scriptL": self.scriptOrderTurbo(L_display),  # Sort by graphical representation
					"_scriptR": self.scriptOrderTurbo(R_display),  # Sort by graphical representation
					"_originalLeft": L0,
					"_originalRight": R0,
					"_productionLeft": L_prod,	# Store production name for tab generation
					"_productionRight": R_prod, # Store production name for tab generation
					"_sortValue": val_int,
				})

		# TURBO: Fast sorting with script blocks
		rows.sort(key=lambda r: (r["_scriptL"][0], r["_scriptR"][0], r["Left"], r["Right"]))

		# TURBO: Efficient separator insertion
		final = []
		lastBlock = None
		for r in rows:
			blk = r["_scriptL"][0]
			if lastBlock is not None and blk != lastBlock:
				final.append({"Left": "────", "Right": "────", "Value": "──", "_isSeparator": True})
			final.append({
				"Left": r["Left"],		# Graphical character for display
				"Right": r["Right"],	# Graphical character for display
				"Value": str(r["Value"]),
				"_originalData": r		# Contains production names for tab
			})
			lastBlock = blk

		self._allPairsTurbo = final
		self._currentDisplayPairsTurbo = final
		tab.pairsList.set(final)

	def clearPairsSearch(self, sender):
		"""TURBO: Instant search clear"""
		tab = self.w.tabs[1]
		tab.searchPairs.set("")
		tab.pairsList.set(self._allPairsTurbo)
		self._currentDisplayPairsTurbo = self._allPairsTurbo

	def filterPairsList(self, sender):
		"""TURBO: Fast search filtering - SEARCHES BOTH GRAPHICAL AND PRODUCTION NAMES"""
		tab = self.w.tabs[1]
		q = sender.get().strip()
		if not q:
			self.clearPairsSearch(None)
			return

		# TURBO: Quick exact match detection
		if q.endswith(","):
			exact = q[:-1].strip()
			filtered = [r for r in self._allPairsTurbo if r["Left"] == exact or r["Right"] == exact]
		else:
			# TURBO: Fast substring search in BOTH graphical and production names
			ql = q.lower()
			filtered = []
			for r in self._allPairsTurbo:
				original_data = r.get("_originalData", {})
				# Search in displayed graphical characters
				if (ql in r["Left"].lower() or 
					ql in r["Right"].lower() or 
					ql in str(r["Value"]) or
					# Also search in production names for better searchability
					ql in original_data.get("_productionLeft", "").lower() or
					ql in original_data.get("_productionRight", "").lower()):
					filtered.append(r)

		tab.pairsList.set(filtered)
		self._currentDisplayPairsTurbo = filtered

	def showSelectedPairsTurbo(self, sender):
		tab = self.w.tabs[1]
		font = Glyphs.font

		if not font or not hasattr(self, '_currentDisplayPairsTurbo'):
			print("⚠️ No kerning pairs loaded")
			return

		rows = self._currentDisplayPairsTurbo
		sel = tab.pairsList.getSelection()
		if not sel:
			print("⚠️ No selection")
			return

		# Prefix / suffix personalitzats (només Tab 2)
		custom_prefix = tab.customPrefixInput.get().strip() or "HH"
		custom_suffix = tab.customSuffixInput.get().strip() or "HH"

		lines = []

		for i in sel:
			row = rows[i]
			if row.get("Left") == "────":
				continue

			data = row.get("_originalData", row)

			left = data["_productionLeft"]
			right = data["_productionRight"]
			value = data["Value"]

			prefix = format_context(custom_prefix, left)
			suffix = format_context(custom_suffix, right)

			# DEBUG EXHAUSTIU
			print("🧪 TAB2 DEBUG -----------------------------")
			print("RAW prefix :", repr(custom_prefix))
			print("RAW suffix :", repr(custom_suffix))
			print("LEFT glyph :", left)
			print("RIGHT glyph:", right)
			print("FMT prefix :", prefix)
			print("FMT suffix :", suffix)

			base = format_kern_pair_block(prefix, left, right, suffix)
			line = f"{base}    {value}"

			print("FINAL LINE :", repr(line))
			print("-------------------------------------------")

			lines.append(line)

		if lines:
			tab_text = "\n".join(lines)
			print("🧪 TAB CONTENT FULL =======================")
			print(tab_text)
			print("===========================================")
			font.newTab(tab_text)

			
			
	# ===================================================
	# MÉTODOS PARA EL GESTOR DE GRUPOS (INTEGRADO)
	# ===================================================

	def getGroupGlyphsTurbo(self, group, side):
		"""TURBO: Fast group member retrieval with caching"""
		font = Glyphs.font
		if not font or not group:
			return []
	
		# TURBO: Check cache first
		cache_key = f"{group}_{side}"
		if cache_key in self._groupCacheTurbo:
			return self._groupCacheTurbo[cache_key]
	
		# TURBO: Get custom order from userData
		key = f"kernOrder_{side}"
		custom_order = font.userData.get(key, {}).get(group, [])
	
		# TURBO: Fast glyph collection
		glyph_names = [g.name for g in font.glyphs if getattr(g, side + "KerningGroup") == group]
	
		# TURBO: Apply custom order if exists
		if custom_order:
			valid_order = [name for name in custom_order if name in glyph_names]
			remaining = [name for name in glyph_names if name not in valid_order]
			glyph_names = valid_order + sorted(remaining)
		else:
			glyph_names = sorted(glyph_names)  # TURBO: Default alphabetical
	
		# TURBO: Format with trophy emoji for leader
		formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyph_names)]
	
		# TURBO: Cache result
		self._groupCacheTurbo[cache_key] = formatted
	
		return formatted

	def activeGroupTabTurbo(self):
		"""TURBO: Fast active tab detection"""
		tab = self.w.tabs[1]
		tab_index = tab.groupsTabs.get()
		font = Glyphs.font
		if not font or not font.selectedLayers:
			return None, None, None
		
		glyph = font.selectedLayers[0].parent
		if tab_index == 0:
			return "left", glyph.leftKerningGroup, tab.groupsTabs[0].list
		else:
			return "right", glyph.rightKerningGroup, tab.groupsTabs[1].list

	def refreshGroupManager(self, sender=None):
		"""TURBO: Fast group list refresh"""
		font = Glyphs.font
		tab = self.w.tabs[1]
	
		if not font or not font.selectedLayers:
			self.showNoGlyphSelectedTurbo()
			return
		
		glyph = font.selectedLayers[0].parent
	
		# TURBO: Parallel group processing
		leftGroup = glyph.leftKerningGroup
		rightGroup = glyph.rightKerningGroup
	
		if leftGroup:
			tab.groupsTabs[0].list.set(self.getGroupGlyphsTurbo(leftGroup, "left"))
		else:
			tab.groupsTabs[0].list.set(["No left group"])
		
		if rightGroup:
			tab.groupsTabs[1].list.set(self.getGroupGlyphsTurbo(rightGroup, "right"))
		else:
			tab.groupsTabs[1].list.set(["No right group"])

	def makeFirstGroup(self, sender):
		"""TURBO: Fast reordering with confirmation"""
		side, group, listView = self.activeGroupTabTurbo()
		if not group:
			Message(f"No {side} group for selected glyph")
			return

		sel = listView.getSelection()
		if not sel:
			Message("No glyph selected in group list")
			return

		selected_name = listView[sel[0]].replace("🏆", "").strip()
	
		# TURBO: Quick confirmation
		from vanilla.dialogs import askYesNo
		if not askYesNo(f"Set '{selected_name}' as first glyph for {side} group '{group}'?"):
			return

		# TURBO: Fast list reordering
		glyphs = [n.replace("🏆", "").strip() for n in listView]
		glyphs.remove(selected_name)
		glyphs.insert(0, selected_name)
		formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyphs)]
		listView.set(formatted)

		Message(f"'{selected_name}' is now first in {side} group")

	def applyGroupOrder(self, sender):
		"""TURBO: Fast order application"""
		side, group, listView = self.activeGroupTabTurbo()
		if not group:
			Message(f"No {side} group for selected glyph")
			return

		order = [n.replace("🏆", "").strip() for n in listView]
		font = Glyphs.font
		key = f"kernOrder_{side}"
	
		# TURBO: Efficient userData update
		if not font.userData.get(key):
			font.userData[key] = {}
		font.userData[key][group] = order

		# TURBO: Clear cache to force refresh
		cache_key = f"{group}_{side}"
		if cache_key in self._groupCacheTurbo:
			del self._groupCacheTurbo[cache_key]

		Message(f"Order applied to {side} group '{group}'")

	def showNoGlyphSelectedTurbo(self):
		"""TURBO: Quick no-selection display"""
		tab = self.w.tabs[1]
		tab.groupsTabs[0].list.set(["Select a glyph"])
		tab.groupsTabs[1].list.set(["Select a glyph"])
	
	
	
	def get_pairs_inside_hash_blocks(self, tab):
		"""
		Retorna un set de (left_name, right_name)
		NOMÉS dels blocs #…# del tab.
		Assumeix que dins del bloc ja hi ha /glyphs.
		"""
		pairs = set()
		if not tab or not hasattr(tab, "layers"):
			return pairs

		layers = tab.layers
		if not layers:
			return pairs

		text = tab.text or ""
		if "#" not in text:
			return pairs

		# Rangs protegits #…#
		hash_ranges = []
		stack = []
		for i, c in enumerate(text):
			if c == "#":
				if not stack:
					stack.append(i)
				else:
					start = stack.pop()
					hash_ranges.append((start, i))

		if not hash_ranges:
			return pairs

		# Mapatge text → layers (només glifs explícits /glyph)
		layer_index = 0
		char_to_layer = {}
		for i, c in enumerate(text):
			if c == "/" and layer_index < len(layers):
				char_to_layer[i] = layer_index
				layer_index += 1

		# Extreure parells consecutius dins de cada #…#
		for start, end in hash_ranges:
			indices = [
				char_to_layer[i]
				for i in range(start, end)
				if i in char_to_layer
			]

			for i in range(len(indices) - 1):
				L = layers[indices[i]]
				R = layers[indices[i + 1]]
				if not L or not R:
					continue

				left = L.parent.name
				right = R.parent.name

				if left == "space" or right == "space":
					continue

				pairs.add((left, right))

		return pairs


	
	
	
	def kernAVCallback(self, sender):
		"""
		Botón #AV#: aplicar el mismo motor de kerning que kernAutoCallback,
		es decir, solo pares dentro de bloques #...# del tab actual.
		"""
		print("\n" + "=" * 80)
		print("🧪 AV# → llamar a kernAutoCallback (AUTO KERN en bloques #...#)")
		print("=" * 80)

		# Reutilizar exactamente el mismo motor
		self.kernAutoCallback(sender)

			
	def initializePairsGeneratorCollections(self):
		self.TEST_WORDS_COLLECTIONS = {
			"Symetric Trios": "/H/H/A/V/A/H/H/space/H/H/A/O/A/H/H/space/H/H/A/T/A/H/H/space/H/H/A/Y/A/H/H/space/H/H/A/S/A/H/H/space/H/H/A/W/A/H/H/space/H/H/A/U/A/H/H/space/H/H/T/A/T/H/H/space/H/H/T/O/T/H/H/space/H/H/Y/A/Y/H/H/space/H/H/Y/O/Y/H/H/space/H/H/U/A/U/H/H/space/H/H/S/Y/S/H/H/space/H/H/S/A/S/H/H/space/H/H/O/T/O/H/H/space/H/H/O/A/O/H/H/space/H/H/O/V/O/H/H/space/H/H/O/W/O/H/H/space/H/H/O/X/O/H/H/space/H/H/O/Y/O/H/H/space/H/H/M/V/M/H/H/space/H/H/X/O/X/H/H\n\/n/h/h/o/w/o/h/h/space/h/h/o/y/o/h/h/space/h/h/o/x/o/h/h/space/h/h/y/o/y/h/h/space/h/h/v/o/v/h/h/space/h/h/w/o/w/h/h/space/h/h/x/o/x/h/h/space/h/h/s/w/s/h/h/space/h/h/s/v/s/h/h/space/h/h/s/y/s/h/h/space/h/h/s/o/s/h/h/space/h/h/o/s/o/h/h",
			"Diacritics": "/A/iacute/l/space/A/igrave/l/space/A/icircumflex/l/space/A/idieresis/l/space/A/i/idieresis/l/space/B/iacute/n/space/B/igrave/n/space/B/icircumflex/n/space/B/idieresis/n/space/C/iacute/n/space/C/igrave/n/space/C/icircumflex/n/space/C/idieresis/n/space/D/iacute/n/space/D/igrave/n/space/D/icircumflex/n/space/D/idieresis/n/space/E/iacute/n/space/E/igrave/n/space/E/icircumflex/n/space/E/idieresis/n/space/F/adieresis/h/r/space/F/odieresis/l/d/e/r/space/F/agrave/n/space/F/aring/n/space/F/aacute/l/space/F/acircumflex/l/space/F/atilde/l/space/F/egrave/space/F/eacute/space/F/ecircumflex/l/space/F/edieresis/l/space/F/iacute/l/space/F/igrave/l/space/F/icircumflex/l/space/F/idieresis/l/space/F/oacute/l/space/F/ograve/space/F/ocircumflex/l/space/F/otilde/l/space/F/uacute/l/space/F/ugrave/space/F/ucircumflex/l/space/F/ydieresis/space/F/udieresis/n/k/space/G/iacute/n/space/G/igrave/n/space/G/icircumflex/n/space/G/idieresis/n/space/H/iacute/n/space/H/igrave/n/space/H/icircumflex/space/H/idieresis/n/space/J/iacute/n/space/J/igrave/n/space/J/icircumflex/n/space/J/idieresis/n/space/K/adieresis/r/n/space/K/odieresis/f/f/space/K/udieresis/d/o/s/space/K/igrave/n/space/K/icircumflex/n/space/K/idieresis/n/space/K/ydieresis/n/space/M/iacute/n/space/M/igrave/n/space/M/icircumflex/space/M/idieresis/n/space/O/iacute/n/space/O/igrave/n/space/O/icircumflex/n/space/O/idieresis/n/space/P/adieresis/l/space/P/odieresis/l/space/P/udieresis/n/k/space/P/aacute/l/space/P/agrave/n/space/P/acircumflex/l/space/P/atilde/l/space/P/aring/n/space/P/eacute/l/space/P/egrave/space/P/ecircumflex/l/space/P/iacute/l/space/P/igrave/space/P/icircumflex/l/space/P/idieresis/l/space/P/oacute/l/space/P/ograve/n/space/P/ocircumflex/l/space/P/otilde/l/space/P/uacute/l/space/P/ugrave/space/P/ucircumflex/l/space/P/ydieresis/space/R/adieresis/n/space/R/odieresis/a/d/space/R/udieresis/n/g/space/R/iacute/n/space/R/igrave/n/space/R/icircumflex/n/space/R/idieresis/n/space/S/iacute/n/space/S/igrave/n/space/S/icircumflex/n/space/S/idieresis/n/space/T/adieresis/p/space/T/odieresis/r/n/space/T/udieresis/f/f/space/T/aacute/l/space/T/agrave/space/T/acircumflex/l/space/T/atilde/l/space/T/aring/l/space/T/eacute/l/space/T/egrave/n/space/T/ecircumflex/l/space/T/edieresis/l/space/T/iacute/l/space/T/igrave/n/space/T/icircumflex/l/space/T/idieresis/l/space/T/oacute/l/space/T/ograve/n/space/T/ocircumflex/l/space/T/otilde/l/space/T/uacute/l/space/T/ugrave/n/space/T/ucircumflex/l/space/T/ydieresis/n/space/U/iacute/n/space/U/igrave/n/space/U/icircumflex/n/space/U/idieresis/n/space/V/adieresis/m/space/V/odieresis/t/space/V/aacute/l/space/V/agrave/n/space/V/acircumflex/l/space/V/atilde/l/space/V/aring/n/space/V/eacute/l/space/V/egrave/n/space/V/ecircumflex/l/space/V/edieresis/n/space/V/iacute/n/space/V/igrave/n/space/V/icircumflex/n/space/V/idieresis/n/space/V/oacute/l/space/V/ograve/n/space/V/ocircumflex/l/space/V/odieresis/n/space/V/otilde/l/space/V/uacute/l/space/V/ugrave/n/space/V/ucircumflex/l/space/V/udieresis/n/space/V/ydieresis/n/space/W/a/i/n/space/space/W/adieresis/m/space/W/odieresis/t/space/W/aacute/l/space/W/agrave/n/space/W/acircumflex/l/space/W/atilde/l/space/W/aring/n/space/W/eacute/l/space/W/egrave/n/space/W/ecircumflex/l/space/W/edieresis/n/space/W/iacute/n/space/W/igrave/n/space/W/icircumflex/n/space/W/idieresis/n/space/W/oacute/l/space/W/ograve/n/space/W/ocircumflex/l/space/W/odieresis/n/space/W/otilde/l/space/W/uacute/l/space/W/ugrave/n/space/W/ucircumflex/l/space/W/udieresis/n/space/W/ydieresis/n/space/X/aacute/l/space/X/agrave/n/space/X/acircumflex/n/space/X/adieresis/n/space/X/atilde/n/space/X/aring/n/space/X/eacute/n/space/X/egrave/n/space/X/ecircumflex/n/space/X/edieresis/n/space/X/iacute/l/space/X/igrave/l/space/X/icircumflex/l/space/X/idieresis/l/space/X/oacute/n/space/X/ograve/n/space/X/ocircumflex/n/space/X/odieresis/n/space/X/otilde/n/space/X/uacute/n/space/X/ugrave/n/space/X/ucircumflex/n/space/X/udieresis/n/space/X/aring/n/space/X/ydieresis/n/space/Y/acircumflex/n/space/Y/adieresis/n/space/Y/atilde/n/space/Y/aring/n/space/Y/eacute/n/space/Y/egrave/n/space/Y/ecircumflex/n/space/Y/edieresis/n/space/Y/iacute/n/space/Y/igrave/n/space/Y/icircumflex/n/space/Y/idieresis/n/space/Y/oacute/n/space/Y/ograve/n/space/Y/ocircumflex/n/space/Y/odieresis/n/space/Y/otilde/n/space/Y/uacute/n/space/Y/ugrave/n/space/Y/ucircumflex/n/space/Y/udieresis/n/space/Z/iacute/n/space/Z/igrave/n/space/Z/icircumflex/n/space/Z/idieresis/n/space/dcaron/a/space/dcaron/i/space/dcaron/o/space/dcaron/u/space/dcaron/k/space/dcaron/A/space/dcaron/I/space/dcaron/O/space/dcaron/U/space/dcaron/quotesingle/space/dcaron/quotedbl/space/dcaron/quotedbl/space/dcaron/quotedbl/space/dcaron/exclam/space/dcaron/question/space/dcaron/parenright/space/dcaron/bracketright/space/dcaron/braceright/space/dcaron/asterisk/space/tcaron/a/space/tcaron/i/space/tcaron/o/space/tcaron/u/space/tcaron/k/space/tcaron/A/space/tcaron/I/space/tcaron/O/space/tcaron/U/space/tcaron/quotesingle/space/tcaron/quotedbl/space/tcaron/quotedbl/space/tcaron/quotedbl/space/tcaron/exclam/space/tcaron/question/space/tcaron/parenright/space/tcaron/bracketright/space/tcaron/braceright/space/tcaron/asterisk/space/Lcaron/a/space/Lcaron/i/space/Lcaron/o/space/Lcaron/k/space/Lcaron/u/space/Lcaron/A/space/Lcaron/I/space/Lcaron/O/space/Lcaron/U/space/Lcaron/quotesingle/Lcaron/quotedbl/Lcaron/quotedbl/space/Lcaron/quotedbl/space/Lcaron/exclam/space/Lcaron/question/space/Lcaron/parenright/space/Lcaron/braceright/space/Lcaron/bracketright/space/Lcaron/asterisk/space/H/Lcaron/H/dcaron/H/lcaron/H/tcaron/H/H/lslash/H/H/space/o/b/j/iacute/zcaron/dcaron/k/o/v/aacute/space/v/dcaron/a/ccaron/iacute/m/e/space/v/e/lcaron/h/o/r/y/space/v/e/lcaron/r/y/b/yacute/c/h/space/scaron/t/v/r/tcaron/h/o/d/i/n/o/v/yacute/space/n/a/j/tcaron/a/zcaron/scaron/iacute/c/h/space/I/l/u/s/t/r/a/c/i/oacute/space/c/e/l/a/space/C/O/L/E/G/I/space/C/E/L/A/space/zacute/r/oacute/d/lslash/o/s/lslash/o/w/u/adieresis/T/adieresis/V/adieresis/W/adieresis/Y/adieresis/space/amacron/T/amacron/V/amacron/W/amacron/Y/amacron/space/aring/T/aring/V/aring/W/aring/Y/aring/space/ccaron/T/ccaron/V/ccaron/W/ccaron/Y/ccaron/space/imacron/T/imacron/V/imacron/W/imacron/Y/imacron/space/idieresis/T/idieresis/V/idieresis/W/idieresis/Y/idieresis/space/gbreve/T/gbreve/V/gbreve/W/gbreve/Y/gbreve/space/ncaron/T/ncaron/V/ncaron/W/ncaron/Y/ncaron/space/emacron/T/emacron/V/emacron/W/emacron/Y/emacron/space/ecaron/T/ecaron/V/ecaron/W/ecaron/Y/ecaron/space/edieresis/T/edieresis/V/edieresis/W/edieresis/Y/edieresis/space/rcaron/T/rcaron/V/rcaron/W/rcaron/Y/rcaron/space/ocircumflex/T/ocircumflex/V/ocircumflex/W/ocircumflex/Y/ocircumflex/space/odieresis/T/odieresis/V/odieresis/W/odieresis/Y/odieresis/space/omacron/T/omacron/V/omacron/W/omacron/Y/omacron/space/scaron/T/scaron/V/scaron/W/scaron/Y/scaron/space/umacron/T/umacron/V/umacron/W/umacron/Y/umacron/space/uring/T/uring/V/uring/W/uring/Y/uring/space/ydieresis/T/ydieresis/V/ydieresis/W/ydieresis/Y/ydieresis/space/ytilde/T/ytilde/V/ytilde/W/ytilde/Y/ytilde/space/zcaron/T/zcaron/V/zcaron/W/zcaron/Y/zcaron",
			"Cyrillic Basic": "Ширяев\nОбъявление\nПодъем\nСъемка",
			"Mixed Scripts": "Hamburgefonstiv\nШиряев\nTypeface\nОбъявление"
		}

	def selectAllCallback(self, sender):
		if not hasattr(self, 'collisionStates') or not self.collisionStates:
			return
	
		# Toggle: si todos están seleccionados -> deseleccionar, sino -> seleccionar todos
		all_selected = all(s.get('checked', False) for s in self.collisionStates.values())
		new_state = not all_selected
	
		for idx in self.collisionStates:
			state = self.collisionStates[idx]
			cb = state.get('checkbox')
			if cb:
				cb.setState_(1 if new_state else 0)
			state['checked'] = new_state
			self.updateRowBackgroundColor(idx, new_state)
	
		# Cambiar título del botón
		try:
			tab = self.w.tabs[0]
			text = tab.text or ""
			layers = [l for l in tab.layers if l and l.parent]

			tab.selectAllButton.setTitle_("Select All" if new_state else "Deselect All")
		except:
			pass




	def get_hash_blocks_text(self, tab):
		"""
		Retorna una llista de textos dins de blocs #...#
		sense els #.
		"""
		if not tab or not tab.text:
			return []

		text = tab.text
		blocks = []
		stack = []

		for i, c in enumerate(text):
			if c == "#":
				if not stack:
					stack.append(i)
				else:
					start = stack.pop()
					content = text[start + 1 : i].strip()
					if content:
						blocks.append(content)

		return blocks


	def kernAutoCallback(self, sender):
		print("\n" + "=" * 80)
		print("🧪 AUTO KERN — BLOCS COMPLETS #...#")
		print("=" * 80)

		font = Glyphs.font
		if not font:
			return

		original_tab = font.currentTab
		if not original_tab:
			return

		blocks = self.get_hash_blocks_text(original_tab)

		print(f"📦 Blocs detectats: {len(blocks)}")
		for b in blocks:
			print(" ", b)

		if not blocks:
			print("⚠️ No hay bloques #...#")
			return

		font.disableUpdateInterface()
		try:
			for block_text in blocks:
				temp_tab = font.newTab(block_text)

				pairs = self.get_pairs_from_tab(temp_tab)
				print(f"🔗 Pares en bloc: {len(pairs)}")

				self.apply_kerning_to_pairs(pairs)

				temp_tab.close()
		finally:
			font.enableUpdateInterface()

		Glyphs.showNotification(
			"Auto Kern",
			f"{len(blocks)} blocs processats"
		)

	def get_pairs_from_tab(self, tab):
		print("\n🧪 DEBUG — get_pairs_from_tab")

		pairs = []
		if not tab:
			print("❌ No tab")
			return pairs

		if not tab.layers:
			print("❌ Tab has no layers")
			return pairs

		layers = tab.layers
		print(f"📐 Total layers: {len(layers)}")

		for i in range(len(layers) - 1):
			L = layers[i]
			R = layers[i + 1]

			if not L or not R:
				print(f"  [{i}] layer None → skip")
				continue

			if not L.parent or not R.parent:
				print(f"  [{i}] layer sense parent → skip")
				continue

			left = L.parent.name
			right = R.parent.name

			print(f"  [{i}] candidat: {left} / {right}")

			if left == "space" or right == "space":
				print("		⤷ skip (space)")
				continue

			pairs.append((left, right))
			pairs.append((right, left))

		print(f"✅ get_pairs_from_tab → {len(pairs)} parells")
		return pairs

		
	def applyCallback(self, sender):
		font = Glyphs.font
		if not font:
			Message("Error", "No font open.", OKButton="OK")
			return

		master = font.selectedFontMaster
		if not master:
			Message("Error", "No master selected.", OKButton="OK")
			return

		# --------------------------------------------------
		# FIND percentage input field (robust)
		# --------------------------------------------------
		percent_field = self.w.tabs[1].marginInput

		if not percent_field:
			Message(
				"Error",
				"Percentage input field not found.\n"
				"Expected one of:\n"
				"percentInput, percentEdit, scaleInput, valueInput",
				OKButton="OK"
			)
			return

		raw_value = percent_field.get()
		if raw_value is None:
			Message("Error", "Percentage field is empty.", OKButton="OK")
			return

		value_str = str(raw_value).strip()
		value_str = value_str.replace(",", ".")

		if value_str.endswith("%"):
			value_str = value_str[:-1].strip()

		try:
			percent = float(value_str)
		except:
			Message(
				"Error",
				f"Invalid percentage value:\n'{raw_value}'",
				OKButton="OK"
			)
			return

		# --------------------------------------------------
		# OPERATION
		# --------------------------------------------------
		operation = "Increase"
		if hasattr(self.w, "modePopup"):
			operation = self.w.modePopup.getItem()

		if operation == "Increase":
			factor = 1.0 - percent / 100.0
		else:  # Decrease
			factor = 1.0 + percent / 100.0


		master_id = master.id
		if master_id not in font.kerning:
			Message("Info", "No kerning found in the active master.", OKButton="OK")
			return

		# --------------------------------------------------
		# COPY kerning data (Glyphs-safe)
		# --------------------------------------------------
		kerning_pairs = []
		for left_key, right_dict in font.kerning[master_id].items():
			for right_key, value in right_dict.items():
				if value is not None:
					kerning_pairs.append((left_key, right_key, value))

		if not kerning_pairs:
			Message("Info", "No kerning pairs to scale.", OKButton="OK")
			return

		# --------------------------------------------------
		# Resolve glyph / group / UUID
		# --------------------------------------------------
		def resolveKey(key):
			if isinstance(key, str) and key.startswith("@MMK_"):
				return key
			if isinstance(key, str) and len(key) == 36:
				for g in font.glyphs:
					if g.id == key:
						return g.name
				return None
			return key

		# --------------------------------------------------
		# APPLY scaling
		# --------------------------------------------------
		count = 0
		font.disableUpdateInterface()
		try:
			for left_key, right_key, value in kerning_pairs:
				left = resolveKey(left_key)
				right = resolveKey(right_key)
				if not left or not right:
					continue

				new_value = int(round(value * factor))
				font.setKerningForPair(master_id, left, right, new_value)
				count += 1
		finally:
			font.enableUpdateInterface()

		Message(
			"Done",
			f"Kerning updated: {count} pairs\n"
			f"Operation: {operation}\n"
			f"Percentage: {percent}%",
			OKButton="OK"
		)



		
		
		

	def apply_kerning_to_pairs(self, pairs):
		font = Glyphs.font
		if not font or not pairs:
			return

		master = font.selectedFontMaster
		mid = master.id

		try:
			target_margin = float(self.w.tabs[0].marginInput.get())
		except:
			target_margin = 40.0

		for left, right in pairs:
			if left not in font.glyphs or right not in font.glyphs:
				continue

			current = margin_for_pair(font, mid, left, right)
			if current is None or current >= 10000:
				continue

			# 👉 NOMÉS KERN POSITIU
			if current >= target_margin:
				continue

			delta = int(round(target_margin - current))
			if delta <= 0:
				continue

			font.setKerningForPair(mid, left, right, delta)
			print(f"✔ Kern +{delta} {left} {right}")




	
	
	
	def createCollisionListWithCheckboxes(self, resultsList, reset_label=False):
		"""Crea una llista de col·lisions amb checkboxes manuales"""
		print(f"🧪 DEBUG: createCollisionListWithCheckboxes called with {len(resultsList)} items, reset_label={reset_label}")
	
		tab = self.w.tabs[0]
	
		if reset_label:
			# Solo limpiar completamente si se especifica
			self.clearCollisionList(reset_label=True)
	
		# Obtener containerView
		containerView = tab.resultsContainer.getNSView()
	
		# Limpiar contenedor visual (si no se hizo en clearCollisionList)
		if not reset_label:
			for subview in containerView.subviews():
				subview.removeFromSuperview()
		
			# Reiniciar variables
			self.collisionCheckboxes = []
			self.collisionStates = {}
			self.selectedCollisionIndex = -1
			self.collisionContentHeight = 0
	
		if not resultsList:
			print("🧪 DEBUG: No results to display")
			noCollisionsLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 80, 360, 22))
			noCollisionsLabel.setStringValue_("No collisions found")
			noCollisionsLabel.setEditable_(False)
			noCollisionsLabel.setBordered_(False)
			noCollisionsLabel.setDrawsBackground_(False)
			noCollisionsLabel.setTextColor_(NSColor.grayColor())
			noCollisionsLabel.setAlignment_(3)
			containerView.addSubview_(noCollisionsLabel)
			return
	
		scrollView = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 180))
		scrollView.setHasVerticalScroller_(True)
		scrollView.setHasHorizontalScroller_(False)
		scrollView.setAutohidesScrollers_(True)
		scrollView.setBorderType_(NSNoBorder)
	
		contentHeight = len(resultsList) * 24
		contentView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 340, contentHeight))
	
		for i, result_text in enumerate(resultsList):
			rowBackground = NSView.alloc().initWithFrame_(NSMakeRect(0, contentHeight - (i+1)*24, 340, 24))
			rowBackground.setWantsLayer_(True)
		
			layer = rowBackground.layer()
			if layer:
				layer.setBackgroundColor_(NSColor.clearColor().CGColor())
		
			checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(10, 2, 20, 20))
			checkbox.setButtonType_(NSSwitchButton)
			checkbox.setTitle_("")
			checkbox.setTag_(i)
			checkbox.setTarget_(self)
			checkbox.setAction_("collisionCheckboxClicked:")
		
			label = NSTextField.alloc().initWithFrame_(NSMakeRect(35, 2, 300, 20))
			label.setStringValue_(result_text)
			label.setEditable_(False)
			label.setBordered_(False)
			label.setDrawsBackground_(False)
			label.setTextColor_(NSColor.blackColor())
		
			rowBackground.addSubview_(checkbox)
			rowBackground.addSubview_(label)
		
			contentView.addSubview_(rowBackground)
		
			self.collisionCheckboxes.append(checkbox)
			self.collisionStates[i] = {
				'text': result_text,
				'checked': False,
				'checkbox': checkbox,
				'label': label,
				'background': rowBackground,
				'rowIndex': i
			}
	
		self.collisionContentHeight = contentHeight
	
		scrollView.setDocumentView_(contentView)
		containerView.addSubview_(scrollView)
	
		print(f"🧪 DEBUG: Created {len(resultsList)} checkboxes")

	def listSelectedPairsCallback(self, sender):
		"""
		Crea tabs amb els parells seleccionats en 4 columnes PERFECTES.
		Layout només amb /glyph (ASCII pur).
		"""

		font = Glyphs.font
		if not font:
			return

		master = font.selectedFontMaster
		if not master:
			return

		mid = master.id
		tab = self.w.tabs[0]

		# -------------------------------------------------
		# Glyphs to check
		# -------------------------------------------------
		try:
			glyphs_to_check_text = tab.glyphsInput.get()
			specified_glyphs = [g.strip() for g in glyphs_to_check_text.split(",") if g.strip()]
		except:
			return

		if not specified_glyphs:
			print("⚠️ No glyphs specified")
			return

		# -------------------------------------------------
		# Selected collision pairs
		# -------------------------------------------------
		selected_pairs = []
		for idx, state in self.collisionStates.items():
			if state.get("checked") and idx < len(self.collisionPairs):
				selected_pairs.append(self.collisionPairs[idx])

		if not selected_pairs:
			print("ℹ️ No collision pairs selected")
			return

		# -------------------------------------------------
		# Hide existing pairs
		# -------------------------------------------------
		try:
			hide_existing = tab.blockCheckbox.get()
		except:
			hide_existing = False

		masterName = master.name

		# -------------------------------------------------
		# Create one tab per glyph
		# -------------------------------------------------
		for glyph_name in specified_glyphs:
			if glyph_name not in font.glyphs:
				continue

			# Collect pairs for this glyph
			glyph_pairs = [
				(left, right, prefix, suffix)
				for (left, right, prefix, suffix) in selected_pairs
				if left == glyph_name or right == glyph_name
			]

			if not glyph_pairs:
				continue

			# Optionally hide existing kerning
			if hide_existing:
				filtered_pairs = []
				for left, right, prefix, suffix in glyph_pairs:
					if not self.hasKerning(font, mid, left, right):
						filtered_pairs.append((left, right, prefix, suffix))
			else:
				filtered_pairs = glyph_pairs

			if not filtered_pairs:
				continue

			# -------------------------------------------------
			# Build CORE strings (/glyph only, no spaces)
			# -------------------------------------------------
			pair_strings = []
			for left, right, prefix, suffix in filtered_pairs:
				pair_strings.append(
					format_kern_pair_core(prefix, left, right, suffix)
				)

			# -------------------------------------------------
			# Layout in 4 columns (ASCII safe)
			# -------------------------------------------------
			num_columns = 4
			num_items = len(pair_strings)
			rows_needed = (num_items + num_columns - 1) // num_columns

			columns = [[] for _ in range(num_columns)]
			for idx, item in enumerate(pair_strings):
				columns[idx % num_columns].append(item)

			column_widths = [
				max(len(item) for item in col) if col else 0
				for col in columns
			]

			# -------------------------------------------------
			# Build final tab text
			# -------------------------------------------------
			lines = []
			lines.append(f"# {glyph_name} - {len(filtered_pairs)} parells seleccionats")
			lines.append(f"# Master: {masterName}")
			lines.append("")

			for row in range(rows_needed):
				row_items = []
				for col in range(num_columns):
					if row < len(columns[col]):
						item = columns[col][row]
						row_items.append(item.ljust(column_widths[col]))
					else:
						row_items.append(" " * column_widths[col])

				# 5 spaces at start, 6 spaces between columns
				lines.append(" " * 5 + (" " * 6).join(row_items).rstrip())

			font.newTab("\n".join(lines))


			
	def format_kern_pair_core(prefix, left, right, suffix):
		"""
		Formatter PUR: MAI afegeix espais.
		"""
		prefix = normalize_context(prefix)
		suffix = normalize_context(suffix)
		return f"{prefix}/{left}/{right}{suffix}"

	
	
	def layersAreCloseCollision(self, layer1, layer2, dx, margin):
		"""Verificar col·lisió entre capes"""
		segs1 = getSegments(layer1)
		segs2 = getSegments(layer2)
		if not segs1 or not segs2:
			print(f"🧪 DEBUG layersAreCloseCollision: No segments")
			return False
	
		shifted = []
		for n1, n2 in segs2:
			shifted.append((
				type("P", (), {"x": n1.x+dx, "y": n1.y}),
				type("P", (), {"x": n2.x+dx, "y": n2.y})
			))
	
		for s1 in segs1:
			for s2 in shifted:
				distance = minDistanceBetweenSegments(s1[0], s1[1], s2[0], s2[1])
				if distance < margin:
					print(f"🧪 DEBUG layersAreCloseCollision: Collision! distance={distance}, margin={margin}")
					return True
	
		return False

	
	
	def boxesAreCloseCollision(self, b1, b2, margin):
		"""Verificar si bounding boxes estan a prop"""
		result = not (b1[2] + margin < b2[0] or b2[2] + margin < b1[0] or b1[3] + margin < b2[1] or b2[3] + margin < b1[1])
		# print(f"🧪 DEBUG boxesAreCloseCollision: b1={b1}, b2={b2}, margin={margin}, result={result}")
		return result
	
	
	def clearCollisionList(self, reset_label=True):
		"""Neteja la llista de col·lisions i checkboxes"""
		tab = self.w.tabs[0]
	
		# Solo resetear contador si se indica
		if reset_label:
			tab.resultsLabel.set("Collisions found: 0")
	
		# Verificar que resultsContainer existe
		if not hasattr(tab, 'resultsContainer'):
			return
	
		containerView = tab.resultsContainer.getNSView()
	
		# Limpiar contenedor
		for subview in containerView.subviews():
			subview.removeFromSuperview()
	
		# Crear vista de estado vacío
		backgroundView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 180))
		backgroundView.setWantsLayer_(True)
		backgroundView.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
	
		# Borde sutil
		borderLayer = CALayer.layer()
		borderLayer.setFrame_(NSMakeRect(0, 0, 360, 180))
		borderLayer.setBorderWidth_(1.0)
		borderLayer.setBorderColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(
			0.9, 0.9, 0.9, 1.0).CGColor())
		backgroundView.layer().addSublayer_(borderLayer)
	
		# Mensaje principal
		messageLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 75, 360, 30))
		messageLabel.setStringValue_("No collisions checked yet")
		messageLabel.setEditable_(False)
		messageLabel.setBordered_(False)
		messageLabel.setDrawsBackground_(False)
		messageLabel.setTextColor_(NSColor.grayColor())
		messageLabel.setAlignment_(NSCenterTextAlignment)
		messageLabel.setFont_(NSFont.systemFontOfSize_(12))
	
		# Instrucciones
		instructionLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 45, 360, 20))
		instructionLabel.setStringValue_("Enter glyphs and click 'Check Collisions'")
		instructionLabel.setEditable_(False)
		instructionLabel.setBordered_(False)
		instructionLabel.setDrawsBackground_(False)
		instructionLabel.setTextColor_(NSColor.lightGrayColor())
		instructionLabel.setAlignment_(NSCenterTextAlignment)
		instructionLabel.setFont_(NSFont.systemFontOfSize_(9))
	
		backgroundView.addSubview_(messageLabel)
		backgroundView.addSubview_(instructionLabel)
	
		containerView.addSubview_(backgroundView)
	
		# Reiniciar variables
		self.collisionCheckboxes = []
		self.collisionStates = {}
		self.selectedCollisionIndex = -1
		self.collisionContentHeight = 0
	
		# Restablir el botó Select All
		try:
			tab.selectAllButton.setTitle("Select All")
		except:
			pass
	
		# Actualizar preview
		self.createEmptyPreviewCollision()

		
				
	def loadJSONPairsCallback(self, sender):
		print("🧪 Import JSON button pressed")

		from vanilla.dialogs import getFile

		paths = getFile(
			fileTypes=["json"],
			allowsMultipleSelection=False
		)

		if not paths:
			return

		pairs = self.loadKerningPairsFromJSON(paths[0])
		if not pairs:
			print("ℹ️ No valid pairs loaded")
			return

		# Guardar pares para que el motor pueda acceder a ellos
		self.importedJSONPairs = pairs
		print(f"✅ Imported {len(pairs)} pairs from JSON")
	
		# Crear tab con los pares usando contexto correcto
		font = Glyphs.font
		if font:
			# Generar cada par con su contexto apropiado
			tab_lines = []
			for left, right in pairs:
				prefix, suffix = self.get_prefix_suffix_for_pair(left, right)
				tab_lines.append(f"{prefix}/{left}/{right}{suffix}")
		
			# Unir con 4 espacios
			tab_content = "	   ".join(tab_lines)
			font.newTab(tab_content)
		
			print(f"📋 Tab creado con {len(pairs)} pares (contexto corregido)")
	
	
	def closeCurrentTabCallback(self, sender):
		font = Glyphs.font
		if not font:
			return

		tab = font.currentTab
		if tab:
			tab.close()
	
	


	

	def __init__(self):
		self.w = None
		self.initializePairsGeneratorCollections()
		self.w = FloatingWindow((400, 900), "Kern with live overwrite")
	
		# Crear pestanyas (solo las 2 que quedan)
		self.w.tabs = Tabs((10, 10, -10, -10), ["Collision Detector", "Tools"])
	
		# Variables para Collision Detector
		self.collisionPairs = []
		self.collisionCheckboxes = []
		self.collisionStates = {}
		self.selectedCollisionIndex = -1
		self.currentCollisionPrefix = ""
		self.currentCollisionLeftGlyph = ""
		self.currentCollisionRightGlyph = ""
		self.currentCollisionSuffix = ""
		self.zoomLevelCollision = ZOOM_LEVEL / 100.0
	
		# ============================================
		# VARIABLES PARA EL LISTADOR TURBO (INICIALIZAR)
		# ============================================
		self._allPairsTurbo = []
		self._currentDisplayPairsTurbo = []
		self._kerningCacheTurbo = {}
		self._keyCacheTurbo = {}
		self._productionCacheTurbo = {}
		self._graphicalCacheTurbo = {}
		self._groupCacheTurbo = {}
		# ============================================
	
		# Construir las pestañas que quedan
		self.buildCollisionDetectorTab()  # ¡PROBLEMA! Esto llama a métodos que aún no están definidos
		self.buildToolsTab()
	
		# Crear UI inicial INMEDIATAMENTE (sin timers, sin clases anidadas)
		self.createImmediateInitialUI()
	
		# INICIALIZAR EL LISTADOR DE PARES
		self.initializeTurboLister()
	
		self.w.open()
		
		
	def initializeTurboLister(self):
		"""Inicializa el listador TURBO con datos"""
		try:
			self.refreshPairsList()
			self.refreshGroupManager()
		except Exception as e:
			print(f"⚠️ Error inicializando listador TURBO: {e}")
			# Inicializa las listas vacías para evitar errores
			self._allPairsTurbo = []
			self._currentDisplayPairsTurbo = []
		
		
	
	def createImmediateInitialUI(self):
		"""Crea la UI inicial inmediatamente después de construir la pestaña"""
		try:
			tab = self.w.tabs[0]
			
			# Crear vista previa vacía
			if hasattr(tab, 'previewView'):
				previewView = tab.previewView.getNSView()
				
				# Limpiar
				for subview in previewView.subviews():
					subview.removeFromSuperview()
				
				# Crear fondo blanco simple
				bgView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 150))
				bgView.setWantsLayer_(True)
				bgView.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
				
				# Agregar borde
				border = CALayer.layer()
				border.setFrame_(NSMakeRect(0, 0, 360, 150))
				border.setBorderWidth_(1)
				border.setBorderColor_(NSColor.lightGrayColor().CGColor())
				bgView.layer().addSublayer_(border)
				
				previewView.addSubview_(bgView)
			
			# Crear área de resultados vacía
			if hasattr(tab, 'resultsContainer'):
				containerView = tab.resultsContainer.getNSView()
				
				# Limpiar
				for subview in containerView.subviews():
					subview.removeFromSuperview()
				
				# Crear fondo blanco simple
				bgView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 180))
				bgView.setWantsLayer_(True)
				bgView.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
				
				# Agregar borde
				border = CALayer.layer()
				border.setFrame_(NSMakeRect(0, 0, 360, 180))
				border.setBorderWidth_(1)
				border.setBorderColor_(NSColor.lightGrayColor().CGColor())
				bgView.layer().addSublayer_(border)
				
				containerView.addSubview_(bgView)
				
		except Exception as e:
			print(f"⚠️ Error en inicialización inmediata: {e}")

			
	def checkCollisionsCallback(self, sender):
		"""Callback per al botó Check Collisions - CON FILTRO DE VECINOS SIN CREACIÓN AUTOMÁTICA DE TAB"""
		print("🧪 DEBUG: checkCollisionsCallback START")
	
		font = Glyphs.font
		if not font:
			print("🧪 DEBUG ERROR: No font open")
			return
	
		tab = self.w.tabs[0]
	
		# Netejar resultats anteriors (RESETEAR LABEL)
		self.clearCollisionList(reset_label=True)
		self.collisionPairs = []
	
		self.createEmptyPreviewCollision()
	
		names = [n.strip() for n in tab.glyphsInput.get().split(",") if n.strip()]
		print(f"🧪 DEBUG: Glyphs to check: {names}")
	
		# ===== OBTENER GLIFOS VECINOS DEL CAMPO NUEVO =====
		neighbors_text = tab.neighborsInput.get()
		neighbor_names = []
	
		if neighbors_text and neighbors_text.strip():
			# Procesar el texto: dividir por líneas, luego por comas
			lines = neighbors_text.split('\n')
			for line in lines:
				line_names = [n.strip() for n in line.split(",") if n.strip()]
				neighbor_names.extend(line_names)
		
			print(f"🧪 DEBUG: Neighbor glyphs specified: {len(neighbor_names)}")
			print(f"🧪 DEBUG: Neighbors: {neighbor_names}")
	
		# ===== FILTRAR NOMBRES CON EXTENSIONES =====
		excluded_extensions = [
			'.sc', '.dnom', '.numr', '.subs', '.sups', '.titl', 
			'.case', '.comb', '.init', '.medi', '.fina', '.isol',
			'.liga', '.calt', '.locl', '.ss01', '.ss02', '.ss03',
			'.ss04', '.ss05', '.ss06', '.ss07', '.ss08', '.ss09',
			'.ss10', '.ss11', '.ss12', '.ss13', '.ss14', '.ss15',
			'.ss16', '.ss17', '.ss18', '.ss19', '.ss20'
		]
	
		filtered_names = []
		for name in names:
			has_extension = False
			for ext in excluded_extensions:
				if ext in name:
					has_extension = True
					print(f"🧪 DEBUG: Skipping glyph with extension '{ext}': {name}")
					break
		
			if not has_extension:
				filtered_names.append(name)
	
		names = filtered_names
		print(f"🧪 DEBUG: Filtered glyphs to check: {names}")
		# ===== FIN DEL FILTRO =====
	
		try:
			margin = float(tab.toleranceInput.get())
			print(f"🧪 DEBUG: Tolerance margin: {margin}")
		except:
			margin = 40.0
			print(f"🧪 DEBUG: Using default margin: {margin}")
	
		if not names:
			print("🧪 DEBUG: No glyph names specified")
			# Mostrar mensaje cuando no hay glifos especificados
			self.createEmptyResultsList("Enter glyphs to check")
			return
	
		master = font.selectedFontMaster
		if not master:
			print("🧪 DEBUG ERROR: No master selected")
			self.createEmptyResultsList("No master selected")
			return
	
		mid = master.id
		print(f"🧪 DEBUG: Master ID: {mid}")
	
		# ===== DETERMINAR LA LISTA DE GLIFOS CONTRA LOS QUE COMPARAR =====
		allGlyphNames = []
	
		if neighbor_names:
			# Si hay glifos vecinos especificados, usar solo esos
			print(f"🧪 DEBUG: Using ONLY neighbor glyphs list")
		
			# Filtrar vecinos con extensiones
			filtered_neighbors = []
			for neighbor in neighbor_names:
				has_extension = False
				for ext in excluded_extensions:
					if ext in neighbor:
						has_extension = True
						print(f"🧪 DEBUG: Skipping neighbor with extension '{ext}': {neighbor}")
						break
			
				if not has_extension and neighbor in font.glyphs:
					filtered_neighbors.append(neighbor)
				elif neighbor not in font.glyphs:
					print(f"🧪 DEBUG WARNING: Neighbor glyph '{neighbor}' not found in font")
		
			allGlyphNames = filtered_neighbors
			print(f"🧪 DEBUG: Using {len(allGlyphNames)} filtered neighbor glyphs")
		else:
			# Si no hay vecinos especificados, usar todos los glifos del font
			print(f"🧪 DEBUG: No neighbor glyphs specified, using ALL font glyphs")
			allGlyphNames = list(font.glyphs.keys())
		
			# Filtrar glifos con extensiones de la lista completa
			filtered_all_glyph_names = []
			for glyph_name in allGlyphNames:
				has_extension = False
				for ext in excluded_extensions:
					if ext in glyph_name:
						has_extension = True
						break
			
				if not has_extension:
					filtered_all_glyph_names.append(glyph_name)
		
			allGlyphNames = filtered_all_glyph_names
			print(f"🧪 DEBUG: Total glyphs in font (filtered): {len(allGlyphNames)}")
	
		# Cache de dades per a millor rendiment
		segCache, bboxCache, adv = {}, {}, {}
	
		print(f"🧪 DEBUG: Processing specified glyphs...")
		for name in names:
			if name in font.glyphs:
				glyph = font.glyphs[name]
				print(f"🧪 DEBUG: Found glyph: {name}")
				layer = None
				for l in glyph.layers:
					if l.associatedMasterId == mid:
						layer = l
						break
				if not layer and glyph.layers:
					layer = glyph.layers[0]
			
				if layer:
					try:
						layer_copy = layer.copyDecomposedLayer()
						print(f"🧪 DEBUG: Decomposed layer for {name}")
					except Exception as e:
						layer_copy = layer
						print(f"🧪 DEBUG: Using original layer for {name}: {e}")
				
					segCache[name] = getSegments(layer_copy)
					bboxCache[name] = self.bboxCollision(layer_copy)
					adv[name] = layer_copy.width
					print(f"🧪 DEBUG: Cached data for {name}: width={layer_copy.width}")
				else:
					print(f"🧪 DEBUG WARNING: No layer found for {name}")
			else:
				print(f"🧪 DEBUG WARNING: Glyph '{name}' not found in font")
	
		specified = [font.glyphs[n] for n in names if n in font.glyphs]
		print(f"🧪 DEBUG: Valid specified glyphs: {len(specified)}")
	
		if not specified:
			print("🧪 DEBUG: No valid glyphs found")
			self.createEmptyResultsList("No valid glyphs found")
			return
	
		# Inicializar resultsList aquí
		resultsList = []
		temp_collision_pairs = []
	
		print(f"🧪 DEBUG: Starting collision detection...")
	
		# FASE 1: Cada glifo especificado como IZQUIERDO contra los vecinos/todos
		print(f"🧪 DEBUG: FASE 1 - Glifos especificados como IZQUIERDOS")
		for left in specified:
			L = None
			for l in left.layers:
				if l.associatedMasterId == mid:
					L = l
					break
			if not L and left.layers:
				L = left.layers[0]
		
			if not L:
				print(f"🧪 DEBUG: No layer for {left.name}, skipping")
				continue
		
			try:
				L = L.copyDecomposedLayer()
				print(f"🧪 DEBUG: Decomposed left layer for {left.name}")
			except Exception as e:
				print(f"🧪 DEBUG: Could not decompose {left.name}: {e}")
				pass
		
			collision_count = 0
			print(f"🧪 DEBUG: Checking {left.name} as LEFT against {len(allGlyphNames)} glyphs...")
		
			# Contador de progreso
			checked = 0
			total_to_check = len(allGlyphNames)
		
			for right_name in allGlyphNames:
				checked += 1
				if checked % 100 == 0:
					print(f"🧪 DEBUG: Progress: {checked}/{total_to_check} glyphs checked")
			
				if right_name == left.name:
					continue
			
				# ===== FILTRAR GLIFOS CON EXTENSIONES DURANTE LA DETECCIÓN =====
				skip_this_glyph = False
				for ext in excluded_extensions:
					if ext in right_name:
						skip_this_glyph = True
						break
			
				if skip_this_glyph:
					continue
				# ===== FIN DEL FILTRO DURANTE DETECCIÓN =====
			
				if right_name not in segCache:
					if right_name in font.glyphs:
						right_glyph = font.glyphs[right_name]
						R_layer = None
						for l in right_glyph.layers:
							if l.associatedMasterId == mid:
								R_layer = l
								break
						if not R_layer and right_glyph.layers:
							R_layer = right_glyph.layers[0]
					
						if R_layer:
							try:
								R_layer_copy = R_layer.copyDecomposedLayer()
							except Exception:
								R_layer_copy = R_layer
						
							segCache[right_name] = getSegments(R_layer_copy)
							bboxCache[right_name] = self.bboxCollision(R_layer_copy)
							adv[right_name] = R_layer_copy.width
			
				# Verificar bounding boxes primer (més ràpid)
				if not self.boxesAreCloseCollision(bboxCache.get(left.name, (0,0,0,0)), 
												bboxCache.get(right_name, (0,0,0,0)), 
												margin):
					continue
			
				dx = adv.get(left.name, 0)
			
				R_for_check = None
				if right_name in font.glyphs:
					right_glyph = font.glyphs[right_name]
					for l in right_glyph.layers:
						if l.associatedMasterId == mid:
							R_for_check = l
							break
					if not R_for_check and right_glyph.layers:
						R_for_check = right_glyph.layers[0]
			
				if R_for_check:
					try:
						R_for_check = R_for_check.copyDecomposedLayer()
					except Exception:
						pass
				
					# Verificar col·lisió real
					if self.layersAreCloseCollision(L, R_for_check, dx, margin):
						pre, suf = self.contextualPrefixSuffixCollision(left, font.glyphs[right_name])
					
						temp_collision_pairs.append((left.name, right_name, pre, suf))
					
						# Format per a la llista amb checkboxes
						displayText = f"{left.name} / {right_name}"
						resultsList.append(displayText)
					
						collision_count += 1
						print(f"🧪 DEBUG COLLISION FOUND: {left.name} / {right_name}")

		# FASE 2: Cada glifo especificado como DERECHO contra los vecinos/todos
		print(f"\n🧪 DEBUG: FASE 2 - Glifos especificados como DERECHOS")
		for right in specified:
			R = None
			for l in right.layers:
				if l.associatedMasterId == mid:
					R = l
					break
			if not R and right.layers:
				R = right.layers[0]
		
			if not R:
				print(f"🧪 DEBUG: No layer for {right.name}, skipping")
				continue
		
			try:
				R = R.copyDecomposedLayer()
				print(f"🧪 DEBUG: Decomposed right layer for {right.name}")
			except Exception as e:
				print(f"🧪 DEBUG: Could not decompose {right.name}: {e}")
				pass
		
			collision_count = 0
			print(f"🧪 DEBUG: Checking {right.name} as RIGHT against {len(allGlyphNames)} glyphs...")
		
			# Contador de progreso
			checked = 0
			total_to_check = len(allGlyphNames)
		
			for left_name in allGlyphNames:
				checked += 1
				if checked % 100 == 0:
					print(f"🧪 DEBUG: Progress: {checked}/{total_to_check} glyphs checked")
			
				if left_name == right.name:
					continue
			
				# ===== FILTRAR GLIFOS CON EXTENSIONES DURANTE LA DETECCIÓN =====
				skip_this_glyph = False
				for ext in excluded_extensions:
					if ext in left_name:
						skip_this_glyph = True
						break
			
				if skip_this_glyph:
					continue
				# ===== FIN DEL FILTRO DURANTE DETECCIÓN =====
			
				if left_name not in segCache:
					if left_name in font.glyphs:
						left_glyph = font.glyphs[left_name]
						L_layer = None
						for l in left_glyph.layers:
							if l.associatedMasterId == mid:
								L_layer = l
								break
						if not L_layer and left_glyph.layers:
							L_layer = left_glyph.layers[0]
					
						if L_layer:
							try:
								L_layer_copy = L_layer.copyDecomposedLayer()
							except Exception:
								L_layer_copy = L_layer
						
							segCache[left_name] = getSegments(L_layer_copy)
							bboxCache[left_name] = self.bboxCollision(L_layer_copy)
							adv[left_name] = L_layer_copy.width
			
				# Necesitamos calcular dx basado en el glifo izquierdo
				dx = adv.get(left_name, 0)
			
				# Verificar bounding boxes primer (més ràpid)
				if not self.boxesAreCloseCollision(bboxCache.get(left_name, (0,0,0,0)), 
												bboxCache.get(right.name, (0,0,0,0)), 
												margin):
					continue
			
				L_for_check = None
				if left_name in font.glyphs:
					left_glyph = font.glyphs[left_name]
					for l in left_glyph.layers:
						if l.associatedMasterId == mid:
							L_for_check = l
							break
					if not L_for_check and left_glyph.layers:
						L_for_check = left_glyph.layers[0]
			
				if L_for_check:
					try:
						L_for_check = L_for_check.copyDecomposedLayer()
					except Exception:
						pass
				
					# Verificar col·lisió real
					if self.layersAreCloseCollision(L_for_check, R, dx, margin):
						# Para pares donde el glifo especificado está a la derecha,
						# necesitamos obtener el contexto apropiado
						left_glyph_obj = font.glyphs[left_name]
						pre, suf = self.contextualPrefixSuffixCollision(left_glyph_obj, right)
					
						temp_collision_pairs.append((left_name, right.name, pre, suf))
					
						# Format per a la llista amb checkboxes
						displayText = f"{left_name} / {right.name}"
						resultsList.append(displayText)
					
						collision_count += 1
						print(f"🧪 DEBUG COLLISION FOUND: {left_name} / {right.name}")
	
		# ===== 6. ACTUALIZAR UI CON RESULTADOS =====
		self.collisionPairs = temp_collision_pairs
	
		if resultsList:
			tab.resultsLabel.set(f"Collisions found: {len(resultsList)}")
		
			self.createCollisionListWithCheckboxes(
				resultsList,
				reset_label=False
			)
		
			# Si hay resultados, mostrar el primero en preview
			if self.collisionPairs:
				left, right, pre, suf = self.collisionPairs[0]
				self.currentCollisionPrefix = pre
				self.currentCollisionLeftGlyph = left
				self.currentCollisionRightGlyph = right
				self.currentCollisionSuffix = suf
				self.selectedCollisionIndex = 0
				self.updateRowBackgroundColor(0, 'navigate')
				self.updatePreviewCollision(pre, left, right, suf)
		else:
			self.createEmptyResultsList("No collisions found")
	
		print(f"✅ checkCollisionsCallback END. Found {len(resultsList)} collisions")

	# ===== AHORA define useSelectedCollisionCallback =====

	def useSelectedCollisionCallback(self, sender):
		print("\n" + "=" * 80)
		print("🧪 USE = Detectar colisiones: NEIGHBORS → GLYPHS TO CHECK")
		print("=" * 80)

		tab = self.w.tabs[0]
		font = Glyphs.font
		if not font:
			print("❌ No font open")
			return

		# --- 1. OBTENER LISTAS DE AMBOS CAMPOS ---
		# Glyphs to check (derecha)
		glyphs_to_check_text = tab.glyphsInput.get()
		right_glyphs = [g.strip() for g in glyphs_to_check_text.split(",") if g.strip()]
	
		# Only neighboring glyphs (izquierda)
		neighbors_text = tab.neighborsInput.get()
		left_glyphs = []
	
		if neighbors_text and neighbors_text.strip():
			lines = neighbors_text.split('\n')
			for line in lines:
				line_names = [n.strip() for n in line.split(",") if n.strip()]
				left_glyphs.extend(line_names)

		print(f"DEBUG left_glyphs (from 'Only neighboring glyphs'): {left_glyphs}")
		print(f"DEBUG right_glyphs (from 'Glyphs to check'): {right_glyphs}")

		if not left_glyphs:
			print("❌ No glyphs in 'Only neighboring glyphs'")
			self.createEmptyResultsList("Enter glyphs in 'Only neighboring glyphs'")
			return
	
		if not right_glyphs:
			print("❌ No glyphs in 'Glyphs to check'")
			self.createEmptyResultsList("Enter glyphs in 'Glyphs to check'")
			return

		# --- 2. OBTENER TOLERANCIA ---
		try:
			margin = float(tab.toleranceInput.get())
			print(f"Tolerance margin: {margin}")
		except:
			margin = 40.0
			print(f"Using default margin: {margin}")

		master = font.selectedFontMaster
		if not master:
			print("❌ No master selected")
			return
	
		mid = master.id
		print(f"Master ID: {mid}")

		# --- 3. FILTRAR GLIFOS VÁLIDOS ---
		excluded_extensions = [
			'.sc', '.dnom', '.numr', '.subs', '.sups', '.titl',
			'.case', '.comb', '.init', '.medi', '.fina', '.isol',
			'.liga', '.calt', '.locl', '.ss01', '.ss02', '.ss03',
			'.ss04', '.ss05', '.ss06', '.ss07', '.ss08', '.ss09',
			'.ss10', '.ss11', '.ss12', '.ss13', '.ss14', '.ss15',
			'.ss16', '.ss17', '.ss18', '.ss19', '.ss20'
		]

		def valid(name):
			return (
				name in font.glyphs and
				not any(ext in name for ext in excluded_extensions)
			)

		valid_left = [n for n in left_glyphs if valid(n)]
		valid_right = [n for n in right_glyphs if valid(n)]

		print(f"VALID left glyphs: {len(valid_left)}")
		print(f"VALID right glyphs: {len(valid_right)}")
		print(f"Valid left: {valid_left}")
		print(f"Valid right: {valid_right}")

		if not valid_left:
			print("❌ No valid glyphs in 'Only neighboring glyphs'")
			self.createEmptyResultsList("No valid glyphs in 'Only neighboring glyphs'")
			return
	
		if not valid_right:
			print("❌ No valid glyphs in 'Glyphs to check'")
			self.createEmptyResultsList("No valid glyphs in 'Glyphs to check'")
			return

		# --- 4. DETECTAR COLISIONES ---
		self.collisionPairs = []
		results_list = []
		seen = set()

		# Cache para rendimiento
		segCache, bboxCache, adv = {}, {}, {}

		def prepare(name):
			if name in segCache:
				return
			g = font.glyphs[name]
			layer = next(
				(l for l in g.layers if l.associatedMasterId == mid),
				g.layers[0]
			)
			try:
				layer = layer.copyDecomposedLayer()
			except:
				pass
			segCache[name] = getSegments(layer)
			bboxCache[name] = self.bboxCollision(layer)
			adv[name] = layer.width

		# Preparar todos los glifos
		for g in valid_left + valid_right:
			prepare(g)

		print(f"\n🔍 DETECTANDO COLISIONES (Neighbors → Glyphs to check)...")
	
		# Detectar colisiones: left (neighbors) → right (glyphs to check)
		for left_name in valid_left:
			print(f"  Checking {left_name} as LEFT...")
			L_layer = font.glyphs[left_name].layers[0].copyDecomposedLayer()
		
			for right_name in valid_right:
				if left_name == right_name:
					continue
			
				# Verificar bounding boxes
				if not self.boxesAreCloseCollision(bboxCache[left_name], bboxCache[right_name], margin):
					continue
			
				# Verificar colisión real
				R_layer = font.glyphs[right_name].layers[0].copyDecomposedLayer()
				dx = adv[left_name]
			
				if self.layersAreCloseCollision(L_layer, R_layer, dx, margin):
					key = (left_name, right_name)
					if key not in seen:
						seen.add(key)
					
						# Obtener contexto
						left_glyph = font.glyphs[left_name]
						right_glyph = font.glyphs[right_name]
						pre, suf = self.contextualPrefixSuffixCollision(left_glyph, right_glyph)
					
						self.collisionPairs.append((left_name, right_name, pre, suf))
						results_list.append(f"{left_name} / {right_name}")
						print(f"    ✅ COLLISION: {left_name} / {right_name}")

		print(f"\n📊 RESULTADOS: {len(results_list)} colisiones encontradas")
		print(f"DEBUG collisionPairs: {self.collisionPairs}")

		# --- 5. ACTUALIZAR UI ---
		self.clearCollisionList(reset_label=False)

		if results_list:
			self.createCollisionListWithCheckboxes(
				results_list,
				reset_label=False
			)
		
			tab.resultsLabel.set(
				f"Collisions found: {len(results_list)} (Neighbors → Glyphs to check)"
			)
		
			# Mostrar primera colisión en preview
			if self.collisionPairs:
				left, right, pre, suf = self.collisionPairs[0]
				self.currentCollisionPrefix = pre
				self.currentCollisionLeftGlyph = left
				self.currentCollisionRightGlyph = right
				self.currentCollisionSuffix = suf
				self.selectedCollisionIndex = 0
				self.updatePreviewCollision(pre, left, right, suf)
		else:
			self.createEmptyResultsList("No collisions found")
			tab.resultsLabel.set("Collisions found: 0")

		print("✔ USE completed (Neighbors → Glyphs to check)")
		print("=" * 80)
	
					
							
	# ===== MÉTODES DE CONSTRUCCIÓN DE UI =====
	
	def buildCollisionDetectorTab(self):
		"""Versión EXTREMADAMENTE SIMPLE sin ningún código complejo"""
		tab = self.w.tabs[0]
		y = 20
	
		# Solo crear los elementos básicos
		tab.glyphsLabel = TextBox((15, y, 120, 22), "Glyphs to check:")
		tab.glyphsInput = EditText((140, y, 200, 22), "A, T, V, L")
		y += 30
	
		tab.toleranceLabel = TextBox((15, y, 70, 22), "Tolerance:")
		tab.toleranceInput = EditText((90, y, 50, 22), "40")
		y += 30
	
		# ¡AHORA checkCollisionsCallback YA ESTÁ DEFINIDO!
		tab.checkButton = Button((15, y, 200, 24), "Check Collisions", callback=self.checkCollisionsCallback)
		y += 40
	
		# NUEVO: Campo "Only neighboring glyphs"
		tab.neighborsLabel = TextBox((15, y, 250, 22), "Only neighboring glyphs:")
		y += 25
	
		# ¡AHORA useSelectedCollisionCallback YA ESTÁ DEFINIDO!
		tab.useButton = Button(
			(300, y, 60, 22),
			"USE",
			callback=self.useSelectedCollisionCallback
		)
	
		tab.neighborsInput = TextEditor((15, y, 280, 60), 
									   "" )
		y += 70
	
		# MODIFICADO: Añadir variable para mostrar número de colisiones
		tab.resultsLabel = TextBox((15, y, 140, 22), "Collisions found: 0")
	
		tab.navUpButton = Button((180, y-2, 30, 24), "↑", callback=self.navigateUpCallback)
		tab.navDownButton = Button((215, y-2, 30, 24), "↓", callback=self.navigateDownCallback)
		tab.selectAllButton = Button((250, y-2, 100, 24), "Select All", callback=self.selectAllCallback)
	
		y += 25
	
		tab.resultsContainer = Group((15, y, 360, 180))
		y += 190
	
		tab.previewLabel = TextBox((15, y, 200, 22), "Preview & Zoom")
		y += 25
	
		tab.previewView = Group((15, y, 360, 150))
		y += 160
	
		tab.zoomSlider = Slider((15, y, 200, 22), minValue=5, maxValue=50, value=ZOOM_LEVEL, callback=self.onZoomChangeCallback)
		tab.zoomValue = TextBox((230, y, 40, 22), f"{ZOOM_LEVEL}%")
		y += 35
	
		tab.selectedPairsButton = Button((15, y, 170, 24), "List selected pairs in Tab", callback=self.listSelectedPairsCallback)
		tab.closeTabsButton = Button((195, y, 150, 24), "CLOSE ALL TABS", callback=self.closeAllTabsCollisionCallback)
		y += 40
	
		tab.positiveLabel = TextBox((15, y, 120, 22), "Positive Kerning")
		y += 25
	
		tab.marginLabel = TextBox((15, y, 50, 22), "Margin:")
		tab.marginInput = EditText((70, y, 50, 22), "40")
		tab.kernButton = Button((135, y, 100, 24), "Kern Tab", callback=self.kernTabCollisionCallback_REAL)
	
		# coordenades base (defineix-les abans)
		btnY = 691	# Ajustado por el nuevo campo
		btnH = 22

		# Botó #AV#
		tab.avButton = Button(
			(240, y+1, 45, btnH),
			"#AV#",
			callback=self.kernAutoCallback
		)

		# Botó X (tancar tab)
		tab.closeTabButton = Button(
			(340, y+1, 22, btnH),
			"X",
			callback=self.closeCurrentTabCallback
		)
		# NUEVO: Botón 🗑️# (eliminar todos los # del tab)
		tab.removeHashButton = Button(
			(290, y+1, 42, btnH),
			"🗑️#",
			callback=self.removeHashFromTabCallback
		)
	
		y += 35
	
		tab.hideButton = Button((15, y, 150, 24), "Hide existing pairs", callback=self.hideExistingPairsCollisionCallback)
		tab.removeButton = Button((180, y, 130, 24), "Remove tab kern", callback=self.removeTabKernCollisionCallback)
		y += 35
	
		tab.blockCheckbox = CheckBox( (15, y, -15, 20), "Hide existing pairs (After generate Tab)", value=False )
	
		tab.importJSONButton = Button(
			(15, y+25, 200, 24),
			"Import Kerning Pairs (JSON)",
			callback=self.loadJSONPairsCallback
		)
		y += 35
	
		tab.exportJSONButton = Button(
			(225, y-10, 110, 24),
			"Tab to JSON",
			callback=self.exportTabToJSONCallback
		)
		y += 35
	

	def addGlyphsToGlyphsInput(self, glyph_names):
		"""
		Afegeix glifs a glyphsInput:
		- sense duplicats
		- formatats amb coma + espai
		"""
		tab = self.w.tabs[0]
		edit = tab.glyphsInput

		if not edit:
			return

		# Glifs existents
		raw = edit.get() or ""
		existing = [g.strip() for g in raw.split(",") if g.strip()]

		# Afegir nous
		for g in glyph_names:
			if g not in existing:
				existing.append(g)

		# Reconstruir string
		edit.set(", ".join(existing))
	
	
	






	
	def createCollisionTabFromPairs(self, collisionPairs, masterName):
		"""
		Crea un tab nou amb els parells de col·lisió.
		Lista los pares en 4 columnas con 6 espacios de separación.
		"""
		font = Glyphs.font
		if not font:
			return

		master = font.selectedFontMaster
		if not master:
			return

		mid = master.id

		# -------------------------------------------------
		# VERIFICAR SI EL CHECKBOX "HIDE EXISTING PAIRS" ESTÁ SELECCIONADO
		# -------------------------------------------------
		try:
			tab = self.w.tabs[0]  # Collision Detector tab
			hide_existing = tab.blockCheckbox.get()
		except:
			hide_existing = False

		# -------------------------------------------------
		# OBTENER LOS GLIFOS ESPECIFICADOS EN "GLYPHS TO CHECK"
		# -------------------------------------------------
		try:
			glyphs_to_check_text = tab.glyphsInput.get()
			specified_glyphs = [g.strip() for g in glyphs_to_check_text.split(",") if g.strip()]
		except:
			print("🧪 DEBUG: No se pudo obtener glyphs to check")
			return

		if not specified_glyphs:
			print("⚠️ No hay glifos especificados en 'Glyphs to check'")
			return

		# -------------------------------------------------
		# FUNCIÓN PARA ESPACIAR TÍTULOS
		# -------------------------------------------------
		def space_title(text):
			"""Añade espacios entre caracteres para evitar pares kernables"""
			if not text.startswith('#'):
				return text
			# Separar cada carácter con un espacio
			return ' '.join(list(text))

		# -------------------------------------------------
		# FUNCIÓN PARA FORMATEAR BLOQUE DE TEXTO CON 5 ESPACIOS ANTES DEL PREFIJO
		# -------------------------------------------------
		def format_block_with_spaces(prefix, left, right, suffix):
			"""Formatea un bloque con exactamente 5 espacios antes del prefijo"""
			# 5 espacios en blanco antes del prefijo
			return f"     {prefix}/{left}/{right}{suffix}"

		# -------------------------------------------------
		# CREAR UN TAB PARA CADA GLIFO ESPECIFICADO
		# -------------------------------------------------
		tabs_created = 0

		for glyph_name in specified_glyphs:
			# Verificar que el glifo existe en la fuente
			if glyph_name not in font.glyphs:
				print(f"⚠️ Glyph '{glyph_name}' not found in font")
				continue

			# Recolectar todos los pares que contengan este glifo
			glyph_pairs = []
			for left, right, prefix, suffix in collisionPairs:
				if left == glyph_name or right == glyph_name:
					glyph_pairs.append((left, right, prefix, suffix))

			if not glyph_pairs:
				print(f"ℹ️ No pairs found for glyph '{glyph_name}'")
				continue

			# Filtrar si es necesario
			if hide_existing:
				filtered_pairs = []
				for left, right, prefix, suffix in glyph_pairs:
					if not self.hasKerning(font, mid, left, right):
						filtered_pairs.append((left, right, prefix, suffix))
			else:
				filtered_pairs = glyph_pairs

			if not filtered_pairs:
				print(f"ℹ️ All pairs for glyph '{glyph_name}' have existing kerning")
				continue

			# -------------------------------------------------
			# CREAR EL CONTENIDO DEL TAB - LISTA EN 4 COLUMNAS
			# -------------------------------------------------
			lines = []

			# Añadir título simple CON ESPACIOS
			title1 = f"# {glyph_name} - {len(filtered_pairs)} pares"
			title2 = f"# Master: {masterName}"

			lines.append(space_title(title1))
			lines.append(space_title(title2))
			lines.append("")

			# Convertir todos los pares a strings CON 5 ESPACIOS ANTES DEL PREFIJO
			all_pair_strings = []
			for left, right, prefix, suffix in filtered_pairs:
				# Usar la función de formateo con 5 espacios
				pair_string = format_block_with_spaces('/'.join(prefix), left, right, '/'.join(suffix))
				all_pair_strings.append(pair_string)

			# Organizar en 4 columnas
			num_columns = 4

			# Calcular cuántas filas necesitamos
			num_pairs = len(all_pair_strings)
			rows_needed = (num_pairs + num_columns - 1) // num_columns

			# Organizar los pares por columnas
			columns = []
			for col in range(num_columns):
				column_items = []
				for row in range(rows_needed):
					index = row * num_columns + col
					if index < num_pairs:
						column_items.append(all_pair_strings[index])
				columns.append(column_items)

			# Calcular el ancho máximo para cada columna
			column_width = []
			for col in range(num_columns):
				max_width = 0
				for item in columns[col]:
					if len(item) > max_width:
						max_width = len(item)
				column_width.append(max_width)

			# Crear las filas con 6 espacios entre columnas
			for row in range(rows_needed):
				row_items = []
				for col in range(num_columns):
					if row < len(columns[col]):
						item = columns[col][row]
						# Añadir espacios para alinear
						padding = column_width[col] - len(item)
						aligned_item = item + (" " * padding)
						row_items.append(aligned_item)
					else:
						# Espacio vacío para mantener la alineación
						row_items.append(" " * column_width[col])

				# Unir columnas con 6 espacios
				line = "      ".join(row_items).rstrip()
				if line.strip():  # Solo añadir líneas no vacías
					lines.append(line)

			tab_content = "\n".join(lines)

			# Crear el tab
			font.newTab(tab_content)
			tabs_created += 1

			print(f"✅ Created tab for {glyph_name} with {len(filtered_pairs)} pairs in 4 columns")
			print(f"   Cada bloque tiene 5 espacios antes del prefijo")

		# Mensaje final
		if tabs_created > 0:
			Glyphs.showNotification(
				"Tabs Created",
				f"Created {tabs_created} tab(s) for specified glyphs\n"
				f"Pairs listed in 4 columns with 5-space padding"
			)
		else:
			Glyphs.showNotification(
				"No Tabs",
				"No pairs found for specified glyphs"
			)
	
	
	def spaceOutHeaderLines(text):
		"""
		Afegeix espais entre lletres a les línies que són capçaleres,
		però NO toca les línies de parelles de kerning que comencen
		amb '/H/H/'.
		"""
		lines = text.splitlines(keepends=True)
		newlines = []

		for line in lines:
			stripped = line.lstrip()

			# Excluir expresamente las líneas de pares del Tools tab
			if stripped.startswith("/H/H/"):
				newlines.append(line)
				continue

			# Aquí decides qué consideras “header”.
			# Ejemplo: cualquier línea que empiece por "/" pero no sea /H/H/
			if stripped.startswith("/"):
				base_indent = line[:len(line) - len(stripped)]
				core = stripped.rstrip("\r\n")
				# Espaciar cada carácter de la cabecera
				spaced = " ".join(list(core))
				newline = base_indent + spaced + "\n"
				newlines.append(newline)
			else:
				newlines.append(line)

		return "".join(newlines)


	
	def buildToolsTab(self):
		tab = self.w.tabs[1]
		y = 10

		# --- Kerning Groups ---
		tab.groupsInfo = TextBox(
			(15, y, -15, 40),
			"Kerning Groups Manager: Click 'Check' to analyze",
			sizeStyle="small"
		)
		y += 45

		tab.checkGroupsButton = Button(
			(15, y-20, 150, 28),
			"Check Kerning Groups",
			callback=self.checkGroupsCallback
		)

		tab.fillGroupsButton = Button(
			(180, y-20, 150, 28),
			"Fill Empty Groups",
			callback=self.fillEmptyGroupsCallback
		)
		y += 40

		# --- Delete Kern Groups ---
		tab.deleteGroupsButton = Button(
			(15, y-25, 150, 28),
			"Delete Kern Groups",
			callback=self.deleteAllKerningGroupsCallback
		)
		y += 40

		tab.separator1 = HorizontalLine((10, y-25, -10, 1))
		y += 15

		# --- Test Words ---
		tab.testWordsLabel = TextBox((10, y-25, 100, 20), "Test Words")
		y += 25

		tab.testWordsPopup = PopUpButton(
			(95, y-52, 115, 24),
			list(self.TEST_WORDS_COLLECTIONS.keys())
		)
		y += 30

		tab.testWordsButton = Button(
			(220, y-87, 140, 28),
			"> Insert Test Words",
			callback=self.insertTestWordsCallback
		)
		y += 45

		# --- Kern Pairs ---
		tab.separatorKernPairs = HorizontalLine((10, y-95, -10, 1))
		y += 15

		tab.kernPairsLabel = TextBox((15, y-100, 150, 20), "List All Kern Pairs")
		y += 22

		


		# --- Prefix / Suffix ---
		tab.prefixLabel = TextBox((145, y-92, 50, 20), "Prefix:")
		tab.prefixInput = EditText((190, y-95, 50, 22), "HH")

		tab.suffixLabel = TextBox((248, y-92, 50, 20), "Suffix:")
		tab.suffixInput = EditText((295, y-95, 50, 22), "HH")
		y += 32

		tab.kernPairsPerLabel = TextBox((15, y-125, 70, 20), "Pairs/Tab:")
		tab.kernPairsPerInput = EditText((80, y-125, 50, 22), "50")

		tab.listAllKernPairsButton = Button(
			(15, y-95, -15, 28),
			"List All Kern Pairs",
			callback=self.listAllKernPairsCallback
		)
		y += 45

		tab.separatorKernAllPairs = HorizontalLine((10, y-100, -10, 1))
		y += 20

		# ===============================
		# 🔧 KERN SCALE (NOU – CORREGIT)
		# ===============================

		tab.percentLabel = TextBox(
			(15, y-79, 120, 22),
			"Percentage:"
		)
		y += 35

		tab.modeLabel = TextBox(
			(170, y-115, 120, 22),
			"Operation:"
		)
		tab.modePopup = PopUpButton(
			(250, y-113, 100, 22),
			["Increase","Decrease"]
		)
		y += 40

		tab.marginInput = EditText(
			(100, y-155, 50, 22),
			"40"
		)

		tab.separatorScaleKern = HorizontalLine((10, y-85, -10, 1))
	
		tab.applyButton = Button(
			(15, y-160 + 35, -15, 28),
			"Apply to Active Master",
			callback=self.applyCallback
		)
		tab.kernScale = TextBox((15, y-185, 290, 20), "Scale Kern by percentage in current master"
		)
		y += 35

		# ===============================
		# 🔍 KERNING PAIRS LISTER (INTEGRADO)
		# ===============================

	
		tab.listerLabel = TextBox((15, y-110, 200, 20), "Kerning Pairs Lister")
		y += 25
	
		# Controles del listador - CORREGIDO: Usar los nombres correctos de los métodos
		tab.showPairsBtn = Button((190, y-135, 80, 24), "Show", callback=self.showSelectedPairsTurbo)
		tab.refreshPairsBtn = Button((280, y-135, 80, 24), "Refresh", callback=self.refreshPairsList)
	
		tab.searchPairs = EditText((15, y-105, 250, 24), placeholder="Search… A, = exact", callback=self.filterPairsList)
		tab.clearSearchBtn = Button((275, y-105, 80, 24), "Clear", callback=self.clearPairsSearch)
	
		# Lista de pares (ocupará el resto del espacio disponible)
		tab.pairsList = List(
			(15, y-70, 350, -40),
			[],
			columnDescriptions=[
				{"title": "Left", "width": 130},
				{"title": "Right", "width": 130}, 
				{"title": "Value", "width": 60},
			],
			allowsMultipleSelection=True,
			enableTypingSensitivity=False,
			selectionCallback=None,	 # No acción en selección simple
			doubleClickCallback=self.showSelectedPairsTurbo	 # Acción solo en doble clic
		)
	
		# Nuevos campos de Prefix/Suffix personalizados
		y_list_end = y - 70 + 180  # Fin de la lista
	
		tab.customPrefixLabel = TextBox((15, y+285 + 15, 60, 22), "Prefix:")
		tab.customPrefixInput = EditText((75, y+285 + 15, 80, 22), "HH")
	
		tab.customSuffixLabel = TextBox((165, y+285 + 15, 60, 22), "Suffix:")
		tab.customSuffixInput = EditText((225, y+285 + 15, 80, 22), "HH")


	
		# Gestor de grupos (lado derecho)
		tab.groupsTabs = Tabs((380, y-140, -15, 150), ["Left Group", "Right Group"])
		tab.groupsTabs[0].list = List((10, 10, -10, -10), [])
		tab.groupsTabs[1].list = List((10, 10, -10, -10), [])
	
		# Botones del gestor de grupos - CORREGIDO: Usar los nombres correctos
		tab.makeFirstBtn = Button((380, y+15, 120, 24), "Make First", callback=self.makeFirstGroup)
		tab.applyOrderBtn = Button((510, y+15, 120, 24), "Apply Order", callback=self.applyGroupOrder)
		tab.refreshGroupsBtn = Button((640, y+15, 100, 24), "Refresh", callback=self.refreshGroupManager)
	
		# Inicializar variables para el listador
		self._allPairs = []
		self._currentDisplayPairs = []
		self._kerningCache = {}
		self._keyCache = {}
		self._productionCache = {}
		self._graphicalCache = {}
		self._groupCache = {}

						
	def applyCustomContextCallback(self, sender):
			"""Aplica el contexto personalizado a los pares seleccionados"""
			font = Glyphs.font
			if not font:
				return
	
			tab = self.w.tabs[1]
	
			# Obtener valores personalizados
			custom_prefix = tab.customPrefixInput.get().strip()
			custom_suffix = tab.customSuffixInput.get().strip()
	
			if not custom_prefix and not custom_suffix:
				Message("No custom values", "Enter prefix and/or suffix values.", OKButton="OK")
				return
	
			# Obtener pares seleccionados
			sel = tab.pairsList.getSelection()
			if not sel:
				Message("No selection", "Please select one or more pairs from the list.", OKButton="OK")
				return
	
			rows = self._currentDisplayPairsTurbo
			lines = []
	
			for i in sel:
				if i < len(rows):
					row = rows[i]
					if row.get("Left") == "────" and row.get("Right") == "────":
						continue
			
					original_data = row.get("_originalData", row)
					left = str(original_data.get("_productionLeft", row["Left"])).strip()
					right = str(original_data.get("_productionRight", row["Right"])).strip()
					value = original_data.get("Value", row["Value"])
			
					# Crear línea con contexto personalizado
					prefix = custom_prefix if custom_prefix else "HH"
					suffix = custom_suffix if custom_suffix else "HH"
			
					# Convertir a formato /H/H/ si es necesario
					if '/' not in prefix:
						prefix = '/'.join(['/' + c for c in prefix]).lstrip('/')
					if '/' not in suffix:
						suffix = '/'.join(['/' + c for c in suffix]).lstrip('/')
			
					line = f"/{prefix}/{left}/{right}/{suffix} {value}"
					lines.append(line)
	
			if lines:
				tab_content = "\n".join(lines)
				Glyphs.font.newTab(tab_content)
				Message(f"Tab created", f"Created tab with {len(lines)} pair(s) using custom context.", OKButton="OK")
				
				

	def updateCustomPrefixSuffix(self, sender):
		"""Actualiza los valores de prefix/suffix personalizados"""
		tab = self.w.tabs[1]
	
		# Almacenar los valores en variables de instancia
		self.custom_prefix = tab.customPrefixInput.get().strip()
		self.custom_suffix = tab.customSuffixInput.get().strip()
	
		print(f"🧪 Custom Prefix/Suffix updated: '{self.custom_prefix}' / '{self.custom_suffix}'")
																
																																				
	def deleteAllKerningGroupsCallback(self, sender):
		"""Elimina TODOS los grupos de kerning de la fuente con confirmación"""
		print("\n" + "=" * 80)
		print("🧪 DEBUG — ELIMINAR TODOS LOS GRUPOS DE KERNING")
		print("=" * 80)
	
		font = Glyphs.font
		if not font:
			print("❌ No hay fuente abierta")
			Message(
				"Error",
				"No font open. Please open a font first.",
				OKButton="OK"
			)
			return
	
		# Contar grupos actuales
		left_groups = set()
		right_groups = set()
	
		for glyph in font.glyphs:
			if glyph.leftKerningGroup:
				left_groups.add(glyph.leftKerningGroup)
			if glyph.rightKerningGroup:
				right_groups.add(glyph.rightKerningGroup)
	
		total_groups = len(left_groups) + len(right_groups)
		glyphs_with_groups = sum(1 for g in font.glyphs if g.leftKerningGroup or g.rightKerningGroup)
	
		print(f"📊 Estadísticas actuales:")
		print(f"  • Grupos izquierdos únicos: {len(left_groups)}")
		print(f"  • Grupos derechos únicos: {len(right_groups)}")
		print(f"  • Total grupos: {total_groups}")
		print(f"  • Glifos con grupos: {glyphs_with_groups}/{len(font.glyphs)}")
	
		if total_groups == 0:
			print("ℹ️ La fuente no tiene grupos de kerning")
			Message(
				"No Kerning Groups",
				"The font doesn't have any kerning groups to delete.",
				OKButton="OK"
			)
			return
	
		# Crear ventana de confirmación
		alert = NSAlert.alloc().init()
	
		# Título y mensaje
		alert.setMessageText_("⚠️ DELETE ALL KERNING GROUPS")
		alert.setInformativeText_(
			f"This will delete ALL kerning groups from the font.\n\n"
			f"• Unique left groups: {len(left_groups)}\n"
			f"• Unique right groups: {len(right_groups)}\n"
			f"• Total groups: {total_groups}\n"
			f"• Glyphs affected: {glyphs_with_groups}\n\n"
			f"This action CANNOT be undone!\n"
			f"Make sure you have a backup."
		)
	
		# Botones (Cancelar por defecto)
		alert.addButtonWithTitle_("Cancel")
		delete_button = alert.addButtonWithTitle_("DELETE ALL GROUPS")
	
		# Estilo de alerta (advertencia)
		alert.setAlertStyle_(NSWarningAlertStyle)
	
		# Cambiar color del botón DELETE a rojo (opcional)
		try:
			# En macOS podemos intentar cambiar el color del botón
			delete_button_key = delete_button.key()
			if hasattr(delete_button, 'cell'):
				delete_button.cell().setBackgroundColor_(NSColor.redColor())
		except:
			pass
	
		# Mostrar alerta y esperar respuesta
		response = alert.runModal()
	
		# NSAlertFirstButtonReturn = Cancel (porque se añadió primero)
		# NSAlertSecondButtonReturn = DELETE ALL GROUPS
		if response != NSAlertSecondButtonReturn:  # 1001
			print("❌ Operación cancelada por el usuario")
			return
	
		print("🧨 Eliminando todos los grupos de kerning...")
	
		# Contadores para estadísticas
		left_removed = 0
		right_removed = 0
	
		# Eliminar grupos de todos los glifos
		for glyph in font.glyphs:
			if glyph.leftKerningGroup:
				glyph.leftKerningGroup = None
				left_removed += 1
		
			if glyph.rightKerningGroup:
				glyph.rightKerningGroup = None
				right_removed += 1
	
		# También limpiar el kerning que depende de grupos
		# (esto es opcional, depende de si quieres mantener el kerning existente)
		masters_affected = 0
		kerning_entries_removed = 0
	
		for master in font.masters:
			master_id = master.id
			if master_id in font.kerning:
				kerning_dict = font.kerning[master_id]
			
				# Crear copia de las claves para iterar
				keys_to_remove = []
			
				for left_key in list(kerning_dict.keys()):
					if isinstance(left_key, str) and left_key.startswith('@MMK_'):
						keys_to_remove.append(left_key)
			
				# Eliminar entradas de kerning por grupos
				for left_key in keys_to_remove:
					kerning_entries_removed += len(kerning_dict[left_key])
					del kerning_dict[left_key]
			
				masters_affected += 1
	
		print(f"✅ Eliminación completada:")
		print(f"  • Grupos izquierdos eliminados: {left_removed}")
		print(f"  • Grupos derechos eliminados: {right_removed}")
		print(f"  • Masters afectados: {masters_affected}")
		print(f"  • Entradas de kerning eliminadas: {kerning_entries_removed}")
	
		# Actualizar la UI del tab Tools
		self.updateGroupsInfoAfterDeletion()
	
		# Mostrar notificación de éxito
		Glyphs.showNotification(
			"Kerning Groups Deleted",
			f"Deleted {total_groups} kerning groups:\n"
			f"• {left_removed} left groups\n"
			f"• {right_removed} right groups\n"
			f"• {kerning_entries_removed} kerning entries removed"
		)
	
		print("=" * 80)

	def updateGroupsInfoAfterDeletion(self):
		"""Actualiza la información de grupos después de la eliminación"""
		font = Glyphs.font
		if not font:
			return
	
		# Contar grupos restantes (debería ser 0)
		remaining_left = sum(1 for g in font.glyphs if g.leftKerningGroup)
		remaining_right = sum(1 for g in font.glyphs if g.rightKerningGroup)
		total_remaining = remaining_left + remaining_right
	
		# Actualizar el texto en el tab Tools
		tab = self.w.tabs[1]
	
		if total_remaining == 0:
			message = "✅ ALL kerning groups have been deleted.\n"
			message += f"Glyphs with groups: 0/{len(font.glyphs)}"
		else:
			message = f"⚠️ Some groups remain:\n"
			message += f"Left groups: {remaining_left}\n"
			message += f"Right groups: {remaining_right}\n"
			message += f"Total remaining: {total_remaining}"
	
		tab.groupsInfo.set(message)
	
		print(f"🧪 UI actualizada: {total_remaining} grupos restantes")
		
		
		
	def kernTabCollisionCallback_REAL(self, sender):
		print("\n" + "=" * 80)
		print("🧪 DEBUG — KERN TAB (GENÈRIC)")
		print("=" * 80)

		font = Glyphs.font
		print("Font:", font)
		if not font:
			print("❌ No font")
			return

		tab = font.currentTab
		print("Tab:", tab)
		if not tab:
			print("❌ No tab")
			return

		if not hasattr(tab, "layers"):
			print("❌ Tab has no layers")
			return

		print(f"📄 TAB TEXT: {repr(tab.text)}")
		print(f"📐 Layers count: {len(tab.layers)}")

		# --- mostrar layers i glifs ---
		glyph_names = []
		for i, layer in enumerate(tab.layers):
			if layer and layer.parent:
				name = layer.parent.name
				glyph_names.append(name)
				print(f"  [{i}] glyph = {name}")
			else:
				print(f"  [{i}] layer buit / None")

		if len(glyph_names) < 2:
			print("⚠️ Menys de 2 glifs → res a kernar")
			return

		# --- obtenir parells ---
		print("\n🔍 OBTENINT PARELLS...")
		pairs = self.get_pairs_from_tab(tab)

		print(f"🔗 PARELLS DETECTATS: {len(pairs)}")
		for i, (l, r) in enumerate(pairs):
			print(f"   {i:02d}: {l} / {r}")

		if not pairs:
			print("❌ get_pairs_from_tab ha retornat cap parell")
			return

		# --- aplicar kerning ---
		print("\n🧮 APLICANT KERNING...")
		self.apply_kerning_to_pairs(pairs)

		print("✅ KERN TAB FINALITZAT")
		print("=" * 80)




		
		
	def useSelectedCollisionCallback(self, sender):
		print("\n" + "=" * 80)
		print("🧪 USE = Detectar colisiones BIDIRECCIONALES entre NEIGHBORS y GLYPHS TO CHECK")
		print("=" * 80)

		tab = self.w.tabs[0]
		font = Glyphs.font
		if not font:
			print("❌ No font open")
			return

		# --- 1. OBTENER LISTAS DE AMBOS CAMPOS ---
		# Glyphs to check
		glyphs_to_check_text = tab.glyphsInput.get()
		names = [g.strip() for g in glyphs_to_check_text.split(",") if g.strip()]
	
		# Only neighboring glyphs
		neighbors_text = tab.neighborsInput.get()
		neighbor_names = []
	
		if neighbors_text and neighbors_text.strip():
			lines = neighbors_text.split('\n')
			for line in lines:
				line_names = [n.strip() for n in line.split(",") if n.strip()]
				neighbor_names.extend(line_names)

		print(f"🧪 Glyphs to check: {names}")
		print(f"🧪 Neighbor glyphs: {neighbor_names}")

		if not names:
			print("❌ No glyphs in 'Glyphs to check'")
			self.createEmptyResultsList("Enter glyphs in 'Glyphs to check'")
			return
	
		if not neighbor_names:
			print("❌ No glyphs in 'Only neighboring glyphs'")
			self.createEmptyResultsList("Enter glyphs in 'Only neighboring glyphs'")
			return

		# --- 2. OBTENER TOLERANCIA ---
		try:
			margin = float(tab.toleranceInput.get())
			print(f"🧪 Tolerance margin: {margin}")
		except:
			margin = 40.0
			print(f"🧪 Using default margin: {margin}")

		master = font.selectedFontMaster
		if not master:
			print("❌ No master selected")
			return
	
		mid = master.id
		print(f"🧪 Master ID: {mid}")

		# --- 3. FILTRAR GLIFOS VÁLIDOS (más permisivo) ---
		excluded_extensions = [
			'.dnom', '.numr', '.subs', '.sups', '.titl',
			'.case', '.comb', '.init', '.medi', '.fina', '.isol',
			'.liga', '.calt', '.locl'
		]
	
		# NO excluir .sc para small caps
		# Mantener solo exclusiones realmente problemáticas

		def valid(name):
			if name not in font.glyphs:
				print(f"⚠️ Glyph '{name}' not found in font")
				return False
		
			# Solo excluir extensiones que realmente causan problemas
			for ext in excluded_extensions:
				if ext in name:
					print(f"⚠️ Skipping glyph with extension '{ext}': {name}")
					return False
		
			return True

		# Filtrar ambas listas
		valid_names = [n for n in names if valid(n)]
		valid_neighbors = [n for n in neighbor_names if valid(n)]

		print(f"🧪 VALID Glyphs to check: {len(valid_names)}")
		print(f"🧪 VALID Neighbor glyphs: {len(valid_neighbors)}")
		print(f"🧪 Valid names: {valid_names}")
		print(f"🧪 Valid neighbors: {valid_neighbors}")

		if not valid_names:
			print("❌ No valid glyphs in 'Glyphs to check'")
			self.createEmptyResultsList("No valid glyphs in 'Glyphs to check'")
			return
	
		if not valid_neighbors:
			print("❌ No valid glyphs in 'Only neighboring glyphs'")
			self.createEmptyResultsList("No valid glyphs in 'Only neighboring glyphs'")
			return

		# --- 4. DETECTAR COLISIONES BIDIRECCIONALES ---
		self.collisionPairs = []
		results_list = []
		seen = set()

		# Cache para rendimiento (igual que en checkCollisionsCallback)
		segCache, bboxCache, adv = {}, {}, {}

		print(f"🧪 Preparing glyphs...")
		for name in valid_names + valid_neighbors:
			if name in segCache:
				continue
			
			g = font.glyphs[name]
			layer = None
			for l in g.layers:
				if l.associatedMasterId == mid:
					layer = l
					break
			if not layer and g.layers:
				layer = g.layers[0]
		
			if layer:
				try:
					layer_copy = layer.copyDecomposedLayer()
				except Exception as e:
					layer_copy = layer
					print(f"🧪 Using original layer for {name}: {e}")
			
				segCache[name] = getSegments(layer_copy)
				bboxCache[name] = self.bboxCollision(layer_copy)
				adv[name] = layer_copy.width
				print(f"🧪 Prepared {name}: width={layer_copy.width}")

		print(f"\n🔍 DETECTANDO COLISIONES BIDIRECCIONALES...")
	
		# DIRECCIÓN 1: Neighbors (left) → Glyphs to check (right)
		print(f"🧪 DIRECCIÓN 1: Neighbors → Glyphs to check")
		for left_name in valid_neighbors:
			print(f"  Checking {left_name} as LEFT...")
			L = None
			left_glyph = font.glyphs[left_name]
			for l in left_glyph.layers:
				if l.associatedMasterId == mid:
					L = l
					break
			if not L and left_glyph.layers:
				L = left_glyph.layers[0]
		
			if not L:
				continue
		
			try:
				L = L.copyDecomposedLayer()
			except Exception:
				pass
		
			for right_name in valid_names:
				if left_name == right_name:
					continue
			
				# Verificar bounding boxes primero (más rápido)
				if not self.boxesAreCloseCollision(bboxCache[left_name], bboxCache[right_name], margin):
					continue
			
				dx = adv[left_name]
			
				# Obtener capa derecha
				R = None
				right_glyph = font.glyphs[right_name]
				for l in right_glyph.layers:
					if l.associatedMasterId == mid:
						R = l
						break
				if not R and right_glyph.layers:
					R = right_glyph.layers[0]
			
				if not R:
					continue
			
				try:
					R = R.copyDecomposedLayer()
				except Exception:
					pass
			
				# Verificar colisión real
				if self.layersAreCloseCollision(L, R, dx, margin):
					key = (left_name, right_name)
					if key not in seen:
						seen.add(key)
					
						# Obtener contexto
						pre, suf = self.contextualPrefixSuffixCollision(left_glyph, right_glyph)
					
						self.collisionPairs.append((left_name, right_name, pre, suf))
						results_list.append(f"{left_name} / {right_name}")
						print(f"    ✅ COLLISION: {left_name} / {right_name}")

		# DIRECCIÓN 2: Glyphs to check (left) → Neighbors (right)
		print(f"\n🧪 DIRECCIÓN 2: Glyphs to check → Neighbors")
		for left_name in valid_names:
			print(f"  Checking {left_name} as LEFT...")
			L = None
			left_glyph = font.glyphs[left_name]
			for l in left_glyph.layers:
				if l.associatedMasterId == mid:
					L = l
					break
			if not L and left_glyph.layers:
				L = left_glyph.layers[0]
		
			if not L:
				continue
		
			try:
				L = L.copyDecomposedLayer()
			except Exception:
				pass
		
			for right_name in valid_neighbors:
				if left_name == right_name:
					continue
			
				# Verificar bounding boxes primero
				if not self.boxesAreCloseCollision(bboxCache[left_name], bboxCache[right_name], margin):
					continue
			
				dx = adv[left_name]
			
				# Obtener capa derecha
				R = None
				right_glyph = font.glyphs[right_name]
				for l in right_glyph.layers:
					if l.associatedMasterId == mid:
						R = l
						break
				if not R and right_glyph.layers:
					R = right_glyph.layers[0]
			
				if not R:
					continue
			
				try:
					R = R.copyDecomposedLayer()
				except Exception:
					pass
			
				# Verificar colisión real
				if self.layersAreCloseCollision(L, R, dx, margin):
					key = (left_name, right_name)
					if key not in seen:
						seen.add(key)
					
						# Obtener contexto
						pre, suf = self.contextualPrefixSuffixCollision(left_glyph, right_glyph)
					
						self.collisionPairs.append((left_name, right_name, pre, suf))
						results_list.append(f"{left_name} / {right_name}")
						print(f"    ✅ COLLISION: {left_name} / {right_name}")

		print(f"\n📊 RESULTADOS: {len(results_list)} colisiones encontradas")
		print(f"🧪 Collision pairs: {self.collisionPairs}")

		# --- 5. ACTUALIZAR UI ---
		self.clearCollisionList(reset_label=False)

		if results_list:
			self.createCollisionListWithCheckboxes(
				results_list,
				reset_label=False
			)
		
			tab.resultsLabel.set(
				f"Collisions found: {len(results_list)} (Bidirectional Neighbors ↔ Glyphs to check)"
			)
		
			# Mostrar primera colisión en preview
			if self.collisionPairs:
				left, right, pre, suf = self.collisionPairs[0]
				self.currentCollisionPrefix = pre
				self.currentCollisionLeftGlyph = left
				self.currentCollisionRightGlyph = right
				self.currentCollisionSuffix = suf
				self.selectedCollisionIndex = 0
				self.updatePreviewCollision(pre, left, right, suf)
		else:
			self.createEmptyResultsList("No collisions found")
			tab.resultsLabel.set("Collisions found: 0")

		print("✔ USE completed (Bidirectional detection)")
		print("=" * 80)

		
	
	def navigateUpCallback(self, sender):
		"""Callback per a botó fletxa amunt"""
		self.navigateCollisionList(-1)

	def navigateDownCallback(self, sender):
		"""Callback per a botó fletxa avall"""
		self.navigateCollisionList(1)
		
	# ===== MÉTODES DE COL·LISIÓ DETECTOR =====

	def createEmptyPreviewCollision(self):
		"""Crea una previsualització buida inicial con mensaje centrado"""
		tab = self.w.tabs[0]  # Collision Detector es ahora la primera pestaña
		previewView = tab.previewView.getNSView()
		
		# Limpiar vista previa
		for subview in previewView.subviews():
			subview.removeFromSuperview()
		
		# Crear imagen con fondo blanco y mensaje
		emptyImage = NSImage.alloc().initWithSize_(NSSize(360, 150))
		emptyImage.lockFocus()
		
		# Fondo blanco
		NSColor.whiteColor().set()
		NSBezierPath.fillRect_(NSMakeRect(0, 0, 360, 150))
		
		# Dibujar borde sutil
		border_path = NSBezierPath.bezierPathWithRect_(NSMakeRect(5, 5, 350, 140))
		NSColor.colorWithCalibratedRed_green_blue_alpha_(0.8, 0.8, 0.8, 1.0).set()
		border_path.setLineWidth_(1.0)
		border_path.stroke()
		
		# Texto centrado
		font = NSFont.systemFontOfSize_(12)
		attrs = {
			NSFontAttributeName: font,
			NSForegroundColorAttributeName: NSColor.grayColor()
		}
		msg = "Click 'Check Collisions' to start"
		attrString = NSAttributedString.alloc().initWithString_attributes_(msg, attrs)
		stringSize = attrString.size()
		attrString.drawAtPoint_(NSMakePoint(
			(360 - stringSize.width) / 2,
			(150 - stringSize.height) / 2
		))
		
		emptyImage.unlockFocus()
		
		imageView = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 150))
		imageView.setImage_(emptyImage)
		imageView.setImageScaling_(NSImageScaleProportionallyUpOrDown)
		previewView.addSubview_(imageView)
	
	def updateRowBackgroundColor(self, rowIndex, state):
		"""Actualitza el color de fons d'una fila
		state pot ser: 
		- False: no seleccionat
		- True: checkbox seleccionat
		- 'navigate': highlight de navegació (però checkbox no seleccionat)
		"""
		if rowIndex in self.collisionStates:
			background = self.collisionStates[rowIndex].get('background')
			if background and background.layer():
				if state == True and self.collisionStates[rowIndex]['checked']:
					# Color quan el checkbox està seleccionat (blau clar)
					color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0.95, 1.0, 0.7)
					background.layer().setBackgroundColor_(color.CGColor())
					label = self.collisionStates[rowIndex].get('label')
					if label:
						label.setTextColor_(NSColor.blackColor())
				elif state == 'navigate' or (state == True and not self.collisionStates[rowIndex]['checked']):
					# Color per a navegació (groc clar) - només highlight visual
					color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.95, 0.8, 0.5)
					background.layer().setBackgroundColor_(color.CGColor())
					label = self.collisionStates[rowIndex].get('label')
					if label:
						label.setTextColor_(NSColor.blackColor())
				else:
					# Color normal (transparent)
					background.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
					label = self.collisionStates[rowIndex].get('label')
					if label:
						label.setTextColor_(NSColor.blackColor())
													
	def navigateCollisionList(self, direction):
		"""Navegar per la llista de col·lisions amb fletxes - NOMÉS PER A NAVEGACIÓ"""
		if not self.collisionStates or len(self.collisionStates) == 0:
			return
		
		# Calcular nou índex
		if self.selectedCollisionIndex == -1:
			new_index = 0 if direction > 0 else len(self.collisionStates) - 1
		else:
			new_index = self.selectedCollisionIndex + direction
		
		# Assegurar que l'índex estigui dins dels líApache2s
		if new_index < 0:
			new_index = len(self.collisionStates) - 1
		elif new_index >= len(self.collisionStates):
			new_index = 0
		
		# NO deseleccionar checkboxes en navegar, només canviar el highlight visual
		# Treure highlight de l'anterior
		if self.selectedCollisionIndex != -1 and self.selectedCollisionIndex in self.collisionStates:
			self.updateRowBackgroundColor(self.selectedCollisionIndex, self.collisionStates[self.selectedCollisionIndex]['checked'])
		
		# Afegir highlight al nou (però NO canviar l'estat del checkbox)
		if new_index in self.collisionStates:
			# Només canviar el color de fons per a indicar navegació
			self.updateRowBackgroundColor(new_index, True)	# True per a highlight especial de navegació
			
			# Actualitzar previsualització si hi ha un parell corresponent
			if new_index < len(self.collisionPairs):
				left, right, pre, suf = self.collisionPairs[new_index]
				self.currentCollisionPrefix = pre
				self.currentCollisionLeftGlyph = left
				self.currentCollisionRightGlyph = right
				self.currentCollisionSuffix = suf
				self.updatePreviewCollision(pre, left, right, suf)
			
			self.selectedCollisionIndex = new_index
			
			# Fer scroll perquè la fila seleccionada sigui visible
			self.scrollToSelectedRow(new_index)
			
	
	def scrollToSelectedRow(self, rowIndex):
		"""Fer scroll perquè la fila seleccionada sigui visible"""
		try:
			tab = self.w.tabs[0]
			containerView = tab.resultsContainer.getNSView()
			
			for subview in containerView.subviews():
				if isinstance(subview, NSScrollView):
					scrollView = subview
					contentView = scrollView.documentView()
					
					rowHeight = 24
					rowY = self.collisionContentHeight - (rowIndex + 1) * rowHeight
					
					visibleRect = scrollView.contentView().bounds()
					
					if rowY < visibleRect.origin.y or rowY + rowHeight > visibleRect.origin.y + visibleRect.size.height:
						newOrigin = NSPoint(0, rowY - (visibleRect.size.height - rowHeight) / 2)
						if newOrigin.y < 0:
							newOrigin.y = 0
						elif newOrigin.y > contentView.bounds().size.height - visibleRect.size.height:
							newOrigin.y = contentView.bounds().size.height - visibleRect.size.height
						
						contentView.scrollPoint_(newOrigin)
					break
		except Exception as e:
			pass  # Mode silenciós

	def getDecomposedLayerCollision(self, glyph):
		"""Obté capa descomposta per al Collision Detector"""
		font = Glyphs.font
		if not font or not glyph:
			return None
		
		master = font.selectedFontMaster
		layer = None
		
		for l in glyph.layers:
			if l.associatedMasterId == master.id:
				layer = l
				break
		
		if not layer and glyph.layers:
			layer = glyph.layers[0]
		
		if not layer:
			return None
		
		try:
			if hasattr(layer, 'components') and layer.components:
				return layer.copyDecomposedLayer()
			else:
				return layer
		except Exception as e:
			return layer

	def updatePreviewCollision(self, prefix, leftGlyphName, rightGlyphName, suffix):
		"""Actualitza la previsualització amb nous dades"""
		previewImage = self.createPreviewImageCollision(prefix, leftGlyphName, rightGlyphName, suffix)
		
		if not previewImage:
			return
		
		tab = self.w.tabs[0]
		previewView = tab.previewView.getNSView()  # Canviat
		
		for subview in previewView.subviews():
			subview.removeFromSuperview()
		
		imageView = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 150))
		imageView.setImage_(previewImage)
		imageView.setImageScaling_(NSImageScaleProportionallyUpOrDown)
		previewView.addSubview_(imageView)

	def onZoomChangeCallback(self, sender):
		"""Quan es canvia el slider de zoom"""
		zoom_value = sender.get()
		self.zoomLevelCollision = zoom_value / 100.0
		tab = self.w.tabs[0]
		tab.zoomValue.set(f"{zoom_value}%")	 # OK
		
		if (hasattr(self, 'currentCollisionLeftGlyph') and self.currentCollisionLeftGlyph and
			hasattr(self, 'currentCollisionRightGlyph') and self.currentCollisionRightGlyph):
			self.updatePreviewCollision(
				self.currentCollisionPrefix,
				self.currentCollisionLeftGlyph,
				self.currentCollisionRightGlyph,
				self.currentCollisionSuffix
			)
	
	def createEmptyResultsList(self, message="No collisions found"):
		"""Crea una vista de resultados vacía con un mensaje"""
		tab = self.w.tabs[0]
		
		# Verificar que resultsContainer existe
		if not hasattr(tab, 'resultsContainer'):
			return
		
		containerView = tab.resultsContainer.getNSView()
		
		# Limpiar contenedor
		for subview in containerView.subviews():
			subview.removeFromSuperview()
		
		# Crear vista de fondo blanco con mensaje
		backgroundView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 180))
		backgroundView.setWantsLayer_(True)
		backgroundView.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
		
		# Agregar borde sutil
		borderLayer = CALayer.layer()
		borderLayer.setFrame_(NSMakeRect(0, 0, 360, 180))
		borderLayer.setBorderWidth_(1.0)
		borderLayer.setBorderColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(
			0.9, 0.9, 0.9, 1.0).CGColor())
		backgroundView.layer().addSublayer_(borderLayer)
		
		# Mensaje principal
		messageLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 75, 360, 30))
		messageLabel.setStringValue_(message)
		messageLabel.setEditable_(False)
		messageLabel.setBordered_(False)
		messageLabel.setDrawsBackground_(False)
		
		# Cambiar color según el tipo de mensaje
		if "found" in message.lower() and "no" in message.lower():
			messageLabel.setTextColor_(NSColor.orangeColor())
		else:
			messageLabel.setTextColor_(NSColor.grayColor())
		
		messageLabel.setAlignment_(NSCenterTextAlignment)
		messageLabel.setFont_(NSFont.systemFontOfSize_(12))
		
		# Instrucciones adicionales
		instructionLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 45, 360, 20))
		
		if "no collisions found" in message.lower():
			instructionLabel.setStringValue_("Try increasing tolerance or check different glyphs")
		elif "enter glyphs" in message.lower():
			instructionLabel.setStringValue_("Example: A, T, V, L")
		elif "no valid glyphs" in message.lower():
			instructionLabel.setStringValue_("Check glyph names and try again")
		else:
			instructionLabel.setStringValue_("")
		
		instructionLabel.setEditable_(False)
		instructionLabel.setBordered_(False)
		instructionLabel.setDrawsBackground_(False)
		instructionLabel.setTextColor_(NSColor.lightGrayColor())
		instructionLabel.setAlignment_(NSCenterTextAlignment)
		instructionLabel.setFont_(NSFont.systemFontOfSize_(9))
		
		backgroundView.addSubview_(messageLabel)
		backgroundView.addSubview_(instructionLabel)
		
		containerView.addSubview_(backgroundView)
		
		# Actualizar preview vacío
		self.createEmptyPreviewCollision()
	
	def bboxCollision(self, layer):
		"""Obtener bounding box per a Collision Detector"""
		if not layer:
			return (0, 0, 0, 0)
		
		if hasattr(layer, 'components') and layer.components:
			try:
				decomposed_layer = layer.copyDecomposedLayer()
				b = decomposed_layer.bounds
				if b:
					return (b.origin.x, b.origin.y, b.origin.x+b.size.width, b.origin.y+b.size.height)
			except Exception as e:
				pass
		
		b = layer.bounds
		if not b:
			return (0, 0, 0, 0)
		return (b.origin.x, b.origin.y, b.origin.x+b.size.width, b.origin.y+b.size.height)

	# ===== FUNCIONALITATS NOVES PER A COLLISION DETECTOR =====

	def closeAllTabsCollisionCallback(self, sender):
		"""Tanca tots els tabs oberts a la font"""
		font = Glyphs.font
		if font:
			while len(font.tabs) > 0:
				font.tabs[-1].close()


	def line_intersects_protected(ls, le, protected_ranges):
		for ps, pe in protected_ranges:
			if not (le <= ps or ls >= pe):
				return True
		return False






	def hideExistingPairsCollisionCallback(self, sender):
		"""Hide blocks where ANY consecutive pair has POSITIVE kerning"""
		print("\n" + "=" * 80)
		print("🧪 DEBUG — HIDE EXISTING PAIRS (checking TWO consecutive pairs)")
		print("=" * 80)
	
		font = Glyphs.font
		if not font:
			print("❌ No font open")
			return
	
		tab = font.currentTab
		if not tab:
			print("❌ No active tab")
			return
	
		text = tab.text
		master = font.selectedFontMaster
		if not master:
			print("❌ No master selected")
			return
	
		mid = master.id
	
		print(f"📄 Tab text length: {len(text)}")
		print(f"🎯 Master: {master.name} (ID: {mid})")
	
		# Función para buscar kerning
		def get_kerning(left, right):
			"""Get kerning between two glyphs"""
			try:
				return font.kerningForPair(mid, left, right)
			except:
				return None
	
		# Función para encontrar nombre de glifo
		def find_glyph_name(name_or_char):
			"""Find glyph name in font"""
			if len(name_or_char) == 1 and name_or_char.isalpha():
				if name_or_char in font.glyphs:
					return name_or_char
				if name_or_char.lower() in font.glyphs:
					return name_or_char.lower()
				if name_or_char.upper() in font.glyphs:
					return name_or_char.upper()
		
			if name_or_char in font.glyphs:
				return name_or_char
		
			if len(name_or_char) == 1:
				char = name_or_char
				code_point = ord(char)
			
				for glyph in font.glyphs:
					if glyph.unicode:
						try:
							unicode_values = glyph.unicode.split()
							for uni_val in unicode_values:
								if int(uni_val, 16) == code_point:
									return glyph.name
						except:
							pass
			
				uni_name = f"uni{code_point:04X}"
				if uni_name in font.glyphs:
					return uni_name
		
			base_name = name_or_char.split('.')[0]
			if base_name in font.glyphs:
				return base_name
		
			return None
	
		# Buscar bloques
		blocks = []
	
		print(f"\n🔍 Searching for blocks...")
	
		patterns = [('hh', 'hh'), ('hh', 'HH'), ('HH', 'hh'), ('HH', 'HH')]
	
		for prefix, suffix in patterns:
			i = 0
			while i < len(text) - (len(prefix) + len(suffix) + 1):
				if text[i:i+len(prefix)] == prefix:
					prefix_start = i
					prefix_end = i + len(prefix)
				
					j = prefix_end
					while j < len(text) - len(suffix) + 1:
						if text[j:j+len(suffix)] == suffix:
							suffix_start = j
							suffix_end = j + len(suffix)
						
							content = text[prefix_end:suffix_start]
						
							if '/' in content:
								slash_pos = content.find('/')
								left_part = content[:slash_pos].strip()
								right_part = content[slash_pos+1:].strip()
							
								left_part = left_part.replace(' ', '').replace('/', '')
								right_part = right_part.split()[0] if ' ' in right_part else right_part
								right_part = right_part.replace('/', '')
							
								if left_part and right_part:
									blocks.append({
										'type': 'explicit',
										'start': prefix_start,
										'end': suffix_end,
										'content': content,
										'full_text': text[prefix_start:suffix_end],
										'left_glyph': left_part,
										'right_glyph': right_part,
										'suffix_char': 'h'	# El 'h' del sufijo
									})
							else:
								clean_content = content.strip()
								if len(clean_content) > 1:
									first_char = clean_content[0]
									if first_char.isalpha():
										rest = clean_content[1:].strip()
										if rest:
											unicode_char = rest[0]
											if ord(unicode_char) > 127:
												blocks.append({
													'type': 'unicode',
													'start': prefix_start,
													'end': suffix_end,
													'content': content,
													'full_text': text[prefix_start:suffix_end],
													'left_char': first_char,
													'unicode_char': unicode_char,
													'suffix_char': 'h'	# El 'h' del sufijo
												})
						
							break
						j += 1
				i += 1
	
		# Eliminar duplicados
		unique_blocks = []
		seen_positions = set()
	
		for block in blocks:
			position_key = (block['start'], block['end'])
			if position_key not in seen_positions:
				unique_blocks.append(block)
				seen_positions.add(position_key)
	
		unique_blocks.sort(key=lambda x: x['start'])
	
		print(f"✅ Found {len(unique_blocks)} unique blocks")
	
		for i, block in enumerate(unique_blocks):
			print(f"\n	Block {i}: '{block['full_text']}'")
			print(f"	Type: {block['type']}, Pos: [{block['start']}:{block['end']}]")
		
			if block['type'] == 'explicit':
				print(f"	Explicit: '{block['left_glyph']}' / '{block['right_glyph']}'")
			else:
				print(f"	Unicode: '{block['left_char']}' + '{block['unicode_char']}'")
	
		# numbersign protection ranges
		pranges = []
		stack = []
		for j, ch in enumerate(text):
			if ch == 'numbersign' or ch == '#':
				if not stack:
					stack.append(j)
				else:
					start = stack.pop()
					pranges.append((start, j+1))
	
		print(f"\n🛡️ Found {len(pranges)} protected numbersign...# ranges")
		for idx, (ps, pe) in enumerate(pranges):
			print(f"  Protected {idx}: pos [{ps}:{pe}] = '{text[ps:pe]}'")
	
		def line_intersects_protected(ls, le, pranges):
			for ps, pe in pranges:
				if not (le <= ps or ls >= pe): 
					return True
			return False
	
		# Check each block - EXAMINANDO DOS PARES
		to_hide = []
	
		for bi, block in enumerate(unique_blocks):
			print(f"\n🔎 Checking block {bi}: '{block['full_text']}'")
			print(f"  Position: [{block['start']}:{block['end']}]")
		
			# Check protection
			if line_intersects_protected(block['start'], block['end'], pranges):
				print(f"  ⛔ Block intersects with protected range → KEEP")
				continue
		
			# Lista para almacenar todos los pares a verificar
			pairs_to_check = []
		
			if block['type'] == 'explicit':
				# Par 1: left_glyph / right_glyph
				left1 = find_glyph_name(block['left_glyph'])
				right1 = find_glyph_name(block['right_glyph'])
				if left1 and right1:
					pairs_to_check.append((f"Pair 1: {left1}/{right1}", left1, right1))
		
				# Par 2: right_glyph / suffix_char ('h')
				right_glyph_name = find_glyph_name(block['right_glyph'])
				suffix_char_name = find_glyph_name(block['suffix_char'])
				if right_glyph_name and suffix_char_name:
					pairs_to_check.append((f"Pair 2: {right_glyph_name}/{suffix_char_name}", right_glyph_name, suffix_char_name))
			
			elif block['type'] == 'unicode':
				# Par 1: left_char / unicode_char
				left1 = find_glyph_name(block['left_char'])
				right1 = find_glyph_name(block['unicode_char'])
				if left1 and right1:
					pairs_to_check.append((f"Pair 1: {left1}/{right1}", left1, right1))
		
				# Par 2: unicode_char / suffix_char ('h')
				unicode_glyph_name = find_glyph_name(block['unicode_char'])
				suffix_char_name = find_glyph_name(block['suffix_char'])
				if unicode_glyph_name and suffix_char_name:
					pairs_to_check.append((f"Pair 2: {unicode_glyph_name}/{suffix_char_name}", unicode_glyph_name, suffix_char_name))
	
			print(f"  Pairs to check: {len(pairs_to_check)}")
		
			# Verificar kerning en CADA par
			has_positive_kern = False
			kern_details = []
		
			for pair_desc, left, right in pairs_to_check:
				kern = get_kerning(left, right)
				if kern is not None:
					kern_details.append(f"{pair_desc} = {kern}")
					if kern > 0:
						has_positive_kern = True
						print(f"  ✅ {pair_desc} has POSITIVE kerning ({kern})")
					else:
						print(f"  ℹ️ {pair_desc} has kerning {kern} (≤ 0)")
				else:
					print(f"  ℹ️ {pair_desc} has NO kerning")
	
			if kern_details:
				print(f"  All kerning values: {', '.join(kern_details)}")
	
			# Decidir si ocultar
			if has_positive_kern:
				print(f"  🚫 Block has AT LEAST ONE positive kerning pair → HIDE")
				to_hide.append((block['start'], block['end']))
			else:
				print(f"  ✅ Block has NO positive kerning pairs → KEEP")
	
		# ============================================================
		# CORRECCIÓN: Mantener alineación eliminando líneas completas
		# ============================================================
		if to_hide:
			print(f"\n🎯 Hiding {len(to_hide)} blocks with positive kerning:")
		
			# Dividir el texto en líneas
			lines = text.split('\n')
			print(f"🧪 DEBUG: Texto tiene {len(lines)} líneas")
		
			# Procesar cada bloque a ocultar
			for start, end in reversed(to_hide):
				print(f"\n	🔧 Procesando bloque en [{start}:{end}]")
			
				# Encontrar en qué línea está este bloque
				block_line_index = -1
				current_pos = 0
			
				for i, line in enumerate(lines):
					line_start = current_pos
					line_end = current_pos + len(line)
				
					# Verificar si el bloque está completamente dentro de esta línea
					if start >= line_start and end <= line_end + 1:	 # +1 para el \n
						block_line_index = i
						block_in_line_start = start - line_start
						block_in_line_end = end - line_start
					
						print(f"	 Bloque en línea {i}: '{line}'")
						print(f"	 Posición en línea: {block_in_line_start} a {block_in_line_end}")
					
						# Verificar si la línea ya está vacía o solo tiene espacios
						if line.strip() == '':
							print(f"	 ⏭️ Línea ya está vacía, saltando")
							break
					
						# Extraer el bloque y los 6 espacios siguientes
						line_after_block = line[block_in_line_end:]
						print(f"	 Texto después del bloque: '{line_after_block[:20]}...'")
					
						# Contar espacios después del bloque
						spaces_after = 0
						for char in line_after_block:
							if char == ' ':
								spaces_after += 1
							else:
								break
					
						print(f"	 Espacios después del bloque: {spaces_after}")
					
						# Eliminar el bloque + 6 espacios (o menos si no hay suficientes)
						spaces_to_remove = min(6, spaces_after)
						total_to_remove = (block_in_line_end - block_in_line_start) + spaces_to_remove
					
						# Crear nueva línea
						new_line = line[:block_in_line_start] + line[block_in_line_start + total_to_remove:]
						print(f"	 Nueva línea ({len(new_line)} chars): '{new_line}'")
					
						# Reemplazar la línea
						lines[i] = new_line
						break
				
					current_pos += len(line) + 1  # +1 para el \n
		
			# Reconstruir el texto manteniendo líneas vacías si es necesario
			final_text = '\n'.join(lines)
		
			print(f"\n🧪 DEBUG: Texto final tiene {len(final_text)} caracteres")
		
			# Aplicar el texto modificado al tab
			tab.text = final_text
		
			print(f"\n✅ {len(to_hide)} bloques ocultos manteniendo alineación")
		
			Glyphs.showNotification(
				"Hide Positive Kerning Pairs", 
				f"Hidden {len(to_hide)} blocks with positive kerning\n"
				f"Alignment maintained"
			)
		else:
			print(f"\nℹ️ No blocks with positive kerning found to hide")
			Glyphs.showNotification(
				"Hide Positive Kerning Pairs", 
				"No blocks with positive kerning found"
			)
	
		print("=" * 80) 
		
		
	def glyphTypeCollision(self, leftGlyph, rightGlyph=None):
		"""
		Classificació simple de col·lisions per tipus de glif.
		Compatible amb crides antigues (1 o 2 arguments).
		"""
		if not leftGlyph:
			return False

		# Si només ens passen un glif, acceptem-lo
		if rightGlyph is None:
			return True

		# Evitar espais
		if leftGlyph.name == "space" or rightGlyph.name == "space":
			return False

		# Només lletres (criteri conservador)
		if leftGlyph.category != "Letter":
			return False
		if rightGlyph.category != "Letter":
			return False

		return True



	# Añadir este método nuevo a la clase KernMarginSlider:
	def removeHashFromTabCallback(self, sender):
		"""Elimina todos los caracteres '#' (numbersign) del tab actual"""
		print("\n" + "=" * 80)
		print("🧪 DEBUG — ELIMINAR TODOS LOS # DEL TAB")
		print("=" * 80)
	
		font = Glyphs.font
		if not font:
			print("❌ No hay fuente abierta")
			return
	
		tab = font.currentTab
		if not tab:
			print("❌ No hay tab activo")
			return
	
		text = tab.text
		if not text:
			print("ℹ️ El tab está vacío")
			return
	
		print(f"📄 Texto original ({len(text)} caracteres):")
		print(repr(text[:200]) + ("..." if len(text) > 200 else ""))
	
		# Contar cuántos # hay
		hash_count = text.count('#')
		print(f"🔍 Encontrados {hash_count} caracteres '#'")
	
		if hash_count == 0:
			print("ℹ️ No hay caracteres '#' para eliminar")
			Glyphs.showNotification(
				"Eliminar #",
				"No hay caracteres '#' en el tab"
			)
			return
	
		# Eliminar todos los #
		new_text = text.replace('#', '')
	
		# También eliminar caracteres "numbersign" si existen
		numbersign_count = text.count('numbersign')
		if numbersign_count > 0:
			print(f"🔍 También encontrados {numbersign_count} caracteres 'numbersign'")
			new_text = new_text.replace('numbersign', '')
	
		print(f"✅ Texto modificado ({len(new_text)} caracteres):")
		print(repr(new_text[:200]) + ("..." if len(new_text) > 200 else ""))
	
		# Aplicar el cambio al tab
		tab.text = new_text
	
		# Mostrar notificación
		total_removed = hash_count + numbersign_count
		Glyphs.showNotification(
			"Caracteres # eliminados",
			f"Eliminados {total_removed} caracteres:\n"
			f"• {hash_count} x '#'\n"
			f"• {numbersign_count} x 'numbersign'"
		)
	
		print(f"✅ Eliminados {total_removed} caracteres del tab")
		print("=" * 80)
		
		
	def removeTabKernCollisionCallback(self, sender):
		print("\n" + "=" * 80)
		print("🧪 DEBUG — REMOVE TAB KERN (PROTEGER BLOQUES numbersign...#)")
		print("=" * 80)

		font = Glyphs.font
		if not font:
			print("❌ No font")
			return

		tab = font.currentTab
		if not tab or not tab.layers:
			print("❌ No tab o tab buit")
			return

		master = font.selectedFontMaster
		if not master:
			print("❌ No master")
			return

		mid = master.id

		# -------------------------------------------------
		# TEXT I GLIFS DEL TAB
		# -------------------------------------------------
		text = tab.text or ""
		print("\n📄 ANALIZANDO TAB...")

		# Obtener glifos del tab
		glyph_names = []
		for i, layer in enumerate(tab.layers):
			if layer and layer.parent:
				name = layer.parent.name
				glyph_names.append(name)
			else:
				glyph_names.append(None)

		print(f"📋 Total glifos en tab: {len(glyph_names)}")

		# -------------------------------------------------
		# IDENTIFICAR BLOQUES PROTEGIDOS numbersign...numbersign
		# -------------------------------------------------
		print("\n🔍 BUSCANDO BLOQUES PROTEGIDOS numbersign...numbersign")
	
		# Lista para almacenar índices de glifos dentro de bloques protegidos
		protected_indices = set()
	
		# Buscar secuencias numbersign...numbersign en los nombres de glifos
		i = 0
		while i < len(glyph_names):
			if glyph_names[i] == "numbersign":
				print(f"  🔎 Encontrado 'numbersign' en posición {i}")
			
				# Buscar el cierre del bloque
				block_end = -1
				for j in range(i + 1, len(glyph_names)):
					if glyph_names[j] == "numbersign":
						block_end = j
						print(f"	→ Encontrado 'numbersign' de cierre en posición {j}")
						break
			
				if block_end > i:
					# Marcar todos los glifos dentro de este bloque como protegidos
					for k in range(i, block_end + 1):
						protected_indices.add(k)
						print(f"	🛡️	 Marcando glifo {k} ('{glyph_names[k]}') como PROTEGIDO")
				
					i = block_end + 1  # Saltar al final del bloque
					continue
		
			i += 1

		print(f"\n✅ Índices protegidos: {sorted(protected_indices)}")
		print(f"   Total glifos protegidos: {len(protected_indices)}")

		# -------------------------------------------------
		# IDENTIFICAR PARES CON KERNING (EXCLUYENDO PROTEGIDOS)
		# -------------------------------------------------
		pairs_with_kern = []

		print("\n🔍 COMPROBANDO PARELLS (EXCLUYENDO PROTEGIDOS):")

		for i in range(len(glyph_names) - 1):
			left_name = glyph_names[i]
			right_name = glyph_names[i + 1]
		
			if not left_name or not right_name:
				continue

			# VERIFICAR SI EL PAR ESTÁ PROTEGIDO
			# Un par está protegido si AMBOS glifos están en un bloque protegido
			# y además el par está COMPLETAMENTE dentro del bloque (no en el borde)
			is_protected = False
		
			# Opción 1: Ambos índices están en protected_indices
			if i in protected_indices and (i + 1) in protected_indices:
				# Pero verificar que no estemos en el borde del bloque
				# (es decir, que left_name no sea el numbersign de apertura)
				if left_name != "numbersign":
					is_protected = True
					print(f"➡️ Parell {i}: {left_name} / {right_name}")
					print(f"  🛡️  PAR COMPLETAMENTE PROTEGIDO (ambos índices en bloque)")
		
			# Opción 2: Par que cruza el borde de un bloque protegido
			# (esto sería raro pero lo manejamos)
			elif (i in protected_indices and left_name != "numbersign") or \
				 ((i + 1) in protected_indices and right_name != "numbersign"):
				is_protected = True
				print(f"➡️ Parell {i}: {left_name} / {right_name}")
				print(f"  🛡️  PAR PARCIALMENTE PROTEGIDO (en borde de bloque)")

			if is_protected:
				print(f"  ✅ Saltando par protegido")
				continue

			# Solo verificar kerning para pares NO protegidos
			print(f"\n➡️ Parell {i}: {left_name} / {right_name}")
		
			has_kern = self.hasKerning(font, mid, left_name, right_name)
			print(f"   Té kerning: {has_kern}")

			if has_kern:
				pairs_with_kern.append((left_name, right_name))
				print(f"  🗑️  Marcado para eliminación")

		if not pairs_with_kern:
			print("\n⚠️ No s'ha detectat cap parell amb kerning (o todos están protegidos)")
			return

		print("\n🧽 PARELLS A ELIMINAR (NO PROTEGIDOS):")
		for idx, p in enumerate(pairs_with_kern):
			print(f"  {idx:3d}: {p[0]} / {p[1]}")

		# -------------------------------------------------
		# ELIMINACIÓN DIRECTA SIN CONFIRMACIÓN
		# -------------------------------------------------
		removed = 0

		print("\n🔨 ELIMINANDO KERNING...")
		for left, right in pairs_with_kern:
			print(f"  🧹 Eliminando {left} / {right}")
			try:
				self.removeKerning(font, mid, left, right)
				removed += 1
				print(f"	 ✅ Eliminado")
			except Exception as e:
				print(f"	 ❌ Error eliminando: {e}")

		print(f"\n✅ TOTAL ELIMINADO: {removed}")
	
		# Resumen final
		print(f"\n📊 RESUMEN FINAL:")
		print(f"  • Glifos totales en tab: {len(glyph_names)}")
		print(f"  • Glifos protegidos: {len(protected_indices)}")
		print(f"  • Pares con kerning encontrados: {len(pairs_with_kern)}")
		print(f"  • Pares eliminados: {removed}")
	
		if removed > 0:
			Glyphs.showNotification(
				"Kerning Eliminado",
				f"Eliminado kerning de {removed} pares\n"
				f"Pares en bloques protegidos preservados"
			)
	
		print("=" * 80)

	# ===== COL·LECCIONS I MÈTODES DEL GENERADOR DE PARES =====


	def getFeatureNames(self):
		"""Obté noms de feature de la font actual"""
		font = Glyphs.font
		if not font:
			return ["No font open"]
		
		features = [f.name for f in font.features]
		return features if features else ["No features"]

	def fillKerningGroups(self, font):
		"""Assigna grups de kerning a glifs que no en tenen"""
		count_left = 0
		count_right = 0
		
		for glyph in font.glyphs:
			if glyph.category in ["Letter", "Number", "Punctuation", "Symbol"]:
				if not glyph.leftKerningGroup:
					glyph.leftKerningGroup = glyph.name
					count_left += 1
					
				if not glyph.rightKerningGroup:
					glyph.rightKerningGroup = glyph.name
					count_right += 1
		
		return count_left + count_right

	def fillGroupsCallback(self, sender):
		"""Omple grups de kerning buits"""
		font = Glyphs.font		  
		if not font:
			return
			
		glyphs_without_groups = 0
		total_base_glyphs = 0
		
		for glyph in font.glyphs:
			if glyph.category in ["Letter", "Number", "Punctuation", "Symbol"]:
				total_base_glyphs += 1
				if not glyph.leftKerningGroup or not glyph.rightKerningGroup:
					glyphs_without_groups += 1
		
		if glyphs_without_groups == 0:
			self.w.tabs[1].groupsInfo.set("✅ Tots els glifs tenen grups de kerning!")
			return
		
		count = self.fillKerningGroups(font)
		
		remaining_without_groups = 0
		for glyph in font.glyphs:
			if glyph.category in ["Letter", "Number", "Punctuation", "Symbol"]:
				if not glyph.leftKerningGroup or not glyph.rightKerningGroup:
					remaining_without_groups += 1
		
		message = f"Grups de Kerning Omplerts:\n"
		message += f"Grups assignats a {count} propietats\n"
		message += f"Resten sense grups: {remaining_without_groups}"
		
		self.w.tabs[1].groupsInfo.set(message)

	def insertTestWordsCallback(self, sender):
		"""Insereix les paraules de prova seleccionades en un nou tab"""
		font = Glyphs.font
		if not font:
			return
			
		tab = self.w.tabs[1]
		selected_index = tab.testWordsPopup.get()
		test_names = list(self.TEST_WORDS_COLLECTIONS.keys())
		
		if 0 <= selected_index < len(test_names):
			test_name = test_names[selected_index]
			test_text = self.TEST_WORDS_COLLECTIONS[test_name]
			
			tab_content = f"# {test_name}\n\n{test_text}"
			font.newTab(tab_content)

	# ===== MÈTODES SANITIZER =====

	def kerningGroupExists(self, font, groupName):
		"""Comprova si un grup de kerning existeix a la font"""
		if groupName.startswith("@MMK_L_"):
			grp = groupName.replace("@MMK_L_", "")
			return any(g.leftKerningGroup == grp for g in font.glyphs)
		if groupName.startswith("@MMK_R_"):
			grp = groupName.replace("@MMK_R_", "")
			return any(g.rightKerningGroup == grp for g in font.glyphs)
		return False

	def format_glyph_display(self, glyph_name):
		font = Glyphs.font
		if not glyph_name or glyph_name not in font.glyphs:
			return f"/{glyph_name}" if glyph_name else "/unknown"
		g = font.glyphs[glyph_name]
		char_or_name = glyph_to_char_or_name(g)
		if not char_or_name:
			return f"/{glyph_name}"
		return char_or_name

	def removeKerning(self, font, master_id, left, right):
		"""
		Elimina kerning directe i de grups.
		left i right han de ser NOMS de glif (str).
		"""
		if not isinstance(left, str) or not isinstance(right, str):
			return

		if left not in font.glyphs or right not in font.glyphs:
			return

		# 1. Kerning directe
		try:
			font.removeKerningForPair(master_id, left, right)
		except Exception:
			pass

		gL = font.glyphs[left]
		gR = font.glyphs[right]

		# 2. Grup esquerre
		if gL.rightKerningGroup:
			try:
				font.removeKerningForPair(
					master_id,
					f"@MMK_L_{gL.rightKerningGroup}",
					right
				)
			except Exception:
				pass

		# 3. Grup dret
		if gR.leftKerningGroup:
			try:
				font.removeKerningForPair(
					master_id,
					left,
					f"@MMK_R_{gR.leftKerningGroup}"
				)
			except Exception:
				pass


	# ============================================================
	# CONSTRUCCIÓN CORRECTA DEL TEXTO PARA EL TAB
	# ============================================================

	def textGlyphs_for_tab(self, tab):
		"""
		DEBUG: devuelve glifos reales del tab y los imprime
		"""
		glyphs = []

		print("\n🧪 DEBUG TAB GLYPHS --------------------")

		try:
			for i, layer in enumerate(tab.layers):
				if layer.parent:
					g = layer.parent
					glyphs.append(g)
					print(
						f"{i:02d} | glyph: {g.name:<20} "
						f"category: {g.category:<12} "
						f"unicode: {g.unicode}"
					)
				else:
					print(f"{i:02d} | layer WITHOUT parent")
		except Exception as e:
			print("❌ ERROR leyendo layers del tab:", e)

		print("🧪 TOTAL GLYPHS:", len(glyphs))
		print("🧪 END TAB GLYPHS ----------------------\n")

		return glyphs

	# ============================================================
	# COMPROBACIÓN DE KERNING EXISTENTE (DIRECTO Y POR GRUPO)
	# ============================================================

	def isKerningCandidate(self, gL, gR):
		if not gL or not gR:
			return False

		# Nunca espacios
		if gL.category == "Space" or gR.category == "Space":
			return False

		# Nunca marks combinantes
		if gL.category == "Mark" or gR.category == "Mark":
			return False

		# Nunca símbolos
		if gL.category == "Symbol" or gR.category == "Symbol":
			return False

		# Opcional: excluir puntuación
		if gL.category == "Punctuation" or gR.category == "Punctuation":
			return False

		# Excluir glifos técnicos
		banned = (
			".case", ".comb", ".init", ".medi", ".fina",
			".isol", ".liga", ".calt", ".locl"
		)

		for b in banned:
			if b in gL.name or b in gR.name:
				return False

		return True

	def hasKerning(self, font, master_id, left, right):
		"""
		Comprova si existeix kerning directe o via grups.
		Versión mejorada con más debug.
		"""
		print(f"🧪 DEBUG hasKerning: Verificando {left} / {right}")
	
		if not isinstance(left, str) or not isinstance(right, str):
			print(f"  ❌ Error: left o right no son strings")
			return False

		if left not in font.glyphs:
			print(f"  ⚠️  Left glyph '{left}' no encontrado en font")
			return False
	
		if right not in font.glyphs:
			print(f"  ⚠️  Right glyph '{right}' no encontrado en font")
			return False

		# Kerning directe
		try:
			kern_value = font.kerningForPair(master_id, left, right)
			if kern_value is not None:
				print(f"  ✅ Kerning directo encontrado: {kern_value}")
				return True
			else:
				print(f"  ℹ️  No kerning directo")
		except Exception as e:
			print(f"  ❌ Error verificando kerning directo: {e}")

		gL = font.glyphs[left]
		gR = font.glyphs[right]

		# Grup esquerre
		if gL.rightKerningGroup:
			try:
				group_left = f"@MMK_L_{gL.rightKerningGroup}"
				kern_value = font.kerningForPair(master_id, group_left, right)
				if kern_value is not None:
					print(f"  ✅ Kerning via grupo izquierdo encontrado: {kern_value}")
					return True
			except Exception as e:
				print(f"  ❌ Error verificando kerning via grupo izquierdo: {e}")

		# Grup dret
		if gR.leftKerningGroup:
			try:
				group_right = f"@MMK_R_{gR.leftKerningGroup}"
				kern_value = font.kerningForPair(master_id, left, group_right)
				if kern_value is not None:
					print(f"  ✅ Kerning via grupo derecho encontrado: {kern_value}")
					return True
			except Exception as e:
				print(f"  ❌ Error verificando kerning via grupo derecho: {e}")

		print(f"  ❌ No se encontró kerning de ningún tipo")
		return False


	def contextualPrefixSuffixCollision(self, l, r):
		lt = self.glyphTypeCollision(l)
		rt = self.glyphTypeCollision(r)

		if lt == "number" or rt == "number":
			return (["H", "H"], ["H", "H"])

		if lt == "upper" and rt == "upper":
			return (["H", "H"], ["H", "H"])

		if lt == "lower" and rt == "upper":
			return (["h", "h"], ["H", "H"])

		if lt == "upper" and rt == "lower":
			return (["H", "H"], ["h", "h"])

		return (["h", "h"], ["h", "h"])

	# ============================================================
	# CARGA Y VALIDACIÓN DE PARES DESDE JSON
	# ============================================================

	def loadKerningPairsFromJSON(self, jsonPath):
		font = Glyphs.font
		if not font:
			return []

		try:
			with open(jsonPath, "r", encoding="utf-8") as f:
				data = json.load(f)
		except Exception as e:
			print("❌ JSON load error:", e)
			return []

		raw_pairs = data.get("pairs", [])
		validated = []

		for item in raw_pairs:
			if not isinstance(item, (list, tuple)) or len(item) != 2:
				continue

			left, right = item

			if left not in font.glyphs or right not in font.glyphs:
				continue

			gL = font.glyphs[left]
			gR = font.glyphs[right]

			if not self.isKerningCandidate(gL, gR):
				continue

			if (left, right) not in validated:
				validated.append((left, right))

		print(f"✅ JSON validated pairs: {len(validated)}")
		print("🧪 VALIDATED PAIRS:", validated)

		return validated

	# ============================================================
	# LISTADO FIJO GENERADO DESDE BOTÓN (EJEMPLO)
	# ============================================================

	def useFixedPairListCallback(self, sender):
		font = Glyphs.font
		if not font:
			return

		pairs = []

		candidates = [
			"i", "icircumflex", "idieresis",
			"igrave", "iacute", "ibreve", "itilde"
		]

		for left in candidates:
			if left in font.glyphs and "l" in font.glyphs:
				pairs.append((left, "l"))

		self.fixedKerningPairs = pairs

		preview = "	   ".join(f"/{l}/{r}" for l, r in pairs)
		font.newTab(preview)

	# ============================================================
	# GENERACIÓN DE TAB (PREVIEW) DESDE COLISIONES
	# ============================================================

	def createPreviewImageCollision(self, prefix, leftGlyphName, rightGlyphName, suffix):
		font = Glyphs.font
		if not font:
			return None

		imageSize = NSSize(360, 150)
		image = NSImage.alloc().initWithSize_(imageSize)
		image.lockFocus()

		BACKGROUND_COLOR.set()
		NSBezierPath.fillRect_(NSMakeRect(0, 0, imageSize.width, imageSize.height))

		try:
			y_baseline = (imageSize.height / 2) + BASELINE_OFFSET
			scale = self.zoomLevelCollision * 0.45

			sequence = []

			# PREFIX (lista de glifos)
			for gname in prefix:
				if gname in font.glyphs:
					glyph = font.glyphs[gname]
					layer = self.getDecomposedLayerCollision(glyph)
					if layer:
						sequence.append((layer, gname))

			# LEFT
			if leftGlyphName in font.glyphs:
				glyph = font.glyphs[leftGlyphName]
				layer = self.getDecomposedLayerCollision(glyph)
				if layer:
					sequence.append((layer, leftGlyphName))

			# RIGHT
			if rightGlyphName in font.glyphs:
				glyph = font.glyphs[rightGlyphName]
				layer = self.getDecomposedLayerCollision(glyph)
				if layer:
					sequence.append((layer, rightGlyphName))

			# SUFFIX (lista de glifos)
			for gname in suffix:
				if gname in font.glyphs:
					glyph = font.glyphs[gname]
					layer = self.getDecomposedLayerCollision(glyph)
					if layer:
						sequence.append((layer, gname))

			# Calcular ancho total
			total_width = sum(layer.width * scale for layer, _ in sequence)
			x_pos = (imageSize.width - total_width) / 2

			# Línea base
			baseline = NSBezierPath.bezierPath()
			baseline.moveToPoint_((x_pos - 10, y_baseline))
			baseline.lineToPoint_((x_pos + total_width + 10, y_baseline))
			NSColor.colorWithCalibratedWhite_alpha_(0.9, 1.0).set()
			baseline.setLineWidth_(1)
			baseline.stroke()

			# Dibujar glifos
			for layer, _ in sequence:
				path = layer.bezierPath.copy()
				transform = NSAffineTransform.transform()
				transform.translateXBy_yBy_(x_pos, y_baseline)
				transform.scaleXBy_yBy_(scale, scale)
				path.transformUsingAffineTransform_(transform)

				GLYPH_COLOR.set()
				path.fill()

				x_pos += layer.width * scale

		except Exception as e:
			print("❌ Preview error:", e)

		image.unlockFocus()
		return image

	def exportTabToJSONCallback(self, sender):
		font = Glyphs.font
		if not font:
			return

		tab = font.currentTab
		if not tab:
			print("ℹ️ No active tab to export")
			return

		from vanilla.dialogs import putFile
		import json

		path = putFile("kerningPairs.json")
		if not path:
			return

		pairs = []
		seen = set()

		# Leer glifos REALES del tab
		glyphs = []
		for layer in tab.layers:
			if layer.parent:
				glyphs.append(layer.parent.name)

		# Convertir a pares consecutivos
		for i in range(len(glyphs) - 1):
			left = glyphs[i]
			right = glyphs[i + 1]

			if (left, right) in seen:
				continue

			# Validar con el motor
			gL = font.glyphs[left] if left in font.glyphs else None
			gR = font.glyphs[right] if right in font.glyphs else None

			if not gL or not gR:
				continue

			if not self.isKerningCandidate(gL, gR):
				continue

			seen.add((left, right))
			pairs.append([left, right])

		data = {
			"name": "Exported from Glyphs tab",
			"pairs": pairs
		}

		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
			print(f"✅ Exported {len(pairs)} pairs to JSON")
		except Exception as e:
			print("❌ Error writing JSON:", e)

	def checkKerningGroupsCallback(self, sender):
		print("🧪 checkKerningGroupsCallback called")

		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.")
			return

		total = 0
		missing = 0

		for g in font.glyphs:
			if not g.export:
				continue

			total += 1

			if not g.leftKerningGroup or not g.rightKerningGroup:
				missing += 1

		text = (
			f"{total} glyphs available\n"
			f"{missing} without kerning group assigned"
		)

		Message(
			"Kerning Groups Check",
			text,
			OKButton="OK"
		)

	def fillEmptyKerningGroupsCallback(self, sender):
		print("🧪 fillEmptyKerningGroupsCallback called")

		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.")
			return

		missingSides = []

		for g in font.glyphs:
			if not g.export:
				continue

			if not g.leftKerningGroup:
				missingSides.append((g, "left"))

			if not g.rightKerningGroup:
				missingSides.append((g, "right"))

		count = len(missingSides)

		if count == 0:
			Message(
				"Kerning Groups",
				"All glyphs already have kerning groups assigned.",
				OKButton="OK"
			)
			return

		question = (
			f"Detected {count} sides without group assignment.\n\n"
			"Groups will be named after the glyph itself."
		)

		result = AskYesNo(
			"Fill Empty Kerning Groups",
			question,
			OKButton="Apply",
			CancelButton="Cancel"
		)

		if not result:
			print("🧪 User cancelled")
			return

		# APPLY
		for g, side in missingSides:
			if side == "left":
				g.leftKerningGroup = g.name
			else:
				g.rightKerningGroup = g.name

		Message(
			"Kerning Groups",
			f"{count} kerning sides assigned.",
			OKButton="OK"
		)

	def _debug(self, msg):
		print("🧪 TOOLS DEBUG:", msg)

	def checkGroupsCallback(self, sender):
		print("🧪 TOOLS: Check Kerning Groups callback executed")

		font = Glyphs.font
		if not font:
			print("❌ No font open")
			return

		total = len(font.glyphs)
		missing = 0

		for g in font.glyphs:
			if not g.leftKerningGroup or not g.rightKerningGroup:
				missing += 1

		alert = NSAlert.alloc().init()
		alert.setMessageText_("Kerning Groups Check")
		alert.setInformativeText_(
			f"{total} glyphs available\n"
			f"{missing} without kerning group assigned"
		)
		alert.addButtonWithTitle_("OK")
		alert.setAlertStyle_(NSInformationalAlertStyle)

		alert.runModal()

	def fillEmptyGroupsCallback(self, sender):
		print("🧪 TOOLS: Fill Empty Groups callback executed")

		font = Glyphs.font
		if not font:
			print("❌ No font open")
			return

		missingSides = []

		for g in font.glyphs:
			if not g.leftKerningGroup:
				missingSides.append((g, "left"))
			if not g.rightKerningGroup:
				missingSides.append((g, "right"))

		count = len(missingSides)

		alert = NSAlert.alloc().init()
		alert.setMessageText_("Fill Empty Kerning Groups")
		alert.setInformativeText_(
			f"Detected {count} sides without kerning group.\n\n"
			"The missing sides will be named after the glyph itself."
		)
		alert.addButtonWithTitle_("Apply")
		alert.addButtonWithTitle_("Cancel")
		alert.setAlertStyle_(NSInformationalAlertStyle)

		response = alert.runModal()

		# NSAlertFirstButtonReturn == Apply
		if response != 1000:
			print("ℹ️ Operation cancelled by user")
			return

		applied = 0

		for g, side in missingSides:
			if side == "left" and not g.leftKerningGroup:
				g.leftKerningGroup = g.name
				applied += 1
			elif side == "right" and not g.rightKerningGroup:
				g.rightKerningGroup = g.name
				applied += 1

		Glyphs.showNotification(
			"Kerning Groups Updated",
			f"{applied} kerning group sides filled."
		)

		print(f"✅ Filled {applied} kerning group sides")

	# ============================================================
	# KERNING GROUP MANAGER FUNCTIONS
	# ============================================================
	
	def openKerningGroupManagerCallback(self, sender):
		"""Open the Kerning Group Manager window"""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton="OK")
			return
		
		# Create the Kerning Group Manager window
		self.createKerningGroupManager()
	
	def createKerningGroupManager(self):
		"""Create the Kerning Group Manager interface"""
		self.kgmWindow = Window((500, 600), "Kerning Group Manager")
		
		# Tabs for left and right groups
		self.kgmWindow.tabs = Tabs((10, 10, -10, -80), ["Left Group", "Right Group"])
		
		# Lists for group members
		self.kgmWindow.tabs[0].list = List((10, 10, -10, -10), [])
		self.kgmWindow.tabs[1].list = List((10, 10, -10, -10), [])
		
		# Action buttons
		self.kgmWindow.makeFirst = Button((10, -65, 120, 24), "Make First", callback=self.kgmMakeFirst)
		self.kgmWindow.applyOrder = Button((140, -65, 120, 24), "Apply Order", callback=self.kgmApplyOrder)
		self.kgmWindow.refreshBtn = Button((270, -65, 100, 24), "Refresh", callback=self.kgmRefreshGroups)
		
		# Status label
		self.kgmWindow.status = TextBox((10, -35, -10, 20), "Select a glyph to view its kerning groups", sizeStyle="small")
		
		self.kgmWindow.open()
		self.kgmRefreshGroups()

	def auto_assign_kerning_groups(self, font):
		"""Automatically assign kerning groups to glyphs that need them"""
		master_id = font.selectedFontMaster.id
		kerning_dict = font.kerning[master_id]
		glyphs_needing_groups = set()
	
		if kerning_dict:
			for left_key, right_dict in kerning_dict.items():
				for right_key, kerning_value in right_dict.items():
					if kerning_value is not None:
						if (isinstance(left_key, str) and left_key.startswith('@MMK_L_') and
							isinstance(right_key, str) and not right_key.startswith('@MMK_') and
							right_key in font.glyphs):
								glyphs_needing_groups.add((right_key, 'R'))
						
						if (isinstance(right_key, str) and right_key.startswith('@MMK_R_') and
							isinstance(left_key, str) and not left_key.startswith('@MMK_') and
							left_key in font.glyphs):
								glyphs_needing_groups.add((left_key, 'L'))
	
		for glyph in font.glyphs:
			if not self.is_base_glyph(glyph):
				continue
			
			if not glyph.leftKerningGroup:
				glyphs_needing_groups.add((glyph.name, 'L'))
			if not glyph.rightKerningGroup:
				glyphs_needing_groups.add((glyph.name, 'R'))
	
		for glyph_name, side in glyphs_needing_groups:
			if glyph_name not in font.glyphs:
				continue
			glyph = font.glyphs[glyph_name]
			if side == 'L' and not glyph.leftKerningGroup:
				glyph.leftKerningGroup = f"@MMK_L_{glyph_name}"
			elif side == 'R' and not glyph.rightKerningGroup:
				glyph.rightKerningGroup = f"@MMK_R_{glyph_name}"
		return True

	def format_glyph_name(self, glyph_name): 
		"""Format glyph name for display"""
		return f"/{glyph_name}"

	def format_glyph_for_display(self, glyph_name): 
		"""Format glyph for display"""
		return self.format_glyph_name(glyph_name)

	def get_all_kern_pairs(self, font, master_id):
		"""Get all kerning pairs from the current master"""
		all_pairs = []
		kerning_dict = font.kerning.get(master_id, {})
		if not kerning_dict: 
			return all_pairs
		
		for left_key, right_dict in kerning_dict.items():
			for right_key, kerning_value in right_dict.items():
				if kerning_value is not None:
					all_pairs.append({
						'left_key': left_key,
						'right_key': right_key, 
						'value': kerning_value
					})
		return all_pairs

	def get_glyph_name_by_id(self, font, glyph_id):
		"""Get glyph name from glyph ID"""
		if isinstance(glyph_id, str) and len(glyph_id) == 36:
			for glyph in font.glyphs:
				if glyph.id == glyph_id: 
					return glyph.name
		return None

	def find_glyph_for_group(self, font, group_name, target_side):
		"""
		Find a glyph that has the specified group on the specified side
		group_name: group name without prefix (e.g., 'acir', 'bcir', 'tcir')
		target_side: 'L' for left, 'R' for right
		"""
		found_glyphs = []
	
		for g in font.glyphs:
			left_group = g.leftKerningGroup or ""
			right_group = g.rightKerningGroup or ""
		
			if target_side == 'L':
				# Search in left groups (compare with and without prefix)
				if (left_group == group_name or 
					left_group == f"@MMK_L_{group_name}" or
					left_group.endswith(f"_{group_name}")):
					found_glyphs.append(g.name)
			elif target_side == 'R':
				# Search in right groups (compare with and without prefix)
				if (right_group == group_name or 
					right_group == f"@MMK_R_{group_name}" or
					right_group.endswith(f"_{group_name}")):
					found_glyphs.append(g.name)
	
		return found_glyphs

	def get_all_convertible_pairs(self, font, master_id):
		"""Convert all kerning pairs to displayable format with glyph names"""
		convertible_pairs = []
		all_pairs = self.get_all_kern_pairs(font, master_id)
		name_fixes = {
			"a-sc": "a.sc",
			"hypen": "hyphen", 
			"guillemotright": "guillemetright", 
			"guillemotleft": "guillemetleft"
		}
	
		for pair in all_pairs:
			left_key = pair['left_key']
			right_key = pair['right_key']
			kerning_value = pair['value']
		
			# Apply name corrections
			for wrong, correct in name_fixes.items():
				if isinstance(left_key, str):
					left_key = left_key.replace(wrong, correct)
				if isinstance(right_key, str):
					right_key = right_key.replace(wrong, correct)
		
			left_glyph = None
			right_glyph = None
		
			# Process left_key
			if isinstance(left_key, str):
				if left_key.startswith('@MMK_L_'):
					group_name = left_key[7:]  # Extract group name without '@MMK_L_'
					left_glyph = group_name
				
					# Find representative glyph for left group
					if group_name in ["acir", "bcir", "tcir", "cometes"]:
						# For a left group, we look for glyphs that have this group on the RIGHT side
						found_glyphs = self.find_glyph_for_group(font, group_name, 'R')
						if found_glyphs:
							# Use the first found glyph as representative
							left_glyph = found_glyphs[0]
				
				elif left_key in font.glyphs:
					left_glyph = left_key
				else:
					gname = self.get_glyph_name_by_id(font, left_key)
					left_glyph = gname if gname else left_key
		
			# Process right_key	 
			if isinstance(right_key, str):
				if right_key.startswith('@MMK_R_'):
					group_name = right_key[7:]	# Extract group name without '@MMK_R_'
					right_glyph = group_name
				
					# Find representative glyph for right group
					if group_name in ["acir", "bcir", "tcir", "cometes"]:
						# For a right group, we look for glyphs that have this group on the LEFT side
						found_glyphs = self.find_glyph_for_group(font, group_name, 'L')
						if found_glyphs:
							# Use the first found glyph as representative
							right_glyph = found_glyphs[0]
				
				elif right_key in font.glyphs:
					right_glyph = right_key
				else:
					gname = self.get_glyph_name_by_id(font, right_key)
					right_glyph = gname if gname else right_key

			if not left_glyph:
				left_glyph = left_key
			if not right_glyph:
				right_glyph = right_key
			
			if left_glyph and right_glyph:
				left_exists = left_glyph in font.glyphs
				right_exists = right_glyph in font.glyphs
				status = 'VALID' if (left_exists and right_exists) else ('PARTIAL' if left_exists or right_exists else 'MISSING')
				convertible_pairs.append({
					'left': left_glyph, 
					'right': right_glyph, 
					'value': kerning_value, 
					'status': status, 
					'left_raw': left_key, 
					'right_raw': right_key
				})
	
		return convertible_pairs

	def sort_kern_pairs(self, pairs):
		"""Sort kerning pairs by case type for better organization"""
		def get_sort_key(pair):
			lt = self.get_glyph_case_type(pair['left'])
			rt = self.get_glyph_case_type(pair['right'])
			order = {
				("uppercase", "uppercase"): 1,
				("lowercase", "lowercase"): 4
			}
			return (order.get((lt, rt), 99), pair['left'], pair['right'])
		return sorted(pairs, key=get_sort_key)

	def create_tabs_for_category(self, font, pairs, category_name, pairs_per_tab, text_size):
		"""Create tabs for a category of kerning pairs"""
		if not pairs: 
			return 0
		
		sorted_pairs = self.sort_kern_pairs(pairs)
		total_tabs = (len(sorted_pairs) + pairs_per_tab - 1) // pairs_per_tab
	
		for t in range(total_tabs):
			start = t * pairs_per_tab
			end = min(start + pairs_per_tab, len(sorted_pairs))
			tab_pairs = sorted_pairs[start:end]
			tab_lines = [
				f"# {category_name} Kern Pairs {start+1}-{end} of {len(sorted_pairs)}",
				""
			]
		
			for p in tab_pairs:
				display = self.build_kern_display(p['left'], p['right'])
				if category_name == "PARTIAL":
					line = f"{display}				 {int(p['value'])}	  [{p['left_raw']} ; {p['right_raw']}]"
				else:
					line = f"{display}				 {int(p['value'])}"
				tab_lines.append(line)
			
			tab_content = "\n".join(tab_lines)
			tab = font.newTab(tab_content)
			try: 
				tab.textView().setFontSize_(text_size)
			except: 
				pass
			
		return total_tabs

	def generateListAllPairsTabs(self, sender):
		"""Main function to generate all kern pair tabs"""
		font = Glyphs.font
		if not font: 
			Message("Error", "No font open", OKButton="OK")
			return
		
		try:
			pairs_per_tab = int(self.w.pairsInput.get())
			text_size = int(self.w.sizeInput.get())
		except:
			pairs_per_tab = 50
			text_size = 40
		
		master_id = font.selectedFontMaster.id
	
		# Auto-assign kerning groups
		self.auto_assign_kerning_groups(font)
	
		# Get all kerning pairs
		all_pairs = self.get_all_convertible_pairs(font, master_id)
	
		if not all_pairs:
			Message("No Kern Pairs", "No kerning pairs found in the font")
			return
		
		# Categorize pairs
		valid = [p for p in all_pairs if p['status'] == "VALID"]
		partial = [p for p in all_pairs if p['status'] == "PARTIAL"]
		missing = [p for p in all_pairs if p['status'] == "MISSING"]
	
		# Create tabs for each category
		vt = self.create_tabs_for_category(font, valid, "VALID", pairs_per_tab, text_size)
		pt = self.create_tabs_for_category(font, partial, "PARTIAL", pairs_per_tab, text_size - 5)
		mt = self.create_tabs_for_category(font, missing, "MISSING", pairs_per_tab, text_size - 10)
	
		# Build summary message
		summary_parts = []
		if vt: 
			summary_parts.append(f"{vt} VALID tabs ({len(valid)} pairs)")
		if pt: 
			summary_parts.append(f"{pt} PARTIAL tabs ({len(partial)} pairs)")
		if mt: 
			summary_parts.append(f"{mt} MISSING tabs ({len(missing)} pairs)")
	
		summary = " + ".join(summary_parts)
	
		# Show success message if tabs were created
		if summary_parts:
			Message("Success", f"Created: {summary}")
		else:
			Message("Info", "No kerning pairs to display")
			
			
			


	def listAllKernPairsCallback(self, sender):
		"""Callback per al botó de llistar tots els parells de kern - CON SUPPORT PARA .sc"""
		font = Glyphs.font
		if not font:
			print("⚠️ No font open")
			return

		print("\n" + "=" * 80)
		print("🧪 DEBUG — LIST ALL KERN PAIRS (CON .sc SUPPORT)")
		print("=" * 80)

		# ============================================================
		# OBTENER VALORES DE LA UI
		# ============================================================
		tab = self.w.tabs[1]  # Tools tab

		pairs_per_tab = 50
		text_size = 40
		custom_prefix_simple = ""
		custom_suffix_simple = ""

		try:
			pairs_per_tab = int(tab.kernPairsPerInput.get())
		except:
			pairs_per_tab = 50

		try:
			custom_prefix_simple = tab.prefixInput.get().strip()
		except:
			custom_prefix_simple = ""

		try:
			custom_suffix_simple = tab.suffixInput.get().strip()
		except:
			custom_suffix_simple = ""

		# ============================================================
		# OBTENER VALORES DE LAS NUEVAS CASILLAS DE PREFIX/SUFFIX
		# ============================================================
		try:
			new_prefix = tab.customPrefixInput.get().strip()
			new_suffix = tab.customSuffixInput.get().strip()
			print(f"🧪 DEBUG: Nuevos valores personalizados - Prefix: '{new_prefix}', Suffix: '{new_suffix}'")
	
			# Usar los nuevos valores si están definidos
			if new_prefix:
				custom_prefix_simple = new_prefix
			if new_suffix:
				custom_suffix_simple = new_suffix
		
			print(f"🧪 DEBUG: Valores finales - Prefix: '{custom_prefix_simple}', Suffix: '{custom_suffix_simple}'")
		except:
			print("🧪 DEBUG: No se pudieron obtener los nuevos valores de prefix/suffix")

		master = font.selectedFontMaster
		if not master:
			print("⚠️ No master selected")
			return

		master_id = master.id
		print(f"🧪 DEBUG: Master: {master.name} (ID: {master_id})")

		# ============================================================
		# FUNCIONES LOCALES (CON SUPPORT PARA .sc)
		# ============================================================

		def get_glyph_case_type(glyph_name):
			"""Determine the case type of a glyph - CON SUPPORT PARA .sc"""
			if glyph_name not in font.glyphs:
				print(f"      [CASE TYPE] Glyph '{glyph_name}' not found in font")
				return "unknown"

			# Small caps
			if '.sc' in glyph_name.lower():
				print(f"      [CASE TYPE] '{glyph_name}' → smallcaps")
				return "smallcaps"

			# Por defecto tratar como uppercase
			print(f"      [CASE TYPE] '{glyph_name}' → uppercase (por defecto)")
			return "uppercase"

		def expand_custom_value(custom_value, glyph_type="uppercase"):
			"""Expande valores personalizados aplicando lógica contextual CON .sc"""
			if not custom_value or not isinstance(custom_value, str):
				print(f"      [EXPAND] Valor vacío o no string: {custom_value}")
				if glyph_type == "smallcaps":
					return "/h.sc/h.sc"
				elif glyph_type == "lowercase":
					return "/h/h"
				else:
					return "/H/H"  # Por defecto mayúsculas

			custom_value = custom_value.strip()
			print(f"      [EXPAND] Valor a expandir: '{custom_value}' para tipo: {glyph_type}")

			# Si ya tiene formato Glyphs, devolver tal cual
			if custom_value.startswith('/'):
				print(f"      [EXPAND] Ya tiene formato Glyphs, devolviendo: {custom_value}")
				return custom_value

			# Para SMALLCAPS
			if glyph_type == "smallcaps":
				print(f"      [EXPAND] Procesando para SMALLCAPS")
		
				# Extraer solo la letra base (primera letra)
				base_letter = custom_value[0] if custom_value else "h"
		
				# Asegurar que sea minúscula para smallcaps
				if base_letter.isupper():
					base_letter = base_letter.lower()
		
				# Añadir .sc si no lo tiene
				if not base_letter.endswith('.sc'):
					base_letter_with_sc = base_letter + '.sc'
				else:
					base_letter_with_sc = base_letter
		
				# Para smallcaps, siempre usar la misma letra duplicada
				result = f"/{base_letter_with_sc}/{base_letter_with_sc}"
				print(f"      [EXPAND] Smallcaps: '{custom_value}' → '{result}'")
				return result

			# Para MAYÚSCULAS y MINÚSCULAS normales
			transformed_value = custom_value

			if glyph_type == "lowercase":
				# Convertir a minúsculas (excepto extensiones como .sc)
				if '.' not in custom_value:
					transformed_value = custom_value.lower()
				print(f"      [EXPAND] Convertido a lowercase: '{custom_value}' → '{transformed_value}'")

			else:  # uppercase por defecto
				# Convertir a mayúsculas (excepto extensiones)
				if '.' not in custom_value:
					transformed_value = custom_value.upper()
				print(f"      [EXPAND] Convertido a uppercase: '{custom_value}' → '{transformed_value}'")

			# Separar cada carácter con /
			if len(transformed_value) > 1:
				parts = list(transformed_value)
				result = '/' + '/'.join(parts)
				print(f"      [EXPAND] Separando caracteres: '{transformed_value}' → '{result}'")
				return result
			else:
				# Una sola letra, repetirla 2 veces
				result = f"/{transformed_value}/{transformed_value}"
				print(f"      [EXPAND] Una letra, duplicando: '{transformed_value}' → '{result}'")
				return result

		def get_prefix_suffix_for_pair(left_glyph, right_glyph):
			"""Get prefix and suffix strings - CON LÓGICA CONTEXTUAL PARA .sc"""
			print(f"\n    [PREFIX/SUFFIX] Para par: {left_glyph}/{right_glyph}")
	
			# Obtener tipos de glifos
			left_type = get_glyph_case_type(left_glyph)
			right_type = get_glyph_case_type(right_glyph)
	
			print(f"    [PREFIX/SUFFIX] Tipos detectados: {left_type}/{right_type}")
	
			# Usar lógica contextual
			if custom_prefix_simple:
				print(f"    [PREFIX/SUFFIX] Usando valor CUSTOM para prefijo: '{custom_prefix_simple}'")
				# Expandir aplicando lógica contextual basada en left_type
				prefix = expand_custom_value(custom_prefix_simple, left_type)
			else:
				print(f"    [PREFIX/SUFFIX] Usando lógica AUTO-CONTEXTUAL para prefijo")
				# Lógica contextual automática
				if left_type == "smallcaps":
					prefix = "/h.sc/h.sc"
				elif left_type == "lowercase":
					prefix = "/h/h"
				else:
					prefix = "/H/H"
	
			if custom_suffix_simple:
				print(f"    [PREFIX/SUFFIX] Usando valor CUSTOM para sufijo: '{custom_suffix_simple}'")
				# Expandir aplicando lógica contextual basada en right_type
				suffix = expand_custom_value(custom_suffix_simple, right_type)
			else:
				print(f"    [PREFIX/SUFFIX] Usando lógica AUTO-CONTEXTUAL para sufijo")
				# Lógica contextual automática
				if right_type == "smallcaps":
					suffix = "/h.sc/h.sc"
				elif right_type == "lowercase":
					suffix = "/h/h"
				else:
					suffix = "/H/H"
	
			print(f"    [PREFIX/SUFFIX] Resultado final: prefix='{prefix}', suffix='{suffix}'")
			print(f"    [PREFIX/SUFFIX] Basado en: {left_glyph}({left_type})/{right_glyph}({right_type})")
	
			return prefix, suffix

		def build_kern_display(left_glyph, right_glyph, kern_value):
			"""Build the display string for a kern pair with prefix and suffix"""
			print(f"\n    [BUILD DISPLAY] Construyendo display para: {left_glyph}/{right_glyph}")
	
			left_display = f"/{left_glyph}"
			right_display = f"/{right_glyph}"
	
			prefix, suffix = get_prefix_suffix_for_pair(left_glyph, right_glyph)
	
			# Verificación de seguridad
			if prefix is None:
				prefix = ""
			if suffix is None:
				suffix = ""
	
			# Asegurar formato correcto
			if prefix and not prefix.startswith('/'):
				prefix = '/' + prefix
			if suffix and not suffix.startswith('/'):
				suffix = '/' + suffix
	
			# 10 ESPACIOS en blanco entre el bloque de texto y el valor
			result = f"{prefix}{left_display}{right_display}{suffix}               {int(kern_value)}"
			print(f"          [BUILD DISPLAY] Resultado final: {result}")
			return result
	
			left_display = f"/{left_glyph}"
			right_display = f"/{right_glyph}"
	
			prefix, suffix = get_prefix_suffix_for_pair(left_glyph, right_glyph)
	
			# Verificación de seguridad
			if prefix is None:
				prefix = ""
				print(f"    [BUILD DISPLAY] ⚠️ Prefijo era None, usando vacío")
			if suffix is None:
				suffix = ""
				print(f"    [BUILD DISPLAY] ⚠️ Sufijo era None, usando vacío")
	
			# Asegurar formato correcto
			if prefix and not prefix.startswith('/'):
				prefix = '/' + prefix
				print(f"    [BUILD DISPLAY] Añadiendo / al prefijo")
			if suffix and not suffix.startswith('/'):
				suffix = '/' + suffix
				print(f"    [BUILD DISPLAY] Añadiendo / al sufijo")
	
			result = f"{prefix}{left_display}{right_display}{suffix}"
			print(f"    [BUILD DISPLAY] Resultado final: {result}")
			return result

		# ============================================================
		# CÓDIGO PRINCIPAL
		# ============================================================

		# Auto-assign kerning groups
		print(f"\n🧪 DEBUG: Auto-assigning kerning groups...")
	
		# Get all kerning pairs
		print(f"\n🧪 DEBUG: Processing kerning pairs...")
		all_pairs = []
		kerning_dict = font.kerning.get(master_id, {})

		for left_key, right_dict in kerning_dict.items():
			for right_key, kerning_value in right_dict.items():
				if kerning_value is not None:
					# Obtener nombres de glifos
					left_glyph = self.resolveKeyTurbo(left_key)
					right_glyph = self.resolveKeyTurbo(right_key)
				
					if left_glyph and right_glyph:
						all_pairs.append({
							'left': left_glyph, 
							'right': right_glyph, 
							'value': kerning_value, 
							'left_raw': left_key, 
							'right_raw': right_key
						})

		print(f"🧪 DEBUG: Found {len(all_pairs)} total kerning pairs")

		if not all_pairs:
			print("⚠️ No kerning pairs found")
			return

		# Sort kerning pairs
		print(f"🧪 DEBUG: Sorting pairs...")
	
		# Crear tabs
		total_tabs = (len(all_pairs) + pairs_per_tab - 1) // pairs_per_tab
		print(f"🧪 DEBUG: Creating {total_tabs} tabs...")

		for t in range(total_tabs):
			start = t * pairs_per_tab
			end = min(start + pairs_per_tab, len(all_pairs))
			tab_pairs = all_pairs[start:end]
	
			# Mostrar valores en el header
			header_prefix = custom_prefix_simple if custom_prefix_simple else "auto-contextual"
			header_suffix = custom_suffix_simple if custom_suffix_simple else "auto-contextual"
	
			tab_lines = [
				f"# Kerning Pairs {start+1}-{end} of {len(all_pairs)}",
				f"# Master: {master.name}",
				f"# Text size: {text_size}",
				f"# Prefix: {header_prefix}",
				f"# Suffix: {header_suffix}",
				""
			]
	
			for p in tab_pairs:
				display = build_kern_display(p['left'], p['right'], p['value'])
				tab_lines.append(display)  # Ya no se añaden espacios extras aquí
	
			tab_content = "\n".join(tab_lines)
			print(f"🧪 DEBUG: Creating tab {t+1}/{total_tabs}")
			print(f"  Content preview: {tab_content[:200]}...")
	
			font.newTab(tab_content)

		print(f"✅ Created {total_tabs} tabs")
		print("=" * 80)

		# ============================================================
		# CÓDIGO PRINCIPAL
		# ============================================================

		# Auto-assign kerning groups
		print(f"\n🧪 DEBUG: Auto-assigning kerning groups...")
		glyphs_needing_groups = set()
		kerning_dict = font.kerning.get(master_id, {})

		if kerning_dict:
			print(f"  Found kerning dict with {len(kerning_dict)} left keys")
			for left_key, right_dict in kerning_dict.items():
				for right_key, kerning_value in right_dict.items():
					if kerning_value is not None:
						if (isinstance(left_key, str) and left_key.startswith('@MMK_L_') and
							isinstance(right_key, str) and not right_key.startswith('@MMK_') and
							right_key in font.glyphs):
								glyphs_needing_groups.add((right_key, 'R'))
				
						if (isinstance(right_key, str) and right_key.startswith('@MMK_R_') and
							isinstance(left_key, str) and not left_key.startswith('@MMK_') and
							left_key in font.glyphs):
								glyphs_needing_groups.add((left_key, 'L'))

		print(f"  Glyphs needing groups from kerning: {len(glyphs_needing_groups)}")

		for glyph in font.glyphs:
			if not self.is_base_glyph(glyph):
				continue
	
			if not glyph.leftKerningGroup:
				glyphs_needing_groups.add((glyph.name, 'L'))
			if not glyph.rightKerningGroup:
				glyphs_needing_groups.add((glyph.name, 'R'))

		print(f"  Total glyphs needing groups: {len(glyphs_needing_groups)}")

		for glyph_name, side in glyphs_needing_groups:
			if glyph_name not in font.glyphs:
				continue
			glyph = font.glyphs[glyph_name]
			if side == 'L' and not glyph.leftKerningGroup:
				glyph.leftKerningGroup = glyph_name
			elif side == 'R' and not glyph.rightKerningGroup:
				glyph.rightKerningGroup = glyph_name

		# Get all kerning pairs
		print(f"\n🧪 DEBUG: Processing kerning pairs...")
		all_pairs = []
		name_fixes = {
			"a-sc": "a.sc",
			"hypen": "hyphen", 
			"guillemotright": "guillemetright", 
			"guillemotleft": "guillemetleft"
		}

		for left_key, right_dict in kerning_dict.items():
			for right_key, kerning_value in right_dict.items():
				if kerning_value is not None:
					# Apply name corrections
					if isinstance(left_key, str):
						for wrong, correct in name_fixes.items():
							left_key = left_key.replace(wrong, correct)
					if isinstance(right_key, str):
						for wrong, correct in name_fixes.items():
							right_key = right_key.replace(wrong, correct)
			
					left_glyph = None
					right_glyph = None
			
					# Process left_key
					if isinstance(left_key, str):
						if left_key.startswith('@MMK_L_'):
							group_name = left_key[7:]  # Extract group name without '@MMK_L_'
							left_glyph = group_name
					
							# Find representative glyph for left group
							if group_name in ["acir", "bcir", "tcir", "cometes"]:
								found_glyphs = find_glyph_for_group(group_name, 'R')
								if found_glyphs:
									left_glyph = found_glyphs[0]
				
						elif left_key in font.glyphs:
							left_glyph = left_key
						else:
							gname = get_glyph_name_by_id_local(left_key)
							left_glyph = gname if gname else left_key
			
					# Process right_key	 
					if isinstance(right_key, str):
						if right_key.startswith('@MMK_R_'):
							group_name = right_key[7:]	# Extract group name without '@MMK_R_'
							right_glyph = group_name
					
							# Find representative glyph for right group
							if group_name in ["acir", "bcir", "tcir", "cometes"]:
								found_glyphs = find_glyph_for_group(group_name, 'L')
								if found_glyphs:
									right_glyph = found_glyphs[0]
				
						elif right_key in font.glyphs:
							right_glyph = right_key
						else:
							gname = get_glyph_name_by_id_local(right_key)
							right_glyph = gname if gname else right_key

					if not left_glyph:
						left_glyph = left_key
					if not right_glyph:
						right_glyph = right_key
			
					if left_glyph and right_glyph:
						left_exists = left_glyph in font.glyphs
						right_exists = right_glyph in font.glyphs
						status = 'VALID' if (left_exists and right_exists) else ('PARTIAL' if left_exists or right_exists else 'MISSING')
						all_pairs.append({
							'left': left_glyph, 
							'right': right_glyph, 
							'value': kerning_value, 
							'status': status, 
							'left_raw': left_key, 
							'right_raw': right_key
						})

		print(f"🧪 DEBUG: Found {len(all_pairs)} total kerning pairs")

		if not all_pairs:
			Message("No Kerning Pairs", "No kerning pairs found for this master.", OKButton="OK")
			return

		# Sort kerning pairs by case type
		print(f"🧪 DEBUG: Sorting pairs...")
		def sort_key(pair):
			lt = get_glyph_case_type(pair['left'])
			rt = get_glyph_case_type(pair['right'])
			order = {
				("uppercase", "uppercase"): 1,
				("lowercase", "lowercase"): 4
			}
			return (order.get((lt, rt), 99), pair['left'], pair['right'])

		sorted_pairs = sorted(all_pairs, key=sort_key)

		# Categorize pairs
		valid = [p for p in sorted_pairs if p['status'] == "VALID"]
		partial = [p for p in sorted_pairs if p['status'] == "PARTIAL"]
		missing = [p for p in sorted_pairs if p['status'] == "MISSING"]

		print(f"🧪 DEBUG: Categorized:")
		print(f"  VALID: {len(valid)} pairs")
		print(f"  PARTIAL: {len(partial)} pairs")
		print(f"  MISSING: {len(missing)} pairs")

		# Create tabs for each category
		vt = create_tabs_for_category(valid, "VALID", pairs_per_tab, text_size)
		pt = create_tabs_for_category(partial, "PARTIAL", pairs_per_tab, text_size - 5)
		mt = create_tabs_for_category(missing, "MISSING", pairs_per_tab, text_size - 10)

		# Build summary message
		summary_parts = []
		if vt: 
			summary_parts.append(f"{vt} VALID tabs ({len(valid)} pairs)")
		if pt: 
			summary_parts.append(f"{pt} PARTIAL tabs ({len(partial)} pairs)")
		if mt: 
			summary_parts.append(f"{mt} MISSING tabs ({len(missing)} pairs)")

		summary = " + ".join(summary_parts)

		# Show success message if tabs were created
		if summary_parts:
			Message("Success", f"Created: {summary}", OKButton="OK")
			Glyphs.showNotification(
				"Kerning Pairs Listed",
				f"Created {vt+pt+mt} tabs with {len(all_pairs)} kerning pairs\n"
				f"Prefix: {custom_prefix_simple if custom_prefix_simple else 'auto-contextual'}\n"
				f"Suffix: {custom_suffix_simple if custom_suffix_simple else 'auto-contextual'}"
			)
		else:
			Message("Info", "No kerning pairs to display", OKButton="OK")

		print("=" * 80)
	
	
	

		
		
	def is_base_glyph(self, g):
		"""Check if glyph is a base glyph (letter, number, punctuation, symbol)"""
		return g.category in ["Letter", "Number", "Punctuation", "Symbol"]

	def collisionCheckboxClicked_(self, sender):
		"""Callback cuando se hace clic en un checkbox - PERApache2E SELECCIÓN MÚLTIPLE"""
		try:
			checkbox_index = sender.tag()
		except:
			# Backup: buscar en la lista
			for i, checkbox in enumerate(self.collisionCheckboxes):
				if checkbox == sender:
					checkbox_index = i
					break
			else:
				return
	
		if checkbox_index in self.collisionStates:
			is_checked = bool(sender.state())
		
			# 🔧 SINCRONIZAR AMBOS: NSButton Y collisionStates
			self.collisionStates[checkbox_index]['checked'] = is_checked
			self.collisionStates[checkbox_index]['checkbox'].setState_(1 if is_checked else 0)
		
			# Actualizar color de fondo
			self.updateRowBackgroundColor(checkbox_index, is_checked)
		
			print(f"✅ Checkbox {checkbox_index} sincronizado: {is_checked}")
		
			# Actualizar preview solo si está marcado
			if is_checked and checkbox_index < len(self.collisionPairs):
				left, right, pre, suf = self.collisionPairs[checkbox_index]
				self.currentCollisionPrefix = pre
				self.currentCollisionLeftGlyph = left
				self.currentCollisionRightGlyph = right
				self.currentCollisionSuffix = suf
				self.selectedCollisionIndex = checkbox_index






	def applyKerningFromPairs(self, pairs):
		"""Aplica kerning automáticamente desde una lista de pares"""
		font = Glyphs.font
		if not font:
			print("❌ No hay fuente abierta")
			return
		
		master = font.selectedFontMaster
		if not master:
			print("❌ No hay master seleccionado")
			return
		
		mid = master.id
		margin = 40	 # Valor de kerning por defecto
	
		try:
			# Intentar obtener el margen del campo de entrada
			margin = float(self.w.tabs[0].marginInput.get())
		except:
			pass
	
		applied_count = 0
		skipped_count = 0
	
		for left_name, right_name in pairs:
			if left_name not in font.glyphs or right_name not in font.glyphs:
				print(f"❌ Glyph no encontrado: {left_name} / {right_name}")
				skipped_count += 1
				continue
			
			gL = font.glyphs[left_name]
			gR = font.glyphs[right_name]
		
			# Verificar si es candidato para kerning
			if not self.isKerningCandidate(gL, gR):
				print(f"⚠️ No es candidato: {left_name} / {right_name}")
				skipped_count += 1
				continue
		
			# Calcular distancia actual
			current_distance = margin_for_pair(font, mid, left_name, right_name)
			if current_distance is None or current_distance >= 10000:
				print(f"⚠️ No se pudo calcular distancia: {left_name} / {right_name}")
				skipped_count += 1
				continue
		
			# Calcular kerning necesario
			delta = int(round(-(current_distance - margin)))
			if delta <= 0:
				print(f"⚠️ Kerning <= 0 ({delta}): {left_name} / {right_name}")
				skipped_count += 1
				continue
		
			# Aplicar kerning
			font.setKerningForPair(mid, left_name, right_name, delta)
			applied_count += 1
			print(f"✅ Kerning aplicado: {left_name} / {right_name} = {delta}")
	
		# Mostrar resumen
		if applied_count > 0:
			Glyphs.showNotification(
				"Kerning aplicado desde JSON",
				f"Aplicado a {applied_count} pares\nOApache2idos: {skipped_count}"
			)
			print(f"✅ Total: {applied_count} pares aplicados, {skipped_count} oApache2idos")
		else:
			Glyphs.showNotification(
				"Kerning JSON",
				f"No se aplicó kerning\nOApache2idos: {skipped_count}"
			)

	def applyAutoKerningFromPairs(self, pairs):
		"""Aplica kerning automáticamente usando el motor para calcular valores"""
		font = Glyphs.font
		if not font:
			print("🧪 DEBUG ERROR: No font open in applyAutoKerningFromPairs")
			return
		
		master = font.selectedFontMaster
		if not master:
			print("🧪 DEBUG ERROR: No master selected")
			return
		
		mid = master.id
	
		# Obtener margen objetivo desde la UI o usar valor por defecto
		try:
			tab = self.w.tabs[0]  # Collision Detector tab
			target_margin = float(tab.marginInput.get())
			print(f"🧪 DEBUG: Using target margin from UI: {target_margin}")
		except:
			target_margin = 40
			print(f"🧪 DEBUG: Using default margin: {target_margin}")
	
		applied_count = 0
		skipped_count = 0
		error_count = 0
	
		print(f"🧪 DEBUG: Starting kerning application for {len(pairs)} pairs...")
	
		for i, (left_name, right_name) in enumerate(pairs):
			print(f"\n🧪 DEBUG: Processing pair {i+1}/{len(pairs)}: {left_name}/{right_name}")
		
			# Verificar si los glifos existen
			if left_name not in font.glyphs:
				print(f"🧪 DEBUG ERROR: Left glyph '{left_name}' not found")
				error_count += 1
				continue
			
			if right_name not in font.glyphs:
				print(f"🧪 DEBUG ERROR: Right glyph '{right_name}' not found")
				error_count += 1
				continue
			
			gL = font.glyphs[left_name]
			gR = font.glyphs[right_name]
		
			# Verificar si es candidato para kerning
			if not self.isKerningCandidate(gL, gR):
				print(f"🧪 DEBUG SKIP: Not a kerning candidate ({gL.category}/{gR.category})")
				skipped_count += 1
				continue
		
			# Verificar si ya tiene kerning
			if self.hasKerning(font, mid, gL, gR):
				print(f"🧪 DEBUG SKIP: Already has kerning")
				skipped_count += 1
				continue
		
			# Calcular distancia actual usando el motor
			print(f"🧪 DEBUG: Calculating current distance...")
			current_distance = margin_for_pair(font, mid, left_name, right_name)
		
			if current_distance is None:
				print(f"🧪 DEBUG ERROR: Could not calculate distance (None)")
				error_count += 1
				continue
			
			if current_distance >= 10000:
				print(f"🧪 DEBUG ERROR: Distance too large ({current_distance})")
				error_count += 1
				continue
		
			print(f"🧪 DEBUG: Current distance: {current_distance:.1f}")
			print(f"🧪 DEBUG: Target margin: {target_margin}")
		
			# Calcular kerning necesario
			delta = int(round(-(current_distance - target_margin)))
			print(f"🧪 DEBUG: Calculated delta: {delta}")
		
			if delta <= 0:
				print(f"🧪 DEBUG SKIP: Delta <= 0 (no kerning needed)")
				skipped_count += 1
				continue
		
			# Aplicar kerning
			try:
				print(f"🧪 DEBUG: Applying kerning: {left_name} / {right_name} = {delta}")
				font.setKerningForPair(mid, left_name, right_name, delta)
			
				# Verificar que se aplicó correctamente
				applied_value = font.kerningForPair(mid, left_name, right_name)
				if applied_value == delta:
					print(f"🧪 DEBUG SUCCESS: Kerning applied and verified")
					applied_count += 1
				else:
					print(f"🧪 DEBUG ERROR: Applied {applied_value} but expected {delta}")
					error_count += 1
				
			except Exception as e:
				print(f"🧪 DEBUG ERROR: Exception applying kerning: {e}")
				error_count += 1
	
		# Mostrar resumen
		print(f"\n🧪 DEBUG SUMMARY:")
		print(f"  Total pairs: {len(pairs)}")
		print(f"  Applied: {applied_count}")
		print(f"  Skipped: {skipped_count}")
		print(f"  Errors: {error_count}")
	
		if applied_count > 0:
			alert = NSAlert.alloc().init()
			alert.setMessageText_("Kerning aplicado desde JSON")
			alert.setInformativeText_(
				f"✅ Kerning aplicado automáticamente\n\n"
				f"• Pares procesados: {len(pairs)}\n"
				f"• Aplicado: {applied_count} pares\n"
				f"• OApache2idos: {skipped_count}\n"
				f"• Errores: {error_count}"
			)
			alert.addButtonWithTitle_("OK")
			alert.runModal()
		
			Glyphs.showNotification(
				"Kerning aplicado",
				f"Aplicado a {applied_count} pares desde JSON"
			)
		else:
			alert = NSAlert.alloc().init()
			alert.setMessageText_("No se aplicó kerning")
			alert.setInformativeText_(
				f"No se pudo aplicar kerning a los pares importados.\n\n"
				f"• Pares procesados: {len(pairs)}\n"
				f"• Aplicado: {applied_count}\n"
				f"• OApache2idos: {skipped_count}\n"
				f"• Errores: {error_count}\n\n"
				f"Revisa la consola para más detalles."
			)
			alert.addButtonWithTitle_("OK")
			alert.runModal()

def margin_for_pair(font, masterID, leftName, rightName):
	"""DEBUG VERSION: Obtiene la distancia entre dos glifos"""
	print(f"🧪 DEBUG margin_for_pair: {leftName} / {rightName}")
	
	gL = font.glyphs[leftName]
	gR = font.glyphs[rightName]
	if not gL or not gR:
		print(f"🧪 DEBUG ERROR: One or both glyphs not found")
		return None

	print(f"🧪 DEBUG: Getting layers...")
	layerL = gL.layers[masterID]
	layerR = gR.layers[masterID]

	try:
		layerL = layerL.copyDecomposedLayer()
		print(f"🧪 DEBUG: Decomposed left layer")
	except:
		print(f"🧪 DEBUG: Could not decompose left layer")

	try:
		layerR = layerR.copyDecomposedLayer()
		print(f"🧪 DEBUG: Decomposed right layer")
	except:
		print(f"🧪 DEBUG: Could not decompose right layer")

	dx = layerL.width
	print(f"🧪 DEBUG: Left width = {dx}")
	
	distance = minDistanceBetweenLayers(layerL, layerR, dx)
	print(f"🧪 DEBUG: Calculated distance = {distance}")
	
	return distance

	def isKerningCandidate(self, gL, gR):
		print(f"🧪 DEBUG isKerningCandidate: {gL.name if gL else 'None'} / {gR.name if gR else 'None'}")
	
		if not gL or not gR:
			print(f"🧪 DEBUG: One or both glyphs are None")
			return False

		# Nunca espacios
		if gL.category == "Space" or gR.category == "Space":
			print(f"🧪 DEBUG: Space glyph")
			return False

		# Nunca marks combinantes
		if gL.category == "Mark" or gR.category == "Mark":
			print(f"🧪 DEBUG: Mark glyph")
			return False

		# Nunca símbolos
		if gL.category == "Symbol" or gR.category == "Symbol":
			print(f"🧪 DEBUG: Symbol glyph")
			return False

		# Opcional: excluir puntuación
		if gL.category == "Punctuation" or gR.category == "Punctuation":
			print(f"🧪 DEBUG: Punctuation glyph")
			return False

		# Excluir glifos técnicos
		banned = (
			".case", ".comb", ".init", ".medi", ".fina",
			".isol", ".liga", ".calt", ".locl"
		)

		for b in banned:
			if b in gL.name or b in gR.name:
				print(f"🧪 DEBUG: Contains banned substring '{b}'")
				return False

		print(f"🧪 DEBUG: Is a valid kerning candidate")
		return True



		
		


	def get_glyph_case_type(self, glyph_name):
		"""Determine the case type of a glyph (uppercase, lowercase, smallcaps, etc.)"""
		font = Glyphs.font
		if glyph_name not in font.glyphs:
			return "unknown"
		g = font.glyphs[glyph_name]
	
		# Primero verificar por nombre específico
		if glyph_name.endswith('.sc') or '.sc.' in glyph_name:
			return "smallcaps"
		
		# Verificar si es mayúscula por nombre
		if glyph_name in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
						 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
						 'Aacute', 'Agrave', 'Acircumflex', 'Adieresis', 'Atilde', 'Aring',
						 'Abreve', 'Amacron', 'Aogonek', 'Acaron', 'Acircumflexacute',
						 'Acircumflexgrave', 'Acircumflexhook', 'Acircumflextilde',
						 'Acircumflexdotbelow', 'Abreveacute', 'Abrevegrave',
						 'Abrevehook', 'Abrevetilde', 'Abrevedotbelow',
						 'Adotbelow', 'Ahook', 'Atildeacute', 'Atildegrave',
						 'Eacute', 'Egrave', 'Ecircumflex', 'Edieresis', 'Emacron',
						 'Ebreve', 'Edotaccent', 'Eogonek', 'Ecaron', 'Ecircumflexacute',
						 'Ecircumflexgrave', 'Ecircumflexhook', 'Ecircumflextilde',
						 'Ecircumflexdotbelow', 'Edieresisacute', 'Edieresiscaron',
						 'Edotbelow', 'Ehook', 'Etilde', 'Iacute', 'Igrave',
						 'Icircumflex', 'Idieresis', 'Imacron', 'Ibreve',
						 'Itilde', 'Idotaccent', 'Iogonek', 'Icircumflexacute',
						 'Icircumflexgrave', 'Icircumflexhook', 'Icircumflextilde',
						 'Icircumflexdotbelow', 'Idieresisacute', 'Idieresiscaron',
						 'Idotbelow', 'Ihook', 'Itildeacute', 'Itildegrave',
						 'Oacute', 'Ograve', 'Ocircumflex', 'Odieresis', 'Otilde',
						 'Omacron', 'Obreve', 'Oslash', 'Oogonek', 'Ocaron',
						 'Ocircumflexacute', 'Ocircumflexgrave', 'Ocircumflexhook',
						 'Ocircumflextilde', 'Ocircumflexdotbelow', 'Oslashacute',
						 'Oslashgrave', 'Odieresisacute', 'Odieresiscaron',
						 'Odotbelow', 'Ohook', 'Otildeacute', 'Otildegrave',
						 'Uacute', 'Ugrave', 'Ucircumflex', 'Udieresis', 'Umacron',
						 'Ubreve', 'Uring', 'Uogonek', 'Ucaron', 'Ucircumflexacute',
						 'Ucircumflexgrave', 'Ucircumflexhook', 'Ucircumflextilde',
						 'Ucircumflexdotbelow', 'Udieresisacute', 'Udieresiscaron',
						 'Udotbelow', 'Uhook', 'Utilde', 'Yacute', 'Ygrave',
						 'Ycircumflex', 'Ydieresis', 'Ymacron', 'Ybreve',
						 'Ytilde', 'Ydotaccent', 'Ycaron', 'Ycircumflexacute',
						 'Ycircumflexgrave', 'Ycircumflexhook', 'Ycircumflextilde',
						 'Ycircumflexdotbelow', 'Ydieresisacute', 'Ydieresiscaron',
						 'Ydotbelow', 'Yhook', 'AE', 'OE', 'Eth', 'Thorn',
						 'Eng', 'Kra', 'Ldot', 'Lslash', 'Nacute', 'Ntilde',
						 'Oslash', 'Sacute', 'Scaron', 'Scedilla', 'Tbar',
						 'Zacute', 'Zcaron', 'Zdotaccent', 'Germandbls',
						 'Aringacute', 'Cacute', 'Ccaron', 'Ccedilla',
						 'Dcaron', 'Dcroat', 'Etilde', 'Gbreve', 'Gcircumflex',
						 'Gcommaaccent', 'Hbar', 'Hcircumflex', 'IJ', 'Jcircumflex',
						 'Lacute', 'Lcaron', 'Lcommaaccent', 'Ncaron',
						 'Ncommaaccent', 'Ntildeacute', 'Ohorn', 'Racute',
						 'Rcaron', 'Rcommaaccent', 'Scommaaccent', 'Tacute',
						 'Tcaron', 'Tcedilla', 'Tcommaaccent', 'Uhorn',
						 'Uringacute', 'Ytildeacute']:
			return "uppercase"
		
		# Verificar si es minúscula por nombre
		if glyph_name in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
						 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
						 'aacute', 'agrave', 'acircumflex', 'adieresis', 'atilde', 'aring',
						 'abreve', 'amacron', 'aogonek', 'acaron', 'acircumflexacute',
						 'acircumflexgrave', 'acircumflexhook', 'acircumflextilde',
						 'acircumflexdotbelow', 'abreveacute', 'abrevegrave',
						 'abrevehook', 'abrevetilde', 'abrevedotbelow',
						 'adotbelow', 'ahook', 'atildeacute', 'atildegrave',
						 'eacute', 'egrave', 'ecircumflex', 'edieresis', 'emacron',
						 'ebreve', 'edotaccent', 'eogonek', 'ecaron', 'ecircumflexacute',
						 'ecircumflexgrave', 'ecircumflexhook', 'ecircumflextilde',
						 'ecircumflexdotbelow', 'edieresisacute', 'edieresiscaron',
						 'edotbelow', 'ehook', 'etilde', 'iacute', 'igrave',
						 'icircumflex', 'idieresis', 'imacron', 'ibreve',
						 'itilde', 'idotaccent', 'iogonek', 'icircumflexacute',
						 'icircumflexgrave', 'icircumflexhook', 'icircumflextilde',
						 'icircumflexdotbelow', 'idieresisacute', 'idieresiscaron',
						 'idotbelow', 'ihook', 'itildeacute', 'itildegrave',
						 'oacute', 'ograve', 'ocircumflex', 'odieresis', 'otilde',
						 'omacron', 'obreve', 'oslash', 'oogonek', 'ocaron',
						 'ocircumflexacute', 'ocircumflexgrave', 'ocircumflexhook',
						 'ocircumflextilde', 'ocircumflexdotbelow', 'oslashacute',
						 'oslashgrave', 'odieresisacute', 'odieresiscaron',
						 'odotbelow', 'ohook', 'otildeacute', 'otildegrave',
						 'uacute', 'ugrave', 'ucircumflex', 'udieresis', 'umacron',
						 'ubreve', 'uring', 'uogonek', 'ucaron', 'ucircumflexacute',
						 'ucircumflexgrave', 'ucircumflexhook', 'ucircumflextilde',
						 'ucircumflexdotbelow', 'udieresisacute', 'udieresiscaron',
						 'udotbelow', 'uhook', 'utilde', 'yacute', 'ygrave',
						 'ycircumflex', 'ydieresis', 'ymacron', 'ybreve',
						 'ytilde', 'ydotaccent', 'ycaron', 'ycircumflexacute',
						 'ycircumflexgrave', 'ycircumflexhook', 'ycircumflextilde',
						 'ycircumflexdotbelow', 'ydieresisacute', 'ydieresiscaron',
						 'ydotbelow', 'yhook', 'ae', 'oe', 'eth', 'thorn',
						 'eng', 'kra', 'ldot', 'lslash', 'nacute', 'ntilde',
						 'oslash', 'sacute', 'scaron', 'scedilla', 'tbar',
						 'zacute', 'zcaron', 'zdotaccent', 'germandbls',
						 'aringacute', 'cacute', 'ccaron', 'ccedilla',
						 'dcaron', 'dcroat', 'etilde', 'gbreve', 'gcircumflex',
						 'gcommaaccent', 'hbar', 'hcircumflex', 'ij', 'jcircumflex',
						 'lacute', 'lcaron', 'lcommaaccent', 'ncaron',
						 'ncommaaccent', 'ntildeacute', 'ohorn', 'racute',
						 'rcaron', 'rcommaaccent', 'scommaaccent', 'tacute',
						 'tcaron', 'tcedilla', 'tcommaaccent', 'uhorn',
						 'uringacute', 'ytildeacute', 'f_f', 'f_f_i', 'f_f_l',
						 'f_i', 'f_l', 's_t', 'longs_t']:
			return "lowercase"
	
		# Verificar por categoría y Unicode
		if hasattr(g, 'unicode') and g.unicode:
			try:
				char = chr(int(g.unicode, 16))
				if char.isupper(): 
					return "uppercase"
				elif char.islower(): 
					return "lowercase"
				elif char.isdigit(): 
					return "number"
			except: 
				pass
	
		# Heurística por nombre
		if glyph_name[0].isupper(): 
			return "uppercase"
		elif glyph_name[0].islower(): 
			return "lowercase"
	
		return "unknown"

		
	def format_context(context_str, glyph_name):
		"""
		Rep NOMÉS STRING.
		Retorna /x/y
		"""
		context_str = normalize_context(context_str)

		if not context_str:
			if '.sc' in glyph_name.lower():
				return "/h.sc/h.sc"
			elif glyph_name and glyph_name[0].islower():
				return "/h/h"
			else:
				return "/H/H"

		# Ja està en format /x/y
		if context_str.startswith("/") and context_str.count("/") >= 2:
			return context_str

		# Sense barres: usar caràcters
		if len(context_str) >= 2:
			return f"/{context_str[0]}/{context_str[1]}"

		return f"/{context_str[0]}/{context_str[0]}"
		
		
	def get_prefix_suffix_for_pair(self, left_glyph, right_glyph):
		"""Get prefix and suffix strings based on glyph case types - CORREGIDO"""
		left_type = self.get_glyph_case_type(left_glyph)
		right_type = self.get_glyph_case_type(right_glyph)

		# REGLA 1: Si izquierda es mayúscula o número, usar contexto mayúscula
		if left_type in ["uppercase", "number"]: 
			if right_type in ["uppercase", "number"]:
				# Ambos mayúsculas/números: usar contexto todo mayúsculas
				prefix = "/H/H/O/H"
				suffix = "/H/O/O/H"
			else:
				# Izquierda mayúscula, derecha minúscula: contexto mixto
				prefix = "/H/H/O/H"
				suffix = "/h/o/o/h"
	
		# REGLA 2: Si izquierda es minúscula, usar contexto minúscula  
		elif left_type == "lowercase": 
			if right_type in ["uppercase", "number"]:
				# Izquierda minúscula, derecha mayúscula: contexto mixto
				prefix = "/h/h/o/h"
				suffix = "/H/O/O/H"
			else:
				# Ambos minúsculas: usar contexto todo minúsculas
				prefix = "/h/h/o/h"
				suffix = "/h/o/o/h"
	
		# REGLA 3: Si izquierda es smallcaps
		elif left_type == "smallcaps": 
			if right_type == "smallcaps":
				# Ambos smallcaps
				prefix = "/h.sc/h.sc/o.sc/h.sc"
				suffix = "/h.sc/o.sc/o.sc/h.sc"
			elif right_type in ["uppercase", "number"]:
				# Smallcaps + mayúscula: usar smallcaps izquierda, mayúscula derecha
				prefix = "/h.sc/h.sc/o.sc/h.sc"
				suffix = "/H/O/O/H"
			else:
				# Smallcaps + minúscula: usar smallcaps izquierda, minúscula derecha
				prefix = "/h.sc/h.sc/o.sc/h.sc"
				suffix = "/h/o/o/h"
	
		# REGLA 4: Caso por defecto (para unknown u otros)
		else:
			if right_type in ["uppercase", "number"]:
				prefix = "/H/H/O/H"
				suffix = "/H/O/O/H"
			else:
				prefix = "/h/h/o/h"
				suffix = "/h/o/o/h"
	
		return prefix, suffix

	def build_kern_display(self, left_glyph, right_glyph):
		"""Build the display string for a kern pair with proper prefix and suffix - CORREGIDO"""
		left_display = f"/{left_glyph}"
		right_display = f"/{right_glyph}"
		prefix, suffix = self.get_prefix_suffix_for_pair(left_glyph, right_glyph)
	
		# IMPORTANTE: Usar solo el par principal sin glifos extra en medio
		return f"{prefix}{left_display}{right_display}{suffix}"


				
	def get_context_strings(self, left_name, right_name):
		"""
		Retorna (prefix, suffix) amb el mateix comportament
		que al Kern Coach.
		"""

		font = Glyphs.font
		if not font:
			return "", ""

		left_glyph = font.glyphs[left_name] if left_name in font.glyphs else None
		right_glyph = font.glyphs[right_name] if right_name in font.glyphs else None

		# ------------------------------------------------
		# Determinar caixa del glif
		# ------------------------------------------------
		def glyph_case(g):
			if not g:
				return "UPPER"

			sub = getattr(g, "subCategory", None)
			if sub == "Lowercase":
				return "LOWER"
			if sub in ("Uppercase", "Smallcaps"):
				return "UPPER"

			base = g.name.split(".")[0]
			if base.islower():
				return "LOWER"
			if base.isupper():
				return "UPPER"

			return "UPPER"

		left_case = glyph_case(left_glyph)
		right_case = glyph_case(right_glyph)

		# ------------------------------------------------
		# Llegir camps UI (si existeixen)
		# ------------------------------------------------
		def read_field(tab, *names):
			for n in names:
				if hasattr(tab, n):
					try:
						return tab.__dict__[n].get().strip()
					except Exception:
						pass
			return ""

		tab = self.w.tabs[0]  # Collision Detector

		ui_prefix = read_field(
			tab,
			"prefixEdit", "prefixField", "prefixInput", "prefixText"
		)
		ui_suffix = read_field(
			tab,
			"suffixEdit", "suffixField", "suffixInput", "suffixText"
		)

		# ------------------------------------------------
		# Construir patrons
		# ------------------------------------------------
		if ui_prefix:
			prefix_pattern = ui_prefix.lower() if left_case == "LOWER" else ui_prefix.upper()
		else:
			prefix_pattern = ""

		if ui_suffix:
			suffix_pattern = ui_suffix.lower() if right_case == "LOWER" else ui_suffix.upper()
		else:
			suffix_pattern = ""

		# ------------------------------------------------
		# Convertir a format Glyphs
		# ------------------------------------------------
		prefix = "".join(f"/{c}" for c in prefix_pattern) if prefix_pattern else ""
		suffix = "".join(f"/{c}" for c in suffix_pattern) if suffix_pattern else ""

		return prefix, suffix
				










	# ============================================================
	# KERNING GROUP MANAGER FUNCTIONS - INTEGRADAS
	# ============================================================
	
	def kgmGetGroupGlyphs(self, group, side):
		"""Get glyphs in a kerning group with custom ordering"""
		font = Glyphs.font
		if not font or not group:
			return []
	
		# Check for custom order in userData
		key = f"kernOrder_{side}"
		custom_order = font.userData.get(key, {}).get(group, [])
	
		# Get all glyphs in this group
		glyph_names = [g.name for g in font.glyphs if getattr(g, side + "KerningGroup") == group]
	
		# Apply custom order if exists
		if custom_order:
			valid_order = [name for name in custom_order if name in glyph_names]
			remaining = [name for name in glyph_names if name not in valid_order]
			glyph_names = valid_order + sorted(remaining)
		else:
			glyph_names = sorted(glyph_names)  # Default alphabetical order
	
		# Format with trophy emoji for leader
		formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyph_names)]
	
		return formatted

	def kgmActiveGroupTab(self):
		"""Get information about the currently active group tab"""
		tab = self.w.tabs[1]
		tab_index = tab.managerTabs.get()
		font = Glyphs.font
		if not font or not font.selectedLayers:
			return None, None, None
	
		glyph = font.selectedLayers[0].parent
		if tab_index == 0:
			return "left", glyph.leftKerningGroup, tab.managerTabs[0].list
		else:
			return "right", glyph.rightKerningGroup, tab.managerTabs[1].list

	def kgmRefreshGroups(self, sender=None):
		"""Refresh the group lists based on selected glyph"""
		font = Glyphs.font
		tab = self.w.tabs[1]
	
		if not font or not font.selectedLayers:
			self.kgmShowNoGlyphSelected()
			return
	
		glyph = font.selectedLayers[0].parent
		glyph_name = glyph.name
	
		# Update current glyph display
		tab.currentGlyphName.set(glyph_name)
	
		# Get group information
		leftGroup = glyph.leftKerningGroup
		rightGroup = glyph.rightKerningGroup
	
		# Update left group list
		if leftGroup:
			tab.managerTabs[0].list.set(self.kgmGetGroupGlyphs(leftGroup, "left"))
			tab.managerStatus.set(f"Left group: {leftGroup} ({len(self.kgmGetGroupGlyphs(leftGroup, 'left'))} glyphs)")
		else:
			tab.managerTabs[0].list.set(["No left group"])
	
		# Update right group list
		if rightGroup:
			tab.managerTabs[1].list.set(self.kgmGetGroupGlyphs(rightGroup, "right"))
			if leftGroup:
				tab.managerStatus.set(f"Left: {leftGroup}, Right: {rightGroup}")
			else:
				tab.managerStatus.set(f"Right group: {rightGroup} ({len(self.kgmGetGroupGlyphs(rightGroup, 'right'))} glyphs)")
		else:
			tab.managerTabs[1].list.set(["No right group"])

	def kgmMakeFirst(self, sender):
		"""Set selected glyph as the first/leader of the group"""
		side, group, listView = self.kgmActiveGroupTab()
		if not group:
			Message(f"No {side} group for selected glyph")
			return
	
		sel = listView.getSelection()
		if not sel:
			Message("No glyph selected in group list")
			return
	
		selected_name = listView[sel[0]].replace("🏆", "").strip()
	
		# Ask for confirmation
		from vanilla.dialogs import askYesNo
		if not askYesNo(f"Set '{selected_name}' as first glyph for {side} group '{group}'?"):
			return
	
		# Reorder the list
		glyphs = [n.replace("🏆", "").strip() for n in listView]
		glyphs.remove(selected_name)
		glyphs.insert(0, selected_name)
	
		# Format with trophy emoji
		formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyphs)]
		listView.set(formatted)
	
		Message(f"'{selected_name}' is now first in {side} group")

	def kgmApplyOrder(self, sender):
		"""Apply the current order to the group (save to font)"""
		side, group, listView = self.kgmActiveGroupTab()
		if not group:
			Message(f"No {side} group for selected glyph")
			return
	
		order = [n.replace("🏆", "").strip() for n in listView]
		font = Glyphs.font
		key = f"kernOrder_{side}"
	
		# Save order to font's userData
		if not font.userData.get(key):
			font.userData[key] = {}
		font.userData[key][group] = order
	
		tab = self.w.tabs[1]
		tab.managerStatus.set(f"Order applied to {side} group '{group}'")
		Message(f"Order applied to {side} group '{group}'")

	def kgmShowNoGlyphSelected(self):
		"""Show placeholder when no glyph is selected"""
		tab = self.w.tabs[1]
		tab.currentGlyphName.set("None selected")
		tab.managerTabs[0].list.set(["Select a glyph"])
		tab.managerTabs[1].list.set(["Select a glyph"])
		tab.managerStatus.set("Select a glyph to view its kerning groups")
		

	# ===================================================
	# MÉTODOS PARA EL LISTADOR DE PARES (INTEGRADO)
	# ===================================================

	def resolveKeyTurbo(self, key):
		"""TURBO: Fast key resolution with caching"""
		font = Glyphs.font
		if not font:
			return str(key)

		if not isinstance(key, str):
			return str(key)

		# TURBO: Cache for frequently resolved keys
		if key in self._keyCache:
			return self._keyCache[key]

		result = key
	
		# TURBO: Fast pattern matching
		if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
			result = key.split("_", 2)[-1]
		elif key.startswith("@") and "_" not in key:
			result = key[1:]
		elif len(key) == 36 and key.count("-") == 4:  # UUID
			g = font.glyphForId_(key)
			if g:
				result = g.name

		# TURBO: Cache result
		self._keyCache[key] = result
	
		return result

	def charToProductionNameTurbo(self, char_or_name):
		"""TURBO: Fast character to production name conversion"""
		print(f"🧪 DEBUG charToProductionNameTurbo: input='{char_or_name}' (type: {type(char_or_name)})")
	
		font = Glyphs.font
		if not font:
			return char_or_name
		
		# TURBO: Cache for production names
		if char_or_name in self._productionCacheTurbo:
			result = self._productionCacheTurbo[char_or_name]
			print(f"🧪 DEBUG: From cache: '{result}'")
			return result
		
		result = char_or_name
	
		# TURBO: Quick font glyph check
		if char_or_name in font.glyphs:
			result = char_or_name
			print(f"🧪 DEBUG: Found in font glyphs: '{result}'")
		else:
			# TURBO: Fast unicode lookup
			for glyph in font.glyphs:
				if glyph.unicode:
					try:
						if chr(int(glyph.unicode, 16)) == char_or_name:
							result = glyph.name
							print(f"🧪 DEBUG: Found by unicode '{char_or_name}': '{result}'")
							break
					except:
						continue
		
			# TURBO: Common character mapping
			char_map = {
				'7': 'seven', '@': 'at', '&': 'ampersand', '#': 'numbersign',
				'$': 'dollar', '%': 'percent', '*': 'asterisk', '+': 'plus',
				'-': 'hyphen', '=': 'equal', '<': 'less', '>': 'greater',
				'?': 'question', '!': 'exclam', '"': 'quotedbl', "'": 'quotesingle',
				'(': 'parenleft', ')': 'parenright', '[': 'bracketleft',
				']': 'bracketright', '{': 'braceleft', '}': 'braceright',
				'/': 'slash', '\\': 'backslash', '|': 'bar', ':': 'colon',
				';': 'semicolon', ',': 'comma', '.': 'period'
			}
			if char_or_name in char_map:
				result = char_map[char_or_name]
				print(f"🧪 DEBUG: Mapped from char_map: '{result}'")

		# TURBO: Cache result
		self._productionCacheTurbo[char_or_name] = result
	
		print(f"🧪 DEBUG: Returning: '{result}'")
		return result

	def nameToGraphicalRepresentationTurbo(self, name):
		"""TURBO: Convert production name to graphical character for display"""
		font = Glyphs.font
		if not font:
			return name
		
		# TURBO: Cache for graphical representations
		if name in self._graphicalCache:
			return self._graphicalCache[name]
		
		result = name
	
		# TURBO: Check if it's a production name that should be shown as character
		production_to_char = {
			'seven': '7', 'at': '@', 'ampersand': '&', 'numbersign': '#',
			'dollar': '$', 'percent': '%', 'asterisk': '*', 'plus': '+',
			'hyphen': '-', 'equal': '=', 'less': '<', 'greater': '>',
			'question': '?', 'exclam': '!', 'quotedbl': '"', 'quotesingle': "'",
			'parenleft': '(', 'parenright': ')', 'bracketleft': '[',
			'bracketright': ']', 'braceleft': '{', 'braceright': '}',
			'slash': '/', 'backslash': '\\', 'bar': '|', 'colon': ':',
			'semicolon': ';', 'comma': ',', 'period': '.'
		}
	
		# TURBO: Convert production name to character if possible
		if name in production_to_char:
			result = production_to_char[name]
		else:
			# TURBO: Try to get unicode character for other glyphs
			if name in font.glyphs:
				g = font.glyphs[name]
				if g.unicode:
					try:
						result = chr(int(g.unicode, 16))
					except:
						pass

		# TURBO: Cache result
		self._graphicalCache[name] = result
	
		return result

	def scriptOrderTurbo(self, ch):
		"""TURBO: Fast script-based ordering"""
		if not ch:
			return (9, ch)
	
		try:
			cp = ord(ch[0])
		except:
			return (9, ch)

		# TURBO: Quick unicode range checks
		if 0x0041 <= cp <= 0x024F: return (0, ch)  # Latin
		if 0x0370 <= cp <= 0x03FF: return (1, ch)  # Greek	
		if 0x0400 <= cp <= 0x052F: return (2, ch)  # Cyrillic
		return (3, ch)	# Other

	def contextualDisplayTurbo(self, L, R, val):
		"""Genera líneas compactas para tab: /H/H/B/ì/H/H 1064"""
		print(f"🧪 DEBUG contextualDisplayTurbo: L='{L}', R='{R}', val={val}")
	
		if isinstance(L, str): L = L.strip()
		if isinstance(R, str): R = R.strip()
	
		Lprod = self.charToProductionNameTurbo(L)
		Rprod = self.charToProductionNameTurbo(R)
	
		# TRUNCAR nombres largos para bloques visualmente compactos
		Lprod = str(Lprod).strip()[:8] if Lprod else ""	 # máx 8 chars
		Rprod = str(Rprod).strip()[:8] if Rprod else ""
	
		result = f"/H/H/{Lprod}/{Rprod}/H/H {val}"
		print(f"🧪 DEBUG: Final result='{result}' ({len(result)})")
		return result



	def refreshPairsList(self, sender=None):
		"""TURBO: High-performance list refresh - SHOWS GRAPHICAL REPRESENTATION"""
		font = Glyphs.font
		if not font:
			Message("No font", "Please open a font first.", OKButton="OK")
			return
		
		tab = self.w.tabs[1]
		mid = font.selectedFontMaster.id
	
		# Asegurar que las variables existen
		if not hasattr(self, '_kerningCacheTurbo'):
			self._kerningCacheTurbo = {}
		if not hasattr(self, '_allPairsTurbo'):
			self._allPairsTurbo = []
		if not hasattr(self, '_currentDisplayPairsTurbo'):
			self._currentDisplayPairsTurbo = []
	
		# TURBO: Cache kerning data
		if mid in self._kerningCacheTurbo:
			kerning = self._kerningCacheTurbo[mid]
		else:
			kerning = font.kerning.get(mid, {})
			self._kerningCacheTurbo[mid] = kerning

		rows = []
		seen = set()

		# TURBO: Optimized kerning processing
		for LK, rightDict in kerning.items():
			for RK, val in rightDict.items():
				try:
					val_int = int(val)
				except (TypeError, ValueError):
					continue

				# TURBO: Fast key resolution
				L0 = self.resolveKeyTurbo(LK)
				R0 = self.resolveKeyTurbo(RK)

				# TURBO: Convert to production names for internal processing
				L_prod = self.charToProductionNameTurbo(L0)
				R_prod = self.charToProductionNameTurbo(R0)

				# TURBO: Convert to graphical representation for DISPLAY
				L_display = self.nameToGraphicalRepresentationTurbo(L_prod)
				R_display = self.nameToGraphicalRepresentationTurbo(R_prod)

				uniq = (L_prod, R_prod, val_int)  # Use production names for uniqueness
				if uniq in seen:
					continue
				seen.add(uniq)

				rows.append({
					"Left": L_display,	# SHOW GRAPHICAL CHARACTER
					"Right": R_display, # SHOW GRAPHICAL CHARACTER
					"Value": val_int,
					"_display": self.contextualDisplayTurbo(L0, R0, val_int),  # Uses production names for tab
					"_scriptL": self.scriptOrderTurbo(L_display),  # Sort by graphical representation
					"_scriptR": self.scriptOrderTurbo(R_display),  # Sort by graphical representation
					"_originalLeft": L0,
					"_originalRight": R0,
					"_productionLeft": L_prod,	# Store production name for tab generation
					"_productionRight": R_prod, # Store production name for tab generation
					"_sortValue": val_int,
				})

		# TURBO: Fast sorting with script blocks
		rows.sort(key=lambda r: (r["_scriptL"][0], r["_scriptR"][0], r["Left"], r["Right"]))

		# TURBO: Efficient separator insertion
		final = []
		lastBlock = None
		for r in rows:
			blk = r["_scriptL"][0]
			if lastBlock is not None and blk != lastBlock:
				final.append({"Left": "────", "Right": "────", "Value": "──", "_isSeparator": True})
			final.append({
				"Left": r["Left"],		# Graphical character for display
				"Right": r["Right"],	# Graphical character for display
				"Value": str(r["Value"]),
				"_originalData": r		# Contains production names for tab
			})
			lastBlock = blk

		self._allPairsTurbo = final
		self._currentDisplayPairsTurbo = final
		tab.pairsList.set(final)
	
		# Mostrar mensaje de éxito
		pair_count = len([r for r in final if not r.get("_isSeparator", False)])
		Message(f"Kerning pairs loaded", f"Loaded {pair_count} kerning pairs.", OKButton="OK")

	def clearPairsSearch(self, sender):
		"""TURBO: Instant search clear"""
		tab = self.w.tabs[1]
		tab.searchPairs.set("")
	
		# Asegurar que la variable existe
		if not hasattr(self, '_allPairsTurbo'):
			self._allPairsTurbo = []
	
		tab.pairsList.set(self._allPairsTurbo)
		self._currentDisplayPairsTurbo = self._allPairsTurbo

	def filterPairsList(self, sender):
		"""TURBO: Fast search filtering - SEARCHES BOTH GRAPHICAL AND PRODUCTION NAMES"""
		tab = self.w.tabs[1]
		q = sender.get().strip()
		if not q:
			self.clearPairsSearch(None)
			return

		# Asegurar que la variable existe
		if not hasattr(self, '_allPairsTurbo'):
			self._allPairsTurbo = []
			self._currentDisplayPairsTurbo = []
	
		# TURBO: Quick exact match detection
		if q.endswith(","):
			exact = q[:-1].strip()
			filtered = [r for r in self._allPairsTurbo if r["Left"] == exact or r["Right"] == exact]
		else:
			# TURBO: Fast substring search in BOTH graphical and production names
			ql = q.lower()
			filtered = []
			for r in self._allPairsTurbo:
				original_data = r.get("_originalData", {})
				# Search in displayed graphical characters
				if (ql in r["Left"].lower() or 
					ql in r["Right"].lower() or 
					ql in str(r["Value"]) or
					# Also search in production names for better searchability
					ql in original_data.get("_productionLeft", "").lower() or
					ql in original_data.get("_productionRight", "").lower()):
					filtered.append(r)

		tab.pairsList.set(filtered)
		self._currentDisplayPairsTurbo = filtered

	def showSelectedPairs(self, sender):
		"""TURBO: Fast selection display - USES PRODUCTION NAMES FOR TAB"""
		tab = self.w.tabs[1]
		rows = self._currentDisplayPairs
		sel = tab.pairsList.getSelection()

		if not sel:
			return

		try:
			lines = []
			for i in sel:
				if i < len(rows):
					row = rows[i]
					if row.get("Left") == "────" and row.get("Right") == "────":
						continue
				
					original_data = row.get("_originalData", row)
				
					# TURBO: Use PRODUCTION NAMES for tab generation, not graphical display
					left = original_data.get("_productionLeft", row["Left"])
					right = original_data.get("_productionRight", row["Right"])
					value = original_data.get("Value", row["Value"])
				
					lines.append(self.contextualDisplayTurbo(left, right, value))
		
			if lines:
				Glyphs.font.newTab("\n".join(lines))
		except Exception as e:
			print(f"TURBO Error: {e}")
			Message("Error showing selection")




		
		
		
KernMarginSlider()