---
name: sonetel-bokslut
description: Create or update a Sonetel AB financial report (Bokslutskommuniké, Halvårsrapport, or Kvartalsrapport). Use when working on Swedish financial communiqués for Sonetel AB (publ).
argument-hint: "[report-type]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel financial reports. If the current working directory does NOT contain `Sonetel/Financial`, STOP immediately and tell the user: "This skill is for Sonetel financial reports only. Current directory: [cwd]". Do NOT proceed.

You are helping Henrik Thomé, CEO of **Sonetel AB (publ)**, prepare a Swedish financial report. The company is listed on Nasdaq First North Growth Market. The working directory is the relevant **Year** folder under `~/Dropbox/Sonetel/Financial/`.

## Report types
- **Bokslutskommuniké** — Full-year (or 18-month) year-end report
- **Halvårsrapport** — H1 half-year report
- **Kvartalsrapport** — Q1 or Q3 interim report

---

## Primary data sources

### Sales analysis (main KPI source)
**Path pattern:** `Month/YYYY MM/Output files from monthly process/sales_analysis_YYYY-MM-DD.xlsx`

Key rows in the **"Data"** sheet (column headers = dates on row 1):

| Row | Metric |
|-----|--------|
| 14  | ARR — annualized payments (MUSD). Convert to MSEK using dagskurs on period end date (e.g. 9.21 SEK/USD for 2025-12-31). **Note:** These values may differ from the finops API `arr_total` — see ARR scaling note below. |
| 703 | CAC — customer acquisition cost (SEK, monthly) |
| 731 | Active paying companies ("In accounts with positive balance") |
| 739 | Premium subscriptions (count) |
| 800 | Phone number subscriptions, **Status=A only** (row 799 = date headers) |

### ARR data reconciliation

The sales_analysis "Annualized payments" (row 14) and the finops API `arr_total` field (in `kommunike_data.json`) may report **different MUSD values** for the same month. The finops API value is considered the official figure used in the kommuniké text.

**Scaling methodology:** When building the ARR chart, scale all sales_analysis values so the final month matches the finops API value:
```python
finops_dec = kommunike_data['q4']['arr_musd']['current']   # e.g. 2.8133
sales_dec  = arr_kalldata_last_musd                         # e.g. 3.0803
scale = finops_dec / sales_dec                              # e.g. 0.9133
arr_musd_scaled = [v * scale for v in arr_musd_raw]
arr_msek = [round(v * exchange_rate, 1) for v in arr_musd_scaled]
```

Use a **single fixed exchange rate** (dagskurs on period end date) for the entire ARR chart series, and note this in the Kommentar box.

### BDO accounting files
**Path:** `ÅR/Från BDO/YYYY MM DD Underlag från Anne/`
- P&L: `.xls` file (use `xlrd`)
- Forex/currency adjustments: `.xlsx` file, sheet "Konto 3960" (use `openpyxl`)
- Marketing costs appear as a **separate line** in the finops Detailed P&L, not lumped into "övriga externa"

---

## Standard Nyckeltal charts

**Brand color:** `#B80404` (dark red). Use this for ALL charts — both bar and line.

**Chart type rules:**
- **Monthly data** (25+ data points) → **line chart** — no markers (`marker` param omitted), no value labels, no end-value annotations, smooth continuous line
- **Quarterly data** (≤8 data points) → **bar chart** — with value labels above bars

**Y-axis formatting:** Always use space ` ` as thousand separator (e.g. `5 000`, `60 000`), never comma.

**Y-axis origin:** All charts (both bar and line) MUST start the y-axis from **0**. Use `ax.set_ylim(0, top * 1.12)`.

### Line chart template (monthly data)

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np

FP_BOLD = fm.FontProperties(fname='/Users/henrik/Library/Fonts/GothamSSm-Bold.otf')
FP_BOOK = fm.FontProperties(fname='/Users/henrik/Library/Fonts/GothamSSm-Book.otf')
RED = '#B80404'
DPI = 200

def space_fmt(x, pos):
    if x == int(x):
        return f'{int(x):,}'.replace(',', ' ')
    return f'{x:,.1f}'.replace(',', ' ')

def line_chart(all_labels, values, title, out, show_idx, w=3.74, h=2.605):
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(all_labels))
    ax.plot(x, values, color=RED, linewidth=2.2, zorder=3)  # NO markers
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color='#1A1A1A', pad=6)
    ax.set_xticks(show_idx)  # must be a sorted list, not a set
    ax.set_xticklabels([all_labels[i] for i in show_idx])
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(FP_BOOK); lbl.set_fontsize(7.5)
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK); lbl.set_fontsize(7.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(space_fmt))
    ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.8, zorder=0)
    for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    top = max(values)
    ax.set_ylim(0, top * 1.12)  # y-axis MUST start from 0
    ax.set_xlim(-0.5, len(values) - 0.5)
    fig.tight_layout(pad=0.5)
    fig.savefig(out, dpi=DPI, bbox_inches='tight')
    plt.close()
```

### Exact pixel sizing for docx injection

Charts must match the original image dimensions in the docx to avoid layout shifts. Use this helper to resize matplotlib output to exact pixel dimensions:

```python
from PIL import Image
import io

def save_chart(fig, out_path, target_w, target_h, dpi=200):
    """Save matplotlib figure resized to exact pixel dimensions."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert('RGBA')
    img = img.resize((target_w, target_h), Image.LANCZOS)
    img.save(out_path)
```

Standard sizes in FY24-25 Bokslutskommuniké:
- image12: 748×521 (standalone bar chart)
- image15-17: 748×521 (Nyckeltal row 1-2 left)
- image18-20: 736×514 (Nyckeltal row 2-3 right)

### Kommentar till grafer text box (PIL)

Elegant style: thin gray border + red left accent bar, large readable text.

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (736, 514), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Thin gray border (1px all sides)
draw.rectangle([0, 0, 735, 513], outline='#CCCCCC', width=1)
# Red left accent bar (5px wide)
draw.rectangle([0, 0, 5, 514], fill='#B80404')

font_bold = ImageFont.truetype('/Users/henrik/Library/Fonts/GothamSSm-Bold.otf', 24)
font_body = ImageFont.truetype('/Users/henrik/Library/Fonts/GothamSSm-Book.otf', 19)

# Title
title = "Kommentar till grafer"
draw.text((28, 24), title, fill='#1A1A1A', font=font_bold)

# Underline below title
tw = draw.textlength(title, font=font_bold)
draw.line([(28, 58), (28 + tw, 58)], fill='#B80404', width=2)

# Body text — use textwrap.wrap with width ~52 chars for 19pt Book font
# Line height ~28px, paragraph gap ~18px
# Example content includes exchange rate note:
# "ARR anges i MSEK, omräknat till fast kurs 9,21 SEK/USD
#  (dagskurs 2025-12-31) för hela perioden."
y = 78
line_h = 28
# Draw wrapped lines with draw.text((28, y), line, fill='#1A1A1A', font=font_body)
```

### Bar chart template (quarterly data)

```python
def bar_chart(labels, values, title, out, w=3.74, h=2.605, fmt='{:.1f}'):
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(labels))
    ax.bar(x, values, color=RED, width=0.65, zorder=3)
    top = max(values)
    for i, v in enumerate(values):
        ax.text(i, v + top*0.02, fmt.format(v), ha='center', va='bottom',
                fontsize=8, fontproperties=FP_BOLD, color='#1A1A1A')
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color='#1A1A1A', pad=6)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(FP_BOOK); lbl.set_fontsize(7.5)
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK); lbl.set_fontsize(7.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(space_fmt))
    ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.8, zorder=0)
    for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
    ax.tick_params(length=0); ax.set_ylim(0, top * 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(out, dpi=DPI, bbox_inches='tight')
    plt.close()
```

**IMPORTANT:** Do NOT use `fontfamily='Gotham SSm'` — all Gotham SSm weights share the same family name in matplotlib. Always use `FontProperties(fname=path)`.

**IMPORTANT:** For x-axis tick indices, always pass a **sorted list** (e.g. `[0, 4, 8, 12]`), never a set — sets have random iteration order and will scramble the labels.

Gotham SSm font files: `~/Library/Fonts/GothamSSm-{Bold,Medium,Book}.otf`

### Nyckeltal page layout (3×2 grid)

The Nyckeltal page has 6 image positions in reading order (left-to-right, top-to-bottom). Each position must be a **unique** chart or element — no duplicates.

**Standard layout (matching kvartalsrapport template):**

| Position | Image | Chart | Type | Data source |
|----------|-------|-------|------|-------------|
| Row 1 left | image15 | Intäkt per kvartal (MSEK) | Line | `Grafkälldata/nettoomsattning_per_kvartal_källdata.csv` |
| Row 1 right | image16 | ARR (MSEK) | Line | `Grafkälldata/arr_källdata.csv` (MSEK column) |
| Row 2 left | image17 | Betalande abonnemangskunder | Line | `finops_monthly_active_customers.json` |
| Row 2 right | image18 | Abonnemang virtuella telefonnummer | Line | `finops_monthly_subs_by_type.json` (Phonenumber) |
| Row 3 left | image19 | Kommentar till grafer | Text image | Hand-crafted PIL image with red border |
| Row 3 right | image20 | Kundabonnemang Premium | Line | `kommunike_data.json` → `premium_plan_customers_monthly` (= "Plan" type unique customers only, NOT Business Plan or BusinessPackage) |

**Note:** Image numbers (15-20) are for the FY24-25 Bokslutskommuniké. Other reports may differ — always verify by parsing `word/document.xml` relationships and checking image order after the "Nyckeltal" heading.

**Note:** There is also a standalone **image12** on a separate page: "Intäkt per kvartal (MSEK)" as a **bar chart** with 8 calendar-year quarters (Q1'24–Q4'25). This is distinct from the line chart version on the Nyckeltal page (image15 with 6 FY quarters).

### Data files in Grafkälldata/

Pre-extracted chart source data with provenance:
- `arr_källdata.csv` — Monthly ARR in MUSD and MSEK (fixed rate)
- `nettoomsattning_per_kvartal_källdata.csv` — Quarterly net revenue
- `cac_källdata.csv` — Monthly CAC in SEK

### Finops JSON data files (in Bokslutskommuniké/)

- `finops_monthly_active_customers.json` — Monthly active customer counts
- `finops_monthly_subs_by_type.json` — Monthly subscription counts by product type
- `kommunike_data.json` — Master data file with all metrics and metadata

---

## Injecting charts into Word (.docx)

Use `zipfile` to replace `word/media/imageNN.png` inside the .docx without touching any other content:

```python
import zipfile, shutil

replacements = {
    'word/media/image13.png': '/tmp/c1_intakt_kvartal.png',
    'word/media/image14.png': '/tmp/c2_arr.png',
    # ... etc
}

src = 'path/to/input.docx'
dst = 'path/to/output.docx'
tmp = dst + '.tmp'

with zipfile.ZipFile(src, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in replacements:
                data = open(replacements[item.filename], 'rb').read()
            else:
                data = zin.read(item.filename)
            zout.writestr(item, data)

shutil.move(tmp, dst)
```

To find which imageNN.png corresponds to which chart: look at `word/document.xml` inside the unzipped docx, or open the docx and compare by position.

---

## Editing text in Word (.docx)

Use `python-docx` to find and update paragraphs:

```python
from docx import Document

doc = Document('input.docx')
for i, para in enumerate(doc.paragraphs):
    if 'search text' in para.text:
        print(f"Para[{i}]: {para.text[:80]}")
        # Edit run text — preserve formatting by editing runs individually
        for run in para.runs:
            if 'old value' in run.text:
                run.text = run.text.replace('old value', 'new value')
doc.save('output.docx')
```

---

## File and version conventions

- **Layoutad document:** `Bokslutskommuniké/Layoutad/Sonetel FY24-25 Bokslutskommuniké Layoutad vNN.docx`
- **Chart source CSVs:** `Bokslutskommuniké/Layoutad/Grafkälldata/`
- **BDO underlag:** `ÅR/Från BDO/YYYY MM DD Underlag från Anne/`
- Always save as a new version (vN+1), never overwrite current base
- **Crashed sessions:** When resuming after a crash, always start from the user's base version (the version they said they edited), not from a half-finished version created by the previous session. Check `ls` for existing versions before creating a new one.

---

## Checklist — metrics to verify/update in each report

- [ ] Revenue (MSEK) from BDO P&L — check total and per quarter
- [ ] ARR (sales_analysis row 14, latest month, × SEK/USD)
- [ ] Active paying companies (row 731, latest month)
- [ ] Premium subscriptions (row 739, latest month)
- [ ] Phone number subscriptions (row 800 Status=A, latest month)
- [ ] CAC (row 703, latest quarter average — 3 months)
- [ ] Marketing costs (finops Detailed P&L, separate line item)
- [ ] Currency/forex adjustments (BDO konto 3960, intercompany effects)
- [ ] EBT = operating result ± forex adjustments
- [ ] Future report dates (XXXX-XX-XX placeholders)
- [ ] **Kalendarium updated per the fiscal-year completeness rule (see below)**
- [ ] **Website kalendarium synced** — `FINANCIAL_CALENDAR` in `sonetel.com/src/components/investor/investor-hub.tsx` matches the report's kalendarium exactly

---

## Kalendarium completeness rule (MANDATORY)

> Why: CR-2026-04-22-investor-kalendarium-full-fiscal-year-completeness — the investor page kalendarium drifted out of sync with the Bokslutskommuniké (wrong Halvårsrapport date, mislabeled Q3 as "Periodrapport", missing Q1 entirely, and the whole next fiscal year absent). Rule formalizes the "all or nothing per fiscal year" expectation set by Nasdaq First North disclosure norms.

**Every fiscal year listed in the kalendarium must include ALL of these events, or NONE:**

1. Bokslutskommuniké
2. Årsredovisning
3. Bolagsstämma
4. Verksamhetsredogörelse Q1
5. Halvårsrapport
6. Verksamhetsredogörelse Q3

A partial fiscal year is never acceptable. If a cycle's Bokslutskommuniké has been published as a press release, it drops out of the forward-looking kalendarium — but its subsequent Årsredovisning + Bolagsstämma MUST still be listed until they too have passed.

**Label convention (per Bokslutskommuniké):**
- Plain event names, no fiscal-year suffix. Example: `"Halvårsrapport"`, NOT `"Halvårsrapport januari – juni 26"`.
- Use `"Bolagsstämma"`, not `"Årsstämma"` (Bokslutskommuniké terminology).
- Use `"Verksamhetsredogörelse Q1"` / `"Verksamhetsredogörelse Q3"`, not `"Periodrapport …"`.

**Companion website sync:** Every time the Bokslutskommuniké kalendarium changes (whether at draft time or when a new published report supersedes the previous forward view), the `FINANCIAL_CALENDAR` array in `sonetel.com/src/components/investor/investor-hub.tsx` MUST be updated in the same session. The arrays are source-of-truth siblings.

---

## PDF export (Mac)

**Do NOT use Print → Save as PDF** — causes floating image displacement on Mac.

**Do NOT use `docx2pdf` or AppleScript automation** — Word on Mac times out on AppleEvents, especially with Dropbox paths and open files.

**Manual workflow (recommended):**
1. Word → **File → Save As** → choose **PDF** as file format
2. If file is large (>5 MB): open in **Preview → File → Export → Quartz Filter: Reduce File Size**

This brings ~11 MB exports down to ~2–3 MB while keeping correct layout.

---

$ARGUMENTS
