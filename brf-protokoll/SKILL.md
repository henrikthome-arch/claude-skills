---
name: brf-protokoll
description: |
  Skriv protokollUTKAST för Brf Rudtorp 6 i Erikas format — föreningsstämma eller styrelsemöte —
  ur ett mötestranskript (helst KB-Whisper) + dagordning. Använd när ett möte ska protokollföras.
  Producerar ett utkast som ankras i stadgarna, poleras av GPT-5 och verifieras av 2 agenter (≥8);
  justering/signering ägs av styrelsen.
---

# brf-protokoll

Omvandlar ett mötestranskript till ett **protokollutkast** i samma format och **knappa ton** som Erikas levererade protokoll. Ett beslutsprotokoll — inte ett ordagrant referat.

## Scope-guard
Skriver bara protokollutkast i rätt mötesmapps `protokoll/` under `Brf Rudtorp 6`. Skriver aldrig över **och flyttar aldrig** Erikas befintliga `.docx` (se "Versionshantering och arkivering"). Tömmer aldrig en `Arkiv/`-mapp. Rör aldrig medlemsregister i `Kunskapsbas/Medlemmar-kontakt/`.

## Format-facit (kanoniska källor — läs vid tvekan)
- Stämma: `Stämmor/2026-05-27 Föreningsstämma/protokoll/Protokoll föreningsstämma 2026-05-27 - utkast (Erika).docx`
- Styrelse (konstituerande): `Styrelsemöten/2026-05-27 Konstituerande möte/protokoll/Protokoll konstituerande styrelsemöte 2026-05-27 - utkast (Erika).docx`
- Formkrav: `Kunskapsbas/Stadgar/Stadgar - nyckelparagrafer för protokoll och styrelsearbete.md`
- Mallar i denna skill: `templates/stamma.md`, `templates/styrelsemote.md`

## Erikas stil (följ exakt — avgörande)
- **Numrerade dagordningspunkter (1., 2., …) med fet rubrik; underpunkter (beslut/detaljer) indragna.** (§23 "nummerföljd" = löpnummer på protokollserien, inte §§ i texten.)
- **Telegrafisk stil:** "godkännes", "väljs", "enhälligt beslut att…". Frasen **"Styrelsen beslutar att…" bara för tunga beslut** (ansvarsfördelning, firmateckning, delegation/attest). Stämman använder **aldrig** "beslutar att".
- **Lydelse "enhälligt":** använd den ordboksriktiga formen **"enhälligt beslut att…"** (Henriks beslut 2026-06-11; se [CR-2026-06-11-brf-protokoll-numrering]). I facit varierar lydelsen — styrelseprotokollen använder övervägande "Enhetligt" (≈11 ggr), stämman "Enhällig(t)" — men framåt skrivs **enhälligt** genomgående. GPT-5-koll-prompten ska inte längre flagga "enhälligt" som avvikelse eller normalisera till "Enhetligt".
- Rubrik i versaler, exakt lydelse per mall.
- Varje beslut + **röstresultat** skrivs in per punkt (§19.3: "Enhälligt", "samtliga röstberättigade", "X röstberättigade").

## Process

1. **Välj mötestyp** (stämma / styrelsemöte; styrelse-undertyp: konstituerande eller ordinarie) och **läs**: transkript (helst `…-kbwhisper.txt`) + dagordning/underlag.
2. **Destillera** till beslutsprotokoll i rätt mall (`templates/`). Beslut, inte referat. Erikas knappa stil.
3. **Stadge-formkravskoll** mot referensen:
   - **Stämma:** §16 alla 24 punkter (Erikas sammanslagning av närliggande punkter OK); §19 röstlängd + beslut + **röstresultat** + justering + (påminn: justerat tillgängligt ≤3 v).
   - **Styrelse:** §22 beslutsförhet (fler än hälften); §23 signering (protokollförare + ordförande + en utsedd ledamot), löpnummer, betryggande förvaring.
4. **GPT-5 svensk-koll** av brödtexten via `~/.claude/scripts/openai_call.py`:
   ```bash
   python3 ~/.claude/scripts/openai_call.py --model gpt-5 \
     --system-file ~/.claude/skills/brf-protokoll/prompts/gpt5-svensk-protokoll.txt \
     --user-file <block> --max-tokens 8000
   ```
   **OBS gpt-5:** `--max-tokens` = `max_completion_tokens` och reasoning-tokens äter budgeten. Kör **per dagordningspunkt/block** (ej hela dokumentet i ett anrop). **Obligatoriskt:** läs stderr; vid `finish_reason != "stop"` höj gräns eller dela mindre och kör om. Foga ihop blocken och säkra tonkonsistens. Prompten bevarar Erikas knappa stil — expandera inte till prosa.
5. **2-agent-verifiering:** spawna två oberoende agenter som var och en granskar utkastet mot (a) transkriptet (varje beslut/namn/siffra stöds), (b) formkraven ovan, (c) svensk språkkvalitet — var och en ger **confidence 1–10**. Iterera tills **båda ≥8** (mellan omgångar: åtgärda granskarnas punkter och kör om; max 2 omgångar; annars lyft till Henrik med kvarstående punkter).
   - **Fallback om Task-spawning ej är tillgänglig** (skillen körs av en redan spawnad agent): kör de **två granskningspassen sekventiellt in-line** mot samma checklista och **flagga i output att de inte var oberoende spawnar**. (Tröskel ≥8 medvetet vald; projektnorm.)
6. **Skriv utkast** till mötesmappens `protokoll/` som `<beskrivning> - utkast.md`. Skriv ej över Erikas docx.
7. **Husstils-finalisering (valfritt, när utkastet är klart):** producera slutprotokollet som **.docx i föreningens husstil** (grönt ordmärke, Times/Arial, A4) via föreningsmallen:
   ```sh
   pandoc "<utkast>.md" --reference-doc "Kunskapsbas/Mallar/Brf Rudtorp 6 – protokollmall.docx" -o "<protokoll>.docx"
   ```
   Mallen är PII-sanerad och bär logga/sidhuvud/sidfot; genererat protokoll ärver inte metadata. Fyll i ordförande/justerare enligt **Signatär-spärr** ovan. Se `Kunskapsbas/Mallar/README.md`.

## Versionshantering och arkivering (CR-2026-08-19-protokoll-arkiv-rutin)

Mötesmappens `protokoll/` innehåller **den gällande versionen** (`.md`, `.docx`, `.pdf`). Överspelade versioner flyttas till `protokoll/Arkiv/` — **ingenting raderas**; signerade handlingar och tidigare utkast är spår som kan behöva åberopas.

- **Arkivera i samma arbetssteg** som den nya versionen produceras, aldrig "sen".
- **Versionsregel (mekanisk):** versionsnumret i filnamnet höjs när innehållet ändras **efter** att filen skickats för signering eller utskick. Ändringar dessförinnan skriver samma version. (Juni 2026 heter `- v3` av historiska skäl — numret sattes innan regeln fanns.)
- **Arkivnamn bär status** för filer som varit signerade eller utskickade, t.ex. `… - v1 signerad (kasserad av styrelsen ÅÅÅÅ-MM-DD).pdf`. Rena arbetsutkast behåller sina namn.
- **Signerad handling hör hemma i rot,** med `signerat` i filnamnet enligt husets mönster (`… - signerat.pdf`). Osignerade filer bär aldrig det ordet — frånvaron av `signerat` i rot betyder att gällande version ännu inte är påskriven.
- **Undantag — arkivera aldrig:** innehållet i de två mötesmapparna från 2026-05-27 (`Stämmor/2026-05-27 Föreningsstämma/protokoll/`, `Styrelsemöten/2026-05-27 Konstituerande möte/protokoll/`). De är format-facit enligt avsnittet ovan, mapparna är avslutade, och en flytt får skillens egna referenser att sluta peka rätt.
- **Dropbox:** kör hela arkiveringen som **ett** atomiskt bash-anrop med verifierande listning i samma anrop:
  ```sh
  mkdir -p Arkiv && mv -n "<gammal fil>" Arkiv/ && ls -1 . Arkiv/
  ```
  `mv -n` är inte valfritt — namn som `- utkast.pdf` återkommer varje cykel, och utan flaggan skriver `mv` tyst över en likanamnad fil i `Arkiv/`. Listningen ska bekräfta att rot innehåller endast gällande version och att `Arkiv/` fått exakt de flyttade filerna. Stämmer det inte, eller dyker en Dropbox `conflicted copy` upp — lyft till Henrik i stället för att göra om tyst. En `conflicted copy` är aldrig gällande version.

## Hederlighet (gissa aldrig)
- Ohörbart/ostyrkt i transkriptet → markera `[OKLART – verifiera]`. Gissa aldrig namn, siffror, belopp eller beslut.
- Namn/siffror som inte kan styrkas mot transkriptet flaggas för mänsklig kontroll (jfr verifieringsminnets overifierbara namn).

## Dataminimering (GDPR) — boende = lägenhetsnummer, inte namn
Följer föreningens personuppgiftspolicy (`Kunskapsbas/GDPR/Personuppgiftspolicy-FÖRSLAG-2026-05-30.md`). Tillämpas i **destilleringssteget** (steg 2), där du har helhetskontext att skilja boende-i-sak från styrelse-i-roll:
- **Boende identifieras med lägenhetsnummer/objekt, inte namn:** "medlem i lgh XXXX", "hyresgäst i lgh XXXX". Gäller reklamationer, kö-/p-plats-/förrådsärenden, överlåtelser, störningar m.m.
- **Personnummer och känsliga/särskilda kategorier (art. 9, t.ex. hälsa) förs ALDRIG in** i protokoll eller bilaga.
- **Namnändringar/överlåtelser:** protokollet anger lägenhet + att ändring/godkännande skett; **efternamnslistor hör till HSB:s lägenhetsförteckning**, inte protokolltexten. Beslutets giltighet kräver inte namnet i protokollet.
- **Tillåtna undantag:** styrelse i sin roll (närvaro/beslut/justering/ansvar) namnges; en **jävig styrelseledamot** namnges sakligt (krävs för beslutets giltighet). En **jävig boende som inte är ledamot** identifieras med lägenhetsnummer.
- Stämmans röstlängd/Bilaga 1 = personuppgifter → stannar i mötesmappen; läggs aldrig i CR/changelog/coordination-log/KALENDER. När du rapporterar en körning: referera sökväg + pass/fail, **klistra aldrig in protokolltext med riktiga namn i changelog/CR**.

## Signatär-spärr (underskriftsblock)
- **Ordförande OCH justerare fylls med mötets faktiska personer** — kopiera ALDRIG default-namn från MALL/äldre exempelprotokoll. (Korpusens MALL defaultar Joe Martarian som ordförande och Harald Odvik som justerare; mallarna här använder `<ordförande>`/`<justeringsman>`-platshållare som ska fyllas med rätt person.)
- **Ordförande** = aktuell ordförande per **senaste konstituerande protokoll**. **Justerare** = den vid mötet faktiskt valda (roterar per möte).
- Källa för aktuella förtroendevalda: minnet `styrelse-2026-sammansattning` + `Protokoll-historik/2026/Protokoll konstituerande styrelsemöte 2026-05-27.docx`.
- **Joe Martarian avled 2026-01-06 → får aldrig stå som ordförande/justerare i protokoll daterade därefter.** Nuvarande ordförande: **George** (interim från 2026-01-07, ordinarie från 2026-05-27).

## Lägen i korthet
| Läge | Mall | Särdrag |
|---|---|---|
| Stämma (ordinarie) | `templates/stamma.md` | 24-punkts §16-dagordning, rösträttsstycke, Bilaga 1 röstlängd, 2 justeringsmän |
| Stämma (extra) | `templates/stamma.md` | endast punkt 1–9 + anmälda ärenden |
| Styrelse (konstituerande) | `templates/styrelsemote.md` (variant B) | rubrik "PROTOKOLL KONSTITUERANDE STYRELSEMÖTE  BRF RUDTORP 6"; ansvarsfördelning, firmateckning, delegation/attest, Bolagsverket; 1 justeringsman |
| Styrelse (ordinarie) | `templates/styrelsemote.md` (variant A) | rubrik "STYRELSEMÖTE BRF RUDTORP 6"; fast ~18-punkts dagordning, ekonomiblock (Saldorapport: HSB transaktionskonto / Lev skulder / Total skuld), åtgärdslista näst sist; 1 justeringsman. Format fastställt mot historisk korpus 2026-05-30 (CR-2026-05-30-brf-protokoll-validering). |
| Styrelse (extra) | `templates/styrelsemote.md` (variant A) | ordinarie-skelett utan full dagordning — endast öppnande/sekreterare/justering + de ärenden mötet faktiskt tar; valideras separat vid behov |
