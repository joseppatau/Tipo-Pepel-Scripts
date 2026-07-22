# Import LSB/RSB from Another Font All masters

A GlyphsApp utility for import lsb/rsb from another font all masters.

## Requirements

- Glyphs App 3.x
- macOS
- Vanilla, included with current Glyphs installations

## Usage

1. Open a font in Glyphs.
2. Select the relevant glyphs, layers, nodes, or master when the tool requires a selection.
3. Run **Import LSB/RSB from Another Font All masters** from the Scripts menu.
4. Review the options and the Macro Panel output before continuing with production files.

## License

Apache 2.0

## Safety improvements

- Source and destination masters are paired explicitly instead of assuming that their internal IDs match across fonts.
- The operation stops when the two fonts have different master counts.
