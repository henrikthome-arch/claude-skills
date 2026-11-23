---
name: sgc
description: Hantera bokföring, årsredovisning, deklaration och bolagsadministration för Swedish General Consulting AB (556071-0229). Använd vid allt arbete med SGC:s ekonomi, bokslut, Skatteverket eller bolagspapper.
argument-hint: "[bokslut | deklaration | faktura | stämma | status]"
---

**DIRECTORY GUARD**: This skill is for Swedish General Consulting AB. If the current working directory does NOT contain `SGC`, STOP immediately and tell the user: "This skill is for SGC only. Current directory: [cwd]". Do NOT proceed.

Du hjälper **Henrik Thomé** (Carl Henrik Thomé, 670105-1036) att hantera alla ekonomiska och administrativa ärenden för hans helägda bolag **Swedish General Consulting AB**.

## Arbetsprocess — obligatorisk

**Läs [PROCESS.md](PROCESS.md) i SGC-mappen innan du färdigställer något dokument.**

Kort version: varje granskningspliktigt dokument (myndighetsinlämning, bolagshandling,
avtal, räkenskapsmaterial, beslutsunderlag) ska genomgå

1. `python3 scripts/kontroller.py` — deterministiska kontroller
2. **två oberoende granskningsagenter** med skilda lenser, spawnade parallellt
3. **≥8/10 från båda**, där 8 = kan lämnas ut utan förbehåll — annars åtgärda och kör om med nya agenter
4. utfallet noteras i `GRANSKNINGSLOGG.md`

Detta gäller utan att Henrik behöver be om det. När han säger "follow the process" är
det denna process han menar.

## Single source of truth

Vid varje sessionsstart, läs igenom dessa filer för att förstå nuläget:

| Fil | Vad |
|-----|-----|
| [PROCESS.md](PROCESS.md) | **Arbetsprocessen — granskningskravet** |
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
| **Säte** | Nacka kommun, Stockholms län (registreringsbeviset skriver "Stockholms län, Nacka kommun" — **sätet är Nacka**, Stockholm är fel) |
| **Adress** | Framnäsbacken 1 LGH 1201, 171 66 Solna |
| **Räkenskapsår** | 1 maj – 30 april (brutet) |
| **Aktiekapital** | 100 000 kr (1 000 aktier) |
| **Reservfond** | 1 900 kr |
| **Ägare** | Henrik Thomé — 1 000 av 1 000 aktier (100%) |
| **Styrelse** | Carl Henrik Thomé (ordinarie + VD), Carl Erik Axel Thomé (suppleant) |
| **Revisor** | Ingen (enligt bolagsordning) |
| **Särskilt företagsnamn** | Epivo (registrerat 2026-03-30 enligt registreringsbeviset; 2026-03-18 är EUIPO-datumet och avser varumärket). Termen *bifirma* utmönstrades 2018 — använd inte den i handlingar |
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

1. **Banken är master för bankhändelser** — varje transaktion i SEB-kontoutdraget = en verifikation
2. **KORTEN är master för utlägg** — inte kvittopärmen. Se nedan.
3. **Utlägg (privat betalda)** bokförs separat: debet kostnadskonto, kredit 2893
4. **Ränta på lån Henrik** (konto 2393) bokförs först vid utbetalning (kontantprincipen).
   **Räntan på aktieägarlånen (konto 2390) periodiseras däremot varje bokslut** — se
   avsnittet om bolagets lån nedan. Att tillämpa kontantprincipen på båda är det
   dyraste fel som gjorts i den här bokföringen
5. **Avprickning** — alla banktransaktioner prickas i `avprickning_seb.yaml`
6. **USD/EUR-kostnader** omräknas till SEK med Riksbankens dagskurs på fakturadatum

### Stäm ALLTID av utläggen mot kortutdragen (hårt lärd 2026-08-13)

Kvittosamlingen är **inte** ett tillförlitligt underlag. Vid bokslut 2025/2026 stämde
bokföringen perfekt mot banken och mot alla insamlade kvitton — och var ändå fel på tre
sätt, alla upptäckta först när kortutdragen lästes:

- **Saknade kostnader** — verkliga debiteringar utan sparat kvitto.
- **Fantomkostnader** — 16 OpenRouter-"kvitton" var omutfärdanden av redan bokförda köp
  och hade bokförts som egna kostnader, ~2 330 USD för mycket.
- **Främmande kostnader** — en Sonetel-faktura låg felnamngiven i SGC:s kvittomapp.

**Ladda ner kortutdrag för hela räkenskapsåret, för varje kort som använts**, och stäm av
post för post innan bokslutet stängs.

### Korten och vilka bolag de tillhör

| Kort | Tillhör | Var utdraget hämtas |
|------|---------|---------------------|
| SAS Amex Premium `…92000` | **Blandat** Sonetel + Epivo | americanexpress.se, PDF per månad |
| Mastercard Bankkort `…5433` | SGC | SEB internetbanken → Korttransaktioner → *Spara som en fil* (XML) |
| Handelsbanken Bankkort (MC) `****7452` | **Henriks privata kort** — SGC-köp på det är utlägg (kredit 2893), inte bolagets kort (bekräftat 2026-10-25) | Handelsbanken (Henrik) |
| SEB Mastercard `552764******8627` | **Sonetel** — rör inte | — |

AMEX-utdragen är **tvåspaltiga**. `pdftotext -layout` lägger båda spalterna på samma rad;
dela vid kolumn 90 och tolka varje halva för sig, annars läses fel belopp.

### Skattekontot hämtas separat

Ligger hos **Skatteverket**, inte SEB: Mina sidor → Skattekonto → Kontoutdrag. Utan det
går varken 1630 eller 2510 att stänga. Där syns också om F-skatt debiterats.

### Riksbankens växelkurser

```bash
curl -s "https://api.riksbank.se/swea/v1/Observations/SEKUSDPMI/2025-05-01/2026-04-30"
curl -s "https://api.riksbank.se/swea/v1/Observations/SEKEURPMI/2025-05-01/2026-04-30"
```

Kurser publiceras **endast bankdagar**. Saknas kurs på fakturadatum används närmast
föregående bankdag — dokumentera vilken kurs som använts i verifikationstexten.

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

## Utländska leverantörer och moms

Detta är det område som orsakade mest arbete i bokslutet 2025/2026. Läs hela avsnittet
innan du bokför en enda utländsk faktura.

### Omvänd skattskyldighet — huvudregeln

Tjänster från utländsk leverantör till SGC är **omvänd skattskyldighet**: säljaren
nollbeskattar, köparen redovisar både utgående och ingående moms. Nettoeffekten är noll.

```
debet kostnadskonto   SEK
kredit 2893           SEK
debet 2645            25 %   (beräknad ingående moms på förvärv från utlandet)
kredit 2614           25 %   (utgående moms omvänd skattskyldighet)
```

| Ruta | Vad |
|------|-----|
| 21 | Inköp av tjänster från **annat EU-land** (Google, Anthropic Ireland) |
| 22 | Inköp av tjänster från **land utanför EU** (OpenRouter, Render, Cloudflare, Carrd, Deepgram) |
| 30 | Utgående moms på ruta 20–24 |
| 48 | Ingående moms att dra av |

### Fällan: leverantör som debiterar svensk moms

Saknas SGC:s momsnummer på leverantörskontot behandlar många leverantörer köpet som
**B2C** och lägger på 25 % svensk moms via OSS. Då gäller **inte** omvänd skattskyldighet.

**Bokför aldrig både säljardebiterad moms och förvärvsmoms** — det blir moms två gånger.
Vid säljardebiterad moms:

```
debet kostnadskonto   netto
debet 2641            momsen
kredit 2893           brutto
```

Detta hände under 2025/2026 med **OpenRouter från 6 mars 2026** och med **Anthropic**.
Kontrollera varje kvitto: står det `0%` / `reverse charge` eller `25% incl.`?

**Åtgärden är att registrera momsnummer `SE556071022901` på varje leverantörskonto.**
Bekräftat att det stoppar momsen. Hos OpenRouter ligger fältet i Stripes checkout
(*Edit Tax ID*), inte i kontoinställningarna.

Notera också: felaktigt debiterad moms är formellt **inte avdragsgill** — rätt väg är
kreditering från säljaren. Beslut 2026-08-13 var ändå att dra av den; underlaget och
resonemanget ligger i `Financials/2025 2026/utlagg_henrik.yaml`.

### Fakturan måste namnge bolaget

För momsavdrag på köp **över 4 000 kr inkl. moms** krävs köparens namn på handlingen
(fullständig faktura). Under 4 000 kr räcker förenklad faktura utan köparnamn.

Detta fällde Inet-fakturan på 9 190 kr, som är ställd till Henrik privat — 1 838 kr i
moms hänger på att den ställs om till bolaget. **Äganderätten till varan spelar ingen
roll**; det är formalian på handlingen som avgör.

Bifirman **Epivo** är registrerad, så fakturor ställda till "Epivo" är giltiga för SGC —
samma juridiska person.

### Leverantörskonton — routa på prefix, inte på leverantörsnamn

Flera leverantörer används av **både** SGC och Sonetel med samma kort. Leverantörsnamnet
avgör därför ingenting.

| Leverantör | SGC | Sonetel |
|------------|-----|---------|
| OpenRouter (Stripe-prefix) | `TQDNYTAW` (person), `LJPQRPEC` (org) | `7BBAC0CB` |
| Render (Team name) | `VNWYXGCO` = "AI tutor" | `GBWSOWXA` = "Sonetel" |
| Cloudflare (momsnr) | `SE556071022901`, faktureras den **20:e** | `SE556486584701`, den **1:a** |

Fakturor med momsnummer avgör saken direkt. Vid tveksamhet: fråga financial-ops
(se avsnittet om systerprojekt nedan).

### OpenRouters omutfärdade kvitton — bokför dem ALDRIG

OpenRouter genererar ibland nya kvitton för redan betalda köp. De känns igen på:

```
Marked as paid on <datum>
OpenRouter Invoice for #<annat kvittonummer>
Paid out of band  Out of band payment for in_...
```

De är administrativa dokument, **inte nya kostnader**. I 2025/2026 hade 16 sådana
(`TQDNYTAW-0031`–`0046`) bokförts som egna kostnader. Kontrollera alltid fältet
*"OpenRouter Invoice for #"* — pekar det på ett annat kvitto är posten en dubblett.

Kontrollräkna dessutom mot **openrouter.ai/settings/credits**, som listar varje
kreditköp. Avgiften är ca 5,92 %: 100 → 105,93, 200 → 211,85, 500 → 529,50. Avviker
beloppet uppåt med 25 % är moms pålagd.

---

## Systerprojekt — ställ frågor dit istället för att gissa

| Fråga | Projekt |
|-------|---------|
| "Är denna kostnad SGC:s eller Sonetels?" | `~/Library/CloudStorage/Dropbox/Workspace/financial-ops` |
| Sonetels bolagsuppgifter, ÅR, aktiebok | `~/Library/CloudStorage/Dropbox/Sonetel/` |
| Epivos leverantörskvitton, e-post | `~/Library/CloudStorage/Dropbox/Git` (repot ÄR Git-mappen) |

Spawna en **read-only** agent dit — instruera uttryckligen att den inte får ändra något
och att den ska läsa projektets `CLAUDE.md` först. Skicka med alla särskiljande data du
har: datum, belopp, kvittonummer, kortsuffix, och en kontrasterande post från SGC-sidan.
Be den säga "oavgjort" hellre än att gissa.

Detta löste två frågor i bokslutet 2025/2026 som inte gick att avgöra från handlingarna:
Deepgram-debiteringarna (Sonetels) och OpenRouter 2 augusti (SGC:s).

### E-poståtkomst för kvitton

Tjänstekonto i Epivo-repot: `Dropbox/Git/google-workspace-sa.json`, domänbehörighet med
`.with_subject("henrik@epivo.ai")`. Når **endast @epivo.ai**.

Leverantörer som loggar in med `henrik.thome@gmail.com` — Render, Cloudflare, Deepgram,
OpenAI, Google Play Console — är **oåtkomliga** därifrån. Be Henrik hämta dem.

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
Intäkter från YouTube-kanalen **"Karima Fitness"**, som **ligger i bolaget** —
bolaget bekostade marknadsföringen och har nu intäkterna. Bekräftat av Henrik
2026-08-14. Det är alltså bolagets egen rörelseintäkt, inte en närståendetransaktion.
- Konto: **3305 Försäljning tjänster till annat EU-land** (nettoomsättning).
  Låg tidigare på 3999 — omklassad 2026-08-14.
- **Google Ireland är köpare** → EU-försäljning av tjänst till företag. Ska redovisas
  i **ruta 39** i momsdeklarationen OCH i **periodisk sammanställning** kvartalsvis.
  Förseningsavgift 1 250 kr per period. Detta är något annat än OSS, som gäller
  försäljning till privatpersoner.
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

## Innehavet i Sonetel AB (publ) — konto 1330

**Allt Henriks ägande i Sonetel går via SGC.** Han äger inga aktier personligen.
Listor som visar "Henrik Thomé 21,35 %" avser SGC:s innehav med Henrik som
företrädare — läs dem inte som personligt ägande.

| | |
|---|---:|
| Antal aktier | 1 616 638 |
| Sonetels totala antal | 7 571 381 |
| Andel av kapital och röster | 21,4 % |
| Redovisat värde 2026-04-30 | 6 193 874 kr |
| Bokfört värde per aktie | 3,83 kr |

**Primärkälla:** `Sonetel/Corporate documents/Bolagsstämmor/2026 04 23 Ordinarie
bolagsstämma/röstlängd/Anmälningsregister.md` — listar innehavaren som Swedish
General Consulting AB, 556071-0229. Den offentliga aktieboken duger INTE: SGC:s
aktier är förvaltarregistrerade och syns bara som en klump under Avanza.

Andelen över 20 % ger presumtion för betydande inflytande enligt ÅRL 1:5 →
posten heter **andelar i intresseföretag**, inte andra långfristiga
värdepappersinnehav.

### Värdering

Anskaffningsvärde. K2 tillåter ingen uppskrivning av finansiella
anläggningstillgångar, så värdet kan aldrig gå upp — bara ned.

**Nedskrivningsprövning är obligatorisk varje bokslut** (ÅRL 4:5, K2 kap. 11):
skriv ned om värdet på balansdagen understiger det bokförda och nedgången kan
antas vara bestående. Dokumentera prövningen i Not 3 även när slutsatsen är att
ingen nedskrivning behövs — annars saknar årsredovisningen en upplysning som
granskare kommer att efterfråga, och posten är 99,7 % av balansomslutningen.

Jämförelsepunkter vid 2025/2026: Sonetels egna kapital 3,84 kr/aktie,
låneavtalens konverteringskurs 4,46 kr, senaste transaktioner 6,00 och 6,50 kr.
Ingen nedskrivning gjordes.

**Räkna alltid om bokfört värde per aktie mot rätt antal aktier.** Divideras
6 193 874 med ett felaktigt aktieantal ändras slutsatsen om nedskrivning helt —
det inträffade under bokslutet 25/26.

## Bolagets lån — TVÅ HELT OLIKA REGELVERK

> **Blanda inte ihop dem.** Det gjordes vid bokslutet 25/26 och kostade
> 341 164 kr i utelämnad räntekostnad över två räkenskapsår. Läs alltid
> [`Avtal/README.md`](Avtal/README.md) före bokslut.

### A. Lån från Sonetel-aktieägare — konto 2390

Sju avtal från juni–juli 2024, totalt **1 850 000 kr**, tecknade för att finansiera
SGC:s teckning i Sonetels riktade emission.

- **Ränta 10 % per år som löper men INTE betalas** förrän på förfallodagen
  2027-06-30 (avtalens punkt 3.1–3.2)
- **Räntan MÅSTE periodiseras varje bokslut** — debet 8400, kredit **2399**.
  Använd inte 2960: räntan betalas enligt punkt 3.2 tillsammans med kapitalbeloppet
  på förfallodagen och är därför en **långfristig** skuld, inte en upplupen kostnad
- Aktierna är **spärrade/pantsatta** enligt punkt 4.5 respektive 5.1
  → ställd säkerhet, ska upplysas om i not
- Långivarna kan välja att få betalt i Sonetel-aktier enligt punkt 4.2
  → eventualförpliktelse, ska upplysas om i not

### B. Lån från Henrik Thomé — konto 2393

- Ränta: SLR per 30 nov föregående år + 1 procentenhet
  (2025: 2,96 %, 2026: 3,55 %)
- **Ränta bokförs först vid utbetalning** (kontantprincipen) — detta gäller
  **bara** Henriks egna lån, aldrig avtalen ovan
- Saldo 2026-04-30: **1 050 414 kr** (750 414 + 300 000, se nedan)
- Henrik har **efterskänkt** räntan för RÅ 2025/2026

De 300 000 kr som betalades in 23–24 juni 2025 med texten "FÖR AKTIEKÖP" kom från
Henrik själv, inte från aktieägarna, och bokförs därför på 2393 — inte 2390 som
banktextens mönster antyder. Pengarna finansierade lösen av köpoptionen från PMJ
Fastigheter och aktiverades på 1330.

### C. Utlägg Henrik — konto 2893
IB 492 520. Ökar med årets utlägg. Saldo 2026-04-30: 605 813 kr.

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
| GOOGLE IRELA | 1930 ↔ 3305 (Adsense, EU-försäljning — ruta 39 + periodisk samm.) |
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
| `scripts/kontroller.py` | Deterministiska bokslutskontroller — **steg 1 i processen** | ✓ Klar (2026-08-14) |
| `scripts/bokforing.py` | YAML→SIE4 bokföring | ✓ Klar |
| `scripts/sru_generator.py` | INK2 SRU-fil → Skatteverket | ✓ Klar (verifierad 2026-05-06) |
| `scripts/generate_ar.py` | K2 Årsredovisning PDF → Bolagsverket | ✓ Klar (omarbetad 2026-08-14) |
| Stämmoprotokoll | Bolagsstämma | ✓ Mall i `Bolagspapper/Bolagsstämmor/2026-10 Årsstämma RÅ 2025-2026/` |
| Fastställelseintyg | Bolagsverket | ✓ Ingår i ÅR-generatorn, spärrad tills stämman hållits |

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

**Kontrollskript (steg 1 i processen, körs före allt annat):**
```bash
python3 scripts/kontroller.py                  # innevarande RÅ
python3 scripts/kontroller.py --tyst           # bara fel och varningar
```
Kontrollerar verifikationsbalans, nummerserie, datumordning, att balansräkningen
sluter, resultatavslut, momsavslut, öppna flaggor, kontoplan, bankavstämning mot
SEB-CSV, kvittofiler, momsmetod, utläggstäckning, upplupen ränta, och att
genererade handlingar är nyare än journalen. **Slutkod 1 = fel som blockerar.**

Hittar en granskningsagent något som skriptet borde ha fångat — lägg till
kontrollen där innan du går vidare.

**ÅR-generator (Bolagsverket):**
```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 scripts/generate_ar.py \
    --journal "Financials/2025 2026/bokforing_2025.yaml" \
    --upplysningar "Financials/2025 2026/Bokslut/upplysningar.yaml" \
    --previous-sie "Financials/2024 2025/FInancials/SIE fil/20240501-20250430 (4).se" \
                   "Financials/2023 2024/Financial/SIE fil/20230501-20240430 (1).se" \
    --output "Financials/2025 2026/Bokslut/Årsredovisning 2026-04-30.pdf" \
    --signeringsdatum 2026-09-30 \
    --stämma-datum 2026-10-15
```
Mall: `scripts/ar_template.html` + `scripts/ar_template.css`.

`--upplysningar` pekar på en YAML med det som **inte går att räkna fram** ur
journalen: väsentliga händelser, närståendetexten, ställda säkerheter,
eventualförpliktelser. Generatorn vägrar köra utan den. Det är avsiktligt — så
länge upplysningarna låg hårdkodade i mallen stod det "Inga ställda säkerheter"
i årsredovisningen medan bolagets samtliga Sonetel-aktier i själva verket var
spärrade enligt låneavtalens punkt 4.5.

Notnumren tilldelas dynamiskt utifrån vilka noter som faktiskt trycks. Lägg
aldrig tillbaka hårdkodade nummer — balansräkningen hänvisade tidigare till en
Not 4 som inte fanns när kontot var noll.

`--signeringsdatum` måste ligga före `--stämma-datum`. Styrelsen undertecknar
årsredovisningen, stämman fastställer den senare; ett gemensamt datum för båda
är formellt fel.

**Beroenden:** `pip install jinja2 weasyprint babel openpyxl xlrd PyYAML pypdf` + `brew install pango`.

### Jämför alltid mot föregående års årsredovisning

`Financials/2024 2025/FInancials/Bokslut/Årsredovisning 2025-04-30.pdf` är
upprättad av extern redovisningskonsult och fastställd utan anmärkning. Den är
formatfacit.

```bash
python3 -c "from pypdf import PdfReader; \
  [print(p.extract_text()) for p in PdfReader('...Årsredovisning 2025-04-30.pdf').pages]"
```

Läs den **innan** du genererar, inte efter att granskarna klagat. Jämförelsen
avslöjade på egen hand att en ÅRL 5:9-tabell inte hörde hemma i dokumentet, att
titeln ska vara "Styrelseledamot och verkställande direktör", och att sätet
angetts fel i flera tidigare årsredovisningar.

---

## Historisk flerårsöversikt

| År | Nettoomsättning | Resultat efter fin.poster | Soliditet |
|----|-----------------|--------------------------|-----------|
| 2025/2026 | 12 155 (Adsense) | **-434 885** | **38,1%** |
| 2024/2025 | 0 | -13 540 | 47,4% |
| 2023/2024 | — | 1 063 | 64,7% |
| 2022/2023 | -1 | 235 | 58,9% |
| 2021/2022 | — | -7 387 | 53,9% |

Resultatet 25/26 blev drygt fem gånger sämre än den preliminära bedömningen om
-90 765 kr. Skillnaden förklaras nästan helt av upplupen ränta 341 164 kr på
aktieägarlånen, som aldrig hade periodiserats, plus kostnader som saknades i
bokföringen (ElevenLabs, GitHub, EUIPO) och en omklassificering av 300 000 kr
från kostnad till aktieinnehav.

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
