# MenuTitle: Live Glyph Preview Engine
# -*- coding: utf-8 -*-
# Description: Real-time glyph preview engine with interpolation, axis control, zoom, and interactive navigation.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2


from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc
import math
import time

# ---------------------------
# GLOBAL VARIABLE to prevent multiple instances
# ---------------------------
_panel_instance = None

# ---------------------------
# CHECK IF SimplePreviewView CLASS ALREADY EXISTS
# ---------------------------
SimplePreviewView = None
try:
    # Intentar obtener la clase existente del runtime Objective-C
    existing_class = objc.lookUpClass("SimplePreviewView")
    if existing_class:
        print("✅ SimplePreviewView class already exists, reusing")
        SimplePreviewView = existing_class
except Exception as e:
    print(f"ℹ️ No existing SimplePreviewView found: {e}")

# Si la clase no existe, definirla
if SimplePreviewView is None:
    print("🆕 Defining new SimplePreviewView class")
    
    # ---------------------------
    # HELPERS
    # ---------------------------
    def parse_brace_from_name(lyr):
        """
        If layer.name is like {124,1,0} or {153,1,0,}, return a list of floats [124,1,0].
        Otherwise return None.
        """
        try:
            nm = lyr.name or ""
            nm = nm.strip()
            if nm.startswith("{") and nm.endswith("}"):
                inside = nm[1:-1].strip()
                if not inside:
                    return None
                parts = [p.strip() for p in inside.split(",") if p.strip() != ""]
                vals = []
                for p in parts:
                    try:
                        vals.append(float(p))
                    except:
                        return None
                return vals
        except Exception:
            pass
        return None

    def interpolate_layers_nodewise(layerA, layerB, t):
        """Interpolate between two layers by node coordinates"""
        try:
            newLayer = layerA.copy()
            
            pathsA = getattr(newLayer, "paths", None)
            pathsB = getattr(layerB, "paths", None)
            if pathsA is None or pathsB is None:
                return None
            if len(pathsA) != len(pathsB):
                return None

            for pi in range(len(pathsA)):
                pa = pathsA[pi]
                pb = pathsB[pi]
                nodesA = getattr(pa, "nodes", None)
                nodesB = getattr(pb, "nodes", None)
                if nodesA is None or nodesB is None:
                    return None
                if len(nodesA) != len(nodesB):
                    return None
                
                for ni in range(len(nodesA)):
                    na = nodesA[ni]
                    nb = nodesB[ni]
                    try:
                        ax = float(na.x)
                        ay = float(na.y)
                        bx = float(nb.x)
                        by = float(nb.y)
                        ix = ax + (bx - ax) * t
                        iy = ay + (by - ay) * t
                        na.x = ix
                        na.y = iy
                    except Exception:
                        return None

            try:
                wa = float(getattr(layerA, "width", 0))
                wb = float(getattr(layerB, "width", 0))
                newLayer.width = wa + (wb - wa) * t
            except Exception:
                pass

            return newLayer
        except Exception as e:
            print(f"interpolate_nodes error: {e}")
            return None

    # ---------------------------
    # REAL-TIME PREVIEW VIEW with Dragging
    # ---------------------------
    
    class SimplePreviewView(NSView):

        @objc.python_method
        def debug_log(self, message):
            print(f"[SimplePreviewView] {message}")

        def initWithFrame_(self, frame):
            self = objc.super(SimplePreviewView, self).initWithFrame_(frame)
            if self is None:
                return None
            
            self.current_glyph_name = None
            self.metrics = None
            self.axisValues = {}
            self.zoom = 1.0
            self.offset_x = 0.0
            self.offset_y = 0.0
            
            self.is_dragging = False
            self.drag_start = None
            self.last_offset = (0.0, 0.0)
            
            self.layer_cache = {}
            
            self.update_timer = None
            
            return self

        @objc.python_method
        def schedulePeriodicUpdate(self):
            """Schedule periodic updates to refresh the view"""
            try:
                if self.update_timer:
                    self.update_timer.invalidate()
                    self.update_timer = None
                
                self.update_timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
                    0.1,
                    self,
                    objc.selector(self.forceRedraw_, signature=b'v@:@'),
                    None,
                    True
                )
                runLoop = NSRunLoop.currentRunLoop()
                runLoop.addTimer_forMode_(self.update_timer, NSRunLoopCommonModes)
                runLoop.addTimer_forMode_(self.update_timer, NSDefaultRunLoopMode)
                self.debug_log("✅ Periodic update timer scheduled")
            except Exception as e:
                self.debug_log(f"❌ Error scheduling periodic update: {e}")

        def forceRedraw_(self, timer):
            self.setNeedsDisplay_(True)

        @objc.python_method
        def stopPeriodicUpdate(self):
            if self.update_timer:
                self.update_timer.invalidate()
                self.update_timer = None
                self.debug_log("✅ Periodic update timer stopped")

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

                idx = self.metrics.get("masterIndex")
                if isinstance(idx, int) and 0 <= idx < len(font.masters):
                    return font.masters[idx]

            return font.masters[0] if font.masters else None

        @objc.python_method
        def setCurrentGlyphName(self, name):
            if self.current_glyph_name != name:
                self.current_glyph_name = name
                self.layer_cache.clear()
                self.setNeedsDisplay_(True)

        @objc.python_method
        def setMetrics(self, metrics):
            self.metrics = metrics
            self.layer_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setAxisValues(self, axisValues):
            self.axisValues = axisValues or {}
            self.layer_cache.clear()
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setZoom(self, zoom):
            self.zoom = max(0.1, min(zoom, 5.0))
            self.setNeedsDisplay_(True)

        @objc.python_method
        def setOffset(self, x, y):
            self.offset_x = x
            self.offset_y = y
            self.setNeedsDisplay_(True)

        @objc.python_method
        def resetView(self):
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.setNeedsDisplay_(True)

        def mouseDown_(self, event):
            point = self.convertPoint_fromView_(event.locationInWindow(), None)
            self.is_dragging = True
            self.drag_start = point
            self.last_offset = (self.offset_x, self.offset_y)

        def mouseDragged_(self, event):
            if self.is_dragging and self.drag_start:
                point = self.convertPoint_fromView_(event.locationInWindow(), None)
                delta_x = point.x - self.drag_start.x
                delta_y = point.y - self.drag_start.y
                
                scale_factor = 1.0 / self.zoom
                
                self.offset_x = self.last_offset[0] + delta_x * scale_factor * 1.5
                self.offset_y = self.last_offset[1] + delta_y * scale_factor * 1.5
                
                self.setNeedsDisplay_(True)

        def mouseUp_(self, event):
            self.is_dragging = False
            self.drag_start = None

        @objc.python_method
        def _getInterpolatedLayer(self):
            """Get interpolated layer using current axis values; if no axes, use selectedLayer for live editing"""
            font = Glyphs.font
            if not font:
                return None

            # Si no hay ejes activos, usamos directamente la capa seleccionada => cambios de nodos en vivo
            if not self.axisValues:
                if font.selectedLayers:
                    return font.selectedLayers[0]
                if not self.current_glyph_name:
                    return None
                glyph = font.glyphs[self.current_glyph_name]
                if not glyph or not glyph.layers:
                    return None
                master = self.getCurrentMaster()
                if master:
                    for layer in glyph.layers:
                        if getattr(layer, "associatedMasterId", None) == master.id:
                            return layer
                return glyph.layers[0]

            if not self.current_glyph_name:
                return None

            cache_key = f"{self.current_glyph_name}_{str(self.axisValues)}"
            
            try:
                glyph = font.glyphs[self.current_glyph_name]
                if not glyph:
                    self.debug_log(f"No glyph found: '{self.current_glyph_name}'")
                    return None
            
                layers_with_coords = []
            
                for m in font.masters:
                    layer = None
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
                    vals = parse_brace_from_name(lyr)
                    if vals:
                        try:
                            if len(vals) >= len(font.axes):
                                coords = [float(v) for v in vals[:len(font.axes)]]
                                layers_with_coords.append((coords, lyr, lyr.name))
                        except Exception:
                            continue
            
                target_coords = []
                for axis in font.axes:
                    axis_name = axis.name
                    axis_tag = getattr(axis, "axisTag", "")
                
                    value = None
                    for key, val in self.axisValues.items():
                        key_lower = key.lower()
                        axis_name_lower = axis_name.lower() if axis_name else ""
                        axis_tag_lower = axis_tag.lower() if axis_tag else ""
                    
                        if (key_lower == axis_name_lower or 
                            (axis_tag_lower and key_lower == axis_tag_lower)):
                            try:
                                value = float(val)
                                break
                            except Exception:
                                continue
                
                    if value is None:
                        master = self.getCurrentMaster()
                        if master:
                            idx = list(font.axes).index(axis)
                            value = float(master.axes[idx])
                        else:
                            value = 0.0
                
                    target_coords.append(value)
            
                for coords, layer, name in layers_with_coords:
                    if len(coords) == len(target_coords):
                        is_exact = True
                        for i in range(len(coords)):
                            if abs(coords[i] - target_coords[i]) > 0.1:
                                is_exact = False
                                break
                        if is_exact:
                            self.layer_cache[cache_key] = layer
                            return layer
            
                if len(layers_with_coords) >= 2:
                    layers_with_distances = []
                    for coords, layer, name in layers_with_coords:
                        distance = 0
                        for i in range(len(coords)):
                            diff = coords[i] - target_coords[i]
                            distance += diff * diff
                        distance = math.sqrt(distance)
                        layers_with_distances.append((distance, coords, layer, name))
                
                    layers_with_distances.sort(key=lambda x: x[0])
                
                    _, coords1, layer1, name1 = layers_with_distances[0]
                    _, coords2, layer2, name2 = layers_with_distances[1]
                
                    if abs(coords2[0] - coords1[0]) > 0.001:
                        t = (target_coords[0] - coords1[0]) / (coords2[0] - coords1[0])
                    else:
                        t_vals = []
                        for i in range(len(coords1)):
                            if abs(coords2[i] - coords1[i]) > 0.001:
                                t_val = (target_coords[i] - coords1[i]) / (coords2[i] - coords1[i])
                                t_vals.append(t_val)
                        t = sum(t_vals) / len(t_vals) if t_vals else 0.5
                
                    interp = interpolate_layers_nodewise(layer1, layer2, t)
                    if interp:
                        self.layer_cache[cache_key] = interp
                        return interp
            
                master = self.getCurrentMaster()
                if master:
                    for layer in glyph.layers:
                        if getattr(layer, 'associatedMasterId', None) == master.id:
                            self.layer_cache[cache_key] = layer
                            return layer
            
                layer = glyph.layers[0] if glyph.layers else None
                self.layer_cache[cache_key] = layer
                return layer
            
            except Exception as e:
                self.debug_log(f"ERROR in _getInterpolatedLayer: {e}")
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
            except Exception as e:
                self.debug_log(f"ERROR in buildPathFromLayer: {e}")
                return None

        def drawRect_(self, rect):
            try:
                NSColor.colorWithCalibratedWhite_alpha_(0.95, 1.0).set()
                NSBezierPath.fillRect_(self.bounds())
            
                font = Glyphs.font
                if not font:
                    return
            
                if not self.current_glyph_name and not font.selectedLayers:
                    return
            
                layer = self._getInterpolatedLayer()
                if not layer:
                    return
            
                master = self.getCurrentMaster()
                if not master:
                    return
            
                w = self.bounds().size.width
                h = self.bounds().size.height
            
                asc = float(master.ascender)
                desc = float(master.descender)
                total_height = asc - desc
                if total_height <= 0:
                    total_height = 1000.0
            
                padding = 40.0
                available_height = h - 2 * padding
                base_scale = (available_height / total_height) * self.zoom
            
                view_baseline = (h / 2) - ((asc + desc) * base_scale / 2) + self.offset_y
                center_x = (w / 2) - ((layer.width * base_scale) / 2) + self.offset_x
            
                self._drawMasterLines(master, base_scale, view_baseline, w, h)
                self._drawGlyph(layer, master, base_scale, center_x, view_baseline)
            
            except Exception as e:
                print(f"❌ ERROR in drawRect: {e}")

        @objc.python_method
        def _drawGlyph(self, layer, master, scale, x_offset, baseline):
            try:
                glyphPath = self.buildPathFromLayer(layer)
                if not glyphPath:
                    return
            
                transform = NSAffineTransform.transform()
                transform.translateXBy_yBy_(x_offset, baseline)
                transform.scaleXBy_yBy_(scale, scale)
            
                transformedPath = glyphPath.copy()
                transformedPath.transformUsingAffineTransform_(transform)
            
                NSColor.blackColor().set()
                transformedPath.fill()
            
            except Exception as e:
                self.debug_log(f"Error in _drawGlyph: {e}")

        @objc.python_method
        def _drawMasterLines(self, master, scale, baseline, w, h):
            asc = float(master.ascender)
            xh = float(master.xHeight)
            desc = float(master.descender)
            cap = float(getattr(master, 'capHeight', asc * 0.9))
        
            NSColor.blackColor().colorWithAlphaComponent_(0.2).set()
            asc_y = baseline + (asc * scale)
            line = NSBezierPath.bezierPath()
            line.moveToPoint_((0, asc_y))
            line.lineToPoint_((w, asc_y))
            line.setLineWidth_(1.0)
            line.stroke()
        
            NSColor.blackColor().colorWithAlphaComponent_(0.2).set()
            cap_y = baseline + (cap * scale)
            line = NSBezierPath.bezierPath()
            line.moveToPoint_((0, cap_y))
            line.lineToPoint_((w, cap_y))
            line.setLineWidth_(1.0)
            line.stroke()
        
            NSColor.blackColor().colorWithAlphaComponent_(0.2).set()
            xh_y = baseline + (xh * scale)
            line = NSBezierPath.bezierPath()
            line.moveToPoint_((0, xh_y))
            line.lineToPoint_((w, xh_y))
            line.setLineWidth_(1.0)
            line.stroke()
        
            NSColor.blackColor().colorWithAlphaComponent_(0.2).set()
            line = NSBezierPath.bezierPath()
            line.moveToPoint_((0, baseline))
            line.lineToPoint_((w, baseline))
            line.setLineWidth_(2.0)
            line.stroke()
        
            NSColor.blackColor().colorWithAlphaComponent_(0.2).set()
            desc_y = baseline + (desc * scale)
            line = NSBezierPath.bezierPath()
            line.moveToPoint_((0, desc_y))
            line.lineToPoint_((w, desc_y))
            line.setLineWidth_(1.0)
            line.stroke()

    print("✅ SimplePreviewView class defined")

# Wrapper class
class RealTimePreviewWrapper(object):
    def __init__(self, posSize):
        self.view = SimplePreviewView.alloc().initWithFrame_(((0, 0), (posSize[2], posSize[3])))
        self._nsObject = self.view
        
    def getNSView(self):
        return self._nsObject

    def setCurrentGlyphName(self, name):
        self.view.setCurrentGlyphName(name)
        
    def setMetrics(self, metrics):
        self.view.setMetrics(metrics)
        
    def setAxisValues(self, axisValues):
        self.view.setAxisValues(axisValues)
        
    def setZoom(self, zoom):
        self.view.setZoom(zoom)
        
    def setOffset(self, x, y):
        self.view.setOffset(x, y)
        
    def resetView(self):
        self.view.resetView()
        
    def startRealTimeUpdates(self):
        self.view.schedulePeriodicUpdate()
        
    def stopRealTimeUpdates(self):
        self.view.stopPeriodicUpdate()

class CocoaViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject

# ---------------------------
# MAIN PANEL
# ---------------------------
class RealTimeGlyphPreviewPanel(object):
    def __init__(self):
        try:
            self.font = Glyphs.font
            if not self.font:
                Message("No Font Open", "Please open a font first")
                return

            self.axes = self.getRealAxes()
            num_axes = len(self.axes)

            total_height = 750 + (num_axes * 30)
            self.w = Window((400, total_height), "Real-time Glyph Preview")

            self.w.title = TextBox((20, 15, 360, 22), 
                                   "Real-time Glyph Preview", 
                                   sizeStyle="small")

            current_tab = self.font.currentTab
            current_glyph = None
            if current_tab and hasattr(current_tab, 'layers'):
                for layer in current_tab.layers:
                    if hasattr(layer, 'parent'):
                        current_glyph = layer.parent
                        break
            
            if not current_glyph and self.font.selectedLayers:
                current_glyph = self.font.selectedLayers[0].parent
            
            self.current_glyph_name = current_glyph.name if current_glyph else "H"
            
            self.w.glyphLabel = TextBox((20, 45, 80, 22), "Current Glyph:")
            self.w.glyphName = TextBox((110, 45, 150, 22), self.current_glyph_name)
            
            masters = [m.name for m in self.font.masters]
            self.w.masterLabel = TextBox((20, 75, 50, 22), "Master:")
            self.w.masterPopup = PopUpButton((80, 75, 150, 22), masters, callback=self.masterChanged)

            self.axes_controls = {}
            axes_y = 110

            if self.axes:
                for i, axis in enumerate(self.axes):
                    axis_safe_name = axis['name'].replace(' ', '_').replace('-', '_').lower()

                    label_name = f"label_{axis_safe_name}_{i}"
                    setattr(self.w, label_name, TextBox((20, axes_y, 80, 22), f"{axis['name']}:"))

                    slider_name = f"slider_{axis_safe_name}_{i}"
                    slider = Slider((100, axes_y, 120, 22),
                                    minValue=axis['minValue'],      # Valor mínimo real
                                    maxValue=axis['maxValue'],      # Valor máximo real
                                    value=axis['defaultValue'], 
                                    callback=self.axisChanged)
                    setattr(self.w, slider_name, slider)

                    value_name = f"value_{axis_safe_name}_{i}"
                    axis_field = EditText((230, axes_y, 50, 22), f"{int(axis['defaultValue'])}",
                                          callback=self.axisValueChanged)
                    setattr(self.w, value_name, axis_field)

                    hide_name = f"hide_{axis_safe_name}_{i}"
                    hide_checkbox = CheckBox((290, axes_y, 60, 22), "Hide",
                                             callback=self.axisHideChanged)
                    setattr(self.w, hide_name, hide_checkbox)

                    self.axes_controls[i] = {
                        'info': axis,
                        'label_name': label_name,
                        'slider_name': slider_name,
                        'value_name': value_name,
                        'hide_name': hide_name,
                        'field': axis_field,
                        'slider': slider,
                        'checkbox': hide_checkbox
                    }
                    axes_y += 30

            self.w.zoomLabel = TextBox((20, axes_y, 50, 22), "Zoom:")
            self.w.zoomSlider = Slider((80, axes_y, 150, 22), 
                                       minValue=10, maxValue=500, value=100, 
                                       callback=self.zoomChanged)
            self.w.zoomValue = EditText((240, axes_y, 50, 22), "100%",
                                        callback=self.zoomValueChanged)
            self.w.resetButton = Button((300, axes_y, 60, 22), "Reset", 
                                        callback=self.resetView)
            
            axes_y += 40

            preview_y = axes_y + 10
            preview_height = 550

            self.preview = RealTimePreviewWrapper((20, preview_y, 360, preview_height))
            self.w.preview = CocoaViewWrapper((20, preview_y, 360, preview_height), 
                                              self.preview.getNSView())

            print("🎉 Real-time preview panel initialized")
            print(f"📊 Current glyph: {self.current_glyph_name}")
            print(f"📍 Axes detected: {len(self.axes)}")

            self.setMaster(0)
            self.preview.setCurrentGlyphName(self.current_glyph_name)
            self.preview.startRealTimeUpdates()
            
            self.w.open()
            self.setupUpdateTimer()

        except Exception as e:
            print(f"❌ ERROR initializing panel: {e}")
            import traceback
            traceback.print_exc()
            Message("Error", "Failed to initialize panel")
            
    def setupUpdateTimer(self):
        """Set up timer to check for glyph changes"""
        try:
            self.update_timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
                0.2,
                self,
                objc.selector(self.checkForUpdates_, signature=b'v@:@'),
                None,
                True
            )
            runLoop = NSRunLoop.currentRunLoop()
            runLoop.addTimer_forMode_(self.update_timer, NSRunLoopCommonModes)
            runLoop.addTimer_forMode_(self.update_timer, NSDefaultRunLoopMode)
        except Exception as e:
            print(f"❌ Error setting up update timer: {e}")

    def checkForUpdates_(self, timer):
        """Check if current glyph has changed"""
        try:
            if self.font.selectedLayers:
                current_layer = self.font.selectedLayers[0]
                if hasattr(current_layer, 'parent'):
                    current_glyph = current_layer.parent
                    if current_glyph and current_glyph.name != self.current_glyph_name:
                        self.current_glyph_name = current_glyph.name
                        self.w.glyphName.set(self.current_glyph_name)
                        self.preview.setCurrentGlyphName(self.current_glyph_name)
                        if hasattr(self.preview.view, 'layer_cache'):
                            self.preview.view.layer_cache.clear()
                        print(f"🔄 Glyph changed to: {self.current_glyph_name}")
        except Exception:
            pass

    @objc.python_method
    def getRealAxes(self):
        axes = []
        try:
            font = Glyphs.font
            if font and hasattr(font, 'axes'):
                for idx, axis in enumerate(font.axes):
                    master_values = [m.axes[idx] for m in font.masters]
                    if not master_values:
                        continue
                    min_val = min(master_values)
                    max_val = max(master_values)
                    default_val = master_values[0]
                
                    # USAR SOLO LOS VALORES REALES DE LOS MASTERS
                    axis_name = getattr(axis, "name", f"Axis {idx+1}")
                    axis_tag = getattr(axis, "axisTag", "")
                
                    axes.append({
                        'name': axis_name,
                        'tag': axis_tag,
                        'minValue': min_val,
                        'maxValue': max_val,
                        'defaultValue': default_val,
                        'extendedMin': min_val,  # Mismo que minValue
                        'extendedMax': max_val,  # Mismo que maxValue
                    })
                    
                    print(f"📊 Eje '{axis_name}': min={min_val}, max={max_val}, default={default_val}")
            return axes
        except Exception as e:
            print(f"❌ Error getting axes: {e}")
            return axes

    def masterChanged(self, sender=None):
        idx = self.w.masterPopup.get()
        self.setMaster(idx)

    def setMaster(self, index):
        try:
            master = self.font.masters[index]
            
            metrics = {
                'masterID': master.id,
                'masterIndex': index,
                'asc': float(master.ascender),
                'desc': float(master.descender),
                'xh': float(master.xHeight),
            }
            
            self.preview.setMetrics(metrics)
            
            for i, axis_data in self.axes_controls.items():
                axis = axis_data['info']
                slider = axis_data['slider']
                axis_field = axis_data['field']
                
                master_axis_value = master.axes[i]
                # Usar minValue y maxValue en lugar de extended
                clamped_value = max(axis['minValue'], min(master_axis_value, axis['maxValue']))
                slider.set(clamped_value)
                axis_field.set(f"{int(clamped_value)}")
            
            self.updateAxes()
            
        except Exception as e:
            print(f"❌ Error in setMaster: {e}")

    def zoomChanged(self, sender=None):
        val = self.w.zoomSlider.get()
        zoom_factor = val / 100.0
        self.w.zoomValue.set(f"{int(val)}%")
        self.preview.setZoom(zoom_factor)

    def zoomValueChanged(self, sender=None):
        try:
            value_str = self.w.zoomValue.get().strip()
            if value_str.endswith('%'):
                value_str = value_str[:-1]
            value = float(value_str)
            value = max(10, min(value, 500))
            self.w.zoomSlider.set(value)
            self.w.zoomValue.set(f"{int(value)}%")
            self.preview.setZoom(value / 100.0)
        except ValueError:
            current_val = self.w.zoomSlider.get()
            self.w.zoomValue.set(f"{int(current_val)}%")

    def resetView(self, sender=None):
        self.preview.resetView()

    def axisChanged(self, sender=None):
        for i, axis_data in self.axes_controls.items():
            if sender == axis_data['slider']:
                value = axis_data['slider'].get()
                axis_data['field'].set(f"{int(value)}")
                break
        self.updateAxes()
        
    def axisValueChanged(self, sender=None):
        try:
            for i, axis_data in self.axes_controls.items():
                axis_field = axis_data['field']
                if sender == axis_field:
                    value_str = axis_field.get().strip()
                    axis = axis_data['info']
                    slider = axis_data['slider']
                    if value_str:
                        try:
                            value = float(value_str)
                            # Usar minValue y maxValue en lugar de extended
                            value = max(axis['minValue'], min(value, axis['maxValue']))
                            slider.set(value)
                            axis_field.set(f"{int(value)}")
                            self.updateAxes()
                        except ValueError:
                            current_val = slider.get()
                            axis_field.set(f"{int(current_val)}")
                    else:
                        current_val = slider.get()
                        axis_field.set(f"{int(current_val)}")
                    break
        except Exception as e:
            print(f"❌ Error in axisValueChanged: {e}")

    def axisHideChanged(self, sender=None):
        self.updateAxes()
    
    def updateAxes(self):
        axisValues = {}
        for i, axis_data in self.axes_controls.items():
            axis = axis_data['info']
            slider = axis_data['slider']
            checkbox = axis_data['checkbox']
            
            value = slider.get()
            axis_name = axis['name']
            
            is_hidden = checkbox.get()
            
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
        
        self.preview.setAxisValues(axisValues)

# ---------------------------
# MAIN ENTRY POINT
# ---------------------------
def main():
    global _panel_instance
    
    # Verificar si ya existe una instancia
    if _panel_instance is not None:
        try:
            if hasattr(_panel_instance, 'w') and _panel_instance.w:
                _panel_instance.w.bringToFront()
                print("📌 Panel already exists, bringing to front")
                return
            else:
                _panel_instance = None
        except:
            _panel_instance = None
    
    try:
        _panel_instance = RealTimeGlyphPreviewPanel()
        
        def cleanup(sender=None):
            global _panel_instance
            try:
                if hasattr(_panel_instance, 'update_timer') and _panel_instance.update_timer:
                    _panel_instance.update_timer.invalidate()
                if hasattr(_panel_instance, 'preview'):
                    _panel_instance.preview.stopRealTimeUpdates()
            except:
                pass
            _panel_instance = None
            print("🧹 Panel closed and timers stopped")
        
        if hasattr(_panel_instance, 'w'):
            _panel_instance.w.bind("close", cleanup)
            
    except Exception as e:
        print(f"❌ Error creating panel: {e}")
        import traceback
        traceback.print_exc()
        Message("Error", "Failed to create panel")

if __name__ == "__main__":
    main()