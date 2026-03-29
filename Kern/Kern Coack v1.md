## Kern Coach v1

**Description**
Automatically applies negative kerning to reduce excessive spacing between glyph pairs using geometric distance analysis, enabling consistent and controlled spacing correction across the font.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Overview

Positive Kerning Engine is an advanced kerning workflow system focused on **automatic spacing correction**.
It identifies glyph pairs that are too far apart and applies **negative kerning adjustments** to achieve visually balanced spacing.

Unlike traditional kerning methods based on sidebearings, this system uses **real outline geometry** to determine optimal distances.

---

## How It Works

### 1. Geometry-Based Distance Analysis

The engine calculates the real distance between glyph outlines by:

* Decomposing shapes for accuracy
* Measuring segment-to-segment distances
* Using bounding-box filtering for performance

This produces a precise **minimum distance value** between glyphs.

---

### 2. Spacing Evaluation

Each pair is evaluated to determine if spacing is excessive:

* If spacing is within acceptable range → no change
* If spacing is too large → kerning is applied
* If spacing is already tight → skipped

---

### 3. Automatic Kerning (Negative)

When adjustment is needed:

* Negative kerning is applied
* Values are calculated based on geometric distance
* Over-tightening is avoided

This ensures consistent spacing without manual trial-and-error.

---

### 4. Pair Generation System

Pairs are generated dynamically using:

* Base glyph(s)
* Category filters:

  * Latin Upper / Lower
  * Numbers
  * Punctuation
  * Symbols
  * Cyrillic
  * Custom glyph sets

The system:

* Filters out glyph variations (`.sc`, `.ss01`, etc.)
* Supports small caps
* Generates left, right, or both pair directions

---

### 5. Kerning Group Awareness

The engine integrates fully with kerning groups:

* Detects group membership
* Supports “@ boss” mode (group leaders only)
* Avoids redundant pairs covered by group kerning
* Handles group hierarchies and variants

---

### 6. Exclusion System

Custom exclusions can be defined:

* Specific glyphs
* Entire kerning groups
* Group prefixes and variations

Exclusions are applied depending on pair position.

---

### 7. Tab-Based Workflow

All operations are visualized in Glyphs tabs:

* Automatic tab generation per glyph/category
* Multi-column layout for readability
* Context strings (prefix/suffix) applied dynamically
* Optional OpenType feature activation

---

### 8. Context-Aware Rendering

Pairs are displayed with adaptive context:

* Uppercase / lowercase aware
* Custom prefix and suffix patterns
* Improved visual evaluation

---

## Tools

### 🔹 Pair Generator

Creates structured kerning test tabs based on selected glyphs and categories.
Supports filtering, exclusions, and group-aware generation.

---

### 🔹 Distance & Margin Analyzer

Displays real spacing values between glyph pairs using geometric calculations.
Shows both margin and current kerning.

---

### 🔹 Kerning Apply (Auto Tightening)

Applies negative kerning to reduce excessive spacing between glyph pairs.
Only modifies pairs that exceed the desired spacing threshold.

---

### 🔹 Group Filter (@ Boss Mode)

LiApache2s processing to group leaders only.
Reduces redundancy and improves workflow clarity.

---

### 🔹 Exclusion Manager

Defines glyphs or groups to ignore during pair generation.
Supports JSON import/export.

---

### 🔹 Kerning Cleaner

Removes kerning pairs from the current tab:

* Preserves protected pairs (`#...#`)
* Supports full cleanup rules

---

### 🔹 Group Inspector

Displays all members of a kerning group in a new tab.
Useful for auditing group structures.

---

### 🔹 Tab Navigation & Management

* Navigate between generated tabs
* Close all tabs
* Apply OpenType features

---

## Options

### Pair Generation

* Base glyph(s)
* Category selection
* Left / Right / Both positions
* Hide existing kerning pairs
* Show only group leaders (@ boss)

---

### Context

* Prefix / suffix strings
* Case-aware adaptation
* Custom test strings

---

### Filtering

* Excluded glyphs (left/right)
* Excluded groups

---

### Kerning Control

* Automatic negative kerning
* Geometry-based spacing evaluation
* Group-aware application

---

### Import / Export

* Save/load exclusion groups (JSON)
* Import kerning pairs

---

## Advanced Features

* Segment-level geometry engine
* Bounding-box optimization
* Multi-column tab layout system
* Variation filtering
* Group caching for performance
* Debug system with multiple levels

---

## Summary

Positive Kerning Engine is a **geometry-driven kerning system** that automates spacing correction by:

* Detecting excessive spacing
* Applying controlled negative kerning
* Integrating with kerning groups
* Providing a structured visual workflow

It bridges the gap between **manual kerning precision** and **automated consistency**, making it suitable for complex type families.

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
