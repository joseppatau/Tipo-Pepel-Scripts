## Copy Kerning from Open Font

**Description**  
Copies kerning data from other open fonts into the current font, with flexible selection of masters and matching logic based on master name or ID.

**Author**  
Your Name (with AI assistance)

**License**  
Apache2

---

## Features

* Copy kerning from any open font (excluding current)
* Supports multiple source fonts simultaneously
* Master matching by ID (current master) or by name
* Select specific masters via checkbox UI
* Select All / Deselect All toggle
* Dynamic UI with scroll support
* Safe kerning overwrite per master

---

## Core

* Master-to-master kerning transfer
* Name-based and ID-based matching logic
* Direct kerning dictionary manipulation
* Multi-font iteration handling

---

## Tools

### 🔹 Current Master Copy

Copies kerning from a source master with the same ID as the current master.

### 🔹 All Masters Copy

Copies kerning from all masters in open fonts, matching by master name.

### 🔹 Selected Masters Copy

Allows manual selection of specific masters to copy kerning from.

### 🔹 Master Selector UI

Interactive list of fonts and masters with checkboxes.

### 🔹 Select All Toggle

Quickly selects or deselects all available masters.

---

## Scope

* Current font
* Selected or matched masters
* All kerning pairs within selected masters

---

## Requirements

* Glyphs App 3.x
* At least two fonts open
* Source fonts must contain kerning data

---

## Usage

1. Open multiple fonts in Glyphs
2. Run the script
3. Choose copy mode:
   - Current master
   - All masters
   - Selected masters
4. (Optional) Select specific masters
5. Click Apply
6. Kerning is transferred to the current font

---

## Notes

* Matching by name requires identical master names
* Matching by ID only works for compatible fonts
* Existing kerning in target masters will be overwritten
* Ignores masters without kerning data

---

## Advanced

* Efficient dictionary-based kerning transfer
* UI dynamically adapts to number of masters
* ScrollView integration for large font families
* Lightweight and fast execution

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry