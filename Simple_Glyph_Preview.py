# Simple Glyph Preview
# -*- coding: utf-8 -*-
# Description: A lightweight and extensible glyph preview panel for GlyphsApp scripts
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

__doc__ = """
A lightweight and extensible glyph preview panel for GlyphsApp scripts
"""


from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc


# ------------------------------------------------------------
#   PROTECTION: define the class only once per session
# ------------------------------------------------------------
if 'SimpleGlyphPreviewView' not in globals():

    class SimpleGlyphPreviewView(NSView):

        # ------------------------------------------------------------
        #   INIT
        # ------------------------------------------------------------
        def initWithFrame_(self, frame):
            self = objc.super(SimpleGlyphPreviewView, self).initWithFrame_(frame)
            if self is None:
                return None
            self.character = "H"
            self.metrics = None
            self._cached = None
            return self

        # ------------------------------------------------------------
        #   PUBLIC SETTERS
        # ------------------------------------------------------------
        def setCharacter_(self, ch):
            self.character = ch if ch and len(ch) else " "
            self._cached = None
            self.setNeedsDisplay_(True)

        def setMetrics_(self, metrics):
            self.metrics = metrics
            self._cached = None
            self.setNeedsDisplay_(True)

        # ------------------------------------------------------------
        #   MASTER, GLYPH AND LAYER LOOKUP
        # ------------------------------------------------------------
        @objc.python_method
        def _current_master(self):
            if not self.metrics:
                return None
            f = Glyphs.font
            if not f or not f.masters:
                return None

            mid = self.metrics.get('masterID')
            idx = int(self.metrics.get('masterIndex', 0))

            if mid:
                for m in f.masters:
                    if m.id == mid:
                        return m

            return f.masters[idx] if 0 <= idx < len(f.masters) else f.masters[0]

        @objc.python_method
        def _find_glyph_and_layer(self):
            f = Glyphs.font
            if not f or not self.character:
                return (None, None)

            ch = self.character

            # Direct lookup by glyph name
            g = f.glyphs[ch] if ch in f.glyphs else None

            # Fallback lookup by unicode value
            if not g:
                for cand in f.glyphs:
                    if cand.unicode:
                        try:
                            if chr(int(cand.unicode, 16)) == ch:
                                g = cand
                                break
                        except Exception:
                            pass

            if not g:
                return (None, None)

            mid = self.metrics.get('masterID') if self.metrics else None
            idx = int(self.metrics.get('masterIndex', 0))

            # Match by masterID
            if mid:
                for lyr in g.layers:
                    if getattr(lyr, 'associatedMasterId', None) == mid or \
                       getattr(lyr, 'masterId', None) == mid:
                        return (g, lyr)

            # Match by index
            return (g, g.layers[idx] if 0 <= idx < len(g.layers)
                    else (g.layers[0] if g.layers else None))

        # ------------------------------------------------------------
        #   BUILD PATH (BEZIER OR MANUAL)
        # ------------------------------------------------------------
        @objc.python_method
        def _build_path(self, layer):
            if not layer:
                return None

            if self._cached:
                return self._cached

            bez = getattr(layer, 'bezierPath', None)
            if bez and bez.elementCount() > 0:
                self._cached = bez
                return bez

            # Manual path reconstruction
            path = NSBezierPath.bezierPath()
            for p in getattr(layer, 'paths', []):
                nodes = list(getattr(p, 'nodes', []))
                if not nodes:
                    continue

                i = 0
                path.moveToPoint_((nodes[0].x, nodes[0].y))

                while i < len(nodes):
                    n = nodes[i]
                    if n.type == GSLINE and i > 0:
                        path.lineToPoint_((n.x, n.y))

                    elif n.type == GSCURVE:
                        if (
                            i + 2 < len(nodes)
                            and nodes[i+1].type == GSOFFCURVE
                            and nodes[i+2].type == GSOFFCURVE
                        ):
                            cp1, cp2 = nodes[i+1], nodes[i+2]
                            end = nodes[i+3] if i + 3 < len(nodes) else n
                            path.curveToPoint_controlPoint1_controlPoint2_(
                                (end.x, end.y),
                                (cp1.x, cp1.y),
                                (cp2.x, cp2.y)
                            )

                    i += 1

                if getattr(p, "closed", False):
                    path.closePath()

            if path.elementCount() > 0:
                self._cached = path
                return path

            return None

        # ------------------------------------------------------------
        #   TRANSFORM CALCULATION (SCALE + BASELINE)
        # ------------------------------------------------------------
        @objc.python_method
        def _view_transform(self, master, bounds):
            w = bounds.size.width
            h = bounds.size.height

            asc = float(master.ascender)
            desc = float(master.descender)

            padding = 20.0
            available_height = max(h - 2 * padding, 1.0)
            total_height = asc - desc if (asc - desc) != 0 else 1.0

            scale = available_height / total_height
            baseline = padding + (-desc * scale)

            return scale, baseline, w, h

        # ------------------------------------------------------------
        #   DRAWING
        # ------------------------------------------------------------
        def drawRect_(self, rect):
            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())
            NSColor.grayColor().set()
            NSBezierPath.strokeRect_(NSInsetRect(self.bounds(), 1, 1))

            if not self.metrics:
                self._draw_message("No metrics available")
                return

            master = self._current_master()
            if not master:
                self._draw_message("No master available")
                return

            self._draw_metrics(master)
            self._draw_glyph(master)

        @objc.python_method
        def _draw_metrics(self, master):
            scale, baseline, w, h = self._view_transform(master, self.bounds())

            asc = float(master.ascender)
            xh  = float(master.xHeight)
            desc = float(master.descender)
            cap = float(getattr(master, 'capHeight', 700))

            gray = NSColor.grayColor().colorWithAlphaComponent_(0.5)
            markers = [
                (baseline + asc*scale,  f"Asc ({int(asc)})"),
                (baseline + cap*scale,  f"Cap ({int(cap)})"),
                (baseline + xh*scale,   f"xH ({int(xh)})"),
                (baseline,              "Base (0)"),
                (baseline + desc*scale, f"Desc ({int(desc)})")
            ]

            for y, label in markers:
                if 0 <= y <= h:
                    gray.set()
                    p = NSBezierPath.bezierPath()
                    p.moveToPoint_((10, y))
                    p.lineToPoint_((w - 10, y))
                    p.stroke()

                    attrs = {
                        NSFontAttributeName: NSFont.systemFontOfSize_(9),
                        NSForegroundColorAttributeName: gray
                    }
                    NSAttributedString.alloc().initWithString_attributes_(
                        label, attrs
                    ).drawAtPoint_((5, y + 2))

        @objc.python_method
        def _draw_glyph(self, master):
            g, layer = self._find_glyph_and_layer()
            if not layer:
                return

            path = self._build_path(layer)
            if not path:
                return

            scale, baseline, w, h = self._view_transform(master, self.bounds())

            lw = float(getattr(layer, 'width', 0))
            xpad = (w - (lw * scale)) / 2.0

            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(xpad, baseline)
            t.scaleXBy_yBy_(scale, scale)

            p = path.copy()
            p.transformUsingAffineTransform_(t)

            NSColor.blackColor().set()
            p.fill()

        @objc.python_method
        def _draw_message(self, msg):
            w = self.bounds().size.width
            h = self.bounds().size.height

            attrs = {
                NSFontAttributeName: NSFont.systemFontOfSize_(12),
                NSForegroundColorAttributeName: NSColor.grayColor()
            }

            s = NSAttributedString.alloc().initWithString_attributes_(msg, attrs)
            sz = s.size()
            s.drawAtPoint_(((w - sz.width)/2, (h - sz.height)/2))


# ------------------------------------------------------------
#   VANILLA WRAPPER
# ------------------------------------------------------------
class NSViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView
    def getNSView(self):
        return self._nsObject


# ------------------------------------------------------------
#   MAIN PANEL
# ------------------------------------------------------------
class SimpleGlyphPreviewPanel(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No Font Open", "Please open a font first")
            return

        self.w = Window((650, 600), "Simple Glyph Preview")

        self.w.charLabel = TextBox((20, 15, 100, 22), "Character:")
        self.w.charInput = EditText((120, 15, 50, 22), "H", callback=self._update)

        masters = [m.name for m in self.font.masters]
        self.w.masterLabel = TextBox((20, 45, 50, 22), "Master:")
        self.w.masterPopup = PopUpButton((70, 45, 200, 22), masters, callback=self._master)

        py, ph = 80, 500
        self.view = SimpleGlyphPreviewView.alloc().initWithFrame_(((0, 0), (598, ph)))
        self.w.preview = NSViewWrapper((20, py, 598, ph), self.view)

        self._set_master(0)
        self.w.open()

    def _update(self, sender=None):
        ch = self.w.charInput.get().strip()
        self.view.setCharacter_(ch)

    def _master(self, sender=None):
        idx = self.w.masterPopup.get()
        self._set_master(idx)

    @objc.python_method
    def _set_master(self, idx):
        try:
            m = self.font.masters[idx]
        except Exception:
            return

        metrics = {
            "masterID": m.id,
            "masterIndex": idx,
            "asc": float(m.ascender),
            "desc": float(m.descender),
            "xh": float(m.xHeight)
        }

        self.view.setMetrics_(metrics)


# ------------------------------------------------------------
#   RUN
# ------------------------------------------------------------
SimpleGlyphPreviewPanel()
