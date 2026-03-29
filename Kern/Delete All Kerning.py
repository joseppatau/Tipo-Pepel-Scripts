# MenuTitle: Delete All Kerning (Safe Universal)
# -*- coding: utf-8 -*-
# Description: Apply equidistant nodes and roughness effects to glyphs
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *

font = Glyphs.font

if not font:
    Message("Error", "Open a font first.", OKButton="OK")

else:
    totalPairs = 0

    font.disableUpdateInterface()

    try:
        for master in font.masters:
            masterID = master.id

            masterKerning = font.kerning.get(masterID)

            if not masterKerning:
                continue

            # Contar pares
            for leftKey in masterKerning:
                rightDict = masterKerning.get(leftKey)
                if rightDict:
                    totalPairs += len(rightDict)

            # Vaciar kerning del master
            font.kerning[masterID] = {}

    finally:
        font.enableUpdateInterface()

    Message(
        "Kerning Deleted",
        f"Deleted {totalPairs} kerning pairs across all masters.",
        OKButton="OK"
    )