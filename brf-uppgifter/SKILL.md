---
name: brf-uppgifter
description: |
  Hantera uppgifter, deadlines och kalenderhändelser för Brf Rudtorp 6 i KALENDER.md (projektroten).
  Använd när en uppgift/deadline ska läggas till eller uppdateras, när uppgifter ska härledas ur ett
  protokoll, eller när Henrik vill se vad som är på gång. KALENDER.md är källan Henriks Chief of staff läser.
---

# brf-uppgifter

Håller `KALENDER.md` i roten av Brf Rudtorp 6-projektet aktuell. Filen är den daterade uppgifts-/deadlinetabellen som Henriks **Chief of staff** läser som "primary, highest-trust source".

## Scope-guard

Denna skill skriver **endast** `KALENDER.md` i `Brf Rudtorp 6`-projektroten. Skriv aldrig kalenderdata i andra projekt. Rör inte medlemsregister i `Kunskapsbas/Medlemmar-kontakt/`.

## Tabellformat

`| Datum (ISO) | Vad | Ansvarig (roll) | Status | Varför/kontext |`

- **Datum:** `ÅÅÅÅ-MM-DD`, eller `Löpande` för poster utan fast datum. (Chief of staff mappar denna kolumn till sitt interna `due_date`-fält; `Löpande` → `null`.)
- **Status:** `open | in_progress | blocked | done` (CoS-kontraktets värden — använd exakt dessa).

## GDPR (hårdregel)

"Ansvarig" anger **enbart roll** som default (Sekreterare, Ordförande, Ekonomiansvarig, Styrelsen, …). Förnamn endast om rollen är tvetydig; **aldrig efternamn eller personnummer**. Skälet: CoS-digesten kan läsas utanför projektet och får inte bli en bakväg för personuppgifter ut ur `Kunskapsbas/Medlemmar-kontakt/`.

## Lägga till / uppdatera en post

1. **Dubblettskydd:** matcha på `Datum` + `Vad` innan du lägger till. Finns posten → uppdatera den (t.ex. statusbyte), duplicera inte.
2. Placera daterade poster under rätt årsrubrik; datumlösa återkommande poster under "Återkommande".
3. Behåll ISO-datum sorterbara.

## Härleda uppgifter ur ett protokoll

När ett protokoll(utkast) bearbetas, skapa en post när protokollet innehåller:
- **(a) framtida datum + åtagande** — t.ex. "Nästa styrelsemöte 2026-06-10" → post med det datumet.
- **(b) åtagande utan eget datum men med ansvar** — t.ex. "Vid nästa möte signerar nya ledamöter tystnadsförbindelse" → post med `Datum` = nästa möte, `Ansvarig` = ansvarig roll.

Sätt `Varför/kontext` till en kort källhänvisning (vilket protokoll/§).

## Statusövergångar

- `open` vid skapande.
- → `in_progress` när arbetet påbörjats.
- → `done` när tillhörande artefakt är klar (t.ex. protokoll signerat) eller deadline passerat **och** åtgärdat.
- → `blocked` när posten väntar på extern part.
- Passerade `done`-poster **behålls** som historik — tas inte bort.

## Chief of staff-koppling

Brf är (eller ska bli) registrerad som "world" i `Chief of staff/worlds.yaml` med `hints: ["KALENDER.md"]`. Ändringar av den registreringen är cross-repo och görs enligt `PROJECT_RULES.md` (initiator-spawns, kollisionskoll, coordination-log). Själva KALENDER.md-underhållet är rent lokalt.
