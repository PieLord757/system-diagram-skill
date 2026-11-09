#!/usr/bin/env python3
"""Render an .excalidraw diagram to PNG so the agent can look at it. Needs Node, no browser.

    python3 scripts/render.py board.excalidraw out.png [--scale 1] [--crop X0 Y0 X1 Y1]

--crop renders only the elements touching that region of the scene, at the size a person
reading that part would see it. Rendering is done by mcp-excalidraw-server (MIT).
"""
import argparse
import json
import subprocess
import sys

TOOL = ["npx", "-y", "mcp-excalidraw-server@2.1.2", "render"]


def bbox(e):
    xs = [e["x"] + p[0] for p in e["points"]] if e.get("points") else [e["x"], e["x"] + e.get("width", 0)]
    ys = [e["y"] + p[1] for p in e["points"]] if e.get("points") else [e["y"], e["y"] + e.get("height", 0)]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("out")
    ap.add_argument("--scale", default="1")
    ap.add_argument("--crop", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"))
    a = ap.parse_args()
    cmd = TOOL + [a.scene, "--out", a.out, "--scale", a.scale, "--padding", "30"]
    if a.crop:
        with open(a.scene, encoding="utf8") as fh:
            elements = json.load(fh)["elements"]
        x0, y0, x1, y1 = a.crop
        ids = []
        for e in elements:
            b = bbox(e)
            if b[2] >= x0 and b[0] <= x1 and b[3] >= y0 and b[1] <= y1:
                ids.append(e["id"])
        cmd += ["--ids", ",".join(ids)]
    sys.exit(subprocess.run(cmd, stdout=subprocess.DEVNULL).returncode)


if __name__ == "__main__":
    main()
