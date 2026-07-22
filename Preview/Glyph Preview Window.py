# MenuTitle: Glyph Preview Window PRO v3
# -*- coding: utf-8 -*-
# Description: Detached real-time glyph preview window with responsive resize, top toolbar, zoom, pan, auto-fit, master lines, blue zones and metric labels.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at:
# https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc


# ------------------------------------------------------------
#   DEFAULT KEYS
# ------------------------------------------------------------

PREFIX = "com.joseppatau.previewpro.v3."

ZOOM_KEY = PREFIX + "zoom"
OFFSET_X_KEY = PREFIX + "offsetX"
OFFSET_Y_KEY = PREFIX + "offsetY"

AUTO_FIT_KEY = PREFIX + "autoFit"

SHOW_MASTER_LINES_KEY = PREFIX + "showMasterLines"
MASTER_LINES_COLOR_KEY = PREFIX + "masterLinesColor"

SHOW_BLUE_ZONES_KEY = PREFIX + "showBlueZones"
BLUE_ZONES_COLOR_KEY = PREFIX + "blueZonesColor"

SHOW_LABELS_KEY = PREFIX + "showLabels"

DEFAULT_MASTER_LINES_COLOR = "C5EFFF"
DEFAULT_BLUE_ZONES_COLOR = "E9F3F2"


# ------------------------------------------------------------
#   PREVIEW VIEW
# ------------------------------------------------------------

# Utilitzem el mateix patró que funcionava a la versió anterior
if "GlyphPreviewProView_v3c" not in globals():

    class GlyphPreviewProView_v3c(NSView):

        def initWithFrame_(self, frame):
            self = objc.super(GlyphPreviewProView_v3c, self).initWithFrame_(frame)
            if self is None:
                return None

            self.zoom = self.floatDefault(ZOOM_KEY, 1.0)
            self.offset = NSPoint(
                self.floatDefault(OFFSET_X_KEY, 0.0),
                self.floatDefault(OFFSET_Y_KEY, 0.0)
            )

            self.autoFit = bool(Glyphs.defaults.get(AUTO_FIT_KEY, True))

            self.showMasterLines = bool(Glyphs.defaults.get(SHOW_MASTER_LINES_KEY, False))
            self.masterLinesColorHex = Glyphs.defaults.get(MASTER_LINES_COLOR_KEY, DEFAULT_MASTER_LINES_COLOR)

            self.showBlueZones = bool(Glyphs.defaults.get(SHOW_BLUE_ZONES_KEY, False))
            self.blueZonesColorHex = Glyphs.defaults.get(BLUE_ZONES_COLOR_KEY, DEFAULT_BLUE_ZONES_COLOR)

            self.showLabels = bool(Glyphs.defaults.get(SHOW_LABELS_KEY, True))

            self.lastDrag = None
            return self

        # ------------------------------------------------------------
        #   DEFAULT HELPERS
        # ------------------------------------------------------------

        @objc.python_method
        def floatDefault(self, key, fallback):
            try:
                return float(Glyphs.defaults.get(key, fallback))
            except:
                return fallback

        @objc.python_method
        def saveViewState(self):
            Glyphs.defaults[ZOOM_KEY] = self.zoom
            Glyphs.defaults[OFFSET_X_KEY] = self.offset.x
            Glyphs.defaults[OFFSET_Y_KEY] = self.offset.y
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit
            Glyphs.defaults[SHOW_MASTER_LINES_KEY] = self.showMasterLines
            Glyphs.defaults[MASTER_LINES_COLOR_KEY] = self.masterLinesColorHex
            Glyphs.defaults[SHOW_BLUE_ZONES_KEY] = self.showBlueZones
            Glyphs.defaults[BLUE_ZONES_COLOR_KEY] = self.blueZonesColorHex
            Glyphs.defaults[SHOW_LABELS_KEY] = self.showLabels

        # ------------------------------------------------------------
        #   CURRENT LAYER
        # ------------------------------------------------------------

        @objc.python_method
        def currentLayer(self):
            f = Glyphs.font
            if not f:
                return None
            if f.selectedLayers:
                return f.selectedLayers[0]
            return None

        # ------------------------------------------------------------
        #   UI SETTERS
        # ------------------------------------------------------------

        def setZoom_(self, value):
            self.zoom = max(0.05, float(value))
            self.autoFit = False
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setAutoFit_(self, value):
            self.autoFit = bool(value)
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit
            if self.autoFit:
                self.offset = NSPoint(0, 0)
                self.zoom = 1.0
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setShowMasterLines_(self, value):
            self.showMasterLines = bool(value)
            Glyphs.defaults[SHOW_MASTER_LINES_KEY] = self.showMasterLines
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setMasterLinesColorHex_(self, value):
            self.masterLinesColorHex = self.cleanHex(value, DEFAULT_MASTER_LINES_COLOR)
            Glyphs.defaults[MASTER_LINES_COLOR_KEY] = self.masterLinesColorHex
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setShowBlueZones_(self, value):
            self.showBlueZones = bool(value)
            Glyphs.defaults[SHOW_BLUE_ZONES_KEY] = self.showBlueZones
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setBlueZonesColorHex_(self, value):
            self.blueZonesColorHex = self.cleanHex(value, DEFAULT_BLUE_ZONES_COLOR)
            Glyphs.defaults[BLUE_ZONES_COLOR_KEY] = self.blueZonesColorHex
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setShowLabels_(self, value):
            self.showLabels = bool(value)
            Glyphs.defaults[SHOW_LABELS_KEY] = self.showLabels
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   RESIZE
        # ------------------------------------------------------------

        def setFrameSize_(self, size):
            objc.super(GlyphPreviewProView_v3c, self).setFrameSize_(size)
            self.setNeedsDisplay_(True)

        def setFrame_(self, frame):
            objc.super(GlyphPreviewProView_v3c, self).setFrame_(frame)
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   COLORS
        # ------------------------------------------------------------

        @objc.python_method
        def cleanHex(self, value, fallback):
            try:
                value = str(value).strip().replace("#", "").upper()
                if len(value) == 3:
                    value = "".join([c + c for c in value])
                if len(value) != 6:
                    return fallback
                int(value, 16)
                return value
            except:
                return fallback

        @objc.python_method
        def colorFromHex(self, value, fallback, alpha=1.0):
            h = self.cleanHex(value, fallback)
            r = int(h[0:2], 16) / 255.0
            g = int(h[2:4], 16) / 255.0
            b = int(h[4:6], 16) / 255.0
            return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, alpha)

        # ------------------------------------------------------------
        #   FIT / ZOOM / PAN
        # ------------------------------------------------------------

        @objc.python_method
        def fitGlyph(self):
            self.autoFit = True
            self.zoom = 1.0
            self.offset = NSPoint(0, 0)
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit
            self.setNeedsDisplay_(True)

        def mouseDown_(self, event):
            if event.clickCount() == 2:
                self.fitGlyph()
                return
            self.lastDrag = event.locationInWindow()

        def mouseDragged_(self, event):
            if not self.lastDrag:
                return

            self.autoFit = False
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit

            newPoint = event.locationInWindow()
            dx = newPoint.x - self.lastDrag.x
            dy = newPoint.y - self.lastDrag.y

            self.offset.x += dx
            self.offset.y += dy

            self.lastDrag = newPoint
            self.setNeedsDisplay_(True)

        def mouseUp_(self, event):
            self.lastDrag = None

        def scrollWheel_(self, event):
            self.autoFit = False
            Glyphs.defaults[AUTO_FIT_KEY] = self.autoFit

            delta = event.deltaY() * 0.05
            self.zoom += delta
            self.zoom = max(0.05, self.zoom)
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   METRIC DATA
        # ------------------------------------------------------------

        @objc.python_method
        def metricLines(self, layer):
            master = layer.master
            if not master:
                return []

            values = []
            metrics = [
                ("Ascender", "ascender"),
                ("Cap Height", "capHeight"),
                ("x-height", "xHeight"),
                ("Baseline", None),
                ("Descender", "descender"),
            ]

            for label, attr in metrics:
                try:
                    if attr is None:
                        y = 0.0
                    else:
                        y = float(getattr(master, attr))
                    values.append((label, y))
                except:
                    pass

            return values

        @objc.python_method
        def zonePositionAndSize(self, zone):
            position = None
            size = None

            try:
                if hasattr(zone, "position"):
                    position = float(zone.position)
            except:
                pass

            try:
                if hasattr(zone, "size"):
                    size = float(zone.size)
            except:
                pass

            if isinstance(zone, (list, tuple)):
                try:
                    if len(zone) > 0:
                        position = float(zone[0])
                    if len(zone) > 1:
                        size = float(zone[1])
                except:
                    pass

            return position, size

        @objc.python_method
        def metricValuePositionAndOvershoot(self, metric_value):
            position = None
            overshoot = None

            for attr in ("position", "pos", "value"):
                try:
                    if hasattr(metric_value, attr):
                        position = float(getattr(metric_value, attr))
                        break
                except:
                    pass

            try:
                if hasattr(metric_value, "overshoot"):
                    overshoot = float(metric_value.overshoot)
            except:
                pass

            if isinstance(metric_value, (list, tuple)):
                try:
                    if len(metric_value) > 0:
                        position = float(metric_value[0])
                    if len(metric_value) > 1:
                        overshoot = float(metric_value[1])
                except:
                    pass

            return position, overshoot

        @objc.python_method
        def blueZones(self, layer):
            master = layer.master
            if not master:
                return []

            zones = []

            for attr in ("alignmentZones", "blueZones"):
                try:
                    if hasattr(master, attr):
                        for z in list(getattr(master, attr)):
                            pos, size = self.zonePositionAndSize(z)
                            if pos is not None and size is not None and size != 0:
                                zones.append((pos, pos + size))
                except:
                    pass

            try:
                metrics = master.metrics
                metric_values = []

                try:
                    if hasattr(metrics, "values"):
                        metric_values = list(metrics.values())
                    elif hasattr(metrics, "allValues"):
                        metric_values = list(metrics.allValues())
                    else:
                        metric_values = list(metrics)
                except:
                    metric_values = []

                for mv in metric_values:
                    pos, overshoot = self.metricValuePositionAndOvershoot(mv)
                    if pos is not None and overshoot is not None and overshoot != 0:
                        zones.append((pos, pos + overshoot))
            except:
                pass

            clean = []
            seen = set()
            for y1, y2 in zones:
                key = (round(y1, 3), round(y2, 3))
                if key not in seen:
                    seen.add(key)
                    clean.append((y1, y2))

            return clean

        # ------------------------------------------------------------
        #   TRANSFORM
        # ------------------------------------------------------------

        @objc.python_method
        def glyphMargins(self):
            left = 100 if self.showLabels and (self.showMasterLines or self.showBlueZones) else 35
            right = 35
            top = 35
            bottom = 35
            return left, right, top, bottom

        @objc.python_method
        def getGlyphTransform(self, layer):
            viewBounds = self.bounds()
            viewW = max(1.0, viewBounds.size.width)
            viewH = max(1.0, viewBounds.size.height)

            glyphBounds = layer.bounds
            if glyphBounds.size.width == 0 or glyphBounds.size.height == 0:
                return None, None

            left, right, top, bottom = self.glyphMargins()

            usableW = max(1.0, viewW - left - right)
            usableH = max(1.0, viewH - top - bottom)

            glyphW = glyphBounds.size.width
            glyphH = glyphBounds.size.height

            baseScale = min(usableW / glyphW, usableH / glyphH)

            if self.autoFit:
                scale = baseScale * 0.90
                currentOffset = NSPoint(0, 0)
            else:
                scale = baseScale * self.zoom
                currentOffset = self.offset

            drawW = glyphW * scale
            drawH = glyphH * scale

            extraX = left + (usableW - drawW) / 2.0
            extraY = bottom + (usableH - drawH) / 2.0

            tx = -glyphBounds.origin.x * scale
            ty = -glyphBounds.origin.y * scale

            transform = NSAffineTransform.transform()
            transform.translateXBy_yBy_(
                tx + extraX + currentOffset.x,
                ty + extraY + currentOffset.y
            )
            transform.scaleXBy_yBy_(scale, scale)

            return transform, scale

        @objc.python_method
        def transformPoint(self, transform, x, y):
            return transform.transformPoint_(NSPoint(x, y))

        # ------------------------------------------------------------
        #   DRAW HELPERS
        # ------------------------------------------------------------

        @objc.python_method
        def drawHorizontalLine(self, transform, y, color, glyphBounds, scale):
            marginUnits = max(20.0, 25.0 / max(scale, 0.001))
            x1 = glyphBounds.origin.x - marginUnits
            x2 = glyphBounds.origin.x + glyphBounds.size.width + marginUnits

            p1 = self.transformPoint(transform, x1, y)
            p2 = self.transformPoint(transform, x2, y)

            color.set()
            path = NSBezierPath.bezierPath()
            path.setLineWidth_(1.0)
            path.moveToPoint_(p1)
            path.lineToPoint_(p2)
            path.stroke()

        @objc.python_method
        def drawHorizontalBand(self, transform, y1, y2, color, glyphBounds, scale):
            marginUnits = max(20.0, 25.0 / max(scale, 0.001))
            x1 = glyphBounds.origin.x - marginUnits
            x2 = glyphBounds.origin.x + glyphBounds.size.width + marginUnits

            p1 = self.transformPoint(transform, x1, y1)
            p2 = self.transformPoint(transform, x2, y2)

            rect = NSMakeRect(
                min(p1.x, p2.x),
                min(p1.y, p2.y),
                abs(p2.x - p1.x),
                abs(p2.y - p1.y)
            )

            color.set()
            NSBezierPath.fillRect_(rect)

        @objc.python_method
        def drawMetricLabel(self, text, y, transform, color):
            if not self.showLabels:
                return

            p = self.transformPoint(transform, 0, y)

            paragraph = NSMutableParagraphStyle.alloc().init()
            paragraph.setAlignment_(NSRightTextAlignment)

            attrs = {
                NSFontAttributeName: NSFont.systemFontOfSize_(10),
                NSForegroundColorAttributeName: color,
                NSParagraphStyleAttributeName: paragraph,
            }

            s = NSString.stringWithString_(text)
            rect = NSMakeRect(8, p.y - 7, 82, 16)
            s.drawInRect_withAttributes_(rect, attrs)

        # ------------------------------------------------------------
        #   DRAW
        # ------------------------------------------------------------

        def drawRect_(self, rect):

            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())

            layer = self.currentLayer()
            if not layer:
                return

            path = layer.completeBezierPath
            if not path:
                return

            glyphBounds = layer.bounds
            if glyphBounds.size.width == 0 or glyphBounds.size.height == 0:
                return

            transform, scale = self.getGlyphTransform(layer)
            if transform is None:
                return

            if self.showBlueZones:
                zoneColor = self.colorFromHex(self.blueZonesColorHex, DEFAULT_BLUE_ZONES_COLOR, alpha=1.0)
                for y1, y2 in self.blueZones(layer):
                    self.drawHorizontalBand(transform, y1, y2, zoneColor, glyphBounds, scale)

            if self.showMasterLines:
                lineColor = self.colorFromHex(self.masterLinesColorHex, DEFAULT_MASTER_LINES_COLOR, alpha=1.0)
                for label, y in self.metricLines(layer):
                    self.drawHorizontalLine(transform, y, lineColor, glyphBounds, scale)
                    self.drawMetricLabel(label, y, transform, lineColor)

            p = path.copy()
            p.transformUsingAffineTransform_(transform)
            NSColor.blackColor().set()
            p.fill()


# ------------------------------------------------------------
#   VANILLA CUSTOM VIEW WRAPPER
# ------------------------------------------------------------

class GlyphPreviewProVanillaView_v3c(VanillaBaseObject):

    nsViewClass = GlyphPreviewProView_v3c

    def __init__(self, posSize):
        self._setupView(self.nsViewClass, posSize)

    def getNSView(self):
        return self._nsObject


# ------------------------------------------------------------
#   WINDOW
# ------------------------------------------------------------

class GlyphPreviewProWindow_v3c(object):

    def __init__(self):

        if not Glyphs.font:
            Message("No Font Open", "Open a font first.")
            return

        self.w = Window(
            (1060, 1800),
            "Glyph Preview PRO",
            minSize=(520, 520)
        )

        # Top toolbar in foreground
        self.w.toolbar = Group((0, 0, -0, 62))
        self.w.toolbar.box = Box((0, 0, -0, -0))

        self.w.toolbar.showMasterLines = CheckBox(
            (20, 18, 135, 22),
            "Show master lines",
            value=bool(Glyphs.defaults.get(SHOW_MASTER_LINES_KEY, False)),
            callback=self.showMasterLinesChanged
        )

        self.w.toolbar.masterLinesColor = EditText(
            (160, 16, 70, 24),
            Glyphs.defaults.get(MASTER_LINES_COLOR_KEY, DEFAULT_MASTER_LINES_COLOR),
            callback=self.masterLinesColorChanged
        )

        self.w.toolbar.showBlueZones = CheckBox(
            (250, 18, 110, 22),
            "View blue zone",
            value=bool(Glyphs.defaults.get(SHOW_BLUE_ZONES_KEY, False)),
            callback=self.showBlueZonesChanged
        )

        self.w.toolbar.blueZonesColor = EditText(
            (365, 16, 70, 24),
            Glyphs.defaults.get(BLUE_ZONES_COLOR_KEY, DEFAULT_BLUE_ZONES_COLOR),
            callback=self.blueZonesColorChanged
        )

        self.w.toolbar.showLabels = CheckBox(
            (455, 18, 75, 22),
            "Labels",
            value=bool(Glyphs.defaults.get(SHOW_LABELS_KEY, True)),
            callback=self.showLabelsChanged
        )

        self.w.toolbar.autoFit = CheckBox(
            (540, 18, 80, 22),
            "Auto fit",
            value=bool(Glyphs.defaults.get(AUTO_FIT_KEY, True)),
            callback=self.autoFitChanged
        )

        # Preview sits below toolbar
        self.w.preview = GlyphPreviewProVanillaView_v3c((20, 72, -20, -82))
        self.view = self.w.preview.getNSView()

        # Bottom controls
        self.w.zoomSlider = Slider(
            (20, -52, -170, 20),
            minValue=0.1,
            maxValue=5.0,
            value=self.view.zoom,
            callback=self.zoomChanged
        )

        self.w.saveButton = Button(
            (-150, -55, 40, 24),
            "💾",
            callback=self.saveView
        )

        self.w.fitButton = Button(
            (-100, -55, 40, 24),
            "⤢",
            callback=self.fitView
        )

        self.w.closeButton = Button(
            (-50, -55, 40, 24),
            "×",
            callback=self.closeWindow
        )

        self.w.bind("close", self.windowClosed)
        self.w.open()

        Glyphs.addCallback(self.updatePreview, UPDATEINTERFACE)

    # ------------------------------------------------------------
    #   CALLBACKS
    # ------------------------------------------------------------

    def showMasterLinesChanged(self, sender):
        self.view.setShowMasterLines_(sender.get())

    def masterLinesColorChanged(self, sender):
        self.view.setMasterLinesColorHex_(sender.get())

    def showBlueZonesChanged(self, sender):
        self.view.setShowBlueZones_(sender.get())

    def blueZonesColorChanged(self, sender):
        self.view.setBlueZonesColorHex_(sender.get())

    def showLabelsChanged(self, sender):
        self.view.setShowLabels_(sender.get())

    def autoFitChanged(self, sender):
        self.view.setAutoFit_(sender.get())

    def zoomChanged(self, sender):
        self.view.setZoom_(sender.get())
        try:
            self.w.toolbar.autoFit.set(False)
        except:
            pass

    def saveView(self, sender):
        self.view.saveViewState()

    def fitView(self, sender):
        self.view.fitGlyph()
        try:
            self.w.toolbar.autoFit.set(True)
        except:
            pass

    def closeWindow(self, sender):
        self.w.close()

    def updatePreview(self, sender=None):
        self.view.setNeedsDisplay_(True)

    def windowClosed(self, sender):
        self.view.saveViewState()
        try:
            Glyphs.removeCallback(self.updatePreview, UPDATEINTERFACE)
        except:
            pass


# ------------------------------------------------------------
#   RUN
# ------------------------------------------------------------

GlyphPreviewProWindow_v3c()