# MenuTitle: Inspect Kern by Glyph
# -*- coding: utf-8 -*-
# Description: Finds kerning pairs where selected glyphs are present and opens them in a new tab.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# License: Apache2

from __future__ import division, print_function, unicode_literals
from GlyphsApp import Glyphs, Message
import vanilla
import re
import time

DEBUG = False


class InspectKernByGlyph(object):

    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Open a font first.")
            return

        self.w = vanilla.FloatingWindow(
            (220, 315),
            "Inspect Kern by Glyph",
            minSize=(220, 315),
            maxSize=(360, 315)
        )

        self.w.text = vanilla.TextBox(
            (12, 14, -12, 18),
            "Glyph name",
            sizeStyle="small"
        )
        self.w.glyphNames = vanilla.EditText(
            (12, 36, -12, 24),
            "",
            sizeStyle="small"
        )
        self.w.inspectButton = vanilla.Button(
            (12, 74, 90, 24),
            "Inspect",
            callback=self.inspect
        )
        self.w.status = vanilla.TextBox(
            (115, 78, -12, 18),
            "",
            sizeStyle="small"
        )
        self.w.line1 = vanilla.HorizontalLine((12, 108, -12, 1))
        self.w.operationLabel = vanilla.TextBox(
            (12, 123, -12, 18),
            "Operation:",
            sizeStyle="small"
        )
        self.w.operation = vanilla.RadioGroup(
            (12, 144, -12, 24),
            ["Increase", "Decrease"],
            isVertical=False
        )
        self.w.operation.set(1)
        self.w.percentLabel = vanilla.TextBox(
            (12, 178, 80, 18),
            "Percentage:",
            sizeStyle="small"
        )
        self.w.percentInput = vanilla.EditText(
            (92, 174, 60, 24),
            "10",
            sizeStyle="small"
        )
        self.w.applyButton = vanilla.Button(
            (12, 207, -12, 24),
            "Apply to Active Master",
            callback=self.applyScale
        )
        self.w.line2 = vanilla.HorizontalLine((12, 240, -12, 1))
        self.w.deleteButton = vanilla.Button(
            (12, 247, -12, 24),
            "Delete in Active Master",
            callback=self.deleteKerning
        )

        self.w.open()
        self.w.makeKey()
        self._left_key_cache = {}
        self._right_key_cache = {}

    def buildRepresentativeCaches(self):
        font = self.font
        self._left_key_cache = {}
        self._right_key_cache = {}

        for glyph in font.glyphs:
            self._left_key_cache[glyph.name] = glyph.name
            self._right_key_cache[glyph.name] = glyph.name

            if glyph.rightKerningGroup:
                key = "@MMK_L_%s" % glyph.rightKerningGroup
                if key not in self._left_key_cache:
                    group_name = glyph.rightKerningGroup
                    self._left_key_cache[key] = group_name if group_name in font.glyphs else glyph.name

            if glyph.leftKerningGroup:
                key = "@MMK_R_%s" % glyph.leftKerningGroup
                if key not in self._right_key_cache:
                    group_name = glyph.leftKerningGroup
                    self._right_key_cache[key] = group_name if group_name in font.glyphs else glyph.name

    def parseGlyphNames(self, text):
        text = text.replace("/", " ")
        names = [n.strip() for n in re.split(r"[,\s]+", text) if n.strip()]
        return list(dict.fromkeys(names))

    def caseForGlyph(self, glyph):
        if not glyph:
            return "H"

        if glyph.category == "Letter":
            if glyph.case == 2:
                return "h"
            if glyph.case == 1:
                return "H"
            if glyph.name and glyph.name[0].islower():
                return "h"
            return "H"

        if glyph.category == "Punctuation":
            return "h"

        return "H"

    def glyphString(self, text):
        if not text:
            return ""
        return "/" + "/".join([c for c in text])

    def glyphNamesString(self, names):
        if not names:
            return ""
        return "/" + "/".join(names)

    def contextualGlyphNames(self, glyph):
        if glyph and glyph.name and glyph.name.endswith(".sc"):
            return ["h.sc", "h.sc"]
        return [self.caseForGlyph(glyph), self.caseForGlyph(glyph)]

    def contextualPairString(self, left_name, right_name):
        font = self.font
        left = font.glyphs[left_name] if left_name in font.glyphs else None
        right = font.glyphs[right_name] if right_name in font.glyphs else None

        prefix = self.contextualGlyphNames(left)
        suffix = self.contextualGlyphNames(right)

        return "%s/%s/%s%s" % (
            self.glyphNamesString(prefix),
            left_name,
            right_name,
            self.glyphNamesString(suffix)
        )

    def keyForLeftGlyph(self, glyph):
        keys = [glyph.name]
        if glyph.rightKerningGroup:
            keys.append("@MMK_L_%s" % glyph.rightKerningGroup)
        return keys

    def keyForRightGlyph(self, glyph):
        keys = [glyph.name]
        if glyph.leftKerningGroup:
            keys.append("@MMK_R_%s" % glyph.leftKerningGroup)
        return keys

    def representativeForLeftKey(self, key):
        if key in self._left_key_cache:
            return self._left_key_cache[key]

        font = self.font
        result = None

        if key.startswith("@MMK_L_"):
            group = key.replace("@MMK_L_", "", 1)
            if group in font.glyphs:
                result = group
            else:
                for glyph in font.glyphs:
                    if glyph.rightKerningGroup == group:
                        result = glyph.name
                        break
        elif key in font.glyphs:
            result = key

        self._left_key_cache[key] = result
        return result

    def representativeForRightKey(self, key):
        if key in self._right_key_cache:
            return self._right_key_cache[key]

        font = self.font
        result = None

        if key.startswith("@MMK_R_"):
            group = key.replace("@MMK_R_", "", 1)
            if group in font.glyphs:
                result = group
            else:
                for glyph in font.glyphs:
                    if glyph.leftKerningGroup == group:
                        result = glyph.name
                        break
        elif key in font.glyphs:
            result = key

        self._right_key_cache[key] = result
        return result

    def displayPairForKerningPair(self, left_key, right_key):
        left_name = self.representativeForLeftKey(left_key)
        right_name = self.representativeForRightKey(right_key)

        if not left_name or not right_name:
            return []

        return [(left_name, right_name)]

    def formatPairs(self, pairs, per_line=6, gap="    "):
        lines = []
        for i in range(0, len(pairs), per_line):
            chunk = pairs[i:i + per_line]
            lines.append(gap.join([
                self.contextualPairString(left, right)
                for left, right in chunk
            ]))
        return lines

    def resolveKerningKey(self, key):
        font = self.font

        if isinstance(key, str) and key.startswith("@MMK_"):
            return key

        if isinstance(key, str) and key in font.glyphs:
            return key

        if isinstance(key, str) and len(key) == 36:
            for glyph in font.glyphs:
                if glyph.id == key:
                    return glyph.name

        return key

    def currentTargetContext(self):
        font = Glyphs.font
        if not font:
            Message("No font open", "Open a font first.")
            return None

        self.font = font
        self.buildRepresentativeCaches()

        master = font.selectedFontMaster
        if not master:
            Message("No master selected", "Select a master first.")
            return None

        target_names = self.parseGlyphNames(self.w.glyphNames.get())
        missing = [name for name in target_names if name not in font.glyphs]
        target_names = [name for name in target_names if name in font.glyphs]

        if not target_names:
            Message("No glyphs found", "Write at least one valid glyph name.")
            return None

        target_keys_by_name = {}
        all_target_left_keys = set()
        all_target_right_keys = set()

        for name in target_names:
            glyph = font.glyphs[name]
            left_keys = set(self.keyForLeftGlyph(glyph))
            right_keys = set(self.keyForRightGlyph(glyph))
            target_keys_by_name[name] = {
                "left": left_keys,
                "right": right_keys,
            }
            all_target_left_keys.update(left_keys)
            all_target_right_keys.update(right_keys)

        return {
            "font": font,
            "master": master,
            "master_id": master.id,
            "target_names": target_names,
            "missing": missing,
            "target_keys_by_name": target_keys_by_name,
            "all_target_left_keys": all_target_left_keys,
            "all_target_right_keys": all_target_right_keys,
        }

    def matchingKerningEntries(self, context):
        font = context["font"]
        master_id = context["master_id"]
        all_target_left_keys = context["all_target_left_keys"]
        all_target_right_keys = context["all_target_right_keys"]

        entries = []
        kerning = font.kerning.get(master_id, {})

        for left_key, right_dict in kerning.items():
            for right_key, value in right_dict.items():
                if left_key not in all_target_left_keys and right_key not in all_target_right_keys:
                    continue
                if value is None:
                    continue
                entries.append((left_key, right_key, value))

        return entries

    def parsePercentage(self):
        raw_value = self.w.percentInput.get()
        if raw_value is None:
            Message("Error", "Percentage field is empty.")
            return None

        value_str = str(raw_value).strip().replace(",", ".")
        if value_str.endswith("%"):
            value_str = value_str[:-1].strip()

        try:
            return float(value_str)
        except:
            Message("Error", "Invalid percentage value: '%s'" % raw_value)
            return None

    def inspect(self, sender=None):
        context = self.currentTargetContext()
        if not context:
            return

        font = context["font"]
        master = context["master"]
        start_time = time.time()

        target_names = context["target_names"]
        missing = context["missing"]
        target_keys_by_name = context["target_keys_by_name"]
        pairs_by_name = {}
        seen_by_name = {}
        for name in target_names:
            pairs_by_name[name] = {
                "left": [],
                "right": [],
            }
            seen_by_name[name] = {
                "left": set(),
                "right": set(),
            }
        touched_kerning_pairs = 0

        print("\n" + "=" * 80)
        print("INSPECT KERN BY GLYPH")
        print("=" * 80)
        print("Master: %s" % master.name)
        print("Targets: %s" % ", ".join(target_names))
        if missing:
            print("Missing glyphs: %s" % ", ".join(missing))

        for left_key, right_key, value in self.matchingKerningEntries(context):
            touched_kerning_pairs += 1
            expanded = self.displayPairForKerningPair(left_key, right_key)
            if DEBUG:
                print("Kerning pair: %s + %s = %s -> %d display pair(s)" % (
                    left_key,
                    right_key,
                    value,
                    len(expanded)
                ))

            for pair in expanded:
                for name in target_names:
                    keys = target_keys_by_name[name]

                    if left_key in keys["left"] and pair not in seen_by_name[name]["left"]:
                        pairs_by_name[name]["left"].append(pair)
                        seen_by_name[name]["left"].add(pair)

                    if right_key in keys["right"] and pair not in seen_by_name[name]["right"]:
                        pairs_by_name[name]["right"].append(pair)
                        seen_by_name[name]["right"].add(pair)

        total_display_pairs = sum(
            len(pairs_by_name[name]["left"]) + len(pairs_by_name[name]["right"])
            for name in target_names
        )

        if not total_display_pairs:
            self.w.status.set("No kerning pairs found")
            Message(
                "No kerning pairs found",
                "No kerning pairs found for: %s" % ", ".join(target_names)
            )
            return

        title = "Inspect Kern: %s (%s)" % (", ".join(target_names), master.name)
        lines = [title, ""]

        multiple_targets = len(target_names) > 1
        for target_index, name in enumerate(target_names):
            left_pairs = pairs_by_name[name]["left"]
            right_pairs = pairs_by_name[name]["right"]

            if not left_pairs and not right_pairs:
                continue

            if target_index > 0 and multiple_targets:
                lines.append("")

            if multiple_targets:
                lines.append("/%s" % name)
                lines.append("")

            if left_pairs:
                lines.append("Left side (%d)" % len(left_pairs))
                lines.extend(self.formatPairs(left_pairs))
                lines.append("")

            if right_pairs:
                lines.append("Right side (%d)" % len(right_pairs))
                lines.extend(self.formatPairs(right_pairs))
                lines.append("")

        while lines and lines[-1] == "":
            lines.pop()

        tab = font.newTab("\n".join(lines))
        font.currentTab = tab

        self.w.status.set("%d pairs" % total_display_pairs)

        print("Kerning pairs touched: %d" % touched_kerning_pairs)
        print("Display pairs generated: %d" % total_display_pairs)
        print("Time: %.3fs" % (time.time() - start_time))
        print("=" * 80)

    def applyScale(self, sender=None):
        context = self.currentTargetContext()
        if not context:
            return

        percent = self.parsePercentage()
        if percent is None:
            return

        operation_idx = self.w.operation.get()
        if operation_idx == 0:
            factor = 1.0 - percent / 100.0
            operation_name = "Increase"
        else:
            factor = 1.0 + percent / 100.0
            operation_name = "Decrease"

        font = context["font"]
        master_id = context["master_id"]
        entries = self.matchingKerningEntries(context)

        if not entries:
            Message("Info", "No kerning pairs found for: %s" % ", ".join(context["target_names"]))
            return

        updated = 0
        font.disableUpdateInterface()
        try:
            for left_key, right_key, value in entries:
                left = self.resolveKerningKey(left_key)
                right = self.resolveKerningKey(right_key)
                if not left or not right:
                    continue

                new_value = int(round(value * factor))
                font.setKerningForPair(master_id, left, right, new_value)
                updated += 1
        finally:
            font.enableUpdateInterface()

        self.w.status.set("%d updated" % updated)
        Message(
            "Done",
            "Updated: %d\nOperation: %s\nPercentage: %s%%\nGlyphs: %s" % (
                updated,
                operation_name,
                percent,
                ", ".join(context["target_names"])
            )
        )
        self.inspect(None)

    def deleteKerning(self, sender=None):
        context = self.currentTargetContext()
        if not context:
            return

        font = context["font"]
        master_id = context["master_id"]
        entries = self.matchingKerningEntries(context)

        if not entries:
            Message("Info", "No kerning pairs found for: %s" % ", ".join(context["target_names"]))
            return

        deleted = 0
        font.disableUpdateInterface()
        try:
            for left_key, right_key, value in entries:
                left = self.resolveKerningKey(left_key)
                right = self.resolveKerningKey(right_key)
                if not left or not right:
                    continue

                font.removeKerningForPair(master_id, left, right)
                deleted += 1
        finally:
            font.enableUpdateInterface()

        self.w.status.set("%d deleted" % deleted)
        Message(
            "Done",
            "Deleted: %d\nGlyphs: %s" % (
                deleted,
                ", ".join(context["target_names"])
            )
        )


InspectKernByGlyph()
