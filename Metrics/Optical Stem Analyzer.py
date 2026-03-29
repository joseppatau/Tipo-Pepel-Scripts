# MenuTitle:Optical Stem Analyzer
# -*- coding: utf-8 -*-
# Description: Analyzes optical stem compensation by comparing straight and curved glyph stems across masters.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2 Kern Group Update metrics

import vanilla
from GlyphsApp import Glyphs
from AppKit import NSPoint


class OpticalStemAnalyzer(object):

    def __init__(self):

        self.w = vanilla.Window((420,420),"Optical Stem Analyzer")

        self.w.text = vanilla.TextBox(
            (20,20,380,20),
            "Measure straight vs curved stem compensation"
        )

        self.w.runButton = vanilla.Button(
            (20,50,200,30),
            "Analyze Font",
            callback=self.runReport
        )

        self.w.report = vanilla.TextEditor(
            (20,90,380,280),
            ""
        )

        self.w.clearButton = vanilla.Button(
            (20,380,120,30),
            "Clear",
            callback=self.clearReport
        )

        self.w.copyButton = vanilla.Button(
            (160,380,120,30),
            "Copy",
            callback=self.copyReport
        )

        self.w.open()

    # --------------------------------------------
    # compensation table
    # --------------------------------------------

    def curveIncrement(self,stem):

        table = [
            (10,1),
            (30,2),
            (60,3.5),
            (90,5),
            (120,6),
            (160,8),
            (200,10),
            (250,13.5)
        ]

        if stem <= table[0][0]:
            return table[0][1]

        for i in range(len(table)-1):

            s1,p1 = table[i]
            s2,p2 = table[i+1]

            if s1 <= stem <= s2:

                t = (stem - s1)/(s2 - s1)

                return p1 + (p2-p1)*t

        return table[-1][1]

    # --------------------------------------------
    # measure stem using intersections
    # --------------------------------------------

    def measureStem(self,layer):

        bounds = layer.bounds

        y = bounds.origin.y + bounds.size.height/2

        p1 = NSPoint(bounds.origin.x-1000,y)
        p2 = NSPoint(bounds.origin.x+bounds.size.width+1000,y)

        intersections = layer.intersectionsBetweenPoints(p1,p2)

        xs = [i.pointValue().x for i in intersections]

        xs.sort()

        values = []

        for i in range(len(xs)-1):

            values.append(xs[i+1]-xs[i])

        if len(values) >= 3:
            values = values[1:-1]

        stems = values[0::2]

        if stems:
            return stems[0]

        return None

    # --------------------------------------------
    # analyze pair
    # --------------------------------------------

    def analyzePair(self,font,master,straightGlyph,roundGlyph):

        gStraight = font.glyphs[straightGlyph]
        gRound = font.glyphs[roundGlyph]

        if not gStraight or not gRound:
            return None

        layerStraight = gStraight.layers[master.id]
        layerRound = gRound.layers[master.id]

        stemStraight = self.measureStem(layerStraight)
        stemRound = self.measureStem(layerRound)

        if not stemStraight or not stemRound:
            return None

        percent = self.curveIncrement(stemStraight)

        suggested = stemStraight * (1 + percent/100)

        diff = stemRound - suggested

        return (stemStraight,stemRound,suggested,diff,percent)

    # --------------------------------------------
    # main report
    # --------------------------------------------

    def runReport(self,sender):

        font = Glyphs.font

        report = "OPTICAL STEM ANALYSIS\n\n"

        pairs = [
            ("H","O","CAPITALS"),
            ("n","o","LOWERCASE")
        ]

        for master in font.masters:

            report += "Master: %s\n" % master.name
            report += "--------------------------------\n"

            for straight,roundG,label in pairs:

                data = self.analyzePair(font,master,straight,roundG)

                if not data:
                    continue

                stemStraight,stemRound,suggested,diff,percent = data

                report += "%s\n" % label
                report += "Straight stem (%s): %.1f\n" % (straight,stemStraight)
                report += "Current curve (%s): %.1f\n" % (roundG,stemRound)
                report += "Suggested curve: %.2f\n" % suggested
                report += "Optical compensation: +%.2f%%\n" % percent

                if abs(diff) <= 2:
                    report += "Status: OK\n\n"
                elif diff > 0:
                    report += "Status: Too thick (%.2f)\n\n" % diff
                else:
                    report += "Status: Too thin (%.2f)\n\n" % abs(diff)

            report += "\n"

        self.w.report.set(report)

    # --------------------------------------------

    def clearReport(self,sender):

        self.w.report.set("")

    # --------------------------------------------

    def copyReport(self,sender):

        text = self.w.report.get()

        Glyphs.showNotification("Copied","Report copied")

        from AppKit import NSPasteboard, NSStringPboardType

        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(text,NSStringPboardType)


OpticalStemAnalyzer()