# Guides Manager

**A comprehensive guide management tool for Glyphs App that creates, transfers, and manages guides across glyphs and components.**

**Author:** Josep Patau Bellart (with AI assistance)  
**License:** Apache 2.0

---

## Description

Guides Manager is a powerful tool for Glyphs App that streamlines the creation and management of guides in your font projects. It allows you to create guides from selected nodes, clear guides, transfer guides between glyphs, and intelligently propagate guides from base glyphs to all glyphs that contain them as components (e.g., transferring guides from "d" to "dcaron", "dcroat", etc.). The script handles both local and global guides, supports multiple masters, and preserves your preferences across sessions.

---

## Features

### Core Features
- **Create guides from selection** — Generate guides from two selected nodes or points
- **Clear guides** — Remove local or global guides from selected glyphs or masters
- **Transfer guides between glyphs** — Copy guides from source to target glyphs
- **Smart component propagation** — Automatically transfer guides from a base glyph to all glyphs that contain it as a component
- **Dual transfer modes** — Choose between automatic detection or manual glyph selection
- **Support for all masters** — Apply operations across all masters or current master only
- **Global vs local guides** — Choose between master-level or layer-level guides
- **Preference persistence** — Remembers your settings across sessions

### Advanced Features
- **Automatic duplicate prevention** — Skips guides that already exist at the same position
- **Transform handling** — Applies component transformations (position and angle) when transferring to components
- **Undo grouping** — Groups operations by glyph for easy undo
- **Cross-version compatibility** — Works with Glyphs 3.x and handles version differences gracefully

---

## Interface

| Control | Description |
|---------|-------------|
| **Create Guide from Selection** | Creates a guide from two selected nodes. Angle and position are determined by the node positions |
| **Clear Guides** | Removes all guides from the target layers |
| **All Masters** | When enabled, applies operations to all masters in the font |
| **Make Global Guides** | When enabled, creates/transfers guides at master level instead of layer level |
| **Transfer (glyph name)** | Transfers guides from the source to a specific target glyph |
| **To glyphs that contain this glyph as component** | Automatically finds and transfers guides to all glyphs that use the current glyph as a component |
| **To selected glyphs (as components)** | Transfers guides to manually selected glyphs |
| **Transfer guides to components** | Executes the component guide transfer operation |

---

## Usage

### Creating Guides
1. Select two nodes or points in your glyph
2. Choose target mode (All Masters or current only)
3. Select guide type (Local or Global)
4. Click **Create Guide from Selection**

### Clearing Guides
1. Select glyph(s) or masters to clear
2. Choose target mode and guide type
3. Click **Clear Guides**

### Transferring Guides Between Glyphs
1. Select source glyph(s) in Font View
2. Enter the target glyph name in the text field
3. Choose target mode and guide type
4. Click **Transfer**

### Propagating Guides to Components (Recommended)
1. Open the base glyph that contains your guides (e.g., "d")
2. Ensure the base glyph has the guides you want to propagate
3. Select **To glyphs that contain this glyph as component**
4. Click **Transfer guides to components**
5. The script will automatically:
   - Find all glyphs that use the base glyph as a component (e.g., "dcaron", "dcroat", etc.)
   - Apply the component transformations to each guide
   - Add the transformed guides to each target glyph

### Manual Component Transfer
1. Select the target glyphs in Font View
2. Open the source glyph (the one with guides)
3. Select **To selected glyphs (as components)**
4. Click **Transfer guides to components**

---

## Workflow Examples

### Example 1: Propagating guides from base glyph to accented glyphs
1. Design guides for your base letter "a"
2. Open the "a" glyph
3. Click **Transfer guides to components**
4. All accented glyphs ("aacute", "agrave", "adieresis", etc.) automatically receive the guides

### Example 2: Creating guides across multiple masters
1. Enable **All Masters**
2. Create guides in one master
3. The same guides are automatically added to all masters

### Example 3: Using global guides
1. Enable **Make Global Guides**
2. Create or transfer guides
3. Guides appear in all layers of that master

---

## Requirements

- **Glyphs App 3.x** (tested with Glyphs 3)
- **macOS** (10.12 or later)
- **Open font** with at least one glyph

---

## Installation

1. Download `Guides Manager.py`
2. Place it in your Glyphs scripts folder:
   - `~/Library/Application Support/Glyphs 3/Scripts/`
3. Restart Glyphs or refresh the Scripts menu
4. Access from **Scripts > Guides Manager**

Alternatively, you can run the script directly from the Macro Panel.

---

## Notes

- **Duplicate prevention:** The script automatically skips guides that already exist at the same Y position
- **Undo support:** Each operation is grouped by glyph, allowing you to undo entire operations
- **Measurement guides:** When possible, the script sets guides as measurement guides (depends on Glyphs version)
- **Transform handling:** Component transformations (position, rotation, scale) are correctly applied to guides
- **Performance:** Works efficiently even with large font files and multiple glyphs

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No guides appear | Ensure **Measurement Guide** is checked (if using older Glyphs version) |
| Components not found | Make sure you're using the correct mode (automatic vs manual) |
| Guides not transforming correctly | Check that components have valid transform matrices |
| Script doesn't run | Verify Glyphs version 3.x and script location |

---

## Technical Details

### Guide Types
- **Local guides** — Stored per layer (accessible only in that specific glyph/master combination)
- **Global guides** — Stored per master (appear in all glyphs of that master)

### Transform Matrix
The script uses 6-value transform matrices:
- `[a, b, c, d, tx, ty]` where:
  - `a, d` = scale
  - `b, c` = rotation/skew
  - `tx, ty` = translation

### Component Detection
The script detects components through:
- `layer.components` (Glyphs 3)
- `layer.shapes` (fallback for older versions)
- Component name comparison

---

## Version History

### 1.0 (Current)
- Initial release
- Guide creation from selection
- Guide clearing
- Guide transfer between glyphs
- Automatic component detection and propagation
- Dual transfer modes (automatic and manual)
- Support for all masters
- Global/local guide options
- Undo grouping

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
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.