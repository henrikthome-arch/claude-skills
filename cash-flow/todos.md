# Cash flow — outstanding work

Living todo list of cash flow forecast model improvements. Created 2026-05-08. Updated as items complete or new ones surface. Future agents: read this in addition to SKILL.md, log.md, and the Calibration Registry.

## ÖPPNA BESLUT OCH LÖSA TRÅDAR (2026-08-18, väntar på Henrik eller på nästa session)

### Väntar på Henrik
- [ ] **Granskningsgrindens nivå.** Dokumenterat är 70 (kassaflödesskillens 5-stegsprocess); för kod finns ingen siffra alls i CLAUDE.md. Jag föreslog **80 för kod som rör produktionens skrivvägar** (migrationer, triggrar, routes) plus en absolut regel: **noll olösta blockerare oavsett poäng**. Skälet: migration 102 passerade på 74/82 och bröt varenda skrivning i portalen; CR-2026-08-18 fick 76/76 med tre blockerare. Han har inte svarat.

### Lösa trådar från 2026-08-17/18
- [ ] **id 81** (43 000, 15 aug, Henrik-återbetalning) avstängd utan att kunna verifieras mot bank — bankdata gick bara till 13 aug. Bekräfta om den betalades; i så fall återaktivera som faktisk post.
- [ ] **Juli Indien-gap:** faktiskt 98 044 USD mot Padmas estimat 110 917 = **12 873 USD**. Total-nivå, ingår i Indien-brevet.
- [ ] **SEB Kort id 7 döljer ~66 KSEK** som hör till konto 5991/5992/5800/5410/6211 (changelog 2026-08-17).
- [ ] **SKILL.md motsäger sig själv på två ställen** och båda ska skrivas om i samma pass som India-tabellen: rad ~567 *"Only the SEB Kort invoice itemises the autogiro charges by vendor"* är motbevisat — kortraderna ligger i `transaction_batches` med `file_type='credit_card'`, radspecificerade. Och rad ~671 *"Per-transaktionsmatchning är en återvändsgränd"* drar mot vendor-nivå-matchning som svepet bygger på. Två regler som pekar åt olika håll.
- [ ] **Parallella sessioner:** 2026-08-17 arbetade två sessioner i modellen samtidigt och bottennivån flyttade sig fyra gånger på en timme utan att någon varnades. Kolla `git log --oneline -5` och `updated_at` på berörda rader innan ändring.
- [ ] **`saveRecurring()` nollställde `is_internal_transfer`** — lagat 2026-08-18, men loggens tidiga poster kan visa spökflippar av det fältet från UI-sparningar före fixen. Läs dem inte som manipulation.

## P0 — VALIDERINGSSVEPET (beslutat 2026-08-18, INTE påbörjat)

CEO 2026-08-18: *"Bin the machinery. Just have a skill do the work."* Metoden ligger i SKILL.md, "Validating an amount against its real payment channel". Ingen migration, inga nya kolumner — verifieringen skrivs som en beskrivningsnotering och loggas automatiskt.

**Status: 6 av 44 rader klara (+2 nya rader). India: listan skickad till Prashant 2026-08-18, svar inväntas.**

56 aktiva recurring-rader totalt: 44 svenska/övriga + 12 India (parkerade tills India svarar).

**Metoden är EN RAD I TAGET** (CEO 2026-08-18: *"One by one. You take one at a time."*). Det ersätter den
tidigare tvåomgångsplanen med batchgodkännande nedan. Format och lärdomar: se SKILL.md, "The sweep — ONE ROW AT
A TIME".

Klara:
- [x] **id 11 Google, 120 000 -> 110 000 SEK/mån** (2026-08-18). Bank: Google Ireland, en betalning/mån, sju
  månader 2026 (jan 353K fallande till ~110K från april). Bokföringen 5990 matchar varje bankrad på öret med
  två perioders förskjutning, och period 202606 = 111 338 ÄR augustibetalningen. Godkänt: *"OK, change to 110
  KSEK"*. Öppen följdfråga: konto 5991 (andra annonskontot) föll från 150-213K/mån 2025 till 30-50K — reds ut
  mot id 7 SEB Kort.

### Omgång 1 — 18 rader, 1 241 511 SEK/mån (52,9 % av modellen)
Kör mot rätt kanal per rad. Presentera med modellbelopp, kanalens utfall (3 mån, 12 där historiken räcker), avvikelse, förslag. Batchgodkännande av Henrik.

- [ ] ~~Omgång 1 / omgång 2 med batchgodkännande~~ **ERSATT 2026-08-18 av en-rad-i-taget.** Ordningen (störst
  månadsekvivalent först) står kvar; batchandet gör det inte.
- [x] **id 7 SEB Kort icke-COGS, 117 000 -> 126 000 SEK/mån** (2026-08-18). Kortblocket (7/57/58/59) stämde
  redan på 442 SEK/mån mot utfallet — ändringen drevs av SAMMANSÄTTNINGEN: META har rampat 30 425 (apr) ->
  63 065 (jul) medan övrig SaaS fallit lika mycket. CEO: *"Expect META to stay at current level"*. 5991 är
  META (matchar kortbatchen på kronan, noll förskjutning) — ingen dold annonskostnad utanför modellen.
- [x] **Salesforce brutet ur id 7 till egen rad, id 67** (2026-08-18). 4 570,08 USD/kvartal, kvartalsmånader
  3,6,9,12 dag 10, och id 7 ned till 111 500. Ligger i USD eftersom varje betalning är exakt samma
  USD-belopp. **Kassamånaderna är INTE inköpsmånaderna** — kortfakturan betalas ~dag 9-14 månaden EFTER
  batchen (tre exakta batch-mot-bank-matchningar: 2025-12 = 129 219 betald 2026-01-09; 2026-05 = 190 864,21
  betald 2026-06-10; 2026-06 = 136 583,53 betald 2026-07-14). Faller i september, inte oktober.
- [ ] **FÖLJDKONTROLL ~1 sep 2026:** augustibatchen ska visa Salesforce ~25 aug. Gapet dec-2025 till feb-2026
  var 56 dagar, inte 90, så kadensen är inte helt ren. Syns den inte — ta upp id 67 igen.
- [x] **id 19 Tomas André (Dolutions AB), 115 625 SEK/mån — VERIFIERAD OFÖRÄNDRAD** (2026-08-18).
  92 500 exkl moms x 1,25, och konto 6550 står på exakt 92 500,00 i period 202511. Sex betalningar på
  exakt 115 625 under sju månader; endast maj 2026 saknas (~115 625 utestående). Junibetalningen låg inne
  i en buntad rad "(2) Corporate Access" 125 188 = Dolutions 115 625 + United Spaces 9 563, bekräftat av
  Henriks Nordea-uppslag. Ingen catch-up-rad: en leverantör som ligger permanent en månad efter påverkar
  inte kassaflödet framåt. Ta upp igen bara om Tomas betalas ikapp.

- [x] **NY RAD: United Spaces styrelsemötesrum, 4 200 SEK/kvartal** (2026-08-18). Kostnaden har funnits i
  minst ett år och låg INTE i prognosen alls. Konto 5011 ligger platt på 5 060 exkl moms och hoppar till
  8 420 i period 202512 och 202603 — överskottet är exakt 3 360 exkl = 4 200 inkl, och det finns en
  bankbetalning på exakt 4 200,00 den 2026-01-08. Möten hålls dec/feb/jun/sep; KASSAN kommer ~en månad
  senare, alltså quarter_months 1,3,7,10 dag 8. **Oktoberutfallet ligger i bottenmånaden.** Godkänt: *"4200 ok"*.

- [x] **id 18 United Spaces — OMSTRUKTURERAD, inte omkalibrerad** (2026-08-18). Raden hade fel FREKVENS.
  Henrik tog fram faktura 2491 (2026-05-26, OCR 249169, 30 dagar netto): en rad, *"Lounge Large
  (2026-07-01 – 2026-09-30)"*, 3,00 x 2 550,00 = 7 650 exkl = 9 562,50 inkl — vilket ÄR betalningen på
  9 563,00 den 2026-06-25 som låg gömd i en Corporate Access-bunt. Alltså **en plats, 2 550/mån exkl moms,
  fakturerad kvartalsvis i förskott**. Raden är nu 9 563 kvartalsvis, quarter_months 3,6,9,12 dag 25.
  Månadsekvivalent 3 188 mot tidigare 3 625.
  - **Två tidigare tolkningar är därmed döda:** (a) 9 563 var INTE månadshyra + styrelsemöte, så uträkningen
    som pekade på en delvis platsminskning i juni var en slump; (b) det fanns ingen styrelsemötesbetalning
    i juni, vilket ÅTERSTÄLLER en månads eftersläpning och bekräftar att id 68 ska ligga kvar på 1,3,7,10.
  - **ANTAGANDE** (Henrik: *"Får förmoda"*): att kvartalsfakturering i förskott är permanent. Bokföringen
    visar en MÅNATLIG bas på 5 060 exkl t.o.m. period 202605, så det är en färsk ändring.
    **TEST ~2026-09-25:** faktura ska utfärdas ~26 aug och betalas ~25 sep för okt–dec. Kommer i stället
    månadsbetalningar tillbaka — ställ om raden till monthly igen.

### Lånklustret — DBT + Nordea, 236 940 SEK/mån

- [x] **id 26 + id 61 DBT Lån 2 (16 425,44 + 50 000) — VERIFIERADE OFÖRÄNDRADE** (2026-08-18). Fem
  räntebetalningar jan–jun i snitt 16 440,88 mot modellens 16 425,44 (15 kr fel). Första fulla betalningen
  66 425,44 den 2026-07-31 = exakt 50 000 + 16 425,44. Konto 2399 rör sig exakt 50 000/mån. CEO: *"Loan 2
  had no amortizations until recently when they started."* **Modellen bar 50 000/mån amortering jan–jun då
  ingen betalades — ca 300 000 övermodellerat.** Ej bakåtkorrigerat; prognosen är framåtblickande och raden
  är rätt från juli.
- [x] **Namn och kontokoder harmoniserade på alla fyra DBT-rader** (2026-08-18). Räntor låg på skuldkonto
  2352, Lån 1:s amortering pekade på Lån 2:s konto 2399. Nu: ränta → 8410, Lån 1 amortering → 2352, Lån 2
  amortering → 2399. Belopp orörda.

- [ ] **id 24 DBT Lån 1 ränta — VÄNTAR PÅ HENRIK.** Modellen 37 098,33 fast; faktiskt fallande ~893/mån
  (jan 39 169 → jun 33 812). Implicerar 10,9 % årsränta och ~3,72 MSEK kvar, vilket stämmer mot 5 MSEK
  minus 13 månaders amortering = 3,73 MSEK. Prognos aug/sep/okt/nov = 32 919 / 32 026 / 31 133 / 30 240.
  **Förslag: 31 500** (snitt aug–nov), med kvartalsvis omprövning. Förbättrar prognosen ~5 600/mån.
- [ ] **id 25 DBT Lån 1 amortering — VÄNTAR PÅ HENRIK.** Beloppet stämmer (konto 2352 = 26 042 Nordea +
  98 039,22 denna; modellen har 98 000, 39 kr fel). **Öppen fråga: julibetalningen sköts till augusti —
  betalas EN eller TVÅ omgångar i augusti?** Två = engångspost ~132 K i augusti som saknas i prognosen.
  En = hela schemat förskjutet en månad, ingen effekt framåt (samma logik som Tomas id 19).

- [ ] Nordea-lånen (id 22 26 041,67 + id 23 9 375) — ej påbörjade.

- [ ] **STRUKTURELLT — bankvalideringens blinda fläck.** 63 % av allt utflödesvärde saknar mottagarnamn.
  Per konto: nordea_main 66 rader / 4,0 MSEK utan namn (44 % av kontots värde), nordea_usd 154 / 16,3 MSEK
  (63 %), nordea_eur 177 / 9,2 MSEK (75 %). Etiketterna är "Ny DEPOSIT VALUTA" (246 rader, valutakontona),
  "Corporate Access" (52 rader, 3,5 MSEK, huvudkontot), bara siffror (95 rader) och "Importerade
  kontohändelser" (4). **Det är beloppsmatchning, inte namnmatchning, som burit svepet hittills** — det
  fungerar när beloppet är distinkt och fallerar när det inte är det. Fråga till Henrik: vad ÄR Corporate
  Access, och finns mottagarnamn i Nordeas export som vi inte importerar? Svaret låser upp validering för
  hela den återstående sweepen, inte bara en rad.

- [ ] Nästa rad efter id 19: **id 25 DBT Lån 1 - amortering, 98 000 SEK/mån** (och id 12 Salaries Sweden
  98 000, samma storlek).

### India — eget spår, 12 rader, 874 068 SEK/mån (37 %)

- [x] ~~**SPÄRR FÖRST:** skillens India-tabell stämde inte med databasen på sex rader.~~ **Löst 2026-08-18 (CR-2026-08-18-monthly-india-confirmation).** Tabellen är borta — 74 rader hårdkodad DB-state ersatta av de två frågor som återskapar dem. Driften var värre än sex rader: PLAN-H 74–80 visades som aktiva fast alla sex är avstängda, och månadstabellen för Indiens kassaflöde var räknad ur just de avstängda raderna, alltså fel i varje rad. Oktoberpåminnelsen citerade 4M INR den 4 nov mot radens 4 024 356 den 30 okt och hade slagit till om ~6 veckor; den frågar nu databasen i stället.
- [ ] **Cirkulariteten:** de sex raderna märkta "covered by Padma SWIFTs" kan bara avgöras av Padmas SWIFT-historik, vilket är det brevet frågar om. Lös 39 (jan) och 40 (jun) mot Nordeas USD-konto på totalnivå; 36/41/42/43 ligger i sep/nov/dec utanför bankdatans fönster (jan–jul) och går som öppna frågor i brevet i stället.
- [x] **Skickat till Prashant 2026-08-18** (CEO skickade själv; ej via Padma som planerat). Listan kom ur databasen: månadsbas 7 719 810 INR, effektivt 7 910 000 t.o.m. november, årsnetto 8 513 356 INR. Innehållet nedan står kvar som mall för nästa omgång — den går nu automatiskt via monthly-intake steg 4d.
  ~~Till Padma Karanam, kopia Prashant Pant.~~ Engelska, tabell i brödtexten, svar inom 10 arbetsdagar, Riksbankens INR-kurs utskriven. Innehåll finns i `docs/plans/CR-2026-08-18-multichannel-validation-sweep.md` (övergiven som CR, men tabellen och brevinnehållet är verifierade och korrekta).
  - Alla tolv raderna med **belopp, frekvens OCH datum**
  - ids 41 och 43 som EN parad rad — båda 30 sep, +1 600 000 mot −1 900 000, netto −300 000
  - De tre inflödesraderna (43, 63, 64) formulerade som "när kommer den och står beloppet sig", inte "bekräfta att ni betalar"
  - T3-tilläggen: scheduled 104–107, +190 190 INR/mån aug–nov, annars bekräftar Padma 4 004 810 mot en modell som planerar 4 195 000
  - T1/T2/T3: begär **underlag** (betalningskalender eller kontoutdrag för en månad), inte ett ja på vår 8/39/53-gissning
  - Goa id 62 (8 000 USD/år) med — annars avgränsas Indien på valuta i stället för kostnadsägarskap
  - Öppen fråga: finns poster Indien betalar som saknar rad hos oss?
- [ ] När svaret kommer: verifieringsnotering per rad med Padmas svar i `basis`, Henriks OK i `approved_by`. Avvikelser blir beloppsändringar och kräver hans godkännande enligt migration 102.

### Övergivet, med avsikt
`CR-2026-08-18` (valideringskolumner + migration 103) — **återuppliva inte** utan att först ha kört en omgång manuellt och funnit att det som saknas verkligen är en "senast kontrollerad"-kolumn.

## P0 — ÅTERKOMMANDE: månatlig kalibreringsgenomgång (införd 2026-08-17)

**Körs varje månad när SIE-datat för den stängda månaden landat** (Fortnox-synken drar in det automatiskt). Ingen hook, ingen timer — den här raden ÄR påminnelsen. CEO 2026-08-17: *"Bättre att ha en skill som identifierar potentiella gap och pratar igenom det hela med mig, t.ex. vid månadskörning av rapporter."*

1. Kör `ssh -i github-actions-deploy ubuntu@44.194.218.109 "dbshell" < ~/.claude/skills/cash-flow/calibration_check.sql`
2. Följ *Månatlig kalibreringsgenomgång* i SKILL.md: översätt varje träff till ett **beslut** med förslag, inte till en observation.
3. Varje post landar i justera / bekräfta-som-den-är / skjut-upp-**med-datum**. Uppskjutet utan datum = posten ruttnar.
4. Uppskjutna poster förs in nedan och tas upp igen nästa månad **med sin ålder**. Två uppskjutanden i rad → lyft som eget beslut: "vad hindrar oss från att bestämma?"

**Senast körd:** 2026-08-17 (första körningen). **Nästa:** när augusti-SIE landat.

### Öppna poster från körningen 2026-08-17 — ej genomgångna med CEO ännu

| Post | Modell | Bokföring | Per mån | Status |
|---|---:|---:|---:|---|
| 6572 PayPal-avgifter (id 53) | 45,000 | 55,218 | −10,218 | Ny — underbudgeterat |
| 6490 Övr förvaltning (ids 13/31/51 + Nasdaq) | 40,158 exkl | 24,447 | +15,711 | Ny — överbudgeterat. Mangold-placeholder id 51 är 107 dgr gammal och ligger här |
| 2890 Henriks skuld | 0 planerat | 691,753 skyldigt | — | Känt, CEO-beslut 2026-08-17: inget planeras |
| 2899 övriga kortfr. skulder | 0 planerat | 136,584 skyldigt | — | Ny — **vems skuld? Troligen Tomas/övriga. Utred.** |
| 6380 / 6996 / 5410 / 5810 | ingen rad alls | 16–72K/mån | — | Ny — oklassade konton utan prognosrad. Klassa: modellera eller lägg i exkluderingslistan med skäl |
| `cashflow_cogs_percent` 21.8% | manuell | — | — | Satt 2026-01-30, **199 dgr sedan**. Omkalibrera mot SIE 4xxx÷intäkt |

### Övriga öppna poster 2026-08-17
- [ ] **Aug OCH okt bryter checkkrediten**: 28 aug −1,019,221 / 30 okt −1,186,923 mot 1 MSEK-taket. Kräver eget beslutsmöte — det är inte en kalibreringsfråga.
- [ ] **id 81 (43,000, 15 aug)** disablad utan att kunna verifieras mot bank (data bara t.o.m. 13 aug). Bekräfta om den betalades → återaktivera som faktisk post.
- [ ] **Juli India total-gap**: faktiskt 98,044 USD mot Padmas estimat 110,917 (~12,900 USD). Total-nivå, värt att stämma av.
- [ ] **Parallella sessioner**: 2026-08-17 arbetade två sessioner i modellen samtidigt, bottennivån flyttade sig tre gånger på en timme utan varning. Kolla `git log --oneline -5` och `updated_at` på berörda rader innan ändring.

## P0 — Active code work (real CRs, blocking other improvements)

### TODO-1: Revise + ship CR-2026-05-08 (PSP fees model fix)
- **File**: `docs/plans/CR-2026-05-08-psp-fees-cogs-model.md`
- **Status (2026-05-08 EOD)**: 
  - v1: 55/100 (premise unverified)
  - v2: 78/82 — gate passed, but reviewer #2 surfaced additional `'cogs'` hardcoded refs in P&L display layer (lines 706-907)
  - v3: simpler data-only proposal — **45/88, gate FAILED**. Reviewer #2 caught critical bug: `business_parameters.cashflow_cogs_percent` is a FALLBACK in `get_auto_cogs_percent` line 1841-1850, NOT an active override. v3's premise is wrong — updating it has no effect on forecast.
- **Conclusion**: TODO-1 genuinely requires a code change. Three viable paths:
  - **(a)** Modify YAML to include 6572 in `cogs` category — affects auto-calc + P&L display together (reviewer #2's preferred fix)
  - **(b)** v2's `cogs_like` flag approach with P&L display layer scope
  - **(c)** Modify `get_auto_cogs_percent()` precedence so `business_parameters` overrides P&L
- **Required for next session**: focused code session with proper testing of chosen path. Not appropriate for inline forecast-edit process.
- **Revision tasks**:
  1. Fix 6571 P&L hole: keep 6571 in `other_external` (Bambora/Adyen still recurring-modeled). Only reclassify 6572 to `cogs_like`.
  2. Address hardcoded `'cogs'` key in `get_auto_cogs_percent()` (line 1808-1809) and `_get_tracked_cogs_monthly()` (line 1877). Implementation must extend to iterate `cogs_like` categories.
  3. Fix acceptance criterion: original "EOM May 31 unchanged ±10K" is wrong. Replace with "forecast revenue inflow rate matches actual bank settlements within ±2% over a 1-month validation window."
- **Implementation steps after revision**:
  - Update `config/analytics/group_pl_categories.yaml` with `cogs_like` flag handling
  - Update `libs/financial_core/services/cash_flow_forecast_service.py` (3 functions)
  - Disable recurring id 53 (PayPal fees synthetic)
  - Update business_parameter `cashflow_cogs_percent` from 21.8% to ~23.5%
- **Effort**: Multi-step. Plan + 2 reviews + 5-step process + code + audit. Probably 4-6 hours.
- **Blocks**: TODO-2 (drift detection should be built against post-fix model), TODO-3 (docstring should reflect post-fix conventions).

### TODO-2: Drift detection enhancement (replaces rejected CR-2026-05-08d)
- **Status**: Standalone validation-script CR rejected (duplicates `BankReconciliationService.get_reconciliation()` and `get_pl_validation_data()`). Replacement is small enhancement to existing code.
- **Tasks**:
  1. Add COGS-divergence check to `cash_flow_forecast_service.get_pl_validation_data()` (~10 lines)
  2. Add drift-threshold flag column to existing reconciliation view (`/analytics/cash-flow` validation panel)
  3. Document in SKILL.md as part of weekly analyst workflow
- **Effort**: ~1 hour, no new file
- **Blocked by**: TODO-1 (must reflect post-PSP-fix COGS model)

### TODO-3: Module docstring on cash_flow_forecast_service.py
- **Status**: Standalone CR rejected (35/42 score) — fold into TODO-1 instead
- **Tasks**: When TODO-1 is being implemented, expand the module docstring to reflect:
  - Gross-revenue convention (post-PSP-fix)
  - COGS%-as-revenue-netting model (now including PSP fees via cogs_like)
  - Recurring/scheduled overlay system
  - Channel mismatches (Voxbone/Openrouter)
  - India tranche split (3 monthly entries)
  - is_internal_transfer flag semantics
- **Blocked by**: TODO-1 (docstring should describe the post-fix state, not the transitional state)

## P1 — Calibration investigations (forecast data, follow 5-step process)

### TODO-4: Google Adwords 5990 — investigate 2× P&L vs model gap
- **Issue**: P&L CY2025 = 249K/mo, recurring id 11 = 120K
- **Possible causes**: Multiple Google ad accounts not all on the bankgiro flow seen in CSV; historical higher spend; account number mismatch
- **Action**: Pull 12-month bank outflow data for Google Ireland; compare to id 11 firings; reconcile against P&L 5990
- **Decision needed**: Adjust id 11 amount, add second recurring entry, or document as accepted variance
- **Effort**: 30 min investigation + 5-step process
- **Priority**: Medium — 2× gap is large but Google is a known cost line, not a hidden risk

### TODO-5: Styrelsearvoden 7240 — investigate 2.8× P&L vs model gap
- **Issue**: P&L CY2025 = 398K/year, recurring id 32 = 140K Dec annual
- **Possible causes**: Semi-annual board fees that aren't captured; P&L 7240 includes social charges (arbetsgivaravgift) on board fees that are tracked elsewhere; bonus payments
- **Action**: Decompose P&L 7240 monthly trend; check if there's a mid-year fee
- **Decision needed**: Add additional recurring entries (mid-year board fee?) or document
- **Effort**: 30 min investigation + 5-step process if change needed
- **Priority**: Low — annual item with predictable December timing

### TODO-6: META + Bing absorption in SEB Kort id 7 verification
- **Issue**: id 28 (META + Bing) was disabled, spend moved to SEB Kort id 7 (190K/mo). Need to verify id 7's budget actually absorbs ~130K/year combined META + Bing on top of other SEB card costs.
- **Action**: Audit one month's SEB Kort spec excel against id 7 budget; identify META + Bing portion vs other SaaS
- **Decision needed**: Confirm id 7 sufficiently sized, or split SEB Kort into multiple recurring entries by spend category
- **Effort**: 20 min audit
- **Priority**: Low — was one-time observation already, not active drift

### TODO-7: India 766K — kept as baseline; no bump
- **Issue framing was misleading**. "Under-budget vs 90 KUSD documented" treated one Padma request as steady-state, but Padma's monthly request ≠ steady-state burn. Some months include catch-ups (e.g. May 4-8 settled Jan invoice 20260001 — not recurring activity).
- **Historical actuals (3 months)**: Jan 2026 = 58 KUSD, Mar 2026 = 110 KUSD, Apr 2026 request = 90 KUSD. Range 58-110, avg ~86 KUSD ≈ 808K SEK.
- **Current 766K is reasonable steady-state**. Slightly under the 3-month avg (~5%) but biases conservative on outflow modeling, which is safer for credit-line management. Single-month spikes (high or low) are absorbed via scheduled overlays when needed.
- **Status**: ACCEPT 766K as baseline. No bump pending until data shows persistent deviation.
- **Re-open trigger**: trailing 3-month avg India actual outflow deviates from 766K by >10% for 2+ consecutive months. That's data-driven, not calendar-driven. Use TODO-2 drift detection (post-PSP-fix) to surface automatically.

### TODO-8: 4xxx COGS items — explicit recurring vs implicit via COGS%
- **Issue**: DIDWW (300K/mo), Net2phone (30K), Net2phone (30K), ShareAsale (37K), SMS providers (17K), AI-tjänster (22K) — none have recurring entries; absorbed by COGS% factor
- **Trade-off**: Adding explicit recurring entries improves daily-level forecast precision but adds maintenance. Current COGS%-implicit approach is monthly-net correct but distributes outflows evenly across the month rather than at actual payment dates.
- **Decision needed**: 
  - Option A: Add explicit recurring for DIDWW (the largest, 300K/mo) for daily-level precision; leave smaller items implicit
  - Option B: Status quo (all implicit via COGS%)
- **Effort**: Option A = 30 min via 5-step process; Option B = 0 effort
- **Priority**: Low — current model is correct on monthly net; daily distortion is the only concern, mostly mitigated by SEK saldo trajectory averaging out

## P2 — Deferred / external dependencies

### TODO-11: VAT refund id 48 vs Skatt id 9 — NO DOUBLE-COUNT (resolved 2026-05-08)
- **Original concern**: id 48 (-100K refund day 12) + id 9 (+70K Skatt day 12) both fire same day → potential double-count.
- **Investigation 2026-05-08**: 
  - Skattekonto mechanics: Sonetel pays monthly Skatt (70K) on day 12 = real cash outflow. Skatteverket credits konto with quarterly refund = accounting credit, no cash. Skatteverket pays bank from konto surplus periodically = real cash inflow.
  - Empirical May 2025 (last Q1 refund cycle): +98,554 refund (May 1) + -70,741 Skatt (May 12) = +27,813 net inflow. Two separate bank transactions.
  - Forecast model: id 48 -100K (modeled as inflow) + id 9 +70K (outflow) on day 12 = +29,259 net inflow.
  - **Match: 27,813 actual vs 29,259 forecast = 1,446 SEK gap, within noise.** Both must fire to get the net cash impact correct.
- **Resolution**: The 100K in id 48 represents GROSS quarterly refund (per skill documentation: "Calculation: ~168K input VAT minus ~42K domestic output VAT = ~126K net... rounded to 100K conservative"). id 9's 70K represents monthly Skatt obligation that's always due regardless of refunds. Both correctly fire. NO double-count. Model is correct on monthly net.
- **Status**: CLOSED no-action. Calibration registry note already captures this.

### TODO-17 (CLOSED 2026-05-10): Payment Schedule view in portal — SHIPPED
- **Source**: User 2026-05-09 — "I have no UI where I can see all payments planned with date and vendor for each month."
- **Shipped**: CR-2026-05-09 v2 (commit 451dde10, deployed via CI/CD 2026-05-10).
  - `/analytics/payment-schedule` page with month picker (6 back, current, 3 forward)
  - Full chronological list (recurring + scheduled, with id refs, currency, native amount, frequency badge)
  - Internal-transfer items flagged yellow + excluded from cash-outflow total
  - Inflows flagged green + reduce cash-outflow total
  - Totals card: cash outflow / internal transfer / revenue inflow estimate / net change / min projected balance + date
  - JSON endpoint `/analytics/payment-schedule.json?month=YYYY-MM` for skill consumption (`PaymentScheduleService`)
- **Deferred to follow-up CRs**:
  - **v1.5 (topic groupings)**: India total, DBT/loans, Skatteverket, Henrik, SEB Kort, EOM cluster as collapsible subsections with TOTAL CASH IMPACT lines
  - **v2 (P&L summary)**: prior-month actual + current-month forecast + budget + deviation + next-month forecast + budget + deviation, sourced from `group_pl_budget`
  - Click-through on any entry to recurring_payment / scheduled_payment row for editing
- **Process**: 5-step. Reviewers passed; auditors 95/92. Audit caught 2 silent bugs in `_extract_min_balance_for_month` (wrong `generate_forecast` signature; string-vs-date comparison swallowed by broad except). Both fixed before commit.

### TODO-18 (NEW 2026-05-09): India intercompany cleanup decision
- **Issue**: ids 2, 8, 14, 15 (is_internal_transfer=true, total ~760K SEK monthly) are book-entry intercompany items that conceptually duplicate ids 54-56 (cash side, 766K SEK monthly). id 37 (now disabled, replaced by 54-56) explicitly stated "replaces internal transfers" — but ids 2, 8, 14, 15 were never disabled.
- **Forecast impact**: zero (M-INT entries are filtered from cash burn anyway)
- **Visibility impact**: confusing when reading the recurring_payment table — sum of all India entries shows ~1.5M SEK rather than the real 766K cash flow
- **Action**: Confirm with Jennifer/BDO that ids 2, 8, 14, 15 are safe to disable from a reporting/accounting perspective. They may be referenced elsewhere outside the cash flow model.
- **Trigger**: When you have a chance to ask Jennifer
- **Effort**: 2 min if BDO confirms safe to disable; 5-step process for the disable

### TODO-15 (NEW 2026-05-09): SEB Kort recalibration after 3 more months
- **Status**: id 7 SEB Kort recalibrated 2026-05-09 from 190K → 140K based on 3-point recent actuals + META decline. Basis is thin (n=3).
- **Trigger**: When 3 more months of actuals available (May/Jun/Jul 2026 invoices, paid in late month autogiro).
- **Target review date**: 2026-08-15 (after Jul 2026 SEB Kort autogiro hits + invoice spec available).
- **Decision rule**: 6-point trailing avg (Dec 2025 + Mar 2026 + Apr 2026 + May 2026 + Jun 2026 + Jul 2026). If avg differs from 140K by >15K, recalibrate via 5-step.
- **Effort**: 30 min (pull 3 invoice specs + compute) + 5-step process.

### TODO-16 (NEW 2026-05-09): SEB Kort drift triggers (monitor)
- **Upside trigger**: SEB Kort actual >175K SEK in any single month → signals META spike or other restart. Manual recalibration via 5-step.
- **Downside trigger**: SEB Kort actual <110K SEK for 2 consecutive months → signals further sustained decline. Recalibrate id 7 downward.
- **Mechanism (manual until TODO-2 drift detection ships)**: Henrik checks SEB Kort spec against trigger thresholds when reviewing monthly statements.

### TODO-14 (NEW 2026-05-08): India people reduction — apply when effective
- **Source**: User 2026-05-08 from Prashant: "People cost - in the works. Planned about 5-6K USD monthly (6-7 people impacted - primarily in R&D). To be announced May 19th. People savings may take 2 months before they kick in."
- **Magnitude**: 5-6K USD/mo savings = ~50K SEK/mo at FX 9.4
- **Effective date estimate**: ~July 19 2026 (May 19 announcement + 2 months kick-in)
- **Action when effective**: Reduce `recurring_payment` id 56 (India T3 salaries) by ~50K SEK. Current 406K → ~356K. Run through 5-step process.
- **Trigger**: Confirmation that people reduction has actually taken effect (check actual India salary outflows for 1+ month after expected effective date). Don't apply on basis of announcement alone.
- **Risk if forgotten**: Forecast over-models India salaries by 50K SEK/month from July onwards.

### Also pending — India AWS reduction (gate failed 72/62 on 2026-05-08)
- Plan was to reduce id 54 vendor 60K → 32K to capture confirmed -3K USD/mo AWS savings.
- Reviewer #2 raised real concern: vendor composition uncertain. If id 54's 60K (Padma vendor portion 6.5K USD) actually bundles AWS + other SaaS + office + pro services, then attributing all savings to id 54 may under-model remaining vendor spend.
- **Action needed from user**: Confirm what's in id 54 (just AWS? or AWS + other items?). If just AWS, 60K → 32K is right. If mixed, need to split or adjust differently.
- **Until clarified**: id 54 stays at 60K (no change applied).

### TODO-13 (NEW 2026-05-08): Re-schedule deferred 100K Henrik loan repayment
- **Status**: 100K SEK was deferred from scheduled_payment id 45 (Jul 15 reduced from 150K → 50K) on 2026-05-08 to ease July saldo trajectory.
- **Open question**: WHEN does the 100K get repaid? Options:
  - Augment id 38 (May 15 100K) → already paid?
  - Add to Aug 29 id 44 (already 107K → 207K)?
  - New Sep/Oct/Nov scheduled entry?
  - 2027 if cash situation requires further deferral?
- **Action**: User decides timing in a future session. Then 5-step process to add the new scheduled_payment.
- **Risk if forgotten**: 100K loan principal effectively un-modeled. Forecast looks ~100K healthier than reality across all months from Jul 15 onward.
- **Trigger**: Cash flow analysis when user is ready to commit to a re-schedule date.

### TODO-12: Voxbone channel-mix audit (6 months) — basis for proper id 1 calibration
- **Status**: id 1 was reverted to day 1 (original baseline) on 2026-05-08 after the day 24 change was found provably wrong (CEO clarified "Voxbone is paid before the 10th"). Day 1 is provisional pending this audit.
- **Data sources**: 
  - Bank CSV history for direct Voxbone payments (account 4010 in Fortnox, supplier Bandwidth/Voxbone)
  - Utlägg batches (Henrik AMEX line items containing Voxbone in `~/Downloads/Accountant_Bundle_*` archives)
- **What to compute**: For each of the last 6 months (Nov 2025 - Apr 2026):
  1. Did Voxbone payment go via direct bank or via utlägg? (Identifying field: presence of `GOOGLE/VOXBONE/BANDWIDTH` in Nordea CSV vs presence in expense bundle line items)
  2. If direct: which day-of-month did it land in Nordea?
  3. If utlägg: which day did the utlägg reimbursement land?
- **Decision rule (pre-committed)**:
  - If 4+ of 6 months show direct payment within day 1-9 → keep id 1 day=1, amount unchanged
  - If 4+ of 6 months show utlägg path with median day 28-30 → restructure id 1 to day=28 (utlägg-anchored) OR split into "Voxbone direct" + "Voxbone utlägg deferral" entries
  - If mixed (no clear majority) → keep day 1 baseline, document the variability
- **Owner**: Henrik or future cash-flow analyst session
- **Trigger date**: end of October 2026 (= 6 months post-revert with consistent post-fix data)
- **Effort**: 1 hour investigation + 5-step process if structural change needed

### TODO-9: Mangold (id 51) first invoice
- **Status**: Recurring entry exists at 12,500 SEK day 15 placeholder. Day_of_month and exact amount unknown until first invoice.
- **Action when invoice lands**: Update id 51 amount + day_of_month via 5-step process
- **Trigger**: When user receives first invoice from Mangold (liquidity guarantee provider)

## P3 — Recurring process (calendar-based)

### TODO-10: Quarterly forecast recalibration cycle
- **Cadence**: Quarterly (next: ~early August 2026 after Q2 close)
- **Tasks**:
  1. Run TODO-2 drift detection (when shipped) to surface variances
  2. Update Calibration Registry with fresh P&L vs model snapshot
  3. Address any new ⚠/❌ entries via 5-step process
  4. Verify VAT day-12 netting model held (Q1 2026 was first quarter using new model)
  5. Verify India tranche split distribution still matches Padma's actual cycle
- **Owner**: Henrik or future cash-flow analyst session

---

## Status board (snapshot 2026-05-08 EOD)

| TODO | Priority | Status | Blocked by |
|---|---|---|---|
| TODO-1 PSP fees CR ship | P0 | Premise confirmed; revision pending | — |
| TODO-2 Drift detection enhancement | P0 | Tasks defined | TODO-1 |
| TODO-3 Module docstring | P0 | Folded into TODO-1 | TODO-1 |
| TODO-4 Google Adwords 2× gap | P1 | Investigation needed | — |
| TODO-5 Styrelsearvoden 2.8× gap | P1 | Investigation needed | — |
| TODO-6 META+Bing in SEB Kort | P1 | Verification needed | — |
| TODO-7 India 766K vs 864K | P1 | Decision needed | — |
| TODO-8 4xxx COGS items explicit | P1 | Decision needed | — |
| TODO-9 Mangold first invoice | P2 | Waiting on external trigger | First invoice |
| TODO-10 Quarterly recalibration | P3 | Future cadence | Calendar (~Aug 2026) |

## Resolved this session (2026-05-08) — for context

- B1, B2, B5: Skill documentation (Model Overview, Calibration Registry, First-time checklist) ✓
- A2: India tranches split (id 37 → ids 54/55/56) ✓
- A3: Bambora calibration analyzed (no change needed) ✓
- A4: Voxbone channel mismatch (id 1 day 1 → 24 + descriptions) ✓
- A6: Bank fees calibration (id 4 5K → 7K) ✓
- A1: PSP fees journal trace (gross-revenue confirmed) ✓
