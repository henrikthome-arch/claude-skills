# Cash Flow Analysis Log

Running log of findings, budget corrections, and patterns discovered during cash flow crosschecks.

---

## 2026-05-06: Mid-month validation against EOM Apr snapshot — Hejdad detection, payment priority tiering, VAT day-12 model

**Position (May 6 mid-day, from CSVs):**
- Nordea SEK 91-55-78-9 saldo: -991,996.73 → 8,003 SEK headroom (improved from -999,572 EOM Apr)
- EUR 214-72-32-9: 2,983.40 → ~32,358 SEK
- USD 214-72-33-7: 7,654.19 → ~71,034 SEK (Bambora settlements rebuilding USD pool)
- 91-55-78-9 EUR/USD subs: ~535 SEK (May 4 download — small, unchanged)
- **Nordea tillgängligt mid-day May 6: ~111,930 SEK**
- PayPal estimated ~2-4K USD (below 5K floor — drained by May 5 sweep of ~7.4K USD = 77,397 SEK; computed not asked)
- **True tillgängligt: ~112K SEK** (PayPal contributes 0 effective)

**MTD May 1-6 crosscheck:**

| Date | Item | Forecast | Actual | Status |
|---|---|---|---|---|
| May 1 | Voxbone 79K direct | -79K | nothing (Labour Day + utlägg channel) | timing — flows via Henrik AMEX |
| May 4 | Loopia 334 | not modeled | -333.75 ✓ | matches kommande |
| May 4 | Mazars 35,500 | -35,500 | nothing (booked May 6) | hit 2 days late |
| May 5 | Linn 22K, Nordea 5K, VAT refund -100K | net +73K | -2K SEB transfer + (3) -95,347 | VAT refund delayed |
| May 5 | (3) -95,347 mystery | not modeled | **BDO 83,066 + Cision 5,250 + CFO 7,031** ✓ | exact decode |
| May 6 | revenue +70K | revenue | +35.76 Adyen, -23,375 Linn, -6,290 Nordea fees, -44,375 Mazars | day's outflow cluster |

**FAVORABLE variances discovered via Fortnox open-invoices ledger:**

| Item | Budget excl. VAT | Actual May invoice (excl. VAT) | Delta |
|---|---|---|---|
| SEB Kort May 11 | 152,000 | 96,896 (121,120 / 1.25) | **-55,104 favorable** |
| Google Adwords May 14 | 120,000 (no VAT) | 83,652 (March service month) | **-36,348 favorable** |
| **Combined favorable** | | | **-91,452 SEK** |

**UNFAVORABLE variances:**
- Fluff/Rainbow: budget 25K vs. actuals: April invoice 38,806 (Hejdad) + May invoice 33,313 = 72,119 SEK incl. VAT in May. Baseline structurally above 25K. Recommend recurring update to ~30K excl. VAT.
- BDO 23-day pull-forward: 83,066 hit May 5 (recurring day_28). Plus residual 7,644 due May 30. Total May BDO ~91K. Forecast had 53K placeholder May 28 — should drop to 7,644 actual residual since main invoice already paid.

**Hejdad finding — CRITICAL learning:**
- Rainbow 38,806 (April invoice, förfall May 1) was auto-Hejdad by Nordea because EOM Apr saldo of -999,572 had only 428 SEK headroom — payment couldn't clear without breaching credit line.
- Today's saldo -991,997 = 8K headroom, still cannot release 38,806 (would breach by ~31K).
- **This is a fundamental insight: Hejdad = silent payment loss to bank algorithm, not a discretionary delay.** Should have been flagged Apr 29 when EOM saldo was at -999,890 with day-1 payments scheduled.

**VAT refund "day 12 netting" model — user's refined hypothesis:**
- VAT refund not yet received as of May 6. Empirical history shows utbetalning clusters around day 12 of post-quarter month (same day as monthly Skatt debit).
- Q4 2025 case: credit Feb 6, monthly debit Feb 12, utbetalning Feb 16 (net -46K).
- For Q1 2026: credit Apr 30, monthly debit May 12, expected utbetalning ~May 12-16.
- Net cash impact in May ≈ refund (~100-130K) − monthly Skatt (70.7K) = +30-60K small inflow around day 12.
- **Updated model in skill: id 48 should be day_12 of months 2/5/8/11, not day 5 (or day 30 of quarter-end month).**

**Google Adwords cycle correction:**
- Google bills 1 month in arrears: service month X invoiced late month X, due ~day 14 of month X+1.
- May 2026 evidence: March service invoice 83,652 due May 14; April service invoice 110,265 due June 11.
- Recurring should be day_14 with 1-month lag built in (currently day_17 same month — wrong on the month, approximately right on the day).

**Skill updates committed (this session):**
1. Step 1 item 3: Hejdad must be checked every run — documented as CRITICAL signal
2. Step 1 item 4: PayPal balance is derivable, don't ask by default
3. Step 1 item 6 (NEW): Fortnox open-invoices ledger as preferred forward-outflow source
4. Step 2 / Cost Outflows table: Google 1-month lag noted
5. Skatteverket VAT refund section: "day 12 netting" refined model
6. Section 5b: removed bad mitigation suggestion ("escalate to credit-line increase"), replaced with priority-tier referral
7. Section 5b.1 (NEW): Payment criticality tiering — Tier 1 (staff/contractors/tax/loans) protected, Tier 2 (SEB Kort, BDO, advisors) deferrable, Tier 3 (small commercials) discretionary
8. Key Rules 16, 17, 18 (NEW): Hejdad detection mandatory; no unsolicited operational advice; payment priority hierarchy non-negotiable

**Action items (for user / portal):**
- [ ] Release Rainbow 38,806 when SEK saldo recovers (~Wed-Thu after Adyen/PayPal weekend settlements clear). Don't make Fluff wait.
- [x] Update recurring id 48 (VAT refund): day 30 → day 12, quarter_months 1/4/7/10 → 2/5/8/11 — **applied 2026-05-06 via dbshell** (quarter_months were already 2,5,8,11 from Apr 29; only day_of_month changed from 5 to 12)
- [x] Update recurring id 29 Fluff/Rainbow budget: 25K → 30K excl. VAT/month — **applied 2026-05-06 via dbshell**
- [x] Update recurring id 11 Google Adwords: day_of_month 17 → 14 (1-month-arrears cycle) — **applied 2026-05-06 via dbshell**
- [x] BDO May placeholder offset + residual — **applied 2026-05-06**: scheduled_payment 51 (+53K is_inflow May 28 to neutralize recurring placeholder), scheduled_payment 48 (-7,644 May 30 residual)
- [x] Rainbow Hejdad release modeled — **applied 2026-05-06**: scheduled_payment 47 (-38,806 May 8)
- [x] SEB Kort May actual override — **applied 2026-05-06**: scheduled_payment 49 (+68,880 is_inflow May 10 to capture actual 121,120 vs 190K recurring)
- [x] Google May actual override — **applied 2026-05-06**: scheduled_payment 50 (+36,348 is_inflow May 14 to capture actual 83,652 vs 120K recurring)
- [ ] (Already noted Apr 29) Add Schibsted Marketing Services AB as annual recurring April day_27 ~7,600 excl. VAT — wait, looking at recurring list this is **id 50 enabled** with amount 7600 day_27 month 4. ✓ Actually applied earlier — verified 2026-05-06.

**Forecast after all edits applied (verified 2026-05-06):**
- Min balance: -777,027 SEK on May 1 (forecast, not actual; actual May 1 was -999,572 since Voxbone flows via utlägg not direct)
- EOM May 31 running balance: **-402,046 SEK** (improved from pre-edit -507,264 — i.e. +105K improvement from corrected modeling, primarily SEB Kort lower than budget +69K, Google May lower +36K, BDO May offset +45K, Fluff Hejdad -39K, Fluff recurring up -5K)
- The forecast still uses EOM Apr starting cash (-755,967) so the May 1-6 actual divergence vs. modeled isn't auto-corrected. For the most accurate forward picture, multiply current view minus actual divergence; or update the cash position snapshot mid-month if the system supports it.

**Forecast verdict for rest of May:**
EOM May projection: starts -756K (Apr 30) → +88K so far (May 1-6) → +50-150K rest-of-May (revenue inflows + favorable SEB/Google variances mostly absorb Fluff overshoot and BDO residual) → **EOM May ~-570K to -670K SEK total cash position**, ~150-200K improvement over EOM Apr. May 11 SEB Kort autogiro will briefly stress the SEK saldo but is Tier 2 and tolerable. **Tight but no liquidity crisis if Fluff Apr invoice releases by May 8.**

---

### Post-mortem: Apr 29 verdict vs. May 6 reality

**Apr 29 verdict was:** *"after the Apr 17 + Apr 18 corrections, remaining structural underbudgeting is ~40K/month"* — and flagged the EOM cluster fragility, the 5K PayPal floor, T+3 PayPal lag, and the credit line being fixed at 1 MSEK.

**What actually happened May 1-6:**
- Total cash position improved from -756K to roughly -668K (Nordea-only +88K, PayPal flat). On track within the ±50K error band for total monthly drift, but with significant offsetting variances inside that net.
- Apr 29 implicitly assumed VAT refund would arrive close to Apr 30 / early May — it did NOT, and the "day 12 netting" pattern was not modeled.
- Apr 29 did NOT flag Hejdad risk on the day-1 May payments despite EOM saldo being 109 SEK short of the limit.

**Drift drivers (May 1-6 only):**

| Driver | SEK impact | Anticipated by Apr 29? |
|---|---:|---|
| SEB Kort May invoice under budget | +55K favorable | No — surfaced via Fortnox ledger |
| Google March service invoice under budget | +36K favorable | No — surfaced via Fortnox ledger |
| Fluff April invoice Hejdad'd by credit-line saturation | -39K (deferred, not timing-neutral) | **No — should have been flagged** |
| Fluff April + May combined vs. budget 25K | -47K | Partial — log noted Fluff structurally over budget |
| BDO 23-day pull-forward (-83K early; +45K residual) | -38K net | No |
| VAT refund delay from May 5 to ~May 12-16 | -100K timing (offsetting +30-60K net later) | Partial |

**Root cause — three Apr 29 misses:**
1. **Hejdad blind spot.** Apr 29 noted SEK saldo at -999,890 but did not run a "what payments are scheduled day 1 against this headroom?" check. That single check would have caught Rainbow Hejdad before it bit. **Closed in Step 1 item 3.**
2. **Fortnox open-invoices ledger not consulted.** The recurring schedule was treated as the forward source. Reality is more accurate from Fortnox supplier ledger when accessible — exposes actual invoice amounts and exact förfallodatum. **Closed in Step 1 item 6.**
3. **VAT refund timing assumed naively.** Apr 29 set day_5 of post-quarter month; reality clusters around day_12 (netting against monthly Skatt debit). **Closed in Skatteverket section.**

**Mid-cycle process gaps closed:**
- [x] Hejdad detection now mandatory (Step 1 + Key Rule 16)
- [x] Fortnox open-invoices ledger added as preferred forward source (Step 1 item 6)
- [x] VAT refund "day 12 netting" model documented
- [x] Payment criticality tiering codified (Section 5b.1 + Key Rule 18) — staff/contractors are Tier 1, never delayed; SEB Kort is Tier 2, can be late
- [x] No-unsolicited-operational-advice rule added (Key Rule 17)
- [x] PayPal balance derivable from data, don't ask by default (Step 1 item 4)

**Process gaps still open for next run:**
- [ ] Verify Q1 2026 VAT refund actually lands by May 16; if not, escalate timing assumption
- [ ] Confirm Rainbow 38,806 released (and timing — Fluff should not wait beyond what's necessary)
- [ ] Confirm SEB Kort May 11 autogiro clearance — note the saldo trajectory
- [ ] Verify BDO 7,644 residual due May 30 actually hits (not consolidated into next month)

**Forward implications:**
- The Apr 29-flagged structural fragility (1M credit line saturation at EOM) is real and persisting. May benefits from favorable cost variances and lower India ask, but EOM May will still be tight. Structural fixes remain in Key Rule 12 set: re-time DBT mid-month, accelerate receivables, reduce structural costs, alternative funding, monthly VAT periods. The credit line itself is not extendable.
- The Hejdad-on-day-1 pattern will recur every month-end the SEK saldo is within 50K of the limit. As a leading indicator, watch the EOM saldo trajectory in the last 3-5 days of every month.

---

## 2026-04-29: EOM crosscheck + India 11 KUSD gap + Forvis ÅR cost split + skill updates

**Position (Apr 29):**
- SEK 91-55-78-9 saldo: -999,890.19 → only 109.81 SEK headroom on 1M credit line
- EUR 214-72-32-9: 18,723.75 (intentionally pre-funded for MOSS Apr 30 = 18,713.84 EUR)
- USD 214-72-33-7: 2,111.29 + USD 91-55-78-9: 170.08 = 2,281 total
- Other small balances: ~290 SEK + 1,615 SEK
- **Tillgängligt total ≈ 228,000 SEK** (Nordea) + **PayPal 6,673.80 USD ≈ 63,400 SEK** = **~291K SEK**
- After MOSS Apr 30 (drains EUR account): **~22K SEK Nordea + 63K PayPal = ~85K SEK free**

**MTD crosscheck against forecast — items confirmed via user drill-downs:**

| Bank entry | Decoded | Status vs budget |
|---|---|---|
| Apr 1 -34,750 (2) Corporate Access | Linn 23,375 + Fluff 11,375 | Linn ~budget; Fluff partial (vs 31K incl) |
| Apr 1 -13,801 Skuldränta | Credit-line interest | +38% over 10K budget — known structural |
| Apr 7 -6,699 AVGIFTER NORDEA | Bank fees | +34% over 5K — known |
| Apr 8 -112,139 (1) Corporate Access | BDO March invoice | ÅR spike (89,711 excl VAT), one-off |
| Apr 9 -136,050 DBT Capital | DBT delayed-from-March (98K + 37K combined) | matches forecast |
| Apr 9 -96,668 (1) Corporate Access | **Skatteverket 70,741 + Corona 26K bundled** | regular monthly + Corona-anstånd |
| Apr 14 -107,044 GOOGLE | Google Adwords | -11% under 120K |
| Apr 14 -315,527 (2) Corporate Access | **SEB Kort 190,527 + Forvis Mazars a conto 125,000** | SEB on budget; Forvis = 100K excl VAT a conto |
| Apr 14 -43,503 (2) Corporate Access | G&W 43,125 + Svensk e-identitet 378 | G&W on budget |
| Apr 24 LÖN x2 + Apr 28 LÖN | Salaries (Sebastian, Henrik, ...) | partial split, ~98K total |
| Apr 27 -14,021 (2) Corporate Access | Euroclear 4,527 + **Schibsted Marketing 9,494** | Euroclear ~budget; Schibsted not in budget |
| Apr 28 -115,625 (1) Corporate Access | Tomas André (DOLUTIONS AB) | exact match: 92,500 × 1.25 ✓ |
| Apr 28 -121,233 SONETEL UTL | Tomas André utlägg | 2890 reimbursement (not in recurring) |
| Apr 28 -5,766 SONETEL UTL | Martin utlägg | 2890 reimbursement (not in recurring) |

**FX-wash entries (NOT real outflows):** Same Meddelande/OCR ID appears in multiple account CSVs as paired ±entries.
- `0260424003669`: -10,288 SEK paired with foreign-account inflow same day
- `0260429008007`: -19,000 SEK ↔ +2,034 USD (SEK→USD)
- `0260429007840`: +18,400 SEK ↔ -2,000 USD (USD→SEK)
- `0260429007794`: -3,557 USD ↔ +3,020 EUR (USD→EUR — used today to top up MOSS-funding EUR account from 15,704 → 18,724)

**Pending Apr 30 (EOM):**
- MOSS 18,713.84 EUR — funded ✓ (in 214-72-32-9)
- BDO Göteborg 83,066 SEK — **osignerade, needs signing**
- DBT EOM block ~149,937 SEK — coming (per user, DBT charges at EOM)
- Henrik utlägg 44,207 SEK — osignerade dated Apr 24 (back-dated)
- Input VAT refund -125K SEK — expected inflow per forecast (not yet received)

**Pending May 4-6 (signed kommande):**
- Mazars 44,375 (slutfaktura — see Forvis split below)
- Loopia 334
- Södra Lund (CFO) 7,031
- Rainbow (Fluff) 38,806
- Cision 5,250
- Linn 23,375
- Total: 119,171 SEK

**India 11 KUSD gap before EOM:**
- April India transfers confirmed: Apr 24 -10,000 + -65,643 = 75,643 USD (the 10K + 65K express Henrik referenced)
- Apr 13 -31K, Apr 14 -6K, Apr 28 -16.8K USD outflows — likely all India per user (need confirming on individual basis but treating as India based on context)
- Padma's Apr 16 ask: 90 KUSD (TDS 14 + Salaries 48 + RTDS 21.5 + Vendor 6.5)
- Padma's Apr 27 follow-up: confirmed receipt of 10K, asking for remaining
- Padma's Apr 29 follow-up: needs balance via express; **May 1 = India holiday**
- **Remaining gap ≈ 11 KUSD** (per user estimate)
- USD available now: 2,281 (Nordea) + 6,674 (PayPal) = 8,955 — but **PayPal has 5,000 USD locked floor for DIDWW auto-refill**, so usable PayPal = 1,674
- **Effective USD liquidity: 2,281 + 1,674 = 3,955 USD → 7,045 USD short of 11K**
- Bambora settles ~3-5K USD/day; **need 1.5–2 more days of settlements** to close gap fully
- May 1 = India holiday means India needs funds **received Apr 30**. Standard SWIFT = 1 day. So express must depart Sweden by ~Apr 30 morning.
- **Realistic plan:** send what's available as express Apr 30 (e.g. 4K), continue with remaining (~7K) on Friday Apr 30 afternoon or Monday May 4 once Bambora batches arrive. Notify Padma that full balance won't arrive Apr 30 and provide expected dates.

**PayPal 5K USD floor (DIDWW auto-refill):**
- DIDWW (telecom vendor) auto-refills its account from this PayPal account
- 5,000 USD must remain at all times — these funds are operationally locked
- When computing tillgängligt or USD funding capacity, ALWAYS subtract 5K from PayPal balance
- This narrows USD liquidity meaningfully (today: -5K USD effective = -47,500 SEK at FX 9.5)

**PayPal → Nordea withdrawal lag: 2–3 banking days:**
- A PayPal withdrawal initiated today does NOT arrive in Swedish bank until 2–3 banking days later
- This means PayPal liquidity is **T+3 cash, not same-day**
- For urgent same-day/next-day needs (India express transfer before EOM, etc.), PayPal CANNOT be the funding source
- **Implication for today's India 11K USD plan:** PayPal cannot help reach 11K by Apr 30. Only Nordea USD balance + overnight Bambora/Adyen settlements are usable. Realistic Apr 30 send capacity = 2,281 + ~3-5K Bambora overnight = ~5-7K USD max. Remaining 4-6K must wait for additional Bambora batches Apr 30 PM / May 4.

**Avoid PayPal → Nordea withdrawals straddling month-end:**
- User preference (Apr 29 2026): do not initiate a PayPal withdrawal that leaves PayPal in month N and arrives in Nordea in month N+1
- Reason: simplifies monthly accounting — avoids in-transit balances at EOM that BDO has to reconcile
- Practical rule: if today is within ~3 banking days of EOM and the withdrawal would land in the new month, **wait until the new month** before initiating
- **Implication for Apr 29 2026:** do NOT initiate the PayPal withdrawal today. Instead start it Monday May 4 (new month, full week ahead). Only Nordea USD + Bambora settlements are funding sources for Apr 30 India transfer.

**Forvis Mazars annual report cost — split correctly:**
- Total audit fee FY2025: **135,500 SEK excl. VAT**
- Already paid: a conto 100K excl. VAT (= 125K incl, hit Apr 14 in the -315K Corporate Access bundle) — matches recurring id 46
- Still due: slutfaktura 35,500 excl. VAT (= 44,375 incl., signed kommande May 4)
- Recurring id 49 (currently 36K, day 15, April) is the slutfaktura placeholder — should be **moved to May day 4 with amount 35,500**, OR kept in April as approximation. Reality: hits May.
- Reference invoice: Forvis Mazars 20213987, faktdat 2026-04-14, förfall 2026-05-04

**Schibsted Marketing — annual AGM ads:**
- Apr 27: 9,494 SEK incl. VAT (~7,595 excl.) — first observed payment
- Bundled with Euroclear in Corporate Access on day 27
- **Action: add as annual recurring SEK, day 27, annual_month 4, ~7,600 excl. VAT, supplier "Schibsted Marketing Services AB"**

**Critical risk flagged:**
- SEK saldo at -999,890 means **109.81 SEK** headroom only
- BDO 83K + DBT 150K = 233K SEK outflow at EOM; VAT refund +125K expected same day
- If outflows hit before refund, SEK could **briefly breach 1M credit line** Apr 29-30
- Mitigation: ensure BDO osignerade is signed promptly; coordinate timing with Skatteverket VAT refund inflow

**Skill updates committed (SKILL.md):**
1. Step 1: AskUserQuestion does NOT support image paste — always use plain chat for screenshot/list inputs
2. Step 1: Add Registrerade betalningar (Kommande + Osignerade tabs) as required input
3. Step 1: Tillgängligt is derived from CSVs (don't ask separately)
4. Step 1: All 5 account CSVs typically together in ~/Downloads
5. Step 2: Common Corporate Access bundles documented (incl. SEB+Forvis-a-conto, G&W+e-identitet, Linn+Fluff, Euroclear+Schibsted)
6. Step 2: FX-wash entries — same Meddelande/OCR ID across account CSVs = currency conversion, not outflow
7. Schibsted Marketing AGM ads added to Annual Report cost structure
8. Forvis Mazars cost properly split (a conto April + slutfaktura May)
9. India transfer mechanics expanded (recipient account, express vs slow, May 1 holiday rule)
10. DBT EOM timing clarified — recurring entries set to day 28 but actual hit Apr 28-30

**Action items (for user to apply in portal):**
- [ ] Sign BDO 83,066 SEK osignerade (Apr 30 due)
- [ ] Sign Henrik 44,207 SEK osignerade if cash allows
- [ ] Send remaining ~11 KUSD to India by Apr 30 (express; wait for ~1 more day of Bambora USD settlement to top up)
- [ ] Add recurring: Schibsted Marketing Services AB — annual SEK, day 27, month 4, 7,600 excl. VAT
- [ ] Update recurring id 49 (Mazar Forvis): 36,000 → 35,500 excl. VAT, day 15 April → day 4 May (slutfaktura timing)
- [ ] Verify recurring id 46 (Forvis Mazars 100K April) matches a conto pattern in future years
- [ ] **Update recurring id 33 (Skatt extra för ersättning styrelse)**: 60,000 → ~95,000 (verified via Skatteverket Jan 2026 payment of 190K vs. normal 70K base = ~120K spike from Dec board fees)
- [ ] **Restructure recurring id 48 (VAT refund)**: change from -125K day 30 of months 1/4/7/10 to -100K (or quarter-specific 150/50/150/80) on day 5 of months 2/5/8/11. Bank payout always lags Skatteverket Moms credit by 1-10 days, and Moms credit posts in the month AFTER quarter end.
- [x] **Corona anstånd remaining schedule verified Apr 29 2026** — almost fully run off. Future payments are SMALL: Aug 12 2026 = 8,107; Feb 12 2027 = 8,107; Apr 12 2027 = 25,859. Total remaining ~42K. The big quarterly batches (75K+ in Feb/Aug) ended with Feb 2026. Earlier projection of "~79K Aug 2026 batch" was WRONG — confirmed via user's Dec 2025 anstånd schedule. Existing scheduled_payment entries (ids 22, 26, 27, 28) are correct.

---

### Post-mortem: why EOM Apr 2026 looked worse than Apr 17/18 promised

**User's question (Apr 29):** "12 days ago you said we were fine. What went wrong?"

**The Apr 17 verdict in this log was actually:** *"April forecast unreliable by ~344K SEK… after corrections, remaining structural underbudgeting is ~40K/month."* So not "we're fine" — but the implicit message after the Apr 17 + Apr 18 corrections was that the forecast was now trustworthy within ~40K/month error. That message was **over-optimistic**.

#### Initial drift estimate (later corrected — see below)

The first version of this post-mortem put utlägg/2890 reimbursements as the largest driver at ~170K SEK. **That framing was wrong.** Per user correction (Apr 29) and verified against the database + the `Accountant_Bundle_2026-03_ver20260428_2103.zip`:

- The 2890 OLD debt of 307K (per Apr 17 log) is **separate** from current monthly expense reimbursements. The 307K is being paid via three SCHEDULED tranches starting June 30 — those have not happened yet. Not part of April drift.
- The Apr 28 utlägg payments (Tomas 121,233 + Martin 5,767 + Henrik 44,207 osignerade) are **for current-period expenses** (per March batches) — i.e. a normal monthly recurring activity, not an unscheduled drag.

**Monthly expense reimbursement history (database query, settled SEK):**

| Period | Henrik | Tomas | Martin | Sebastian | Total |
|---|---:|---:|---:|---:|---:|
| 2025-10 | 2,912 | – | – | – | 2,912 |
| 2025-11 | 7,591 | – | – | – | 7,591 |
| 2025-12 | 2,910 | 52,747 | 8,235 | – | 63,892 |
| 2026-01 | 47,239 | 26,075 | – | 1,270 | 74,584 |
| 2026-02 | 68,567 | – | – | – | 68,567 |
| 2026-03 | 146,041 | 98,822 *(backfill)* | 5,767 | – | 250,630 |

**6-month average ≈ 78K SEK/month.** April's 171K outflow decomposes as ~78K normal monthly + ~93K backfill catch-up (Tomas's March batch covers Dec 2025–Apr 2026 expenses bundled into one payment).

**Corrected drift drivers (refined further per user, Apr 29):**

Henrik's Mar batch (146,041 SEK) decomposed:
- Apr 1 Voxbone telecom 69,184 = this month's normal Voxbone (covered by recurring id 1, budget ~79K)
- Nov 11 Voxbone wallet top-up 38,925 = catch-up
- Nov 18 Voxbone wallet top-up 19,351 = catch-up
- Feb 3 Voxbone wallet top-up 18,327 = catch-up
- Jan 28 Domain 254 = small catch-up
- **Henrik Voxbone catch-up total ≈ 77K SEK** (3 wallet top-ups skipped in Nov/Feb monthly cycles)

| Driver | SEK | Was it anticipated? |
|---|---:|---|
| Tomas backfill catch-up — 5 months Anthropic/OpenRouter/travel in one Mar batch (dates Dec 2025–Apr 2026) | ~95K | No. New observation. |
| **Henrik Voxbone catch-up — Nov 2025 + Feb 2026 wallet top-ups not reimbursed in those cycles** | **~77K** | No. User correction: should be tracked monthly. |
| VAT refund (id 48 -125K) still not received as of Apr 29 | up to -125K (timing risk) | Partial. Apr 18 added the recurring inflow but didn't pre-validate Skatteverket processing timeline. |
| India 11 KUSD residual — within annual India budget but creates timing pressure (PayPal lag, Bambora lumpy settlement) | ~100K SEK USD-equivalent | No. Apr 17 log said "falls within India monthly recurring budget" — true on monthly basis, but didn't model FX-channel friction. |
| Salary remainder — only 57.5K of 98K budget paid (Sebastian 16.8K + 40.7K Apr 28). HT or KT 40K still outstanding | -40K | Timing only |
| Schibsted Marketing AGM ads (annual, ~9.5K) | -9K | No (first-time observation) |
| Bank fees + credit interest structural overrun | -5K | Yes |

**Total backfill drift ≈ 170K SEK (95K Tomas + 77K Henrik Voxbone catch-up).** Plus VAT refund and India timing risks on top.

**Note on attribution:** The 170K figure I originally cited as "drift" was directionally correct in magnitude but wrongly attributed (called "unscheduled 2890 reimbursement"). Correct attribution: it is **multi-month expense reimbursement backfill** (Tomas spanning 5 months, Henrik missing 2 Voxbone cycles), not unscheduled 2890 OLD-debt repayment. The 2890 OLD debt remains separate (scheduled June/July/Aug tranches).

**Why this matters going forward:** If expense batches are run monthly without backlog, drift drops to near zero. If they're allowed to accumulate (as happened here), one big catch-up payment lands in a single EOM cycle and squeezes liquidity. Suggested process control: monthly expense batches should always be processed within the same month, or the cash-flow forecast must explicitly anticipate backfill payments based on the gap between latest batch dates and current month.

**Nordea credit-line expansion ruled out (user, Apr 29):** Nordea cannot expand the 1 MSEK facility. Structural fixes for EOM-clustering risk must come from: (a) renegotiate vendor payment timing — particularly DBT EOM block (~150K) to mid-month, (b) shorten the cash-conversion cycle on receivables, (c) reduce structural costs (India envelope, BDO baseline, ad-hoc reimbursements), (d) alternative funding (other banks, factoring, shareholder loans), (e) move to monthly VAT periods (instead of quarterly) so refunds arrive 12 times/year at smaller amounts, smoothing the cycle. Do not propose "expand credit line" — Nordea is a closed door.

#### Structural budget gap exposed by this drift

The recurring budget is **missing a line for monthly expense reimbursements** (~78K SEK/month average). Some of the underlying spend is *implicitly* covered by recurring entries with the WRONG channel:

- id 1 Voxbone 79,205 — budgeted as direct vendor payment, actual flow is Henrik AMEX → 2890 → Henrik utlägg reimbursement
- id 27 Openrouter 50,000 — budgeted as direct payment, actual flow is Tomas personal card → utlägg reimbursement
- id 7 SEB credit card 190,000 — correctly covers what's on the COMPANY SEB card (Anthropic, META, Awin etc. on that channel). But Tomas's PERSONAL-card Anthropic/OpenRouter spend runs in PARALLEL and is NOT in any recurring entry.

The cash leaves the bank either way, but the budget structure obscures it. **Action: add a recurring "Monthly expense reimbursements" SEK line for ~78K, day 28, OR re-tag ids 1 and 27 to indicate utlägg-channel rather than direct payment, OR split per-person utlägg recurring lines.** Then forecast variance will measure real drift, not channel mis-tagging.

**Root cause: conflated *budget accuracy* with *liquidity timing*.**

The Apr 17/18 corrections fixed the **recurring budget structure** (right amounts, right months, VAT-correct, MOSS as recurring, VAT refund as recurring). What they did NOT do:

1. **Stress-test EOM clustering.** MOSS 206K + BDO 83K + DBT 150K + India transfer all hitting Apr 28–30 against a 1M credit line at 99.99% utilization is fragile by design — even a perfect forecast doesn't help if all timing collapses to one week.
2. **Model 2890 utlägg as monthly drag.** Voxbone alone adds ~79K/month to 2890; plus equipment, plus other vendor expenses. The forecast scheduled three tranches *later* but didn't account for ad-hoc reimbursement decisions in between.
3. **Pre-validate VAT refund timing.** Recurring id 48 (-125K day 30) was added confidently. Skatteverket's actual Q1 momsdeklaration processing was never confirmed — refunds typically arrive *during* the month after filing, not on day 30 reliably.
4. **Flag PayPal as not-emergency-cash.** The 6.6K USD looked like working capital but isn't (5K floor + T+3 lag + month-end avoidance). With those rules, "available cash" was always ~50K SEK lower than the dashboard suggested.

**Process gaps to close (apply in next cash-flow cycle):**

- [ ] **2890 utlägg drag tracker** — show running balance + MTD reimbursements as a dedicated line, separate from recurring outflows. Treat ad-hoc reimbursement decisions as a third payment category alongside recurring/scheduled.
- [ ] **VAT refund timing realism** — change recurring id 48 description to "expected during month, not day 30". Optionally split: smaller portion mid-month, balance day 30. Investigate Skatteverket Q1 refund actual landing date for calibration.
- [ ] **EOM-cluster stress test** — for every forecast, identify any 7-day window where outflows exceed (cash + run-rate revenue × days) and flag as red.
- [ ] **Funding-source tags on recurring entries** — "SEK only", "USD-funded", "EUR-funded" so MOSS doesn't look like SEK pressure when it isn't (and India/USD vendor stuff doesn't look like SEK relief).
- [ ] **Operational SEK saldo floor at -950K** (50K buffer below 1M credit limit). Any plan that drops below should require explicit decision/communication, not happen passively.
- [ ] **Tillgängligt computed with full deductions** — apply PayPal 5K floor, exclude EUR earmarked for MOSS, before reporting "available cash".

**What this means for May:**
Even if everything in the action list lands cleanly, May has the same EOM cluster (DBT EOM + BDO + India + Voxbone day 1 + SEB card day 10). The structural fragility doesn't go away with budget tweaks; it requires either (a) more revenue, (b) larger credit line, or (c) re-timed payment schedule (e.g. negotiate DBT to mid-month). Worth raising at the next CFO/board cadence.

---

## 2026-04-18: VAT handling decision + BDO cost audit + recurring payment cleanup

**Decision: All recurring payment budgets are EXCLUDING VAT.**
- Revenue in forecast is NET of VAT (~2.6 MSEK/month from "Revenue" column in sales report, VAT ~82K tracked separately)
- Costs are excl. VAT (the real cost to the company)
- Bank CSV amounts are incl. VAT → divide by 1.25 for Swedish suppliers when comparing
- MOSS/OSS: KEEP as quarterly scheduled payment (~200K). Bank balance includes accumulated VAT from customers even though revenue is net. MOSS drains this quarterly. Without it, forecast overstates cash by up to 246K.
- Input VAT refund: Initially removed (scheduled_payment ids 6,8 disabled), then RESTORED as recurring payment id 48 (-125K quarterly) — see below
- **Known timing artifact:** EOM cash snapshots include 0–246K of accrued MOSS debt. This inflates starting cash by up to 164K in months 2-3 of MOSS quarter. Forecast self-corrects when MOSS payment hits.

**Revenue confirmed NET of VAT:**
- Monthly revenue (~2.6 MSEK) comes from "Revenue" column in monthly sales report CSVs
- VAT (~82K/month) is a separate column in the same spreadsheet
- The forecast manual override of 2.6 MSEK/month matches the net revenue figure
- Therefore MOSS/OSS must remain as a scheduled outflow — the VAT cash is in the bank but never counted as revenue

**BDO invoice audit (15 invoices, Dec 2024 – Mar 2026):**

Annual cost structure (all excl. VAT):
- Monthly baseline: ~33K/month (bokföring, leverantörer, lön, licenser) = ~394K/year
- ÅR/Bokslut (Jan–Mar): ~121K (one-off, spread across 3 months)
- Kvartalsrapport Q3: ~38K (one-off in ~November)
- Halvårsrapport koncern: ~32K (one-off in ~February)
- Löpande konsult FS: ~36K (irregular)
- Other one-offs: ~15K
- **Total annual: ~636K excl. VAT = avg ~53K/month**

**Budget corrections APPLIED (2026-04-18):**

| recurring_payment ID | Recipient | Was | Now (excl. VAT) | Reason |
|---|---|---|---|---|
| 31 | G&W | 43,125 (incl.) | 34,500 | ÷ 1.25, quarterly advisor |
| 46 | Forvis Mazars | 125,000 (incl.) | 100,000 | ÷ 1.25, annual audit |
| 20 | BDO | 55,000 | 53,000 | Invoice audit confirmed avg ~53K excl. |

**Scheduled payment changes APPLIED:**

| scheduled_payment ID | Action | Description |
|---|---|---|
| 6 | Disabled | VAT refund 2026-01-30 (-100K) — costs are excl. VAT, no matching refund needed |
| 8 | Disabled | VAT refund 2026-04-30 (-100K) — same reason |
| 7 | Disabled | MOSS 2026-01-30 (200K) — replaced by recurring payment id 47 |
| 9 | Disabled | MOSS 2026-04-30 (200K) — replaced by recurring payment id 47 |

**MOSS converted to recurring payment (id 47):** 206K SEK (~18,714 EUR) quarterly on day 30, quarter_months 1,4,7,10.
- Actual Apr 2026 MOSS payment: 18,713.84 EUR. Paid in EUR, amount grows with EU revenue.
- Updated from initial 200K to 206K based on actual Apr 2026 figure.
- Old one-off scheduled_payment ids 7 and 9 disabled.
- No longer need to manually add MOSS entries each quarter.
- **Note:** MOSS is denominated in EUR. Budget in SEK will drift with EUR/SEK rate. Review annually.

**All other recurring payments confirmed already excl. VAT:**
- Round-number budgets (Linn 22K, CFO 5K, Cision 5K, Fluff 25K, United Spaces 6K, Euroclear 3.5K) verified against Fortnox MOMS column — all excl. VAT
- Tomas André 92.5K — description explicitly says "excluding VAT"
- Financial services (Nordea, DBT, Bambora, Skatteverket) — no VAT applies
- Foreign suppliers (Google, AWS, Voxbone, LetsLaw, Openrouter) — reverse charge, no Swedish VAT

**Input VAT refund restored as recurring inflow (id 48):** -125K SEK quarterly on day 30, quarter_months 1,4,7,10.
- Calculation: ~168K input VAT (25% on ~212.5K/month Swedish suppliers × 3) minus ~42K domestic output VAT (25% on ~55K/month SEK revenue × 3) = ~126K net, rounded to 125K.
- SEK revenue is only ~2% of total (~53-73K/month from service_revenue_cogs table).
- The bank pays costs incl. VAT even though budgets are excl. — the refund is real cash returning.
- Net quarterly VAT impact: MOSS -206K + refund +125K = -81K net outflow.
- **Earlier error:** Removed this refund thinking costs excl. VAT made it unnecessary. Wrong — the bank still pays incl. VAT, so the refund is a real cash inflow regardless of how costs are budgeted.

**Henrik Thome — accumulated company debt (account 2890 "Utlägg Henrik Thome"):**
- SIE data through Jan 2026: running balance -100,700 SEK (company owes Henrik)
- Unbooked expenses Feb–Apr 2026: ~207K SEK (Voxbone top-ups, MacBook, telecom services)
- Estimated total owed: ~307K SEK
- Key driver: Henrik paying Voxbone from personal AMEX (recurring ~79K/month) plus equipment purchases
- **Separate from the 400K loan** (scheduled id 38: 100K May 15, id 39: 300K Jun 15)
- **Reimbursement scheduled in 3 tranches:**
  - Scheduled id 42: 100K on 2026-06-30
  - Scheduled id 43: 100K on 2026-07-31
  - Scheduled id 44: 107K on 2026-08-29 (verify actual balance before paying)
- **Cash flow impact by month:**
  - May: 100K (loan tranche 1)
  - June: 300K loan + 100K reimbursement = 400K to Henrik
  - July: 100K reimbursement
  - August: 107K reimbursement
- **Note:** The 307K estimate may grow — new Voxbone/expense claims will keep adding. The final tranche should be reconciled against actual 2890 balance.

**India cash requirement April 2026 (Padma email Apr 16):**
- Total request: 90 KUSD (~945K SEK). India bank balance: 643 USD (nearly empty).
- Breakdown: TDS March 14K USD + Salaries 48K USD + RTDS invoices 21.5K USD + Vendor payments 6.5K USD
- The 90K USD INCLUDES the delayed March TDS — it is NOT extra on top.
- The 90K falls within existing monthly India recurring budget (~1.5M SEK ≈ ~143K USD). Not extra cost, but transfer is urgent.
- **Scheduled payment id 17 DISABLED:** March advance tax 117,162 SEK was a separate line item, but this cost is already covered within the regular India monthly recurring payments. Keeping it would double-count.
- India's fiscal year starts April 1, so March TDS timeline is "relaxed at the start of the financial year" per Padma.

**March 2026 one-off cost spikes (India trip):**
- Fluff/Rainbow: regular consulting 16,900/month, India trip added ~14K (flights + visa)
- Tomas André: Finnair 20,011 + MrJets 1,447 = ~21.5K travel costs on top of regular 92.5K fee
- These are one-offs, not baseline changes

---

## 2026-04-17: First MTD crosscheck (April 2026)

**Data sources:** Nordea SEK CSV (Apr 1–16), MCP recurring/forecast

**MTD cost comparison:**

| Item | Budget (SEK) | Actual (SEK) | Delta | Notes |
|---|---|---|---|---|
| Skatteverket | 96,800 | 98,762 | +2% | On budget |
| DBT loans | 135,098 | 136,050 | +0.7% | On budget. Hit as single payment Apr 9, not split on day 28 |
| Google Adwords | 120,000 | 107,044 | -11% | Under budget. Hit Apr 14, earlier than planned day 17 |
| SEB credit card | 120,000 | 190,527 | +59% | META ads (5×7,500 = 37,500) moved to card. Remaining ~33K gap = normal variance |
| BDO accounting | 55,000 | 112,139 | +104% | Extra work for annual report (ÅR). One-off spike, not new baseline |
| Nordea bank fees | 5,000 | 6,699 | +34% | Consistently over budget |
| Credit line interest | 10,000 | 13,801 | +38% | Depends on utilization level. Credit line drawn to ~927K of 1M |
| G&W advisor (quarterly) | 0 (wrong month) | 43,125 | Unbudgeted | Was scheduled for months 2,5,8,11 — actually hits 1,4,7,10 |
| Forvis Mazars (audit) | 0 | 125,000 | Unbudgeted | Annual audit fee. Was missing entirely from forecast |
| Svensk e-identitet | 0 | 378 | Minor | BankID service |
| **TOTAL matched** | **~542,000** | **~886,000** | **+63%** | |

**Payments planned but not in SEK CSV (may be paid from other accounts):**
- Voxbone 79,205 (day 1)
- AWS 2,000 (day 2)
- Linn Kristensson 22,000 (day 5)
- CFO 5,000 (day 7)
- Cision 5,000 (day 15)

**Unidentified entries:** 34,750 (Apr 1) + 17,784 (Apr 15) = 52,534 SEK — not yet drilled into.

**Budget corrections applied:**
1. SEB credit card (id 7): 120,000 → 190,000 SEK
2. META & Bing (id 28): disabled (spend now on SEB card, was double-counted)
3. G&W (id 31): quarter_months 2,5,8,11 → 1,4,7,10
4. Forvis Mazars (id 46): added as annual 125,000 SEK in April (new) — later corrected to 100,000 excl. VAT on 2026-04-18

**Key learnings:**
- "Corporate Access" in Nordea CSV bundles unrelated payments — always drill into sub-items
- "(1) Corporate Access" = Skatteverket and BDO payments
- "(2) Corporate Access" = SEB credit card, G&W, Forvis Mazars
- Revenue inflows are lumpy (Adyen settles every few days in large batches, not daily)
- Several planned payments don't appear in the SEK CSV — likely paid from EUR/USD accounts or other channels

**Forecast reliability verdict:** April forecast unreliable by ~344K SEK (63% cost overrun MTD), primarily driven by unbudgeted items now corrected. After corrections, remaining structural underbudgeting is ~40K/month (bank fees + credit interest).

---

## 2026-05-10 — COGS taxonomy session (CEO clarifications, structural learnings)

**Trigger**: CEO scrutiny on forecast trust ("entire forecasting model has been wrecked"). Began with audit of 8 recurring changes in last 7 days, evolved into structural double-count diagnosis.

### Confirmed: cogs_factor calibration source

CEO 2026-05-10: "COGS factor is derived from accounting, where all COGS (paid via PayPal or Nordea) are accounted for." → cogs_factor = total 4xxx ÷ revenue, includes ALL 4xxx items regardless of payment channel.

### Confirmed: COGS taxonomy

CEO 2026-05-10:
- COGS = phone numbers (Voxbone via AMEX/bank, DIDWW via PayPal) + call termination (IDT, DIDWW via PayPal, others) + SMS (Direct7 via SEB Kort) + AI production (OpenAI via SEB Kort)
- 4030 AI-tjänster = OpenAI ONLY (production)
- Anthropic + OpenRouter = dev tools = should be 6540 (NOT 4030)
- 4020 Awin (legacy P&L name "ShareASale") = same vendor (Awin acquired ShareASale)

### Confirmed: channel rules

- SEB Kort cannot catch up — autogiro hits in real time
- Catch-up reclassification ONLY possible via expense claims (Tomas/Henrik utlägg)
- SEB Kort invoice details = source of truth for per-vendor breakdown (SIE aggregates pool across vendors)

### Identified double-counts

- id 1 Voxbone 79K (account 4010) — also in cogs_factor → double count
- id 17 Europlanet 4K (account 4015) — also in cogs_factor → double count
- id 7 SEB Kort 140K — partial double count: ~75-90K/mo of items also in cogs_factor (OpenAI 4030 + Awin 4020 + SMS 4021)
- **Total phantom outflow: ~158-173K/mo**
- Fix: 3 separate 5-step processes (disable id 1, disable id 17, reduce id 7 to ~55K non-COGS portion)
- **Status**: NOT YET EXECUTED. Awaiting CEO go-ahead.

### Identified data bug — supplier default_account_number

`suppliers` table has Anthropic default_account_number = 4030. Should be 6540 (dev tools). This causes Tomas's Anthropic claims to flow to 4030 in BDO's books, contributing to the Mar 2026 4030 spike. **Action needed**: ask Jennifer/BDO to fix supplier default + reclassify historical entries.

### Mar 2026 4030 -165K spike — partly diagnosed, partly open

Receipts pipeline shows Mar 2026 AI vendor charges totalling ~88K (OpenAI ~20K + Anthropic ~25K + OpenRouter ~44K). SIE 4030 = -165K → ~77K gap unexplained. CEO ruled out catch-up via SEB Kort. Likely sources of gap:
- Direct OpenAI API usage invoice not yet processed in receipts pipeline (need SEB Kort Mar invoice)
- Other Mar transactions misclassified to 4030 by BDO

**Action needed**: pull SEB Kort Mar 2026 invoice + ask BDO what else is on 4030 Mar.

### id 7 description updated 2026-05-10 (description-only, no 5-step)

Added 4021 SMS providers, noted Awin = ShareASale, noted Anthropic/Openrouter should be 6540, noted SEB Kort invoice = source of truth, flagged ~75-90K partial double-count pending 5-step.

### Skill updates 2026-05-10

Added new section "COGS taxonomy + double-count rules" to SKILL.md covering:
- cogs_factor source (accounting-based per CEO)
- Full COGS components table with vendor + account + channel + double-count flag
- Non-COGS items (5xxx/6xxx) modeled separately
- Channel typology (SEB Kort, utlägg, PayPal, bank, SWIFT)
- AI cost classification (OpenAI vs dev tools)
- Known double-counts table
- Verification rule (SEB Kort invoice for SEB items)
- Catch-up reclassification rule (only via expense claims)

---

## 2026-05-10 CORRECTION (later same day) — DOUBLE-COUNT DIAGNOSIS WAS WRONG

After spawning reviewers for PLAN-A (disable id 1 Voxbone + id 17 Europlanet), reviewer #1 scored 62/FAIL and flagged: "Edge case missed: calibration period — the plan doesn't state whether the 21.8% was calibrated over a window that included these specific Voxbone/Europlanet postings."

Investigating in code: `cash_flow_forecast_service.py:1898 get_effective_cogs_percent()` reveals:
```
effective_cogs_percent = full_cogs_percent − tracked_cogs_percent
```
where tracked_cogs_percent = sum of enabled recurring_payment items on 4xxx accounts ÷ revenue.

**The system is DESIGNED to avoid the double-count.** Tracked items affect the forecast via fixed-cost firing only; untracked items affect it via revenue-netting only. Each cost counted exactly once.

### Retractions

1. PLAN-A withdrawn. id 1 Voxbone and id 17 Europlanet are NOT double-counted (they are properly tracked-subtracted from full COGS). Disabling would NOT save any cash; it would just shift the same money from per-day netting to fixed-day outflow.
2. Earlier-today claim of "id 7 partial double-count of ~75-90K" — partially WRONG, partially RIGHT. id 7 has account_number = 6540 (not 4xxx), so its 4xxx-account components (4030 OpenAI + 4020 Awin + 4021 SMS) are NOT in tracked_cogs subtraction. id 7 IS partially double-counted (~50-90K/mo), but the fix is to split id 7 into 4xxx and 6xxx halves, NOT to disable id 1 / id 17.
3. SKILL.md "COGS taxonomy + double-count rules" section rewritten to reflect actual mechanism.
4. id 7 description corrected in DB.

### Lesson learned

**Before proposing to disable any 4xxx recurring item, READ the actual cogs_factor derivation code** (`get_effective_cogs_percent()` and `_get_tracked_cogs_monthly()`). Don't infer the mechanism from black-box reasoning about what cogs_factor "should" mean.

### What remains real

- **Anthropic supplier default = 4030** (should be 6540) — still real, still needs fixing in DB + Jennifer email for historical reclassification.
- **id 7 SEB Kort partial double-count via missing 4xxx tracking** — real but smaller than originally claimed; needs SEB Kort invoice for accurate split.
- **Mar 2026 4030 -77K gap** in receipts vs SIE — still real, still needs SEB Kort Mar invoice + BDO query.
- **Overall trust gap raised by CEO** — still real; the recent forecast changes (8 in 7 days) deserve scrutiny independent of this incorrect double-count framing.

---

## 2026-05-10 — PLAN-C v2 + PLAN-B EXECUTED (5-step process, both audited PASS)

### PLAN-C v2: id 7 SEB Kort split (audited 85/84)

Fixed the partial double-count where id 7's 4xxx-component charges (Awin 4020, SMS 4021, AI 4030) escaped tracked_cogs subtraction because id 7's account_number was 6540.

**Changes**:
- UPDATE id 7: amount 140K → 100K (non-COGS portion: META + SaaS dev + misc), account 6540 unchanged
- INSERT id 57: "SEB Kort - Awin", 30K, account 4020, day 10
- INSERT id 58: "SEB Kort - SMS providers", 7K, account 4021, day 10
- INSERT id 59: "SEB Kort - AI prod", 25K, account 4030, day 10
- All new entries: supplier_id=NULL (don't compete with id 7 in bank reconciliation)
- Total SEB Kort bundle: 162K (was 140K, +22K matching 3-mo avg 161K)

**Forecast effect (verified live via MCP)**:
- tracked_cogs_monthly: 83K → 145K (+62K)
- effective_cogs_percent: 18.6% → 16.2% (-2.4pp)
- Revenue inflow estimate: +62K/mo
- Net cash flow improvement: +40K/mo
- EOM May projection: -855K → ~-815K
- 6-month cumulative improvement: ~+240K

**Process discipline**:
- v1 plan FAILED gate at 72/58 (single-month basis, bundling, stale total)
- v1 was REVISED into v2 with multi-month data, per-account split, recalibrated total
- v2 PASSED reviewers 78/72, then auditors 85/84
- Auditor #2 ran live MCP verification confirming forecast service picked up the change correctly

### PLAN-B: Anthropic supplier default 4030 → 6540 (audited 88/82)

`suppliers.default_account_number` for "Anthropic" updated from 4030 (AI-tjänster, OpenAI production) to 6540 (Molntjänster, dev SaaS). Forward-only effect — future Tomas/Henrik expense claims for Anthropic will default to 6540.

**Open follow-up for Jennifer/BDO**:
- Reclassify Q1 2026 historical SIE entries on 4030 from Anthropic claims (~70K SEK estimated)
- Until done, historical 4030 overstates "AI production COGS" — small inflation of full_cogs_percent calibration

### Lesson learned (also captured in SKILL.md)

The first-iteration "double-count rules" framing was wrong because the system has a built-in tracked_cogs subtraction. Real bug was narrower: id 7's account_number=6540 caused its 4xxx components to escape the subtraction. RESOLVED.

### Other findings still open (not acted on today)

- Mar 2026 4030 -77K gap in receipts vs SIE — needs SEB Kort Mar invoice or BDO query (likely a direct OpenAI ACH invoice for production API usage)
- 4-month SEB Kort trend declining (Apr 122K vs 3-mo avg 161K) — recalibration in 1-2 months may be needed
- META projected to continue declining (currently 30K Apr from peak 55K) — could drop further toward 0
