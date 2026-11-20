---
name: log-failure
description: Record a way the agent broke, or could break, in docs/failure_log.md. Use whenever a run gives a wrong figure, wrong call, wrong document, crash, or surprising result.
---

# Log a failure

1. Read `docs/failure_log.md`. Check whether this failure is already there:
   - if an `anticipated` entry now happened for real, update that entry (status `observed`,
     add the date, release, and what happened) and stop;
   - otherwise use the next free number (F-005, F-006, ...).
2. Gather the facts. Ask for anything missing; don't guess:
   - which release or file, and who found it
   - what the agent produced (quote the figure, call, and rule from `data/runs/` if a run was saved)
   - what the right answer was, and how the team knows
3. Work out the root cause by reading the saved run and the release text. Name the step where it
   went wrong: fetch, extract, calculate/check, classify, decide, or draft. If you can't tell,
   write "unknown" and what would be needed to find out.
4. Set severity:
   - `high`: a wrong number or call reached the output looking correct (verified, not flagged)
   - `medium`: wrong or missing, but flagged or sent to NEEDS REVIEW
   - `low`: inconvenience only
5. Set status: `observed`, `mitigated` (name the check, rule, or prompt version that handles it),
   or `accepted` (documented, not fixed, with the reason).
6. Append the entry using the template at the top of the file. Write it so someone who wasn't
   there understands it. Keep "what happened" to facts and put interpretation under "why".
7. Tell the user the entry number and, in one line, whether it's worth a slide.

Don't fix anything as part of this skill. Logging and fixing are separate decisions.
