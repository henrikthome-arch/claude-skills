# METHODOLOGY.md — the 9 hard-won lessons

These are the methodology choices that survived 30+ turns of iteration on Sonetel's customer-churn analysis. Each one names a *decision* (what we chose to do) and a *failure mode* (what would happen if you violated it). Treat them as load-bearing — every one was learned by failing first.

---

## 1. REFRAME from "tag rankings" to "named mechanisms"

The naive analysis is: extract issue tags per support interaction, compute cohort over-representation (early-churn vs retained), multiply by LTV, rank. This produces a *tag-ranked table with tiny dollar figures and no operator can decide anything from it.*

The reframe: **stop ranking tags. Identify named, fixable mechanisms.** Each row is a specific thing one engineer or one CS team member could go fix this week or this quarter. The methodology serves the answer, not the other way around.

The shift in unit:
- WRONG: `primary_issue|verification_friction over-indexes 1.16× in cohort 2`
- RIGHT: `Upload tool returns 'request is invalid' on valid JPEGs — 14 hits in cohort 2 sample, 1 eng-week to fix, ~$3K/yr realistic ARR recovery.`

Failure mode if violated: see ANTIPATTERNS.md §1 (the v1 LTV-tag-rankings disaster — six iterations to abandon).

---

## 2. ALWAYS split deliverables into three buckets

Three mechanically distinct things drive ARR. They have different denominators and different action owners.

| Bucket | What it is | Population | Impact metric | Owner |
|---|---|---|---|---|
| **A. Conversion** | signup → paying | monthly signups | conversion-rate uplift (pp) | Marketing + Product + Growth |
| **B. Churn** | paying → churned | paying base | churn-rate drop (pp) | Product + CS + Engineering |
| **C. Upsell** | Basic → Premium | Basic-tier paying customers | upgrade-rate uplift | Product + Marketing + Eng |

**Never merge these into a single "8% to X%" claim.** They affect different denominators. The board reads three separate aggregate statements:

> "Top-3 conversion fixes: +0.7pp on conversion → +233 new payers/month → $11K/yr realistic ARR."
> "Top-3 churn fixes: -0.55pp on churn → +184 retained/month → $9K/yr realistic ARR."
> "Pricing-page upsell A/B test: +928 upgrades/month → $86K/yr realistic ARR."

Failure mode if violated: cohort-1 conversion uplift gets mixed into a "churn-rate dropped" claim, board reviewer catches it, memo flops.

---

## 3. REQUIRE the granularity test on every mechanism

Each mechanism label must name a *file, screen, error string, policy clause, or feature gap*. Concrete handle, not abstract category.

| PASS | FAIL |
|---|---|
| "Upload tool returns 'request is invalid' on valid JPEGs" | "Verification friction" |
| "Pricing page does not surface Premium-feature delta inline at upgrade CTA" | "Pricing issues" |
| "WhatsApp Business compatibility article on sonetel.com is wrong" | "Communication problems" |
| "Pre-purchase product page silent on VoIP-OTP rejection by third parties" | "Pre-purchase opacity" |
| "Free-trial balance warning email fires during trial window" | "Trial UX confusion" |

If a mechanism doesn't pass, **drop it**. Do not weaken the test to keep more rows in the table — better to have 10 sharp mechanisms than 30 vague ones.

Programmatic enforcement: the pipeline's Stage 3 runs a regex / classifier pass on `granularity_anchor` field and drops mechanisms whose anchor doesn't match the pattern. Hand-curation is not enough — make the gate automated.

---

## 4. REPORT lower-bound / upper-bound ranges, never point estimates

Every ARR figure in the memo is a range. Two reasons:

1. **Support-contact-only bias**: only a fraction of affected customers contact support. The visible-from-data number is a lower bound; the true population impact is a multiple. Use silent-bounce multipliers (5× for Bucket A, 3× for Bucket B, 1× for Bucket C since upsell is directly observable) as the upper bound. Anchor: ~6% of cohort-1 accounts contact support over 12mo → silent population is ~16× → conservatively haircut to 5×.

2. **Point estimates are unfalsifiable**: a CFO will ask "why $8,750 and not $8,000 or $10,000?" There is no answer. A range answer ("$5-12K/yr") is honest about the parameter uncertainty.

Every row reports: `ARR realistic (lower) / ARR upper-bound (silent-adjusted)`. The aggregate sections also report ranges, not points.

Failure mode if violated: false precision invites pushback you can't survive.

---

## 5. NEVER multiply by 12 to annualise ARR — the ×12 trap

`recovered_customers_per_month × MRR × 12` overstates ARR by ~2× on Basic-heavy customer bases. Why: a saved customer continues to face their plan's natural monthly churn rate. On Basic (8-12% monthly churn), expected residual months ≈ 1/0.10 = 10, not 12.

Correct formula:
```
expected_post_save_tenure = min(12, 1 / plan_mix_weighted_monthly_churn_rate)
annual_ARR_recovery = recovered_customers_per_month × weighted_MRR × expected_post_save_tenure
```

For Basic-heavy mixes (which is most B2B SaaS at typical conversion rates), use **8 months realistic + 12 months best-case ceiling** as a dual report.

Exception: upsell mechanisms (Bucket C). Plan-tier changes are essentially permanent until the customer churns entirely, so 12-month tenure is appropriate. Use the standard 12.

Failure mode if violated: ARR claims overstated 2×, CFO catches it, methodology defensibility tanks.

---

## 6. OPERATOR REVIEW IS A DROP-PASS, NOT A CALIBRATION PASS

The pipeline is **automated extraction → operator drop-pass → automated scoring**.

The operator (Stage 4) does ONE thing: **deletes mechanisms that the LLM clearly mis-classified or duplicated**. Examples worth dropping: a compliance/ethics issue tagged as a churn driver; near-duplicates the clustering missed; mechanisms whose evidence quotes don't actually support the label.

The operator **does NOT**:
- Set or adjust `loss_rate`
- Set or adjust `fix_fraction`
- Attach `effort_tier`
- Attach `owner`

Those are computed (loss_rate from data) or omitted entirely (effort_tier and owner are out of scope — the memo answers "what drives churn and what's addressable", not "how does each fix get shipped"). See ANTIPATTERNS.md §11.

### How loss_rate is computed (not asked of the operator)

For each canonical mechanism, look up the underlying interactions and compute:

```
loss_rate = count(resolution_outcome ∈ {customer_disengaged, unresolved, explicit_cancellation_request, escalated-without-resolution}) / count(all_interactions_for_this_mechanism)
```

Cite the count in the per-row rationale: *"5 of 7 underlying interactions ended in customer_disengaged or unresolved → loss_rate 0.71."* This is observational, not speculative.

### How fix_fraction is computed (heuristic with stated source)

A published heuristic from the `fix_type` field, stated in the memo's caveats:

| fix_type | fix_fraction range | rationale |
|---|---|---|
| copy | 0.8 – 0.9 | wording fix recovers nearly all mis-fit purchases pre-checkout |
| config | 0.7 – 0.9 | flag flip + UX surface; high recovery |
| engineering | 0.6 – 0.8 | bug fix recovers most, edge cases remain |
| policy | 0.3 – 0.5 | per-country alternative document paths; partial only |
| process | 0.3 – 0.4 | process redesign — partial improvement; long tail remains |

A specific mechanism may override the heuristic if its evidence justifies — but the override gets a sentence in the rationale.

### When something requires business context Claude can't infer

E.g. "Is this policy externally regulatory or internal?" or "Is feature X already on the roadmap?" — surface as `ASSUMPTION (pending <person>)` in the memo. Pick a defensible default and ship; the operator's read updates the assumption note, not the per-row math (which is recomputed when the assumption is resolved).

**Failure mode if violated**: the operator is asked to speculate about numbers they have no observational basis for. The memo's calibration becomes a fiction. See ANTIPATTERNS.md §4 (hand-curated lists pretending to be a model) and §11.

---

## 7. REVIEWER-ROUND DISCIPLINE — stop at convergence

When iterating on the memo (after Stage 7), spawn TWO reviewer agents with different lenses:

- **Alignment with stated goal**: scores against what the user asked for (e.g., "named contributors, per-line ARR, aggregate impact")
- **Business sanity / CFO lens**: scores against operational defensibility (arithmetic, cohort denominators, CAC, time-to-impact realism)

Target: both ≥ 8/10. **Stop iterating at convergence — do not chase 10/10.** Convergence = both ≥ 8 AND no new structural critique (only polish-tier wording edits) in the most recent round.

If reviewers plateau at 7 across two rounds with same critique, **escalate to operator** with the diff and ask whether to ship at 7 or pivot. Do not silently keep iterating.

Failure mode if violated: rounds-on-rounds of reviewer theatre. The user gets impatient; the actual deliverable doesn't improve.

---

## 8. THE 6 HONESTY CONSTRAINTS — memo-killing if violated

These are scored in the audit gate. Any single 0 = hard-fail the memo, revise.

1. **No `time-to-impact` column in the decision tables.** Effort tier (cost) yes; timing speculation no. Sequencing belongs in the recommendation section, not the per-row table.
2. **Asterisk N<5 rows.** Mechanisms with fewer than 5 hits in their target cohort are flagged `*(N<5: directional only)*` in the published table. Do not commit budget against these rows alone.
3. **Ranges, not points.** Every ARR figure is a range. Every fix_fraction is hand-calibrated with rationale.
4. **Per-row rationale present.** Each `loss_rate` and `fix_fraction` carries a one-sentence explanation. Boilerplate copy-paste rationale fails this check.
5. **Aggregate sums per-bucket only, no rate-merging.** Conversion-rate uplift and churn-rate drop are NOT additive; report them separately.
6. **Recommendations are concrete shipping actions.** "Commission another memo" or "Investigate further" or "Consider..." is forbidden. Each recommendation names *what to ship* and *what monthly ARR uplift it produces*. **Owner and eng-cost are explicitly out of scope** — the memo answers what + how-much, not who + how-long. See ANTIPATTERNS.md §11.

---

## 9. AVOID the structural failure modes (see ANTIPATTERNS.md)

These are the specific historical mistakes that this skill exists to prevent. Read the file. Don't repeat the experiments.

Short list:
- LTV-weighted tag rankings (the v1 disaster)
- Punting upsell to a follow-on memo when it's the biggest line item
- Hand-curated mechanism lists pretending to be a model
- Manufactured "awaiting X" gates in conversation when forward work is available
- Reviewer theatre — spawning rounds-on-rounds beyond convergence
- Time-to-impact columns inviting false precision
- ×12 ARR multiplier (overstatement)
- Asking "do you have what you need?" instead of trying it

---

## 10. DERIVE silent-bounce multipliers from data, not heuristic anchors

The v1-v3 methodology used heuristic silent-bounce multipliers (5× for Bucket A, 3× for B, 1× for C), anchored to a hand-stated "~6% of cohort-1 accounts contact support." That number was itself a guess. When Sonetel actually derived contact rates from `accounts.csv`, the empirical values were materially different:

| Cohort | Heuristic contact rate | Empirical (derived 2026-05-15) | Heuristic multiplier | Empirical math ceiling (1/rate) |
|---|---:|---:|---:|---:|
| C1 (never paid) | 6% | **0.76%** | 5× | **132×** |
| C2 (early churn) | 55% | **27.7%** | 3× | **3.61×** |
| C3 (late churn) | 30% | **26.6%** | 3× | **3.76×** |
| C4 (retained) | 10% | **40.8%** | 1× | **2.45×** |

The heuristic was off by 2-5× in multiple cohorts. The CR's own *predicted* empirical values (drafted before derivation) were also wrong — particularly C3 at predicted 75.6% vs actual 26.6%. Finding the predictions wrong IS the win; that's the whole point of deriving from data.

**The modern formula**: `applied_multiplier = math_ceiling × ceiling_fraction`, where:
- `math_ceiling = 1 / empirical_contact_rate` (derived from `accounts.csv`)
- `ceiling_fraction` is the *only* operator-judgment knob per cohort (haircut)
- Hard invariant: `applied_multiplier ≤ math_ceiling` (enforced in code)

The applied multipliers shipped: C1 = 132 × 0.04 = **5.28×**, C2 = 3.61 × 1.0 = **3.61×**, C3 = 3.76 × 1.0 = **3.76×**, C4 = 2.45 × 0 = **0×** (signal-only).

**C1's deep haircut (0.04) is independent reasoning**, not a back-fit to the prior 5×. C1 is dominated by signup ghosts who abandoned before encountering the support-revealed mechanisms — their counterfactual incidence on those mechanisms is structurally lower than visible contactors. Document this *in the memo* (don't let it look like the fraction was tuned to land near the heuristic).

Failure mode if violated: heuristic multipliers drift from reality; "C3's 3× exceeds its 1.32× ceiling" type claims that turn out to be false under actual data; reviewer asking "how did you arrive at these numbers" with no defensible answer.

---

## 11. STATE explicitly what the realistic ARR figure is grounded in (and what it isn't)

The realistic ARR is computed entirely within visible-contactor signal:
```
affected_monthly = cohort_monthly_volume × sample_inc_rate × empirical_contact_rate
recovered_monthly = affected_monthly × loss_rate × fix_fraction
annual_arr_realistic = recovered_monthly × plan_ltv_12m
```

The `× empirical_contact_rate` step extracts the visible-contactor portion. **The realistic figure assumes silent customers contribute zero.** The silent multiplier only enters in the upper-bound figure (`upper = realistic × silent_multiplier`).

**This distinction must be explicit in the memo**, in three places:
1. Under the §1 headline table — one line: "all figures grounded in customers who actually contacted Sonetel support; upper-bound below extends to silent customers under uniform-incidence."
2. At the start of §9 caveat 4 (silent multipliers) — restate the same distinction before introducing the multiplier mechanics.
3. In any prose discussion of "Combined upper" or "upper-bound" — flag that it's a sensitivity, not a forecast.

Failure mode if violated: board reader sees `realistic = $37K, upper = $146K` and either treats them as alternative scenarios (wrong — they're floor and ceiling of the same scenario) or dismisses the upper as "pie in the sky" without understanding its uniform-incidence grounding. See ANTIPATTERNS.md §12.

**Companion lesson — Year-1 ramp**: the stated ARR is *steady-state annual run-rate*, not Year-1 actual. With recoveries arriving month-by-month, Year-1 averages **~54% of the steady-state figure** (average active cohorts during Year 1 = 6.5; steady-state = 12; ratio = 6.5/12). State this in §9: "$37K/yr steady-state ≈ $20K in Year 1, $37K/yr Year 2+." A board member committing budget against the stated figure needs to know the Year-1 ramp.

---

## 12. THE LTV-OPTIMISM CAVEAT — `plan_ltv_12m ≈ MRR × 12` deserves scrutiny

If your `plan_ltv_12m` figure from FinOps looks suspiciously close to `MRR × 12` (i.e., it implies full 12-month retention), it is probably NOT meaningfully churn-weighted, regardless of what the FinOps caveat claims. Validate against monthly-churn assumptions: if the cohort has 8.8%/month gross churn, expected residual revenue per customer is ≈ MRR × (1 - 0.912^12) / 0.088 ≈ MRR × 7.7, not MRR × 12. A `plan_ltv_12m` ≈ MRR × 12 figure is optimistic.

If you can't get a reliably-churn-weighted LTV: state the LTV-optimism caveat in §9 explicitly. *"If recovered customers churn at the cohort's normal monthly rate, both the Year-1 and steady-state figures could be 30-50% lower."* Treat the stated figures as a ceiling on expected recovery revenue, not a guarantee.

Failure mode if violated: silently inflated ARR by ~30-50%; CFO catches it on review or after deployment when actuals come in low; methodology defensibility tanks.

---

## 13. AUDIT fix_fraction on cancel-heavy mechanisms before shipping

The default `fix_fraction` heuristic by `fix_type` (engineering=0.7, policy=0.4, copy=0.85, process=0.35) assumes the customer wants the underlying service to work. **This breaks for mechanisms whose underlying customers were on the way out before the mechanism ever touched them.**

After Stage 5 scores mechanisms, run this audit before the operator approves the memo:

**Diagnostic** — for every Yes-fixable mechanism, look at the underlying interaction-level fields:
- `explicit_cancellation_request` rate
- `churn_intent_score` distribution
- evidence quotes (do they describe customers asking the service to WORK, or asking to LEAVE?)

**Classification**:

| Pattern | Indicator | Treatment |
|---|---|---|
| **Friction-caused exit intent** | High cancel-request rate BUT mechanism anchor is about signup/activation/feature-gap/UX. Evidence quotes describe customers wanting service to work but failing. | **Keep heuristic** fix_fraction. The fix removes the friction; the cancel-request was a symptom. |
| **Pre-existing exit intent** | High cancel-request rate AND mechanism anchor is about cancellation flow / refund flow / deactivation / reactivation friction. Evidence quotes describe customers asking to leave or get money back. | **Haircut** fix_fraction to 0.10-0.25 depending on win-back potential. The mechanism's "fix" mostly delivers operational savings (less ticket time, fewer chargebacks), not retention. |
| **Decision-moment friction** | Mechanism is at a fork (top up vs cancel; renew vs lapse). Customers are explicitly choosing exit. | **Haircut** to ~0.25. Some marginal customers would have stayed with one-click recovery (silent attrition recovery); most chose to leave. |

Worked example from Sonetel run (2026-05-16):

| ID | Mechanism | cancel% | Default fix_fraction | Audited fix_fraction | ARR impact |
|---|---|---:|---:|---:|---|
| m024 | No in-call cancellation | 100% | 0.7 (eng) | **0.15** | $4,510 → $966 |
| m038 | No self-serve cancellation | 80% | 0.7 (eng) | **0.15** | $3,151 → $675 |
| m035 | Refund to balance not CC | 60% | 0.4 (policy) | **0.10** | $4,508 → $1,127 |
| m021 | Calls-paused email no top-up CTA | 83% | 0.7 (eng) | **0.25** | $4,901 → $1,750 |

**Net effect on the Sonetel headline**: Combined realistic dropped from $30,741 to $24,209 (−21%), which was the right correction — those mechanisms were overstating recoverable revenue from customers who were already leaving.

**Failure mode if violated**: every mechanism with cancellation-flow framing inherits the default 0.7 fix_fraction and contributes engineering-tier ARR. The combined number looks defensible until the board reviewer asks "how is making cancellation easier going to retain customers who came to cancel?" — and the methodology has no answer. See ANTIPATTERNS.md §14.

**Implementation hook**: add to Stage 7 (memo generation) a pre-flight check that flags every Yes-fixable mechanism with cancel_request rate > 50% for operator review. Either the operator overrides fix_fraction, or they confirm "this is friction-caused" with a one-sentence note.

---

## When to deviate from this methodology

Almost never. These rules came from failures. If a project's data shape genuinely requires deviating (e.g., no support-contact data exists at all), surface the deviation to the operator explicitly with rationale and audit-trail — do not silently improvise.
