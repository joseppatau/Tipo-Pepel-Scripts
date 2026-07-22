# MenuTitle: Guides Manager
# -*- coding: utf-8 -*-
# Description: Creates and manages horizontal zones with visual overlays and node-edge highlighting for precise vertical control.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
from AppKit import NSPoint
import vanilla
import math

class GuideManager(object):

    def __init__(self):
        self.w = vanilla.FloatingWindow((340, 360), "Guides Manager")

        # --- TOP ---
        self.w.createButton = vanilla.Button(
            (10, 10, -10, 25),
            "Create Guide from Selection",
            callback=self.createGuide
        )

        self.w.clearButton = vanilla.Button(
            (10, 45, -10, 25),
            "Clear Guides",
            callback=self.clearGuides
        )

        self.w.allMasters = vanilla.CheckBox(
            (10, 80, -10, 20),
            "All Masters",
            value=False
        )

        self.w.measurement = vanilla.CheckBox(
            (10, 105, -10, 20),
            "Measurement Guide",
            value=True
        )

        self.w.globalGuides = vanilla.CheckBox(
            (10, 130, -10, 20),
            "Make Global Guides",
            value=False
        )

        # --- SEPARATOR ---
        self.w.sep = vanilla.HorizontalLine((10, 155, -10, 1))

        # --- TRANSFER SECTION ---
        self.w.transferLabel = vanilla.TextBox(
            (10, 165, -10, 20),
            "Transfer guides"
        )

        self.w.charInput = vanilla.EditText(
            (10, 190, 120, 22),
            placeholder="glyph name"
        )

        self.w.transferButton = vanilla.Button(
            (140, 190, -10, 22),
            "Transfer",
            callback=self.transferGuides
        )

        # Opciones para transferir a componentes
        self.w.transferCompLabel = vanilla.TextBox(
            (10, 220, -10, 20),
            "Transfer guides to components:"
        )
        
        self.w.transferToContainingGlyphs = vanilla.RadioButton(
            (10, 245, 200, 20),
            "To glyphs that contain this glyph as component",
            value=True,
            callback=self.toggleTransferMode
        )
        
        self.w.transferToSelectedGlyphs = vanilla.RadioButton(
            (10, 270, 200, 20),
            "To selected glyphs (as components)",
            value=False,
            callback=self.toggleTransferMode
        )

        self.w.transferCompButton = vanilla.Button(
            (10, 310, -10, 25),
            "Transfer guides to components",
            callback=self.transferToComponents
        )

        self.w.open()

    def toggleTransferMode(self, sender):
        pass

    # ---------- HELPERS ----------

    def getCurrentGlyph(self):
        try:
            if Glyphs.font.currentTab:
                if hasattr(Glyphs.font.currentTab, 'graphicView'):
                    if hasattr(Glyphs.font.currentTab.graphicView, 'layerController'):
                        layer = Glyphs.font.currentTab.graphicView.layerController
                        if layer and hasattr(layer, 'glyph'):
                            return layer.glyph
                
                if hasattr(Glyphs.font.currentTab, 'selectedLayers'):
                    selected = Glyphs.font.currentTab.selectedLayers
                    if selected:
                        return selected[0].parent
            
            if Glyphs.font.selectedLayers:
                return Glyphs.font.selectedLayers[0].parent
            
            return None
        except:
            return None

    def getMasterById(self, master_id):
        font = Glyphs.font
        for master in font.masters:
            if master.id == master_id:
                return master
        return None

    def findGlyphsContainingComponent(self, component_name):
        font = Glyphs.font
        containing_glyphs = []
        
        for glyph in font.glyphs:
            for master in font.masters:
                layer = glyph.layers[master.id]
                if hasattr(layer, 'components'):
                    for comp in layer.components:
                        comp_name = comp.name if hasattr(comp, 'name') else comp.componentName if hasattr(comp, 'componentName') else None
                        if comp_name == component_name:
                            containing_glyphs.append(glyph)
                            break
                elif hasattr(layer, 'shapes'):
                    for shape in layer.shapes:
                        if isinstance(shape, GSComponent):
                            comp_name = shape.name if hasattr(shape, 'name') else shape.componentName if hasattr(shape, 'componentName') else None
                            if comp_name == component_name:
                                containing_glyphs.append(glyph)
                                break
        
        seen = set()
        unique_glyphs = []
        for glyph in containing_glyphs:
            if glyph.name not in seen:
                seen.add(glyph.name)
                unique_glyphs.append(glyph)
        
        return unique_glyphs

    def getComponentsFromGlyph(self, glyph, master_id):
        components = []
        layer = glyph.layers[master_id]
        
        if hasattr(layer, 'components'):
            components = layer.components
        elif hasattr(layer, 'shapes'):
            components = [s for s in layer.shapes if isinstance(s, GSComponent)]
        
        return components

    def getLayers(self):
        font = Glyphs.font
        layers = []

        if self.w.allMasters.get():
            for layer in font.selectedLayers:
                glyph = layer.parent
                for m in font.masters:
                    layers.append(glyph.layers[m.id])
        else:
            layers = font.selectedLayers

        return layers

    def getGuideContainer(self, layer):
        if self.w.globalGuides.get():
            return layer.master.guides
        else:
            return layer.guides

    def getSelectionPoints(self, layer):
        nodes = [n for n in layer.selection if isinstance(n, GSNode)]
        if len(nodes) >= 2:
            return nodes[0].position, nodes[1].position

        for path in layer.paths:
            for segment in path.segments:
                if all(n.selected for n in segment):
                    return segment[0].position, segment[-1].position

        return None, None

    def transformPoint(self, point, t):
        x, y = point.x, point.y
        newX = t[0] * x + t[2] * y + t[4]
        newY = t[1] * x + t[3] * y + t[5]
        return NSPoint(newX, newY)

    def transformAngle(self, angle, t):
        radians = math.atan2(t[1], t[0])
        return angle + math.degrees(radians)

    # ---------- ACTIONS ----------

    def createGuide(self, sender):
        try:
            for layer in self.getLayers():
                p1, p2 = self.getSelectionPoints(layer)
                guide = GSGuide()

                if p1 and p2:
                    guide.position = NSPoint(p1.x, p1.y)
                    dx = p2.x - p1.x
                    dy = p2.y - p1.y
                    guide.angle = math.degrees(math.atan2(dy, dx))
                else:
                    guide.position = NSPoint(0, 0)
                    guide.angle = 0

                self.getGuideContainer(layer).append(guide)

            Glyphs.redraw()
        except Exception:
            pass

    def clearGuides(self, sender):
        try:
            processedMasters = set()

            for layer in self.getLayers():
                if self.w.globalGuides.get():
                    masterID = layer.master.id
                    if masterID in processedMasters:
                        continue
                    layer.master.guides = []
                    processedMasters.add(masterID)
                else:
                    layer.guides = []

            Glyphs.redraw()
        except Exception:
            pass

    def transferGuides(self, sender):
        try:
            font = Glyphs.font
            targetName = self.w.charInput.get()

            if not targetName:
                return

            targetGlyph = font.glyphs[targetName]

            if not targetGlyph:
                return

            for sourceLayer in font.selectedLayers:
                sourceGlyph = sourceLayer.parent

                if self.w.allMasters.get():
                    for m in font.masters:
                        src = sourceGlyph.layers[m.id]
                        dst = targetGlyph.layers[m.id]

                        if self.w.globalGuides.get():
                            dst.master.guides = []
                            for g in src.master.guides:
                                newGuide = GSGuide()
                                newGuide.position = g.position
                                newGuide.angle = g.angle
                                dst.master.guides.append(newGuide)
                        else:
                            dst.guides = []
                            for g in src.guides:
                                newGuide = GSGuide()
                                newGuide.position = g.position
                                newGuide.angle = g.angle
                                dst.guides.append(newGuide)
                else:
                    masterID = sourceLayer.associatedMasterId
                    src = sourceLayer
                    dst = targetGlyph.layers[masterID]

                    if self.w.globalGuides.get():
                        dst.master.guides = []
                        for g in src.master.guides:
                            newGuide = GSGuide()
                            newGuide.position = g.position
                            newGuide.angle = g.angle
                            dst.master.guides.append(newGuide)
                    else:
                        dst.guides = []
                        for g in src.guides:
                            newGuide = GSGuide()
                            newGuide.position = g.position
                            newGuide.angle = g.angle
                            dst.guides.append(newGuide)

            Glyphs.redraw()
        except Exception:
            pass

    def transferToComponents(self, sender):
        try:
            font = Glyphs.font
            
            source_glyph = self.getCurrentGlyph()
            if not source_glyph:
                return
            
            if self.w.allMasters.get():
                masters_to_process = font.masters
            else:
                current_master_id = None
                for layer in font.selectedLayers:
                    if layer.parent == source_glyph:
                        current_master_id = layer.associatedMasterId
                        break
                
                if current_master_id:
                    current_master = self.getMasterById(current_master_id)
                    if current_master:
                        masters_to_process = [current_master]
                    else:
                        masters_to_process = [font.masters[0]]
                else:
                    masters_to_process = [font.masters[0]]
            
            if self.w.transferToContainingGlyphs.get():
                target_glyphs = self.findGlyphsContainingComponent(source_glyph.name)
                if not target_glyphs:
                    return
            else:
                target_glyphs = list(set([layer.parent for layer in font.selectedLayers]))
                if not target_glyphs:
                    return
            
            for master in masters_to_process:
                master_id = master.id
                source_layer = source_glyph.layers[master_id]
                
                if self.w.globalGuides.get():
                    source_guides = source_layer.master.guides
                else:
                    source_guides = source_layer.guides
                
                if not source_guides:
                    continue
                
                for target_glyph in target_glyphs:
                    target_layer = target_glyph.layers[master_id]
                    
                    components = self.getComponentsFromGlyph(target_glyph, master_id)
                    matching_components = []
                    
                    for comp in components:
                        comp_name = comp.name if hasattr(comp, 'name') else comp.componentName if hasattr(comp, 'componentName') else None
                        if comp_name == source_glyph.name:
                            matching_components.append(comp)
                    
                    if not matching_components:
                        continue
                    
                    new_guides = []
                    
                    for comp in matching_components:
                        t = None
                        if hasattr(comp, 'transform'):
                            t = comp.transform
                        
                        if not t:
                            continue
                        
                        for g in source_guides:
                            new_guide = GSGuide()
                            new_guide.position = self.transformPoint(g.position, t)
                            new_guide.angle = self.transformAngle(g.angle, t)
                            new_guides.append(new_guide)
                    
                    if new_guides:
                        guide_container = self.getGuideContainer(target_layer)
                        guide_container.extend(new_guides)
            
            Glyphs.redraw()
        except Exception:
            pass


GuideManager()