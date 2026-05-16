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
- **Nano Banana 2** (`--model nb2`) is for portraits with strong eye/expression detail — wrong tool for distance shots. Don't use for cover unless a specific test calls for it.
