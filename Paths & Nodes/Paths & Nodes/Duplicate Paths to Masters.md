## Duplicate Paths to Masters

**Description**  
Utility script for duplicating paths from the current master to all other masters in selected glyphs.

Optionally replaces existing paths and copies metrics, making it ideal for synchronizing masters during early design stages or fixing inconsistencies.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Duplicate paths from source master to all other masters
* Optional replacement of existing paths
* Optional copy of metrics (LSB, RSB, width)
* Works on multiple selected glyphs
* Safe duplication using path copies
* Clear status feedback and error reporting

---

## Core

* Master-based layer detection (`associatedMasterId`)
* Path duplication via `.copy()`
* Safe path removal per layer
* Metrics transfer system
* Vanilla-based UI with options

---

## Scope

* Selected glyphs only
* All masters in the font
* Source = current master

---

## Requirements

* Glyphs App 3.x
* Font with multiple masters

---

## Usage

1. Select one or more glyphs in the Font view  
2. Run the script  
3. Choose options:
   * Replace existing paths  
   * Copy metrics  
4. Click **Duplicate Paths**

---

## Output

* Paths duplicated across all masters
* Optional metrics synchronization
* Console log with detailed feedback
* Status summary in UI

---

## Notes

* Source master is determined by current layer selection  
* Existing paths can be overwritten if enabled  
* Metrics copy ensures consistency but may override intended differences  
* Useful for initializing masters or fixing broken interpolations  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry