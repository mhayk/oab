# Scenario 07 — Nothing needs to change

## What this guards against

**The reflex to always recommend something.** A review that always finds work is a review
that finds nothing: the team learns to discount it, and the genuine finding — when it
eventually appears — arrives with no credibility.

This scenario is not in the founding brief. It was added during design because it is the one
OAB is most likely to fail: producing an empty findings list requires the model to resist a
strong pull toward being helpful by listing observations.

## Why these assertions

- **`findings` length 0** — not "few findings", none. The system described has the
  scale-independent fundamentals in place (tested restores, timeouts, error tracking) and an
  architecture proportional to 12 RPS. There is nothing to report.
- **`triggers ≥ 2`** — but the review must still be useful. "Change nothing" without telling
  the team what to watch is an abdication, not an answer.

## The trap

A tempting failure is to report INFORMATIONAL observations to appear thorough. The assertion
allows INFORMATIONAL entries in the counts but requires the findings array itself to be empty,
so padding is not available.
