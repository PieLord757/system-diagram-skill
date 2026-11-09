# Likely questions and the grill

Two things live here: how to predict what someone will be asked about a system, and how to test whether they can answer.

## Predicting the questions

Walk every box and arrow in the ledger and ask each lens below. Keep a question when a sharp outsider would really ask it and the answer changes what they think. Skip the rest.

| Lens | The question it produces |
| --- | --- |
| **Existence** | What breaks if this part is removed? |
| **Alternatives** | Why this, and not the obvious option? What did you try first? |
| **Numbers** | Where does this number come from? What is it at 10x? |
| **Bottleneck** | What runs out first: money, time, a rate limit, a person? |
| **Failure** | What happens if this step dies halfway? Can it be re-run safely? Who notices? |
| **State** | Where is the source of truth? What if two copies disagree? |
| **Trust** | Who can read this? What stops one user seeing another's data? What if the input is hostile? |
| **Evidence** | How do you know it works? Who graded it? What is the denominator? |
| **Ownership** | Which parts did you build, and which are someone else's? Why can't this be copied? |
| **Real or planned** | Is that running today? Show me where. |
| **Follow-up** | Take the likely answer and ask "why?" twice more. |

Questions that cannot be answered well are the most valuable output. Put the honest answer beside them, and say what would have to change for a better one. Add anything the user has actually been asked, in meetings or reviews, and mark those as asked.

When a person's stated answer would not survive a follow-up, say so and give the true version. Teach the strongest answer that is true, even when a vaguer one would sound better.

## The grill

Offered at the end. If they accept, ask who is across the table: a senior engineer, a new teammate, an examiner. The persona sets the tone and which lenses come first, never the standard of truth.

Interview relentlessly until the knowledge tree is empty. The **knowledge tree** maps what must be understood: each concept branches into what depends on it (you cannot defend a cache size before you understand what is being cached).

Work in **rounds**. The **frontier** is every concept whose prerequisites they have already shown they understand. Ask 5 or more frontier questions at once, numbered:

```
❓ **Q1** - **<short title>**: <the question, as that person would actually put it>
```

Then stop and wait. Show no answer yet, because an answer in view turns a test of recall into a test of reading.

When they reply, for each question:

```
**Q1**: Right | Partly | Wrong
What held up. What was missing or false.
➡️ The answer I would give, in the words I would say it.
Source: `repo/path:line`
```

Grade against the ledger, never against your own impression of what sounds right. "I don't know" is a good answer when it is true and comes with what they would check; credit it.

Each round reshapes the tree. A right answer pushes the frontier deeper: ask the follow-up. A wrong one sends the frontier back to the concept beneath it, in simpler terms from one concrete example, before moving on. Bring missed questions back later, reworded, to see if it stuck.

**When someone is learning, not defending.** If they miss a foundation, ask what a term means, or say they are still learning, teach before you test, and keep the round: explain each concept from one concrete example in a few lines, then ask several questions together that make them work new examples. Ask one question alone only when the next one truly depends on its answer. Move on once a concept is explained twice and still not landing, and mark it shaky.

Finding facts is your job. If a question needs something outside the ledger, send a subagent to look while you carry on with the rest of the frontier. If the grill exposes a real gap in the design, which is a decision and not a fact, name it, recommend an answer, and let the user decide.

## Improving the guide and diagram as you go

A wrong answer is evidence about the explanation as well as the person. A missed idea or a word they had to ask about means the guide failed there.

- **After every round, update the guide.** Put each fix in the section where that concept lives, written as if it had always been there. Headings stay about the system, never about the grill.
- **At the end, rebuild the diagram once.** Rebuild sooner only if it is factually wrong or they missed the same concept twice, because a picture that shifts mid-test changes what is being tested.
- Add only what has already been graded, so an update cannot reveal an upcoming question. Add new facts to the ledger first.

## Finishing

The grill is done when the frontier is empty: every branch visited, and they have answered it unaided at least once. When time is short, agree a number of questions at the start and take the weakest branches first. Finish with a short scorecard: solid, shaky, and the three answers to practice.
