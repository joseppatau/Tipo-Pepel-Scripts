# MenuTitle: Kern Coach v2
# -*- coding: utf-8 -*-
# Description: A guided kerning workflow system for precision and control
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import vanilla
import json
import re
import math
import time
import traceback
from GlyphsApp import Glyphs, GSFeature, Message, OFFCURVE
from vanilla.dialogs import askYesNo
from AppKit import NSOpenPanel, NSSavePanel, NSFont, NSAttributedString, NSFontAttributeName


PREF = "com.kingSubdit.sets"
PREF_NO_KERN = "com.kingSubdit.noKern"
PREF_EXCLUDE = "com.kingSubdit.exclude"
PREF_GAP = "com.kingSubdit.gap"
PREF_EXCLUDE_EXISTING = "com.kingSubdit.excludeExisting"
PREF_PREFIX = "com.kingSubdit.prefix"
PREF_SUFFIX = "com.kingSubdit.suffix"
PREF_PERLINE = "com.kingSubdit.perline"
PREF_POSITIVE_ONLY = "com.kingSubdit.positiveOnly"
PREF_SHOW_ONE_PER_GROUP = "com.kingSubdit.showOnePerGroup"
PREF_CONTEXTUAL_AFFIXES = "com.kingSubdit.contextualAffixes"


# ======== GEOMETRY HELPERS ========

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def minDistanceBetweenSegments(a1, a2, b1, b2):
    def clamp(x, a, b):
        return max(a, min(b, x))

    A = (a1.x, a1.y); B = (a2.x, a2.y)
    C = (b1.x, b1.y); D = (b2.x, b2.y)

    def closestPoint(P, Q, R):
        vx, vy = Q[0]-P[0], Q[1]-P[1]
        denom = vx*vx + vy*vy
        if denom == 0:
            return P
        t = ((R[0]-P[0])*vx + (R[1]-P[1])*vy) / denom
        t = clamp(t, 0, 1)
        return (P[0] + t*vx, P[1] + t*vy)

    dmin = float("inf")
    for p in (A, B):
        q = closestPoint(C, D, p)
        dmin = min(dmin, distance(p, q))
    for p in (C, D):
        q = closestPoint(A, B, p)
        dmin = min(dmin, distance(p, q))

    return dmin

def getSegments(layer):
    segs = []
    for path in layer.paths:
        nodes = path.nodes
        if not nodes:
            continue
        count = len(nodes)
        for i in range(count):
            n1 = nodes[i]
            if path.closed:
                n2 = nodes[(i+1) % count]
            elif i+1 < count:
                n2 = nodes[i+1]
            else:
                continue
            segs.append((n1, n2))
    return segs

def minDistanceBetweenLayers(layer1, layer2, dx, liApache2=10000):
    segs1 = getSegments(layer1)
    segs2 = getSegments(layer2)
    if not segs1 or not segs2:
        return liApache2

    shifted = []
    for n1, n2 in segs2:
        shifted.append((
            type("P", (), {"x": n1.x + dx, "y": n1.y}),
            type("P", (), {"x": n2.x + dx, "y": n2.y})
        ))

    dmin = liApache2
    for s1 in segs1:
        for s2 in shifted:
            d = minDistanceBetweenSegments(s1[0], s1[1], s2[0], s2[1])
            if d < dmin:
                dmin = d
            if dmin <= 0:
                return 0.0
    return dmin

def margin_for_pair(font, masterID, leftName, rightName):
    gL = font.glyphs[leftName]
    gR = font.glyphs[rightName]
    if not gL or not gR:
        return None

    layerL = gL.layers[masterID]
    layerR = gR.layers[masterID]

    try:
        layerL = layerL.copyDecomposedLayer()
    except:
        pass

    try:
        layerR = layerR.copyDecomposedLayer()
    except:
        pass

    dx = layerL.width
    return minDistanceBetweenLayers(layerL, layerR, dx)


class KingSubditKerningEngine:
    
    def __init__(self):
        self._kerningCache = {}
        self._segmentCache = {}
        self._group_members_cache = {}  # Cache para miembros de grupos
        self.DEBUG = False
        self.loadDefaults()
        self.loadNoKernDefaults()
        self.loadExcludeDefaults()
        self.loadGapDefaults()
        self.loadExcludeExistingDefaults()
        self.loadPrefixSuffixDefaults()
        self.loadPositiveOnlyDefaults()
        self.loadShowOnePerGroupDefaults()
        self.loadContextualAffixesDefaults()
        self.positiveOnly = False
        self.showOnePerGroup = True
        self.contextualAffixes = True
        self.setupUI()
    
    
    def setupUI(self):
        self.w = vanilla.FloatingWindow((440, 850), "King / Subdit Kerning Engine v2.8")

        self.w.tabs = vanilla.Tabs((0, 0, -0, -0), ["Main", "Settings", "Tools"])

        # ===== PESTAÑA MAIN =====
        main = self.w.tabs[0]
        y = 10

        # CURRENT (LEFT / RIGHT)
        main.currentLabel = vanilla.TextBox((10, y+2, 60, 20), "Current")

        # Left glyph
        main.currentLeft = vanilla.EditText((70, y, 60, 22), "H", callback=self.refreshMargin)

        # Separator visual
        main.sep = vanilla.TextBox((135, y+2, 10, 20), "/")

        # Right glyph
        main.currentRight = vanilla.EditText((150, y, 60, 22), "H", callback=self.refreshMargin)

        # Resultat
        main.resultLabel = vanilla.TextBox((220, y+2, -10, 20), "margin: — • kern: —", alignment="left")

        y += 32

        main.featureLabel = vanilla.TextBox((10, y+2, 60, 20), "Feature")
        self.featureList = self.getFeatureList()
        main.featureDropdown = vanilla.PopUpButton((70, y, 150, 22), self.featureList)

        # NUEVOS BOTONES: #AV# y @Tab
        # Botón #AV# con negrita
        main.hashAVButton = vanilla.Button((190, y+30, 50, 22), "#AV#", callback=self.kernHashWordsCallback)
        hashAV_title = NSAttributedString.alloc().initWithString_attributes_(
            "#AV#", {NSFontAttributeName: NSFont.boldSystemFontOfSize_(NSFont.systemFontSize())}
        )
        main.hashAVButton.getNSButton().setAttributedTitle_(hashAV_title)

        main.atTabButton = vanilla.Button((345, y, 50, 22), "@Tab", callback=self.listKerningGroupMembersInNewTab)
        main.atTabButton.getNSButton().setToolTip_("List members of the kerning group of the glyph to the right of cursor")

        y += 32

        main.marginLabel = vanilla.TextBox((10, y+2, 60, 20), "Margin:")
        main.mValue = vanilla.EditText((70, y-1, 40, 22), "80")

        # Botón Kern Tab con negrita
        main.kernButton = vanilla.Button((115, y-3, 70, 24), "Kern Tab", callback=self.kernFromSelectedSet)
        kern_title = NSAttributedString.alloc().initWithString_attributes_(
            "Kern Tab", {NSFontAttributeName: NSFont.boldSystemFontOfSize_(NSFont.systemFontSize())}
        )
        main.kernButton.getNSButton().setAttributedTitle_(kern_title)


        main.deleteKernButton = vanilla.Button((250, y-3, 90, 24), "Delete Kern", callback=self.deleteTabKern)

        main.closeTabsButton = vanilla.Button((400, y-33, 24, 24), "X", 
        callback=self.closeAllTabs)
        
        main.DeleteHashButton = vanilla.Button((390, y-3, 34, 24), "#X", 
                callback=self.deleteHashBlocksCallback)
        
        main.deleteHashButton = vanilla.Button((345, y-3, 40, 24), "🗑️#", callback=self.deleteKernInHashBlocks)

        y += 30

        main.list = vanilla.List(
            (10, y, -10, 290),
            self.displayList(),
            selectionCallback=self.loadSet,
            doubleClickCallback=self.generateFromSelection
        )

        y += 300

        main.loadButton = vanilla.Button((10, 400, 80, 25), "Load", callback=self.loadJSON)
        main.saveButton = vanilla.Button((100, 400, 80, 25), "Save", callback=self.saveJSON)
        main.deleteButton = vanilla.Button((-90, 400, 80, 25), "Delete", callback=self.deleteSet)

        y += 40

        main.textName = vanilla.TextBox((10, 440, 120, 20), "Set Name")
        y += 20
        main.setName = vanilla.EditText((10, 460, -10, 22))

        y += 30

        main.textKings = vanilla.TextBox((10, 490, 120, 20), "Kings Glyphs")
        y += 20
        main.kings = vanilla.EditText((10, 510, -10, 22))

        y += 30

        main.textSubdits = vanilla.TextBox((10, 540, 120, 20), "Subdit Glyphs")
        y += 20
        main.subdits = vanilla.TextEditor((10, 560, -10, 80))

        y += 90

        main.addButton = vanilla.Button((10, 650, 100, 25), "Add Set", callback=self.addSet)
        main.updateButton = vanilla.Button((120, 650, 100, 25), "Update Set", callback=self.updateSet)

        y += 40

        main.mode = vanilla.RadioGroup(
            (10, 690, -10, 60),
            ["Left (Subdit–King)", "Right (King–Subdit)", "Both"],
            isVertical=True
        )
        main.mode.set(2)

        y += 70

        main.preview = vanilla.TextBox((10, 760, -10, 20), "Pairs: 0")

        y += 22
        main.progress = vanilla.ProgressBar((10, 785, -10, 12))
        main.progress.set(0)

        # ===== PESTAÑA SETTINGS =====
        settings = self.w.tabs[1]
        y = 10

        settings.noKernTitle = vanilla.TextBox((10, y, 200, 20), "Kerning pairs filters")
        settings.noKernTitle.getNSTextField().setFont_(NSFont.boldSystemFontOfSize_(12))
        y += 25

        settings.noKernLeftLabel = vanilla.TextBox((10, y, 120, 20), "No Kern RightSD:")
        settings.noKernRightLabel = vanilla.TextBox((200, y, 120, 20), "No Kern LeftSD:")
        y += 18

        settings.noKernLeft = vanilla.TextEditor((10, y, 160, 70), self._savedNoKernLeft)
        settings.noKernRight = vanilla.TextEditor((200, y, 160, 70), self._savedNoKernRight)
        y += 80

        settings.saveNoKernButton = vanilla.Button((10, y, 75, 22), "Save", callback=self.saveNoKernSettings)
        settings.loadNoKernButton = vanilla.Button((95, y, 75, 22), "Load", callback=self.loadNoKernSettings)
        y += 40

        settings.separator1 = vanilla.HorizontalLine((10, y, -10, 1))
        y += 15

        settings.excludeTitle = vanilla.TextBox((10, y, 200, 20), "Generating pairs Filters")
        settings.excludeTitle.getNSTextField().setFont_(NSFont.boldSystemFontOfSize_(12))
        y += 25

        settings.excludeFirstLabel = vanilla.TextBox((10, y, 150, 20), "Exclude first RightSB:")
        settings.excludeSecondLabel = vanilla.TextBox((200, y, 150, 20), "Exclude second LeftSB:")
        y += 18

        settings.excludeFirst = vanilla.TextEditor((10, y, 160, 70), self._savedExcludeFirst)
        settings.excludeSecond = vanilla.TextEditor((200, y, 160, 70), self._savedExcludeSecond)
        y += 80

        settings.saveExcludeFileButton = vanilla.Button((10, y, 75, 22), "Save File", callback=self.saveExcludeToFile)
        settings.loadExcludeFileButton = vanilla.Button((90, y, 75, 22), "Load File", callback=self.loadExcludeFromFile)
        y += 35

        settings.separator2 = vanilla.HorizontalLine((10, y, -10, 1))
        y += 15

        settings.excludeExistingCheck = vanilla.CheckBox(
            (10, y, 200, 20),
            "Exclude existing pairs",
            value=self.excludeExisting,
            callback=self.toggleExcludeExisting
        )
        y += 25

        settings.positiveOnlyCheck = vanilla.CheckBox(
            (10, y, 200, 20),
            "Enable positive kern mode",
            value=self.positiveOnly,
            callback=self.togglePositiveOnly
        )
        y += 25

        settings.showOnePerGroupCheck = vanilla.CheckBox(
            (10, y, 220, 20),
            "Show only one member @Group",
            value=self.showOnePerGroup,
            callback=self.toggleShowOnePerGroup
        )
        y += 25

        settings.contextualAffixesCheck = vanilla.CheckBox(
            (10, y, 250, 20),
            "Use contextual prefixes/suffixes",
            value=self.contextualAffixes,
            callback=self.toggleContextualAffixes
        )
        y += 25

        settings.separator3 = vanilla.HorizontalLine((10, y, -10, 1))
        y += 15

        settings.formatTitle = vanilla.TextBox((10, y, 200, 20), "Output Format")
        settings.formatTitle.getNSTextField().setFont_(NSFont.boldSystemFontOfSize_(12))
        y += 25

        settings.prefixLabel = vanilla.TextBox((10, y, 50, 20), "Prefix:")
        settings.prefix = vanilla.EditText((70, y, 100, 22), self.prefix)

        settings.suffixLabel = vanilla.TextBox((190, y, 50, 20), "Suffix:")
        settings.suffix = vanilla.EditText((240, y, 100, 22), self.suffix)
        y += 30

        settings.perLineLabel = vanilla.TextBox((10, y, 100, 20), "Pairs per line:")
        settings.perLine = vanilla.EditText((120, y, 50, 22), str(self.perline))
        settings.saveFormatButton = vanilla.Button((200, y, 75, 22), "Save", callback=self.savePrefixSuffix)
        y += 30

        settings.separator4 = vanilla.HorizontalLine((10, y, -10, 1))
        y += 15

        settings.gapTitle = vanilla.TextBox((10, y, 200, 20), "Block spacing")
        settings.gapTitle.getNSTextField().setFont_(NSFont.boldSystemFontOfSize_(12))
        y += 25

        settings.gapLabel = vanilla.TextBox((10, y, 150, 20), "Spaces between blocks:")
        settings.gapSpaces = vanilla.EditText((160, y, 50, 22), str(self.gapSpaces))
        settings.saveGapButton = vanilla.Button((220, y, 75, 22), "Save", callback=self.saveGapSettings)
        y += 30

        settings.note1 = vanilla.TextBox(
            (10, y, -10, 100),
            "• Glyph names: exact matches\n"
            "• @group: matches all group members\n"
            "• Extensions are handled automatically\n"
            "• Prefix/Suffix accept multiple characters\n"
            "• Debug info in console\n"
            "• #AV# applies kerning only in #...# blocks\n"
            "• @Tab lists all members of kerning group",
            sizeStyle="small"
        )

        # ===== PESTAÑA TOOLS (Kern Coach Tools) =====
        tools = self.w.tabs[2]
        y = 10
    
        # SECTION 1: KERNING GROUPS GENERATOR
        tools.groupSectionLabel = vanilla.TextBox((15, y, 200, 20), "KERNING GROUPS GENERATOR", sizeStyle='small')
        y += 25
    
        # Main buttons
        tools.deleteButton = vanilla.Button((15, y, 200, 24), "Delete font kerning names", callback=self.deleteKerningGroups)
        tools.generateButton = vanilla.Button((220, y, 200, 24), "Generate Groups", callback=self.generateKerningGroups)
        y += 35
    
        # Manual group assignment
        tools.manualLabel = vanilla.TextBox((15, y, 320, 20), "Change group to selected glyphs:")
        y += 25
    
        # Radio buttons
        tools.radioGroup = vanilla.RadioGroup((15, y-10, 320, 40), 
                                       ["LSB (left)", "RSB (right)", "Both"], 
                                       sizeStyle='small',
                                       isVertical=False)
        tools.radioGroup.set(0)
        y += 45
    
        # Group name input
        tools.groupLabel = vanilla.TextBox((15, y-20, 50, 22), "Group:")
        tools.groupEdit = vanilla.EditText((65, y-22, 150, 22), "", callback=self.editGroupText)
        tools.applyButton = vanilla.Button((225, y-24, 95, 24), "Apply", callback=self.applyCustomGroup)
        y += 35
    
        # Info text for groups
        tools.groupInfoText = vanilla.TextBox((15, y-20, 400, 30), "-", sizeStyle='small')
        y += 40
    
        tools.separator1 = vanilla.HorizontalLine((15, y-35, -15, 1))
        y += 20
    
        # SECTION 2: TEST WORDS
        self.TEST_WORDS_COLLECTIONS = {
            "Symetric Trios": "/H/H/A/V/A/H/H/space/H/H/A/O/A/H/H/space/H/H/A/T/A/H/H/space/H/H/A/Y/A/H/H/space/H/H/A/S/A/H/H/space/H/H/A/W/A/H/H/space/H/H/A/U/A/H/H/space/H/H/T/A/T/H/H/space/H/H/T/O/T/H/H/space/H/H/Y/A/Y/H/H/space/H/H/Y/O/Y/H/H/space/H/H/U/A/U/H/H/space/H/H/S/Y/S/H/H/space/H/H/S/A/S/H/H/space/H/H/O/T/O/H/H/space/H/H/O/A/O/H/H/space/H/H/O/V/O/H/H/space/H/H/O/W/O/H/H/space/H/H/O/X/O/H/H/space/H/H/O/Y/O/H/H/space/H/H/M/V/M/H/H/space/H/H/X/O/X/H/H\n\/n/h/h/o/w/o/h/h/space/h/h/o/y/o/h/h/space/h/h/o/x/o/h/h/space/h/h/y/o/y/h/h/space/h/h/v/o/v/h/h/space/h/h/w/o/w/h/h/space/h/h/x/o/x/h/h/space/h/h/s/w/s/h/h/space/h/h/s/v/s/h/h/space/h/h/s/y/s/h/h/space/h/h/s/o/s/h/h",
            "Diacritics": "/A/iacute/l/space/A/igrave/l/space/A/icircumflex/l/space/A/idieresis/l/space/A/i/idieresis/l/space/B/iacute/n/space/B/igrave/n/space/B/icircumflex/n/space/B/idieresis/n/space/C/iacute/n/space/C/igrave/n/space/C/icircumflex/n/space/C/idieresis/n/space/D/iacute/n/space/D/igrave/n/space/D/icircumflex/n/space/D/idieresis/n/space/E/iacute/n/space/E/igrave/n/space/E/icircumflex/n/space/E/idieresis/n/space/F/adieresis/h/r/space/F/odieresis/l/d/e/r/space/F/agrave/n/space/F/aring/n/space/F/aacute/l/space/F/acircumflex/l/space/F/atilde/l/space/F/egrave/space/F/eacute/space/F/ecircumflex/l/space/F/edieresis/l/space/F/iacute/l/space/F/igrave/l/space/F/icircumflex/l/space/F/idieresis/l/space/F/oacute/l/space/F/ograve/space/F/ocircumflex/l/space/F/otilde/l/space/F/uacute/l/space/F/ugrave/space/F/ucircumflex/l/space/F/ydieresis/space/F/udieresis/n/k/space/G/iacute/n/space/G/igrave/n/space/G/icircumflex/n/space/G/idieresis/n/space/H/iacute/n/space/H/igrave/n/space/H/icircumflex/space/H/idieresis/n/space/J/iacute/n/space/J/igrave/n/space/J/icircumflex/n/space/J/idieresis/n/space/K/adieresis/r/n/space/K/odieresis/f/f/space/K/udieresis/d/o/s/space/K/igrave/n/space/K/icircumflex/n/space/K/idieresis/n/space/K/ydieresis/n/space/M/iacute/n/space/M/igrave/n/space/M/icircumflex/space/M/idieresis/n/space/O/iacute/n/space/O/igrave/n/space/O/icircumflex/n/space/O/idieresis/n/space/P/adieresis/l/space/P/odieresis/l/space/P/udieresis/n/k/space/P/aacute/l/space/P/agrave/n/space/P/acircumflex/l/space/P/atilde/l/space/P/aring/n/space/P/eacute/l/space/P/egrave/space/P/ecircumflex/l/space/P/iacute/l/space/P/igrave/space/P/icircumflex/l/space/P/idieresis/l/space/P/oacute/l/space/P/ograve/n/space/P/ocircumflex/l/space/P/otilde/l/space/P/uacute/l/space/P/ugrave/space/P/ucircumflex/l/space/P/ydieresis/space/R/adieresis/n/space/R/odieresis/a/d/space/R/udieresis/n/g/space/R/iacute/n/space/R/igrave/n/space/R/icircumflex/n/space/R/idieresis/n/space/S/iacute/n/space/S/igrave/n/space/S/icircumflex/n/space/S/idieresis/n/space/T/adieresis/p/space/T/odieresis/r/n/space/T/udieresis/f/f/space/T/aacute/l/space/T/agrave/space/T/acircumflex/l/space/T/atilde/l/space/T/aring/l/space/T/eacute/l/space/T/egrave/n/space/T/ecircumflex/l/space/T/edieresis/l/space/T/iacute/l/space/T/igrave/n/space/T/icircumflex/l/space/T/idieresis/l/space/T/oacute/l/space/T/ograve/n/space/T/ocircumflex/l/space/T/otilde/l/space/T/uacute/l/space/T/ugrave/n/space/T/ucircumflex/l/space/T/ydieresis/n/space/U/iacute/n/space/U/igrave/n/space/U/icircumflex/n/space/U/idieresis/n/space/V/adieresis/m/space/V/odieresis/t/space/V/aacute/l/space/V/agrave/n/space/V/acircumflex/l/space/V/atilde/l/space/V/aring/n/space/V/eacute/l/space/V/egrave/n/space/V/ecircumflex/l/space/V/edieresis/n/space/V/iacute/n/space/V/igrave/n/space/V/icircumflex/n/space/V/idieresis/n/space/V/oacute/l/space/V/ograve/n/space/V/ocircumflex/l/space/V/odieresis/n/space/V/otilde/l/space/V/uacute/l/space/V/ugrave/n/space/V/ucircumflex/l/space/V/udieresis/n/space/V/ydieresis/n/space/W/a/i/n/space/space/W/adieresis/m/space/W/odieresis/t/space/W/aacute/l/space/W/agrave/n/space/W/acircumflex/l/space/W/atilde/l/space/W/aring/n/space/W/eacute/l/space/W/egrave/n/space/W/ecircumflex/l/space/W/edieresis/n/space/W/iacute/n/space/W/igrave/n/space/W/icircumflex/n/space/W/idieresis/n/space/W/oacute/l/space/W/ograve/n/space/W/ocircumflex/l/space/W/odieresis/n/space/W/otilde/l/space/W/uacute/l/space/W/ugrave/n/space/W/ucircumflex/l/space/W/udieresis/n/space/W/ydieresis/n/space/X/aacute/l/space/X/agrave/n/space/X/acircumflex/n/space/X/adieresis/n/space/X/atilde/n/space/X/aring/n/space/X/eacute/n/space/X/egrave/n/space/X/ecircumflex/n/space/X/edieresis/n/space/X/iacute/l/space/X/igrave/l/space/X/icircumflex/l/space/X/idieresis/l/space/X/oacute/n/space/X/ograve/n/space/X/ocircumflex/n/space/X/odieresis/n/space/X/otilde/n/space/X/uacute/n/space/X/ugrave/n/space/X/ucircumflex/n/space/X/udieresis/n/space/X/aring/n/space/X/ydieresis/n/space/Y/acircumflex/n/space/Y/adieresis/n/space/Y/atilde/n/space/Y/aring/n/space/Y/eacute/n/space/Y/egrave/n/space/Y/ecircumflex/n/space/Y/edieresis/n/space/Y/iacute/n/space/Y/igrave/n/space/Y/icircumflex/n/space/Y/idieresis/n/space/Y/oacute/n/space/Y/ograve/n/space/Y/ocircumflex/n/space/Y/odieresis/n/space/Y/otilde/n/space/Y/uacute/n/space/Y/ugrave/n/space/Y/ucircumflex/n/space/Y/udieresis/n/space/Z/iacute/n/space/Z/igrave/n/space/Z/icircumflex/n/space/Z/idieresis/n/space/dcaron/a/space/dcaron/i/space/dcaron/o/space/dcaron/u/space/dcaron/k/space/dcaron/A/space/dcaron/I/space/dcaron/O/space/dcaron/U/space/dcaron/quotesingle/space/dcaron/quotedbl/space/dcaron/quotedbl/space/dcaron/quotedbl/space/dcaron/exclam/space/dcaron/question/space/dcaron/parenright/space/dcaron/bracketright/space/dcaron/braceright/space/dcaron/asterisk/space/tcaron/a/space/tcaron/i/space/tcaron/o/space/tcaron/u/space/tcaron/k/space/tcaron/A/space/tcaron/I/space/tcaron/O/space/tcaron/U/space/tcaron/quotesingle/space/tcaron/quotedbl/space/tcaron/quotedbl/space/tcaron/quotedbl/space/tcaron/exclam/space/tcaron/question/space/tcaron/parenright/space/tcaron/bracketright/space/tcaron/braceright/space/tcaron/asterisk/space/Lcaron/a/space/Lcaron/i/space/Lcaron/o/space/Lcaron/k/space/Lcaron/u/space/Lcaron/A/space/Lcaron/I/space/Lcaron/O/space/Lcaron/U/space/Lcaron/quotesingle/Lcaron/quotedbl/Lcaron/quotedbl/space/Lcaron/quotedbl/space/Lcaron/exclam/space/Lcaron/question/space/Lcaron/parenright/space/Lcaron/braceright/space/Lcaron/bracketright/space/Lcaron/asterisk/space/H/Lcaron/H/dcaron/H/lcaron/H/tcaron/H/H/lslash/H/H/space/o/b/j/iacute/zcaron/dcaron/k/o/v/aacute/space/v/dcaron/a/ccaron/iacute/m/e/space/v/e/lcaron/h/o/r/y/space/v/e/lcaron/r/y/b/yacute/c/h/space/scaron/t/v/r/tcaron/h/o/d/i/n/o/v/yacute/space/n/a/j/tcaron/a/zcaron/scaron/iacute/c/h/space/I/l/u/s/t/r/a/c/i/oacute/space/c/e/l/a/space/C/O/L/E/G/I/space/C/E/L/A/space/zacute/r/oacute/d/lslash/o/s/lslash/o/w/u/adieresis/T/adieresis/V/adieresis/W/adieresis/Y/adieresis/space/amacron/T/amacron/V/amacron/W/amacron/Y/amacron/space/aring/T/aring/V/aring/W/aring/Y/aring/space/ccaron/T/ccaron/V/ccaron/W/ccaron/Y/ccaron/space/imacron/T/imacron/V/imacron/W/imacron/Y/imacron/space/idieresis/T/idieresis/V/idieresis/W/idieresis/Y/idieresis/space/gbreve/T/gbreve/V/gbreve/W/gbreve/Y/gbreve/space/ncaron/T/ncaron/V/ncaron/W/ncaron/Y/ncaron/space/emacron/T/emacron/V/emacron/W/emacron/Y/emacron/space/ecaron/T/ecaron/V/ecaron/W/ecaron/Y/ecaron/space/edieresis/T/edieresis/V/edieresis/W/edieresis/Y/edieresis/space/rcaron/T/rcaron/V/rcaron/W/rcaron/Y/rcaron/space/ocircumflex/T/ocircumflex/V/ocircumflex/W/ocircumflex/Y/ocircumflex/space/odieresis/T/odieresis/V/odieresis/W/odieresis/Y/odieresis/space/omacron/T/omacron/V/omacron/W/omacron/Y/omacron/space/scaron/T/scaron/V/scaron/W/scaron/Y/scaron/space/umacron/T/umacron/V/umacron/W/umacron/Y/umacron/space/uring/T/uring/V/uring/W/uring/Y/uring/space/ydieresis/T/ydieresis/V/ydieresis/W/ydieresis/Y/ydieresis/space/ytilde/T/ytilde/V/ytilde/W/ytilde/Y/ytilde/space/zcaron/T/zcaron/V/zcaron/W/zcaron/Y/zcaron",
            "Impallari's Minimal Kerning Pairs": "/I/m/p/a/l/l/a/r/i/quotesingle/s/space/M/i/n/i/m/a/l/space/K/e/r/n/i/n/g/space/P/a/i/r/s/space/C/h/e/c/k/l/i/s/t\n\n\n/C/a/p/space/t/o/space/C/a/p\n\n/H/H/A/T/A/H/H/space/H/H/T/AE/H/H\n/H/H/A/U/A/H/H/space/H/H/U/AE/H/H\n/H/H/A/V/A/H/H/space/H/H/V/AE/H/H\n/H/H/A/W/A/H/H/space/H/H/W/AE/H/H\n/H/H/A/Y/A/H/H/space/H/H/Y/AE/H/H\n/H/H/A/O/A/H/H/space/H/H/A/Q/A/H/H/space/H/H/A/C/H/H/space/H/H/A/G/H/H/space/H/H/D/A/H/H\n/H/H/O/AE/H/H/space/H/H/D/AE/H/H/space/H/H/Q/AE/H/H\n/H/H/O/T/O/H/H/space/H/H/Q/T/Q/H/H/space/H/H/D/T/H/H/space/H/H/T/C/H/H/space/H/H/T/G/H/H\n/H/H/O/V/O/H/H/space/H/H/Q/V/Q/H/H/space/H/H/D/V/H/H/space/H/H/V/C/H/H/space/H/H/V/G/H/H\n/H/H/O/W/O/H/H/space/H/H/Q/W/Q/H/H/space/H/H/D/W/H/H/space/H/H/W/C/H/H/space/H/H/W/G/H/H\n/H/H/O/X/O/H/H/space/H/H/Q/X/Q/H/H/space/H/H/D/X/H/H/space/H/H/X/C/H/H/space/H/H/X/G/H/H\n/H/H/O/Y/O/H/H/space/H/H/Q/Y/Q/H/H/space/H/H/D/Y/H/H/space/H/H/Y/C/H/H/space/H/H/Y/G/H/H\n/H/H/K/O/H/H/space/H/H/K/C/H/H/space/H/H/K/G/H/H/space/H/H/K/Q/H/H\n/H/H/L/O/H/H/space/H/H/L/C/H/H/space/H/H/L/G/H/H/space/H/H/L/Q/H/H\n/H/H/E/O/H/H/space/H/H/E/C/H/H/space/H/H/E/G/H/H/space/H/H/E/Q/H/H\n/H/H/F/O/H/H/space/H/H/F/C/H/H/space/H/H/F/G/H/H/space/H/H/F/Q/H/H\n/H/H/F/A/H/H/space/H/H/F/AE/H/H\n/H/H/P/A/H/H/space/H/H/P/AE/H/H\n/H/H/S/Y/H/H/space/H/H/Y/S/H/H\n/H/H/B/T/H/H/space/H/H/L/T/H/H/space/H/H/R/T/H/H\n/H/H/B/V/H/H/space/H/H/L/V/H/H/space/H/H/P/V/H/H/space/H/H/R/V/H/H/space/H/H/G/V/H/H\n/H/H/B/W/H/H/space/H/H/L/W/H/H/space/H/H/P/W/H/H/space/H/H/R/W/H/H/space/H/H/G/W/H/H\n/H/H/B/X/H/H/space/H/H/L/X/H/H/space/H/H/P/X/H/H/space/H/H/R/X/H/H/space/H/H/G/X/H/H\n/H/H/B/Y/H/H/space/H/H/L/Y/H/H/space/H/H/P/Y/H/H/space/H/H/R/Y/H/H/space/H/H/G/Y/H/H\n/H/H/F/J/H/H/space/H/H/P/J/H/H/space/H/H/T/J/H/H/space/H/H/V/J/H/H/space/H/H/W/J/H/H/space/H/H/Y/J/H/H\n/H/H/L/U/H/H/space/H/H/R/U/H/H\n/H/H/A/A/H/H/space/H/H/L/A/H/H/space/H/H/R/A/H/H/space/H/H/K/A/H/H\n\n\n/C/a/p/space/t/o/space/L/o/w/e/r\n\n/F/a/n/n/o/n/space/K/a/n/n/o/n/space/P/a/n/n/o/n/space/T/a/n/n/o/n/space/V/a/n/n/o/n/space/W/a/n/n/o/n/space/Y/a/n/n/o/n\n/F/c/n/n/o/n/space/K/c/n/n/o/n/space/P/c/n/n/o/n/space/T/c/n/n/o/n/space/V/c/n/n/o/n/space/W/c/n/n/o/n/space/X/c/n/n/o/n/space/Y/c/n/n/o/n\n/F/d/n/n/o/n/space/K/d/n/n/o/n/space/P/d/n/n/o/n/space/T/d/n/n/o/n/space/V/d/n/n/o/n/space/W/d/n/n/o/n/space/X/d/n/n/o/n/space/Y/d/n/n/o/n\n/F/e/n/n/o/n/space/K/e/n/n/o/n/space/P/e/n/n/o/n/space/T/e/n/n/o/n/space/V/e/n/n/o/n/space/W/e/n/n/o/n/space/X/e/n/n/o/n/space/Y/e/n/n/o/n\n/F/q/n/n/o/n/space/K/q/n/n/o/n/space/P/q/n/n/o/n/space/T/q/n/n/o/n/space/V/q/n/n/o/n/space/W/q/n/n/o/n/space/X/q/n/n/o/n/space/Y/q/n/n/o/n\n/F/o/n/n/o/n/space/K/o/n/n/o/n/space/P/o/n/n/o/n/space/T/o/n/n/o/n/space/V/o/n/n/o/n/space/W/o/n/n/o/n/space/X/o/n/n/o/n/space/Y/o/n/n/o/n\n/F/g/n/n/o/n/space/K/g/n/n/o/n/space/P/g/n/n/o/n/space/T/g/n/n/o/n/space/V/g/n/n/o/n/space/W/g/n/n/o/n/space/X/g/n/n/o/n/space/Y/g/n/n/o/n\n/V/i/n/n/o/n/space/W/i/n/n/o/n/space/Y/i/n/n/o/n\n/T/m/n/n/o/n/space/V/m/n/n/o/n/space/W/m/n/n/o/n/space/Y/m/n/n/o/n\n/T/n/n/n/o/n/space/V/n/n/n/o/n/space/W/n/n/n/o/n/space/Y/n/n/n/o/n\n/T/p/n/n/o/n/space/V/p/n/n/o/n/space/W/p/n/n/o/n/space/Y/p/n/n/o/n\n/T/r/n/n/o/n/space/V/r/n/n/o/n/space/W/r/n/n/o/n/space/Y/r/n/n/o/n\n/T/s/n/n/o/n/space/V/s/n/n/o/n/space/W/s/n/n/o/n/space/Y/s/n/n/o/n\n/A/t/n/n/o/n/space/Y/t/n/n/o/n\n/F/u/n/n/o/n/space/K/u/n/n/o/n/space/T/u/n/n/o/n/space/V/u/n/n/o/n/space/W/u/n/n/o/n/space/Y/u/n/n/o/n/space/X/u/n/n/o/n\n/A/v/n/n/o/n/space/K/v/n/n/o/n/space/L/v/n/n/o/n/space/T/v/n/n/o/n/space/V/v/n/n/o/n/space/Y/v/n/n/o/n/space/X/v/n/n/o/n\n/A/w/n/n/o/n/space/K/w/n/n/o/n/space/L/w/n/n/o/n/space/T/w/n/n/o/n/space/V/w/n/n/o/n/space/Y/w/n/n/o/n/space/X/w/n/n/o/n\n/T/x/n/n/o/n/space/Y/x/n/n/o/n\n/A/y/n/n/o/n/space/K/y/n/n/o/n/space/L/y/n/n/o/n/space/T/y/n/n/o/n/space/V/y/n/n/o/n/space/W/y/n/n/o/n/space/Y/y/n/n/o/n/space/X/y/n/n/o/n\n/T/z/n/n/o/n/space/Y/z/n/n/o/n\n\n\n/L/o/w/e/r/space/t/o/space/L/o/w/e/r\n\n/n/o/n/a/v/n/o/n/space/n/o/n/v/a/n/o/n/space/n/o/n/a/w/n/o/n/space/n/o/n/w/a/n/o/n\n/n/o/n/o/v/o/n/o/n/space/n/o/n/c/v/c/n/o/n/space/n/o/n/e/v/e/n/o/n/space/n/o/n/b/v/d/n/o/n/space/n/o/n/p/v/q/n/o/n\n/n/o/n/o/w/o/n/o/n/space/n/o/n/c/w/c/n/o/n/space/n/o/n/e/w/e/n/o/n/space/n/o/n/b/w/d/n/o/n/space/n/o/n/p/w/q/n/o/n\n/n/o/n/o/x/o/n/o/n/space/n/o/n/c/x/c/n/o/n/space/n/o/n/e/x/e/n/o/n/space/n/o/n/b/x/d/n/o/n/space/n/o/n/p/x/q/n/o/n\n/n/o/n/o/y/o/n/o/n/space/n/o/n/c/y/c/n/o/n/space/n/o/n/e/y/e/n/o/n/space/n/o/n/b/y/d/n/o/n/space/n/o/n/p/y/q/n/o/n\n/n/o/n/k/o/n/o/n/space/n/o/n/k/c/n/o/n/space/n/o/n/k/e/n/o/n/space/n/o/n/k/d/n/o/n/space/n/o/n/k/q/n/o/n\n/n/o/n/r/a/n/o/n/space/n/o/n/r/o/n/o/n/space/n/o/n/r/c/n/o/n/space/n/o/n/r/e/n/o/n/space/n/o/n/r/d/n/o/n/space/n/o/n/r/q/n/o/n\n/n/o/n/o/f/o/n/o/n/space/n/o/n/c/f/c/n/o/n/space/n/o/n/e/f/e/n/o/n/space/n/o/n/b/f/d/n/o/n/space/n/o/n/p/f/q/n/o/n\n/n/o/n/o/t/o/n/o/n/space/n/o/n/c/t/c/n/o/n/space/n/o/n/e/t/e/n/o/n/space/n/o/n/b/t/d/n/o/n/space/n/o/n/p/t/q/n/o/n\n\n\n/C/a/p/s/space/a/n/d/space/p/u/n/c/t/u/a/t/i/o/n\n\n/H/H/quoteleft/A/H/H/space/H/H/A/quoteright/H/H/space/H/H/quoteright/A/H/H/space/H/H/quoteleft/O/H/H/space/H/H/O/quoteright/H/H/space/H/H/quoteright/O/H/H/space/H/H/L/quoteright/H/H\n/H/H/quotedblleft/A/H/H/space/H/H/A/quotedblright/H/H/space/H/H/quotedblright/A/H/H/space/H/H/quotedblleft/O/H/H/space/H/H/O/quotedblright/H/H/space/H/H/quotedblright/O/H/H/space/H/H/L/quotedblright/H/H\n/H/H/quotesingle/A/quotesingle/H/H/space/H/H/quotesingle/O/quotesingle/H/H/space/H/H/L/quotesingle/H/H/space/H/H/quotedbl/A/quotedbl/H/H/space/H/H/quotedbl/O/quotedbl/H/H/space/H/H/L/quotedbl/H/H\n/H/H/asterisk/A/asterisk/H/H/space/H/H/asterisk/O/asterisk/H/H/space/H/H/L/asterisk/H/H\n/H/H/period/O/period/H/H/space/H/H/period/T/period/H/H/space/H/H/period/U/period/H/H/space/H/H/period/V/period/H/H/space/H/H/period/W/period/H/H/space/H/H/period/Y/period/H/H\n/H/H/D/period/H/H/space/H/H/F/period/H/H/space/H/H/P/period/H/H\n/H/H/comma/O/comma/H/H/space/H/H/comma/T/comma/H/H/space/H/H/comma/U/comma/H/H/space/H/H/comma/V/comma/H/H/space/H/H/comma/W/comma/H/H/space/H/H/comma/Y/comma/H/H\n/H/H/D/comma/H/H/space/H/H/F/comma/H/H/space/H/H/P/comma/H/H\n/H/H/K/hyphen/H/H/space/H/H/L/hyphen/H/H\n/H/H/hyphen/T/hyphen/H/H/space/H/H/hyphen/V/hyphen/H/H/space/H/H/hyphen/W/hyphen/H/H/space/H/H/hyphen/X/hyphen/H/H/space/H/H/hyphen/Y/hyphen/H/H/space/H/H/hyphen/Z/hyphen/H/H\n/H/H/T/colon/H/H/space/H/H/V/colon/H/H/space/H/H/W/colon/H/H/space/H/H/Y/colon/H/H\n/H/H/T/semicolon/H/H/space/H/H/V/semicolon/H/H/space/H/H/W/semicolon/H/H/space/H/H/Y/semicolon/H/H\n/H/H/questiondown/J/H/H/space/H/H/exclamdown/J/H/H\n\n\n/L/o/w/e/r/space/a/n/d/space/p/u/n/c/t/u/a/t/i/o/n\n\n/n/n/period/f/period/n/n/space/n/n/period/o/period/n/n/space/n/n/period/v/period/n/n/space/n/n/period/w/period/n/n/space/n/n/period/y/period/n/n/space/n/n/r/period/n/n\n/n/n/comma/f/comma/n/n/space/n/n/comma/o/comma/n/n/space/n/n/comma/v/comma/n/n/space/n/n/comma/w/comma/n/n/space/n/n/comma/y/comma/n/n/space/n/n/r/comma/n/n\n/n/o/n/f/asterisk/n/o/n/space/n/o/n/f/question/n/o/n/space/n/o/n/parenleft/f/parenright/n/o/n/space/n/o/n/bracketleft/f/bracketright/n/o/n/space/n/o/n/braceleft/f/braceright/n/o/n\n/n/o/n/f/quotesingle/n/o/n/space/n/o/n/f/quotedbl/n/o/n/space/n/o/n/f/quoteright/n/o/n/space/n/o/n/f/quotedblright/n/o/n/space/n/o/n/f/quoteleft/n/o/n/space/n/o/n/f/quotedblleft/n/o/n\n/n/o/n/questiondown/j/n/o/n/space/n/o/n/parenleft/j/parenright/n/o/n/space/n/o/n/bracketleft/j/bracketright/n/o/n/space/n/o/n/braceleft/j/braceright/n/o/n\n/n/o/n/k/hyphen/n/o/n/space/n/o/n/r/hyphen/n/o/n/space/n/o/n/hyphen/x/hyphen/n/o/n\n/n/o/n/quoteright/s/n/o/n\n",
            "Cabarga's Kern King": "/S/o/u/r/c/e/colon/space/L/e/s/l/i/e/space/C/a/b/a/r/g/a/quotesingle/s/space/K/e/r/n/space/K/i/n/g\n\n/P/a/r/t/space/one/colon/space/A/l/l/space/L/o/w/e/r/c/a/s/e/space/hyphen/space/three/two/p/x\n\n/l/y/n/x/space/t/u/f/t/space/f/r/o/g/s/comma/space/d/o/l/p/h/i/n/s/space/a/b/d/u/c/t/space/b/y/space/p/r/o/x/y/space/t/h/e/space/e/v/e/r/space/a/w/k/w/a/r/d/space/k/l/u/t/z/comma/space/d/u/d/comma/space/d/u/m/m/k/o/p/f/comma/space/j/i/n/x/space/s/n/u/b/n/o/s/e/space/f/i/l/m/g/o/e/r/comma/space/o/r/p/h/a/n/space/s/g/t/period/space/r/e/n/f/r/u/w/space/g/r/u/d/g/e/k/space/r/e/y/f/u/s/comma/space/m/d/period/space/s/i/k/h/space/p/s/y/c/h/space/i/f/space/h/a/l/t/space/t/y/m/p/a/n/y/space/j/e/w/e/l/r/y/space/s/r/i/space/h/e/h/exclam/space/t/w/y/e/r/space/v/s/space/j/o/j/o/space/p/n/e/u/space/f/y/l/f/o/t/space/a/l/c/a/a/b/a/space/s/o/n/space/o/f/space/n/o/n/p/l/u/s/s/e/d/space/h/a/l/f/b/r/e/e/d/space/b/u/b/b/l/y/space/p/l/a/y/b/o/y/space/g/u/g/g/e/n/h/e/i/m/space/d/a/d/d/y/space/c/o/c/c/y/x/space/s/g/r/a/f/f/i/t/o/space/e/f/f/e/c/t/comma/space/v/a/c/u/u/m/space/d/i/r/n/d/l/e/space/i/m/p/o/s/s/i/b/l/e/space/a/t/t/e/m/p/t/space/t/o/space/d/i/s/v/a/l/u/e/comma/space/m/u/z/z/l/e/space/t/h/e/space/a/f/g/h/a/n/space/c/z/e/c/h/space/c/z/a/r/space/a/n/d/space/e/x/n/i/n/j/a/comma/space/b/o/b/space/b/i/x/b/y/space/d/v/o/r/a/k/space/w/o/o/d/space/d/h/u/r/r/i/e/space/s/a/v/v/y/comma/space/d/i/z/z/y/space/e/y/e/space/a/e/o/n/space/c/i/r/c/u/m/c/i/s/i/o/n/space/u/v/u/l/a/space/s/c/r/u/n/g/y/space/p/i/c/n/i/c/space/l/u/x/u/r/i/o/u/s/space/s/p/e/c/i/a/l/space/t/y/p/e/space/c/a/r/b/o/h/y/d/r/a/t/e/space/o/v/o/i/d/space/a/d/z/u/k/i/space/k/u/m/q/u/a/t/space/b/o/m/b/question/space/a/f/t/e/r/g/l/o/w/s/space/g/o/l/d/space/g/i/r/l/space/p/y/g/m/y/space/g/n/o/m/e/space/l/b/period/space/a/n/k/h/s/space/a/c/m/e/space/a/g/g/r/o/u/p/m/e/n/t/space/a/k/m/e/d/space/b/r/o/u/h/h/a/space/t/v/space/w/t/period/space/u/j/j/a/i/n/space/m/s/period/space/o/z/space/a/b/a/c/u/s/space/m/n/e/m/o/n/i/c/s/space/b/h/i/k/k/u/space/k/h/a/k/i/space/b/w/a/n/a/space/a/o/r/t/a/space/e/m/b/o/l/i/s/m/space/v/i/v/i/d/space/o/w/l/s/space/o/f/t/e/n/space/k/v/e/t/c/h/space/o/t/h/e/r/w/i/s/e/comma/space/w/y/s/i/w/y/g/space/d/e/n/s/f/o/r/t/space/w/r/i/g/h/t/space/y/o/u/quoteright/v/e/space/a/b/s/o/r/b/e/d/space/r/h/y/t/h/m/comma/space/p/u/t/space/o/b/s/t/a/c/l/e/space/k/y/a/k/s/space/k/r/i/e/g/space/k/e/r/n/space/w/u/r/s/t/space/s/u/b/j/e/c/t/space/e/n/m/i/t/y/space/e/q/u/i/t/y/space/c/o/q/u/e/t/space/q/u/o/r/u/m/space/p/i/q/u/e/space/t/z/e/t/s/e/space/h/e/p/z/i/b/a/h/space/s/u/l/f/h/y/d/r/y/l/space/b/r/i/e/f/c/a/s/e/space/a/j/a/x/space/e/h/l/e/r/space/k/a/f/k/a/space/f/j/o/r/d/space/e/l/f/s/h/i/p/space/h/a/l/f/d/r/e/s/s/e/d/space/j/u/g/f/u/l/space/e/g/g/c/u/p/space/h/u/m/m/i/n/g/b/i/r/d/s/space/s/w/i/n/g/d/e/v/i/l/space/b/a/g/p/i/p/e/space/l/e/g/w/o/r/k/space/r/e/p/r/o/a/c/h/f/u/l/space/h/u/n/c/h/b/a/c/k/space/a/r/c/h/k/n/a/v/e/space/b/a/g/h/d/a/d/space/w/e/j/h/space/r/i/j/s/w/i/j/k/space/r/a/j/b/a/n/s/i/space/r/a/j/p/u/t/space/a/j/d/i/r/space/o/k/a/y/space/w/e/e/k/d/a/y/space/o/b/f/u/s/c/a/t/e/space/s/u/b/p/o/e/n/a/space/l/i/e/b/k/n/e/c/h/t/space/m/a/r/c/g/r/a/v/i/a/space/e/c/b/o/l/i/c/space/a/r/c/t/i/c/w/a/r/d/space/d/i/c/k/c/i/s/s/e/l/space/p/i/n/c/p/i/n/c/space/b/o/l/d/f/a/c/e/space/m/a/i/d/k/i/n/space/a/d/j/e/c/t/i/v/e/space/a/d/c/r/a/f/t/space/a/d/m/a/n/space/d/w/a/r/f/n/e/s/s/space/a/p/p/l/e/j/a/c/k/space/d/a/r/k/b/r/o/w/n/space/k/i/l/n/space/p/a/l/z/y/space/a/l/w/a/y/s/space/f/a/r/m/l/a/n/d/space/f/l/i/m/f/l/a/m/space/u/n/b/o/s/s/y/space/n/o/n/l/i/n/e/a/l/space/s/t/e/p/b/r/o/t/h/e/r/space/l/a/p/d/o/g/space/s/t/o/p/g/a/p/space/s/x/space/c/o/u/n/t/d/o/w/n/space/b/a/s/k/e/t/b/a/l/l/space/b/e/a/u/j/o/l/a/i/s/space/v/b/period/space/f/l/o/w/c/h/a/r/t/space/a/z/t/e/c/space/l/a/z/y/space/b/o/z/o/space/s/y/r/u/p/space/t/a/r/z/a/n/space/a/n/n/o/y/i/n/g/space/d/y/k/e/space/y/u/c/k/y/space/h/a/w/g/space/g/a/g/z/h/u/k/z/space/c/u/z/c/o/space/s/q/u/i/r/e/space/w/h/e/n/space/h/i/h/o/space/m/a/y/h/e/m/space/n/i/e/t/z/s/c/h/e/space/s/z/a/s/z/space/g/u/m/d/r/o/p/space/m/i/l/k/space/e/m/p/l/o/t/m/e/n/t/space/a/m/b/i/d/e/x/t/r/o/u/s/l/y/space/l/a/c/q/u/e/r/space/b/y/w/a/y/space/e/c/c/l/e/s/i/a/s/t/e/s/space/s/t/u/b/c/h/e/n/space/h/o/b/g/o/b/l/i/n/s/space/c/r/a/b/m/i/l/l/space/a/q/u/a/space/h/a/w/a/i/i/space/b/l/v/d/period/space/s/u/b/q/u/a/l/i/t/y/space/b/y/z/a/n/t/i/n/e/space/e/m/p/i/r/e/space/d/e/b/t/space/o/b/v/i/o/u/s/space/c/e/r/v/a/n/t/e/s/space/j/e/k/a/b/z/e/e/l/space/a/n/e/c/d/o/t/e/space/f/l/i/c/f/l/a/c/space/m/e/c/h/a/n/i/c/v/i/l/l/e/space/b/e/d/b/u/g/space/c/o/u/l/d/n/quoteright/t/space/i/quoteright/v/e/space/i/t/quoteright/s/space/t/h/e/y/quoteright/l/l/space/t/h/e/y/quoteright/d/space/d/p/t/period/space/h/e/a/d/q/u/a/r/t/e/r/space/b/u/r/k/h/a/r/d/t/space/x/e/r/x/e/s/space/a/t/k/i/n/s/space/g/o/v/t/period/space/e/b/e/n/e/z/e/r/space/l/g/period/space/l/h/a/m/a/space/a/m/t/r/a/k/space/a/m/w/a/y/space/f/i/x/i/t/y/space/a/x/m/e/n/space/q/u/u/m/b/a/b/d/a/space/u/p/j/o/h/n/space/h/r/u/m/p/f\n\n/space\n/P/a/r/t/space/one/colon/space/A/l/l/space/U/p/p/e/r/c/a/s/e/space/hyphen/space/three/two/p/x\n\n/L/Y/N/X/space/T/U/F/T/space/F/R/O/G/S/comma/space/D/O/L/P/H/I/N/S/space/A/B/D/U/C/T/space/B/Y/space/P/R/O/X/Y/space/T/H/E/space/E/V/E/R/space/A/W/K/W/A/R/D/space/K/L/U/T/Z/comma/space/D/U/D/comma/space/D/U/M/M/K/O/P/F/comma/space/J/I/N/X/space/S/N/U/B/N/O/S/E/space/F/I/L/M/G/O/E/R/comma/space/O/R/P/H/A/N/space/S/G/T/period/space/R/E/N/F/R/U/W/space/G/R/U/D/G/E/K/space/R/E/Y/F/U/S/comma/space/M/D/period/space/S/I/K/H/space/P/S/Y/C/H/space/I/F/space/H/A/L/T/space/T/Y/M/P/A/N/Y/space/J/E/W/E/L/R/Y/space/S/R/I/space/H/E/H/exclam/space/T/W/Y/E/R/space/V/S/space/J/O/J/O/space/P/N/E/U/space/F/Y/L/F/O/T/space/A/L/C/A/A/B/A/space/S/O/N/space/O/F/space/N/O/N/P/L/U/S/S/E/D/space/H/A/L/F/B/R/E/E/D/space/B/U/B/B/L/Y/space/P/L/A/Y/B/O/Y/space/G/U/G/G/E/N/H/E/I/M/space/D/A/D/D/Y/space/C/O/C/C/Y/X/space/S/G/R/A/F/F/I/T/O/space/E/F/F/E/C/T/comma/space/V/A/C/U/U/M/space/D/I/R/N/D/L/E/space/I/M/P/O/S/S/I/B/L/E/space/A/T/T/E/M/P/T/space/T/O/space/D/I/S/V/A/L/U/E/comma/space/M/U/Z/Z/L/E/space/T/H/E/space/A/F/G/H/A/N/space/C/Z/E/C/H/space/C/Z/A/R/space/A/N/D/space/E/X/N/I/N/J/A/comma/space/B/O/B/space/B/I/X/B/Y/space/D/V/O/R/A/K/space/W/O/O/D/space/D/H/U/R/R/I/E/space/S/A/V/V/Y/comma/space/D/I/Z/Z/Y/space/E/Y/E/space/A/E/O/N/space/C/I/R/C/U/M/C/I/S/I/O/N/space/U/V/U/L/A/space/S/C/R/U/N/G/Y/space/P/I/C/N/I/C/space/L/U/X/U/R/I/O/U/S/space/S/P/E/C/I/A/L/space/T/Y/P/E/space/C/A/R/B/O/H/Y/D/R/A/T/E/space/O/V/O/I/D/space/A/D/Z/U/K/I/space/K/U/M/Q/U/A/T/space/B/O/M/B/question/space/A/F/T/E/R/G/L/O/W/S/space/G/O/L/D/space/G/I/R/L/space/P/Y/G/M/Y/space/G/N/O/M/E/space/L/B/period/space/A/N/K/H/S/space/A/C/M/E/space/A/G/G/R/O/U/P/M/E/N/T/space/A/K/M/E/D/space/B/R/O/U/H/H/A/space/T/V/space/W/T/period/space/U/J/J/A/I/N/space/M/S/period/space/O/Z/space/A/B/A/C/U/S/space/M/N/E/M/O/N/I/C/S/space/B/H/I/K/K/U/space/K/H/A/K/I/space/B/W/A/N/A/space/A/O/R/T/A/space/E/M/B/O/L/I/S/M/space/V/I/V/I/D/space/O/W/L/S/space/O/F/T/E/N/space/K/V/E/T/C/H/space/O/T/H/E/R/W/I/S/E/comma/space/W/Y/S/I/W/Y/G/space/D/E/N/S/F/O/R/T/space/W/R/I/G/H/T/space/Y/O/U/quoteright/V/E/space/A/B/S/O/R/B/E/D/space/R/H/Y/T/H/M/comma/space/P/U/T/space/O/B/S/T/A/C/L/E/space/K/Y/A/K/S/space/K/R/I/E/G/space/K/E/R/N/space/W/U/R/S/T/space/S/U/B/J/E/C/T/space/E/N/M/I/T/Y/space/E/Q/U/I/T/Y/space/C/O/Q/U/E/T/space/Q/U/O/R/U/M/space/P/I/Q/U/E/space/T/Z/E/T/S/E/space/H/E/P/Z/I/B/A/H/space/S/U/L/F/H/Y/D/R/Y/L/space/B/R/I/E/F/C/A/S/E/space/A/J/A/X/space/E/H/L/E/R/space/K/A/F/K/A/space/F/J/O/R/D/space/E/L/F/S/H/I/P/space/H/A/L/F/D/R/E/S/S/E/D/space/J/U/G/F/U/L/space/E/G/G/C/U/P/space/H/U/M/M/I/N/G/B/I/R/D/S/space/S/W/I/N/G/D/E/V/I/L/space/B/A/G/P/I/P/E/space/L/E/G/W/O/R/K/space/R/E/P/R/O/A/C/H/F/U/L/space/H/U/N/C/H/B/A/C/K/space/A/R/C/H/K/N/A/V/E/space/B/A/G/H/D/A/D/space/W/E/J/H/space/R/I/J/S/W/I/J/K/space/R/A/J/B/A/N/S/I/space/R/A/J/P/U/T/space/A/J/D/I/R/space/O/K/A/Y/space/W/E/E/K/D/A/Y/space/O/B/F/U/S/C/A/T/E/space/S/U/B/P/O/E/N/A/space/L/I/E/B/K/N/E/C/H/T/space/M/A/R/C/G/R/A/V/I/A/space/E/C/B/O/L/I/C/space/A/R/C/T/I/C/W/A/R/D/space/D/I/C/K/C/I/S/S/E/L/space/P/I/N/C/P/I/N/C/space/B/O/L/D/F/A/C/E/space/M/A/I/D/K/I/N/space/A/D/J/E/C/T/I/V/E/space/A/D/C/R/A/F/T/space/A/D/M/A/N/space/D/W/A/R/F/N/E/S/S/space/A/P/P/L/E/J/A/C/K/space/D/A/R/K/B/R/O/W/N/space/K/I/L/N/space/P/A/L/Z/Y/space/A/L/W/A/Y/S/space/F/A/R/M/L/A/N/D/space/F/L/I/M/F/L/A/M/space/U/N/B/O/S/S/Y/space/N/O/N/L/I/N/E/A/L/space/S/T/E/P/B/R/O/T/H/E/R/space/L/A/P/D/O/G/space/S/T/O/P/G/A/P/space/S/X/space/C/O/U/N/T/D/O/W/N/space/B/A/S/K/E/T/B/A/L/L/space/B/E/A/U/J/O/L/A/I/S/space/V/B/period/space/F/L/O/W/C/H/A/R/T/space/A/Z/T/E/C/space/L/A/Z/Y/space/B/O/Z/O/space/S/Y/R/U/P/space/T/A/R/Z/A/N/space/A/N/N/O/Y/I/N/G/space/D/Y/K/E/space/Y/U/C/K/Y/space/H/A/W/G/space/G/A/G/Z/H/U/K/Z/space/C/U/Z/C/O/space/S/Q/U/I/R/E/space/W/H/E/N/space/H/I/H/O/space/M/A/Y/H/E/M/space/N/I/E/T/Z/S/C/H/E/space/S/Z/A/S/Z/space/G/U/M/D/R/O/P/space/M/I/L/K/space/E/M/P/L/O/T/M/E/N/T/space/A/M/B/I/D/E/X/T/R/O/U/S/L/Y/space/L/A/C/Q/U/E/R/space/B/Y/W/A/Y/space/E/C/C/L/E/S/I/A/S/T/E/S/space/S/T/U/B/C/H/E/N/space/H/O/B/G/O/B/L/I/N/S/space/C/R/A/B/M/I/L/L/space/A/Q/U/A/space/H/A/W/A/I/I/space/B/L/V/D/period/space/S/U/B/Q/U/A/L/I/T/Y/space/B/Y/Z/A/N/T/I/N/E/space/E/M/P/I/R/E/space/D/E/B/T/space/O/B/V/I/O/U/S/space/C/E/R/V/A/N/T/E/S/space/J/E/K/A/B/Z/E/E/L/space/A/N/E/C/D/O/T/E/space/F/L/I/C/F/L/A/C/space/M/E/C/H/A/N/I/C/V/I/L/L/E/space/B/E/D/B/U/G/space/C/O/U/L/D/N/quoteright/T/space/I/quoteright/V/E/space/I/T/quoteright/S/space/T/H/E/Y/quoteright/L/L/space/T/H/E/Y/quoteright/D/space/D/P/T/period/space/H/E/A/D/Q/U/A/R/T/E/R/space/B/U/R/K/H/A/R/D/T/space/X/E/R/X/E/S/space/A/T/K/I/N/S/space/G/O/V/T/period/space/E/B/E/N/E/Z/E/R/space/L/G/period/space/L/H/A/M/A/space/A/M/T/R/A/K/space/A/M/W/A/Y/space/F/I/X/I/T/Y/space/A/X/M/E/N/space/Q/U/U/M/B/A/B/D/A/space/U/P/J/O/H/N/space/H/R/U/M/P/F\n\n/space\n/P/a/r/t/space/two/colon/space/M/o/s/t/space/C/o/m/m/o/n/space/I/n/i/t/i/a/l/space/C/a/p/s/space/hyphen/space/three/two/p/x\n\n/A/a/r/o/n/space/A/b/r/a/h/a/m/space/A/d/a/m/space/A/e/n/e/a/s/space/A/g/f/a/space/A/h/o/y/space/A/i/l/e/e/n/space/A/k/b/a/r/space/A/l/a/n/o/n/space/A/m/e/r/i/c/a/n/i/s/m/space/A/n/g/l/i/c/a/n/space/A/o/r/t/a/space/A/p/r/i/l/space/F/o/o/l/quoteright/s/space/D/a/y/space/A/q/u/a/space/L/u/n/g/space/parenleft/T/m/period/parenright/space/A/r/a/b/i/c/space/A/s/h/space/W/e/d/n/e/s/d/a/y/space/A/u/t/h/o/r/i/z/e/d/space/V/e/r/s/i/o/n/space/A/v/e/space/M/a/r/i/a/space/A/w/a/y/space/A/x/e/l/space/A/y/space/A/z/t/e/c/space/B/h/u/t/a/n/space/B/i/l/l/space/B/j/o/r/n/space/B/k/space/B/t/u/period/space/B/v/a/r/t/space/B/z/o/n/g/a/space/C/a/l/i/f/o/r/n/i/a/space/C/b/space/C/d/space/C/e/r/v/a/n/t/e/s/space/C/h/i/c/a/g/o/space/C/l/u/t/e/space/C/i/t/y/comma/space/T/x/period/space/C/m/d/r/period/space/C/n/o/s/s/u/s/space/C/o/c/o/space/C/r/a/c/k/e/r/space/S/t/a/t/e/comma/space/G/e/o/r/g/i/a/space/C/s/space/C/t/period/space/C/w/a/c/k/e/r/space/C/y/r/a/n/o/space/D/a/v/i/d/space/D/e/b/r/a/space/D/h/a/r/m/a/space/D/i/a/n/e/space/D/j/a/k/a/r/t/a/space/D/m/space/D/n/e/p/r/space/D/o/r/i/s/space/D/u/d/l/e/y/space/D/w/a/y/n/e/space/D/y/l/a/n/space/D/z/e/r/z/h/i/n/s/k/space/E/a/m/e/s/space/E/c/t/o/m/o/r/p/h/space/E/d/e/n/space/E/e/r/i/e/space/E/f/f/i/n/g/h/a/m/comma/space/I/l/period/space/E/g/y/p/t/space/E/i/f/f/e/l/space/T/o/w/e/r/space/E/j/e/c/t/space/E/k/l/a/n/d/space/E/l/m/o/r/e/space/E/n/t/r/e/a/t/y/space/E/o/l/i/a/n/space/E/p/s/t/e/i/n/space/E/q/u/i/n/e/space/E/r/a/s/m/u/s/space/E/s/k/i/m/o/space/E/t/h/i/o/p/i/a/space/E/u/r/o/p/e/space/E/v/a/space/E/w/a/n/space/E/x/o/d/u/s/space/J/a/n/space/v/a/n/space/E/y/c/k/space/E/z/r/a/space/F/a/b/i/a/n/space/F/e/b/r/u/a/r/y/space/F/h/a/r/a/space/F/i/f/i/space/F/j/o/r/d/space/F/l/o/r/i/d/a/space/F/m/space/F/r/a/n/c/e/space/F/s/space/F/t/period/space/F/u/r/y/space/F/y/n/space/G/a/b/r/i/e/l/space/G/c/space/G/d/y/n/i/a/space/G/e/h/r/i/g/space/G/h/a/n/a/space/G/i/l/l/i/g/a/n/space/K/a/r/l/space/G/j/e/l/l/e/r/u/p/space/G/k/period/space/G/l/e/n/space/G/m/space/G/n/o/s/i/s/space/G/p/period/E/period/space/G/r/e/g/o/r/y/space/G/s/space/G/t/period/space/B/r/period/space/G/u/i/n/e/v/e/r/e/space/G/w/a/t/h/m/e/y/space/G/y/p/s/y/space/G/z/a/g/s/space/H/e/b/r/e/w/space/H/f/space/H/g/space/H/i/l/e/a/h/space/H/o/r/a/c/e/space/H/r/d/l/i/c/k/a/space/H/s/i/a/space/H/t/s/period/space/H/u/b/e/r/t/space/H/w/a/n/g/space/H/a/i/space/H/y/a/c/i/n/t/h/space/H/z/period/space/I/a/c/c/o/c/a/space/I/b/s/e/n/space/I/c/e/l/a/n/d/space/I/d/a/h/o/space/I/f/space/I/g/g/y/space/I/h/r/e/space/I/j/i/t/space/I/k/e/space/I/l/i/a/d/space/I/m/m/e/d/i/a/t/e/space/I/n/n/o/c/e/n/t/space/I/o/n/e/space/I/p/s/w/i/t/c/h/space/I/q/u/a/r/u/s/space/I/r/e/l/a/n/d/space/I/s/l/a/n/d/space/I/t/space/I/u/d/space/I/v/e/r/t/space/I/w/e/r/k/s/space/I/x/n/a/y/space/I/y/space/J/a/s/p/e/r/space/J/e/n/k/s/space/J/h/e/r/r/y/space/J/i/l/l/space/J/m/space/J/n/space/J/o/r/g/e/space/J/r/period/space/J/u/l/i/e/space/K/e/r/r/y/space/K/h/a/r/m/a/space/K/i/k/i/space/K/l/e/a/r/space/K/o/k/o/space/K/r/u/s/e/space/K/u/s/a/c/k/space/K/y/l/i/e/space/L/a/b/o/e/space/L/b/period/space/L/e/s/l/i/e/space/L/h/i/h/a/n/e/space/L/l/a/m/a/space/L/o/r/r/i/e/space/L/t/period/space/L/u/c/y/space/L/y/l/e/space/M/a/d/e/i/r/a/space/M/e/c/h/a/n/i/c/space/M/g/period/space/M/i/n/n/i/e/space/M/o/r/r/i/e/space/M/r/period/space/M/s/period/space/M/t/period/space/M/u/s/i/c/space/M/y/space/N/a/n/n/y/space/N/e/l/l/i/e/space/N/i/l/l/i/e/space/N/o/v/o/c/a/n/e/space/N/u/l/l/space/N/y/a/c/k/space/O/a/k/space/O/b/l/i/q/u/e/space/O/c/c/a/r/i/n/a/space/O/d/d/space/O/e/d/i/p/u/s/space/O/f/f/space/O/g/m/a/n/e/space/O/h/i/o/space/O/i/l/space/O/j/space/O/k/l/a/h/o/m/a/space/O/l/i/o/space/O/m/n/i/space/O/n/l/y/space/O/o/p/s/space/O/p/e/r/a/space/O/q/u/space/O/r/d/e/r/space/O/s/t/r/a/space/O/t/t/m/a/r/space/O/u/t/space/O/v/u/m/space/O/w/space/O/x/space/O/y/s/t/e/r/space/O/z/space/P/a/r/a/d/e/space/P/d/period/space/P/e/p/e/space/P/f/i/s/t/e/r/space/P/g/period/space/P/h/i/l/space/P/i/p/p/i/space/P/j/space/P/l/e/a/s/e/space/P/n/e/u/m/o/n/i/a/space/P/o/r/r/i/d/g/e/space/P/r/i/c/e/space/P/s/a/l/m/space/P/t/period/space/P/u/r/p/l/e/space/P/v/space/P/w/space/P/y/r/e/space/Q/t/period/space/Q/u/i/n/c/y/space/R/a/d/i/o/space/R/d/period/space/R/e/d/space/R/h/e/a/space/R/i/g/h/t/space/R/j/space/R/o/c/h/e/space/R/r/space/R/s/space/R/t/period/space/R/u/r/a/l/space/R/w/a/n/d/a/space/R/y/d/e/r/space/S/a/c/r/i/f/i/c/e/space/S/e/r/i/e/s/space/S/g/r/a/f/f/i/t/o/space/S/h/i/r/t/space/S/i/s/t/e/r/space/S/k/e/e/t/space/S/l/o/w/space/S/m/o/r/e/space/S/n/o/o/p/space/S/o/o/n/space/S/p/e/c/i/a/l/space/S/q/u/i/r/e/space/S/r/space/S/t/period/space/S/u/z/y/space/S/v/e/l/t/e/space/S/w/i/s/s/space/S/y/space/S/z/a/c/h/space/T/d/space/T/e/a/c/h/space/T/h/e/r/e/space/T/i/t/l/e/space/T/o/t/a/l/space/T/r/u/s/t/space/T/s/e/n/a/space/T/u/l/i/p/space/T/w/i/c/e/space/T/y/l/e/r/space/T/z/e/a/n/space/U/a/space/U/d/d/e/r/space/U/e/space/U/f/space/U/g/h/space/U/h/space/U/i/space/U/k/space/U/l/space/U/m/space/U/n/k/e/m/p/t/space/U/o/space/U/p/space/U/q/space/U/r/s/u/l/a/space/U/s/e/space/U/t/m/o/s/t/space/U/v/u/l/a/space/U/w/space/U/x/u/r/i/o/u/s/space/U/z/germandbls/a/i/space/V/a/l/e/r/i/e/space/V/e/l/o/u/r/space/V/h/space/V/i/c/k/y/space/V/o/l/v/o/space/V/s/space/W/a/t/e/r/space/W/e/r/e/space/W/h/e/r/e/space/W/i/t/h/space/W/o/r/l/d/space/W/t/period/space/W/u/l/k/space/W/y/l/e/r/space/X/a/v/i/e/r/space/X/e/r/o/x/space/X/i/space/X/y/l/o/p/h/o/n/e/space/Y/a/b/o/e/space/Y/e/a/r/space/Y/i/p/e/s/space/Y/o/space/Y/p/s/i/l/a/n/t/space/Y/s/space/Y/u/space/Z/a/b/a/r/quoteright/s/space/Z/e/r/o/space/Z/h/a/n/e/space/Z/i/z/i/space/Z/o/r/r/o/space/Z/u/space/Z/y/space/D/o/n/quoteright/t/space/I/quoteright/l/l/space/I/quoteright/m/space/I/quoteright/s/e\n"
            
        }
    
        tools.testWordsLabel = vanilla.TextBox((15, y-40, 100, 20), "TEST WORDS", sizeStyle='small')
        y += 25
    
        tools.testWordsPopup = vanilla.PopUpButton((105, y-70, 190, 24), list(self.TEST_WORDS_COLLECTIONS.keys()))
        tools.testWordsButton = vanilla.Button((305, y-72, 120, 24), "Insert", callback=self.insertTestWordsCallback)
        y += 35
    
        tools.separator2 = vanilla.HorizontalLine((15, y-70, -15, 1))
        y += 20
    
        # SECTION 3: SCALE KERN BY PERCENTAGE
        tools.scaleLabel = vanilla.TextBox((15, y-75, 200, 20), "SCALE KERN BY PERCENTAGE", sizeStyle='small')
        y += 25
    
        tools.percentLabel = vanilla.TextBox((15, y-77, 80, 22), "Percentage:")
        tools.marginInput = vanilla.EditText((95, y-77, 60, 22), "40")
    
        tools.modeLabel = vanilla.TextBox((165, y-77, 70, 22), "Operation:")
        tools.modePopup = vanilla.PopUpButton((235, y-77, 100, 22), ["Increase", "Decrease"])
        y += 35
    
        tools.applyScaleButton = vanilla.Button((15, y-80, 200, 24), "Apply to Active Master", callback=self.applyScaleCallback)
        y += 40
    
        tools.separator3 = vanilla.HorizontalLine((15, y-80, -15, 1))
        y += 20
    
        # SECTION 4: KERNING PAIRS LISTER
        tools.listerLabel = vanilla.TextBox((15, y-80, 200, 20), "KERNING PAIRS LISTER", sizeStyle='small')
        y += 25
    
        # Prefix/Suffix controls
        tools.prefixLabel = vanilla.TextBox((15, y-80, 50, 22), "Prefix:")
        tools.prefixInput = vanilla.EditText((65, y-80, 80, 22), "HH")
    
        tools.suffixLabel = vanilla.TextBox((155, y-80, 50, 22), "Suffix:")
        tools.suffixInput = vanilla.EditText((205, y-80, 80, 22), "HH")
    
        tools.refreshPairsBtn = vanilla.Button((295, y-80, 80, 24), "Refresh", callback=self.refreshPairsList)
        y += 35
    
        # Search field
        tools.searchPairs = vanilla.EditText((15, y-80, 250, 24), placeholder="Search pairs...", callback=self.filterPairsList)
        tools.clearSearchBtn = vanilla.Button((275, y-80, 80, 24), "Clear", callback=self.clearPairsSearch)
        y += 35
    
        # Pairs list
        tools.pairsList = vanilla.List(
            (15, y-80, 410, 325),
            [],
            columnDescriptions=[
                {"title": "Left", "width": 130},
                {"title": "Right", "width": 130}, 
                {"title": "Value", "width": 80},
            ],
            allowsMultipleSelection=True,
            doubleClickCallback=self.showSelectedPairs
        )
        y += 190
    
        # Pairs per tab and buttons
        tools.pairsPerLabel = vanilla.TextBox((15, y+67, 80, 22), "Pairs/Tab:")
        tools.pairsPerInput = vanilla.EditText((95, y+65, 60, 22), "50")
    
        tools.listAllButton = vanilla.Button((165, y+65, 150, 24), "List All Pairs", callback=self.listAllPairsCallback)
        tools.closeTabsButton = vanilla.Button((325, y+65, 100, 24), "Close All Tabs", callback=self.closeAllTabsCallback)
        y += 35
    
        # Initialize caches for pairs lister
        self._allPairsTurbo = []
        self._currentDisplayPairsTurbo = []
        self._kerningCacheTurbo = {}
        self._keyCacheTurbo = {}
        self._productionCacheTurbo = {}
        self._graphicalCacheTurbo = {}

        self.w.open()
        self.updatePreview()
        self.refreshMargin(None)
    # -----------------------------
    # FUNCIONES DE CARGA
    # -----------------------------
    
    def loadDefaults(self):
        data = Glyphs.defaults.get(PREF)
        if data:
            self.sets = json.loads(data)
        else:
            self.sets = {}
    
    def saveDefaults(self):
        Glyphs.defaults[PREF] = json.dumps(self.sets)
    
    def loadNoKernDefaults(self):
        data = Glyphs.defaults.get(PREF_NO_KERN)
    
        def addGroup(existing, newGroup):
            groups = existing.splitlines() if existing else []
            if newGroup not in groups:
                groups.append(newGroup)
            return "\n".join(groups)

        if data:
            noKernData = json.loads(data)
            self._savedNoKernLeft = addGroup(noKernData.get("left", ""), "@n\n@h.sc")
            self._savedNoKernRight = addGroup(noKernData.get("right", ""), "@l\n@h.sc")
        else:
            self._savedNoKernLeft = "@H\n@n"
            self._savedNoKernRight = "@H\n@l"
    
    def saveNoKernDefaults(self):
        left_text = self.w.tabs[1].noKernLeft.get()
        right_text = self.w.tabs[1].noKernRight.get()
        data = {
            "left": left_text,
            "right": right_text
        }
        Glyphs.defaults[PREF_NO_KERN] = json.dumps(data)
        print("✅ No Kern settings saved")
    
    def loadExcludeDefaults(self):
        data = Glyphs.defaults.get(PREF_EXCLUDE)
        if data:
            excludeData = json.loads(data)
            self._savedExcludeFirst = excludeData.get("first", "")
            self._savedExcludeSecond = excludeData.get("second", "")
        else:
            self._savedExcludeFirst = ""
            self._savedExcludeSecond = "@H"
    
    def saveExcludeDefaults(self):
        data = {
            "first": self.w.tabs[1].excludeFirst.get(),
            "second": self.w.tabs[1].excludeSecond.get()
        }
        Glyphs.defaults[PREF_EXCLUDE] = json.dumps(data)
        print("✅ Exclude settings saved to defaults")
    
    def loadGapDefaults(self):
        data = Glyphs.defaults.get(PREF_GAP)
        if data:
            self.gapSpaces = data
        else:
            self.gapSpaces = 4
    
    def saveGapDefaults(self):
        Glyphs.defaults[PREF_GAP] = self.gapSpaces
    
    def loadExcludeExistingDefaults(self):
        data = Glyphs.defaults.get(PREF_EXCLUDE_EXISTING)
        if data is not None:
            self.excludeExisting = data
        else:
            self.excludeExisting = False
    
    def saveExcludeExistingDefaults(self):
        Glyphs.defaults[PREF_EXCLUDE_EXISTING] = self.excludeExisting
    
    def loadPrefixSuffixDefaults(self):
        prefix_data = Glyphs.defaults.get(PREF_PREFIX)
        if prefix_data is not None:
            self.prefix = prefix_data
        else:
            self.prefix = "HH"
        
        suffix_data = Glyphs.defaults.get(PREF_SUFFIX)
        if suffix_data is not None:
            self.suffix = suffix_data
        else:
            self.suffix = "HH"
        
        perline_data = Glyphs.defaults.get(PREF_PERLINE)
        if perline_data is not None:
            self.perline = perline_data
        else:
            self.perline = 6
    
    def savePrefixSuffixDefaults(self):
        Glyphs.defaults[PREF_PREFIX] = self.prefix
        Glyphs.defaults[PREF_SUFFIX] = self.suffix
        Glyphs.defaults[PREF_PERLINE] = self.perline
    
    def loadPositiveOnlyDefaults(self):
        data = Glyphs.defaults.get(PREF_POSITIVE_ONLY)
        if data is not None:
            self.positiveOnly = data
        else:
            self.positiveOnly = False
    
    def savePositiveOnlyDefaults(self):
        Glyphs.defaults[PREF_POSITIVE_ONLY] = self.positiveOnly
    
    def loadShowOnePerGroupDefaults(self):
        data = Glyphs.defaults.get(PREF_SHOW_ONE_PER_GROUP)
        if data is not None:
            self.showOnePerGroup = data
        else:
            self.showOnePerGroup = True
    
    def saveShowOnePerGroupDefaults(self):
        Glyphs.defaults[PREF_SHOW_ONE_PER_GROUP] = self.showOnePerGroup

    def loadContextualAffixesDefaults(self):
        data = Glyphs.defaults.get(PREF_CONTEXTUAL_AFFIXES)
        if data is not None:
            self.contextualAffixes = data
        else:
            self.contextualAffixes = True
    
    def saveContextualAffixesDefaults(self):
        Glyphs.defaults[PREF_CONTEXTUAL_AFFIXES] = self.contextualAffixes
    
    # -----------------------------
    # FUNCIONES PARA OBTENER VALORES ACTUALES
    # -----------------------------
    
    def getCurrentNoKernLeft(self):
        return self.w.tabs[1].noKernLeft.get()
    
    def getCurrentNoKernRight(self):
        return self.w.tabs[1].noKernRight.get()
    
    def getCurrentExcludeFirst(self):
        return self.w.tabs[1].excludeFirst.get()
    
    def getCurrentExcludeSecond(self):
        return self.w.tabs[1].excludeSecond.get()
    
    def getCurrentExcludeExisting(self):
        return self.w.tabs[1].excludeExistingCheck.get()
    
    def getCurrentPrefix(self):
        return self.w.tabs[1].prefix.get()
    
    def getCurrentSuffix(self):
        return self.w.tabs[1].suffix.get()
    
    def getCurrentPerLine(self):
        try:
            return int(self.w.tabs[1].perLine.get())
        except:
            return 6
    
    def getCurrentPositiveOnly(self):
        return self.w.tabs[1].positiveOnlyCheck.get()
    
    def getCurrentShowOnePerGroup(self):
        """Obtiene el valor actual del checkbox Show only one member per group."""
        try:
            value = self.w.tabs[1].showOnePerGroupCheck.get()
            print(f"📌 Show one per group: {value}")
            return value
        except:
            return self.showOnePerGroup
    
    def getCurrentContextualAffixes(self):
        return self.w.tabs[1].contextualAffixesCheck.get()
    
    # -----------------------------
    # FUNCIÓN: PREFIJOS/SUFIJOS CONTEXTUALES
    # -----------------------------
    
    def _get_contextual_affixes(self, left_glyph_name, right_glyph_name):
        font = Glyphs.font
        if not font:
            return self.getCurrentPrefix(), self.getCurrentSuffix()

        gL = font.glyphs[left_glyph_name]
        gR = font.glyphs[right_glyph_name]

        if not gL or not gR:
            return self.getCurrentPrefix(), self.getCurrentSuffix()

        if not self.getCurrentContextualAffixes():
            return self.getCurrentPrefix(), self.getCurrentSuffix()

        base_prefix = self.getCurrentPrefix()
        base_suffix = self.getCurrentSuffix()

        def case_for_glyph(g):
            if g.category == "Letter":
                if g.case == 1:
                    return "H"
                if g.case == 2:
                    return "h"
                if g.name and g.name[0].islower():
                    return "h"
                return "H"
            if g.category == "Number":
                return "H"
            if g.category == "Punctuation":
                return "h"
            if g.category == "Symbol":
                return "H"
            return "H"

        prefix_case = case_for_glyph(gL)
        suffix_case = case_for_glyph(gR)

        def apply_case(template, case_char):
            result = ""
            for c in template:
                if c in ("H", "h"):
                    result += case_char
                else:
                    result += c
            return result

        prefix = apply_case(base_prefix, prefix_case)
        suffix = apply_case(base_suffix, suffix_case)

        return prefix, suffix
    
    # -----------------------------
    # FUNCIÓN: DEDUPLICAR POR GRUPO
    # -----------------------------
    
    def _deduplicate_by_group(self, glyphs_list, position):
        """Elimina duplicados mostrando solo un miembro por grupo de kerning."""
        if not glyphs_list or not self.getCurrentShowOnePerGroup():
            return glyphs_list

        font = Glyphs.font
        if not font:
            return glyphs_list

        # Verificar si smcp está activo
        smcp_active = False
        tab = font.currentTab
        if tab and hasattr(tab, 'features'):
            smcp_active = 'smcp' in tab.features
            print(f"\n📌 Show one per group - smcp active: {smcp_active}")

        print(f"\n🔍 DEDUPLICATE BY GROUP [{position}]:")
        print(f"   Input glyphs: {glyphs_list}")
    
        seen = set()
        result = []
        debug_info = []

        for gname in glyphs_list:
            glyph = font.glyphs[gname]
            if not glyph:
                result.append(gname)
                continue

            # Si smcp está activo, buscar el glyph .sc correspondiente
            if smcp_active:
                sc_glyph_name = f"{gname}.sc"
                sc_glyph = font.glyphs[sc_glyph_name] if sc_glyph_name in font.glyphs else None
            
                if sc_glyph:
                    print(f"\n   Glyph '{gname}': found .sc version '{sc_glyph_name}'")
                
                    if position == "first":
                        # Para posición first, usar UNA CLAVE COMPUESTA de ambos lados
                        right_key = sc_glyph.rightKerningKey or 'none'
                        left_key = sc_glyph.leftKerningKey or 'none'
                        key = f"{right_key}|{left_key}"
                        print(f"   → Using COMPOUND key: right='{right_key}', left='{left_key}' → '{key}'")
                    else:
                        key = sc_glyph.leftKerningKey
                        group = sc_glyph.leftKerningGroup
                        print(f"   → Using .sc leftKerningKey: '{key}', leftKerningGroup: '{group}'")
                else:
                    print(f"\n   Glyph '{gname}': no .sc version found, using original")
                    if position == "first":
                        right_key = glyph.rightKerningKey or 'none'
                        left_key = glyph.leftKerningKey or 'none'
                        key = f"{right_key}|{left_key}"
                    else:
                        key = glyph.leftKerningKey
            else:
                # smcp no activo, usar glyph original
                if position == "first":
                    right_key = glyph.rightKerningKey or 'none'
                    left_key = glyph.leftKerningKey or 'none'
                    key = f"{right_key}|{left_key}"
                else:
                    key = glyph.leftKerningKey

            # Si no hay clave, usar el nombre
            if not key or key == 'none|none':
                key = gname
                print(f"   → Using glyph name as key: '{key}'")

            if key in seen:
                print(f"   → Key '{key}' already seen, skipping '{gname}'")
                continue
            
            seen.add(key)
            result.append(gname)
            debug_info.append(f"{gname} (key: {key})")

        print(f"\n   Result after deduplication: {result}")
        print(f"   Keys seen: {seen}")
        return result
    
    # -----------------------------
    # FUNCIÓN: OBTENER MIEMBROS DE GRUPO
    # -----------------------------
    
    def getKerningGroupMembers(self, glyph, side="left"):
        """Obtiene todos los miembros de un grupo de kerning (solo miembros exactos, excluyendo .ss, .sc, etc.)"""
        font = Glyphs.font
        if not font or not glyph:
            return []

        group = glyph.leftKerningGroup if side == "left" else glyph.rightKerningGroup
        if not group:
            return []

        # Usar cache
        cache_key = f"{group}_{side}"
        if cache_key in self._group_members_cache:
            return self._group_members_cache[cache_key]

        members = []
        group_clean = group.lstrip('@')
    
        for g in font.glyphs:
            if side == "left":
                grp = g.leftKerningGroup
            else:
                grp = g.rightKerningGroup
            
            if grp:
                grp_clean = grp.lstrip('@')
                # Solo incluir si el grupo es EXACTAMENTE igual
                # Esto excluirá automáticamente grupos como @A.ss, @A.sc, etc.
                if grp_clean == group_clean:
                    # Verificación adicional para excluir glyphs con sufijos problemáticos
                    glyph_name = g.name
                    # Excluir si tiene .ss, .sc, .alt, etc. en el nombre
                    if not any(suffix in glyph_name for suffix in ['.ss', '.sc', '.alt', '.ornm']):
                        members.append(g.name)

        members = sorted(set(members))
        self._group_members_cache[cache_key] = members
        return members
    
    # -----------------------------
    # FUNCIÓN: VERIFICAR KERNING POR GRUPOS
    # -----------------------------
    
    def _has_group_kerning_only(self, font, master_id, left_name, right_name):
        if left_name not in font.glyphs or right_name not in font.glyphs:
            return False

        left_glyph = font.glyphs[left_name]
        right_glyph = font.glyphs[right_name]

        kerning_dict = font.kerning.get(master_id, {})

        left_keys = {left_name}
        right_keys = {right_name}

        if left_glyph.rightKerningGroup:
            left_keys.add(f"@MMK_L_{left_glyph.rightKerningGroup}")

        if right_glyph.leftKerningGroup:
            right_keys.add(f"@MMK_R_{right_glyph.leftKerningGroup}")

        for lk in left_keys:
            if lk not in kerning_dict:
                continue
            rk_dict = kerning_dict.get(lk, {})
            for rk in right_keys:
                if rk in rk_dict:
                    return True
        return False
    
    # -----------------------------
    # FUNCIÓN: ELIMINAR KERNING EN BLOQUES #
    # -----------------------------
    
    def deleteKernInHashBlocks(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No font open")
            return

        tab = font.currentTab
        if not tab:
            print("❌ No tab open")
            return

        master_id = font.selectedFontMaster.id
        tab_text = tab.text or ""

        import re
        hash_matches = list(re.finditer(r'#([^#]+)#', tab_text))

        if not hash_matches:
            print("⚠️ No #...# blocks found in tab")
            return

        removed = 0
        protected = 0
        processed_pairs = set()

        for match in hash_matches:
            content = match.group(1).strip()
            if len(content) < 2:
                continue

            glyph_names = []
            for char in content:
                try:
                    g = font.glyphForCharacter_(ord(char))
                    if g:
                        glyph_names.append(g.name)
                    else:
                        if char in font.glyphs:
                            glyph_names.append(char)
                except:
                    if char in font.glyphs:
                        glyph_names.append(char)

            if len(glyph_names) < 2:
                continue

            for i in range(len(glyph_names) - 1):
                left = glyph_names[i]
                right = glyph_names[i + 1]

                if left not in font.glyphs or right not in font.glyphs:
                    continue

                pair_key = (left, right)
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)

                left_keys = {left}
                right_keys = {right}

                gL = font.glyphs[left]
                gR = font.glyphs[right]

                if gL and gL.rightKerningGroup:
                    left_keys.add(f"@MMK_L_{gL.rightKerningGroup}")
                if gR and gR.leftKerningGroup:
                    right_keys.add(f"@MMK_R_{gR.leftKerningGroup}")

                pair_removed = False
                for lk in left_keys:
                    for rk in right_keys:
                        try:
                            if font.kerningForPair(master_id, lk, rk) is not None:
                                font.removeKerningForPair(master_id, lk, rk)
                                removed += 1
                                pair_removed = True
                        except:
                            pass

                if not pair_removed:
                    protected += 1

        if master_id in self._kerningCache:
            del self._kerningCache[master_id]

        print(f"\n📊 DELETE KERN IN # BLOCKS")
        print(f"   Total pairs in blocks: {len(processed_pairs)}")
        print(f"   Pairs removed: {removed}")
        print(f"   Pairs without kerning: {protected}")
        self.refreshMargin(None)
    
    # -----------------------------
    # FUNCIÓN: #AV# - KERN SOLO EN BLOQUES #
    # -----------------------------
    
    def kernHashWordsCallback(self, sender=None):
        """Aplica kerning SOLO a los pares dentro de bloques #...#"""
        font = Glyphs.font
        if not font or not font.currentTab:
            print("❌ No font or tab open")
            return

        try:
            baseMargin = float(self.w.tabs[0].mValue.get())
        except Exception:
            print("❌ Invalid margin value")
            return

        tab = font.currentTab
        layers = [l for l in tab.layers if l and l.parent]
        if len(layers) < 2:
            return

        masterID = font.selectedFontMaster.id
        glyph_names = [l.parent.name for l in layers]

        def is_hash(name):
            return name.split(".")[0] == "numbersign"

        hash_positions = [i for i, n in enumerate(glyph_names) if is_hash(n)]

        if len(hash_positions) < 2:
            print("⚠️ Need at least two # symbols to define blocks")
            return

        applied = 0
        errors = 0

        for b in range(0, len(hash_positions) - 1, 2):
            start = hash_positions[b]
            end = hash_positions[b + 1]
            inner = glyph_names[start + 1 : end]

            if len(inner) < 2:
                continue

            for i in range(len(inner) - 1):
                left = inner[i]
                right = inner[i + 1]

                if left not in font.glyphs or right not in font.glyphs:
                    continue

                try:
                    no_kern_left, no_kern_right = self._get_no_kern_items()
                    if self._is_glyph_no_kern_for_position(left, no_kern_left, "first"):
                        continue
                    if self._is_glyph_no_kern_for_position(right, no_kern_right, "second"):
                        continue
                except:
                    errors += 1
                    continue

                try:
                    m = margin_for_pair(font, masterID, left, right)
                    if m is None or m >= 10000:
                        continue
                except:
                    errors += 1
                    continue

                needed = -(m - baseMargin)
                if needed >= 0:
                    continue

                k_value = int(round(needed))

                try:
                    gL = font.glyphs[left]
                    gR = font.glyphs[right]

                    left_key = left
                    right_key = right

                    if gL and gL.rightKerningGroup:
                        left_key = f"@MMK_L_{gL.rightKerningGroup}"
                    if gR and gR.leftKerningGroup:
                        right_key = f"@MMK_R_{gR.leftKerningGroup}"

                    font.setKerningForPair(masterID, left_key, right_key, k_value)
                    applied += 1
                except Exception as e:
                    errors += 1

        if masterID in self._kerningCache:
            del self._kerningCache[masterID]

        print(f"\n📊 #AV# SUMMARY")
        print(f"   Pairs kerned inside # blocks: {applied}")
        print(f"   Errors: {errors}")

        if applied > 0:
            self.refreshMargin(None)
    
    # -----------------------------
    # FUNCIÓN: @Tab - LISTAR MIEMBROS DEL GRUPO
    # -----------------------------
    
    def listKerningGroupMembersInNewTab(self, sender=None):
        """Lista todos los miembros del grupo de kerning del glifo a la derecha del cursor"""
        font = Glyphs.font
        if not font or not font.currentTab:
            print("❌ No font or tab open")
            return

        tab = font.currentTab
        layers = tab.layers
        cursor = tab.textCursor

        if cursor is None or not layers:
            print("❌ No cursor position")
            return

        if cursor >= len(layers) or cursor - 1 < 0:
            print("❌ Invalid cursor position")
            return

        right_glyph = layers[cursor].parent if layers[cursor] else None
        left_glyph = layers[cursor - 1].parent if layers[cursor - 1] else None

        if not left_glyph or not right_glyph:
            print("❌ No glyphs at cursor")
            return

        group_name = None
        group_side = None
        
        if right_glyph.leftKerningGroup:
            group_name = right_glyph.leftKerningGroup
            group_side = "left"
        elif right_glyph.rightKerningGroup:
            group_name = right_glyph.rightKerningGroup
            group_side = "right"

        if not group_name:
            print(f"⚠️ Glyph '{right_glyph.name}' has no kerning groups")
            return

        members = self.getKerningGroupMembers(right_glyph, group_side)
        if not members:
            print(f"⚠️ No members found for group {group_name}")
            return

        # Construir pares
        all_pairs = []

        for m in members:
            if m in font.glyphs:
                prefix, suffix = self._get_contextual_affixes(left_glyph.name, m)
                prefix_str = self.glyphString(prefix) if prefix else ""
                suffix_str = self.glyphString(suffix) if suffix else ""
                pair = f"{prefix_str}/{left_glyph.name}/{m}{suffix_str}"
                all_pairs.append(pair)

        all_pairs.append("")

        for m in members:
            if m in font.glyphs:
                prefix, suffix = self._get_contextual_affixes(m, left_glyph.name)
                prefix_str = self.glyphString(prefix) if prefix else ""
                suffix_str = self.glyphString(suffix) if suffix else ""
                pair = f"{prefix_str}/{m}/{left_glyph.name}{suffix_str}"
                all_pairs.append(pair)

        # Crear nuevo tab
        new_tab = font.newTab("")
        lines = []
        
        lines.append(f"M e m b e r s    @ {group_name}    ( {len(members)} )")
        lines.append("")

        perLine = self.getCurrentPerLine()
        try:
            gap_spaces = int(self.w.tabs[1].gapSpaces.get())
        except:
            gap_spaces = 4
        gap = " " * gap_spaces

        # Formatear en columnas
        for i in range(0, len(all_pairs), perLine):
            chunk = all_pairs[i:i + perLine]
            if chunk:
                line = chunk[0]
                for block in chunk[1:]:
                    line += gap + block
                lines.append(line)

        new_tab.text = "\n".join(lines)
        font.currentTab = new_tab
        
        # Activar feature seleccionada
        selectedFeature = self.getSelectedFeature()
        if selectedFeature and selectedFeature != "— None —":
            new_tab.features = [str(selectedFeature)]

        print(f"✅ Created tab with {len(members)} members of group {group_name}")
    
    # -----------------------------
    # FUNCIÓN PARA CERRAR TODOS LOS TABS
    # -----------------------------
    
    def closeAllTabs(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No font open")
            return
        
        tabs = font.tabs
        if not tabs:
            print("ℹ️ No tabs to close")
            return
        
        num_tabs = len(tabs)
        
        for i in range(num_tabs - 1, -1, -1):
            try:
                tab = tabs[i]
                tab.close()
            except:
                pass
        
        if len(font.tabs) == 0:
            print(f"✅ Closed all {num_tabs} tabs")
    
    # -----------------------------
    # FUNCIONES DE DEBUG
    # -----------------------------
    
    def debug(self, msg):
        if self.DEBUG:
            print(f"🔍 {msg}")
    
    # -----------------------------
    # FUNCIONES DE FEATURES
    # -----------------------------
    
    def getFeatureList(self):
        features = ["— None —"]
        font = Glyphs.font
        if font:
            for feature in font.features:
                if hasattr(feature, "name") and feature.name:
                    features.append(feature.name)
        return features
    
    def getSelectedFeature(self):
        idx = self.w.tabs[0].featureDropdown.get()
    
        if not hasattr(self, "featureList"):
            self.featureList = self.getFeatureList()
    
        if idx is not None and idx >= 0 and idx < len(self.featureList):
            feature = self.featureList[idx]
            if feature != "— None —":
                return str(feature)
    
        return None
    
    # -----------------------------
    # FUNCIONES DE NO KERN
    # -----------------------------
    
    def _get_no_kern_items(self):
        no_kern_left_items = set()
        no_kern_right_items = set()
        
        left_text = self.getCurrentNoKernLeft()
        right_text = self.getCurrentNoKernRight()
        
        for line in left_text.splitlines():
            item = line.strip()
            if item:
                no_kern_left_items.add(item)
                
        for line in right_text.splitlines():
            item = line.strip()
            if item:
                no_kern_right_items.add(item)
        
        return no_kern_left_items, no_kern_right_items

    def _is_glyph_no_kern_for_position(self, glyph_name, no_kern_items, position):
        font = Glyphs.font
        if not font or glyph_name not in font.glyphs:
            return False
        
        glyph = font.glyphs[glyph_name]
        
        if glyph_name in no_kern_items:
            return True
        
        if position == "first":
            group_to_check = glyph.rightKerningGroup
        else:
            group_to_check = glyph.leftKerningGroup
        
        if group_to_check:
            group_name_clean = group_to_check.lstrip('@')
            
            if f"@{group_name_clean}" in no_kern_items:
                return True
            if group_name_clean in no_kern_items:
                return True
        
        return False
    
    
    def deleteAllHashBlocks(self, sender):
        """Elimina solo los símbolos # que rodean los bloques, conservando el contenido interno"""
        font = Glyphs.font
        if not font:
            print("❌ No font open")
            return
    
        tab = font.currentTab
        if not tab:
            print("❌ No tab open")
            return
    
        import re
        tab_text = tab.text or ""
    
        # Buscar todos los bloques #...#
        hash_matches = list(re.finditer(r'#([^#]+)#', tab_text))
    
        if not hash_matches:
            print("⚠️ No #...# blocks found in tab")
            return
    
        # Eliminar solo los # que rodean los bloques, conservando el contenido
        # Esto reemplaza cada #contenido# por contenido (sin los #)
        new_text = re.sub(r'#([^#]+)#', r'\1', tab_text)
    
        # Actualizar el tab
        tab.text = new_text
    
        print(f"✅ Removed # symbols from {len(hash_matches)} block(s), content preserved")

    def deleteHashBlocksCallback(self, sender):
        """Callback para el botón #X"""
        self.deleteAllHashBlocks(sender)
        
            
                    
    # -----------------------------
    # FUNCIONES DE EXCLUSIÓN
    # -----------------------------
    
    def _parse_exclude_lines(self, raw_text, side_name):
        """Parsea las líneas de exclusión, separando glyphs y grupos.
        Ahora con debug para ver qué se está parseando."""
        glyphs = set()
        groups = set()
    
        print(f"\n🔍 DEBUG _parse_exclude_lines [{side_name}]:")
        print(f"   Raw text: '{raw_text}'")
    
        for line_num, line in enumerate(raw_text.splitlines()):
            txt = line.strip()
            if not txt:
                continue
            if txt.startswith("@"):
                groups.add(txt)
                print(f"   Line {line_num}: Added GROUP '{txt}'")
            else:
                glyphs.add(txt)
                print(f"   Line {line_num}: Added GLYPH '{txt}'")
    
        print(f"   Result: glyphs={glyphs}, groups={groups}")
        return glyphs, groups

    def _get_glyph_base(self, glyph_name):
        if not glyph_name:
            return ""
        return glyph_name.split('.')[0]

    def _get_glyph_variants(self, font, base_name):
        """Obtiene todas las variantes de un glyph base (con extensiones)."""
        variants = []
        base_lower = base_name.lower()
    
        print(f"\n🔍 DEBUG _get_glyph_variants for base '{base_name}':")
    
        for glyph in font.glyphs:
            name = glyph.name
            if name == base_name:
                continue
            
            # Dividir en base y extensión
            parts = name.split('.', 1)
            if len(parts) > 1 and parts[0] == base_name:
                variants.append(name)
                print(f"   Found variant (dot): {name}")
            # También verificar variantes sin punto (ej: Aacute, Agrave, etc.)
            elif name.startswith(base_name) and len(name) > len(base_name):
                rest = name[len(base_name):]
                if rest and rest[0].islower():
                    variants.append(name)
                    print(f"   Found variant (accent): {name}")
    
        print(f"   Total variants found: {len(variants)}")
        return variants

    def _glyph_belongs_to_group(self, glyph, group_name, position):
        """Verifica si un glyph pertenece a un grupo específico, considerando features activos."""
        print(f"\n🔍 DEBUG _glyph_belongs_to_group:")
        print(f"   Glyph: {glyph.name}")
        print(f"   Position: {position}")
        print(f"   Target group: '{group_name}'")
    
        # Verificar si el feature smcp está activo en el tab actual
        smcp_active = False
        tab = Glyphs.font.currentTab
        if tab and hasattr(tab, 'features'):
            smcp_active = 'smcp' in tab.features
            print(f"   Feature smcp active: {smcp_active}")
    
        # Obtener el grupo del glyph según la posición
        if position == "first":
            current_group = glyph.rightKerningGroup
            print(f"   Glyph's rightKerningGroup: '{current_group}'")
        else:
            current_group = glyph.leftKerningGroup
            print(f"   Glyph's leftKerningGroup: '{current_group}'")
    
        if not current_group:
            print("   No group assigned, returning False")
            return False
    
        # Limpiar @ de ambos
        current_clean = current_group.lstrip('@')
        target_clean = group_name.lstrip('@')
    
        print(f"   Clean glyph group: '{current_clean}'")
        print(f"   Clean target group: '{target_clean}'")
    
        # 1. Comparación exacta
        if current_clean == target_clean:
            print(f"   ✓ Exact match: {current_clean} == {target_clean}")
            return True
    
        # 2. Si smcp está activo, mapear minúsculas a sus equivalentes small caps
        if smcp_active:
            # Mapeo de grupos de minúsculas a grupos small caps
            lowercase_to_sc = {
                # leftKerningGroup (para posición second) mapeado a grupos small caps
                'a': 'a.sc',
                'b': 'h.sc',  # b minúscula → small caps group h.sc
                'c': 'o.sc',  # c minúscula → small caps group o.sc
                'd': 'o.sc',  # d minúscula → small caps group o.sc
                'e': 'h.sc',  # e minúscula → small caps group h.sc
                'f': 'h.sc',  # f minúscula → small caps group h.sc
                'g': 'o.sc',  # g minúscula → small caps group o.sc
                'h': 'h.sc',  # h minúscula → small caps group h.sc
                'i': 'i.sc',
                'j': 'j.sc',
                'k': 'k.sc',
                'l': 'l.sc',
                'm': 'm.sc',
                'n': 'h.sc',  # n minúscula → small caps group h.sc
                'o': 'o.sc',
                'p': 'h.sc',  # p minúscula → small caps group h.sc
                'q': 'o.sc',  # q minúscula → small caps group o.sc
                'r': 'r.sc',
                's': 's.sc',
                't': 't.sc',
                'u': 'u.sc',
                'v': 'v.sc',
                'w': 'w.sc',
                'x': 'x.sc',
                'y': 'y.sc',
                'z': 'z.sc',
            }
        
            if current_clean in lowercase_to_sc:
                sc_equivalent = lowercase_to_sc[current_clean]
                print(f"   With smcp active: {current_clean} → {sc_equivalent}")
            
                if sc_equivalent == target_clean:
                    print(f"   ✓ Target matches smcp equivalent: {target_clean}")
                    return True
            
                # También verificar si el target es la base del grupo small caps
                if target_clean.endswith('.sc'):
                    base_target = target_clean.replace('.sc', '')
                    if current_clean == base_target:
                        print(f"   ✓ Target small caps group matches base with smcp: {target_clean} → {base_target}")
                        return True


    def _is_glyph_excluded_for_position(self, glyphname, position):
        """Verifica si un glyph debe ser excluido de la generación de pares."""
        font = Glyphs.font
        if not font or glyphname not in font.glyphs:
            return False

        print(f"\n{'='*60}")
        print(f"🔍 CHECKING EXCLUSION: {glyphname} at position {position}")
        print(f"{'='*60}")

        # Verificar si smcp está activo
        smcp_active = False
        tab = font.currentTab
        if tab and hasattr(tab, 'features'):
            smcp_active = 'smcp' in tab.features
            print(f"📌 Feature smcp active: {smcp_active}")

        if position == "first":
            exclude_text = self.getCurrentExcludeFirst()
            print(f"Exclude First text: '{exclude_text}'")
        else:
            exclude_text = self.getCurrentExcludeSecond()
            print(f"Exclude Second text: '{exclude_text}'")

        exglyphs, exgroups = self._parse_exclude_lines(exclude_text, position)
        g = font.glyphs[glyphname]

        # 1. Verificar nombre exacto
        if glyphname in exglyphs:
            print(f"   ✓ Exact match found: '{glyphname}' in exglyphs")
            return True

        # 2. Verificar nombre base
        base_name = glyphname.split('.')[0]
        if base_name in exglyphs:
            print(f"   ✓ Base name match: '{base_name}' in exglyphs")
            return True

        # 3. Verificar variantes
        variants = self._get_glyph_variants(font, base_name)
        for variant in variants:
            if variant in exglyphs:
                print(f"   ✓ Variant match: '{variant}' in exglyphs")
                return True

        # 4. Verificar grupos de exclusión
        print(f"\n📌 Check 4: Group check")
        print(f"   Excluded groups: {exgroups}")
    
        # Obtener el grupo REAL del glyph
        if position == "first":
            current_group = g.rightKerningGroup
            print(f"   Glyph's rightKerningGroup: '{current_group}'")
        else:
            current_group = g.leftKerningGroup
            print(f"   Glyph's leftKerningGroup: '{current_group}'")
    
        # 5. NUEVO: Lista de exclusión específica para posición second con smcp
        if smcp_active and position == "second":
            # Glyphs que quieres excluir en posición second con smcp activado
            excluded_glyphs_with_smcp = {
                'e', 'r', 'p', 'd', 'f', 'h', 'k', 'l', 'b', 'n'
            }
        
            # Obtener el nombre base del glyph (sin extensiones)
            glyph_base = glyphname.split('.')[0]
        
            if glyph_base in excluded_glyphs_with_smcp:
                print(f"   ✓ Glyph '{glyphname}' (base: '{glyph_base}') excluded by smcp exclusion list")
                return True
    
        # Verificar grupos normalmente
        if current_group:
            group_clean = current_group.lstrip('@')
            for excluded_group in exgroups:
                excluded_clean = excluded_group.lstrip('@')
                if group_clean == excluded_clean:
                    print(f"   ✓ Group match: {group_clean} == {excluded_clean}")
                    return True

        print(f"\n❌ FINAL: '{glyphname}' is NOT excluded for position {position}")
        return False
        
                                        
    # -----------------------------
    # FUNCIONES DE UTILIDAD
    # -----------------------------
    
    def parseGlyphs(self, text):
        items = re.split(r"[,\s]+", text.strip())
        return [g for g in items if g]
        
    def _getPairsFromTab(self):
        font = Glyphs.font
        tab = font.currentTab
        pairs = []
        seen = set()

        if not tab:
            return pairs

        for layer in tab.layers:
            if not layer or not layer.parent or layer.parent.name == "space":
                continue

            if hasattr(layer, "nextKerning"):
                L = layer.parent.name
                R = layer.nextKerning.parent.name if layer.nextKerning else None
            else:
                continue

            if not R or R == "space":
                continue

            pair = (L, R)
            if pair not in seen:
                pairs.append(pair)
                seen.add(pair)

        return pairs
    
    def glyphString(self, text):
        if not text:
            return ""
        glyphs = []
        for char in text:
            glyphs.append(char)
        return "/" + "/".join(glyphs)
    
    def displayList(self):
        single_letter = []
        multi_letter = []

        for name in self.sets.keys():
            kings = self.parseGlyphs(self.sets[name]["kings"])
            subs = self.parseGlyphs(self.sets[name]["subdits"])
            count = len(kings) * len(subs)

            if len(kings) == 1 and len(kings[0]) == 1:
                single_letter.append(name)
            else:
                multi_letter.append(name)

        single_letter.sort()
        multi_letter.sort()
        self._orderedSetNames = single_letter + multi_letter

        items = []
        for name in self._orderedSetNames:
            kings = self.parseGlyphs(self.sets[name]["kings"])
            subs = self.parseGlyphs(self.sets[name]["subdits"])
            count = len(kings) * len(subs)
            items.append(f"{name} ({count})")

        return items
    
    def refreshList(self):
        self.w.tabs[0].list.set(self.displayList())
    
    def updatePreview(self):
        kings = self.parseGlyphs(self.w.tabs[0].kings.get())
        subs = self.parseGlyphs(self.w.tabs[0].subdits.get())
        count = len(kings) * len(subs)
        if self.w.tabs[0].mode.get() == 2:
            count *= 2
        self.w.tabs[0].preview.set(f"Pairs: {count}")
    
    def refreshMargin(self, sender):
        font = Glyphs.font
        if not font:
            self.w.tabs[0].resultLabel.set("margin: — • kern: —")
            return

        # 🔹 Llegir camps separats
        L = self.w.tabs[0].currentLeft.get().strip()
        R = self.w.tabs[0].currentRight.get().strip()

        if not L or not R:
            self.w.tabs[0].resultLabel.set("margin: — • kern: —")
            return

        # 🔹 Validar que existeixen al font
        if L not in font.glyphs or R not in font.glyphs:
            self.w.tabs[0].resultLabel.set("margin: — • kern: —")
            return

        try:
            mid = font.selectedFontMaster.id

            # Margin real
            m = margin_for_pair(font, mid, L, R)
            m_disp = "—" if m is None or m >= 10000 else f"{int(round(m))}"

            # Kerning (incloent grups)
            k = font.kerningForPair(mid, L, R)
            k_disp = f"{int(round(k))}" if k is not None else "—"

            self.w.tabs[0].resultLabel.set(f"margin: {m_disp} • kern: {k_disp}")

        except Exception as e:
            print("refreshMargin error:", e)
            self.w.tabs[0].resultLabel.set("margin: ERR • kern: —")
    # -----------------------------
    # FUNCIONES DE LA UI PRINCIPAL
    # -----------------------------
    
    def loadSet(self, sender):
        index = sender.getSelection()
        if not index:
            return
        name = self._orderedSetNames[index[0]]
        data = self.sets[name]
        self.w.tabs[0].setName.set(name)
        self.w.tabs[0].kings.set(data["kings"])
        self.w.tabs[0].subdits.set(data["subdits"])
        self.updatePreview()
    
    def addSet(self, sender):
        name = self.w.tabs[0].setName.get().strip()
        if not name:
            return
        kings = self.w.tabs[0].kings.get()
        subdits = self.w.tabs[0].subdits.get()
        if name in self.sets:
            answer = askYesNo("Set already exists.\nOverwrite existing set?")
            if not answer:
                return
        self.sets[name] = {"kings": kings, "subdits": subdits}
        self.saveDefaults()
        self.refreshList()
    
    def updateSet(self, sender):
        name = self.w.tabs[0].setName.get().strip()
        if name not in self.sets:
            return
        self.sets[name]["kings"] = self.w.tabs[0].kings.get()
        self.sets[name]["subdits"] = self.w.tabs[0].subdits.get()
        self.saveDefaults()
        self.refreshList()
    
    def deleteSet(self, sender):
        indexes = self.w.tabs[0].list.getSelection()
        if not indexes:
            return

        selected_names = [self._orderedSetNames[i] for i in indexes]

        if len(selected_names) == 1:
            msg = f"Delete set '{selected_names[0]}'?"
        else:
            msg = f"Delete {len(selected_names)} selected sets?"

        confirm = askYesNo(msg)
        if not confirm:
            return

        for name in selected_names:
            if name in self.sets:
                del self.sets[name]

        self.saveDefaults()
        self.refreshList()
        print(f"🗑️ Deleted {len(selected_names)} set(s)")
    
    def loadJSON(self, sender):
        panel = NSOpenPanel.openPanel()
        if panel.runModal():
            path = panel.URL().path()
            with open(path) as f:
                self.sets = json.load(f)
            self.saveDefaults()
            self.refreshList()
    
    def saveJSON(self, sender):
        panel = NSSavePanel.savePanel()
        if panel.runModal():
            path = panel.filename()
            with open(path, "w") as f:
                json.dump(self.sets, f, indent=4)
    
    # -----------------------------
    # FUNCIÓN: GENERATE FROM SELECTION
    # -----------------------------
    
    def generateFromSelection(self, sender):
        index = sender.getSelection()
        if not index:
            return

        name = self._orderedSetNames[index[0]]
        data = self.sets[name]

        self.w.tabs[0].setName.set(name)
        self.w.tabs[0].kings.set(data["kings"])
        self.w.tabs[0].subdits.set(data["subdits"])

        font = Glyphs.font
        if not font:
            return

        kings = self.parseGlyphs(data["kings"])
        subs = self.parseGlyphs(data["subdits"])

        validKings = [g for g in kings if font.glyphs[g]]
        validSubs = [g for g in subs if font.glyphs[g] and g not in validKings]

        if self.getCurrentShowOnePerGroup():
            validKings = self._deduplicate_by_group(validKings, "second")
            validSubs = self._deduplicate_by_group(validSubs, "first")

        perLine = self.getCurrentPerLine()
        exclude_existing = self.getCurrentExcludeExisting()
        master_id = font.selectedFontMaster.id
        mode = self.w.tabs[0].mode.get()

        try:
            gap_spaces = int(self.w.tabs[1].gapSpaces.get())
        except:
            gap_spaces = 4
        gap = " " * gap_spaces

        pairs_left = []
        pairs_right = []

        total_pairs = len(validKings) * len(validSubs)
        processed = 0

        print("\n" + "="*80)
        print("GENERATING PAIRS WITH EXCLUSION FILTERS")
        print("="*80)

        if hasattr(self.w.tabs[0], "progress"):
            self.w.tabs[0].progress.set(0)

        for k in validKings:
            for s in validSubs:
                processed += 1
                if total_pairs > 0 and hasattr(self.w.tabs[0], "progress"):
                    progress = int((processed / float(total_pairs)) * 100)
                    self.w.tabs[0].progress.set(progress)

                # LEFT MODE
                print(f"\n--- Processing pair: {s} (left) + {k} (right) ---")
                exclude_s_first = self._is_glyph_excluded_for_position(s, "first")
                exclude_k_second = self._is_glyph_excluded_for_position(k, "second")

                if not exclude_s_first and not exclude_k_second:
                    print(f"✅ Pair ACCEPTED for LEFT mode")
                    if exclude_existing:
                        if not self._has_group_kerning_only(font, master_id, s, k):
                            pairs_left.append((s, k))
                        else:
                            print(f"   But excluded because pair already has kerning")
                    else:
                        pairs_left.append((s, k))
                else:
                    print(f"❌ Pair REJECTED for LEFT mode")

                # RIGHT MODE
                print(f"\n--- Processing pair: {k} (left) + {s} (right) ---")
                exclude_k_first = self._is_glyph_excluded_for_position(k, "first")
                exclude_s_second = self._is_glyph_excluded_for_position(s, "second")

                if not exclude_k_first and not exclude_s_second:
                    print(f"✅ Pair ACCEPTED for RIGHT mode")
                    if exclude_existing:
                        if not self._has_group_kerning_only(font, master_id, k, s):
                            pairs_right.append((k, s))
                        else:
                            print(f"   But excluded because pair already has kerning")
                    else:
                        pairs_right.append((k, s))
                else:
                    print(f"❌ Pair REJECTED for RIGHT mode")

        pairs_left = list(dict.fromkeys(pairs_left))
        pairs_right = list(dict.fromkeys(pairs_right))

        print(f"\n{'='*80}")
        print(f"FINAL RESULTS:")
        print(f"Left pairs accepted: {len(pairs_left)}")
        print(f"Right pairs accepted: {len(pairs_right)}")
        print(f"{'='*80}")

        lines = []

        if mode == 0:
            if pairs_left:
                lines.extend(self.format_pairs_columns(pairs_left, perLine, gap))
        elif mode == 1:
            if pairs_right:
                lines.extend(self.format_pairs_columns(pairs_right, perLine, gap))
        else:
            if pairs_left:
                lines.extend(self.format_pairs_columns(pairs_left, perLine, gap))
            if pairs_left and pairs_right:
                lines.append("")
            if pairs_right:
                lines.extend(self.format_pairs_columns(pairs_right, perLine, gap))

        if not lines:
            print("❌ No pairs generated after filters")
            return

        text = "\n".join(lines)
        tab = font.newTab(text)

        selectedFeature = self.getSelectedFeature()
        if selectedFeature and selectedFeature != "— None —":
            tab.features = [selectedFeature]

        if hasattr(self.w.tabs[0], "progress"):
            self.w.tabs[0].progress.set(100)

        self.updatePreview()
        print(f"✅ Generated {len(pairs_left)} left pairs + {len(pairs_right)} right pairs")
    
    
    def format_pairs_columns(self, pairs, perLine, gap):
        """Formatea los pares en columnas para mostrarlos en el tab."""
        if not pairs:
            return []

        lines = []
    
        for i in range(0, len(pairs), perLine):
            chunk = pairs[i:i + perLine]
            line_parts = []

            for left, right in chunk:
                prefix, suffix = self._get_contextual_affixes(left, right)
                prefix_str = self.glyphString(prefix) if prefix else ""
                suffix_str = self.glyphString(suffix) if suffix else ""
                final_string = f"{prefix_str}/{left}/{right}{suffix_str}"
                line_parts.append(final_string)

            lines.append(gap.join(line_parts))

        return lines
    
    
    
    # -----------------------------
    # FUNCIÓN: DELETE TAB KERN
    # -----------------------------
    
    def deleteTabKern(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No font open")
            return
            
        tab = font.currentTab
        if not tab:
            print("❌ No tab open")
            return
            
        layers = tab.layers
        master_id = font.selectedFontMaster.id
        removed = 0
        seen = set()

        for i in range(len(layers) - 1):
            L = layers[i]
            R = layers[i + 1]
            if not L or not R:
                continue

            left = L.parent.name
            right = R.parent.name
            if left == "space" or right == "space":
                continue

            key = (left, right)
            if key in seen:
                continue
            seen.add(key)

            left_keys = {left}
            right_keys = {right}

            gL = font.glyphs[left] if left in font.glyphs else None
            gR = font.glyphs[right] if right in font.glyphs else None

            if gL and gL.rightKerningGroup:
                left_keys.add(f"@MMK_L_{gL.rightKerningGroup}")
            if gR and gR.leftKerningGroup:
                right_keys.add(f"@MMK_R_{gR.leftKerningGroup}")

            for lk in left_keys:
                for rk in right_keys:
                    try:
                        if font.kerningForPair(master_id, lk, rk) is not None:
                            font.removeKerningForPair(master_id, lk, rk)
                            removed += 1
                    except:
                        pass

        if master_id in self._kerningCache:
            del self._kerningCache[master_id]

        print(f"✔️ Removed {removed} kerning pairs from tab")
        self.refreshMargin(None)
    
    # -----------------------------
    # FUNCIÓN: KERN FROM SELECTED SET
    # -----------------------------
    
    def kernFromSelectedSet(self, sender):
        font = Glyphs.font
        tab = font.currentTab

        if not font or not tab:
            print("No font/tab")
            return

        masterID = font.selectedFontMaster.id

        try:
            targetMargin = float(self.w.tabs[0].mValue.get())
        except:
            print("Invalid margin")
            return

        positive_only = self.getCurrentPositiveOnly()
    
        if positive_only:
            print("\n🔧 MODE: POSITIVE KERNING")
        else:
            print("\n🔧 MODE: NEGATIVE KERNING")

        pairs = []
        seen = set()
    
        for i in range(len(tab.layers) - 1):
            L = tab.layers[i]
            R = tab.layers[i+1]

            if not L.parent or not R.parent:
                continue

            left = L.parent.name
            right = R.parent.name

            if left == "space" or right == "space":
                continue

            pair = (left, right)
            if pair not in seen:
                pairs.append(pair)
                seen.add(pair)

        no_kern_left, no_kern_right = self._get_no_kern_items()
    
        applied = 0
        skipped_no_kern = 0
        skipped_condition = 0
        skipped_no_margin = 0

        for Lname, Rname in pairs:
            if self._is_glyph_no_kern_for_position(Lname, no_kern_left, "first"):
                skipped_no_kern += 1
                continue
            
            if self._is_glyph_no_kern_for_position(Rname, no_kern_right, "second"):
                skipped_no_kern += 1
                continue

            current = margin_for_pair(font, masterID, Lname, Rname)

            if current is None or current >= 10000:
                skipped_no_margin += 1
                continue

            if positive_only:
                if current >= targetMargin:
                    skipped_condition += 1
                    continue
                delta = int(round(targetMargin - current))
            else:
                if current <= targetMargin:
                    skipped_condition += 1
                    continue
                delta = int(round(targetMargin - current))

            gL = font.glyphs[Lname]
            gR = font.glyphs[Rname]

            if positive_only:
                leftKey = Lname
                if gR.leftKerningGroup:
                    rightKey = f"@MMK_R_{gR.leftKerningGroup}"
                else:
                    rightKey = Rname
            else:
                leftKey = gL.rightKerningKey
                rightKey = gR.leftKerningKey

            font.setKerningForPair(masterID, leftKey, rightKey, delta)
            applied += 1

        print(f"\nSUMMARY")
        print(f"Mode: {'Positive' if positive_only else 'Negative'} kerning")
        print(f"Total pairs: {len(pairs)}")
        print(f"Kerned: {applied}")
        print(f"Skipped NoKern: {skipped_no_kern}")
        print(f"Skipped condition: {skipped_condition}")
        print(f"Skipped no margin: {skipped_no_margin}")
    
    # -----------------------------
    # FUNCIONES DE LA PESTAÑA SETTINGS
    # -----------------------------
    
    def saveNoKernSettings(self, sender):
        self.saveNoKernDefaults()
    
    def loadNoKernSettings(self, sender):
        self.loadNoKernDefaults()
        self.w.tabs[1].noKernLeft.set(self._savedNoKernLeft)
        self.w.tabs[1].noKernRight.set(self._savedNoKernRight)
        print("✅ No Kern settings loaded")
    
    def saveExcludeSettings(self, sender):
        self.saveExcludeDefaults()
    
    def loadExcludeSettings(self, sender):
        self.loadExcludeDefaults()
        self.w.tabs[1].excludeFirst.set(self._savedExcludeFirst)
        self.w.tabs[1].excludeSecond.set(self._savedExcludeSecond)
        print("✅ Exclude settings loaded from defaults")
    
    def saveExcludeToFile(self, sender):
        data = {
            "exclude_first": self.w.tabs[1].excludeFirst.get(),
            "exclude_second": self.w.tabs[1].excludeSecond.get()
        }
        panel = NSSavePanel.savePanel()
        panel.setAllowedFileTypes_(["json"])
        panel.setNameFieldStringValue_("exclude_settings.json")
        if panel.runModal():
            path = panel.URL().path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Exclude settings saved to {path}")
    
    def loadExcludeFromFile(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setAllowedFileTypes_(["json"])
        panel.setAllowsMultipleSelection_(False)
        if panel.runModal():
            path = panel.URLs()[0].path()
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.w.tabs[1].excludeFirst.set(data.get("exclude_first", ""))
            self.w.tabs[1].excludeSecond.set(data.get("exclude_second", ""))
            print(f"✅ Exclude settings loaded from {path}")
    
    def saveGapSettings(self, sender):
        try:
            self.gapSpaces = int(self.w.tabs[1].gapSpaces.get())
            self.saveGapDefaults()
            print(f"✅ Gap spaces saved: {self.gapSpaces}")
        except:
            print("❌ Invalid gap spaces value")
    
    def toggleExcludeExisting(self, sender):
        self.excludeExisting = sender.get()
        self.saveExcludeExistingDefaults()
        print(f"✅ Exclude existing pairs: {self.excludeExisting}")
    
    def savePrefixSuffix(self, sender):
        self.prefix = self.w.tabs[1].prefix.get()
        self.suffix = self.w.tabs[1].suffix.get()
        try:
            self.perline = int(self.w.tabs[1].perLine.get())
        except:
            self.perline = 6
        self.savePrefixSuffixDefaults()
        print(f"✅ Settings saved: Prefix='{self.prefix}', Suffix='{self.suffix}', Per line={self.perline}")
    
    def togglePositiveOnly(self, sender):
        self.positiveOnly = sender.get()
        self.savePositiveOnlyDefaults()
        print(f"✅ Positive only: {self.positiveOnly}")
    
    def toggleShowOnePerGroup(self, sender):
        self.showOnePerGroup = sender.get()
        self.saveShowOnePerGroupDefaults()
        print(f"✅ Show only one member per group: {self.showOnePerGroup}")
    
    def toggleContextualAffixes(self, sender):
        self.contextualAffixes = sender.get()
        self.saveContextualAffixesDefaults()
        print(f"✅ Contextual affixes: {self.contextualAffixes}")

    # ===================================================
    # TOOLS METHODS (Kern Coach Tools)
    # ===================================================

    # ---------- GROUPS GENERATOR METHODS ----------

    def editGroupText(self, sender):
        """Ensure group text starts with @"""
        text = sender.get()
        if text and not text.startswith('@'):
            sender.set('@' + text)

    def getAllGlyphs(self):
        """Get all glyphs in the font."""
        Font = Glyphs.font
        if not Font:
            self.showInfo("Error: No font open")
            return None
        return Font.glyphs

    def showInfo(self, message):
        """Update info text in Tools tab."""
        self.w.tabs[2].groupInfoText.set(message)

    def clearKerningGroups(self, glyph):
        """Remove LSB and RSB groups from a glyph."""
        glyph.leftKerningGroup = None
        glyph.rightKerningGroup = None

    # Uppercase LSB groups
    uppercase_lsb_groups = {
        'A': ['A'],
        'O': ['O', 'Q', 'C', 'G'],
        'H': ['H', 'E', 'R', 'I', 'P', 'D', 'F', 'K', 'L', 'N', 'B', 'Dcroat', 'Hbar', 'Germandbls'],
        'M': ['M'],
        'V': ['V'],
        'W': ['W'],
        'T': ['T', 'Tcommaaccent'],
        'Y': ['Y'],
        'U': ['U'],
        'S': ['S'],
        'J': ['J'],
        'Z': ['Z'],
        'X': ['X'],
    }

    # Uppercase RSB groups
    uppercase_rsb_groups = {
        'H': ['H', 'N', 'M', 'E', 'I', 'Hbar'],
        'M': ['M'],
        'O': ['Q', 'O', 'D', 'Schwa', 'thorn', 'Dcroat', 'Oslashacute'],
        'C': ['C'],
        'W': ['W'],
        'R': ['R'],
        'T': ['T', 'Tcommaaccent'],
        'Y': ['Y'],
        'U': ['U', 'J', 'IJ'],
        'P': ['P'],
        'A': ['A', 'AEacute'],
        'E': ['E'],
        'S': ['S'],
        'F': ['F'],
        'G': ['G'],
        'K': ['K'],
        'L': ['L'],
        'Z': ['Z'],
        'X': ['X'],
        'V': ['V'],
        'B': ['B'],
        'C': ['C'],
        'Germandbls': ['Germandbls'],
    }

    # Lowercase LSB groups
    lowercase_lsb_groups = {
        'a': ['a', 'aeacute'],
        'l': ['l', 'b', 'h', 'k', 'thorn', 'lcaron', 'germandbls', 'hbar', 'fl', ],
        'o': ['o', 'c', 'd', 'e', 'g', 'q', 'dcaron', 'dcroat', 'oslashacute'],
        'f': ['f', 'longs', 'fi', 'fl'],
        'i': ['i', 'idotless', 'idblgrave', 'fi'],
        'j': ['j', 'jdotless'],
        'n': ['n', 'm', 'p', 'r', 'kgreenlandic'],
        's': ['s'],
        't': ['t'],
        'u': ['u'],
        'v': ['v'],
        'w': ['w'],
        'x': ['x'],
        'y': ['y'],
        'z': ['z'],
        'eth': ['eth'],
        'quoteright': [],
        'quotesingle': ['napostrophe'],
    }

    # Lowercase RSB groups
    lowercase_rsb_groups = {
        'a': ['a'],
        'o': ['o', 'e', 'p', 'b', 'thorn', 'dcaron', 'oslashacute', 'aeacute'],
        'c': ['c'],
        'l': ['l', 'd', 'dcroat', 'hbar', 'fl'],
        'f': ['f', 'longs'],
        'u': ['u', 'g', 'q'],
        'n': ['n', 'h', 'm', 'napostrophe', 'kgreenlandic'],
        'i': ['i', 'idotless', 'idblgrave', 'fi'],
        'j': ['j', 'jdotless'],
        'k': ['k', 'kgreenlandic'],
        'r': ['r'],
        's': ['s'],
        't': ['t'],
        'v': ['v'],
        'w': ['w'],
        'x': ['x'],
        'y': ['y'],
        'z': ['z'],
        'eth': ['eth'],
        'quoteright': ['lcaron', 'tcaron'],
        'quotesingle': ['dcaron', 'tcaron'],
        'Germandbls': ['germandbls'],
    }

    # Punctuation groups
    punctuation_groups = {
        'period': ['period', 'comma', 'ellipsis', 'quotesinglbase', 'quotedblbase'],
        'colon': ['colon', 'semicolon'],
        'periodcentered': ['periodcentered', 'bullet'],
        'hyphen': ['hyphen', 'endash', 'emdash'],
        'parenleft': ['parenleft', 'braceleft', 'bracketleft'],
        'parenright': ['parenright', 'braceright', 'bracketright'],
        'quoteleft': ['quoteleft', 'quotedblleft'],
        'quoteright': ['quoteright', 'quotedblright'],
        'guilsinglleft': ['guilsinglleft', 'guillemetleft'],
        'guilsinglright': ['guilsinglright', 'guillemetright'],
        'quotesingle': ['quotesingle', 'quotedbl'],
    }

    # Punctuation .sc groups
    punctuation_sc_groups = {
        'period.sc': ['period.sc', 'comma.sc', 'ellipsis.sc', 'quotesinglbase.sc', 'quotedblbase.sc'],
        'colon.sc': ['colon.sc', 'semicolon.sc'],
        'periodcentered.sc': ['periodcentered.sc', 'bullet.sc'],
        'hyphen.sc': ['hyphen.sc', 'endash.sc', 'emdash.sc'],
        'parenleft.sc': ['parenleft.sc', 'braceleft.sc', 'bracketleft.sc'],
        'parenright.sc': ['parenright.sc', 'braceright.sc', 'bracketright.sc'],
        'quoteleft.sc': ['quoteleft.sc', 'quotedblleft.sc'],
        'quoteright.sc': ['quoteright.sc', 'quotedblright.sc'],
        'guilsinglleft.sc': ['guilsinglleft.sc', 'guillemetleft.sc'],
        'guilsinglright.sc': ['guilsinglright.sc', 'guillemetright.sc'],
        'quotesingle.sc': ['quotesingle.sc', 'quotedbl.sc'],
    }

    # Diacritics that should go to nokern group
    diacritics_list = [
        'dieresiscomb', 'dotaccentcomb', 'gravecomb', 'acutecomb', 'hungarumlautcomb',
        'circumflexcomb', 'caroncomb', 'brevecomb', 'ringcomb', 'tildecomb', 'macroncomb',
        'dblgravecomb', 'breveinvertedcomb', 'commaturnedabovecomb', 'dotbelowcomb',
        'commaaccentcomb', 'cedillacomb', 'ogonekcomb', 'slashshortcomb', 'slashlongcomb',
        'ringcomb.001', 'cedillacomb.001',
        'dieresiscomb.case', 'dotaccentcomb.case', 'gravecomb.case', 'acutecomb.case',
        'hungarumlautcomb.case', 'circumflexcomb.case', 'caroncomb.case', 'brevecomb.case',
        'ringcomb.case', 'tildecomb.case', 'macroncomb.case', 'dblgravecomb.case',
        'breveinvertedcomb.case', 'strokeshortcomb.case', 'strokelongcomb.case',
        'commaaccentcomb.loclMAH',
        'dieresiscomb.sc', 'dotaccentcomb.sc', 'gravecomb.sc', 'acutecomb.sc',
        'hungarumlautcomb.sc', 'circumflexcomb.sc', 'caroncomb.sc', 'brevecomb.sc',
        'ringcomb.sc', 'tildecomb.sc', 'macroncomb.sc', 'dblgravecomb.sc',
        'dieresis', 'dotaccent', 'grave', 'acute', 'hungarumlaut', 'circumflex',
        'caron', 'breve', 'ring', 'tilde', 'macron', 'cedilla', 'ogonek'
    ]

    # Diacritic suffixes for name analysis
    diacritic_suffixes = [
        'invertedbreve', 'hungarumlaut', 'circumflex', 'dieresis',
        'dotaccent', 'dotbelow', 'macron', 'ogonek', 'cedilla',
        'breve', 'caron', 'grave', 'acute', 'tilde', 'ring',
        'hook', 'horn', 'stroke', 'dblgrave', 'commaaccent', 'bar', 'slash', 'slashacute'
    ]

    # Letters sensitive to angle analysis for .ss
    angle_sensitive_letters = ['A', 'W', 'V', 'Y', 'X', 'K']

    # Base to .sc group mapping
    base_to_sc_group = {
        'a': ('a.sc', 'a.sc'),
        'b': ('h.sc', 'b.sc'),
        'c': ('o.sc', 'c.sc'),
        'd': ('h.sc', 'o.sc'),
        'e': ('h.sc', 'h.sc'),
        'f': ('h.sc', 'f.sc'),
        'g': ('o.sc', 'g.sc'),
        'h': ('h.sc', 'h.sc'),
        'i': ('h.sc', 'h.sc'),
        'j': ('j.sc', 'u.sc'),
        'k': ('h.sc', 'k.sc'),
        'l': ('h.sc', 'l.sc'),
        'm': ('h.sc', 'h.sc'),
        'm_inclined': ('m.sc', 'm.sc'),
        'n': ('h.sc', 'h.sc'),
        'o': ('o.sc', 'o.sc'),
        'p': ('h.sc', 'p.sc'),
        'q': ('o.sc', 'o.sc'),
        'r': ('h.sc', 'r.sc'),
        's': ('s.sc', 's.sc'),
        't': ('t.sc', 't.sc'),
        'u': ('u.sc', 'u.sc'),
        'v': ('v.sc', 'v.sc'),
        'w': ('w.sc', 'w.sc'),
        'x': ('x.sc', 'x.sc'),
        'y': ('y.sc', 'y.sc'),
        'z': ('z.sc', 'z.sc'),
        'ae': ('a.sc', 'e.sc'),
        'oe': ('o.sc', 'e.sc'),
        'eth': ('h.sc', 'o.sc'),
        'thorn': ('h.sc', 'thorn.sc'),
        'germandbls': ('l.sc', 'germandbls.sc'),
    }

    def getGlyphAngle(self, glyph):
        """
        Calculate main angle of a glyph.
        Returns average angle or None if cannot determine.
        """
        if not glyph.layers or not glyph.layers[0]:
            return None
        
        layer = glyph.layers[0]
        paths = layer.paths
        
        if not paths:
            return None
        
        angles = []
        
        for path in paths:
            nodes = path.nodes
            for i in range(len(nodes)):
                node = nodes[i]
                next_node = nodes[(i + 1) % len(nodes)]
                
                if node.type != OFFCURVE and next_node.type != OFFCURVE:
                    dx = next_node.x - node.x
                    dy = next_node.y - node.y
                    
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 50:
                        angle = abs(math.degrees(math.atan2(dy, dx))) % 180
                        if angle > 90:
                            angle = 180 - angle
                        
                        if 30 <= angle <= 60 or 120 <= angle <= 150:
                            angles.append(angle)
        
        if not angles:
            return None
        
        return sum(angles) / len(angles)

    def hasVerticalStem(self, glyph):
        """
        Detect if glyph has vertical stems.
        Returns True if significantly vertical.
        """
        if not glyph.layers or not glyph.layers[0]:
            return False
        
        layer = glyph.layers[0]
        paths = layer.paths
        
        if not paths:
            return False
        
        vertical_count = 0
        total_count = 0
        
        for path in paths:
            nodes = path.nodes
            for i in range(len(nodes)):
                node = nodes[i]
                next_node = nodes[(i + 1) % len(nodes)]
                
                if node.type != OFFCURVE and next_node.type != OFFCURVE:
                    dx = next_node.x - node.x
                    dy = next_node.y - node.y
                    
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 50:
                        angle = abs(math.degrees(math.atan2(dy, dx))) % 180
                        if angle > 90:
                            angle = 180 - angle
                        
                        total_count += 1
                        if 80 <= angle <= 100:
                            vertical_count += 1
        
        if total_count == 0:
            return False
        
        return (vertical_count / total_count) > 0.3

    def getBaseGlyphName(self, glyphName):
        """
        Extract base name from a glyph with diacritics.
        """
        suffixes = sorted(self.diacritic_suffixes, key=len, reverse=True)
        
        for suffix in suffixes:
            if glyphName.endswith(suffix):
                base = glyphName[:-len(suffix)]
                return base
        
        return glyphName

    def hasInclinedStem(self, glyph):
        """
        Detect if M has inclined stems.
        Returns True if inclined, False if vertical.
        """
        if not glyph.layers or not glyph.layers[0]:
            return False
        
        layer = glyph.layers[0]
        paths = layer.paths
        
        if not paths:
            return False
        
        angles = []
        
        for path in paths:
            nodes = path.nodes
            for i in range(len(nodes)):
                node = nodes[i]
                next_node = nodes[(i + 1) % len(nodes)]
                
                if node.type != OFFCURVE and next_node.type != OFFCURVE:
                    dx = next_node.x - node.x
                    dy = next_node.y - node.y
                    
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 50:
                        angle = abs(math.degrees(math.atan2(dy, dx))) % 180
                        if angle > 90:
                            angle = 180 - angle
                        
                        if 70 <= angle <= 110:
                            angles.append(angle)
        
        if not angles:
            return False
        
        avg_angle = sum(angles) / len(angles)
        is_inclined = abs(avg_angle - 90) > 5
        
        return is_inclined

    def getBaseLetterFromGlyphName(self, glyphName):
        """
        Extract the base letter from a .sc glyph name.
        Example: 'ecircumflex.sc' -> 'e'
                 'idotless.sc' -> 'i'
                 'ae.sc' -> 'ae'
        """
        if '.sc' in glyphName:
            nameWithoutSc = glyphName.replace('.sc', '')
        else:
            nameWithoutSc = glyphName
        
        if nameWithoutSc in ['ae', 'oe', 'eth', 'thorn', 'germandbls']:
            return nameWithoutSc
        
        for suffix in self.diacritic_suffixes:
            if nameWithoutSc.endswith(suffix):
                return nameWithoutSc[:-len(suffix)]
        
        if len(nameWithoutSc) == 1 and nameWithoutSc.isalpha():
            return nameWithoutSc
        
        return nameWithoutSc

    def assignScGroups(self, glyph):
        """
        Assign groups to .sc glyphs according to specific rules.
        All .sc glyphs inherit from their base letter's .sc groups.
        """
        glyphName = glyph.name
        baseLetter = self.getBaseLetterFromGlyphName(glyphName)
        
        if baseLetter == 'm' and glyphName == 'm.sc':
            has_incline = self.hasInclinedStem(glyph)
            if has_incline:
                glyph.leftKerningGroup = 'm.sc'
                glyph.rightKerningGroup = 'm.sc'
                return
        
        if baseLetter in self.base_to_sc_group:
            lsb, rsb = self.base_to_sc_group[baseLetter]
            glyph.leftKerningGroup = lsb
            glyph.rightKerningGroup = rsb
            return
        
        if baseLetter == 'ae':
            glyph.leftKerningGroup = 'a.sc'
            glyph.rightKerningGroup = 'e.sc'
            return
            
        if baseLetter == 'ae':
            glyph.leftKerningGroup = 'a.sc'
            glyph.rightKerningGroup = 'e.sc'
            return
            
        
        if baseLetter == 'oe':
            glyph.leftKerningGroup = 'o.sc'
            glyph.rightKerningGroup = 'e.sc'
            return
        
        if baseLetter == 'eth' 'thorn':
            glyph.leftKerningGroup = 'h.sc'
            glyph.rightKerningGroup = 'o.sc'
            return
        
        if baseLetter == 'thorn':
            glyph.leftKerningGroup = 'h.sc'
            glyph.rightKerningGroup = 'thorn.sc'
            return
        
        if baseLetter == 'germandbls':
            glyph.leftKerningGroup = 'l'
            glyph.rightKerningGroup = 'germandbls'
            return
            
        if baseLetter == 'adblgrave':
            glyph.leftKerningGroup = 'a.sc'
            glyph.rightKerningGroup = 'a.sc'
            return
        
        glyph.leftKerningGroup = '' + glyphName.lower()
        glyph.rightKerningGroup = '' + glyphName.lower()

    def assignDiacriticGlyph(self, glyph):
        """
        Assign groups to a glyph with diacritic based on first letter.
        Used for glyphs that might have been missed.
        """
        glyphName = glyph.name
        
        if '.sc' in glyphName:
            self.assignScGroups(glyph)
            return
        
        firstLetter = glyphName[0] if glyphName else ''
        is_uppercase = firstLetter.isupper()
        
        if is_uppercase:
            for group, members in self.uppercase_lsb_groups.items():
                if firstLetter in members or firstLetter.upper() in members:
                    glyph.leftKerningGroup = group
                    break
            for group, members in self.uppercase_rsb_groups.items():
                if firstLetter in members or firstLetter.upper() in members:
                    glyph.rightKerningGroup = group
                    break
        else:
            for group, members in self.lowercase_lsb_groups.items():
                if firstLetter in members:
                    glyph.leftKerningGroup = group
                    break
            for group, members in self.lowercase_rsb_groups.items():
                if firstLetter in members:
                    glyph.rightKerningGroup = group
                    break
        
        if not glyph.leftKerningGroup:
            glyph.leftKerningGroup = '' + glyphName
        if not glyph.rightKerningGroup:
            glyph.rightKerningGroup = '' + glyphName

    def assignKerningGroups(self, glyph):
        """Assign LSB and RSB groups to a glyph according to rules."""
        glyphName = glyph.name
        
        # --- First: Check if it's a diacritic (goes to nokern) ---
        if glyphName in self.diacritics_list:
            glyph.leftKerningGroup = 'nokern'
            glyph.rightKerningGroup = 'nokern'
            return True
        
        # --- Second: Regular punctuation ---
        for group, members in self.punctuation_groups.items():
            if glyphName in members:
                glyph.leftKerningGroup = group
                glyph.rightKerningGroup = group
                return True
        
        # --- Third: Punctuation .sc ---
        if '.sc' in glyphName:
            for group, members in self.punctuation_sc_groups.items():
                if glyphName in members:
                    glyph.leftKerningGroup = group
                    glyph.rightKerningGroup = group
                    return True
        
        # --- Fourth: .ornm ---
        if '.ornm' in glyphName:
            groupName = '' + glyphName
            glyph.leftKerningGroup = groupName
            glyph.rightKerningGroup = groupName
            return True
        
        # --- Fifth: .sc (small caps) - specific rules ---
        if '.sc' in glyphName:
            self.assignScGroups(glyph)
            return True
        
        # --- Sixth: .ss (stylistic sets) ---
        if '.ss' in glyphName:
            baseName = glyphName.split('.')[0]
    
            if glyph.layers and glyph.layers[0].components:
                self.assignComponentGlyphGroups(glyph)
                return True
    
            if baseName in self.angle_sensitive_letters:
                baseGlyph = Glyphs.font.glyphs[baseName]
                if baseGlyph:
                    baseAngle = self.getGlyphAngle(baseGlyph)
                    ssAngle = self.getGlyphAngle(glyph)
            
                    if baseAngle is not None and ssAngle is not None:
                        angleDiff = abs(baseAngle - ssAngle)
                
                        if angleDiff > 3:
                            # Asignar grupos regulares basados en el nombre base, NO crear @grupo
                            self.assignRegularGlyphGroups(glyph)
                            return True
    
            if baseName == 'B':
                baseGlyph = Glyphs.font.glyphs[baseName]
                if baseGlyph:
                    baseVertical = self.hasVerticalStem(baseGlyph)
                    ssVertical = self.hasVerticalStem(glyph)
            
                    if baseVertical != ssVertical:
                        # Asignar grupos regulares basados en el nombre base, NO crear @grupo
                        self.assignRegularGlyphGroups(glyph)
                        return True
    
            found_lsb = False
            found_rsb = False
    
            for group, members in self.uppercase_lsb_groups.items():
                if baseName in members:
                    glyph.leftKerningGroup = group
                    found_lsb = True
                    break
    
            for group, members in self.uppercase_rsb_groups.items():
                if baseName in members:
                    glyph.rightKerningGroup = group
                    found_rsb = True
                    break
    
            if not found_lsb:
                for group, members in self.lowercase_lsb_groups.items():
                    if baseName in members:
                        glyph.leftKerningGroup = group
                        found_lsb = True
                        break
    
            if not found_rsb:
                for group, members in self.lowercase_rsb_groups.items():
                    if baseName in members:
                        glyph.rightKerningGroup = group
                        found_rsb = True
                        break
    
            if not found_lsb and not found_rsb:
                # Si no se encuentra en ningún grupo, asignar grupos regulares basados en el nombre base
                self.assignRegularGlyphGroups(glyph)
            return True
            
                            
        # --- Seventh: Special glyph rules ---
        special_rules = {
            'aeacute': ('a', 'o'),
            'fi': ('f', 'i'),
            'fl': ('f', 'l'),
            'AEacute': ('A', 'H'),
            'Dcroat': ('H', 'O'),
            'Hbar': ('H', 'H'),
            'Oslashacute': ('O', 'O'),
            'Germandbls': ('H', 'Germandbls'),
            'Tcommaaccent': ('T', 'T'),
            'dcaron': ('o', 'quotesingle'),
            'dcroat': ('o', 'l'),
            'hbar': ('l', 'n'),
            'i': ('i', 'i'),
            'idotless': ('i', 'i'),
            'idblgrave': ('i', 'i'),
            'j': ('j', 'j'),
            'jdotless': ('j', 'j'),
            'kgreenlandic': ('n', 'k'),
            'lcaron': ('l', 'quoteright'),
            'oslashacute': ('o', 'o'),
            'germandbls': ('l', 'Germandbls'),
            'Schwa': ('O', 'O'),
            'eth': ('eth', 'eth'),
            'napostrophe': ('quotesingle', 'n'),
            'longs': ('f', 'f'),
            'tcaron': ('l', 'quotesingle'),
            'thorn': ('l', 'o'),
            'Thorn': ('H', 'Thorn'),
            'IJ': ('H', 'U'),
            'Tdotbelow': ('T', 'T'),
            'ddotbelow': ('o', 'l'),
            'y': ('v', 'v'),
            'q': ('o', 'u'),
        }
        
        if glyphName in special_rules:
            lsb, rsb = special_rules[glyphName]
            glyph.leftKerningGroup = lsb
            glyph.rightKerningGroup = rsb
            return True
        
        # --- Uppercase M special case ---
        if glyphName == 'M' or glyphName.startswith('M.') or (glyphName.startswith('M') and not glyphName[1:].isalpha()):
            has_incline = self.hasInclinedStem(glyph)
            if has_incline:
                glyph.leftKerningGroup = 'M'
                glyph.rightKerningGroup = 'M'
            else:
                glyph.leftKerningGroup = 'M'
                glyph.rightKerningGroup = 'H'
            return True
        
        # --- Glyphs with diacritics (base name detection) ---
        baseName = self.getBaseGlyphName(glyphName)
        if baseName != glyphName:
            if glyph.layers and glyph.layers[0].components:
                self.assignComponentGlyphGroups(glyph)
                return True
            
            found_lsb = False
            found_rsb = False
            
            for group, members in self.uppercase_lsb_groups.items():
                if baseName in members:
                    glyph.leftKerningGroup = group
                    found_lsb = True
                    break
            
            for group, members in self.uppercase_rsb_groups.items():
                if baseName in members:
                    glyph.rightKerningGroup = group
                    found_rsb = True
                    break
            
            if not found_lsb:
                for group, members in self.lowercase_lsb_groups.items():
                    if baseName in members:
                        glyph.leftKerningGroup = group
                        found_lsb = True
                        break
            
            if not found_rsb:
                for group, members in self.lowercase_rsb_groups.items():
                    if baseName in members:
                        glyph.rightKerningGroup = group
                        found_rsb = True
                        break
            
            if found_lsb or found_rsb:
                return True
        
        # --- Ligatures ---
        if '.' not in glyphName and ('_' in glyphName or glyphName in ['AE', 'OE']):
            self.assignLigatureGroups(glyph)
            return True
        
        # --- Glyphs with components ---
        if glyph.layers and glyph.layers[0].components:
            self.assignComponentGlyphGroups(glyph)
            return True
        
        # --- Regular glyphs ---
        self.assignRegularGlyphGroups(glyph)
        return True

    def assignRegularGlyphGroups(self, glyph):
        """Assign groups to a normal glyph based on dictionaries."""
        glyphName = glyph.name
        
        found_lsb = False
        found_rsb = False
        
        for group, members in self.uppercase_lsb_groups.items():
            if glyphName in members:
                glyph.leftKerningGroup = group
                found_lsb = True
                break
        
        for group, members in self.uppercase_rsb_groups.items():
            if glyphName in members:
                glyph.rightKerningGroup = group
                found_rsb = True
                break
        
        if not found_lsb:
            for group, members in self.lowercase_lsb_groups.items():
                if glyphName in members:
                    glyph.leftKerningGroup = group
                    found_lsb = True
                    break
        
        if not found_rsb:
            for group, members in self.lowercase_rsb_groups.items():
                if glyphName in members:
                    glyph.rightKerningGroup = group
                    found_rsb = True
                    break
        
        if not found_lsb and not found_rsb:
            groupName = '' + glyphName
            glyph.leftKerningGroup = groupName
            glyph.rightKerningGroup = groupName

    def assignLigatureGroups(self, glyph):
        """Assign groups to a ligature (LSB of first letter, RSB of last letter)."""
        glyphName = glyph.name
        components = []
        
        if glyphName == 'AE':
            components = ['A', 'E']
        elif glyphName == 'OE':
            components = ['O', 'E']
        elif '_' in glyphName:
            components = glyphName.split('_')
        else:
            self.assignRegularGlyphGroups(glyph)
            return
        
        if not components or len(components) < 2:
            self.assignRegularGlyphGroups(glyph)
            return
        
        firstComp = components[0]
        lastComp = components[-1]
        
        lsbGroup = None
        for group, members in self.uppercase_lsb_groups.items():
            if firstComp in members:
                lsbGroup = group
                break
        if not lsbGroup:
            for group, members in self.lowercase_lsb_groups.items():
                if firstComp in members:
                    lsbGroup = group
                    break
        
        rsbGroup = None
        for group, members in self.uppercase_rsb_groups.items():
            if lastComp in members:
                rsbGroup = group
                break
        if not rsbGroup:
            for group, members in self.lowercase_rsb_groups.items():
                if lastComp in members:
                    rsbGroup = group
                    break
        
        if lsbGroup:
            glyph.leftKerningGroup = lsbGroup
        if rsbGroup:
            glyph.rightKerningGroup = rsbGroup
            
        if not lsbGroup and not rsbGroup:
            glyph.leftKerningGroup = '@' + firstComp
            glyph.rightKerningGroup = '@' + lastComp

    def assignComponentGlyphGroups(self, glyph):
        """Assign groups to a component glyph based on main component (Y > 250)."""
        glyphName = glyph.name
        
        if not glyph.layers or not glyph.layers[0].components:
            self.assignRegularGlyphGroups(glyph)
            return
        
        masterLayer = glyph.layers[0]
        bestComponent = None
        highestY = -float('inf')
        
        for component in masterLayer.components:
            compPos = component.position
            if compPos:
                yPos = compPos.y
                if yPos > highestY and yPos > 250:
                    highestY = yPos
                    bestComponent = component
        
        if not bestComponent:
            highestY = -float('inf')
            for component in masterLayer.components:
                if component.position:
                    yPos = component.position.y
                    if yPos > highestY:
                        highestY = yPos
                        bestComponent = component
            if not bestComponent and masterLayer.components:
                bestComponent = masterLayer.components[0]
        
        if bestComponent and bestComponent.componentName:
            motherGlyphName = bestComponent.componentName
            motherGlyph = Glyphs.font.glyphs[motherGlyphName]
            
            if motherGlyph:
                lsbGroup = motherGlyph.leftKerningGroup
                rsbGroup = motherGlyph.rightKerningGroup
                
                if not lsbGroup:
                    for group, members in self.uppercase_lsb_groups.items():
                        if motherGlyphName in members:
                            lsbGroup = group
                            break
                    if not lsbGroup:
                        for group, members in self.lowercase_lsb_groups.items():
                            if motherGlyphName in members:
                                lsbGroup = group
                                break
                
                if not rsbGroup:
                    for group, members in self.uppercase_rsb_groups.items():
                        if motherGlyphName in members:
                            rsbGroup = group
                            break
                    if not rsbGroup:
                        for group, members in self.lowercase_rsb_groups.items():
                            if motherGlyphName in members:
                                rsbGroup = group
                                break
                
                if lsbGroup:
                    glyph.leftKerningGroup = lsbGroup
                if rsbGroup:
                    glyph.rightKerningGroup = rsbGroup
            else:
                glyph.leftKerningGroup = '' + glyphName
                glyph.rightKerningGroup = '' + glyphName
        else:
            glyph.leftKerningGroup = '' + glyphName
            glyph.rightKerningGroup = '' + glyphName

    def checkAllGlyphsAssigned(self):
        """Check if all glyphs have groups assigned."""
        Font = Glyphs.font
        if not Font:
            return True
        
        for glyph in Font.glyphs:
            if not glyph.leftKerningGroup and not glyph.rightKerningGroup:
                return False
        return True

    def secondPassCheck(self):
        """
        Second pass to ensure no glyphs are left with empty groups.
        Focus on glyphs containing diacritics.
        """
        Font = Glyphs.font
        if not Font:
            return
        
        diacritic_markers = ['invertedbreve', 'acute', 'caron', 'circumflex', 
                             'dotaccent', 'macron', 'bar', 'slash', 'slashacute', 
                             'ogonek', 'cedilla']
        
        for glyph in Font.glyphs:
            if not glyph.leftKerningGroup and not glyph.rightKerningGroup:
                glyphName = glyph.name
                
                contains_diacritic = False
                for marker in diacritic_markers:
                    if marker in glyphName:
                        contains_diacritic = True
                        break
                
                if contains_diacritic:
                    self.assignDiacriticGlyph(glyph)

    def loopUntilAllAssigned(self, maxPasses=10):
        """
        Loop through all glyphs until all have groups assigned,
        with a safety liApache2 to prevent infinite loops.
        """
        Font = Glyphs.font
        if not Font:
            return
        
        pass_count = 0
        while pass_count < maxPasses:
            for glyph in Font.glyphs:
                if not glyph.leftKerningGroup and not glyph.rightKerningGroup:
                    self.assignKerningGroups(glyph)
            
            if self.checkAllGlyphsAssigned():
                break
            
            self.secondPassCheck()
            
            if self.checkAllGlyphsAssigned():
                break
            
            pass_count += 1
        
        for glyph in Font.glyphs:
            if not glyph.leftKerningGroup and not glyph.rightKerningGroup:
                glyph.leftKerningGroup = '@' + glyph.name
                glyph.rightKerningGroup = '@' + glyph.name

    def applyCustomGroup(self, sender):
        """Apply custom group to selected glyphs according to radio option."""
        Font = Glyphs.font
        if not Font:
            self.showInfo("Error: No font open")
            return
        
        selectedLayers = Font.selectedLayers
        selectedGlyphs = []
        
        if selectedLayers:
            for layer in selectedLayers:
                if layer.parent:
                    selectedGlyphs.append(layer.parent)
        
        if not selectedGlyphs:
            self.showInfo("Select at least one glyph")
            return
        
        groupName = self.w.tabs[2].groupEdit.get().strip()
        if not groupName:
            self.showInfo("Error: Group name cannot be empty")
            return
        
        if not groupName.startswith('@'):
            groupName = '@' + groupName
            self.w.tabs[2].groupEdit.set(groupName)
        
        selection = self.w.tabs[2].radioGroup.get()
        
        Font.disableUpdateInterface()
        
        try:
            count = 0
            for glyph in selectedGlyphs:
                if selection == 0:
                    glyph.leftKerningGroup = groupName
                elif selection == 1:
                    glyph.rightKerningGroup = groupName
                else:
                    glyph.leftKerningGroup = groupName
                    glyph.rightKerningGroup = groupName
                count += 1
            
            side = ["LSB", "RSB", "LSB and RSB"][selection]
            success_msg = f"Group {groupName} applied to {count} glyph(s) ({side})"
            self.showInfo(success_msg)
            
        except Exception as e:
            self.showInfo(f"Error: {e}")
            traceback.print_exc()
        finally:
            Font.enableUpdateInterface()

    def deleteKerningGroups(self, sender):
        """Delete kerning groups from ALL glyphs."""
        Font = Glyphs.font
        if not Font:
            self.showInfo("Error: No font open")
            return
        
        allGlyphs = self.getAllGlyphs()
        if not allGlyphs:
            return
        
        Font.disableUpdateInterface()
        
        try:
            count = 0
            for glyph in allGlyphs:
                if glyph.leftKerningGroup or glyph.rightKerningGroup:
                    self.clearKerningGroups(glyph)
                    count += 1
            
            self.showInfo(f"Groups deleted from {count} glyph(s)")
        except Exception as e:
            self.showInfo(f"Error: {e}")
            traceback.print_exc()
        finally:
            Font.enableUpdateInterface()

    def generateKerningGroups(self, sender):
        """Generate kerning groups for ALL glyphs according to rules."""
        Font = Glyphs.font
        if not Font:
            self.showInfo("Error: No font open")
            return
        
        allGlyphs = self.getAllGlyphs()
        if not allGlyphs:
            return
        
        Font.disableUpdateInterface()
        
        try:
            for glyph in allGlyphs:
                self.clearKerningGroups(glyph)
            
            self.loopUntilAllAssigned()
            
            self.showInfo(f"Groups generated for all glyphs, review the results")
        except Exception as e:
            self.showInfo(f"Error: {e}")
            traceback.print_exc()
        finally:
            Font.enableUpdateInterface()

    # ---------- TEST WORDS METHODS ----------

    def insertTestWordsCallback(self, sender):
        """Insert selected test words in a new tab."""
        font = Glyphs.font
        if not font:
            Message("No font open", "Please open a font first.", OKButton="OK")
            return
        
        selected_index = self.w.tabs[2].testWordsPopup.get()
        test_names = list(self.TEST_WORDS_COLLECTIONS.keys())
        
        if 0 <= selected_index < len(test_names):
            test_name = test_names[selected_index]
            test_text = self.TEST_WORDS_COLLECTIONS[test_name]
            
            tab_content = f"# {test_name}\n\n{test_text}"
            font.newTab(tab_content)

    # ---------- SCALE KERN METHODS ----------

    def applyScaleCallback(self, sender):
        """Scale kerning by percentage in active master."""
        font = Glyphs.font
        if not font:
            Message("Error", "No font open.", OKButton="OK")
            return

        master = font.selectedFontMaster
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return

        raw_value = self.w.tabs[2].marginInput.get()
        if raw_value is None:
            Message("Error", "Percentage field is empty.", OKButton="OK")
            return

        value_str = str(raw_value).strip()
        value_str = value_str.replace(",", ".")

        if value_str.endswith("%"):
            value_str = value_str[:-1].strip()

        try:
            percent = float(value_str)
        except:
            Message("Error", f"Invalid percentage value: '{raw_value}'", OKButton="OK")
            return

        operation = self.w.tabs[2].modePopup.getItem()

        if operation == "Increase":
            factor = 1.0 - percent / 100.0
        else:  # Decrease
            factor = 1.0 + percent / 100.0

        master_id = master.id
        if master_id not in font.kerning:
            Message("Info", "No kerning found in the active master.", OKButton="OK")
            return

        # Collect all kerning pairs
        kerning_pairs = []
        for left_key, right_dict in font.kerning[master_id].items():
            for right_key, value in right_dict.items():
                if value is not None:
                    kerning_pairs.append((left_key, right_key, value))

        if not kerning_pairs:
            Message("Info", "No kerning pairs to scale.", OKButton="OK")
            return

        # Resolve key to glyph name
        def resolveKey(key):
            if isinstance(key, str) and key.startswith("@MMK_"):
                return key
            if isinstance(key, str) and len(key) == 36:
                for g in font.glyphs:
                    if g.id == key:
                        return g.name
                return None
            return key

        # Apply scaling
        count = 0
        font.disableUpdateInterface()
        try:
            for left_key, right_key, value in kerning_pairs:
                left = resolveKey(left_key)
                right = resolveKey(right_key)
                if not left or not right:
                    continue

                new_value = int(round(value * factor))
                font.setKerningForPair(master_id, left, right, new_value)
                count += 1
        finally:
            font.enableUpdateInterface()

        Message("Done", f"Kerning updated: {count} pairs\nOperation: {operation}\nPercentage: {percent}%", OKButton="OK")

    # ---------- KERNING PAIRS LISTER METHODS ----------

    def resolveKeyTurbo(self, key):
        """Fast key resolution with caching"""
        font = Glyphs.font
        if not font:
            return str(key)

        if not isinstance(key, str):
            return str(key)

        if key in self._keyCacheTurbo:
            return self._keyCacheTurbo[key]

        result = key
    
        if key.startswith("@MMK_L_") or key.startswith("@MMK_R_"):
            result = key.split("_", 2)[-1]
        elif key.startswith("@") and "_" not in key:
            result = key[1:]
        elif len(key) == 36 and key.count("-") == 4:
            g = font.glyphForId_(key)
            if g:
                result = g.name

        self._keyCacheTurbo[key] = result
        return result

    def charToProductionNameTurbo(self, char_or_name):
        """Fast character to production name conversion"""
        font = Glyphs.font
        if not font:
            return char_or_name
        
        if char_or_name in self._productionCacheTurbo:
            return self._productionCacheTurbo[char_or_name]
        
        result = char_or_name
    
        if char_or_name in font.glyphs:
            result = char_or_name
        else:
            for glyph in font.glyphs:
                if glyph.unicode:
                    try:
                        if chr(int(glyph.unicode, 16)) == char_or_name:
                            result = glyph.name
                            break
                    except:
                        continue
        
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

        self._productionCacheTurbo[char_or_name] = result
        return result

    def nameToGraphicalRepresentationTurbo(self, name):
        """Convert production name to graphical character for display"""
        font = Glyphs.font
        if not font:
            return name
        
        if name in self._graphicalCacheTurbo:
            return self._graphicalCacheTurbo[name]
        
        result = name
    
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
    
        if name in production_to_char:
            result = production_to_char[name]
        else:
            if name in font.glyphs:
                g = font.glyphs[name]
                if g.unicode:
                    try:
                        result = chr(int(g.unicode, 16))
                    except:
                        pass

        self._graphicalCacheTurbo[name] = result
        return result

    def scriptOrderTurbo(self, ch):
        """Fast script-based ordering"""
        if not ch:
            return (9, ch)
    
        try:
            cp = ord(ch[0])
        except:
            return (9, ch)

        if 0x0041 <= cp <= 0x024F: return (0, ch)
        if 0x0370 <= cp <= 0x03FF: return (1, ch)
        if 0x0400 <= cp <= 0x052F: return (2, ch)
        return (3, ch)

    def contextualDisplayTurbo(self, L, R, val):
        """Generate compact display for tab: /H/H/B/ì/H/H 1064"""
        if isinstance(L, str): L = L.strip()
        if isinstance(R, str): R = R.strip()
    
        Lprod = self.charToProductionNameTurbo(L)
        Rprod = self.charToProductionNameTurbo(R)
    
        Lprod = str(Lprod).strip()[:8] if Lprod else ""
        Rprod = str(Rprod).strip()[:8] if Rprod else ""
    
        return f"/H/H/{Lprod}/{Rprod}/H/H {val}"

    def refreshPairsList(self, sender=None):
        """Refresh the kerning pairs list."""
        font = Glyphs.font
        if not font:
            Message("No font", "Please open a font first.", OKButton="OK")
            return
        
        mid = font.selectedFontMaster.id
    
        if mid in self._kerningCacheTurbo:
            kerning = self._kerningCacheTurbo[mid]
        else:
            kerning = font.kerning.get(mid, {})
            self._kerningCacheTurbo[mid] = kerning

        rows = []
        seen = set()

        for LK, rightDict in kerning.items():
            for RK, val in rightDict.items():
                try:
                    val_int = int(val)
                except (TypeError, ValueError):
                    continue

                L0 = self.resolveKeyTurbo(LK)
                R0 = self.resolveKeyTurbo(RK)

                L_prod = self.charToProductionNameTurbo(L0)
                R_prod = self.charToProductionNameTurbo(R0)

                L_display = self.nameToGraphicalRepresentationTurbo(L_prod)
                R_display = self.nameToGraphicalRepresentationTurbo(R_prod)

                uniq = (L_prod, R_prod, val_int)
                if uniq in seen:
                    continue
                seen.add(uniq)

                rows.append({
                    "Left": L_display,
                    "Right": R_display,
                    "Value": val_int,
                    "_display": self.contextualDisplayTurbo(L0, R0, val_int),
                    "_scriptL": self.scriptOrderTurbo(L_display),
                    "_scriptR": self.scriptOrderTurbo(R_display),
                    "_originalLeft": L0,
                    "_originalRight": R0,
                    "_productionLeft": L_prod,
                    "_productionRight": R_prod,
                    "_sortValue": val_int,
                })

        rows.sort(key=lambda r: (r["_scriptL"][0], r["_scriptR"][0], r["Left"], r["Right"]))

        final = []
        lastBlock = None
        for r in rows:
            blk = r["_scriptL"][0]
            if lastBlock is not None and blk != lastBlock:
                final.append({"Left": "────", "Right": "────", "Value": "──", "_isSeparator": True})
            final.append({
                "Left": r["Left"],
                "Right": r["Right"],
                "Value": str(r["Value"]),
                "_originalData": r
            })
            lastBlock = blk

        self._allPairsTurbo = final
        self._currentDisplayPairsTurbo = final
        self.w.tabs[2].pairsList.set(final)
    
        pair_count = len([r for r in final if not r.get("_isSeparator", False)])
        Message("Kerning pairs loaded", f"Loaded {pair_count} kerning pairs.", OKButton="OK")

    def clearPairsSearch(self, sender):
        """Clear search filter."""
        self.w.tabs[2].searchPairs.set("")
    
        if not hasattr(self, '_allPairsTurbo'):
            self._allPairsTurbo = []
    
        self.w.tabs[2].pairsList.set(self._allPairsTurbo)
        self._currentDisplayPairsTurbo = self._allPairsTurbo

    def filterPairsList(self, sender):
        """Filter pairs list based on search query."""
        q = sender.get().strip()
        if not q:
            self.clearPairsSearch(None)
            return

        if not hasattr(self, '_allPairsTurbo'):
            self._allPairsTurbo = []
            self._currentDisplayPairsTurbo = []
    
        if q.endswith(","):
            exact = q[:-1].strip()
            filtered = [r for r in self._allPairsTurbo if r["Left"] == exact or r["Right"] == exact]
        else:
            ql = q.lower()
            filtered = []
            for r in self._allPairsTurbo:
                original_data = r.get("_originalData", {})
                if (ql in r["Left"].lower() or 
                    ql in r["Right"].lower() or 
                    ql in str(r["Value"]) or
                    ql in original_data.get("_productionLeft", "").lower() or
                    ql in original_data.get("_productionRight", "").lower()):
                    filtered.append(r)

        self.w.tabs[2].pairsList.set(filtered)
        self._currentDisplayPairsTurbo = filtered

    def showSelectedPairs(self, sender):
        """Show selected pairs in a new tab."""
        if not hasattr(self, '_currentDisplayPairsTurbo'):
            self._currentDisplayPairsTurbo = []
        
        rows = self._currentDisplayPairsTurbo
        sel = self.w.tabs[2].pairsList.getSelection()

        if not sel:
            Message("No selection", "Please select one or more pairs from the list.", OKButton="OK")
            return

        try:
            lines = []
            for i in sel:
                if i < len(rows):
                    row = rows[i]
                    if row.get("Left") == "────" and row.get("Right") == "────":
                        continue
                
                    original_data = row.get("_originalData", row)
                
                    left = original_data.get("_productionLeft", row["Left"])
                    right = original_data.get("_productionRight", row["Right"])
                    value = original_data.get("Value", row["Value"])
                
                    lines.append(self.contextualDisplayTurbo(left, right, value))
        
            if lines:
                Glyphs.font.newTab("\n".join(lines))
                Message("Tab created", f"Created tab with {len(lines)} pair(s).", OKButton="OK")
        except Exception as e:
            print(f"Error showing selection: {e}")
            Message("Error", f"Error creating tab: {e}", OKButton="OK")

    def listAllPairsCallback(self, sender):
        """List all kerning pairs in tabs."""
        font = Glyphs.font
        if not font:
            Message("No font", "Please open a font first.", OKButton="OK")
            return
        
        try:
            pairs_per_tab = int(self.w.tabs[2].pairsPerInput.get())
        except:
            pairs_per_tab = 50

        custom_prefix = self.w.tabs[2].prefixInput.get().strip() or "HH"
        custom_suffix = self.w.tabs[2].suffixInput.get().strip() or "HH"

        master = font.selectedFontMaster
        if not master:
            Message("Error", "No master selected.", OKButton="OK")
            return

        master_id = master.id

        # Get all kerning pairs
        all_pairs = []
        kerning_dict = font.kerning.get(master_id, {})

        for left_key, right_dict in kerning_dict.items():
            for right_key, val in right_dict.items():
                if val is not None:
                    left_glyph = self.resolveKeyTurbo(left_key)
                    right_glyph = self.resolveKeyTurbo(right_key)
                    
                    if left_glyph and right_glyph:
                        all_pairs.append({
                            'left': left_glyph,
                            'right': right_glyph,
                            'value': val
                        })

        if not all_pairs:
            Message("Info", "No kerning pairs found.", OKButton="OK")
            return

        # Sort pairs
        all_pairs.sort(key=lambda p: (p['left'], p['right']))

        # Create tabs
        total_tabs = (len(all_pairs) + pairs_per_tab - 1) // pairs_per_tab

        for t in range(total_tabs):
            start = t * pairs_per_tab
            end = min(start + pairs_per_tab, len(all_pairs))
            tab_pairs = all_pairs[start:end]

            lines = [
                f"# Kerning Pairs {start+1}-{end} of {len(all_pairs)}",
                f"# Master: {master.name}",
                f"# Prefix: {custom_prefix}",
                f"# Suffix: {custom_suffix}",
                ""
            ]

            for p in tab_pairs:
                # Create display with prefix and suffix
                prefix = custom_prefix
                suffix = custom_suffix
                display = f"/{prefix}/{p['left']}/{p['right']}/{suffix}"
                lines.append(f"{display}    {int(p['value'])}")

            font.newTab("\n".join(lines))

        Message("Success", f"Created {total_tabs} tabs with {len(all_pairs)} kerning pairs.", OKButton="OK")

    def closeAllTabsCallback(self, sender):
        """Close all open tabs."""
        font = Glyphs.font
        if font:
            while len(font.tabs) > 0:
                font.tabs[-1].close()


# Ejecutar
KingSubditKerningEngine()