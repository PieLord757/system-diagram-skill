# Coach mode

The user holds the pen, because being able to defend the system is the point. You supply the structure, the facts and the critique; they place every box.

## Their drawing

When they share an `.excalidraw` file, read it first:

```bash
python3 scripts/check_scene.py their-board.excalidraw --describe
```

Check each statement on it against the ledger. Report what is wrong or missing, the most important first, with the evidence.

## Feeding them the next piece

Give one section at a time, and wait for them to draw it. Each piece names:

- the shape and what goes in it, in words short enough to letter ("Cylinder: Postgres")
- where it sits relative to what they already have
- the arrow in or out, and what moves along it
- one sentence they could say out loud about why it is built that way, or "no reason recorded" when the code gives none

When they are confused, rebuild the explanation from the real problem and one example before giving more to draw.

Done when they can walk through the drawing unaided: ask them to, and mark where they stumble against the ledger.
