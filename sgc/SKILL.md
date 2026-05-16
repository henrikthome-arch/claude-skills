---
name: sgc
description: Hantera bokföring, årsredovisning, deklaration och bolagsadministration för Swedish General Consulting AB (556071-0229). Använd vid allt arbete med SGC:s ekonomi, bokslut, Skatteverket eller bolagspapper.
argument-hint: "[bokslut | deklaration | faktura | stämma | status]"
---

**DIRECTORY GUARD**: This skill is for Swedish General Consulting AB. If the current working directory does NOT contain `SGC`, STOP immediately and tell the user: "This skill is for SGC only. Current directory: [cwd]". Do NOT proceed.

Du hjälper **Henrik Thomé** (Carl Henrik Thomé, 670105-1036) att hantera alla ekonomiska och administrativa ärenden för hans helägda bolag **Swedish General Consulting AB**.

## Single source of truth

Vid varje sessionsstart, läs igenom dessa tre filer för att förstå nuläget:

| Fil | Vad |
|-----|-----|
| [COMPLIANCE.md](COMPLIANCE.md) | Legala krav, format, riskbedömning |
| [KALENDER.md](KALENDER.md) | Alla deadlines och återkommande kontroller |
| [CHECKLISTA.md](CHECKLISTA.md) | Konkreta uppgifter som ska bockas av |

**När användaren säger "vad är status?" eller "vad ska göras?" — utgå alltid från dessa filer.**

**När en uppgift slutförs:** uppdatera CHECKLISTA.md med `[x] YYYY-MM-DD` direkt.

**Inlämningsformat valt:** PDF manuellt (inte iXBRL). Stämmer med KALENDER.md.

## Automatisk månadskoll (remote agent)

En remote-agent kör den 15:e varje månad och rapporterar kommande SGC-deadlines:
- **URL:** https://claude.ai/code/routines/trig_01DZFZVZCXXvCgmmGXuNfHgf
- **Schedule:** `0 7 15 * *` UTC = 09:00 sommartid / 08:00 vintertid Europe/Stockholm
- **Modell:** claude-sonnet-4-6
- **Skapad:** 2026-04-30
- Agenten har ingen filåtkomst — generisk påminnelse baserad på inbäddade deadline-regler

---

## Bolagsuppgifter

| Uppgift | Värde |
|---------|-------|
| **Firma** | Swedish General Consulting Aktiebolag |
| **Org.nr** | 556071-0229 |
| **Registrerat** | 1960 |
| **Säte** | Nacka kommun, Stockholms län |
| **Adress** | Framnäsbacken 1 LGH 1201, 171 66 Solna |
| **Räkenskapsår** | 1 maj – 30 april (brutet) |
| **Aktiekapital** | 100 000 kr (1 000 aktier) |
| **Reservfond** | 1 900 kr |
| **Ägare** | Henrik Thomé — 1 000 av 1 000 aktier (100%) |
| **Styrelse** | Carl Henrik Thomé (ordinarie + VD), Carl Erik Axel Thomé (suppleant) |
| **Revisor** | Ingen (enligt bolagsordning) |
| **Bifirma** | Epivo (under registrering mars 2026) |
| **F-skatt** | Ja |
| **Kontoplan** | EUBAS97 |
| **Redovisningsprincip** | K2 — BFNAR 2016:10 (Årsredovisning i mindre företag) |

### K2-begränsningar att känna till

- **Egenupparbetade immateriella tillgångar får INTE aktiveras** under K2 (kapitel 10). Utvecklingskostnader (t.ex. OpenRouter AI-API för Epivo) måste kostnadsföras direkt. Byte till K3 krävs för att aktivera.
- Komponentavskrivning krävs inte
- Uppskjuten skatt redovisas inte

### Verksamhet (ny bolagsordning 2026-03-27)

Bolaget ska bedriva utveckling, försäljning och drift av digitala utbildningsplattformar och AI-baserade läromedel, bedriva och förmedla konsulttjänster inom telekommunikation, digitala medier och informationsteknologi, förvalta fast och lös egendom, samt bedriva därmed förenlig verksamhet.

---

## Redovisning — In-house fr.o.m. RÅ 2025/2026

**Petra Kratz (Kratz Redovisning) har lagt ner verksamheten.** SGC sköter all redovisning själv från och med räkenskapsår 2025/2026.

### Vad som nu görs internt

| Område | Tidigare | Nu |
|--------|----------|-----|
| Löpande bokföring | Petra/Spiris | YAML-journal → SIE4 |
| Bokslut | Petra | Henrik + Claude |
| Årsredovisning | Petra | Henrik + Claude |
| Inkomstdeklaration 2 | Petra | Henrik + Claude |
| SIE4-export | Spiris | `scripts/bokforing.py` |

### Praktiska konsekvenser

- **Inga fler arvoden** till Petra (var 6 000 kr/år upplupet, ~9 100 kr fakturerat 2024/2025)
- **Konto 2990** (upplupna kostnader) på 6 000 kr per 2025-04-30 ska reverseras
- **Verktyg som behövs:**
  - YAML-bokföringen (redan på plats)
  - Mall/process för K2-årsredovisning (att bygga)
  - Mall/process för INK2 (att bygga)
- **Bolagsverket digital inlämning:** årsredovisning.bolagsverket.se (XBRL-format)
- **Skatteverket digital INK2:** via skatteverket.se eller fil-uppladdning (SRU-format)

### Arvskifte från Petra
- Sista SIE-fil från Spiris: 2024/2025 (`20240501-20250430 (4).se`)
- Inga fler SIE-filer kommer levereras
- Befintlig kontoplan (EUBAS97) bevaras
- Ingående balanser per 2025-05-01 är fastställda och korrekta

---

## Grundprinciper för bokföring

1. **Banken är master** — varje transaktion i SEB-kontoutdraget = en verifikation
2. **Utlägg (privat betalda)** bokförs separat: debet kostnadskonto, kredit 2893
3. **Ränta på lån Henrik** bokförs först vid utbetalning (kontantprincipen), inte som upplupen kostnad
4. **Avprickning** — alla banktransaktioner prickas i `avprickning_seb.yaml`
5. **USD/EUR-kostnader** omräknas till SEK med dagskurs på fakturadatum

---

## Mappstruktur

```
~/Library/CloudStorage/Dropbox/SGC/
├── scripts/
│   └── bokforing.py              # YAML→SIE4 bokföringsverktyg
├── Financials/
│   ├── YYYY YYYY/                # Per räkenskapsår (t.ex. "2025 2026")
│   │   ├── bokforing_2025.yaml   # Bokföringsjournal (YAML-mellanformat)
│   │   ├── avprickning_seb.yaml  # Avprickning banktransaktioner
│   │   ├── utlagg_henrik.yaml    # Sammanställning privata utlägg
│   │   ├── Låneavstämning Henrik Thomé 2025.md
│   │   ├── SEB kontoutdrag/      # Bank CSV + PDF
│   │   ├── Fakturor/             # Utställda kundfakturor
│   │   ├── Receipts/             # Kvitton (OpenRouter, Render, Cloudflare etc.)
│   │   ├── Felplacerade/         # Filer som inte tillhör SGC
│   │   └── Skatteverket/
│   ├── Lån Henrik Thomé/         # Historisk lånesammanställning (Excel)
│   └── Självdeklarationer/
├── Bolagspapper/
│   ├── Registreringsbevis/
│   ├── Bolagsstämmor/
│   └── Bolagsordning/
├── Avtal/
└── Skatteverket/
```

---

## Verksamhetsprojekt inom SGC

### Epivo (epivo.ai)
Digitala utbildningsplattformar och AI-baserade läromedel. Registreras som bifirma.
- Domäner: epivo.ai, epivo.academy
- Varumärke: EUIPO-registrering pågår

### Volos School (volos.school)
Internationell skola i Volos, Grekland.
- Backend hostad på Render
- Domän: volos.school (Cloudflare)

---

## Intäktsströmmar

### 1. Google Adsense (Karima Fitness)
Intäkter från **Karimas YouTube-kanal "Karima Fitness"**. Adsense-kontot är kopplat till SGC, utbetalas till SEB.
- Konto: 3999 (Övriga rörelseintäkter)
- Frekvens: ca varannan månad, ~5 000-7 000 kr/gång
- Bokförs: vid insättning på SEB (banken är master)

### 2. Räntefakturor till Sonetel AB (historiskt)
Lån SGC→Sonetel reglerades helt under 2024/2025. Per 2025-04-30: 0 kr i fordran.
Inga räntefakturor under 2025/2026.

---

## Kostnader — privata utlägg (Henrik betalar med eget kort)

Sammanställning i `utlagg_henrik.yaml`. Bokförs: debet kostnadskonto, kredit 2893.

### Återkommande leverantörer

| Leverantör | Tjänst | Projekt | Konto | Valuta |
|------------|--------|---------|-------|--------|
| **OpenRouter** | AI API-anrop | Epivo | 5420 | USD |
| **Render** | Hosting (backend) | Volos School | 5420 | USD |
| **Cloudflare** | Domänregistrering | Epivo/Volos | 6991 | USD |
| **Carrd** | Webbsida | Epivo | 5420 | USD |
| **Deepgram** | Speech-to-text API | Epivo | 5420 | USD |
| **EUIPO** | Varumärkesregistrering | Epivo | 6991 | EUR |

### Kvitton per leverantör

- **OpenRouter:** openrouter.ai/settings/credits → "Get invoice"
- **Render:** dashboard.render.com → Billing → Invoice History → "..." → Download
- **Cloudflare:** dash.cloudflare.com → Billing → Invoices

### Hårdvara (konto 5410, svenska kvitton med moms)

| Datum | Leverantör | Beskrivning | Inkl moms | Exkl moms | Moms 25% |
|-------|-----------|-------------|-----------|-----------|----------|
| 2025-11-18 | Inet | PNY RTX 5070 Ti GPU 16GB | 9 190 | 7 352 | 1 838 |
| 2025-12-01 | Elgiganten | LG 65" C5 Pro OLED TV + väggfäste | 21 480 | 17 184 | 4 296 |
| 2025-12-19 | Kjell & Co | Motorized TV Mount + TP-Link wifi-repeater | 2 868 | 2 294 | 574 |
| 2025-12-26 | Webhallen | Seagate 5TB HDD + Andersson högtalare | 1 798 | 1 438 | 360 |
| 2025-12-27 | Kjell & Co | USB-C RJ45 hub | 450 | 360 | 90 |

Alla betalda med Henriks kort ****7452.

---

## Lån Henrik Thomé → SGC

### Villkor
- Ränta: **SLR per 30 nov föregående år + 1 procentenhet**
- 2025: 2,96% (SLR 1,96% + 1%)
- 2026: 3,55% (SLR 2,55% + 1%)
- Princip: **Ränta bokförs och deklareras först vid utbetalning** (kontantprincipen)
- Konto: 2393 (Lån från närstående, långfristig del)

### Skuldutveckling RÅ 2025/2026

| Datum | Händelse | Belopp | Saldo |
|-------|----------|--------|-------|
| 2025-05-01 | Ingående skuld | — | 757 414 |
| 2025-05-02 | Amortering | -8 000 | 749 414 |
| 2025-10-02 | Amortering | -5 500 | 743 914 |
| 2025-12-16 | Nytt lån | +6 500 | 750 414 |
| **2026-04-30** | **Utgående skuld** | — | **750 414** |

Ingen ränta utbetald 2025/2026 → ingen räntekostnad bokförd.
Fullständig avstämning: `Låneavstämning Henrik Thomé 2025.md`

### Övriga långfristiga skulder (konto 2390)
Lån från Sonetel-aktieägare för aktieköp. IB: 1 850 000, tillägg 300 000 under året = UB: 2 150 000.

### Kortfristiga skulder Henrik (konto 2893)
IB: 492 520. Ökar med utlägg under året.

---

## Bankkonto SEB

- SEB Företagskonto — alla bolagets transaktioner
- Kontoutdrag: CSV (semikolonseparerad, UTF-8 med BOM)
- Saldo normalt lågt (6 162 kr per 2026-03-26)

### Vanliga transaktionsmönster

| Mönster i SEB-text | Kontering |
|---------------------|-----------|
| BANKTJÄNSTER / 100XXXXXXXXX | 1930 ↔ 6570 (bankkostnader) |
| DEPÅAVGIFT | 1930 ↔ 6570 (bankkostnader) |
| GOOGLE IRELA | 1930 ↔ 3999 (Adsense, Karima Fitness) |
| SK5560710229 | 1930 ↔ 2650 (momsåterbetalning) |
| SKATTEVERKET | 1930 ↔ 1630 (skattekonto) |
| KRATZ REDOVISNING AB | 1930 ↔ 6530 + 2641 (redovisning + moms 25%) |
| LÅN HENRIK | 1930 ↔ 2393 (nytt lån, inbetalning) |
| LÅN ÅTER | 1930 ↔ 2393 (amortering, utbetalning) |
| FÖR AKTIEKÖP | 1930 ↔ 2390 (lån för aktieköp) |
| PMJ FASTIGHETER AB | 1930 ↔ 1330 (aktieköp Sonetel) |
| BG NNN-NNNN | Okänd avsändare — se nedan |

### Identifiera okänd BG-inbetalning

Om en transaktion endast har bankgironummer (t.ex. `BG 269-0147`):

1. Logga in på **SEB Internetbanken**
2. Gå till transaktionsdetaljerna för posten
3. Klicka på **"Bg-detalj"** (PDF-rapport från Bankgirot)
4. Rapporten visar avsändarens namn, bankgironummer och betalningsreferens
5. Ladda ner PDF, spara i `Receipts/` med beskrivande filnamn

**Krediteringar/återbetalningar** från en leverantör bokförs som motkonto till ursprungskostnaden (ej som intäkt). Exempel: Kratz återbetalar 90 kr → debet 1930, kredit 6530.

---

## Bokföring — YAML-mellanformat + SIE4-export

### Verktyg

Script: `scripts/bokforing.py`

```bash
# Importera befintlig SIE4-fil → YAML
python3 scripts/bokforing.py import-sie "path/to/file.se"

# Generera SIE4 från YAML
python3 scripts/bokforing.py generate-sie "path/to/journal.yaml"

# Validera
python3 scripts/bokforing.py validate "path/to/journal.yaml"

# Resultaträkning / Balansräkning
python3 scripts/bokforing.py resultat "path/to/journal.yaml"
python3 scripts/bokforing.py balans "path/to/journal.yaml"
```

### Nyckelfiler innevarande RÅ

| Fil | Innehåll |
|-----|----------|
| `bokforing_2025.yaml` | Bokföringsjournal (alla verifikationer) |
| `avprickning_seb.yaml` | Avprickning: varje SEB-rad → verifikation + kontering |
| `utlagg_henrik.yaml` | Sammanställning alla utlägg Henrik betalt privat |
| `Låneavstämning Henrik Thomé 2025.md` | Skuldutveckling + ränteberäkning |

### SIE4-filer

Filformat: PC8 (CP437-encoding).

```python
with open('file.se', 'r', encoding='cp437') as f:
    content = f.read()
```

### SEB CSV-format

```
Bokförd;Valutadatum;Text;Typ;Insättningar/uttag;Bokfört saldo
```
Encoding: UTF-8 med BOM (`utf-8-sig`). Decimalavgränsare: komma. Tusenseparator: punkt.

---

## Årsredovisning — process (K2, in-house)

### Tidsplan per räkenskapsår (1 maj – 30 april)

| Deadline | Åtgärd |
|----------|--------|
| 30 april | Räkenskapsårets slut — sista SEB-utdrag laddas ner |
| Maj | Slutför YAML-journal, kör bokslutsposter |
| Juni–juli | Upprätta ÅR (förvaltningsberättelse, RR, BR, noter) |
| September | Sista granskning + signering |
| Oktober (senast 31 okt) | Årsstämma |
| November | ÅR + stämmoprotokoll till Bolagsverket |
| 1 nov/1 dec | Inkomstdeklaration 2 till Skatteverket |

### Bokslutsposter att hantera

- Reversera upplupen kostnad Petra (6 000 kr på 2990) — inte längre relevant
- Avskrivningar (ev. på hårdvara om aktiveras som anläggningstillgång)
- Skatteberäkning (20,6%) → bokföra på 8910 + 2510
- Omföring årets resultat (8999 → 2099)
- Ingående balanser nästa år: omföring 2099 → 2091

### ÅR-struktur (K2 / BFNAR 2016:10)

1. **Förvaltningsberättelse**
   - Allmänt om verksamheten
   - Flerårsöversikt (5 år)
   - Förändringar i eget kapital
   - Resultatdisposition (förslag till stämman)
2. **Resultaträkning**
3. **Balansräkning**
4. **Noter**
   - Not 1: Redovisningsprinciper (BFNAR 2016:10)
   - Not 2: Medelantalet anställda (0)
   - Not 3: Andelar i intresseföretag (Sonetel)
   - Not 4: Andra långfristiga fordringar
5. **Underskrifter** (Henrik som VD/ordinarie)
6. **Fastställelseintyg**

### Inlämning till Bolagsverket

**Valt format: PDF (manuell inlämning)** via årsredovisning.bolagsverket.se. Avgift: 0 kr.

Filer som ska bifogas:
- ÅR (PDF — genereras från markdown-mall)
- Fastställelseintyg (PDF, signerat av Henrik)
- Stämmoprotokoll (PDF, signerat)

iXBRL-inlämning är inte aktuell — formatet är komplext och PDF accepteras.

---

## Deklaration — Inkomstdeklaration 2 (aktiebolag)

### Tidsplan

| Deadline | Åtgärd |
|----------|--------|
| 1 juli | Deklarationsdag (grundregel) |
| 1 november | Med anstånd (papper) |
| 1 december | Med anstånd (digitalt) |

### Förfarande (in-house)

Bolagsskatt: 20,6%. SGC har F-skatt.

**Två alternativ:**

**A) SRU-fil (rekommenderas, kräver att SRU-generator byggs)**
1. Generera `INFO.SRU` + `BLANKETTER.SRU` från YAML-bokföringen
   - Mappar konton → SRU-fältkoder enligt SKV 269 (Tekniska beskrivningen)
   - Inkluderar bilaga 2A (Räkenskapsschema) + 2B (Skattemässiga justeringar)
2. Logga in på skatteverket.se med BankID
3. Ladda upp SRU-filerna under "Inkomstdeklaration 2"
4. Verifiera, signera, lämna in

**B) Webbformulär (manuellt)**
1. Logga in på skatteverket.se med BankID
2. Fyll i fält för fält baserat på fastställd ÅR
3. Beräkna skatt på resultat före skatt × 20,6%
4. Signera och lämna in

### Underskott rullas framåt

Vid förlust (som RÅ 2025/2026 ~91 kSEK): underskottet rullas framåt utan tidsbegränsning och kvittas mot framtida vinster. Inga ägarförändringar planeras → ingen beloppsspärr/koncernbidragsspärr aktiveras.

### Preliminär skatt (F-skatt)

- Debiteras månadsvis baserat på föregående års resultat
- Vid lågt/negativt resultat: ansök om **nedsättning av prelskatt** via skatteverket.se
- Per 2025-04-30: skatteskuld 216 kr (i princip noll)

---

## Koppling till Henriks privata deklaration

SGC-lånet påverkar Henriks Inkomstdeklaration 1:
- **K10-blankett** lämnas varje år (förenklingsregeln, sparat utdelningsutrymme)
- **Ränteintäkt från SGC** (ruta 7.2) — bara faktiskt utbetald ränta (kontantprincipen)
- **2025:** Ingen ränta utbetald → 0 kr att deklarera
- Se `/deklaration`-skillen för fullständig deklarationsprocess

---

## Status RÅ 2025/2026 (avslutat 2026-04-30)

### Resultat
- Adsense-intäkter (Karima Fitness): 12 245 kr
- Kostnader (inkl. utlägg): -103 010 kr
- **Resultat före skatt: -90 765 kr**
- Soliditet: 43,7%

### Banktransaktioner
- 27 transaktioner i SEB, 26 prickade
- Oklassificerad: BG 269-0147 (90 kr, 2026-01-26)

### Saknade kvitton
- Render mars 2026 (pending — fakturera ~3 april)

För full status och nästa steg, se [CHECKLISTA.md](CHECKLISTA.md).

---

## Verktyg

| Verktyg | Syfte | Status |
|---------|-------|--------|
| `scripts/bokforing.py` | YAML→SIE4 bokföring | ✓ Klar |
| `scripts/sru_generator.py` | INK2 SRU-fil → Skatteverket | ✓ Klar (verifierad 2026-05-06) |
| `scripts/generate_ar.py` | K2 Årsredovisning PDF → Bolagsverket | ✓ Klar (verifierad 2026-05-06) |
| Stämmoprotokoll-mall | Bolagsstämma | ⏳ |
| Fastställelseintyg-mall | Bolagsverket | ⏳ |

### Användning av nya verktygen

**SRU-generator (INK2 till Skatteverket):**
```bash
cd ~/Library/CloudStorage/Dropbox/SGC
python3 scripts/sru_generator.py \
    --journal "Financials/2025 2026/bokforing_2025.yaml" \
    --output "Financials/2025 2026/INK2 deklaration/"
```
Genererar `INFO.SRU` + `BLANKETTER.SRU` i ISO-8859-1, CRLF.
Blankettkod-format: `INK2-{år då RÅ slutar}{period}`. För SGC RÅ 25/26: `INK2-2026P1`.
Spec: `scripts/specs/SRU_TECHNICAL_DOCS.md`. Auktoritativa SKV-fältkoder i `scripts/specs/SKV_2025P4/`.

**ÅR-generator (Bolagsverket):**
```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 scripts/generate_ar.py \
    --journal "Financials/2025 2026/bokforing_2025.yaml" \
    --previous-sie "Financials/2024 2025/.../20240501-20250430 (4).se" \
                   "Financials/2023 2024/Financial/SIE fil/20230501-20240430 (1).se" \
    --output "Financials/2025 2026/Bokslut/Årsredovisning 2026-04-30.pdf" \
    --stämma-datum 2026-10-15
```
Genererar K2-ÅR PDF med flerårsöversikt. Inkluderar Not 5 (närstående) och Not 6 (säkerheter) per ÅRL.
Mall: `scripts/ar_template.html` + `scripts/ar_template.css`.

**Beroenden:** `pip install jinja2 weasyprint babel openpyxl xlrd PyYAML` + `brew install pango`.

---

## Historisk flerårsöversikt

| År | Nettoomsättning | Resultat efter fin.poster | Soliditet |
|----|-----------------|--------------------------|-----------|
| 2025/2026 | 12 245 (Adsense) | -90 765 (prel.) | 43,7% (prel.) |
| 2024/2025 | 0 | -13 540 | 47,4% |
| 2023/2024 | — | 1 063 | 64,6% |
| 2022/2023 | -1 | 235 | 58,9% |
| 2021/2022 | — | -7 387 | 53,9% |

---

## Kommandon

| Kommando | Vad det gör |
|----------|-------------|
| `/sgc status` | Sammanfatta nuläget från CHECKLISTA + KALENDER |
| `/sgc bokslut` | Hjälp med bokslutsarbete (RÅ-stängning, ÅR) |
| `/sgc deklaration` | Hjälp med INK2 (SRU-generering eller webbformulär) |
| `/sgc faktura` | Skapa ny kundfaktura |
| `/sgc stämma` | Upprätta stämmoprotokoll |
| `/sgc utlägg` | Lägg till privat utlägg i utlagg_henrik.yaml |

---

$ARGUMENTS
