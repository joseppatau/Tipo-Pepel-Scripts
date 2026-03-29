# MenuTitle: Macro Panel
# -*- coding: utf-8 -*-
# Description: Advanced macro recorder and shortcut manager for Glyphs App.  
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
__doc__ = """
Advanced macro recorder and shortcut manager for Glyphs App.  
Allows recording, editing, saving, and replaying sequences of keyboard actions for repetitive workflows.
"""

import vanilla
import time
import json
import os
from AppKit import NSEvent, NSApp, NSColor, NSOpenPanel, NSSavePanel, NSEventTypeKeyDown
from Quartz import *

# Datos por defecto del JSON adjunto (shortcuts y macros integrados)
DEFAULT_DATA = {
    "macros": {
        "Copy to next Master": [
            {"keycode": 0, "char": "a", "cmd": True, "alt": False, "shift": False, "ctrl": False},
            {"keycode": 8, "char": "c", "cmd": True, "alt": False, "shift": False, "ctrl": False},
            {"keycode": 125, "char": "\uf701", "cmd": True, "alt": True, "shift": False, "ctrl": False},
            {"keycode": 0, "char": "a", "cmd": True, "alt": False, "shift": False, "ctrl": False},
            {"keycode": 51, "char": "\u007f", "cmd": False, "alt": False, "shift": False, "ctrl": True},
            {"keycode": 9, "char": "v", "cmd": True, "alt": False, "shift": False, "ctrl": False}
        ]
    },
    "shortcuts": [
        {"shortcut": "\u2318A", "description": "Select All", "keycode": 0, "char": "a", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318C", "description": "Copy", "keycode": 8, "char": "c", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318V", "description": "Paste", "keycode": 9, "char": "v", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2325\u2193", "description": "Next Master", "keycode": 125, "char": "\uf701", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "^1", "description": "Flip Horizontal  \u2014", "keycode": 18, "char": "1", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^2", "description": "Flip Vertical | ", "keycode": 19, "char": "2", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u2192", "description": "Move 100 \u2192", "keycode": 124, "char": "\uf703", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2190", "description": "Move 100 \u2190", "keycode": 123, "char": "\uf702", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2191", "description": "Move 100 \u2191", "keycode": 126, "char": "\uf700", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2193", "description": "Move 100 \u2193", "keycode": 125, "char": "\uf701", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u21e7\u2192", "description": "Move 10 \u2192", "keycode": 124, "char": "\uf703", "cmd": False, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "\u21e7\u2190", "description": "Move 10 \u2190", "keycode": 123, "char": "\uf702", "cmd": False, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "\u21e7\u2191", "description": "Move 10 \u2191", "keycode": 126, "char": "\uf700", "cmd": False, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "\u21e7\u2193", "description": "Move 10 \u2193", "keycode": 125, "char": "\uf701", "cmd": False, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "^T", "description": "Align Horizontal Center \u25af\u25ae\u25af", "keycode": 17, "char": "t", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^\u232b", "description": "Clear", "keycode": 51, "char": "\u007f", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^Q", "description": "Align Left \u25ae\u25af\u25af", "keycode": 12, "char": "q", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^W", "description": "Align Right \u25af\u25af\u25ae", "keycode": 13, "char": "w", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^E", "description": "Align Top \u2b06", "keycode": 14, "char": "e", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^R", "description": "Align Bottom \u2b07", "keycode": 15, "char": "r", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^Y", "description": "Align Vertical Center |\u2195", "keycode": 16, "char": "y", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^U", "description": "Scale Up", "keycode": 32, "char": "u", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^I", "description": "Scale Down", "keycode": 34, "char": "i", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^O", "description": "Rotate right \u21bb", "keycode": 31, "char": "o", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^P", "description": "Rotale Left \u21ba", "keycode": 35, "char": "p", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^A", "description": "Slant Right  \u2b08", "keycode": 0, "char": "a", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^S", "description": "Slant Left \u2b09", "keycode": 1, "char": "s", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^D", "description": "Slant Up  \u2b09\u2191", "keycode": 2, "char": "d", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^F", "description": "Slant Down  \u2b09\u2193", "keycode": 3, "char": "f", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u21e7O", "description": "Remove Overlap", "keycode": 31, "char": "O", "cmd": True, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "^G", "description": "Substract  \u229d", "keycode": 5, "char": "g", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^H", "description": "Intersect  \u29c9", "keycode": 4, "char": "h", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318U", "description": "Set Anchors  \u2693", "keycode": 32, "char": "u", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2325U", "description": "Anchors All Masters \u2693", "keycode": 32, "char": "u", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "^J", "description": "Reset Anchors", "keycode": 38, "char": "j", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^K", "description": "Reset Anchors All Masters", "keycode": 40, "char": "k", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318S", "description": "Save", "keycode": 1, "char": "s", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318W", "description": "Close", "keycode": 13, "char": "w", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318I", "description": "Font Info", "keycode": 34, "char": "i", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318E", "description": "Export", "keycode": 14, "char": "e", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318Z", "description": "Undo", "keycode": 6, "char": "z", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318X", "description": "Cut", "keycode": 7, "char": "x", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2325A", "description": "Deselect All", "keycode": 0, "char": "a", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u21e7F", "description": "Find & Replace", "keycode": 3, "char": "F", "cmd": True, "alt": False, "shift": True, "ctrl": False},
        {"shortcut": "\u2318^M", "description": "Update Metrics", "keycode": 46, "char": "m", "cmd": True, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u2325^M", "description": "Update Metrics All Masters", "keycode": 46, "char": "m", "cmd": True, "alt": True, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u2325^R", "description": "Reverse Contours", "keycode": 15, "char": "r", "cmd": True, "alt": True, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u2325X", "description": "Add Extremes", "keycode": 7, "char": "x", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u00c7", "description": "Transformations", "keycode": 42, "char": "\u00e7", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318B", "description": "Edit Background", "keycode": 11, "char": "b", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318J", "description": "Selection to Background", "keycode": 38, "char": "j", "cmd": True, "alt": False, "shift": False, "ctrl": False},
        {"shortcut": "\u2318\u2325J", "description": "Ad Selection to Background", "keycode": 38, "char": "j", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "^M", "description": "Expand Outline", "keycode": 46, "char": "m", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^N", "description": "Expand Outline all Mastes", "keycode": 45, "char": "n", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^B", "description": "Make Node First", "keycode": 11, "char": "b", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^V", "description": "Node First all Masters", "keycode": 9, "char": "v", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "\u2318\u2325\u2191", "description": "Previous Master", "keycode": 126, "char": "\uf700", "cmd": True, "alt": True, "shift": False, "ctrl": False},
        {"shortcut": "^\u00a1", "description": "Convert to Cubic", "keycode": 24, "char": "\u00a1", "cmd": False, "alt": False, "shift": False, "ctrl": True},
        {"shortcut": "^'", "description": "Convert to Quadratic", "keycode": 27, "char": "'", "cmd": False, "alt": False, "shift": False, "ctrl": True}
    ]
}

def sendkey(keycode, cmd=False, alt=False, shift=False, ctrl=False):
    flags = 0
    if cmd: flags |= kCGEventFlagMaskCommand
    if alt: flags |= kCGEventFlagMaskAlternate
    if shift: flags |= kCGEventFlagMaskShift
    if ctrl: flags |= kCGEventFlagMaskControl
    edown = CGEventCreateKeyboardEvent(None, keycode, True)
    CGEventSetFlags(edown, flags)
    CGEventPost(kCGHIDEventTap, edown)
    eup = CGEventCreateKeyboardEvent(None, keycode, False)
    CGEventSetFlags(eup, flags)
    CGEventPost(kCGHIDEventTap, eup)

TITLE = "-----------------------------"

class MacroRecorderPRO:
    def __init__(self):
        self.recording = False
        self.dragIndex = None
        self.recording_shortcut_for_list = False
        self.current_macro = []
        self.repeat_count = 1
        self.repeat_pause = 0.60
        self.action_delay = 0.05
        self.monitor = None
        self.updatingList = False
        self.path = os.path.expanduser("~/Library/Application Support/Glyphs/Macros/macrospro.json")
        self.data = {"macros": {}, "shortcuts": []}
        self.filteredShortcuts = []
        self.loadData()
        self.buildUI()
        self.refreshMacroList()
        self.refreshShortcutList()

    def loadData(self):
        """Carga datos: prioriza archivo local, sino usa default y copia."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.data = json.load(f)
                print(f"Datos cargados desde {self.path}")
            except Exception as e:
                print(f"Error cargando {self.path}: {e}. Usando datos por defecto.")
                self.data = DEFAULT_DATA.copy()
                self.saveToFile()
        else:
            self.data = DEFAULT_DATA.copy()
            self.saveToFile()
            print(f"Creado {self.path} con datos por defecto.")

    def saveToFile(self):
        """Guarda datos en archivo local."""
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error guardando {self.path}: {e}")

    def onMainListDoubleClick(self, sender):
        if self.dragIndex is None:
            return

        sel = sender.getSelection()
        if not sel:
            return

        targetIndex = sel[0]
        if targetIndex == self.dragIndex:
            return

        item = self.current_macro.pop(self.dragIndex)
        self.current_macro.insert(targetIndex, item)
        self.updateList()
        self.dragIndex = targetIndex

    # -------------------------
    # SAFE MONITOR
    # -------------------------
    def stopMonitor(self):
        if self.monitor:
            try:
                NSEvent.removeMonitor_(self.monitor)
            except:
                pass
        self.monitor = None

    def onMainListSelection(self, sender):
        sel = sender.getSelection()
        if sel:
            self.dragIndex = sel[0]
        else:
            self.dragIndex = None

    # -------------------------
    # UI
    # -------------------------
    def buildUI(self):
        self.w = vanilla.FloatingWindow((300, 650), "Macro Recorder PRO Ultra")
        self.w.getNSWindow().setLevel_(3)
        self.w.tabs = vanilla.Tabs((10, 10, -10, -10), ("Main", "My Shortcuts"))
        main = self.w.tabs[0]
        short = self.w.tabs[1]

        # MAIN
        main.recordBtn = vanilla.Button((10, 10, 60, 30), "REC", callback=self.openShortcutPicker)

        # Delay entre acciones
        main.delayLabel = vanilla.TextBox((90, 15, 70, 20), "Delay (s):")
        main.delayInput = vanilla.EditText(
            (154, 13, 40, 25), "{:.2f}".format(self.action_delay),
            callback=self.onDelayChange
        )

        main.playBtn = vanilla.Button(
            (205, 10, 60, 30), "▶ PLAY", callback=self.playMacro
        )

        main.list = vanilla.List(
            (10, 50, -10, 200),
            [],
            selectionCallback=self.onMainListSelection,
            doubleClickCallback=self.onMainListDoubleClick,
        )

        main.saveBtn = vanilla.Button(
            (10, 260, 120, 30), "Save Macro", callback=self.askMacroName
        )

        main.macroLabel = vanilla.TextBox((10, 300, -10, 20), "Macro list")
        main.macroList = vanilla.List(
            (10, 320, -10, 200), [], selectionCallback=self.loadSelectedMacro
        )

        main.saveAllBtn = vanilla.Button(
            (10, 530, 60, 30), "Save", callback=self.saveMacrosToJson
        )
        main.loadBtn = vanilla.Button(
            (80, 530, 60, 30), "Load", callback=self.loadMacrosFromJson
        )
        main.deleteBtn = vanilla.Button(
            (150, 530, 120, 30), "Delete Macro", callback=self.deleteMacro
        )

        # SHORTCUTS
        short.shortcutList = vanilla.List(
            (10, 10, -10, -90),
            [],
            columnDescriptions=[
                {"title": "Shortcut", "key": "shortcut"},
                {"title": "Description", "key": "description", "editable": True},
            ],
            editCallback=self.onShortcutEdit,
        )

        # Up and Down buttons with triangles
        short.upBtn = vanilla.Button(
            (10, -60, 60, 30), "▲ Up", callback=self.moveShortcutUp
        )
        short.downBtn = vanilla.Button(
            (80, -60, 60, 30), "▼ Down", callback=self.moveShortcutDown
        )

        short.recordBtn = vanilla.Button(
            (150, -60, 120, 30),
            "Record Shortcut",
            callback=self.recordShortcutForList,
        )

        short.deleteBtn = vanilla.Button(
            (280, -60, 120, 30),
            "Delete Shortcut",
            callback=self.deleteShortcut,
        )

        self.w.open()

    def _moveMacroItem(self, direction):
        if not self.current_macro:
            return

        sel = self.w.tabs[0].list.getSelection()
        if not sel:
            return

        i = sel[0]
        j = i + direction

        if j < 0 or j >= len(self.current_macro):
            return

        item = self.current_macro.pop(i)
        self.current_macro.insert(j, item)
        self.updateList()
        self.w.tabs[0].list.setSelection([j])

    def moveMacroItemUp(self, sender):
        self._moveMacroItem(-1)

    def moveMacroItemDown(self, sender):
        self._moveMacroItem(+1)

    def onMainListReorder(self, sender):
        if not self.current_macro:
            return

        order = sender.getOrder()
        if not order:
            return

        try:
            self.current_macro = [self.current_macro[i] for i in order]
        except IndexError:
            return

        self.updateList()

    # -------------------------
    # SHORTCUT PICKER (PRO)
    # -------------------------
    def openShortcutPicker(self, sender):
        self.current_macro = []

        self.picker = vanilla.FloatingWindow((300, 500), "Shortcuts")
        self.picker.getNSWindow().setLevel_(3)

        self.picker.search = vanilla.EditText(
            (10, 10, -10, 25),
            placeholder="Search...",
            callback=self.filterShortcuts,
        )

        self.picker.list = vanilla.List(
            (10, 40, -10, -50),
            [],
            columnDescriptions=[
                {"title": "Shortcut", "key": "shortcut"},
                {"title": "Description", "key": "description"},
            ],
            doubleClickCallback=self.addShortcutToMacro,
        )

        self.picker.stopBtn = vanilla.Button(
            (10, -40, -10, 30),
            "■ STOP",
            callback=self.closeShortcutPicker,
        )

        self.filteredShortcuts = list(self.data["shortcuts"])
        self.refreshPicker()
        self.picker.open()

    def closeShortcutPicker(self, sender):
        try:
            if hasattr(self, "picker"):
                self.picker.close()
        except:
            pass

    def filterShortcuts(self, sender):
        q = sender.get().lower()

        self.filteredShortcuts = [
            s
            for s in self.data["shortcuts"]
            if q in s.get("shortcut", "").lower()
            or q in s.get("description", "").lower()
        ]

        self.refreshPicker()

    def refreshPicker(self):
        if hasattr(self, "picker"):
            self.picker.list.set(self.filteredShortcuts)

    def addShortcutToMacro(self, sender):
        sel = sender.getSelection()
        if not sel:
            return

        s = self.filteredShortcuts[sel[0]]

        action = {
            "keycode": s["keycode"],
            "char": s["char"],
            "cmd": s["cmd"],
            "alt": s["alt"],
            "shift": s["shift"],
            "ctrl": s["ctrl"],
        }

        self.current_macro.append(action)
        self.updateList()

    # -------------------------
    # RECORD SHORTCUT (CREAR)
    # -------------------------
    def recordShortcutForList(self, sender):
        self.stopMonitor()
        self.recording_shortcut_for_list = True

        self.monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            1 << 10,
            self.captureShortcutForList,
        )

    def captureShortcutForList(self, event):
        if event.type() != NSEventTypeKeyDown:
            return event

        if not self.recording_shortcut_for_list:
            return event

        char = event.charactersIgnoringModifiers() or ""
        flags = event.modifierFlags()

        shortcut = {
            "keycode": int(event.keyCode()),
            "char": str(char),
            "cmd": bool(flags & (1 << 20)),
            "alt": bool(flags & (1 << 19)),
            "shift": bool(flags & (1 << 17)),
            "ctrl": bool(flags & (1 << 18)),
            "description": "",
        }

        shortcut["shortcut"] = self.formatShortcutDisplay(shortcut)

        existing = [s["shortcut"] for s in self.data["shortcuts"]]

        if shortcut["shortcut"] not in existing:
            self.data["shortcuts"].append(shortcut)
            self.refreshShortcutList()
            self.saveToFile()

        self.recording_shortcut_for_list = False
        self.stopMonitor()

        return None

    # -------------------------
    # DISPLAY
    # -------------------------
    def formatShortcutDisplay(self, a):
        special = {
            126: "↑",
            125: "↓",
            123: "←",
            124: "→",
            36: "↩",
            51: "⌫",
            53: "⎋",
        }

        keys = []
        if a.get("cmd"):
            keys.append("⌘")
        if a.get("alt"):
            keys.append("⌥")
        if a.get("shift"):
            keys.append("⇧")
        if a.get("ctrl"):
            keys.append("^")

        key_display = special.get(a.get("keycode"), a.get("char", "").upper())
        keys.append(key_display)

        return "".join(keys)

    def updateList(self):
        items = []

        for a in self.current_macro:
            display = self.formatShortcutDisplay(a)

            desc = ""
            for s in self.data["shortcuts"]:
                if (
                    s.get("keycode") == a.get("keycode")
                    and s.get("cmd") == a.get("cmd")
                    and s.get("alt") == a.get("alt")
                    and s.get("shift") == a.get("shift")
                    and s.get("ctrl") == a.get("ctrl")
                ):
                    desc = s.get("description", "")
                    break

            if desc:
                items.append(f"{display:<6} {desc}")
            else:
                items.append(display)

        self.w.tabs[0].list.set(items)

    # -------------------------
    # SHORTCUT LIST
    # -------------------------
    
    def _moveShortcutItem(self, direction):
        sel = self.w.tabs[1].shortcutList.getSelection()
        if not sel:
            return

        i = sel[0]
        j = i + direction

        if j < 0 or j >= len(self.data["shortcuts"]):
            return

        item = self.data["shortcuts"].pop(i)
        self.data["shortcuts"].insert(j, item)
        self.refreshShortcutList()
        self.w.tabs[1].shortcutList.setSelection([j])
        self.saveToFile()

        if hasattr(self, "picker"):
            self.filteredShortcuts = list(self.data["shortcuts"])
            self.refreshPicker()

    def moveShortcutUp(self, sender):
        self._moveShortcutItem(-1)

    def moveShortcutDown(self, sender):
        self._moveShortcutItem(+1)

    def refreshShortcutList(self):
        self.updatingList = True
        clean = [dict(s) for s in self.data["shortcuts"]]
        self.w.tabs[1].shortcutList.set(clean)
        self.updatingList = False

    def onShortcutEdit(self, sender):
        if self.updatingList:
            return

        clean = []
        for item in sender.get():
            clean.append(
                {
                    "shortcut": str(item.get("shortcut", "")),
                    "description": str(item.get("description", "")),
                    "keycode": int(item.get("keycode", 0)),
                    "char": str(item.get("char", "")),
                    "cmd": bool(item.get("cmd", False)),
                    "alt": bool(item.get("alt", False)),
                    "shift": bool(item.get("shift", False)),
                    "ctrl": bool(item.get("ctrl", False)),
                }
            )

        self.data["shortcuts"] = clean
        self.saveToFile()

    def deleteShortcut(self, sender):
        try:
            sel = self.w.tabs[1].shortcutList.getSelection()
            if not sel:
                return
            del self.data["shortcuts"][sel[0]]
            self.refreshShortcutList()
            self.saveToFile()
        except:
            pass

    # -------------------------
    # DELAYS
    # -------------------------
    def getDelayForAction(self, action):
        base = self.action_delay

        char = (action.get("char") or "").lower()
        cmd = action.get("cmd")

        if cmd and char == "a":
            return max(base, 0.10)
        if cmd and char == "c":
            return max(base, 0.08)
        if cmd and char == "v":
            return max(base, 0.06)

        if cmd:
            return max(base, 0.03)

        return max(base, 0.005)

    # -------------------------
    # PLAY
    # -------------------------
    def runSingleMacroPass(self):
        for action in self.current_macro:
            sendkey(
                action.get("keycode"),
                cmd=action.get("cmd"),
                alt=action.get("alt"),
                shift=action.get("shift"),
                ctrl=action.get("ctrl"),
            )
            time.sleep(self.getDelayForAction(action))

    def playMacro(self, sender=None):
        if not self.current_macro:
            return

        for i in range(self.repeat_count):
            self.runSingleMacroPass()
            if i < self.repeat_count - 1:
                time.sleep(self.repeat_pause)

    # -------------------------
    # MACROS
    # -------------------------
    def askMacroName(self, sender):
        self.dialog = vanilla.Window((300, 120), "Save Macro")
        self.dialog.getNSWindow().setLevel_(3)

        self.dialog.input = vanilla.EditText((10, 35, -10, 25), "")
        self.dialog.ok = vanilla.Button(
            (180, 70, 100, 30), "Save", callback=self.saveNamedMacro
        )
        self.dialog.open()

    def saveNamedMacro(self, sender):
        name = self.dialog.input.get().strip()
        if not name:
            return

        self.data["macros"][name] = self.current_macro.copy()
        self.saveToFile()
        self.dialog.close()
        self.refreshMacroList()

    def refreshMacroList(self):
        self.w.tabs[0].macroList.set(list(self.data["macros"].keys()))

    def loadSelectedMacro(self, sender):
        sel = sender.getSelection()
        if not sel:
            return

        name = list(self.data["macros"].keys())[sel[0]]
        self.current_macro = self.data["macros"][name]
        self.updateList()

    def deleteMacro(self, sender):
        sel = self.w.tabs[0].macroList.getSelection()
        if not sel:
            return

        name = list(self.data["macros"].keys())[sel[0]]
        del self.data["macros"][name]

        self.saveToFile()
        self.refreshMacroList()

    # -------------------------
    # INPUT HANDLERS
    # -------------------------
    def onRepeatChange(self, sender):
        try:
            value = int(sender.get())
            if value < 1:
                value = 1
        except:
            value = 1

        self.repeat_count = value
        sender.set(str(value))

    def onDelayChange(self, sender):
        txt = sender.get().strip().replace(",", ".")
        try:
            value = float(txt)
            if value < 0:
                value = 0.0
        except:
            value = self.action_delay

        self.action_delay = value
        sender.set("{:.2f}".format(self.action_delay))

    # -------------------------
    # JSON IMPORT/EXPORT
    # -------------------------
    def saveMacrosToJson(self, sender=None):
        try:
            panel = NSSavePanel.savePanel()
            if panel.runModal() == 1:
                path = panel.URL().path()
                with open(path, "w") as f:
                    json.dump(self.data, f, indent=2)
        except:
            pass

    def loadMacrosFromJson(self, sender=None):
        try:
            panel = NSOpenPanel.openPanel()
            panel.setAllowedFileTypes_(["json"])

            if panel.runModal() == 1:
                path = panel.URL().path()

                with open(path) as f:
                    loaded = json.load(f)

                if "macros" in loaded:
                    self.data["macros"].update(loaded["macros"])

                if "shortcuts" in loaded:
                    existing = {s["shortcut"]: s for s in self.data["shortcuts"]}

                    for s in loaded["shortcuts"]:
                        if s["shortcut"] not in existing:
                            self.data["shortcuts"].append(s)

                self.refreshMacroList()
                self.refreshShortcutList()
                self.saveToFile()
        except:
            pass

    # -------------------------
    # FILE
    # -------------------------
    def saveMacrosToFile(self, sender=None):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def loadMacrosFile(self, sender=None):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    self.data = json.load(f)
            except:
                self.data = {"macros": {}, "shortcuts": []}
        else:
            self.data = {"macros": {}, "shortcuts": []}

# RUN
if __name__ == "__main__":
    MacroRecorderPRO()