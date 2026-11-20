---
name: explain
description: Explain a file, function, error message, or run result from this project in plain English for someone with no programming background. Use when a team member asks what something does, why something happened, or how to describe it in the presentation.
---

# Explain it plainly

The team knows finance, not code. They will have to explain this project to a professor and to
classmates trying to break it.

## How to explain

1. **One sentence first**: what this thing is for, in terms of the analyst's job.
2. **Where it sits**: which of the seven steps (fetch, extract, calculate/check, classify,
   decide, draft, approve) and who does it (Claude, code, or a person).
3. **What goes in and what comes out**, using the practice release's real values where possible
   (for example: `165,512` in thousands goes in, 165.512 comes out).
4. **Why it's built that way**, tied to the design principle in `CLAUDE.md`.
5. **A finance analogy** when one fits naturally (a source quote is a footnote; the checks are
   a tick-and-tie; the rules are an investment committee's written policy).
6. Offer to go one level deeper, and stop there.

## For an error message

Say what it means, the most likely cause, and the single next thing to try. Most errors in
this project are one of: `.venv` not active, a package not installed, something missing from
`.env`, or a typo in a CSV file.

## For a run result

Walk through it using the `rule` on each row: which rule fired, what condition triggered it,
and what evidence it rested on. `docs/PROJECT_GUIDE.md` section 7 has the rules.

## Style

- No jargon without a definition. `docs/PROJECT_GUIDE.md` section 17 is the glossary.
- Don't read code aloud line by line. Describe what a block accomplishes.
- Don't change any file during this skill.
- If asked "is this right?" about the design, give an honest answer including weaknesses;
  section 13 of the guide lists the known ones.
