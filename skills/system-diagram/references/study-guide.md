# The study guide

The reader starts out knowing nothing about this system and must end able to answer any question about any part of it. It is easy to read at the top and exact at the bottom.

## Order

1. **The real problem**, with one concrete example. No system yet.
2. **What must be true** for any solution to work, as a short list.
3. **Why the obvious approaches fail**, each against that list.
4. **The system in one paragraph**, then the diagram.
5. **Each part in the order the diagram runs.** Build up: the next part only uses ideas already explained.
6. **What is real and what is not**: what is built, what is manual, what is planned, what was measured and what was only claimed.
7. **Questions you will be asked**, from [grill.md](grill.md), with the answer and its source.
8. **A glossary** of every term and file name.

## Each part

Use the same headings every time, so a reader can find the thing they need under pressure:

- **The problem it solves.** What would go wrong without it, with a concrete case.
- **How it works.** Plain words first, then the exact mechanism: inputs, outputs, field names, thresholds.
- **The numbers**, derived.
- **Why it is built this way.** The recorded reason, or "no reason recorded". Include what it costs and what was rejected.
- **How it fails.** What happens, who notices, how it is recovered.
- **Where it lives.** `repo/path:line`.
- **If you are asked.** The 2 to 4 hardest questions on this part, answered in sentences a person could say aloud.

## Writing

- Short sentences. One idea per paragraph. Define a word before using it.
- Every claim comes from the ledger. Where docs and code disagree, say which is true today.
- Show weaknesses in the same voice as strengths, next to the part they belong to. A reader who is surprised in the room was failed by the guide.
- Answers are the strongest true thing to say. A question with no good answer says so and says what would fix it.

Write one self-contained HTML file beside the diagram, `<diagram>.guide.html`, with the diagram image in it and a contents list a reader can jump around. Where the session can publish pages, publish it as a private page too and give the user the link.
