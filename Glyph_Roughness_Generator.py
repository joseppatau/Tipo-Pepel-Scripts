# Glyph Roughness Generator
# -*- coding: utf-8 -*-
# Description: Apply equidistant nodes and roughness effects to glyphs
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT

__doc__ = """
Apply equidistant nodes and roughness effects to glyphs
"""

from GlyphsApp import *
from vanilla import *
from AppKit import *
from Foundation import NSPoint
import objc
import random

__doc__ = """
Glyph Roughness Generator:
- Preview equidistant nodes + roughness + remove handles.
- Apply effect to current glyph, selected glyphs, or entire font.
"""

def debug_message(message):
    print("[DEBUG]", message)

# Optimized helper functions
def distance_between_points(p1, p2):
    """Calculate distance between two points"""
    if hasattr(p1, "x"):
        x1, y1 = p1.x, p1.y
    else:
        x1, y1 = p1[0], p1[1]
    if hasattr(p2, "x"):
        x2, y2 = p2.x, p2.y
    else:
        x2, y2 = p2[0], p2[1]
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

def identify_segment_type(path, i):
    """Identify the type of segment at given index"""
    nodes = path.nodes
    current_node = nodes[i]
    next_node = nodes[(i + 1) % len(nodes)]
    if current_node.type == GSOFFCURVE:
        return "offcurve"
    if next_node.type == GSOFFCURVE:
        return "curve_start"
    return "line"

def get_curve_points(path, start_index):
    """Get the four points defining a bezier curve"""
    nodes = path.nodes
    count = len(nodes)
    p0 = nodes[start_index].position
    p1 = nodes[(start_index + 1) % count].position
    p2 = nodes[(start_index + 2) % count].position
    p3 = nodes[(start_index + 3) % count].position
    return p0, p1, p2, p3

def bezier_point_at_t(p0, p1, p2, p3, t):
    """Calculate point on bezier curve at parameter t"""
    u = 1 - t
    x = (
        u**3 * p0.x +
        3 * u**2 * t * p1.x +
        3 * u * t**2 * p2.x +
        t**3 * p3.x
    )
    y = (
        u**3 * p0.y +
        3 * u**2 * t * p1.y +
        3 * u * t**2 * p2.y +
        t**3 * p3.y
    )
    return NSPoint(x, y)

def approximate_curve_length(p0, p1, p2, p3, steps=20):
    """Approximate the length of a bezier curve"""
    length = 0.0
    prev = p0
    for s in range(1, steps + 1):
        t = s / float(steps)
        cur = bezier_point_at_t(p0, p1, p2, p3, t)
        length += distance_between_points(prev, cur)
        prev = cur
    return length

def add_equidistant_nodes_mixed(path, spacing):
    """Add equidistant nodes to paths (lines and curves)"""
    if spacing <= 0:
        return 0
        
    total_added = 0
    nodes = list(path.nodes)
    count = len(nodes)
    if count < 2:
        return 0
        
    inserts = []
    
    for i in range(count):
        seg_type = identify_segment_type(path, i)
        current_node = nodes[i]
        next_node = nodes[(i + 1) % count]
        
        if seg_type == "line":
            p0 = current_node.position
            p1 = next_node.position
            seg_len = distance_between_points(p0, p1)
            
            if seg_len <= spacing:
                continue
                
            num = int(seg_len // spacing)
            if num <= 0:
                continue
                
            new_nodes = []
            for k in range(1, num + 1):
                t = float(k) / (num + 1)
                x = p0.x + t * (p1.x - p0.x)
                y = p0.y + t * (p1.y - p0.y)
                n = GSNode()
                n.position = NSPoint(x, y)
                n.type = GSLINE
                new_nodes.append(n)
                
            inserts.append((i + 1, new_nodes))
            total_added += len(new_nodes)
            
        elif seg_type == "curve_start":
            p0, p1, p2, p3 = get_curve_points(path, i)
            seg_len = approximate_curve_length(p0, p1, p2, p3, steps=20)
            
            if seg_len <= spacing:
                continue
                
            num = int(seg_len // spacing)
            if num <= 0:
                continue
                
            new_nodes = []
            for k in range(1, num + 1):
                t = float(k) / (num + 1)
                pos = bezier_point_at_t(p0, p1, p2, p3, t)
                n = GSNode()
                n.position = pos
                n.type = GSCURVE
                new_nodes.append(n)
                
            inserts.append((i + 1, new_nodes))
            total_added += len(new_nodes)
    
    # Apply inserts in reverse order to maintain correct indices
    for insert_index, nodes_to_insert in reversed(inserts):
        for n in reversed(nodes_to_insert):
            path.nodes.insert(insert_index, n)
            
    return total_added

def apply_roughness(path, roughness, mode="random"):
    """Apply roughness effect to path nodes"""
    if roughness <= 0:
        return
        
    nodes = path.nodes
    count = len(nodes)
    if count < 2:
        return
        
    last_sign = None
    
    for i in range(count):
        n = nodes[i]
        if n.type == GSOFFCURVE:
            continue
            
        prev_node = nodes[(i - 1) % count]
        next_node = nodes[(i + 1) % count]
        p = n.position
        p_prev = prev_node.position
        p_next = next_node.position
        
        # Calculate perpendicular direction
        vx = p_next.x - p_prev.x
        vy = p_next.y - p_prev.y
        length = (vx**2 + vy**2) ** 0.5
        if length == 0:
            continue
            
        nx = -vy / length
        ny = vx / length
        
        # Apply displacement
        if mode == "regular":
            if last_sign is None:
                current_sign = 1
            else:
                current_sign = last_sign * -1
            d = roughness * current_sign
            last_sign = current_sign
        else:
            d = (random.random() * 2.0 - 1.0) * roughness
            last_sign = None
            
        new_x = p.x + nx * d
        new_y = p.y + ny * d
        n.position = NSPoint(new_x, new_y)

def remove_all_handles_and_flatten(path):
    """Remove all offcurve points and flatten path"""
    new_nodes = []
    for n in path.nodes:
        if n.type != GSOFFCURVE:
            new_nodes.append(n)
    path.nodes = new_nodes
    for n in path.nodes:
        n.type = GSLINE

def add_equidistant_nodes(layer, spacing, roughness, rough_mode):
    """Main function to process layer with equidistant nodes and roughness"""
    total_added = 0
    for path_index, path in enumerate(layer.paths):
        before = len(path.nodes)
        added = add_equidistant_nodes_mixed(path, spacing)
        if roughness > 0:
            apply_roughness(path, roughness, mode=rough_mode)
        remove_all_handles_and_flatten(path)
        after = len(path.nodes)
        total_added += (after - before)
    return total_added


if 'SimpleGlyphPreviewView' not in globals():
    class SimpleGlyphPreviewView(NSView):
        def initWithFrame_(self, frame):
            self = objc.super(SimpleGlyphPreviewView, self).initWithFrame_(frame)
            if self is None:
                return None
            self.character = "H"
            self.metrics = None
            self._cached = None
            self.previewLayer = None
            self._cachedSourceLayer = None
            return self

        def setCharacter_(self, ch):
            """Set character to preview"""
            self.character = ch if ch and len(ch) else " "
            self._cached = None
            self.previewLayer = None
            self._cachedSourceLayer = None
            self.setNeedsDisplay_(True)

        def setMetrics_(self, metrics):
            """Set font metrics for preview"""
            self.metrics = metrics
            self._cached = None
            self._cachedSourceLayer = None
            self.setNeedsDisplay_(True)

        @objc.python_method
        def _current_master(self):
            """Get current master based on metrics"""
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
            """Find glyph and layer for current character"""
            f = Glyphs.font
            if not f or not self.character:
                return (None, None)
            ch = self.character

            # Try direct glyph access first
            g = f.glyphs[ch] if ch in f.glyphs else None

            # Search by unicode if not found
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

            # Get appropriate layer
            mid = self.metrics.get('masterID') if self.metrics else None
            idx = int(self.metrics.get('masterIndex', 0))

            if mid:
                for lyr in g.layers:
                    if getattr(lyr, 'associatedMasterId', None) == mid or \
                       getattr(lyr, 'masterId', None) == mid:
                        return (g, lyr)

            return (g, g.layers[idx] if 0 <= idx < len(g.layers)
                    else (g.layers[0] if g.layers else None))

        @objc.python_method
        def _build_path(self, layer):
            """Build NSBezierPath from layer data"""
            if not layer:
                return None
                
            # Use cache to avoid rebuilding
            if self._cached and self._cachedSourceLayer is layer:
                return self._cached

            # Try to get existing bezier path
            bez = getattr(layer, 'bezierPath', None)
            if bez and bez.elementCount() > 0:
                self._cached = bez
                self._cachedSourceLayer = layer
                return bez

            # Build path manually
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
                            i += 3
                            continue
                    i += 1
                if getattr(p, "closed", False):
                    path.closePath()

            if path.elementCount() > 0:
                self._cached = path
                self._cachedSourceLayer = layer
                return path
            return None

        @objc.python_method
        def _view_transform(self, master, bounds):
            """Calculate view transformation for proper scaling"""
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

        def drawRect_(self, rect):
            """Main drawing method"""
            # Draw background
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
            """Draw metric lines (ascender, descender, etc.)"""
            scale, baseline, w, h = self._view_transform(master, self.bounds())
            asc = float(master.ascender)
            xh = float(master.xHeight)
            desc = float(master.descender)
            cap = float(getattr(master, 'capHeight', 700))
            gray = NSColor.grayColor().colorWithAlphaComponent_(0.5)

            markers = [
                (baseline + asc*scale, "Asc (%d)" % int(asc)),
                (baseline + cap*scale, "Cap (%d)" % int(cap)),
                (baseline + xh*scale, "xH (%d)" % int(xh)),
                (baseline, "Base (0)"),
                (baseline + desc*scale, "Desc (%d)" % int(desc)),
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
                        NSForegroundColorAttributeName: gray,
                    }
                    s = NSAttributedString.alloc().initWithString_attributes_(label, attrs)
                    s.drawAtPoint_((5, y + 2))

        @objc.python_method
        def _draw_glyph(self, master):
            """Draw the actual glyph"""
            g, layer = self._find_glyph_and_layer()
            if not layer:
                return

            layerToDraw = self.previewLayer if self.previewLayer is not None else layer
            path = self._build_path(layerToDraw)
            if not path:
                return

            scale, baseline, w, h = self._view_transform(master, self.bounds())
            lw = float(getattr(layerToDraw, 'width', 0))
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
            """Draw message when no glyph is available"""
            w = self.bounds.size.width
            h = self.bounds.size.height
            attrs = {
                NSFontAttributeName: NSFont.systemFontOfSize_(12),
                NSForegroundColorAttributeName: NSColor.grayColor(),
            }
            s = NSAttributedString.alloc().initWithString_attributes_(msg, attrs)
            sz = s.size()
            s.drawAtPoint_(((w - sz.width)/2, (h - sz.height)/2))


class NSViewWrapper(VanillaBaseObject):
    """Wrapper for NSView in Vanilla"""
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject


class GlyphRoughnessGenerator(object):
    """Main panel for glyph roughness generation"""
    
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No Font Open", "Please open a font first")
            return

        self.w = Window((650, 730), "Glyph Roughness Generator")

        # Character input
        self.w.charLabel = TextBox((20, 15, 80, 22), "Character:")
        self.w.charInput = EditText((100, 15, 50, 22), "H", callback=self._charChanged)

        # Master selection
        masters = [m.name for m in self.font.masters]
        self.w.masterLabel = TextBox((170, 15, 50, 22), "Master:")
        self.w.masterPopup = PopUpButton((220, 15, 200, 22), masters, callback=self._masterChanged)

        # Spacing controls
        y0 = 50
        self.w.spacingLabel = TextBox((20, y0, 80, 22), "Spacing:")
        self.w.spacingSlider = Slider((100, y0 + 3, 200, 20), minValue=5, maxValue=200, value=50,
                                     callback=self._spacingSliderChanged)
        self.w.spacingEdit = EditText((310, y0, 50, 22), "50", callback=self._spacingEditChanged)

        # Roughness controls
        y1 = y0 + 30
        self.w.roughLabel = TextBox((20, y1, 80, 22), "Roughness:")
        self.w.roughSlider = Slider((100, y1 + 3, 200, 20), minValue=0, maxValue=100, value=10,
                                    callback=self._roughSliderChanged)
        self.w.roughEdit = EditText((310, y1, 50, 22), "10", callback=self._roughEditChanged)

        # Mode selection
        y2 = y1 + 30
        self.w.modeLabel = TextBox((20, y2, 80, 22), "Mode:")
        self.w.modeRadio = RadioGroup((100, y2, 200, 22), ["Regular", "Random"], isVertical=False,
                                     callback=self._modeChanged)
        self.w.modeRadio.set(1)

        # Preview area
        py, ph = y2 + 40, 520
        self.view = SimpleGlyphPreviewView.alloc().initWithFrame_(((0, 0), (598, ph)))
        self.w.preview = NSViewWrapper((20, py, 598, ph), self.view)

        # Action buttons
        y3 = py + ph + 10
        self.w.previewButton = Button((20, y3, 120, 30), "Preview", callback=self._preview)

        applyOptions = ["Previewed Glyph", "Selected Glyphs", "Entire Font"]
        self.w.applyLabel = TextBox((350, y3 + 7, 40, 20), "Apply:")
        self.w.applyPopup = PopUpButton((395, y3, 140, 22), applyOptions)
        self.w.applyButton = Button((545, y3, 100, 30), "Apply", callback=self._apply)

        # Initialize
        self._set_master(0)
        self._charChanged()

        self.w.open()

    def _charChanged(self, sender=None):
        """Handle character input change"""
        ch = self.w.charInput.get().strip()
        self.view.setCharacter_(ch)

    def _masterChanged(self, sender=None):
        """Handle master selection change"""
        idx = self.w.masterPopup.get()
        self._set_master(idx)

    def _spacingSliderChanged(self, sender=None):
        """Handle spacing slider change"""
        value = int(self.w.spacingSlider.get())
        self.w.spacingEdit.set(str(value))

    def _spacingEditChanged(self, sender=None):
        """Handle spacing edit field change"""
        try:
            v = float(self.w.spacingEdit.get().strip())
        except:
            v = 50.0
        v = max(1.0, min(200.0, v))
        self.w.spacingEdit.set(str(int(v)))
        self.w.spacingSlider.set(v)

    def _roughSliderChanged(self, sender=None):
        """Handle roughness slider change"""
        value = int(self.w.roughSlider.get())
        self.w.roughEdit.set(str(value))

    def _roughEditChanged(self, sender=None):
        """Handle roughness edit field change"""
        try:
            v = float(self.w.roughEdit.get().strip())
        except:
            v = 10.0
        v = max(0.0, min(100.0, v))
        self.w.roughEdit.set(str(int(v)))
        self.w.roughSlider.set(v)

    def _modeChanged(self, sender=None):
        """Handle mode radio button change"""
        pass

    def _preview(self, sender=None):
        """Generate preview with current settings"""
        f = self.font
        if not f:
            return
            
        g, layer = self.view._find_glyph_and_layer()
        if not layer:
            return
            
        spacing, roughness, rough_mode = self._getParams()
        
        # Create temporary layer for preview
        tempLayer = layer.copy()
        add_equidistant_nodes(tempLayer, spacing, roughness, rough_mode)
        self.view.previewLayer = tempLayer
        self.view._cached = None
        self.view._cachedSourceLayer = None
        self.view.setNeedsDisplay_(True)

    def _apply(self, sender=None):
        """Apply effects to glyphs based on selection"""
        f = self.font
        if not f:
            return
            
        spacing, roughness, rough_mode = self._getParams()
        targetMode = self.w.applyPopup.get()

        try:
            if targetMode == 0:  # Previewed Glyph
                g, layer = self.view._find_glyph_and_layer()
                if not layer:
                    return
                    
                layer.beginChanges()
                try:
                    add_equidistant_nodes(layer, spacing, roughness, rough_mode)
                finally:
                    layer.endChanges()
                    
            elif targetMode == 1:  # Selected Glyphs
                selectedLayers = list(f.selectedLayers)
                if not selectedLayers:
                    return
                    
                for layer in selectedLayers:
                    if not hasattr(layer, "paths"):
                        continue
                        
                    layer.beginChanges()
                    try:
                        add_equidistant_nodes(layer, spacing, roughness, rough_mode)
                    finally:
                        layer.endChanges()
                        
            else:  # Entire Font
                masterIndex = self.w.masterPopup.get()
                if not (0 <= masterIndex < len(f.masters)):
                    return
                    
                masterID = f.masters[masterIndex].id
                for g in f.glyphs:
                    layer = g.layers[masterID]
                    if not layer or not hasattr(layer, "paths"):
                        continue
                        
                    layer.beginChanges()
                    try:
                        add_equidistant_nodes(layer, spacing, roughness, rough_mode)
                    finally:
                        layer.endChanges()

            # Update display
            if f.currentTab:
                f.currentTab.redraw()

            # Reset preview
            self.view.previewLayer = None
            self.view._cached = None
            self.view._cachedSourceLayer = None
            self.view.setNeedsDisplay_(True)
            
        except Exception as e:
            print(f"Error applying effects: {e}")
            import traceback
            traceback.print_exc()

    @objc.python_method
    def _set_master(self, idx):
        """Set current master and update metrics"""
        try:
            m = self.font.masters[idx]
        except Exception:
            return
            
        metrics = {
            "masterID": m.id,
            "masterIndex": idx,
            "asc": float(m.ascender),
            "desc": float(m.descender),
            "xh": float(m.xHeight),
        }
        self.view.setMetrics_(metrics)

    @objc.python_method
    def _getParams(self):
        """Get current parameter values"""
        try:
            spacing = float(self.w.spacingEdit.get().strip())
        except:
            spacing = 50.0
            self.w.spacingEdit.set("50")
            
        try:
            roughness = float(self.w.roughEdit.get().strip())
        except:
            roughness = 10.0
            self.w.roughEdit.set("10")
            
        if spacing <= 0:
            spacing = 1.0
            self.w.spacingEdit.set("1")
            
        if roughness < 0:
            roughness = 0.0
            self.w.roughEdit.set("0")
            
        mode_idx = self.w.modeRadio.get()
        rough_mode = "regular" if mode_idx == 0 else "random"
        
        return spacing, roughness, rough_mode

# Launch the panel
GlyphRoughnessGenerator()