---
name: familjebudget
description: Hantera familjebudget 2026 med scenarioanalys för flytt till Spanien. Uppdatera inkomster, utgifter, scenarion, och generera HTML-dashboard.
argument-hint: "[åtgärd, t.ex. 'lägg till scenario', 'uppdatera hyra', 'generera html']"
---

**DIRECTORY GUARD**: Arbetskatalog är `/Users/henrik/Library/CloudStorage/Dropbox/Privat/Ekonomi/`.

Du hanterar familjebudgeten för **Henrik Thomé** och **Karima** (2026).

## Filer

| Fil | Syfte |
|-----|-------|
| `familjebudget_2026.py` | Huvudfil: all data (inkomster, utgifter, tillgångar, skulder) + scenariofunktioner + terminalutskrift |
| `generate_budget_html.py` | Genererar HTML-dashboard från data i huvudfilen. Kör: `python3 generate_budget_html.py` |
| `familjebudget_2026.html` | Genererad HTML-dashboard (öppnas automatiskt vid körning) |

**VIKTIGT:** Scenarion definieras i BÅDA filerna (`familjebudget_2026.py` och `generate_budget_html.py`). Vid ändring av scenarion, uppdatera alltid båda.

## Familjemedlemmar

- **Henrik** - bruttolön 693 000 (57 750/mån, Sonetel AB, vd; lönebesked okt 2026), skatt 162 516 (tabell 30), YouTube 12 000/år (≈ 1 000 kr/mån, nov 2026)
- **Karima** - bruttolön 630 000 (52 500/mån, Sonetel AB, assistent; lönebesked okt 2026), skatt 141 672 (tabell 31), barnbidrag/underhåll 0 (underhåll Gabriel upphör; var 24 000)
- Totalt 110 250 kr/mån brutto (`LÖN_TOTAL` = 1 323 000). `scenario_spanien` har `flyg_sverige_sek=24_000` (2 000 kr/mån) och `besparing_som_lön=True` (Sonetels sparade arbetsgivaravgift till den som har lön över taket) som standard.
- **Jodie** (Henriks dotter) - fritids, kläder, övriga
- **Gabriel** (17, Karimas son) - bor i Sverige vid Spanien-flytt
- **Israa** (21, Karimas dotter, studerar) - bor i Sverige, bara matkostnad bekostas
- **Erik** (Henriks son) - bara mobiltelefon
- **Amir** - bara mobiltelefon (gemensamma fasta)

## Scenariostruktur: Spanien-flytt

Grundpremiss vid alla Spanien-scenarion:
- **Henrik + Karima + Jodie** flyttar till Costa del Sol
- **Gabriel + Israa** bor kvar i BRF Framnäsbacken i Sverige
- **BRF och bolån behålls** - alltid, i alla scenarion
- **Bil Sverige säljs** vid flytt (`behåll_bil_sverige=False`, beslut okt 2026). Försäljningssumman är inte medräknad.
- Två parallella hushåll: Sverige (Gabriel+Israa) + Spanien (H+K+Jodie)

### Kostnadssplit
- **Sverige (kvarstår):** BRF-avgift, bolåneränta, Gabriel (busskort/månadspeng/kläder/discord/klippning), mat Gabriel+Israa (40% av matbudget = 2/5 pers), Erik
- **Spanien (nytt):** Hyra, el, vatten, internet, mat (H+K+Jodie), skola Jodie, sjukförsäkring, transport (bil+kollektivt), Karima personligt (justerat), Henrik personligt (justerat), Jodie (kläder+övriga, ej fritids)
- **Gemensamt:** Mobiler, Grekland (bil + hus)

### Scenariovarianter (mars 2026)

Alla scenarion har samma grundparametrar:
- Hyra: 1 100 €/mån
- El: 100 €, Vatten: 40 €, Internet: 40 €
- Bil drift: 200 €/mån (liten begagnad bil, nov 2026; inköp ~8 000 € ej med), Kollektivtrafik: 50 €/mån
- Sjukförsäkring: 0 €/mån (vård via spansk socialförsäkring; var 200 € före okt 2026)
- Familjen räknas som utflyttad (>1 år): `spansk_socialförsäkring=True`, `sv_barnbidrag_jodie=False`
- EUR/SEK: 11,0 (Riksbanken 31 okt 2026; tidigare 11,5)

Skillnader:

| SC | Skola | Pris/mån | Mat €/mån | Skatt | Lunch ingår? |
|----|-------|----------|-----------|-------|-------------|
| 1 | Internationell | 750 € | 600 | IRPF ~29% | Nej |
| 2 | Svenska Skolan | 680 € | 550 | IRPF ~29% | Ja |
| 3 | Beckham + intl. | 750 € | 600 | Beckham 24% | Nej |
| 4 | Offentlig | 100 € | 600 | IRPF ~29% | Nej |
| 5 | Beckham + offentlig | 100 € | 600 | Beckham 24% | Nej |
| 6 | Beckham + Sv. Skolan | 680 € | 550 | Beckham 24% | Ja |
| 7 | B+SvSk KÖPA (utökat sv. lån) | 680 € | 550 | Beckham 24% | Ja, äger bostad |
| 8 | B+SvSk KÖPA spanskt bolån | 680 € | 550 | Beckham 24% | Ja, äger bostad |
| 9 | Plan nov 2026 (Beckham, en lön) | 575 € (statsbidrag) | 550 | Beckham 24% | Ja. Hela lönen + `arbetsgivarbesparing_sek(LÖN_TOTAL, 1.0)` (≈ 17 400 €) till Henrik, Karima 0, hyra 1 450 €, `hyresintäkt_sverige=60_000` |
| 10 | Plan nov 2026 utan Beckham | 575 € | 550 | IRPF | Ja. Delad lön 693k/630k, hyra 1 450 €, hyresintäkt 60 000 |
| 11 | Utan Beckham, 85 % Henrik | 575 € | 550 | IRPF | Ja. 85/15 + `arbetsgivarbesparing_sek()` som lön, hyra 1 450 €, hyresintäkt 60 000 (bästa utan Beckham) |
| 12 | Sålt i Sverige, köpt i Spanien (Beckham) | 575 € | 550 | Beckham 24% | `sälj_sv_lägenhet=True`, köpris 300 000 € kontant, comunidad 150/IBI 60/försäkring 40/sopor 15 €, underhåll 1 %, ingen hyra från Israa, `alternativränta_pct=0`. Gabriels boende 6 000 kr/mån, svensk hemförsäkring bort. Engångsbelopp i `sälj_köp_engång()` (uppskov räknat). Ekonomisk syn: köpkostnad + mäklare/skatt Sverige fördelat 6 år |
| 13 | Som 12 utan Beckham, 85 % Henrik | 575 € | 550 | IRPF | |

### Skatt Spanien
- **IRPF progressiv:** 19%–47% (`IRPF_BRACKETS`, stat + Andalucía sammanslagna med Andalucías egna skiktgränser 13 000/21 100 €), med 2 000 € arbetsavdrag och mínimo personal (statligt 5 550 + Andalucía 5 790, à 9,5 %) och mínimo descendiente 2 400 € à 19 % (delas om båda har inkomst). Tillagt nov 2026; kontroll ≈ 23,5 % effektivt på 57 400 € (guiafiscal: 24,3 % på 60 000 €)
- Med delad lön ger Beckham ingen vinst (SC 6 ≈ SC 2). Beckham lönar sig bara med en lön (SC 9).
- **Beckham-lagen:** Platt 24% i 6 år för nyinflyttade, 47 % över 600 000 €
- **`spanien_tillägg()`** (alla Spanien-scenarier, både .py-filerna): skatterådgivare 125 €/mån; Beckham + ägt hem: skatt på schablonhyra (omstridd); vid försäljning: Gabriels boende och mäklare + skatt fördelat 6 år
- Funktionen `spansk_skatt(brutto_sek, beckham=False, avdrag_sek=0)` beräknar per person
- **Socialavgift (anställd):** 6,5 % på lön (ej YouTube), tak 5 101,20 €/mån (2026), plus anställds 1/6 av solidaritetsavgiften över taket, via `spansk_socialavgift()`. `arbetsgivarbesparing_sek()` drar av arbetsgivarens 5/6 av solidaritetsavgiften utöver vad 50/50 ger, och delar med (1 + marginalsats × 5/6). `reduktion_arbetsinkomst_eur()` = art. 20 för låga löner. Sonetel har ingen ITP. Dras av före IRPF men inte under Beckham. Arbetsgivarens del ligger utanför hushållsbudgeten.

### Boende: äga vs hyra
- Hyra: 1 100 €/mån (SC 1-6)
- Bil Spanien: `bil_drift_eur=280` (drift 200 + värdeminskning 80, 2 nov 2026)
- Äga: comunidad 150 + IBI 60 + försäkring 40 + basura 15 = 265 €/mån + ev. bolån (IBI sänkt från 100 efter granskning 2 nov 2026)
- Köpkostnad ~250 000 EUR + 10% avgifter = ~275 000 EUR
- SC 7: Finansieras via utökat svenskt bolån 2 012 500 SEK (= 175k EUR × 11,5) @ 2,9%
- SC 8: Spanskt bolån 175k EUR @ 3,75% = 900 €/mån
- Båda lånar samma belopp (175k EUR), bara i olika länder → samma total skuld
- **Köpkalkyl (SC 7-8, `köpris_eur=250_000`):** köpkostnad 10 % (25k €) fördelas över 6 år som utgift, och utebliven ränta 2,5 % på kontantinsatsen (100k €) räknas som utgift. Då blir hyra (SC 6) bättre än köp.

### Svenska Skolan Costa del Sol (Fuengirola) — vald skola (Marbella utesluten nov 2026)
- 2026/27 åk F–6: 8 050 €/år, **lunch och läromedel ingår** → mat_spanien 550 €/mån
- Medlemskap 100 €/familj/år; ansökningsavgift 1 000 € (engång)
- Statsbidrag (Skolverket): −1 250 €/år → 575 €/mån; utan: 680 €/mån. Oklart om statsbidrag ges vid permanent flytt med distansjobb
- Källa: skolan.es/skolavgifter-2026-2027
- Projektmapp med underlag: `Dropbox/Spanien/` (memo: `01_Economy/Spain_economics_memo.md`)

## Arbetsprocess

1. **Läs** `familjebudget_2026.py` för aktuell data
2. **Gör ändringar** i `familjebudget_2026.py` (data + scenarion)
3. **Spegla scenarioändringar** i `generate_budget_html.py`
4. **Kör** `python3 generate_budget_html.py` för att generera och öppna HTML
5. **Verifiera** terminalutskrift med `python3 familjebudget_2026.py`

## Viktiga regler

- Ändra aldrig hyra, sjukförsäkring eller andra grundparametrar för enskilda scenarion utan att användaren ber om det - dessa ska vara normaliserade
- `mat_spanien_eur` ska vara 550 för scenarion med Svenska Skolan (lunch ingår), 600 för övriga
- Grekland-kostnader (bil + hus) inkluderas alltid (`behåll_grekland=True`)
- **Bolåneränta i Spanien-scenarion: BRUTTO** (inget svenskt ränteavdrag som spansk skatteresident)
  - Befintligt bolån: 2 886 668 kr @ 2,9% = 83 713 kr/år brutto
  - I Sverige-scenariot: 58 640 kr/år netto (30% avdrag)
  - Parametern `extra_sv_bolån` lägger till belopp i SEK på befintligt bolån (SC 7 = 1 800 000)
- Israa: bara mat. Inga fika/försäkring/fritid/nöjen-kostnader
- `scenario_spanien(karima_brutto_spanien=0)` betyder ingen lön (None = standardlön)
- `hyresintäkt_sverige`: Israa + Erik betalar för lägenheten (SEK/år), ej skattad
- SC 1–8 har normaliserad hyra 1 100 €; SC 9–11 använder 1 450 € (Henriks beslut nov 2026)
- Volos-lägenheten köps EJ → 1 MSEK av likvida medel frigjorda för ev. Spanien-köp
