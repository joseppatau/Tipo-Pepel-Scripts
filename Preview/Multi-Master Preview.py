# MenuTitle: Multi-Master Preview
# -*- coding: utf-8 -*-
# Description: Displays the current glyph across all masters side by side for visual comparison.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc


if 'SimpleGlyphPreviewView' not in globals():

    class SimpleGlyphPreviewView(NSView):

        def initWithFrame_(self, frame):

            self = objc.super(SimpleGlyphPreviewView, self).initWithFrame_(frame)
            if self is None:
                return None

            self.glyph_name = None
            self.metrics_list = []
            self.zoom = 0.5
            self._layout = None

            self.on_double_click = None
            self.parent_panel = None

            self.is_dragging = False
            self.drag_start_x = 0
            self.drag_start_y = 0

            self.space_pressed = False

            return self


        def setGlyph_(self, name):

            self.glyph_name = name
            self._layout = None
            self.setNeedsDisplay_(True)


        def setMetricsList_(self, metrics):

            self.metrics_list = metrics
            self._layout = None
            self.setNeedsDisplay_(True)


        def setZoom_(self, zoom):

            self.zoom = zoom
            self._layout = None
            self.setNeedsDisplay_(True)


        def setDoubleClickCallback_(self, callback):

            self.on_double_click = callback


        def setParentPanel_(self, panel):

            self.parent_panel = panel


        @objc.python_method
        def _getMaster(self, masterID):

            f = Glyphs.font

            for m in f.masters:
                if m.id == masterID:
                    return m

            return None


        @objc.python_method
        def _getLayer(self, glyph, masterID):

            for l in glyph.layers:
                if l.associatedMasterId == masterID:
                    return l

            return None


        @objc.python_method
        def _buildLayout(self):

            f = Glyphs.font

            if not f or not self.glyph_name:
                return []

            glyph = f.glyphs[self.glyph_name]

            if not glyph:
                return []

            height = 600   # ALTURA FIJA (evita zoom fantasma)

            x = 40
            padding = 30

            layout = []

            for metrics in self.metrics_list:

                master = self._getMaster(metrics["masterID"])
                if not master:
                    continue

                layer = self._getLayer(glyph, master.id)
                if not layer:
                    continue

                asc = master.ascender
                desc = master.descender
                total_height = asc - desc

                available_height = height - 100
                scale = (available_height / total_height) * self.zoom

                baseline = 80 + (-desc * scale)

                width = layer.width * scale

                rect = NSMakeRect(x - 10, 0, width + 20, height)

                item = {
                    "glyph": glyph.name,
                    "layer": layer,
                    "path": layer.completeBezierPath.copy(),
                    "masterID": master.id,
                    "scale": scale,
                    "baseline": baseline,
                    "x": x,
                    "rect": rect
                }

                layout.append(item)

                x += width + 50

            return layout


        def drawRect_(self, rect):

            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())

            if not self.glyph_name or not self.metrics_list:
                return

            if self._layout is None:
                self._layout = self._buildLayout()

            for item in self._layout:

                path = item["path"].copy()

                t = NSAffineTransform.transform()

                t.translateXBy_yBy_(item["x"], item["baseline"])
                t.scaleXBy_yBy_(item["scale"], item["scale"])

                path.transformUsingAffineTransform_(t)

                NSColor.blackColor().set()
                path.fill()

                NSColor.darkGrayColor().set()
                path.stroke()


        def scrollWheel_(self, event):

            # zoom solo con CMD
            if not (event.modifierFlags() & NSEventModifierFlagCommand):
                objc.super(SimpleGlyphPreviewView, self).scrollWheel_(event)
                return

            delta = event.deltaY()

            zoom_factor = 1.1 if delta > 0 else 0.9

            new_zoom = self.zoom * zoom_factor
            new_zoom = max(0.5, min(3.0, new_zoom))

            if self.parent_panel:
                slider_value = (new_zoom - 0.5) / 2.5
                self.parent_panel.w.zoom.set(slider_value)

            self.setZoom_(new_zoom)

            if self.parent_panel:
                self.parent_panel.updateContentSize()


        def mouseDown_(self, event):

            if event.clickCount() == 2:

                point = self.convertPoint_fromView_(event.locationInWindow(), None)

                if not self._layout:
                    return

                for item in self._layout:

                    if NSPointInRect(point, item["rect"]):

                        if self.on_double_click:
                            self.on_double_click(item["glyph"], item["masterID"])

                        return

            if NSEvent.modifierFlags() & NSEventModifierFlagOption or self.space_pressed:

                self.is_dragging = True
                self.drag_start_x = event.locationInWindow().x
                self.drag_start_y = event.locationInWindow().y
                NSCursor.closedHandCursor().set()


        def mouseDragged_(self, event):

            if not self.is_dragging:
                return

            scroll_view = None
            view = self.superview()

            while view and not scroll_view:
                if hasattr(view, 'documentView'):
                    scroll_view = view
                    break
                view = view.superview()

            if not scroll_view:
                return

            current_x = event.locationInWindow().x
            current_y = event.locationInWindow().y

            delta_x = self.drag_start_x - current_x
            delta_y = self.drag_start_y - current_y

            clip_view = scroll_view.contentView()
            current_bounds = clip_view.bounds()

            new_x = current_bounds.origin.x + delta_x
            new_y = current_bounds.origin.y + delta_y

            clip_view.scrollToPoint_(NSMakePoint(new_x, new_y))
            scroll_view.reflectScrolledClipView_(clip_view)

            self.drag_start_x = current_x
            self.drag_start_y = current_y


        def mouseUp_(self, event):

            self.is_dragging = False
            NSCursor.arrowCursor().set()



class NSViewWrapper(VanillaBaseObject):

    def __init__(self, posSize, view):

        self._posSize = posSize
        self._nsObject = view

    def getNSView(self):
        return self._nsObject



class SimpleGlyphPreviewPanel(object):

    def __init__(self):

        self.font = Glyphs.font

        if not self.font:
            Message("No Font Open", "Open a font first")
            return

        self.w = Window((1900,650), "Glyph Preview")

        self.w.zoom = Slider(
            (20,10,680,20),
            value=0.0,
            minValue=0.0,
            maxValue=1.0,
            callback=self.zoom
        )

        self.w.reset_button = Button(
            (720, 8, 160, 23),
            "Reset View",
            callback=self.resetView
        )

        height = 560

        self.scroll = NSScrollView.alloc().initWithFrame_(((0,0),(860,height)))

        self.scroll.setHasHorizontalScroller_(True)
        self.scroll.setHasVerticalScroller_(True)

        self.view = SimpleGlyphPreviewView.alloc().initWithFrame_(((0,0),(2000, height)))

        self.view.setDoubleClickCallback_(self.openGlyph)
        self.view.setParentPanel_(self)

        self.scroll.setDocumentView_(self.view)

        self.w.preview = NSViewWrapper((20,60,1860,height), self.scroll)

        Glyphs.addCallback(self.liveUpdate, UPDATEINTERFACE)

        self.updateMetrics()
        self.liveUpdate()

        self.w.open()


    def zoom(self, sender):

        slider_value = sender.get()

        zoom_value = 0.5 + (slider_value * 2.5)

        self.view.setZoom_(zoom_value)

        self.updateContentSize()


    def resetView(self, sender):

        self.w.zoom.set(0.0)

        self.view.setZoom_(0.5)

        self.updateContentSize()

        clip_view = self.scroll.contentView()

        clip_view.scrollToPoint_(NSMakePoint(0,0))

        self.scroll.reflectScrolledClipView_(clip_view)


    def liveUpdate(self, sender=None):

        f = Glyphs.font

        if not f:
            return

        layers = f.selectedLayers

        if not layers:
            return

        glyph = layers[0].parent

        if self.view.glyph_name != glyph.name:

            self.view.setGlyph_(glyph.name)

            self.updateContentSize()

        self.view._layout = None
        self.view.setNeedsDisplay_(True)


    def updateContentSize(self):

        self.view._layout = None

        layout = self.view._buildLayout()

        if not layout:
            return

        last_item = layout[-1]

        last_layer = last_item["layer"]

        asc = self._getMaster(last_item["masterID"]).ascender
        desc = self._getMaster(last_item["masterID"]).descender

        height = 600

        total_height = asc - desc

        available_height = height - 100

        scale = (available_height / total_height) * self.view.zoom

        last_width = last_layer.width * scale

        total_width = last_item["x"] + last_width + 100

        scroll_width = self.scroll.contentView().bounds().size.width

        new_width = max(total_width, scroll_width)

        self.view.setFrameSize_((new_width, height))


    def _getMaster(self, masterID):

        for m in Glyphs.font.masters:

            if m.id == masterID:
                return m

        return None


    def updateMetrics(self):

        metrics = []

        for i, m in enumerate(self.font.masters):

            metrics.append({
                "masterID": m.id,
                "masterIndex": i
            })

        self.view.setMetricsList_(metrics)


    def openGlyph(self, glyphName, masterID):

        f = Glyphs.font

        glyph = f.glyphs[glyphName]

        for layer in glyph.layers:

            if layer.associatedMasterId == masterID:

                f.newTab([layer])

                return


SimpleGlyphPreviewPanel()