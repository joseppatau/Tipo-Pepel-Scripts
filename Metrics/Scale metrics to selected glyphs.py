# MenuTitle: Scale metrics to selected glyphs
# -*- coding: utf-8 -*-
# Description: Escala el LSB i RSB dels glifs seleccionats usant increments (ex: 10 o -10).
# Author: Josep Patau Bellart & Gemini

from GlyphsApp import Glyphs, UPDATEINTERFACE
from vanilla import FloatingWindow, TextBox, EditText, CheckBox, Button, RadioGroup

class ScaleMetricsRelative(object):
    def __init__(self):
        self.w = FloatingWindow((250, 190), "Escalar Mètriques %")
        
        self.w.text = TextBox((15, 12, -15, 17), "Increment (ex: 10 o -10):", sizeStyle='small')
        self.w.percentage = EditText((15, 35, -15, 22), "10")
        
        self.w.mode = RadioGroup((15, 65, -15, 20), ["LSB", "RSB", "Ambdós"], isVertical=False)
        self.w.mode.set(2)
        
        self.w.round = CheckBox((15, 95, -15, 20), "Arrodonir a enters", value=True, sizeStyle='small')
        
        self.w.runButton = Button((15, 130, -15, 25), "Aplicar Escala", callback=self.scaleAction)
        
        self.w.open()

    def scaleAction(self, sender):
        font = Glyphs.font
        if font is None:
            return

        try:
            # Nova lògica: 1 + (valor/100). Ex: 1 + (10/100) = 1.1
            input_val = float(self.w.percentage.get())
            factor = 1.0 + (input_val / 100.0)
        except ValueError:
            print("Error: Introdueix un número vàlid (ex: 10 o -10.5).")
            return

        mode = self.w.mode.get()
        should_round = self.w.round.get()
        selected_layers = font.selectedLayers
        
        font.disableUpdateInterface()
        
        try:
            for layer in selected_layers:
                # Escalar LSB
                if mode in [0, 2]:
                    new_lsb = layer.LSB * factor
                    layer.LSB = round(new_lsb) if should_round else new_lsb
                
                # Escalar RSB
                if mode in [1, 2]:
                    new_rsb = layer.RSB * factor
                    layer.RSB = round(new_rsb) if should_round else new_rsb
                    
            print(f"Mètriques ajustades un {input_val}% (Factor: {factor:.2f})")
            
        except Exception as e:
            print(f"Error: {e}")
            
        finally:
            font.enableUpdateInterface()
            Glyphs.redraw()

ScaleMetricsRelative()