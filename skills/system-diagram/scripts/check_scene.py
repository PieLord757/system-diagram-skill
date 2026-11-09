#!/usr/bin/env python3
"""Check an .excalidraw board against the system-diagram rules. Standard library only.

    python3 check_scene.py board.excalidraw [--ledger board.ledger.md] [--root REPO]
    python3 check_scene.py board.excalidraw --describe

Exit code 0 means no errors. --describe prints the words and connections, for reading a
drawing someone else made.
"""
import argparse
import json
import math
import os
import re
import sys

MIN_FONT = 22
MAX_WORDS_IN_SHAPE = 14
MAX_WORDS_TOTAL = 560
MIN_ARROW = 60
LABEL_CLEARANCE = 40
MAX_FREE_TEXT_WORDS = 34
MAX_RECT_SHARE = 0.75
FILE_TOKEN = re.compile(r"[\w./-]+\.(?:py|mjs|js|ts|tsx|json|md|sql)\b")


def rect(e):
    if e.get("points"):
        xs = [e["x"] + p[0] for p in e["points"]]
        ys = [e["y"] + p[1] for p in e["points"]]
        return min(xs), min(ys), max(xs), max(ys)
    return e["x"], e["y"], e["x"] + e.get("width", 0), e["y"] + e.get("height", 0)


def overlap(a, b, margin=2):
    return min(a[2], b[2]) - max(a[0], b[0]) > margin and min(a[3], b[3]) - max(a[1], b[1]) > margin


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def seg_hits(p, q, r):
    """Does segment p-q pass through rectangle r?"""
    steps = max(2, int(math.dist(p, q) / 6))
    return any(inside((p[0] + (q[0] - p[0]) * i / steps, p[1] + (q[1] - p[1]) * i / steps), r) for i in range(steps + 1))


def words(t):
    return len(t.get("text", "").split())


def load(path):
    with open(path, encoding="utf8") as fh:
        d = json.load(fh)
    return [e for e in d["elements"] if not e.get("isDeleted")]


def is_helper(e):
    c = e.get("customData") or {}
    return c.get("anchor") or c.get("zone")


def describe(E):
    by = {e["id"]: e for e in E}
    label = {t["containerId"]: t["text"].replace("\n", " ") for t in E if t["type"] == "text" and t.get("containerId")}
    for e in E:
        if e["type"] in ("rectangle", "ellipse", "diamond") and e["id"] in label:
            print(f"{e['type']}: {label[e['id']]}")
    for t in E:
        if t["type"] == "text" and not t.get("containerId"):
            print(f"note: {t['text'].replace(chr(10), ' ')}")
    for a in E:
        if a["type"] != "arrow":
            continue
        ends = [(a.get("startBinding") or {}).get("elementId"), (a.get("endBinding") or {}).get("elementId")]
        names = [label.get(i, "(unbound)" if i is None else i) for i in ends]
        lab = f"  [{label[a['id']]}]" if a["id"] in label else ""
        print(f"arrow: {names[0]} -> {names[1]}{lab}")


def check(E, ledger=None, root=None):
    errors = []
    by = {e["id"]: e for e in E}
    texts = [e for e in E if e["type"] == "text"]
    arrows = [e for e in E if e["type"] == "arrow"]
    frames = [e for e in E if e["type"] == "frame"]
    label_of = {t["containerId"]: t for t in texts if t.get("containerId")}

    for a in arrows:
        for end in ("startBinding", "endBinding"):
            b = a.get(end)
            if not b or b.get("elementId") not in by:
                errors.append(f"arrow {a['id']}: {end} is not attached to a shape")
            elif not any(x.get("id") == a["id"] for x in by[b["elementId"]].get("boundElements") or []):
                errors.append(f"arrow {a['id']}: {b['elementId']} does not list it in boundElements")

    for t in texts:
        if t.get("fontSize", 0) < MIN_FONT:
            errors.append(f"text too small ({t.get('fontSize')}): {t['text'][:40]!r}")
        c = by.get(t.get("containerId"))
        if t.get("containerId") and c is None:
            errors.append(f"text {t['id']}: container is missing")
        if c and c["type"] != "arrow":
            if t["width"] > c["width"] - 8 or t["height"] > c["height"] - 8:
                errors.append(f"text overflows its shape: {t['text'][:40]!r}")
            if words(t) > MAX_WORDS_IN_SHAPE:
                errors.append(f"{words(t)} words in one shape (limit {MAX_WORDS_IN_SHAPE}): {t['text'][:40]!r}")
        if not c and words(t) > MAX_FREE_TEXT_WORDS:
            errors.append(f"{words(t)}-word block of loose text (limit {MAX_FREE_TEXT_WORDS}): {t['text'][:40]!r}")

    dots = [e for e in E if (e.get("customData") or {}).get("agent")]
    for t in texts:
        if not t.get("containerId") and any(overlap(rect(t), rect(d), 0) for d in dots):
            errors.append(f"text sits on agent dots: {t['text'][:40]!r}")

    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if overlap(rect(a), rect(b)):
                errors.append(f"text collides: {a['text'][:30]!r} and {b['text'][:30]!r}")

    plain = [e for e in E if e["type"] in ("rectangle", "ellipse", "diamond") and not is_helper(e) and not (e.get("customData") or {}).get("agent")]
    for a in arrows:
        pts = [(a["x"] + p[0], a["y"] + p[1]) for p in a["points"]]
        ends = {(a.get("startBinding") or {}).get("elementId"), (a.get("endBinding") or {}).get("elementId")}
        own = label_of.get(a["id"])
        segs = list(zip(pts, pts[1:]))
        for t in texts:
            if t is own or t.get("containerId") in ends:
                continue
            if any(seg_hits(p, q, rect(t)) for p, q in segs):
                errors.append(f"arrow {a['id']} runs through text: {t['text'][:40]!r}")
        for s in plain:
            if s["id"] in ends:
                continue
            r = rect(s)
            inner = (r[0] + 6, r[1] + 6, r[2] - 6, r[3] - 6)
            if any(seg_hits(p, q, inner) for p, q in segs):
                errors.append(f"arrow {a['id']} runs through shape {label_of.get(s['id'], {}).get('text', s['id'])[:40]!r}")

    if plain:
        rects = sum(1 for s in plain if s["type"] == "rectangle")
        if rects / len(plain) > MAX_RECT_SHARE:
            errors.append(f"card look: {rects} of {len(plain)} shapes are rectangles (limit {MAX_RECT_SHARE:.0%})")

    if frames:
        errors.append("frames split it into boards: draw one continuous diagram")
    total = sum(words(t) for t in texts)
    if total > MAX_WORDS_TOTAL:
        errors.append(f"{total} words on the diagram (limit {MAX_WORDS_TOTAL})")

    for s in plain:
        r = rect(s)
        held = [o for o in plain if o is not s and inside(rect(o)[:2], r) and inside(rect(o)[2:], r)]
        if len(held) >= 3:
            errors.append(f"panel: a shape encloses {len(held)} others, which reads as a board")

    sized = {}
    for s in plain:
        if s["type"] == "rectangle":
            sized.setdefault((round(s["y"] / 12), round(s["width"] / 12), round(s["height"] / 12)), []).append(s)
    for group in sized.values():
        if len(group) >= 4:
            errors.append(f"card row: {len(group)} same-size rectangles side by side")

    for a in arrows:
        pts = [(a["x"] + p[0], a["y"] + p[1]) for p in a["points"]]
        segs = [math.dist(p, q) for p, q in zip(pts, pts[1:])]
        if sum(segs) < MIN_ARROW:
            errors.append(f"arrow {a['id']} is too short to read ({sum(segs):.0f})")
        lab = label_of.get(a["id"])
        if lab:
            if len(pts) % 2:
                errors.append(f"label sits on a corner: {lab['text'][:30]!r} (give the arrow an even number of points)")
            else:
                i = len(pts) // 2 - 1
                p, q = pts[i], pts[i + 1]
                need = lab["width"] if abs(q[0] - p[0]) >= abs(q[1] - p[1]) else lab["height"]
                if segs[i] < need + 2 * LABEL_CLEARANCE:
                    errors.append(f"arrow is collapsed around its label {lab['text'][:30]!r}: {segs[i]:.0f} long, needs {need + 2 * LABEL_CLEARANCE:.0f}")

    if ledger:
        with open(ledger, encoding="utf8") as fh:
            body = fh.read()
        for t in texts:
            for tok in FILE_TOKEN.findall(t["text"]):
                if tok not in body:
                    errors.append(f"{tok} is on the board but not in the ledger")
        for src in re.findall(r"`([\w./-]+):(\d+)`", body):
            p = os.path.join(root or ".", src[0])
            if not os.path.isfile(p):
                errors.append(f"ledger cites a missing file: {src[0]}")
            else:
                with open(p, encoding="utf8", errors="ignore") as fh:
                    if int(src[1]) > sum(1 for _ in fh):
                        errors.append(f"ledger cites past the end of {src[0]}: line {src[1]}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--ledger")
    ap.add_argument("--root", default=".")
    ap.add_argument("--describe", action="store_true")
    a = ap.parse_args()
    E = load(a.scene)
    if a.describe:
        describe(E)
        return 0
    errors = check(E, a.ledger, a.root)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
