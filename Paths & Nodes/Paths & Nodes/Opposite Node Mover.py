# MenuTitle: Opposite Node Mover Dual 8-Way + Stable Tension
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs, OFFCURVE
from AppKit import NSFloatingWindowLevel
from vanilla import FloatingWindow, SquareButton, TextBox, EditText, CheckBox
import math


class OppositeNodeMover(object):

    def __init__(self):
        self.w = FloatingWindow(
            (150, 440),  # Alçada reduïda (de 470 a 440)
            "Move nodes",
            autosaveName="com.chatgpt.OppositeNodeMover8Way"
        )

        self.w._window.setLevel_(NSFloatingWindowLevel)

        # ---------- POSITIVE PAD ----------
        self.makePad("Pos", 10)

        self.w.labelPos = TextBox((10, 125, 80, 18), "Distance")
        self.w.distancePos = EditText((10, 145, 60, 22), "2")

        # ---------- NEGATIVE PAD ----------
        self.makePad("Neg", 200)

        self.w.labelNeg = TextBox((10, 315, 80, 18), "Distance")
        self.w.distanceNeg = EditText((10, 335, 60, 22), "-2")

        # ---------- OPTIONS ----------
        self.w.tension = CheckBox((10, 370, 100, 20), "Tension", value=True)
        self.w.debugCB = CheckBox((10, 395, 100, 20), "Debug", value=False)

        self.tensionCache = {}
        self.cachedLayerId = None

        self.w.open()
        self.w.makeKey()

    # ---------------------------------------------------------

    def makePad(self, suffix, y):
        positions = {
            "NW": (10, y),
            "UP": (50, y),
            "NE": (90, y),

            "LEFT": (10, y + 40),
            "RIGHT": (90, y + 40),

            "SW": (10, y + 80),
            "DOWN": (50, y + 80),
            "SE": (90, y + 80),
        }

        labels = {
            "NW": "↖",
            "UP": "↑",
            "NE": "↗",
            "LEFT": "←",
            "RIGHT": "→",
            "SW": "↙",
            "DOWN": "↓",
            "SE": "↘",
        }

        callbacks = {
            "NW": getattr(self, f"moveNW{suffix}"),
            "UP": getattr(self, f"moveUp{suffix}"),
            "NE": getattr(self, f"moveNE{suffix}"),
            "LEFT": getattr(self, f"moveLeft{suffix}"),
            "RIGHT": getattr(self, f"moveRight{suffix}"),
            "SW": getattr(self, f"moveSW{suffix}"),
            "DOWN": getattr(self, f"moveDown{suffix}"),
            "SE": getattr(self, f"moveSE{suffix}"),
        }

        for key in positions:
            setattr(
                self.w,
                f"{key}{suffix}",
                SquareButton(
                    (*positions[key], 28, 28),
                    labels[key],
                    callback=callbacks[key]
                )
            )

    # ---------------------------------------------------------

    def debug(self, msg):
        if self.w.debugCB.get():
            print(msg)

    # ---------------------------------------------------------

    def resetCache(self):
        """Buida la caché internament"""
        self.tensionCache = {}
        self.cachedLayerId = None
        self.debug("\n=== CACHE CLEARED ===")

    # ---------------------------------------------------------

    def getSelectedNodes(self):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            return []
        return [n for n in font.selectedLayers[0].selection if hasattr(n, "position")]

    # ---------------------------------------------------------

    def getDistance(self, negative=False):
        try:
            return float(self.w.distanceNeg.get() if negative else self.w.distancePos.get())
        except:
            return -2.0 if negative else 2.0

    # ---------------------------------------------------------

    def distance(self, a, b):
        return math.hypot(b.x - a.x, b.y - a.y)

    # ---------------------------------------------------------

    def getHandle(self, node, side):
        h = node.prevNode if side == "prev" else node.nextNode
        if h and h.type == OFFCURVE:
            return h
        return None

    # ---------------------------------------------------------

    def findOppositeOncurve(self, node, side):
        handle = self.getHandle(node, side)
        if not handle:
            return None

        n = handle.prevNode if side == "prev" else handle.nextNode

        while n and n.type == OFFCURVE:
            n = n.prevNode if side == "prev" else n.nextNode

        return n

    # ---------------------------------------------------------

    def buildGlobalCache(self, layer):
        """Sempre construeix la caché des de zero (sense comprovar si existeix)"""
        self.tensionCache = {}
        self.cachedLayerId = layer.layerId

        self.debug("\n=== GLOBAL CACHE BUILT ===")

        for path in layer.paths:
            for node in path.nodes:
                nodeData = []

                for side in ["prev", "next"]:
                    handle = self.getHandle(node, side)
                    if not handle:
                        continue

                    opposite = self.findOppositeOncurve(node, side)
                    if not opposite:
                        continue

                    segLen = self.distance(node, opposite)
                    if segLen == 0:
                        continue

                    vx = handle.x - node.x
                    vy = handle.y - node.y
                    handleLen = math.hypot(vx, vy)

                    if handleLen == 0:
                        continue

                    nodeData.append({
                        "side": side,
                        "ratio": handleLen / segLen,
                        "ux": vx / handleLen,
                        "uy": vy / handleLen,
                    })

                if nodeData:
                    self.tensionCache[id(node)] = nodeData

    # ---------------------------------------------------------

    def moveNodeRigid(self, node, dx, dy):
        node.x += dx
        node.y += dy

        for side in ["prev", "next"]:
            h = self.getHandle(node, side)
            if h:
                h.x += dx
                h.y += dy

    # ---------------------------------------------------------

    def moveNodeStable(self, node, dx, dy):
        node.x += dx
        node.y += dy

        cache = self.tensionCache.get(id(node), [])

        for d in cache:
            handle = self.getHandle(node, d["side"])
            opposite = self.findOppositeOncurve(node, d["side"])

            if not handle or not opposite:
                continue

            segLen = self.distance(node, opposite)
            targetLen = segLen * d["ratio"]

            handle.x = node.x + d["ux"] * targetLen
            handle.y = node.y + d["uy"] * targetLen

    # ---------------------------------------------------------

    def moveNode(self, node, dx, dy):
        if self.w.tension.get():
            self.moveNodeStable(node, dx, dy)
        else:
            self.moveNodeRigid(node, dx, dy)

    # ---------------------------------------------------------

    def process(self, mode, negative=False):
        font = Glyphs.font
        if not font:
            return

        layer = font.selectedLayers[0]
        nodes = self.getSelectedNodes()
        if not nodes:
            return

        # SEMPRE buidar la caché abans de cada operació
        self.resetCache()
        
        if self.w.tension.get():
            self.buildGlobalCache(layer)

        dist = self.getDistance(negative)

        vectors = {
            "left": (-dist, 0),
            "right": (dist, 0),
            "up": (0, dist),
            "down": (0, -dist),
            "nw": (-dist, dist),
            "ne": (dist, dist),
            "sw": (-dist, -dist),
            "se": (dist, -dist),
        }

        layer.parent.beginUndo()

        if len(nodes) == 1:
            dx, dy = vectors[mode]
            self.moveNode(nodes[0], dx, dy)

        else:
            cx = sum(n.x for n in nodes) / len(nodes)
            cy = sum(n.y for n in nodes) / len(nodes)

            for node in nodes:
                dx = dy = 0

                if mode in ("left", "right"):
                    if node.x < cx:
                        dx = -dist
                    elif node.x > cx:
                        dx = dist

                elif mode in ("up", "down"):
                    if node.y < cy:
                        dy = -dist
                    elif node.y > cy:
                        dy = dist

                elif mode in ("nw", "se"):
                    v = (node.x - cx) - (node.y - cy)
                    if v < 0:
                        dx, dy = -dist, dist
                    elif v > 0:
                        dx, dy = dist, -dist

                elif mode in ("ne", "sw"):
                    v = (node.x - cx) + (node.y - cy)
                    if v < 0:
                        dx, dy = -dist, -dist
                    elif v > 0:
                        dx, dy = dist, dist

                if dx or dy:
                    self.moveNode(node, dx, dy)

        layer.parent.endUndo()
        layer.updateMetrics()

    # POS
    def moveNWPos(self, s): self.process("nw", False)
    def moveUpPos(self, s): self.process("up", False)
    def moveNEPos(self, s): self.process("ne", False)
    def moveLeftPos(self, s): self.process("left", False)
    def moveRightPos(self, s): self.process("right", False)
    def moveSWPos(self, s): self.process("sw", False)
    def moveDownPos(self, s): self.process("down", False)
    def moveSEPos(self, s): self.process("se", False)

    # NEG
    def moveNWNeg(self, s): self.process("nw", True)
    def moveUpNeg(self, s): self.process("up", True)
    def moveNENeg(self, s): self.process("ne", True)
    def moveLeftNeg(self, s): self.process("left", True)
    def moveRightNeg(self, s): self.process("right", True)
    def moveSWNeg(self, s): self.process("sw", True)
    def moveDownNeg(self, s): self.process("down", True)
    def moveSENeg(self, s): self.process("se", True)


OppositeNodeMover()