---
name: system-diagram
description: Explain a system with a diagram on Excalidraw and a study guide, grounded in the real code, then grill the reader on it. Use when someone asks for a system design, architecture or workflow diagram or an Excalidraw board, wants to understand, explain or defend how a system works, prepare for technical questions about it, or get help assembling or critiquing a diagram they are drawing themselves.
---

# System diagram

Three things come out, built on one ledger of facts:

- **One continuous diagram**: a single connected drawing you can trace with a finger from the first actor to the last output. Detail hangs off the place it belongs. It opens in real Excalidraw and every arrow stays attached when a box moves.
- **A study guide** that starts from the problem and builds to exact mechanics, so the reader can answer a question about any part.
- **The questions people will ask**, with the answers, and an offer to be grilled on them.

Pick the mode from the request. **Draw** when they want the diagram made. **Coach** when they say they are drawing it themselves or want it assembled with them: read [references/coach.md](references/coach.md) and follow that; step 1 still applies.

Paths below are relative to this skill's folder. Files for the diagram go in `docs/architecture/`, named after its subject.

## 1. Ledger

Read the code the diagram describes, then write `<diagram>.ledger.md`: one row per claim that will appear, with its evidence as `` `repo/path:line` ``.

```
| Claim | Evidence |
| Short codes are the row id in base62 | `src/shortener/codes.py:12` |
```

An existing drawing is a source of questions, never of facts; check each of its statements against the code. A claim with no evidence goes in the ledger as `assumed`, and is shown that way or left off. A reason nobody recorded is written as "no reason recorded". Inventing a plausible why is the most common failure here, and it is what a sharp questioner catches first.

Done when every box, arrow and number planned for the diagram has a row.

## 2. The spoken walk

Write the walk you would give out loud, in about 150 words, around one concrete example carried from start to finish (one file, one user, one request). Show it to the user and get their reaction before drawing. The diagram is what you can say, with the words taken out.

From the walk, choose the **spine**: the one path everything hangs off. Each question a sharp reviewer would ask gets an answer attached at the point in the spine where it comes up. Thread the concrete example along the spine as numbered stops.

## 3. Draw

Read [references/look.md](references/look.md) first. Write a build script beside the diagram using `scripts/draw.py`, one stretch of the spine at a time.

After each stretch, render that region and look at it at reading size:

```bash
python3 scripts/render.py diagram.excalidraw out.png --crop X0 Y0 X1 Y1
```

Fix the build script and render again until the region has nothing you would apologize for, then continue. Finish by rendering the whole diagram and following every arrow from the start with your eye.

## 4. Check

```bash
python3 scripts/check_scene.py diagram.excalidraw --ledger diagram.ledger.md --root .
```

Done when it prints `0 errors` and you have viewed a final render after the last edit. When a limit fails, give the arrow more room, cut words, or move the idea; the limits stay as they are.

## 5. Study guide and questions

Read [references/study-guide.md](references/study-guide.md) and [references/grill.md](references/grill.md), then write the guide. The guide often needs more of the ledger than the diagram did: add the rows first.

Done when a person who has read only the guide could answer every question it lists, every number is derived, and a fresh subagent has checked the guide's claims against the code and its errors are fixed.

## 6. Hand over, then offer the grill

Give the user the `.excalidraw` file, the guide and the ledger, and tell them to drag the diagram onto excalidraw.com. Say what you could not establish. Make an excalidraw.com link only when asked, with `uv run --quiet --with cryptography python scripts/share.py diagram.excalidraw`.

Ask whether they want to be grilled on it. If yes, run the grill in [references/grill.md](references/grill.md).
