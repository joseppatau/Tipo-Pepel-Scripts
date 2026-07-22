# Fit Curves in all masters

**Real‑time curve fitting with orthogonal constraint memory for Glyphs App.**


## Description

Interactive tool to adjust off‑curve smoothness in real time, preserving orthogonal relationships across all masters.  
Unlike simple curve smoothing scripts, this tool stores the orthogonal behavior (horizontal/vertical handles) from the active master and applies proportional adjustments to the same nodes in all other masters simultaneously.

Supports **live sync** of curve tension changes, with an optional **Safe Orthogonal** mode that locks handle movement to the detected axis (X or Y) to prevent unwanted slanting.

## Author

**Josep Patau Bellart** (with AI assistance)

## License

**Apache License 2.0**

---

## Features

### Core Features

- **Real‑time curve adjustment** (no script rerun needed)
- **Orthogonal constraint memory** – detects horizontal/vertical handles and locks movement to that axis
- **Live sync across all masters** (optional, but recommended)
- **Two independent controls**:
  - **Smooth %** – absolute smoothness (0–100%)
  - **Delta %** – relative offset from Smooth % (-50 to +50)
- **Safe Orthogonal mode** (default ON) – prevents diagonal distortion of orthogonal handle pairs
- **Works on selected nodes only** – safe for partial edits
- **Non‑destructive** – original node positions are never overwritten outside the live session

### Visual Controls

| Control | Function |
|---------|----------|
| **Smooth %** slider | Absolute curve tension (0 = no change, 100 = fully smooth) |
| **Delta %** slider | Fine‑tuning offset relative to Smooth % |
| **Sync all Masters** checkbox | When ON, applies changes to every master layer of the current glyph |
| Real‑time value display | Shows current percentages next to each slider |

### Technical Core

- Orthogonal detection via geometric tolerance (`2.0` units)
- Memory‑based per‑node constraint storage (`x` for horizontal, `y` for vertical)
- Proportional handle interpolation:  
  `handle_position = owner_position + (original_offset × final_ratio)`
- Automatic owner/target identification (even with off‑curve‑first structures)
- Safe iteration using path node copies
- Works with both master layers and special layers (e.g., brace layers)

---

## Scope

- Selected off‑curve nodes in the active layer
- Current glyph (all layers when Sync is ON)
- Works with multiple paths and complex contours

---

## Requirements

- **Glyphs App 3.x**
- **macOS 10.12 or later**
- **Vanilla** (included with Glyphs)

---

## Installation

### Automatic (Recommended)

1. Download `Fit curves.py`
2. Double‑click to install or place in:
   - `~/Library/Application Support/Glyphs 3/Scripts/`
3. Restart Glyphs or refresh the Scripts menu

### Manual

1. Open Glyphs App
2. Go to **Script > Open Scripts Folder**
3. Copy `Fit curves.py` to that folder
4. Refresh Scripts menu

---

## Usage

1. Open a glyph in Edit view
2. **Select one or more off‑curve nodes** (handles)
3. Run **Fit Curves in all masters** from the Script menu
4. Adjust the **Smooth %** slider – changes appear live
5. Use **Delta %** for micro‑adjustments
6. Keep **Sync all Masters** ON to propagate changes to all masters
7. Close the window when done

> ⚠️ **Important**  
> The script only affects **selected off‑curve nodes**. If nothing is selected, nothing happens.

---

## Why This Works

Standard curve smoothing moves handles arbitrarily, often breaking orthogonal relationships (e.g., perfectly horizontal handles become slanted). This script:

1. Detects which handles are **truly horizontal** or **vertical** in the active master
2. Stores that constraint (`x` or `y`) in memory
3. Applies smoothness only **along the constrained axis** in every master
4. Leaves the perpendicular coordinate untouched

This preserves the original design intent while improving curve quality – especially useful for italic masters where orthogonal constraints are critical for clean interpolation.

---

## Notes

- Designed for **type designers working with multiple masters**
- The orthogonal memory resets when you change glyphs or selection
- Safe Orthogonal mode is **always active** (no checkbox to disable it)
- Delta % is applied multiplicatively:  
  `final_ratio = (Smooth/100) × (1 + Delta/100)`
- Works with both TrueType and PostScript outlines
- Background layers are ignored by design

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Nothing happens when moving sliders | Ensure at least one off‑curve node is selected |
| Changes apply only to the active master | Check **Sync all Masters** is ON |
| Horizontal/vertical handles move diagonally | Orthogonal memory may have failed – try reselecting the nodes |
| Glyphs becomes slow | Close the script window when not in use (live updates are frequent) |
| Memory errors after editing many glyphs | Close and reopen the script to reset internal memory |

---

## Version History

### 1.0 (Current)

- Initial release
- Orthogonal constraint memory with geometric detection
- Live dual‑slider interface (Smooth + Delta)
- Real‑time multi‑master sync
- Safe handling of off‑curve‑first node sequences

---

## Contributing

Feel free to submit issues or pull requests on GitHub. Suggestions for improvements are welcome.

---

## Support the Author

If you find this script useful, you can show your appreciation by purchasing any font at:

[https://www.myfonts.com/collections/tipo-pepel-foundry](https://www.myfonts.com/collections/tipo-pepel-foundry)

Your support helps fund continued development and maintenance of tools like this.

---

## License

Copyright 2024 Josep Patau Bellart

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.