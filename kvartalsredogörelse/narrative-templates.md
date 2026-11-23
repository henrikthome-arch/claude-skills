# Textmallar — Kommentarer kring verksamheten

Mönstren är hämtade ur **två** publicerade rapporter, inte en: halvårsrapporten jan–jun 2025
(sidorna 6–10) och Bokslutskommunikén FY24-25 v21 (sidorna 7–9). Det som återkommer i båda är
mall; det som bara finns i en är en engångsformulering och ska inte kopieras.

`{slot}` fylls från `data.json` eller från tabellerna. Alla tal ska vara härledda, aldrig
inskrivna för hand — se avsnittet *Derived figures are computed, never typed* i SKILL.md.

---

## Genomgående stilregler

Belagda i båda källorna:

- **Jämförelsetalet i parentes direkt efter.** "uppgick till 25,3 MSEK (25,8)".
- **Procenttal med tecken.** "+54%", "-16%". Minskningar bär minustecken (Henrik 2026-08-20).
- **"under perioden" / "vid periodens slut"** — flöde respektive ställning. Blanda aldrig.
- **Förklara alltid en förändring i samma stycke som talet.** Källorna anger orsak omedelbart:
  *"Ökningen drevs primärt av…"*, *"Förbättringen på 3,6 MSEK berodde primärt på…"*,
  *"Kostnadsökningen berodde primärt på…"*. En siffra utan orsak är inte färdigskriven.
- **Ca-tal när precisionen inte bär.** "ca 78%", "ca 7 USD per månad".
- Aldrig superlativ om marknaden eller egen prestation utan tal bakom.

---

## Intäkter

> Bolagets försäljning under perioden {period} {förändring} till {nettoomsättning} MSEK, jämfört
> med {jämförelse} MSEK samma period föregående år. Intäkterna kom från kunder i ca 170 länder.
> De största marknaderna är {marknader}. Huvuddelen av intäkterna består av abonnemangsintäkter
> (ARR).

Bokslutskommunikén lägger till, när det är relevant: andel utanför Sverige, andel Nordamerika,
snittintäkt per kund, samt att tjänsterna förbetalas.

**När kvartalet avviker från halvåret ska båda anges.** Det är nytt för jan–jun 2026 och följer
av att sammandraget nu har två block.

## Virtuella telefonnummer

> Antalet abonnemang för virtuella telefonnummer {förändring} jämfört med året innan. Abonnemang
> för virtuella telefonnummer representerar {andel}% av tjänsteintäkterna.

Bokslutskommunikén utökar med bruttomarginal per tjänst och prispunkt, samt hänvisar till grafen:
*"Grafen nedan visar antal telefonnummerabonnemang vid respektive kvartals slut."*

## Premium och Business

> Ca {andel}% av kunderna hade tilläggstjänsterna Premium eller Business vid periodens slut,
> vilket kan jämföras med {andel föregående}% ett år tidigare. Antalet Premium- och
> Businesskunder var vid periodens slut {förändring} jämfört med ett år tidigare. Premium och
> Business stod vid periodens slut för ca {andel}% av tjänsteintäkterna.

## Årligt återkommande intäkter (ARR)

> Det årliga värdet av samtliga aktiva kundabonnemang (ARR) uppgick vid periodens slut till
> {arr} MSEK ({jämförelse}), {förändring}. Räknat i USD – bolagets huvudsakliga valuta för
> intäkter – {förändring USD} till {arr MUSD} MUSD ({jämförelse}).

**Ange alltid både SEK och USD.** Båda källorna gör det, och skillnaden mellan dem är
valutaeffekten — som i en period med rörlig dollar är en väsentlig del av förklaringen.

## Bruttomarginal

> Bruttomarginalen på bolagets samtliga SaaS-tjänster låg på ca {marginal}% vilket var
> {förändring} från {jämförelse}%.

## Kostnader

> Bolaget hade under perioden kostnader på {kostnader} MSEK vilket kan jämföras med {jämförelse}
> MSEK under samma period föregående år. {Orsak till förändringen.}

Bokslutskommunikén punktar de väsentligaste posterna med belopp och orsak per post. Använd
punktform när fler än två poster rör sig materiellt.

## Investeringar

> Bolaget gjorde under perioden ca {investeringar} MSEK i investeringar i utvecklingen av
> bolagets tjänster vilket kan jämföras med ca {jämförelse} MSEK samma period föregående år.

## Resultat

> Koncernen redovisade under perioden ett resultat före skatt på ca {resultat} MSEK vilket kan
> jämföras med ca {jämförelse} MSEK under samma period föregående år. {Förklaring av
> förändringen med belopp.}

Bokslutskommunikén lägger till en justerad rad när valutakursdifferenser på koncerninterna
skulder är materiella: *"Justerat för valutakursdifferenser på koncerninterna skulder uppgick
resultatet före skatt till…"*. **Relevant för jan–jun 2026**, där valutakursförluster på 0,64
MSEK ligger i rörelsekostnaderna.

## Kassaflöde

> Kassaflödet från den löpande verksamheten var ca {kassaflöde} MSEK under perioden. Detta kan
> jämföras med ca {jämförelse} MSEK under samma period föregående år. {Förklaring.}

## Kundanskaffning

> {antal} nya betalande kunder inkom under perioden. Det är {förändring} än under samma period
> föregående år. Kundanskaffningskostnaden (CAC) för samtliga nya kunder låg under perioden i
> snitt på ca {cac} SEK, vilket kan jämföras med ca {jämförelse} SEK samma period föregående år.
> Återbetalningstiden för kundanskaffningskostnaden per ny betalande kund var {återbetalningstid}
> i snitt under perioden.

Följs av tabellen **AKTIVA KUNDER** med fem månadsslut.

## Kundbetyg

> Sonetels kundbetyg på Trustpilot låg vid periodens slut på {betyg} av 5 möjliga
> ("{omdöme}"). Detta kan jämföras med {jämförelse} vid samma tidpunkt föregående år.
> {Förklaring vid förändring.}

Halvårsrapporten jan–jun 2025 är förebilden för hur en försämring hanteras: orsakerna räknas upp
rakt, inklusive egna brister — *"bolagets mobila appar kvalitetsproblem som gör dem långsamma och
svåranvända"* — och avslutas med vad som görs åt saken. Den öppenheten är stilnorm, inte undantag.

---

## Var skillen ska skriva kompletterande text själv

Mallen fyller i det återkommande. Utöver det ska en analys göras och text läggas till när något
av följande gäller:

| Utlösare | Vad som ska skrivas |
|---|---|
| **Kvartalet avviker väsentligt från halvåret** | Ange båda. För jan–jun 2026: omsättningen −4% på halvåret men −16% i kvartalet, samtidigt som kvartalet var mer lönsamt än halvåret. Utan båda talen är bilden falsk åt något håll |
| **En post ändras kraftigt utan uppenbar orsak** | Undersök i huvudbok, specifikationer eller finops innan texten skrivs. Övriga rörelsekostnader gick 7 tkr → 639 tkr för jan–jun 2026; svaret, valutakursförluster på konto 7960, fanns i saldolistan |
| **En trend vänder** | Namnge vändpunkten och storleken. ARR toppade i oktober 2025; kundbasen i januari 2026 |
| **Ett tal är koncentrerat till få enheter** | Skriv ut koncentrationen. 93% av ARR-nedgången jan–jun 2026 låg hos en enda grossistkund |
| **Föregående rapport lovade något** | Rapportera tillbaka. 4.4.6(h) kräver framtidsinformation jämförd med föregående rapport, och jan–jun 2025 utlovade AI-orchestrators, femdubblad effektivitet och nya mobilappar |
| **Ett mått bytt källa eller definition** | Flagga att jämförelsen inte är strikt jämförbar |
| **Valutan förklarar en väsentlig del** | Ange både SEK och USD. För jan–jun 2026 föll SEK-omsättningen medan den fakturerade USD-omsättningen steg |

**Och motsatsen — skriv inte:**

- Tal som inte går att belägga ur en dokumenterad källa
- Förbättringar i ett delsteg när utfallet nedströms inte rört sig
- En orsak som inte finns i datan. *"Bolaget arbetar med att…"* är bättre än en gissad förklaring
