## Adjust Smart Components Values (.sc)

**Description**  
Tool for adjusting smart component axis values across selected glyphs in the current master.

Provides a simple UI to input numeric values for each smart axis and applies them consistently to all selected layers.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Detects smart component axes in selected glyphs
* Editable UI for setting axis values
* Batch update of smart component values
* Works across multiple selected glyphs
* Safe handling of missing or incompatible components

---

## Core

* Smart component axis detection (`smartComponentAxes`)
* Value mapping via axis IDs
* Layer-specific application (current master)
* Vanilla-based dynamic UI

---

## Scope

* Selected glyphs only
* Active master layer

---

## Requirements

* Glyphs App 3.x
* Open font with smart components

---

## Usage

1. Select one or more glyphs containing smart components  
2. Run the script  
3. Enter desired values for each axis  
4. Click **Apply**  

---

## Output

* Updated smart component values in selected glyph layers
* No structural changes to glyphs or components
* Non-destructive workflow

---

## Notes

* Only affects components with smart axes  
* Values are applied per master (not globally)  
* Missing or invalid inputs default to `0`  
* Useful for synchronizing `.sc` glyph variations  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry