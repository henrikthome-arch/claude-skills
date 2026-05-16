---
name: bolagsstamma
description: Planning and document management for Sonetel AB's annual general meeting (bolagsstämma). Use when drafting meeting notices, agendas, board proposals, minutes, or managing the meeting timeline.
argument-hint: "[dokument-typ | status | tidslinje]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel bolagsstämmor. If the current working directory does NOT contain `Sonetel/Corporate`, STOP immediately and tell the user: "This skill is for Sonetel bolagsstämmor only. Current directory: [cwd]". Do NOT proceed.

Du hjälper Henrik Thomé, VD för **Sonetel AB (publ)**, att planera och genomföra ordinarie bolagsstämma. Bolaget är listat på **Nasdaq First North Growth Market** och registrerat hos Euroclear Sweden (avstämningsbolag).

Arbetsmappen är:
`~/Library/CloudStorage/Dropbox/Sonetel/Corporate documents/Bolagsstämmor/[ÅÅÅÅ MM DD Ordinarie bolagsstämma]/`

---

## Bolagets profil

- **Bolag:** Sonetel AB (publ), org.nr 556486-5847
- **Lista:** Nasdaq First North Growth Market
- **Certified Adviser:** [uppdatera vid behov]
- **Aktiebok:** Euroclear Sweden (avstämningsbolag)
- **Räkenskapsår:** januari–december (ändrat från brutet räkenskapsår juli–juni vid extra stämma 2025-05-22)
- **VD:** Henrik Thomé

---

## Standardagenda (12 punkter)

Alla ordinarie bolagsstämmor följer denna dagordning:

1. Val av ordförande vid stämman
2. Upprättande och godkännande av röstlängd
3. Val av en eller två justeringsmän
4. Prövande av om stämman blivit behörigen sammankallad
5. Godkännande av dagordning
6. Framläggande av årsredovisning och revisionsberättelse
7. Beslut om:
   a. Fastställande av resultat- och balansräkning
   b. Dispositioner beträffande bolagets resultat (vinstdisposition)
   c. Ansvarsfrihet för styrelseledamöter och VD
8. Fastställande av arvoden till styrelse och revisor
9. Val av styrelse och revisor
10. Principer för tillsättande av valberedning
11. Beslut om bemyndigande för styrelsen att besluta om emission
12. Stämmans avslutande

---

## Dokumentchecklista

### Obligatoriska dokument (alltid)

**Inför stämman:**
- [ ] **Kallelse** – minst 4 veckor före (ABL 7:18), publiceras via Cision, hemsida, PoIT och SvD
- [ ] **Styrelsens förslag – resultatdisposition** (punkt 7b)
- [ ] **Styrelsens förslag – bemyndigande** (punkt 11, kräver 2/3 majoritet)
- [ ] **Valberedningens förslag** – styrelseledamöter, revisor, arvoden, valberedningsprinciper (punkterna 1, 8, 9, 10)
- [ ] **Fullmaktsformulär** – PDF för nedladdning på hemsidan

**På stämmodagen:**
- [ ] **Röstlängd** – upprättas från Euroclear-utdrag + inlämnade fullmakter
- [ ] **Bolagsstämmoaktiebok** – från Euroclear/Bolagsverket
- [ ] **Inlämnade fullmakter** – sammanställda

**Efter stämman:**
- [ ] **Stämmoprotokoll** – justerat och påskrivet
- [ ] **Kommuniké** – pressrelease via Cision, samma dag eller dagen efter
- [ ] **Registrering Bolagsverket** – vid beslut som kräver registrering (bemyndigande m.m.)

> **OBS:** Protokollet publiceras **inte** på bolagets hemsida. Det är inget krav för First North-bolag. Kommunikén är det offentliga dokumentet.

### Rekommenderade dokument

- [ ] **Ordförandemanus / talmanus** – mötesscript för ordföranden
- [ ] **Kalendarium** – tidslinje (se TIDSLINJE.md)
- [ ] **Print-mapp** – utskriftsklara versioner

### Vid behov (inte varje år)

- [ ] Förslag till ändring av **bolagsordning**
- [ ] **Personaloptionsprogram** – incitamentsprogram för anställda
- [ ] Extra styrelsens förslag vid specifika ärenden

---

## Regler och regelverk

### ABL (Aktiebolagslagen)
- **7:18** – Kallelse ska utfärdas tidigast 6 veckor och senast 4 veckor före stämman
- **7:23** – Kallelse i avstämningsbolag ska publiceras i Post och Inrikes Tidningar och annonseras i rikstäckande dagstidning
- **7:28** – Röstlängd ska upprättas av styrelsen
- **7:48** – Protokoll ska föras och justeras inom 2 veckor

### Nasdaq First North Growth Market
- Kallelse ska publiceras via **Cision** (nyhetskanal för bolaget)
- Stämmobeslut ska kommuniceras som pressrelease via Cision
- Certified Adviser ska informeras om väsentliga beslut

### Euroclear Sweden (avstämningsbolag)
- Aktiebok-utdrag (bolagsstämmoaktiebok) **beställs från Euroclear i god tid** (beställ minst 6–8 veckor före stämman)
- **Avstämningsdag** för rösträtt fastställs och anges i kallelsen
- **Sista dag för anmälan** anges i kallelsen – baserat på 2022–2024 är mönstret **+1 dag efter avstämningsdag** (t.ex. avstämning 15 april → anmälan senast 16 april)
- Innehavare via förvaltare (nominee) måste omregistrera senast på avstämningsdagen för att rösta

---

## Standardtext – återkommande formuleringar

### Kallelse – inledning
```
Aktieägarna i Sonetel AB (publ), org. nr 556486-5847, kallas härmed till
ordinarie bolagsstämma [dag] den [datum] kl. [tid] på [plats].
```

### Kallelse – anmälan
```
ANMÄLAN M.M.
Aktieägare som vill delta i bolagsstämman ska:
  dels vara införd i den av Euroclear Sweden AB förda aktieboken
  den [avstämningsdag],
  dels senast den [anmälningsdag] anmäla sig till bolaget.
```

### Styrelsens förslag – resultatdisposition (om ingen utdelning)
```
Styrelsen föreslår att ingen utdelning lämnas och att till förfogande
stående medel om [belopp] kronor balanseras i ny räkning.
```

### Styrelsens förslag – bemyndigande (standardtext)
```
Styrelsen föreslår att bolagsstämman bemyndigar styrelsen att, vid ett
eller flera tillfällen under tiden fram till nästa ordinarie bolagsstämma,
med eller utan avvikelse från aktieägarnas företrädesrätt, besluta om
emission av aktier, teckningsoptioner och/eller konvertibler.
Bemyndigandet ska vara begränsat till att sammanlagt omfatta emission
motsvarande högst tio (10) procent av det totala antalet utestående
aktier vid tidpunkten för årsstämman.
```

**OBS:** Bemyndigandet sänktes från 20% till 10% inför stämman 2026 (CR-2026-03-18-001). Använd 10% som standard tills vidare.

---

## Tidslinje (mall – baklänges från stämmodatum)

Anpassa datumen utifrån faktisk stämmodag:

| Veckor före | Datum (exempel) | Uppgift |
|---|---|---|
| -8 v | | Fastställ dagordning och plats |
| -7 v | | Kontakta valberedningen |
| -6 v | | Styrelsemöte – godkänn förslag och kallelse |
| -4 v – 3 dagar | | **Boka annons SvD** senast kl 16:00 (3 arbetsdagar före publicering) |
| -4 v – 1 dag | | **Beställ kungörelse PoIT** via poit.bolagsverket.se (publiceras nästkommande vardag) |
| -4 v (senast) | | **Skicka kallelse** via Cision + PoIT + SvD |
| -4 v | | Publicera årsredovisning (om ej gjort) |
| -2 v | | Sista dag aktiebok (Euroclear) |
| -1 v | | Sista dag anmälan |
| Dag 0 | | **Bolagsstämma** |
| Dag 0 | | Konstituerande styrelsemöte (direkt efter stämman) |
| Dag +1 | | Kommuniké via Cision |
| Dag +14 | | Justerat protokoll klart |
| Dag +14 | | Protokoll publiceras på hemsidan |
| Dag +30 | | Registrering Bolagsverket (vid behov) |

---

## Per capsulam – styrelsebeslut om kallelse och förslag

Innan kallelse publiceras krävs ett **per capsulam styrelsebeslut** som godkänner:
- a) Kallelsen (inkl. dagordning och publicering)
- b) Digital stämma (om tillämpligt) – med hänvisning till § 11 bolagsordningen och ABL 7:15
- c) Styrelsens förslag resultatdisposition (punkt 7b) – med referens till Addendum 1
- d) Styrelsens förslag bemyndigande (punkt 11) – med referens till Addendum 2

**Bilagor till protokollet:**
- Bilaga: Kallelsen (PDF)
- Addendum 1: Styrelsens förslag resultatdisposition
- Addendum 2: Styrelsens förslag bemyndigande

Protokollet sparas i Board-mappen:
`~/Dropbox/Sonetel/Board/Board meetings/[år]/[datum] Per capsulam kallelse och förslag till stämma ([nr])/Protokoll/`

Protokollet följer samma format som övriga per capsulam-protokoll (se board-minutes skill). Signeras av alla styrelseledamöter via Egreement.

---

## Konstituerande styrelsemöte

Hålls **direkt efter** ordinarie bolagsstämman, per capsulam. Mötet är numrerat i den löpande nummerserien för styrelsemöten (inte separat numrering).

**Standardinnehåll (§§ 1–7):**

| § | Beslut |
|---|---|
| §1 | Mötet öppnas (av styrelseordföranden) |
| §2 | Val av protokollförare (Henrik Thomé) – justeras av ordföranden |
| §3 | Firmateckning: styrelsen samt VD ensam |
| §4 | Val av styrelseordförande |
| §5 | Val av vice styrelseordförande |
| §6 | Styrelsens arbetsordning godkänns – **inkluderar VD-instruktion som Bilaga 1** (ny version daterad stämmodagen) |
| §7 | Bolagets informationspolicy godkänns (aktuell version) |

**Relaterade dokument och sökvägar:**
- Protokoll: `~/Dropbox/Sonetel/Board/Board meetings/[år]/[datum] Konstituerande styrelsemöte ([nr])/Protokoll/`
- Styrelsens arbetsordning: `~/Dropbox/Sonetel/Board/Styrelsens arbetsordning/[ÅÅÅÅ MM DD]/` (ny daterad mapp varje år)
- Informationspolicy: `~/Dropbox/Sonetel/Corporate documents/Informationspolicy/`

**Bilagor till protokollet:**
- Bilaga 1: Styrelsens arbetsordning (PDF, daterad stämmodagen, inkluderar VD-instruktion)
- Bilaga 2: Informationspolicy (PDF, aktuell version)

**Obs:**
- Ny version av styrelsens arbetsordning ska upprättas och dateras till stämmodagen. Vanligen är det bara datum-referenserna inuti dokumentet som ändras (rad om "godkänts av styrelsen" + rad om "fastställt vid styrelsemöte" inne i VD-instruktionen) – innehållet i övrigt oförändrat. Verifiera ändå med diff.
- VD-instruktionen är en del av (Bilaga 1 i) arbetsordningen, inte ett separat dokument.
- Kontrollera aktuellt versionsnummer på informationspolicyn i ovanstående mapp.

---

## Legala krav och principer för protokoll/kommuniké

Oavsett vilken mall du kopierar från: **säkerställ att dessa punkter finns** (ABL-krav och publiceringsregler):

**Protokoll:**
- **Bemyndigande-beslut:** Notera explicit att 2/3-kravet i ABL 16a kap uppfylldes:
  > "Det noterades att beslutet fattades enhälligt och därmed med biträde av aktieägare med mer än två tredjedelar (2/3) av såväl de avgivna rösterna som de aktier som var företrädda vid stämman, varigenom kravet i 16 a kap. aktiebolagslagen uppfylldes."
- **Digital stämma:** Notera omröstningsmetod under § 2 röstlängd (t.ex. muntliga ja-rop + Teams chattfunktion, identitetskontroll mot anmälningslistan) för ABL 7:4c-compliance.
- **Ansvarsfrihet (ABL 7:46):** Använd "enhälligt av röstberättigade deltagare" (inte "ingen röstade emot") och notera att styrelseledamöter/VD inte deltog i beslut om egen ansvarsfrihet.

**Arvodestext (protokoll + kommuniké):**
- Båda villkoren (ej anställd + ej huvudägare) ska stå i **samma mening**, inte delas. Harmonisera med kallelsens exakta formulering:
  > "…240 000 kr till styrelseordföranden samt 100 000 kr **till var och en av övriga styrelseledamöter som inte är anställda i bolaget eller utgör huvudägare**."

**Kommuniké för Cision:**
- Rubriker ("Om Sonetel", "Kontakt") och kontaktrader ("VD / Telefon / Email") ska vara **separata paragrafer**, inte soft line breaks inom samma paragraf.
- Presentationstexter för nyvalda ledamöter tas bort vid omval.

**Bemyndigande (aktuell procentsats):**
- Från 2026 är nivån **10%** (sänkt från 20% per CR-2026-03-18-001). Kontrollera alltid aktuell procentsats mot senaste valberedningsförslag innan du skriver protokoll/kommuniké.

**Revisor:**
- Sedan 2026 heter tidigare Mazars SET AB nu **Forvis Mazars AB**. Kontrollera aktuellt namn mot senaste årsredovisning/revisionsberättelse.

---

## Förvaltarregistrerade aktier och röstlängd

Aktier via Avanza, Nordnet eller pensionsförsäkringar (Futur, SEB Pension m.fl.) är **förvaltarregistrerade**. För att ägaren ska få rösträtt på stämman måste de **omregistreras till eget namn före avstämningsdagen**. Om det inte är gjort:

- Ägaren finns **inte** i bolagsstämmoaktieboken
- Aktierna finns hos förvaltaren (t.ex. AVANZA BANK AB, NORDNET BANK AB)
- Ägaren saknar rösträtt med dessa aktier
- I röstlängden ska aktierna placeras under **"Aktier ej representerade"**, INTE "Övriga närvarande" (som kan missförstås som representerade)

**Vanligt förekommande:** Styrelseledamöter kan ha sina aktier via pensionsförsäkring och saknar rösträtt. Sebastian Ahlskog hade 98 195 aktier förvaltarregistrerade 2026 – ordförande men ej röstberättigad.

---

## Förifyllda fullmakter för Egreement-signering

När du skapar förifyllda fullmakter för aktieägare (för att underlätta signering):

- **Använd det officiella fullmaktsformuläret** som layout (tabeller för Ombud + Aktieägare) – INTE ett förenklat textformat.
- Bygg DOCX via python-docx med "Table Grid"-style, konvertera till PDF med LibreOffice.
- Förifyll allt utom datum (Egreement tidsstämplar).
- Lämna telefonnummer/e-post blanka om du inte har dem – aktieägaren kan fylla i manuellt eller lämna tomt.
- Spara i `fullmakt/Förifyllda/`. Original i `fullmakt/Inlämnade fullmakter/` när signerat retur kommer in.

---

## PDF-generering (docx/xlsx → PDF)

**Default: LibreOffice headless** – fungerar för de flesta dokument:

```bash
/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless --convert-to pdf --outdir <utmapp> <fil.docx eller fil.xlsx>
```

Installeras via `brew install --cask libreoffice`.

**När LibreOffice inte räcker — använd Word direkt:**

LibreOffice tolkar Words tab-indentering i numrerade listor (t.ex. "8.1 [tab] Text…") annorlunda och kan bryta texten på fel ställen. Detta märks tydligt i dokument med Word-specifik formatering – t.ex. **Styrelsens arbetsordning** och VD-instruktionen, där numreringen 8.1, 8.2 etc. får text att radbrytas felaktigt.

För sådana dokument: **starta om Word fresh, sedan AppleScript "save as"**:

```bash
# 1. Quit Word fully (viktigt för att rensa state)
osascript -e 'tell application "Microsoft Word" to quit'
sleep 2

# 2. Convert via fresh Word state
osascript <<EOF
tell application "Microsoft Word"
    activate
    delay 1
    open POSIX file "/path/to/file.docx"
    delay 3
    set theDoc to active document
    save as theDoc file name "/path/to/file.pdf" file format format PDF
    delay 2
    close theDoc saving no
end tell
EOF
```

Word AppleScript "save as" misslyckar om Word redan har öppna dokument från tidigare misslyckade försök – därför `quit` först. Verifiera resultatet genom att jämföra med tidigare års PDF.

**Fungerar INTE tillförlitligt:**
- `docx2pdf` (Python-biblioteket)
- `weasyprint` – saknar native-bibliotek på Mac

---

## Multi-agent audit före signering/publicering

Innan dokument (talmanus, röstlängd, protokoll, kommuniké, kallelse) skickas till Egreement eller publiceras via Cision: **kör alltid 2 oberoende granskare i parallell** med olika fokus:

- Granskare 1: Format/innehåll – dates, shareholder data, stale references, typos
- Granskare 2: Juridisk compliance – ABL 7 kap, ABL 16a kap (Leo-lag för bemyndigande), Svensk kod, cross-document consistency

Om fixar görs efter audit: **kör ny audit**. Agent-fynd är bara bra om de faktiskt implementeras *korrekt*.

---

## Leverantörer och kontakter

### SvD-annons (bolagsstämma-kungörelse)
- **Leverantör:** Annonsdax (förmedlar till Schibsted/SvD)
- **Kontakt bokning:** Sandra Marklund, Client Manager – ostersund@annonsdax.se, 08-555 00 620
- **Korrektur/produktion:** Sidsel Udø Bergum, Schibsted Productions – sidsel.bergum@schibsted.com, +47 971 15 804
- **Deadline bokning:** Senast **3 arbetsdagar före publicering, kl 16:00**
- **Deadline korrektur:** Senast **kl 08:00 en arbetsdag före publicering** (om inget svar betraktas annonsen som godkänd)
- **Vad som behövs:** Annonstext i Word-format, fakturaadress
- **Sektion:** SvD Näringsliv, Bolagsärenden Eftertext
- **Format 2026:** Modul 22B (80×65 mm), kostnad ca 7 595 kr exkl. moms
- **Ordernummer 2026:** 206037

### Bolagsverket-registrering (stämmobeslut + ÅR)

- **Leverantör:** Kommissionären för Aktiebolagsärenden AB
- **Kontakt:** Lars Hellman, 060-55 37 72
- **Adress:** Box 817, 851 23 Sundsvall (besök: Storgatan 1)
- **Används för:** Registrering av stämmobeslut som kräver inlämning (t.ex. bemyndigande enligt ABL 16a kap) samt inlämning av årsredovisning med revisionsberättelse och tillstyrkande
- **Varför extern partner:** Säkerställer korrekt handläggning och formkrav hos Bolagsverket. Föreslå inte verksamt.se som default.

### PoIT (Post och Inrikes Tidningar)
- **Leverantör:** Bolagsverket (e-tjänst)
- **URL:** poit.bolagsverket.se (kräver e-legitimation)
- **Deadline:** Publiceras nästkommande vardag – skicka in **senast dagen före** önskad publiceringsdag
- **Format:** Elektronisk inlämning, ingen tryckt version
- **Typ av kungörelse:** "Kallelse till stämma"
- **OBS:** PoIT ska innehålla **fullständig kallelse** (inte en kortversion som SvD-annonsen)
- **Spara kungörelse-id** från kvittot (t.ex. K215951/26)

---

## Lokal och praktisk info

**2024 (årsstämma):** Fysisk – United Spaces, Klarabergsviadukten 63, Stockholm, kl. 14:00

**2026 (årsstämma):** Helt digital via Microsoft Teams, kl. 14:00 – med stöd av § 11 bolagsordningen och ABL 7:4c/7:15. Ingen fysisk mötesplats. Möteslänk skickas per e-post till anmälda aktieägare.

**Viktigt vid digital stämma:**
- Anmälan kräver e-postadress (för möteslänk)
- Fullmakter kan skickas per e-post till investors@sonetel.com (alternativt per post till Mailbox 647, 114 11 Stockholm)
- Fullmaktsformulär ska inte kräva "uppvisande av original på stämman" – anpassa texten
- Stöd i bolagsordningen § 11 + ABL 7 kap. 4 c § ska anges i kallelsen

---

## Dokumentversionskonventioner

- Namnge utkast: `kallelse-v0.1.docx`, `kallelse-v0.2.docx`, `kallelse-v1.0.pdf`
- v0.x = interna utkast under granskning
- v1.0 = godkänd, redo att distribuera
- Spara alla versioner – radera ingenting
- Slutgiltig distribuerad version alltid som PDF

---

## Mappstruktur

```
[stämmodatum] Ordinarie bolagsstämma/
├── kallelse/
├── protokoll/
│   └── Påskrivet/
├── röstlängd/
│   ├── Fullmakter/
│   └── Registreringsbevis/
├── styrelsens-förslag/
│   ├── Bemyndigande/
│   └── Resultatdisposition/
├── valberedningens-förslag/
├── fullmakt/
│   └── Inlämnade fullmakter/
├── kommuniké/
├── talmanus/
├── bolagsstämmoaktiebok/
├── PoIT/
├── SvD-annons/
├── registrering-bolagsverket/
├── print/
└── change-requests/
```

---

## Projektspecifikt underlag

Varje stämmas projektmapp innehåller en `underlag/`-mapp med projektspecifik fakta som **inte** ska ligga i skillet (för att skillet ska vara återanvändbart):

| Fil | Innehåll |
|---|---|
| `underlag/styrelse-och-revisorer.md` | Nuvarande styrelsesammansättning, revisor, arvoden och förväntade förslag |
| `underlag/aktier.md` | Antal aktier och röster vid kallelsedatum (källa: senaste bokslutskommuniké eller halvårsrapport) |

**Läs alltid `underlag/`-mappen** i början av ett arbetspass för att få aktuell information om styrelse, arvoden och förväntade förslag. Uppdatera filerna där när ny information kommer in (t.ex. formellt valberedningsförslag).

---

## Hur du arbetar

1. **Läs alltid `underlag/`, TIDSLINJE.md och CLAUDE.md** i projektmappen först
2. **Kontrollera dokumentstatus** innan du redigerar – Distribuerade dokument kräver CR
3. **Uppdatera alltid CHANGELOG.md** efter varje ändring
4. **Fråga alltid** innan du ändrar färdigställda eller distribuerade dokument
5. **PDF-generering**: Använd LibreOffice headless (`soffice --convert-to pdf`) – se avsnitt "PDF-generering" ovan. Henrik behöver inte längre exportera manuellt från Word.

$ARGUMENTS
