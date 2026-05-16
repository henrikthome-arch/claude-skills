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

- **Henrik** - bruttolön 660 000, skatt tabell 30, YouTube 24 000/år
- **Karima** - bruttolön 600 000, skatt tabell 29, barnbidrag/underhåll 24 000
- **Jodie** (Henriks dotter) - fritids, kläder, övriga
- **Gabriel** (17, Karimas son) - bor i Sverige vid Spanien-flytt
- **Israa** (21, Karimas dotter, studerar) - bor i Sverige, bara matkostnad bekostas
- **Erik** (Henriks son) - bara mobiltelefon
- **Amir** - bara mobiltelefon (gemensamma fasta)

## Scenariostruktur: Spanien-flytt

Grundpremiss vid alla Spanien-scenarion:
- **Henrik + Karima + Jodie** flyttar till Costa del Sol
- **Gabriel + Israa** bor kvar i BRF Framnäsbacken i Sverige
- **BRF, bil Sverige och bolån behålls** - alltid, i alla scenarion
- Två parallella hushåll: Sverige (Gabriel+Israa) + Spanien (H+K+Jodie)

### Kostnadssplit
- **Sverige (kvarstår):** BRF-avgift, bolåneränta, bil Sverige, Gabriel (busskort/månadspeng/kläder/discord/klippning), mat Gabriel+Israa (40% av matbudget = 2/5 pers), Erik
- **Spanien (nytt):** Hyra, el, vatten, internet, mat (H+K+Jodie), skola Jodie, sjukförsäkring, transport (bil+kollektivt), Karima personligt (justerat), Henrik personligt (justerat), Jodie (kläder+övriga, ej fritids)
- **Gemensamt:** Mobiler, Grekland (bil + hus)

### Scenariovarianter (mars 2026)

Alla scenarion har samma grundparametrar:
- Hyra: 1 100 €/mån
- El: 100 €, Vatten: 40 €, Internet: 40 €
- Bil drift: 150 €/mån, Kollektivtrafik: 50 €/mån
- Sjukförsäkring: 200 €/mån
- EUR/SEK: 11,5

Skillnader:

| SC | Skola | Pris/mån | Mat €/mån | Skatt | Lunch ingår? |
|----|-------|----------|-----------|-------|-------------|
| 1 | Internationell | 750 € | 600 | IRPF ~29% | Nej |
| 2 | Svenska Skolan | 685 € | 550 | IRPF ~29% | Ja |
| 3 | Beckham + intl. | 750 € | 600 | Beckham 24% | Nej |
| 4 | Offentlig | 100 € | 600 | IRPF ~29% | Nej |
| 5 | Beckham + offentlig | 100 € | 600 | Beckham 24% | Nej |
| 6 | Beckham + Sv. Skolan | 685 € | 550 | Beckham 24% | Ja |
| 7 | B+SvSk KÖPA (utökat sv. lån) | 685 € | 550 | Beckham 24% | Ja, äger bostad |
| 8 | B+SvSk KÖPA spanskt bolån | 685 € | 550 | Beckham 24% | Ja, äger bostad |

### Skatt Spanien
- **IRPF progressiv:** 19%–47% (brackets definierade i `IRPF_BRACKETS`)
- **Beckham-lagen:** Platt 24% i 6 år för nyinflyttade
- Funktionen `spansk_skatt(brutto_sek, beckham=False)` beräknar per person

### Boende: äga vs hyra
- Hyra: 1 100 €/mån (SC 1-6)
- Äga: comunidad 150 + IBI 100 + försäkring 40 + basura 15 = 305 €/mån + ev. bolån
- Köpkostnad ~250 000 EUR + 10% avgifter = ~275 000 EUR
- SC 7: Finansieras via utökat svenskt bolån 2 012 500 SEK (= 175k EUR × 11,5) @ 2,9%
- SC 8: Spanskt bolån 175k EUR @ 3,75% = 900 €/mån
- Båda lånar samma belopp (175k EUR), bara i olika länder → samma total skuld

### Svenska Skolan Marbella
- Terminsavgift: 4 100 €/termin med statsbidrag (Jodie kvalificerar)
- Utan statsbidrag: 5 200 €/termin
- **Lunch ingår** i avgiften → mat_spanien sänks till 550 €/mån
- Inskrivningsavgift: 1 000 € (engång)
- Fritids finns: 600 €/termin (1-2 dgr) eller 1 100 €/termin (3-5 dgr)
- Källa: svenskaskolanmarbella.com/priser-antagning

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
- Volos-lägenheten köps EJ → 1 MSEK av likvida medel frigjorda för ev. Spanien-köp
