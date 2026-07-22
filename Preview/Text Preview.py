# MenuTitle: Text Viewer Pro
# Glyphs 3.4.x

from GlyphsApp import Glyphs, GSControlLayer
from vanilla import (
    Window,
    EditText,
    TextBox,
    ScrollView,
    Button,
    PopUpButton
)

from AppKit import (
    NSView,
    NSColor,
    NSBezierPath,
    NSAffineTransform,
    NSMakeSize,
    NSTimer,
    NSRunLoop,
    NSDefaultRunLoopMode
)

from Foundation import NSUserDefaults
import uuid


BACKGROUNDS = {
    0: NSColor.whiteColor(),
    1: NSColor.colorWithCalibratedWhite_alpha_(0.95, 1.0),
    2: NSColor.blackColor(),
}


# ---------------------------------------------------------
# SAFE NSVIEW CLASS
# ---------------------------------------------------------

_previewClassName = "TVPPreviewView_" + uuid.uuid4().hex

TVPPreviewView = type(
    _previewClassName,
    (NSView,),
    {
        "isFlipped": lambda self: True,
        "drawRect_": lambda self, rect: (
            self.owner._drawPreview(rect)
            if hasattr(self, "owner") and self.owner
            else None
        ),
    }
)


class TextViewerPro(object):

    def __init__(self):
        self.lastSignature = None
        self.lastKerningSignature = None
        self.isAlive = True  # Flag to track if window is still alive

        self.loadSettings()
        self.loadMasterList()

        self.w = Window(
            (1000, 700),
            "Text Viewer Pro",
            minSize=(600, 400)
        )

        y = 12

        # Size field with + and - buttons
        self.w.sizeLabel = TextBox(
            (12, y + 3, 40, 20),
            "Size"
        )

        self.w.sizeMinus = Button(
            (55, y, 24, 24),
            "-",
            callback=self.sizeMinus
        )

        self.w.sizeField = EditText(
            (79, y, 50, 24),
            str(int(self.fontSize)),
            callback=self.settingsChanged
        )

        self.w.sizePlus = Button(
            (129, y, 24, 24),
            "+",
            callback=self.sizePlus
        )

        # Galley field with + and - buttons
        self.w.widthLabel = TextBox(
            (170, y + 3, 50, 20),
            "Galley"
        )

        self.w.widthMinus = Button(
            (220, y, 24, 24),
            "-",
            callback=self.widthMinus
        )

        self.w.widthField = EditText(
            (244, y, 50, 24),
            str(int(self.galleyWidth)),
            callback=self.settingsChanged
        )

        self.w.widthPlus = Button(
            (294, y, 24, 24),
            "+",
            callback=self.widthPlus
        )

        # Line field with + and - buttons
        self.w.lineLabel = TextBox(
            (335, y + 3, 40, 20),
            "Line"
        )

        self.w.lineMinus = Button(
            (375, y, 24, 24),
            "-",
            callback=self.lineMinus
        )

        self.w.lineField = EditText(
            (399, y, 50, 24),
            f"{self.lineHeight:.5f}",
            callback=self.settingsChanged
        )

        self.w.linePlus = Button(
            (449, y, 24, 24),
            "+",
            callback=self.linePlus
        )

        # After field with + and - buttons
        self.w.spaceLabel = TextBox(
            (490, y + 3, 45, 20),
            "After"
        )

        self.w.spaceMinus = Button(
            (535, y, 24, 24),
            "-",
            callback=self.spaceMinus
        )

        self.w.spaceField = EditText(
            (559, y, 50, 24),
            str(int(self.spaceAfter)),
            callback=self.settingsChanged
        )

        self.w.spacePlus = Button(
            (609, y, 24, 24),
            "+",
            callback=self.spacePlus
        )

        # Align buttons (Left, Center, Right)
        self.w.alignLabel = TextBox(
            (650, y + 3, 40, 20),
            "Align"
        )

        self.w.alignLeft = Button(
            (695, y, 35, 24),
            "L",
            callback=self.alignLeft
        )

        self.w.alignCenter = Button(
            (735, y, 35, 24),
            "C",
            callback=self.alignCenter
        )

        self.w.alignRight = Button(
            (775, y, 35, 24),
            "R",
            callback=self.alignRight
        )

        # Background buttons (White, Light, Black)
        self.w.bgLabel = TextBox(
            (825, y + 3, 40, 20),
            "Bg"
        )

        self.w.bgWhite = Button(
            (870, y, 35, 24),
            "W",
            callback=self.bgWhite
        )

        self.w.bgLight = Button(
            (910, y, 35, 24),
            "L",
            callback=self.bgLight
        )

        self.w.bgBlack = Button(
            (950, y, 35, 24),
            "B",
            callback=self.bgBlack
        )

        # Master popup (kept as dropdown)
        self.w.masterLabel = TextBox(
            (12, y + 35, 50, 20),
            "Master"
        )

        self.w.masterPopup = PopUpButton(
            (65, y + 32, 180, 24),
            self.masterNames,
            callback=self.masterChanged
        )

        if self.masterNames:
            self.w.masterPopup.set(
                min(
                    self.selectedMasterIndex,
                    len(self.masterNames) - 1
                )
            )

        # Refresh button for manual update
        self.w.refreshButton = Button(
            (260, y + 32, 80, 24),
            "Refresh",
            callback=self.manualRefresh
        )

        self.preview = TVPPreviewView.alloc().init()
        self.preview.owner = self

        self.w.scroll = ScrollView(
            (12, 65, -12, -12),
            self.preview
        )

        self.w.open()

        # Timer for live refresh
        self.liveTimer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.3,
            self,
            "checkTextChange:",
            None,
            True
        )

        NSRunLoop.currentRunLoop().addTimer_forMode_(
            self.liveTimer,
            NSDefaultRunLoopMode
        )

        # Register for font change notifications
        from Foundation import NSNotificationCenter
        nc = NSNotificationCenter.defaultCenter()
        
        nc.addObserver_selector_name_object_(
            self,
            "fontChanged:",
            "NSFontChangedNotification",
            None
        )
        
        nc.addObserver_selector_name_object_(
            self,
            "fontChanged:",
            "GlyphsFontDidChangeNotification",
            None
        )

        self.updatePreviewSize()
    
    def fontChanged_(self, notification):
        """Called when font changes (including kerning edits)"""
        if not self.isAlive:
            return
            
        f = Glyphs.font
        if f and f.masters:
            newNames = [m.name for m in f.masters]
            if newNames != self.masterNames:
                self.masterNames = newNames
                try:
                    self.w.masterPopup.setItems(self.masterNames)
                except:
                    pass
        
        self.updatePreviewSize()
        
    # ---------------------------------------------------------
    # SETTINGS
    # ---------------------------------------------------------

    def loadSettings(self):
        d = NSUserDefaults.standardUserDefaults()

        self.fontSize = d.floatForKey_("TVP_fontSize") or 72
        self.galleyWidth = d.floatForKey_("TVP_galleyWidth") or 700
        self.lineHeight = d.floatForKey_("TVP_lineHeight") or 1.2
        self.spaceAfter = d.floatForKey_("TVP_spaceAfter") or 30
        self.align = d.integerForKey_("TVP_align") or 0
        self.bg = d.integerForKey_("TVP_bg") or 0
        self.selectedMasterIndex = (
            d.integerForKey_("TVP_selectedMaster") or 0
        )

    def saveSettings(self):
        d = NSUserDefaults.standardUserDefaults()

        d.setFloat_forKey_(
            self.fontSize,
            "TVP_fontSize"
        )

        d.setFloat_forKey_(
            self.galleyWidth,
            "TVP_galleyWidth"
        )

        d.setFloat_forKey_(
            self.lineHeight,
            "TVP_lineHeight"
        )

        d.setFloat_forKey_(
            self.spaceAfter,
            "TVP_spaceAfter"
        )

        d.setInteger_forKey_(
            self.align,
            "TVP_align"
        )

        d.setInteger_forKey_(
            self.bg,
            "TVP_bg"
        )

        d.setInteger_forKey_(
            self.selectedMasterIndex,
            "TVP_selectedMaster"
        )

    # ---------------------------------------------------------
    # MASTER MANAGEMENT
    # ---------------------------------------------------------

    def loadMasterList(self):
        f = Glyphs.font

        if f and f.masters:
            self.masterNames = [
                m.name for m in f.masters
            ]
        else:
            self.masterNames = ["No Font"]

    def currentMaster(self):
        f = Glyphs.font

        if not f:
            return None

        if not f.masters:
            return None

        idx = min(
            self.selectedMasterIndex,
            len(f.masters) - 1
        )

        return f.masters[idx]

    # ---------------------------------------------------------
    # BUTTON CALLBACKS
    # ---------------------------------------------------------

    def sizeMinus(self, sender):
        self.fontSize = max(6, self.fontSize - 1)
        self.w.sizeField.set(str(int(self.fontSize)))
        self.saveSettings()
        self.updatePreviewSize()

    def sizePlus(self, sender):
        self.fontSize = min(300, self.fontSize + 1)
        self.w.sizeField.set(str(int(self.fontSize)))
        self.saveSettings()
        self.updatePreviewSize()

    def widthMinus(self, sender):
        self.galleyWidth = max(100, self.galleyWidth - 10)
        self.w.widthField.set(str(int(self.galleyWidth)))
        self.saveSettings()
        self.updatePreviewSize()

    def widthPlus(self, sender):
        self.galleyWidth = min(2000, self.galleyWidth + 10)
        self.w.widthField.set(str(int(self.galleyWidth)))
        self.saveSettings()
        self.updatePreviewSize()

    def lineMinus(self, sender):
        self.lineHeight = round(max(0.5, self.lineHeight - 0.05), 5)
        self.w.lineField.set(f"{self.lineHeight:.5f}")
        self.saveSettings()
        self.updatePreviewSize()

    def linePlus(self, sender):
        self.lineHeight = round(min(3.0, self.lineHeight + 0.05), 5)
        self.w.lineField.set(f"{self.lineHeight:.5f}")
        self.saveSettings()
        self.updatePreviewSize()

    def spaceMinus(self, sender):
        self.spaceAfter = max(0, self.spaceAfter - 5)
        self.w.spaceField.set(str(int(self.spaceAfter)))
        self.saveSettings()
        self.updatePreviewSize()

    def spacePlus(self, sender):
        self.spaceAfter = min(200, self.spaceAfter + 5)
        self.w.spaceField.set(str(int(self.spaceAfter)))
        self.saveSettings()
        self.updatePreviewSize()

    def alignLeft(self, sender):
        self.align = 0
        self.saveSettings()
        self.updatePreviewSize()

    def alignCenter(self, sender):
        self.align = 1
        self.saveSettings()
        self.updatePreviewSize()

    def alignRight(self, sender):
        self.align = 2
        self.saveSettings()
        self.updatePreviewSize()

    def bgWhite(self, sender):
        self.bg = 0
        self.saveSettings()
        try:
            self.preview.setNeedsDisplay_(True)
        except:
            pass

    def bgLight(self, sender):
        self.bg = 1
        self.saveSettings()
        try:
            self.preview.setNeedsDisplay_(True)
        except:
            pass

    def bgBlack(self, sender):
        self.bg = 2
        self.saveSettings()
        try:
            self.preview.setNeedsDisplay_(True)
        except:
            pass

    def manualRefresh(self, sender):
        """Manual refresh button callback"""
        self.updatePreviewSize()

    # ---------------------------------------------------------
    # SETTINGS CHANGED
    # ---------------------------------------------------------

    def settingsChanged(self, sender=None):
        try:
            self.fontSize = float(
                self.w.sizeField.get()
            )

            self.galleyWidth = float(
                self.w.widthField.get()
            )

            self.lineHeight = float(
                self.w.lineField.get()
            )

            self.spaceAfter = float(
                self.w.spaceField.get()
            )

            self.saveSettings()
            self.updatePreviewSize()

        except:
            pass

    def masterChanged(self, sender):
        self.selectedMasterIndex = self.w.masterPopup.get()
        self.saveSettings()
        self.updatePreviewSize()

    # ---------------------------------------------------------
    # LAYOUT ENGINE
    # ---------------------------------------------------------

    def getKerningSignature(self):
        """Generate a signature of current kerning to detect changes"""
        f = Glyphs.font
        if not f:
            return None
        
        kerning = f.kerning
        if not kerning:
            return None
        
        sig_items = []
        for master_id, master_kerning in kerning.items():
            if master_kerning:
                for pair, value in master_kerning.items():
                    sig_items.append(f"{master_id}:{pair}:{value}")
        
        return tuple(sorted(sig_items))

    def layoutGlyphs(self):
        positioned = []
        height = 600

        f = Glyphs.font
        if not f or not f.currentTab:
            return positioned, height

        master = self.currentMaster()
        scale = self.fontSize / float(f.upm)
        lineHeightAbs = self.fontSize * self.lineHeight

        tab = f.currentTab
        layers = list(tab.layers)

        gv = tab.graphicView()
        lm = gv.layoutManager()

        try:
            editorScale = gv.scale()
        except:
            editorScale = 1.0

        xStart = 40
        yStart = 160
        lineY = yStart
        lineAdvance = 0.0

        glyphItems = []
        spaceGlyphNames = set(
            [
                "space",
                "nbspace",
                "uni00A0",
                "emspace",
                "enspace",
                "figurespace",
                "thinspace",
                "hairspace",
                "zerowidthspace",
            ]
        )

        for i, layer in enumerate(layers):

            if isinstance(layer, GSControlLayer):
                glyphItems.append(None)
                continue

            renderLayer = layer

            if master and getattr(layer, "parent", None):
                try:
                    renderLayer = layer.parent.layers[master.id]
                except:
                    pass

            try:
                pos = lm.cachedLayersPositionAtIndex_(i)
            except:
                continue

            path = None
            bounds = None

            if hasattr(renderLayer, "completeBezierPath"):
                path = renderLayer.completeBezierPath

                if path and not path.isEmpty():
                    bounds = path.bounds()

            glyphName = ""

            try:
                glyphName = layer.parent.name
            except:
                pass

            glyphItems.append(
                {
                    "layer": renderLayer,
                    "bounds": bounds,
                    "visible": bounds is not None,
                    "pos": pos,
                    "advance": getattr(renderLayer, "width", 0) or 0,
                    "isSpace": glyphName in spaceGlyphNames,
                    "tabIndex": i,
                }
            )

        for index, item in enumerate(glyphItems):

            if item is None:
                continue

            pos = item["pos"]
            advance = item["advance"]

            for nextItem in glyphItems[index + 1:]:
                if nextItem is None:
                    break

                nextPos = nextItem["pos"]

                if abs(nextPos.y - pos.y) > 1:
                    break

                advance = (nextPos.x - pos.x) / editorScale
                break

            item["advance"] = advance

        tokens = []
        currentToken = None

        for item in glyphItems:

            if item is None:
                if currentToken:
                    tokens.append(currentToken)
                    currentToken = None

                tokens.append(None)
                continue

            tokenType = "space" if item["isSpace"] else "word"

            if not currentToken or currentToken["type"] != tokenType:
                if currentToken:
                    tokens.append(currentToken)

                currentToken = {
                    "type": tokenType,
                    "items": [],
                    "advance": 0.0,
                }

            currentToken["items"].append(item)
            currentToken["advance"] += item["advance"] * scale

        if currentToken:
            tokens.append(currentToken)

        for token in tokens:

            if token is None:
                lineY += lineHeightAbs + self.spaceAfter
                lineAdvance = 0.0
                continue

            if token["type"] == "space" and lineAdvance == 0:
                continue

            if (
                token["type"] == "word"
                and
                lineAdvance > 0
                and lineAdvance + token["advance"] > self.galleyWidth
            ):
                lineY += lineHeightAbs
                lineAdvance = 0.0

            tokenX = xStart + lineAdvance
            itemAdvance = 0.0

            for item in token["items"]:
                if item["visible"]:
                    positioned.append(
                        (
                            item["layer"],
                            tokenX + itemAdvance,
                            lineY,
                            item["bounds"]
                        )
                    )

                itemAdvance += (
                    item["advance"]
                    * scale
                )

            lineAdvance += token["advance"]

        if positioned:
            height = max(positioned[-1][2] + 300, 600)

        return positioned, height

    def lineWidthsForPositionedGlyphs(self, positioned):
        scale = 1.0
        f = Glyphs.font

        if f:
            scale = self.fontSize / float(f.upm)

        lines = {}
        lineWidths = {}

        for (
            layer,
            x,
            y,
            bounds
        ) in positioned:

            if y not in lines:
                lines[y] = []

            lines[y].append(
                (
                    layer,
                    x,
                    bounds
                )
            )

        for y, items in lines.items():
            minLeft = None
            maxRight = 0

            for (
                layer,
                x,
                bounds
            ) in items:
                left = x
                right = (
                    x
                    + bounds.size.width * scale
                )

                if minLeft is None or left < minLeft:
                    minLeft = left

                if right > maxRight:
                    maxRight = right

            lineWidths[y] = maxRight - (minLeft or 0)

        return lineWidths

    def alignedOffsetForLine(self, lineWidth):
        if self.align == 1:
            return (
                self.galleyWidth
                - lineWidth
            ) / 2.0

        if self.align == 2:
            return (
                self.galleyWidth
                - lineWidth
            )

        return 0
    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------

    def _drawPreview(self, rect):
        BACKGROUNDS[int(self.bg)].set()

        try:
            NSBezierPath.fillRect_(
                self.preview.bounds()
            )
        except:
            return

        positioned, _ = self.layoutGlyphs()

        fillColor = (
            NSColor.whiteColor()
            if int(self.bg) == 2
            else NSColor.blackColor()
        )

        fillColor.set()

        f = Glyphs.font

        if not f:
            return

        master = self.currentMaster()

        scale = (
            self.fontSize / float(f.upm)
        )

        lineWidths = self.lineWidthsForPositionedGlyphs(positioned)

        for (
            layer,
            x,
            y,
            bounds
        ) in positioned:

            drawX = (
                x
                + self.alignedOffsetForLine(lineWidths[y])
            )

            path = layer.completeBezierPath

            if not path:
                continue

            if path.isEmpty():
                continue

            tpath = path.copy()

            trans = (
                NSAffineTransform.transform()
            )

            trans.translateXBy_yBy_(
                drawX,
                y
            )

            trans.scaleXBy_yBy_(
                scale,
                -scale
            )

            descender = 0

            if master:
                descender = (
                    master.descender
                )

            trans.translateXBy_yBy_(
                0,
                -descender
            )

            tpath.transformUsingAffineTransform_(
                trans
            )

            tpath.fill()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def updatePreviewSize(self):
        if not self.isAlive:
            return
            
        try:
            _, h = self.layoutGlyphs()

            # Get window size safely
            window_width = 800  # default fallback
            try:
                window_width = self.w.getPosSize()[2]
            except:
                pass

            self.preview.setFrameSize_(
                NSMakeSize(
                    max(
                        self.galleyWidth + 120,
                        window_width - 30
                    ),
                    h
                )
            )

            self.preview.setNeedsDisplay_(True)
        except:
            pass

    # ---------------------------------------------------------
    # LIVE REFRESH
    # ---------------------------------------------------------

    def checkTextChange_(self, timer):
        if not self.isAlive:
            return
            
        try:
            f = Glyphs.font

            if not f:
                return

            if not f.currentTab:
                return

            # Update master list if font changed
            if f.masters:
                newNames = [m.name for m in f.masters]
                if newNames != self.masterNames:
                    self.masterNames = newNames
                    try:
                        self.w.masterPopup.setItems(self.masterNames)
                    except:
                        pass
                    if self.selectedMasterIndex >= len(self.masterNames):
                        self.selectedMasterIndex = 0
                        try:
                            self.w.masterPopup.set(self.selectedMasterIndex)
                        except:
                            pass

            # Get current kerning signature
            currentKerningSig = self.getKerningSignature()
            
            # Create signature including kerning
            sig = (
                f.currentTab.text,
                self.fontSize,
                self.galleyWidth,
                self.selectedMasterIndex,
                currentKerningSig
            )

            if sig != self.lastSignature:
                self.lastSignature = sig
                self.updatePreviewSize()
        except:
            pass

    def __del__(self):
        """Cleanup when window is closed"""
        self.isAlive = False
        if hasattr(self, 'liveTimer'):
            try:
                self.liveTimer.invalidate()
            except:
                pass


# ---------------------------------------------------------
# CLEAN RESTART
# ---------------------------------------------------------

if "tvpWindow" in globals():
    try:
        tvpWindow.isAlive = False
        tvpWindow.w.close()
    except:
        pass

tvpWindow = TextViewerPro()
