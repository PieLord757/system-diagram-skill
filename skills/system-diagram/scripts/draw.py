"""Build one real, editable Excalidraw diagram from Python. Standard library only.

A build script imports this module, places named things, connects them, and saves:

    from draw import Scene
    s = Scene()
    s.title("How one link is shortened", "One sentence on what it does.")
    a = s.box(120, 300, 300, 130, "POST /shorten", fill="blue")
    b = s.store(760, 290, 260, 150, "Postgres")
    s.arrow(a, b, "a new row")
    s.save("board.excalidraw")

Every arrow is bound at both ends, so moving a box in Excalidraw brings its arrows along.
"""
import json
import math
import random

STROKE = "#1e1e1e"
MUTED = "#495057"
FILL = {
    "none": "transparent", "blue": "#a5d8ff", "green": "#b2f2bb", "yellow": "#ffec99",
    "purple": "#d0bfff", "teal": "#96f2d7", "red": "#ffc9c9", "orange": "#ffd8a8",
    "white": "#ffffff", "grey": "#e9ecef",
}
INK = {"black": STROKE, "muted": MUTED, "blue": "#1971c2", "green": "#2f9e44", "red": "#e03131",
       "orange": "#e8590c", "purple": "#6741d9", "teal": "#0c8599"}
FONT = 5  # Excalifont, the hand-lettered face
LINE = 1.25


def char_width(c):
    if c in "ilj.,:;'!|ft ()[]":
        return 0.36
    if c in "mwMW@":
        return 0.86
    if c.isupper() or c.isdigit():
        return 0.66
    return 0.56


def text_width(text, size):
    return max(sum(char_width(c) for c in line) for line in text.split("\n")) * size


def text_height(text, size):
    return (text.count("\n") + 1) * size * LINE


def wrap(text, size, width):
    """Break text on spaces to fit width. Explicit newlines are kept."""
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = f"{line} {word}".strip()
            if line and text_width(trial, size) > width:
                out.append(line)
                line = word
            else:
                line = trial
        out.append(line)
    return "\n".join(out)


class Node:
    """A placed thing that arrows can attach to."""

    def __init__(self, id_, x, y, w, h):
        self.id, self.x, self.y, self.w, self.h = id_, x, y, w, h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def edge(self, side, at=0.5):
        return {"l": (self.x, self.y + self.h * at), "r": (self.x + self.w, self.y + self.h * at),
                "t": (self.x + self.w * at, self.y), "b": (self.x + self.w * at, self.y + self.h)}[side]


class Scene:
    def __init__(self, seed=7):
        self.els, self.n, self.rng, self.by_id = [], 0, random.Random(seed), {}
        self.groups = 0

    def _id(self, kind):
        self.n += 1
        return f"{kind}{self.n}"

    def _group(self):
        self.groups += 1
        return f"group{self.groups}"

    def _add(self, type_, x, y, w, h, **kw):
        el = {
            "id": kw.pop("id", None) or self._id(type_[:3]), "type": type_, "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": STROKE, "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": None, "seed": self.rng.randint(1, 2**31 - 1),
            "version": 1, "versionNonce": self.rng.randint(1, 2**31 - 1), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        }
        el.update(kw)
        self.els.append(el)
        self.by_id[el["id"]] = el
        return el

    # ---- page furniture ----

    def title(self, text, sub=None, x=60, y=40):
        self.text(x, y, text, size=76)
        if sub:
            self.text(x + 4, y + 104, sub, size=36, color="muted")

    def boundary(self, x0, x1, y, above=None, below=None, label_x=None):
        """A hand-drawn dashed line where the system changes machine or owner."""
        self._add("line", x0, y, x1 - x0, 0, points=[[0, 0], [x1 - x0, 0]], strokeStyle="dashed", strokeColor=INK["muted"])
        lx = label_x if label_x is not None else x1 - 500
        if above:
            self.text(lx, y - 54, above, size=34, color="teal")
        if below:
            self.text(lx, y + 14, below, size=34, color="purple")

    def cluster(self, x, y, w, h):
        """An invisible target, so an arrow can land on a heading plus its dots as one thing."""
        a = self._add("rectangle", x, y, w, h, strokeColor="transparent", strokeWidth=1, customData={"anchor": True})
        return Node(a["id"], x, y, w, h)

    # ---- marks ----

    def text(self, x, y, text, size=28, color="black", vcenter=False, align="left", width=None):
        if width:
            text = wrap(text, size, width)
        w, h = text_width(text, size), text_height(text, size)
        if vcenter:
            y -= h / 2
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
            align = "left"
        return self._add("text", x, y, w, h, text=text, originalText=text, fontSize=size, fontFamily=FONT,
                         textAlign=align, verticalAlign="top", containerId=None, lineHeight=LINE,
                         strokeColor=INK[color], autoResize=True)

    def _label(self, owner, text, size, color="black"):
        w, h = text_width(text, size), text_height(text, size)
        cx, cy = owner.get("_c") or (owner["x"] + owner["width"] / 2, owner["y"] + owner["height"] / 2)
        el = self._add("text", cx - w / 2, cy - h / 2, w, h, text=text, originalText=text, fontSize=size,
                       fontFamily=FONT, textAlign="center", verticalAlign="middle", containerId=owner["id"],
                       lineHeight=LINE, strokeColor=INK[color], autoResize=True, groupIds=list(owner["groupIds"]))
        owner["boundElements"].append({"type": "text", "id": el["id"]})
        return el

    def _shape(self, type_, x, y, w, h, text, fill, size, stroke, dashed, inset):
        round_ = {"type": 3} if type_ == "rectangle" else None
        el = self._add(type_, x, y, w, h, backgroundColor=FILL[fill], roundness=round_, strokeColor=INK[stroke],
                       strokeStyle="dashed" if dashed else "solid")
        if text:
            self._label(el, wrap(text, size, w - inset), size)
        return Node(el["id"], x, y, w, h)

    def box(self, x, y, w, h, text, fill="white", size=32, stroke="black", dashed=False):
        return self._shape("rectangle", x, y, w, h, text, fill, size, stroke, dashed, 44)

    def oval(self, x, y, w, h, text, fill="white", size=32, stroke="black", dashed=False):
        return self._shape("ellipse", x, y, w, h, text, fill, size, stroke, dashed, w * 0.32)

    def gate(self, x, y, w, h, text, fill="yellow", size=30, stroke="black"):
        return self._shape("diamond", x, y, w, h, text, fill, size, stroke, False, w * 0.45)

    def _anchor(self, x, y, w, h, group):
        return self._add("rectangle", x, y, w, h, strokeColor="transparent", backgroundColor="transparent",
                         strokeWidth=1, groupIds=[group], customData={"anchor": True})

    def store(self, x, y, w, h, text, fill="teal", size=30):
        """A data store, drawn as a cylinder."""
        g, cap = self._group(), min(46, h * 0.3)
        c = FILL[fill]
        self._add("ellipse", x, y + h - cap, w, cap, backgroundColor=c, groupIds=[g])
        self._add("rectangle", x, y + cap / 2, w, h - cap, backgroundColor=c, strokeColor="transparent", groupIds=[g])
        for lx in (x, x + w):
            self._add("line", lx, y + cap / 2, 0, h - cap, points=[[0, 0], [0, h - cap]], groupIds=[g])
        self._add("ellipse", x, y, w, cap, backgroundColor=c, groupIds=[g])
        a = self._anchor(x, y, w, h, g)
        a["_c"] = (x + w / 2, y + h / 2 + cap / 3)
        self._label(a, wrap(text, size, w - 30), size)
        return Node(a["id"], x, y, w, h)

    def doc(self, x, y, w, h, text, fill="white", size=28):
        """A document: a page with a folded corner."""
        g, fold = self._group(), min(40, w * 0.22)
        pts = [[0, 0], [w - fold, 0], [w, fold], [w, h], [0, h], [0, 0]]
        self._add("line", x, y, w, h, points=pts, backgroundColor=FILL[fill], groupIds=[g], polygon=True)
        self._add("line", x + w - fold, y, fold, fold, points=[[0, 0], [0, fold], [fold, fold]], groupIds=[g])
        a = self._anchor(x, y, w, h, g)
        if text:
            self._label(a, wrap(text, size, w - 30), size)
        return Node(a["id"], x, y, w, h)

    def person(self, x, y, label, size=30):
        """A stick person with a name under it. x,y is the top-left of the figure."""
        g = self._group()
        self._add("ellipse", x + 30, y, 50, 50, backgroundColor=FILL["white"], groupIds=[g])
        self._add("line", x, y + 58, 110, 58, groupIds=[g], backgroundColor=FILL["white"], polygon=True,
                  roundness={"type": 2}, points=[[0, 58], [18, 12], [55, 0], [92, 12], [110, 58], [0, 58]])
        a = self._anchor(x, y, 110, 118, g)
        if not label:
            return Node(a["id"], x, y, 110, 118)
        lbl = self.text(x + 55, y + 124, label, size=size, align="center")
        lbl["groupIds"] = [g]
        return Node(a["id"], x, y, 110, 118 + size * 1.5)

    def swarm(self, x, y, n, cols, color="purple", d=22, gap=8, paint=None):
        """n agents, one circle each, so the picture is the count. paint maps index to a hex fill."""
        g = self._group()
        rows = math.ceil(n / cols)
        for i in range(n):
            r, c = divmod(i, cols)
            self._add("ellipse", x + c * (d + gap), y + r * (d + gap), d, d, backgroundColor=(paint or {}).get(i, FILL[color]), strokeWidth=1,
                      groupIds=[g], customData={"agent": True})
        w, h = cols * (d + gap) - gap, rows * (d + gap) - gap
        a = self._anchor(x, y, w, h, g)
        return Node(a["id"], x, y, w, h)

    def tag(self, x, y, text, fill="yellow", d=56, size=28):
        """A numbered step marker."""
        return self.oval(x, y, d, d, text, fill=fill, size=size)

    def arrow(self, a, b, label=None, via=None, sides=None, color="black", dashed=False, width=2, at=(0.5, 0.5), size=26):
        """Connect two Nodes. via is a list of absolute waypoints; sides like 'rl' pick the edges."""
        if not sides:
            dx, dy = b.cx - a.cx, b.cy - a.cy
            sides = ("rl" if dx > 0 else "lr") if abs(dx) >= abs(dy) else ("bt" if dy > 0 else "tb")
        p0, p1 = a.edge(sides[0], at[0]), b.edge(sides[1], at[1])
        path = [p0] + list(via or []) + [p1]
        pts = [[px - p0[0], py - p0[1]] for px, py in path]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        el = self._add("arrow", p0[0], p0[1], max(xs) - min(xs), max(ys) - min(ys), points=pts, strokeColor=INK[color],
                       strokeWidth=width, strokeStyle="dashed" if dashed else "solid", endArrowhead="arrow",
                       startArrowhead=None, elbowed=False,
                       startBinding={"elementId": a.id, "focus": 0, "gap": 8},
                       endBinding={"elementId": b.id, "focus": 0, "gap": 8})
        self.by_id[a.id]["boundElements"].append({"type": "arrow", "id": el["id"]})
        self.by_id[b.id]["boundElements"].append({"type": "arrow", "id": el["id"]})
        if label:
            # Excalidraw centres a label on the middle point, or the middle segment when
            # the point count is even. Anywhere else, moving the arrow makes the label jump.
            n = len(path)
            el["_c"] = path[n // 2] if n % 2 else ((path[n // 2 - 1][0] + path[n // 2][0]) / 2, (path[n // 2 - 1][1] + path[n // 2][1]) / 2)
            self._label(el, label, size, color=color)
        return el

    # ---- output ----

    def scene(self):
        els = []
        for e in self.els:
            e = {k: v for k, v in e.items() if not k.startswith("_")}
            if e["type"] == "line" and e.get("polygon") is None:
                e.pop("polygon", None)
            if e["type"] in ("line", "arrow"):
                e.setdefault("lastCommittedPoint", None)
                e.setdefault("startArrowhead", None)
                e.setdefault("endArrowhead", None)
            els.append(e)
        return {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": els,
                "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}

    def save(self, path):
        with open(path, "w", encoding="utf8") as fh:
            json.dump(self.scene(), fh, indent=0)
        print(f"wrote {path}: {len(self.els)} elements")
