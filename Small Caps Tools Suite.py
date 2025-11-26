# MenuTitle: Smallcaps Tools Suite
# -*- coding: utf-8 -*-
# Description: Small caps generator based on uppercase letter components
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
__doc__="""
Small caps generator based on uppercase letter components"""

from GlyphsApp import *
from vanilla import Window, Tabs, TextBox, EditText, Button, PopUpButton, RadioGroup
import re

Glyphs.clearLog()
font = Glyphs.font

if not font or not font.selectedLayers:
    Message("Error", "Open a font and select at least one layer to determine the master.", OKButton="OK")
else:
    masterID = font.selectedLayers[0].master.id


# Cyrillic base glyphs (checked if uni0416 exists)
cyrillicList = [
    "uni0410", "uni0411", "uni0412", "uni0413", "uni0403", "uni0490", "uni0414",
    "uni0415", "uni0400", "uni0401", "uni0416", "uni0417", "uni0418", "uni0419",
    "uni040D", "uni041A", "uni040C", "uni041B", "uni041C", "uni041D", "uni041E",
    "uni041F", "uni0420", "uni0421", "uni0422", "uni0423", "uni0424", "uni0425",
    "uni0426", "uni0427", "uni0428", "uni0429", "uni040F", "uni042C", "uni042B",
    "uni042A", "uni0409", "uni040A", "uni0405", "uni0404", "uni042D", "uni0406",
    "uni0407", "uni0408", "uni040B", "uni042E", "uni042F", "uni0402",
]


# Basic mapping for Latin, numerals, and symbols
scComponents = {
    "a.sc": ["A"], "b.sc": ["B"], "c.sc": ["C"], "d.sc": ["D"], "e.sc": ["E"], "f.sc": ["F"],
    "g.sc": ["G"], "h.sc": ["H"], "i.sc": ["I"], "j.sc": ["J"], "k.sc": ["K"], "l.sc": ["L"],
    "m.sc": ["M"], "n.sc": ["N"], "o.sc": ["O"], "p.sc": ["P"], "q.sc": ["Q"], "r.sc": ["R"],
    "s.sc": ["S"], "t.sc": ["T"], "u.sc": ["U"], "v.sc": ["V"], "w.sc": ["W"], "x.sc": ["X"],
    "y.sc": ["Y"], "z.sc": ["Z"],
    "oe.sc": ["U+0152"], "ae.sc": ["U+00C6"], "germandbls.sc": ["U+00DF"],
    "zero.sc": ["zero"], "one.sc": ["one"], "two.sc": ["two"], "three.sc": ["three"],
    "four.sc": ["four"], "five.sc": ["five"], "six.sc": ["six"], "seven.sc": ["seven"],
    "eight.sc": ["eight"], "nine.sc": ["nine"],
    "ampersand.sc": ["ampersand"], "at.sc": ["at"], "percent.sc": ["percent"],
    "euro.sc": ["euro"], "dollar.sc": ["dollar"], "numbersign.sc": ["numbersign"],
    "asterisk.sc": ["asterisk"], "plus.sc": ["plus"], "minus.sc": ["minus"],
    "equal.sc": ["equal"], "less.sc": ["less"], "greater.sc": ["greater"],
    "slash.sc": ["slash"], "backslash.sc": ["backslash"], "hyphen.sc": ["hyphen"],
    "endash.sc": ["endash"], "emdash.sc": ["emdash"], "question.sc": ["question"],
    "exclam.sc": ["exclam"], "questiondown.sc": ["questiondown"], "exclamdown.sc": ["exclamdown"],
    "parenleft.sc": ["parenleft"], "parenright.sc": ["parenright"],
    "bracketleft.sc": ["bracketleft"], "bracketright.sc": ["bracketright"],
    "braceleft.sc": ["braceleft"], "braceright.sc": ["braceright"],
    "guillemetleft.sc": ["guillemetleft"], "guillemetright.sc": ["guillemetright"],
    "guilsinglleft.sc": ["guilsinglleft"], "guilsinglright.sc": ["guilsinglright"],
    "quoteleft.sc": ["quoteleft"], "quoteright.sc": ["quoteright"],
    "quotedblleft.sc": ["quotedblleft"], "quotedblright.sc": ["quotedblright"],
    "colon.sc": ["colon"], "semicolon.sc": ["semicolon"],
    "periodcentered.sc": ["periodcentered"], "bullet.sc": ["bullet"]
}

SUFFIX = ".sc"

# Explicit special cases for small caps mapping
SPECIAL_MAP = {
    "ae": "AE",
    "oe": "OE",
    "eng": "ENG",
    "eth": "ETH",
    "thorn": "THORN",
    "schwa": "SCHWA",
    "germandbls": "SS",
    "lslash": "Lslash",
    "oslash": "Oslash",
    "nhookleft": "N",
}

# Ensure coverage for digits, punctuation, and symbols
FORCED_BASES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "colon", "semicolon", "exclam", "exclamdown", "question", "questiondown",
    "periodcentered", "bullet", "asterisk", "numbersign", "slash", "backslash",
    "hyphen", "endash", "emdash", "parenleft", "parenright", "braceleft", "braceright",
    "bracketleft", "bracketright", "quotedblleft", "quotedblright", "quoteleft",
    "quoteright", "guillemetleft", "guillemetright", "guilsinglleft", "guilsinglright",
    "at", "ampersand", "dollar", "euro", "plus", "minus", "equal", "greater", "less", "percent"
]


# Find glyph by name or Unicode
def glyph_by_name_or_unicode(ref):
    if ref.startswith("U+"):
        uni_val = ref.replace("U+", "").lower()
        for g in font.glyphs:
            if g.unicode and g.unicode.lower() == uni_val:
                return g
    else:
        for g in font.glyphs:
            if g.name.lower() == ref.lower():
                return g
    return None


def disable_auto_alignment_for_layer(layer):
    """Disable automatic alignment for all components while keeping their original position"""
    for comp in layer.components:
        try:
            pos = comp.position
            comp.automaticAlignment = False
            comp.setPosition_(pos)
        except Exception:
            pass


def update_metrics_for_current_master():
    """Update metrics for all glyphs in the current master"""
    try:
        master = font.selectedFontMaster
        if not master:
            return
        for g in font.glyphs:
            layer = g.layers[master.id]
            if layer:
                layer.updateMetrics()
                layer.syncMetrics()
    except Exception:
        pass


def find_base_name_for_smallcap(sc_name):
    """Determine the correct base glyph name for a small cap"""
    base_name = sc_name[:-len(SUFFIX)]
    
    # Explicit mapping for known exceptions
    if base_name in SPECIAL_MAP:
        return SPECIAL_MAP[base_name]
    
    # Forced inclusion list (numbers, punctuation, symbols)
    if base_name in FORCED_BASES:
        return base_name
    
    # If purely alphabetic, use uppercase
    if re.match(r"^[a-z]+$", base_name):
        return base_name.upper()
    
    # Otherwise, return as is
    return base_name


class SmallcapsToolsSuite:
    def __init__(self):
        # Get font axes to calculate window height
        axes = font.axes
        adjust_sc_height = 150 + 30 * len(axes)
        window_height = max(400, adjust_sc_height)
        
        self.w = Window((500, window_height), "Smallcaps Tools Suite", minSize=(500, 400))
        
        self.w.tabs = Tabs((10, 10, -10, -10), ["SC Generator", "Adjust SC", "Metrics to SC", "Duplicate Components"])
        
        # Tab 1: SC Generator
        self.setup_sc_generator_tab()
        
        # Tab 2: Adjust Smart Components
        self.setup_adjust_sc_tab()
        
        # Tab 3: Metrics to SC
        self.setup_metrics_to_sc_tab()
        
        # Tab 4: Duplicate Components
        self.setup_duplicate_components_tab()
        
        self.w.open()
    
    def setup_sc_generator_tab(self):
        # SC Generator Tab
        tab = self.w.tabs[0]
        
        # Use unique attribute names to avoid conflicts
        tab.scaleText = TextBox((10, 12, 200, 20), "Smallcaps scale (%):")
        tab.scaleInput = EditText((220, 12, 80, 20), "85")

        tab.widthText = TextBox((10, 42, 60, 20), "Width:")
        tab.widthMode = PopUpButton((80, 40, 110, 20), ["Increase", "Decrease"])
        tab.widthValue = EditText((200, 40, 60, 20), "8")
        tab.percentSign = TextBox((265, 42, 20, 20), "%")

        tab.scopeRadio = RadioGroup(
            (10, 72, 420, 40),
            ["Apply to all mapping", "Apply only to selected glyphs"],
            isVertical=False,
        )
        tab.scopeRadio.set(0)

        tab.generateButton = Button((10, 120, 440, 36), "Generate smallcaps", callback=self.generate_smallcaps)
    
    def setup_adjust_sc_tab(self):
        # Adjust Smart Components Tab
        tab = self.w.tabs[1]
        
        axes = font.axes
        
        # Use unique attribute names
        tab.instructionText = TextBox((10, 10, 300, 20), "Enter values for each axis:")

        # Store axis inputs in a list
        tab.axisInputs = []
        y = 40
        
        for i, axis in enumerate(axes):
            name = axis.name
            # Create unique attribute names for each control
            label_attr = f"axisLabel_{i}"
            input_attr = f"axisInput_{i}"
            
            setattr(tab, label_attr, TextBox((10, y + 3, 120, 20), f"{name}:"))
            setattr(tab, input_attr, EditText((140, y, 160, 20), "0"))
            
            # Store reference to the input
            tab.axisInputs.append(getattr(tab, input_attr))
            y += 30

        tab.applyButton = Button((10, y, 300, 30), "Apply", callback=self.adjust_smart_components)
    
    def setup_metrics_to_sc_tab(self):
        # Metrics to SC Tab
        tab = self.w.tabs[2]
        
        tab.descriptionText = TextBox(
            (15, 12, 400, 80),
            "Disables automatic alignment (keeping original positions)\n"
            "and assigns metric keys (left/right/widthMetricsKey)\n"
            "to all small caps (.sc) based on their uppercase, number, or symbol counterpart.\n\n"
            "After completion, metrics for the current master are updated."
        )
        tab.metricsButton = Button(
            (15, 100, 400, 50),
            "Assign Metric Keys to All Small Caps (.sc)",
            callback=self.assign_metrics_to_sc
        )
    
    def setup_duplicate_components_tab(self):
        # Duplicate Components Tab
        tab = self.w.tabs[3]
        
        tab.descriptionText = TextBox(
            (15, 12, 400, 80),
            "Duplicates selected components in the active layer to all other masters.\n\n"
            "Make sure you have components selected in the active layer of a glyph."
        )
        tab.duplicateButton = Button(
            (15, 100, 400, 50),
            "Duplicate Selected Components to All Masters",
            callback=self.duplicate_components
        )
    
    def generate_smallcaps(self, sender):
        tab = self.w.tabs[0]
        try:
            scaleFactor = float(tab.scaleInput.get()) / 100.0
            widthPercent = float(tab.widthValue.get()) / 100.0
            if tab.widthMode.get() == 1:
                widthPercent = -widthPercent
        except Exception:
            Message("Error", "Please enter valid numeric values.", OKButton="OK")
            return

        applyToSelected = (tab.scopeRadio.get() == 1)
        master = font.masters[masterID]
        createdCount = scaledCount = renamedCount = 0
        useCyrillic = glyph_by_name_or_unicode("U+0416")

        font.disableUpdateInterface()
        try:
            targetGlyphs = {}

            if applyToSelected:
                for l in font.selectedLayers:
                    base = l.parent
                    if not base:
                        continue
                    targetGlyphs[base.name.lower() + ".sc"] = [base.name]
            else:
                for k, v in scComponents.items():
                    targetGlyphs[k] = v[:]

                if useCyrillic:
                    for baseName in cyrillicList:
                        baseGlyph = glyph_by_name_or_unicode(baseName)
                        if not baseGlyph:
                            continue
                        targetName = baseGlyph.name.lower() + ".sc"
                        targetGlyphs[targetName] = [baseGlyph.name]

            for scName, baseList in targetGlyphs.items():
                if not isinstance(scName, str):
                    continue

                scGlyph = glyph_by_name_or_unicode(scName)
                if not scGlyph:
                    scGlyph = GSGlyph(scName)
                    font.glyphs.append(scGlyph)
                    createdCount += 1

                if masterID not in scGlyph.layers:
                    scGlyph.layers[masterID] = scGlyph.layers[0].copy() if scGlyph.layers else GSLayer()

                targetLayer = scGlyph.layers[masterID]

                try:
                    targetLayer.shapes = []
                    targetLayer.components = []
                    targetLayer.anchors = []
                except Exception:
                    targetLayer.clear()

                componentFound = False
                for baseName in baseList:
                    baseGlyph = glyph_by_name_or_unicode(baseName)
                    if not baseGlyph:
                        print(f"⚠️ Base glyph not found: {baseName}")
                        continue
                    componentFound = True

                    newC = GSComponent(baseGlyph.name)
                    targetLayer.components.append(newC)
                    try:
                        newC.setDisableAlignment_(False)
                    except Exception:
                        pass

                    widthScale = 1.0 + widthPercent
                    newC.transform = NSAffineTransformStruct(
                        m11=scaleFactor * widthScale, m12=0.0,
                        m21=0.0, m22=scaleFactor,
                        tX=0.0, tY=0.0
                    )

                    try:
                        targetLayer.alignComponents()
                    except Exception:
                        pass

                    scaledCount += 1

                if componentFound:
                    scGlyph.category = "Letter"
                    scGlyph.subCategory = "Smallcaps"

            for g in font.glyphs:
                if g.name.endswith(".sc"):
                    baseName = g.name[:-3]
                    if baseName.endswith("-cy"):
                        info = Glyphs.glyphInfoForName(baseName)
                        if info and info.unicode:
                            newName = f"uni{info.unicode.upper()}.sc"
                            if g.name != newName:
                                print(f"🔠 Renaming {g.name} → {newName}")
                                g.name = newName
                                renamedCount += 1

        finally:
            font.enableUpdateInterface()

        Message(
            "Process completed",
            f"Created {createdCount} .sc glyphs, added {scaledCount} components and renamed {renamedCount} Cyrillic glyphs to Unicode names.",
            OKButton="OK"
        )
    
    def adjust_smart_components(self, sender):
        tab = self.w.tabs[1]
        axes = font.axes
        
        values = {}
        for i, axis in enumerate(axes):
            name = axis.name
            try:
                values[name] = float(tab.axisInputs[i].get())
            except:
                values[name] = 0.0

        processed = 0
        font.disableUpdateInterface()
        try:
            for layer in font.selectedLayers:
                glyph = layer.parent
                targetLayer = glyph.layers[masterID]  # only active master
                for comp in targetLayer.components:
                    originalGlyph = font.glyphs[comp.componentName]
                    if originalGlyph and originalGlyph.smartComponentAxes:
                        for axis in originalGlyph.smartComponentAxes:
                            if axis.name in values:
                                comp.smartComponentValues[axis.id] = values[axis.name]
                        processed += 1
        finally:
            font.enableUpdateInterface()

        print(f"Updated {processed} smart components in active master.")
        Message("Process completed", f"Updated {processed} smart components in active master.", OKButton="OK")
    
    def assign_metrics_to_sc(self, sender):
        processed = 0
        skipped = 0

        font.disableUpdateInterface()

        for g in font.glyphs:
            if not g.name.endswith(SUFFIX):
                continue

            base_name = find_base_name_for_smallcap(g.name)
            base_glyph = font.glyphs[base_name]

            if not base_glyph:
                skipped += 1
                continue

            for layer in g.layers:
                if getattr(layer, "isMasterLayer", False):
                    disable_auto_alignment_for_layer(layer)

            g.leftMetricsKey = base_name
            g.rightMetricsKey = base_name
            g.widthMetricsKey = base_name

            processed += 1

        font.enableUpdateInterface()
        update_metrics_for_current_master()

        summary = f"""Processed {processed} small caps (.sc)
Skipped {skipped} without a matching base glyph.
Automatic alignment was disabled while keeping component positions.
Metrics were updated for the current master."""
        
        Message("Process Completed", summary, OKButton="OK")
    
    def duplicate_components(self, sender):
        selectedLayers = font.selectedLayers

        if not selectedLayers:
            Message("No glyph selected", "Select a glyph before running the script.", OKButton="OK")
            return

        layer = selectedLayers[0]
        glyph = layer.parent

        # Selected components
        selectedComponents = [c for c in layer.components if c.selected]
        if not selectedComponents:
            Message("No component selected", "Select a component in the active layer.", OKButton="OK")
            return

        font.disableUpdateInterface()
        try:
            for master in font.masters:
                targetLayer = glyph.layers[master.id]
                if targetLayer != layer:
                    for sourceComponent in selectedComponents:
                        # Create new copy
                        newComponent = GSComponent(sourceComponent.componentName)
                        newComponent.transform = sourceComponent.transform
                        targetLayer.components.append(newComponent)
        finally:
            font.enableUpdateInterface()

        Message("Success", f"Duplicated {len(selectedComponents)} components (including smart) to all masters of {glyph.name}.", OKButton="OK")


# Run the tool suite
SmallcapsToolsSuite()