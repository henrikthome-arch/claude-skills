# Image style — Sonetel Kvartalsredogörelse (cover + Affärsmodell scene + VD-banner)

This applies to **all three photographic positions** in the Kvartalsredogörelse:
1. **Cover (page 1)** — full-bleed photo, white overlay text in lower-left
2. **VD-banner (page 3)** — wide cropped header, B&W via CSS filter (so prompt can be color)
3. **Affärsmodell scene (page 4)** — bottom-half illustrative image, full-bleed horizontal

Each position has its own framing requirements (cover = portrait 9:16, Affärsmodell = landscape 16:9, banner = wide horizontal — generally use 16:9 and let the CSS crop), but they share **the same brand voice**: editorial documentary photography, real entrepreneurs in real contexts globally, never stock-photo or motivational-poster aesthetic.

This file forks the original `sonetel-image-generator-skill`'s `brand/visual-style.md` and `brand/prompt-rules.md`. When the two diverge, this file wins for Kvartalsredogörelse images.

---

## VARIATION IS THE RULE — DO NOT FALL INTO TROPES

**Hard learned 2026-05-13**: the first generated Affärsmodell image was a rainy-night Hanoi street scene with a Vietnamese woman on a phone (because the published v1.0 jul-sep 2025 used that exact composition). Reusing the same setting across quarters made the next Kvartalsredogörelse look like the previous one — exactly the opposite of what a real business wants.

**Henrik's correction**: "the rule isn't 'always a woman in rain with cars'. No company wants nearly identical motifs every quarter."

### One picture per report should meet the reader's eye (Henrik 2026-08-21)

*"Det är bra om någon bild i varje rapport har något foto där personen tittar in i kameran."*
Everything else in the set can be observed-from-outside; one frame should look back. It gives the
report a person in it rather than a series of scenes. nb2 is the model for this — eye and
expression detail is exactly what it is documented as being better at.

### Variation applies WITHIN a report too, not only between quarters (Henrik 2026-08-21)

The rule below was written about consecutive quarters, and reading it that narrowly produced the
mistake it exists to prevent: the halvårsrapport jan–jun 2026 got a Faroe Islands photograph for
the VD-ordet that was, next to its own cover, near-identical — **a lone woman standing beside a
pickup with a phone in a vast empty landscape, muted palette**. Only the ground cover differed,
sand for grass. Henrik: *"it is almost identical to cover page."*

Before generating any picture, **lay out every other photograph in the same report** and check
each axis separately. Two pictures may share at most one:

| Axis | Ask |
|---|---|
| Subject | Same gender? Same rough age? Aim for a mix across the set |
| Posture & action | Both standing? Both phone-to-ear? Vary it. **This axis got missed** on the halvårsrapport jan–jun 2026: the cover's woman and the VD-ordet's man both stood upright in profile with a phone, and Henrik caught it after the table above had already been written. Seating the man on a rock fixed it. Writing the checklist is not running it |
| Gaze | Looking away, or into the lens? |
| Hero prop | A vehicle in both? A counter in both? A vehicle is a *very* strong visual signature — do not repeat one |
| Composition | Lone figure dwarfed by emptiness, versus structure and depth, versus a group, versus an interior |
| Palette & light | Both cold and muted? Both warm and golden? |
| Inside / outside | |

Emptiness is the trap. A vast landscape with one small person is a strong, satisfying composition,
which is exactly why it gets reached for twice.

### The 5–20% framing rule is also what keeps the picture from looking AI-generated

Henrik, 2026-08-21, on a Faroese picture with the subject at roughly half the frame height:
*"something is off — AIish. Can't say what."* Enlarged, three things had broken, and all three
break **only at close range**:

- **Hands.** The hand resting on a pole merged into the wood with no thumb wrapping it. The hand
  holding the phone was mush. Hands touching objects are the single most reliable failure.
- **Repeating structures do not resolve.** The fish-drying racks passed through each other and
  emerged from the face of a plank with no joint. Any dense lattice — racks, scaffolding,
  railings, fences seen close — will fail somewhere.
- **Objects hang from nothing.** Strings ran through the poles and stopped in mid-air; the fish
  were attached to nothing.

These break only at close range. The cure is distance, not prompt language: at 5–20% of frame
height a hand is a few pixels and cannot be wrong.

**When a picture reads as "off" but nobody can say why, crop into it at 3× and look at hands,
joints and attachment points before regenerating.** Naming the defect gives you the corrective
prompt; guessing gives you another bad picture.

**BRIEF THE IMAGE MODEL SHORT. This is the most important line on this page.**

Henrik, 2026-08-21, after a prompt that specified the exact grip: *"No one holds their phone like
that. I think you are overengineering again, and micromanaging the skill instead of giving it more
free reins."* He was right twice over — the picture *and* this guide had both been over-specified.

Prescribing anatomy produces anatomy that is technically compliant and humanly wrong. "A simple
relaxed closed fist, fingers together, curled around the phone, none touching the face" produced a
man gripping his phone like a walkie-talkie. The fix was a **two-sentence brief**:

> Editorial documentary photograph. A Faroese village of black timber houses with turf roofs on a
> green slope above a fjord, basalt mountains disappearing into mist. A man in a worn jacket stands
> on the grass taking a call on his mobile, looking out over the water. Overcast Nordic light.
> No text or signage anywhere.

That gave a natural grip, a legible phone and a better photograph, first try.

**Say the subject, the place, the light, the photographic direction, and the one or two things that
must not appear.** Nothing else.

Photographic direction — *35mm at f/5.6, deep depth of field, natural light, one small figure in a
large landscape* — is **style, and it belongs in the brief.** It is how the house tells the model
what kind of photograph this is. Finger positions, grip descriptions and elbow angles are
**micromanagement, and they belong nowhere.** The difference: direct the camera, never the body. This is the same rule that already governs briefing GPT-5 for the VD-ordet: give a skilled
professional the material and the boundaries, not a list of conditions. Reach for more prompt only
when a *specific named defect* has to be forbidden — and then add one clause, not a paragraph.

**Keeping a setting is fine; keeping the setting's inhabitants is not.** When a picture is rejected
for resembling another, the place usually is not the problem — Henrik kept the Faroes and asked for
everything else to change. What actually made the two pictures twins was the triad he named:
**"car + object + woman."** The fix was a man instead of a woman, no vehicle at all, timber drying
racks and turf roofs filling the frame instead of open sky, and a phone held in the hand and looked
at rather than pressed to an ear. Same islands, unmistakably a different photograph.

### The business must be legible — lessons from the jul–sep 2026 cover (Henrik 2026-11-17)

Eight rounds to one approved cover, and every rejection came down to one of four things:

| Rejected because | Fix that worked |
|---|---|
| *"Why is she overweight and sloppy dressed … she can just as well be a shopper ordering too much"* — the brief named no attire and no business, so the model chose both | State the role **and** the dress in the brief: *"the owner of an online shop … in a tailored suit"* |
| A packing table **in the road / on the lawn** — *"why stand in the middle of the road packaging boxes?"* | Give the work a plausible place: a garage converted into a stockroom, door open. Flux ignored "on the porch" three times out of three |
| The garage read as household storage, not a business | Name what makes it a business: *"rows of shelving with neatly stacked product boxes, a packing table with a tape dispenser and shipping supplies, outgoing parcels"* |
| *"Ganska tråkig"* at 5–20% frame height | Henrik overrode the distance rule for this cover: subject at ~⅓–½ of frame height, smiling toward the camera, street receding beside her. The approved cover is closer than this guide's default — the guide's rule is a default, the person reviewing decides |

Two recurring Flux defects on a "business call" brief: **a second phone in the other hand** (5 of 9
takes) and **a visible Apple logo** on a laptop. One clause each fixed them: *"one phone held to her
ear"*, *"no brand marks on any device"*. Also: the cover title sits over the lower ~15% of the page —
when the subject stands full-figure there, render the candidates as actual covers before choosing
(`omslag-jamforelse-*.png` in the period's `bilder-utkast/`).

### Variation requirements (every quarter must differ from the last)

- **Geography**: pick a different continent / city per quarter. Rotate through Sonetel's 170-country reach.
- **Time of day / weather**: golden hour, blue hour, dawn, mid-afternoon, dusk, sunny, overcast — but never the same as the previous quarter.
- **Gender / age / ethnicity**: vary explicitly. Track the last 2-3 quarters and pick complementarily.
- **Setting type**: rotate through café / market / rooftop / co-working / street / port / studio / atelier / workshop / restaurant / bookshop / tech-hub / public space.
- **Posture & action**: phone-to-ear, phone-in-hand-checking, phone-on-table-being-glanced-at, walking-and-on-call, leaning-and-talking, listening-while-others-talk-around — vary.
- **NOT EVERY IMAGE NEEDS RAIN, CARS, NEON, OR NIGHT.** That's a single mood among many. Use it sparingly across the calendar year (max 1 of 4 quarters).
- **NOT EVERY IMAGE NEEDS A YOUNG WOMAN.** Mix in male subjects, older subjects, etc. Sonetel's customers are SMB entrepreneurs of every demographic.

### "Entrepreneur on phone" composition rules

The subject should read clearly as **an entrepreneur or small-business owner using a phone in their working context** — not a tourist, not a posed model, not a busy-businessperson stock-photo. Concrete:

- **In their workspace** (café they own, atelier, market stall, fishing dock, repair shop, design studio, kitchen, farm) — not in some unrelated tourist setting
- **The phone is naturally part of the moment** — checking inventory, taking a customer call, glancing at a notification, dictating a note — not posed-with-phone
- **Real-world props**: open laptop nearby, scattered receipts, half-drunk coffee, tools, samples, paperwork, food, kids' drawings on the wall, plants, hand-written signs — the texture of actual work


## SETTINGS: GO FURTHER THAN SHOPS AND OFFICES (Henrik, 2026-08-19)

**Henrik's steer, verbatim: _"Butiker och kontor är rätt gammaldags."_**

The approved-settings list below skews to cafés, shops, ateliers and market stalls. That is too
safe and too domestic. The product is that a business is reachable **anywhere** — so the setting
should make that point, not merely provide a backdrop. Extreme, remote or vivid environments say
more about Sonetel than a well-lit café ever will.

Settings Henrik proposed, all sanctioned:

| | |
|---|---|
| A desert — vast dunes, a folding table, a pickup | Used for the halvårsrapport jan–jun 2026 cover |
| An auto-rickshaw in India, working from the cab | Used for that report's affärsmodell image |
| The Faroe Islands — fish-drying racks among turf-roofed timber houses | Used for the halvårsrapport jan–jun 2026 VD-ordet closing photograph. Chosen because the other three pictures were desert, South Asia and Latin America — **no Western-recognisable setting at all**, in a report whose two largest markets are the USA and Canada. Check the whole set against the audience-balance rule, not just the cover/affärsmodell pair. The *setting* survived two attempts; the first take had to be thrown out because its **subject, prop and composition** copied the cover (see the within-report rule above) |
| A colour festival in India | |
| The Siberian tundra | |
| The Faroe Islands | |
| An artisan cooperative in Guatemala | |
| A beekeeper in the Greek mountains | |
| A jungle | |
| An endless construction site | |
| A futuristic environment | Watch the guide's existing cyberpunk/neon anti-trope |

**What does NOT change:** the framing discipline. Wide environmental shot, the setting as
protagonist, the person at 5–20% of frame height, 28–35mm at f/4–5.6, deep depth of field, clear
lower third, no text. The halvårsrapport cover works precisely because the emptiness of the dunes
is the subject and the woman is a small deliberate mark within it. Boldness belongs in the
*choice of place*, not in moving the camera closer.

**Audience-balance rule still applies** — at least one Western-recognisable setting per pair. The
Faroes, Greek mountains and Siberian tundra all satisfy it while being far from a café window.

### Approved variety palette (rotate, don't repeat consecutive quarters)

| Setting type | Examples |
|---|---|
| Café/bookshop owner | Mexico City corner café at morning; Cairo bookshop in late afternoon |
| Market vendor | Lagos textile market stall mid-morning; Hanoi flower market dawn; Mumbai spice market afternoon |
| Atelier / studio | Marrakech leather atelier; Istanbul fabric studio; Buenos Aires woodworking workshop |
| Rooftop / terrace | Athens rooftop golden hour; Lima rooftop blue hour; Tel Aviv terrace at dusk |
| Restaurant / kitchen | Naples trattoria mid-service; Hanoi street-food stall lunch hour; Bangkok khao-soi shop |
| Co-working / tech hub | Bangalore courtyard co-working golden hour; Tallinn loft co-working morning; Mexico City Roma Norte loft |
| Outdoor working | Cape Town fishing dock at dawn; Casablanca farm stand afternoon; Hanoi rural roadside stall |
| Window / interior | Stockholm winter, person at café window with phone, snow outside; Lisbon azulejo café window late afternoon |
| Street vendor mid-day | Manila street vendor at noon; Lagos roadside stand; Karachi tea cart at mid-afternoon |

The previous quarter's image should never share the same **city** or same **weather/lighting**. If Q1 used Athens dusk, Q2 should NOT use Lima dusk — different city AND different time of day.

### Anti-tropes (explicit avoid list)

- ❌ Rainy night urban street with neon (used in v1.0 jul-sep 2025 — retire this until 2027 at earliest)
- ❌ Single young woman as default — too predictable; rotate
- ❌ "Cyberpunk" / neon-heavy / hyper-stylized look
- ❌ Anything that reads "stock photo: hustle culture"
- ❌ Phone close-up with screen glow as hero — the entrepreneur and setting are the hero
- ❌ Reusing the same setting from the last 3 quarters

### Audience-balance rule — mix Western and non-Western per quarter

**Audience reality**: the primary reader is a Swedish private retail investor on Avanza/Nordnet (per VD-ordet style guide §10 audience). They identify more easily with European/Western settings — but Sonetel's value proposition is global reach. The right mix per quarter:

- **At least ONE Western-recognizable setting** (Mediterranean Europe, Northern Europe, North America, Latin America cities with Western-looking architecture)
- **At least ONE non-Western setting** to express the 170-country reach
- For Q1 jan-mar 2026: cover = Lisbon (Western); affärsmodell = Marrakech (non-Western) → balanced ✓

**Picking the mix per quarter**: cover is the high-visibility position; default to Western there since the cover sets the tone. Use Affärsmodell or VD-banner positions for non-Western variety. If only one photographic position is used in a given quarter (e.g. minimal layout), default to Western.

**Avoid**: an entire quarter where ALL images are non-Western — readers may perceive the company as "exotic outsourced" rather than "Swedish capital-light SaaS with global customers".

### AI-image anatomy quality control (mandatory check before slotting)

**Repetition is a tell, and it shows up in the SCENE as well as in hands.** Henrik, 2026-08-21:
*"husen i bilden ser perfekt likformiga ut. Liknar AI."* The model had drawn one house and
repeated it across the whole village.

**But the cure is fewer words, not more.** Answering that note with a sentence specifying every
variation — *"black tarred timber beside white and ochre and deep red, turf beside corrugated iron
and slate, small old cottages beside larger newer houses"* — produced a catalogue of house types
arranged like a sample chart. Henrik: *"Now it looks like a cluttered sample view of houses. Can
you let the model free?"*

What worked was deleting almost everything:

> Editorial documentary photograph, 35mm at f/5.6. A village on the Faroe Islands above a fjord.
> A man stands on the grass talking on his phone. Overcast light. No text.

Three takes from that brief, pick the best one. The village came out varied and settled because
that is what villages look like and the model knows it — it only produced a module when told to
produce a module, and a catalogue when told to produce a catalogue.

**The pattern to recognise in yourself:** each critique tempts you to add a clause. Six rounds of
that is how the picture got worse and the guide got longer. When a picture is wrong, first try
saying *less*, and generate three. Only name a defect explicitly when it survives that.

AI image generators (Flux, NB2) frequently fail on:

- **Limb anatomy** — legs twisting unnaturally, knees bent at impossible angles, especially when partially occluded by tables, counters, or benches
- **Hands** — too many fingers, fingers merging into objects
- **Phones** — sometimes appear as a "block" rather than recognizable smartphone; double-check the phone is identifiable
- **Eye focus** — pupils sometimes misaligned, looking in different directions
- **Text on signs** — always garbled; the prompt should already say "no readable text" but verify

**Mandatory check**: open the generated image at full resolution and scan for anatomy artifacts before slotting into data.json. If a leg looks twisted or a hand has wrong fingers, regenerate with a tighter pose constraint:

- For standing poses: *"Standing upright with weight on left leg, right foot planted naturally beside it, both legs visible from knee down, anatomically correct posture"*
- For seated poses: *"Seated naturally with both hands visible, holding the phone in two hands or one hand resting on the table"*
- For walking: *"Mid-stride with one foot fully visible on the ground, the other lifted naturally — clean anatomy"*

If a regeneration still has anatomy issues after 2-3 attempts, pick a different composition entirely (different posture, different framing) rather than fighting the same prompt.

## What this style is

- **Wide environmental shots** — the setting is the protagonist; the human is part of the composition, not the subject of a portrait.
- **Mid-distance to wide framing** — person occupies ~5–20% of the frame height, not 40–60% as in ads.
- **Editorial documentary feel** — Magnum, FT Weekend, Monocle. Not stock, not advertising.
- **Globally varied** — reflects Sonetel's 170-country customer base. Vary geography across quarters.
- **A4 portrait full-bleed** — the image fills the entire cover page. Text overlays the bottom third (period label, report type, tagline, company line).

## What this style is NOT

- ❌ Close-up portrait — the ad-image skill's default. Wrong for a financial report cover.
- ❌ "Slim modern smartphone resting against her cheek" — that closeup grip language is for ads. The phone may not even be visible at this distance, and that's fine.
- ❌ Posed corporate photography — no boardroom shots, no diverse-group-around-table, no stock-photo lighting.
- ❌ Anything with visible text/logos/signage — Flux still mangles those.

## Composition for A4 cover

- **Vertical/portrait orientation** — closest aspect from the model is `9:16` (~0.56 ratio); A4 portrait is ~0.71. The image will be cropped slightly on the sides when stretched to A4 full-bleed; compose with that in mind (keep critical content in the central column).
- **Bottom third must be clear-zone** — that's where the title, period label, and company name overlay. Lighter sky or sparser content in the bottom helps text legibility.
- **Subject placement: upper-mid or middle** — never bottom-center (collides with overlay text).
- **Atmosphere over detail** — late afternoon, golden hour, available light. The cover is seen at small sizes (preview, PDF thumbnail) before opened — silhouettes and atmosphere read better than fine detail.

## Approved settings (vary across quarters)

Same global list as the ad skill, but framed wider:

- **Marrakech rooftop** at golden hour, terraces stepping down, distant figure with a phone
- **Lisbon street** with azulejo tile walls, café tables in middle distance, a person seated working
- **Buenos Aires balcony at dusk**, city lights coming on, person leaning on railing in the background
- **Bangalore co-working courtyard**, plants and warm lamps, person in conversation at a far table
- **Istanbul tea house** with bay window onto the Bosphorus, tea glasses on tables, person mid-call by the window
- **Nairobi market-side terrace** at late afternoon, traders below, person standing near the edge
- **Mexico City corner café**, jacaranda blooms outside, person at a window table from a distance
- **Hanoi alley café**, lanterns at dusk, person seated at a low table, scooters passing

## Camera / lens defaults

| Mood | Suffix |
|------|--------|
| **Default cover** (editorial documentary) | `Shot wide on a 28mm lens at f/4. Available light only. Late afternoon. Documentary editorial style.` |
| Atmospheric / cinematic | `Shot on Arri Alexa Mini. Cooke S4/i 32mm T2. Available light. Late afternoon, long shadows.` |
| Architectural emphasis | `35mm equivalent lens, f/5.6. Geometric composition emphasising the architecture. Person small in frame.` |

Front-load **the setting**, then describe the figure as part of the scene, then atmosphere — opposite ordering from the ad skill where the person leads.

## Prompt rules that still apply

From the ad skill's `brand/prompt-rules.md`, the still-load-bearing rules:

1. **No text overlays / labels / signage** — Flux mangles them. Period label + company name are added by the WeasyPrint CSS overlay, not the image.
2. **Avoid angry-coded focus words** — "intent", "concentrated", "focused" produce stern expressions even at distance.
3. **Distinctive settings, not stock** — Marrakech rooftop > Stockholm reception desk. Buenos Aires balcony > white-desk laptop.
4. **Specific lighting** — name time of day, source, quality.
5. **Specific nationality / ethnicity / age** — even at distance, "Brazilian woman in her 40s" beats "person". Vary across quarters.

## Rules that change for the cover use case

| Rule (ad style) | Cover style |
|---|---|
| Subject roughly centered, ~25% headroom | Subject in upper-mid or middle-distance; bottom third clear-zone |
| Phone-to-ear posture in detail | Phone may not be visible; if visible, just "a phone in hand" or "a phone resting on the table beside them" |
| 50mm at f/1.8 (shallow DoF for portrait) | 28–35mm at f/4–f/5.6 (deeper DoF, environment in focus) |
| Imperfection language ("coffee-stained desk") | Still useful but operates at the scene level — "rooftop with weathered terracotta tiles" rather than desk detail |
| "Duchenne smile mechanics" | Less load-bearing at distance — the face is small. Body language and posture matter more. |

## Default cover prompt template

```
[SETTING] at [TIME OF DAY]. [LIGHTING DESCRIPTION].
A [NATIONALITY] [AGE] is [POSTURE/ACTIVITY] in the [middle distance / upper-mid frame],
small in the composition. [ENVIRONMENT DETAIL — what fills the frame around them].
[ATMOSPHERE — long shadows, golden hour, late afternoon].
Vertical 9:16 composition with a clearer lower-third for caption space.
No text, no signage, no logos.
[CAMERA SUFFIX from table above].
```

## Aspect ratio

Always `9:16` for the cover. The render pipeline stretches/crops to A4 (210x297mm).
Other aspects (4:5, 1:1, 16:9) are available in `generate-image.mjs` but not appropriate for the cover.

## Model selection

- **Flux 2 Pro** (`--model flux`) is the default — better at wider environments and atmosphere, which is exactly the cover use case.
- **Nano Banana 2** (`--model nb2`) is for portraits with strong eye/expression detail — wrong tool
  for distance shots. Don't use for cover unless a specific test calls for it.

**ASK WHICH CASE YOU ARE IN BEFORE YOU GENERATE (Henrik 2026-08-21).** The two lines above are the
whole decision and they were skipped for six straight attempts on the halvårsrapport jan–jun 2026
VD-ordet picture, because `flux` is the CLI default and the default was never questioned. The
picture needed a *gesture to be readable* — a man visibly on a phone — which is the portrait case,
not the wide-environment case. Flux produced six unnatural grips in a row; **nb2 got it right on
the first try, with a shorter prompt.**

The tell that you are in the portrait case: **a hand, a face or an object being held has to read.**
If the picture works as a silhouette in a landscape, use flux. If the viewer must see what the
person is *doing*, use nb2.

Trade-off to know: nb2 returns about **928×1152** against Flux's 1536×1920 — roughly 112 dpi at
210mm width versus 186. Acceptable for a screen-read PDF (the cover has always run near 130), but
Flux is the better choice whenever the picture is a landscape and no gesture has to carry.
