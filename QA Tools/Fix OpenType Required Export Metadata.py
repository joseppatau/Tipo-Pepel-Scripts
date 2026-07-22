#MenuTitle: Fix OpenType Required Export Metadata
# -*- coding: utf-8 -*-
"""
Glyphs.app script.

Opens a diagnostic window, shows debug output, and fixes the source metadata
Glyphs uses to build required OpenType tables during export.
"""

from GlyphsApp import Glyphs, GSCustomParameter

try:
    from GlyphsApp import Message
except Exception:
    Message = None

try:
    from GlyphsApp import INSTANCETYPEVARIABLE
except Exception:
    INSTANCETYPEVARIABLE = None

try:
    from vanilla import Button, FloatingWindow, TextBox, TextEditor
except Exception:
    Button = None
    FloatingWindow = None
    TextBox = None
    TextEditor = None


GLOBAL_PARAMETERS = {
    "fsType": [],
    "Use Typo Metrics": True,
    "codePageRanges": [1252],
    "unicodeRanges": [0],
}

VERTICAL_METRICS = {
    "typoAscender": 800,
    "typoDescender": -230,
    "typoLineGap": 170,
    "hheaAscender": 800,
    "hheaDescender": -230,
    "hheaLineGap": 170,
    "winAscent": 1088,
    "winDescent": 260,
}


def compact_style_name(name):
    return (name or "").lower().replace(" ", "").replace("-", "").replace("_", "")


def weight_from_name(name):
    style = compact_style_name(name)
    if "thin" in style or "hair" in style:
        return 100
    if "extralight" in style or "ultralight" in style:
        return 200
    if "light" in style:
        return 300
    if "medium" in style:
        return 500
    if "semibold" in style or "demibold" in style:
        return 600
    if "extrabold" in style or "ultrabold" in style:
        return 800
    if "black" in style or "heavy" in style:
        return 900
    if "bold" in style:
        return 700
    return 400


def width_from_name(name):
    style = compact_style_name(name)
    if "ultracond" in style or "extracond" in style or "compressed" in style:
        return 2
    if "cond" in style or "narrow" in style:
        return 3
    if "semicond" in style:
        return 4
    if "semiexp" in style:
        return 6
    if "expanded" in style or "wide" in style:
        return 7
    return 5


def custom_parameter(owner, name):
    try:
        parameters = owner.customParameters
    except Exception:
        return None
    for parameter in parameters:
        if parameter.name == name:
            return parameter
    return None


def set_custom_parameter(owner, name, value):
    parameter = custom_parameter(owner, name)
    if parameter is None:
        owner.customParameters.append(GSCustomParameter(name, value))
        return "added"
    if parameter.value == value:
        return "same"
    old_value = parameter.value
    parameter.value = value
    return "changed from %r" % old_value


def get_custom_parameter_value(owner, name):
    parameter = custom_parameter(owner, name)
    if parameter is None:
        return None
    return parameter.value


def missing_value(value):
    return value is None or value == 0 or value == ""


def set_attr_if_missing(owner, attr, value):
    try:
        current = getattr(owner, attr)
    except Exception as error:
        return "unavailable: %s" % error
    if not missing_value(current):
        return "same existing %r" % current
    setattr(owner, attr, value)
    return "set"


def set_bool_if_false(owner, attr, value=True):
    try:
        current = getattr(owner, attr)
    except Exception as error:
        return "unavailable: %s" % error
    if current:
        return "same true"
    setattr(owner, attr, value)
    return "set"


def is_variable_instance(instance):
    if INSTANCETYPEVARIABLE is not None:
        try:
            if instance.type == INSTANCETYPEVARIABLE:
                return True
        except Exception:
            pass
    try:
        type_name = instance.typeName()
        if "variable" in str(type_name).lower():
            return True
    except Exception:
        pass
    try:
        if "variable" in str(instance.type).lower():
            return True
    except Exception:
        pass
    return False


def owner_name(owner, fallback):
    try:
        return owner.name or fallback
    except Exception:
        return fallback


class DebugRunner(object):
    def __init__(self):
        self.lines = []
        self.change_count = 0
        self.warning_count = 0

    def log(self, message=""):
        self.lines.append(str(message))

    def change(self, message):
        self.change_count += 1
        self.log("[CHANGE] %s" % message)

    def warn(self, message):
        self.warning_count += 1
        self.log("[WARN] %s" % message)

    def log_parameter(self, owner, name):
        self.log("    %s = %r" % (name, get_custom_parameter_value(owner, name)))

    def fix_global_parameters(self, font):
        self.log("")
        self.log("Global parameters")
        for name in sorted(GLOBAL_PARAMETERS.keys()):
            before = get_custom_parameter_value(font, name)
            result = set_custom_parameter(font, name, GLOBAL_PARAMETERS[name])
            after = get_custom_parameter_value(font, name)
            self.log("  %s: before=%r after=%r result=%s" % (name, before, after, result))
            if result != "same":
                self.change("global %s = %r" % (name, after))

    def fix_vertical_metrics(self, owner, label):
        self.log("")
        self.log("%s vertical metrics" % label)
        for name in sorted(VERTICAL_METRICS.keys()):
            before = get_custom_parameter_value(owner, name)
            result = set_custom_parameter(owner, name, VERTICAL_METRICS[name])
            after = get_custom_parameter_value(owner, name)
            self.log("  %s: before=%r after=%r result=%s" % (name, before, after, result))
            if result != "same":
                self.change("%s %s = %r" % (label, name, after))

    def fix_instance(self, instance, index):
        instance_name = owner_name(instance, "Instance %s" % index)
        variable = is_variable_instance(instance)

        self.log("")
        self.log("Instance %s: %s" % (index, instance_name))
        self.log("  variable = %s" % variable)

        export_result = set_bool_if_false(instance, "exports", True)
        self.log("  exports result = %s" % export_result)
        if export_result == "set":
            self.change("%s exports = True" % instance_name)

        self.fix_vertical_metrics(instance, "Instance %s" % instance_name)

        if variable:
            self.log("  Skipping static weight/width flags for variable instance.")
            return

        weight = weight_from_name(instance_name)
        width = width_from_name(instance_name)
        self.log("  inferred weightClass = %s" % weight)
        self.log("  inferred widthClass = %s" % width)

        weight_result = set_attr_if_missing(instance, "weightClass", weight)
        self.log("  weightClass result = %s" % weight_result)
        if weight_result == "set":
            self.change("%s weightClass = %s" % (instance_name, weight))

        width_result = set_attr_if_missing(instance, "widthClass", width)
        self.log("  widthClass result = %s" % width_result)
        if width_result == "set":
            self.change("%s widthClass = %s" % (instance_name, width))

        if weight >= 700:
            bold_result = set_bool_if_false(instance, "isBold", True)
            self.log("  isBold result = %s" % bold_result)
            if bold_result == "set":
                self.change("%s isBold = True" % instance_name)

        if "italic" in instance_name.lower() or "oblique" in instance_name.lower():
            italic_result = set_bool_if_false(instance, "isItalic", True)
            self.log("  isItalic result = %s" % italic_result)
            if italic_result == "set":
                self.change("%s isItalic = True" % instance_name)

    def run(self):
        self.lines = []
        self.change_count = 0
        self.warning_count = 0

        font = Glyphs.font
        self.log("OpenType Required Export Metadata Debug")
        self.log("=" * 42)

        if font is None:
            self.warn("No font is open. Open a .glyphs file and run the script again.")
            return self.text()

        self.log("Family: %s" % (font.familyName or "(empty family name)"))
        self.log("Masters: %s" % len(font.masters))
        self.log("Instances: %s" % len(font.instances))
        try:
            self.log("File path: %s" % font.filepath)
        except Exception:
            self.log("File path: unavailable")

        if not font.familyName:
            self.warn("Family name is empty.")

        self.fix_global_parameters(font)

        self.log("")
        self.log("Masters")
        for index, master in enumerate(font.masters, 1):
            master_name = owner_name(master, "Master %s" % index)
            self.fix_vertical_metrics(master, "Master %s" % master_name)

        self.log("")
        self.log("Instances")
        for index, instance in enumerate(font.instances, 1):
            self.fix_instance(instance, index)

        self.log("")
        self.log("Summary")
        self.log("  Changes: %s" % self.change_count)
        self.log("  Warnings: %s" % self.warning_count)
        if self.change_count:
            self.log("  Save the .glyphs file and export fonts again.")
        else:
            self.log("  No changes needed by this script.")
        return self.text()

    def text(self):
        return "\n".join(self.lines)


class DebugWindow(object):
    def __init__(self):
        self.runner = DebugRunner()
        self.w = FloatingWindow((760, 560), "OpenType Export Metadata Debug")
        self.w.title = TextBox((14, 12, -14, 20), "Fix OpenType Required Export Metadata")
        self.w.runButton = Button((14, 40, 140, 28), "Run Fix", callback=self.run_fix)
        self.w.closeButton = Button((164, 40, 90, 28), "Close", callback=self.close)
        self.w.text = TextEditor((14, 80, -14, -14), "")
        self.w.open()
        self.run_fix(None)

    def set_text(self, text):
        self.w.text.set(text)

    def run_fix(self, sender):
        try:
            self.set_text("Running...\n")
            text = self.runner.run()
            self.set_text(text)
            Glyphs.showNotification("OpenType metadata debug finished", "See the debug window for details.")
        except Exception as error:
            self.set_text("ERROR\n=====\n%s" % error)
            if Message is not None:
                Message(title="OpenType metadata script error", message=str(error), OKButton="OK")

    def close(self, sender):
        self.w.close()


def run_in_macro_window():
    runner = DebugRunner()
    try:
        Glyphs.showMacroWindow()
    except Exception:
        pass
    text = runner.run()
    print(text)
    if Message is not None:
        Message(
            title="OpenType metadata debug finished",
            message="Vanilla window support was not available. Debug output was sent to the Macro Panel.",
            OKButton="OK",
        )


if FloatingWindow is None:
    run_in_macro_window()
else:
    DebugWindow()
