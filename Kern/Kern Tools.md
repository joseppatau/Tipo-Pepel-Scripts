## Kern Tools

**Description**  
Comprehensive kerning toolkit for Glyphs App featuring a multi-tab interface with advanced tools for generating, analyzing, cleaning, and managing kerning pairs.

Designed as an all-in-one environment for professional kerning workflows.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
MIT

---

## Features

* Multi-tab interface for kerning workflows
* Pair generation with customizable glyph sets
* Built-in test word collections (Ken Lunde, Briem, etc.)
* List and inspect kerning pairs
* Collision detection (visual QA)
* Convert kerning to small caps
* Kerning sanitizer and cleanup tools
* Clear & restore kerning data
* Scale kerning values by percentage
* Support for Latin and Cyrillic scripts
* Optional kerning group handling

---

## Core

* Kerning pair generation engine
* Unicode-aware glyph classification (Latin / Cyrillic / symbols)
* Kerning group detection and management
* Batch processing across font data
* Vanilla-based tabbed UI system

---

## Scope

* Entire font kerning data
* Active master (depending on tool)
* Selected glyphs (in some operations)

---

## Requirements

* Glyphs App 3.x
* Open font with kerning data

---

## Usage

1. Run the script to open the **Kern Tools panel**
2. Navigate through tabs depending on the task:

   * **Pairs Generator** → create kerning test strings  
   * **List Pairs / All Pairs** → inspect kerning  
   * **Find Collisions** → detect spacing issues  
   * **Kern to SC** → transfer kerning to small caps  
   * **Sanitizer** → clean kerning inconsistencies  
   * **Clear & Restore** → backup/reset kerning  
   * **Scale %** → adjust kerning globally  

3. Apply operations as needed

---

## Output

* Kerning strings for testing
* Modified kerning values
* Cleaned or reorganized kerning data
* Visual QA support for spacing

---

## Notes

* Some operations affect the entire font — use with care  
* Kerning groups can significantly alter results  
* Supports both Latin and Cyrillic glyph systems  
* Designed for production-level kerning workflows  
* Best used with a backup or version control  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry