# MenuTitle: Arab text preview
# -*- coding: utf-8 -*-
# Description: Arabic shaping preview and debugging tool for Glyphs 3.5.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at:
# https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import Glyphs
from vanilla import (
    FloatingWindow,
    TextBox,
    EditText,
    Slider,
    PopUpButton,
    CheckBox,
    Button,
    TextEditor,
    ScrollView,
)

from AppKit import (
    NSView,
    NSColor,
    NSBezierPath,
    NSAffineTransform,
    NSMakeSize,
    NSMakePoint,
    NSMakeRect,
    NSTimer,
    NSRunLoop,
    NSDefaultRunLoopMode,
)
from Foundation import NSUserDefaults
import uuid


DEBUG = True


def log(message):
    if DEBUG:
        print("[Shaping Debugger] %s" % message)


PREF_PREFIX = "ShapingDebugger."
PREVIEW_LEFT_MARGIN = 56
PREVIEW_TOP_MARGIN = 190
PREVIEW_RIGHT_SAFETY = 520
PREVIEW_BOTTOM_SAFETY = 180

PRESETS = [
    ("Arabic Basic", ["ccmp", "locl", "rlig", "calt", "mark", "mkmk", "kern"]),
    ("Arabic Full", ["ccmp", "locl", "rlig", "liga", "dlig", "calt", "mark", "mkmk", "kern"]),
    ("No Optional Ligatures", ["ccmp", "locl", "rlig", "calt", "mark", "mkmk", "kern"]),
    ("Latin Standard", ["liga", "calt", "mark", "mkmk", "kern"]),
    ("Custom", []),
]

PRESET_NAMES = [preset[0] for preset in PRESETS]
PRESET_FEATURES = dict(PRESETS)


ARABIC_GLYPH_NAMES = {
    "\u0621": ["hamza-ar", "uni0621"],
    "\u0622": ["alefMadda-ar", "uni0622"],
    "\u0623": ["alefHamzaabove-ar", "uni0623"],
    "\u0624": ["wawHamzaabove-ar", "uni0624"],
    "\u0625": ["alefHamzabelow-ar", "uni0625"],
    "\u0626": ["yehHamzaabove-ar", "uni0626"],
    "\u0627": ["alef-ar", "uni0627"],
    "\u0628": ["beh-ar", "uni0628"],
    "\u0629": ["tehMarbuta-ar", "uni0629"],
    "\u062A": ["teh-ar", "uni062A"],
    "\u062B": ["theh-ar", "uni062B"],
    "\u062C": ["jeem-ar", "uni062C"],
    "\u062D": ["hah-ar", "uni062D"],
    "\u062E": ["khah-ar", "uni062E"],
    "\u062F": ["dal-ar", "uni062F"],
    "\u0630": ["thal-ar", "uni0630"],
    "\u0631": ["reh-ar", "uni0631"],
    "\u0632": ["zain-ar", "uni0632"],
    "\u0633": ["seen-ar", "uni0633"],
    "\u0634": ["sheen-ar", "uni0634"],
    "\u0635": ["sad-ar", "uni0635"],
    "\u0636": ["dad-ar", "uni0636"],
    "\u0637": ["tah-ar", "uni0637"],
    "\u0638": ["zah-ar", "uni0638"],
    "\u0639": ["ain-ar", "uni0639"],
    "\u063A": ["ghain-ar", "uni063A"],
    "\u0640": ["tatweel-ar", "uni0640"],
    "\u0641": ["feh-ar", "uni0641"],
    "\u0642": ["qaf-ar", "uni0642"],
    "\u0643": ["kaf-ar", "uni0643"],
    "\u0644": ["lam-ar", "uni0644"],
    "\u0645": ["meem-ar", "uni0645"],
    "\u0646": ["noon-ar", "uni0646"],
    "\u0647": ["heh-ar", "uni0647"],
    "\u0648": ["waw-ar", "uni0648"],
    "\u0649": ["alefMaksura-ar", "uni0649"],
    "\u064A": ["yeh-ar", "uni064A"],
    "\u067E": ["peh-ar", "uni067E"],
    "\u0686": ["tcheh-ar", "uni0686"],
    "\u0698": ["zheh-ar", "uni0698"],
    "\u06A4": ["veh-ar", "uni06A4"],
    "\u06AF": ["gaf-ar", "uni06AF"],
}

ARABIC_MARK_NAMES = {
    "\u064B": ["fathatan-ar", "uni064B"],
    "\u064C": ["dammatan-ar", "uni064C"],
    "\u064D": ["kasratan-ar", "uni064D"],
    "\u064E": ["fatha-ar", "uni064E"],
    "\u064F": ["damma-ar", "uni064F"],
    "\u0650": ["kasra-ar", "uni0650"],
    "\u0651": ["shadda-ar", "uni0651"],
    "\u0652": ["sukun-ar", "uni0652"],
    "\u0653": ["maddaabove-ar", "uni0653"],
    "\u0654": ["hamzaabove-ar", "uni0654"],
    "\u0655": ["hamzabelow-ar", "uni0655"],
}

ARABIC_MARK_ORDER = {
    "\u0651": 10,  # shadda, closest to the base in common Arabic stacks
    "\u0653": 15,
    "\u0654": 16,
    "\u064E": 20,
    "\u064F": 21,
    "\u0652": 22,
    "\u064B": 23,
    "\u064C": 24,
    "\u0650": 30,
    "\u064D": 31,
    "\u0655": 32,
}

DUAL_JOINING = set([
    "\u0626", "\u0628", "\u062A", "\u062B", "\u062C", "\u062D", "\u062E",
    "\u0633", "\u0634", "\u0635", "\u0636", "\u0637", "\u0638", "\u0639",
    "\u063A", "\u0640", "\u0641", "\u0642", "\u0643", "\u0644", "\u0645",
    "\u0646", "\u0647", "\u064A", "\u067E", "\u0686", "\u06A4", "\u06AF",
])

RIGHT_JOINING = set([
    "\u0622", "\u0623", "\u0624", "\u0625", "\u0627", "\u0629", "\u062F",
    "\u0630", "\u0631", "\u0632", "\u0648", "\u0649", "\u0698",
])

LAM_ALEF_NAMES = {
    "\u0622": ["lam_alefMadda-ar", "lam_alefMaddaabove-ar", "uniFEF5"],
    "\u0623": ["lam_alefHamzaabove-ar", "uniFEF7"],
    "\u0625": ["lam_alefHamzabelow-ar", "uniFEF9"],
    "\u0627": ["lam_alef-ar", "uniFEFB"],
}


_previewClassName = "ShapingDebuggerPreview_" + uuid.uuid4().hex

ShapingDebuggerPreviewView = type(
    _previewClassName,
    (NSView,),
    {
        "isFlipped": lambda self: True,
        "acceptsFirstMouse_": lambda self, event: True,
        "acceptsFirstResponder": lambda self: True,
        "mouseDown_": lambda self, event: (
            self.owner.previewMouseDown_(event)
            if hasattr(self, "owner") and self.owner
            else None
        ),
        "mouseDragged_": lambda self, event: (
            self.owner.previewMouseDragged_(event)
            if hasattr(self, "owner") and self.owner
            else None
        ),
        "mouseUp_": lambda self, event: (
            self.owner.previewMouseUp_(event)
            if hasattr(self, "owner") and self.owner
            else None
        ),
        "drawRect_": lambda self, rect: (
            self.owner.drawPreview(rect)
            if hasattr(self, "owner") and self.owner
            else None
        ),
    },
)


class ShapingDebugger(object):

    def __init__(self):
        self.isAlive = True
        self.isUpdating = False
        self.lastLiveSignature = None
        self.shapedLines = []
        self.hitTargets = []
        self.frozenText = None
        self.dragStartPoint = None
        self.dragStartOrigin = None
        self.lastDragPoint = None
        self.diagnosticsText = ""
        self.loadSettings()

        self.w = FloatingWindow((980, 720), "Shaping Debugger", minSize=(720, 480))

        y = 12
        self.w.presetLabel = TextBox((12, y + 3, 48, 20), "Preset")
        self.w.presetPopup = PopUpButton((62, y, 170, 24), PRESET_NAMES, callback=self.settingsChanged)
        self.w.presetPopup.set(self.presetIndex)

        self.w.sizeLabel = TextBox((246, y + 3, 32, 20), "Size")
        self.w.sizeSlider = Slider(
            (282, y + 2, 150, 20),
            minValue=8,
            maxValue=300,
            value=self.fontSize,
            callback=self.settingsChanged,
        )
        self.w.sizeField = EditText((438, y, 48, 24), str(int(self.fontSize)), callback=self.settingsChanged)

        self.w.widthLabel = TextBox((500, y + 3, 42, 20), "Width")
        self.w.widthField = EditText((546, y, 58, 24), str(int(self.galleyWidth)), callback=self.settingsChanged)

        self.w.applyButton = Button((620, y, 70, 24), "Apply", callback=self.applyCallback)
        self.w.refreshButton = Button((696, y, 78, 24), "Refresh", callback=self.applyCallback)

        y += 34
        self.w.rtlCheck = CheckBox((12, y, 125, 22), "Right-to-left", value=self.rtl, callback=self.settingsChanged)
        self.w.liveCheck = CheckBox((146, y, 110, 22), "Live update", value=self.liveUpdate, callback=self.settingsChanged)
        self.w.namesCheck = CheckBox((270, y, 165, 22), "Show shaped glyph names", value=self.showGlyphNames, callback=self.settingsChanged)
        self.w.blockTabCheck = CheckBox((448, y, 92, 22), "Block tab", value=self.blockTab, callback=self.settingsChanged)
        self.w.preserveCheck = CheckBox((552, y, 180, 22), "Preserve Unicode text", value=True, callback=self.settingsChanged)
        self.w.preserveCheck.enable(False)

        y += 34
        self.w.customLabel = TextBox((12, y + 3, 98, 20), "Custom features")
        self.w.customFeatures = EditText((112, y, 330, 24), self.customFeatures, callback=self.settingsChanged)
        self.w.info = TextEditor((456, y, -12, 72), text="")
        try:
            self.w.info.getNSTextView().setEditable_(False)
        except Exception:
            pass

        self.preview = ShapingDebuggerPreviewView.alloc().init()
        self.preview.owner = self
        self.w.scroll = ScrollView((12, 126, -12, -12), self.preview)
        self.configureScrollView()

        self.w.bind("close", self.windowClosed)
        self.w.open()

        self.applyPreview()

        self.liveTimer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.5, self, "liveTimer:", None, True
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.liveTimer, NSDefaultRunLoopMode)

    # Settings

    def prefKey(self, name):
        return PREF_PREFIX + name

    def loadSettings(self):
        d = NSUserDefaults.standardUserDefaults()
        self.presetIndex = d.integerForKey_(self.prefKey("presetIndex")) or 0
        if self.presetIndex >= len(PRESET_NAMES):
            self.presetIndex = 0
        self.rtl = bool(d.boolForKey_(self.prefKey("rtl")))
        self.liveUpdate = bool(d.boolForKey_(self.prefKey("liveUpdate")))
        self.showGlyphNames = bool(d.boolForKey_(self.prefKey("showGlyphNames")))
        self.blockTab = bool(d.boolForKey_(self.prefKey("blockTab")))
        self.fontSize = d.floatForKey_(self.prefKey("fontSize")) or 96
        self.galleyWidth = d.floatForKey_(self.prefKey("galleyWidth")) or 860
        self.customFeatures = d.stringForKey_(self.prefKey("customFeatures")) or ""

    def saveSettings(self):
        d = NSUserDefaults.standardUserDefaults()
        d.setInteger_forKey_(self.presetIndex, self.prefKey("presetIndex"))
        d.setBool_forKey_(bool(self.rtl), self.prefKey("rtl"))
        d.setBool_forKey_(bool(self.liveUpdate), self.prefKey("liveUpdate"))
        d.setBool_forKey_(bool(self.showGlyphNames), self.prefKey("showGlyphNames"))
        d.setBool_forKey_(bool(self.blockTab), self.prefKey("blockTab"))
        d.setFloat_forKey_(float(self.fontSize), self.prefKey("fontSize"))
        d.setFloat_forKey_(float(self.galleyWidth), self.prefKey("galleyWidth"))
        d.setObject_forKey_(self.customFeatures, self.prefKey("customFeatures"))

    def settingsChanged(self, sender=None):
        try:
            self.presetIndex = self.w.presetPopup.get()
            self.rtl = bool(self.w.rtlCheck.get())
            self.liveUpdate = bool(self.w.liveCheck.get())
            self.showGlyphNames = bool(self.w.namesCheck.get())
            previousBlockTab = self.blockTab
            self.blockTab = bool(self.w.blockTabCheck.get())
            if sender == self.w.sizeSlider:
                self.fontSize = max(8, float(self.w.sizeSlider.get()))
                self.w.sizeField.set(str(int(round(self.fontSize))))
            else:
                self.fontSize = max(8, float(self.w.sizeField.get()))
                self.w.sizeSlider.set(self.fontSize)
            self.galleyWidth = max(160, float(self.w.widthField.get()))
            self.customFeatures = self.w.customFeatures.get()
            if self.blockTab and not previousBlockTab:
                self.frozenText = self.currentTabText()
            elif not self.blockTab:
                self.frozenText = None
            self.saveSettings()
            self.applyPreview()
        except Exception as e:
            log("Settings error: %s" % e)

    # Text and shaping

    def currentFont(self):
        font = Glyphs.font
        if not font:
            self.setDiagnostics("No hi ha cap font oberta.")
            return None
        return font

    def currentTabText(self):
        font = self.currentFont()
        if not font:
            return ""
        tab = getattr(font, "currentTab", None)
        if not tab:
            self.setDiagnostics("No hi ha cap tab actiu per llegir el text Unicode.")
            return ""
        try:
            return tab.text or ""
        except Exception:
            return ""

    def currentPreviewText(self):
        if self.blockTab:
            if self.frozenText is None:
                self.frozenText = self.currentTabText()
            return self.frozenText or ""
        return self.currentTabText()

    def activeFeatures(self):
        presetName = PRESET_NAMES[self.w.presetPopup.get()]
        if presetName == "Custom":
            return [tag for tag in self.w.customFeatures.get().replace(",", " ").split() if tag]
        return PRESET_FEATURES.get(presetName, [])

    def glyphExists(self, font, name):
        try:
            return bool(font.glyphs[name])
        except Exception:
            return False

    def firstExistingGlyphName(self, font, candidates):
        for name in candidates:
            if self.glyphExists(font, name):
                return name
        return None

    def glyphCandidatesForForm(self, char, form):
        baseNames = ARABIC_GLYPH_NAMES.get(char, [])
        if form == "isol":
            suffixes = [".isol", ""]
        elif form == "init":
            suffixes = [".init", ""]
        elif form == "medi":
            suffixes = [".medi", ""]
        else:
            suffixes = [".fina", ""]
        candidates = []
        for name in baseNames:
            for suffix in suffixes:
                candidates.append(name + suffix)
        return candidates

    def isArabicLetter(self, char):
        return char in ARABIC_GLYPH_NAMES

    def isArabicMark(self, char):
        return char in ARABIC_MARK_NAMES

    def canJoinAfter(self, char):
        return char in DUAL_JOINING

    def canJoinBefore(self, char):
        return char in DUAL_JOINING or char in RIGHT_JOINING

    def detectScript(self, text):
        arabic = 0
        latin = 0
        for char in text:
            code = ord(char)
            if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0x08A0 <= code <= 0x08FF:
                arabic += 1
            elif 0x0041 <= code <= 0x007A or 0x00C0 <= code <= 0x024F:
                latin += 1
        if arabic:
            return "Arabic"
        if latin:
            return "Latin"
        return "Unknown"

    def baseItems(self, line):
        items = []
        for char in line:
            if self.isArabicMark(char):
                if items and items[-1].get("char") and self.isArabicLetter(items[-1].get("char")):
                    items[-1].setdefault("marks", []).append(char)
                else:
                    items.append({"char": None, "marks": [char], "space": False})
            elif self.isArabicLetter(char):
                items.append({"char": char, "marks": []})
            else:
                items.append({"char": char, "marks": [], "space": char.isspace()})
        return items

    def shapeArabicLine(self, font, line):
        items = self.baseItems(line)
        shaped = []
        substitutions = []
        missing = []
        i = 0

        while i < len(items):
            item = items[i]
            char = item.get("char")
            if not char:
                i += 1
                continue

            if item.get("space"):
                shaped.append({"glyphs": [], "advance": self.spaceAdvance(font)})
                i += 1
                continue

            if not self.isArabicLetter(char):
                shaped.append({"text": char, "glyphs": [], "advance": self.spaceAdvance(font) * 0.6})
                i += 1
                continue

            prevItem = self.previousArabicItem(items, i)
            nextIndex, nextItem = self.nextArabicItemWithIndex(items, i)
            joinsPrev = bool(prevItem and self.canJoinAfter(prevItem["char"]) and self.canJoinBefore(char))
            joinsNext = bool(nextItem and self.canJoinAfter(char) and self.canJoinBefore(nextItem["char"]))

            if char == "\u0644" and nextItem and nextItem["char"] in LAM_ALEF_NAMES:
                form = "fina" if joinsPrev else "isol"
                ligatureCandidates = []
                for name in LAM_ALEF_NAMES[nextItem["char"]]:
                    ligatureCandidates.extend([name + ("." + form), name])
                glyphName = self.firstExistingGlyphName(font, ligatureCandidates)
                if glyphName:
                    marks = item.get("marks", []) + nextItem.get("marks", [])
                    shaped.append({"glyphs": [glyphName] + self.markGlyphNames(font, marks), "source": char + nextItem["char"]})
                    substitutions.append("%s + %s -> %s" % (char, nextItem["char"], glyphName))
                    i = nextIndex + 1
                    continue

            if joinsPrev and joinsNext:
                form = "medi"
            elif joinsPrev:
                form = "fina"
            elif joinsNext:
                form = "init"
            else:
                form = "isol"

            glyphName = self.firstExistingGlyphName(font, self.glyphCandidatesForForm(char, form))
            if glyphName:
                if form != "isol" or "." in glyphName:
                    substitutions.append("%s -> %s" % (char, glyphName))
                shaped.append({"glyphs": [glyphName] + self.markGlyphNames(font, item.get("marks", [])), "source": char})
            else:
                missing.append("U+%04X" % ord(char))
            i += 1

        # The preview canvas draws left-to-right, so reverse shaped Arabic groups.
        shaped.reverse()
        return shaped, substitutions, missing

    def previousArabicItem(self, items, index):
        for j in range(index - 1, -1, -1):
            char = items[j].get("char")
            if char and self.isArabicLetter(char):
                return items[j]
            if char:
                return None
            if items[j].get("space"):
                return None
        return None

    def nextArabicItem(self, items, index):
        foundIndex, foundItem = self.nextArabicItemWithIndex(items, index)
        return foundItem

    def nextArabicItemWithIndex(self, items, index):
        for j in range(index + 1, len(items)):
            char = items[j].get("char")
            if char and self.isArabicLetter(char):
                return j, items[j]
            if char:
                return None, None
            if items[j].get("space"):
                return None, None
        return None, None

    def markGlyphNames(self, font, marks):
        names = []
        for mark in self.orderedMarks(marks):
            name = self.firstExistingGlyphName(font, ARABIC_MARK_NAMES.get(mark, []))
            if name:
                names.append(name)
        return names

    def orderedMarks(self, marks):
        return sorted(
            marks,
            key=lambda mark: ARABIC_MARK_ORDER.get(mark, 100),
        )

    def spaceAdvance(self, font):
        try:
            master = font.selectedFontMaster
            glyph = font.glyphs["space"]
            return glyph.layers[master.id].width
        except Exception:
            try:
                return font.upm * 0.35
            except Exception:
                return 350

    def applyCallback(self, sender):
        if sender == self.w.applyButton and self.blockTab:
            self.frozenText = self.currentTabText()
        self.applyPreview()

    def applyPreview(self):
        if self.isUpdating:
            return
        self.isUpdating = True
        try:
            font = self.currentFont()
            text = self.currentPreviewText()
            if not font or not text:
                self.shapedLines = []
                self.resizePreview(600)
                self.redrawPreview()
                return

            if self.detectScript(text) == "Arabic":
                self.w.rtlCheck.set(True)
                self.rtl = True

            lines = text.splitlines() or [text]
            shapedLines = []
            substitutions = []
            missing = []
            for line in lines:
                shaped, lineSubs, lineMissing = self.shapeArabicLine(font, line)
                shapedLines.append(shaped)
                substitutions.extend(lineSubs)
                missing.extend(lineMissing)

            self.shapedLines = shapedLines
            height = self.previewHeight(font)
            self.resizePreview(height)
            self.redrawPreview()
            self.updateDiagnostics(text, substitutions, missing)
            self.saveSettings()
        finally:
            self.isUpdating = False

    # Drawing

    def configureScrollView(self):
        scrollView = self.nsScrollView()
        if not scrollView:
            return
        for methodName, value in [
            ("setHasVerticalScroller_", True),
            ("setHasHorizontalScroller_", True),
            ("setAutohidesScrollers_", False),
        ]:
            try:
                getattr(scrollView, methodName)(value)
            except Exception:
                pass

    def nsScrollView(self):
        try:
            return self.w.scroll.getNSScrollView()
        except Exception:
            try:
                return self.w.scroll._nsObject
            except Exception:
                return None

    def previewHeight(self, font):
        lineHeight = self.fontSize * 1.55
        visualLines = 1
        for line in self.shapedLines:
            x = PREVIEW_LEFT_MARGIN
            for group in line:
                advance = self.groupAdvance(font, group)
                if x + advance > self.galleyWidth and x > PREVIEW_LEFT_MARGIN:
                    visualLines += 1
                    x = PREVIEW_LEFT_MARGIN
                x += advance
            visualLines += 1
        return max(720, int(PREVIEW_TOP_MARGIN + PREVIEW_BOTTOM_SAFETY + visualLines * lineHeight))

    def resizePreview(self, height):
        width = max(self.galleyWidth + PREVIEW_LEFT_MARGIN + PREVIEW_RIGHT_SAFETY, 1200)
        self.preview.setFrameSize_(NSMakeSize(width, height))
        self.configureScrollView()
        try:
            self.preview.setNeedsDisplay_(True)
        except Exception:
            pass

    def redrawPreview(self):
        try:
            self.preview.setNeedsDisplay_(True)
        except Exception:
            pass

    def drawPreview(self, rect):
        NSColor.whiteColor().set()
        NSBezierPath.fillRect_(self.preview.bounds())
        self.hitTargets = []

        font = Glyphs.font
        if not font:
            return

        try:
            upm = float(font.upm)
        except Exception:
            upm = 1000.0
        scale = self.fontSize / upm
        margin = PREVIEW_LEFT_MARGIN
        lineY = PREVIEW_TOP_MARGIN
        lineHeight = self.fontSize * 1.55
        try:
            descender = font.selectedFontMaster.descender
        except Exception:
            descender = -200

        NSColor.blackColor().set()
        for line in self.shapedLines:
            x = margin
            for group in line:
                advance = self.groupAdvance(font, group)
                if x + advance > self.galleyWidth and x > margin:
                    x = margin
                    lineY += lineHeight
                if group.get("advance") is not None:
                    x += advance
                    continue
                groupAdvance = 0
                for glyphName, layer, markOffsetX, markOffsetY in self.groupPlacements(font, group):
                    path = layer.completeBezierPath
                    if path and not path.isEmpty():
                        tpath = path.copy()
                        trans = NSAffineTransform.transform()
                        trans.translateXBy_yBy_(
                            x + markOffsetX * scale,
                            lineY - markOffsetY * scale,
                        )
                        trans.scaleXBy_yBy_(scale, -scale)
                        trans.translateXBy_yBy_(0, -descender)
                        tpath.transformUsingAffineTransform_(trans)
                        tpath.fill()
                        try:
                            bounds = tpath.bounds()
                            self.hitTargets.append(
                                {
                                    "rect": (
                                        bounds.origin.x - 5,
                                        bounds.origin.y - 5,
                                        bounds.size.width + 10,
                                        bounds.size.height + 10,
                                    ),
                                    "source": group.get("source"),
                                    "glyphName": glyphName,
                                    "glyphs": [glyphName],
                                }
                            )
                        except Exception:
                            pass
                    try:
                        if layer.width > groupAdvance:
                            groupAdvance = layer.width
                    except Exception:
                        pass
                x += max(groupAdvance * scale, advance)
            lineY += lineHeight

    def layerForGlyphName(self, font, glyphName):
        try:
            glyph = font.glyphs[glyphName]
            if not glyph:
                return None
            master = font.selectedFontMaster
            return glyph.layers[master.id]
        except Exception:
            return None

    def unionRect(self, current, rect):
        if current is None:
            return rect
        minX = min(current.origin.x, rect.origin.x)
        minY = min(current.origin.y, rect.origin.y)
        maxX = max(current.origin.x + current.size.width, rect.origin.x + rect.size.width)
        maxY = max(current.origin.y + current.size.height, rect.origin.y + rect.size.height)
        return NSMakeRect(minX, minY, maxX - minX, maxY - minY)

    def groupAdvance(self, font, group):
        explicitAdvance = group.get("advance")
        if explicitAdvance is not None:
            return explicitAdvance * (self.fontSize / float(getattr(font, "upm", 1000) or 1000))
        maxWidth = 0
        for glyphName in group.get("glyphs", []):
            layer = self.layerForGlyphName(font, glyphName)
            if not layer:
                continue
            try:
                if layer.width > maxWidth:
                    maxWidth = layer.width
            except Exception:
                pass
        try:
            upm = float(font.upm)
        except Exception:
            upm = 1000.0
        return maxWidth * (self.fontSize / upm)

    def groupPlacements(self, font, group):
        placements = []
        glyphNames = group.get("glyphs", [])
        baseLayer = None
        lastTopLayer = None
        lastTopDX = 0
        lastTopDY = 0
        lastBottomLayer = None
        lastBottomDX = 0
        lastBottomDY = 0

        for glyphIndex, glyphName in enumerate(glyphNames):
            layer = self.layerForGlyphName(font, glyphName)
            if not layer:
                continue
            if glyphIndex == 0:
                baseLayer = layer
                placements.append((glyphName, layer, 0, 0))
                continue

            markSide = self.markSide(glyphName, layer)
            if markSide == "bottom" and lastBottomLayer:
                dx, dy = self.markOffsetFromPlacedLayer(lastBottomLayer, layer, lastBottomDX, lastBottomDY, markSide)
            elif markSide == "top" and lastTopLayer:
                dx, dy = self.markOffsetFromPlacedLayer(lastTopLayer, layer, lastTopDX, lastTopDY, markSide)
            elif baseLayer:
                dx, dy = self.markOffset(baseLayer, layer, markSide)
            else:
                dx, dy = 0, 0

            placements.append((glyphName, layer, dx, dy))
            if markSide == "bottom":
                lastBottomLayer = layer
                lastBottomDX = dx
                lastBottomDY = dy
            else:
                lastTopLayer = layer
                lastTopDX = dx
                lastTopDY = dy
        return placements

    def markSide(self, glyphName, layer):
        lowerName = glyphName.lower()
        if "kasra" in lowerName or "below" in lowerName:
            return "bottom"
        if self.anchorPosition(layer, "_bottom"):
            return "bottom"
        return "top"

    def markOffset(self, baseLayer, markLayer):
        return self.markOffsetFromPlacedLayer(baseLayer, markLayer, 0, 0, None)

    def markOffsetFromPlacedLayer(self, targetLayer, markLayer, targetDX, targetDY, preferredSide):
        for baseName, markName in self.anchorPairsForSide(preferredSide):
            baseAnchor = self.anchorPosition(targetLayer, baseName)
            markAnchor = self.anchorPosition(markLayer, markName)
            if baseAnchor and markAnchor:
                return (
                    targetDX + baseAnchor.x - markAnchor.x,
                    targetDY + baseAnchor.y - markAnchor.y,
                )
        return 0, 0

    def anchorPairsForSide(self, side):
        if side == "bottom":
            return [
                ("bottom", "_bottom"),
                ("below", "_below"),
                ("mark", "_mark"),
                ("center", "_center"),
                ("top", "_top"),
                ("above", "_above"),
            ]
        if side == "top":
            return [
                ("top", "_top"),
                ("above", "_above"),
                ("mark", "_mark"),
                ("center", "_center"),
                ("bottom", "_bottom"),
                ("below", "_below"),
            ]
        return [
            ("top", "_top"),
            ("above", "_above"),
            ("bottom", "_bottom"),
            ("below", "_below"),
            ("mark", "_mark"),
            ("center", "_center"),
        ]

    def anchorPosition(self, layer, anchorName):
        try:
            anchor = layer.anchors[anchorName]
            if anchor:
                return anchor.position
        except Exception:
            pass
        try:
            for anchor in layer.anchors:
                if getattr(anchor, "name", None) == anchorName:
                    return anchor.position
        except Exception:
            pass
        return None

    def previewMouseDown_(self, event):
        try:
            try:
                self.preview.window().makeFirstResponder_(self.preview)
            except Exception:
                pass
            if event.clickCount() < 2:
                self.dragStartPoint = event.locationInWindow()
                self.dragStartOrigin = self.visibleOrigin()
                self.lastDragPoint = self.dragStartPoint
                return
            self.dragStartPoint = None
            self.dragStartOrigin = None
            self.lastDragPoint = None
            point = self.preview.convertPoint_fromView_(event.locationInWindow(), None)
            target = self.hitTargetAtPoint(point)
            if not target:
                return
            self.openSourceInNewTab(target)
        except Exception as e:
            log("Double-click error: %s" % e)

    def previewMouseDragged_(self, event):
        try:
            if self.lastDragPoint is None:
                return
            current = event.locationInWindow()
            origin = self.visibleOrigin()
            dx = current.x - self.lastDragPoint.x
            dy = current.y - self.lastDragPoint.y
            self.scrollPreviewToPoint(
                origin.x - dx,
                origin.y - dy,
            )
            self.lastDragPoint = current
        except Exception as e:
            log("Drag error: %s" % e)

    def previewMouseUp_(self, event):
        self.dragStartPoint = None
        self.dragStartOrigin = None
        self.lastDragPoint = None

    def visibleOrigin(self):
        try:
            return self.preview.visibleRect().origin
        except Exception:
            return NSMakePoint(0, 0)

    def scrollPreviewToPoint(self, x, y):
        scrollView = self.nsScrollView()
        if not scrollView:
            return
        try:
            contentView = scrollView.contentView()
            maxX = max(0, self.preview.frame().size.width - contentView.bounds().size.width)
            maxY = max(0, self.preview.frame().size.height - contentView.bounds().size.height)
            x = min(max(0, x), maxX)
            y = min(max(0, y), maxY)
            contentView.scrollToPoint_(NSMakePoint(x, y))
            scrollView.reflectScrolledClipView_(contentView)
        except Exception as e:
            log("Scroll error: %s" % e)

    def hitTargetAtPoint(self, point):
        x = point.x
        y = point.y
        bestTarget = None
        bestDistance = None
        for target in reversed(self.hitTargets):
            rx, ry, rw, rh = target["rect"]
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                centerX = rx + rw / 2.0
                centerY = ry + rh / 2.0
                distance = ((x - centerX) * (x - centerX)) + ((y - centerY) * (y - centerY))
                if bestDistance is None or distance < bestDistance:
                    bestDistance = distance
                    bestTarget = target
        return bestTarget

    def openSourceInNewTab(self, target):
        font = self.currentFont()
        if not font:
            return
        glyphName = target.get("glyphName")
        source = target.get("source")
        tabText = None
        label = None
        if glyphName:
            tabText = "/" + glyphName
            label = glyphName
        elif source:
            tabText = source
            label = source
        if not tabText:
            return
        try:
            font.newTab(tabText)
            glyphs = " ".join(target.get("glyphs", []))
            self.setDiagnostics(
                self.diagnosticsText
                + "\n\nOpened in new tab: %s\nGlyphs: %s" % (label, glyphs)
            )
        except Exception as e:
            self.setDiagnostics("No s'ha pogut obrir el glif en un tab nou: %s" % e)

    # Diagnostics and live update

    def updateDiagnostics(self, text, substitutions, missing):
        glyphNames = []
        for line in self.shapedLines:
            for group in line:
                glyphNames.extend(group.get("glyphs", []))
        lines = [
            "Script: %s" % self.detectScript(text),
            "Direction: RTL preview canvas",
            "Unicode characters: %s" % len(text.replace("\n", "")),
            "Rendered glyphs: %s" % len(glyphNames),
            "Substitutions: %s" % len(substitutions),
            "Features requested: %s" % " ".join(self.activeFeatures()),
            "Engine: script Arabic joining preview, outside Glyphs tabs",
        ]
        if missing:
            lines.append("Missing glyphs: %s" % " ".join(missing[:40]))
        if self.showGlyphNames and glyphNames:
            lines.append("")
            lines.append("Glyph names:")
            lines.append(" ".join(glyphNames[:240]))
        self.setDiagnostics("\n".join(lines))

    def setDiagnostics(self, text):
        self.diagnosticsText = text
        try:
            self.w.info.set(text)
        except Exception:
            log(text)

    def liveTimer_(self, timer):
        if not self.isAlive or not bool(self.w.liveCheck.get()):
            return
        signature = (
            self.currentPreviewText(),
            self.w.presetPopup.get(),
            self.w.customFeatures.get(),
            self.w.sizeField.get(),
            self.w.widthField.get(),
            bool(self.w.blockTabCheck.get()),
        )
        if signature != self.lastLiveSignature:
            self.lastLiveSignature = signature
            self.applyPreview()
        else:
            self.redrawPreview()

    def windowClosed(self, sender):
        self.isAlive = False
        self.saveSettings()
        try:
            self.liveTimer.invalidate()
        except Exception:
            pass


if "shapingDebuggerWindow" in globals():
    try:
        shapingDebuggerWindow.windowClosed(None)
        shapingDebuggerWindow.w.close()
    except Exception:
        pass

shapingDebuggerWindow = ShapingDebugger()
