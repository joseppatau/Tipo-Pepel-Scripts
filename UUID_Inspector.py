# MenuTitle: UUID Inspector
# -*- coding: utf-8 -*-
# Description: Find glyphs by UUID or character/name and display detailed information
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
__doc__="""
Find glyphs by UUID or character/name and display detailed information"""



from GlyphsApp import *
import uuid
from vanilla import Window, Tabs, TextBox, EditText, Button, TextEditor

def findGlyphByUUID(uuid_string):
    """
    Find a glyph by its UUID and display detailed information
    """
    font = Glyphs.font
    if not font:
        return "❌ No font open"
    
    output_lines = []
    output_lines.append(f"🔍 Searching UUID: {uuid_string}")
    
    # Check if UUID has valid format
    try:
        uuid_obj = uuid.UUID(uuid_string)
        output_lines.append(f"✅ Valid UUID: {uuid_obj}")
    except ValueError:
        output_lines.append(f"❌ Invalid UUID format: {uuid_string}")
        return "\n".join(output_lines)
    
    found_glyph = None
    
    # Search in all font glyphs
    for glyph in font.glyphs:
        if glyph.id.lower() == uuid_string.lower():
            found_glyph = glyph
            break
    
    if found_glyph:
        output_lines.extend(getGlyphInfo(found_glyph))
    else:
        output_lines.append(f"❌ No glyph found with UUID: {uuid_string}")
        output_lines.append("\n📋 Some available UUIDs in the font:")
        count = 0
        for glyph in font.glyphs:
            if count < 5:
                output_lines.append(f"   {glyph.name}: {glyph.id}")
                count += 1
            else:
                break
    
    return "\n".join(output_lines)

def findGlyphByCharacter(char_or_name):
    """
    Find a glyph by character or name
    """
    font = Glyphs.font
    if not font:
        return "❌ No font open"
    
    output_lines = []
    output_lines.append(f"🔍 Searching: '{char_or_name}'")
    
    found_glyphs = []
    
    # Search by exact name
    if char_or_name in font.glyphs:
        found_glyphs.append(font.glyphs[char_or_name])
        output_lines.append(f"✅ Found by name: {char_or_name}")
    
    # Search by single character
    elif len(char_or_name) == 1:
        char = char_or_name
        unicode_hex = f"{ord(char):04X}"
        unicode_name = f"uni{unicode_hex}"
        
        output_lines.append(f"🔤 Character: '{char}' (U+{unicode_hex})")
        
        # Search by Unicode
        for glyph in font.glyphs:
            if hasattr(glyph, 'unicode') and glyph.unicode == unicode_hex:
                found_glyphs.append(glyph)
                output_lines.append(f"✅ Found by Unicode: {glyph.name}")
                break
        
        # Search by unicode name
        if unicode_name in font.glyphs and font.glyphs[unicode_name] not in found_glyphs:
            found_glyphs.append(font.glyphs[unicode_name])
            output_lines.append(f"✅ Found by Unicode name: {unicode_name}")
    
    # Search by partial name
    else:
        matching_glyphs = []
        for glyph in font.glyphs:
            if char_or_name.lower() in glyph.name.lower():
                matching_glyphs.append(glyph)
        
        if matching_glyphs:
            found_glyphs.extend(matching_glyphs)
            output_lines.append(f"✅ Found {len(matching_glyphs)} glyphs with '{char_or_name}' in the name")
    
    if found_glyphs:
        for i, glyph in enumerate(found_glyphs):
            if i > 0:
                output_lines.append("\n" + "═" * 40 + "\n")
            output_lines.extend(getGlyphInfo(glyph))
    else:
        output_lines.append(f"❌ No glyph found for: '{char_or_name}'")
        output_lines.append("\n💡 Suggestions:")
        output_lines.append("   - Use a single character (ex: 'A')")
        output_lines.append("   - Use the exact glyph name (ex: 'Aacute')")
        output_lines.append("   - Use part of the name (ex: 'sc')")
    
    return "\n".join(output_lines)

def getGlyphInfo(glyph):
    """Get detailed glyph information safely"""
    info_lines = []
    info_lines.append(f"✅ GLYPH FOUND:")
    info_lines.append(f"   📝 Name: {glyph.name}")
    info_lines.append(f"   🆔 UUID: {glyph.id}")
    
    # Unicode information with safe handling
    unicode_info = getattr(glyph, 'unicode', None)
    info_lines.append(f"   🔤 Unicode: {unicode_info}")
    
    # Category information with safe handling
    category = getattr(glyph, 'category', 'N/A')
    subCategory = getattr(glyph, 'subCategory', 'N/A')
    info_lines.append(f"   📂 Category: {category}")
    info_lines.append(f"   🏷️ Subcategory: {subCategory}")
    
    # Width information from master layer
    try:
        master_layer = glyph.layers[0]
        width = master_layer.width
        info_lines.append(f"   📏 Width: {width}")
    except:
        info_lines.append(f"   📏 Width: N/A")
    
    # Color information
    color = getattr(glyph, 'color', 'N/A')
    info_lines.append(f"   🎨 Color: {color}")
    
    # Export information
    export = getattr(glyph, 'export', 'N/A')
    info_lines.append(f"   📊 Export: {export}")
    
    # Character information if has Unicode
    if unicode_info:
        try:
            char_code = int(unicode_info, 16)
            character = chr(char_code)
            info_lines.append(f"   🔤 Character: '{character}' (U+{unicode_info})")
        except:
            info_lines.append(f"   🔤 Character: Could not decode (Unicode: {unicode_info})")
    else:
        info_lines.append(f"   🔤 Character: No Unicode code")
    
    # Kerning groups information
    left_group = getattr(glyph, 'leftKerningGroup', None)
    right_group = getattr(glyph, 'rightKerningGroup', None)
    info_lines.append(f"   ⬅️ Left kerning group: {left_group}")
    info_lines.append(f"   ➡️ Right kerning group: {right_group}")
    
    # Layer information
    try:
        if glyph.layers:
            master_layer = glyph.layers[0]
            if hasattr(master_layer, 'bounds') and master_layer.bounds:
                bounds = master_layer.bounds
                info_lines.append(f"   📐 Height: {bounds.size.height:.1f}")
                info_lines.append(f"   📐 Width: {bounds.size.width:.1f}")
            else:
                info_lines.append(f"   📐 Dimensions: Not available")
    except:
        info_lines.append(f"   📐 Dimensions: Error getting")
    
    return info_lines

def findUUIDInKerning(search_string):
    """
    Search if UUID or name appears in font kerning
    """
    font = Glyphs.font
    if not font:
        return "❌ No font open"
    
    output_lines = []
    output_lines.append(f"🔍 Searching in kerning: {search_string}")
    
    master = font.selectedFontMaster
    kerning_dict = font.kerning.get(master.id, {})
    
    found_in_kerning = False
    
    # Determine if it's UUID or name
    is_uuid = False
    try:
        uuid.UUID(search_string)
        is_uuid = True
    except ValueError:
        is_uuid = False
    
    for left_key in kerning_dict.keys():
        left_name = nameForID(font, left_key)
        
        # Search in left side
        if (is_uuid and str(left_key).lower() == search_string.lower()) or \
           (not is_uuid and search_string.lower() in left_name.lower()):
            output_lines.append(f"✅ FOUND IN LEFT KERNING")
            output_lines.append(f"   ⬅️ Left side: {left_name} ({left_key})")
            right_pairs = kerning_dict[left_key]
            for right_key, value in right_pairs.items():
                right_name = nameForID(font, right_key)
                output_lines.append(f"   ➡️ Pair with: {right_name} ({right_key}) = {value}")
            found_in_kerning = True
        
        # Search in right side within each left pair
        right_pairs = kerning_dict[left_key]
        for right_key in right_pairs.keys():
            right_name = nameForID(font, right_key)
            
            if (is_uuid and str(right_key).lower() == search_string.lower()) or \
               (not is_uuid and search_string.lower() in right_name.lower()):
                output_lines.append(f"✅ FOUND IN RIGHT KERNING")
                output_lines.append(f"   ⬅️ Pair with: {left_name} ({left_key})")
                output_lines.append(f"   ➡️ Right side: {right_name} ({right_key}) = {right_pairs[right_key]}")
                found_in_kerning = True
    
    if not found_in_kerning:
        output_lines.append("❌ Not found in kerning")
    
    return "\n".join(output_lines)

def nameForID(font, ID):
    """Helper function to get glyph name from ID"""
    try:
        if isinstance(ID, str) and ID.startswith("@"):
            return ID
        else:
            glyph = font.glyphForId_(ID)
            return glyph.name if glyph else str(ID)
    except:
        return str(ID)

class UUIDInspector:
    def __init__(self):
        # Create window with tabs
        self.w = Window((650, 750), "UUID Inspector", minSize=(550, 550))
        
        # Main title
        self.w.title = TextBox((15, 15, -15, 25), "UUID Inspector")
        
        # UUID search field
        self.w.uuidLabel = TextBox((15, 50, -15, 20), "Search by UUID:")
        self.w.uuidInput = EditText((15, 75, -15, 24), "98D74AA0-5FE6-4F21-83DA-BBAD2AAB8B3F")
        
        # Character/name search field
        self.w.charLabel = TextBox((15, 115, -15, 20), "Search by character or name:")
        self.w.charInput = EditText((15, 140, -15, 24), "A")
        
        # Buttons in row
        self.w.searchUUIDButton = Button((15, 180, 130, 30), "🔍 Search by UUID", callback=self.searchUUIDCallback)
        self.w.searchCharButton = Button((155, 180, 150, 30), "🔤 Search by Character", callback=self.searchCharCallback)
        self.w.clearButton = Button((315, 180, 80, 30), "Clear", callback=self.clearCallback)
        
        # Results tabs
        self.w.tabs = Tabs((15, 225, -15, -15), ["Glyph", "Kerning"])
        
        # Results area for Glyph
        self.w.tabs[0].results = TextEditor((10, 10, -10, -10), "", readOnly=True)
        
        # Results area for Kerning
        self.w.tabs[1].results = TextEditor((10, 10, -10, -10), "", readOnly=True)
        
        self.w.open()
    
    def searchUUIDCallback(self, sender):
        """Callback for UUID search"""
        uuid_string = self.w.uuidInput.get().strip()
        
        if not uuid_string:
            self.clearCallback(None)
            self.w.tabs[0].results.set("❌ Please enter a UUID")
            self.w.tabs[1].results.set("❌ Please enter a UUID")
            return
        
        # Search glyph information
        glyph_result = findGlyphByUUID(uuid_string)
        self.w.tabs[0].results.set(glyph_result)
        
        # Search kerning information
        kerning_result = findUUIDInKerning(uuid_string)
        self.w.tabs[1].results.set(kerning_result)
    
    def searchCharCallback(self, sender):
        """Callback for character or name search"""
        char_string = self.w.charInput.get().strip()
        
        if not char_string:
            self.clearCallback(None)
            self.w.tabs[0].results.set("❌ Please enter a character or name")
            self.w.tabs[1].results.set("❌ Please enter a character or name")
            return
        
        # Search glyph information
        glyph_result = findGlyphByCharacter(char_string)
        self.w.tabs[0].results.set(glyph_result)
        
        # Search kerning information
        kerning_result = findUUIDInKerning(char_string)
        self.w.tabs[1].results.set(kerning_result)
    
    def clearCallback(self, sender):
        """Callback to clear results"""
        self.w.tabs[0].results.set("")
        self.w.tabs[1].results.set("")

# Execute script
if __name__ == "__main__":
    font = Glyphs.font
    if not font:
        Message("Error", "Open a font before running this script", OKButton="OK")
    else:
        UUIDInspector()