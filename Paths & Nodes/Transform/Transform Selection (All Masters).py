# MenuTitle: Transform Selection (All Masters)
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs
from vanilla import *


class TransformSelection(object):

    def __init__(self):

        self.anchorIndex = 4

        self.w = FloatingWindow(
            (150, 210),
            "Transform"
        )

        # Anchor buttons 3x3
        self.anchorButtons = []

        startX = 18
        startY = 30
        step = 20

        for row in range(3):
            for col in range(3):

                idx = row * 3 + col

                rb = RadioButton(
                    (
                        startX + col * step,
                        startY + row * step,
                        18,
                        18
                    ),
                    "",
                    callback=self.anchorCallback,
                    sizeStyle="small"
                )

                setattr(self.w, "anchor_%d" % idx, rb)
                self.anchorButtons.append(rb)

        self.anchorButtons[4].set(True)

        # Width
        self.w.widthLabel = TextBox(
            (12, 102, 25, 17),
            u"W↔"
        )

        self.w.widthValue = EditText(
            (40, 98, 60, 22),
            ""
        )

        # Height
        self.w.heightLabel = TextBox(
            (12, 130, 25, 17),
            u"H↕"
        )

        self.w.heightValue = EditText(
            (40, 126, 60, 22),
            ""
        )

        # All Masters
        self.w.allMasters = CheckBox(
            (12, 158, 120, 20),
            "All masters",
            value=False
        )

        # Apply
        self.w.applyButton = Button(
            (12, 182, 126, 20),
            "Apply",
            callback=self.applyTransform
        )

        self.w.open()

    def anchorCallback(self, sender):

        for i, rb in enumerate(self.anchorButtons):

            if rb == sender:
                rb.set(True)
                self.anchorIndex = i
            else:
                rb.set(False)

    def getSelectedNodeMap(self, layer):

        nodeMap = set()

        for pIndex, path in enumerate(layer.paths):

            nodeCount = len(path.nodes)

            for nIndex, node in enumerate(path.nodes):

                if not node.selected:
                    continue

                # node seleccionat
                nodeMap.add((pIndex, nIndex))

                # Si és un node on-curve, incloure els handles adjacents
                if node.type != "offcurve":

                    prevIndex = (nIndex - 1) % nodeCount
                    nextIndex = (nIndex + 1) % nodeCount

                    prevNode = path.nodes[prevIndex]
                    nextNode = path.nodes[nextIndex]

                    if prevNode.type == "offcurve":
                        nodeMap.add((pIndex, prevIndex))

                    if nextNode.type == "offcurve":
                        nodeMap.add((pIndex, nextIndex))

        return list(nodeMap)

    def getNodesFromMap(self, layer, nodeMap):

        nodes = []

        for pIndex, nIndex in nodeMap:

            try:
                nodes.append(layer.paths[pIndex].nodes[nIndex])
            except:
                pass

        return nodes

    def boundsOfNodes(self, nodes):

        xs = [n.position.x for n in nodes]
        ys = [n.position.y for n in nodes]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys)
        )

    def getAnchorPoint(self, bounds, anchorIndex):

        xMin, yMin, xMax, yMax = bounds

        col = anchorIndex % 3
        row = anchorIndex // 3

        if col == 0:
            ax = xMin
        elif col == 1:
            ax = (xMin + xMax) * 0.5
        else:
            ax = xMax

        if row == 0:
            ay = yMax
        elif row == 1:
            ay = (yMin + yMax) * 0.5
        else:
            ay = yMin

        return ax, ay

    def resolveTargetValue(self, textValue, currentValue):

        if not textValue:
            return None

        try:

            if textValue.startswith("+"):
                return currentValue + float(textValue)

            elif textValue.startswith("-"):
                return currentValue + float(textValue)

            else:
                return float(textValue)

        except:
            return None

    def transformLayer(
        self,
        layer,
        nodeMap,
        widthText,
        heightText
    ):

        # Get all nodes from the map (selected + automatically included handles)
        allNodes = self.getNodesFromMap(layer, nodeMap)
        if len(allNodes) < 2:
            return

        # Separate on-curve nodes (those originally selected, not handles)
        onCurveNodes = [node for node in allNodes if node.type != "offcurve"]
        if not onCurveNodes:
            # Fallback: no on-curve selected, scale everything (old behaviour)
            self.scaleNodes(allNodes, targetWidth=None, targetHeight=None, anchorIndex=self.anchorIndex,
                            widthText=widthText, heightText=heightText)
            return

        # Bounding box based ONLY on on-curve nodes
        xMin, yMin, xMax, yMax = self.boundsOfNodes(onCurveNodes)
        currentWidth = xMax - xMin
        currentHeight = yMax - yMin

        targetWidth = self.resolveTargetValue(widthText, currentWidth)
        targetHeight = self.resolveTargetValue(heightText, currentHeight)

        if targetWidth is None and targetHeight is None:
            return

        # Anchor point from the on‑curve bounding box
        ax, ay = self.getAnchorPoint((xMin, yMin, xMax, yMax), self.anchorIndex)

        # Scale factors
        sx = 1.0
        sy = 1.0
        if targetWidth is not None and currentWidth > 0:
            sx = targetWidth / currentWidth
        if targetHeight is not None and currentHeight > 0:
            sy = targetHeight / currentHeight

        # Build a dictionary for quick node access
        nodeDict = {}
        for pIdx, nIdx in nodeMap:
            try:
                nodeDict[(pIdx, nIdx)] = layer.paths[pIdx].nodes[nIdx]
            except:
                pass

        # Store original positions and handle offsets
        updates = []          # (node, new_x, new_y)
        handlesMap = {}       # onCurveNode -> list of (handleNode, dx, dy)

        # First pass: compute new positions for on‑curve nodes
        for node in onCurveNodes:
            origX = node.position.x
            origY = node.position.y
            newX = ax + (origX - ax) * sx
            newY = ay + (origY - ay) * sy
            updates.append((node, newX, newY))

            # Find its handles (adjacent off‑curve nodes that are in nodeMap)
            # Need to find the path and index of this node
            for (pIdx, nIdx), n in nodeDict.items():
                if n is node and n.type != "offcurve":
                    path = layer.paths[pIdx]
                    nodeCount = len(path.nodes)
                    prevIdx = (nIdx - 1) % nodeCount
                    nextIdx = (nIdx + 1) % nodeCount
                    handles = []
                    prevNode = path.nodes[prevIdx]
                    if prevNode.type == "offcurve" and (pIdx, prevIdx) in nodeMap:
                        dx = prevNode.position.x - node.position.x
                        dy = prevNode.position.y - node.position.y
                        handles.append((prevNode, dx, dy))
                    nextNode = path.nodes[nextIdx]
                    if nextNode.type == "offcurve" and (pIdx, nextIdx) in nodeMap:
                        dx = nextNode.position.x - node.position.x
                        dy = nextNode.position.y - node.position.y
                        handles.append((nextNode, dx, dy))
                    if handles:
                        handlesMap[node] = handles
                    break

        # Second pass: reposition handles using original offsets
        for onNode, handles in handlesMap.items():
            # Find the new position of this on‑curve node
            newPos = None
            for n, nx, ny in updates:
                if n is onNode:
                    newPos = (nx, ny)
                    break
            if newPos is None:
                continue
            for handleNode, dx, dy in handles:
                newHandleX = newPos[0] + dx
                newHandleY = newPos[1] + dy
                updates.append((handleNode, newHandleX, newHandleY))

        # Apply all updates
        for node, newX, newY in updates:
            node.position = (newX, newY)

    def scaleNodes(
        self,
        nodes,
        targetWidth=None,
        targetHeight=None,
        anchorIndex=4,
        widthText="",
        heightText=""
    ):

        if len(nodes) < 2:
            return

        xMin, yMin, xMax, yMax = self.boundsOfNodes(nodes)
        currentWidth = xMax - xMin
        currentHeight = yMax - yMin

        # Resolve target values if they were passed as strings
        if isinstance(targetWidth, str) or targetWidth is None:
            targetWidth = self.resolveTargetValue(widthText, currentWidth)
        if isinstance(targetHeight, str) or targetHeight is None:
            targetHeight = self.resolveTargetValue(heightText, currentHeight)

        if targetWidth is None and targetHeight is None:
            return

        ax, ay = self.getAnchorPoint((xMin, yMin, xMax, yMax), anchorIndex)

        sx = 1.0
        sy = 1.0
        if targetWidth and currentWidth > 0:
            sx = targetWidth / currentWidth
        if targetHeight and currentHeight > 0:
            sy = targetHeight / currentHeight

        for node in nodes:
            x = node.position.x
            y = node.position.y
            node.position = (ax + (x - ax) * sx, ay + (y - ay) * sy)

    def applyTransform(self, sender):

        font = Glyphs.font

        if not font:
            return

        layer = font.selectedLayers[0]
        glyph = layer.parent

        nodeMap = self.getSelectedNodeMap(layer)

        if not nodeMap:
            print("No nodes selected.")
            return

        widthText = self.w.widthValue.get().strip()
        heightText = self.w.heightValue.get().strip()

        font.disableUpdateInterface()

        try:

            if self.w.allMasters.get():

                for master in font.masters:

                    masterLayer = glyph.layers[master.id]

                    self.transformLayer(
                        masterLayer,
                        nodeMap,
                        widthText,
                        heightText
                    )

            else:

                self.transformLayer(
                    layer,
                    nodeMap,
                    widthText,
                    heightText
                )

        finally:

            font.enableUpdateInterface()


TransformSelection()