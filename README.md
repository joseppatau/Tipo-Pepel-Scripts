# Type Design Scripts Suite

A curated collection of production-ready scripts for GlyphsApp, developed to streamline real-world type design workflows.

---

## Overview

This repository contains a set of tools built progressively to solve specific, recurring problems encountered during type design.
Each script is focused, practical, and tested in real production scenarios.

Rather than a theoretical toolkit, this suite reflects an evolving workflow: tools were created only when needed, resulting in a system that is efficient, coherent, and free of unnecessary features.

---

## Categories

### ✏️ Paths & Nodes

Tools for direct outline manipulation, node cleanup, alignment, and geometric corrections.

### 📐 Metrics

Spacing tools, metrics key assignment, and structural consistency helpers.

### 🔤 Kern

Kerning utilities and engines for adjusting and managing spacing relationships.

### 🧩 Components

Component-based workflows, duplication, synchronization, and structural reuse.

### 🔁 Intermediate Glyphs

Tools for interpolation, intermediate layers, and multi-master consistency.

### 🔠 Small Caps

Automation tools for generating, adjusting, and managing small caps systems.

### 👁️ Preview

Advanced visualization tools:

* Precision preview window
* Multi-master comparison
* Real-time interpolation preview

### 📏 Guides

Utilities for working with guides, alignment references, and structural helpers.

### 🎨 Creative

Experimental or stylistic tools for controlled transformations and effects.

### 🧰 Misc

General utilities and helpers that don’t fit into a specific category.

---

## Philosophy

* Built from real needs, not abstract ideas
* One tool = one clear purpose
* Optimized for speed and daily use
* Minimal UI, maximum efficiency
* Designed to integrate naturally into the Glyphs workflow

---

## Key Capabilities

* Multi-master operations across entire fonts
* Cross-font data transfer
* Smart node manipulation with typographic awareness
* Automated glyph construction (small caps, numerators, etc.)
* Advanced preview systems for validation and inspection
* Cleanup and optimization of outlines
* OpenType feature testing

---

## Requirements

* Glyphs App 3.x
* macOS
* Basic familiarity with scripting in Glyphs

---

## Installation

1. Download or clone this repository
2. Copy the scripts into your Glyphs Scripts folder
3. Restart Glyphs (or reload scripts)

---

## Usage

Scripts are organized by category for quick access.
Each tool is designed to perform a specific task with minimal setup.

Use them as needed within your workflow — there is no required order or dependency between tools.

---

## Author

Josep Patau Bellart
Graphic designer and self-taught type designer since 1996.

These scripts are the result of real needs encountered over years of practice, developed to improve efficiency, precision, and control in type design workflows.

---

## Custom Typeface Work

I am available for custom typeface design and corporate typography projects.

If you are interested in a bespoke type solution, feel free to get in touch.

---

## License

Apache2

---

## Support the Author

If you find these scripts useful, you can support my work by purchasing any font at:
https://www.myfonts.com/collections/tipo-pepel-foundry

---

## Final Note

This is not a static toolkit.
It is a living system shaped by real use.

New tools may appear only when necessary — never by default.
## Script index

The repository currently includes the following documented scripts:

### Anchors

- [PRO – Find & Fix Diacritics Alignment](Anchors/Align%20Anchor%20to%20Segment%20Center.md)
- [Build Diacritics](Anchors/Build%20diacritics.md)
- [Move Anchors to Metrics Lines](Anchors/Move%20Anchors%20to%20Metrics%20Lines.md)

### Components

- [Adjust Smart Components Values (.sc) Final](Components/Adjust%20Smart%20Components%20Values.md)
- [Decompose Components in All Masters](Components/Decompose%20Components%20in%20All%20Masters.md)
- [Decompose corner Components in All Masters](Components/Decompose%20corner%20Components%20in%20All%20Masters.md)
- [Duplicate components in all masters (improved)](Components/Duplicate_components_in_all_masters.md)
- [Enable/disable components in All Masters](Components/Enable:disable%20components%20in%20All%20Masters.md)
- [Find & Replace Corner Components (Pro)](Components/Find%20&%20Replace%20Corner%20Components.md)
- [Force re-link Smart Components (No Base Glyph)](Components/Force_re-link_Smart_Components_(No_Base_Glyph).md)
- [Make Components Smart (Glyphs 3 Safe)](Components/Make%20Components%20Smart.md)
- [Move Components in Selected Masters (Floating DEBUG)](Components/Move%20Components%20in%20Selected%20Masters.md)
- [Remove Smart Glyph Properties From All Glyphs](Components/Remove%20Smart%20Glyph%20Properties%20From%20All%20Glyphs.md)
- [Corner Tool Pro (SMART SYNC FIX)](Components/Replace%20selected%20corner%20components%20in%20all%20masters.md)
- [Selected Glyphs to components with extension](Components/Selected%20Glyphs%20to%20components%20with%20extension.md)

### Creative

- [Glyph Fill Engine](Creative/Glyph%20Fill%20Engine.md)
- [Outline Pattern Engine](Creative/Outline%20Pattern%20Engine.md)
- [Pattern Fill Engine](Creative/Pattern%20Fill%20Engine.md)
- [Random Node Movement](Creative/Random%20Node%20Movement.md)
- [Roughness Generator](Creative/Roughness%20Generator.md)
- [Shadow Engine](Creative/Shadow%20Engine.md)

### Generate Glyphs

- [Create accented alternates from selected stylistic glyphs](Generate%20Glyphs/Create%20accented%20alternates%20from%20selected%20stylistic%20glyphs.md)
- [Genera accents dels glifs seleccionats (DEBUG)](Generate%20Glyphs/Generate%20accented%20glyphs.md)

### Guides

- [🦸 Delete ALL Guides TURBO (global + glyph guides)](Guides/Delete%20all%20Guidelines%20(all%20masters)%20.md)
- [Delimite Zones](Guides/Delimit%20Zones.md)
- [Guides Manager](Guides/Guides%20Manager.md)
- [Measurement Guide Creator](Guides/Measurement%20Guide%20Creator.md)

### Intermediate Glyphs

- [Intermediate Axis Engine](Intermediate%20Glyphs/Intermediate%20Axis%20Engine.md)

### Kern

- [Clean Kerned Pairs in Tab](Kern/Clean%20Kerned%20Pairs%20in%20Tab.md)
- [Copy Kerning from Open Font](Kern/Copy%20Kerning%20from%20Open%20Font.md)
- [Delete All Kerning (Safe Universal)](Kern/Delete%20All%20Kerning.md)
- [Inspect Kern by Glyph](Kern/Inspect%20Kern%20by%20Glyph.md)
- [Kern Coach v2](Kern/Kern%20Coach%20v2.md)
- [Kern Coach v1](Kern/Kern%20Coack%20v1.md)
- [Kern Tools](Kern/Kern%20Tools.md)
- [Kerning Groups from Name](Kern/Kerning%20Groups%20from%20Name.md)
- [Kerning Master Manager](Kern/Kerning%20Master%20Manager.md)
- [Kerning Scale Tool](Kern/Kerning%20Scale%20Tool.md)
- [Positive Kerning Engine](Kern/Positive%20Kerning%20Engine.md)

### Metrics

- [Adjust Metrics by Kerning Group (Pro Final)](Metrics/Adjust%20Metrics%20by%20Kerning%20Group.md)
- [Advanced Stem Analyzer](Metrics/Advanced%20Stem%20Analyzer.md)
- [Assign Metrics to Small Caps in all masters](Metrics/Assign%20Metrics%20to%20Small%20Caps%20in%20all%20masters.md)
- [Auto Metrics Keys (First Letter)](Metrics/Auto%20Metrics%20Keys%20(First%20Letter).md)
- [Clear Metrics Keys in selected glyphs](Metrics/Clear%20Metrics%20Keys%20in%20selected%20glyphs.md)
- [Copy Sidebearings Between Masters](Metrics/Copy%20Metrics%20Between%20Masters.md)
- [Copy Metrics to Multiple Masters](Metrics/Copy%20Metrics%20to%20Multiple%20Masters.md)
- [Import LSB/RSB from Another Font All masters](Metrics/Copy%20metrics%20from%20font%20All%20masters.md)
- [Copy metrics from font](Metrics/Copy%20metrics%20from%20font.md)
- [Group Metrics Toolkit](Metrics/Group%20Metrics%20Toolkit.md)
- [Optical Stem Analyzer](Metrics/Optical%20Stem%20Analyzer.md)
- [Scale Metrics by Percent](Metrics/Scale%20metrics%20by%20percent.md)
- [Scale metrics to selected glyphs](Metrics/Scale%20metrics%20to%20selected%20glyphs.md)

### Misc

- [Copy Color to Composite Glyphs](Misc/Copy%20Color%20to%20Composite%20Glyphs.md)
- [Macro Panel](Misc/Macro%20Panel%20Glyphs%20OK.md)
- [Mark as Revised!](Misc/Mark%20as%20Revised!.md)
- [Marks by Master](Misc/Marks%20by%20Master.md)
- [UUID Glyph Debugger](Misc/UUID%20Glyph%20Debugger.md)

### Names

- [Copy instance name to Style Linking and append Italic](Names/Copy%20instance%20name%20to%20Style%20Linking%20and%20append%20Italic.md)

### Paths & Nodes

- [Alignment PRO FIXED (Italic X)](Paths%20&%20Nodes/Align/Alignment_PRO.md)
- [Center Shapes in Width](Paths%20&%20Nodes/Align/Center%20Shapes%20in%20Width.md)
- [Multi-Master Node Align](Paths%20&%20Nodes/Align/Multi-Master%20Node%20Align.md)
- [Vertical Line Align Tool](Paths%20&%20Nodes/Align/Vertical%20Line%20Align%20Tool.md)
- [Open Corners in All Masters (Custom Length)](Paths%20&%20Nodes/Corners/Open%20Corners%20in%20All%20Masters.md)
- [Find nodes at Y](Paths%20&%20Nodes/Find/Find%20nodes%20at%20Y.md)
- [Prepolator Toolkit](Paths%20&%20Nodes/Interpolate/Prepolator%20Toolkit.md)
- [Smart Interpolation Engine](Paths%20&%20Nodes/Interpolate/Smart%20Interpolation%20Engine.md)
- [Move Noder Engine](Paths%20&%20Nodes/Move/Move%20Noder%20Engine.md)
- [Move Nodes & components (All Masters)](Paths%20&%20Nodes/Move/Move%20Nodes%20&%20components%20(All%20Masters).md)
- [Move elements in masters](Paths%20&%20Nodes/Move/Move%20elements%20in%20masters.md)
- [Proportion Space & Tension (Angle Preservation)](Paths%20&%20Nodes/Move/Proportion%20Space%20&%20Tension.md)
- [Add Handles to SELECTED SEGMENT (DEBUG)](Paths%20&%20Nodes/Paths%20&%20Nodes/Add%20Handles%20to%20segment%20in%20all%20masters.md)
- [Backup Paths to Background](Paths%20&%20Nodes/Paths%20&%20Nodes/Backup%20Paths%20to%20Background.md)
- [Character Tuner](Paths%20&%20Nodes/Paths%20&%20Nodes/Character%20Tuner.md)
- [Fit Curve & Ductus PRO (Slope Lock + Green Harmony G2)](Paths%20&%20Nodes/Paths%20&%20Nodes/Curves+ductus%20G2%20OK%20Guardar.md)
- [Fit Curve & Ductus PRO (DEBUG STABLE UI)](Paths%20&%20Nodes/Paths%20&%20Nodes/Curves+ductus.md)
- [Duplicate Selected Paths to Masters](Paths%20&%20Nodes/Paths%20&%20Nodes/Duplicate%20Paths%20to%20Masters.md)
- [Enter to All Masters](Paths%20&%20Nodes/Paths%20&%20Nodes/Enter%20to%20All%20Masters.md)
- [Fit Curves in all masters](Paths%20&%20Nodes/Paths%20&%20Nodes/Fit%20Curves%20in%20all%20masters.md)
- [green armony all masters](Paths%20&%20Nodes/Paths%20&%20Nodes/Green%20armony%20all%20masters.md)
- [Multi-Master Fit Curve & Ductus PRO](Paths%20&%20Nodes/Paths%20&%20Nodes/Multi-Master%20Preview%20&%20Fit%20Curve%20PRO.md)
- [Node Cleanup Tool](Paths%20&%20Nodes/Paths%20&%20Nodes/Node%20Cleanup%20Tool.md)
- [Opposite Node Mover Dual 8-Way + Stable Tension](Paths%20&%20Nodes/Paths%20&%20Nodes/Opposite%20Node%20Mover.md)
- [Reset Handles Tool - ( 1 & 2 keys)](Paths%20&%20Nodes/Paths%20&%20Nodes/Reset%20Handles%20Tool%20-%20(%201%20&%202%20keys).md)
- [Segment Angle Tool](Paths%20&%20Nodes/Paths%20&%20Nodes/Segment%20Angle%20Tool.md)
- [Sync Paths with Background](Paths%20&%20Nodes/Paths%20&%20Nodes/Sync%20Paths%20with%20Background.md)
- [Delete Glyph Content (Smart)](Paths%20&%20Nodes/Remove/Delete%20Glyph%20Content.md)
- [Delete Nodes (All Masters)](Paths%20&%20Nodes/Remove/Delete%20Nodes%20(All%20Masters).md)
- [Remove Handles (Selected Nodes)](Paths%20&%20Nodes/Remove/Remove%20Handles%20(Selected%20Nodes).md)
- [Remove Nodes by ProxiApache2y (Floating)](Paths%20&%20Nodes/Remove/Remove%20Nodes%20by%20Proximity.md)
- [Remove Overlap Paths All masters](Paths%20&%20Nodes/Remove/Remove%20Overlap%20Paths%20All%20masters.md)
- [Remove Overlapping Nodes](Paths%20&%20Nodes/Remove/Remove%20Overlapping%20Nodes%20(All%20Masters).md)
- [Cross-Font Outline Replace](Paths%20&%20Nodes/Replace/Cross-Font%20Outline%20Replace.md)
- [MasterSync Glyphs](Paths%20&%20Nodes/Replace/MasterSync%20Glyphs.md)
- [Replace Outlines From Master (with Corners)](Paths%20&%20Nodes/Replace/Replace%20Outlines%20From%20Master.md)
- [Stem Width/Height by Side](Paths%20&%20Nodes/Transform/Change%20Stem%20Width:Height%20by%20Side.md)
- [Transform (All Masters) - TURBO](Paths%20&%20Nodes/Transform/Transform%20(All%20Masters).md)
- [Transform Selection (All Masters)](Paths%20&%20Nodes/Transform/Transform%20Selection%20(All%20Masters).md)
- [Transform Selection (All Masters)](Paths%20&%20Nodes/Transform/Transform%20Selection%20by%20side.md)
- [Copy Selected Glyphs to Other Masters](Paths%20&%20Nodes/duplicate/Copy%20Selected%20Glyphs%20to%20Other%20Masters.md)

### Plugins

- [Background Magnetic Handles](Plugins/BackgroundMagneticHandles.md)

### Preview

- [Arab text preview](Preview/Arab%20text%20preview.md)
- [Component Usage Preview PRO (Anchors FIXED + Generate)](Preview/Diacritics%20Preview.md)
- [Glyph Preview Engine](Preview/Glyph%20Preview%20Engine.md)
- [Glyph Preview Window PRO v3](Preview/Glyph%20Preview%20Window.md)
- [Live Glyph Preview Engine](Preview/Live%20Glyph%20Preview%20Engine.md)
- [Multi-Master Preview PRO (Full & ⌘ Drag)](Preview/Multi-Master%20Preview.md)
- [OpenType Feature Toggle](Preview/OpenType%20Feature%20Toggle.md)
- [Preview Glyph in all masters](Preview/Preview%20Glyph%20in%20all%20masters.md)
- [Text Viewer Pro](Preview/Text%20Preview.md)

### QA Tools

- [Fix OpenType Required Export Metadata](QA%20Tools/Fix%20OpenType%20Required%20Export%20Metadata.md)

### Small Caps

- [Assign Metrics Keys to Small Caps](Small%20Caps/Assign%20Metrics%20Keys%20to%20Small%20Caps.md)
- [Create Small Caps & Numerals Smart Components](Small%20Caps/Create%20Small%20Caps%20&%20Numerals%20Smart%20Components%20.md)
- [# -*- coding: utf-8 -*-](Small%20Caps/Small%20Caps%20Tools%20Suite.md)

### diacritics

- [Change Diacritics Components](diacritics/Change%20Diacritics%20Components.md)
- [Find diacritics with disabled auto alignment (fixed)](diacritics/Find%20diacritics%20with%20disabled%20auto%20alignment.md)
- [List all diacritics (all masters)](diacritics/List%20all%20diacritics%20(all%20masters).md)
