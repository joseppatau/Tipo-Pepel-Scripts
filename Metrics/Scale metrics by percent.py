# -*- coding: utf-8 -*-
# MenuTitle: Scale Metrics by Percent
# www.josepfont.com - VERSIÓ 100% FUNCIONANT

from GlyphsApp import *
from GlyphsApp.plugins import *
import vanilla

class ScaleMetricsPRO(object):
    def __init__(self):
        self.w = vanilla.FloatingWindow((340, 260), "Scale Metrics PRO")

        self.w.text1 = vanilla.TextBox((20, 15, -20, 22), "Percentage (+/-):")
        self.w.percent = vanilla.EditText((20, 38, 300, 24), "40")

        # Mode
        self.w.mode = vanilla.Group((20, 70, 160, 90))
        self.w.mode.lsb = vanilla.RadioButton((10, 10, 50, 20), "LSB")
        self.w.mode.rsb = vanilla.RadioButton((10, 35, 50, 20), "RSB")
        self.w.mode.both = vanilla.RadioButton((10, 60, 50, 20), "Both")
        self.w.mode.both.set(True)

        # Scope
        self.w.scope = vanilla.Group((200, 70, 120, 90))
        self.w.scope.selected = vanilla.RadioButton((10, 10, 100, 20), "Selected glyphs")
        self.w.scope.all = vanilla.RadioButton((10, 35, 80, 20), "All glyphs")
        self.w.scope.selected.set(True)

        self.w.applyAllMasters = vanilla.CheckBox((20, 165, 300, 20), "Apply to all masters")

        self.w.apply = vanilla.Button((20, 195, 300, 28), "Apply", callback=self.apply)
        self.w.open()

    def _get_mode(self):
        if self.w.mode.lsb.get():
            return "LSB"
        elif self.w.mode.rsb.get():
            return "RSB"
        return "Both"

    def _get_scope(self):
        return self.w.scope.selected.get()

    def apply(self, sender):
        font = Glyphs.font
        if not font:
            Message("Scale Metrics PRO", "No hi ha cap font oberta.")
            return

        try:
            percent = float(self.w.percent.get().replace(",", "."))
        except:
            Message("Scale Metrics PRO", "Introdueix un percentatge vàlid.")
            return

        scale = 1.0 + (percent / 100.0)
        mode = self._get_mode()
        scope_selected = self._get_scope()
        allMasters = self.w.applyAllMasters.get()

        # Glifs seleccionats a la graella
        if scope_selected:
            glyphs = [layer.parent for layer in font.selectedLayers if layer.parent]
        else:
            glyphs = [g for g in font.glyphs if g.exported]

        if not glyphs:
            Message("Scale Metrics PRO", "Selecciona glifs a la graella.")
            return

        if allMasters:
            masters = font.masters
        else:
            master = font.selectedFontMaster
            masters = [master] if master else [font.masters[0]]

        # ✅ CORREGIT: sense updateInterface()
        font.disableUpdateInterface()

        try:
            changed_count = 0
            for glyph in glyphs:
                for master in masters:
                    layer = glyph.layers[master.id]
                    if not layer:
                        continue

                    changed = False
                    if mode in ("LSB", "Both"):
                        old_lsb = layer.LSB
                        layer.LSB = int(round(layer.LSB * scale))
                        if layer.LSB != old_lsb:
                            changed = True
                    if mode in ("RSB", "Both"):
                        old_rsb = layer.RSB
                        layer.RSB = int(round(layer.RSB * scale))
                        if layer.RSB != old_rsb:
                            changed = True
                    
                    if changed:
                        changed_count += 1

        finally:
            font.enableUpdateInterface()

        Message("Scale Metrics PRO", 
                f"✅ {changed_count} capes modificades\n"
                f"📊 {len(glyphs)} glifs × {len(masters)} masters")

ScaleMetricsPRO()