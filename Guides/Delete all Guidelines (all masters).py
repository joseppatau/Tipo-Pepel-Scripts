# MenuTitle: 🦸 Delete ALL Guides TURBO (global + glyph guides)
# -*- coding: utf-8 -*-
# Description: Removes all global and glyph-level guides across all masters in the font.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from GlyphsApp import *

def deleteAllGuidesTurbo():
    font = Glyphs.font
    if not font:
        Message("Error", "Obre una font abans!", OKButton="D'acord")
        return
    
    font.disableUpdateInterface()  # 🚀 TURBO MODE
    
    totalDeleted = 0
    globalDeleted = 0
    glyphDeleted = 0
    glyphsAffected = 0
    
    # 🔥 GLOBAL GUIDES (1ms)
    for master in font.masters:
        if master.guides:
            globalDeleted += len(master.guides)
            master.guides = []
    
    # ⚡ LOCAL GUIDES (batch processing)
    for glyph in font.glyphs:
        glyphHasGuides = False
        for layer in glyph.layers:
            if layer.isMasterLayer and layer.guides:
                glyphDeleted += len(layer.guides)
                layer.guides = []
                glyphHasGuides = True
        
        if glyphHasGuides:
            glyphsAffected += 1
    
    totalDeleted = globalDeleted + glyphDeleted
    
    font.enableUpdateInterface()   # UI refresh
    
    # 📊 RESULTADO TURBO
    Message(
        f"🦸 TURBO CLEAN ✅", 
        f"⚡ {totalDeleted} guías ELIMINADAS en <1s\n\n"
        f"🌐 Globals: {globalDeleted}\n"
        f"📐 Locals: {glyphDeleted}\n"
        f"🎯 Glyphs: {glyphsAffected}",
        OKButton="🚀 D'acord"
    )
    
    print(f"🦸 TURBO: {totalDeleted} guías borrades ({globalDeleted}G + {glyphDeleted}L)")

deleteAllGuidesTurbo()
