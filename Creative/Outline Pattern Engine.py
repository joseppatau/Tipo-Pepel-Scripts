# MenuTitle: Outline Pattern Engine
# -*- coding: utf-8 -*-
# Description: Generates dotted or glyph-based patterns along glyph outlines with adaptive spacing and size control.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
# Description: Create dotted outlines with circles or custom glyphs on glyph contours (OPTIMIZED)
# Author: Modified based on Glyph Roughness Generator
# License: MIT

__doc__ = """
Create dotted outlines with circles or custom glyphs on glyph contours
"""

from GlyphsApp import *
from vanilla import *
from AppKit import *
from Foundation import NSPoint
import objc
import math
import random
import traceback
import time
from collections import defaultdict

# Cache para longitudes de curva calculadas
_curve_length_cache = {}

def debug_message(msg):
    """Print debug message with timestamp"""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def debug_error(msg):
    """Print error message with traceback"""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {msg}")
    traceback.print_exc()

# Helper functions for working with paths
def distance_between_points(p1, p2):
    """Calculate distance between two points"""
    try:
        if hasattr(p1, "x"):
            x1, y1 = p1.x, p1.y
        else:
            x1, y1 = p1[0], p1[1]
        if hasattr(p2, "x"):
            x2, y2 = p2.x, p2.y
        else:
            x2, y2 = p2[0], p2[1]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    except Exception as e:
        debug_error(f"Error in distance_between_points: {e}")
        return 0

def identify_segment_type(path, i):
    """Identify the type of segment at given index"""
    try:
        nodes = path.nodes
        current_node = nodes[i]
        next_node = nodes[(i + 1) % len(nodes)]
        if current_node.type == GSOFFCURVE:
            return "offcurve"
        if next_node.type == GSOFFCURVE:
            return "curve_start"
        return "line"
    except Exception as e:
        debug_error(f"Error in identify_segment_type: {e}")
        return "unknown"

def get_curve_points(path, start_index):
    """Get the four points defining a bezier curve"""
    try:
        nodes = path.nodes
        count = len(nodes)
        p0 = nodes[start_index].position
        p1 = nodes[(start_index + 1) % count].position
        p2 = nodes[(start_index + 2) % count].position
        p3 = nodes[(start_index + 3) % count].position
        return p0, p1, p2, p3
    except Exception as e:
        debug_error(f"Error in get_curve_points: {e}")
        return None, None, None, None

def bezier_point_at_t(p0, p1, p2, p3, t):
    """Calculate point on bezier curve at parameter t (optimized)"""
    try:
        u = 1 - t
        u2 = u * u
        u3 = u2 * u
        t2 = t * t
        t3 = t2 * t
        
        x = u3 * p0.x + 3 * u2 * t * p1.x + 3 * u * t2 * p2.x + t3 * p3.x
        y = u3 * p0.y + 3 * u2 * t * p1.y + 3 * u * t2 * p2.y + t3 * p3.y
        return NSPoint(x, y)
    except Exception as e:
        debug_error(f"Error in bezier_point_at_t: {e}")
        return NSPoint(0, 0)

def approximate_curve_length(p0, p1, p2, p3, steps=10):
    """Approximate the length of a bezier curve (optimized with fewer steps)"""
    try:
        # Usar caché para evitar recalcular la misma curva
        cache_key = (p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
        if cache_key in _curve_length_cache:
            return _curve_length_cache[cache_key]
        
        length = 0.0
        prev_x, prev_y = p0.x, p0.y
        
        for s in range(1, steps + 1):
            t = s / float(steps)
            cur = bezier_point_at_t(p0, p1, p2, p3, t)
            length += math.hypot(cur.x - prev_x, cur.y - prev_y)
            prev_x, prev_y = cur.x, cur.y
        
        _curve_length_cache[cache_key] = length
        return length
    except Exception as e:
        debug_error(f"Error in approximate_curve_length: {e}")
        return 0

def parse_irregular_values(text, default):
    """Parse comma-separated values for irregular spacing/diameter"""
    if not text or not text.strip():
        return [float(default)]
    try:
        # Reemplazar comas decimales por puntos y parsear
        values = []
        for x in text.split(','):
            x = x.strip().replace(',', '.')
            if x:
                values.append(float(x))
        if values:
            return values
        else:
            return [float(default)]
    except Exception as e:
        debug_error(f"Error parsing irregular values '{text}': {e}")
        return [float(default)]

def parse_glyph_list(text):
    """Parse comma-separated list of glyph names"""
    if not text or not text.strip():
        return []
    try:
        glyphs = [x.strip() for x in text.split(',') if x.strip()]
        return glyphs
    except Exception as e:
        debug_error(f"Error parsing glyph list: {e}")
        return []

def rotate_point(x, y, center_x, center_y, angle_degrees):
    """Rotate a point around a center by given angle in degrees"""
    try:
        angle = math.radians(angle_degrees)
        x_rel = x - center_x
        y_rel = y - center_y
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x_rot = x_rel * cos_a - y_rel * sin_a
        y_rot = x_rel * sin_a + y_rel * cos_a
        return x_rot + center_x, y_rot + center_y
    except Exception as e:
        debug_error(f"Error in rotate_point: {e}")
        return x, y

def create_circle_path(center_x, center_y, diameter):
    """Create a circle path at specified center with given diameter (optimized)"""
    try:
        if diameter <= 0:
            return None
            
        r = diameter / 2.0
        k = 0.55228 * r
        
        circle_path = GSPath()
        
        # Crear todos los nodos de una vez
        positions = [
            (center_x + r, center_y, GSCURVE),  # start
            (center_x + r, center_y + k, GSOFFCURVE),
            (center_x + k, center_y + r, GSOFFCURVE),
            (center_x, center_y + r, GSCURVE),
            (center_x - k, center_y + r, GSOFFCURVE),
            (center_x - r, center_y + k, GSOFFCURVE),
            (center_x - r, center_y, GSCURVE),
            (center_x - r, center_y - k, GSOFFCURVE),
            (center_x - k, center_y - r, GSOFFCURVE),
            (center_x, center_y - r, GSCURVE),
            (center_x + k, center_y - r, GSOFFCURVE),
            (center_x + r, center_y - k, GSOFFCURVE),
            (center_x + r, center_y, GSCURVE),  # back to start
        ]
        
        for x, y, node_type in positions:
            node = GSNode()
            node.position = NSPoint(x, y)
            node.type = node_type
            circle_path.nodes.append(node)
        
        circle_path.closed = True
        return circle_path
    except Exception as e:
        debug_error(f"Error creating circle path: {e}")
        return None

def transform_glyph_to_size(glyph_layer, target_width, target_height, rotation=0):
    """Transform a glyph to fit within target dimensions and rotate if needed (optimized)"""
    try:
        if not glyph_layer or not glyph_layer.paths:
            return None
        
        # Calculate bounds of the glyph
        bounds = None
        for path in glyph_layer.paths:
            for node in path.nodes:
                if bounds is None:
                    bounds = [node.x, node.y, node.x, node.y]
                else:
                    if node.x < bounds[0]: bounds[0] = node.x
                    if node.y < bounds[1]: bounds[1] = node.y
                    if node.x > bounds[2]: bounds[2] = node.x
                    if node.y > bounds[3]: bounds[3] = node.y
        
        if not bounds:
            return None
        
        current_width = bounds[2] - bounds[0]
        current_height = bounds[3] - bounds[1]
        
        if current_width <= 0 or current_height <= 0:
            return None
        
        scale = min(target_width / current_width, target_height / current_height)
        center_x = (bounds[0] + bounds[2]) * 0.5
        center_y = (bounds[1] + bounds[3]) * 0.5
        
        # Pre-calculate rotation matrix if needed
        if rotation != 0:
            angle = math.radians(rotation)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
        
        transformed_layer = GSLayer()
        
        for path in glyph_layer.paths:
            new_path = GSPath()
            for node in path.nodes:
                new_node = GSNode()
                # Translate to center and scale
                new_x = (node.x - center_x) * scale
                new_y = (node.y - center_y) * scale
                
                # Apply rotation if needed
                if rotation != 0:
                    x_rot = new_x * cos_a - new_y * sin_a
                    y_rot = new_x * sin_a + new_y * cos_a
                    new_x, new_y = x_rot, y_rot
                
                new_node.position = NSPoint(new_x, new_y)
                new_node.type = node.type
                new_path.nodes.append(new_node)
            new_path.closed = path.closed
            transformed_layer.paths.append(new_path)
        
        return transformed_layer
    except Exception as e:
        debug_error(f"Error transforming glyph: {e}")
        return None

def place_glyph_at_point(target_layer, glyph_layer, center_x, center_y):
    """Place a transformed glyph at the specified center point (optimized)"""
    try:
        if not glyph_layer or not glyph_layer.paths:
            return
        
        for path in glyph_layer.paths:
            new_path = GSPath()
            for node in path.nodes:
                new_node = GSNode()
                new_node.position = NSPoint(node.x + center_x, node.y + center_y)
                new_node.type = node.type
                new_path.nodes.append(new_node)
            new_path.closed = path.closed
            target_layer.paths.append(new_path)
    except Exception as e:
        debug_error(f"Error placing glyph at point: {e}")

def calculate_path_length(path):
    """Calculate total length of a path (optimized)"""
    try:
        nodes = list(path.nodes)
        count = len(nodes)
        
        if count < 2:
            return 0
            
        total_length = 0.0
        i = 0
        
        while i < count:
            node_type = identify_segment_type(path, i)
            
            if node_type == "line":
                p0 = nodes[i].position
                p1 = nodes[(i + 1) % count].position
                total_length += math.hypot(p1.x - p0.x, p1.y - p0.y)
                i += 1
            elif node_type == "curve_start":
                p0, p1, p2, p3 = get_curve_points(path, i)
                if p0 and p1 and p2 and p3:
                    total_length += approximate_curve_length(p0, p1, p2, p3, steps=8)
                i += 3
            else:
                i += 1
                
        return total_length
    except Exception as e:
        debug_error(f"Error calculating path length: {e}")
        return 0

def get_point_at_distance(path, target_distance):
    """Get point on path at specified distance from start (optimized)"""
    try:
        nodes = list(path.nodes)
        count = len(nodes)
        
        if count < 2 or target_distance < 0:
            return None
            
        accumulated = 0.0
        i = 0
        
        while i < count:
            node_type = identify_segment_type(path, i)
            
            if node_type == "line":
                p0 = nodes[i].position
                p1 = nodes[(i + 1) % count].position
                seg_len = math.hypot(p1.x - p0.x, p1.y - p0.y)
                
                if accumulated + seg_len >= target_distance:
                    t = (target_distance - accumulated) / seg_len if seg_len > 0 else 0
                    x = p0.x + t * (p1.x - p0.x)
                    y = p0.y + t * (p1.y - p0.y)
                    return NSPoint(x, y)
                
                accumulated += seg_len
                i += 1
                
            elif node_type == "curve_start":
                p0, p1, p2, p3 = get_curve_points(path, i)
                if p0 and p1 and p2 and p3:
                    seg_len = approximate_curve_length(p0, p1, p2, p3, steps=8)
                    
                    if accumulated + seg_len >= target_distance:
                        t = (target_distance - accumulated) / seg_len if seg_len > 0 else 0
                        return bezier_point_at_t(p0, p1, p2, p3, t)
                    
                    accumulated += seg_len
                i += 3
            else:
                i += 1
                
        return None
    except Exception as e:
        debug_error(f"Error getting point at distance: {e}")
        return None

def create_dotted_outline(layer, spacing_values, diameter_values, use_glyph=False, glyph_names=None, rotation_mode="none", rotation_value=0):
    """Create a new layer with dotted outline (circles or glyphs at irregular intervals) - OPTIMIZED"""
    
    if not spacing_values or not diameter_values or not layer or not hasattr(layer, 'paths'):
        return None
    
    # Parse glyph list if needed
    glyph_list = []
    if use_glyph and glyph_names:
        glyph_list = parse_glyph_list(glyph_names)
        if not glyph_list:
            return None

    # Clear cache for this run
    _curve_length_cache.clear()
    
    # Create new layer for the dotted outline
    try:
        dotted_layer = GSLayer()
        dotted_layer.width = layer.width
    except Exception as e:
        debug_error(f"Error creating dotted layer: {e}")
        return None

    total_elements = 0
    spacing_index = 0
    diameter_index = 0
    glyph_index = 0
    element_count = 0
    
    # Pre-calculate path lengths and points for all paths
    for path in layer.paths:
        try:
            total_length = calculate_path_length(path)
            if total_length == 0:
                continue
            
            # Pre-calculate all points on this path
            points_on_contour = []
            current_pos = 0.0
            
            while current_pos < total_length:
                spacing = spacing_values[spacing_index % len(spacing_values)]
                point = get_point_at_distance(path, current_pos)
                if point:
                    points_on_contour.append(point)
                current_pos += spacing
                spacing_index += 1
                
                if spacing_index > 10000:  # Safety limit
                    break
            
            # Create elements at each point
            for point in points_on_contour:
                diameter = diameter_values[diameter_index % len(diameter_values)]
                diameter_index += 1
                
                # Calculate rotation
                rotation = 0
                if rotation_mode == "random":
                    rotation = random.uniform(-rotation_value, rotation_value)
                elif rotation_mode == "progressive":
                    rotation = (element_count * rotation_value) % 360
                
                if use_glyph and glyph_list:
                    glyph_name = glyph_list[glyph_index % len(glyph_list)]
                    glyph_index += 1
                    
                    try:
                        font = Glyphs.font
                        if font and glyph_name in font.glyphs:
                            glyph = font.glyphs[glyph_name]
                            master_id = layer.associatedMasterId
                            if master_id and master_id in glyph.layers:
                                glyph_layer = glyph.layers[master_id]
                            else:
                                glyph_layer = glyph.layers[0] if glyph.layers else None
                            
                            if glyph_layer:
                                transformed = transform_glyph_to_size(glyph_layer, diameter, diameter, rotation)
                                if transformed:
                                    place_glyph_at_point(dotted_layer, transformed, point.x, point.y)
                                    total_elements += 1
                                    element_count += 1
                    except:
                        pass
                else:
                    circle_path = create_circle_path(point.x, point.y, diameter)
                    if circle_path:
                        dotted_layer.paths.append(circle_path)
                        total_elements += 1
                        element_count += 1
                        
        except Exception as e:
            debug_error(f"Error processing path: {e}")
            continue
    
    return dotted_layer if total_elements > 0 else None


if 'SimpleGlyphPreviewView' not in globals():
    class SimpleGlyphPreviewView(NSView):
        def initWithFrame_(self, frame):
            try:
                self = objc.super(SimpleGlyphPreviewView, self).initWithFrame_(frame)
                if self is None:
                    return None
                self.character = "H"
                self.metrics = None
                self._cached = None
                self.previewLayer = None
                self._cachedSourceLayer = None
                return self
            except Exception as e:
                debug_error(f"Error in initWithFrame: {e}")
                return None

        def setCharacter_(self, ch):
            try:
                self.character = ch if ch and len(ch) else " "
                self._cached = None
                self.previewLayer = None
                self._cachedSourceLayer = None
                self.setNeedsDisplay_(True)
            except Exception as e:
                debug_error(f"Error in setCharacter_: {e}")

        def setMetrics_(self, metrics):
            try:
                self.metrics = metrics
                self._cached = None
                self._cachedSourceLayer = None
                self.setNeedsDisplay_(True)
            except Exception as e:
                debug_error(f"Error in setMetrics_: {e}")

        @objc.python_method
        def _current_master(self):
            try:
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
            except Exception as e:
                debug_error(f"Error in _current_master: {e}")
                return None

        @objc.python_method
        def _find_glyph_and_layer(self):
            try:
                f = Glyphs.font
                if not f or not self.character:
                    return (None, None)
                ch = self.character

                g = f.glyphs[ch] if ch in f.glyphs else None
                if not g:
                    for cand in f.glyphs:
                        if cand.unicode:
                            try:
                                if chr(int(cand.unicode, 16)) == ch:
                                    g = cand
                                    break
                            except:
                                pass

                if not g:
                    return (None, None)

                mid = self.metrics.get('masterID') if self.metrics else None
                idx = int(self.metrics.get('masterIndex', 0))

                if mid:
                    for lyr in g.layers:
                        if getattr(lyr, 'associatedMasterId', None) == mid or \
                           getattr(lyr, 'masterId', None) == mid:
                            return (g, lyr)

                layer = g.layers[idx] if 0 <= idx < len(g.layers) else (g.layers[0] if g.layers else None)
                return (g, layer)
            except Exception as e:
                debug_error(f"Error in _find_glyph_and_layer: {e}")
                return (None, None)

        @objc.python_method
        def _build_path(self, layer):
            try:
                if not layer:
                    return None
                    
                if self._cached and self._cachedSourceLayer is layer:
                    return self._cached

                bez = getattr(layer, 'bezierPath', None)
                if bez and bez.elementCount() > 0:
                    self._cached = bez
                    self._cachedSourceLayer = layer
                    return bez

                path = NSBezierPath.bezierPath()
                for p in getattr(layer, 'paths', []):
                    nodes = list(getattr(p, 'nodes', []))
                    if not nodes:
                        continue
                        
                    path.moveToPoint_((nodes[0].x, nodes[0].y))
                    i = 1
                    while i < len(nodes):
                        n = nodes[i]
                        if n.type == GSLINE:
                            path.lineToPoint_((n.x, n.y))
                            i += 1
                        elif n.type == GSOFFCURVE and i + 2 < len(nodes):
                            cp1 = n
                            cp2 = nodes[i+1]
                            end = nodes[i+2]
                            path.curveToPoint_controlPoint1_controlPoint2_(
                                (end.x, end.y), (cp1.x, cp1.y), (cp2.x, cp2.y)
                            )
                            i += 3
                        else:
                            i += 1
                            
                    if getattr(p, "closed", False):
                        path.closePath()

                if path.elementCount() > 0:
                    self._cached = path
                    self._cachedSourceLayer = layer
                    return path
                
                return None
            except Exception as e:
                debug_error(f"Error in _build_path: {e}")
                return None

        @objc.python_method
        def _view_transform(self, master, bounds):
            try:
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
            except Exception as e:
                debug_error(f"Error in _view_transform: {e}")
                return 1.0, 0, 0, 0

        def drawRect_(self, rect):
            try:
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
            except Exception as e:
                debug_error(f"Error in drawRect_: {e}")

        @objc.python_method
        def _draw_metrics(self, master):
            try:
                scale, baseline, w, h = self._view_transform(master, self.bounds())
                asc = float(master.ascender)
                xh = float(master.xHeight)
                desc = float(master.descender)
                cap = float(getattr(master, 'capHeight', 700))
                gray = NSColor.grayColor().colorWithAlphaComponent_(0.5)

                markers = [
                    (baseline + asc*scale, f"Asc ({int(asc)})"),
                    (baseline + cap*scale, f"Cap ({int(cap)})"),
                    (baseline + xh*scale, f"xH ({int(xh)})"),
                    (baseline, "Base (0)"),
                    (baseline + desc*scale, f"Desc ({int(desc)})"),
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
            except Exception as e:
                debug_error(f"Error in _draw_metrics: {e}")

        @objc.python_method
        def _draw_glyph(self, master):
            try:
                g, layer = self._find_glyph_and_layer()
                if not layer:
                    self._draw_message("No glyph found")
                    return

                layerToDraw = self.previewLayer if self.previewLayer is not None else layer
                path = self._build_path(layerToDraw)
                if not path:
                    self._draw_message("No path to draw")
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
                p.setLineWidth_(1.0)
                p.stroke()
            except Exception as e:
                debug_error(f"Error in _draw_glyph: {e}")

        @objc.python_method
        def _draw_message(self, msg):
            try:
                w = self.bounds.size.width
                h = self.bounds.size.height
                attrs = {
                    NSFontAttributeName: NSFont.systemFontOfSize_(12),
                    NSForegroundColorAttributeName: NSColor.grayColor(),
                }
                s = NSAttributedString.alloc().initWithString_attributes_(msg, attrs)
                sz = s.size()
                s.drawAtPoint_(((w - sz.width)/2, (h - sz.height)/2))
            except Exception as e:
                debug_error(f"Error in _draw_message: {e}")


class NSViewWrapper(VanillaBaseObject):
    """Wrapper for NSView in Vanilla"""
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject


class GlyphDottedOutlineGenerator(object):
    """Main panel for glyph dotted outline generation"""
    
    def __init__(self):
        debug_message("=== Initializing GlyphDottedOutlineGenerator TURBO ===")
        try:
            self.font = Glyphs.font
            if not self.font:
                Message("No Font Open", "Please open a font first")
                return

            self.w = Window((650, 900), "Glyph Dotted Outline Generator TURBO")

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
            self.w.spacingEdit = EditText((100, y0, 80, 22), "46.0", callback=self._spacingEditChanged)
            
            # Irregular spacing checkbox and input
            y0_5 = y0 + 25
            self.w.irregularSpacingCheckbox = CheckBox((20, y0_5, 150, 22), "Irregular spacing (comma separated)", 
                                                       callback=self._toggleIrregularSpacing)
            self.w.irregularSpacingInput = EditText((180, y0_5, 180, 22), "50.5, 15.2, 15.2, 15.2", 
                                                    callback=self._irregularSpacingChanged)
            self.w.irregularSpacingInput.enable(False)

            # Element size controls
            y1 = y0_5 + 30
            self.w.diameterLabel = TextBox((20, y1, 100, 22), "Element size:")
            self.w.diameterEdit = EditText((120, y1, 80, 22), "46.0", callback=self._diameterEditChanged)
            
            # Irregular diameter checkbox and input
            y1_5 = y1 + 25
            self.w.irregularDiameterCheckbox = CheckBox((20, y1_5, 150, 22), "Irregular Diameter (comma separated)", 
                                                        callback=self._toggleIrregularDiameter)
            self.w.irregularDiameterInput = EditText((180, y1_5, 180, 22), "12.5, 32.0", 
                                                     callback=self._irregularDiameterChanged)
            self.w.irregularDiameterInput.enable(False)

            # Use glyph checkbox and multiple glyph input
            y2 = y1_5 + 30
            self.w.useGlyphCheckbox = CheckBox((20, y2, 120, 22), "Use glyph(s):", callback=self._toggleGlyphInput)
            self.w.glyphNameInput = EditText((140, y2, 220, 22), "_star, _circle, _triangle", callback=self._glyphNameChanged)
            
            # Rotation controls
            y2_5 = y2 + 30
            self.w.rotationLabel = TextBox((20, y2_5, 80, 22), "Rotation:")
            
            # Radio buttons for rotation mode
            self.w.rotationNone = RadioButton((100, y2_5, 60, 22), "None", value=0, 
                                              callback=self._rotationModeChanged, sizeStyle="small")
            self.w.rotationRandom = RadioButton((170, y2_5, 70, 22), "Random", value=1, 
                                                callback=self._rotationModeChanged, sizeStyle="small")
            self.w.rotationProgressive = RadioButton((250, y2_5, 90, 22), "Progressive", value=2, 
                                                     callback=self._rotationModeChanged, sizeStyle="small")
            
            # Rotation value input
            self.w.rotationValueLabel = TextBox((350, y2_5, 40, 22), "°:")
            self.w.rotationValue = EditText((380, y2_5, 50, 22), "15.0", callback=self._rotationValueChanged)
            
            # Preview area
            py, ph = y2_5 + 30, 450
            self.view = SimpleGlyphPreviewView.alloc().initWithFrame_(((0, 0), (598, ph)))
            self.w.preview = NSViewWrapper((20, py, 598, ph), self.view)

            # Action buttons
            y3 = py + ph + 10
            self.w.previewButton = Button((20, y3, 120, 30), "Preview", callback=self._preview)

            applyOptions = ["Previewed Glyph", "Selected Glyphs", "Entire Font"]
            self.w.applyLabel = TextBox((350, y3 + 7, 40, 20), "Apply:")
            self.w.applyPopup = PopUpButton((395, y3, 140, 22), applyOptions)
            self.w.applyButton = Button((545, y3, 100, 30), "Apply", callback=self._apply)

            # Metric lines labels (for reference)
            y4 = y3 + 40
            self.w.metricsLabel = TextBox((20, y4, 600, 20), 
                "Asc (800)   Cap (700)   xH (580)   Base (0)   Desc (-200)")

            # Initialize
            self.w.glyphNameInput.enable(False)
            self.w.rotationNone.set(True)
            self._rotation_mode = "none"
            self._set_master(0)
            self._charChanged()

            debug_message("Opening window...")
            self.w.open()
            
        except Exception as e:
            debug_error(f"Error in __init__: {e}")

    def _toggleIrregularSpacing(self, sender=None):
        enabled = self.w.irregularSpacingCheckbox.get()
        self.w.irregularSpacingInput.enable(enabled)
        self.w.spacingEdit.enable(not enabled)

    def _irregularSpacingChanged(self, sender=None):
        pass

    def _toggleIrregularDiameter(self, sender=None):
        enabled = self.w.irregularDiameterCheckbox.get()
        self.w.irregularDiameterInput.enable(enabled)
        self.w.diameterEdit.enable(not enabled)

    def _irregularDiameterChanged(self, sender=None):
        pass

    def _toggleGlyphInput(self, sender=None):
        enabled = self.w.useGlyphCheckbox.get()
        self.w.glyphNameInput.enable(enabled)

    def _glyphNameChanged(self, sender=None):
        pass

    def _rotationModeChanged(self, sender=None):
        if self.w.rotationNone.get():
            self._rotation_mode = "none"
        elif self.w.rotationRandom.get():
            self._rotation_mode = "random"
        elif self.w.rotationProgressive.get():
            self._rotation_mode = "progressive"

    def _rotationValueChanged(self, sender=None):
        try:
            value = float(self.w.rotationValue.get().strip().replace(',', '.'))
            self.w.rotationValue.set(f"{value:.1f}")
        except:
            self.w.rotationValue.set("15.0")

    def _charChanged(self, sender=None):
        ch = self.w.charInput.get().strip()
        self.view.setCharacter_(ch)

    def _masterChanged(self, sender=None):
        idx = self.w.masterPopup.get()
        self._set_master(idx)

    def _spacingEditChanged(self, sender=None):
        try:
            v = float(self.w.spacingEdit.get().strip().replace(',', '.'))
            self.w.spacingEdit.set(f"{v:.1f}")
        except:
            self.w.spacingEdit.set("46.0")

    def _diameterEditChanged(self, sender=None):
        try:
            v = float(self.w.diameterEdit.get().strip().replace(',', '.'))
            self.w.diameterEdit.set(f"{v:.1f}")
        except:
            self.w.diameterEdit.set("46.0")

    def _getSpacingValues(self):
        try:
            if self.w.irregularSpacingCheckbox.get():
                text = self.w.irregularSpacingInput.get().strip()
                return parse_irregular_values(text, 46.0)
            else:
                return [float(self.w.spacingEdit.get())]
        except:
            return [46.0]

    def _getDiameterValues(self):
        try:
            if self.w.irregularDiameterCheckbox.get():
                text = self.w.irregularDiameterInput.get().strip()
                return parse_irregular_values(text, 46.0)
            else:
                return [float(self.w.diameterEdit.get())]
        except:
            return [46.0]

    def _getRotationParams(self):
        try:
            mode = self._rotation_mode
            value = float(self.w.rotationValue.get().strip().replace(',', '.'))
            return mode, value
        except:
            return "none", 0

    def _preview(self, sender=None):
        start = time.time()
        
        f = self.font
        if not f:
            return
            
        g, layer = self.view._find_glyph_and_layer()
        if not layer:
            Message("No Glyph", "Could not find the specified character")
            return
        
        spacing_values = self._getSpacingValues()
        diameter_values = self._getDiameterValues()
        use_glyph = self.w.useGlyphCheckbox.get()
        glyph_names = self.w.glyphNameInput.get().strip() if use_glyph else None
        rotation_mode, rotation_value = self._getRotationParams()
        
        tempLayer = create_dotted_outline(layer, spacing_values, diameter_values, use_glyph, glyph_names, rotation_mode, rotation_value)
        
        if tempLayer:
            self.view.previewLayer = tempLayer
        else:
            self.view.previewLayer = None
            
        self.view._cached = None
        self.view._cachedSourceLayer = None
        self.view.setNeedsDisplay_(True)
        
        elapsed = (time.time() - start) * 1000
        debug_message(f"Preview generated in {elapsed:.1f}ms")

    def _apply(self, sender=None):
        start = time.time()
        
        f = self.font
        if not f:
            return

        spacing_values = self._getSpacingValues()
        diameter_values = self._getDiameterValues()
        use_glyph = self.w.useGlyphCheckbox.get()
        glyph_names = self.w.glyphNameInput.get().strip() if use_glyph else None
        rotation_mode, rotation_value = self._getRotationParams()
        targetMode = self.w.applyPopup.get()

        if targetMode == 0:  # Previewed Glyph
            g, layer = self.view._find_glyph_and_layer()
            if not layer:
                Message("No Glyph", "Could not find the specified character")
                return

            dotted_layer = create_dotted_outline(layer, spacing_values, diameter_values, use_glyph, glyph_names, rotation_mode, rotation_value)
            if not dotted_layer:
                Message("Error", "Failed to create dotted outline")
                return

            layer.beginChanges()
            try:
                anchors_to_keep = []
                for anchor in layer.anchors:
                    anchors_to_keep.append({
                        'name': anchor.name,
                        'x': anchor.x,
                        'y': anchor.y
                    })
                
                layer.shapes = []
                
                for p in dotted_layer.paths:
                    layer.shapes.append(p.copy())
                
                for anchor_data in anchors_to_keep:
                    new_anchor = GSAnchor()
                    new_anchor.name = anchor_data['name']
                    new_anchor.position = NSPoint(anchor_data['x'], anchor_data['y'])
                    layer.anchors.append(new_anchor)
            finally:
                layer.endChanges()

        elif targetMode == 1:  # Selected Glyphs
            selectedLayers = list(f.selectedLayers)
            if not selectedLayers:
                Message("No Selection", "Please select some glyphs first")
                return

            for layer in selectedLayers:
                dotted_layer = create_dotted_outline(layer, spacing_values, diameter_values, use_glyph, glyph_names, rotation_mode, rotation_value)
                if not dotted_layer:
                    continue

                layer.beginChanges()
                try:
                    anchors_to_keep = []
                    for anchor in layer.anchors:
                        anchors_to_keep.append({
                            'name': anchor.name,
                            'x': anchor.x,
                            'y': anchor.y
                        })
                    
                    layer.shapes = []
                    
                    for p in dotted_layer.paths:
                        layer.shapes.append(p.copy())
                    
                    for anchor_data in anchors_to_keep:
                        new_anchor = GSAnchor()
                        new_anchor.name = anchor_data['name']
                        new_anchor.position = NSPoint(anchor_data['x'], anchor_data['y'])
                        layer.anchors.append(new_anchor)
                finally:
                    layer.endChanges()

        else:  # Entire Font
            masterIndex = self.w.masterPopup.get()
            masterID = f.masters[masterIndex].id

            for g in f.glyphs:
                layer = g.layers[masterID]
                if not layer:
                    continue

                dotted_layer = create_dotted_outline(layer, spacing_values, diameter_values, use_glyph, glyph_names, rotation_mode, rotation_value)
                if not dotted_layer:
                    continue

                layer.beginChanges()
                try:
                    anchors_to_keep = []
                    for anchor in layer.anchors:
                        anchors_to_keep.append({
                            'name': anchor.name,
                            'x': anchor.x,
                            'y': anchor.y
                        })
                    
                    layer.shapes = []
                    
                    for p in dotted_layer.paths:
                        layer.shapes.append(p.copy())
                    
                    for anchor_data in anchors_to_keep:
                        new_anchor = GSAnchor()
                        new_anchor.name = anchor_data['name']
                        new_anchor.position = NSPoint(anchor_data['x'], anchor_data['y'])
                        layer.anchors.append(new_anchor)
                finally:
                    layer.endChanges()

        if f.currentTab:
            f.currentTab.redraw()

        self.view.previewLayer = None
        self.view._cached = None
        self.view._cachedSourceLayer = None
        self.view.setNeedsDisplay_(True)

        elapsed = (time.time() - start) * 1000
        debug_message(f"Applied in {elapsed:.1f}ms")
        Message("Success", f"Dotted outline applied in {elapsed:.1f}ms")
            
    @objc.python_method
    def _set_master(self, idx):
        try:
            m = self.font.masters[idx]
            metrics = {
                "masterID": m.id,
                "masterIndex": idx,
                "asc": float(m.ascender),
                "desc": float(m.descender),
                "xh": float(m.xHeight),
            }
            self.view.setMetrics_(metrics)
        except Exception as e:
            debug_error(f"Error in _set_master: {e}")

# Launch the panel
debug_message("Launching GlyphDottedOutlineGenerator TURBO")
GlyphDottedOutlineGenerator()