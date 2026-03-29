# MenuTitle: Kerning Scale Tool
# -*- coding: utf-8 -*-
# Description: Scales kerning pairs by a percentage with optional group filtering in the active master.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
import math
from GlyphsApp import Glyphs, Message
from AppKit import NSFont, NSAttributedString, NSFontAttributeName


class ScaleKerningWithGroups:
    
    def __init__(self):
        self.w = vanilla.FloatingWindow((220, 260), "Kerning Scale Tool")
        
        y = 15
        
        # Título
        title = vanilla.TextBox((15, y, -15, 22), "SCALE KERN BY PERCENTAGE")
        title.getNSTextField().setFont_(NSFont.boldSystemFontOfSize_(13))
        y += 30
        
        # Percentage input
        self.w.percentLabel = vanilla.TextBox((15, y-10, 80, 22), "Percentage:")
        self.w.percentInput = vanilla.EditText((95, y-10, 60, 22), "10")
        y += 30
        
        # Operation radio (Increase/Decrease)
        self.w.operationLabel = vanilla.TextBox((15, y-8, 80, 22), "Operation:")
        self.w.operation = vanilla.RadioGroup((15, y+10, 200, 30), ["Increase", "Decrease"], isVertical=False)
        self.w.operation.set(1)  # Default: Decrease
        y += 35
        
        # Group filter
        self.w.groupFilterLabel = vanilla.TextBox((15, y+10, 150, 22), "Apply only in these groups:")
        y += 22
        self.w.groupFilter = vanilla.EditText((15, y+10, 180, 22), placeholder="@A @V @T")
        y += 35
        
        # Note about group format
        self.w.note = vanilla.TextBox((15, y+5, -15, 40), 
            "• Separate groups with spaces\n"

            "• Leave empty to apply to ALL pairs",
            sizeStyle="small"
        )
        y += 45
        
        # Apply button
        self.w.applyButton = vanilla.Button((15, y, 180, 24), "Apply to Active Master", callback=self.applyScale)
        
        self.w.open()
    
    def getGroupsList(self):
        """Parse groups from input field"""
        text = self.w.groupFilter.get().strip()
        if not text:
            return []
        
        groups = []
        for item in text.split():
            item = item.strip()
            if item:
                # Ensure group has @ prefix for kerning groups
                if not item.startswith('@'):
                    item = '@' + item
                groups.append(item)
        
        return groups
    
    def keyMatchesGroups(self, key, groups):
        """Check if a kerning key matches any of the specified groups"""
        if not groups:
            return True
        
        # Convert key to string for comparison
        key_str = str(key)
        
        for group in groups:
            # Check exact match
            if key_str == group:
                return True
            
            # Check if it's a group member key (@MMK_L_group or @MMK_R_group)
            if key_str.startswith('@MMK_L_') and key_str[7:] == group[1:]:
                return True
            if key_str.startswith('@MMK_R_') and key_str[7:] == group[1:]:
                return True
        
        return False
    
    def applyScale(self, sender):
        """Apply scaling to kerning pairs"""
        font = Glyphs.font
        if not font:
            Message("Error", "No font open.", OKButton="OK")
            return
        
        master = font.selectedFontMaster
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return
        
        # Get percentage value
        raw_value = self.w.percentInput.get()
        if raw_value is None:
            Message("Error", "Percentage field is empty.", OKButton="OK")
            return
        
        value_str = str(raw_value).strip()
        value_str = value_str.replace(",", ".")
        
        if value_str.endswith("%"):
            value_str = value_str[:-1].strip()
        
        try:
            percent = float(value_str)
        except:
            Message("Error", f"Invalid percentage value: '{raw_value}'", OKButton="OK")
            return
        
        # Get operation
        operation_idx = self.w.operation.get()
        if operation_idx == 0:  # Increase
            factor = 1.0 - percent / 100.0
            operation_name = "Increase"
        else:  # Decrease
            factor = 1.0 + percent / 100.0
            operation_name = "Decrease"
        
        # Get groups filter
        filter_groups = self.getGroupsList()
        has_filter = len(filter_groups) > 0
        
        master_id = master.id
        if master_id not in font.kerning:
            Message("Info", "No kerning found in the active master.", OKButton="OK")
            return
        
        # Collect kerning pairs that match the filter
        kerning_pairs = []
        filtered_count = 0
        total_count = 0
        
        for left_key, right_dict in font.kerning[master_id].items():
            for right_key, value in right_dict.items():
                if value is not None:
                    total_count += 1
                    
                    # Apply filter if specified
                    if has_filter:
                        left_match = self.keyMatchesGroups(left_key, filter_groups)
                        right_match = self.keyMatchesGroups(right_key, filter_groups)
                        
                        if not (left_match or right_match):
                            continue
                    
                    kerning_pairs.append((left_key, right_key, value))
                    filtered_count += 1
        
        if not kerning_pairs:
            if has_filter:
                groups_str = ", ".join(filter_groups)
                Message("Info", f"No kerning pairs found in specified groups: {groups_str}", OKButton="OK")
            else:
                Message("Info", "No kerning pairs to scale.", OKButton="OK")
            return
        
        # Resolve key to glyph name for setting kerning
        def resolveKey(key):
            if isinstance(key, str) and key.startswith("@MMK_"):
                return key
            if isinstance(key, str) and len(key) == 36:
                for g in font.glyphs:
                    if g.id == key:
                        return g.name
                return None
            return key
        
        # Apply scaling
        count = 0
        font.disableUpdateInterface()
        try:
            for left_key, right_key, value in kerning_pairs:
                left = resolveKey(left_key)
                right = resolveKey(right_key)
                if not left or not right:
                    continue
                
                new_value = int(round(value * factor))
                font.setKerningForPair(master_id, left, right, new_value)
                count += 1
        finally:
            font.enableUpdateInterface()
        
        # Show summary
        if has_filter:
            groups_str = ", ".join(filter_groups)
            summary = (
                f"Total pairs in master: {total_count}\n"
                f"Filtered pairs: {filtered_count}\n"
                f"Updated: {count}\n"
                f"Groups: {groups_str}\n"
                f"Operation: {operation_name}\n"
                f"Percentage: {percent}%"
            )
        else:
            summary = (
                f"Total pairs: {total_count}\n"
                f"Updated: {count}\n"
                f"Operation: {operation_name}\n"
                f"Percentage: {percent}%"
            )
        
        Message("Done", summary, OKButton="OK")


# Run the script
ScaleKerningWithGroups()