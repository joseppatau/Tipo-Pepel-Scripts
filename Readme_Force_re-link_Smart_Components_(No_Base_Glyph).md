# Smart Component Re-linker

A Python script for Glyphs App that forcibly re-links smart components that have lost their connection to the base glyph.

## Description

This script scans through all master layers in your font and re-creates any smart components that have become disconnected from their base glyphs. This can happen when components lose their smart component values but still reference smart component glyphs.

## Features

- Detects smart components that have become unlinked
- Preserves all component attributes (position, scale, rotation)
- Only processes master layers (ignores special layers)
- Provides feedback on the number of components fixed
- Automatically redraws the current tab

## Usage

1. Open your font in Glyphs App
2. Run the script via the Script menu (Window > Plugin > Scripts)
3. The script will process all master layers and report results

## What It Does

- Identifies components that have `smartComponentValues` but are no longer properly linked
- Creates new components with the same name and transformation properties
- Removes the old "broken" components
- Maintains all positional and transformation data

## Output

The script prints a message indicating how many smart components were re-linked: