## DeliApache2 Zones

**Description**
Interactive tool to create, visualize, and manage horizontal zones in glyphs, with live drawing overlays and node-edge highlighting for precise vertical control.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Create editable horizontal zones (Y min / Y max)
* Live visual overlay in the Glyphs editor
* Highlight nodes located on zone edges
* Auto-create diacritics zone based on glyph bounds
* Generate zones from selection
* Adjustable node highlight size
* Show/hide zones individually
* Save and load zones as JSON

---

## Core

* Dynamic NSPanel UI with table editing
* Custom drawing callbacks (background + foreground)
* Zone data model with color and visibility
* Selection-based geometry analysis
* Component and node bounds calculation

---

## Scope

* Current editing view (live overlay)
* All glyphs (zone system is global per session)
* Nodes, paths, and components (for zone creation)

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Run the script
2. Use **Add new zone** or **Acote from selection**
3. Adjust values directly in the table
4. Toggle visibility or edit colors
5. (Optional) Highlight nodes on zone edges
6. Save/load zones if needed

---

## Notes

* Zones are visual guides (non-destructive)
* Automatically creates a *Diacritics* zone if `circumflexcomb` is found
* Uses dynamic class creation to avoid conflicts on re-run
* Includes safe callback handling on window close

---

## Advanced

* Background drawing renders zone bands across the canvas
* Foreground drawing highlights nodes aligned with zone edges
* Supports tolerance-based edge detection
* Fully editable table with live updates

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
