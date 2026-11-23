---
name: brf-kommunikation
description: |
  Författa medlemsinfobrev ("Informationsbrev N <år>") för Brf Rudtorp 6 i föreningens
  gröna husstil, ur Henriks ämnespunkter. Använd när ett infobrev till medlemmarna ska skrivas.
  Producerar ett utkast i precedensbrevens stil/ton, putsat av GPT-5, levererat som PDF i
  Kunskapsbas/Medlemsinfo/Tidigare utskick/. Skillen FÖRFATTAR och formger — utskick (e-post)
  och beslut att skicka ägs av Henrik/styrelsen.
---

# brf-kommunikation

Omvandlar ämnespunkter till ett **Informationsbrev** till medlemmarna i samma **gröna husstil** och varma "vi"-ton som föreningens tidigare brev. Ett kort, skummbart brev — inte en uppsats.

## Scope-guard
- Skriver bara infobrevsutkast (md + PDF) i `Kunskapsbas/Medlemsinfo/Tidigare utskick/`.
- **Skickar aldrig e-post** och publicerar inte på hemsidan — det gör Henrik/styrelsen (avsändare rudtorp6@gmail.com).
- Rör **aldrig** medlemsregister/personuppgifter i `Kunskapsbas/Medlemmar-kontakt/`. Skriver aldrig över befintliga brev.
- Brevet riktas till "medlemmar" och signeras "Styrelsen" — **inga enskilda namn**, inga personuppgifter.

## Format-facit (kanoniska källor — läs vid tvekan)
- Precedensbrev: `Kunskapsbas/Medlemsinfo/Tidigare utskick/Medlemsbrev 2 2026.pdf` (titel inuti = "Informationsbrev 2 2026") och `Informationsbrev 3 2026.pdf`.
- Mall: `templates/informationsbrev.md` (denna skill).
- Renderingstema: `Kunskapsbas/Mallar/infobrev-tema.css` (grön husstil).
- Stadge-referens (faktakoll): `Kunskapsbas/Stadgar/Stadgar - nyckelparagrafer för protokoll och styrelsearbete.md`.

## STILREGLER (följ exakt — destillerat ur precedensbreven)

**Struktur**
- Grönt sidhuvud (logga) → **grön titel** `# Informationsbrev N <år>` → fet **"Hej!"** → 1 mening kort säsongs-/lägesöppning → **2–4 ämnessektioner**, var och en med **fet `##`-underrubrik** + 1–3 korta stycken → avslut **"Mvh / Styrelsen"** (facit i båda breven; GPT-5 kan föreslå det formella "Med vänlig hälsning" — behåll ändå "Mvh", det är föreningens röst).
- Kollektivt **"vi"** (styrelsen) till "ni/alla". **Aldrig enskilda namn** som avsändare.

**Färg & fetning**
- **Endast titeln är grön** (temat sätter `#3A8C2A`). Underrubriker = **feta svarta**. Allt annat svart; hyperlänkar blå (temat).
- Feta (`**...**`): underrubriker, samt **datum, tid och plats** i brödtexten ("**söndagen den 19 april kl. 10.00**"). Och "Hej!". **Inga andra fetningar.**

**Ton & röst**
- Varm, personlig, kollektiv "vi". Säsongsöppning är vanlig ("Nu är äntligen våren här…").
- **Får vara rakt/bestämt** vid behov (ordningsregler, nedskräpning) — men aldrig nedlåtande.
- Använd **kostnadsargument** där det passar ("hjälps vi åt → lägre kostnader / annars extern hjälp = ökade kostnader").

**Längd & uppmaningar**
- Kort och skummbart — normalt **1 sida**. Korta sektioner.
- **Konkreta CTA:er**: exakt tid/plats; stegvisa instruktioner ("logga in på Mitt HSB → Min bostad → Mina köer"); deadlines med datum.

**Emoji**
- Sparsamt: **0–3 per brev** (t.ex. 🌱 🙂) och **bara i varma stycken**. Aldrig i bestämda/allvarliga stycken (jfr Informationsbrev 2, som är helt emoji-fritt).

**Språk**
- Svensk sakprosa, du-/ni-tilltal, undvik byråkratiska och engelska termer, skriv ut datum tydligt. Slutpoleras alltid av GPT-5-koll.

**Får ALDRIG**
- Namnge enskilda medlemmar negativt, skriva ut personuppgifter, ange enskilda styrelseledamöter som avsändare, eller utlova beslut som inte fattats.

## Numrering
"Informationsbrev N <år>", löpande **per år**. Härled nästa N:
1. Lista filer i `Kunskapsbas/Medlemsinfo/Tidigare utskick/` **för innevarande år**.
2. Matcha **båda** mönstren `Informationsbrev N <år>` **och** `Medlemsbrev N <år>` (brev 2 ligger som "Medlemsbrev 2 2026.pdf" men har titeln "Informationsbrev 2 2026" — läs PDF-titeln vid tvekan).
3. Nästa N = `max(N) + 1`. **Nytt år utan brev → N = 1.**
4. Nya brev döps kanoniskt **"Informationsbrev N <år>"** (befintlig "Medlemsbrev 2" döps inte om men räknas).

## Stadgeankring (PROJECT_RULES kräver det — regeln namnger infobrev)
Innan formella moment skrivs in, **faktakolla mot stadge-referensen** (vid tvekan stadge-PDF:en):
- Motion/motionsdeadline, kallelsetider och -sätt, stämmodatum, ansvarsfrihet, andrahands-/p-platsregler m.m.
Layout/ton är inte stadgestyrt; det är **sakuppgifterna om föreningsformalia** som ska stämma.

## Process
1. **Bestäm N** (se Numrering) och **samla ämnen** från Henrik (vad ska brevet ta upp? ev. deadlines/datum?).
2. **Skriv utkast** i `templates/informationsbrev.md`-struktur enligt STILREGLERNA. Behåll mallens `<div class="brand">`/`<div class="addr-footer">`-rader (sidhuvud/sidfot) och den absoluta loggsökvägen.
3. **Stadge-faktakoll** av formella moment (se ovan).
4. **GPT-5 svensk-koll** av brödtexten:
   ```bash
   python3 ~/.claude/scripts/openai_call.py --model gpt-5 \
     --system-file ~/.claude/skills/brf-kommunikation/prompts/gpt5-svensk-infobrev.txt \
     --user-file <utkast>.md --max-tokens 6000
   ```
   Kontrollera `finish_reason` (scriptet varnar vid trunkering på stderr).
5. **2-agent review (≥8) — obligatoriskt före utskick** (Henriks krav 2026-06-14; ett infobrev går till ~50 hushåll). Två oberoende agenter bedömer utkastet:
   - **Agent A — sak & GDPR:** stämmer varje sakuppgift mot mötesprotokollet? Är rätt saker med, och har känsligt/internt material (lån, ekonomi, leverantörstvister, enskilda lägenheter/personer) utelämnats? Inga personuppgifter utöver styrelsens kontaktperson-roll?
   - **Agent B — ton, stil & språk:** följer brevet STILREGLERNA + precedensen (struktur, 2–4 sektioner, feta datum, endast titeln grön, varm "vi"-ton, "Mvh/Styrelsen"); svensk korrekthet; lagom längd (≈1 sida).
   - Båda ska ge **CONFIDENCE ≥8**. Iterera annars (vid materiell textändring: kör om GPT-5-kollen, steg 4). Max 2 omgångar, annars lyft till Henrik.
6. **Rendera PDF** (grön husstil):
   ```bash
   cd "/Users/henrik/Library/CloudStorage/Dropbox/Workspace/Brf Rudtorp 6"
   pandoc "<utkast>.md" --standalone --embed-resources \
     -c "Kunskapsbas/Mallar/infobrev-tema.css" -o /tmp/infobrev.html
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless=new --disable-gpu --no-pdf-header-footer \
     --print-to-pdf="Kunskapsbas/Medlemsinfo/Tidigare utskick/Informationsbrev N 2026.pdf" \
     "file:///tmp/infobrev.html"
   ```
   Läs PDF:ens sida 1 och **jämför visuellt mot precedensen** (grönt ordmärke, grön titel, feta svarta rubriker, fet "Hej!", "Mvh/Styrelsen", adress-sidfot). Justera `--gron` i temat om nyansen avviker.
7. **Arkivera** md-källan bredvid PDF:en i `Tidigare utskick/`.
8. Om brevet innehåller en **deadline/händelse** (städdag, stämma, motionsstopp) → lägg in i `KALENDER.md` via **brf-uppgifter**.
9. **Henriks läsning/godkännande = slutgrind** innan utskick.

## GDPR
Mottagarlistor minimeras och hanteras aldrig i skillen, CR eller changelog (PROJECT_RULES). Brevet självt är PII-fritt. Massutskicket görs av Henrik.

## Husstil
Föreningen har **en grön husstil** för utåtriktade dokument (protokoll + infobrev). Den tidigare "mauve/sage"-linjen (`Kunskapsbas/Mallar/infoblad-tema.css`) är **Deprecated** (byggde på overifierade färggissningar; inget dokument använde den). Se `Kunskapsbas/Mallar/README.md`.
