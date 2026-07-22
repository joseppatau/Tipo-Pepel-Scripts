# MenuTitle:Create Small Caps & Numerals Smart Components
# -*- coding: utf-8 -*-
# Description: Adjusts LSB and RSB values for glyphs based on kerning group membership across selected masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Create Small Caps % Numerals smartComponent
# -*- coding: utf-8 -*-


from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc
import math
import os
import json
from vanilla import List, CheckBoxListCell 

# ✅ 1️⃣ Listas de glyphs
PUNCTUATION_GLYPHS = [
    "period","comma","colon","semicolon","ellipsis","exclam","exclamdown",
    "question","questiondown","periodcentered","bullet","asterisk","numbersign",
    "slash","backslash","hyphen","endash","emdash","parenleft","parenright",
    "braceleft","braceright","bracketleft","bracketright","quotesinglbase",
    "quotedblbase","quotedblleft","quotedblright","quoteleft","quoteright",
    "guillemetleft","guillemetright","guilsinglleft","guilsinglright",
    "quotedbl","quotesingle"
]

SYMBOL_GLYPHS = [
    "at","ampersand","paragraph","section","copyright","registered","trademark",
    "degree","bar","brokenbar","dagger","daggerdbl","cent","currency","dollar",
    "euro","sterling","yen","plus","minus","multiply","divide","equal",
    "notequal","greater","less","greaterequal","lessequal","plusminus",
    "approxequal","asciitilde","logicalnot","asciicircum","percent","perthousand"
]

# ✅ 2️⃣ Funciones JSON Save/Load
def saveGlyphConfig(data):
    panel = NSSavePanel.savePanel()
    panel.setAllowedFileTypes_(["json"])
    if panel.runModal():
        path = panel.URL().path()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

def loadGlyphConfig():
    panel = NSOpenPanel.openPanel()
    panel.setAllowedFileTypes_(["json"])
    if panel.runModal():
        path = panel.URL().path()
        with open(path) as f:
            return json.load(f)
    return None

def get_uppercase_glyphs():
    uppercase_glyphs = {
        'latin': {
            'basic': [
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "AE", "OE", "Aring", "Oslash", "Thorn", "Eth", "Germandbls", 
                "SharpS", "Schwa", "Eng", "IJ",
                "Esh", "Ezh", "Hbar", "Dcroat", "Ash", "Oethel", "Wynn", 
                "Yogh", "InsularG"
            ],
            'extended': [
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "AE", "OE", "Aring", "Oslash", "Thorn", "Eth", "Germandbls",
                "SharpS", "Schwa", "Eng", "IJ", "Esh", "Ezh", "Hbar", "Dcroat",
                "Ash", "Oethel", "Wynn", "Yogh", "InsularG", "Gamma", "Lambda"
            ],
            'compact': "ABCDEFGHIJKLMNOPQRSTUVWXYZAEOEAringOslashThornEthGermandblsSharpSSchwaEngIJ"
        },
        'cyrillic': {
            'option1': [
                "A-cy", "Be-cy", "Ve-cy", "Ge-cy", "Gje-cy", "Geupturn-cy", 
                "Gestroked-cy", "De-cy", "Ie-cy", "Iegrave-cy", "Io-cy", "Zhe-cy", 
                "Ze-cy", "Ii-cy", "Iishort-cy", "Iigrave-cy", "Ka-cy", "Kje-cy", 
                "El-cy", "Em-cy", "En-cy", "O-cy", "Pe-cy", "Er-cy", "Es-cy", 
                "Te-cy", "U-cy", "Ushort-cy", "Ef-cy", "Ha-cy", "Tse-cy", 
                "Che-cy", "Sha-cy", "Shcha-cy", "Dzhe-cy", "Softsign-cy", 
                "Yeru-cy", "Hardsign-cy", "Lje-cy", "Nje-cy", "Dze-cy", "E-cy", 
                "Ereversed-cy", "I-cy", "Yi-cy", "Je-cy", "Tshe-cy", "Yu-cy", 
                "Ya-cy", "Dje-cy", "Yat-cy", "Yusbig-cy", "Fita-cy", "Izhitsa-cy", 
                "Zhedescender-cy", "Kadescender-cy", "Endescender-cy", 
                "Ustraight-cy", "Ustraightstroke-cy", "Hadescender-cy", 
                "Chedescender-cy", "Shha-cy", "Palochka-cy", "Schwa-cy", 
                "Imacron-cy", "Obarred-cy", "Umacron-cy", "De-cy.loclBGR", 
                "El-cy.loclBGR", "Ef-cy.loclBGR"
            ],
            'option2': [
                "Acy", "Becy", "Vecy", "Gecy", "Gjecy", "Geupturncy", 
                "Gestrokedcy", "Decy", "Iecy", "Iegravecy", "Iocy", "Zhecy", 
                "Zecy", "Iicy", "Iishortcy", "Iigravecy", "Kacy", "Kjecy", 
                "Elcy", "Emcy", "Ency", "Ocy", "Pecy", "Ercy", "Escy", "Tecy", 
                "Ucy", "Ushortcy", "Efcy", "Hacy", "Tsecy", "Checy", "Shacy", 
                "Shchacy", "Dzhecy", "Softsigncy", "Yerucy", "Hardsigncy", 
                "Ljecy", "Njecy", "Dzecy", "Ecy", "Ereversedcy", "Icy", "Yicy", 
                "Jecy", "Tshecy", "Yucy", "Yacy", "Djecy", "Yatcy", "Yusbigcy", 
                "Fitacy", "Izhitsacy", "Zhedescendercy", "Kadescendercy", 
                "Endescendercy", "Ustraightcy", "Ustraightstrokecy", 
                "Hadescendercy", "Chedescendercy", "Shhacy", "Palochkacy", 
                "Schwacy", "Imacroncy", "Obarredcy", "Umacroncy", 
                "Decy.loclBGR", "Elcy.loclBGR", "Efcy.loclBGR"
            ],
            'option3': [
                "uni0410", "uni0411", "uni0412", "uni0413", "uni0403", 
                "uni0490", "uni0492", "uni0414", "uni0415", "uni0400", 
                "uni0401", "uni0416", "uni0417", "uni0418", "uni0419", 
                "uni040D", "uni041A", "uni040C", "uni041B", "uni041C", 
                "uni041D", "uni041E", "uni041F", "uni0420", "uni0421", 
                "uni0422", "uni0423", "uni040E", "uni0424", "uni0425", 
                "uni0426", "uni0427", "uni0428", "uni0429", "uni040F", 
                "uni042C", "uni042B", "uni042A", "uni0409", "uni040A", 
                "uni0405", "uni0404", "uni042D", "uni0406", "uni0407", 
                "uni0408", "uni040B", "uni042E", "uni042F", "uni0402", 
                "uni0462", "uni046A", "uni0472", "uni0474", "uni0496", 
                "uni049A", "uni04A2", "uni04AE", "uni04B0", "uni04B2", 
                "uni04B6", "uni04BA", "uni04C0", "uni04D8", "uni04E2", 
                "uni04E8", "uni04EE", "uni0414.loclBGR", "uni041B.loclBGR", 
                "uni0424.loclBGR"
            ],
            'russian_basic': [
                "A-cy", "Be-cy", "Ve-cy", "Ge-cy", "De-cy", "Ie-cy", "Io-cy",
                "Zhe-cy", "Ze-cy", "I-cy", "ShortI-cy", "Ka-cy", "El-cy",
                "Em-cy", "En-cy", "O-cy", "Pe-cy", "Er-cy", "Es-cy", "Te-cy",
                "U-cy", "Ef-cy", "Ha-cy", "Tse-cy", "Che-cy", "Sha-cy",
                "Shcha-cy", "HardSign-cy", "Yeru-cy", "SoftSign-cy", "E-cy",
                "Yu-cy", "Ya-cy"
            ]
        },
        'greek': {
            'option1': [
                "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta",
                "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron",
                "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi",
                "Omega", "Alphatonos", "Epsilontonos", "Etatonos", "Iotatonos",
                "Omicrontonos", "Upsilontonos", "Omegatonos", "Iotadieresis",
                "Upsilondieresis", "Heta", "Archaicsampi", "Pamphyliandigamma",
                "KoppaArchaic", "Stigma", "Digamma", "Koppa", "Sampi", "KaiSymbol",
                "Sho", "San"
            ],
            'option2': [
                "uni0391", "uni0392", "uni0393", "uni0394", "uni0395", "uni0396",
                "uni0397", "uni0398", "uni0399", "uni039A", "uni039B", "uni039C",
                "uni039D", "uni039E", "uni039F", "uni03A0", "uni03A1", "uni03A3",
                "uni03A4", "uni03A5", "uni03A6", "uni03A7", "uni03A8", "uni03A9",
                "uni0386", "uni0388", "uni0389", "uni038A", "uni038C", "uni038E",
                "uni038F", "uni03AA", "uni03AB", "uni0370", "uni0372", "uni0376",
                "uni03D8", "uni03DA", "uni03DC", "uni03DE", "uni03E0", "uni03CF",
                "uni03F7", "uni03FA"
            ],
            'option3': [
                "0391", "0392", "0393", "0394", "0395", "0396", "0397", "0398",
                "0399", "039A", "039B", "039C", "039D", "039E", "039F", "03A0",
                "03A1", "03A3", "03A4", "03A5", "03A6", "03A7", "03A8", "03A9",
                "0386", "0388", "0389", "038A", "038C", "038E", "038F", "03AA",
                "03AB", "0370", "0372", "0376", "03D8", "uni03DA", "03DC", "03DE",
                "03E0", "03CF", "03F7", "03FA"
            ],
            'modern_basic': [
                "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta",
                "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron",
                "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi",
                "Omega"
            ]
        },
        'symbols': {
            'currency': [
                "baht", "at", "ampersand", "paragraph", "section", "copyright",
                "registered", "trademark", "degree", "bar", "brokenbar",
                "dagger", "daggerdbl", "cent", "currency", "dollar", "euro",
                "sterling", "yen"
            ],
            'math': [
                "plus", "minus", "multiply", "divide", "equal", "notequal",
                "greater", "less", "greaterequal", "lessequal", "plusminus",
                "logicalnot", "asciicircum", "partialdiff", "percent",
                "perthousand"
            ]
        },
        'numerals': {
            'digits': [
                "zero", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine"
            ],
            'numeral_symbols': [
                "parenleft", "parenright", "braceleft", "braceright",
                "bracketleft", "bracketright"
            ],
            'all_numerals': [
                "zero", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "parenleft", "parenright", "braceleft",
                "braceright", "bracketleft", "bracketright"
            ]
        },
        'centered': [
            "parenleft.sc", "parenright.sc", "braceleft.sc", "braceright.sc",
            "bracketleft.sc", "bracketright.sc", "hyphen.sc", "endash.sc",
            "emdash.sc", "exclamdown.sc", "questiondown.sc", "periodcentered.sc",
            "bullet.sc", "guillemetleft.sc", "guillemetright.sc", "guilsinglleft.sc",
            "guilsinglright.sc", "currency.sc", "plus.sc", "minus.sc", "multiply.sc",
            "divide.sc", "equal.sc", "notequal.sc", "greater.sc", "less.sc",
            "greaterequal.sc", "lessequal.sc", "plusminus.sc"
        ],
        'combined': {
            'latin_basic': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            'latin_extended': "ABCDEFGHIJKLMNOPQRSTUVWXYZAEOEAringOslashThornEthGermandbls",
            'cyrillic_russian': "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            'greek_basic': "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
        }
    }
    return uppercase_glyphs

_panel_instance = None
_combined_preview_class_registered = False

try:
    existing_class = objc.lookUpClass('CombinedPreviewView')
    if existing_class:
        CombinedPreviewView = existing_class
        _combined_preview_class_registered = True
    else:
        _combined_preview_class_registered = False
except:
    _combined_preview_class_registered = False

if not _combined_preview_class_registered:
    class CombinedPreviewView(NSView):
        def initWithFrame_(self, frame):
            self = objc.super(CombinedPreviewView, self).initWithFrame_(frame)
            if self is None:
                return None
            
            self.static_char = "H"
            self.dynamic_chars = "HXD"
            self.metrics = None
            self.showXbeam = True
            self.showYbeam = True
            self.xbeamPosition = 0
            self.ybeamPosition = 300
            self.axisValues = {}
            self.dynamicScale = 1.0
            self.widthScale = 1.0
            
            self.scale = 1.0
            self.view_baseline = 0
            
            self.static_cache = {}
            self.dynamic_cache = {}
            
            return self

        @objc.python_method
        def getCurrentMaster(self):
            font = Glyphs.font
            if not font or not font.masters:
                return None

            if self.metrics:
                masterID = self.metrics.get("masterID")
                if masterID:
                    for m in font.masters:
                        if m.id == masterID:
                            return m

            if self.metrics:
                idx = self.metrics.get("masterIndex")
                if isinstance(idx, int) and 0 <= idx < len(font.masters):
                    return font.masters[idx]

            return font.masters[0]

        @objc.python_method
        def calculateXHeightScale(self, layer, master):
            try:
                if not layer or not master:
                    return 1.0, 100
            
                max_y = -float('inf')
                min_y = float('inf')
            
                if hasattr(layer, 'paths') and layer.paths:
                    for path in layer.paths:
                        if hasattr(path, 'nodes') and path.nodes:
                            for node in path.nodes:
                                y = float(node.y)
                                max_y = max(max_y, y)
                                min_y = min(min_y, y)
            
                if max_y == -float('inf') or min_y == float('inf'):
                    if hasattr(layer, 'bounds') and layer.bounds:
                        bounds = layer.bounds
                        min_y = bounds.origin.y
                        max_y = bounds.origin.y + bounds.size.height
                    else:
                        return 1.0, 100
            
                char_height = max_y - min_y if min_y < 0 else max_y
                x_height = float(master.xHeight)
            
                if char_height > 0:
                    scale_to_xheight = x_height / char_height
                    percentage = int(scale_to_xheight * 100)
                    return scale_to_xheight, percentage
                else:
                    return 1.0, 100
                
            except Exception:
                return 1.0, 100

        @objc.python_method
        def setDynamicScale_(self, scale):
            self.dynamicScale = max(0.0, min(scale, 2.0))
            self.dynamic_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setWidthScale_(self, scale):
            self.widthScale = max(0.5, min(scale, 2.0))
            self.dynamic_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setStaticChar_(self, ch):
            if ch and len(ch) > 0:
                self.static_char = ch[0].upper()
            else:
                self.static_char = " "
            self.static_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setDynamicChars_(self, chars):
            digit_map = {
                "0": "zero",
                "1": "one", 
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
                "(": "parenleft",
                ")": "parenright",
                "{": "braceleft",
                "}": "braceright",
                "[": "bracketleft",
                "]": "bracketright",
                "-": "hyphen",
                "$": "dollar",
                "€": "euro",
                "£": "sterling",
                "¥": "yen",
                "¢": "cent",
                "@": "at",
                "&": "ampersand",
                "#": "numbersign",
                "%": "percent",
                "+": "plus",
                "=": "equal",
                "*": "asterisk",
                "/": "slash",
                "\\": "backslash",
                "_": "underscore",
                "|": "bar",
                "¦": "brokenbar",
                "©": "copyright",
                "®": "registered",
                "™": "trademark",
                "°": "degree",
                "§": "section",
                "¶": "paragraph",
                "†": "dagger",
                "‡": "daggerdbl",
                "•": "bullet",
                "…": "ellipsis",
                "¡": "exclamdown",
                "¿": "questiondown",
                "‹": "guilsinglleft",
                "›": "guilsinglright",
                "«": "guillemetleft",
                "»": "guillemetright",
                "'": "quotesingle",
                '"': "quotedbl",
                "`": "quoteleft",
                "´": "quoteright",
                "‚": "quotesinglbase",
                "„": "quotedblbase",
                "‘": "quoteleft",
                "’": "quoteright",
                "": "quotedblleft",
                "": "quotedblright",
                ".": "period",
                ",": "comma",
                ":": "colon",
                ";": "semicolon",
                "!": "exclam",
                "?": "question",
                "<": "less",
                ">": "greater",
                "≤": "lessequal",
                "≥": "greaterequal",
                "≠": "notequal",
                "±": "plusminus",
                "×": "multiply",
                "÷": "divide",
                "¬": "logicalnot",
                "∂": "partialdiff",
                "‰": "perthousand",
                "฿": "baht"
            }
    
            if chars:
                self.dynamic_chars = chars
                self.dynamic_cache.clear()
                self.setNeedsDisplay_(True)
            else:
                self.dynamic_chars = " "

        @objc.python_method
        def setMetrics_(self, metrics):
            self.metrics = metrics
            self.static_cache.clear()
            self.dynamic_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setXbeamPosition_(self, position):
            self.xbeamPosition = float(position)
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setYbeamPosition_(self, position):
            self.ybeamPosition = float(position)
            self.setNeedsDisplay_(True)
            
        @objc.python_method
        def setShowXbeam_(self, show):
            self.showXbeam = bool(show)
            self.setNeedsDisplay_(True)
            
        @objc.python_method
        def setShowYbeam_(self, show):
            self.showYbeam = bool(show)
            self.setNeedsDisplay_(True)
            
        @objc.python_method
        def setAxisValues_(self, axisValues):
            self.axisValues = axisValues or {}
            self.dynamic_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def _getStaticLayer(self, char):
            digit_map = {
                "0": "zero",
                "1": "one", 
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
                "(": "parenleft",
                ")": "parenright",
                "{": "braceleft",
                "}": "braceright",
                "[": "bracketleft",
                "]": "bracketright",
                "-": "hyphen",
                "$": "dollar",
                "€": "euro",
                "£": "sterling",
                "¥": "yen",
                "¢": "cent",
                "@": "at",
                "&": "ampersand",
                "#": "numbersign",
                "%": "percent",
                "+": "plus",
                "=": "equal",
                "*": "asterisk",
                "/": "slash",
                "\\": "backslash",
                "_": "underscore",
                "|": "bar",
                "¦": "brokenbar",
                "©": "copyright",
                "®": "registered",
                "™": "trademark",
                "°": "degree",
                "§": "section",
                "¶": "paragraph",
                "†": "dagger",
                "‡": "daggerdbl",
                "•": "bullet",
                "…": "ellipsis",
                "¡": "exclamdown",
                "¿": "questiondown",
                "‹": "guilsinglleft",
                "›": "guilsinglright",
                "«": "guillemetleft",
                "»": "guillemetright",
                "'": "quotesingle",
                '"': "quotedbl",
                "`": "quoteleft",
                "´": "quoteright",
                "‚": "quotesinglbase",
                "„": "quotedblbase",
                "": "quoteleft",
                "": "quoteright",
                "": "quotedblleft",
                "": "quotedblright",
                ".": "period",
                ",": "comma",
                ":": "colon",
                ";": "semicolon",
                "!": "exclam",
                "?": "question",
                "<": "less",
                ">": "greater",
                "≤": "lessequal",
                "≥": "greaterequal",
                "≠": "notequal",
                "±": "plusminus",
                "×": "multiply",
                "÷": "divide",
                "¬": "logicalnot",
                "∂": "partialdiff",
                "‰": "perthousand",
                "฿": "baht"
            }
    
            glyph_name = char
    
            if char in digit_map:
                glyph_name = digit_map[char]
            elif char.isdigit():
                digit_names = ["zero", "one", "two", "three", "four", 
                              "five", "six", "seven", "eight", "nine"]
                try:
                    idx = int(char)
                    if 0 <= idx <= 9:
                        glyph_name = digit_names[idx]
                except:
                    glyph_name = char.upper()
            else:
                glyph_name = char.upper()
    
            cache_key = f"static_{glyph_name}"
            if cache_key in self.static_cache:
                return self.static_cache[cache_key]
        
            try:
                font = Glyphs.font
                if not font:
                    return None
            
                glyph = None
                if glyph_name in font.glyphs:
                    glyph = font.glyphs[glyph_name]
        
                if not glyph:
                    for g in font.glyphs:
                        if g.name and g.name.upper() == glyph_name:
                            glyph = g
                            break
        
                if not glyph:
                    for g in font.glyphs:
                        if g.name and g.name.lower() == glyph_name.lower():
                            glyph = g
                            break
        
                if not glyph:
                    return None
        
                master = self.getCurrentMaster()
                if not master:
                    layer = glyph.layers[0] if glyph.layers else None
                    self.static_cache[cache_key] = layer
                    return layer

                for layer in glyph.layers:
                    if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master.id) or \
                       (hasattr(layer, 'masterId') and layer.masterId == master.id):
                        self.static_cache[cache_key] = layer
                        return layer

                layer = glyph.layers[0] if glyph.layers else None
                self.static_cache[cache_key] = layer
                return layer
        
            except Exception:
                return None

        @objc.python_method
        def _getDynamicLayer(self, char):
            digit_map = {
                "0": "zero",
                "1": "one", 
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
                "(": "parenleft",
                ")": "parenright",
                "{": "braceleft",
                "}": "braceright",
                "[": "bracketleft",
                "]": "bracketright",
                "-": "hyphen",
                "$": "dollar",
                "€": "euro",
                "£": "sterling",
                "¥": "yen",
                "¢": "cent",
                "@": "at",
                "&": "ampersand",
                "#": "numbersign",
                "%": "percent",
                "+": "plus",
                "=": "equal",
                "*": "asterisk",
                "/": "slash",
                "\\": "backslash",
                "_": "underscore",
                "|": "bar",
                "¦": "brokenbar",
                "©": "copyright",
                "®": "registered",
                "™": "trademark",
                "°": "degree",
                "§": "section",
                "¶": "paragraph",
                "†": "dagger",
                "‡": "daggerdbl",
                "•": "bullet",
                "…": "ellipsis",
                "¡": "exclamdown",
                "¿": "questiondown",
                "‹": "guilsinglleft",
                "›": "guilsinglright",
                "«": "guillemetleft",
                "»": "guillemetright",
                "'": "quotesingle",
                '"': "quotedbl",
                "`": "quoteleft",
                "´": "quoteright",
                "‚": "quotesinglbase",
                "„": "quotedblbase",
                "": "quoteleft",
                "": "quoteright",
                "": "quotedblleft",
                "": "quotedblright",
                ".": "period",
                ",": "comma",
                ":": "colon",
                ";": "semicolon",
                "!": "exclam",
                "?": "question",
                "<": "less",
                ">": "greater",
                "≤": "lessequal",
                "≥": "greaterequal",
                "≠": "notequal",
                "±": "plusminus",
                "×": "multiply",
                "÷": "divide",
                "¬": "logicalnot",
                "∂": "partialdiff",
                "‰": "perthousand",
                "฿": "baht"
            }
    
            glyph_name = char
    
            if char in digit_map:
                glyph_name = digit_map[char]
            elif char.isdigit():
                digit_names = ["zero", "one", "two", "three", "four", 
                              "five", "six", "seven", "eight", "nine"]
                try:
                    idx = int(char)
                    if 0 <= idx <= 9:
                        glyph_name = digit_names[idx]
                except:
                    glyph_name = char.upper()
            else:
                glyph_name = char.upper()
    
            cache_key = f"dynamic_{glyph_name}_{str(self.axisValues)}"
            if cache_key in self.dynamic_cache:
                return self.dynamic_cache[cache_key]

            try:
                font = Glyphs.font
                if not font:
                    return None

                glyph = None
                if glyph_name in font.glyphs:
                    glyph = font.glyphs[glyph_name]
                else:
                    for g in font.glyphs:
                        if g.name and g.name.upper() == glyph_name.upper():
                            glyph = g
                            break

                if not glyph:
                    return None

                if not self.axisValues:
                    layer = self._getStaticLayer(glyph_name)
                    self.dynamic_cache[cache_key] = layer
                    return layer

                layers_with_coords = []

                for m in font.masters:
                    layer = None
                    try:
                        layer = glyph.layerForKey_(m.id)
                    except Exception:
                        layer = None

                    if not layer:
                        for lyr in glyph.layers:
                            if getattr(lyr, "associatedMasterId", None) == m.id:
                                layer = lyr
                                break

                    if layer:
                        coords = []
                        for axis in font.axes:
                            idx = list(font.axes).index(axis)
                            coords.append(float(m.axes[idx]))
                        layers_with_coords.append((coords, layer, f"master-{m.name}"))

                for lyr in glyph.layers:
                    attrs = getattr(lyr, "attributes", None)
                    if isinstance(attrs, dict) and "coordinates" in attrs:
                        try:
                            coords = [float(c) for c in attrs["coordinates"]]
                            layers_with_coords.append((coords, lyr, lyr.name))
                        except Exception:
                            pass

                target_coords = []
                for axis in font.axes:
                    axis_name = axis.name.lower() if axis.name else ""
                    axis_tag = getattr(axis, "axisTag", "").lower()

                    value = None
                    for k, v in self.axisValues.items():
                        kl = k.lower()
                        if kl == axis_name or (axis_tag and kl == axis_tag):
                            value = float(v)
                            break

                    if value is None:
                        master = self.getCurrentMaster()
                        idx = list(font.axes).index(axis)
                        value = float(master.axes[idx]) if master else 0.0

                    target_coords.append(value)

                for coords, layer, name in layers_with_coords:
                    if len(coords) == len(target_coords):
                        if all(abs(coords[i] - target_coords[i]) < 0.1 for i in range(len(coords))):
                            self.dynamic_cache[cache_key] = layer
                            return layer

                try:
                    inst = GSInstance.alloc().init()
                    inst.font = font
                    inst.axes = target_coords
                    vf = inst.interpolatedFont

                    if vf and glyph.name in vf.glyphs:
                        layer = vf.glyphs[glyph.name].layers[0]
                        self.dynamic_cache[cache_key] = layer
                        return layer

                except Exception:
                    pass

                layer = self._getStaticLayer(glyph_name)
                self.dynamic_cache[cache_key] = layer
                return layer

            except Exception:
                return None
                
        @objc.python_method
        def buildPathFromLayer(self, layer):
            if not layer:
                return None
                
            try:
                if hasattr(layer, 'bezierPath'):
                    bezier_path = layer.bezierPath
                    if bezier_path and bezier_path.elementCount() > 0:
                        return bezier_path
                
                path = NSBezierPath.bezierPath()
                if hasattr(layer, 'paths') and layer.paths:
                    for glyph_path in layer.paths:
                        if not hasattr(glyph_path, 'nodes') or not glyph_path.nodes:
                            continue
                        nodes = list(glyph_path.nodes)
                        point_count = len(nodes)
                        for i in range(point_count):
                            node = nodes[i]
                            if i == 0:
                                path.moveToPoint_((node.x, node.y))
                            elif node.type == GSLINE:
                                path.lineToPoint_((node.x, node.y))
                            elif node.type == GSCURVE:
                                if i + 2 < point_count and nodes[i+1].type == GSOFFCURVE and nodes[i+2].type == GSOFFCURVE:
                                    cp1 = nodes[i+1]
                                    cp2 = nodes[i+2]
                                    end = nodes[i+3] if i+3 < point_count else node
                                    path.curveToPoint_controlPoint1_controlPoint2_(
                                        (end.x, end.y), (cp1.x, cp1.y), (cp2.x, cp2.y))
                        if glyph_path.closed:
                            path.closePath()
                
                if path.elementCount() > 0:
                    return path
                
                return None
            except Exception:
                return None
                
        @objc.python_method
        def _getLayerHeight(self, layer):
            if not layer:
                return 0.0

            try:
                if hasattr(layer, "bounds") and layer.bounds:
                    return layer.bounds.size.height

                min_y = float("inf")
                max_y = float("-inf")

                if hasattr(layer, "paths"):
                    for path in layer.paths:
                        for node in path.nodes:
                            y = float(node.y)
                            min_y = min(min_y, y)
                            max_y = max(max_y, y)

                if min_y == float("inf") or max_y == float("-inf"):
                    return 0.0

                return max_y - min_y

            except Exception:
                return 0.0

        @objc.python_method
        def _getTransformedCharData(self, char, is_static=True):
            try:
                if is_static:
                    layer = self._getStaticLayer(char)
                else:
                    layer = self._getDynamicLayer(char)
            
                if not layer:
                    return None
    
                master = self.getCurrentMaster()
                if not master:
                    return None
    
                base_scale = self.scale
    
                if is_static:
                    actual_scale = base_scale
                    width_scale = 1.0
                    current_height_font_units = self._getLayerHeight(layer)
                else:
                    if self.dynamicScale <= 1.0:
                        actual_scale = base_scale * self.dynamicScale
                        current_height_font_units = self._getLayerHeight(layer) * self.dynamicScale
                    else:
                        actual_scale = base_scale * self.dynamicScale
                        current_height_font_units = self._getLayerHeight(layer) * self.dynamicScale
            
                    width_scale = self.widthScale
    
                scale_x = actual_scale * width_scale
                scale_y = actual_scale
        
                result = {
                    'layer': layer,
                    'scale': actual_scale,
                    'scale_x': scale_x,
                    'scale_y': scale_y,
                    'width_scale': width_scale,
                    'width': float(layer.width) * scale_x,
                    'height': self._getLayerHeight(layer) * scale_y,
                    'current_height_font_units': current_height_font_units,
                    'font_units_scale_factor': actual_scale / base_scale if base_scale > 0 else 1.0
                }
        
                return result
        
            except Exception:
                return None

        @objc.python_method
        def _getYbeamSegmentsFromPath(self, bezierPath, x_view, tolerance=1.0):
            ys = []
            eps = 0.5

            if not bezierPath:
                return []

            for i in range(bezierPath.elementCount()):
                etype, pts = bezierPath.elementAtIndex_associatedPoints_(i)

                if etype == NSMoveToBezierPathElement:
                    last = pts[0]
                elif etype == NSLineToBezierPathElement:
                    p1 = last
                    p2 = pts[0]

                    x1, x2 = p1.x, p2.x
                    if min(x1, x2) <= x_view <= max(x1, x2):
                        if abs(x2 - x1) > 0.001:
                            t = (x_view - x1) / (x2 - x1)
                            y = p1.y + (p2.y - p1.y) * t
                            ys.append(y)

                    last = p2
                elif etype == NSCurveToBezierPathElement:
                    p1 = last
                    p2 = pts[0]
                    p3 = pts[1]
                    p4 = pts[2]
                    
                    x_min = min(p1.x, p2.x, p3.x, p4.x)
                    x_max = max(p1.x, p2.x, p3.x, p4.x)
                    
                    if x_min <= x_view <= x_max:
                        if abs(p4.x - p1.x) > 0.001:
                            t = (x_view - p1.x) / (p4.x - p1.x)
                            y = p1.y + (p4.y - p1.y) * t
                            ys.append(y)
                    
                    last = p4
                else:
                    continue

            ys.sort()
            clean = []
            for y in ys:
                if not clean or abs(y - clean[-1]) > eps:
                    clean.append(y)

            segments = []
            for i in range(0, len(clean) - 1, 2):
                segments.append((clean[i], clean[i + 1]))

            return segments

        @objc.python_method
        def _getXbeamSegmentsFromPath(self, bezierPath, y_view, tolerance=1.0):
            xs = []
            eps = 0.5

            if not bezierPath:
                return []

            for i in range(bezierPath.elementCount()):
                etype, pts = bezierPath.elementAtIndex_associatedPoints_(i)

                if etype == NSMoveToBezierPathElement:
                    last = pts[0]
                elif etype == NSLineToBezierPathElement:
                    p1 = last
                    p2 = pts[0]

                    y1, y2 = p1.y, p2.y
                    if min(y1, y2) <= y_view <= max(y1, y2):
                        if abs(y2 - y1) > 0.001:
                            t = (y_view - y1) / (y2 - y1)
                            x = p1.x + (p2.x - p1.x) * t
                            xs.append(x)

                    last = p2
                elif etype == NSCurveToBezierPathElement:
                    p1 = last
                    p2 = pts[0]
                    p3 = pts[1]
                    p4 = pts[2]
                    
                    y_min = min(p1.y, p2.y, p3.y, p4.y)
                    y_max = max(p1.y, p2.y, p3.y, p4.y)
                    
                    if y_min <= y_view <= y_max:
                        if abs(p4.y - p1.y) > 0.001:
                            t = (y_view - p1.y) / (p4.y - p1.y)
                            x = p1.x + (p4.x - p1.x) * t
                            xs.append(x)
                    
                    last = p4
                else:
                    continue

            xs.sort()
            clean = []
            for x in xs:
                if not clean or abs(x - clean[-1]) > eps:
                    clean.append(x)

            segments = []
            for i in range(0, len(clean) - 1, 2):
                segments.append((clean[i], clean[i + 1]))

            return segments

        def drawRect_(self, rect):
            try:
                context = NSGraphicsContext.currentContext()
                
                NSColor.whiteColor().set()
                NSBezierPath.fillRect_(self.bounds())
                NSColor.grayColor().set()
                NSBezierPath.strokeRect_(NSInsetRect(self.bounds(), 1, 1))
                
                if not self.metrics:
                    self._drawMessage("No metrics available")
                    return
                
                current_master = self.getCurrentMaster()
                if not current_master:
                    self._drawMessage("No master available")
                    return
                
                w = self.bounds().size.width
                h = self.bounds().size.height
                asc = float(current_master.ascender)
                desc = float(current_master.descender)
                padding = 20.0
                available_height = h - 2 * padding
                total_height = asc - desc
                if total_height <= 0:
                    total_height = 1000.0
                
                self.scale = available_height / total_height
                self.view_baseline = padding + (-desc * self.scale)
                
                self._drawMetrics(current_master, self.scale, self.view_baseline, w, h)
                self._drawAllCharacters(current_master, w, h)
                
                if self.showXbeam:
                    self._drawXbeam(current_master, self.scale, self.view_baseline, w, h)
                
                if self.showYbeam:
                    self._drawYbeam(current_master, self.scale, self.view_baseline, w, h)
                
            except Exception:
                self._drawMessage("Display error")

        @objc.python_method
        def _drawAllCharacters(self, master, w, h):
            try:
                char_x = 20
        
                if self.static_char and self.static_char != " ":
                    self._drawSingleCharacter(self.static_char, master, char_x, is_static=True)
                    char_data = self._getTransformedCharData(self.static_char, is_static=True)
                    if char_data:
                        char_x += char_data['width']
                    else:
                        char_x += 150 * self.scale + 20
        
                if self.dynamic_chars:
                    for idx, ch in enumerate(self.dynamic_chars):
                        if ch and ch != " ":
                            self._drawSingleCharacter(ch, master, char_x, is_static=False)
                            char_data = self._getTransformedCharData(ch, is_static=False)
                            if char_data:
                                char_x += char_data['width']
                            else:
                                char_x += 150 * self.scale + 20
            
            except Exception:
                pass

        @objc.python_method
        def _drawSingleCharacter(self, char, master, x_offset, is_static=True):
            try:
                char_data = self._getTransformedCharData(char, is_static)
                if not char_data or not char_data["layer"]:
                    self._drawCharPlaceholder(
                        char, master, x_offset,
                        self.scale, self.view_baseline,
                        self.bounds().size.height, is_static
                    )
                    return

                layer = char_data["layer"]
                scale_x = char_data["scale_x"]
                scale_y = char_data["scale_y"]

                glyphPath = self.buildPathFromLayer(layer)
                if not glyphPath:
                    return

                transform = NSAffineTransform.transform()
                transform.translateXBy_yBy_(x_offset, self.view_baseline)
                transform.scaleXBy_yBy_(scale_x, scale_y)

                path = glyphPath.copy()
                path.transformUsingAffineTransform_(transform)

                NSColor.blackColor().set()
                path.fill()

                self._drawCharacterLabel(char, x_offset, scale_x, scale_y, layer, is_static, char_data)

            except Exception:
                pass

        @objc.python_method
        def _drawCharacterLabel(self, char, x_offset, scale_x, scale_y, layer, is_static, char_data=None):
            try:
                fontLabel = NSFont.systemFontOfSize_(10)
                width_pixels = float(layer.width) * scale_x
            
                if is_static:
                    label_text = f"Static: {char}"
                    color = NSColor.darkGrayColor()
                else:
                    label_text = f"Dynamic: {char}"
                    color = NSColor.darkGrayColor()
            
                    if char_data:
                        width_scale = char_data['width_scale']
                        height_info = f"H:{int(self.dynamicScale*100)}%"
                        
                        if width_scale != 1.0:
                            width_percent = int(width_scale * 100)
                            if width_percent > 100:
                                width_info = f"W:+{width_percent-100}%"
                            elif width_percent < 100:
                                width_info = f"W:-{100-width_percent}%"
                            else:
                                width_info = "W:100%"
                        else:
                            width_info = "W:100%"
                        
                        label_text += f" ({height_info}, {width_info})"
            
                attrs = {
                    NSFontAttributeName: fontLabel,
                    NSForegroundColorAttributeName: color
                }
            
                label_str = NSAttributedString.alloc().initWithString_attributes_(label_text, attrs)
                label_size = label_str.size()
                label_x = x_offset + (width_pixels - label_size.width) / 2.0
                label_y = 5
            
                bg_rect = NSRect((label_x - 2, label_y - 1), (label_size.width + 4, label_size.height + 2))
                NSColor.whiteColor().colorWithAlphaComponent_(0.8).set()
                NSBezierPath.fillRect_(bg_rect)
            
                label_str.drawAtPoint_((label_x, label_y))
            
            except Exception:
                pass

        @objc.python_method
        def _drawCharPlaceholder(self, char, master, x_offset, scale, view_baseline, total_height, is_static=True):
            try:
                actual_scale = scale
                if not is_static:
                    xheight_percentage = 70
                    dynamic_scale_factor = self.dynamicScale
                    
                    if dynamic_scale_factor == 1.0:
                        actual_scale = scale
                    elif dynamic_scale_factor == 0.0:
                        actual_scale = scale * (xheight_percentage / 100.0)
                    else:
                        interpolated_scale = 1.0 + ((xheight_percentage / 100.0) - 1.0) * (1.0 - dynamic_scale_factor)
                        actual_scale = scale * interpolated_scale
                
                placeholder_width = 100 * actual_scale
                placeholder_height = 700 * actual_scale
                
                placeholder_rect = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                    ((x_offset, view_baseline), (placeholder_width, placeholder_height)), 10, 10)
                
                NSColor.lightGrayColor().colorWithAlphaComponent_(0.5).set()
                placeholder_rect.fill()
                
                NSColor.grayColor().colorWithAlphaComponent_(0.7).set()
                placeholder_rect.setLineWidth_(1.0)
                placeholder_rect.stroke()
                
                font = NSFont.systemFontOfSize_(24 * actual_scale)
                attrs = {
                    NSFontAttributeName: font,
                    NSForegroundColorAttributeName: NSColor.darkGrayColor()
                }
                
                placeholder_char = "?" if char == " " else char
                placeholder_str = NSAttributedString.alloc().initWithString_attributes_(placeholder_char, attrs)
                text_size = placeholder_str.size()
                text_x = x_offset + (placeholder_width - text_size.width) / 2.0
                text_y = view_baseline + (placeholder_height - text_size.height) / 2.0
                placeholder_str.drawAtPoint_((text_x, text_y))
                
                fontLabel = NSFont.systemFontOfSize_(10)
                if is_static:
                    label_text = f"Static: {self.static_char} (missing)"
                    color = NSColor.redColor()
                else:
                    label_text = f"Dynamic: {char} (missing)"
                    
                    xheight_percentage = 70
                    
                    if self.dynamicScale == 1.0:
                        label_text += f" ({xheight_percentage}% xH)"
                    elif self.dynamicScale == 0.0:
                        label_text += " (100% H)"
                    else:
                        current_percentage = 100 - int((100 - xheight_percentage) * self.dynamicScale)
                        if current_percentage < 100:
                            label_text += f" ({current_percentage}% xH)"
                        else:
                            label_text += f" ({current_percentage}% H)"
                    
                    color = NSColor.redColor()
                
                label_attrs = {
                    NSFontAttributeName: fontLabel,
                    NSForegroundColorAttributeName: color
                }
                
                label_str = NSAttributedString.alloc().initWithString_attributes_(label_text, label_attrs)
                label_size = label_str.size()
                label_x = x_offset + (placeholder_width - label_size.width) / 2.0
                label_y = 5
                label_str.drawAtPoint_((label_x, label_y))
                
            except Exception:
                pass

        @objc.python_method
        def _drawMetrics(self, master, scale, view_baseline, w, h):
            asc = float(master.ascender)
            xh = float(master.xHeight)
            desc = float(master.descender)
            cap = float(getattr(master, 'capHeight', 700))
            
            gray_color = NSColor.grayColor().colorWithAlphaComponent_(0.5)
            lines = [
                (view_baseline + (asc * scale), f"Asc ({int(asc)})", gray_color),
                (view_baseline + (cap * scale), f"Cap ({int(cap)})", gray_color),
                (view_baseline + (xh * scale), f"xH ({int(xh)})", gray_color),
                (view_baseline, "Base (0)", gray_color),
                (view_baseline + (desc * scale), f"Desc ({int(desc)})", gray_color)
            ]
            
            for y_pos, label, color in lines:
                if 0 <= y_pos <= h:
                    color.set()
                    line_path = NSBezierPath.bezierPath()
                    line_path.moveToPoint_((10, y_pos))
                    line_path.lineToPoint_((w - 10, y_pos))
                    line_path.setLineWidth_(1.0)
                    line_path.stroke()
                    
                    fontLabel = NSFont.systemFontOfSize_(9)
                    attrs = {NSFontAttributeName: fontLabel, NSForegroundColorAttributeName: color}
                    NSAttributedString.alloc().initWithString_attributes_(label, attrs).drawAtPoint_((5, y_pos + 2))

        @objc.python_method
        def _drawXbeam(self, master, scale, view_baseline, w, h):
            try:
                if not self.showXbeam:
                    return
        
                xbeam_y_view = view_baseline + (self.xbeamPosition * scale)
        
                NSColor.blueColor().colorWithAlphaComponent_(0.7).set()
                beam = NSBezierPath.bezierPath()
                beam.moveToPoint_((10, xbeam_y_view))
                beam.lineToPoint_((w - 10, xbeam_y_view))
                beam.setLineDash_count_phase_([4, 2], 2, 0)
                beam.setLineWidth_(2)
                beam.stroke()
        
                char_x = 20
                all_chars = []
        
                if self.static_char and self.static_char != " ":
                    all_chars.append((self.static_char, True))
        
                if self.dynamic_chars:
                    for ch in self.dynamic_chars:
                        if ch and ch != " ":
                            all_chars.append((ch, False))
        
                for char, is_static in all_chars:
                    char_data = self._getTransformedCharData(char, is_static)
                    if not char_data or not char_data['layer']:
                        if is_static:
                            char_x += 150 * scale + 20
                        else:
                            char_x += 150 * scale + 20
                        continue
            
                    layer = char_data['layer']
                    actual_scale = char_data['scale']
            
                    glyphPath = self.buildPathFromLayer(layer)
                    if glyphPath:
                        transform = NSAffineTransform.transform()
                        transform.translateXBy_yBy_(char_x, view_baseline)
                        transform.scaleXBy_yBy_(actual_scale, actual_scale)
                
                        path = glyphPath.copy()
                        path.transformUsingAffineTransform_(transform)
                
                        segments = self._getXbeamSegmentsFromPath(path, xbeam_y_view)
                
                        for x1, x2 in segments:
                            color = NSColor.redColor() if is_static else NSColor.orangeColor()
                            color.set()
                    
                            seg = NSBezierPath.bezierPath()
                            seg.moveToPoint_((x1, xbeam_y_view))
                            seg.lineToPoint_((x2, xbeam_y_view))
                            seg.setLineWidth_(3)
                            seg.stroke()
                    
                            width_pixels = abs(x2 - x1)
                            width_font_units = width_pixels / scale if scale > 0 else 0
                    
                            label = f"{int(round(width_font_units))}"
                            font = NSFont.systemFontOfSize_(9)
                        
                            label_attrs = {
                                NSFontAttributeName: font,
                                NSForegroundColorAttributeName: color
                            }
                            label_str = NSAttributedString.alloc().initWithString_attributes_(label, label_attrs)
                            label_size = label_str.size()
                        
                            rect_width = max(20, label_size.width + 6)
                            rect_height = label_size.height + 4
                            rect_x = ((x1 + x2) / 2) - (rect_width / 2)
                            rect_y = xbeam_y_view + 2
                        
                            NSColor.whiteColor().set()
                            bg_rect = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                                ((rect_x, rect_y), (rect_width, rect_height)), 3, 3)
                            bg_rect.fill()
                        
                            NSColor.lightGrayColor().set()
                            bg_rect.setLineWidth_(0.5)
                            bg_rect.stroke()
                        
                            text_x = rect_x + (rect_width - label_size.width) / 2
                            text_y = rect_y + (rect_height - label_size.height) / 2
                            label_str.drawAtPoint_((text_x, text_y))
            
                    char_x += char_data['width']
        
            except Exception:
                pass
                
        @objc.python_method
        def _drawYbeam(self, master, scale, view_baseline, w, h):
            try:
                if not self.showYbeam:
                    return
        
                char_x = 20
                all_chars = []
        
                if self.static_char and self.static_char != " ":
                    all_chars.append((self.static_char, True))
        
                if self.dynamic_chars:
                    for ch in self.dynamic_chars:
                        if ch and ch != " ":
                            all_chars.append((ch, False))
        
                for char, is_static in all_chars:
                    char_data = self._getTransformedCharData(char, is_static)
                    if not char_data or not char_data['layer']:
                        if is_static:
                            char_x += 150 * scale + 20
                        else:
                            char_x += 150 * scale + 20
                        continue
            
                    layer = char_data['layer']
                    actual_scale = char_data['scale']
            
                    beam_x_view = char_x + (self.ybeamPosition * actual_scale)
            
                    NSColor.darkGrayColor().colorWithAlphaComponent_(0.7).set()
                    beam = NSBezierPath.bezierPath()
                    beam.moveToPoint_((beam_x_view, 10))
                    beam.lineToPoint_((beam_x_view, h - 10))
                    beam.setLineDash_count_phase_([4, 2], 2, 0)
                    beam.setLineWidth_(2)
                    beam.stroke()
            
                    glyphPath = self.buildPathFromLayer(layer)
                    if glyphPath:
                        transform = NSAffineTransform.transform()
                        transform.translateXBy_yBy_(char_x, view_baseline)
                        transform.scaleXBy_yBy_(actual_scale, actual_scale)
                
                        path = glyphPath.copy()
                        path.transformUsingAffineTransform_(transform)
                
                        segments = self._getYbeamSegmentsFromPath(path, beam_x_view)
                
                        for y1, y2 in segments:
                            seg = NSBezierPath.bezierPath()
                            seg.moveToPoint_((beam_x_view, y1))
                            seg.lineToPoint_((beam_x_view, y2))
                            seg.setLineWidth_(3)
                            seg.stroke()
                    
                            height_pixels = abs(y2 - y1)
                            height_font_units = height_pixels / scale if scale > 0 else 0
                    
                            label = f"{int(round(height_font_units))}"
                            font = NSFont.systemFontOfSize_(9)
                        
                            color = NSColor.darkGrayColor()
                            label_attrs = {
                                NSFontAttributeName: font,
                                NSForegroundColorAttributeName: color
                            }
                            label_str = NSAttributedString.alloc().initWithString_attributes_(label, label_attrs)
                            label_size = label_str.size()
                        
                            rect_width = max(20, label_size.width + 6)
                            rect_height = label_size.height + 4
                            rect_x = beam_x_view + 4
                            rect_y = ((y1 + y2) / 2) - (rect_height / 2)
                        
                            NSColor.whiteColor().set()
                            bg_rect = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                                ((rect_x, rect_y), (rect_width, rect_height)), 3, 3)
                            bg_rect.fill()
                        
                            NSColor.lightGrayColor().set()
                            bg_rect.setLineWidth_(0.5)
                            bg_rect.stroke()
                        
                            text_x = rect_x + (rect_width - label_size.width) / 2
                            text_y = rect_y + (rect_height - label_size.height) / 2
                            label_str.drawAtPoint_((text_x, text_y))
            
                    char_x += char_data['width']
        
            except Exception:
                pass

        @objc.python_method
        def _drawMessage(self, message):
            w = self.bounds().size.width
            h = self.bounds().size.height
            font = NSFont.systemFontOfSize_(12)
            attrs = {
                NSFontAttributeName: font,
                NSForegroundColorAttributeName: NSColor.grayColor()
            }
            msg_str = NSAttributedString.alloc().initWithString_attributes_(message, attrs)
            msg_size = msg_str.size()
            x = (w - msg_size.width) / 2
            y = (h - msg_size.height) / 2
            msg_str.drawAtPoint_((x, y))

    _combined_preview_class_registered = True

class CombinedPreviewWrapper(object):
    def __init__(self, posSize):
        self.view = CombinedPreviewView.alloc().initWithFrame_(((0, 0), (posSize[2], posSize[3])))
        self._nsObject = self.view
        
    def setDynamicScale(self, scale):
        self.view.setDynamicScale_(scale)
        
    def setWidthScale(self, scale):
        self.view.setWidthScale_(scale)
        
    def getNSView(self):
        return self._nsObject

    def setStaticChar(self, ch):
        self.view.setStaticChar_(ch)

    def setDynamicChars(self, chars):
        self.view.setDynamicChars_(chars)

    def setMetrics(self, metrics):
        self.view.setMetrics_(metrics)
        
    def setXbeamPosition(self, position):
        self.view.setXbeamPosition_(position)
        
    def setYbeamPosition(self, position):
        self.view.setYbeamPosition_(position)
        
    def setShowXbeam(self, show):
        self.view.setShowXbeam_(show)
        
    def setShowYbeam(self, show):
        self.view.setShowYbeam_(show)
        
    def setAxisValues(self, axisValues):
        self.view.setAxisValues_(axisValues)

class CocoaViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject

def generate_numerals_smallcaps(font, master_id, axis_values, scale_percentages, 
                                selected_punctuation=None, selected_symbols=None, selected_others=None):
    try:
        if selected_punctuation is None:
            selected_punctuation = []
        if selected_symbols is None:
            selected_symbols = []
        if selected_others is None:
            selected_others = []
            
        font_has_smart_axes = False
        
        if hasattr(font, 'smartComponentAxes'):
            smart_axes = font.smartComponentAxes
            if smart_axes is not None and hasattr(smart_axes, '__len__') and len(smart_axes) > 0:
                font_has_smart_axes = True
        
        if font_has_smart_axes:
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Component Type")
            alert.setInformativeText_("This font has Smart Component capabilities.\n\n"
                                     "What type of components do you want to create?\n\n"
                                     "• Smart Components: Can be interpolated\n"
                                     "• Regular Components: Simple, fixed scale")
            alert.addButtonWithTitle_("Smart Components")
            alert.addButtonWithTitle_("Regular Components")
            alert.addButtonWithTitle_("Cancel")
        
            result = alert.runModal()
        
            if result == NSAlertFirstButtonReturn:
                return generate_smart_numerals_smallcaps(font, master_id, axis_values, scale_percentages, 
                                                         selected_punctuation, selected_symbols, selected_others)
            elif result == NSAlertSecondButtonReturn:
                pass
            else:
                return 0
        
        master = None
        for m in font.masters:
            if m.id == master_id:
                master = m
                break
    
        if not master:
            return 0
    
        cap_height = float(getattr(master, 'capHeight', 700))
    
        all_glyphs = []
        glyphs_dict = get_uppercase_glyphs()
        
        if 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals']:
            numeral_glyphs = [n for n in glyphs_dict['numerals']['digits'] if n in font.glyphs]
            all_glyphs.extend(numeral_glyphs)
        
        for glyph_name in selected_symbols:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        for glyph_name in selected_punctuation:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        for glyph_name in selected_others:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        special_forms = {}
        for form_type in ['numr', 'dnom', 'sinf', 'sups']:
            if form_type in scale_percentages:
                scale = float(scale_percentages[form_type])
                scale = max(10, min(scale, 200))
                special_forms[form_type] = scale
        
        if not special_forms:
            return 0
    
        existing = []
        for glyph_name in all_glyphs:
            for form_type in special_forms.keys():
                form_name = f"{glyph_name}.{form_type}"
                if form_name in font.glyphs:
                    existing.append(form_name)
        
        if existing:
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Update Existing Glyphs?")
            alert.setInformativeText_(f"{len(existing)} special form glyphs already exist.\n\n"
                                     f"This will UPDATE their scale and positioning.\n\n"
                                     f"Continue?")
            alert.addButtonWithTitle_("Update")
            alert.addButtonWithTitle_("Cancel")
            
            if alert.runModal() != NSAlertFirstButtonReturn:
                return 0
        
        generated = 0
        updated = 0
        font.disableUpdateInterface()
        
        try:
            for glyph_name in all_glyphs:
                base_glyph = font.glyphs[glyph_name]
                base_layer = None
                
                for layer in base_glyph.layers:
                    if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master_id) or \
                       (hasattr(layer, 'masterId') and layer.masterId == master_id):
                        base_layer = layer
                        break
                
                if not base_layer and base_glyph.layers:
                    base_layer = base_glyph.layers[0]
                
                if not base_layer:
                    continue
                
                bounds = base_layer.bounds
                if not bounds:
                    continue
                
                base_height = bounds.size.height
                base_min_y = bounds.origin.y
                base_max_y = base_min_y + base_height
                base_center_y = base_min_y + (base_height / 2.0)
                
                for form_type, scale_percent in special_forms.items():
                    form_name = f"{glyph_name}.{form_type}"
                    
                    scale = scale_percent / 100.0
                    width_scale = scale_percentages.get('width', 100) / 100.0
                    
                    translate_y = 0.0
                    
                    if form_type == 'numr':
                        scaled_max_y = base_max_y * scale
                        translate_y = cap_height - scaled_max_y
                        
                    elif form_type == 'dnom':
                        scaled_min_y = base_min_y * scale
                        translate_y = -scaled_min_y
                        
                    elif form_type == 'sinf':
                        scaled_center_y = base_center_y * scale
                        translate_y = -scaled_center_y
                        
                    elif form_type == 'sups':
                        scaled_center_y = base_center_y * scale
                        translate_y = cap_height - scaled_center_y
                    
                    glyph_exists = form_name in font.glyphs
                    
                    if glyph_exists:
                        formglyph = font.glyphs[form_name]
                        updated += 1
                        
                        if master_id in formglyph.layers:
                            del formglyph.layers[master_id]
                    else:
                        formglyph = GSGlyph(form_name)
                        
                        if 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals'] and glyph_name in glyphs_dict['numerals']['digits']:
                            formglyph.category = "Number"
                        elif glyph_name in PUNCTUATION_GLYPHS:
                            formglyph.category = "Separator"
                        else:
                            formglyph.category = "Symbol"
                        
                        formglyph.subCategory = f"Special{form_type.capitalize()}"
                        
                        formglyph.leftMetricsKey = f"={glyph_name}"
                        formglyph.rightMetricsKey = f"={glyph_name}"
                        formglyph.widthMetricsKey = f"={glyph_name}"
                        
                        font.glyphs.append(formglyph)
                        generated += 1
                    
                    layer = GSLayer()
                    
                    component = GSComponent(glyph_name)
                    layer.components.append(component)
                    
                    transform = NSAffineTransformStruct(
                        m11=scale * width_scale,
                        m12=0.0,
                        m21=0.0,
                        m22=scale,
                        tX=0.0,
                        tY=translate_y
                    )
                    component.transform = transform
                    
                    alignment_set = False
                    
                    if hasattr(component, 'automaticAlignment'):
                        try:
                            component.automaticAlignment = True
                            alignment_set = True
                        except Exception:
                            pass
                    
                    if not alignment_set and hasattr(component, 'setAutomaticAlignment_'):
                        try:
                            component.setAutomaticAlignment_(True)
                            alignment_set = True
                        except Exception:
                            pass
                    
                    if not alignment_set:
                        try:
                            component.setValue_forKey_(True, "automaticAlignment")
                            alignment_set = True
                        except Exception:
                            pass
                    
                    formglyph.layers[master_id] = layer
        
        except Exception:
            pass
            
        finally:
            font.enableUpdateInterface()
            
            try:
                if hasattr(font, 'currentTab') and font.currentTab:
                    font.currentTab.graphicView().redraw()
            except Exception:
                pass
        
        total = generated + updated
        
        if total > 0:
            forms_list = "\n".join([f"• .{ft}: {sp}%" for ft, sp in special_forms.items()])
            
            alert = NSAlert.alloc().init()
            alert.setMessageText_("✅ Special Forms Generated")
            alert.setInformativeText_(f"Successfully processed {total} glyphs:\n\n"
                                     f"New: {generated}\n"
                                     f"Updated: {updated}\n\n"
                                     f"Scales applied:\n{forms_list}")
            alert.addButtonWithTitle_("OK")
            alert.setAlertStyle_(NSInformationalAlertStyle)
            alert.runModal()
        
        return total
        
    except Exception as e:
        print(f"Error in generate_numerals_smallcaps: {e}")
        return 0

def generate_smart_numerals_smallcaps(font, master_id, axis_values, scale_percentages, 
                                      selected_punctuation=None, selected_symbols=None, selected_others=None):
    try:
        if selected_punctuation is None:
            selected_punctuation = []
        if selected_symbols is None:
            selected_symbols = []
        if selected_others is None:
            selected_others = []
            
        master = None
        for m in font.masters:
            if m.id == master_id:
                master = m
                break
    
        if not master:
            return 0
        
        has_smart_axes = False
        smart_axes_info = []
        if hasattr(font, 'smartComponentAxes'):
            smart_axes = font.smartComponentAxes
            if smart_axes and len(smart_axes) > 0:
                has_smart_axes = True
                for axis in smart_axes:
                    axis_info = {
                        'name': axis.name,
                        'axisId': axis.axisId,
                        'bottomValue': axis.bottomValue,
                        'topValue': axis.topValue,
                        'defaultValue': getattr(axis, 'defaultValue', (axis.bottomValue + axis.topValue) / 2)
                    }
                    smart_axes_info.append(axis_info)
        
        if not has_smart_axes:
            return generate_numerals_smallcaps(font, master_id, axis_values, scale_percentages, 
                                              selected_punctuation, selected_symbols, selected_others)
        
        all_glyphs = []
        glyphs_dict = get_uppercase_glyphs()
        
        if 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals']:
            numeral_glyphs = [n for n in glyphs_dict['numerals']['digits'] if n in font.glyphs]
            all_glyphs.extend(numeral_glyphs)
        
        for glyph_name in selected_symbols:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        for glyph_name in selected_punctuation:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        for glyph_name in selected_others:
            if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                all_glyphs.append(glyph_name)
        
        special_forms = {}
        for form_type in ['numr', 'dnom', 'sinf', 'sups']:
            if form_type in scale_percentages:
                scale = float(scale_percentages[form_type])
                scale = max(10, min(scale, 200))
                special_forms[form_type] = scale
        
        if not special_forms:
            return 0
    
        existing = []
        for glyph_name in all_glyphs:
            for form_type in special_forms.keys():
                form_name = f"{glyph_name}.{form_type}"
                if form_name in font.glyphs:
                    existing.append(form_name)
        
        if existing:
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Update Existing Glyphs?")
            alert.setInformativeText_(f"{len(existing)} special form glyphs already exist.\n\n"
                                     f"This will UPDATE their scale and positioning.\n\n"
                                     f"Continue?")
            alert.addButtonWithTitle_("Update")
            alert.addButtonWithTitle_("Cancel")
            
            if alert.runModal() != NSAlertFirstButtonReturn:
                return 0
        
        generated = 0
        updated = 0
        font.disableUpdateInterface()
        
        try:
            for glyph_name in all_glyphs:
                base_glyph = font.glyphs[glyph_name]
                base_layer = None
                
                for layer in base_glyph.layers:
                    if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master_id) or \
                       (hasattr(layer, 'masterId') and layer.masterId == master_id):
                        base_layer = layer
                        break
                
                if not base_layer and base_glyph.layers:
                    base_layer = base_glyph.layers[0]
                
                if not base_layer:
                    continue
                
                bounds = base_layer.bounds
                if not bounds:
                    continue
                
                base_height = bounds.size.height
                base_min_y = bounds.origin.y
                base_max_y = base_min_y + base_height
                base_center_y = base_min_y + (base_height / 2.0)
                
                for form_type, scale_percent in special_forms.items():
                    form_name = f"{glyph_name}.{form_type}"
                    
                    scale = scale_percent / 100.0
                    width_scale = scale_percentages.get('width', 100) / 100.0
                    
                    translate_y = 0.0
                    cap_height = float(getattr(master, 'capHeight', 700))
                    
                    if form_type == 'numr':
                        scaled_max_y = base_max_y * scale
                        translate_y = cap_height - scaled_max_y
                        
                    elif form_type == 'dnom':
                        scaled_min_y = base_min_y * scale
                        translate_y = -scaled_min_y
                        
                    elif form_type == 'sinf':
                        scaled_center_y = base_center_y * scale
                        translate_y = -scaled_center_y
                        
                    elif form_type == 'sups':
                        scaled_center_y = base_center_y * scale
                        translate_y = cap_height - scaled_center_y
                    
                    glyph_exists = form_name in font.glyphs
                    
                    if glyph_exists:
                        formglyph = font.glyphs[form_name]
                        updated += 1
                        
                        if master_id in formglyph.layers:
                            del formglyph.layers[master_id]
                    else:
                        formglyph = GSGlyph(form_name)
                        
                        if 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals'] and glyph_name in glyphs_dict['numerals']['digits']:
                            formglyph.category = 'numerals'
                        elif glyph_name in PUNCTUATION_GLYPHS:
                            formglyph.category = "Separator"
                        else:
                            formglyph.category = 'symbols'
                        
                        formglyph.subCategory = f"Special{form_type.capitalize()}"
                        
                        formglyph.leftMetricsKey = f"={glyph_name}"
                        formglyph.rightMetricsKey = f"={glyph_name}"
                        formglyph.widthMetricsKey = f"={glyph_name}"
                        
                        font.glyphs.append(formglyph)
                        generated += 1
                    
                    layer = GSLayer()
                    
                    component = GSComponent(glyph_name)
                    layer.components.append(component)
                    
                    transform = NSAffineTransformStruct(
                        m11=scale * width_scale,
                        m12=0.0,
                        m21=0.0,
                        m22=scale,
                        tX=0.0,
                        tY=translate_y
                    )
                    component.transform = transform
                    
                    alignment_set = False
                    if hasattr(component, 'automaticAlignment'):
                        try:
                            component.automaticAlignment = False
                            alignment_set = True
                        except Exception:
                            pass
                    
                    if hasattr(component, 'smartComponentValues'):
                        for axis_info in smart_axes_info:
                            axis_name = axis_info['name']
                            axis_id = axis_info['axisId']
                            
                            target_value = None
                            
                            axis_lower = axis_name.lower()
                            if 'size' in axis_lower or 'scale' in axis_lower or 'height' in axis_lower:
                                target_value = scale * 100
                            elif 'weight' in axis_lower:
                                target_value = axis_info['defaultValue']
                            else:
                                target_value = axis_info['defaultValue']
                            
                            try:
                                component.smartComponentValues[axis_name] = target_value
                            except:
                                pass
                            
                            try:
                                component.smartComponentValues[str(axis_id)] = target_value
                            except:
                                pass
                            
                            try:
                                component.setValue_forKey_(target_value, axis_name)
                            except:
                                pass
                            
                            if hasattr(component, axis_name):
                                try:
                                    setattr(component, axis_name, target_value)
                                except:
                                    pass
                        
                        try:
                            if hasattr(component, 'updateSmartComponentValues'):
                                component.updateSmartComponentValues()
                        except:
                            pass
                    
                    formglyph.layers[master_id] = layer
        
        except Exception:
            pass
            
        finally:
            font.enableUpdateInterface()
            
            try:
                if hasattr(font, 'currentTab') and font.currentTab:
                    font.currentTab.graphicView().redraw()
            except Exception:
                pass
        
        total = generated + updated
        
        if total > 0:
            forms_list = "\n".join([f"• .{ft}: {sp}%" for ft, sp in special_forms.items()])
            
            alert = NSAlert.alloc().init()
            alert.setMessageText_("✅ Smart Special Forms Generated")
            alert.setInformativeText_(f"Successfully processed {total} glyphs:\n\n"
                                     f"New: {generated}\n"
                                     f"Updated: {updated}\n\n"
                                     f"Scales applied:\n{forms_list}\n\n"
                                     f"Note: Created as SMART COMPONENTS.")
            alert.addButtonWithTitle_("OK")
            alert.setAlertStyle_(NSInformationalAlertStyle)
            alert.runModal()
        
        return total
        
    except Exception:
        return 0

class CombinedGlyphPreviewPanel:
    def tabChanged(self, sender):
        try:
            old_tab = getattr(self, 'current_tab', 0)
            self.current_tab = self.w.tabs.get()
        
            if self.current_tab == 0:
                self.setMaster(self.w.tabs[0].masterPopup.get())
                self.updatePreview()
            elif self.current_tab == 1:
                self.setNumbersMaster(self.w.tabs[1].masterPopup.get())
                self.updateNumbersPreview()
            elif self.current_tab == 2:
                pass
        
        except Exception:
            pass
                      
    def getRealAxes(self):
        axes = []
        try:
            font = Glyphs.font
            if font and hasattr(font, 'axes'):
                for idx, axis in enumerate(font.axes):
                    master_values = [m.axes[idx] for m in font.masters]
                    min_val = min(master_values)
                    max_val = max(master_values)
                    default_val = master_values[0] if master_values else min_val
            
                    current_range = max_val - min_val
                    # Ampliar zona de extrapolación al 25% por delante y 25% por detrás
                    extension_start = current_range * 0.45  # Antes era 0.12
                    extension_end = current_range * 0.75    # Antes era 0.50
            
                    extended_min = min_val - extension_start
                    extended_max = max_val + extension_end
            
                    axis_name = getattr(axis, "name", f"Axis {idx+1}")
                    axis_tag = getattr(axis, "axisTag", "")
            
                    axes.append({
                        'name': axis_name,
                        'tag': axis_tag,
                        'minValue': min_val,
                        'maxValue': max_val,
                        'defaultValue': default_val,
                        'extendedMin': extended_min,
                        'extendedMax': extended_max,
                        'extensionStartPercent': 25,  # Actualizado
                        'extensionEndPercent': 25     # Actualizado
                    })
        except Exception:
            pass
        return axes       
    def __init__(self):
        try:
            self.font = Glyphs.font
            if not self.font:
                return

            self.current_tab = 0
    
            self.axes = self.getRealAxes()
            num_axes = len(self.axes)

            base_height = 700 + (num_axes * 30)
            self.w = Window((1000, base_height), "Intermediate Glyphs Maker - Combined Preview")

            self.w.tabs = Tabs(
                (0, 0, -0, -0),
                ["Letters", "Numbers", "Glyphs preferences"]
            )
    
            letters_tab = self.w.tabs[0]
    
            letters_tab.title = TextBox((20, 15, 960, 22), 
                                      "Combined Preview: Static (left) + Dynamic (right)", 
                                      sizeStyle="small")

            letters_tab.staticCharLabel = TextBox((20, 45, 80, 22), "Init char:")
            letters_tab.staticChar = EditText((100, 45, 50, 22), "H", callback=self.updatePreview)

            letters_tab.dynamicCharsLabel = TextBox((170, 45, 100, 22), "Dynamic chars:")
            letters_tab.dynamicChars = EditText((270, 45, 200, 22), "HXD", callback=self.updatePreview)

            masters = [m.name for m in self.font.masters]
            letters_tab.masterLabel = TextBox((20, 80, 50, 22), "Master:")
            letters_tab.masterPopup = PopUpButton((90, 80, 200, 22), masters, callback=self.masterChanged)

            right_column_y = 120

            letters_tab.xbeamLabel = TextBox((380, right_column_y, 80, 22), "Xbeam:")
            letters_tab.xbeamSlider = Slider((440, right_column_y, 120, 22), 
                                           minValue=-200, maxValue=1000, value=0, 
                                           callback=self.xbeamChanged)
            letters_tab.xbeamValue = EditText((580, right_column_y, 40, 22), "0",
                                            callback=self.xbeamValueChanged)
            letters_tab.xbeamMinus = Button((625, right_column_y, 20, 22), "◀", 
                                          callback=self.xbeamDecrement)
            letters_tab.xbeamPlus = Button((650, right_column_y, 20, 22), "▶", 
                                         callback=self.xbeamIncrement)
            letters_tab.xbeamHide = CheckBox((675, right_column_y, 60, 22), "Hide", 
                                           callback=self.xbeamHideChanged)

            right_column_y += 30

            letters_tab.ybeamLabel = TextBox((380, right_column_y, 80, 22), "Ybeam:")
            letters_tab.ybeamSlider = Slider((440, right_column_y, 120, 22), 
                                           minValue=0, maxValue=1000, value=300, 
                                           callback=self.ybeamChanged)
            letters_tab.ybeamValue = EditText((580, right_column_y, 40, 22), "300",
                                            callback=self.ybeamValueChanged)
            letters_tab.ybeamMinus = Button((625, right_column_y, 20, 22), "◀", 
                                          callback=self.ybeamDecrement)
            letters_tab.ybeamPlus = Button((650, right_column_y, 20, 22), "▶", 
                                         callback=self.ybeamIncrement)
            letters_tab.ybeamHide = CheckBox((675, right_column_y, 60, 22), "Hide", 
                                           callback=self.ybeamHideChanged)

            right_column_y += 30

            letters_tab.dynamicScaleLabel = TextBox((380, right_column_y, 80, 22), "Height:")
            letters_tab.dynamicScaleSlider = Slider((440, right_column_y, 120, 22), 
                                                 minValue=0, maxValue=100, value=100,
                                                 callback=self.dynamicScaleChanged)
            letters_tab.dynamicScaleValue = EditText((580, right_column_y, 40, 22), "100%",
                                                  callback=self.dynamicScaleValueChanged)
            letters_tab.heightMinus = Button((625, right_column_y, 20, 22), "◀", 
                                           callback=self.heightDecrement)
            letters_tab.heightPlus = Button((650, right_column_y, 20, 22), "▶", 
                                          callback=self.heightIncrement)

            right_column_y += 30

            letters_tab.widthScaleLabel = TextBox((380, right_column_y, 80, 22), "Width:")
            letters_tab.widthScaleSlider = Slider((440, right_column_y, 120, 22), 
                                               minValue=50, maxValue=200, value=100,
                                               callback=self.widthScaleChanged)
            letters_tab.widthScaleValue = EditText((580, right_column_y, 40, 22), "100%",
                                                callback=self.widthScaleValueChanged)
            letters_tab.widthMinus = Button((625, right_column_y, 20, 22), "◀", 
                                          callback=self.widthDecrement)
            letters_tab.widthPlus = Button((650, right_column_y, 20, 22), "▶", 
                                         callback=self.widthIncrement)

            right_column_y += 30

            axes_y = 120
            self.axes_controls = {}

            if self.axes:
                for i, axis in enumerate(self.axes):
                    label_name = f"axis_label_{i}"
                    slider_name = f"axis_slider_{i}"
                    value_name = f"axis_value_{i}"
                    minus_name = f"axis_minus_{i}"
                    plus_name = f"axis_plus_{i}"
                    hide_name = f"axis_hide_{i}"
            
                    setattr(letters_tab, label_name, TextBox((20, axes_y, 80, 22), f"{axis['name']}:"))
            
                    slider = Slider((100, axes_y, 120, 22),
                                  minValue=axis['extendedMin'],
                                  maxValue=axis['extendedMax'],
                                  value=axis['defaultValue'], 
                                  callback=self.axisChanged)
                    setattr(letters_tab, slider_name, slider)
            
                    axis_field = EditText((230, axes_y, 40, 22), f"{int(axis['defaultValue'])}",
                                        callback=self.axisValueChanged)
                    setattr(letters_tab, value_name, axis_field)
            
                    minus_btn = Button((275, axes_y, 20, 22), "◀", 
                                     callback=lambda s, idx=i: self.axisDecrement(idx))
                    setattr(letters_tab, minus_name, minus_btn)
            
                    plus_btn = Button((300, axes_y, 20, 22), "▶", 
                                    callback=lambda s, idx=i: self.axisIncrement(idx))
                    setattr(letters_tab, plus_name, plus_btn)
            
                    hide_checkbox = CheckBox((325, axes_y, 60, 22), "Hide",
                                           callback=self.axisHideChanged)
                    setattr(letters_tab, hide_name, hide_checkbox)

                    self.axes_controls[i] = {
                        'info': axis,
                        'field': axis_field,
                        'slider': slider,
                        'checkbox': hide_checkbox
                    }
                    axes_y += 30

            smallcaps_y = max(axes_y, right_column_y) + 20
            letters_tab.scSeparator = HorizontalLine((20, smallcaps_y, -20, 1))
            smallcaps_y += 10

            letters_tab.scTitle = TextBox((20, smallcaps_y, 200, 22), "Small Caps Generation", sizeStyle="small")
            smallcaps_y += 30

            letters_tab.scriptLabel = TextBox((20, smallcaps_y, 80, 22), "Script:")
            letters_tab.scriptType = PopUpButton((80, smallcaps_y, 120, 22), 
                                               ["latin", "cyrillic", "greek"])
            smallcaps_y += -2

            letters_tab.setsLabel = TextBox((220, smallcaps_y, 120, 22), "Sets:")
            letters_tab.includeLetters = CheckBox((270, smallcaps_y, 80, 22), "Letters", value=True)
            letters_tab.includeNumerals = CheckBox((350, smallcaps_y, 80, 22), "Numerals", value=True)
            letters_tab.includeSymbols = CheckBox((445, smallcaps_y, 80, 22), "Symbols", value=True)
            letters_tab.includePunctuation = CheckBox((530, smallcaps_y, 90, 22), "Punctuation", value=True)
            smallcaps_y += 0

            letters_tab.metricsOption = PopUpButton((650, smallcaps_y, 150, 22), 
                                                   ["Scale Sidebearings", "Equal Base Glyphs"])

            letters_tab.generateSC = Button((840, smallcaps_y, 120, 22), "Generate SC",
                                          callback=self.generateSmallCaps)

            preview_y = smallcaps_y + 40
            preview_height = 350

            self.combinedPreview = CombinedPreviewWrapper((20, preview_y, 960, preview_height))
            letters_tab.combinedPreview = CocoaViewWrapper((20, preview_y, 960, preview_height), 
                                                         self.combinedPreview.getNSView())

            numbers_tab = self.w.tabs[1]

            numbers_tab.title = TextBox((20, 15, 960, 22), 
                                      "Numerals Small Caps Generation", 
                                      sizeStyle="small")

            numbers_tab.staticCharLabel = TextBox((20, 45, 80, 22), "Init char:")
            numbers_tab.staticChar = EditText((100, 45, 50, 22), "H", callback=self.updateNumbersPreview)

            numbers_tab.dynamicCharsLabel = TextBox((170, 45, 100, 22), "Dynamic chars:")
            numbers_tab.dynamicChars = EditText((270, 45, 200, 22), "(123)", callback=self.updateNumbersPreview)

            right_column_y = 45

            numbers_tab.xbeamLabel = TextBox((480, right_column_y, 80, 22), "Xbeam:")
            numbers_tab.xbeamSlider = Slider((540, right_column_y, 120, 22), 
                                           minValue=-200, maxValue=1000, value=0, 
                                           callback=self.numbersXbeamChanged)
            numbers_tab.xbeamValue = EditText((680, right_column_y, 40, 22), "0",
                                            callback=self.numbersXbeamValueChanged)
            numbers_tab.xbeamMinus = Button((725, right_column_y, 20, 22), "◀", 
                                          callback=self.numbersXbeamDecrement)
            numbers_tab.xbeamPlus = Button((750, right_column_y, 20, 22), "▶", 
                                         callback=self.numbersXbeamIncrement)
            numbers_tab.xbeamHide = CheckBox((775, right_column_y, 60, 22), "Hide", 
                                           callback=self.numbersXbeamHideChanged)

            right_column_y += 30

            numbers_tab.ybeamLabel = TextBox((480, right_column_y, 80, 22), "Ybeam:")
            numbers_tab.ybeamSlider = Slider((540, right_column_y, 120, 22), 
                                           minValue=0, maxValue=1000, value=300, 
                                           callback=self.numbersYbeamChanged)
            numbers_tab.ybeamValue = EditText((680, right_column_y, 40, 22), "300",
                                            callback=self.numbersYbeamValueChanged)
            numbers_tab.ybeamMinus = Button((725, right_column_y, 20, 22), "◀", 
                                          callback=self.numbersYbeamDecrement)
            numbers_tab.ybeamPlus = Button((750, right_column_y, 20, 22), "▶", 
                                         callback=self.numbersYbeamIncrement)
            numbers_tab.ybeamHide = CheckBox((775, right_column_y, 60, 22), "Hide", 
                                           callback=self.numbersYbeamHideChanged)

            right_column_y += 30

            numbers_tab.masterLabel = TextBox((480, right_column_y, 120, 22), "Master:")
            numbers_tab.masterPopup = PopUpButton((540, right_column_y, 200, 22), masters, callback=self.numbersMasterChanged)

            right_column_y += 30

            left_column_y = 80

            numbers_tab.numHeightLabel = TextBox((20, left_column_y, 80, 22), "Height %:")
            numbers_tab.numHeightValue = EditText((100, left_column_y, 40, 22), "55",
                                                callback=self.numbersHeightChanged)
            numbers_tab.numHeightMinus = Button((145, left_column_y, 20, 22), "◀", 
                                              callback=self.numbersHeightDecrement)
            numbers_tab.numHeightPlus = Button((170, left_column_y, 20, 22), "▶", 
                                             callback=self.numbersHeightIncrement)

            left_column_y += 30

            numbers_tab.numWidthLabel = TextBox((20, left_column_y, 80, 22), "Width %:")
            numbers_tab.numWidthValue = EditText((100, left_column_y, 40, 22), "100",
                                               callback=self.numbersWidthChanged)
            numbers_tab.numWidthMinus = Button((145, left_column_y, 20, 22), "◀", 
                                             callback=self.numbersWidthDecrement)
            numbers_tab.numWidthPlus = Button((170, left_column_y, 20, 22), "▶", 
                                            callback=self.numbersWidthIncrement)

            self.numbers_axes_controls = {}
            if self.axes:
                axes_y = left_column_y + 30
                numbers_tab.axesLabel = TextBox((20, axes_y+5, 80, 22), "Axes:")

                axes_y += 30

                for i, axis in enumerate(self.axes):
                    label_name = f"numbers_axis_label_{i}"
                    slider_name = f"numbers_axis_slider_{i}"
                    value_name = f"numbers_axis_value_{i}"
                    minus_name = f"numbers_axis_minus_{i}"
                    plus_name = f"numbers_axis_plus_{i}"
                    hide_name = f"numbers_axis_hide_{i}"
            
                    setattr(numbers_tab, label_name, TextBox((20, axes_y, 80, 22), f"{axis['name']}:"))
            
                    slider = Slider((100, axes_y, 120, 22),
                                  minValue=axis['extendedMin'],
                                  maxValue=axis['extendedMax'],
                                  value=axis['defaultValue'], 
                                  callback=self.numbersAxisChanged)
                    setattr(numbers_tab, slider_name, slider)
            
                    axis_field = EditText((230, axes_y, 40, 22), f"{int(axis['defaultValue'])}",
                                        callback=self.numbersAxisValueChanged)
                    setattr(numbers_tab, value_name, axis_field)

                    minus_btn = Button((275, axes_y, 20, 22), "◀", 
                                     callback=lambda s, idx=i: self.numbersAxisDecrement(idx))
                    setattr(numbers_tab, minus_name, minus_btn)

                    plus_btn = Button((300, axes_y, 20, 22), "▶", 
                                    callback=lambda s, idx=i: self.numbersAxisIncrement(idx))
                    setattr(numbers_tab, plus_name, plus_btn)

                    hide_checkbox = CheckBox((325, axes_y, 60, 22), "Hide",
                                           callback=self.numbersAxisHideChanged)
                    setattr(numbers_tab, hide_name, hide_checkbox)

                    self.numbers_axes_controls[i] = {
                        'info': axis,
                        'field': axis_field,
                        'slider': slider,
                        'checkbox': hide_checkbox
                    }
                    axes_y += 30

            horizontal_y = max(axes_y if self.axes else left_column_y + 30, right_column_y) + 20

            numbers_tab.specialFormsTitle = TextBox((20, horizontal_y, 200, 22), "Select for generate and choose %", sizeStyle="small")
            horizontal_y += 30

            numbers_tab.numrCheck = CheckBox((20,280, 20, 22), "", value=True)
            numbers_tab.numrLabel = TextBox((40, 280, 50, 22), ".numr")

            numbers_tab.dnomCheck = CheckBox((170, 280, 20, 22), "", value=True)
            numbers_tab.dnomLabel = TextBox((190, 280, 50, 22), ".dnom")


            horizontal_y += 30

            numbers_tab.sinfCheck = CheckBox((100, 280, 20, 22), "", value=True)
            numbers_tab.sinfLabel = TextBox((120, 280, 50, 22), ".sinf")


            numbers_tab.supsCheck = CheckBox((260, 280, 20, 22), "", value=True)
            numbers_tab.supsLabel = TextBox((280, 280, 50, 22), ".sups")


            horizontal_y += 30

            numbers_tab.includeLabel = TextBox((20, 330, 60, 22), "Include")
            numbers_tab.includeSymbols = CheckBox((80, 330, 80, 22), "Symbols", value=True)
            numbers_tab.includePunctuation = CheckBox((170, 330, 100, 22), "Punctuation", value=False)

            numbers_tab.generateNumerals = Button((275, 330, 150, 22), "Generate Numerals",
                                                callback=self.generateNumerals)

            horizontal_y += 30
    
            horizontal_y += 30

    
            horizontal_y += 10

            preview_height = 350

            self.numbersPreview = CombinedPreviewWrapper((20, 370, 960, preview_height))
            numbers_tab.numbersPreview = CocoaViewWrapper((20, 370, 960, preview_height), 
                                                        self.numbersPreview.getNSView())
                                                    
            self.numbersPreview.setStaticChar("H")
            text = numbers_tab.dynamicChars.get()
            self.numbersPreview.setDynamicChars(text)

            self.numbersPreview.setXbeamPosition(0)
            self.numbersPreview.setYbeamPosition(300)
            self.numbersPreview.setDynamicScale(0.55)
            self.numbersPreview.setWidthScale(1.0)

            self.setNumbersMaster(0)

            print("\n=== Inicializando pestaña Glyphs preferences ===")
            print(f"PUNCTUATION_GLYPHS: {len(PUNCTUATION_GLYPHS)} glyphs")
            print(f"SYMBOL_GLYPHS: {len(SYMBOL_GLYPHS)} glyphs")
    
            pref = self.w.tabs[2]
    
            pref.punctuationTitle = TextBox((10, 10, 150, 20), "Punctuation")

            punct_symbol_map = {
                "period": ".", "comma": ",", "colon": ":", "semicolon": ";", "ellipsis": "…",
                "exclam": "!", "exclamdown": "¡", "question": "?", "questiondown": "¿",
                "periodcentered": "·", "bullet": "•", "asterisk": "*", "numbersign": "#",
                "slash": "/", "backslash": "\\", "hyphen": "-", "endash": "–", "emdash": "—",
                "parenleft": "(", "parenright": ")", "braceleft": "{", "braceright": "}",
                "bracketleft": "[", "bracketright": "]", "quotesinglbase": "‚", "quotedblbase": "„",
                "quotedblleft": "“", "quotedblright": "”", "quoteleft": "‘", "quoteright": "’",
                "guillemetleft": "«", "guillemetright": "»", "guilsinglleft": "‹", "guilsinglright": "›",
                "quotedbl": '"', "quotesingle": "'"
            }

            punctuation_items = []
            for glyph_name in PUNCTUATION_GLYPHS:
                display_char = punct_symbol_map.get(glyph_name, glyph_name)
                punctuation_items.append({
                    "glyph": glyph_name, 
                    "display": f"{display_char}  {glyph_name}", 
                    "use": True
                })

            pref.punctuationList = List(
                (10, 30, 290, 590),
                punctuation_items,
                columnDescriptions=[
                    {"title": "", "key": "use", "cell": CheckBoxListCell(), "width": 30},
                    {"title": "Glyph", "key": "display"}
                ]
            )

            pref.punctuationToggle = Button(
                (10, 640, 290, 20),
                "Deselect All",
                callback=self.togglePunctuation
            )
    
            pref.symbolTitle = TextBox((320, 10, 150, 20), "Symbols")
    
            symbol_map = {
                "at": "@", "ampersand": "&", "paragraph": "¶", "section": "§", "copyright": "©",
                "registered": "®", "trademark": "™", "degree": "°", "bar": "|", "brokenbar": "¦",
                "dagger": "†", "daggerdbl": "‡", "cent": "¢", "currency": "¤", "dollar": "$",
                "euro": "€", "sterling": "£", "yen": "¥", "plus": "+", "minus": "−",
                "multiply": "×", "divide": "÷", "equal": "=", "notequal": "≠", "greater": ">",
                "less": "<", "greaterequal": "≥", "lessequal": "≤", "plusminus": "±",
                "approxequal": "≈", "asciitilde": "~", "logicalnot": "¬", "asciicircum": "^",
                "percent": "%", "perthousand": "‰"
            }

            symbol_items = []
            for glyph_name in SYMBOL_GLYPHS:
                display_char = symbol_map.get(glyph_name, glyph_name)
                symbol_items.append({
                    "glyph": glyph_name, 
                    "display": f"{display_char}  {glyph_name}", 
                    "use": True
                })

            pref.symbolList = List(
                (320, 30, 290, 590),
                symbol_items,
                columnDescriptions=[
                    {"title": "", "key": "use", "cell": CheckBoxListCell(), "width": 30},
                    {"title": "Glyph", "key": "display"}
                ]
            )
    
            pref.symbolToggle = Button(
                (320, 640, 290, 20),
                "Deselect All",
                callback=self.toggleSymbols
            )
    
            pref.othersTitle = TextBox((630, 10, 150, 20), "Others")
    
            pref.othersList = List(
                (630, 30, 290, 590),
                [],
                columnDescriptions=[
                    {"title": "", "key": "use", "cell": CheckBoxListCell(), "width": 30},
                    {"title": "Glyph", "key": "glyph"}
                ]
            )
            print("Lista otros creada (vacía)")
    
            pref.addGlyph = Button(
                (630, 640, 95, 20),
                "Add Glyph",
                callback=self.addGlyph
            )
    
            pref.deleteGlyph = Button(
                (735, 640, 130, 20),
                "Delete Selected",
                callback=self.deleteGlyph
            )
    
            pref.save = Button(
                (10, 670, 100, 25),
                "Save Config",
                callback=self.saveConfig
            )
    
            pref.load = Button(
                (120, 670, 100, 25),
                "Load",
                callback=self.loadConfig
            )
    
            print("Verificando listas después de crear:")
            try:
                p_items = pref.punctuationList.get()
                print(f"Lista puntuación tiene {len(p_items)} items")
                if p_items:
                    print(f"Primer item: {p_items[0]}")
            except Exception as e:
                print(f"Error al obtener lista puntuación: {e}")
        
            try:
                s_items = pref.symbolList.get()
                print(f"Lista símbolos tiene {len(s_items)} items")
                if s_items:
                    print(f"Primer item: {s_items[0]}")
            except Exception as e:
                print(f"Error al obtener lista símbolos: {e}")
        
            try:
                o_items = pref.othersList.get()
                print(f"Lista otros tiene {len(o_items)} items")
            except Exception as e:
                print(f"Error al obtener lista otros: {e}")
        
            print("=== Inicialización de Glyphs preferences completada ===\n")
    
            self.current_tab = 0
            self.setMaster(0)
    
            self.updatePreview()
            self.current_tab = 1
            self.updateNumbersPreview()
            self.current_tab = 0
    
            self.w.open()
   
        except Exception as e:
            print(f"Error in __init__: {e}")
            import traceback
            traceback.print_exc()            
                
    def xbeamDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].xbeamValue.get())
            new_val = current_val - 1
            self.w.tabs[0].xbeamSlider.set(new_val)
            self.xbeamChanged()
        except:
            pass
    
    def xbeamIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].xbeamValue.get())
            new_val = current_val + 1
            self.w.tabs[0].xbeamSlider.set(new_val)
            self.xbeamChanged()
        except:
            pass
    
    def ybeamDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].ybeamValue.get())
            new_val = current_val - 1
            self.w.tabs[0].ybeamSlider.set(new_val)
            self.ybeamChanged()
        except:
            pass
    
    def ybeamIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].ybeamValue.get())
            new_val = current_val + 1
            self.w.tabs[0].ybeamSlider.set(new_val)
            self.ybeamChanged()
        except:
            pass
    
    def heightDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].dynamicScaleSlider.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[0].dynamicScaleSlider.set(new_val)
            self.dynamicScaleChanged()
        except:
            pass
    
    def heightIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].dynamicScaleSlider.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[0].dynamicScaleSlider.set(new_val)
            self.dynamicScaleChanged()
        except:
            pass
    
    def widthDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].widthScaleSlider.get())
            new_val = max(50, current_val - 1)
            self.w.tabs[0].widthScaleSlider.set(new_val)
            self.widthScaleChanged()
        except:
            pass
    
    def widthIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[0].widthScaleSlider.get())
            new_val = min(200, current_val + 1)
            self.w.tabs[0].widthScaleSlider.set(new_val)
            self.widthScaleChanged()
        except:
            pass
    
    def axisDecrement(self, axis_idx):
        try:
            axis_data = self.axes_controls[axis_idx]
            slider = axis_data['slider']
            current_val = float(slider.get())
            new_val = current_val - 1
            slider.set(new_val)
            self.axisChanged()
        except:
            pass
    
    def axisIncrement(self, axis_idx):
        try:
            axis_data = self.axes_controls[axis_idx]
            slider = axis_data['slider']
            current_val = float(slider.get())
            new_val = current_val + 1
            slider.set(new_val)
            self.axisChanged()
        except:
            pass
    
    def numbersHeightDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numHeightValue.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[1].numHeightValue.set(str(int(new_val)))
            self.updateNumbersPreview()
        except:
            pass
    
    def numbersHeightIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numHeightValue.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[1].numHeightValue.set(str(int(new_val)))
            self.updateNumbersPreview()
        except:
            pass
    
    def numbersWidthDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numWidthValue.get())
            new_val = max(50, current_val - 1)
            self.w.tabs[1].numWidthValue.set(str(int(new_val)))
            self.updateNumbersPreview()
        except:
            pass
    
    def numbersWidthIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numWidthValue.get())
            new_val = min(200, current_val + 1)
            self.w.tabs[1].numWidthValue.set(str(int(new_val)))
            self.updateNumbersPreview()
        except:
            pass
    
    def numrDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numrValue.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[1].numrValue.set(str(int(new_val)))
        except:
            pass
    
    def numrIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].numrValue.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[1].numrValue.set(str(int(new_val)))
        except:
            pass
    
    def dnomDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].dnomValue.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[1].dnomValue.set(str(int(new_val)))
        except:
            pass
    
    def dnomIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].dnomValue.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[1].dnomValue.set(str(int(new_val)))
        except:
            pass
    
    def sinfDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].sinfValue.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[1].sinfValue.set(str(int(new_val)))
        except:
            pass
    
    def sinfIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].sinfValue.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[1].sinfValue.set(str(int(new_val)))
        except:
            pass
    
    def supsDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].supsValue.get())
            new_val = max(0, current_val - 1)
            self.w.tabs[1].supsValue.set(str(int(new_val)))
        except:
            pass
    
    def supsIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].supsValue.get())
            new_val = min(100, current_val + 1)
            self.w.tabs[1].supsValue.set(str(int(new_val)))
        except:
            pass
    
    def updatePreview(self, sender=None):
        try:
            tab = self.w.tabs[0]
        
            static_char = tab.staticChar.get().strip()
            dynamic_chars = tab.dynamicChars.get().strip()
        
            if hasattr(self, 'combinedPreview'):
                self.combinedPreview.setStaticChar(static_char)
                self.combinedPreview.setDynamicChars(dynamic_chars)
            
        except Exception:
            pass            
                
    def masterChanged(self, sender=None):
        """Actualizar todos los controles al cambiar de master en la pestaña Letters"""
        try:
            idx = self.w.tabs[0].masterPopup.get()
            self.setMaster(idx)
        
            # Forzar la actualización de la vista previa
            self.updatePreview()
        
            # Actualizar también los valores de los ejes en la interfaz
            master = self.font.masters[idx]
            for i, axis_data in self.axes_controls.items():
                axis = axis_data['info']
                slider = axis_data['slider']
                axis_field = axis_data['field']
            
                # Obtener el valor del eje del master actual
                master_axis_value = master.axes[i]
            
                # Aplicar al slider
                slider.set(master_axis_value)
            
                # Actualizar el campo de texto
                is_extrapolated_start = master_axis_value < axis['minValue']
                is_extrapolated_end = master_axis_value > axis['maxValue']
            
                if is_extrapolated_start:
                    axis_field.set(f"{int(master_axis_value)}*◄")
                elif is_extrapolated_end:
                    axis_field.set(f"{int(master_axis_value)}*►")
                else:
                    axis_field.set(f"{int(master_axis_value)}")
        
            # Actualizar los valores de los ejes en la vista previa
            self.updateAxes()
        
        except Exception as e:
            print(f"Error in masterChanged: {e}")
            import traceback
            traceback.print_exc()
    
    def numbersMasterChanged(self, sender=None):
        """Actualizar todos los controles al cambiar de master en la pestaña Numbers"""
        try:
            idx = self.w.tabs[1].masterPopup.get()
            self.setNumbersMaster(idx)
        
            # Forzar la actualización de la vista previa de números
            self.updateNumbersPreview()
        
            # Actualizar también los valores de los ejes en la interfaz de números
            master = self.font.masters[idx]
            if hasattr(self, 'numbers_axes_controls'):
                for i, axis_data in self.numbers_axes_controls.items():
                    axis = axis_data['info']
                    slider = axis_data['slider']
                    axis_field = axis_data['field']
                    checkbox = axis_data['checkbox']
                
                    # Obtener el valor del eje del master actual
                    master_axis_value = master.axes[i]
                
                    # Solo actualizar si el slider no está oculto
                    if not checkbox.get():
                        # Aplicar al slider
                        slider.set(master_axis_value)
                    
                        # Actualizar el campo de texto
                        is_extrapolated_start = master_axis_value < axis['minValue']
                        is_extrapolated_end = master_axis_value > axis['maxValue']
                    
                        if is_extrapolated_start:
                            axis_field.set(f"{int(master_axis_value)}*◄")
                        elif is_extrapolated_end:
                            axis_field.set(f"{int(master_axis_value)}*►")
                        else:
                            axis_field.set(f"{int(master_axis_value)}")
            
                # Actualizar los valores de los ejes en la vista previa de números
                self.updateNumbersAxes()
        
        except Exception as e:
            print(f"Error in numbersMasterChanged: {e}")
            import traceback
            traceback.print_exc()

    def updateNumbersPreview(self, sender=None):
        try:
            tab = self.w.tabs[1]
        
            static_char = tab.staticChar.get().strip() or "0"
            dynamic_chars = tab.dynamicChars.get().strip() or ""

            if hasattr(self, 'numbersPreview'):
                self.numbersPreview.setStaticChar(static_char)
                self.numbersPreview.setDynamicChars(dynamic_chars)

                try:
                    height_percent = float(tab.numHeightValue.get() or 55)
                    width_percent = float(tab.numWidthValue.get() or 100)
                
                    self.numbersPreview.setDynamicScale(height_percent / 100.0)
                    self.numbersPreview.setWidthScale(width_percent / 100.0)
                except Exception:
                    pass

                if hasattr(tab, "xbeamSlider"):
                    xbeam_val = tab.xbeamSlider.get()
                    self.numbersPreview.setXbeamPosition(xbeam_val)

                if hasattr(tab, "ybeamSlider"):
                    ybeam_val = tab.ybeamSlider.get()
                    self.numbersPreview.setYbeamPosition(ybeam_val)
            
        except Exception:
            pass



    def setNumbersMaster(self, index):
        try:
            # Guardar estado actual de los checkboxes y sliders de números
            saved_states = {}
            if hasattr(self, 'numbers_axes_controls'):
                for i, axis_data in self.numbers_axes_controls.items():
                    checkbox = axis_data['checkbox']
                    saved_states[i] = {
                        'checkbox_state': checkbox.get(),
                        'slider_value': axis_data['slider'].get() if hasattr(axis_data['slider'], 'get') else None
                    }
        
            master = self.font.masters[index]

            metrics = {
                'masterID': master.id,
                'masterIndex': index,
                'asc': float(master.ascender),
                'desc': float(master.descender),
                'xh': float(master.xHeight),
            }

            self.numbersPreview.setMetrics(metrics)

            baseline_y = 0
            self.w.tabs[1].xbeamSlider.set(baseline_y)
            self.w.tabs[1].xbeamValue.set(str(int(baseline_y)))
            self.numbersPreview.setXbeamPosition(baseline_y)
    
            ybeam_default = 300
            self.w.tabs[1].ybeamSlider.set(ybeam_default)
            self.w.tabs[1].ybeamValue.set(str(int(ybeam_default)))
            self.numbersPreview.setYbeamPosition(ybeam_default)
    
            # Mantener los valores de altura y anchura
            height_default = float(self.w.tabs[1].numHeightValue.get() or 55)
            width_default = float(self.w.tabs[1].numWidthValue.get() or 100)
        
            self.numbersPreview.setDynamicScale(height_default / 100.0)
            self.numbersPreview.setWidthScale(width_default / 100.0)
        
            # Actualizar controles de ejes si existen
            if hasattr(self, 'numbers_axes_controls'):
                for i, axis_data in self.numbers_axes_controls.items():
                    axis = axis_data['info']
                    slider = axis_data['slider']
                    axis_field = axis_data['field']
                    checkbox = axis_data['checkbox']
                
                    master_axis_value = master.axes[i]
                
                    extended_min = axis['extendedMin']
                    extended_max = axis['extendedMax']
                
                    # Restaurar estado guardado del checkbox si existe
                    if i in saved_states:
                        checkbox.set(saved_states[i]['checkbox_state'])
                
                    # Si el slider no está oculto, usar valor guardado o valor del master
                    if not checkbox.get() and i in saved_states and saved_states[i]['slider_value'] is not None:
                        clamped_value = max(extended_min, min(saved_states[i]['slider_value'], extended_max))
                    else:
                        clamped_value = max(extended_min, min(master_axis_value, extended_max))
                
                    slider.set(clamped_value)
                
                    is_extrapolated_start = clamped_value < axis['minValue']
                    is_extrapolated_end = clamped_value > axis['maxValue']
                
                    if is_extrapolated_start:
                        axis_field.set(f"{int(clamped_value)}*◄")
                    elif is_extrapolated_end:
                        axis_field.set(f"{int(clamped_value)}*►")
                    else:
                        axis_field.set(f"{int(clamped_value)}")
            
                self.updateNumbersAxes()

            self.updateNumbersPreview()

        except Exception as e:
            print(f"Error in setNumbersMaster: {e}")
            import traceback
            traceback.print_exc()
        
    def setMaster(self, index):
        try:
            # Guardar estado actual de los checkboxes y sliders
            saved_states = {}
            for i, axis_data in self.axes_controls.items():
                checkbox = axis_data['checkbox']
                saved_states[i] = {
                    'checkbox_state': checkbox.get(),
                    'slider_value': axis_data['slider'].get() if hasattr(axis_data['slider'], 'get') else None
                }
        
            master = self.font.masters[index]
        
            metrics = {
                'masterID': master.id,
                'masterIndex': index,
                'asc': float(master.ascender),
                'desc': float(master.descender),
                'xh': float(master.xHeight),
            }
        
            self.combinedPreview.setMetrics(metrics)
        
            baseline_y = 0
            self.w.tabs[0].xbeamSlider.set(baseline_y)
            self.w.tabs[0].xbeamValue.set(str(int(baseline_y)))
            self.combinedPreview.setXbeamPosition(baseline_y)
        
            ybeam_default = 300
            self.w.tabs[0].ybeamSlider.set(ybeam_default)
            self.w.tabs[0].ybeamValue.set(str(int(ybeam_default)))
            self.combinedPreview.setYbeamPosition(ybeam_default)
        
            static_char = self.w.tabs[0].staticChar.get().strip() or "H"
            static_layer = self.combinedPreview.view._getStaticLayer(static_char)
        
            if static_layer:
                xh_scale, xh_percentage = self.combinedPreview.view.calculateXHeightScale(static_layer, master)
                self.w.tabs[0].dynamicScaleSlider.set(xh_percentage)
                self.w.tabs[0].dynamicScaleValue.set(f"{int(xh_percentage)}%")
                self.combinedPreview.setDynamicScale(xh_scale)
            else:
                default_percentage = 70
                self.w.tabs[0].dynamicScaleSlider.set(default_percentage)
                self.w.tabs[0].dynamicScaleValue.set(f"{default_percentage}%")
                self.combinedPreview.setDynamicScale(default_percentage / 100.0)
        
            width_default = 100
            self.w.tabs[0].widthScaleSlider.set(width_default)
            self.w.tabs[0].widthScaleValue.set(f"{width_default}%")
            self.applyWidthScale()
        
            for i, axis_data in self.axes_controls.items():
                axis = axis_data['info']
                slider = axis_data['slider']
                axis_field = axis_data['field']
                checkbox = axis_data['checkbox']
            
                master_axis_value = master.axes[i]
            
                extended_min = axis['extendedMin']
                extended_max = axis['extendedMax']
            
                # Restaurar estado guardado del checkbox si existe
                if i in saved_states:
                    checkbox.set(saved_states[i]['checkbox_state'])
            
                # Si el slider no está oculto, usar valor guardado o valor del master
                if not checkbox.get() and i in saved_states and saved_states[i]['slider_value'] is not None:
                    clamped_value = max(extended_min, min(saved_states[i]['slider_value'], extended_max))
                else:
                    clamped_value = max(extended_min, min(master_axis_value, extended_max))
            
                slider.set(clamped_value)
            
                is_extrapolated_start = clamped_value < axis['minValue']
                is_extrapolated_end = clamped_value > axis['maxValue']
            
                if is_extrapolated_start:
                    axis_field.set(f"{int(clamped_value)}*◄")
                elif is_extrapolated_end:
                    axis_field.set(f"{int(clamped_value)}*►")
                else:
                    axis_field.set(f"{int(clamped_value)}")
        
            self.updateAxes()
        
        except Exception as e:
            print(f"Error in setMaster: {e}")
            import traceback
            traceback.print_exc()
        
        
        
    def xbeamChanged(self, sender=None):
        val = self.w.tabs[0].xbeamSlider.get()
        self.w.tabs[0].xbeamValue.set(str(int(val)))
        self.combinedPreview.setXbeamPosition(val)
    
    def ybeamChanged(self, sender=None):
        val = self.w.tabs[0].ybeamSlider.get()
        self.w.tabs[0].ybeamValue.set(str(int(val)))
        self.combinedPreview.setYbeamPosition(val)
    
    def xbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[0].xbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                master = self.font.masters[self.w.tabs[0].masterPopup.get()]
                desc = int(master.descender)
                asc = int(master.ascender)
                value = max(desc, min(value, asc))
                self.w.tabs[0].xbeamSlider.set(value)
                self.w.tabs[0].xbeamValue.set(str(int(value)))
                self.combinedPreview.setXbeamPosition(value)
        except ValueError:
            current_val = self.w.tabs[0].xbeamSlider.get()
            self.w.tabs[0].xbeamValue.set(str(int(current_val)))
    
    def ybeamValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[0].ybeamValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 1000))
                self.w.tabs[0].ybeamSlider.set(value)
                self.w.tabs[0].ybeamValue.set(str(int(value)))
                self.combinedPreview.setYbeamPosition(value)
        except ValueError:
            current_val = self.w.tabs[0].ybeamSlider.get()
            self.w.tabs[0].ybeamValue.set(str(int(current_val)))
    
    def xbeamHideChanged(self, sender=None):
        hide = self.w.tabs[0].xbeamHide.get()
        self.combinedPreview.setShowXbeam(not hide)
    
    def ybeamHideChanged(self, sender=None):
        hide = self.w.tabs[0].ybeamHide.get()
        self.combinedPreview.setShowYbeam(not hide)
    
    def dynamicScaleChanged(self, sender=None):
        val = self.w.tabs[0].dynamicScaleSlider.get()
        self.w.tabs[0].dynamicScaleValue.set(f"{int(val)}%")
        scale_factor = val / 100.0
        self.combinedPreview.setDynamicScale(scale_factor)
    
    def dynamicScaleValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[0].dynamicScaleValue.get().strip()
            if value_str:
                if value_str.endswith('%'):
                    value_str = value_str[:-1]
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[0].dynamicScaleSlider.set(value)
                self.w.tabs[0].dynamicScaleValue.set(f"{int(value)}%")
                scale_factor = value / 100.0
                self.combinedPreview.setDynamicScale(scale_factor)
        except ValueError:
            current_val = self.w.tabs[0].dynamicScaleSlider.get()
            self.w.tabs[0].dynamicScaleValue.set(f"{int(current_val)}%")
    
    def widthScaleChanged(self, sender=None):
        val = self.w.tabs[0].widthScaleSlider.get()
        self.w.tabs[0].widthScaleValue.set(f"{int(val)}%")
        self.applyWidthScale()
    
    def widthScaleValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[0].widthScaleValue.get().strip()
            if value_str:
                if value_str.endswith('%'):
                    value_str = value_str[:-1]
                value = float(value_str)
                value = max(50, min(value, 200))
                self.w.tabs[0].widthScaleSlider.set(value)
                self.w.tabs[0].widthScaleValue.set(f"{int(value)}%")
                self.applyWidthScale()
        except ValueError:
            current_val = self.w.tabs[0].widthScaleSlider.get()
            self.w.tabs[0].widthScaleValue.set(f"{int(current_val)}%")
    
    def applyWidthScale(self):
        try:
            width_percentage = self.w.tabs[0].widthScaleSlider.get()
            width_factor = width_percentage / 100.0
            self.combinedPreview.setWidthScale(width_factor)
        except Exception:
            pass
    
    def axisChanged(self, sender=None):
        self.updateAxes()
    
    def axisValueChanged(self, sender=None):
        from time import sleep
        sleep(0.05)
        try:
            for i, axis_data in self.axes_controls.items():
                axis_field = axis_data['field']
                if sender == axis_field:
                    value_str = axis_field.get().strip()
                    if value_str:
                        try:
                            value = float(value_str)
                            axis = axis_data['info']
                            slider = axis_data['slider']
                            value = max(axis['extendedMin'], min(value, axis['extendedMax']))
                            slider.set(value)
                            self.updateAxes()
                        except ValueError:
                            current_val = slider.get()
                            axis_field.set(str(int(current_val)))
                    else:
                        current_val = slider.get()
                        axis_field.set(str(int(current_val)))
                    break
        except Exception:
            pass
    
    def axisHideChanged(self, sender=None):
        try:
            for i, axis_data in self.axes_controls.items():
                checkbox = axis_data['checkbox']
                if sender == checkbox:
                    self.updateAxes()
                    break
        except Exception:
            pass
    
    def updateAxes(self):
        axisValues = {}
        for i, axis_data in self.axes_controls.items():
            axis = axis_data['info']
            axis_field = axis_data['field']
            slider = axis_data['slider']
            checkbox = axis_data['checkbox']
            
            value = slider.get()
            axis_name = axis['name']
            is_hidden = checkbox.get()
            
            original_min = axis['minValue']
            original_max = axis['maxValue']
            is_extrapolated_start = value < original_min
            is_extrapolated_end = value > original_max
            is_extrapolated = is_extrapolated_start or is_extrapolated_end
            
            if not is_hidden:
                axisValues[axis_name.lower()] = value
                
                axis_lower = axis_name.lower()
                if 'weight' in axis_lower or 'wght' in axis_lower:
                    axisValues['weight'] = value
                    axisValues['wght'] = value
                elif 'width' in axis_lower or 'wdth' in axis_lower:
                    axisValues['width'] = value
                    axisValues['wdth'] = value
                elif 'optical' in axis_lower or 'opsz' in axis_lower:
                    axisValues['optical'] = value
                    axisValues['opsz'] = value
                elif 'italic' in axis_lower or 'ital' in axis_lower:
                    axisValues['italic'] = value
                    axisValues['ital'] = value
                elif 'slant' in axis_lower or 'slnt' in axis_lower:
                    axisValues['slant'] = value
                    axisValues['slnt'] = value
            
            if is_extrapolated:
                if is_extrapolated_start:
                    display_value = f"{int(value)}*◄"
                else:
                    display_value = f"{int(value)}*►"
            else:
                display_value = f"{int(value)}"
            
            axis_field.set(display_value)
            slider.enable(not is_hidden)
            axis_field.enable(not is_hidden)
    
        self.combinedPreview.setAxisValues(axisValues)
        self.updatePreview()
    
    def generateSmallCaps(self, sender=None):
        try:
            script_type_index = self.w.tabs[0].scriptType.get()
        
            pref_tab = self.w.tabs[2]
        
            selected_punctuation = [item["glyph"] for item in pref_tab.punctuationList.get() if item["use"]]
            selected_symbols = [item["glyph"] for item in pref_tab.symbolList.get() if item["use"]]
            selected_others = [item["glyph"] for item in pref_tab.othersList.get()]
        
            print(f"=== Generando Small Caps con selecciones de preferencias ===")
            print(f"Puntuación seleccionada: {selected_punctuation}")
            print(f"Símbolos seleccionados: {selected_symbols}")
            print(f"Otros seleccionados: {selected_others}")
        
            char_sets = []
            if self.w.tabs[0].includeLetters.get():
                char_sets.append('letters')
            if self.w.tabs[0].includeNumerals.get():
                char_sets.append('numerals')
        
            metrics_option_idx = self.w.tabs[0].metricsOption.get()
            metrics_options = ["Scale Sidebearings", "Equal Base Glyphs"]
            metrics_option = metrics_options[metrics_option_idx]
        
            try:
                scale_percentage = self.w.tabs[0].dynamicScaleSlider.get()
                if scale_percentage is None:
                    scale_percentage = 70
                scale_factor = float(scale_percentage) / 100.0
            
                if scale_factor <= 0 or scale_factor > 1.5:
                    scale_factor = 0.7
                
            except Exception as e:
                print(f"Error al obtener scale_factor, usando valor por defecto: {e}")
                scale_factor = 0.7
        
            print(f"Scale factor usado: {scale_factor}")
        
            master_idx = self.w.tabs[0].masterPopup.get()
            if master_idx < 0 or master_idx is None:
                master_idx = 0
        
            master = self.font.masters[master_idx]
            master_id = master.id
        
            axis_values = {}
            for i, axis_data in self.axes_controls.items():
                axis = axis_data['info']
                slider = axis_data['slider']
                checkbox = axis_data['checkbox']
            
                if not checkbox.get():
                    value = slider.get()
                    if value is not None:
                        axis_values[axis['name'].lower()] = value
        
            generated = self.generate_smallcaps_with_selection(
                font=self.font,
                script_type_index=script_type_index,
                char_sets=char_sets,
                master_id=master_id,
                axis_values=axis_values,
                scale_factor=scale_factor,
                metrics_option=metrics_option,
                selected_punctuation=selected_punctuation,
                selected_symbols=selected_symbols,
                selected_others=selected_others
            )
        
            if generated and generated > 0:
                print(f"✅ Generados {generated} glyphs correctamente")
                try:
                    self.font.disableUpdateInterface()
                    self.font.enableUpdateInterface()
                    if hasattr(self.font, 'currentTab') and self.font.currentTab:
                        self.font.currentTab.graphicView().redraw()
                except Exception as e:
                    print(f"Error al actualizar interfaz: {e}")
            else:
                print("❌ No se generaron glyphs")
        
        except Exception as e:
            print(f"Error in generateSmallCaps: {e}")
            import traceback
            traceback.print_exc()

    def generate_smallcaps_with_selection(self, font, script_type_index, char_sets, master_id, 
                                         axis_values, scale_factor, metrics_option,
                                         selected_punctuation, selected_symbols, selected_others):
        try:
            script_types = ["latin", "cyrillic", "greek"]
            script_type = script_types[script_type_index]

            selected_master = None
            for master in font.masters:
                if master.id == master_id:
                    selected_master = master
                    break
        
            if not selected_master:
                print("No se encontró el master seleccionado")
                return 0

            x_height = float(selected_master.xHeight)
    
            all_glyphs = []
            glyphs_dict = get_uppercase_glyphs()

            if 'letters' in char_sets:
                if script_type == "latin":
                    base_glyphs = glyphs_dict['latin']['basic']
                elif script_type == "cyrillic":
                    base_glyphs = glyphs_dict['cyrillic']['option1']
                elif script_type == "greek":
                    base_glyphs = glyphs_dict['greek']['option1']
                else:
                    base_glyphs = []
            
                for glyph_name in base_glyphs:
                    if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                        all_glyphs.append(glyph_name)
                print(f"Añadidas {len([g for g in base_glyphs if g in font.glyphs])} letras del script {script_type}")
        
            for glyph_name in selected_symbols:
                if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                    all_glyphs.append(glyph_name)
            print(f"Añadidos {len([g for g in selected_symbols if g in font.glyphs])} símbolos de preferencias")
        
            for glyph_name in selected_punctuation:
                if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                    all_glyphs.append(glyph_name)
            print(f"Añadidos {len([g for g in selected_punctuation if g in font.glyphs])} puntuación de preferencias")
        
            for glyph_name in selected_others:
                if glyph_name in font.glyphs and glyph_name not in all_glyphs:
                    all_glyphs.append(glyph_name)
            print(f"Añadidos {len([g for g in selected_others if g in font.glyphs])} otros de preferencias")
        
            if 'numerals' in char_sets and 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals']:
                numeral_glyphs = [n for n in glyphs_dict['numerals']['digits'] if n in font.glyphs]
                for glyph_name in numeral_glyphs:
                    if glyph_name not in all_glyphs:
                        all_glyphs.append(glyph_name)
                print(f"Añadidos {len(numeral_glyphs)} numerals")
        
            if not all_glyphs:
                print("No hay glyphs para procesar")
                return 0
            
            print(f"TOTAL de glyphs a procesar: {len(all_glyphs)}")
        
            centered_base_glyphs = []
            if 'centered' in glyphs_dict:
                for glyph_sc_name in glyphs_dict['centered']:
                    if glyph_sc_name.endswith('.sc'):
                        base_name = glyph_sc_name[:-3]
                        centered_base_glyphs.append(base_name)
        
            existing_glyphs = [g for g in all_glyphs if g in font.glyphs]
        
            if not existing_glyphs:
                print("No hay glyphs existentes en la fuente")
                return 0

            smart_axis_values = {}
            if axis_values and hasattr(font, 'axes'):
                for i, axis in enumerate(font.axes):
                    axis_name = axis.name
                    if axis_name.lower() in axis_values:
                        smart_axis_values[axis_name] = axis_values[axis_name.lower()]
                    elif hasattr(axis, 'axisTag') and axis.axisTag.lower() in axis_values:
                        smart_axis_values[axis_name] = axis_values[axis.axisTag.lower()]
                    else:
                        smart_axis_values[axis_name] = float(selected_master.axes[i])

            print(f"Valores de ejes para smart components: {smart_axis_values}")

            reference_h_sc_height = None
            reference_h_sc_center_y = None
        
            if 'h' in font.glyphs and 'h' in existing_glyphs:
                h_index = existing_glyphs.index('h')
                if h_index > 0:
                    existing_glyphs.insert(0, existing_glyphs.pop(h_index))

            generated_count = 0
            updated_count = 0
            created_glyphs = []
            updated_glyphs = []
            font.disableUpdateInterface()

            try:
                for glyph_name in existing_glyphs:
                    is_centered_glyph = glyph_name in centered_base_glyphs
                    sc_name = f"{glyph_name.lower()}.sc"
                
                    glyph_category = "letter"
                    if is_centered_glyph:
                        glyph_category = "centered"
                    elif glyph_name in selected_symbols:
                        glyph_category = "symbol"
                    elif glyph_name in selected_punctuation:
                        glyph_category = "punctuation"
                    elif glyph_name in selected_others:
                        glyph_category = "other"
                    elif 'numerals' in glyphs_dict and 'digits' in glyphs_dict['numerals'] and glyph_name in glyphs_dict['numerals']['digits']:
                        glyph_category = "numeral"
                
                    if glyph_name not in font.glyphs:
                        continue
                
                    base_glyph = font.glyphs[glyph_name]
                
                    if not base_glyph.smartComponentAxes or len(base_glyph.smartComponentAxes) == 0:
                        print(f"Creando ejes smart para {base_glyph.name}...")
                    
                        for i, fontAxis in enumerate(font.axes):
                            axisValues = [m.axes[i] for m in font.masters]
                        
                            newAxis = GSSmartComponentAxis()
                            newAxis.name = fontAxis.name
                            newAxis.bottomValue = min(axisValues)
                            newAxis.topValue = max(axisValues)
                        
                            base_glyph.smartComponentAxes.append(newAxis)
                        
                            for layer in base_glyph.layers:
                                if not layer.isMasterLayer:
                                    continue
                            
                                master = layer.associatedFontMaster()
                                masterValue = master.axes[i]
                            
                                if masterValue == newAxis.bottomValue:
                                    layer.smartComponentPoleMapping[newAxis.id] = 1
                                elif masterValue == newAxis.topValue:
                                    layer.smartComponentPoleMapping[newAxis.id] = 2
                
                    scglyph_exists = sc_name in font.glyphs
                    scglyph = None
                
                    if scglyph_exists:
                        scglyph = font.glyphs[sc_name]
                        if master_id in scglyph.layers:
                            del scglyph.layers[master_id]
                            updated_count += 1
                            updated_glyphs.append(sc_name)
                        else:
                            generated_count += 1
                            created_glyphs.append(sc_name)
                    else:
                        scglyph = GSGlyph(sc_name)
                    
                        if glyph_category == "numeral":
                            scglyph.category = "Number"
                        elif glyph_category in ["punctuation", "symbol", "other"]:
                            scglyph.category = "Symbol"
                        else:
                            scglyph.category = "Letter"
                    
                        scglyph.subCategory = "Smallcaps"
                    
                        if metrics_option == "Equal Base Glyphs":
                            scglyph.leftMetricsKey = f"={base_glyph.name}"
                            scglyph.rightMetricsKey = f"={base_glyph.name}"
                            scglyph.widthMetricsKey = f"={base_glyph.name}"
                    
                        font.glyphs.append(scglyph)
                        generated_count += 1
                        created_glyphs.append(sc_name)
                
                    base_layer = None
                    for layer in base_glyph.layers:
                        if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master_id) or \
                           (hasattr(layer, 'masterId') and layer.masterId == master_id):
                            base_layer = layer
                            break
                
                    if not base_layer and base_glyph.layers:
                        base_layer = base_glyph.layers[0]
                
                    translate_y = 0.0
                
                    if base_layer and base_layer.bounds:
                        bounds = base_layer.bounds
                        base_height = bounds.size.height
                        base_min_y = bounds.origin.y
                        base_center_y = base_min_y + (base_height / 2.0)
                    
                        if is_centered_glyph:
                            if glyph_name == 'h' and sc_name == 'h.sc':
                                translate_y = 0.0
                            else:
                                if reference_h_sc_center_y is not None and reference_h_sc_height is not None:
                                    scaled_center_y = base_center_y * scale_factor
                                    translate_y = reference_h_sc_center_y - scaled_center_y
                                else:
                                    scaled_x_height = x_height * scale_factor
                                    theoretical_h_sc_center = scaled_x_height / 2.0
                                    scaled_center_y = base_center_y * scale_factor
                                    translate_y = theoretical_h_sc_center - scaled_center_y
                        else:
                            scaled_min_y = base_min_y * scale_factor
                            translate_y = -scaled_min_y
                
                    sclayer = GSLayer()
                    component = GSComponent(glyph_name)
                    sclayer.components.append(component)
                
                    transform = NSAffineTransformStruct(
                        m11=scale_factor,
                        m12=0.0,
                        m21=0.0,
                        m22=scale_factor,
                        tX=0.0,
                        tY=translate_y
                    )
                    component.transform = transform
                
                    if hasattr(component, 'automaticAlignment'):
                        try:
                            component.automaticAlignment = True
                        except Exception:
                            pass
                
                    scglyph.layers[master_id] = sclayer
                
                    for layer in scglyph.layers:
                        if not layer.isMasterLayer:
                            continue
                    
                        master = layer.associatedFontMaster()
                    
                        for comp in layer.components:
                            if comp.name != base_glyph.name:
                                continue
                        
                            for i, smartAxis in enumerate(base_glyph.smartComponentAxes):
                                if i < len(master.axes):
                                    interpolationValue = master.axes[i]
                                    try:
                                        comp.smartComponentValues[smartAxis.id] = interpolationValue
                                    except Exception as e:
                                        print(f"Error asignando valor al eje {smartAxis.id}: {e}")
                        
                            if master.id == master_id:
                                for axis_name, axis_value in smart_axis_values.items():
                                    try:
                                        for smartAxis in base_glyph.smartComponentAxes:
                                            if smartAxis.name == axis_name:
                                                comp.smartComponentValues[smartAxis.id] = axis_value
                                                break
                                    except Exception:
                                        pass
                        
                            try:
                                if hasattr(comp, 'updateSmartComponentValues'):
                                    comp.updateSmartComponentValues()
                            except Exception:
                                pass
                
                    if sc_name == 'h.sc':
                        if sclayer and hasattr(sclayer, 'bounds') and sclayer.bounds:
                            bounds = sclayer.bounds
                            reference_h_sc_height = bounds.size.height
                            reference_h_sc_center_y = bounds.origin.y + (bounds.size.height / 2.0)

            except Exception as e:
                print(f"Error durante la generación: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                font.enableUpdateInterface()
            
                if 'reference_h_sc_center_y' in locals() and reference_h_sc_center_y is not None:
                    for sc_name in created_glyphs + updated_glyphs:
                        base_name = sc_name[:-3]
                        if base_name in centered_base_glyphs and sc_name != 'h.sc':
                            if sc_name in font.glyphs and base_name in font.glyphs:
                                scglyph = font.glyphs[sc_name]
                                base_glyph = font.glyphs[base_name]
                            
                                if scglyph and base_glyph and master_id in scglyph.layers:
                                    sclayer = scglyph.layers[master_id]
                                    if sclayer.components and len(sclayer.components) > 0:
                                        component = sclayer.components[0]
                                    
                                        base_layer = None
                                        for layer in base_glyph.layers:
                                            if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master_id) or \
                                               (hasattr(layer, 'masterId') and layer.masterId == master_id):
                                                base_layer = layer
                                                break
                                    
                                        if base_layer and base_layer.bounds:
                                            bounds = base_layer.bounds
                                            base_min_y = bounds.origin.y
                                            base_height = bounds.size.height
                                            base_center_y = base_min_y + (base_height / 2.0)
                                        
                                            scaled_center_y = base_center_y * scale_factor
                                            new_translate_y = reference_h_sc_center_y - scaled_center_y
                                        
                                            transform = NSAffineTransformStruct(
                                                m11=scale_factor,
                                                m12=0.0,
                                                m21=0.0,
                                                m22=scale_factor,
                                                tX=0.0,
                                                tY=new_translate_y
                                            )
                                            component.transform = transform
                                        
                                            try:
                                                sclayer.updateMetrics()
                                            except:
                                                pass
            
                try:
                    NSNotificationCenter.defaultCenter().postNotificationName_object_(
                        "GSUpdateInterface", font)
                except:
                    pass
            
                try:
                    if hasattr(font, 'currentTab') and font.currentTab:
                        if hasattr(font.currentTab, 'graphicView'):
                            font.currentTab.graphicView().redraw()
                except:
                    pass
        
            total = generated_count + updated_count
            print(f"✅ Generados: {generated_count}, Actualizados: {updated_count}, Total: {total}")
            print(f"✅ Todos los glyphs son SMART COMPONENTS con valores de ejes: {smart_axis_values}")
            return total
        
        except Exception as e:
            print(f"Error in generate_smallcaps_with_selection: {e}")
            import traceback
            traceback.print_exc()
            return 0
            
    def togglePunctuation(self, sender):
        try:
            lst = self.w.tabs[2].punctuationList.get()
            all_selected = all(item["use"] for item in lst)
        
            for item in lst:
                item["use"] = not all_selected
        
            self.w.tabs[2].punctuationList.set(lst)
            sender.setTitle("Select All" if all_selected else "Deselect All")
        
        except Exception as e:
            print("togglePunctuation error:", e)

    def toggleSymbols(self, sender):
        try:
            lst = self.w.tabs[2].symbolList.get()
            all_selected = all(item["use"] for item in lst)
        
            for item in lst:
                item["use"] = not all_selected
        
            self.w.tabs[2].symbolList.set(lst)
            sender.setTitle("Select All" if all_selected else "Deselect All")
        
        except Exception as e:
            print("toggleSymbols error:", e)

    def addGlyph(self, sender):
        try:
            value = AskString("Glyph name")
            if not value:
                return
        
            value = value.strip()
            lst = self.w.tabs[2].othersList.get()
            existing = [i["glyph"] for i in lst]
        
            if value in existing:
                return
        
            lst.append({"glyph": value, "use": True})
            self.w.tabs[2].othersList.set(lst)
        
        except Exception as e:
            print("addGlyph error:", e)

    def deleteGlyph(self, sender):
        try:
            lst = self.w.tabs[2].othersList.get()
            new_list = [item for item in lst if not item["use"]]
            self.w.tabs[2].othersList.set(new_list)
        
        except Exception as e:
            print("deleteGlyph error:", e)

    def saveConfig(self, sender):
        try:
            punct = [i["glyph"] for i in self.w.tabs[2].punctuationList.get() if i["use"]]
            symbols = [i["glyph"] for i in self.w.tabs[2].symbolList.get() if i["use"]]
            others = [i["glyph"] for i in self.w.tabs[2].othersList.get()]
        
            data = {
                "punctuation": punct,
                "symbols": symbols,
                "others": others
            }
        
            saveGlyphConfig(data)
        
        except Exception as e:
            print("saveConfig error:", e)

    def loadConfig(self, sender):
        try:
            data = loadGlyphConfig()
            if not data:
                return
        
            punct_list = self.w.tabs[2].punctuationList.get()
            for item in punct_list:
                item["use"] = item["glyph"] in data.get("punctuation", [])
            self.w.tabs[2].punctuationList.set(punct_list)
        
            symbol_list = self.w.tabs[2].symbolList.get()
            for item in symbol_list:
                item["use"] = item["glyph"] in data.get("symbols", [])
            self.w.tabs[2].symbolList.set(symbol_list)
        
            others = [{"glyph": g, "use": True} for g in data.get("others", [])]
            self.w.tabs[2].othersList.set(others)
        
        except Exception as e:
            print("loadConfig error:", e)
            	
    def numbersAxisChanged(self, sender=None):
        self.updateNumbersAxes()

    def numbersAxisValueChanged(self, sender=None):
        from time import sleep
        sleep(0.05)
        try:
            for i, axis_data in self.numbers_axes_controls.items():
                axis_field = axis_data['field']
                if sender == axis_field:
                    value_str = axis_field.get().strip()
                    if value_str:
                        try:
                            value = float(value_str)
                            axis = axis_data['info']
                            slider = axis_data['slider']
                            value = max(axis['extendedMin'], min(value, axis['extendedMax']))
                            slider.set(value)
                            self.updateNumbersAxes()
                        except ValueError:
                            current_val = slider.get()
                            axis_field.set(str(int(current_val)))
                    else:
                        current_val = slider.get()
                        axis_field.set(str(int(current_val)))
                    break
        except Exception:
            pass

    def numbersAxisHideChanged(self, sender=None):
        try:
            for i, axis_data in self.numbers_axes_controls.items():
                checkbox = axis_data['checkbox']
                if sender == checkbox:
                    self.updateNumbersAxes()
                    break
        except Exception:
            pass

    def numbersAxisDecrement(self, axis_idx):
        try:
            axis_data = self.numbers_axes_controls[axis_idx]
            slider = axis_data['slider']
            current_val = float(slider.get())
            new_val = current_val - 1
            slider.set(new_val)
            self.updateNumbersAxes()
        except:
            pass

    def numbersAxisIncrement(self, axis_idx):
        try:
            axis_data = self.numbers_axes_controls[axis_idx]
            slider = axis_data['slider']
            current_val = float(slider.get())
            new_val = current_val + 1
            slider.set(new_val)
            self.updateNumbersAxes()
        except:
            pass

    def updateNumbersAxes(self):
        axisValues = {}
        for i, axis_data in self.numbers_axes_controls.items():
            axis = axis_data['info']
            axis_field = axis_data['field']
            slider = axis_data['slider']
            checkbox = axis_data['checkbox']
        
            value = slider.get()
            axis_name = axis['name']
            is_hidden = checkbox.get()
        
            original_min = axis['minValue']
            original_max = axis['maxValue']
            is_extrapolated_start = value < original_min
            is_extrapolated_end = value > original_max
            is_extrapolated = is_extrapolated_start or is_extrapolated_end
        
            if not is_hidden:
                axisValues[axis_name.lower()] = value
            
                axis_lower = axis_name.lower()
                if 'weight' in axis_lower or 'wght' in axis_lower:
                    axisValues['weight'] = value
                    axisValues['wght'] = value
                elif 'width' in axis_lower or 'wdth' in axis_lower:
                    axisValues['width'] = value
                    axisValues['wdth'] = value
                elif 'optical' in axis_lower or 'opsz' in axis_lower:
                    axisValues['optical'] = value
                    axisValues['opsz'] = value
                elif 'italic' in axis_lower or 'ital' in axis_lower:
                    axisValues['italic'] = value
                    axisValues['ital'] = value
                elif 'slant' in axis_lower or 'slnt' in axis_lower:
                    axisValues['slant'] = value
                    axisValues['slnt'] = value
        
            if is_extrapolated:
                if is_extrapolated_start:
                    display_value = f"{int(value)}*◄"
                else:
                    display_value = f"{int(value)}*►"
            else:
                display_value = f"{int(value)}"
        
            axis_field.set(display_value)
            slider.enable(not is_hidden)
            axis_field.enable(not is_hidden)
    
        if hasattr(self, 'numbersPreview'):
            self.numbersPreview.setAxisValues(axisValues)
            self.updateNumbersPreview()
    
    def numbersXbeamChanged(self, sender=None):
        val = self.w.tabs[1].xbeamSlider.get()
        self.w.tabs[1].xbeamValue.set(str(int(val)))
        if hasattr(self, 'numbersPreview'):
            self.numbersPreview.setXbeamPosition(val)
    
    def numbersYbeamChanged(self, sender=None):
        val = self.w.tabs[1].ybeamSlider.get()
        self.w.tabs[1].ybeamValue.set(str(int(val)))
        if hasattr(self, 'numbersPreview'):
            self.numbersPreview.setYbeamPosition(val)
    
    def numbersXbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].xbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                master = self.font.masters[self.w.tabs[1].masterPopup.get()]
                desc = int(master.descender)
                asc = int(master.ascender)
                value = max(desc, min(value, asc))
                self.w.tabs[1].xbeamSlider.set(value)
                self.w.tabs[1].xbeamValue.set(str(int(value)))
                if hasattr(self, 'numbersPreview'):
                    self.numbersPreview.setXbeamPosition(value)
        except ValueError:
            current_val = self.w.tabs[1].xbeamSlider.get()
            self.w.tabs[1].xbeamValue.set(str(int(current_val)))
    
    def numbersYbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].ybeamValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 1000))
                self.w.tabs[1].ybeamSlider.set(value)
                self.w.tabs[1].ybeamValue.set(str(int(value)))
                if hasattr(self, 'numbersPreview'):
                    self.numbersPreview.setYbeamPosition(value)
        except ValueError:
            current_val = self.w.tabs[1].ybeamSlider.get()
            self.w.tabs[1].ybeamValue.set(str(int(current_val)))
    
    def numbersXbeamHideChanged(self, sender=None):
        hide = self.w.tabs[1].xbeamHide.get()
        if hasattr(self, 'numbersPreview'):
            self.numbersPreview.setShowXbeam(not hide)
    
    def numbersYbeamHideChanged(self, sender=None):
        hide = self.w.tabs[1].ybeamHide.get()
        if hasattr(self, 'numbersPreview'):
            self.numbersPreview.setShowYbeam(not hide)
    
    def numbersXbeamDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].xbeamValue.get())
            new_val = current_val - 1
            self.w.tabs[1].xbeamSlider.set(new_val)
            self.numbersXbeamChanged()
        except:
            pass
    
    def numbersXbeamIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].xbeamValue.get())
            new_val = current_val + 1
            self.w.tabs[1].xbeamSlider.set(new_val)
            self.numbersXbeamChanged()
        except:
            pass
    
    def numbersYbeamDecrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].ybeamValue.get())
            new_val = current_val - 1
            self.w.tabs[1].ybeamSlider.set(new_val)
            self.numbersYbeamChanged()
        except:
            pass
    
    def numbersYbeamIncrement(self, sender=None):
        try:
            current_val = float(self.w.tabs[1].ybeamValue.get())
            new_val = current_val + 1
            self.w.tabs[1].ybeamSlider.set(new_val)
            self.numbersYbeamChanged()
        except:
            pass
    
    def numbersHeightChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].numHeightValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[1].numHeightValue.set(str(int(value)))
                self.updateNumbersPreview()
        except:
            pass
    
    def numbersWidthChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].numWidthValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(50, min(value, 200))
                self.w.tabs[1].numWidthValue.set(str(int(value)))
                self.updateNumbersPreview()
        except:
            pass
    
    def numrValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].numrValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[1].numrValue.set(str(int(value)))
        except:
            pass
    
    def dnomValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].dnomValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[1].dnomValue.set(str(int(value)))
        except:
            pass
    
    def sinfValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].sinfValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[1].sinfValue.set(str(int(value)))
        except:
            pass
    
    def supsValueChanged(self, sender=None):
        try:
            value_str = self.w.tabs[1].supsValue.get().strip()
            if value_str:
                value = float(value_str)
                value = max(0, min(value, 100))
                self.w.tabs[1].supsValue.set(str(int(value)))
        except:
            pass
    
    def generateNumerals(self, sender=None):
        try:
            master_idx = self.w.tabs[1].masterPopup.get()
            if master_idx < 0:
                master_idx = 0
    
            master = self.font.masters[master_idx]
            master_id = master.id
    
            scale_percentages = {
                'height': float(self.w.tabs[1].numHeightValue.get() or 55),
                'width': float(self.w.tabs[1].numWidthValue.get() or 100),
            }
    
            if hasattr(self.w.tabs[1], 'numrCheck') and self.w.tabs[1].numrCheck.get():
                scale_percentages['numr'] = float(self.w.tabs[1].numrValue.get() or 55)
            if hasattr(self.w.tabs[1], 'dnomCheck') and self.w.tabs[1].dnomCheck.get():
                scale_percentages['dnom'] = float(self.w.tabs[1].dnomValue.get() or 55)
            if hasattr(self.w.tabs[1], 'sinfCheck') and self.w.tabs[1].sinfCheck.get():
                scale_percentages['sinf'] = float(self.w.tabs[1].sinfValue.get() or 55)
            if hasattr(self.w.tabs[1], 'supsCheck') and self.w.tabs[1].supsCheck.get():
                scale_percentages['sups'] = float(self.w.tabs[1].supsValue.get() or 55)
    
            special_forms_selected = any(key in scale_percentages for key in ['numr', 'dnom', 'sinf', 'sups'])
    
            if not special_forms_selected:
                return
    
            pref_tab = self.w.tabs[2]
        
            selected_punctuation = [item["glyph"] for item in pref_tab.punctuationList.get() if item["use"]]
            selected_symbols = [item["glyph"] for item in pref_tab.symbolList.get() if item["use"]]
            selected_others = [item["glyph"] for item in pref_tab.othersList.get()]
        
            print(f"Generando con: {len(selected_punctuation)} puntuación, {len(selected_symbols)} símbolos, {len(selected_others)} otros")
    
            result = generate_numerals_smallcaps(
                font=self.font,
                master_id=master_id,
                axis_values={},
                scale_percentages=scale_percentages,
                selected_punctuation=selected_punctuation,
                selected_symbols=selected_symbols,
                selected_others=selected_others
            )
    
        except Exception as e:
            print(f"Error in generateNumerals: {e}")
            import traceback
            traceback.print_exc()

def main():
    global _panel_instance
    
    if _panel_instance is not None:
        try:
            _panel_instance.w.bringToFront()
            return
        except:
            _panel_instance = None
    
    try:
        _panel_instance = CombinedGlyphPreviewPanel()
        
        def cleanup(sender=None):
            global _panel_instance
            _panel_instance = None
        
        if hasattr(_panel_instance, 'w'):
            _panel_instance.w.bind("close", cleanup)
            
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()