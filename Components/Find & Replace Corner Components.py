# MenuTitle: Find & Replace Corner Components (Pro)

import vanilla
from GlyphsApp import Glyphs, CORNER

class CornerComponentReplacer(object):
    
    def __init__(self):
        
        self.w = vanilla.FloatingWindow((340, 380), "Corner Component Replace")
        
        # --- FIND ---
        self.w.findTitle = vanilla.TextBox((15, 10, 200, 20), "Find")
        self.w.findName = vanilla.EditText((15, 30, 310, 22), placeholder="Component name")
        self.w.findWidth = vanilla.EditText((15, 55, 150, 22), placeholder="% width")
        self.w.findHeight = vanilla.EditText((175, 55, 150, 22), placeholder="% height")
        
        self.w.ignoreScale = vanilla.CheckBox((15, 80, 200, 20), "Ignore scale in search", value=True)
        
        # --- REPLACE ---
        self.w.replaceTitle = vanilla.TextBox((15, 110, 200, 20), "Replace")
        self.w.replaceName = vanilla.EditText((15, 130, 310, 22), placeholder="New component name")
        self.w.replaceWidth = vanilla.EditText((15, 155, 150, 22), placeholder="% width")
        self.w.replaceHeight = vanilla.EditText((175, 155, 150, 22), placeholder="% height")
        
        # --- SCOPE GLYPHS ---
        self.w.scopeGlyphs = vanilla.RadioGroup(
            (15, 190, 310, 40),
            ["Selected Glyphs", "All Glyphs"],
            isVertical=True
        )
        self.w.scopeGlyphs.set(0)
        
        # --- SCOPE MASTERS ---
        self.w.scopeMasters = vanilla.RadioGroup(
            (15, 235, 310, 40),
            ["This Master", "All Masters"],
            isVertical=True
        )
        self.w.scopeMasters.set(0)
        
        # --- BUTTON ---
        self.w.runButton = vanilla.Button((15, 285, 310, 35), "Apply", callback=self.run)
        
        # --- STATUS ---
        self.w.status = vanilla.TextBox((15, 325, 310, 20), "")
        
        self.w.open()
    
    def run(self, sender):
        
        font = Glyphs.font
        if not font:
            return
        
        currentMasterID = font.selectedFontMaster.id
        
        findName = self.w.findName.get().strip()
        replaceName = self.w.replaceName.get().strip()
        
        ignoreScale = self.w.ignoreScale.get()
        
        # --- Parse find scale ---
        try:
            findW = float(self.w.findWidth.get()) / 100 if self.w.findWidth.get() else None
            findH = float(self.w.findHeight.get()) / 100 if self.w.findHeight.get() else None
        except:
            findW, findH = None, None
        
        # --- Parse replace scale ---
        try:
            replaceW = float(self.w.replaceWidth.get()) / 100 if self.w.replaceWidth.get() else None
            replaceH = float(self.w.replaceHeight.get()) / 100 if self.w.replaceHeight.get() else None
        except:
            replaceW, replaceH = None, None
        
        # --- Glyph scope ---
        if self.w.scopeGlyphs.get() == 0:
            glyphs = list(set([l.parent for l in font.selectedLayers]))
        else:
            glyphs = font.glyphs
        
        totalChanges = 0
        
        font.disableUpdateInterface()
        
        for glyph in glyphs:
            glyph.beginUndo()
            
            # --- Master filtering ---
            if self.w.scopeMasters.get() == 0:
                layers = [l for l in glyph.layers if l.associatedMasterId == currentMasterID]
            else:
                layers = [l for l in glyph.layers if l.associatedMasterId is not None]
            
            for layer in layers:
                
                for hint in layer.hints:
                    
                    if hint.type != CORNER:
                        continue
                    
                    if findName and hint.name != findName:
                        continue
                    
                    # --- Scale matching ---
                    if not ignoreScale:
                        if findW is not None:
                            if abs(hint.scale.x - findW) > 0.001:
                                continue
                        if findH is not None:
                            if abs(hint.scale.y - findH) > 0.001:
                                continue
                    
                    # --- APPLY CHANGES ---
                    changed = False
                    
                    if replaceName:
                        hint.name = replaceName
                        changed = True
                    
                    currentX = hint.scale.x
                    currentY = hint.scale.y
                    
                    newX = replaceW if replaceW is not None else currentX
                    newY = replaceH if replaceH is not None else currentY
                    
                    if (newX != currentX) or (newY != currentY):
                        hint.scale = (newX, newY)
                        changed = True
                    
                    if changed:
                        totalChanges += 1
            
            glyph.endUndo()
        
        font.enableUpdateInterface()
        
        self.w.status.set(f"{totalChanges} changes applied")
        Glyphs.showNotification("Corner Components Updated", f"{totalChanges} changes applied")


CornerComponentReplacer()