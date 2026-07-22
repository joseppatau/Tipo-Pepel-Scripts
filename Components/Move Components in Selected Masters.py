# MenuTitle: Move Components in Selected Masters (Floating DEBUG)
# -*- coding: utf-8 -*-
# Description: Moves components by a specified offset across selected masters for selected glyphs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from GlyphsApp import *
import vanilla

DEFAULT_KEY = "com.tunombre.movecomponents.value"


class MoveComponentsSelectedMastersFloating(object):

    def __init__(self):
        print("DEBUG: init window")

        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Open a font first.")
            return

        self.masters = self.font.masters
        self.masterNameByID = {m.id: m.name for m in self.masters}

        print(f"DEBUG: masters = {[m.name for m in self.masters]}")

        # ---------------------------------
        # WINDOW
        # ---------------------------------
        self.w = vanilla.FloatingWindow(
            (280, 340),
            "Move components in masters",
            closable=True
        )

        # ---------------------------------
        # MOVE VALUE
        # ---------------------------------
        self.w.valueText = vanilla.TextBox(
            (10, 10, -10, 17),
            "Move (units):"
        )

        savedValue = Glyphs.defaults.get(DEFAULT_KEY, 10)
        self.w.value = vanilla.EditText(
            (10, 30, -10, 22),
            str(savedValue)
        )

        # ---------------------------------
        # MASTER LIST (SCROLL BUILT-IN)
        # ---------------------------------
        self.w.masterLabel = vanilla.TextBox(
            (10, 65, -10, 17),
            "Apply to masters (multi-select):"
        )

        masterNames = [m.name for m in self.masters]

        self.w.masterList = vanilla.List(
            (10, 85, -10, 140),
            masterNames,
            allowsMultipleSelection=True
        )

        # Preselect all masters
        self.w.masterList.setSelection(list(range(len(masterNames))))

        # ---------------------------------
        # MOVE BUTTONS
        # ---------------------------------
        buttonsTop = 235

        self.w.up = vanilla.Button(
            (120, buttonsTop, 40, 20),
            "↑",
            callback=lambda s: self.move(0, 1)
        )
        self.w.left = vanilla.Button(
            (75, buttonsTop + 25, 40, 20),
            "←",
            callback=lambda s: self.move(-1, 0)
        )
        self.w.right = vanilla.Button(
            (165, buttonsTop + 25, 40, 20),
            "→",
            callback=lambda s: self.move(1, 0)
        )
        self.w.down = vanilla.Button(
            (120, buttonsTop + 50, 40, 20),
            "↓",
            callback=lambda s: self.move(0, -1)
        )

        self.w.open()

    # -------------------------------------------------
    # MOVE COMPONENTS (NO SELECTION REQUIRED)
    # -------------------------------------------------
    def move(self, xDir, yDir):
        print("\nDEBUG: MOVE CALLED")

        font = self.font

        try:
            value = float(self.w.value.get())
        except:
            Message("Invalid value", "Please enter a numeric value.")
            return

        Glyphs.defaults[DEFAULT_KEY] = value

        dx = xDir * value
        dy = yDir * value
        print(f"DEBUG: dx={dx}, dy={dy}")

        selectedIndexes = self.w.masterList.getSelection()
        selectedMasterIDs = [self.masters[i].id for i in selectedIndexes]

        print(f"DEBUG: selected masters = {[self.masterNameByID[i] for i in selectedMasterIDs]}")

        if not selectedMasterIDs:
            Message("No masters selected", "Select at least one master.")
            return

        undoManager = font.undoManager()
        undoManager.beginUndoGrouping()
        font.disableUpdateInterface()

        moved = 0

        print(f"DEBUG: selected layers = {len(font.selectedLayers)}")

        for layer in font.selectedLayers:
            glyph = layer.parent
            print(f"\nDEBUG: glyph {glyph.name}")

            sourceLayer = glyph.layers[font.selectedFontMaster.id]
            sourceComponents = list(sourceLayer.components)

            print(f"DEBUG: source components = {[c.componentName for c in sourceComponents]}")

            if not sourceComponents:
                print("DEBUG: no components in source layer")
                continue

            for masterID in selectedMasterIDs:
                masterLayer = glyph.layers[masterID]
                if not masterLayer:
                    continue

                # map components by name
                targetByName = {
                    c.componentName: c for c in masterLayer.components
                }

                for sourceComponent in sourceComponents:
                    targetComponent = targetByName.get(sourceComponent.componentName)
                    if not targetComponent:
                        print(
                            f"DEBUG: component '{sourceComponent.componentName}' "
                            f"missing in master {self.masterNameByID[masterID]}"
                        )
                        continue

                    before = (targetComponent.x, targetComponent.y)
                    targetComponent.x += dx
                    targetComponent.y += dy
                    after = (targetComponent.x, targetComponent.y)

                    print(
                        f"DEBUG: moved '{sourceComponent.componentName}' "
                        f"in {self.masterNameByID[masterID]} "
                        f"{before} → {after}"
                    )

                    moved += 1

        font.enableUpdateInterface()
        undoManager.endUndoGrouping()

        print(f"\nDEBUG: TOTAL COMPONENTS MOVED = {moved}")

        if moved == 0:
            Message(
                "Nothing moved",
                "No components were moved.\n"
                "Check that the glyphs contain components.",
                OKButton="OK"
            )
        else:
            Glyphs.showNotification(
                "Move components",
                f"Moved {moved} components."
            )


# Always create a new window
MoveComponentsSelectedMastersFloating()
