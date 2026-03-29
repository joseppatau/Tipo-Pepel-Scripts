# MenuTitle: Pattern Fill Engine
# -*- coding: utf-8 -*-
# Description: Fills glyph shapes with scalable and repeatable patterns using custom glyphs and grid-based tiling.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
import math
import objc
from GlyphsApp import *
from Foundation import NSAffineTransform, NSPoint
from AppKit import NSView, NSColor, NSBezierPath, NSAffineTransform, NSInsetRect
import time
from vanilla.vanillaBase import VanillaBaseObject


# ------------------------------------------------------------
# UTILIDAD BOUNDS
# ------------------------------------------------------------
def getRealBounds(layer):
    if not layer.paths:
        return None
    
    first = True
    minX = minY = maxX = maxY = 0
    
    for path in layer.paths:
        for node in path.nodes:
            x = node.position.x
            y = node.position.y
            if first:
                minX = maxX = x
                minY = maxY = y
                first = False
            else:
                minX = min(minX, x)
                minY = min(minY, y)
                maxX = max(maxX, x)
                maxY = max(maxY, y)
    
    if first:
        return None
    
    return (minX, minY, maxX - minX, maxY - minY)


# ------------------------------------------------------------
# PREVIEW VIEW DUAL (original + resultado)
# ------------------------------------------------------------
if 'DualPatternPreview' not in globals():

    class DualPatternPreview(NSView):

        def initWithFrame_(self, frame):
            self = objc.super(DualPatternPreview, self).initWithFrame_(frame)
            if self is None:
                return None
            self.originalLayer = None
            self.resultLayer = None
            return self

        def setOriginalLayer_resultLayer_(self, original, result):
            self.originalLayer = original
            self.resultLayer = result
            self.setNeedsDisplay_(True)

        def drawRect_(self, rect):
            # Fondo blanco
            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())
            
            # Borde gris
            NSColor.grayColor().set()
            NSBezierPath.strokeRect_(self.bounds())
            
            w = self.bounds().size.width
            h = self.bounds().size.height
            
            # Dibujar original en gris claro
            if self.originalLayer:
                try:
                    path = self.originalLayer.bezierPath
                    if path and path.elementCount() > 0:
                        bounds = path.bounds()
                        if bounds.size.width > 0 and bounds.size.height > 0:
                            scale = min((w-40)/bounds.size.width, (h-40)/bounds.size.height)
                            if scale > 0:
                                t = NSAffineTransform.transform()
                                t.translateXBy_yBy_(w/2, h/2)
                                t.scaleBy_(scale)
                                t.translateXBy_yBy_(-bounds.origin.x - bounds.size.width/2,
                                                    -bounds.origin.y - bounds.size.height/2)
                                
                                p = path.copy()
                                p.transformUsingAffineTransform_(t)
                                
                                NSColor.lightGrayColor().colorWithAlphaComponent_(0.3).set()
                                p.fill()
                except:
                    pass
            
            # Dibujar resultado en negro
            if self.resultLayer:
                try:
                    path = self.resultLayer.bezierPath
                    if path and path.elementCount() > 0:
                        bounds = path.bounds()
                        if bounds.size.width > 0 and bounds.size.height > 0:
                            scale = min((w-40)/bounds.size.width, (h-40)/bounds.size.height)
                            if scale > 0:
                                t = NSAffineTransform.transform()
                                t.translateXBy_yBy_(w/2, h/2)
                                t.scaleBy_(scale)
                                t.translateXBy_yBy_(-bounds.origin.x - bounds.size.width/2,
                                                    -bounds.origin.y - bounds.size.height/2)
                                
                                p = path.copy()
                                p.transformUsingAffineTransform_(t)
                                
                                NSColor.blackColor().set()
                                p.fill()
                except:
                    pass


# ------------------------------------------------------------
# VANILLA WRAPPER
# ------------------------------------------------------------
class NSViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView
    
    def getNSView(self):
        return self._nsObject


# ------------------------------------------------------------
# PATTERN ROW (con incremento de rotación)
# ------------------------------------------------------------
class PatternRow(object):
    
    HEIGHT = 85
    
    def __init__(self, parent, y, index):
        self.parent = parent
        self.index = index
        
        self.group = vanilla.Group((0, y, 560, self.HEIGHT))
        
        # Fila 1
        self.group.patternLabel = vanilla.TextBox((10, 5, 55, 20), "Pattern:")
        self.group.pattern = vanilla.EditText((75, 2, 120, 22), "")
        
        self.group.scaleLabel = vanilla.TextBox((210, 5, 65, 20), "Scale:")
        self.group.scale = vanilla.EditText((260, 2, 40, 22), "100")
        
        self.group.rotLabel = vanilla.TextBox((320, 5, 60, 20), "Rotate:")
        self.group.rotation = vanilla.EditText((370, 2, 40, 22), "0")
        
        # Incremento de rotación
        self.group.incLabel = vanilla.TextBox((425, 5, 30, 20), "Incº:")
        self.group.increment = vanilla.EditText((455, 2, 40, 22), "0")
        
        # Fila 2
        self.group.offXLabel = vanilla.TextBox((10, 35, 90, 20), "Offset  X:")
        self.group.offX = vanilla.EditText((75, 32, 40, 22), "0")
        
        self.group.offYLabel = vanilla.TextBox((130, 35, 20, 20), "Y:")
        self.group.offY = vanilla.EditText((150, 32, 40, 22), "0")
        
        # Márgenes
        self.group.marginLabel = vanilla.TextBox((210, 35, 65, 20), "Margin:")
        
        self.group.mULabel = vanilla.TextBox((260, 35, 50, 20), "U↑")
        self.group.mU = vanilla.EditText((282, 32, 40, 22), "0")
        
        self.group.mDLabel = vanilla.TextBox((325, 35, 50, 20), "D↓")
        self.group.mD = vanilla.EditText((348, 32, 40, 22), "0")
        
        self.group.mLLabel = vanilla.TextBox((390, 35, 50, 20), "←L")
        self.group.mL = vanilla.EditText((415, 32, 40, 22), "0")
        
        self.group.mRLabel = vanilla.TextBox((455, 35, 50, 20), "R→")
        self.group.mR = vanilla.EditText((480, 32, 40, 22), "0")
        
        # Botón eliminar
        self.group.delete = vanilla.Button((530, 15, 25, 22), "✕",
                                           callback=self.delete)
        
        # Línea separadora
        self.group.line = vanilla.HorizontalLine((10, 65, 530, 1))
    
    def delete(self, sender):
        self.parent.removePattern(self.index)
    
    def values(self):
        try:
            return {
                "pattern": self.group.pattern.get().strip(),
                "scale": float(self.group.scale.get())/100.0,
                "rotation": float(self.group.rotation.get()),
                "increment": float(self.group.increment.get()),
                "offsetX": float(self.group.offX.get()),
                "offsetY": float(self.group.offY.get()),
                "marginUp": float(self.group.mU.get()),
                "marginDown": float(self.group.mD.get()),
                "marginLeft": float(self.group.mL.get()),
                "marginRight": float(self.group.mR.get())
            }
        except:
            return None


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
class PatternFillerPro(object):
    
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("Error", "Please open a font first")
            return
        
        self.patternRows = []
        
        # Obtener lista de masters
        self.master_names = [m.name for m in self.font.masters]
        self.master_ids = [m.id for m in self.font.masters]
        
        # Ventana
        self.w = vanilla.FloatingWindow((620, 780), "Pattern Filler Pro MULTI")
        
        y = 10
        
        # ScrollView
        self.w.scroll = vanilla.ScrollView(
            (15, y, -15, 280),
            None,
            hasVerticalScroller=True
        )
        
        self.scrollContent = vanilla.Group((0, 0, 580, 0))
        self.w.scroll.getNSScrollView().setDocumentView_(
            self.scrollContent.getNSView()
        )
        y += 295
        
        # Botón añadir patrón
        self.w.addButton = vanilla.Button((15, y, 120, 24), 
                                          "+ Add Pattern", 
                                          callback=self.addPattern)
        y += 40
        
        # Desplegable para master
        self.w.masterLabel = vanilla.TextBox((15, 350, 80, 24), "Master:")
        self.w.masterPopup = vanilla.PopUpButton((70, 350, 150, 24), 
                                                 self.master_names,
                                                 callback=self._master_changed)
        y += 40        
        # Campo para excluir glifos
        self.w.excludeLabel = vanilla.TextBox((15, y, 100, 24), "Exclude glyphs:")
        self.w.excludeGlyphs = vanilla.EditText((115, y-3, 200, 22), 
                                                "", 
                                                placeholder="ej: a, e, i, o, u")
        y += 40
        
        # Desplegable para ámbito de aplicación
        self.w.scopeLabel = vanilla.TextBox((240, 350, 80, 24), "Apply to:")
        self.w.scopePopup = vanilla.PopUpButton((310, 350, 150, 24), 
                                                ["Current Glyph", "Selected Glyphs", "Entire Font"],
                                                callback=None)
        y += 40
        
        self.w.previewButton = vanilla.Button((15, 430, 150, 24), 
                                              "Update Preview", 
                                              callback=self.update_preview)
        self.w.applyButton = vanilla.Button((180, 430, -15, 24), 
                                            "Apply", 
                                            callback=self.apply)
        y += 40
        
        # Preview dual (original + resultado)
        self.w.previewLabel = vanilla.TextBox((15, 470, -15, 20), 
                                              "Preview (light gray = original, black = result)")
        y += 25
        
        self.previewView = DualPatternPreview.alloc().initWithFrame_(((0, 0), (580, 240)))
        self.w.previewBox = NSViewWrapper((15, 495, -15, 240), self.previewView)
        y += 185
        
        # Status
        self.w.status = vanilla.TextBox((15, 750, -15, 20), "Ready")
        
        # Seleccionar master actual por defecto
        current_master = self.font.selectedFontMaster
        if current_master and current_master.id in self.master_ids:
            default_index = self.master_ids.index(current_master.id)
            self.w.masterPopup.set(default_index)
        
        # Primer patrón
        self.addPattern()
        
        self.w.open()
    
    def _master_changed(self, sender=None):
        """Actualizar el preview cuando cambia el master"""
        self.update_preview()
    
    def addPattern(self, sender=None):
        index = len(self.patternRows)
        y = index * PatternRow.HEIGHT
        
        row = PatternRow(self, y, index)
        setattr(self.scrollContent, f"row{index}", row.group)
        
        self.patternRows.append(row)
        self.scrollContent.setPosSize((0, 0, 580, (index+1) * PatternRow.HEIGHT))
        self.w.status.set(f"{index+1} pattern(s)")
    
    def removePattern(self, index):
        if len(self.patternRows) <= 1:
            return
        
        del self.patternRows[index]
        
        # Reconstruir
        for attr in dir(self.scrollContent):
            if attr.startswith("row"):
                delattr(self.scrollContent, attr)
        
        for i, row in enumerate(self.patternRows):
            row.index = i
            row.group.setPosSize((0, i * PatternRow.HEIGHT, 580, PatternRow.HEIGHT))
            setattr(self.scrollContent, f"row{i}", row.group)
        
        self.scrollContent.setPosSize(
            (0, 0, 580, len(self.patternRows) * PatternRow.HEIGHT)
        )
        self.w.status.set(f"{len(self.patternRows)} pattern(s)")
    
    def get_all_pattern_values(self):
        values = []
        for row in self.patternRows:
            vals = row.values()
            if vals and vals['pattern']:
                values.append(vals)
        return values
    
    def get_excluded_glyphs(self):
        """Obtener lista de glifos excluidos"""
        exclude_text = self.w.excludeGlyphs.get().strip()
        if not exclude_text:
            return []
        
        # Separar por comas y limpiar espacios
        excluded = [g.strip() for g in exclude_text.split(',')]
        return [g for g in excluded if g]
    
    def is_glyph_excluded(self, glyph_name):
        """Comprobar si un glifo está excluido"""
        excluded = self.get_excluded_glyphs()
        return glyph_name in excluded
    
    def get_selected_master(self):
        """Obtener el master seleccionado en el desplegable"""
        idx = self.w.masterPopup.get()
        if 0 <= idx < len(self.font.masters):
            return self.font.masters[idx]
        return self.font.selectedFontMaster
    
    def generate_for_layer(self, layer, master):
        """Genera el patrón para una capa específica usando el master seleccionado"""
        pattern_values = self.get_all_pattern_values()
        
        if not pattern_values:
            return None
        
        originalCopy = layer.copy()
        origBounds = getRealBounds(originalCopy)
        if not origBounds:
            return None
        
        # Capa temporal para combinar todos los patrones
        combinedLayer = GSLayer()
        combinedLayer.width = layer.width
        
        # Procesar cada patrón por separado
        for p_values in pattern_values:
            try:
                patternGlyph = self.font.glyphs[p_values['pattern']]
                if not patternGlyph:
                    continue
                
                # Usar el master seleccionado para obtener el patrón
                basePatternLayer = patternGlyph.layers[master.id]
                
                bounds = getRealBounds(basePatternLayer)
                if not bounds:
                    continue
                px, py, pw, ph = bounds
                
                origX, origY, origW, origH = origBounds
                
                # Calcular tamaño del tile con márgenes
                tileTotalW = pw + p_values['marginLeft'] + p_values['marginRight']
                tileTotalH = ph + p_values['marginUp'] + p_values['marginDown']
                
                # Escalar el tamaño del tile
                if p_values['scale'] != 1.0:
                    tileTotalW *= p_values['scale']
                    tileTotalH *= p_values['scale']
                
                # Calcular rango de celdas
                startCol = int(math.floor((origX - p_values['offsetX']) / tileTotalW)) - 1
                endCol = int(math.ceil((origX + origW - p_values['offsetX']) / tileTotalW)) + 1
                
                startRow = int(math.floor((origY - p_values['offsetY']) / tileTotalH)) - 1
                endRow = int(math.ceil((origY + origH - p_values['offsetY']) / tileTotalH)) + 1
                
                # PASO 1: Generar tiles con INCREMENTO de rotación (si existe)
                patternTempLayer = GSLayer()
                patternTempLayer.width = layer.width
                
                for col in range(startCol, endCol + 1):
                    for row in range(startRow, endRow + 1):
                        tileLayer = basePatternLayer.copy()
                        
                        if tileLayer.components:
                            tileLayer.decomposeComponents()
                        
                        tileLayer.removeOverlap()
                        
                        # Normalizar (mover a origen)
                        normalize = NSAffineTransform.transform()
                        normalize.translateXBy_yBy_(-px, -py)
                        tileLayer.applyTransform(normalize.transformStruct())
                        
                        # Aplicar márgenes (desplazar dentro del tile)
                        if (p_values['marginLeft'] > 0 or p_values['marginRight'] > 0 or 
                            p_values['marginUp'] > 0 or p_values['marginDown'] > 0):
                            marginMove = NSAffineTransform.transform()
                            marginMove.translateXBy_yBy_(p_values['marginLeft'], p_values['marginDown'])
                            tileLayer.applyTransform(marginMove.transformStruct())
                        
                        # Escalar
                        if p_values['scale'] != 1.0:
                            scale = NSAffineTransform.transform()
                            scale.scaleBy_(p_values['scale'])
                            tileLayer.applyTransform(scale.transformStruct())
                        
                        # Posicionar en la cuadrícula
                        move = NSAffineTransform.transform()
                        move.translateXBy_yBy_(
                            origX + col * tileTotalW + p_values['offsetX'],
                            origY + row * tileTotalH + p_values['offsetY']
                        )
                        tileLayer.applyTransform(move.transformStruct())
                        
                        # APLICAR INCREMENTO DE ROTACIÓN (rotación individual por tile)
                        if p_values['increment'] != 0.0:
                            tileAngle = (abs(col) + abs(row)) * p_values['increment']
                            
                            if tileAngle != 0.0:
                                tileBounds = getRealBounds(tileLayer)
                                if tileBounds:
                                    tileCenterX = tileBounds[0] + tileBounds[2]/2
                                    tileCenterY = tileBounds[1] + tileBounds[3]/2
                                    
                                    rotate = NSAffineTransform.transform()
                                    rotate.translateXBy_yBy_(tileCenterX, tileCenterY)
                                    rotate.rotateByDegrees_(tileAngle)
                                    rotate.translateXBy_yBy_(-tileCenterX, -tileCenterY)
                                    
                                    tileLayer.applyTransform(rotate.transformStruct())
                        
                        for path in tileLayer.paths:
                            patternTempLayer.paths.append(path.copy())
                
                # PASO 2: Aplicar rotación GENERAL a todo el patrón
                if p_values['rotation'] != 0.0:
                    centerX = origX + origW / 2.0
                    centerY = origY + origH / 2.0
                    
                    rotate = NSAffineTransform.transform()
                    rotate.translateXBy_yBy_(centerX, centerY)
                    rotate.rotateByDegrees_(p_values['rotation'])
                    rotate.translateXBy_yBy_(-centerX, -centerY)
                    
                    patternTempLayer.applyTransform(rotate.transformStruct())
                
                # Añadir los paths de este patrón a la capa combinada
                for path in patternTempLayer.paths:
                    combinedLayer.paths.append(path.copy())
                
            except Exception as e:
                print(f"Error procesando patrón: {e}")
                continue
        
        resultLayer = layer.copy()
        resultLayer.clear()
        
        for path in combinedLayer.paths:
            resultLayer.paths.append(path.copy())
        
        resultLayer.removeOverlap()
        
        if resultLayer.paths:
            try:
                resultLayer.pathIntersect_from_error_(
                    list(resultLayer.paths),
                    list(originalCopy.paths),
                    None
                )
                resultLayer.removeOverlap()
            except:
                pass
        
        return resultLayer
    
    def generate_preview_layer(self):
        """Genera una capa de preview (solo para la capa seleccionada)"""
        if not self.font or not self.font.selectedLayers:
            return None
        
        layer = self.font.selectedLayers[0]
        master = self.get_selected_master()
        return self.generate_for_layer(layer, master)
    
    def update_preview(self, sender=None):
        start = time.time()
        
        if not self.font or not self.font.selectedLayers:
            self.w.status.set("Error: No layer selected")
            return
        
        layer = self.font.selectedLayers[0]
        result = self.generate_preview_layer()
        
        if result:
            self.previewView.setOriginalLayer_resultLayer_(layer, result)
            elapsed = (time.time() - start) * 1000
            self.w.status.set(f"Preview updated in {elapsed:.1f}ms")
        else:
            self.w.status.set("Error generating preview")
    
    def apply(self, sender):
        start = time.time()
        
        if not self.font:
            Message("Error", "No font open")
            return
        
        # Obtener el master seleccionado
        selected_master = self.get_selected_master()
        selected_master_id = selected_master.id
        
        # Obtener lista de patrones para verificar exclusiones
        pattern_values = self.get_all_pattern_values()
        pattern_names = [p['pattern'] for p in pattern_values if p and p['pattern']]
        
        # Obtener el ámbito seleccionado
        scope_index = self.w.scopePopup.get()
        scope_options = ["current", "selected", "all"]
        scope = scope_options[scope_index]
        
        layers_to_process = []
        
        if scope == "current":
            # Solo la capa seleccionada actualmente, pero solo si es del master seleccionado
            if not self.font.selectedLayers:
                Message("Error", "No layer selected")
                return
            
            # Buscar la capa del master seleccionado en el glifo actual
            current_layer = self.font.selectedLayers[0]
            glyph = current_layer.parent
            
            # Obtener la capa específica del master seleccionado
            target_layer = glyph.layers[selected_master_id]
            if target_layer:
                layers_to_process = [target_layer]
            else:
                Message("Error", f"Master '{selected_master.name}' not found in current glyph")
                return
            
        elif scope == "selected":
            # Todas las capas seleccionadas, pero solo las del master seleccionado
            if not self.font.selectedLayers:
                Message("Error", "No layers selected")
                return
            
            # Para cada capa seleccionada, obtener su glifo y luego la capa del master seleccionado
            processed_glyphs = set()  # Para evitar duplicados
            
            for layer in self.font.selectedLayers:
                glyph = layer.parent
                if glyph.name in processed_glyphs:
                    continue
                
                target_layer = glyph.layers[selected_master_id]
                if target_layer and not self.is_glyph_excluded(glyph.name):
                    layers_to_process.append(target_layer)
                    processed_glyphs.add(glyph.name)
            
        elif scope == "all":
            # Toda la fuente, solo los masters seleccionados
            for glyph in self.font.glyphs:
                if not self.is_glyph_excluded(glyph.name):
                    target_layer = glyph.layers[selected_master_id]
                    if target_layer:
                        layers_to_process.append(target_layer)
        
        if not layers_to_process:
            Message("Error", "No layers to process (all excluded or master not found)")
            return
        
        # Procesar cada capa
        processed_count = 0
        skipped_count = 0
        
        for layer in layers_to_process:
            glyph_name = layer.parent.name
            
            # Verificar si es un patrón (para no perderlo)
            if glyph_name in pattern_names:
                skipped_count += 1
                continue
            
            try:
                result = self.generate_for_layer(layer, selected_master)
                if result:
                    # Guardar el width original
                    original_width = layer.width
                    
                    # Guardar anchors originales
                    anchors_to_keep = []
                    for anchor in layer.anchors:
                        anchors_to_keep.append({
                            'name': anchor.name,
                            'x': anchor.x,
                            'y': anchor.y
                        })
                    
                    # Guardar componentes si existen
                    components_to_keep = []
                    if hasattr(layer, 'components') and layer.components:
                        for component in layer.components:
                            components_to_keep.append(component.copy())
                    
                    # Limpiar SOLO los paths
                    layer.shapes = [p.copy() for p in result.paths]
                    
                    # Restaurar el width original (NO modificar métricas)
                    layer.width = original_width
                    
                    # Restaurar anchors
                    for anchor_data in anchors_to_keep:
                        new_anchor = GSAnchor()
                        new_anchor.name = anchor_data['name']
                        new_anchor.position = NSPoint(anchor_data['x'], anchor_data['y'])
                        layer.anchors.append(new_anchor)
                    
                    # Restaurar componentes
                    for component in components_to_keep:
                        layer.components.append(component)
                    
                    layer.removeOverlap()
                    # NO llamar a syncMetrics() para no modificar métricas
                    
                    processed_count += 1
            except Exception as e:
                print(f"Error processing layer {glyph_name}: {e}")
                skipped_count += 1
        
        elapsed = (time.time() - start) * 1000
        
        # Actualizar preview con la primera capa procesada (si existe)
        if self.font.selectedLayers:
            first_glyph = self.font.selectedLayers[0].parent
            if not self.is_glyph_excluded(first_glyph.name):
                first_layer = first_glyph.layers[selected_master_id]
                if first_layer:
                    result = self.generate_for_layer(first_layer, selected_master)
                    if result:
                        # Para el preview, también preservamos width y anchors
                        original_width = first_layer.width
                        
                        anchors_to_keep = []
                        for anchor in first_layer.anchors:
                            anchors_to_keep.append({
                                'name': anchor.name,
                                'x': anchor.x,
                                'y': anchor.y
                            })
                        
                        # Crear capa de preview con los paths del resultado
                        preview_result = GSLayer()
                        preview_result.width = original_width
                        preview_result.shapes = [p.copy() for p in result.paths]
                        
                        for anchor_data in anchors_to_keep:
                            new_anchor = GSAnchor()
                            new_anchor.name = anchor_data['name']
                            new_anchor.position = NSPoint(anchor_data['x'], anchor_data['y'])
                            preview_result.anchors.append(new_anchor)
                        
                        self.previewView.setOriginalLayer_resultLayer_(first_layer, preview_result)
        
        msg = f"Applied to {processed_count} layer(s) in {selected_master.name}"
        if skipped_count > 0:
            msg += f", skipped {skipped_count} pattern glyphs"
        msg += f" in {elapsed:.1f}ms"
        
        Glyphs.showNotification("Pattern Filler", msg)
        self.w.status.set(msg)


PatternFillerPro()