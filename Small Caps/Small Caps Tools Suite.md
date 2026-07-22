## Small Caps Tools Suite

**Description**  
Comprehensive tool suite for generating, adjusting, and managing small caps (.sc) in Glyphs App.

Includes multiple tools in a tabbed interface to automate small caps creation, smart component adjustment, metrics synchronization, and component duplication across masters.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache 2.0

---

## Features

* Generate small caps from uppercase, numerals, and symbols
* Adjustable scale and width transformation
* Support for Latin and Cyrillic glyph systems
* Smart component value adjustment via UI
* Automatic metric key assignment for `.sc` glyphs
* Disable automatic alignment while preserving component positions
* Duplicate selected components across all masters
* Multi-tab interface for organized workflows

---

## Core

* Component-based small caps generation
* Smart component axis control (`smartComponentAxes`)
* Metrics key system (`leftMetricsKey`, `rightMetricsKey`, `widthMetricsKey`)
* Unicode-aware glyph detection
* Batch processing across glyphs and masters
* Vanilla-based tabbed UI

---

## Scope

* Entire font (depending on operation)
* Selected glyphs (optional modes)
* Active master or all masters (depending on tool)

---

## Requirements

* Glyphs App 3.x
* Open font with uppercase glyph set
* Smart components (for adjustment features)

---

## Usage

Run the script to open the **Small Caps Tools Suite** panel.

### Tabs overview:

**1. SC Generator**
* Generate `.sc` glyphs from uppercase
* Control scale (%) and width adjustment
* Apply to all mappings or selected glyphs only

**2. Adjust SC**
* Set values for smart component axes
* Apply to selected glyphs in active master

**3. Metrics to SC**
* Assign metric keys based on base glyphs
* Disable auto-alignment while preserving positions
* Update metrics automatically

**4. Duplicate Components**
* Copy selected components to all masters
* Preserves transforms and smart behavior

---

## Output

* Generated `.sc` glyphs with components
* Updated smart component values
* Synchronized metrics across small caps
* Duplicated components across masters
* Console feedback and summary messages

---

## Notes

* `.sc` glyphs are generated using components (non-destructive)  
* Width and scale adjustments are applied via component transforms  
* Metrics assignment assumes consistent base glyph naming  
* Cyrillic support is enabled if detected in the font  
* Some operations affect the entire font — use version control  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry