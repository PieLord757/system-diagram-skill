# The look

The target is one drawing on a whiteboard by someone who understands the system: big hand-lettered words, few of them, shapes that mean something, and arrows you can follow from the first thing to the last. The giveaway of a machine-made diagram is that it is built from cards and boards. A person draws one connected thing.

## One drawing

- One spine, usually top to bottom. Everything connects to it, directly or by an arrow.
- Detail hangs off the place it belongs: a note beside the step, a worked example next to the code that does it. A separate section with its own title breaks the drawing.
- The ending connects back when the system is a loop. An order confirmation, for example, travels back up to the person who placed the order.
- A boundary between machines or owners is one dashed line with a word on each side. Open space does the grouping. Backdrop panels and frames turn it into boards.

## Words

- Hand-lettered Excalifont everywhere. `draw.py` sets it.
- A box says what the thing is in 2 to 6 words. A sharp detail goes on the arrow or beside the step.
- Type is big: title 76, shapes 30 to 46, notes 26 to 38. Nothing under 22.
- A note is one short sentence next to the thing it explains.
- Use the system's real names (`build_index.py`, `orders.json`) where they carry meaning.
- Plain words. No middle dots, no em dashes, no grey filler captions.

## Shapes carry meaning

| Thing | Shape | `draw.py` |
| --- | --- | --- |
| Person | stick figure | `person` |
| Where data rests | cylinder | `store` |
| A file or output | page with a folded corner | `doc` |
| A decision or gate | diamond | `gate` |
| Something that thinks (agent, orchestrator) | oval | `oval` |
| Code that runs | rounded box | `box` |
| Many workers | one dot each, true count | `swarm` |
| A stop on the worked example | numbered circle | `tag` |
| A heading plus its dots, as one arrow target | invisible | `cluster` |

Reach for the shape that says what the thing is before a box.

## Arrows

- Arrows get room. A label sits on a long straight run, with clear line showing on both sides of it. If an arrow looks squeezed, move the shapes apart.
- Fan-out and fan-in run as a tree: one trunk, a horizontal bus, then straight drops. Route with `via` waypoints so the lines are horizontal and vertical.
- A loop is an arrow that goes back, and it lands on the thing it returns to.
- Every arrow says what moves along it when that is not obvious: a file, a question, a verdict.
- Arrows stay off text and shapes.

## Color

Solid Excalidraw pastels on dark outlines. One color means one kind of thing across the whole drawing, and a small key says so once.

## Show the mechanism with the real thing

An abstract chain of files and scripts explains nothing. Show actual items passing through: real file names turning into batches turning into workers. Size shows scale: a phase with 80 workers takes more room than one with 8, and counts are drawn, not only written. Give arithmetic where a number needs defending ("400 files / 5 per worker = 80 workers").

## Defaults

Keep one light, hand-drawn drawing that shows why as well as what. By default, leave out frames or titled sections that split it into boards, rows of identical rounded cards, filled background panels, short arrows collapsed around a label, dark themes, grid backgrounds, monospace type, code-terminal blocks, small grey captions, explanatory paragraphs next to each step, and abstract pipelines of file names.
