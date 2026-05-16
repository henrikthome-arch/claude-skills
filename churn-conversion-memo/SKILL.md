---
name: churn-conversion-memo
description: |
  Produce a board memo dissecting customer churn, signup-to-paid conversion, AND upsell barriers into named, fixable mechanisms with per-mechanism monthly ARR impact — given a sample of customer support interactions + accounts data + per-plan-tier LTV. Each mechanism names a specific file, screen, error string, policy clause, or feature gap (no abstract category labels). Output is a three-bucket decision table (Conversion / Churn / Upsell) plus aggregate impact claims (conversion-rate uplift, churn-rate drop, upsell-driven MRR uplift) plus a 3-bullet "what to ship in the next sprint" recommendation. The methodology was iterated through 30+ turns of trial and error on Sonetel's customer-service data; this skill captures what worked and what catastrophically failed. Read METHODOLOGY.md before producing any output.
argument-hint: <project_dir_path>
---

# churn-conversion-memo — entry point

## Use this skill when

- Producing a board / leadership memo on churn or conversion drivers from support-interaction data
- The user asks "what's driving our churn?" or "what fixes would grow ARR most?"
- Working in a project that has `data/accounts.csv` + `outputs/extractions_*.jsonl` (cohort-tagged customer interactions) + `data/ltv/ltv_by_plan.csv` (per-plan-tier LTV) — or equivalent

## Do NOT use this skill for

- Multi-year LTV projection work (different methodology — this skill operates on monthly rates)
- Productizing a customer-facing analytics feature
- Causal inference / experiments on retention (this skill does correlational analysis on support-conditional data)
- One-off ad-hoc questions about a specific customer

## The 6 hardest-to-recover rules — read these before anything else

1. **NEVER rank issue tags by LTV-weighted cohort over-representation.** That produces a tag-ranked table with tiny dollar figures that no operator can decide anything from. It is the methodology that took six iterations to abandon. Read ANTIPATTERNS.md §1 if tempted.

2. **ALWAYS split the deliverable into three buckets**: Conversion (signup → paying), Churn (paying → churned), Upsell (Basic → Premium). Never merge them into a single "8% to X%" claim. They affect different denominators.

3. **EACH mechanism must name a file, a screen, an error string, a policy clause, or a specific feature gap.** If a mechanism doesn't pass this test, drop it. "Verification friction" fails; "Upload tool returns 'request is invalid' on valid JPEGs" passes.

4. **NEVER multiply by 12 to get annual ARR from a monthly save.** On Basic-tier (typically 90%+ of paying base), monthly churn is ~8-12%, so expected post-save tenure is ~8-11 months not 12. Naive ×12 overstates headline ARR by ~2×. Use `min(12, 1/monthly_churn_rate)` — see METHODOLOGY.md §5.

5. **OPERATOR REVIEW is a thin drop-pass, not a calibration pass.** Stage 4 writes a markdown table for review and a JSON template — but the operator's only job is to DELETE mis-classified mechanisms. Claude computes `loss_rate` from the actual resolution-outcome distribution of underlying interactions, derives `fix_fraction` from a published `fix_type` heuristic, and surfaces both rationales inline in the memo. **Effort_tier and owner are out of scope** — the memo answers "what drives churn / what's addressable", not "who ships it / how long it takes". See METHODOLOGY.md §6 and ANTIPATTERNS.md §11.

6. **DERIVE contact rates from data; STATE the visible-vs-silent distinction explicitly in §1.** Heuristic silent-bounce multipliers (5/3/1) drift from reality — Sonetel's empirical contact rates differed from heuristic by 2-5× in multiple cohorts. Use `1 / empirical_contact_rate` as the math ceiling, with a single operator-judgment haircut (`ceiling_fraction`) per cohort; enforce `applied_multiplier ≤ math_ceiling` as a hard invariant in code. Then state explicitly in §1 (under the headline table) that *realistic ARR is grounded in customers who actually contacted support; upper-bound extends to silent customers under uniform-incidence* — otherwise a board reader misreads which figure is the floor and which is the sensitivity. See METHODOLOGY.md §10-12 and ANTIPATTERNS.md §12.

## Skill structure (load on demand, not all at once)

- **SKILL.md** (this file) — load at invocation. < 200 lines.
- **METHODOLOGY.md** — load at start of each new project's first invocation AND at the operator-review gate. The 9 hard-won lessons.
- **RUNBOOK.md** — load at execution start. Step-by-step ops guide.
- **ANTIPATTERNS.md** — load only when reviewer score < 8 and you need to know what failure mode to avoid.
- **EXAMPLES/SONETEL_v3.1_CASE_STUDY.md** — load on first invocation in a fresh project, as a worked-example template. Not on subsequent runs.
- **PROMPTS/*.md** — read by the pipeline scripts, not by Claude directly.

## Companion pipeline

This skill orchestrates the implementation specified in `CR-bulletproof-pipeline.md`. The skill knows the pipeline's stage names and contracts; the pipeline scripts compute. The skill does not duplicate pipeline logic.

If you are in a project that doesn't have the pipeline scripts yet (`scripts/extract_mechanisms.py`, `cluster_mechanisms.py`, etc.), STOP and either:
1. Build them first per `CR-bulletproof-pipeline.md` (substantial work, ~1 day)
2. Tell the user the prerequisite is missing and ask whether to defer

Do not improvise mechanism extraction by hand-curating a list — that's the v0 failure mode this whole skill exists to prevent.

## Convergence stop (don't chase 10/10)

Reviewer iteration on the memo stops when BOTH:
- Both reviewers score ≥ 8/10
- No new structural critiques (only polish-tier edits) in the most recent round

After that, ship. Do not run another reviewer round for the sake of process.

## The recommendation section MUST end the memo

The memo's final section is exactly 3 bullets, each a concrete shipping action with a named owner. Never:
- "Commission another memo"
- "Investigate further"
- "Consider..."

Each bullet names what to ship, who owns it, what eng cost it incurs, and what monthly ARR uplift it produces. If you can't say that, the bullet doesn't make the memo.

## Quick reference

| Step | Script | Output | LLM cost |
|---|---|---|---|
| 0. Validate inputs | `scripts/validate_inputs.py` | exit code | — |
| 1. Profile signup funnel | `scripts/profile_signup_funnel.py` | `outputs/funnel_profile.json` | — |
| 2. Extract mechanisms (LLM) | `scripts/extract_mechanisms.py` | `outputs/mechanisms_raw.jsonl` | ~$5-10 |
| 3. Cluster mechanisms | `scripts/cluster_mechanisms.py` | `outputs/mechanisms_canonical.json` | ~$1 (embeddings) |
| 4. **OPERATOR REVIEW gate** | (manual) | `outputs/operator_signoff.json` | — |
| 4.5. Validate signoff | `scripts/validate_signoff.py` | exit code | — |
| 5. Score mechanisms | `scripts/score_mechanisms.py` | `outputs/mechanisms_scored.json` | — |
| 6. Build decision tables | `scripts/build_decision_tables_v2.py` | three CSVs + `aggregate_impact.json` | — |
| 7. Generate memo | `scripts/generate_memo.py` | `MEMO.md` | ~$0.50 |
| 8. Audit gate | `scripts/audit_memo.py` | `outputs/audit_round_*.json` | ~$3-6 |
| 9. v3.1 baseline compare | `scripts/baseline_compare.py` | exit code | — |

Total per memo: ~$15-30 + ~30-60 min operator review.

## Files in this skill (paths relative to `~/.claude/skills/churn-conversion-memo/`)

- `SKILL.md` — this file
- `METHODOLOGY.md` — the 9 durable lessons
- `RUNBOOK.md` — step-by-step ops guide (deferred to implementation session — see CR-bulletproof-pipeline.md and CR-skill-churn-memo.md in any churn project for the spec)
- `ANTIPATTERNS.md` — what NOT to do, with named historical failures
- `EXAMPLES/SONETEL_v3.1_CASE_STUDY.md` — the worked example
- `PROMPTS/extract_mechanisms.md` — the Stage-2 LLM prompt template (deferred to implementation)
- `PROMPTS/reviewer_alignment.md`, `reviewer_business_sanity.md` — audit-agent prompt templates (deferred)
