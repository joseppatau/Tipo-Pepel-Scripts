# Create Shadows Script for Glyphs App

Create Shadows is a Glyphs App script that generates shadow-like shapes for selected glyphs by offsetting their paths in X and Y directions and performing boolean subtraction to create clean shadow contours.

## Overview

This script provides a floating control panel for type designers working in Glyphs App. It automates the creation of shadows or extruded effects by translating glyph outlines and subtracting the original shapes, leaving only the shadow region visible.

## Features

- Floating UI panel with ΔX (horizontal) and ΔY (vertical) offset controls
- Applies shadows to all currently selected glyphs simultaneously
- Uses Glyphs' native boolean operations for clean path results
- Preserves undo functionality for each glyph modification

## Installation

1. Copy the entire script into a new file named `CreateShadows.py`
2. Place the file in your Glyphs scripts folder: `~/Library/Application Support/Glyphs 3/Scripts/`
3. Restart Glyphs App or use Scripts → Reload Scripts
4. Access via Scripts menu → Create Shadows

## Usage

1. Open your Glyphs font file
2. Select one or more glyphs in the font view
3. Run the script (Scripts → Create Shadows)
4. In the floating "Shadow" window:
   - Set ΔX (e.g., `40` for right shadow)
   - Set ΔY (e.g., `-40` for downward shadow)
   - Click **Apply to selection**

The script will modify selected glyphs immediately. Use Cmd+Z to undo if needed.

## How It Works

-   Clears non-master layers, focuses on current master

-   Decomposes components and removes overlaps

-   Backs up original shapes to background layer

-   Offsets foreground layer by ΔX, ΔY values

-   Subtracts original shapes from offset layer (boolean op)

-   Cleans up paths and removes overlaps


## Requirements

- Glyphs App 3.x with Python scripting enabled
- Vanilla library (included with Glyphs)
- PyObjC (standard in Glyphs Python environment)

## Author

Designed by **Josep Patau Bellart**, programmed with AI tools

**Support the author:** Purchase a font from [Tipo Pepel Foundry](https://www.myfonts.com/collections/tipo-pepel-foundry)

## License

MIT License







