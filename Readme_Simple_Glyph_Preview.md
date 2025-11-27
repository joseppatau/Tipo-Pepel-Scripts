# Simple Glyph Preview for GlyphsApp

### A lightweight and extensible glyph preview panel for GlyphsApp scripts.

This script provides a clean and efficient way to preview any glyph
inside GlyphsApp using **custom drawing**, **master switching**, and
**scaling based on font metrics**.\
It is designed to be used **stand-alone**, or as a **drop-in preview
engine** for more advanced tools.

------------------------------------------------------------------------

##  Features

### ✔ Live glyph preview

-   Type any character to preview it immediately\
-   Automatically resolves glyph name or Unicode

### ✔ Master selection

-   Preview any master of the current font\
-   Automatically finds the correct corresponding layer

### ✔ Accurate font metrics rendering

Draws: - Ascender\
- Descender\
- x-Height\
- Cap height\
- Baseline

### ✔ Automatic scaling and centering

-   Computes scale based on ascender/descender\
-   Centers glyph horizontally\
-   Computes baseline position dynamically

### ✔ Robust path rendering

Falls back to: - `layer.bezierPath` (native Glyphs method)\
- Manual NSBezierPath reconstruction when necessary

### ✔ Safe to run multiple times

Prevents this common PyObjC error:

    objc.error: SimpleGlyphPreviewView is overriding existing Objective-C class

### ✔ Modular and reusable

Useful as a preview engine for: - stroke contrast visualizers\
- interpolation previews\
- metrics debugging tools\
- outline analysis\
- filter previews\
- autotrace evaluation\
- master comparison utilities

------------------------------------------------------------------------

## File Structure

-   **SimpleGlyphPreviewView** --- drawing, metrics, scaling, path
    building\
-   **NSViewWrapper** --- embeds NSView into Vanilla\
-   **SimpleGlyphPreviewPanel** --- user interface

------------------------------------------------------------------------

## How to Use

1.  Open GlyphsApp\
2.  Open the Macro Panel\
3.  Paste the script\
4.  Run it\
5.  A preview window appears

------------------------------------------------------------------------

## Extending the Script

Possible enhancements: - Draw nodes\
- Draw handles\
- Add zoom and pan\
- Multi-glyph preview\
- Drag & drop glyphs\
- Make it a Glyphs Plugin

------------------------------------------------------------------------

## License

MIT License.

------------------------------------------------------------------------

## Credits

Original concept/UI: **Josep Patau Bellart**\
Refactor & optimization with AI assistance.
If you find this script useful, you can show your appreciation by purchasing 
a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry

