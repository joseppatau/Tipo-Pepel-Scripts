#MenuTitle: Clean Kerned Pairs in Tab
# -*- coding: utf-8 -*-
# Description: 
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from GlyphsApp import *
from vanilla import *
from AppKit import NSFloatingWindowLevel

class HideKerningPairsInTab(object):

    def __init__(self):
        self.font = Glyphs.font
        self.w = Window((300, 120), "Clean Kerned Pairs in Tab", minSize=(280, 110))
        
        # MÁXIMO NIVEL: siempre encima de todo
        self.w._window.setLevel_(NSFloatingWindowLevel)
        
        self.w.text = TextBox(
            (10, 10, -10, 40),
            "Removes glyph pairs with defined kerning from the active tab.\n"
            "Kerning values ​​are retained in the font."
        )

        self.w.button = Button(
            (10, 70, -10, 24),
            "Clean pairs with kerning",
            callback=self.hideKerningPairs,
        )

        self.w.open()
        self.w.makeKey()

    def ensureAlwaysOnTop(self):
        """Forzar que la ventana permanezca siempre en primer plano"""
        try:
            self.w._window.setLevel_(NSFloatingWindowLevel)
            self.w.makeKey()
        except:
            pass

    def hideKerningPairs(self, sender):
        # Mantener ventana en primer plano ANTES de procesar
        self.ensureAlwaysOnTop()
        
        font = Glyphs.font
        if not font:
            Message("No font open", "Abre una fuente primero.")
            self.ensureAlwaysOnTop()
            return

        tab = font.currentTab
        if not tab:
            Message("No active tab", "Abre un tab de edición primero.")
            self.ensureAlwaysOnTop()
            return

        master = font.selectedFontMaster
        masterID = master.id

        layers = list(tab.layers)
        if not layers:
            Message("Empty tab", "El tab actual no contiene nada.")
            self.ensureAlwaysOnTop()
            return

        newLayers = []
        i = 0
        while i < len(layers):
            currentLayer = layers[i]
            currentGlyph = currentLayer.parent

            if i == len(layers) - 1 or currentGlyph is None:
                newLayers.append(currentLayer)
                i += 1
                continue

            nextLayer = layers[i + 1]
            nextGlyph = nextLayer.parent

            if nextGlyph is None:
                newLayers.append(currentLayer)
                i += 1
                continue

            leftKey = getattr(currentGlyph, 'rightKerningKey', currentGlyph.name) or currentGlyph.name
            rightKey = getattr(nextGlyph, 'leftKerningKey', nextGlyph.name) or nextGlyph.name

            kernValue = 0
            try:
                kernDic = font.kerning.get(masterID)
                if kernDic and leftKey in kernDic:
                    kernValue = kernDic[leftKey].get(rightKey, 0)
            except Exception as e:
                print("Error leyendo kerning:", e)
                kernValue = 0

            if kernValue != 0:
                print(f"Removing kerned pair: {currentGlyph.name} ({leftKey}) + {nextGlyph.name} ({rightKey}) = {kernValue}")
                i += 2
            else:
                newLayers.append(currentLayer)
                i += 1

        tab.layers = newLayers

        removedPairs = max(0, (len(layers) - len(newLayers)) // 2)
        Message(
            "Pares con kerning ocultos",
            f"Se han eliminado {removedPairs} parejas con kerning del tab.\n"
            "Los valores siguen disponibles en la ventana de kerning."
        )

        # IMPORTANTE: NO cerrar la ventana, mantenerla siempre visible
        self.ensureAlwaysOnTop()

HideKerningPairsInTab()
