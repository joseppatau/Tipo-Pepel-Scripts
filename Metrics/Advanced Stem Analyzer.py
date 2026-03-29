#MenuTitle: Advanced Stem Analyzer
# -*- coding: utf-8 -*-
# Description: Analyzes stem consistency across glyphs, detecting deviations in vertical, diagonal, and curved stems using tolerance-based evaluation.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import Glyphs, GSGuide
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

    def savePrefs(self):

        Glyphs.defaults[self.prefID+".width"] = self.width
        Glyphs.defaults[self.prefID+".curveWidth"] = self.curveWidth
        Glyphs.defaults[self.prefID+".margin"] = self.margin
        Glyphs.defaults[self.prefID+".diagonalMargin"] = self.diagonalMargin
        Glyphs.defaults[self.prefID+".curveMargin"] = self.curveMargin
        Glyphs.defaults[self.prefID+".discardPercent"] = self.discardPercent
        Glyphs.defaults[self.prefID+".yValues"] = self.yValues
        Glyphs.defaults[self.prefID+".reportMode"] = self.reportMode

    # -------------------------
    # UI
    # -------------------------

    def buildUI(self):

        self.w = vanilla.Window((520,500),"Advanced Stem Analyzer")

        self.w.text1 = vanilla.TextBox((15,15,100,20),"Target stem:")
        self.w.text1a = vanilla.TextBox((130,15,40,20),"Rect")
        self.w.width = vanilla.EditText((170,12,60,22),str(self.width))
        
        self.w.text1b = vanilla.TextBox((250,15,40,20),"Curve")
        self.w.curveWidth = vanilla.EditText((290,12,60,22),str(self.curveWidth))

        self.w.text2 = vanilla.TextBox((15,45,100,20),"Tolerance:")
        self.w.text2a = vanilla.TextBox((130,45,40,20),"Rect")
        self.w.margin = vanilla.EditText((170,42,60,22),str(self.margin))
        
        self.w.text2b = vanilla.TextBox((250,45,40,20),"Curve")
        self.w.curveMargin = vanilla.EditText((290,42,60,22),str(self.curveMargin))
        
        self.w.text2c = vanilla.TextBox((370,45,60,20),"Diagonals")
        self.w.diagonalMargin = vanilla.EditText((430,42,60,22),str(self.diagonalMargin))

        self.w.text3 = vanilla.TextBox((15,75,150,20),"Rule Out %: (ej: 30 = ±30%)")
        self.w.discardPercent = vanilla.EditText((170,72,60,22),str(self.discardPercent))

        self.w.text4 = vanilla.TextBox((15,105,150,20),"Xbeam positions:")
        self.w.yValues = vanilla.EditText((170,102,320,22),self.yValues)
        self.w.text4a = vanilla.TextBox((170,125,320,15),"Multiple lines, comma separated")

        self.w.inspectSel = vanilla.Button(
            (15,150,200,28),
            "Inspect selected glyphs",
            callback=self.inspectSelected
        )

        self.w.simpleReport = vanilla.CheckBox(
            (15,190,120,20),
            "Simple Report",
            value=(self.reportMode == "simple"),
            callback=self.toggleReportMode
        )
        
        self.w.fullReport = vanilla.CheckBox(
            (140,190,120,20),
            "Full Report",
            value=(self.reportMode == "full"),
            callback=self.toggleReportMode
        )

        self.w.reportLabel = vanilla.TextBox((15,220,100,20),"Report")
        self.w.reportText = vanilla.TextEditor(
            (15,240,490,200),
            text="",
            readOnly=True
        )

        self.w.clearReport = vanilla.Button(
            (15,450,120,22),
            "Clear Report",
            callback=self.clearReport
        )
        
        self.w.copyReport = vanilla.Button(
            (140,450,120,22),
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
                    self.addToReport(f"Advertencia: '{v}' no es un número válido, ignorando\n")
        
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
        
        if dy == 0:
            return 1.0, 0, "horizontal"
            
        angle = math.degrees(math.atan(abs(dx)/abs(dy)))
        rad = math.radians(angle)
        
        if dx * dy < 0:
            diagonalType = "\\"
            factor = 1 + 0.22 * math.sin(rad)
        else:
            diagonalType = "/"
            factor = 1 - 0.22 * math.sin(rad)
            
        return factor, angle, diagonalType

    # -------------------------
    # CHECK IF SEGMENT IS CURVED (mismo que script 1)
    # -------------------------

    def isCurvedSegment(self, n1, n2):
        """
        Detecta si un segmento tiene curvas verificando si alguno de los nodos
        tiene manejadores (handle) y no están en la posición por defecto
        """
        # Verificar si n1 tiene manejadores
        if hasattr(n1, 'connection') and n1.connection == OFFCURVE:
            return True
            
        # Verificar si n2 tiene manejadores
        if hasattr(n2, 'connection') and n2.connection == OFFCURVE:
            return True
            
        # Verificar si hay manejadores en las curvas Bezier
        if hasattr(n1, 'position') and hasattr(n2, 'position'):
            if hasattr(n1, 'type') and n1.type == CURVE:
                return True
            if hasattr(n2, 'type') and n2.type == CURVE:
                return True
                
        if hasattr(n1, 'hasHandle') and n1.hasHandle():
            return True
        if hasattr(n2, 'hasHandle') and n2.hasHandle():
            return True
            
        return False

    # -------------------------
    # SHOULD DISCARD
    # -------------------------
    
    def shouldDiscard(self, measured_width, expected_width):
        if expected_width == 0:
            return True
            
        difference_percent = abs(measured_width - expected_width) / expected_width * 100
        return difference_percent > self.discardPercent

    # -------------------------
    # ANALYZE SEGMENTS AT Y (mismo que script 1)
    # -------------------------

    def analyzeSegmentsAtY(self, layer, y):
        layer = layer.copyDecomposedLayer()
        layer.removeOverlap()
        
        segments_info = []
        
        for path in layer.paths:
            nodes = path.nodes
            for i in range(len(nodes)):
                n1 = nodes[i]
                n2 = nodes[(i + 1) % len(nodes)]
                
                y_min = min(n1.y, n2.y)
                y_max = max(n1.y, n2.y)
                
                if y_min <= y <= y_max and y_max - y_min > 0.1:
                    if n2.y != n1.y:
                        t = (y - n1.y) / (n2.y - n1.y)
                        x_intersect = n1.x + t * (n2.x - n1.x)
                        
                        is_curved = self.isCurvedSegment(n1, n2)
                        
                        factor = 1.0
                        angle = 0
                        diag_type = ""
                        
                        if abs(n1.x - n2.x) < 0.1:
                            if is_curved:
                                stem_type = "curve_vertical"
                            else:
                                stem_type = "vertical"
                        else:
                            factor, angle, diag_type = self.calculateDiagonalFactor(n1, n2)
                            
                            if is_curved:
                                stem_type = "curve_diagonal"
                            else:
                                stem_type = f"diagonal_{diag_type}"
                        
                        segments_info.append({
                            'x': x_intersect,
                            'type': stem_type,
                            'is_curved': is_curved,
                            'factor': factor,
                            'angle': angle,
                            'diag_type': diag_type,
                            'n1': n1,
                            'n2': n2
                        })
        
        segments_info.sort(key=lambda s: s['x'])
        
        stem_segments = []
        for i in range(0, len(segments_info)-1, 2):
            if i+1 < len(segments_info):
                left = segments_info[i]
                right = segments_info[i+1]
                width = right['x'] - left['x']
                
                # CRUCIAL: La misma lógica que el script 1
                if left['is_curved'] or right['is_curved']:
                    stem_type = "curve"
                    expected_base = self.curveWidth
                    tolerance = self.curveMargin
                elif "diagonal" in left['type'] or "diagonal" in right['type']:
                    stem_type = "diagonal"
                    expected_base = self.width * left['factor']
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
                    'y': y
                })
        
        return stem_segments

    # -------------------------
    # STEM TEST - VERTICAL
    # -------------------------

    def checkGlyphVertical(self, glyph, problem_dict):
        font = Glyphs.font
        master = font.selectedFontMaster.id
        layer = glyph.layers[master]
        
        glyph_details = []
        
        for y in self.yList:
            if not (layer.bounds.origin.y < y < layer.bounds.origin.y + layer.bounds.size.height):
                continue
                
            stems = self.analyzeSegmentsAtY(layer, y)
            
            for stem in stems:
                if stem['type'] != "vertical":
                    continue
                    
                out_of_tolerance = abs(stem['width'] - stem['expected']) > stem['tolerance']
                is_discarded = self.shouldDiscard(stem['width'], stem['expected'])
                
                if out_of_tolerance and not is_discarded:
                    glyph_details.append({
                        'y': stem['y'],
                        'width': stem['width'],
                        'expected': stem['expected'],
                        'tolerance': stem['tolerance']
                    })
        
        if glyph_details:
            problem_dict[glyph.name] = glyph_details
        
        return len(glyph_details) > 0

    # -------------------------
    # STEM TEST - CURVE (usando misma lógica que script 1)
    # -------------------------

    def checkGlyphCurve(self, glyph, problem_dict):
        font = Glyphs.font
        master = font.selectedFontMaster.id
        layer = glyph.layers[master]
        
        glyph_details = []
        stems_analyzed = 0
        stems_discarded = 0
        
        for y in self.yList:
            if not (layer.bounds.origin.y < y < layer.bounds.origin.y + layer.bounds.size.height):
                continue
                
            stems = self.analyzeSegmentsAtY(layer, y)
            
            for stem in stems:
                if stem['type'] != "curve":
                    continue
                    
                stems_analyzed += 1
                is_discarded = self.shouldDiscard(stem['width'], stem['expected'])
                
                if is_discarded:
                    stems_discarded += 1
                
                out_of_tolerance = abs(stem['width'] - stem['expected']) > stem['tolerance']
                
                if out_of_tolerance and not is_discarded:
                    glyph_details.append({
                        'y': stem['y'],
                        'width': stem['width'],
                        'expected': stem['expected'],
                        'tolerance': stem['tolerance']
                    })
        
        if glyph_details:
            problem_dict[glyph.name] = glyph_details
        
        return len(glyph_details) > 0

    # -------------------------
    # STEM TEST - DIAGONAL
    # -------------------------

    def checkGlyphDiagonal(self, glyph, problem_dict):
        font = Glyphs.font
        master = font.selectedFontMaster.id
        layer = glyph.layers[master]
        
        glyph_details = []
        
        for y in self.yList:
            if not (layer.bounds.origin.y < y < layer.bounds.origin.y + layer.bounds.size.height):
                continue
                
            stems = self.analyzeSegmentsAtY(layer, y)
            
            for stem in stems:
                if stem['type'] != "diagonal":
                    continue
                    
                out_of_tolerance = abs(stem['width'] - stem['expected']) > stem['tolerance']
                is_discarded = self.shouldDiscard(stem['width'], stem['expected'])
                
                if out_of_tolerance and not is_discarded:
                    glyph_details.append({
                        'y': stem['y'],
                        'width': stem['width'],
                        'expected': stem['expected'],
                        'tolerance': stem['tolerance']
                    })
        
        if glyph_details:
            problem_dict[glyph.name] = glyph_details
        
        return len(glyph_details) > 0

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
    # OPEN UNIFIED TAB
    # -------------------------

    def openUnifiedTab(self, vertical_dict, curve_dict, diagonal_dict):
        font = Glyphs.font
        tab_content = "=== STEM ANALYSIS REPORT ===\n\n"
        
        tab_content += "=== VERTICAL STEMS ===\n"
        if vertical_dict:
            glyphs_list = []
            for glyph_name in vertical_dict.keys():
                glyphs_list.append(f"/{glyph_name}")
            tab_content += " ".join(glyphs_list) + "\n\n"
        else:
            tab_content += "No problems detected.\n\n"
        
        tab_content += "=== CURVED STEMS ===\n"
        if curve_dict:
            glyphs_list = []
            for glyph_name in curve_dict.keys():
                glyphs_list.append(f"/{glyph_name}")
            tab_content += " ".join(glyphs_list) + "\n\n"
        else:
            tab_content += "No problems detected.\n\n"
        
        tab_content += "=== DIAGONAL STEMS ===\n"
        if diagonal_dict:
            glyphs_list = []
            for glyph_name in diagonal_dict.keys():
                glyphs_list.append(f"/{glyph_name}")
            tab_content += " ".join(glyphs_list) + "\n"
        else:
            tab_content += "No problems detected.\n"
        
        tab = font.newTab(tab_content)
        
        for layer in tab.layers:
            for y in self.yList:
                self.addMeasurementGuide(layer, y)

    # -------------------------
    # INSPECT
    # -------------------------

    def inspect(self, glyphs):
        
        vertical_problems = {}
        curve_problems = {}
        diagonal_problems = {}
        
        for glyph in glyphs:
            try:
                self.checkGlyphVertical(glyph, vertical_problems)
                self.checkGlyphCurve(glyph, curve_problems)
                self.checkGlyphDiagonal(glyph, diagonal_problems)
                    
            except Exception as e:
                self.addToReport(f"\nError en glyph {glyph.name}: {str(e)}\n")
                if self.reportMode == "full":
                    traceback.print_exc()
        
        self.addToReport(f"\n--- RESULTADOS ---\n")
        
        self.addToReport(f"\n=== VERTICAL STEMS ===\n")
        if vertical_problems:
            self.addToReport(f"Glifos con problemas: {len(vertical_problems)}\n")
            for glyph_name, details in vertical_problems.items():
                self.addToReport(f"\n/{glyph_name}\n")
                for d in details:
                    self.addToReport(f"  Y={d['y']}: ancho={d['width']:.2f} (esperado={d['expected']:.2f}, tolerancia={d['tolerance']})\n")
        else:
            self.addToReport("No se detectaron problemas.\n")
        
        self.addToReport(f"\n=== CURVED STEMS ===\n")
        if curve_problems:
            self.addToReport(f"Glifos con problemas: {len(curve_problems)}\n")
            for glyph_name, details in curve_problems.items():
                self.addToReport(f"\n/{glyph_name}\n")
                for d in details:
                    self.addToReport(f"  Y={d['y']}: ancho={d['width']:.2f} (esperado={d['expected']:.2f}, tolerancia={d['tolerance']})\n")
        else:
            self.addToReport("No se detectaron problemas.\n")
        
        self.addToReport(f"\n=== DIAGONAL STEMS ===\n")
        if diagonal_problems:
            self.addToReport(f"Glifos con problemas: {len(diagonal_problems)}\n")
            for glyph_name, details in diagonal_problems.items():
                self.addToReport(f"\n/{glyph_name}\n")
                for d in details:
                    self.addToReport(f"  Y={d['y']}: ancho={d['width']:.2f} (esperado={d['expected']:.2f}, tolerancia={d['tolerance']})\n")
        else:
            self.addToReport("No se detectaron problemas.\n")
        
        if len(vertical_problems) == 0 and len(curve_problems) == 0 and len(diagonal_problems) == 0:
            self.addToReport("\nNo stem problems detected.\n")
            return
        
        self.addToReport(f"\n→ Abriendo tab con glifos problemáticos...\n")
        self.openUnifiedTab(vertical_problems, curve_problems, diagonal_problems)

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
        self.addToReport(f"--- Inspección {now} ---\n")
        
        self.inspect(glyphs)


XBeamInspector()