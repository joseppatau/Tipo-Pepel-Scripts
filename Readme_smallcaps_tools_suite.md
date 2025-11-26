# Overview

Smallcaps Tools Suite is a multi-tool script designed for GlyphsApp that automates the creation, adjustment, and maintenance of small caps (.sc) glyphs.
It enables fast component-based generation of small caps, smart component adjustments, metric syncing, and cross-master duplication of components.

The script supports:

- Latin alphabet  
- Digits and symbols  
- Optional Cyrillic (auto-enabled if uni0416 exists)

# Features

The suite provides four main modules, accessible via tabs in a single interface.

## 1. SC Generator

Automatically generates small caps from uppercase components.

### Capabilities

- Creates .sc glyphs if missing.
- Clears and regenerates layers using uppercase components.
- Adjustable:
  - Scale (% height)
  - Width expansion or contraction
- Works on:
  - All predefined mappings
  - Only selected glyphs
- Handles special cases (ae, oe, ß, eth, etc.).
- Optionally maps Cyrillic if available.
- Auto-renames Cyrillic .sc glyphs to proper Unicode-based names.
- Assigns:
  - category = Letter
  - subCategory = Smallcaps

## 2. Adjust SC (Smart Components)

Batch-applies Smart Component axis values to selected glyphs.

### Capabilities

- Reads all design axes defined in the font (Weight, Width, Optical Size…)
- Allows numeric assignment per axis.
- Applies values to components in the current master only.
- Affects only components with smart axes.

## 3. Metrics to SC

Assigns metric keys to all small caps and updates spacing.

### Capabilities

- Disables automatic alignment but preserves component positions.
- Assigns:
  - leftMetricsKey = BASE
  - rightMetricsKey = BASE
  - widthMetricsKey = BASE
- Updates metrics for the current master.
- Produces a summary of processed and skipped small caps.

## 4. Duplicate Components

Duplicates selected components into all masters of the current glyph.

### Capabilities

- Requires a glyph with selected components.
- Copies the selected components into every master.
- Keeps:
  - Transformations
  - Positions
  - Smart Component values
- Skips the source master to prevent duplication on the same layer.

# Internal Helper Functions

- `glyph_by_name_or_unicode(ref)` — resolves glyphs by name or Unicode.
- `disable_auto_alignment_for_layer(layer)` — keeps positions while turning off auto-alignment.
- `find_base_name_for_smallcap(sc_name)` — resolves the correct uppercase, symbol, or special mapping base.
- `update_metrics_for_current_master()` — syncs metrics on the active master.

# Requirements

- GlyphsApp 3.x
- Python modules:
  - GlyphsApp
  - vanilla
  - re

# Usage

1. Open a font in GlyphsApp.  
2. Select glyphs when required (for certain tabs).  
3. Run the script.  
4. Use any of the four tools through the tabbed interface.

# License

MIT License

# Author

Designed by **Josep Patau Bellart**  
Programmed with the assistance of AI tools  

If you find this tool useful, you can support the author by purchasing a font from the Tipo Pepel Foundry:  
https://www.myfonts.com/collections/tipo-pepel-foundry
