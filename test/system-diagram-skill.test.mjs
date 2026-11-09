import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

// The system-diagram skill's guarantees are in code: boards it builds keep arrows attached
// when a box moves, and the checker refuses the things that made earlier boards unreadable.
const root = fileURLToPath(new URL("..", import.meta.url));
const scripts = join(root, "skills/system-diagram/scripts");

const run = (args, cwd) => spawnSync("python3", args, { cwd, encoding: "utf8" });

function build(body) {
  const dir = mkdtempSync(join(tmpdir(), "diagram-"));
  writeFileSync(
    join(dir, "build.py"),
    `import sys\nsys.path.insert(0, ${JSON.stringify(scripts)})\nfrom draw import Scene\ns = Scene()\n${body}\ns.save("b.excalidraw")\n`,
  );
  execFileSync("python3", ["build.py"], { cwd: dir, stdio: "pipe" });
  return dir;
}

const check = (dir) => run([join(scripts, "check_scene.py"), "b.excalidraw"], dir);
const GOOD = `a = s.oval(100, 300, 300, 160, "Lead agent")\nb = s.store(700, 300, 260, 180, "Blob")\ns.arrow(a, b, "file")\n`;

test("a built board passes and every arrow is bound at both ends", () => {
  const dir = build(GOOD);
  const out = check(dir);
  assert.equal(out.status, 0, out.stdout);
  const { elements } = JSON.parse(readFileSync(join(dir, "b.excalidraw"), "utf8"));
  const arrow = elements.find((e) => e.type === "arrow");
  for (const end of [arrow.startBinding, arrow.endBinding]) {
    const shape = elements.find((e) => e.id === end.elementId);
    assert.ok(shape.boundElements.some((b) => b.id === arrow.id));
  }
});

test("the checker rejects a detached arrow", () => {
  const dir = build(GOOD);
  const scene = JSON.parse(readFileSync(join(dir, "b.excalidraw"), "utf8"));
  scene.elements.find((e) => e.type === "arrow").endBinding = null;
  writeFileSync(join(dir, "b.excalidraw"), JSON.stringify(scene));
  const out = check(dir);
  assert.equal(out.status, 1);
  assert.match(out.stdout, /not attached/);
});

for (const [name, body, message] of [
  ["small text", GOOD + `s.text(100, 700, "tiny", size=14)\n`, /too small/],
  ["a paragraph of loose text", GOOD + `s.text(100, 700, ${JSON.stringify("word ".repeat(40).trim())}, size=24, width=1800)\n`, /loose text/],
  ["too many words in a box", `s.box(100, 300, 1500, 500, ${JSON.stringify("word ".repeat(20).trim())}, size=24)\n`, /words in one shape/],
  ["a board of only cards", `a = s.box(100, 300, 300, 160, "One")\nb = s.box(700, 300, 300, 160, "Two")\ns.arrow(a, b)\n`, /card look/],
  ["an arrow through a shape", `a = s.oval(100, 300, 300, 160, "A")\nm = s.oval(600, 300, 300, 160, "M")\nb = s.oval(1100, 300, 300, 160, "B")\ns.arrow(a, b)\n`, /runs through shape/],
  ["an arrow through text", `a = s.oval(100, 300, 300, 160, "A")\nb = s.oval(1100, 300, 300, 160, "B")\ns.text(650, 365, "note", size=30)\ns.arrow(a, b)\n`, /runs through text/],
  ["a board made of frames", GOOD + `s._add("frame", 0, 0, 2400, 1350, name="One")\n`, /frames split it/],
  ["a panel enclosing other shapes", GOOD + `p = s.box(50, 200, 1200, 500, "")\ns.oval(100, 520, 200, 100, "C")\n`, /panel/],
  ["a row of identical cards", `for i in range(4):\n    s.box(100 + i * 400, 300, 300, 160, str(i))\ns.oval(100, 700, 300, 160, "A")\ns.oval(600, 700, 300, 160, "B")\ns.oval(1100, 700, 300, 160, "C")\n`, /card row/],
  ["an arrow collapsed around its label", `a = s.oval(100, 300, 300, 160, "A")\nb = s.store(480, 300, 260, 180, "B")\ns.arrow(a, b, "a very long label")\n`, /collapsed/],
  ["a label on a corner", `a = s.oval(100, 300, 300, 160, "A")\nb = s.store(900, 700, 260, 180, "B")\ns.arrow(a, b, "file", via=[(1030, 380)], sides="rt")\n`, /on a corner/],
  ["a stub of an arrow", `a = s.oval(100, 300, 300, 160, "A")\nb = s.store(430, 300, 260, 180, "B")\ns.arrow(a, b)\n`, /too short/],
  ["text on top of agent dots", GOOD + `s.swarm(100, 700, 10, 10)\ns.text(120, 700, "note", size=30)\n`, /agent dots/],
  ["colliding text", GOOD + `s.text(100, 700, "same", size=30)\ns.text(105, 705, "spot", size=30)\n`, /collides/],
]) {
  test(`the checker rejects ${name}`, () => {
    const out = check(build(body));
    assert.equal(out.status, 1, out.stdout);
    assert.match(out.stdout, message);
  });
}

test("a file named on the board must be in the ledger, and ledger citations must exist", () => {
  const dir = build(GOOD + `s.text(100, 700, "build_index.py", size=30)\n`);
  writeFileSync(join(dir, "real.txt"), "one line\n");
  writeFileSync(join(dir, "l.md"), "| x | `real.txt:1` |\n| y | `real.txt:9` |\n| z | `gone.py:1` |\n");
  const out = run([join(scripts, "check_scene.py"), "b.excalidraw", "--ledger", "l.md", "--root", dir], dir);
  assert.equal(out.status, 1);
  assert.match(out.stdout, /build_index\.py is on the board but not in the ledger/);
  assert.match(out.stdout, /past the end of real\.txt/);
  assert.match(out.stdout, /missing file: gone\.py/);
});

test("the worked example passes with its ledger", () => {
  const example = join(root, "examples/url-shortener");
  const out = run(
    [join(scripts, "check_scene.py"), "url-shortener.excalidraw", "--ledger", "url-shortener.ledger.md", "--root", example],
    example,
  );
  assert.equal(out.status, 0, out.stdout);
  assert.match(out.stdout, /^0 errors/m);
});
