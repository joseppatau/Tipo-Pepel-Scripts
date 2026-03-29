# MenuTitle: Glyph Preview Window
# -*- coding: utf-8 -*-
# Description: A detached, real-time preview window that mirrors the current glyph with zoom, pan, and persistent view settings.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc

# ------------------------------------------------------------
#   GLOBAL DEFAULT KEYS
# ------------------------------------------------------------

ZOOM_KEY = "com.joseppatau.preview.zoom"
OFFSET_X_KEY = "com.joseppatau.preview.offsetX"
OFFSET_Y_KEY = "com.joseppatau.preview.offsetY"


# ------------------------------------------------------------
#   PREVIEW VIEW
# ------------------------------------------------------------

if "AdvancedGlyphPreviewStable" not in globals():

    class AdvancedGlyphPreviewStable(NSView):

        def initWithFrame_(self, frame):
            self = objc.super(AdvancedGlyphPreviewStable, self).initWithFrame_(frame)
            if self is None:
                return None

            self.zoom = Glyphs.defaults.get(ZOOM_KEY, 1.0)
            ox = Glyphs.defaults.get(OFFSET_X_KEY, 0.0)
            oy = Glyphs.defaults.get(OFFSET_Y_KEY, 0.0)

            self.offset = NSPoint(ox, oy)
            self.lastDrag = None

            return self

        # ------------------------------------------------------------
        #   CURRENT LAYER (Edit View or Font View)
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
        #   SAVE STATE (GLOBAL)
        # ------------------------------------------------------------

        @objc.python_method
        def saveViewState(self):
            Glyphs.defaults[ZOOM_KEY] = self.zoom
            Glyphs.defaults[OFFSET_X_KEY] = self.offset.x
            Glyphs.defaults[OFFSET_Y_KEY] = self.offset.y

        # ------------------------------------------------------------
        #   FIT
        # ------------------------------------------------------------

        @objc.python_method
        def fitGlyph(self):
            layer = self.currentLayer()
            if not layer:
                return

            bounds = layer.bounds
            if bounds.size.width == 0 or bounds.size.height == 0:
                return

            viewBounds = self.bounds()

            scaleX = viewBounds.size.width / bounds.size.width
            scaleY = viewBounds.size.height / bounds.size.height

            self.zoom = min(scaleX, scaleY) * 0.95
            self.offset = NSPoint(0, 0)
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   ZOOM
        # ------------------------------------------------------------

        def setZoom_(self, value):
            self.zoom = max(0.05, value)
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   MOUSE EVENTS
        # ------------------------------------------------------------

        def mouseDown_(self, event):
            if event.clickCount() == 2:
                self.fitGlyph()
                return
            self.lastDrag = event.locationInWindow()

        def mouseDragged_(self, event):
            if not self.lastDrag:
                return

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
            delta = event.deltaY() * 0.05
            self.zoom += delta
            self.zoom = max(0.05, self.zoom)
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   DRAW
        # ------------------------------------------------------------

        def drawRect_(self, rect):

            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())

            layer = self.currentLayer()
            if not layer:
                return

            path = layer.completeBezierPath  # includes components
            if not path:
                return

            viewBounds = self.bounds()
            viewW = viewBounds.size.width
            viewH = viewBounds.size.height

            glyphBounds = layer.bounds
            if glyphBounds.size.width == 0 or glyphBounds.size.height == 0:
                return

            glyphW = glyphBounds.size.width
            glyphH = glyphBounds.size.height

            baseScale = min(viewW / glyphW, viewH / glyphH)
            scale = baseScale * self.zoom

            tx = -glyphBounds.origin.x * scale
            ty = -glyphBounds.origin.y * scale

            extraX = (viewW - glyphW * scale) / 2.0
            extraY = (viewH - glyphH * scale) / 2.0

            transform = NSAffineTransform.transform()
            transform.translateXBy_yBy_(tx + extraX + self.offset.x,
                                        ty + extraY + self.offset.y)
            transform.scaleXBy_yBy_(scale, scale)

            p = path.copy()
            p.transformUsingAffineTransform_(transform)

            NSColor.blackColor().set()
            p.fill()


# ------------------------------------------------------------
#   WRAPPER
# ------------------------------------------------------------

class NSViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject


# ------------------------------------------------------------
#   WINDOW
# ------------------------------------------------------------

class AdvancedPreviewWindowStable(object):

    def __init__(self):

        if not Glyphs.font:
            Message("No Font Open", "Open a font first.")
            return

        self.w = Window(
            (1060, 1850),
            "Advanced Glyph Preview STABLE",
            minSize=(1060, 1850)
        )

        self.view = AdvancedGlyphPreviewStable.alloc().initWithFrame_(((0, 0), (100, 100)))
        self.w.preview = NSViewWrapper((20, 20, -20, -90), self.view)

        self.w.zoomSlider = Slider(
            (20, -55, -120, 20),
            minValue=0.1,
            maxValue=5.0,
            value=self.view.zoom,
            callback=self.zoomChanged
        )

        self.w.saveButton = Button(
            (-100, -58, 40, 24),
            "💾",
            callback=self.saveView
        )

        self.w.fitButton = Button(
            (-50, -58, 40, 24),
            "⤢",
            callback=self.fitView
        )

        self.w.bind("close", self.windowClosed)
        self.w.open()

        Glyphs.addCallback(self.updatePreview, UPDATEINTERFACE)

    def zoomChanged(self, sender):
        self.view.setZoom_(sender.get())

    def saveView(self, sender):
        self.view.saveViewState()

    def fitView(self, sender):
        self.view.fitGlyph()

    def updatePreview(self, sender=None):
        self.view.setNeedsDisplay_(True)

    def windowClosed(self, sender):
        self.view.saveViewState()
        Glyphs.removeCallback(self.updatePreview, UPDATEINTERFACE)


# ------------------------------------------------------------
#   RUN
# ------------------------------------------------------------

AdvancedPreviewWindowStable()