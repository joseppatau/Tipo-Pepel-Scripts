#MenuTitle: Copy Kerning from Open Font
# -*- coding: utf-8 -*-
# Description: Copies kerning data from other open fonts into the current font, with flexible selection of masters and matching logic based on master name or ID.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import GlyphsApp
import vanilla

class CopyKerningFromFont(object):

    def __init__(self):
        self.current_font = Glyphs.font
        self.current_master = self.current_font.selectedFontMaster if self.current_font else None

        self.source_fonts = [f for f in Glyphs.fonts if f != self.current_font]

        # --- NO HAY FUENTES ---
        if not self.source_fonts:
            self.w = vanilla.FloatingWindow((300, 120), "Copy Kerning from Open Font")
            self.w.text = vanilla.TextBox((10, 10, -10, 30), "No other fonts open.")
            self.w.close_button = vanilla.Button((10, 50, -10, 30), "Close", callback=self.CloseCallback)
            self.w.center()
            self.w.open()
            return

        # --- GENERAR LISTA ---
        self.scroll_items = []
        self.checkboxes = []
        self.master_keys = []

        y = 5

        for font in self.source_fonts:
            self.scroll_items.append(("title", font.familyName, y, None, None))
            y += 22

            for master in font.masters:
                self.scroll_items.append(("cb", master.name, y, font, master))
                y += 20

            y += 6

        self.scroll_height = y + 10

        # --- ALTURA DINÁMICA ---
        window_height = min(self.scroll_height + 170, 700)

        self.w = vanilla.FloatingWindow((320, window_height), "Copy Kerning from Open Font")

        # --- CONTENIDO INTERNO ---
        self.inner = vanilla.Group((0, 0, 300, self.scroll_height))

        for i, item in enumerate(self.scroll_items):
            typ, text, y, font, master = item

            if typ == "title":
                t = vanilla.TextBox((10, y, -10, 18), text, sizeStyle="small")
                setattr(self.inner, f"title_{i}", t)

            else:
                cb = vanilla.CheckBox(
                    (10, y, -10, 18),
                    text,
                    value=False,
                    callback=self.MasterCheckboxCallback
                )
                setattr(self.inner, f"cb_{i}", cb)

                self.checkboxes.append(cb)
                self.master_keys.append((font, master))

        # --- SCROLL (FIX GLYPHS) ---
        self.w.scroll = vanilla.ScrollView(
            (10, 10, -10, window_height - 150),
            self.inner.getNSView()
        )

        # --- BOTONES ---
        self.select_all_state = True

        self.w.select_all = vanilla.Button(
            (10, window_height - 130, 140, 30),
            "Select All",
            callback=self.SelectAllCallback
        )

        self.w.radio = vanilla.RadioGroup(
            (10, window_height - 95, -10, 60),
            ["Current selected master", "All masters", "Selected masters"]
        )
        self.w.radio.set(0)

        self.w.apply = vanilla.Button(
            (10, window_height - 35, -10, 30),
            "Apply",
            callback=self.ApplyCallback
        )

        self.w.setDefaultButton(self.w.apply)
        self.w.center()
        self.w.open()

    # --- CALLBACKS ---

    def CloseCallback(self, sender):
        self.w.close()

    def MasterCheckboxCallback(self, sender):
        pass

    def SelectAllCallback(self, sender):
        state = self.select_all_state

        for cb in self.checkboxes:
            cb.set(state)

        self.select_all_state = not state
        self.w.select_all.setTitle("Deselect All" if state else "Select All")

    def GetSelectedMasters(self):
        selected = []
        for i, cb in enumerate(self.checkboxes):
            if cb.get():
                selected.append(self.master_keys[i])
        return selected

    # --- MAIN ---

    def ApplyCallback(self, sender):
        option = self.w.radio.get()
        masters_to_copy = []

        if option == 0:
            if not self.current_master:
                Glyphs.showNotification("Error", "No current master selected.")
                return

            for font in self.source_fonts:
                for m in font.masters:
                    if m.id == self.current_master.id:
                        masters_to_copy.append((font, m))
                        break

        elif option == 1:
            for font in self.source_fonts:
                for m in font.masters:
                    target = next(
                        (tm for tm in self.current_font.masters if tm.name == m.name),
                        None
                    )
                    if target:
                        masters_to_copy.append((font, m, target))

        else:
            for font, m in self.GetSelectedMasters():
                target = next(
                    (tm for tm in self.current_font.masters if tm.name == m.name),
                    None
                )
                if target:
                    masters_to_copy.append((font, m, target))

        if not masters_to_copy:
            Glyphs.showNotification("Error", "No valid masters found.")
            return

        total = 0

        for item in masters_to_copy:
            if option == 0:
                font, sm = item
                tm = self.current_master
            else:
                font, sm, tm = item

            kerning = font.kerning.get(sm.id, {}) if font.kerning else {}

            if not kerning:
                continue

            if self.current_font.kerning is None:
                self.current_font.kerning = {}

            if tm.id not in self.current_font.kerning:
                self.current_font.kerning[tm.id] = {}

            target_kern = self.current_font.kerning[tm.id]

            for pair, value in kerning.items():
                target_kern[pair] = value

            total += 1

        Glyphs.showNotification("Done", f"Kerning copied from {total} masters.")
        self.w.close()


if __name__ == "__main__":
    CopyKerningFromFont()