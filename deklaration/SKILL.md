---
name: deklaration
description: Hjälp med Henriks privata inkomstdeklaration (Inkomstdeklaration 1). Använd vid deklarationsarbete, skatteberäkningar, eller förberedelse av underlag.
argument-hint: "[inkomstår]"
---

**DIRECTORY GUARD**: This skill is for Henrik Thomé's personal tax declarations. The working directory should be under `~/Library/CloudStorage/Dropbox/Privat/Ekonomi/Deklarationer/`.

Du hjälper **Henrik Thomé** (670105-1036) att fylla i sin privata inkomstdeklaration (Inkomstdeklaration 1).

## Personuppgifter

- **Namn:** Henrik Thomé
- **Personnummer:** 670105-1036
- **Kommun:** Solna
- **Kommunalskattesats:** ~29,75% (kontrollera aktuellt år)
- **Begravningsavgift:** ~0,28% (kontrollera aktuellt år)
- **Tillhör:** Enbart begravningsavgift (ej medlem i trossamfund)
- **Arbetsgivare:** Sonetel AB (publ)
- **A-kassa:** Ledarnas arbetslöshetskassa

## Mappstruktur

Deklarationer lagras i: `Deklarationer/Inkomståret YYYY/`

Typisk struktur:
```
Inkomståret YYYY/
  Deklaration/
    Ifylld deklaration/     <- Slutgiltig ifylld deklaration
    Underlag/
      Deklarationsblankett/ <- Blankett från SKV
      Erlagda räntor/       <- Räntesammanställningar
      Mottagna räntor/      <- Ränta från SGC m.fl.
      [Övriga underlag]/
  Jämkning/                 <- Eventuell jämkning
  Slutlig skatt/            <- Slutskattebesked
```

## Återkommande poster varje år

### 1. Inkomster - Tjänst (avsnitt 1)
- **1.1 Lön:** Från Sonetel AB (publ). Förifyllt av SKV.

### 2. K10 - Fåmansföretagsandelar (blankett K10)
- **Företag:** Swedish General Consulting Aktiebolag (556071-0229)
- **Andelar:** 1 000 av 1 000 (100% ägare)
- **Metod:** Förenklingsregeln (alternativ 1)
- **Historik:** Ingen utdelning tas ut. Sparat utdelningsutrymme ackumuleras.

**Sparat utdelningsutrymme (historik):**
| Inkomstår | Sparat utdelningsutrymme till nästa år |
|-----------|---------------------------------------|
| 2022      | 2 761 560                             |
| 2023      | 3 093 231                             |
| 2024      | 3 471 396                             |

**Beräkning av K10 med förenklingsregeln:**
1. **1.1** Årets gränsbelopp = schablonbelopp (fastställs av SKV varje år) x (ägda andelar / totala andelar)
2. **1.2** Sparat utdelningsutrymme från föregående år x uppräkningsfaktor (fastställs av SKV)
3. **1.3** = 1.1 + 1.2 = Gränsbelopp
4. **1.5** = 1.3 - 1.4 (normalt 0) = Gränsbelopp att utnyttja
5. Om utdelning = 0: **1.9** = sparat utdelningsutrymme = 1.5 (negativt = sparas)
6. **1.11** = sparat utdelningsutrymme till nästa år

**Årets schablonbelopp och uppräkningsfaktorer:**
| Inkomstår | Schablonbelopp (1.1) | Uppräkning sparat utd.utr. |
|-----------|---------------------|---------------------------|
| 2022      | 187 550 kr          | x 103,23%                 |
| 2023      | 195 250 kr          | x 104,94%                 |
| 2024      | 204 325 kr          | x 105,62%                 |

OBS: Schablonbeloppet och uppräkningsprocenten för aktuellt inkomstår måste slås upp på Skatteverkets webbplats.

### 3. Ränteutgifter (avsnitt 8)

**Förifyllda av SKV (från kontrolluppgifter):**
- Bolåneräntor (Danske Hypotek, Stadshypotek m.fl.)
- Kreditkort/blancolån (American Express, Danske Bank, SHB)

**Manuella tillägg (ej förifyllda - VIKTIGT):**
Henrik har privata lån där ränta betalats som SKV INTE känner till:

1. **Lån till Anna Tulldahl** - Henrik betalar ränta till Anna. Underlag finns i mappen `Erlagda räntor/Lån Anna Tulldahl/`. Se Excel-sammanställning.
2. **Lån till Bo Thomé (Henriks pappa)** - Henrik betalade ränta till Bo. Underlag finns i `Erlagda räntor/Lån Bo Thome/`. **OBS: Lånet slutbetalades under 2025.** Ränta för den del av 2025 lånet var aktivt ska beräknas och deklareras.

Dessa räntor ska **adderas** till de förifyllda ränteutgifterna i ruta 8.1 (lån med säkerhet) eller 8.8 (lån utan säkerhet, nytt fr.o.m. 2025).

**NYTT FR.O.M. INKOMSTÅR 2025:** Ruta 8.1 avser nu enbart "lån med säkerhet" och ny ruta **8.8** gäller "lån utan säkerhet" (blancolån, kortkrediter, privatlån). Avdrag för lån utan säkerhet medges med halva beloppet.

### 4. Ränteinkomster (avsnitt 7.2)

**Förifyllda:** Bankräntor (SBAB m.fl.)

**Manuella tillägg:**
- **Ränta från Swedish General Consulting AB** - Henrik har ett lån till SGC och mottar ränta. Underlag finns i mappen `Mottagna räntor/`.

### 5. Fastighetsavgift (avsnitt 5)
- **GÅSÖ 3:104** - Småhus, 100% ägarandel. Förifyllt av SKV.
- Takunderlaget fastställs årligen av SKV.

### 6. Skattereduktioner (avsnitt 4)
- **ROT/RUT** - förifyllt av SKV om anlitade företag rapporterat.
- **A-kassa** - skattereduktion 25% av avgift, hanteras automatiskt.

## Poster som varierar mellan år

### Kapitalvinster/-förluster
- **2024:** Försäljning av fastighet Gåsö 3:104 (blankett K5). Vinst 6 887 734 kr -> ruta 7.6.
- **2025:** Försäljning av bostadsrätt BRF Ankdammen 33 lgh 1601 (blankett K6).
  - **Avtalsdag:** 2025-11-28 (skattemässig tidpunkt = inkomstår 2025). Tillträde 2026-01-16.
  - **Ägarandelar:** Karima 40/100, Henrik 60/100 (köpt 2017: Karima 4/10, Henrik 6/10)
  - **Total köpeskilling köp (2017):** 4 750 000 kr. Henrik 60% = 2 850 000, Karima 40% = 1 900 000
  - **Total köpeskilling försäljning (2025):** 4 500 000 kr. Henrik 60% = 2 700 000, Karima 40% = 1 800 000
  - **Försäljningsutgifter:** Mäklararvode 55 000 + Hemnet Premium 8 990 = 63 990 totalt
  - **Kapitaltillskott:** Totalt 251 842 kr för lgh 1601 (SKV förifyllde 125 921 = 50%, men ägarandelarna är 60/40)
    - Henrik 60%: 151 105 kr
    - Karima 40%: 100 737 kr
    - **OBS:** Att verifiera mot BRF:ens årsredovisningar (amorteringsdata 2017-2025)
  - **OBS:** SKV:s förifyllda uppgifter baserades genomgående på 50% ägarandel (fel). Korrigerat till 60/40.
  - **Henriks K6:** 2 700 000 - 38 394 - 2 850 000 - 151 105 = **-339 499** (förlust)
  - **Karimas K6:** 1 800 000 - 25 596 - 1 900 000 - 100 737 = **-226 333** (förlust)
  - Karima lämnar egen K6 i sin deklaration.
- **2025:** Försäljning av sjötomt Gåsö 3:140 (blankett K5, privatbostadsfastighet).
  - **Fastighet:** Nacka GÅSÖ 3:140, Söderuddsvägen 24B, 133 37 Saltsjöbaden
  - **Köpare:** JA Liquid AB (556916-7728)
  - **Avtalsdag:** 2025-11-10. Tillträde: 2025-11-18.
  - **Historik:** Hela Gåsö 3:104 ägdes av Henrik (via bodelning 2017). Bestod av:
    - Ursprungliga 3:104, köpt ~1996 för 825 000 kr
    - Gamla 3:103, köpt ~2000 för ~1 200 000 kr, sammanslagen med 3:104
    - Avstyckning 2024-12-19: nya 3:104 (3 702 m²) + nya 3:140 (4 360 m²)
    - 3:104 såldes 2024 (K5 2024, inköpspris 825 000 = ursprungliga 3:104)
    - 3:140 motsvarar gamla 3:103 → inköpspris ~1 200 000 (exakt belopp i pärm på ön)
  - **Försäljningspris:** 4 750 000 kr
  - **Försäljningsutgifter:** Mäklare 100 000 + Hemnet 6 975 + strandskyddsdispens 8 838 + advokat ~35 000 = ~150 813
  - **Inköpspris:** ~1 200 000 (TBD exakt)
  - **Förbättringsutgifter:** Att inventera
  - **Preliminär vinst:** ~3 399 187
  - **Skatt 22%:** ~747 822
  - **OBS:** Förrättningskostnad 117 350 redan avdragen i K5 2024
- **2023:** Hyresintäkter 89 249 kr -> ruta 7.3. Hyresintäkter netto efter schablonavdrag.

### Arv
- **2025:** Arv efter Henriks mamma, ca 1,3 MSEK. Arv är skattefritt i Sverige och ska INTE deklareras. Dock kan eventuella inkomster från ärvda tillgångar (räntor, utdelningar) behöva deklareras.

### Bostadsköp
- **2025:** Henrik och fru Karima köpte ny lägenhet Framnäsbacken 1 LGH 1201, 171 66 Solna. Relevant för eventuellt uppskov vid bostadsförsäljning (K6).

### Allmänna avdrag
- **2022:** Socialförsäkringsavgifter enl. EU-förordningen 220 000 kr i ruta 3.1

## Arbetsprocess - steg för steg

### Steg 1: Samla underlag
1. Läs SKV:s förifyllda blankett (Inkomstdeklaration1_YYYY_196701051036.pdf)
2. Läs specifikation och kontroll-/inkomstuppgifter
3. Läs preliminär skatteberäkning
4. Identifiera vilka tillägg/ändringar som behövs

### Steg 2: Identifiera manuella tillägg
Kontrollera om det finns underlag för:
- [ ] Erlagda räntor till Anna Tulldahl (finns sammanställning?)
- [ ] Erlagda räntor till Bo Thomé (finns sammanställning? OBS: slutbetalat 2025, beräkna delårsränta)
- [ ] Mottagna räntor från SGC (finns underlag?)
- [ ] Hyresintäkter (om tillämpligt)
- [ ] Kapitalvinster/-förluster (försäljningar av bostad/fastighet/tomt)
- [ ] K10 för SGC (beräkna nytt gränsbelopp)
- [ ] Arv (skattefritt, men kontrollera inkomster från ärvda tillgångar)

### Steg 3: Fyll i blanketter
1. **Inkomstdeklaration 1** - Huvudblanketten med alla belopp
2. **K10** - Kvalificerade andelar SGC (förenklingsregeln)
3. **K5** - Om fastighet sålts
4. **K6** - Om bostadsrätt sålts
5. Andra bilagor efter behov

### Steg 4: Beräkna skatten
Kontrollera att beräknad skatt stämmer med förväntningarna. Viktiga komponenter:
- Kommunal inkomstskatt (~29,75%)
- Statlig inkomstskatt (20% på förvärvsinkomst över brytpunkt, 2025: ca 615 700 kr)
- Kapitalskatt (30% på överskott av kapital)
- Skattereduktion för underskott av kapital (30% på första 100 000 kr, 21% på resten)
- Fastighetsavgift
- Pensionsavgift, begravningsavgift, public service-avgift

### Steg 5: Verifiera
- Jämför med Skatteverkets preliminära beräkning
- Räkna ut förväntad kvarskatt
- Kontrollera att alla bilagor stämmer med huvudblanketten

## Deadlines och betalning

- **Deklaration ska vara inne:** Senast 2 maj (normalt) eller 4 maj 2026 för inkomstår 2025
- **Betalning kvarskatt > 30 000 kr:** Bör betalas senast 12 februari för att undvika kostnadsränta
- **Betalning kvarskatt upp till 30 000 kr:** Senast 2 maj
- **Bankgiro:** 5050-1055
- **OCR-nummer:** 1967010510369

## Redovisningsbyrå (historiskt)

Tidigare år har deklarationen lämnats till **Petra Kratz** (Kratz Redovisning):
- E-post: petra@kratzredovisning.se
- Tel: 070-4504392
- Adress: Krossgatan 25, 162 50 Vällingby
- Använde: Visma Skatt Proffs

Fr.o.m. inkomstår 2025 gör Henrik deklarationen själv.

## Viktiga påminnelser

1. **Privata räntor glöms lätt bort** - Alltid kontrollera om det finns underlag för räntor till Anna Tulldahl och Bo Thomé
2. **K10 ska alltid lämnas** - Även om ingen utdelning tagits ut, för att spara utdelningsutrymme
3. **Kontrollera schablonbelopp** - Ändras varje år, slå upp aktuellt på skatteverket.se
4. **Nya adress:** Fr.o.m. 2025 bor Henrik på Framnäsbacken 1 LGH 1201, 171 66 Solna (köpt tillsammans med fru Karima)
5. **Gåsö 3:104 såldes 2024** men ska fortfarande finnas som underlag för fastighetsavgift 2025 (ägt del av året eller helåret beroende på tillträde)
6. **Arv är skattefritt** - Behöver inte deklareras, men inkomster från ärvda tillgångar ska deklareras
7. **Lån till Bo Thomé slutbetalat 2025** - Beräkna ränta för den aktiva perioden
8. **Fru:** Karima (relevant vid samägande av bostad, omfördelning av skattereduktioner m.m.)
