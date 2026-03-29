#MenuTitle: Advanced Stem Analyzer (DIAGONAL + SEMI-VERTICAL FIX)
# -*- coding: utf-8 -*-
# Description: Analyzes stem consistency across glyphs, detecting deviations in vertical, diagonal, and curved stems using tolerance-based evaluation. Includes semi-vertical detection.
# Author: Designed by Josep Patau Bellart, programmed with AI tools + DIAGONAL + SEMI-VERTICAL FIX
# License: Apache2

from GlyphsApp import Glyphs, GSGuide, CURVE, GSPath, GSNode
from AppKit import NSPoint
import vanilla
import math
import traceback


class XBeamInspector(object):

    prefID = "com.xbeam.inspector.pro"

    # -------------------------
    # INIT
    # -------------------------
    def __init__(self):
        self.loadPrefs()
        self.buildUI()
        self.report_text = ""

    # -------------------------
    # PREFERENCES
    # -------------------------
    def loadPrefs(self):
        self.width = Glyphs.defaults.get(self.prefID+".width",45)
        self.curveWidth = Glyphs.defaults.get(self.prefID+".curveWidth",49)
        self.margin = Glyphs.defaults.get(self.prefID+".margin",1)
        self.diagonalMargin = Glyphs.defaults.get(self.prefID+".diagonalMargin",1.5)
        self.curveMargin = Glyphs.defaults.get(self.prefID+".curveMargin",2)
        self.discardPercent = Glyphs.defaults.get(self.prefID+".discardPercent",30)
        self.yValues = Glyphs.defaults.get(self.prefID+".yValues","500")
        self.reportMode = Glyphs.defaults.get(self.prefID+".reportMode","simple")
        self.semiVerticalMaxDx = Glyphs.defaults.get(self.prefID+".semiVerticalMaxDx",5.0)
        self.semiVerticalMaxAngle = Glyphs.defaults.get(self.prefID+".semiVerticalMaxAngle",3.0)

    def savePrefs(self):
        Glyphs.defaults[self.prefID+".width"] = self.width
        Glyphs.defaults[self.prefID+".curveWidth"] = self.curveWidth
        Glyphs.defaults[self.prefID+".margin"] = self.margin
        Glyphs.defaults[self.prefID+".diagonalMargin"] = self.diagonalMargin
        Glyphs.defaults[self.prefID+".curveMargin"] = self.curveMargin
        Glyphs.defaults[self.prefID+".discardPercent"] = self.discardPercent
        Glyphs.defaults[self.prefID+".yValues"] = self.yValues
        Glyphs.defaults[self.prefID+".reportMode"] = self.reportMode
        Glyphs.defaults[self.prefID+".semiVerticalMaxDx"] = self.semiVerticalMaxDx
        Glyphs.defaults[self.prefID+".semiVerticalMaxAngle"] = self.semiVerticalMaxAngle
        
    def nodeHasHandle(self, node):
        try:
            if hasattr(node, 'outgoingHandle') and node.outgoingHandle:
                if abs(node.outgoingHandle.x) > 0.01 or abs(node.outgoingHandle.y) > 0.01:
                    return True
            if hasattr(node, 'incomingHandle') and node.incomingHandle:
                if abs(node.incomingHandle.x) > 0.01 or abs(node.incomingHandle.y) > 0.01:
                    return True
        except:
            pass
        return False
        

    # -------------------------
    # UI
    # -------------------------
    def buildUI(self):
        self.w = vanilla.Window((580,550),"Advanced Stem Analyzer")

        # Fila 1: Target stems (rectas y curvas)
        self.w.text1 = vanilla.TextBox((15,15,100,20),"Target stem:")
        self.w.text1a = vanilla.TextBox((130,15,40,20),"Rect")
        self.w.width = vanilla.EditText((170,12,60,22),str(self.width))
        
        self.w.text1b = vanilla.TextBox((250,15,40,20),"Curve")
        self.w.curveWidth = vanilla.EditText((290,12,60,22),str(self.curveWidth))

        # Fila 2: Tolerances (rectas, curvas, diagonales)
        self.w.text2 = vanilla.TextBox((15,45,100,20),"Tolerance:")
        self.w.text2a = vanilla.TextBox((130,45,40,20),"Rect")
        self.w.margin = vanilla.EditText((170,42,60,22),str(self.margin))
        
        self.w.text2b = vanilla.TextBox((250,45,40,20),"Curve")
        self.w.curveMargin = vanilla.EditText((290,42,60,22),str(self.curveMargin))
        
        self.w.text2c = vanilla.TextBox((370,45,70,20),"Diagonals")
        self.w.diagonalMargin = vanilla.EditText((440,42,60,22),str(self.diagonalMargin))

        # Fila 3: Semi-vertical thresholds
        self.w.text3a = vanilla.TextBox((15,75,150,20),"Semi-vertical:")
        self.w.text3b = vanilla.TextBox((170,75,40,20),"Max ΔX")
        self.w.semiVerticalMaxDx = vanilla.EditText((210,72,50,22),str(self.semiVerticalMaxDx))
        self.w.text3c = vanilla.TextBox((270,75,50,20),"Max angle")
        self.w.semiVerticalMaxAngle = vanilla.EditText((320,72,50,22),str(self.semiVerticalMaxAngle))
        self.w.text3d = vanilla.TextBox((380,75,120,20),"degrees")

        # Fila 4: Rule Out percentage
        self.w.text4 = vanilla.TextBox((15,105,150,20),"Rule Out %: (ej: 30 = ±30%)")
        self.w.discardPercent = vanilla.EditText((170,102,60,22),str(self.discardPercent))

        # Fila 5: Xbeam positions
        self.w.text5 = vanilla.TextBox((15,135,150,20),"Xbeam positions:")
        self.w.yValues = vanilla.EditText((170,132,320,22),self.yValues)
        self.w.text5a = vanilla.TextBox((170,155,320,15),"Multiple lines, comma separated")

        # Botón Inspect selected glyphs
        self.w.inspectSel = vanilla.Button(
            (15,180,200,28),
            "Inspect selected glyphs",
            callback=self.inspectSelected
        )

        # Report mode checkboxes
        self.w.simpleReport = vanilla.CheckBox(
            (15,220,120,20),
            "Simple Report",
            value=(self.reportMode == "simple"),
            callback=self.toggleReportMode
        )
        
        self.w.fullReport = vanilla.CheckBox(
            (140,220,120,20),
            "Full Report",
            value=(self.reportMode == "full"),
            callback=self.toggleReportMode
        )

        # Report text area
        self.w.reportLabel = vanilla.TextBox((15,250,100,20),"Report")
        self.w.reportText = vanilla.TextEditor(
            (15,270,550,220),
            text="",
            readOnly=True
        )

        # Report buttons
        self.w.clearReport = vanilla.Button(
            (15,500,120,22),
            "Clear Report",
            callback=self.clearReport
        )
        
        self.w.copyReport = vanilla.Button(
            (140,500,120,22),
            "Copy Report",
            callback=self.copyReport
        )

        self.w.open()

    def toggleReportMode(self, sender):
        if sender == self.w.simpleReport and self.w.simpleReport.get():
            self.w.fullReport.set(False)
            self.reportMode = "simple"
        elif sender == self.w.fullReport and self.w.fullReport.get():
            self.w.simpleReport.set(False)
            self.reportMode = "full"
        self.savePrefs()

    def clearReport(self, sender):
        self.report_text = ""
        self.w.reportText.set("")

    def copyReport(self, sender):
        from AppKit import NSPasteboard, NSStringPboardType
        pb = NSPasteboard.generalPasteboard()
        pb.declareTypes_owner_([NSStringPboardType], None)
        pb.setString_forType_(self.report_text, NSStringPboardType)
        original_title = self.w.copyReport.getTitle()
        self.w.copyReport.setTitle("✓ Copiado!")
        import time
        self.w.copyReport.setTitle(original_title)

    # -------------------------
    # READ UI
    # -------------------------
    def parseYValues(self, y_text):
        if not y_text or y_text.isspace():
            return [500.0]
        y_list = []
        for v in y_text.split(","):
            v = v.strip()
            if v:
                try:
                    y_list.append(float(v))
                except ValueError:
                    self.addToReport(f"Warning: '{v}' is not a valid number, ignoring\n")
        if not y_list:
            return [500.0]
        return y_list

    def readUI(self):
        self.width = float(self.w.width.get())
        self.curveWidth = float(self.w.curveWidth.get())
        self.margin = float(self.w.margin.get())
        self.diagonalMargin = float(self.w.diagonalMargin.get())
        self.curveMargin = float(self.w.curveMargin.get())
        self.discardPercent = float(self.w.discardPercent.get())
        self.yValues = self.w.yValues.get()
        self.yList = self.parseYValues(self.yValues)
        self.semiVerticalMaxDx = float(self.w.semiVerticalMaxDx.get())
        self.semiVerticalMaxAngle = float(self.w.semiVerticalMaxAngle.get())
        self.savePrefs()

    # -------------------------
    # REPORT
    # -------------------------
    def addToReport(self, text):
        self.report_text += text
        self.w.reportText.set(self.report_text)

    def clearReportContent(self):
        self.report_text = ""
        self.w.reportText.set("")

    # -------------------------
    # DIAGONAL STEM CALCULATION
    # -------------------------
    def calculateDiagonalFactor(self, n1, n2):
        dx = n2.x - n1.x
        dy = n2.y - n1.y
    
        if abs(dy) < 0.001:
            return 1.0, 0.0, "horizontal"
    
        dx_abs = abs(dx)
        dy_abs = abs(dy)
        angle_rad = math.atan(dx_abs / dy_abs)
        angle_deg = math.degrees(angle_rad)
    
        # Detectar semi-vertical con umbrales configurables
        if self.isSemiVerticalSegment(n1, n2):
            return 1.0, angle_deg, "semi_vertical"
    
        # Diagonal real
        factor = min(1.0 / math.cos(angle_rad), 1.25)
        diag_type = "/" if dx * dy > 0 else "\\\\"
    
        return factor, angle_deg, diag_type

    # -------------------------
    # CHECK IF SEGMENT IS CURVED - SIMPLIFICADO
    # -------------------------
    def nodeHasAnyHandle(self, node):
        """Check if node has ANY handle (incoming or outgoing) with length > 0"""
        try:
            # Check outgoing handle
            if hasattr(node, 'outgoingHandle') and node.outgoingHandle:
                dx = node.outgoingHandle.x - node.x
                dy = node.outgoingHandle.y - node.y
                if abs(dx) > 0.01 or abs(dy) > 0.01:
                    return True
            
            # Check incoming handle
            if hasattr(node, 'incomingHandle') and node.incomingHandle:
                dx = node.incomingHandle.x - node.x
                dy = node.incomingHandle.y - node.y
                if abs(dx) > 0.01 or abs(dy) > 0.01:
                    return True
        except:
            pass
        return False
    
    def isCurvedSegment(self, n1, n2):
        """
        Real curve detection based on Bézier logic:
        - 0 handles → straight line
        - 1 handle → almost straight / transitional
        - 2 handles → real curve
        """

        handle_count = self.countHandlesBetween(n1, n2)

        return handle_count == 2
    
    def isColinear(self, n1, n2, hx, hy):
        seg_dx = n2.x - n1.x
        seg_dy = n2.y - n1.y
    
        # cross product ≈ 0 → alineat
        return abs(seg_dx * hy - seg_dy * hx) < 0.01
    
    
    def getSegmentTypeInfo(self, n1, n2):
        """Returns detailed info about segment type for debugging"""

        def node_handles(node):
            handles = []
            try:
                if hasattr(node, 'outgoingHandle') and node.outgoingHandle:
                    dx = node.outgoingHandle.x - node.x
                    dy = node.outgoingHandle.y - node.y
                    if abs(dx) > 0.01 or abs(dy) > 0.01:
                        handles.append(f"out({dx:.1f},{dy:.1f})")

                if hasattr(node, 'incomingHandle') and node.incomingHandle:
                    dx = node.incomingHandle.x - node.x
                    dy = node.incomingHandle.y - node.y
                    if abs(dx) > 0.01 or abs(dy) > 0.01:
                        handles.append(f"in({dx:.1f},{dy:.1f})")

            except:
                pass

            if hasattr(node, 'type'):
                handles.append(f"type={node.type}")
            if hasattr(node, 'smooth') and node.smooth:
                handles.append("smooth")

            return ", ".join(handles) if handles else "line"

        # ADD handle count info (molt útil per debug)
        handle_count = self.countHandlesBetween(n1, n2)

        return f"[handles={handle_count} | n1:{node_handles(n1)} | n2:{node_handles(n2)}]"
        
        
        
    # -------------------------
    # SHOULD DISCARD
    # -------------------------
    def shouldDiscard(self, measured_width, expected_width):
        if expected_width == 0:
            return True
        difference_percent = abs(measured_width - expected_width) / expected_width * 100
        return difference_percent > self.discardPercent

    # -------------------------
    # ANALYZE SEGMENTS AT Y
    # -------------------------
    
    def isSemiVerticalSegment(self, n1, n2):
        """
        Detects semi-vertical segments:
        - ΔX < max_dx OR angle < max_angle_deg from vertical
        """
        dx = abs(n2.x - n1.x)
        dy = abs(n2.y - n1.y)
    
        if dy < 0.001:
            return False
        
        # Angle in degrees from vertical
        angle_deg = math.degrees(math.atan(dx / dy))
    
        return (dx < self.semiVerticalMaxDx) or (angle_deg < self.semiVerticalMaxAngle)
    
    def analyzeSegmentsAtY(self, layer, y):
        """
        Analyzes all segments intersecting at Y position
        """
        segments_info = []
        
        for path in layer.paths:
            nodes = path.nodes
            node_count = len(nodes)
            
            for i in range(node_count):
                n1 = nodes[i]
                n2 = nodes[(i + 1) % node_count]
                
                # Check intersection with Y line
                y_min = min(n1.y, n2.y)
                y_max = max(n1.y, n2.y)
                
                if y_min <= y <= y_max and y_max - y_min > 0.1:
                    if abs(n2.y - n1.y) > 0.001:
                        t = (y - n1.y) / (n2.y - n1.y)
                        x_intersect = n1.x + t * (n2.x - n1.x)
                        
                        # Detect segment type (curved or not)
                        is_curved = self.isCurvedSegment(n1, n2)
                        
                        curve_info = self.getSegmentTypeInfo(n1, n2) if is_curved else ""
                        
                        factor = 1.0
                        angle = 0.0
                        diag_type = ""
                        
                        # Determine stem type
                        if abs(n1.x - n2.x) < 0.1:  # Perfect vertical
                            stem_type = "curve_vertical" if is_curved else "vertical"
                        else:  # Diagonal or semi-vertical
                            factor, angle, diag_type = self.calculateDiagonalFactor(n1, n2)
                            
                            # ADD EXPLICIT SEMI-VERTICAL DEBUG MESSAGE
                            if diag_type == "semi_vertical" and self.reportMode == "full":
                                dx = abs(n2.x - n1.x)
                                dy = abs(n2.y - n1.y)
                                self.addToReport(
                                    f"  → Semi-vertical line detected! "
                                    f"ΔX = {dx:.2f} units, "
                                    f"Angle = {angle:.1f}° from vertical, "
                                    f"ΔY = {dy:.2f} units\n"
                                )
                            
                            if diag_type == "semi_vertical":
                                stem_type = "semi_vertical" if not is_curved else "curve_semi_vertical"
                            else:
                                stem_type = "curve_diagonal" if is_curved else f"diagonal_{diag_type}"
                        
                        segments_info.append({
                            'x': x_intersect,
                            'type': stem_type,
                            'is_curved': is_curved,
                            'factor': factor,
                            'angle': angle,
                            'diag_type': diag_type,
                            'curve_info': curve_info,
                            'n1': n1,
                            'n2': n2
                        })
        
        segments_info.sort(key=lambda s: s['x'])
        
        # Group stems
        stem_segments = []
        for i in range(0, len(segments_info)-1, 2):
            if i+1 < len(segments_info):
                left = segments_info[i]
                right = segments_info[i+1]
                width = right['x'] - left['x']
                
                # Determine type and expected_width
                if left['is_curved'] or right['is_curved']:
                    stem_type = "curve"
                    expected_base = self.curveWidth
                    tolerance = self.curveMargin
                elif "semi_vertical" in left['type'] or "semi_vertical" in right['type']:
                    stem_type = "semi_vertical"
                    expected_base = self.width
                    tolerance = self.diagonalMargin
                elif "diagonal" in left['type'] or "diagonal" in right['type']:
                    factor = min(left['factor'], right['factor'])
                    stem_type = "diagonal"
                    expected_base = self.width * factor
                    tolerance = self.diagonalMargin
                else:
                    stem_type = "vertical"
                    expected_base = self.width
                    tolerance = self.margin
                
                stem_segments.append({
                    'width': width,
                    'type': stem_type,
                    'left_info': left,
                    'right_info': right,
                    'expected': expected_base,
                    'tolerance': tolerance,
                    'x_center': (left['x'] + right['x']) / 2,
                    'factor': factor if 'factor' in locals() else 1.0,
                    'angle': left.get('angle', 0.0)
                })
        
        return stem_segments

    # -------------------------
    # CHECK GLYPH
    # -------------------------
    def checkGlyph(self, glyph, problem_glyphs_list):
        font = Glyphs.font
        master = font.selectedFontMaster.id
        layer = glyph.layers[master]

        glyph_has_problems = False
        stems_analyzed = 0
        stems_discarded = 0
        glyph_report = ""
        full_debug = (self.reportMode == "full")

        for y in self.yList:
            if not (layer.bounds.origin.y < y < layer.bounds.origin.y + layer.bounds.size.height):
                continue

            # Add header for this Y position in full debug mode
            if full_debug:
                glyph_report += f"\n{'='*70}\n"
                glyph_report += f"Glyph: {glyph.name}  |  Y Position: {y}\n"
                glyph_report += f"{'='*70}\n"

            stems = self.analyzeSegmentsAtY(layer, y)

            if not stems:
                if full_debug:
                    glyph_report += "  No stems detected at this Y position\n"
                continue

            for i, stem in enumerate(stems):
                stems_analyzed += 1
                
                is_discarded = self.shouldDiscard(stem['width'], stem['expected'])
                if is_discarded:
                    stems_discarded += 1
                
                # Build extra info for different stem types
                extra_info = ""
                if stem['type'] == 'diagonal' and full_debug:
                    extra_info = f" (factor={stem['factor']:.2f}, angle={stem['left_info']['angle']:.0f}°)"
                elif stem['type'] == 'semi_vertical' and full_debug:
                    dx = abs(stem['left_info']['n2'].x - stem['left_info']['n1'].x)
                    extra_info = f" (SEMI-VERTICAL: ΔX={dx:.2f}, angle={stem['angle']:.1f}° from vertical)"
                elif stem['type'] == 'curve' and full_debug:
                    # Show curve details
                    left_curve = stem['left_info'].get('curve_info', '')
                    right_curve = stem['right_info'].get('curve_info', '')
                    extra_info = f" (CURVED: left side [{left_curve}], right side [{right_curve}])"
                elif 'curve' in stem['type'] and full_debug:
                    extra_info = f" (curved segment: {stem['left_info'].get('curve_info', '')})"
                
                stem_line = f"  Stem {i+1}: width={stem['width']:.2f} (expected {stem['expected']:.2f}, type={stem['type']}, tolerance={stem['tolerance']}){extra_info}"
                
                if is_discarded:
                    if full_debug:
                        stem_line += f" (discarded >{self.discardPercent}%)"
                
                out_of_tolerance = abs(stem['width'] - stem['expected']) > stem['tolerance']
                
                if out_of_tolerance:
                    stem_line += f"\n    ⚠ OUT OF TOLERANCE"
                    if not is_discarded:
                        glyph_has_problems = True
                
                if full_debug:
                    glyph_report += stem_line + "\n"
                else:
                    if out_of_tolerance and not is_discarded:
                        if not glyph_report or f"Glyph: {glyph.name}" not in glyph_report:
                            glyph_report += f"\nGlyph: {glyph.name}  Y: {y}\n"
                        glyph_report += stem_line + "\n    ⚠ OUT OF TOLERANCE\n"

            if full_debug and stems_discarded > 0:
                glyph_report += f"  Total: {stems_analyzed} stems analyzed, {stems_discarded} discarded (>{self.discardPercent}% deviation)\n"

        if glyph_report:
            self.addToReport(glyph_report)

        if glyph_has_problems:
            problem_glyphs_list.append(glyph.name)

        return glyph_has_problems

    # -------------------------
    # ADD MEASUREMENT GUIDE
    # -------------------------
    def addMeasurementGuide(self, layer, y):
        guide = GSGuide()
        guide.position = NSPoint(0, y)
        guide.angle = 0
        try:
            guide.showMeasurement = True
        except AttributeError:
            try:
                guide.measurement = True
            except AttributeError:
                pass
        layer.guides.append(guide)

    # -------------------------
    # INSPECT
    # -------------------------
    def inspect(self, glyphs):
        font = Glyphs.font
        problem_glyphs = []

        for glyph in glyphs:
            try:
                self.checkGlyph(glyph, problem_glyphs)
            except Exception as e:
                self.addToReport(f"\nError in glyph {glyph.name}: {str(e)}\n")
                if self.reportMode == "full":
                    traceback.print_exc()

        if not problem_glyphs:
            self.addToReport("\nNo stem problems detected.\n")
            return

        glyphs_string = "/" + "/".join(problem_glyphs)
        tab = font.newTab(glyphs_string)
        for layer in tab.layers:
            for y in self.yList:
                self.addMeasurementGuide(layer, y)

                
    def countHandlesBetween(self, n1, n2):
        """
        Counts ONLY the handles that define the segment n1 → n2.
        This follows real Bézier logic:
        - n1.outgoingHandle
        - n2.incomingHandle
        """

        count = 0

        try:
            # outgoing handle from n1 (main control)
            if hasattr(n1, 'outgoingHandle') and n1.outgoingHandle:
                dx = n1.outgoingHandle.x - n1.x
                dy = n1.outgoingHandle.y - n1.y
                if abs(dx) > 0.01 or abs(dy) > 0.01:
                    count += 1

            # incoming handle to n2 (main control)
            if hasattr(n2, 'incomingHandle') and n2.incomingHandle:
                dx = n2.incomingHandle.x - n2.x
                dy = n2.incomingHandle.y - n2.y
                if abs(dx) > 0.01 or abs(dy) > 0.01:
                    count += 1

        except:
            pass

        return count
                
    # -------------------------
    # BUTTONS
    # -------------------------
    def inspectSelected(self, sender):
        font = Glyphs.font
        self.readUI()
        self.clearReportContent()

        glyphs = [l.parent for l in font.selectedLayers]
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.addToReport(f"--- Inspection {now} (DIAGONAL + SEMI-VERTICAL + CURVE FIX) ---\n")
        self.addToReport(f"Settings: Max ΔX={self.semiVerticalMaxDx}, Max Angle={self.semiVerticalMaxAngle}°\n\n")
        
        self.inspect(glyphs)


XBeamInspector()