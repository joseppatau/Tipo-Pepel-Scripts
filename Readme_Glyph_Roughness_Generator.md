# Glyph Roughness Generator

A script and UI panel for **Glyphs App** that adds equidistant nodes,
applies roughness effects, and removes Bézier handles to create
hand-crafted or distressed shapes from existing glyph outlines.

Designed by **Josep Patau Bellart**, programmed with AI tools.

------------------------------------------------------------------------

##  Features

-   Add **equidistant nodes** to both straight and curved segments\
-   Apply **roughness / jitter** (regular or random mode)\
-   Flatten curves by **removing all Bézier handles**\
-   Live visual **preview** of the effect\
-   Apply modifications to:
    -   the **previewed glyph**
    -   **selected glyphs**
    -   the **entire font**
-   Fully supports Glyphs **masters** and metrics

------------------------------------------------------------------------

##  Requirements

-   **Glyphs App** (with Python + Vanilla UI support)
-   Built‑in Glyphs modules:
    -   `GlyphsApp`
    -   `vanilla`
    -   `AppKit`
    -   `Foundation`
    -   `objc`

------------------------------------------------------------------------

##  Installation

1.  Download the script file:\
    **`Glyph Roughness Generator.py`**

2.  Place it in your Glyphs scripts folder:

        ~/Library/Application Support/Glyphs/Scripts/

3.  In Glyphs, run:\
    **Scripts → Reload Scripts**

4.  The script will now appear in the Scripts menu.\
    Launch it to open the **Glyph Roughness Generator panel**.

------------------------------------------------------------------------

##  How It Works

### 1. **Equidistant Node Generation**

The script analyzes each path and segment:

-   Straight segments are measured using Euclidean distance.\
-   Bézier curves are approximated by sampling intermediate points to
    estimate their length.

According to the chosen spacing, the script inserts new nodes at equal
intervals, ensuring **consistent geometric distribution** across the
outline.

------------------------------------------------------------------------

### 2. **Applying Roughness**

Each on-curve node is displaced along a direction **perpendicular** to
the segment it belongs to.

Two roughness modes are available:

#### **Regular Mode**

-   Roughness alternates between positive and negative offsets
-   Produces a rhythmic "zig‑zag" or chiseled texture

#### **Random Mode**

-   Each node receives a random offset within the set roughness range\
-   Creates a more organic, hand-drawn aesthetic

------------------------------------------------------------------------

### 3. **Handle Removal**

After modifying the outline, all off-curve points (Bézier handles) are
removed.\
All segments are converted to **straight lines**, giving the final shape
a raw, faceted texture.

------------------------------------------------------------------------

### 4. **Preview System**

The script includes a fully custom **NSView preview renderer**:

-   Draws glyph outlines using master metrics\
-   Displays baseline, ascender, cap height, x‑height\
-   Centers and scales previewed glyphs\
-   Renders the processed temporary layer for immediate visual feedback

------------------------------------------------------------------------

##  UI Overview

-   **Character**: glyph to preview\
-   **Master**: select master for calculations\
-   **Spacing**: distance between inserted nodes\
-   **Roughness**: displacement intensity\
-   **Mode**: Regular / Random\
-   **Preview**: generate a temporary modified layer\
-   **Apply**: commit changes to glyphs

------------------------------------------------------------------------

##  License

This project is distributed under the **MIT License**.

------------------------------------------------------------------------

## Support the Author

If this tool improves your workflow, consider supporting the designer:

**https://www.myfonts.com/collections/tipo-pepel-foundry**
