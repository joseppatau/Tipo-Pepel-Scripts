# MenuTitle: Kern Tools
# -*- coding: utf-8 -*-
# Description: Central panel with multiple tabs for kerning-related tools
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing a single font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# Version: 1.0
# License: MIT
__doc__="""
Central panel with multiple tabs for kerning-related tools"""

from GlyphsApp import *
from vanilla import Window, Tabs, TextBox, EditText, PopUpButton, Button, CheckBox, HorizontalLine, TextEditor, RadioGroup, List
from AppKit import NSAlert, NSInformationalAlertStyle, NSTextField, NSView, NSMakeRect, NSNormalWindowLevel, NSColor
import json, os, math, unicodedata
from vanilla.dialogs import askYesNo

# ===========================================================
# Helper function used by Clear & Restore
# ===========================================================
def nameForID(font, ID):
    try:
        if ID[0] == "@":
            return ID
        else:
            return font.glyphForId_(ID).name
    except:
        return None

# ===========================================================
# MAIN CLASS
# ===========================================================
class KernTools:
    def __init__(self):
        # Main window - INCREASED HEIGHT to fit all elements
        self.w = Window((780, 700), "Kern Tools")  # Changed from 600 to 700, width to 780
        tabNames = [
            "Pairs Generator",
            "List All Pairs", 
            "List Pairs",
            "Find Collisions",
            "Kern to SC",
            "Sanitizer",
            "Clear & Restore",
            "Scale %"
        ]
        self.w.tabs = Tabs((10, 10, -10, -10), tabNames)

        # -----------------------------------------------------------
        # 1. Pairs Generator
        self.buildPairsGeneratorTab()

        # 2. List All Pairs
        self.buildListAllPairsTab()

        # 3. List Pairs (TURBO VERSION)
        self.buildListPairsTab()

        # 4. Find Collisions (TURBO VERSION)
        self.buildFindCollisionsTab()

        # 5. Kern to SC
        self.buildKernToSCTab()

        # 6. Sanitizer
        self.buildSanitizerTab()

        # -----------------------------------------------------------
        # 7. CLEAR & RESTORE
        self.buildClearRestoreTab()

        # -----------------------------------------------------------
        # 8. SCALE %
        self.buildScaleTab()

        self.w.open()
        self.refreshAll()  # Auto-refresh on startup

    def refreshAll(self):
        """TURBO: Fast refresh of all components"""
        self.refreshList(None)
        self.refreshGroups(None)

    def getFeatureNames(self):
        """Return list of feature names in the currently open font, or a fallback."""
        font = Glyphs.font
        if not font:
            return ["No font open"]
        try:
            return [f.name for f in font.features]
        except Exception:
            return ["(no features)"]

    # ===========================================================
    # PAIRS GENERATOR TAB - CORRECTED WITH BETTER LAYOUT
    # ===========================================================
    def buildPairsGeneratorTab(self):
        tab = self.w.tabs[0]
        
        # --- Basic helpers ---
        self.SYMMETRIC_TRIOS = [
            "AWA", "AVA", "ATA", "AYA", "AUA", "AOA", "AXA",
            "WAW", "WOW", "WSW",
            "TAT", "TOT", "TMT", 
            "YAY", "YOY", 
            "UAU", 
            "SYS",
            "OTO", "OVO", "OWO", "OMO", "OXO", "OAO",
            "MVM", "MWM", "MOM", "MUM", "MYM", "MTM",
            "XOX",
            "VAV", "VOV", "VSV",
            "ovo", "owo", "oyo", "oxo",
            "yoy", "vov", "wow", "xox"
        ]

        # --- TEST WORDS COLLECTIONS ---
        self.TEST_WORDS_COLLECTIONS = {
                "Kenr King Lowercase": "lynx tuft frogs, dolphins abduct by proxy the ever awkward klutz, dud, dummkopf, jinx snubnose filmgoer, orphan sgt. renfruw grudgek reyfus, md. sikh psych if halt tympany jewelry sri heh! twyer vs jojo pneu fylfot alcaaba son of nonplussed halfbreed bubbly playboy guggenheim daddy coccyx sgraffito effect, vacuum dirndle impossible attempt to disvalue, muzzle the afghan czech czar and exninja, bob bixby dvorak wood dhurrie savvy, dizzy eye aeon circumcision uvula scrungy picnic luxurious special type carbohydrate ovoid adzuki kumquat bomb? afterglows gold girl pygmy gnome lb. ankhs acme aggroupment akmed brouhha tv wt. ujjain ms. oz abacus mnemonics bhikku khaki bwana aorta embolism vivid owls often kvetch otherwise, wysiwyg densfort wright you’ve absorbed rhythm, put obstacle kyaks krieg kern wurst subject enmity equity coquet quorum pique tzetse hepzibah sulfhydryl briefcase ajax ehler kafka fjord elfship halfdressed jugful eggcup hummingbirds swingdevil bagpipe legwork reproachful hunchback archknave baghdad wejh rijswijk rajbansi rajput ajdir okay weekday obfuscate subpoena liebknecht marcgravia ecbolic arcticward dickcissel pincpinc boldface maidkin adjective adcraft adman dwarfness applejack darkbrown kiln palzy always farmland flimflam unbossy nonlineal stepbrother lapdog stopgap sx countdown basketball beaujolais vb. flowchart aztec lazy bozo syrup tarzan annoying dyke yucky hawg gagzhukz cuzco squire when hiho mayhem nietzsche szasz gumdrop milk emplotment ambidextrously lacquer byway ecclesiastes stubchen hobgoblins crabmill aqua hawaii blvd. subquality byzantine empire debt obvious cervantes jekabzeel anecdote flicflac mechanicville bedbug couldn’t i’ve it’s they’ll they’d dpt. headquarter burkhardt xerxes atkins govt. ebenezer lg. lhama amtrak amway fixity axmen quumbabda upjohn hrumpf",
                "Kenr King All Uppercase": "LYNX TUFT FROGS, DOLPHINS ABDUCT BY PROXY THE EVER AWKWARD KLUTZ, DUD, DUMMKOPF, JINX SNUBNOSE FILMGOER, ORPHAN SGT. RENFRUW GRUDGEK REYFUS, MD. SIKH PSYCH IF HALT TYMPANY JEWELRY SRI HEH! TWYER VS JOJO PNEU FYLFOT ALCAABA SON OF NONPLUSSED HALFBREED BUBBLY PLAYBOY GUGGENHEIM DADDY COCCYX SGRAFFITO EFFECT, VACUUM DIRNDLE IMPOSSIBLE ATTEMPT TO DISVALUE, MUZZLE THE AFGHAN CZECH CZAR AND EXNINJA, BOB BIXBY DVORAK WOOD DHURRIE SAVVY, DIZZY EYE AEON CIRCUMCISION UVULA SCRUNGY PICNIC LUXURIOUS SPECIAL TYPE CARBOHYDRATE OVOID ADZUKI KUMQUAT BOMB? AFTERGLOWS GOLD GIRL PYGMY GNOME LB. ANKHS ACME AGGROUPMENT AKMED BROUHHA TV WT. UJJAIN MS. OZ ABACUS MNEMONICS BHIKKU KHAKI BWANA AORTA EMBOLISM VIVID OWLS OFTEN KVETCH OTHERWISE, WYSIWYG DENSFORT WRIGHT YOU’VE ABSORBED RHYTHM, PUT OBSTACLE KYAKS KRIEG KERN WURST SUBJECT ENMITY EQUITY COQUET QUORUM PIQUE TZETSE HEPZIBAH SULFHYDRYL BRIEFCASE AJAX EHLER KAFKA FJORD ELFSHIP HALFDRESSED JUGFUL EGGCUP HUMMINGBIRDS SWINGDEVIL BAGPIPE LEGWORK REPROACHFUL HUNCHBACK ARCHKNAVE BAGHDAD WEJH RIJSWIJK RAJBANSI RAJPUT AJDIR OKAY WEEKDAY OBFUSCATE SUBPOENA LIEBKNECHT MARCGRAVIA ECBOLIC ARCTICWARD DICKCISSEL PINCPINC BOLDFACE MAIDKIN ADJECTIVE ADCRAFT ADMAN DWARFNESS APPLEJACK DARKBROWN KILN PALZY ALWAYS FARMLAND FLIMFLAM UNBOSSY NONLINEAL STEPBROTHER LAPDOG STOPGAP SX COUNTDOWN BASKETBALL BEAUJOLAIS VB. FLOWCHART AZTEC LAZY BOZO SYRUP TARZAN ANNOYING DYKE YUCKY HAWG GAGZHUKZ CUZCO SQUIRE WHEN HIHO MAYHEM NIETZSCHE SZASZ GUMDROP MILK EMPLOTMENT AMBIDEXTROUSLY LACQUER BYWAY ECCLESIASTES STUBCHEN HOBGOBLINS CRABMILL AQUA HAWAII BLVD. SUBQUALITY BYZANTINE EMPIRE DEBT OBVIOUS CERVANTES JEKABZEEL ANECDOTE FLICFLAC MECHANICVILLE BEDBUG COULDN’T I’VE IT’S THEY’LL THEY’D DPT. HEADQUARTER BURKHARDT XERXES ATKINS GOVT. EBENEZER LG. LHAMA AMTRAK AMWAY FIXITY AXMEN QUUMBABDA UPJOHN HRUMPF", 
                "Kenr King Most Common Initial Caps": "Aaron Abraham Adam Aeneas Agfa Ahoy Aileen Akbar Alanon Americanism Anglican Aorta April Fool’s Day Aqua Lung (Tm.) Arabic Ash Wednesday Authorized Version Ave Maria Away Axel Ay Aztec Bhutan Bill Bjorn Bk Btu. Bvart Bzonga California Cb Cd Cervantes Chicago Clute City, Tx. Cmdr. Cnossus Coco Cracker State, Georgia Cs Ct. Cwacker Cyrano David Debra Dharma Diane Djakarta Dm Dnepr Doris Dudley Dwayne Dylan Dzerzhinsk Eames Ectomorph Eden Eerie Effingham, Il. Egypt Eiffel Tower Eject Ekland Elmore Entreaty Eolian Epstein Equine Erasmus Eskimo Ethiopia Europe Eva Ewan Exodus Jan van Eyck Ezra Fabian February Fhara Fifi Fjord Florida Fm France Fs Ft. Fury Fyn Gabriel Gc Gdynia Gehrig Ghana Gilligan Karl Gjellerup Gk. Glen Gm Gnosis Gp.E. Gregory Gs Gt. Br. Guinevere Gwathmey Gypsy Gzags Hebrew Hf Hg Hileah Horace Hrdlicka Hsia Hts. Hubert Hwang Hai Hyacinth Hz. Iaccoca Ibsen Iceland Idaho If Iggy Ihre Ijit Ike Iliad Immediate Innocent Ione Ipswitch Iquarus Ireland Island It Iud Ivert Iwerks Ixnay Iy Jasper Jenks Jherry Jill Jm Jn Jorge Jr. Julie Kerry Kharma Kiki Klear Koko Kruse Kusack Kylie Laboe Lb. Leslie Lhihane Llama Lorrie Lt. Lucy Lyle Madeira Mechanic Mg. Minnie Morrie Mr. Ms. Mt. Music My Nanny Nellie Nillie Novocane Null Nyack Oak Oblique Occarina Odd Oedipus Off Ogmane Ohio Oil Oj Oklahoma Olio Omni Only Oops Opera Oqu Order Ostra Ottmar Out Ovum Ow Ox Oyster Oz Parade Pd. Pepe Pfister Pg. Phil Pippi Pj Please Pneumonia Porridge Price Psalm Pt. Purple Pv Pw Pyre Qt. Quincy Radio Rd. Red Rhea Right Rj Roche Rr Rs Rt. Rural Rwanda Ryder Sacrifice Series Sgraffito Shirt Sister Skeet Slow Smore Snoop Soon Special Squire Sr St. Suzy Svelte Swiss Sy Szach Td Teach There Title Total Trust Tsena Tulip Twice Tyler Tzean Ua Udder Ue Uf Ugh Uh Ui Uk Ul Um Unkempt Uo Up Uq Ursula Use Utmost Uvula Uw Uxurious Uzßai Valerie Velour Vh Vicky Volvo Vs Water Were Where With World Wt. Wulk Wyler Xavier Xerox Xi Xylophone Yaboe Year Yipes Yo Ypsilant Ys Yu Zabar’s Zero Zhane Zizi Zorro Zu Zy Don’t I’ll I’m I’se",
                "Briem's": "/A/y/space/A/w/space/A/v/space/A/quotesingle/space/A/Y/space/A/W/space/A/V/space/A/T/space/F/period/space/F/comma/space/F/A/space/L/y/space/L/quotesingle/space/L/Y/space/L/W/space/L/V/space/L/T/space/P/period/space/P/comma/space/P/A/space/R/y\n/space/R/Y/R/W/space/R/V/space/R/T/space/T/y/space/T/w/space/T/u/space/T/semicolon/space/T/s/space/T/r/space/T/period/space/T/o/space/T/i/space/T/hyphen/space/T/e/space/T/comma/space/T/colon/space/T/c/space/T/a/space/T/A/space/V/y/space/V/u/space\n/V/semicolon/space/V/r/space/V/period/space/V/o/space/V/i/space/V/hyphen/space/V/e/space/V/comma/space/V/colon/space/V/a/space/V/A/space/W/y/space/W/u/space/W/semicolon/space/W/r/space/W/period/space/W/o/space/W/i/space/W/hyphen/space/W/e\n/space/W/comma/space/W/colon/space/W/a/space/W/A/space/Y/v/space/Y/u/space/Y/semicolon/space/Y/q/space/Y/period/space/Y/p/space/Y/o/space/Y/i/space/Y/hyphen/space/Y/e/space/Y/comma/space/Y/colon/space/Y/a/space/Y/A\n/f/quotesingle/space/f/f/space/space/quotesingle/t/space/quotesingle/s/space/quotesingle/quotesingle/space/r/z/space/r/y/space/r/x/space/r/w/space/r/v/space/r/u/space/r/t/space/r/r/space/r/quotesingle/space/r/q/space/r/period/space/r/o/space/r/n/space/r/m/space/r/hyphen/space/r/h/space/r/g/space/r/f/space/r/e/space/r/d/space/r/comma/space/r/c/space/v/period/space/v/comma\n/space/w/period/space/w/comma/space/y/period/space/y/comma/space/n/period/space/r/period/space/v/period/space/w/period/space/y/period/space/n/hyphen/n/space/o/hyphen/o\n\n/n/n/a/n/n/b/n/n/c/n/n/d/n/n/e/n/n\n/n/n/f/n/n/g/n/n/h/n/n/i/n/n/j/n/n\n/n/n/k/n/n/l/n/n/m/n/n/o/n/n/p/n/n\n/n/n/q/n/n/r/n/n/s/n/n/t/n/n/u/n/n\n/n/n/v/n/n/w/n/n/x/n/n/y/n/n/z/n/n\n\n/o/o/a/o/o/b/o/o/c/o/o/d/o/o/e/o/o\n/o/o/f/o/o/g/o/o/h/o/o/i/o/o/j/o/o\n/o/o/k/o/o/l/o/o/m/o/o/n/o/o/p/o/o\n/o/o/q/o/o/r/o/o/s/o/o/t/o/o/u/o/o\n/o/o/v/o/o/w/o/o/x/o/o/y/o/o/z/o/o\n\n/n/n/A/n/n/B/n/n/C/n/n\n/n/n/D/n/n/E/n/n/F/n/n/G/n/n/H/n/n\n/n/n/I/n/n/J/n/n/K/n/n/L/n/n/M/n/n\n/n/n/N/n/n/O/n/n/P/n/n/Q/n/n/R/n/n\n/n/n/S/n/n/T/n/n/U/n/n/V/n/n/W/n/n\n/n/n/X/n/n/Y/n/n/Z/n/n\n\n/o/o/A/o/o/B/o/o/C/o/o\n/o/o/D/o/o/E/o/o/F/o/o/G/o/o/H/o/o\n/o/o/I/o/o/J/o/o/K/o/o/L/o/o/M/o/o\n/o/o/N/o/o/O/o/o/P/o/o/Q/o/o/R/o/o\n/o/o/S/o/o/T/o/o/U/o/o/V/o/o/W/o/o\n/o/o/X/o/o/Y/o/o/Z/o/o\n\n/H/space/H/space/A/space/H/space/H/space/T/space/H/space/H/space/V/space/H/space/H/space/W/space/H/space/H/space/Y/space/H/space/H\n/O/space/O/space/A/space/O/space/O/space/T/space/O/space/O/space/V/space/O/space/O/space/W/space/O/space/O/space/Y/space/O/space/O\n\n/H/A/H/B/H/C/H/D/H/E/H/F/H\n/H/G/H/I/H/J/H/K/H/L/H/M/H/N/H\n/H/N/H/O/H/P/H/Q/H/R/H/S/H/T/H\n/H/U/H/V/H/W/H/X/H/Y/H/Z/H\n\n/O/A/O/B/O/C/O/D/O/E/O/F/O\n/O/G/O/H/O/I/O/J/O/K/O/L/O/M/O\n/O/N/O/P/O/Q/O/R/O/S/O/T/O\n/O/U/O/V/O/W/O/X/O/Y/O/Z/O\n", 
                "Stephenson Blake": "/C/O/M/M/O/O/N/W/E/A/L/T/H/question/space/W/A/R/W/I/C/K/S/H/I/R/E/semicolon/space/B/A/L/A/C/L/A/V/A/H/exclam\n/B/I/R/M/I/N/G/H/A/M/space/O/S/S/O/R/Y/quotesingle/S/space/M/U/Z/Z/L/E/M/space/E/N/J/O/Y/M/AE/N/T/S\n/S/U/P/P/R/O/S/S/OE/N/S/space/L/I/V/E/E/R/P/O/O/L/space/S/O/C/I/E/T/I/E/S/space/Q/U/R/Q/U/H/A/R/T/S\n/S/H/E/F/F/I/E/L/D/space/U/N/I/T/E/D/colon/space/V/E/C/C/H/I/hyphen/H/I/N/T/T/I/N/G\n\n/H/H/A/A/H/B/B/H/C/C/H/D/D/H/E/E/H/F/F/H/G/G/H/I/I/H/J/J/H/K/K/H/L/L/H/M/M/H\n/H/N/N/H/O/O/H/P/P/H/Q/Q/H/R/R/H/S/S/H/T/T/H/U/U/H/V/V/H/W/W/H/X/X/H\n/H/Y/Y/H/Z/Z/H/AE/AE/H/OE/OE/H/ampersand/c/period/comma/ampersand/c/period/space/space/space/space/space/space/H/H/O/O/H/period/space/n/n/o/o/n/period\n\n/h/a/m/m/o/n/d/semicolon/space/w/e/l/c/h/p/o/o/l/colon/space/c/a/r/b/o/n/i/f/e/r/o/u/s/exclam/space/w/e/e/d/hyphen/h/a/a/r/l/e/m/space/h/o/d/d/l/e/d/o/p\n/m/o/g/g/o/r/t/o/n/quotesingle/s/space/d/i/v/i/n/e/s/space/e/x/c/e/l/e/n/t/space/q/u/i/n/q/u/e/n/n/i/a/l/space/i/x/i/a/s/space/m/a/c/c/a/b/e/e/s\n/c/o/m/m/o/o/n/w/e/a/l/t/h/question/space/t/a/r/q/u/i/n/space/p/o/s/s/e/s/s/i/o/n/s/space/p/a/t/r/i/a/r/c/h/s/space/i/n/f/l/a/m/e\n/m/u/z/z/l/e/m/space/parenleft/s/a/n/c/t/i/f/i/e/d/parenright/space/d/e/s/c/h/ae/p/e/l/e/s/space/s/u/m/oe/t/r/a/space/n/w/a/v/e/y/n\n\n/n/n/a/a/n/b/b/n/c/c/n/d/d/n/e/e/n/f/f/n/g/g/n/h/h/n/i/i/n/j/j/n/k/k/n/l/l/n/m/m/n/o/o/n\n/n/p/p/n/q/q/n/r/r/n/s/s/n/t/t/n/u/u/n/v/v/n/w/w/n/x/x/n/y/y/n/z/z/n/ae/ae/n/oe/oe/n\n/n/f/i/f/i/n/f/l/f/l/n/f/f/f/f/n/f/f/i/f/f/i/n/f/f/l/f/f/l/n/ampersand/c/period/comma/ampersand/c/period/space/space/space/space/space/N/o/v/e/m/b/e/r/space/two/six/t/h/comma/space/one/nine/five/eight\n\n/n/n/comma/comma/n/period/period/n/colon/colon/n/hyphen/hyphen/n/space/space/space/space/space/H/H/exclam/exclam/H/question/question/H/quoteleft/H/quoteright/H/quotedblleft/H/quotedblright/H\n\n/sterling/zero/zero/one/one/zero/two/two/zero/three/three/zero/four/four/zero/five/five/zero/six/six/zero/seven/seven/zero/eight/eight/zero/nine/nine/zero/sterling\n/dollar/zero/three/one/nine/two/eight/three/four/seven/five/four/one/five/nine/two/six/one/four/eight/three/seven/five/nine/one/seven/one/dollar\n",
                "Numbers": "/zero/one/zero/two/zero/three/zero/four/zero/five/zero/six/zero/seven/zero/eight/zero/nine/zero/zero\n/nine/one/nine/two/nine/three/nine/four/nine/five/nine/six/nine/seven/nine/eight/nine/nine/zero/nine\n/eight/one/eight/two/eight/three/eight/four/eight/five/eight/six/eight/seven/eight/eight/nine/eight/zero/eight\n/seven/one/seven/two/seven/three/seven/four/seven/five/seven/six/seven/seven/eight/seven/nine/seven/zero/seven\n/six/one/six/two/six/three/six/four/six/five/six/six/seven/six/eight/six/nine/six/zero/six\n/five/one/five/two/five/three/five/four/five/five/six/five/seven/five/eight/five/nine/five/zero/five\n/four/one/four/two/four/three/four/four/five/four/six/four/seven/four/eight/four/nine/four/zero/four\n/three/one/three/two/three/three/four/three/five/three/six/three/seven/three/eight/three/nine/three/zero/three\n/two/one/two/two/three/two/four/two/five/two/six/two/seven/two/eight/two/nine/two/zero/two\n/one/one/two/one/three/one/four/one/five/one/six/one/seven/one/eight/one/nine/one/zero/one\n\n/period/one/period/two/period/three/period/four/period/five/period/six/period/seven/period/eight/period/nine/period/zero/period\n/quotesingle/one/quotesingle/two/quotesingle/three/quotesingle/four/quotesingle/five/quotesingle/six/quotesingle/seven/quotesingle/eight/quotesingle/nine/quotesingle/zero/quotesingle\n/hyphen/one/hyphen/two/hyphen/three/hyphen/four/hyphen/five/hyphen/six/hyphen/seven/hyphen/eight/hyphen/nine/hyphen/zero/hyphen\n",
                "Minimal Kerning Pairs": "/H/H/A/T/A/H/H/space/H/H/T/AE/H/H\n/H/H/A/U/A/H/H/space/H/H/U/AE/H/H\n/H/H/A/V/A/H/H/space/H/H/V/AE/H/H\n/H/H/A/W/A/H/H/space/H/H/W/AE/H/H\n/H/H/A/Y/A/H/H/space/H/H/Y/AE/H/H\n/H/H/A/O/A/H/H/space/H/H/A/Q/A/H/H/space/H/H/A/C/H/H/space/H/H/A/G/H/H/space/H/H/D/A/H/H\n/H/H/O/AE/H/H/space/H/H/D/AE/H/H/space/H/H/Q/AE/H/H\n/H/H/O/T/O/H/H/space/H/H/Q/T/Q/H/H/space/H/H/D/T/H/H/space/H/H/T/C/H/H/space/H/H/T/G/H/H\n/H/H/O/V/O/H/H/space/H/H/Q/V/Q/H/H/space/H/H/D/V/H/H/space/H/H/V/C/H/H/space/H/H/V/G/H/H\n/H/H/O/W/O/H/H/space/H/H/Q/W/Q/H/H/space/H/H/D/W/H/H/space/H/H/W/C/H/H/space/H/H/W/G/H/H\n/H/H/O/X/O/H/H/space/H/H/Q/X/Q/H/H/space/H/H/D/X/H/H/space/H/H/X/C/H/H/space/H/H/X/G/H/H\n/H/H/O/Y/O/H/H/space/H/H/Q/Y/Q/H/H/space/H/H/D/Y/H/H/space/H/H/Y/C/H/H/space/H/H/Y/G/H/H\n/H/H/K/O/H/H/space/H/H/K/C/H/H/space/H/H/K/G/H/H/space/H/H/K/Q/H/H\n/H/H/L/O/H/H/space/H/H/L/C/H/H/space/H/H/L/G/H/H/space/H/H/L/Q/H/H\n/H/H/E/O/H/H/space/H/H/E/C/H/H/space/H/H/E/G/H/H/space/H/H/E/Q/H/H\n/H/H/F/O/H/H/space/H/H/F/C/H/H/space/H/H/F/G/H/H/space/H/H/F/Q/H/H\n/H/H/F/A/H/H/space/H/H/F/AE/H/H\n/H/H/P/A/H/H/space/H/H/P/AE/H/H\n/H/H/S/Y/H/H/space/H/H/Y/S/H/H\n/H/H/B/T/H/H/space/H/H/L/T/H/H/space/H/H/R/T/H/H\n/H/H/B/V/H/H/space/H/H/L/V/H/H/space/H/H/P/V/H/H/space/H/H/R/V/H/H/space/H/H/G/V/H/H\n/H/H/B/W/H/H/space/H/H/L/W/H/H/space/H/H/P/W/H/H/space/H/H/R/W/H/H/space/H/H/G/W/H/H\n/H/H/B/X/H/H/space/H/H/L/X/H/H/space/H/H/P/X/H/H/space/H/H/R/X/H/H/space/H/H/G/X/H/H\n/H/H/B/Y/H/H/space/H/H/L/Y/H/H/space/H/H/P/Y/H/H/space/H/H/R/Y/H/H/space/H/H/G/Y/H/H\n/H/H/F/J/H/H/space/H/H/P/J/H/H/space/H/H/T/J/H/H/space/H/H/V/J/H/H/space/H/H/W/J/H/H/space/H/H/Y/J/H/H\n/H/H/L/U/H/H/space/H/H/R/U/H/H\n/H/H/A/A/H/H/space/H/H/L/A/H/H/space/H/H/R/A/H/H/space/H/H/K/A/H/H\n\n\n/C/a/p/space/t/o/space/L/o/w/e/r\n\n/F/a/n/n/o/n/space/K/a/n/n/o/n/space/P/a/n/n/o/n/space/T/a/n/n/o/n/space/V/a/n/n/o/n/space/W/a/n/n/o/n/space/Y/a/n/n/o/n\n/F/c/n/n/o/n/space/K/c/n/n/o/n/space/P/c/n/n/o/n/space/T/c/n/n/o/n/space/V/c/n/n/o/n/space/W/c/n/n/o/n/space/X/c/n/n/o/n/space/Y/c/n/n/o/n\n/F/d/n/n/o/n/space/K/d/n/n/o/n/space/P/d/n/n/o/n/space/T/d/n/n/o/n/space/V/d/n/n/o/n/space/W/d/n/n/o/n/space/X/d/n/n/o/n/space/Y/d/n/n/o/n\n/F/e/n/n/o/n/space/K/e/n/n/o/n/space/P/e/n/n/o/n/space/T/e/n/n/o/n/space/V/e/n/n/o/n/space/W/e/n/n/o/n/space/X/e/n/n/o/n/space/Y/e/n/n/o/n\n/F/q/n/n/o/n/space/K/q/n/n/o/n/space/P/q/n/n/o/n/space/T/q/n/n/o/n/space/V/q/n/n/o/n/space/W/q/n/n/o/n/space/X/q/n/n/o/n/space/Y/q/n/n/o/n\n/F/o/n/n/o/n/space/K/o/n/n/o/n/space/P/o/n/n/o/n/space/T/o/n/n/o/n/space/V/o/n/n/o/n/space/W/o/n/n/o/n/space/X/o/n/n/o/n/space/Y/o/n/n/o/n\n/F/g/n/n/o/n/space/K/g/n/n/o/n/space/P/g/n/n/o/n/space/T/g/n/n/o/n/space/V/g/n/n/o/n/space/W/g/n/n/o/n/space/X/g/n/n/o/n/space/Y/g/n/n/o/n\n/V/i/n/n/o/n/space/W/i/n/n/o/n/space/Y/i/n/n/o/n\n/T/m/n/n/o/n/space/V/m/n/n/o/n/space/W/m/n/n/o/n/space/Y/m/n/n/o/n\n/T/n/n/n/o/n/space/V/n/n/n/o/n/space/W/n/n/n/o/n/space/Y/n/n/n/o/n\n/T/p/n/n/o/n/space/V/p/n/n/o/n/space/W/p/n/n/o/n/space/Y/p/n/n/o/n\n/T/r/n/n/o/n/space/V/r/n/n/o/n/space/W/r/n/n/o/n/space/Y/r/n/n/o/n\n/T/s/n/n/o/n/space/V/s/n/n/o/n/space/W/s/n/n/o/n/space/Y/s/n/n/o/n\n/A/t/n/n/o/n/space/Y/t/n/n/o/n\n/F/u/n/n/o/n/space/K/u/n/n/o/n/space/T/u/n/n/o/n/space/V/u/n/n/o/n/space/W/u/n/n/o/n/space/Y/u/n/n/o/n/space/X/u/n/n/o/n\n/A/v/n/n/o/n/space/K/v/n/n/o/n/space/L/v/n/n/o/n/space/T/v/n/n/o/n/space/V/v/n/n/o/n/space/Y/v/n/n/o/n/space/X/v/n/n/o/n\n/A/w/n/n/o/n/space/K/w/n/n/o/n/space/L/w/n/n/o/n/space/T/w/n/n/o/n/space/V/w/n/n/o/n/space/Y/w/n/n/o/n/space/X/w/n/n/o/n\n/T/x/n/n/o/n/space/Y/x/n/n/o/n\n/A/y/n/n/o/n/space/K/y/n/n/o/n/space/L/y/n/n/o/n/space/T/y/n/n/o/n/space/V/y/n/n/o/n/space/W/y/n/n/o/n/space/Y/y/n/n/o/n/space/X/y/n/n/o/n\n/T/z/n/n/o/n/space/Y/z/n/n/o/n\n\n\n/L/o/w/e/r/space/t/o/space/L/o/w/e/r\n\n/n/o/n/a/v/n/o/n/space/n/o/n/v/a/n/o/n/space/n/o/n/a/w/n/o/n/space/n/o/n/w/a/n/o/n\n/n/o/n/o/v/o/n/o/n/space/n/o/n/c/v/c/n/o/n/space/n/o/n/e/v/e/n/o/n/space/n/o/n/b/v/d/n/o/n/space/n/o/n/p/v/q/n/o/n\n/n/o/n/o/w/o/n/o/n/space/n/o/n/c/w/c/n/o/n/space/n/o/n/e/w/e/n/o/n/space/n/o/n/b/w/d/n/o/n/space/n/o/n/p/w/q/n/o/n\n/n/o/n/o/x/o/n/o/n/space/n/o/n/c/x/c/n/o/n/space/n/o/n/e/x/e/n/o/n/space/n/o/n/b/x/d/n/o/n/space/n/o/n/p/x/q/n/o/n\n/n/o/n/o/y/o/n/o/n/space/n/o/n/c/y/c/n/o/n/space/n/o/n/e/y/e/n/o/n/space/n/o/n/b/y/d/n/o/n/space/n/o/n/p/y/q/n/o/n\n/n/o/n/k/o/n/o/n/space/n/o/n/k/c/n/o/n/space/n/o/n/k/e/n/o/n/space/n/o/n/k/d/n/o/n/space/n/o/n/k/q/n/o/n\n/n/o/n/r/a/n/o/n/space/n/o/n/r/o/n/o/n/space/n/o/n/r/c/n/o/n/space/n/o/n/r/e/n/o/n/space/n/o/n/r/d/n/o/n/space/n/o/n/r/q/n/o/n\n/n/o/n/o/f/o/n/o/n/space/n/o/n/c/f/c/n/o/n/space/n/o/n/e/f/e/n/o/n/space/n/o/n/b/f/d/n/o/n/space/n/o/n/p/f/q/n/o/n\n/n/o/n/o/t/o/n/o/n/space/n/o/n/c/t/c/n/o/n/space/n/o/n/e/t/e/n/o/n/space/n/o/n/b/t/d/n/o/n/space/n/o/n/p/t/q/n/o/n\n\n\n/C/a/p/s/space/a/n/d/space/p/u/n/c/t/u/a/t/i/o/n\n\n/H/H/quoteleft/A/H/H/space/H/H/A/quoteright/H/H/space/H/H/quoteright/A/H/H/space/H/H/quoteleft/O/H/H/space/H/H/O/quoteright/H/H/space/H/H/quoteright/O/H/H/space/H/H/L/quoteright/H/H\n/H/H/quotedblleft/A/H/H/space/H/H/A/quotedblright/H/H/space/H/H/quotedblright/A/H/H/space/H/H/quotedblleft/O/H/H/space/H/H/O/quotedblright/H/H/space/H/H/quotedblright/O/H/H/space/H/H/L/quotedblright/H/H\n/H/H/quotesingle/A/quotesingle/H/H/space/H/H/quotesingle/O/quotesingle/H/H/space/H/H/L/quotesingle/H/H/space/H/H/quotedbl/A/quotedbl/H/H/space/H/H/quotedbl/O/quotedbl/H/H/space/H/H/L/quotedbl/H/H\n/H/H/asterisk/A/asterisk/H/H/space/H/H/asterisk/O/asterisk/H/H/space/H/H/L/asterisk/H/H\n/H/H/period/O/period/H/H/space/H/H/period/T/period/H/H/space/H/H/period/U/period/H/H/space/H/H/period/V/period/H/H/space/H/H/period/W/period/H/H/space/H/H/period/Y/period/H/H\n/H/H/D/period/H/H/space/H/H/F/period/H/H/space/H/H/P/period/H/H\n/H/H/comma/O/comma/H/H/space/H/H/comma/T/comma/H/H/space/H/H/comma/U/comma/H/H/space/H/H/comma/V/comma/H/H/space/H/H/comma/W/comma/H/H/space/H/H/comma/Y/comma/H/H\n/H/H/D/comma/H/H/space/H/H/F/comma/H/H/space/H/H/P/comma/H/H\n/H/H/K/hyphen/H/H/space/H/H/L/hyphen/H/H\n/H/H/hyphen/T/hyphen/H/H/space/H/H/hyphen/V/hyphen/H/H/space/H/H/hyphen/W/hyphen/H/H/space/H/H/hyphen/X/hyphen/H/H/space/H/H/hyphen/Y/hyphen/H/H/space/H/H/hyphen/Z/hyphen/H/H\n/H/H/T/colon/H/H/space/H/H/V/colon/H/H/space/H/H/W/colon/H/H/space/H/H/Y/colon/H/H\n/H/H/T/semicolon/H/H/space/H/H/V/semicolon/H/H/space/H/H/W/semicolon/H/H/space/H/H/Y/semicolon/H/H\n/H/H/questiondown/J/H/H/space/H/H/exclamdown/J/H/H\n\n\n/L/o/w/e/r/space/a/n/d/space/p/u/n/c/t/u/a/t/i/o/n\n\n/n/n/period/f/period/n/n/space/n/n/period/o/period/n/n/space/n/n/period/v/period/n/n/space/n/n/period/w/period/n/n/space/n/n/period/y/period/n/n/space/n/n/r/period/n/n\n/n/n/comma/f/comma/n/n/space/n/n/comma/o/comma/n/n/space/n/n/comma/v/comma/n/n/space/n/n/comma/w/comma/n/n/space/n/n/comma/y/comma/n/n/space/n/n/r/comma/n/n\n/n/o/n/f/asterisk/n/o/n/space/n/o/n/f/question/n/o/n/space/n/o/n/parenleft/f/parenright/n/o/n/space/n/o/n/bracketleft/f/bracketright/n/o/n/space/n/o/n/braceleft/f/braceright/n/o/n\n/n/o/n/f/quotesingle/n/o/n/space/n/o/n/f/quotedbl/n/o/n/space/n/o/n/f/quoteright/n/o/n/space/n/o/n/f/quotedblright/n/o/n/space/n/o/n/f/quoteleft/n/o/n/space/n/o/n/f/quotedblleft/n/o/n\n/n/o/n/questiondown/j/n/o/n/space/n/o/n/parenleft/j/parenright/n/o/n/space/n/o/n/bracketleft/j/bracketright/n/o/n/space/n/o/n/braceleft/j/braceright/n/o/n\n/n/o/n/k/hyphen/n/o/n/space/n/o/n/r/hyphen/n/o/n/space/n/o/n/hyphen/x/hyphen/n/o/n\n/n/o/n/quoteright/s/n/o/n\n",
            }

        # --- GLYPH LISTS CORRECTED - SEPARATED BY SCRIPT --
        # LATIN: only latin
        self.LATIN_LOWERCASE = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ]

        self.LATIN_UPPERCASE = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        # CYRILLIC: only cyrillic
        self.CYRILLIC_UPPERCASE = [
            # Standard English names
            'Acy', 'Becy', 'Vecy', 'Gecy', 'Gjecy', 'Djecy', 'Decy', 'Iecy', 
            'Iocy', 'Zhecy', 'Zecy', 'Iicy', 'Iishortcy', 'Kacy', 'Elcy', 
            'Emcy', 'Ency', 'Ocy', 'Pecy', 'Ercy', 'Escy', 'Tecy', 'Ucy', 
            'Efcy', 'Khacy', 'Tsecy', 'Checy', 'Shacy', 'Shchacy', 'Hardsigncy',
            'Yericy', 'Softsigncy', 'Ereversedcy', 'IUcy', 'IAcy', 'Yatcy',
            # Unicode names (UPPERCASE ONLY - range 0400-04FF)
            'uni0400', 'uni0401', 'uni0402', 'uni0403', 'uni0404', 'uni0405', 'uni0406', 'uni0407', 
            'uni0408', 'uni0409', 'uni040A', 'uni040B', 'uni040C', 'uni040D', 'uni040E', 'uni040F',
            'uni0410', 'uni0411', 'uni0412', 'uni0413', 'uni0414', 'uni0415', 'uni0416', 'uni0417',
            'uni0418', 'uni0419', 'uni041A', 'uni041B', 'uni041C', 'uni041D', 'uni041E', 'uni041F',
            'uni0420', 'uni0421', 'uni0422', 'uni0423', 'uni0424', 'uni0425', 'uni0426', 'uni0427',
            'uni0428', 'uni0429', 'uni042A', 'uni042B', 'uni042C', 'uni042D', 'uni042E', 'uni042F',
            'uni0490', 'uni0491'  # Additional Gje
        ]

        self.CYRILLIC_LOWERCASE = [
            # Standard English names (lowercase)
            'acy', 'becy', 'vecy', 'gecy', 'gjecy', 'djecy', 'decy', 'iecy', 
            'iocy', 'zhecy', 'zecy', 'iicy', 'iishortcy', 'kacy', 'elcy', 
            'emcy', 'ency', 'ocy', 'pecy', 'ercy', 'escy', 'tecy', 'ucy', 
            'efcy', 'khacy', 'tsecy', 'checy', 'shacy', 'shchacy', 'hardsigncy',
            'yericy', 'softsigncy', 'ereversedcy', 'iucy', 'iacy', 'yatcy',
            # Unicode names (LOWERCASE ONLY - range 0430-045F)
            'uni0430', 'uni0431', 'uni0432', 'uni0433', 'uni0434', 'uni0435', 'uni0436', 'uni0437',
            'uni0438', 'uni0439', 'uni043A', 'uni043B', 'uni043C', 'uni043D', 'uni043E', 'uni043F',
            'uni0440', 'uni0441', 'uni0442', 'uni0443', 'uni0444', 'uni0445', 'uni0446', 'uni0447',
            'uni0448', 'uni0449', 'uni044A', 'uni044B', 'uni044C', 'uni044D', 'uni044E', 'uni044F',
            'uni0450', 'uni0451', 'uni0452', 'uni0453', 'uni0454', 'uni0455', 'uni0456', 'uni0457',
            'uni0458', 'uni0459', 'uni045A', 'uni045B', 'uni045C', 'uni045D', 'uni045E', 'uni045F',
            'uni0491'  # Additional gje lowercase
        ]

        self.BASIC_NUMBERS = [
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]

        # DIACRITICS - separated by script
        self.LATIN_UPPERCASE_DIACRITICS = [
            'Aacute', 'Abreve', 'Acaron', 'Acircumflex', 'Adblgrave', 'Adieresis', 'Adotbelow', 
            'Agrave', 'Ainvertedbreve', 'Amacron', 'Aogonek', 'Aring', 'Atilde', 'AEacute', 
            'Bdotaccent', 'Cacute', 'Ccaron', 'Ccedilla', 'Ccircumflex', 'Cdotaccent', 
            'Dcaron', 'Ddotaccent', 'Ddotbelow', 'Eacute', 'Ebreve', 'Ecaron', 'Ecircumflex', 
            'Edblgrave', 'Edieresis', 'Edotaccent', 'Edotbelow', 'Egrave', 'Einvertedbreve', 
            'Emacron', 'Eogonek', 'Etilde', 'Fdotaccent', 'Gacute', 'Gbreve', 'Gcaron', 
            'Gcircumflex', 'Gcommaaccent', 'Gdotaccent', 'Gmacron', 'Hbar', 'Hcircumflex', 
            'Hdotbelow', 'Iacute', 'Ibreve', 'Icaron', 'Icircumflex', 'Idblgrave', 'Idieresis', 
            'Idotaccent', 'Idotbelow', 'Igrave', 'Iinvertedbreve', 'Imacron', 'Iogonek', 
            'Itilde', 'Jacute', 'Jcircumflex', 'Kcommaaccent', 'Lacute', 'Lcaron', 
            'Lcommaaccent', 'Lslash', 'Mdotaccent', 'Nacute', 'Ncaron', 'Ncommaaccent', 
            'Ndotaccent', 'Nhookleft', 'Ntilde', 'Eng', 'Oacute', 'Obreve', 'Ocaron', 
            'Ocircumflex', 'Odblgrave', 'Odieresis', 'Odotbelow', 'Ograve', 'Ohungarumlaut', 
            'Oinvertedbreve', 'Omacron', 'Oogonek', 'Oslash', 'Oslashacute', 'Otilde', 
            'Pdotaccent', 'Racute', 'Rcaron', 'Rcommaaccent', 'Rdblgrave', 'Rdotbelow', 
            'Rinvertedbreve', 'Sacute', 'Scaron', 'Scedilla', 'Scircumflex', 'Scommaaccent', 
            'Sdotaccent', 'Sdotbelow', 'Tbar', 'Tcaron', 'Tcedilla', 'Tcommaaccent', 
            'Tdotaccent', 'Tdotbelow', 'Uacute', 'Ubreve', 'Ucaron', 'Ucircumflex', 
            'Udblgrave', 'Udieresis', 'Udotbelow', 'Ugrave', 'Uhungarumlaut', 'Uinvertedbreve', 
            'Umacron', 'Uogonek', 'Uring', 'Utilde', 'Wacute', 'Wcircumflex', 'Wdieresis', 
            'Wgrave', 'Yacute', 'Ycircumflex', 'Ydieresis', 'Ygrave', 'Ymacron', 'Ytilde', 
            'Zacute', 'Zcaron', 'Zdotaccent', 'Zdotbelow', 'Lcommaaccent.loclMAH', 'Ncommaaccent.loclMAH'
        ]

        self.LATIN_LOWERCASE_DIACRITICS = [
            'aacute', 'abreve', 'acaron', 'acircumflex', 'adblgrave', 'adieresis', 'adotbelow', 
            'agrave', 'ainvertedbreve', 'amacron', 'aogonek', 'aring', 'atilde', 'ae', 
            'bdotaccent', 'cacute', 'ccaron', 'ccedilla', 'ccircumflex', 'cdotaccent', 
            'dcaron', 'ddotaccent', 'ddotbelow', 'eacute', 'ebreve', 'ecaron', 'ecircumflex', 
            'edblgrave', 'edieresis', 'edotaccent', 'edotbelow', 'egrave', 'einvertedbreve', 
            'emacron', 'eogonek', 'etilde', 'fdotaccent', 'gacute', 'gbreve', 'gcaron', 
            'gcircumflex', 'gcommaaccent', 'gdotaccent', 'gmacron', 'hbar', 'hcircumflex', 
            'hdotbelow', 'iacute', 'ibreve', 'icaron', 'icircumflex', 'idblgrave', 'idieresis', 
            'idotaccent', 'idotbelow', 'igrave', 'iinvertedbreve', 'imacron', 'iogonek', 
            'itilde', 'jacute', 'jcircumflex', 'kcommaaccent', 'lacute', 'lcaron', 
            'lcommaaccent', 'lslash', 'mdotaccent', 'nacute', 'ncaron', 'ncommaaccent', 
            'ndotaccent', 'nhookleft', 'ntilde', 'eng', 'oacute', 'obreve', 'ocaron', 
            'ocircumflex', 'odblgrave', 'odieresis', 'odotbelow', 'ograve', 'ohungarumlaut', 
            'oinvertedbreve', 'omacron', 'oogonek', 'oslash', 'otilde', 'pdotaccent', 
            'racute', 'rcaron', 'rcommaaccent', 'rdblgrave', 'rdotbelow', 'rinvertedbreve', 
            'sacute', 'scaron', 'scedilla', 'scircumflex', 'scommaaccent', 'sdotaccent', 
            'sdotbelow', 'tbar', 'tcaron', 'tcedilla', 'tcommaaccent', 'tdotaccent', 
            'tdotbelow', 'uacute', 'ubreve', 'ucaron', 'ucircumflex', 'udblgrave', 'udieresis', 
            'udotbelow', 'ugrave', 'uhungarumlaut', 'uinvertedbreve', 'umacron', 'uogonek', 
            'uring', 'utilde', 'wacute', 'wcircumflex', 'wdieresis', 'wgrave', 'yacute', 
            'ycircumflex', 'ydieresis', 'ygrave', 'ymacron', 'ytilde', 'zacute', 'zcaron', 
            'zdotaccent', 'zdotbelow', 'lcommaaccent.loclMAH', 'ncommaaccent.loclMAH'
        ]

        # Cyrillic diacritics (if any)
        self.CYRILLIC_UPPERCASE_DIACRITICS = [
            # Add specific cyrillic diacritics if they exist
        ]

        self.CYRILLIC_LOWERCASE_DIACRITICS = [
            # Add specific cyrillic diacritics if they exist
        ]

        self.PUNCTUATION_GLYPHS = [
            'period', 'comma', 'colon', 'semicolon', 'ellipsis', 'exclam', 'exclamdown', 
            'question', 'questiondown', 'periodcentered', 'bullet', 'asterisk', 'numbersign', 
            'slash', 'backslash', 'hyphen', 'endash', 'emdash', 'underscore', 'parenleft', 
            'parenright', 'braceleft', 'braceright', 'bracketleft', 'bracketright', 
            'quotesinglbase', 'quotedblbase', 'quotedblleft', 'quotedblright', 'quoteleft', 
            'quoteright', 'guillemetleft', 'guillemetright', 'guilsinglleft', 'guilsinglright', 
            'quotedbl', 'quotesingle'
        ]

        self.SYMBOLS_GLYPHS = [
            'baht', 'at', 'ampersand', 'paragraph', 'section', 'copyright', 'registered', 
            'trademark', 'degree', 'bar', 'brokenbar', 'dagger', 'daggerdbl', 'cent', 
            'currency', 'dollar', 'euro', 'sterling', 'yen', 'plus', 'minus', 'multiply', 
            'divide', 'equal', 'notequal', 'greater', 'less', 'greaterequal', 'lessequal', 
            'plusminus', 'logicalnot', 'asciicircum', 'partialdiff', 'percent', 'perthousand', 
            'upArrow', 'northEastArrow', 'rightArrow', 'southEastArrow', 'downArrow', 
            'southWestArrow', 'leftArrow', 'northWestArrow', 'leftRightArrow', 'upDownArrow', 
            'lozenge'
        ]

        # Combine lists CORRECTED - SEPARATED BY SCRIPT
        # LATIN: only latin elements
        self.BASIC_LATIN_LOWERCASE = self.LATIN_LOWERCASE
        self.BASIC_LATIN_UPPERCASE = self.LATIN_UPPERCASE
        self.EXTENDED_LATIN_LOWERCASE = self.LATIN_LOWERCASE + self.LATIN_LOWERCASE_DIACRITICS
        self.EXTENDED_LATIN_UPPERCASE = self.LATIN_UPPERCASE + self.LATIN_UPPERCASE_DIACRITICS

        # CYRILLIC: only cyrillic elements
        self.BASIC_CYRILLIC_LOWERCASE = self.CYRILLIC_LOWERCASE
        self.BASIC_CYRILLIC_UPPERCASE = self.CYRILLIC_UPPERCASE
        self.EXTENDED_CYRILLIC_LOWERCASE = self.CYRILLIC_LOWERCASE + self.CYRILLIC_LOWERCASE_DIACRITICS
        self.EXTENDED_CYRILLIC_UPPERCASE = self.CYRILLIC_UPPERCASE + self.CYRILLIC_UPPERCASE_DIACRITICS

        # UI Elements - COMPACT LAYOUT
        y = 10

        # Base glyphs
        tab.baseLabel = TextBox((15, y, -15, 20), "Base glyph names (comma separated):")
        y += 25
        tab.baseInput = EditText((15, y, -15, 24), "A, V, T, L, f, v, o")
        y += 40

        # Position dropdown - compact
        tab.positionLabel = TextBox((15, y, 80, 20), "Position:")
        tab.positionPopup = PopUpButton((100, y, 120, 24), ["Left", "Right", "Both"])
        tab.positionPopup.set(2)
        y += 40

        # Neighboring sets - MORE COMPACT layout
        tab.neighLabel = TextBox((15, y, -15, 20), "Neighboring sets:")
        y += 25
        
        # First row - LATIN and Numbers
        tab.latinUpperCheck = CheckBox((15, y, 100, 20), "Latin Upper", value=False)
        tab.latinLowerCheck = CheckBox((120, y, 100, 20), "Latin Lower", value=True)
        tab.numCheck = CheckBox((225, y, 80, 20), "Numbers", value=False)
        y += 25
        
        # Second row - Punctuation and Symbols
        tab.puncCheck = CheckBox((15, y, 100, 20), "Punctuation", value=False)
        tab.symCheck = CheckBox((120, y, 80, 20), "Symbols", value=False)
        y += 25
        
        # Third row - CYRILLIC
        tab.cyrillicUpperCheck = CheckBox((15, y, 110, 20), "Cyrillic Upper", value=False)
        tab.cyrillicLowerCheck = CheckBox((130, y, 110, 20), "Cyrillic Lower", value=False)
        y += 40

        # Editable prefixes and suffixes - COMPACT
        tab.prefixLabel = TextBox((15, y, 50, 20), "Prefix:")
        tab.prefixInput = EditText((70, y, 80, 24), "HHOH") 
        tab.suffixLabel = TextBox((165, y, 50, 20), "Suffix:")
        tab.suffixInput = EditText((220, y, 80, 24), "HOOH")
        y += 40

        # Options - compact
        tab.considerGroups = CheckBox((15, y, -15, 20), "Consider kerning groups (avoid duplicates)", value=True)
        y += 25
        tab.showExisting = CheckBox((15, y, -15, 20), "Show existing kerns at top (with values)", value=True)
        y += 40

        # Text size - compact
        tab.sizeLabel = TextBox((15, y, 100, 20), "Sample text size:")
        tab.sizeInput = EditText((120, y, 60, 24), "60")
        y += 40

        # Kerning groups information - COMPACT
        tab.groupsInfo = TextBox((15, y, -15, 20), "Kerning groups status: Click 'Check' to analyze", sizeStyle="small")
        y += 30
        
        # Kerning groups buttons - COMPACT
        tab.checkGroupsButton = Button((15, y, 140, 24), "Check Kerning Groups", callback=self.checkGroupsCallback)
        tab.fillGroupsButton = Button((165, y, 120, 24), "Fill Empty Groups", callback=self.fillGroupsCallback)
        y += 40

        
        # Feature selector (OpenType features from the open font)
        feature_names = self.getFeatureNames()
        tab.featureLabel = TextBox((15, y, 120, 18), "Select feature:")
        tab.featurePopup = PopUpButton((140, y-2, 200, 24), feature_names)
        y += 36
# Main button
        tab.generateButton = Button((15, y, -15, 32), "Generate Tabs", callback=self.generatePairsGeneratorCallback)
        y += 50
        
        # Test Words section - NOW VISIBLE
        tab.testWordsLabel = TextBox((15, y, 80, 20), "Test Words:")
        tab.testWordsPopup = PopUpButton((100, y, 200, 24), list(self.TEST_WORDS_COLLECTIONS.keys()))
        y += 35
        tab.testWordsButton = Button((15, y, -15, 28), "Insert Test Words", callback=self.insertTestWordsCallback)

    # --- IMPROVED FUNCTION: Determine glyph script ---
    def get_glyph_script(self, glyph_name):
        """Determines if a glyph is latin, cyrillic, number, punctuation, etc."""
        if not glyph_name:
            return "unknown"
        
        # Check explicit lists first
        if (glyph_name in self.LATIN_LOWERCASE or glyph_name in self.LATIN_UPPERCASE or 
            glyph_name in self.LATIN_LOWERCASE_DIACRITICS or glyph_name in self.LATIN_UPPERCASE_DIACRITICS):
            return "latin"
        
        if (glyph_name in self.CYRILLIC_LOWERCASE or glyph_name in self.CYRILLIC_UPPERCASE or 
            glyph_name in self.CYRILLIC_LOWERCASE_DIACRITICS or glyph_name in self.CYRILLIC_UPPERCASE_DIACRITICS):
            return "cyrillic"
        
        if glyph_name in self.BASIC_NUMBERS:
            return "number"
        
        if glyph_name in self.PUNCTUATION_GLYPHS:
            return "punctuation"
        
        if glyph_name in self.SYMBOLS_GLYPHS:
            return "symbol"
        
        # Check by unicode if in font
        font = Glyphs.font
        if glyph_name in font.glyphs:
            g = font.glyphs[glyph_name]
            if g.unicode:
                try:
                    codepoint = int(g.unicode, 16)
                    # Basic latin range
                    if (0x0041 <= codepoint <= 0x005A) or (0x0061 <= codepoint <= 0x007A):
                        return "latin"
                    # Cyrillic range
                    if 0x0400 <= codepoint <= 0x04FF:
                        return "cyrillic"
                    # Numbers
                    if 0x0030 <= codepoint <= 0x0039:
                        return "number"
                except:
                    pass
        
        # Check by unicode name
        if glyph_name.startswith("uni"):
            try:
                codepoint = int(glyph_name[3:7], 16)
                # Basic latin range
                if (0x0041 <= codepoint <= 0x005A) or (0x0061 <= codepoint <= 0x007A):
                    return "latin"
                # Cyrillic range
                if 0x0400 <= codepoint <= 0x04FF:
                    return "cyrillic"
                # Numbers
                if 0x0030 <= codepoint <= 0x0039:
                    return "number"
            except:
                pass
        
        return "unknown"

    # --- IMPROVED FUNCTION: Determine if a glyph is uppercase ---
    def is_uppercase_glyph(self, glyph_name):
        """Determine if a glyph is uppercase based on its name and unicode"""
        font = Glyphs.font
        if not glyph_name:
            return True  # default safe

        # 1. Check explicit lists first (most reliable)
        if (glyph_name in self.LATIN_UPPERCASE or glyph_name in self.LATIN_UPPERCASE_DIACRITICS or 
            glyph_name in self.CYRILLIC_UPPERCASE or glyph_name in self.CYRILLIC_UPPERCASE_DIACRITICS):
            return True
        
        if (glyph_name in self.LATIN_LOWERCASE or glyph_name in self.LATIN_LOWERCASE_DIACRITICS or 
            glyph_name in self.CYRILLIC_LOWERCASE or glyph_name in self.CYRILLIC_LOWERCASE_DIACRITICS):
            return False

        # 2. If glyph exists in font, inspect its unicode value
        if glyph_name in font.glyphs:
            g = font.glyphs[glyph_name]
            if g.unicode:
                try:
                    char = chr(int(g.unicode, 16))
                    # For latin and cyrillic, use standard functions
                    if char.isupper():
                        return True
                    if char.islower():
                        return False
                except:
                    pass

        # 3. For unicode names (uni0410, etc.), check the range
        if glyph_name.startswith("uni") and len(glyph_name) == 7:
            try:
                codepoint = int(glyph_name[3:7], 16)
                # Cyrillic uppercase: 0400-04FF where isupper() is True
                if 0x0400 <= codepoint <= 0x04FF:
                    char = chr(codepoint)
                    return char.isupper()
                # Latin uppercase: 0041-005A
                if 0x0041 <= codepoint <= 0x005A:
                    return True
                # Latin lowercase: 0061-007A  
                if 0x0061 <= codepoint <= 0x007A:
                    return False
            except:
                pass

        # 4. Name heuristic (last resort)
        first_char = glyph_name[0] if glyph_name else ''
        if first_char.isalpha():
            return first_char.isupper()

        # 5. Default to uppercase (conservative)
        return True

    # --- IMPROVED FUNCTION: Get available cyrillic glyphs from font ---
    def get_available_cyrillic_glyphs(self):
        """Get all available cyrillic glyphs in current font"""
        font = Glyphs.font
        if not font:
            return []
        
        cyrillic_glyphs = []
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
                
            # Check by unicode (cyrillic range)
            if glyph.unicode:
                try:
                    codepoint = int(glyph.unicode, 16)
                    if 0x0400 <= codepoint <= 0x04FF:
                        cyrillic_glyphs.append({
                            'name': glyph.name,
                            'unicode': glyph.unicode,
                            'char': chr(codepoint),
                            'is_upper': chr(codepoint).isupper()
                        })
                except:
                    pass
            # Check by name containing 'cy' or in our lists
            elif 'cy' in glyph.name.lower():
                cyrillic_glyphs.append({
                    'name': glyph.name,
                    'unicode': None,
                    'char': None,
                    'is_upper': glyph.name[0].isupper() if glyph.name else True
                })
        
        return cyrillic_glyphs

    # --- IMPROVED FUNCTION: For debugging ---
    def debug_cyrillic_glyphs(self, base_names):
        """Function to debug cyrillic glyphs"""
        font = Glyphs.font
        if not font:
            return "No font open"
        
        debug_info = ["=== CYRILLIC DEBUG ==="]
        
        # Cyrillic glyphs available information
        available_cyr = self.get_available_cyrillic_glyphs()
        debug_info.append(f"Cyrillic glyphs found: {len(available_cyr)}")
        
        for cyr in available_cyr[:10]:  # Show only first 10
            debug_info.append(f"  {cyr['name']} (U+{cyr['unicode']}) -> '{cyr['char']}' -> {'UPPERCASE' if cyr['is_upper'] else 'lowercase'}")
        
        # Check requested base glyphs
        debug_info.append("\n=== REQUESTED BASE GLYPHS ===")
        for base in base_names:
            if base in font.glyphs:
                g = font.glyphs[base]
                unicode_info = f"U+{g.unicode}" if g.unicode else "No unicode"
                char_info = f" -> '{chr(int(g.unicode, 16))}'" if g.unicode else ""
                script_info = self.get_glyph_script(base)
                case_info = "UPPERCASE" if self.is_uppercase_glyph(base) else "lowercase"
                debug_info.append(f"  {base} ({unicode_info}{char_info}) -> {script_info} {case_info}")
            else:
                debug_info.append(f"  {base} -> NOT FOUND")
        
        return "\n".join(debug_info)

    # --- CORRECTED FUNCTION: Convert character to glyph name ---
    def char_to_glyph_name(self, char):
        """Converts a character to glyph name (unicode)"""
        if not char or len(char) != 1:
            return char
        
        # Get character Unicode code
        unicode_value = ord(char)
        
        # Format as Unicode glyph name (4 digit hexadecimal in UPPERCASE)
        glyph_name = f"uni{unicode_value:04X}"
        
        return glyph_name

    # --- IMPROVED FUNCTION: Check if glyph exists and is valid ---
    def glyph_exists_and_valid(self, glyph_name):
        """Checks if a glyph exists and is a valid base glyph"""
        font = Glyphs.font
        if not glyph_name:
            return False
        
        # If it's a single character (like "Л"), convert to glyph name
        if len(glyph_name) == 1:
            unicode_name = self.char_to_glyph_name(glyph_name)
            
            # Search in both formats: original and alternative (uppercase/lowercase)
            if unicode_name in font.glyphs:
                return self.is_base_glyph(font.glyphs[unicode_name])
            
            # Also search alternative version (change uppercase/lowercase)
            alt_unicode_name = unicode_name.lower() if unicode_name.isupper() else unicode_name.upper()
            if alt_unicode_name in font.glyphs:
                return self.is_base_glyph(font.glyphs[alt_unicode_name])
        
        # Search by exact name
        if glyph_name in font.glyphs:
            return self.is_base_glyph(font.glyphs[glyph_name])
        
        # If name is already in unicode format (uni041B), check directly
        if glyph_name.startswith('uni') and len(glyph_name) == 7:
            if glyph_name in font.glyphs:
                return self.is_base_glyph(font.glyphs[glyph_name])
        
        return False

    # --- CORRECTED FUNCTION: glyph_to_char_or_name improved for cyrillic characters ---
    def glyph_to_char_or_name(self, glyph):
        if not glyph: 
            return ""
        
        # First try with unicode
        if glyph.unicode:
            try: 
                char = chr(int(glyph.unicode, 16))
                # For cyrillic characters and others that are not spaces/control, use them directly
                if ord(char) >= 32 and not char.isspace():
                    return char
                # If space or control character, use name
                return f"/{glyph.name}"
            except: 
                return f"/{glyph.name}"
        
        # If no unicode, use name with slash
        return f"/{glyph.name}"

    # --- CORRECTED FUNCTION: format_glyph_display improved to not return None ---
    def format_glyph_display(self, glyph_name):
        font = Glyphs.font
        if not glyph_name or glyph_name not in font.glyphs:
            return f"/{glyph_name}" if glyph_name else "/unknown"
        
        g = font.glyphs[glyph_name]
        char_or_name = self.glyph_to_char_or_name(g)
        
        # If glyph_to_char_or_name returns empty string or None, use glyph name
        if not char_or_name:
            return f"/{glyph_name}"
        
        return char_or_name

    def is_base_glyph(self, g):
        return g.category in ["Letter", "Number", "Punctuation", "Symbol"]

    def group_to_glyph(self, group_key):
        if not group_key or not group_key.startswith("@"): return group_key
        name = group_key.split("_")[-1]
        return name if name else group_key

    def representative_for_group(self, font, group_name):
        if not group_name: return None
        for g in font.glyphs:
            if g.leftKerningGroup == group_name or g.rightKerningGroup == group_name:
                return g.name
        return None

    def all_kernings_between(self, font, master_id, left_name, right_name):
        out = []
        for L in [left_name, f"@MMK_L_{left_name}"]:
            for R in [right_name, f"@MMK_R_{right_name}"]:
                try:
                    val = font.kerningForPair(master_id, L, R)
                except Exception:
                    val = None
                if val is not None:
                    out.append((L, R, val))
        return out

    def filter_unique_by_groups(self, font, glyph_names):
        """Filter duplicate glyphs by kerning groups"""
        seen_groups = set()
        result = []
        
        for name in glyph_names:
            if name not in font.glyphs:
                continue
                
            g = font.glyphs[name]
            left_group = g.leftKerningGroup
            
            if not left_group:
                left_group = f"NO_GROUP_{name}"
            
            if left_group in seen_groups:
                continue
                
            seen_groups.add(left_group)
            result.append(name)
        
        return result

    # --- Function to count glyphs without kerning groups ---
    def count_glyphs_without_kerning_groups(self, font):
        """Count how many base glyphs don't have kerning groups assigned"""
        count_left = 0
        count_right = 0
        
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
                
            if not glyph.leftKerningGroup:
                count_left += 1
                
            if not glyph.rightKerningGroup:
                count_right += 1
        
        return count_left + count_right

    # --- Function to fill kerning groups ---
    def fillKerningGroups(self, font):
        """Assign kerning groups to glyphs that don't have them"""
        count_left = 0
        count_right = 0
        
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
                
            if not glyph.leftKerningGroup:
                glyph.leftKerningGroup = glyph.name
                count_left += 1
                
            if not glyph.rightKerningGroup:
                glyph.rightKerningGroup = glyph.name
                count_right += 1
        
        return count_left + count_right

    # --- CORRECTED FUNCTION: Check kerning groups status ---
    def checkGroupsCallback(self, sender):
        """Shows information about missing kerning groups"""
        font = Glyphs.font
        if not font:
            return
            
        total_base_glyphs = 0
        glyphs_without_groups = 0
        
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
                
            total_base_glyphs += 1
            
            # Count glyphs that don't have BOTH groups assigned
            if not glyph.leftKerningGroup or not glyph.rightKerningGroup:
                glyphs_without_groups += 1
        
        message = f"Kerning Groups Analysis:\n"
        message += f"Total base glyphs: {total_base_glyphs}\n"
        message += f"Glyphs without kerning groups: {glyphs_without_groups}\n"
        
        if glyphs_without_groups == 0:
            message += "✅ All glyphs have kerning groups!"
        else:
            message += f"❌ {glyphs_without_groups} glyphs need groups assigned"
        
        # Update interface text
        self.w.tabs[0].groupsInfo.set(message)
        
        # Also show message
        Message("Kerning Groups Analysis", 
               f"Found {glyphs_without_groups} glyphs without kerning groups\nout of {total_base_glyphs} total base glyphs")

    # --- MODIFIED FUNCTION: Fill kerning groups ---
    def fillGroupsCallback(self, sender):
        """Fill empty kerning groups"""
        font = Glyphs.font
        if not font:
            return
            
        # First check current status
        glyphs_without_groups = 0
        total_base_glyphs = 0
        
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
                
            total_base_glyphs += 1
            if not glyph.leftKerningGroup or not glyph.rightKerningGroup:
                glyphs_without_groups += 1
        
        if glyphs_without_groups == 0:
            Message("No action needed", "All glyphs already have kerning groups")
            self.w.tabs[0].groupsInfo.set("✅ All glyphs have kerning groups!")
            return
        
        # Execute filling
        count = self.fillKerningGroups(font)
        
        # Update information
        remaining_without_groups = 0
        for glyph in font.glyphs:
            if not self.is_base_glyph(glyph):
                continue
            if not glyph.leftKerningGroup or not glyph.rightKerningGroup:
                remaining_without_groups += 1
        
        message = f"Kerning Groups Filled:\n"
        message += f"Assigned groups to {count} properties\n"
        message += f"Remaining without groups: {remaining_without_groups}"
        
        self.w.tabs[0].groupsInfo.set(message)
        Message("Kerning Groups Filled", 
               f"Successfully assigned kerning groups to {count} glyph properties\n{remaining_without_groups} glyphs still need attention")

    # --- Helper: detect if glyph name refers to Cyrillic (by lists or unicode block) ---
    def is_cyrillic_glyph_name(self, glyph_name):
        # Explicit lists
        if glyph_name in self.CYRILLIC_UPPERCASE or glyph_name in self.CYRILLIC_LOWERCASE:
            return True
        # Try to resolve unicode codepoint
        font = Glyphs.font
        if glyph_name in font.glyphs:
            g = font.glyphs[glyph_name]
            if g.unicode:
                try:
                    cp = int(g.unicode, 16)
                    if 0x0400 <= cp <= 0x04FF:
                        return True
                except:
                    pass
        # uniXXXX style
        if glyph_name.startswith("uni") and len(glyph_name) >= 7:
            try:
                cp = int(glyph_name[3:7], 16)
                if 0x0400 <= cp <= 0x04FF:
                    return True
            except:
                pass
        return False

    # --- MODIFIED FUNCTION: Insert test words - SILENT VERSION ---
    def insertTestWordsCallback(self, sender):
        """Insert selected test words into a new tab - silent version"""
        font = Glyphs.font
        if not font:
            return
            
        selected_index = self.w.tabs[0].testWordsPopup.get()
        test_names = list(self.TEST_WORDS_COLLECTIONS.keys())
        
        if 0 <= selected_index < len(test_names):
            test_name = test_names[selected_index]
            test_text = self.TEST_WORDS_COLLECTIONS[test_name]
            
            # Create tab with test words - silent, no messages
            tab_content = f"# {test_name}\n\n{test_text}"
            tab = font.newTab(tab_content)
            
            # Apply text size
            try: 
                text_size = int(self.w.tabs[0].sizeInput.get())
                tab.textView().setFontSize_(text_size)
            except: 
                pass

    def generatePairsGeneratorCallback(self, sender):
        self.generatePairsGenerator()

    def generatePairsGenerator(self):
        font = Glyphs.font
        if not font:
            return
            
        tab = self.w.tabs[0]
        base_names = [n.strip() for n in tab.baseInput.get().split(",") if n.strip()]
        
        # DEBUG: Show cyrillic glyphs information (commented out for silence)
        # debug_info = self.debug_cyrillic_glyphs(base_names)
        # print(debug_info)
        
        # FILTER and convert characters to glyph names
        valid_base_names = []
        
        for base in base_names:
            final_name = base
            
            # If it's a single character, convert to unicode name
            if len(base) == 1:
                unicode_name = self.char_to_glyph_name(base)
                
                # Search in both formats
                if unicode_name in font.glyphs:
                    final_name = unicode_name
                else:
                    # Search alternative version (uppercase/lowercase)
                    alt_unicode_name = unicode_name.lower() if unicode_name.isupper() else unicode_name.upper()
                    if alt_unicode_name in font.glyphs:
                        final_name = alt_unicode_name
            
            # Check if glyph exists
            if final_name in font.glyphs and self.is_base_glyph(font.glyphs[final_name]):
                valid_base_names.append(final_name)
        
        if not valid_base_names:
            # Show diagnostic information
            cyrillic_chars = []
            for base in base_names:
                if len(base) == 1:
                    unicode_val = ord(base)
                    unicode_name = f"uni{unicode_val:04X}"  # In uppercase
                    alt_unicode_name = unicode_name.lower()  # In lowercase
                    exists_upper = "✓" if unicode_name in font.glyphs else "✗"
                    exists_lower = "✓" if alt_unicode_name in font.glyphs else "✗"
                    cyrillic_chars.append(f"'{base}' (U+{unicode_val:04X}) -> {unicode_name} {exists_upper} / {alt_unicode_name} {exists_lower}")
            
            message = f"No valid glyphs found.\n\n"
            if cyrillic_chars:
                message += "Cyrillic characters search:\n" + "\n".join(cyrillic_chars) + "\n\n"
            
            # Show some available cyrillic glyphs
            available_cyrillic = []
            for glyph in font.glyphs:
                if glyph.name.startswith('uni04'):  # Cyrillic range
                    available_cyrillic.append(f"{glyph.name} -> {self.format_glyph_display(glyph.name)}")
                    if len(available_cyrillic) >= 5:  # Show only 5
                        break
            
            if available_cyrillic:
                message += "Available cyrillic glyphs:\n" + "\n".join(available_cyrillic)
            
            Message("Glyph Search", message)
            return
        
        # If we got here, we have valid glyphs
        
        position = ["left", "right", "both"][tab.positionPopup.get()]
        
        # GET SELECTED SECTIONS - NOW SEPARATED BY SCRIPT
        sections = []
        if tab.latinUpperCheck.get(): sections.append("Latin Uppercase")
        if tab.latinLowerCheck.get(): sections.append("Latin Lowercase")
        if tab.cyrillicUpperCheck.get(): sections.append("Cyrillic Uppercase")
        if tab.cyrillicLowerCheck.get(): sections.append("Cyrillic Lowercase")
        if tab.numCheck.get(): sections.append("Numbers")
        if tab.puncCheck.get(): sections.append("Punctuation")
        if tab.symCheck.get(): sections.append("Symbols")

        use_groups = tab.considerGroups.get()
        show_existing = tab.showExisting.get()

        try: text_size = int(tab.sizeInput.get())
        except: text_size = 60
        master_id = font.selectedFontMaster.id

        # Generate tabs only for valid base glyphs
        for base in valid_base_names:
            g_base = font.glyphs[base]
            base_disp = self.format_glyph_display(base)
            
            if not base_disp:
                continue
                
            tab_lines = [f"# {base} ({base_disp})", ""]

            existing_pairs_set = set()
            if show_existing:
                tab_lines += ["# Existing kerning pairs (with values)", "# ———"]
                for sec in sections:
                    neighs = self.neighbors_for_section(sec, use_groups)
                    
                    for n in neighs:
                        # Verify that neighbor glyph is valid
                        if not self.glyph_exists_and_valid(n):
                            continue
                            
                        n_disp = self.format_glyph_display(n)
                        if not n_disp:
                            continue
                            
                        for L, R, val in self.all_kernings_between(font, master_id, base, n) + self.all_kernings_between(font, master_id, n, base):
                            L_glyph = self.group_to_glyph(L)
                            R_glyph = self.group_to_glyph(R)
                            Ldisp = self.format_glyph_display(L_glyph)
                            Rdisp = self.format_glyph_display(R_glyph)
                            
                            if not Ldisp or not Rdisp:
                                continue
                                
                            pair_key = (Ldisp, Rdisp)
                            if pair_key in existing_pairs_set:
                                continue
                            existing_pairs_set.add(pair_key)
                            
                            prefix, suffix = self._getContextualSuffixes(L_glyph, R_glyph)
                            line = f"{prefix}{Ldisp}{Rdisp}{suffix}" + " " * 10 + f"{int(val)}"
                            tab_lines.append(line)
                tab_lines.append("")

            # Generate symmetric trios automatically mixed with regular pairs
            symmetric_trios = self.get_symmetric_trios_for_glyph(base, master_id)
            if symmetric_trios:
                tab_lines += ["# Symmetric trios (check consistency)", ""]
                # Remove duplicates while preserving order
                seen = set()
                unique_trios = []
                for trio in symmetric_trios:
                    if trio not in seen:
                        seen.add(trio)
                        unique_trios.append(trio)
                
                for trio_line in unique_trios:
                    tab_lines.append(trio_line)
                tab_lines.append("")

            # Generate new pairs with intelligent context - CORRECTED
            for sec in sections:
                neighs = self.neighbors_for_section(sec, use_groups)
                
                if position in ["left", "both"]:
                    tab_lines.append(f"# Left pairs - {sec}")
                    tab_lines.append("")
                    for n in neighs:
                        # VERIFY that neighbor glyph is valid
                        if not self.glyph_exists_and_valid(n):
                            continue
                            
                        n_disp = self.format_glyph_display(n)
                        if not n_disp:
                            continue
                            
                        pair_key = (base_disp, n_disp)
                        
                        existing_kern = any(self.all_kernings_between(font, master_id, base, n))
                        if pair_key in existing_pairs_set or existing_kern:
                            continue
                        
                        prefix, suffix = self._getContextualSuffixes(base, n)
                        tab_lines.append(f"{prefix}{base_disp}{n_disp}{suffix}")
                    tab_lines.append("")
                
                if position in ["right", "both"]:
                    tab_lines.append(f"# Right pairs - {sec}")
                    tab_lines.append("")
                    for n in neighs:
                        # VERIFY that neighbor glyph is valid
                        if not self.glyph_exists_and_valid(n):
                            continue
                            
                        n_disp = self.format_glyph_display(n)
                        if not n_disp:
                            continue
                            
                        pair_key = (n_disp, base_disp)
                        
                        existing_kern = any(self.all_kernings_between(font, master_id, n, base))
                        if pair_key in existing_pairs_set or existing_kern:
                            continue
                        
                        prefix, suffix = self._getContextualSuffixes(n, base)
                        tab_lines.append(f"{prefix}{n_disp}{base_disp}{suffix}")
                    tab_lines.append("")

            if len(tab_lines) > 2:
                tab_content = "\n".join(tab_lines)
                new_tab = font.newTab(tab_content)
                try:
                    # Apply selected OT feature to the newly opened tab (if any)
                    try:
                        feature_list = [f.name for f in font.features]
                        idx = tab.featurePopup.get() if hasattr(tab, 'featurePopup') else None
                        if idx is not None and isinstance(idx, int) and 0 <= idx < len(feature_list):
                            selectedFeature = feature_list[idx]
                            new_tab.features = [selectedFeature]
                    except Exception:
                        pass
                    new_tab.textView().setFontSize_(text_size)
                except:
                    pass


    def neighbors_for_section(self, section, use_groups=True):
        font = Glyphs.font
        out = []
        
        # SELECT LIST ACCORDING TO SCRIPT AND CASE
        if use_groups:
            # WITH groups: use only basic lists
            if section == "Latin Lowercase":
                target_list = self.BASIC_LATIN_LOWERCASE
            elif section == "Latin Uppercase":
                target_list = self.BASIC_LATIN_UPPERCASE
            elif section == "Cyrillic Lowercase":
                target_list = self.BASIC_CYRILLIC_LOWERCASE
            elif section == "Cyrillic Uppercase":
                target_list = self.BASIC_CYRILLIC_UPPERCASE
            elif section == "Numbers":
                target_list = self.BASIC_NUMBERS
            elif section == "Punctuation":
                target_list = self.PUNCTUATION_GLYPHS
            elif section == "Symbols":
                target_list = self.SYMBOLS_GLYPHS
            else:
                target_list = []
        else:
            # WITHOUT groups: use complete extended lists for letters and numbers
            if section == "Latin Uppercase":
                target_list = self.EXTENDED_LATIN_UPPERCASE
            elif section == "Latin Lowercase":
                target_list = self.EXTENDED_LATIN_LOWERCASE
            elif section == "Cyrillic Uppercase":
                target_list = self.EXTENDED_CYRILLIC_UPPERCASE
            elif section == "Cyrillic Lowercase":
                target_list = self.EXTENDED_CYRILLIC_LOWERCASE
            elif section == "Numbers":
                target_list = self.BASIC_NUMBERS
            elif section == "Punctuation":
                target_list = self.PUNCTUATION_GLYPHS
            elif section == "Symbols":
                target_list = self.SYMBOLS_GLYPHS
            else:
                target_list = []
        
        # First get all valid glyphs
        valid_glyphs = []
        for glyph_name in target_list:
            if glyph_name in font.glyphs and self.is_base_glyph(font.glyphs[glyph_name]):
                valid_glyphs.append(glyph_name)
        
        # THEN apply group filter if enabled
        if use_groups:
            out = self.filter_unique_by_groups(font, valid_glyphs)
        else:
            out = valid_glyphs
        
        return sorted(set(out))

    # --- NEW FUNCTION: Contextual prefixes and suffixes as internal util ---
    def _getContextualSuffixes(self, left_glyph_name, right_glyph_name):
        """
        Internal helper that returns (prefix, suffix) according to glyph types.
        Uses Glyphs' category and subCategory fields when available.
        """
        font = Glyphs.font

        # Helper: robust classification
        def classify(name):
            if not name:
                return "uppercase"
            g = font.glyphs[name] if name in font.glyphs else None

            # Primary: Glyphs internal category/subCategory
            if g:
                cat = g.category or ""
                sub = g.subCategory or ""

                if "Smallcaps" in sub or ".sc" in name:
                    return "smallcap"
                if "Lowercase" in sub or sub == "Lower":
                    return "lowercase"
                if "Uppercase" in sub or sub == "Upper":
                    return "uppercase"
                if cat == "Number":
                    return "number"
                if cat in ("Punctuation", "Symbol"):
                    return "symbol"

            # Fallbacks by name
            n = name.lower()
            if ".sc" in n:
                return "smallcap"
            if any(num in n for num in ["zero","one","two","three","four","five","six","seven","eight","nine"]):
                return "number"
            if any(p in n for p in ["comma","period","hyphen","dash","colon","semicolon","paren","bracket","quote","question","exclam","slash","backslash"]):
                return "symbol"
            if name[0].islower():
                return "lowercase"
            if name[0].isupper():
                return "uppercase"
            return "symbol"

        # Get both sides' types
        left_type = classify(left_glyph_name)
        right_type = classify(right_glyph_name)

        # Assign contextual codes
        prefix = "HHOH" if left_type in ("uppercase","number","symbol") else "hhoh"
        suffix = "HOOH" if right_type in ("uppercase","number","symbol") else "hooh"

        return prefix, suffix

    # --- CORRECTED FUNCTION: Get symmetric trios for glyph - ALWAYS VISIBLE ---
    def get_symmetric_trios_for_glyph(self, base_name, master_id):
        """Get symmetric trios that include the specified base glyph - ALWAYS VISIBLE"""
        font = Glyphs.font
        base_disp = self.format_glyph_display(base_name)
        if not base_disp:
            return []
        
        # Remove slash if present for matching
        base_char = base_disp.strip('/')
        
        # Determine if base glyph is uppercase or lowercase
        base_is_upper = self.is_uppercase_glyph(base_name)
        
        symmetric_trios = []
        
        for trio in self.SYMMETRIC_TRIOS:
            # Check if base character is in this trio
            if base_char in trio:
                # Check case consistency: all characters in trio should be same case
                all_upper = trio.isupper()
                all_lower = trio.islower()
                
                # Skip if mixed case or doesn't match base glyph case
                if not all_upper and not all_lower:
                    continue
                    
                if base_is_upper and not all_upper:
                    continue
                    
                if not base_is_upper and not all_lower:
                    continue
                
                # Check if all glyphs in the trio exist in the font
                glyphs_exist = True
                trio_glyphs = []
                
                for char in trio:
                    char_found = False
                    for g in font.glyphs:
                        g_disp = self.format_glyph_display(g.name)
                        if g_disp == char:
                            trio_glyphs.append(g.name)
                            char_found = True
                            break
                    if not char_found:
                        glyphs_exist = False
                        break
            
                # MODIFICACIÓN PRINCIPAL: Siempre incluir el trio si todos los glifos existen
                # Eliminamos la verificación de kerning existente
                if glyphs_exist and len(trio_glyphs) == 3:
                    # Get contextual prefix/suffix for the entire trio
                    first_glyph = trio_glyphs[0]
                    last_glyph = trio_glyphs[2]
                    prefix, suffix = self._getContextualSuffixes(first_glyph, last_glyph)
                    symmetric_trios.append(f"{prefix}{trio}{suffix}")
    
        return symmetric_trios

    # ===========================================================
    # LIST ALL PAIRS TAB - SILENT VERSION
    # ===========================================================
    def buildListAllPairsTab(self):
        tab = self.w.tabs[1]
        
        tab.pairsLabel = TextBox((15, 15, 100, 20), "Pairs per tab:")
        tab.pairsInput = EditText((120, 10, 60, 24), "50")
        
        tab.sizeLabel = TextBox((15, 45, 100, 20), "Text size:")
        tab.sizeInput = EditText((120, 40, 60, 24), "40")
        
        tab.generateButton = Button((15, 75, 150, 32), "Generate All Kern Pairs", callback=self.generateListAllPairs)
        
        # Remove the TextEditor that shows debug messages to make it silent
        # tab.results = TextEditor((15, 120, -15, -15), "", readOnly=True)

    def generateListAllPairs(self, sender):
        try:
            # Silent version - no logging
            self.generateListAllPairsTabs()
        except Exception as e:
            # Only show error message if something goes wrong
            Message("Error", f"An error occurred: {e}")

    # Remove the listAllPairsLog method to eliminate debug messages
    # def listAllPairsLog(self, msg):
    #     tab = self.w.tabs[1]
    #     current_text = tab.results.get()
    #     tab.results.set(current_text + msg + "\n")
    #     print(msg)

    def auto_assign_kerning_groups(self):
        # Automatically assign kerning groups to glyphs that need them
        font = Glyphs.font
        if not font:
            return False
            
        master_id = font.selectedFontMaster.id
        kerning_dict = font.kerning[master_id]
        glyphs_needing_groups = set()
        
        if kerning_dict:
            for left_key, right_dict in kerning_dict.items():
                for right_key, kerning_value in right_dict.items():
                    if kerning_value is not None:
                        if (isinstance(left_key, str) and left_key.startswith('@MMK_L_') and
                            isinstance(right_key, str) and not right_key.startswith('@MMK_') and
                            right_key in font.glyphs):
                                glyphs_needing_groups.add((right_key, 'R'))
                        
                        if (isinstance(right_key, str) and right_key.startswith('@MMK_R_') and
                            isinstance(left_key, str) and not left_key.startswith('@MMK_') and
                            left_key in font.glyphs):
                                glyphs_needing_groups.add((left_key, 'L'))
        
        for glyph in font.glyphs:
            if not glyph.leftKerningGroup:
                glyphs_needing_groups.add((glyph.name, 'L'))
            if not glyph.rightKerningGroup:
                glyphs_needing_groups.add((glyph.name, 'R'))
        
        for glyph_name, side in glyphs_needing_groups:
            if glyph_name not in font.glyphs:
                continue
            glyph = font.glyphs[glyph_name]
            if side == 'L' and not glyph.leftKerningGroup:
                glyph.leftKerningGroup = f"@MMK_L_{glyph_name}"
            elif side == 'R' and not glyph.rightKerningGroup:
                glyph.rightKerningGroup = f"@MMK_R_{glyph_name}"
        return True
    
    def get_glyph_case_type(self, glyph_name):
        # Determine the case type of a glyph (uppercase, lowercase, smallcaps, etc.)
        font = Glyphs.font
        if glyph_name not in font.glyphs:
            return "unknown"
        g = font.glyphs[glyph_name]
        if glyph_name.endswith('.sc') or '.sc.' in glyph_name:
            return "smallcaps"
        if glyph_name in ['zero','one','two','three','four','five','six','seven','eight','nine']:
            return "number"
        punctuation_glyphs = ['period','comma','colon','semicolon','exclam','question','quotedbl','quoteleft','quoteright']
        if glyph_name in punctuation_glyphs:
            return "punctuation"
        symbol_glyphs = ['plus','minus','equal','less','greater','dollar','cent','sterling','yen','euro']
        if glyph_name in symbol_glyphs:
            return "symbols"
        if hasattr(g,'unicode') and g.unicode:
            try:
                char = chr(int(g.unicode,16))
                if char.isupper(): return "uppercase"
                elif char.islower(): return "lowercase"
                elif char.isdigit(): return "number"
            except: pass
        if glyph_name.isupper(): return "uppercase"
        elif glyph_name.islower(): return "lowercase"
        return "unknown"
    
    def format_glyph_name(self, glyph_name): 
        return f"/{glyph_name}"
    
    def get_prefix_suffix_for_pair(self, left_glyph, right_glyph):
        # Get prefix and suffix strings based on glyph case types for proper display
        left_type = self.get_glyph_case_type(left_glyph)
        right_type = self.get_glyph_case_type(right_glyph)
        
        if left_type in ["uppercase","number"]: 
            prefix = "/H/H/O/H"
        elif left_type == "lowercase": 
            prefix = "/h/h/o/h"
        elif left_type == "smallcaps": 
            prefix = "/h.sc/h.sc/o.sc/h.sc"
        else: 
            prefix = "/H/H/O/H"
            
        if right_type in ["uppercase","number"]: 
            suffix = "/H/O/O/H"
        elif right_type == "lowercase": 
            suffix = "/h/o/o/h"
        elif right_type == "smallcaps": 
            suffix = "/h.sc/o.sc/o.sc/h.sc"
        else: 
            suffix = "/H/O/O/H"
            
        return prefix, suffix
    
    def format_glyph_for_display(self, glyph_name): 
        return self.format_glyph_name(glyph_name)
    
    def build_kern_display(self, left_glyph, right_glyph):
        # Build the display string for a kern pair with proper prefix and suffix
        left_display = self.format_glyph_for_display(left_glyph)
        right_display = self.format_glyph_for_display(right_glyph)
        prefix, suffix = self.get_prefix_suffix_for_pair(left_glyph, right_glyph)
        return f"{prefix}{left_display}{right_display}{suffix}"
    
    def get_all_kern_pairs(self, master_id):
        # Get all kerning pairs from the current master
        font = Glyphs.font
        all_pairs = []
        kerning_dict = font.kerning[master_id]
        if not kerning_dict: 
            return all_pairs
            
        for left_key, right_dict in kerning_dict.items():
            for right_key, kerning_value in right_dict.items():
                if kerning_value is not None:
                    all_pairs.append({
                        'left_key': left_key,
                        'right_key': right_key, 
                        'value': kerning_value
                    })
        return all_pairs
    
    def get_glyph_name_by_id(self, glyph_id):
        # Get glyph name from glyph ID
        font = Glyphs.font
        if isinstance(glyph_id, str) and len(glyph_id) == 36:
            for glyph in font.glyphs:
                if glyph.id == glyph_id: 
                    return glyph.name
        return None

    def find_glyph_for_group(self, group_name, target_side):
        """
        Find a glyph that has the specified group on the specified side
        group_name: group name without prefix (e.g., 'acir', 'bcir', 'tcir')
        target_side: 'L' for left, 'R' for right
        """
        font = Glyphs.font
        found_glyphs = []
        
        for g in font.glyphs:
            left_group = g.leftKerningGroup or ""
            right_group = g.rightKerningGroup or ""
            
            if target_side == 'L':
                # Search in left groups (compare with and without prefix)
                if (left_group == group_name or 
                    left_group == f"@MMK_L_{group_name}" or
                    left_group.endswith(f"_{group_name}")):
                    found_glyphs.append(g.name)
            elif target_side == 'R':
                # Search in right groups (compare with and without prefix)
                if (right_group == group_name or 
                    right_group == f"@MMK_R_{group_name}" or
                    right_group.endswith(f"_{group_name}")):
                    found_glyphs.append(g.name)
        
        return found_glyphs

    def get_all_convertible_pairs(self, master_id):
        # Convert all kerning pairs to displayable format with glyph names
        font = Glyphs.font
        convertible_pairs = []
        all_pairs = self.get_all_kern_pairs(master_id)
        name_fixes = {
            "a-sc": "a.sc",
            "hypen": "hyphen", 
            "guillemotright": "guillemetright", 
            "guillemotleft": "guillemetleft"
        }
        
        for pair in all_pairs:
            left_key = pair['left_key']
            right_key = pair['right_key']
            kerning_value = pair['value']
            
            # Apply name corrections
            for wrong, correct in name_fixes.items():
                if isinstance(left_key, str):
                    left_key = left_key.replace(wrong, correct)
                if isinstance(right_key, str):
                    right_key = right_key.replace(wrong, correct)
            
            left_glyph = None
            right_glyph = None
            
            # Process left_key
            if isinstance(left_key, str):
                if left_key.startswith('@MMK_L_'):
                    group_name = left_key[7:]  # Extract group name without '@MMK_L_'
                    left_glyph = group_name
                    
                    # Find representative glyph for left group
                    if group_name in ["acir", "bcir", "tcir", "cometes"]:
                        # For a left group, we look for glyphs that have this group on the RIGHT side
                        found_glyphs = self.find_glyph_for_group(group_name, 'R')
                        if found_glyphs:
                            # Use the first found glyph as representative
                            left_glyph = found_glyphs[0]
                    
                elif left_key in font.glyphs:
                    left_glyph = left_key
                else:
                    gname = self.get_glyph_name_by_id(left_key)
                    left_glyph = gname if gname else left_key
            
            # Process right_key  
            if isinstance(right_key, str):
                if right_key.startswith('@MMK_R_'):
                    group_name = right_key[7:]  # Extract group name without '@MMK_R_'
                    right_glyph = group_name
                    
                    # Find representative glyph for right group
                    if group_name in ["acir", "bcir", "tcir", "cometes"]:
                        # For a right group, we look for glyphs that have this group on the LEFT side
                        found_glyphs = self.find_glyph_for_group(group_name, 'L')
                        if found_glyphs:
                            # Use the first found glyph as representative
                            right_glyph = found_glyphs[0]
                    
                elif right_key in font.glyphs:
                    right_glyph = right_key
                else:
                    gname = self.get_glyph_name_by_id(right_key)
                    right_glyph = gname if gname else right_key

            if not left_glyph:
                left_glyph = left_key
            if not right_glyph:
                right_glyph = right_key
                
            if left_glyph and right_glyph:
                left_exists = left_glyph in font.glyphs
                right_exists = right_glyph in font.glyphs
                status = 'VALID' if (left_exists and right_exists) else ('PARTIAL' if left_exists or right_exists else 'MISSING')
                convertible_pairs.append({
                    'left': left_glyph, 
                    'right': right_glyph, 
                    'value': kerning_value, 
                    'status': status, 
                    'left_raw': left_key, 
                    'right_raw': right_key
                })
        
        return convertible_pairs
    
    def sort_kern_pairs(self, pairs):
        # Sort kerning pairs by case type for better organization
        def get_sort_key(pair):
            lt = self.get_glyph_case_type(pair['left'])
            rt = self.get_glyph_case_type(pair['right'])
            order = {
                ("uppercase", "uppercase"): 1,
                ("lowercase", "lowercase"): 4
            }
            return (order.get((lt, rt), 99), pair['left'], pair['right'])
        return sorted(pairs, key=get_sort_key)
    
    def create_tabs_for_category(self, pairs, category_name, pairs_per_tab, text_size):
        # Create tabs for a category of kerning pairs
        font = Glyphs.font
        if not pairs: 
            return 0
            
        sorted_pairs = self.sort_kern_pairs(pairs)
        total_tabs = (len(sorted_pairs) + pairs_per_tab - 1) // pairs_per_tab
        
        for t in range(total_tabs):
            start = t * pairs_per_tab
            end = min(start + pairs_per_tab, len(sorted_pairs))
            tab_pairs = sorted_pairs[start:end]
            tab_lines = [
                f"# {category_name} Kern Pairs {start+1}-{end} of {len(sorted_pairs)}",
                ""
            ]
            
            for p in tab_pairs:
                display = self.build_kern_display(p['left'], p['right'])
                if category_name == "PARTIAL":
                    line = f"{display}               {int(p['value'])}    [{p['left_raw']} ; {p['right_raw']}]"
                else:
                    line = f"{display}               {int(p['value'])}"
                tab_lines.append(line)
                
            tab_content = "\n".join(tab_lines)
            tab = font.newTab(tab_content)
            try: 
                tab.textView().setFontSize_(text_size)
            except: 
                pass
                
        return total_tabs
    
    def generateListAllPairsTabs(self):
        # Main function to generate all kern pair tabs - SILENT VERSION
        font = Glyphs.font
        if not font: 
            Message("Error", "No font open", OKButton="OK")
            return
            
        try:
            pairs_per_tab = int(self.w.tabs[1].pairsInput.get())
            text_size = int(self.w.tabs[1].sizeInput.get())
        except:
            pairs_per_tab = 50
            text_size = 40
            
        master_id = font.selectedFontMaster.id
        
        # Silent execution - no logging
        self.auto_assign_kerning_groups()
        all_pairs = self.get_all_convertible_pairs(master_id)
        
        if not all_pairs:
            Message("No Kern Pairs", "No kerning pairs found in the font")
            return
            
        valid = [p for p in all_pairs if p['status'] == "VALID"]
        partial = [p for p in all_pairs if p['status'] == "PARTIAL"]
        missing = [p for p in all_pairs if p['status'] == "MISSING"]
        
        # Create tabs silently
        vt = self.create_tabs_for_category(valid, "VALID", pairs_per_tab, text_size)
        pt = self.create_tabs_for_category(partial, "PARTIAL", pairs_per_tab, text_size - 5)
        mt = self.create_tabs_for_category(missing, "MISSING", pairs_per_tab, text_size - 10)
        
        summary_parts = []
        if vt: summary_parts.append(f"{vt} VALID tabs ({len(valid)} pairs)")
        if pt: summary_parts.append(f"{pt} PARTIAL tabs ({len(partial)} pairs)")
        if mt: summary_parts.append(f"{mt} MISSING tabs ({len(missing)} pairs)")
        
        summary = " + ".join(summary_parts)
        
        # Only show success message if tabs were created
        if summary_parts:
            Message("Success", f"Created: {summary}")

    # ===================================================
    # TAB 3 — LIST PAIRS (TURBO OPTIMIZED)
    # ===================================================
    def buildListPairsTab(self):
        tab = self.w.tabs[2]

        # TURBO: Compact button layout
        tab.showBtn = Button((10, 10, 80, 24), "Show", callback=self.showSelected)
        tab.refreshBtn = Button((100, 10, 80, 24), "Refresh", callback=self.refreshList)

        # TURBO: Fast search with caching
        tab.search = EditText((10, 45, 250, 24), placeholder="Search… A, = exact", callback=self.filterList)
        tab.clearSearch = Button((270, 45, 80, 24), "Clear", callback=self.clearSearch)

        # TURBO: High-performance list with pre-sorted data
        tab.list = List(
            (10, 80, 350, -20), [],
            columnDescriptions=[
                {"title": "Left", "width": 130},
                {"title": "Right", "width": 130}, 
                {"title": "Value", "width": 60},
            ],
            allowsMultipleSelection=True,
            enableTypingSensitivity=False,  # TURBO: Disable auto-sort for speed
            selectionCallback=self.showSelected
        )

        # TURBO: Group manager with cached data
        tab.groups = Tabs((380, 10, -10, -80), ["Left Group", "Right Group"])
        tab.groups[0].list = List((10, 10, -10, -10), [])
        tab.groups[1].list = List((10, 10, -10, -10), [])

        # TURBO: Action buttons
        tab.makeFirst = Button((380, -65, 120, 24), "Make First", callback=self.makeFirst)
        tab.applyOrder = Button((510, -65, 120, 24), "Apply Order", callback=self.applyOrder)
        tab.refreshGroupsBtn = Button((640, -65, 100, 24), "Refresh", callback=self.refreshGroups)

        # TURBO: Data caching for performance
        self._allPairs = []
        self._currentDisplayPairs = []
        self._kerningCache = {}  # Cache for kerning data
        self._keyCache = {}  # Cache for key resolution
        self._productionCache = {}  # Cache for production names
        self._graphicalCache = {}  # Cache for graphical representations
        self._groupCache = {}  # Cache for group data

    # ===================================================
    # GROUP MANAGER (TURBO OPTIMIZED)
    # ===================================================
    def get_group_glyphs(self, group, side):
        """TURBO: Fast group member retrieval with caching"""
        font = Glyphs.font
        if not font or not group:
            return []
        
        # TURBO: Check cache first
        cache_key = f"{group}_{side}"
        if cache_key in self._groupCache:
            return self._groupCache[cache_key]
        
        # TURBO: Get custom order from userData
        key = f"kernOrder_{side}"
        custom_order = font.userData.get(key, {}).get(group, [])
        
        # TURBO: Fast glyph collection
        glyph_names = [g.name for g in font.glyphs if getattr(g, side + "KerningGroup") == group]
        
        # TURBO: Apply custom order if exists
        if custom_order:
            valid_order = [name for name in custom_order if name in glyph_names]
            remaining = [name for name in glyph_names if name not in valid_order]
            glyph_names = valid_order + sorted(remaining)
        else:
            glyph_names = sorted(glyph_names)  # TURBO: Default alphabetical
        
        # TURBO: Format with trophy emoji for leader
        formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyph_names)]
        
        # TURBO: Cache result
        self._groupCache[cache_key] = formatted
        
        return formatted

    def active_group_tab(self):
        """TURBO: Fast active tab detection"""
        tab_index = self.w.tabs[2].groups.get()
        font = Glyphs.font
        if not font or not font.selectedLayers:
            return None, None, None
            
        glyph = font.selectedLayers[0].parent
        if tab_index == 0:
            return "left", glyph.leftKerningGroup, self.w.tabs[2].groups[0].list
        else:
            return "right", glyph.rightKerningGroup, self.w.tabs[2].groups[1].list

    def refreshGroups(self, sender=None):
        """TURBO: Fast group list refresh"""
        font = Glyphs.font
        if not font or not font.selectedLayers:
            self.showNoGlyphSelected()
            return
            
        glyph = font.selectedLayers[0].parent
        
        # TURBO: Parallel group processing
        leftGroup = glyph.leftKerningGroup
        rightGroup = glyph.rightKerningGroup
        
        if leftGroup:
            self.w.tabs[2].groups[0].list.set(self.get_group_glyphs(leftGroup, "left"))
        else:
            self.w.tabs[2].groups[0].list.set(["No left group"])
            
        if rightGroup:
            self.w.tabs[2].groups[1].list.set(self.get_group_glyphs(rightGroup, "right"))
        else:
            self.w.tabs[2].groups[1].list.set(["No right group"])

    def makeFirst(self, sender):
        """TURBO: Fast reordering with confirmation"""
        side, group, listView = self.active_group_tab()
        if not group:
            Message(f"No {side} group for selected glyph")
            return

        sel = listView.getSelection()
        if not sel:
            Message("No glyph selected in group list")
            return

        selected_name = listView[sel[0]].replace("🏆", "").strip()
        
        # TURBO: Quick confirmation
        if not askYesNo(f"Set '{selected_name}' as first glyph for {side} group '{group}'?"):
            return

        # TURBO: Fast list reordering
        glyphs = [n.replace("🏆", "").strip() for n in listView]
        glyphs.remove(selected_name)
        glyphs.insert(0, selected_name)
        formatted = [f"🏆 {n}" if i == 0 else f"  {n}" for i, n in enumerate(glyphs)]
        listView.set(formatted)

        Message(f"'{selected_name}' is now first in {side} group")

    def applyOrder(self, sender):
        """TURBO: Fast order application"""
        side, group, listView = self.active_group_tab()
        if not group:
            Message(f"No {side} group for selected glyph")
            return

        order = [n.replace("🏆", "").strip() for n in listView]
        font = Glyphs.font
        key = f"kernOrder_{side}"
        
        # TURBO: Efficient userData update
        if not font.userData.get(key):
            font.userData[key] = {}
        font.userData[key][group] = order

        # TURBO: Clear cache to force refresh
        cache_key = f"{group}_{side}"
        if cache_key in self._groupCache:
            del self._groupCache[cache_key]

        Message(f"Order applied to {side} group '{group}'")

    def showNoGlyphSelected(self):
        """TURBO: Quick no-selection display"""
        self.w.tabs[2].groups[0].list.set(["Select a glyph"])
        self.w.tabs[2].groups[1].list.set(["Select a glyph"])

    # ===================================================
    # KERNING PAIRS PROCESSING (TURBO OPTIMIZED)
    # ===================================================
    def resolveKey(self, key):
        """TURBO: Fast key resolution with caching"""
        font = Glyphs.font
        if not font:
            return str(key)

        if not isinstance(key, str):
            return str(key)

        # TURBO: Cache for frequently resolved keys
        if key in self._keyCache:
            return self._keyCache[key]

        result = key
        
        # TURBO: Fast pattern matching
        if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
            result = key.split("_", 2)[-1]
        elif key.startswith("@") and "_" not in key:
            result = key[1:]
        elif len(key) == 36 and key.count("-") == 4:  # UUID
            g = font.glyphForId_(key)
            if g:
                result = g.name

        # TURBO: Cache result
        self._keyCache[key] = result
        
        return result

    def charToProductionName(self, char_or_name):
        """TURBO: Fast character to production name conversion"""
        font = Glyphs.font
        if not font:
            return char_or_name
            
        # TURBO: Cache for production names
        if char_or_name in self._productionCache:
            return self._productionCache[char_or_name]
            
        result = char_or_name
        
        # TURBO: Quick font glyph check
        if char_or_name in font.glyphs:
            result = char_or_name
        else:
            # TURBO: Fast unicode lookup
            for glyph in font.glyphs:
                if glyph.unicode:
                    try:
                        if chr(int(glyph.unicode, 16)) == char_or_name:
                            result = glyph.name
                            break
                    except:
                        continue
            
            # TURBO: Common character mapping
            char_map = {
                '7': 'seven', '@': 'at', '&': 'ampersand', '#': 'numbersign',
                '$': 'dollar', '%': 'percent', '*': 'asterisk', '+': 'plus',
                '-': 'hyphen', '=': 'equal', '<': 'less', '>': 'greater',
                '?': 'question', '!': 'exclam', '"': 'quotedbl', "'": 'quotesingle',
                '(': 'parenleft', ')': 'parenright', '[': 'bracketleft',
                ']': 'bracketright', '{': 'braceleft', '}': 'braceright',
                '/': 'slash', '\\': 'backslash', '|': 'bar', ':': 'colon',
                ';': 'semicolon', ',': 'comma', '.': 'period'
            }
            result = char_map.get(char_or_name, result)

        # TURBO: Cache result
        self._productionCache[char_or_name] = result
        
        return result

    def nameToGraphicalRepresentation(self, name):
        """TURBO: Convert production name to graphical character for display"""
        font = Glyphs.font
        if not font:
            return name
            
        # TURBO: Cache for graphical representations
        if name in self._graphicalCache:
            return self._graphicalCache[name]
            
        result = name
        
        # TURBO: Check if it's a production name that should be shown as character
        production_to_char = {
            'seven': '7', 'at': '@', 'ampersand': '&', 'numbersign': '#',
            'dollar': '$', 'percent': '%', 'asterisk': '*', 'plus': '+',
            'hyphen': '-', 'equal': '=', 'less': '<', 'greater': '>',
            'question': '?', 'exclam': '!', 'quotedbl': '"', 'quotesingle': "'",
            'parenleft': '(', 'parenright': ')', 'bracketleft': '[',
            'bracketright': ']', 'braceleft': '{', 'braceright': '}',
            'slash': '/', 'backslash': '\\', 'bar': '|', 'colon': ':',
            'semicolon': ';', 'comma': ',', 'period': '.'
        }
        
        # TURBO: Convert production name to character if possible
        if name in production_to_char:
            result = production_to_char[name]
        else:
            # TURBO: Try to get unicode character for other glyphs
            if name in font.glyphs:
                g = font.glyphs[name]
                if g.unicode:
                    try:
                        result = chr(int(g.unicode, 16))
                    except:
                        pass

        # TURBO: Cache result
        self._graphicalCache[name] = result
        
        return result

    def scriptOrder(self, ch):
        """TURBO: Fast script-based ordering"""
        if not ch:
            return (9, ch)
        
        try:
            cp = ord(ch[0])
        except:
            return (9, ch)

        # TURBO: Quick unicode range checks
        if 0x0041 <= cp <= 0x024F: return (0, ch)  # Latin
        if 0x0370 <= cp <= 0x03FF: return (1, ch)  # Greek  
        if 0x0400 <= cp <= 0x052F: return (2, ch)  # Cyrillic
        return (3, ch)  # Other

    def contextualDisplay(self, L, R, val):
        """TURBO: Fast contextual string generation - USES PRODUCTION NAMES FOR TAB"""
        # For the tab, always use production names
        L_prod = self.charToProductionName(L)
        R_prod = self.charToProductionName(R)
        
        # TURBO: Quick case detection
        pL = "/h/h/o/h" if L.lower() == L else "/H/H/O/H"
        pR = "/h/o/o/h" if R.lower() == R else "/H/O/O/H"
        
        return f"{pL}/{L_prod}/{R_prod}{pR}                            {val}"

    def refreshList(self, sender):
        """TURBO: High-performance list refresh - SHOWS GRAPHICAL REPRESENTATION"""
        font = Glyphs.font
        if not font:
            return
            
        mid = font.selectedFontMaster.id
        
        # TURBO: Cache kerning data
        if mid in self._kerningCache:
            kerning = self._kerningCache[mid]
        else:
            kerning = font.kerning.get(mid, {})
            self._kerningCache[mid] = kerning

        rows = []
        seen = set()

        # TURBO: Optimized kerning processing
        for LK, rightDict in kerning.items():
            for RK, val in rightDict.items():
                try:
                    val_int = int(val)
                except (TypeError, ValueError):
                    continue

                # TURBO: Fast key resolution
                L0 = self.resolveKey(LK)
                R0 = self.resolveKey(RK)

                # TURBO: Convert to production names for internal processing
                L_prod = self.charToProductionName(L0)
                R_prod = self.charToProductionName(R0)

                # TURBO: Convert to graphical representation for DISPLAY
                L_display = self.nameToGraphicalRepresentation(L_prod)
                R_display = self.nameToGraphicalRepresentation(R_prod)

                uniq = (L_prod, R_prod, val_int)  # Use production names for uniqueness
                if uniq in seen:
                    continue
                seen.add(uniq)

                rows.append({
                    "Left": L_display,  # SHOW GRAPHICAL CHARACTER
                    "Right": R_display, # SHOW GRAPHICAL CHARACTER
                    "Value": val_int,
                    "_display": self.contextualDisplay(L0, R0, val_int),  # Uses production names for tab
                    "_scriptL": self.scriptOrder(L_display),  # Sort by graphical representation
                    "_scriptR": self.scriptOrder(R_display),  # Sort by graphical representation
                    "_originalLeft": L0,
                    "_originalRight": R0,
                    "_productionLeft": L_prod,  # Store production name for tab generation
                    "_productionRight": R_prod, # Store production name for tab generation
                    "_sortValue": val_int,
                })

        # TURBO: Fast sorting with script blocks
        rows.sort(key=lambda r: (r["_scriptL"][0], r["_scriptR"][0], r["Left"], r["Right"]))

        # TURBO: Efficient separator insertion
        final = []
        lastBlock = None
        for r in rows:
            blk = r["_scriptL"][0]
            if lastBlock is not None and blk != lastBlock:
                final.append({"Left": "────", "Right": "────", "Value": "──", "_isSeparator": True})
            final.append({
                "Left": r["Left"],      # Graphical character for display
                "Right": r["Right"],    # Graphical character for display
                "Value": str(r["Value"]),
                "_originalData": r      # Contains production names for tab
            })
            lastBlock = blk

        self._allPairs = final
        self._currentDisplayPairs = final
        self.w.tabs[2].list.set(final)

    # ===================================================
    # SEARCH & FILTERING (TURBO OPTIMIZED)
    # ===================================================
    def clearSearch(self, sender):
        """TURBO: Instant search clear"""
        self.w.tabs[2].search.set("")
        self.w.tabs[2].list.set(self._allPairs)
        self._currentDisplayPairs = self._allPairs

    def filterList(self, sender):
        """TURBO: Fast search filtering - SEARCHES BOTH GRAPHICAL AND PRODUCTION NAMES"""
        q = sender.get().strip()
        if not q:
            self.clearSearch(None)
            return

        # TURBO: Quick exact match detection
        if q.endswith(","):
            exact = q[:-1].strip()
            filtered = [r for r in self._allPairs if r["Left"] == exact or r["Right"] == exact]
        else:
            # TURBO: Fast substring search in BOTH graphical and production names
            ql = q.lower()
            filtered = []
            for r in self._allPairs:
                original_data = r.get("_originalData", {})
                # Search in displayed graphical characters
                if (ql in r["Left"].lower() or 
                    ql in r["Right"].lower() or 
                    ql in str(r["Value"]) or
                    # Also search in production names for better searchability
                    ql in original_data.get("_productionLeft", "").lower() or
                    ql in original_data.get("_productionRight", "").lower()):
                    filtered.append(r)

        self.w.tabs[2].list.set(filtered)
        self._currentDisplayPairs = filtered

    def showSelected(self, sender):
        """TURBO: Fast selection display - USES PRODUCTION NAMES FOR TAB"""
        tab = self.w.tabs[2]
        rows = self._currentDisplayPairs
        sel = tab.list.getSelection()

        if not sel:
            return

        try:
            lines = []
            for i in sel:
                if i < len(rows):
                    row = rows[i]
                    if row.get("Left") == "────" and row.get("Right") == "────":
                        continue
                    
                    original_data = row.get("_originalData", row)
                    
                    # TURBO: Use PRODUCTION NAMES for tab generation, not graphical display
                    left = original_data.get("_productionLeft", row["Left"])
                    right = original_data.get("_productionRight", row["Right"])
                    value = original_data.get("Value", row["Value"])
                    
                    lines.append(self.contextualDisplay(left, right, value))
            
            if lines:
                Glyphs.font.newTab("\n".join(lines))
        except Exception as e:
            print(f"TURBO Error: {e}")
            Message("Error showing selection")

    # ===================================================
    # TAB 4 — COLLISION DETECTOR (TURBO OPTIMIZED)
    # ===================================================
    def buildFindCollisionsTab(self):
        """Fast collision detector setup"""
        tab = self.w.tabs[3]
        
        tab.title = TextBox((20, 20, -20, 20), "Collision Detector")
        tab.glyphLabel = TextBox((20, 50, 80, 20), "Glyphs:")
        tab.glyphField = EditText((90, 45, 200, 25), "i")
        tab.tolLabel = TextBox((20, 85, 80, 20), "Tolerance:")
        tab.tolField = EditText((90, 80, 60, 25), "40")
        tab.checkBtn = Button((170, 80, 100, 25), "Check", callback=self.checkCollisions)
        tab.out = TextEditor((20, 120, -20, -20), "")

    # TURBO: Optimized geometry functions
    def distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def minDistanceBetweenSegments(self, a1, a2, b1, b2):
        def clamp(x, a, b): return max(a, min(b, x))
        A, B = (a1.x, a1.y), (a2.x, a2.y)
        C, D = (b1.x, b1.y), (b2.x, b2.y)
        
        def closestPoint(P, Q, R):
            vx, vy = Q[0]-P[0], Q[1]-P[1]
            denom = vx*vx + vy*vy
            if denom == 0: return P
            t = ((R[0]-P[0])*vx + (R[1]-P[1])*vy) / denom
            return (P[0] + clamp(t, 0, 1)*vx, P[1] + clamp(t, 0, 1)*vy)
            
        dmin = float("inf")
        for p in (A, B):
            dmin = min(dmin, self.distance(p, closestPoint(C, D, p)))
        for p in (C, D):
            dmin = min(dmin, self.distance(p, closestPoint(A, B, p)))
        return dmin

    def getSegments(self, layer):
        """TURBO: Fast segment extraction"""
        segs = []
        for p in layer.paths:
            nodes = p.nodes
            if not nodes: continue
            count = len(nodes)
            for i in range(count):
                n1 = nodes[i]
                if p.closed:
                    n2 = nodes[(i+1) % count]
                elif i+1 < count:
                    n2 = nodes[i+1]
                else:
                    continue
                segs.append((n1, n2))
        return segs

    def bbox(self, layer):
        b = layer.bounds
        return (b.origin.x, b.origin.y, b.origin.x+b.size.width, b.origin.y+b.size.height)

    def boxesAreClose(self, b1, b2, margin):
        return not (b1[2] + margin < b2[0] or b2[2] + margin < b1[0] or 
                   b1[3] + margin < b2[1] or b2[3] + margin < b1[1])

    def layersAreClose(self, layer1, layer2, dx, margin):
        """TURBO: Fast collision detection"""
        segs1 = self.getSegments(layer1)
        shifted = [(type("P", (), {"x": n1.x+dx, "y": n1.y}),
                    type("P", (), {"x": n2.x+dx, "y": n2.y}))
                  for n1, n2 in self.getSegments(layer2)]
                  
        for s1 in segs1:
            for s2 in shifted:
                if self.minDistanceBetweenSegments(s1[0], s1[1], s2[0], s2[1]) < margin:
                    return True
        return False

    def glyphType(self, g):
        """TURBO: Fast glyph type detection"""
        if not g: return "lower"
        if g.category == "Number": return "number"
        if g.category in ("Punctuation", "Symbol"): return "symbol"
        if ".sc" in g.name: return "lower"
        if g.name[0].isupper(): return "upper"
        if g.name[0].islower(): return "lower"
        return "symbol"

    def contextualPrefixSuffix(self, l, r):
        """TURBO: Quick context generation"""
        lt, rt = self.glyphType(l), self.glyphType(r)
        if lt == "number" or rt == "number": return ("HHOH", "HOOH")
        if lt == "upper" and rt == "upper": return ("HHOH", "HOOH")
        if lt == "lower" and rt == "upper": return ("hhoh", "HOOH")
        if lt == "upper" and rt == "lower": return ("HHOH", "hooh")
        if lt == "lower" and rt == "lower": return ("hhoh", "hooh")
        return ("hhoh", "hooh")

    def checkCollisions(self, sender):
        """TURBO: High-performance collision detection"""
        font = Glyphs.font
        if not font:
            Message("No font open")
            return

        tab = self.w.tabs[3]
        names = [n.strip() for n in tab.glyphField.get().split(",") if n.strip()]
        try:
            margin = float(tab.tolField.get())
        except:
            margin = 15.0

        master = font.selectedFontMaster
        mid = master.id

        # TURBO: Fast glyph filtering
        allGlyphs = [g for g in font.glyphs if g.layers[mid] and (g.layers[mid].paths or g.layers[mid].components)]
        specified = [font.glyphs[n] for n in names if n in font.glyphs]
        
        results = []

        # TURBO: Optimized collision checking
        for left in specified:
            L = left.layers[mid]
            try:
                L = L.copyDecomposedLayer()
            except:
                pass
                
            for right in allGlyphs:
                if right == left: continue
                
                R = right.layers[mid]
                try:
                    R = R.copyDecomposedLayer()
                except:
                    pass

                if not self.boxesAreClose(self.bbox(L), self.bbox(R), margin):
                    continue

                if self.layersAreClose(L, R, L.width, margin):
                    pre, suf = self.contextualPrefixSuffix(left, right)
                    results.append((f"/{left.name}/{right.name}", pre, suf))

        # TURBO: Fast results processing
        if results:
            txt = "\n".join([f"{' '.join('/'+c for c in pre)} {pair} {' '.join('/'+c for c in suf)}" 
                           for pair, pre, suf in results])
            font.newTab(txt)
            tab.out.set(f"✅ {len(results)} collisions found!")
        else:
            tab.out.set("✅ No collisions detected")

    # ===========================================================
    #  KERN TO SC TAB - FIXED VERSION WITH COMPLETION MESSAGES
    # ===========================================================
    def buildKernToSCTab(self):
        tab = self.w.tabs[4]
    
        # Percentage UI
        tab.factorText = TextBox((15, 15, 100, 20), "Percentage:")
        tab.factorEdit = EditText((120, 12, 60, 22), "70")
        tab.percentText = TextBox((185, 15, 20, 20), "%")
    
        # Transfer Type with updated radio button
        tab.modeText = TextBox((15, 45, -15, 20), "Transfer Type:")
        tab.modeRadio = RadioGroup((15, 70, -15, 150),
            ["Uppercase → Uppercase (.sc) - FIXED", "Uppercase-Lowercase → SC (Group Aware)"], isVertical=True)
        tab.modeRadio.set(0)  # Default to the fixed uppercase method
    
        # Checkboxes
        tab.overwriteCheck = CheckBox((15, 230, -15, 20), "Overwrite existing", value=True)
        tab.debugCheck = CheckBox((15, 255, -15, 20), "Debug mode", value=False)
    
        tab.button = Button((15, 285, -15, 30), "Transfer Kerning", callback=self.transferKerning)
    
        # Log area
        tab.logText = TextEditor((15, 330, -15, -15), readOnly=True)
        
        

    def transferKerning(self, sender):
        """Callback for the button that executes kerning transfer"""
        try:
            font = Glyphs.font
            if not font:
                self.kernToSCLog("Error: No font open")
                return
            
            transfer_mode = self.w.tabs[4].modeRadio.get()
        
            if transfer_mode == 0:
                # FIXED Uppercase → Uppercase (.sc) method
                try:
                    percentage = float(self.w.tabs[4].factorEdit.get())
                    if percentage <= 0 or percentage > 200:
                        self.showResultsWindow("Error", "Percentage must be between 0.1 and 200!", is_error=True)
                        return
                    factor = percentage / 100.0
                except:
                    self.showResultsWindow("Error", "Please enter a valid percentage!", is_error=True)
                    return
            
                debug_mode = self.w.tabs[4].debugCheck.get()
                overwrite = self.w.tabs[4].overwriteCheck.get()
            
                self.kernToSCLog("Starting Uppercase→Uppercase SC transfer (FIXED)...")
                self.kernToSCLog(f"Percentage: {percentage}%, Factor: {factor}")
                self.kernToSCLog(f"Overwrite: {overwrite}, Debug: {debug_mode}")
            
                result = self.transfer_upper_to_upper_sc_fixed(font, factor, percentage, overwrite, debug_mode)
            
                # Show results window for fixed method
                if isinstance(result, dict) and 'created' in result and 'updated' in result:
                    self.showResultsWindow(
                        "Transfer Completed", 
                        f"Uppercase → Uppercase SC Transfer\n\n"
                        f"New pairs: {result['created']}\n"
                        f"Updated pairs: {result['updated']}\n"
                        f"Percentage applied: {percentage}%",
                        created=result['created'],
                        updated=result['updated'],
                        percentage=percentage
                    )
            
            else:
                # Uppercase-Lowercase → SC - USE GROUP AWARE FUNCTION
                try:
                    percentage = float(self.w.tabs[4].factorEdit.get())
                    if percentage <= 0 or percentage > 200:
                        self.showResultsWindow("Error", "Percentage must be between 0.1 and 200!", is_error=True)
                        return
                    factor = percentage / 100.0
                except:
                    self.showResultsWindow("Error", "Please enter a valid percentage!", is_error=True)
                    return
                
                overwrite = self.w.tabs[4].overwriteCheck.get()
                debug_mode = self.w.tabs[4].debugCheck.get()
            
                self.kernToSCLog("Starting kerning transfer (Uppercase-Lowercase to SC)...")
                self.kernToSCLog(f"Percentage: {percentage}%, Factor: {factor}, Overwrite: {overwrite}, Debug: {debug_mode}")
            
                # Use the GROUP AWARE function that gives 258 results
                result = self.transfer_upper_lower_bidirectional_sc(font, factor, overwrite, debug_mode)
            
                self.kernToSCLog(f"Kerning transfer completed. Total applied: {result}")
            
                # Show results window for group aware method
                self.showResultsWindow(
                    "Transfer Completed",
                    f"Uppercase-Lowercase → SC Transfer\n\n"
                    f"Total kerning pairs applied: {result}\n"
                    f"Percentage applied: {percentage}%",
                    created=result,
                    updated=0,
                    percentage=percentage
                )
            
        except Exception as e:
            self.kernToSCLog(f"Error: {str(e)}")
            import traceback
            self.kernToSCLog(traceback.format_exc())
            self.showResultsWindow("Error", f"An error occurred during transfer:\n{str(e)}", is_error=True)

    def showResultsWindow(self, title, message, created=0, updated=0, percentage=0, is_error=False):
        """Display a professional results window"""
        try:
            # Calculate window dimensions based on content
            lines = message.count('\n') + 1
            window_height = max(200, 150 + (lines * 15))
        
            # Create results window
            results_window = Window((400, window_height), title)
        
            # Header
            header_height = 60
            header = Group((0, 0, 400, header_height))
            if not is_error:
                header.setBackgroundColor_(0.2, 0.4, 0.8, 1.0)
            else:
                header.setBackgroundColor_(0.8, 0.3, 0.3, 1.0)
        
            header_text = TextBox((20, 20, 360, 30), title)
            header_text.setFont_(NSFont.boldSystemFontOfSize_(18))
            header_text.setTextColor_(NSColor.whiteColor())
        
            # Content area
            content_y = header_height + 10
            message_text = TextBox((20, content_y, 360, window_height - content_y - 60), message)
            message_text.setFont_(NSFont.systemFontOfSize_(13))
        
            # Progress visualization for successful transfers
            if not is_error and (created > 0 or updated > 0):
                total = created + updated
                progress_y = window_height - 80
            
                # Progress bar background
                progress_bg = Group((20, progress_y, 360, 20))
                progress_bg.setBackgroundColor_(0.9, 0.9, 0.9, 1.0)
                progress_bg.setCornerRadius_(10)
            
                # Progress bar fill
                progress_width = min(360, (total / max(total, 1)) * 360) if total > 0 else 0
                progress_fill = Group((20, progress_y, progress_width, 20))
                if not is_error:
                    progress_fill.setBackgroundColor_(0.2, 0.6, 0.2, 1.0)
                else:
                    progress_fill.setBackgroundColor_(0.8, 0.2, 0.2, 1.0)
                progress_fill.setCornerRadius_(10)
            
                # Progress text
                progress_text = TextBox((20, progress_y - 25, 360, 20), f"Progress: {created + updated} pairs processed")
                progress_text.setFont_(NSFont.systemFontOfSize_(11))
                progress_text.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.4, 0.4, 0.4, 1.0))
        
            # OK button
            ok_button = Button((150, window_height - 40, 100, 30), "OK")
            ok_button.setCallback_(self._closeResultsWindow)
        
            results_window.addView(header)
            results_window.addView(header_text)
            results_window.addView(message_text)
        
            if not is_error and (created > 0 or updated > 0):
                results_window.addView(progress_bg)
                results_window.addView(progress_fill)
                results_window.addView(progress_text)
        
            results_window.addView(ok_button)
        
            # Store reference to close later
            self._current_results_window = results_window
        
            results_window.open()
        
        except Exception as e:
            # Fallback to simple message if window creation fails
            print(f"Results window error: {e}")
            Message(message, title)

    def _closeResultsWindow(self, sender):
        """Close the results window"""
        if hasattr(self, '_current_results_window'):
            self._current_results_window.close()

    def kernToSCLog(self, *args):
        """Add text to the Kern to SC tab log area"""
        text = " ".join(str(arg) for arg in args)
        tab = self.w.tabs[4]  # Kern to SC tab is index 4
        current_text = tab.logText.get()
        tab.logText.set(current_text + text + "\n")
        print(text)  # Also print to console for debug

    # Kern-Tools.py (fragmento corregido)

    def transfer_upper_to_upper_sc_fixed(self, font, factor, percentage, overwrite, debug_mode=False):
        created = updated = 0
        processed_pairs = set()

        if debug_mode:
            self.kernToSCLog(f"[DEBUG] Iniciando Uppercase→Uppercase SC transfer")
            self.kernToSCLog(f"[DEBUG] Porcentaje: {percentage}%, Factor: {factor}")

        font.disableUpdateInterface()
        try:
            masters = [font.selectedFontMaster]
            for master in masters:
                mid = master.id
                kerning_dict = font.kerning.get(mid, {})
                all_kerning_sources = {}

                for left_key, right_dict in kerning_dict.items():
                    for right_key, value in right_dict.items():
                        all_kerning_sources[(str(left_key), str(right_key))] = ("font.kerning", value)

                transfer_pairs = []
                excluded_sc = 0
                total_pairs = 0

                for (leftKey_str, rightKey_str), (source, original_value) in all_kerning_sources.items():
                    total_pairs += 1
                    if ".sc" in leftKey_str or ".sc" in rightKey_str:
                        excluded_sc += 1
                        continue
                    transfer_pairs.append({
                        'left': leftKey_str,
                        'right': rightKey_str,
                        'value': original_value
                    })

                if debug_mode:
                    self.kernToSCLog(f"[DEBUG] Total pares: {total_pairs}, Transferir: {len(transfer_pairs)}, Excluidos SC: {excluded_sc}")

                unique_pairs_to_process = []

                for pair_info in transfer_pairs:
                    leftKey_str = pair_info['left']
                    rightKey_str = pair_info['right']
                    original_value = pair_info['value']

                    leftSC = self.convert_to_sc_like_original(leftKey_str, font)
                    rightSC = self.convert_to_sc_like_original(rightKey_str, font)

                    if not self._checkGlyphExists(font, leftSC) or not self._checkGlyphExists(font, rightSC):
                        if debug_mode:
                            missing = []
                            if not self._checkGlyphExists(font, leftSC): missing.append(leftSC)
                            if not self._checkGlyphExists(font, rightSC): missing.append(rightSC)
                            self.kernToSCLog(f"[DEBUG] Saltado pares por glifos SC faltantes: {missing}")
                        continue

                    if leftSC != leftKey_str or rightSC != rightKey_str:
                        pair_key = f"{leftSC}|{rightSC}"
                        if pair_key not in processed_pairs:
                            processed_pairs.add(pair_key)
                            unique_pairs_to_process.append({
                                'leftSC': leftSC,
                                'rightSC': rightSC,
                                'original_value': original_value,
                                'pair_key': pair_key,
                            })

                if debug_mode:
                    self.kernToSCLog(f"[DEBUG] Pares únicos a procesar: {len(unique_pairs_to_process)}")

                for pair in unique_pairs_to_process:
                    leftSC = pair['leftSC']
                    rightSC = pair['rightSC']
                    original_value = pair['original_value']
                    try:
                        newValue = int(round(float(original_value) * factor))
                    except:
                        continue

                    try:
                        existing = font.kerningForPair(mid, leftSC, rightSC)
                    except:
                        existing = None

                    if existing is not None and not overwrite:
                        if debug_mode:
                            self.kernToSCLog(f"[DEBUG] Saltado (existe): {leftSC} + {rightSC}")
                        continue

                    try:
                        font.setKerningForPair(mid, leftSC, rightSC, newValue)
                        if existing is not None:
                            updated += 1
                            if debug_mode and updated <= 25:
                                self.kernToSCLog(f"[DEBUG] Actualizado: {leftSC} + {rightSC} = {newValue}")
                        else:
                            created += 1
                            if debug_mode and created <= 25:
                                self.kernToSCLog(f"[DEBUG] Creado: {leftSC} + {rightSC} = {newValue}")
                    except Exception as e:
                        if debug_mode:
                            self.kernToSCLog(f"[ERROR] {leftSC} + {rightSC}: {e}")

        except Exception as e:
            if debug_mode:
                self.kernToSCLog(f"[ERROR] {str(e)}")
            import traceback
            self.kernToSCLog(f"[TRACEBACK] {traceback.format_exc()}")

        finally:
            font.enableUpdateInterface()

        self.kernToSCLog(f"✅ Transferencia completada!")
        self.kernToSCLog(f"Pares nuevos: {created}")
        self.kernToSCLog(f"Pares actualizados: {updated}")
        self.kernToSCLog(f"Porcentaje aplicado: {percentage}%")

        return {'created': created, 'updated': updated}


    def _checkGlyphExists(self, font, key):
        """Verifica si un glifo existe en la fuente"""
        if not key:
            return False
            
        # Para grupos de kerning, siempre asumir que existen
        if key.startswith("@MMK_"):
            return True
            
        # Para glifos individuales, verificar existencia
        try:
            if key in font.glyphs:
                return True
                
            # Si es un ID, intentar obtener el glifo
            g = font.glyphForId_(key)
            if g:
                return True
                
        except:
            pass
            
        return False

    def convert_to_sc_like_original(self, key, font):
        if not key:
            return None

        if key.startswith("@MMK_L_"):
            base_name = key[7:]
            sc_name = base_name.lower() + ".sc"
            if sc_name in font.glyphs:
                return "@MMK_L_" + sc_name
            else:
                return None

        if key.startswith("@MMK_R_"):
            base_name = key[7:]
            sc_name = base_name.lower() + ".sc"
            if sc_name in font.glyphs:
                return "@MMK_R_" + sc_name
            else:
                return None

        # Para glifos individuales
        glyph_name = None
        try:
            glyph = font.glyphForId_(key)
            glyph_name = glyph.name if glyph else None
        except:
            if key in font.glyphs:
                glyph_name = key
    
        if glyph_name:
            sc_name = glyph_name + ".sc"
            if sc_name in font.glyphs:
                return sc_name
    
        return None

    def transfer_upper_lower_bidirectional_sc(self, font, factor, overwrite, debug_mode):
        """Group Aware Transfer - same as the 258 results script"""
        try:
            masters = font.masters
            total_applied = 0
            total_seen = 0
            total_discarded = 0
            debug_limit_shown = 100

            self.kernToSCLog("=== KERN TRANSFER UPPERCASE-LOWERCASE TO SC (GROUP AWARE) ===")
            self.kernToSCLog(f"Masters: {len(masters)}, Factor: {factor}, Overwrite: {overwrite}")
        
            # GROUP ANALYSIS - KEY FOR MORE RESULTS
            group_analysis = {}
        
            for master in masters:
                mid = master.id
                kernDict = font.kerning.get(mid, {})
                if not kernDict:
                    continue
            
                for leftKey, rightDict in kernDict.items():
                    for rightKey, value in rightDict.items():
                        # Analyze right groups
                        if rightKey.startswith("@MMK_R_"):
                            group_key = rightKey[7:]
                            left_name = self._glyphNameFromKey(font, leftKey)
                            if left_name and left_name in font.glyphs:
                                if group_key not in group_analysis:
                                    group_analysis[group_key] = {"left_members": set(), "right_members": set()}
                                group_analysis[group_key]["left_members"].add(left_name)
                    
                        # Analyze left groups
                        if leftKey.startswith("@MMK_L_"):
                            group_key = leftKey[7:]
                            right_name = self._glyphNameFromKey(font, rightKey)
                            if right_name and right_name in font.glyphs:
                                if group_key not in group_analysis:
                                    group_analysis[group_key] = {"left_members": set(), "right_members": set()}
                                group_analysis[group_key]["right_members"].add(right_name)
        
            if debug_mode:
                self.kernToSCLog("=== GROUP ANALYSIS ===")
                for group_key, data in group_analysis.items():
                    self.kernToSCLog(f"Group {group_key}:")
                    self.kernToSCLog(f"  Left members: {sorted(data['left_members'])}")
                    self.kernToSCLog(f"  Right members: {sorted(data['right_members'])}")
        
            font.disableUpdateInterface()
            try:
                for master in masters:
                    mid = master.id
                    kernDict = font.kerning.get(mid, {})
                    if not kernDict:
                        continue
                
                    pairs_in_master = sum(len(rd) for rd in kernDict.values())
                    self.kernToSCLog(f"Master {mid}: {pairs_in_master} pairs to analyze")
                
                    processed_pairs = set()
                
                    for leftKey, rightDict in kernDict.items():
                        for rightKey, value in rightDict.items():
                            total_seen += 1
                        
                            # Case 1: Upper left -> Lower right (T + @MMK_R_o)
                            if self._isUpperCase(font, leftKey) and self._isLowerCase(font, rightKey):
                            
                                base_key = self._resolveKeyForSetting(font, leftKey)
                            
                                # GROUP AWARE: If the rightKey is a group
                                if rightKey.startswith("@MMK_R_"):
                                    group_key = rightKey[7:]
                                
                                    if debug_mode and total_seen <= debug_limit_shown:
                                        self.kernToSCLog(f"=== PROCESSING GROUP: {group_key} ===")
                                        self.kernToSCLog(f"  Base: {base_key}, Group: {group_key}, Value: {value}")
                                
                                    # Get REAL members of this group
                                    if group_key in group_analysis:
                                        left_members = group_analysis[group_key]["left_members"]
                                    
                                        if debug_mode and total_seen <= debug_limit_shown:
                                            self.kernToSCLog(f"  Left members in group: {left_members}")
                                    
                                        # Only process if base_key is in the left members of the group
                                        base_name = self._glyphNameFromKey(font, base_key)
                                        if base_name in left_members:
                                        
                                            # Find ALL right members of the group to find their SC
                                            right_members = group_analysis[group_key]["right_members"]
                                        
                                            for right_member in right_members:
                                                sc_name = self._findSCForGroupMember(font, right_member)
                                                if sc_name and sc_name in font.glyphs:
                                                    target_sc = "@MMK_R_" + sc_name
                                                    pair_id = f"{base_key}+{target_sc}"
                                                
                                                    if pair_id in processed_pairs:
                                                        continue
                                                    processed_pairs.add(pair_id)
                                                
                                                    existing_kern = self._safeKerningForPair(font, mid, base_key, target_sc)
                                                    if existing_kern is not None and not overwrite:
                                                        if debug_mode and total_seen <= debug_limit_shown:
                                                            self.kernToSCLog(f"  → Kerning exists, skipping: {base_key} + {target_sc}")
                                                        continue
                                                
                                                    new_value = round(value * factor)
                                                    try:
                                                        font.setKerningForPair(mid, base_key, target_sc, new_value)
                                                        total_applied += 1
                                                        if debug_mode and total_seen <= debug_limit_shown:
                                                            self.kernToSCLog(f"*** APPLIED: {base_key} + {target_sc} = {new_value} ***")
                                                    except Exception as e:
                                                        if debug_mode and total_seen <= debug_limit_shown:
                                                            self.kernToSCLog(f"  → Error: {e}")
                            
                                # Normal case (rightKey is not a group)
                                else:
                                    target_sc = self._getSCEquivalent(font, rightKey)
                                    # VERIFICACIÓN AÑADIDA: Comprobar que el glifo SC existe
                                    if not self._checkGlyphExists(font, target_sc):
                                        if debug_mode and total_seen <= debug_limit_shown:
                                            self.kernToSCLog(f"  → Target SC not found: {target_sc}")
                                        continue
                                        
                                    pair_id = f"{base_key}+{target_sc}"
                                
                                    if pair_id in processed_pairs:
                                        continue
                                    processed_pairs.add(pair_id)
                                
                                    if target_sc and base_key:
                                        if not target_sc.startswith("@MMK_") and target_sc not in font.glyphs:
                                            if debug_mode and total_seen <= debug_limit_shown:
                                                self.kernToSCLog(f"  → Target not found: {target_sc}")
                                            continue
                                    
                                        existing_kern = self._safeKerningForPair(font, mid, base_key, target_sc)
                                        if existing_kern is not None and not overwrite:
                                            if debug_mode and total_seen <= debug_limit_shown:
                                                self.kernToSCLog(f"  → Kerning exists, skipping: {base_key} + {target_sc}")
                                            continue
                                    
                                        new_value = round(value * factor)
                                        try:
                                            font.setKerningForPair(mid, base_key, target_sc, new_value)
                                            total_applied += 1
                                            if debug_mode and total_seen <= debug_limit_shown:
                                                self.kernToSCLog(f"*** APPLIED: {base_key} + {target_sc} = {new_value} ***")
                                        except Exception as e:
                                            if debug_mode and total_seen <= debug_limit_shown:
                                                self.kernToSCLog(f"  → Error: {e}")
                        
                            # Case 2: Lower left -> Upper right (inverse - @MMK_L_o + T)
                            elif self._isLowerCase(font, leftKey) and self._isUpperCase(font, rightKey):
                            
                                base_key = self._resolveKeyForSetting(font, rightKey)
                            
                                # GROUP AWARE: If the leftKey is a group
                                if leftKey.startswith("@MMK_L_"):
                                    group_key = leftKey[7:]
                                
                                    # Get REAL members of this group
                                    if group_key in group_analysis:
                                        right_members = group_analysis[group_key]["right_members"]
                                    
                                        # Only process if base_key is in the right members of the group
                                        base_name = self._glyphNameFromKey(font, base_key)
                                        if base_name in right_members:
                                        
                                            # Find ALL left members of the group to find their SC
                                            left_members = group_analysis[group_key]["left_members"]
                                        
                                            for left_member in left_members:
                                                sc_name = self._findSCForGroupMember(font, left_member)
                                                if sc_name and sc_name in font.glyphs:
                                                    target_sc = "@MMK_L_" + sc_name
                                                    pair_id = f"{target_sc}+{base_key}"
                                                
                                                    if pair_id in processed_pairs:
                                                        continue
                                                    processed_pairs.add(pair_id)
                                                
                                                    existing_kern = self._safeKerningForPair(font, mid, target_sc, base_key)
                                                    if existing_kern is not None and not overwrite:
                                                        continue
                                                
                                                    new_value = round(value * factor)
                                                    try:
                                                        font.setKerningForPair(mid, target_sc, base_key, new_value)
                                                        total_applied += 1
                                                        if debug_mode and total_seen <= debug_limit_shown:
                                                            self.kernToSCLog(f"*** APPLIED INVERSE: {target_sc} + {base_key} = {new_value} ***")
                                                    except Exception as e:
                                                        pass
                            
                                # Normal case (leftKey is not a group)
                                else:
                                    target_sc = self._getSCEquivalent(font, leftKey)
                                    # VERIFICACIÓN AÑADIDA: Comprobar que el glifo SC existe
                                    if not self._checkGlyphExists(font, target_sc):
                                        continue
                                        
                                    pair_id = f"{target_sc}+{base_key}"
                                
                                    if pair_id in processed_pairs:
                                        continue
                                    processed_pairs.add(pair_id)
                                
                                    if target_sc and base_key:
                                        if not target_sc.startswith("@MMK_") and target_sc not in font.glyphs:
                                            continue
                                    
                                        existing_kern = self._safeKerningForPair(font, mid, target_sc, base_key)
                                        if existing_kern is not None and not overwrite:
                                            continue
                                    
                                        new_value = round(value * factor)
                                        try:
                                            font.setKerningForPair(mid, target_sc, base_key, new_value)
                                            total_applied += 1
                                            if debug_mode and total_seen <= debug_limit_shown:
                                                self.kernToSCLog(f"*** APPLIED INVERSE: {target_sc} + {base_key} = {new_value} ***")
                                        except Exception as e:
                                            pass
                                
            finally:
                font.enableUpdateInterface()

            self.kernToSCLog("=== SUMMARY ===")
            self.kernToSCLog(f"Total pairs analyzed: {total_seen}")
            self.kernToSCLog(f"Total kerning pairs applied: {total_applied}")
            self.kernToSCLog(f"Total discarded: {total_discarded}")
        
            return total_applied
        
        except Exception as e:
            self.kernToSCLog(f"Error in transfer_upper_lower_bidirectional_sc: {str(e)}")
            import traceback
            self.kernToSCLog(traceback.format_exc())
            return 0

    # HELPER FUNCTIONS FOR GROUP AWARE
    def _glyphNameFromKey(self, font, key):
        """Get glyph name from a kerning key"""
        if not key:
            return None
        if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
            return key.split("_", 2)[-1]
        if key in font.glyphs:
            return key
        try:
            g = font.glyphForId_(key)
            if g and g.name:
                return g.name
        except:
            pass
        return None

    def _safeKerningForPair(self, font, master_id, left_key, right_key):
        """Get kerning value safely"""
        try:
            return font.kerningForPair(master_id, left_key, right_key)
        except:
            return None

    def _isUpperCase(self, font, key):
        """Determine if a kerning key represents uppercase"""
        if not key:
            return False
        
        glyph_name = self._glyphNameFromKey(font, key)
        if not glyph_name:
            return False
        
        if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
            return glyph_name and glyph_name[0].isupper()
    
        return bool(glyph_name) and glyph_name[0].isupper()

    def _isLowerCase(self, font, key):
        """Determine if a kerning key represents lowercase"""
        if not key:
            return False
        
        glyph_name = self._glyphNameFromKey(font, key)
        if not glyph_name:
            return False
        
        if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
            return glyph_name and glyph_name[0].islower()
    
        return bool(glyph_name) and glyph_name[0].islower()

    def _getSCEquivalent(self, font, key):
        """Get SC equivalent for a kerning key"""
        if not key:
            return None
        
        glyph_name = self._glyphNameFromKey(font, key)
        if not glyph_name:
            return None
        
        possible_names = [
            glyph_name + ".sc",
            glyph_name.lower() + ".sc", 
            glyph_name.upper() + ".sc",
            glyph_name.capitalize() + ".sc"
        ]
    
        for name in possible_names:
            if name in font.glyphs:
                if key.startswith("@MMK_L_"):
                    return "@MMK_L_" + name
                elif key.startswith("@MMK_R_"):
                    return "@MMK_R_" + name
                else:
                    return name
        return None

    def _findSCForGroupMember(self, font, original_glyph_name):
        """Find SC equivalent for a specific glyph"""
        if not original_glyph_name:
            return None
    
        possible_names = [
            original_glyph_name + ".sc",
            original_glyph_name.lower() + ".sc", 
            original_glyph_name.upper() + ".sc",
            original_glyph_name.capitalize() + ".sc"
        ]
    
        for name in possible_names:
            if name in font.glyphs:
                return name
    
        return None

    def _resolveKeyForSetting(self, font, key):
        """Resolve a kerning key for use in setKerningForPair"""
        if not key:
            return None
        if key.startswith("@MMK_"):
            return key
        if key in font.glyphs:
            return key
        try:
            g = font.glyphForId_(key)
            if g and g.name:
                return g.name
        except Exception:
            pass
        return None
                                                                                                                                                                                                                                                                                                                                                                                                                                              
    # ===========================================================
    #  SANITIZER TAB
    # ===========================================================
    def buildSanitizerTab(self):
        tab = self.w.tabs[5]
        
        tab.textDescription = TextBox((15, 10, -15, 40),
            "Fixes kerning inconsistencies:\n"
            "UUIDs, missing kerning groups, and .sc group inheritance, Ghost Kerning pairs.",
            sizeStyle="small")
        
        y = 60
        tab.cleanAndConvert = Button((15, y, -15, 35), "🧹 Clean & Convert All", callback=self.cleanAndConvertCallback)
        y += 50
        tab.results = TextEditor((15, y, -15, -15), "", readOnly=True)

    # ===========================================================
    #  KERNING GROUP VALIDATOR (NEW)
    # ===========================================================
    def kerningGroupExists(self, font, groupName):
        if groupName.startswith("@MMK_L_"):
            grp = groupName.replace("@MMK_L_", "")
            return any(g.leftKerningGroup == grp for g in font.glyphs)
        if groupName.startswith("@MMK_R_"):
            grp = groupName.replace("@MMK_R_", "")
            return any(g.rightKerningGroup == grp for g in font.glyphs)
        return False

    # ===========================================================
    #  SANITIZER ENGINE
    # ===========================================================
    def cleanAndConvertCallback(self, sender):
        font = Glyphs.font
        if not font:
            self.sanitizerLog("⚠️ No font open.")
            return
        
        master = font.selectedFontMaster
        kerning = font.kerning[master.id]
        converted = 0
        removed = 0

        self.sanitizerLog("---------- KERNING CLEANUP & CONVERSION ----------")

        old_kerning = dict(kerning)

        # ======================================================
        # 🕳️ 1) REMOVE GHOST KERNING PAIRS
        # ======================================================
        ghostRemoved = 0
        for leftKey in list(old_kerning.keys()):
            for rightKey in list(old_kerning[leftKey].keys()):

                leftValid = False
                rightValid = False

                # Validate left side
                if str(leftKey).startswith("@"):
                    if self.kerningGroupExists(font, leftKey):
                        leftValid = True
                else:
                    g = font.glyphForId_(leftKey) or font.glyphs[leftKey]
                    if g:
                        leftValid = True

                # Validate right side
                if str(rightKey).startswith("@"):
                    if self.kerningGroupExists(font, rightKey):
                        rightValid = True
                else:
                    g = font.glyphForId_(rightKey) or font.glyphs[rightKey]
                    if g:
                        rightValid = True

                # Remove ghost (invalid pair)
                if not leftValid or not rightValid:
                    try:
                        del kerning[leftKey][rightKey]
                        ghostRemoved += 1
                    except:
                        pass

        self.sanitizerLog(f"🧽 Ghost pairs removed: {ghostRemoved}")

        # ======================================================
        # 🔄 2) CONVERT UUIDs & FIX GROUP INHERITANCE
        # ======================================================

        old_kerning = dict(kerning)  # refresh after removals

        for leftKey in list(old_kerning.keys()):
            for rightKey in list(old_kerning[leftKey].keys()):
                value = old_kerning[leftKey][rightKey]
                newLeft, newRight = leftKey, rightKey
                changed = False

                # 🧩 Convert UUIDs to glyph names
                if not str(leftKey).startswith("@"):
                    g = font.glyphForId_(leftKey)
                    if g:
                        newLeft = g.name
                        changed = True

                if not str(rightKey).startswith("@"):
                    g = font.glyphForId_(rightKey)
                    if g:
                        newRight = g.name
                        changed = True

                # 🔁 Convert glyphs to proper group references
                if not str(newLeft).startswith("@") and newLeft in font.glyphs:
                    g = font.glyphs[newLeft]
                    if g.leftKerningGroup:
                        newLeft = f"@MMK_L_{g.leftKerningGroup}"
                        changed = True

                if not str(newRight).startswith("@") and newRight in font.glyphs:
                    g = font.glyphs[newRight]
                    if g.rightKerningGroup:
                        newRight = f"@MMK_R_{g.rightKerningGroup}"
                        changed = True

                if changed:
                    try:
                        font.setKerningForPair(master.id, newLeft, newRight, value)
                        if leftKey in kerning and rightKey in kerning[leftKey]:
                            del kerning[leftKey][rightKey]
                        converted += 1
                    except Exception as e:
                        self.sanitizerLog(f"❌ Error with {leftKey} — {rightKey}: {e}")
                        removed += 1

        # ======================================================
        # 🔧 3) REASSIGN .sc GROUP INHERITANCE
        # ======================================================

        reassigned = 0
        for g in font.glyphs:
            if g.name.endswith(".sc"):
                base_name = g.name[:-3]
                base = font.glyphs[base_name]
                if base:
                    if not g.leftKerningGroup and base.leftKerningGroup:
                        g.leftKerningGroup = base.leftKerningGroup
                        reassigned += 1
                    if not g.rightKerningGroup and base.rightKerningGroup:
                        g.rightKerningGroup = base.rightKerningGroup
                        reassigned += 1

        # ======================================================
        # 📊 SUMMARY
        # ======================================================
        self.sanitizerLog(f"🔄 Converted pairs: {converted}")
        self.sanitizerLog(f"🗑️ Removed during conversion: {removed}")
        self.sanitizerLog(f"🧽 Ghost pairs removed earlier: {ghostRemoved}")
        self.sanitizerLog(f"🔠 .sc glyphs re-linked: {reassigned}")
        self.sanitizerLog("--------------------------------")


    def sanitizerLog(self, msg):
        tab = self.w.tabs[5]
        current_text = tab.results.get()
        tab.results.set(current_text + msg + "\n")
        print(msg)

    # ===========================================================
    #  CLEAR & RESTORE TAB
    # ===========================================================
    def buildClearRestoreTab(self):
        tab = self.w.tabs[6]

        tab.titleLabel = TextBox((15, 15, -15, 20), "Select master:")
        tab.masterPopup = PopUpButton((15, 40, -15, 20), self.getMasterNames())
        
        # Automatically select current master
        self.selectCurrentMaster()

        tab.sep1 = HorizontalLine((15, 75, -15, 1))
        tab.deleteButton = Button((15, 90, -15, 20), "🗑️ Delete kerning of selected master", callback=self.deleteKerning)
        tab.backupCheck = CheckBox((15, 120, -15, 20), "Create JSON backup before deleting", value=True)
        tab.restoreButton = Button((15, 150, -15, 20), "♻️ Restore kerning from JSON backup", callback=self.restoreCallback)

        tab.sep2 = HorizontalLine((15, 185, -15, 1))
        tab.smallValLabel = TextBox((15, 200, -15, 20), "Delete small-value pairs in active master:")
        tab.threshold = EditText((15, 225, 60, 22), "10")
        tab.negativeOnly = CheckBox((90, 225, -15, 20), "Only negative", value=True)
        tab.deleteSmallButton = Button((15, 255, -15, 20), "🧹 Delete small values", callback=self.deleteSmallKerning)

    def getMasterNames(self):
        font = Glyphs.font
        if not font:
            return ["No font open"]
        return [f"{i+1}: {m.name}" for i, m in enumerate(font.masters)]

    def getSelectedMaster(self):
        font = Glyphs.font
        if not font:
            return None
        idx = self.w.tabs[6].masterPopup.get()
        return font.masters[idx]

    def selectCurrentMaster(self):
        """Automatically select current master in dropdown"""
        font = Glyphs.font
        if not font:
            return
        
        current_master = font.selectedFontMaster
        if current_master:
            # Find index of current master in masters list
            for i, master in enumerate(font.masters):
                if master.id == current_master.id:
                    self.w.tabs[6].masterPopup.set(i)
                    print(f"✅ Master automatically selected: {master.name}")
                    break

    # ---------- DELETE ALL ----------
    def deleteKerning(self, sender):
        font = Glyphs.font
        if not font:
            Message("Error", "Please open a font first.", OKButton="OK")
            return

        master = self.getSelectedMaster()
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return

        if self.w.tabs[6].backupCheck.get():
            self.backupKerning(master)

        count = 0
        kdict = font.kerning.get(master.id, {})
        for leftKey in list(kdict.keys()):
            count += len(kdict[leftKey])
            kdict[leftKey].clear()
        print(f"🗑️ Deleted {count} pairs in {master.name}")
        Message("Done", f"🗑️ Deleted {count} kerning pairs in '{master.name}'.", OKButton="OK")

    # ---------- BACKUP ----------
    def backupKerning(self, master):
        font = Glyphs.font
        if not font:
            return
        from GlyphsApp import GetSaveFile
        masterName = master.name.replace(" ", "_")
        filePath = GetSaveFile(message="Save JSON Backup As", ProposedFileName=f"{masterName}_kerning_backup.json")
        if not filePath:
            return
        
        try:
            # Convert MGOrderedDictionary to serializable dictionary
            kerning_data = font.kerning.get(master.id, {})
            serializable_data = {}
            
            for leftKey in kerning_data.keys():
                right_dict = kerning_data[leftKey]
                serializable_right_dict = {}
                
                for rightKey in right_dict.keys():
                    serializable_right_dict[str(rightKey)] = right_dict[rightKey]
                
                serializable_data[str(leftKey)] = serializable_right_dict
            
            with open(filePath, "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, indent=2)
            
            print(f"💾 Backup saved: {filePath}")
            print(f"📊 Kerning pairs backed up: {sum(len(v) for v in serializable_data.values())}")
            
        except Exception as e:
            print(f"❌ DEBUG - Error details: {type(e).__name__}: {e}")
            Message("Error", f"Could not save backup: {e}", OKButton="OK")

    # ---------- RESTORE ----------
    def restoreCallback(self, sender):
        from GlyphsApp import GetOpenFile
        filePath = GetOpenFile(message="Select kerning JSON backup")
        if not filePath:
            return
        self.restoreKerning(filePath)

    def restoreKerning(self, filePath):
        font = Glyphs.font
        if not font:
            Message("Error", "Open a font first.", OKButton="OK")
            return
        master = self.getSelectedMaster()
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return
            
        try:
            with open(filePath, "r", encoding="utf-8") as f:
                data = json.load(f)

            count = 0
            for left, rightDict in data.items():
                for right, value in rightDict.items():
                    try:
                        font.setKerningForPair(master.id, left, right, value)
                        count += 1
                    except Exception as e:
                        print(f"❌ {left}-{right}: {e}")
            print(f"✅ Imported {count} pairs into {master.name}")
            Message("Done", f"✅ Imported {count} pairs into '{master.name}'.", OKButton="OK")
            
        except Exception as e:
            Message("Error", f"Could not restore backup: {e}", OKButton="OK")

    # ---------- DELETE SMALL VALUES ----------
    def deleteSmallKerning(self, sender):
        font = Glyphs.font
        if not font:
            Message("Error", "Open a font first.", OKButton="OK")
            return
        master = font.selectedFontMaster
        masterID = master.id
        kernDict = font.kerning[masterID]
        try:
            threshold = abs(float(self.w.tabs[6].threshold.get()))
        except:
            Message("Error", "Threshold must be numeric.", OKButton="OK")
            return
        negativeOnly = self.w.tabs[6].negativeOnly.get()

        toDelete = []
        for leftID in kernDict.keys():
            for rightID in kernDict[leftID].keys():
                val = kernDict[leftID][rightID]
                if (negativeOnly and 0 > val > -threshold) or (not negativeOnly and abs(val) <= threshold):
                    leftName = nameForID(font, leftID)
                    rightName = nameForID(font, rightID)
                    if leftName and rightName:
                        toDelete.append((leftName, rightName))

        for left, right in toDelete:
            font.removeKerningForPair(masterID, left, right)

        print(f"🧹 Deleted {len(toDelete)} small-value pairs ≤ {threshold} in '{master.name}'.")
        Message("Done", f"🧹 Deleted {len(toDelete)} small-value pairs ≤ {threshold} in '{master.name}'.", OKButton="OK")

    # ===========================================================
    # SCALE % TAB
    # ===========================================================
    def buildScaleTab(self):
        tab = self.w.tabs[7]
        tab.text = TextBox((10, 10, -10, 20), "Enter percentage (e.g., 70 = 70%)")
        tab.input = EditText((10, 40, 280, 20), "100")
        tab.directionText = TextBox((10, 70, 100, 20), "Action:")
        tab.direction = PopUpButton((110, 70, 180, 20), ["Decrease", "Increase"])
        tab.button = Button((10, 100, 280, 30), "Apply", callback=self.applyScale)

    def applyScale(self, sender):
        font = Glyphs.font
        if not font:
            Message("Error", "Open a font first.", OKButton="OK")
            return

        try:
            percentage = float(self.w.tabs[7].input.get())
        except:
            Message("Error", "Please enter a valid number.", OKButton="OK")
            return

        masterID = font.selectedFontMaster.id
        if masterID not in font.kerning:
            Message("Info", "This master has no kerning.", OKButton="OK")
            return

        if self.w.tabs[7].direction.get() == 0:
            scaleFactor = percentage / 100.0
        else:
            scaleFactor = 1.0 + (percentage / 100.0)

        kernDict = font.kerning[masterID]
        adjustedCount = 0
        pairs = []

        for left, rightDict in kernDict.items():
            for right, value in rightDict.items():
                pairs.append((left, right, value))

        font.disableUpdateInterface()
        try:
            for left, right, oldValue in pairs:
                newValue = int(round(oldValue * scaleFactor))
                if newValue != oldValue:
                    font.kerning[masterID][left][right] = newValue
                    adjustedCount += 1
        finally:
            font.enableUpdateInterface()

        Message(
            "Process completed",
            f"{adjustedCount} kerning pairs adjusted with scale factor {scaleFactor:.2f}.",
            OKButton="OK"
        )

# Execute script
font = Glyphs.font
if not font:
    Message("Error", "Open a font before running this script.", OKButton="OK")
else:
    KernTools()
