# RUNBOOK.md — operational guide

Load this file at execution start (when you're about to run the pipeline). It assumes you've already read SKILL.md and METHODOLOGY.md.

## Prerequisites (before running anything)

Project must have:
- `data/accounts.csv` — account-level data with required columns (see Stage 0).
- `outputs/extractions_*.jsonl` — cohort-tagged customer interactions with structured extractions (the v2 schema from the source project's extract.py).
- `data/ltv/ltv_by_plan.csv` — per-plan customer counts and LTV figures.
- `config/pipeline.yaml` — tunables (min_n_floor, silent-bounce multipliers, tenure, etc.).
- `.env` with `ANTHROPIC_API_KEY` set.
- Python packages: `anthropic`, `pydantic`, `pyyaml`, `scikit-learn`, `numpy`, `python-dotenv`.

If any prerequisite is missing, STOP and tell the operator what's missing — do not improvise data.

## Cost guidance

- Stage 2 (mechanism extraction): ~$2 for 1000 interactions on Sonnet 4.6 with prompt caching.
- Stage 8 (audit): ~$1 per round (two reviewers in parallel).
- Total per memo run: ~$3-5.

Don't ask the operator for permission for spends ≤ $30. Ask before any operation that would exceed $100.

## Stage-by-stage execution

Run stages in strict order. Each script reads the previous stage's outputs and writes its own. If a stage exits non-zero, fix the cited issue and re-run — don't skip ahead.

### Stage 0 — validate inputs

```
python3 scripts/validate_inputs.py
```

Schema-gates required files. Exit 0 → proceed. Exit 1 → fix the named issue.

### Stage 1 — profile signup funnel

```
python3 scripts/profile_signup_funnel.py
```

Writes `outputs/funnel_profile.json`. Reads accounts.csv. Computes monthly signup volume (post-Skype-wave normalised), per-cohort conversion rates, blended-base churn rate, plan mix.

**Known gotcha**: per-plan monthly churn rate uses a fixed-window survival formula (`1 - (1-p)^(1/T)`). The earlier linear-`p/T` form returns 0.0 — that bug is documented in METHODOLOGY.md §5 and fixed in the script. Verify Basic comes out in the 15-30%/mo range (cohort early-attrition) and the blended-base figure separately matches the ~8-12% expected from current-payer methodology.

### Stage 2 — LLM mechanism extraction

```
python3 scripts/extract_mechanisms.py [--restart]
```

For each row in `outputs/extractions_mvp_v2.jsonl`, calls Sonnet 4.6 with the `record_mechanisms` tool. Writes `outputs/mechanisms_raw.jsonl` (~3-5 mechanisms per interaction on average) and a checkpoint file `outputs/extract_mechanisms.processed.jsonl`. Resumable — re-run without `--restart` to continue.

**Reproducibility**: temperature=0, prompt-cached system prompt → re-runs on the same data produce >85% Jaccard similarity on canonical mechanism labels after Stage 3. If the second run drops below 85%, something is wrong (model upgrade, schema change).

Expect ~25 minutes wall clock, ~$2.

### Stage 3 — cluster near-duplicates

```
python3 scripts/cluster_mechanisms.py
```

TF-IDF char-ngrams (3-5) + agglomerative clustering with cosine distance threshold 0.6. Drops `specificity_score == 1` mechanisms (abstract categories — METHODOLOGY.md §3). Applies the programmatic granularity test (regex pattern over the anchor field). Enforces MIN_N_FLOOR. Writes `outputs/mechanisms_canonical.json`.

**Tuning the distance threshold**: 0.6 is loose enough to merge "Multi-round IDV" with "Document portal returns 'cannot create submission'" but tight enough to keep distinct mechanisms apart. If you see way too many singleton clusters, increase to 0.7. If similar concepts are being split, increase more.

Expect 20-50 canonical mechanisms after all filters. The v3.1 baseline had 15 (hand-curated, tighter).

### Stage 4 — operator review gate ⚠️ HUMAN-IN-THE-LOOP

```
python3 scripts/operator_review.py
```

Writes `outputs/REVIEW_ME.md` (markdown table for review) and `outputs/operator_signoff_template.json` (pre-filled JSON for the operator to edit).

**STOP HERE.** The pipeline is on a hard checkpoint. The operator must:
1. Read `outputs/REVIEW_ME.md`.
2. Edit `outputs/operator_signoff_template.json` — fill `<<EDIT...>>` fields for each mechanism kept (loss_rate + rationale, fix_fraction + rationale, effort_tier, owner). Delete entries for mechanisms to drop. Set `manual_override=true` + justification if `loss_rate × fix_fraction > 0.7`.
3. Save as `outputs/operator_signoff.json` (drop the `_template`).
4. Resume the pipeline at Stage 4.5.

If you're invoked AFTER the operator has filled the signoff, skip Stage 4 (don't overwrite their work).

**For end-to-end TESTING ONLY**: invoke `operator_review.py --from-baseline-v3` to auto-populate the signoff from a prior hand-curated baseline (e.g. `outputs/mechanisms_v3.json`). This is NOT a substitute for real review — it exists to validate that downstream stages run cleanly.

### Stage 4.5 — validate signoff

```
python3 scripts/validate_signoff.py
```

Pydantic + bounds checks (CR reviewer fix #3): rates in range, `manual_override` flag where required, granularity-anchor regex still passes, at least one evidence quote, no unfilled `<<EDIT>>` placeholders, target_cohort recognised. Exit 0 → proceed. Exit 1 → fix the named issue in operator_signoff.json.

### Stage 5 — score mechanisms

```
python3 scripts/score_mechanisms.py
```

Applies the financial model from CR-actionable-reframe + Bucket-C upsell math from CR-bulletproof-pipeline reviewer fix #1. Writes `outputs/mechanisms_scored.json`.

**Three formulas, three buckets**:
- Bucket A (conversion): `affected = N_monthly × inc × contact_rate; recovered = affected × loss × fix; ARR = recovered × weighted_MRR × tenure_8mo`. Silent multiplier 5×.
- Bucket B (churn): same shape but denominator is `monthly_paying_base`. Silent multiplier 3×.
- Bucket C (upsell): `affected = basic_paying_base × inc` (no contact-rate haircut — observable). `monthly_upgrades = affected × loss × fix`. `ARR = upgrades × MRR_DELTA ($7.75) × 12mo`. Silent multiplier 1×.

`cross-cutting` bucket is routed into Bucket B for math (kept as separate label in the table for traceability).

### Stage 6 — build decision tables

```
python3 scripts/build_decision_tables_v2.py
```

Reads `mechanisms_scored.json`. Writes:
- `outputs/decision_table_conversion.csv`
- `outputs/decision_table_churn.csv`
- `outputs/decision_table_upsell.csv`
- `outputs/aggregate_impact.json`

Schema enforced: NO `time_to_impact` column (ANTIPATTERNS §7). `*` flag on rows below MIN_N_FLOOR. Aggregate roll-up per bucket — rate impacts NEVER summed across buckets (METHODOLOGY.md §2).

### Stage 7 — generate memo

```
python3 scripts/generate_memo.py
```

Template-driven memo synthesis from the three decision tables + aggregate impact. No LLM call — the structure is rigid by design (METHODOLOGY.md §1). Writes `MEMO.md` with the 10-section structure.

**Per-row rationale must be inline** (honesty constraint #4). The script renders `loss_rate_rationale` and `fix_fraction_rationale` directly in each row.

**The recommendation section ships exactly the top-3 ARR mechanisms per bucket** — the bullets must align with the §1 headline figures (alignment-reviewer hard requirement).

### Stage 8 — audit gate

```
python3 scripts/audit_memo.py
```

Spawns two reviewer agents in parallel (alignment lens + business-sanity lens). Each scores 1-10 overall plus 6 honesty constraints individually. Writes `outputs/audit_round_<N>.json`.

Pass condition: BOTH reviewers ≥ 8/10 AND no honesty constraint scored 0.

**Stop iterating at convergence** (METHODOLOGY.md §7 / ANTIPATTERNS §6). If both reviewers hit 8/10 with only polish-tier critique, ship. If they plateau at 7/10 across two rounds with the same critique, escalate to operator — don't silently keep iterating.

### Stage 9 — v3.1 baseline compare (only if you have a v3.1 baseline)

```
python3 scripts/baseline_compare.py [--accept-divergence --note "..."]
```

Verifies the new pipeline reproduces ≥ 80% of v3.1's mechanisms by fuzzy label match AND that top-3 ARR per bucket is within ±30% of v3.1. Fail → exit 1 unless `--accept-divergence` is set with a note.

Expected behaviour on a fresh sample: the new pipeline finds MORE mechanisms than v3.1 (the methodology is more comprehensive), so ARR sums may exceed v3.1's by 2-3×. That's a documentable divergence, not a failure — pass `--accept-divergence --note "<reason>"`.

## What to do when a stage fails

| Failure | Where to look | Fix |
|---|---|---|
| Stage 0 missing column | the named CSV | data prep upstream |
| Stage 2 row malformed | `outputs/mechanisms_raw.jsonl` | Stage 3 skips them; if >5% are malformed, investigate the LLM prompt |
| Stage 3 too few mechanisms (< 15) | `outputs/mechanisms_canonical.json` | loosen `cluster.distance_threshold` from 0.6 to 0.7, OR lower `min_n_floor` from 5 to 3 |
| Stage 4.5 placeholder still present | `outputs/operator_signoff.json` | operator needs to finish editing |
| Stage 5 KeyError on bucket | `score_mechanisms.py:get_silent_multiplier` | add bucket to `config/pipeline.yaml` |
| Stage 8 < 8/10 with same critique twice | `outputs/audit_round_*.json` | escalate to operator — don't keep iterating |
| Stage 9 ARR divergence | the data, not the code | accept-divergence with note IF the new pipeline finds more mechanisms; investigate IF same mechanism count |

## When to STOP and ask the operator

- A stage fails twice with the same error after a fix attempt.
- Two audit rounds plateau at 7/10 with no new structural critiques.
- A mechanism the operator clearly mis-classified is dominating the table (e.g. compliance items showing as churn drivers — see SONETEL_v3.1_CASE_STUDY.md for the "$10 credit incentive" example).
- Cost projection for a re-run exceeds $30.

## What ships at the end

- `MEMO.md` (the deliverable)
- `outputs/mechanisms_scored.json` (every claim is traceable through this)
- `outputs/operator_signoff.json` (the human-in-the-loop calibration)
- `outputs/aggregate_impact.json`
- Three `decision_table_*.csv` files
- `outputs/audit_round_<final>.json`

Per PII residency (CR §"Secondary fixes" #11): raw inputs (accounts.csv, extractions_mvp_v2.jsonl) and `mechanisms_raw.jsonl` are deleted from local disk after the memo is finalised. `MEMO.md` and the canonical/scored JSONs retain only 250-char evidence excerpts.
