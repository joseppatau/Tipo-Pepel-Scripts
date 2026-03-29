## Convert Smart to Dumb Component

**Description**  
Utility script that converts smart components into regular (dumb) components by replacing them with static outlines via a temporary glyph.

This allows freezing smart component instances for safer editing, export, or compatibility workflows.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Converts smart components into static components
* Preserves position and scale of original components
* Automatically creates temporary glyphs for conversion
* Works on all selected glyph layers
* Non-destructive to original smart component glyphs

---

## Core

* Detection of smart components via `smartComponentAxes`
* Temporary glyph generation
* Shape duplication from source master
* Component replacement workflow

---

## Scope

* Selected glyph layers only
* Active master

---

## Requirements

* Glyphs App 3.x
* Open font with smart components

---

## Usage

1. Select one or more glyphs containing smart components  
2. Run the script  
3. Smart components will be replaced with static components  

---

## Output

* Smart components replaced by regular components
* Temporary glyphs (`_temp_*`) created in the font
* Original smart glyphs remain unchanged

---

## Notes

* Temporary glyphs are created per component base name  
* Resulting components are no longer parametric  
* Useful before export or when avoiding smart component dependencies  
* You may want to clean up `_temp_*` glyphs after use  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry