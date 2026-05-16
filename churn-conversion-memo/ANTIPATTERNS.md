# ANTIPATTERNS.md — what NOT to do

Each entry below is a real failure from the Sonetel churn-analysis project (2026-05-13 → 2026-05-15). They are the specific mistakes this skill exists to prevent. Read this if a reviewer score comes back < 8 — you are probably committing one of these.

---

## 1. The LTV-weighted tag-rankings disaster (v1 — six iterations to abandon)

**What we did**: extracted issue tags per support interaction (verification_friction, billing_friction, etc.), computed cohort over-representation ratios, multiplied by per-segment LTV from Finops, ranked. Produced a table where the top driver was "pricing-in-funnel: $26K ARR-at-stake."

**Why it failed**: a $26K-scale headline on a ~$4.4M ARR business is illegible to the board. Tag names are abstract — "verification friction" describes 5 different fixable mechanisms in 5 different parts of the codebase. The board cannot fund "verification friction" — they can fund "fix the 'request is invalid' upload error" or "raise the 1MB upload limit". Tags don't translate to actions.

**How Henrik flagged it**: *"I am not seeing how this can be useful and actionable. Help me understand."* — direct, terminal-velocity feedback after six rounds of methodology refinement that made the table more polished but no more actionable.

**The fix**: stop ranking tags. Name fixable mechanisms with a granularity-anchor (file/screen/error/policy/feature). See METHODOLOGY.md §1 and §3.

---

## 2. The ×12 ARR trap

**What we did**: `recovered_customers_per_month × MRR × 12 = annual_ARR`. Used 12 because "annual."

**Why it failed**: on Basic tier (92% of paying base at $5.25/mo, monthly churn ~8.8%), a saved customer's expected residual life is ~10 months, not 12. The ×12 multiplier overstated headline ARR by ~2×. CFO-lens reviewer caught it in v2.

**The fix**: `expected_post_save_tenure = min(12, 1 / plan_mix_weighted_monthly_churn_rate)`. Realistic 8mo / best-case 12mo dual report. See METHODOLOGY.md §5.

---

## 3. Punting upsell to a "follow-on memo"

**What we did**: identified that Basic → Premium upgrade had the single biggest revenue lever (~$86K/yr at 3% upgrade, ~$144K at 5%). Relegated it to §5 "sidebar" in the memo. Recommended commissioning *another* memo to analyze it properly.

**Why it failed**: it was the single biggest line item in the deck. Telling the board "the biggest opportunity is X, here's what you might do about it... but please wait while we write another memo" is a confession of analysis incompleteness AND missing the point of the deliverable. Board-deliverability reviewer scored 3/10 on that section alone.

**The fix**: Bucket C upsell goes in the decision table, not the sidebar. Treat it co-equal with conversion and churn. The "follow-on memo" framing is forbidden in recommendations (METHODOLOGY.md §8 honesty constraint #6).

---

## 4. Hand-curated mechanism lists pretending to be a model

**What we did**: built `scripts/build_decision_tables.py` with `MECHANISMS = [{label: "WhatsApp Business...", loss_rate: 0.85, fix_fraction: 0.90, ...}, ...]` — 14 mechanisms typed as a Python list literal. Wrapped a financial-scoring function around it. Called it "the pipeline."

**Why it failed**: re-running this on a different sample, time window, or customer-base subset requires manually re-curating. The "model" is fiat. Audit reviewer scored it 3/10 on Mechanism-Identification-Process. Henrik asked directly: *"Did the CR change the model for generating the memo, and not just the memo itself?"*

**The fix**: real LLM extraction over freetext fields with constrained output schema (`record_mechanisms` tool with granularity_anchor, specificity_score, evidence_quote). Clustering for dedup. Operator review (Stage 4) is calibration, not authoring. See CR-bulletproof-pipeline.md.

---

## 5. Manufactured "awaiting X" gates in conversation

**What we did**: at the end of a turn with concrete forward work available, claimed to be "awaiting Venkata's CSVs and PLAN.md decisions before the next concrete step."

**Why it failed**: the forward work was sitting right there — filter the SF emails to 12 months, thread them by Case ParentId, profile what remains. None of it needed Venkata or PLAN.md. Henrik called it out: *"nothing moving from your side. Does that mean you are stuck?"*

**The fix**: end a turn with "blocked" only when truly exhausted. Pre-process, filter, profile, write the script you'll need, build smoke fixtures. See the user-level feedback memory `feedback-continue-means-act` for the full pattern.

---

## 6. Reviewer-theatre — rounds-on-rounds beyond convergence

**What we did**: spawned 2 reviewers, got 7.5 / 8. Spawned 2 more reviewers, got 8.5 / 8.2. Considered spawning a third round to push to 9. Henrik became visibly frustrated with the process.

**Why it failed**: at the convergence point (both ≥ 8, no new structural critique, only polish-tier edits), additional reviewer rounds add calendar time without adding insight. The marginal score gain comes from cosmetic feedback. The user reads it as process theatre, not progress.

**The fix**: stop at convergence. Both ≥ 8 + only polish-tier critique = SHIP. See METHODOLOGY.md §7.

---

## 7. Time-to-impact column inviting false precision

**What we did**: added a `time_to_impact` column to the decision tables: "next month / 30-60d / 60-90d / Quarter+".

**Why it failed**: the CR explicitly forbade it ("cost only, not timing" — Henrik's call). The column gives a board member something to challenge ("how did you derive 60-90d?") with no defensible answer. Implementation reviewer caught the CR violation. Time sequencing belongs in the recommendation section ("ship in Sprint 1"), not in the per-row decision table.

**The fix**: effort tier (Copy / Config / eng-weeks / Quarter+) yes; time-to-impact column no.

---

## 8. Asking "do you have what you need?" instead of trying it

**What we did**: at multiple points, asked Henrik clarifying questions about whether to proceed (Sonnet vs Haiku, 250 or 500 per cohort, etc.) when reasonable defaults existed.

**Why it failed**: each round-trip cost Henrik 5+ minutes of attention. Many of the "questions" were Claude offloading judgment onto the user. The user's stated preference: *"act, don't ask another question."*

**The fix**: pick reasonable defaults (Sonnet for quality on board-level work; 250-per-cohort for MVP), proceed, surface only the trade-offs that genuinely need user input. See `feedback-continue-means-act` memory.

---

## 9. Forgetting to verify before destroying

**What we did**: Henrik said "I'll cp the file to the new folder, you delete the source." Claude treated "ok" as confirmation the copy had landed and ran `rm` on the source. The destination was empty. Had to reconstruct from chat context.

**Why it failed**: implicit trust that the user's half of a split operation succeeded. "ok" usually means "go ahead" not "I have completed the action and verified the result."

**The fix**: any time the user says they'll do step N and asks for step N+1 where N+1 destroys state needed if N failed, **verify N happened first**. One `ls` is cheap. See `feedback-verify-before-destroy` memory.

---

## 10. Building methodology on top of methodology

**What we did**: spent 4-5 turns adding refinements to the CR (cell-size gates, multiple-testing correction, ICC computation, time-trend analysis, sensitivity multipliers) before producing any actual memo. By the time the v1 memo landed, the methodology spec was longer than the memo would ever be.

**Why it failed**: methodology that doesn't ship doesn't earn its keep. The honest test of a methodology is whether running it on real data produces a defensible deliverable. Defer methodology refinements until after a real run reveals what actually needs fixing.

**The fix**: minimum viable methodology → run it → audit the output → fix the specific failure modes you observed. Don't build for failure modes you haven't seen.

---

## 11. Pushing calibration onto the operator instead of doing it from data

**What we did**: built Stage 4 as a "fill the loss_rate / fix_fraction / effort_tier / owner for each of 43 mechanisms" task for the operator. ~25-45 min of focused review work to set 6 fields per row.

**Why it failed**: the operator has no observational basis for the per-row loss_rate or fix_fraction — those numbers come from looking at customer-dialogue + outcome data, which is what Claude already did during extraction. Asking the operator to "calibrate" them is asking them to speculate.

Effort_tier and owner are operationally relevant but **not memo-relevant**. They overreach the deliverable's scope ("what drives churn, what's addressable") into implementation territory ("how does each fix get shipped, who owns it"). The memo loses focus and invites pushback on details that aren't its job to answer.

**How Henrik flagged it** (2026-05-15): *"loss rate and fix fraction is nothing I can speculate about. Better if you do a best estimate and ensure that the assumptions and rationale behind the number are in the memo. effort_tier is irrelevant. We use Claude Code for changes. It is agile and fast. The memo should not bother about that, it overreaches its target results by even thinking about challenges with implementation. Same with owner. That's out of scope."*

**The fix**:
- Compute `loss_rate` from the actual resolution-outcome distribution of the underlying interactions. State the count in the rationale.
- Derive `fix_fraction` from a published heuristic per `fix_type`, with a single-sentence rationale per mechanism if overridden.
- Drop `effort_tier` and `owner` from the schema, decision tables, recommendation bullets, and audit constraints entirely.
- Operator review becomes a thin **drop-pass**: delete mis-classified rows. ~5 min, not 45.
- Use `ASSUMPTION (pending <person>)` inline markers when business context is needed that data can't provide. Don't block — pick a default and ship.

## 12. Conflating realistic with upper-bound in the headline section

**What we did**: §1 headline table showed only "realistic" ARR figures, then a prose paragraph below mentioned "Upper-bound (silent-bounce sensitivity adjusted): $XK/yr." Nowhere in §1 did the doc say plainly *"realistic = customers who actually contacted us; upper = realistic extrapolated to silent customers."* The §9 caveats explained silent multipliers but never explicitly defined what the realistic figure was grounded in.

**Why it failed**: a board member skimming §1 sees two big numbers ($37K vs $146K) without knowing which one is the conservative floor and which is the sensitivity. Henrik flagged it: *"is this some pie in the sky? Or is it actually grounded in something. Otherwise it may not make sense to include it"* — he was reading "Combined upper" without seeing the silent-extrapolation framing it needed.

**The fix**: under the §1 headline table, add one explicit note: *"Every figure above is grounded in customers who actually contacted Sonetel support. No silent-customer extrapolation. The upper-bound figure below extends this to silent customers under a uniform-incidence assumption — see §9 caveat 4. Realistic = conservative budget anchor; upper = sensitivity."* Also expand §9 caveat 4 to lead with the same distinction.

**The deeper lesson**: ARR figures live in two layers — visible-contactor signal vs silent-extrapolation. The board reader cannot tell which is which from the numbers alone. **Make the layer explicit anywhere the number appears** (headline, body, caveats).

---

## 13. Operator-override rationale stored but not rendered in the deliverable

**What we did**: the operator flipped 11 mechanisms from `fixable_by_sonetel: No` → `Yes` over a session, with one-sentence rationales for each ("engineering, releasing this month"; "policy, operator authorises change"; etc.). Each rationale was persisted in `operator_signoff.json`. The memo only showed the resulting `✓ Yes` marker — not the rationale.

**Why it failed**: the audit trail existed in the signoff JSON but the board reader couldn't see *why* a row had moved from No to Yes between drafts. A reviewer asking "did this used to be marked unfixable? what changed?" couldn't answer from the memo alone. Henrik flagged it: *"All flips done in the doc. rationale added?"*

**The fix**: in `mech_row()` (or equivalent renderer), append `fixable_by_sonetel_rationale` inline next to the ✓/✗ marker, in italics. Same pattern as `loss_rate_rationale` and `fix_fraction_rationale` — every operator-meaningful field should carry its rationale into the final memo, not just sit in a JSON file.

**The deeper lesson**: the deliverable is what the board reads. Persisting rationale in a signoff JSON is necessary for audit but insufficient for the deliverable. **Anywhere an operator made a non-default judgment call, the rationale must surface in the memo** — otherwise the audit trail isn't board-visible.

---

## 14. Defaulting fix_fraction to the heuristic tier when underlying customers were leaving anyway

**What we did**: applied the default `fix_fraction` heuristic per `fix_type` (engineering=0.7, policy=0.4, etc.) to *every* mechanism uniformly — including mechanisms where the underlying interactions showed the customers had pre-existing exit intent (cancel_request=True, churn_intent=1.0). Examples that overstated ARR:
- m024 "No in-call cancellation": fix=0.7 → ARR $4,510. But all 6 underlying interactions had cancel_request=True. Making cancellation easier doesn't retain people who came to cancel.
- m038 "No self-serve cancellation": fix=0.7 → ARR $3,151. Vamshi (CS head) had said in the original No rationale that these customers are gone regardless.
- m035 "Refund to balance not original CC": fix=0.4 → ARR $4,508. 3 of 5 had cancel_request=True; the evidence quote shows customers wanting refund AS PART of leaving.
- m021 "Calls-paused email no top-up CTA": fix=0.7 → ARR $4,901. 5 of 6 replied to the email with a one-line deactivation request.

**Why it failed**: the default `fix_fraction` heuristic assumes the customer wants the underlying service to work. For a customer who explicitly wants to cancel, fixing the mechanism just speeds up their exit (or operationally smooths it) — it does not retain them. Henrik flagged it on m024: *"Is it really likely that customers that want to cancel their account will stay on if we simply make it easier for them to cancel?"* The honest answer was no.

**The fix — distinguish pre-existing exit intent from friction-caused exit intent**:

| Pattern | Signal | fix_fraction treatment |
|---|---|---|
| **Pre-existing exit intent** (customer came to cancel; mechanism is friction during the cancellation flow) | High `cancel_request=True` rate AND mechanism is about cancellation/refund/account-closure flow | **Haircut to 0.10-0.25** depending on win-back potential. The fix has operational value (less ticket time, fewer chargebacks) but ~no retention. |
| **Friction-caused exit intent** (customer was trying to USE the service; friction frustrated them into a cancel-request) | High cancel_request rate BUT mechanism is about signup/activation/feature-gap | **Keep heuristic tier**. Fix removes the friction at the source; cancel-request goes away. |

**Concrete diagnostic**: read the evidence quotes. If they describe customers asking for the service to *work* (m011 mobile inbound, m026 signup name-mismatch), the mechanism is friction-caused — keep heuristic. If they describe customers asking to *leave* (m024 "wants to cancel", m035 "requested refund"), the mechanism is exit-intent — haircut.

**Don't** confuse "high cancel_request rate" with "high recovery potential." Sometimes the cancel_request IS the signal that recovery is gone.

---

## Pattern across all 14: failure when methodology serves itself instead of the answer

The unifying lesson: **the methodology serves the deliverable, not the other way around**. Every antipattern above came from a moment when methodology elegance, defensibility, or completeness was prioritised over producing a board-actionable artifact. When in doubt, ask: "would this make the memo more useful to the user, or just more methodologically pure?" If the answer is the latter, don't do it.
