# Alignment for Glyphs App

**Advanced alignment tool for Glyphs App with italic-aware projection method.**


## Description

Advanced alignment tool for Glyphs using an italic-aware projection method.  
Instead of relying on unreliable bounding boxes, it computes alignment using real node geometry, ensuring visually correct results in both roman and italic masters.

Supports multiple alignment modes including global alignment, true width centering, and individual element centering.

## Author

**Josep Patau Bellart** (with AI assistance)

## License

**Apache License 2.0**

---

## Features

### Core Features

- **True alignment in italic masters** (no bounding box errors)
- **Geometric projection** (italic-aware)
- **Intersection-based center calculation**
- **Multi-sampling across multiple Y positions**
- **Intelligent fallback** when intersections fail
- **Automatically keeps the largest element fixed**
- **Moves the smaller component** (e.g., crossbar)
- **Current master or all masters** support
- **Non-destructive** (background is restored after execution)

### Core Alignment

- Up
- Center Y
- Down
- Left
- Center X
- Right

### True Width Mode

Centers the glyph based on the **actual drawn width**, not bounding boxes:

- Detects overflow outside glyph width
- Uses projected coordinates for accuracy in italic
- Assigns LSB and RSB directly
- Matches professional spacing workflow

### Technical Core

- Temporary decomposition using background layer (safe context)
- Component → multi-path mapping
- Segment intersection with horizontal scanlines
- Multi-sample averaging for stability
- Global fallback projection when no intersections are found
- De-italicized coordinate system: `x' = x - y * tan(angle)`

---

## Scope

- Components in selected glyph(s)
- Current master or all masters
- Automatically detects:
  - Reference shape (largest)
  - Target shape (smaller)

---

## Requirements

- **Glyphs App 3.x**
- **Glyphs with components**
- **At least two components**
- **macOS 10.12 or later**

---

## Installation

### Automatic (Recommended)

1. Download `AlignmentPRO.py`
2. Double-click to install or place in:
   - `~/Library/Application Support/Glyphs 3/Scripts/`
3. Restart Glyphs or refresh Scripts menu

### Manual

1. Open Glyphs App
2. Go to **Script > Open Scripts Folder**
3. Copy `AlignmentPRO.py` to the folder
4. Refresh Scripts menu

---

## Usage

1. Select glyph(s)
2. Ensure components are present (e.g., base + accent/bar)
3. Choose alignment direction (**Center X** recommended)
4. Choose scope:
   - Current master
   - All masters
5. Run the script

---

## Why This Works

Instead of aligning bounding boxes, the script:

1. Projects outlines according to italic angle
2. Samples multiple horizontal slices
3. Computes real left/right extremes via intersections
4. Falls back to global projection when needed
5. Calculates a true visual center

This matches how alignment is perceived in professional type design.

---

## Notes

- Designed specifically for italic workflows
- Avoids common misalignment caused by skewed bounding boxes
- Works even when no nodes exist at the target height
- Handles complex outlines (multiple paths, serifs, etc.)
- Background layer is fully restored after execution

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Alignment not working in italic | Verify italic angle is set in master |
| Components not aligning | Ensure component glyphs exist in font |
| Wrong reference shape | Script automatically uses largest shape |
| No alignment occurs | Make sure at least two components are selected |

## Version History

### 1.0 (Current)

- Initial release
- Italic-aware projection method
- True width centering
- Multi-master support
- Component-based alignment

## Contributing

Feel free to submit issues or pull requests on GitHub. Suggestions for improvements are welcome.

## Support the Author

If you find this script useful, you can show your appreciation by purchasing any font at:

[https://www.myfonts.com/collections/tipo-pepel-foundry](https://www.myfonts.com/collections/tipo-pepel-foundry)

Your support helps fund continued development and maintenance of tools like this.

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