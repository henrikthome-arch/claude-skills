# SONETEL v3.1 CASE STUDY — what the methodology looked like on real data

Read this on the first invocation in a fresh project. It's the worked example the rest of the skill abstracts from. Annotated decision points where the methodology nearly went off the rails.

## The deliverable

A board memo answering: "what specifically drives Sonetel customer churn and signup-to-paid conversion, and which mechanisms are addressable?"

Final output: 15 named mechanisms across 3 buckets (Conversion / Churn / Upsell), with per-mechanism ARR figures (realistic + silent-bounce upper bound) and a 3-bullet recommendation.

## The data shape

- 1,000 customer-service interactions sampled across 4 cohorts (250 each):
  - **C1 / "1_never_paid"**: signed up but never paid
  - **C2 / "2_early_paid_churn"**: paid once then churned within 60 days
  - **C3 / "3_late_paid_churn"**: paid for > 60 days then churned
  - **C4 / "4_retained"**: still actively paying
- Per-interaction structured extractions already exist (the v2 schema with primary_issue_freetext, agent_observations_freetext, resolution_outcome, etc.).
- Account-level data joined from the company's prod database.
- Per-plan LTV figures from the finance team.

## Headline numbers — final v3.1 memo

| Bucket | Top-3 ARR/yr realistic | Combined-all ARR/yr | Rate impact |
|---|---|---|---|
| A. Conversion | $11K | $15K | +0.675pp conversion |
| B. Churn | $9K | $13K | -0.55pp churn (8.8% → 8.25%) |
| C. Upsell | **$86K** | **$86K** | +929 upgrades/mo |
| All three | — | **$113K** | — |

## Decision points and how they nearly broke the memo

### Decision 1: Should the deliverable rank issue tags or name mechanisms?

The naive impulse was: "extract tags per interaction, compute over-representation in churn cohorts, rank by LTV impact, ship." Six rounds of methodology refinement made the resulting table prettier without making it more useful.

What broke through: Henrik's question — *"I am not seeing how this can be useful and actionable. Help me understand."*

The reframe: stop ranking tags. **Name fixable mechanisms.** Each row must be a specific thing one engineer or CS team member could go fix this week or this quarter. "Verification friction" → "Upload tool returns 'request is invalid' on valid JPEGs". The granularity test became hard-required (METHODOLOGY.md §3).

### Decision 2: How many buckets?

First impulse: one table, ranked by ARR. But "+0.7pp conversion" and "-0.55pp churn" aren't additive — they affect different denominators (signups vs paying base). A "combined rate change" claim is unfalsifiable.

The fix: **always three buckets** (Conversion / Churn / Upsell). Aggregate per bucket. Never merge into a single rate claim. The board reads three separate aggregate statements.

### Decision 3: 8 months or 12 months tenure?

`recovered_customers/month × MRR × 12` = annual ARR. Standard formula.

But: on Basic-tier (92% of paying base, $5.25/mo, monthly churn ~8.8%), a saved customer's expected residual lifetime is ~10 months, not 12. The ×12 multiplier overstates by ~2× on Basic-heavy bases.

The fix: `expected_post_save_tenure = min(12, 1/monthly_churn_rate)`. Use 8 months realistic / 12 months ceiling as a dual report. The CFO-lens reviewer caught the ×12 trap in v2. (Exception: Bucket C upsell uses 12 because plan-tier changes are permanent until full churn.)

### Decision 4: Should Bucket C upsell be a sidebar or co-equal?

First impulse: the v2 sample's strongest signal for Bucket C was a single pricing-page mechanism. Relegated to §5 "sidebar." Recommended commissioning another memo to analyze upsell properly.

What broke that: it was the single biggest line item ($86K/yr at 3% upgrade lift — vs. $11K + $9K = $20K for buckets A and B combined top-3). The board-deliverability reviewer scored that section 3/10. Telling the board "the biggest opportunity is over here, but we'll need another memo" was an analysis-incompleteness confession AND missed the point of the deliverable.

The fix: Bucket C co-equal with A and B in the decision table. Never punt to a follow-on memo (METHODOLOGY.md §8 honesty constraint #6).

### Decision 5: How to handle silent-bouncers?

Visible-from-data: ~6% of cohort-1 accounts contact support over 12mo. The other 94% experience the same friction silently.

Naive multiplier: 1/0.06 = 16.7×. Inflates ARR claims dramatically.

The fix: report realistic (visible) AND upper-bound (silent-adjusted) per row and in aggregates. Conservatively haircut the multiplier — 5× Bucket A, 3× Bucket B, 1× Bucket C (observable). Anchor: the haircut is "what fraction of silent bouncers would respond to the fix at the same rate as visible support contacts." Not all of them — many silently bounce for reasons orthogonal to the fix.

Always report as range: `realistic / upper`. Never report points (METHODOLOGY.md §4).

### Decision 6: When does the operator review happen?

Tried: automate end-to-end (LLM extraction → cluster → score → memo). Problem: LLM-extracted loss_rate and fix_fraction values are hallucinations without grounding. A board memo built on hallucinated calibration is fiat dressed up as analysis.

The fix: **explicit human-in-the-loop checkpoint at Stage 4.** Pipeline writes a markdown review file + a pre-filled JSON template, then HALTS. Operator reviews each mechanism, adjusts loss/fix with rationale, sets effort tier and owner. Pipeline refuses to run Stage 5 without the signoff file.

The operator is a calibrator, not the source of mechanism truth (the LLM provides the mechanisms). This split avoids the "hand-curated list pretending to be a model" antipattern (ANTIPATTERNS §4).

### Decision 7: How many reviewer rounds in the audit gate?

Tried: spawn 2 reviewers, get 7.5/8. Spawn 2 more, get 8.5/8.2. Consider a third round to push to 9.

What broke that: Henrik became visibly frustrated. Each round was adding cosmetic feedback, not insight. The user read it as process theatre.

The fix: **stop at convergence.** Both ≥ 8/10 + only polish-tier critique = SHIP. If reviewers plateau at 7 across two rounds with same critique, escalate to operator — don't keep iterating (METHODOLOGY.md §7).

### Decision 8: How honest should we be about pipeline limitations?

The pipeline's auto-baseline-v3 mode (a test harness that auto-populates operator signoff from prior baseline data) PRODUCES MEMOS THAT FAIL THE AUDIT in real ways:
- The `cross-cutting` bucket mechanism "agent offering $10 credit for App Store reviews" survives clustering, gets routed into churn for display, and arrives in the recommendation. The audit reviewers correctly flag this as a category error.
- Auto-inherited rationale from cross-bucket fuzzy matches polluted churn rows with upsell language.

The fix: do not silently work around. Surface these as expected divergences from real operator review. The audit gate finding real issues IS the pipeline working correctly. A real operator would drop those mechanisms in Stage 4.

## The 3-bullet recommendation that ended v3.1

> **1. Sprint-1 ship: 5 Copy-tier conversion fixes** (~0 eng cost)
>    - Correct WhatsApp Business compatibility article
>    - Add pre-purchase VoIP-SMS-OTP disclosure
>    - Suppress free-trial balance emails during trial window
>    - Add canonical Skype-migration landing page + FAQ
>    - Add outbound-SMS-not-supported disclosure pre-purchase
>    Combined: +0.78pp conversion, $14K/yr lower bound, ~$69K/yr upper bound. Marketing+CS owned.

> **2. Sprint-1 ship: 2 engineering-day IDV upload fixes**
>    - Fix 'request is invalid' upload error on valid JPEGs
>    - Raise 1MB upload limit + surface clear error message
>    Combined: ~$3K/yr lower bound, pure engineering. Also reduces support load.

> **3. Sprint-2 ship: Pricing-page upsell A/B test** (the biggest single opportunity)
>    - Redesign /pricing to surface Premium feature-list inline at upgrade CTA. A/B test.
>    - 1-2 eng-weeks (build) + 4-6 weeks (A/B-test run) = ship + measure within Q3.
>    - **Realistic ARR**: $86K/yr at 3% upgrade lift; $144K/yr at 5%.
>    - Highest-ROI commitment in this memo. Product+Marketing+Eng owned.

Notice what's MISSING:
- No "commission another memo" — the upsell bullet is a shipping commitment, not analysis deferral.
- No "investigate further" — every bullet ends with a specific commitment.
- No time-to-impact column in the source tables — sequencing belongs in the recommendation section ("Sprint-1", "Sprint-2") not in per-row.
- No single combined rate claim — the buckets remain separately reported.
- No point estimates — every ARR is a range.

That's what the methodology produces when it stays on the rails.
