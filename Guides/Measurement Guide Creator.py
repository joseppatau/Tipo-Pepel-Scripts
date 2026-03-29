#MenuTitle: Measurement Guide Creator
# -*- coding: utf-8 -*-
# Description:Creates and manages horizontal measurement guides at custom Y positions across selected glyphs and masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
from GlyphsApp import Glyphs, GSGuide, Message
from AppKit import NSPoint
import vanilla

class MeasurementGuideCreator(object):

    prefID = "com.measurement.guide.creator"

    def __init__(self):
        self.loadPrefs()
        
        self.w = vanilla.FloatingWindow((360, 220), "Measurement Guide Creator")
        
        # Y positions input
        self.w.text1 = vanilla.TextBox((15, 15, 100, 20), "Y positions:")
        self.w.yPositions = vanilla.EditText((120, 12, 220, 22), self.savedYPositions)
        self.w.text1a = vanilla.TextBox((120, 35, 220, 15), "comma separated")
        
        # Master selection radio buttons
        self.w.text2 = vanilla.TextBox((15, 60, 100, 20), "Apply to:")
        self.w.masterSelection = vanilla.RadioGroup(
            (120, 58, 200, 40),
            ["Current Master", "All Masters"],
            isVertical=False
        )
        self.w.masterSelection.set(self.savedMasterSelection)
        
        # Buttons
        self.w.applyButton = vanilla.Button(
            (15, 100, 120, 24),
            "Apply",
            callback=self.applyGuides
        )
        
        self.w.clearButton = vanilla.Button(
            (140, 100, 120, 24),
            "Clear Guides",
            callback=self.clearGuides
        )
        
        # Info text
        self.w.info = vanilla.TextBox(
            (15, 140, 330, 60),
            "Creates measurement guides at specified Y positions\nGuides are horizontal and show measurements"
        )
        
        self.w.open()
    
    def loadPrefs(self):
        """Load saved preferences"""
        self.savedYPositions = Glyphs.defaults.get(self.prefID + ".yPositions", "500, 550, 600")
        self.savedMasterSelection = Glyphs.defaults.get(self.prefID + ".masterSelection", 0)
    
    def savePrefs(self):
        """Save current preferences"""
        Glyphs.defaults[self.prefID + ".yPositions"] = self.w.yPositions.get()
        Glyphs.defaults[self.prefID + ".masterSelection"] = self.w.masterSelection.get()
    
    def getSelectedLayers(self):
        """Get selected layers from active font"""
        font = Glyphs.font
        if not font:
            return []
        return [layer for layer in font.selectedLayers if layer]
    
    def parseYPositions(self, y_text):
        """Convert comma-separated Y positions to list of floats"""
        if not y_text or y_text.isspace():
            return []
        y_list = []
        for v in y_text.split(","):
            v = v.strip()
            if v:
                try:
                    y_list.append(float(v))
                except ValueError:
                    print(f"Warning: '{v}' is not a valid number, ignoring")
        return y_list
    
    def getTargetLayers(self, glyph, master_selection):
        """Get layers to apply guides based on master selection"""
        if master_selection == 0:  # Current Master
            font = Glyphs.font
            current_master_id = font.selectedFontMaster.id
            return [glyph.layers[current_master_id]]
        else:  # All Masters
            return [layer for layer in glyph.layers if layer.isMasterLayer]
    
    def addGuidesToLayer(self, layer, y_positions):
        """Add measurement guides to a layer"""
        guides_added = 0
        for y in y_positions:
            # Check if guide already exists at this Y
            existing = False
            for guide in layer.guides:
                if abs(guide.position.y - y) < 0.1 and guide.angle == 0:
                    existing = True
                    break
            
            if not existing:
                # Create guide
                guide = GSGuide()
                guide.position = NSPoint(0, y)
                guide.angle = 0  # Horizontal guide
                
                # Set measurement property (Glyphs 3)
                try:
                    guide.showMeasurement = True
                except AttributeError:
                    try:
                        guide.measurement = True
                    except AttributeError:
                        print(f"Note: Could not set measurement property for guide at y={y}")
                
                # Add to layer
                layer.guides.append(guide)
                guides_added += 1
        
        return guides_added
    
    def clearGuidesFromLayer(self, layer, y_positions=None):
        """Clear guides from a layer"""
        guides_removed = 0
        guides_to_remove = []
        
        for guide in layer.guides:
            if guide.angle == 0:  # Horizontal guides only
                if y_positions is None:  # Clear all
                    guides_to_remove.append(guide)
                else:  # Clear specific Y positions
                    for y in y_positions:
                        if abs(guide.position.y - y) < 0.1:
                            guides_to_remove.append(guide)
                            break
        
        for guide in guides_to_remove:
            layer.guides.remove(guide)
            guides_removed += 1
        
        return guides_removed
    
    def applyGuides(self, sender):
        """Apply guides to selected glyphs"""
        font = Glyphs.font
        if not font:
            Message("Error", "No font open")
            return
        
        y_text = self.w.yPositions.get()
        y_positions = self.parseYPositions(y_text)
        
        if not y_positions:
            Message("Error", "Please enter valid Y positions")
            return
        
        master_selection = self.w.masterSelection.get()
        master_text = ["Current Master", "All Masters"][master_selection]
        
        self.savePrefs()
        
        selected_layers = self.getSelectedLayers()
        if not selected_layers:
            Message("Error", "No glyphs selected")
            return
        
        # Group by glyph
        glyphs_dict = {}
        for layer in selected_layers:
            glyph = layer.parent
            if glyph not in glyphs_dict:
                glyphs_dict[glyph] = []
        
        # Apply guides
        total_guides_added = 0
        glyphs_affected = []
        
        font.disableUpdateInterface()
        
        try:
            for glyph in glyphs_dict.keys():
                target_layers = self.getTargetLayers(glyph, master_selection)
                glyph_guides_added = 0
                
                for layer in target_layers:
                    if master_selection == 0:
                        if layer not in selected_layers:
                            continue
                    
                    glyph.beginUndo()
                    guides_added = self.addGuidesToLayer(layer, y_positions)
                    glyph.endUndo()
                    
                    glyph_guides_added += guides_added
                
                if glyph_guides_added > 0:
                    glyphs_affected.append(f"/{glyph.name}")
                    total_guides_added += glyph_guides_added
        
        finally:
            font.enableUpdateInterface()
        
        # Show result
        if total_guides_added == 0:
            Message("No changes", "No guides were added (they may already exist)")
        else:
            glyphs_list = ", ".join(glyphs_affected[:5])
            if len(glyphs_affected) > 5:
                glyphs_list += f" and {len(glyphs_affected)-5} more"
            
            Message(
                "Guides Added",
                f"✅ Added {total_guides_added} measurement guides\n"
                f"📏 Y positions: {', '.join(str(int(y)) for y in y_positions)}\n"
                f"🎯 Applied to: {master_text}\n"
                f"📋 Affected glyphs: {glyphs_list}"
            )
    
    def clearGuides(self, sender):
        """Clear guides from selected glyphs"""
        font = Glyphs.font
        if not font:
            Message("Error", "No font open")
            return
        
        y_text = self.w.yPositions.get()
        y_positions = self.parseYPositions(y_text) if y_text.strip() else None
        master_selection = self.w.masterSelection.get()
        master_text = ["Current Master", "All Masters"][master_selection]
        
        self.savePrefs()
        
        selected_layers = self.getSelectedLayers()
        if not selected_layers:
            Message("Error", "No glyphs selected")
            return
        
        # Group by glyph
        glyphs_dict = {}
        for layer in selected_layers:
            glyph = layer.parent
            if glyph not in glyphs_dict:
                glyphs_dict[glyph] = []
        
        # Clear guides
        total_guides_removed = 0
        glyphs_affected = []
        
        font.disableUpdateInterface()
        
        try:
            for glyph in glyphs_dict.keys():
                target_layers = self.getTargetLayers(glyph, master_selection)
                glyph_guides_removed = 0
                
                for layer in target_layers:
                    if master_selection == 0:
                        if layer not in selected_layers:
                            continue
                    
                    glyph.beginUndo()
                    guides_removed = self.clearGuidesFromLayer(layer, y_positions)
                    glyph.endUndo()
                    
                    glyph_guides_removed += guides_removed
                
                if glyph_guides_removed > 0:
                    glyphs_affected.append(f"/{glyph.name}")
                    total_guides_removed += glyph_guides_removed
        
        finally:
            font.enableUpdateInterface()
        
        # Show result
        if total_guides_removed == 0:
            if y_positions:
                Message("No changes", "No matching guides found to clear")
            else:
                Message("No changes", "No guides found to clear")
        else:
            glyphs_list = ", ".join(glyphs_affected[:5])
            if len(glyphs_affected) > 5:
                glyphs_list += f" and {len(glyphs_affected)-5} more"
            
            if y_positions:
                pos_text = f"at Y: {', '.join(str(int(y)) for y in y_positions)}"
            else:
                pos_text = "all horizontal guides"
            
            Message(
                "Guides Cleared",
                f"✅ Removed {total_guides_removed} guides\n"
                f"📏 {pos_text}\n"
                f"🎯 Applied to: {master_text}\n"
                f"📋 Affected glyphs: {glyphs_list}"
            )

# Run the script
MeasurementGuideCreator()
