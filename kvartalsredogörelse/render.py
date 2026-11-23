"""Sonetel Kvartalsredogörelse renderer.

Pipeline:  data.json  ->  pydantic validate  ->  reconciliation guards
        ->  matplotlib charts  ->  Jinja2 HTML  ->  WeasyPrint PDF

Usage:
    python3 render.py path/to/data.json output.pdf [--debug] [--allow-date-mismatch]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

# WeasyPrint needs Homebrew libs on macOS — set before import.
os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")

from pydantic import BaseModel, ConfigDict, Field, model_validator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np

from weasyprint import HTML, CSS

import i18n as _i18n

# Output language. "sv" is the default, and every language-aware branch below falls through to the
# Swedish literal when LANG == "sv" — so the Swedish render cannot change.
LANG = "sv"
_STRINGS = None   # i18n.Strings,  set in render()
_GLOSSARY = None  # i18n.Glossary, set in render()

# ----------------------------------------------------------------- constants

BRAND_RED = "#B80404"
BRAND_NAVY = "#2E4A7C"
FONT_DIR = Path.home() / "Library" / "Fonts"
FP_BOOK = fm.FontProperties(fname=str(FONT_DIR / "GothamSSm-Book.otf"))
FP_BOLD = fm.FontProperties(fname=str(FONT_DIR / "GothamSSm-Bold.otf"))

SKILL_DIR = Path(__file__).parent
TEMPLATE_DIR = SKILL_DIR / "template"

# ------------------------------------------------------------- pydantic models

class KpiPair(BaseModel):
    model_config = ConfigDict(extra="allow")
    current: float | None = None
    prior: float | None = None
    unit: str | None = None
    yoy_pct: float | None = None

class TableRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    label: str
    values: list[float | None] | None = None
    section_header: bool = False
    summa: bool = False
    bold: bool = False
    indent: int = 0
    footnote_marker: str | None = None
    format: str | None = None
    continuation_break: bool = False

class EquityBlock(BaseModel):
    """One movement block in a förändring i eget kapital table — opening balance, movements,
    closing balance — for a single period. The table repeats one block per period."""
    model_config = ConfigDict(extra="allow")
    period: str
    rows: list[TableRow]

class FinTable(BaseModel):
    model_config = ConfigDict(extra="allow")
    currency_unit: str
    columns: list[str]
    # Period-column tables carry `rows`; förändring i eget kapital carries `blocks` instead,
    # because its columns are equity components rather than periods (CR-2026-08-19).
    rows: list[TableRow] = []
    blocks: list[EquityBlock] | None = None
    footnotes: dict[str, str] | None = None

    @model_validator(mode="after")
    def _rows_or_blocks(self):
        if not self.rows and not self.blocks:
            raise ValueError("table has neither rows nor blocks")
        return self

class Meta(BaseModel):
    model_config = ConfigDict(extra="allow")
    period_label: str
    period_short: str
    period_short_compare: str
    fiscal_year: str
    report_type: str
    footer_label: str
    publication_date: str
    tagline: str

class BoardMember(BaseModel):
    namn: str
    roll: str

class Governance(BaseModel):
    model_config = ConfigDict(extra="allow")
    board: list[BoardMember]
    vd_namn: str
    vd_titel: str
    vd_signing_location: str
    vd_signing_date: str

class KalendariumEvent(BaseModel):
    event: str
    date: str

class DataModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    meta: Meta
    kpis: dict[str, KpiPair]
    kpi_tiles: list[dict[str, str]]
    narrative: dict[str, Any]
    tables: dict[str, FinTable]
    share_capital: dict[str, Any]
    governance: Governance
    disclosures: dict[str, Any]
    transaktioner_narstaende: str | None = None
    kalendarium: list[KalendariumEvent]
    definitioner: list[dict[str, str]] | None = None
    boilerplate: dict[str, Any]
    units: dict[str, Any]
    assets: dict[str, str] | None = None


# ------------------------------------------------------------ formatters

def _round_half_up(value: float, places: int = 0) -> Decimal:
    """Round half away from zero, the way a reader expects.

    Python rounds halves to even: round(10.5) is 10, and f"{2.25:.1f}" is "2.2". That silently
    published +10% for a customer base that grew 10,54%, and 2,2 MSEK for a cash flow of
    2 250 450 kr. Both were found by the pre-publication audit on 2026-08-23.

    The trap is DOUBLE rounding. 10,5442 was first rounded to one decimal in derive_kpis, which
    created an exact half, and the second rounding then broke the tie downwards. Round once, from
    the full-precision figure, and half-up.
    """
    q = Decimal(1).scaleb(-places)
    return Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)


def _space_thousands(n: float | int) -> str:
    if isinstance(n, float) and not n.is_integer():
        s = f"{abs(n):,.2f}"
        if LANG != "en":  # sv: 32 133,45   en: 32,133.45
            s = s.replace(",", " ").replace(".", ",")
    else:
        s = f"{abs(int(n)):,}"
        if LANG != "en":
            s = s.replace(",", " ")
    return ("-" + s) if n < 0 else s

_TBD_PLACEHOLDER = "XX"  # draft-mode placeholder for missing numbers; visually distinct, won't trigger 4-char XXXX guard

def fmt_int(n: int | float | None) -> str:
    if n is None:
        return _TBD_PLACEHOLDER
    return _space_thousands(int(n))

def fmt_msek(n: float | None) -> str:
    """MSEK with comma decimal, one decimal place. Clamps near-zero to '0,0' to avoid '-0,0'."""
    if n is None:
        return _TBD_PLACEHOLDER
    if abs(n) < 0.05:  # round to clean zero, avoid -0,0 display
        return "0.0" if LANG == "en" else "0,0"
    s = str(_round_half_up(abs(n), 1))
    if LANG != "en":
        s = s.replace(".", ",")
    return ("-" + s) if n < 0 else s

def fmt_decimal(n: float | None, places: int = 2) -> str:
    # Sibling formatters all return the placeholder on None; this one did not, and
    # template.html calls it unguarded on kpis.resultat_per_aktie — so a draft render with
    # that KPI still null raised TypeError. Found in review of CR-2026-08-19.
    if n is None:
        return _TBD_PLACEHOLDER
    # Thousand separators, not just a decimal comma. Without the "," in the format spec a
    # large value renders as 52145444,49 — which is what the published jan-jun 2026 report
    # showed in six balансräkning cells (2026-08-25).
    s = f"{abs(n):,.{places}f}"
    if LANG != "en":
        s = s.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", " ")
    return ("-" + s) if n < 0 else s


def fmt_change(yoy: float | None) -> str:
    """"ökade med 11%" / "minskade med 2%" — never "ökade med -2%".

    The template used to hardcode "ökade med +{pct}%", which silently turns a decline into a
    nonsense sentence. A half-year report is exactly where that happens.
    """
    if yoy is None:
        return (f"changed by {_TBD_PLACEHOLDER}%" if LANG == "en"
                else f"förändrades med {_TBD_PLACEHOLDER}%")
    n = int(_round_half_up(yoy, 0))
    if n == 0:
        return "was unchanged" if LANG == "en" else "var oförändrad"
    if n > 0:
        return f"increased by {n}%" if LANG == "en" else f"ökade med {n}%"
    # Decreases carry the minus sign (Henrik 2026-08-19), so the direction is visible in the
    # figure itself and matches the signed KPI tiles. English mirrors the convention deliberately.
    return f"decreased by {n}%" if LANG == "en" else f"minskade med {n}%"

def fmt_table_value(v: float | int | None, fmt: str | None = None) -> str:
    if v is None:
        return _TBD_PLACEHOLDER
    if fmt == "percent":
        return f"{int(v)}%"
    if fmt == "decimal2":
        return fmt_decimal(v, 2)
    if isinstance(v, float) and not v.is_integer():
        # SEK tables are whole kronor. BDO's workbook carries öre on a handful of rows;
        # showing them on three rows while the rest of the column is integer looks like a
        # rendering fault — which is how it read in the published jan-jun 2026 report.
        # Small values (resultat per aktie) keep their decimals.
        if abs(v) >= 1000:
            return _space_thousands(int(round(v)))
        return fmt_decimal(v, 2)
    return _space_thousands(int(v))

_SV_MONTHS = ["januari", "februari", "mars", "april", "maj", "juni",
              "juli", "augusti", "september", "oktober", "november", "december"]
_EN_MONTHS = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

def format_signing_date(iso: str) -> str:
    y, m, d = iso.split("-")
    months = _EN_MONTHS if LANG == "en" else _SV_MONTHS
    return f"{int(d)} {months[int(m) - 1]} {y}"




# ------------------------------------------------------- derived KPIs

def _find(table, label, col=0):
    """Last row whose label matches and that carries data.

    Last, not first: BDO wraps some statements so the same label appears twice — once as a
    two-line heading with no figures, once as the real total.
    """
    hit = None
    for r in table.rows:
        if r.label.strip().casefold() == label.casefold() and r.values:
            if r.values[col] is not None:
                hit = r.values[col]
    return hit


def derive_kpis(data: DataModel) -> list[str]:
    """Compute every KPI that follows arithmetically from the tables.

    A figure that can be derived should never be typed in — that is the transcription risk the
    extractor removed from the tables, and it applies to the KPI block too. Supplied values are
    not overwritten; they are checked, and a disagreement is a hard error.
    """
    notes: list[str] = []
    rr = data.tables.get("resultatrakning_koncern")
    br = data.tables.get("balansrakning_koncern")
    kf = data.tables.get("kassaflode_koncern")
    if rr is None:
        return notes

    def col(i):
        net = _find(rr, "Nettoomsättning", i)
        dk = _find(rr, "Direkta kostnader sålda tjänster", i)
        ror = _find(rr, "Rörelseresultat", i)
        avs = _find(rr, "Avskrivningar av materiella och immateriella tillgångar", i)
        d = {}
        if net:
            if dk is not None:
                d["bruttomarginal_pct"] = 100.0 * (net + dk) / net
            if ror is not None and avs is not None:
                d["ebitda_pct"] = 100.0 * (ror - avs) / net
            d["nettoomsattning"] = net / 1e6
        if ror is not None:
            d["rorelseresultat"] = ror / 1e6
        rfs = _find(rr, "Resultat efter finansiella poster", i)
        if rfs is not None:
            d["resultat_fore_skatt"] = rfs / 1e6
        if br is not None and i < len(br.columns):
            ek = _find(br, "Summa Eget kapital", i) or _find(br, "Summa eget kapital", i)
            ta = _find(br, "Summa tillgångar", i)
            if ek and ta:
                d["soliditet_pct"] = 100.0 * ek / ta
            lm = _find(br, "Likvida medel", i)
            if lm is not None:
                d["likvida_medel_eom"] = lm / 1e6
        if kf is not None:
            cf = _find(kf, "Kassaflöde från den löpande verksamheten", i)
            if cf is not None:
                d["kassaflode_loepande"] = cf / 1e6
        return d

    cur, pri = col(0), col(1)

    # Quarterly block. Only FLOW measures belong here — likvida medel, soliditet, antal kunder
    # and the like are measured at period end and are identical whether the period is called a
    # quarter or a half-year, so repeating them would be noise. Columns 2/3 are the quarter and
    # its comparative when the report carries them (halvårsrapport); a kvartalsredogörelse has
    # no such columns and this block is skipped.
    FLOW_ONLY = {"nettoomsattning", "rorelseresultat", "resultat_fore_skatt",
                 "bruttomarginal_pct", "ebitda_pct", "kassaflode_loepande"}
    if len(rr.columns) >= 4:
        q_cur, q_pri = col(2), col(3)
        kq: dict[str, KpiPair] = {}
        for key in FLOW_ONLY:
            c, pr = q_cur.get(key), q_pri.get(key)
            if c is None and pr is None:
                continue
            yoy = round(100.0 * (c - pr) / abs(pr), 1) if (c is not None and pr) else None
            kq[key] = KpiPair(current=round(c, 3 if abs(c) < 100 else 1) if c is not None else None,
                              prior=round(pr, 3 if abs(pr) < 100 else 1) if pr is not None else None,
                              yoy_pct=yoy)
        if kq:
            object.__setattr__(data, "kpis_kvartal", kq)
            notes.append(f"kpis_kvartal: {len(kq)} värden ur kolumn 2/3")

    # SaaS40 per Sonetel's own definition: nettoomsättning YoY growth + EBITDA margin.
    # Not ARR-based — see SKILL.md, confirmed by Henrik for Q1 2026.
    if "nettoomsattning" in cur and pri.get("nettoomsattning"):
        net_yoy = 100.0 * (cur["nettoomsattning"] - pri["nettoomsattning"]) / abs(pri["nettoomsattning"])
        if "ebitda_pct" in cur:
            cur["saas40_pct"] = net_yoy + cur["ebitda_pct"]

    for key in set(cur) | set(pri):
        kp = data.kpis.get(key)
        if kp is None:
            kp = KpiPair()
            data.kpis[key] = kp
        for attr, src in (("current", cur), ("prior", pri)):
            want = src.get(key)
            if want is None:
                continue
            have = getattr(kp, attr)
            if have is None:
                setattr(kp, attr, round(want, 3 if abs(want) < 100 else 1))
                notes.append(f"{key}.{attr} = {getattr(kp, attr)}")
            else:
                tol = max(0.05, abs(want) * 0.005)
                if abs(have - want) > tol:
                    raise SystemExit(
                        f"[guard 23] kpis.{key}.{attr} is {have} but the tables give "
                        f"{want:.3f}. A derivable KPI must not disagree with its own table."
                    )

    # Any KPI with both sides and no declared yoy_pct gets one, so the narrative and the
    # tiles cannot drift from the figures they describe.
    for key, kp in data.kpis.items():
        if kp.yoy_pct is None and kp.current is not None and kp.prior:
            # NO pre-rounding here. Rounding to one decimal first created exact halves that
            # the display rounding then broke the wrong way (see _round_half_up).
            kp.yoy_pct = 100.0 * (kp.current - kp.prior) / abs(kp.prior)
            notes.append(f"{key}.yoy_pct = {kp.yoy_pct}")
    return notes


# ----------------------------------------------------------- KPI tile SVG

def kpi_tile_svg(value: str, label: str) -> Markup:
    return Markup(f"""<svg class="kpi-tile" viewBox="0 0 156 96" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <rect width="156" height="96" fill="{BRAND_RED}"/>
  <text x="78" y="48" text-anchor="middle" dominant-baseline="middle" font-family="Gotham SSm" font-weight="700" font-size="28" fill="#FFFFFF">{value}</text>
  <text x="78" y="76" text-anchor="middle" dominant-baseline="middle" font-family="Gotham SSm" font-weight="500" font-size="9" letter-spacing="1" fill="#FFFFFF">{label}</text>
</svg>""")


# ----------------------------------------------------------- table renderer

def _row_to_html(r: TableRow, n_cols: int) -> str:
    classes = []
    if r.section_header:
        classes.append("section")
    if r.summa:
        classes.append("summa-bold" if r.bold else "summa")
    tr_class = (" class=\"" + " ".join(classes) + "\"") if classes else ""

    label_classes = []
    if r.indent == 1:
        label_classes.append("indent-1")
    elif r.indent >= 2:
        label_classes.append("indent-2")
    label_class_attr = (" class=\"" + " ".join(label_classes) + "\"") if label_classes else ""

    # Glossary is applied HERE, at print time — never to the model. r.label is the key that
    # derive_kpis(), the guards and mark_summa_rows() match on, so it must survive untouched
    # until the moment the cell is written.
    label_html = _GLOSSARY.row(r.label) if _GLOSSARY else r.label
    if r.footnote_marker:
        label_html += f'<span class="footnote-marker">{r.footnote_marker}</span>'

    if r.section_header or r.values is None:
        # Label in col 1, empty value cells for the rest — preserves column structure
        # so the current-period tint via :nth-child(2) renders continuously from top to bottom
        cells = f'<td{label_class_attr}>{label_html}</td>' + ('<td></td>' * n_cols)
    else:
        value_cells = "".join(f"<td>{fmt_table_value(v, r.format)}</td>" for v in r.values)
        cells = f"<td{label_class_attr}>{label_html}</td>{value_cells}"
    return f"<tr{tr_class}>{cells}</tr>"


# Set False in data.json via meta.drop_zero_rows to keep BDO's full row set.
DROP_ZERO_ROWS = True
_DROPPED_ZERO_ROWS: list[str] = []


def _is_all_zero(r) -> bool:
    """True for a data row whose every column is exactly zero.

    A row with any None is NOT all-zero — guard 0 already refuses to build in that case, and
    treating a hole as a zero would hide it.
    """
    vals = getattr(r, "values", None) if not isinstance(r, dict) else r.get("values")
    hdr = getattr(r, "section_header", False) if not isinstance(r, dict) else r.get("section_header")
    if hdr or not vals:
        return False
    return all(v is not None and float(v) == 0 for v in vals)


def drop_zero_rows(rows, table_name: str = ""):
    """Omit rows that are zero in every reported column.

    ÅRL 3:4 §5 allows a post carrying no amount to be left out when the comparative carries none
    either; here the row is zero in *every* column shown, so the condition holds with room to
    spare. Sebastian Ahlskog (styrelsen) asked for it on 2026-08-21 — 42 such rows across the
    eight statements, worst in förändring i eget kapital where three of seven movement rows in
    each parent block were empty.

    Every omission is recorded and printed, so the deviation from BDO's own layout is auditable
    rather than silent.
    """
    kept = []
    for r in rows:
        if _is_all_zero(r):
            label = (r.get("label") if isinstance(r, dict) else r.label) or ""
            _DROPPED_ZERO_ROWS.append(f"{table_name}: {label}")
            continue
        kept.append(r)
    return kept


def bind_range_dash(s: str) -> str:
    """Tie the en dash of a date range to the date before it.

    "2026-04-01 – 2026-06-30" in a narrow column was wrapping at both spaces, printing the
    dash alone on a line of its own between the two dates. A non-breaking space before the
    dash leaves exactly one legal break point — after it (Henrik 2026-08-21).
    """
    return s.replace(" – ", "\u00a0– ").replace(" - ", "\u00a0- ")


def render_fin_table(table: FinTable, header_first_cell: str = "SEK",
                     tint_current: bool = True, rows: list[TableRow] | None = None,
                     emit_footnotes: bool | None = None) -> Markup:
    """Render a financial table. Pass a subset of rows for the continuation case.

    `emit_footnotes` defaults to "only when rendering the whole table". The split case must
    pass it explicitly on the final part — otherwise both halves suppress the footnotes and
    they vanish from the report entirely (bug found in review of CR-2026-08-19).
    """
    use_rows = rows if rows is not None else table.rows
    if DROP_ZERO_ROWS:
        use_rows = drop_zero_rows(use_rows, header_first_cell)
    _first = _GLOSSARY.cell(header_first_cell) if _GLOSSARY else header_first_cell
    headers_html = f"<th>{_first}</th>" + "".join(
        f"<th>{bind_range_dash(_GLOSSARY.column(c) if _GLOSSARY else c)}</th>"
        for c in table.columns)
    rows_html = "\n".join(_row_to_html(r, len(table.columns)) for r in use_rows)

    if emit_footnotes is None:
        emit_footnotes = rows is None
    footnotes_html = ""
    if table.footnotes and emit_footnotes:
        items = "".join(
            f'<div><span class="footnote-marker">{k}</span> {v}</div>'
            for k, v in table.footnotes.items()
        )
        footnotes_html = f'<div class="footnotes">{items}</div>'

    tint_class = " tint-current" if tint_current else ""
    return Markup(f"""<table class="fin{tint_class}">
  <thead><tr>{headers_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>{footnotes_html}""")


def render_balansrakning(table: FinTable) -> Markup:
    """Balansräkning splits across two pages — Tillgångar (page 9) + Eget kapital och skulder
    (page 10). Page 10 has no large title; uses 'Balansräkning fortsättning' as left-cell label.
    Split at row marked continuation_break=True."""
    split_idx = None
    for i, r in enumerate(table.rows):
        if getattr(r, "continuation_break", False):
            split_idx = i
            break
    if split_idx is None:
        # Without a split marker the statement flows as one table over two pages; jul-sep 2026
        # ran one row onto a third page, so the rows are tightened (.bal-cont, Henrik 2026-11-18).
        return Markup(f'<div class="bal-cont">{render_fin_table(table, header_first_cell="SEK", tint_current=True)}</div>')
    first = table.rows[:split_idx]
    rest = table.rows[split_idx:]
    table1 = render_fin_table(table, header_first_cell="SEK", tint_current=True, rows=first,
                              emit_footnotes=False)
    table2 = render_fin_table(table, header_first_cell="Balansräkning fortsättning",
                              tint_current=True, rows=rest, emit_footnotes=True)
    # The second half (eget kapital och skulder) ran one row over a page in jul-sep 2026,
    # stranding "Summa skulder och eget kapital" alone on the next page; .bal-cont tightens
    # its rows (Henrik 2026-11-18).
    return Markup(f'{table1}<div class="section-break"></div><div class="bal-cont">{table2}</div>')


def render_forandring_ek(table) -> Markup:
    """Förändring i eget kapital.

    A different geometry from the period-column tables: columns are equity *components*
    (aktiekapital, överkursfond, …) and the table repeats as one movement block per period.
    `tint_current`'s :nth-child(2) rule is meaningless here, so no tint is applied.
    """
    data = table if isinstance(table, dict) else table.model_dump()
    cols = data.get("columns") or []
    headers = "<th></th>" + "".join(
        f"<th>{_GLOSSARY.column(c) if _GLOSSARY else c}</th>" for c in cols)

    parts = []
    for blk in data.get("blocks") or []:
        body = []
        blk_rows = blk.get("rows") or []
        if DROP_ZERO_ROWS:
            blk_rows = drop_zero_rows(blk_rows, "förändring eget kapital")
        for r in blk_rows:
            label = (r.get("label") or "").strip()
            # The summa class is computed from the SWEDISH label. Translate only after, or both
            # equity tables lose their opening/closing-balance emphasis — silently.
            lead = label.casefold()
            cls = ' class="summa"' if lead.startswith(("ingående", "utgående")) else ""
            shown = _GLOSSARY.row(label) if _GLOSSARY else label
            cells = "".join(f"<td>{fmt_table_value(v)}</td>" for v in r.get("values") or [])
            body.append(f"<tr{cls}><td>{shown}</td>{cells}</tr>")
        parts.append(
            f'<table class="fin ek">\n'
            f'  <thead><tr>{headers}</tr></thead>\n'
            f'  <tbody>{"".join(body)}</tbody>\n'
            f'</table>'
        )
    return Markup('<div class="ek-block">' + "".join(parts) + "</div>")


def inline_bold_prefix(s: str) -> Markup:
    """Make the leading "Word." or "Word eller Word." part bold for affärsmodell bullets."""
    import re as _re
    m = _re.match(r'^([^.\n]+\.)\s*(.*)', s)
    if m:
        return Markup(f"<strong>{m.group(1)}</strong> {m.group(2)}")
    return Markup(s)


# ----------------------------------------------------------- charts

def _space_fmt(x, _pos):
    # Swedish convention: space as thousands separator, comma as decimal separator.
    # English keeps Python's own comma/period.
    if x == int(x):
        s = f"{int(x):,}"
        return s if LANG == "en" else s.replace(",", " ")
    s = f"{x:,.1f}"
    return s if LANG == "en" else s.replace(",", " ").replace(".", ",")

def line_chart(labels: list[str], values: list[float], title: str, out_path: str,
               show_idx: list[int] | None = None, w: float = 3.74, h: float = 2.6) -> None:
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(labels))
    ax.plot(x, values, color=BRAND_RED, linewidth=2.2, zorder=3)
    # Own tick size: bar_chart computes one from its bar count, and line_chart used to
    # borrow that name from module scope. It no longer exists there.
    n = len(values)
    tick_size = 7.5 if n <= 5 else (6.6 if n <= 8 else 6.0)
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color="#1A1A1A", pad=6)
    ticks = show_idx if show_idx is not None else list(range(0, len(labels), max(1, len(labels) // 6)))
    ax.set_xticks(ticks)
    _lab = [_STRINGS.month_label(l) for l in labels] if (LANG == "en" and _STRINGS) else labels
    ax.set_xticklabels([_lab[i] for i in ticks])
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK)
        lbl.set_fontsize(tick_size)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_space_fmt))
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.8, zorder=0)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    ax.set_ylim(0, max(values) * 1.12)
    ax.set_xlim(-0.5, len(values) - 0.5)
    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def bar_chart(labels: list[str], values: list[float], title: str, out_path: str,
              w: float = 3.74, h: float = 2.6, fmt: str = "{:.1f}") -> None:
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(labels))
    pending = [v is None for v in values]
    values = [0.0 if v is None else v for v in values]
    ax.bar(x, values, color=BRAND_RED, width=0.65, zorder=3)
    top = max(values) or 1.0
    # Value labels must shrink as bars are added, or five-digit figures collide at 8 bars
    # in a 3.74" panel — the labels overlap and the chart reads as a smear. Found when the
    # quarterly series was widened from 5 to 8 for the jan-jun 2026 report.
    n = len(values)
    narrow_and_crowded = n > 8 and w <= 4.0
    label_size = 8 if n <= 5 else (6.6 if n <= 8 else 5.8)
    tick_size = 7.5 if n <= 5 else (6.6 if n <= 8 else 6.0)
    for i, v in enumerate(values):
        if pending[i]:
            # Draft only (--utkast-grafer): the period's slot is on the axis, visibly empty.
            ax.text(i, top * 0.02, "XX", ha="center", va="bottom",
                    fontsize=label_size, fontproperties=FP_BOLD, color=BRAND_RED)
            continue
        # Use space-thousand delimiter for integer-format labels (Swedish convention)
        if fmt == "{:.0f}" and abs(v) >= 1000:
            label = _space_thousands(int(v))
        else:
            # Swedish decimal comma. Python formats 9.0; a Swedish financial report
            # writes 9,0 everywhere else in the document, so the charts must match.
            label = fmt.format(v)
            if LANG != "en":
                label = label.replace(".", ",")
        if not narrow_and_crowded:
            ax.text(i, v + top * 0.02, label, ha="center", va="bottom",
                    fontsize=label_size, fontproperties=FP_BOLD, color="#1A1A1A")
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color="#1A1A1A", pad=6)
    ax.set_xticks(x)
    # Thin the axis labels on a narrow, crowded chart — thirteen month labels in one
    # column of a two-column page run together into an unreadable band.
    _lab = [_STRINGS.month_label(l) for l in labels] if (LANG == "en" and _STRINGS) else labels
    ax.set_xticklabels([l if (not narrow_and_crowded or i % 2 == 0) else ""
                        for i, l in enumerate(_lab)])
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK)
        lbl.set_fontsize(tick_size)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_space_fmt))
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.8, zorder=0)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    ax.set_ylim(0, top * 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def flow_chart(labels: list[str], new: list[float], lost: list[float], net: list[float],
               title: str, out_path: str, after_from: int | None = None,
               w: float = 3.74, h: float = 2.6) -> None:
    """Customer flow per day on ONE scale: new and lost as directly labelled lines, net as
    green/red bars from zero. No legend. Months from `after_from` lie after the report period
    and sit on a light band (Henrik 2026-11-18: clean, keep the net, one scale)."""
    en = LANG == "en"
    GROW, SHRINK = "#9CC3BA", "#E2A6A4"
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(labels))
    new_a, lost_a, net_a = np.array(new, float), np.array(lost, float), np.array(net, float)
    ax.bar(x, net_a, color=[GROW if v >= 0 else SHRINK for v in net_a], width=0.62, zorder=2)
    ax.axhline(0, color="#888888", linewidth=0.6, zorder=3)
    ax.plot(x, new_a, color=BRAND_NAVY, linewidth=1.8, zorder=4)
    ax.plot(x, lost_a, color=BRAND_RED, linewidth=1.8, zorder=4)
    hi = max(new_a.max(), lost_a.max()); lo = min(0, net_a.min())
    ax.set_ylim(lo * 1.3 if lo < 0 else 0, hi + 28)   # room above for the "Nya" label
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.set_yticks([t for t in range(0, int(hi + 28) + 1, 50)])
    if after_from is not None and after_from < len(labels):
        ax.axvspan(after_from - 0.5, len(x) - 0.4, color="#EEEEEE", zorder=0, linewidth=0)
        ax.text((after_from - 0.5 + len(x) - 0.4) / 2, ax.get_ylim()[1], "efter\nperioden" if not en else "after\nperiod",
                fontproperties=FP_BOOK, fontsize=5.2, color="#777777", va="top", ha="center")
    top_is_new = new_a[0] >= lost_a[0]
    for vals, col, txt, above in ((new_a, BRAND_NAVY, "Nya" if not en else "New", top_is_new),
                                  (lost_a, BRAND_RED, "Avslutade" if not en else "Lost", not top_is_new)):
        ax.annotate(txt, (x[0], vals[0]), xytext=(3, 6 if above else -6), textcoords="offset points",
                    ha="left", va="bottom" if above else "top", fontproperties=FP_BOLD, fontsize=6.4, color=col)
    # "Netto" beside the first bar, which is the tallest of the early run.
    ax.annotate("Netto" if not en else "Net", (x[0] + 0.35, net_a[0]), xytext=(2, 0), textcoords="offset points",
                ha="left", va="top" if net_a[0] >= 0 else "bottom", fontproperties=FP_BOLD, fontsize=6.4, color="#4E8A7E")
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color="#1A1A1A", pad=10)
    ax.text(0, 1.0, "kunder per dag, månadssnitt" if not en else "customers per day, monthly average",
            transform=ax.transAxes, fontproperties=FP_BOOK, fontsize=5.6, color="#666666", va="bottom", ha="left")
    ax.set_xticks(x)
    ax.set_xticklabels([l if (len(labels) - 1 - k) % 3 == 0 else "" for k, l in enumerate(labels)])  # anchored on the last month
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK); lbl.set_fontsize(6.6)
    ax.yaxis.grid(True, color="#E4E4E4", linewidth=0.6, zorder=0)
    for sp in ["top", "right", "left", "bottom"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _read_quarterly_csv(csv_path: Path, kvartal_col_prefix: str = "Kvartal", value_col_substring: str = "MSEK",
                        keep_pending: bool = False) -> list[tuple[str, float | None]] | None:
    """Read a quarterly Grafkälldata CSV. Returns list of (kvartal_label, value) for
    rows that have a numeric value, in order. Returns None if file missing or no rows.
    Header lookup is by PREFIX so 'Kvartal (kalenderår)' matches kvartal_col_prefix='Kvartal'."""
    import csv as _csv
    if not csv_path.exists():
        return None
    rows = []
    SKIP_PREFIXES = ("Kontroll", "Ursprunglig", "Ursprungliga", "Definition", "Validering", "SAMMA", "NOTERA", "SEK-konvertering", "Kurs")
    with csv_path.open() as f:
        reader = _csv.DictReader(f)
        # Resolve actual header column matching the prefix
        actual_kv_col = None
        for h in (reader.fieldnames or []):
            if h and h.strip().startswith(kvartal_col_prefix):
                actual_kv_col = h
                break
        if actual_kv_col is None:
            return None
        for r in reader:
            kv = (r.get(actual_kv_col) or "").strip()
            if not kv or any(kv.startswith(pfx) for pfx in SKIP_PREFIXES):
                continue
            matched = False
            for header, raw in r.items():
                if header is None or value_col_substring not in header:
                    continue
                matched = True
                if raw is None:
                    continue
                v = raw.strip().replace(" ", "").replace(",", ".")
                try:
                    rows.append((kv, float(v)))
                    break
                except ValueError:
                    pass
            else:
                # No numeric value in this row. Dropping it silently is how the jul–sep 2026
                # draft ended three charts on Q2 (a Q3 row held 'XX'). Callers that check the
                # period ask for these rows back as None.
                if keep_pending and matched and re.match(r"^Q[1-4] \d\d$", kv):
                    rows.append((kv, None))
    return rows or None

def _report_quarter_label(data: DataModel) -> str | None:
    """'Q3 26' for a report whose balance sheet is dated 2026-09-30. The balance-sheet date is
    the one date every report type carries in column 0, whatever order the flow columns use."""
    br = data.tables.get("balansrakning_koncern")
    if br is None or not br.columns:
        return None
    m = re.match(r"\s*(\d{4})-(\d{2})-\d{2}", str(br.columns[0]))
    if not m:
        return None
    y, mo = int(m.group(1)), int(m.group(2))
    return f"Q{(mo - 1) // 3 + 1} {y % 100:02d}"


_MONTHS_SV = ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti",
              "september", "oktober", "november", "december"]
_MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]


def kpi_band_comparison(data: DataModel) -> str | None:
    """'mot jul–sep 2025' — the caption under each signed KPI tile, saying what it is compared
    with, derived from the comparison column (column 1) of the income statement, so every report
    carries it without anyone typing it (Henrik 2026-11-18). meta.kpi_band_jamforelse overrides."""
    rr = data.tables.get("resultatrakning_koncern")
    if rr is None or len(rr.columns) < 2:
        return None
    col = str(rr.columns[1])
    m = (re.match(r"\s*(\d{4})-(\d{2})-\d{2}\s*[–-]\s*(\d{4})-(\d{2})-\d{2}", col)
         or re.match(r"\s*(\d{4})(\d{2})\s*-\s*(\d{4})(\d{2})\s*$", col))   # BDO token 202501-202503
    if not m:
        return None
    y1, m1, y2, m2 = (int(g) for g in m.groups())
    names = _MONTHS_EN if LANG == "en" else _MONTHS_SV
    short = lambda n: n[:3]
    span = (f"{short(names[m1-1])}–{short(names[m2-1])} {y2}" if y1 == y2
            else f"{short(names[m1-1])} {y1}–{short(names[m2-1])} {y2}")
    return f"vs {span}" if LANG == "en" else f"mot {span}"


def build_placeholder_charts(data: DataModel, out_dir: Path,
                             data_path: Path | None = None,
                             allow_pending: bool = False) -> list[dict[str, str]]:
    """Build chart PNGs. Source series come from <period>/Grafkälldata/*.csv.

    grafkalldata_dir is derived from data_path — where the SOURCE lives — never from
    out_dir. Deriving it from the output path made the source directory move whenever the
    PDF was written somewhere else: rendering to Layoutad/Archive/ resolved it to
    Layoutad/Grafkälldata, which does not exist, and every chart silently degraded. That
    shipped placeholder charts in the published jan-jun 2026 report (2026-08-25).

    A spec that names a CSV and cannot read it is a FAILURE, not a fallback. Only specs
    with csv_name=None may fall back to the 2-bar KPI chart.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    k = data.kpis
    charts = []          # Nyckeltal overview page, in order
    extra = []           # built but rendered only where a narrative block asks for them
    labels_2bar = [data.meta.period_short_compare, data.meta.period_short]

    if data.assets.get("grafkalldata_dir"):
        grafkalldata_dir = Path(data.assets["grafkalldata_dir"])
    elif data_path is not None:
        grafkalldata_dir = data_path.resolve().parent / "Grafkälldata"
    else:
        raise ChartSourceError(
            "build_placeholder_charts needs data_path to locate Grafkälldata/. "
            "Deriving it from the output path is what shipped placeholder charts on 2026-08-25."
        )
    chart_errors: list[str] = []
    # Guard 25: a quarterly chart ENDS at the report's quarter — derived from the data, never
    # from whatever the CSV's last numeric row happens to be. Before 2026-11-18 the window was
    # "last N numeric rows", so a period row holding XX was skipped and the chart quietly
    # ended a quarter early (jul–sep 2026 draft: ARR and kunder stopped at Q2 26).
    report_q = _report_quarter_label(data)
    _QLABEL = re.compile(r"^Q[1-4] \d\d$")

    # Each spec: (filename, title, kpi_key, fmt, csv_filename, csv_value_col_substring, n_bars)
    #
    # n_bars = how many trailing quarters to plot. Default 5 (last four quarters plus the
    # same quarter a year earlier). Widen it when the five-quarter window would start AT a
    # one-off peak — then the chart shows only the descent and reads as a collapse. The
    # jan-jun 2026 report widened nettoomsättning to 8 so the pre-Skype base (Q3-Q4 2024)
    # is visible alongside the Q2 2025 spike; without it the same data tells the opposite
    # story. Check this whenever a period is compared against an exceptional prior quarter.
    # (filename, title, kpi_key, fmt, csv_filename, csv_value_col_substring, n_bars, on_nyckeltal, wide[, kind])
    #
    # kind defaults to 'bar'. Use 'line' for a long monthly series — thirty months of bars
    # in one column is unreadable, and a line carries the shape better.
    #
    # on_nyckeltal=False builds the chart but keeps it OFF the Nyckeltal overview page. Use it
    # for charts that a narrative block renders inline. Henrik 2026-08-20: the Nyckeltal page
    # stays as it is, and an inline chart must be a DIFFERENT cut of the data — showing the
    # same chart twice in one report is wasted space.
    #
    # n_bars = trailing periods to plot. Default 5. Widen it when a five-period window would
    # start AT a one-off peak; then the chart shows only the descent and reads as a collapse.
    specs = [
        ("chart_intakt_kvartal.png", "Nettoomsättning per kvartal (MSEK)", "nettoomsattning", "{:.1f}",
         "nettoomsattning_per_kvartal_källdata.csv", "Nettoomsättning", 8, True, False, "bar"),
        ("chart_arr.png", "Årligt värde (MSEK) av kundabonnemang (ARR)", "arr", "{:.1f}",
         "arr_per_kvartal_källdata.csv", "MSEK", 8, True, False, "bar"),
        ("chart_kunder.png", "Betalande abonnemangskunder", "aktiva_betalande_kunder", "{:.0f}",
         "kunder_per_kvartal_källdata.csv", "Antal", 8, True, False, "bar"),
        ("chart_telefonnummer.png", "Kundabonnemang virtuella telefonnummer", None, "{:.0f}",
         "telefonnummer_per_kvartal_källdata.csv", "Antal", 8, True, False, "bar"),
        ("chart_premium.png", "Kundabonnemang Premium", None, "{:.0f}",
         "premium_per_kvartal_källdata.csv", "Antal", 8, True, False, "bar"),
        # Replaced on the Nyckeltal page by the customer flow from jul-sep 2026 (Henrik
        # 2026-11-18): the flow shows inflow, churn and net, not inflow alone. Kept off-page
        # so a narrative block can still use it.
        ("chart_nya_kunder.png", "Nya betalande kunder per kvartal", None, "{:.0f}",
         "nya_kunder_per_kvartal_källdata.csv", "Antal", 8, False, False, "bar"),
        ("chart_kundflode.png", "Betalande kunder: inflöde och bortfall", None, "{:.0f}",
         "kundflode_per_manad_källdata.csv", "per dag", 18, True, False, "flow"),
        # --- inline only, different cuts of data the overview page already covers ---
        ("chart_premium_andel.png", "Andel kunder med Premium eller Business (%)", None, "{:.1f}",
         "premium_andel_per_kvartal_källdata.csv", "Andel", 8, False, False, "bar"),
        ("chart_kunder_manad.png", "Betalande kunder", None, "{:.0f}",
         "kunder_per_manad_källdata.csv", "Antal", 30, False, False, "line"),
        ("chart_nya_kunder_manad.png", "Nya betalande kunder per månad", None, "{:.0f}",
         "nya_kunder_per_manad_källdata.csv", "Antal", 13, False, False, "bar"),
    ]

    def placeholder(out_path: str, title: str, msg: str = "[placeholder]\nwire time-series data"):
        fig, ax = plt.subplots(figsize=(3.74, 2.6))
        ax.text(0.5, 0.5, msg, ha="center", va="center",
                fontproperties=FP_BOOK, fontsize=10, color="#888")
        ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color=BRAND_NAVY, pad=6)
        ax.set_axis_off()
        fig.tight_layout(pad=0.5)
        fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    for fname, title, key, fmt, csv_name, csv_col, n_bars, on_nyckeltal, wide, kind in specs:
        if LANG == "en" and _STRINGS:
            title = _STRINGS.chart_title(fname, title)
        # A chart placed full-width needs a wider figure, or 13 five-digit labels collide
        # at any font size that is still legible.
        dims = {"w": 7.6, "h": 2.9} if wide else {}
        p = out_dir / fname

        # Try multi-quarter CSV first. n_bars trailing quarters; falls back to whatever
        # the CSV holds if it is shorter, as long as it has at least 5 rows.
        csv_used = False
        if kind == "flow":
            fp = grafkalldata_dir / csv_name
            rows_f = []
            if fp.exists():
                import csv as _csv
                for r in _csv.DictReader(fp.open(encoding="utf-8")):
                    try:
                        rows_f.append((r["Månad"], r["Period"], float(r["Nya per dag"]),
                                       float(r["Avslutade per dag"]), float(r["Netto per dag"])))
                    except (KeyError, TypeError, ValueError):
                        continue
            pe = (data.tables.get("balansrakning_koncern").columns[0][:7]
                  if data.tables.get("balansrakning_koncern") else None)
            if not rows_f or pe not in [r[1] for r in rows_f]:
                chart_errors.append(f"[guard 25] {fname}: '{csv_name}' has no row for the report's last "
                                    f"month {pe}" if rows_f else
                                    f"[guard 24] {fname}: source series '{csv_name}' unusable at {fp}")
                placeholder(str(p), title)
            else:
                rows_f = rows_f[-n_bars:]
                after = next((i for i, r in enumerate(rows_f) if r[1] > pe), None)
                if LANG == "en" and _STRINGS:
                    title = _STRINGS.chart_title(fname, title)
                flow_chart([r[0] for r in rows_f], [r[2] for r in rows_f], [r[3] for r in rows_f],
                           [r[4] for r in rows_f], title, str(p), after_from=after, **dims)
            entry = {"title": title, "path": str(p.resolve())}
            (charts if on_nyckeltal else extra).append(entry)
            continue
        if csv_name:
            csv_rows = _read_quarterly_csv(grafkalldata_dir / csv_name, value_col_substring=csv_col,
                                           keep_pending=True)
            if csv_rows and report_q and all(_QLABEL.match(r[0]) for r in csv_rows):
                idx = next((i for i, r in enumerate(csv_rows) if r[0] == report_q), None)
                if idx is None:
                    chart_errors.append(
                        f"[guard 25] {fname}: '{csv_name}' has no row for the report quarter "
                        f"{report_q} — last row is {csv_rows[-1][0]}. Append the period's row.")
                    csv_rows = None
                else:
                    csv_rows = csv_rows[:idx + 1]      # the axis ends at the report quarter
                    missing = [lab for lab, v in csv_rows[-n_bars:] if v is None]
                    if missing and not allow_pending:
                        chart_errors.append(
                            f"[guard 25] {fname}: '{csv_name}' has no value for {', '.join(missing)} "
                            f"(XX/PENDING). Fill it, or render a draft with --utkast-grafer.")
                        csv_rows = None
            elif csv_rows:
                # Monthly or non-standard series: no period anchor. Pending rows are dropped
                # as before; these charts are narrative-only, not on the Nyckeltal page.
                csv_rows = [r for r in csv_rows if r[1] is not None] or None
            # >=2 rather than >=5: a deliberately short series (e.g. the three months after
            # period end) is a valid chart, and the old floor silently dropped it to a placeholder.
            if csv_rows and len(csv_rows) >= 2:
                window = csv_rows[-n_bars:]
                _labels = [r[0] for r in window]
                _values = [r[1] for r in window]
                if kind == "line":
                    line_chart(_labels, _values, title, str(p), **dims)
                else:
                    bar_chart(_labels, _values, title, str(p), fmt=fmt, **dims)
                csv_used = True

        if not csv_used:
            if csv_name:
                # The spec declares a source series. Silence here is what published broken
                # charts once; it does not get a second chance.
                src = grafkalldata_dir / csv_name
                why = "directory not found" if not grafkalldata_dir.is_dir() else (
                    "file not found" if not src.exists() else "fewer than 2 usable rows")
                if any(e.startswith(f"[guard 25] {fname}:") for e in chart_errors):
                    placeholder(str(p), title)
                    entry = {"title": title, "path": str(p.resolve())}
                    (charts if on_nyckeltal else extra).append(entry)
                    continue
                chart_errors.append(
                    f"[guard 24] {fname}: source series '{csv_name}' unusable ({why}) at {src}")
                placeholder(str(p), title)
            elif key is None:
                placeholder(str(p), title)
            else:
                kp = k[key]
                if kp.current is None or kp.prior is None:
                    placeholder(str(p), title, msg=f"[TBD]\n{key} pending\noperational data")
                else:
                    bar_chart(labels_2bar, [kp.prior, kp.current], title, str(p), fmt=fmt)

        # Absolute — the template emits file://{{ chart.path }}, and a relative path there
        # produces a URL WeasyPrint silently cannot load, leaving empty chart boxes.
        entry = {"title": title, "path": str(p.resolve())}
        if on_nyckeltal:
            charts.append(entry)
        else:
            extra.append(entry)

    if chart_errors:
        raise ChartSourceError(
            "Chart source data could not be read — the report would ship placeholder charts:\n  "
            + "\n  ".join(chart_errors)
            + "\n\nGrafkälldata is located relative to data.json, not to the output PDF."
        )

    return charts, extra


# ----------------------------------------------------------- reconciliation

class ChartSourceError(RuntimeError):
    """A chart spec declares a source series that could not be read."""


class ReconciliationError(AssertionError):
    pass

def _table_row(table: FinTable, label_substring: str) -> TableRow | None:
    """Find first non-header row whose label contains label_substring (case-insensitive)."""
    needle = label_substring.lower()
    for r in table.rows:
        if r.section_header:
            continue
        if needle in r.label.lower():
            return r
    return None

def run_guards(data: DataModel, allow_date_mismatch: bool = False) -> list[str]:
    """Returns list of warnings. Raises ReconciliationError on any failure."""
    warnings: list[str] = []
    errors: list[str] = []

    # 0) No half-empty data rows. fmt_table_value renders None as the "XX" draft
    # placeholder, which is invisible in a data.json placeholder count but prints
    # straight into the published tables. A row that carries numbers in some columns
    # and None in others is a blank cell in BDO's workbook, not a section header —
    # it must be set to 0 before publication. Section headers legitimately hold only
    # None and are exempt. Found on 2026-08-20 with 11 such rows one render before
    # publication week.
    for _tname, _tab in data.tables.items():
        _rows = list(_tab.rows or [])
        for _b in (_tab.blocks or []):
            _rows.extend(_b.rows)
        for _r in _rows:
            if _r.section_header or not _r.values:
                continue
            if any(v is None for v in _r.values) and any(v is not None for v in _r.values):
                errors.append(
                    f"[guard 0] {_tname}: raden '{_r.label}' har tomma celler bland "
                    f"sina tal ({_r.values}) och skulle skriva ut platshållaren "
                    f"{_TBD_PLACEHOLDER} i den publicerade tabellen. Sätt 0."
                )

    # 1) Revenue ↔ KPI nettoomsattning
    res = data.tables.get("resultatrakning_koncern")
    if res:
        netto_row = _table_row(res, "Nettoomsättning")
        kpi_msek = data.kpis["nettoomsattning"].current
        if netto_row and netto_row.values and netto_row.values[0] is not None and kpi_msek is not None:
            table_msek = netto_row.values[0] / 1_000_000
            if abs(table_msek - kpi_msek) > 0.05:
                errors.append(
                    f"[guard 1] Nettoomsättning mismatch: tables={table_msek:.3f} MSEK vs kpis={kpi_msek} MSEK"
                )

    # 2) Rörelseresultat structural
    if res:
        summa_int = _table_row(res, "Summa intäkter")
        summa_kost = _table_row(res, "Summa rörelsens kostnader")
        ror_res = _table_row(res, "Rörelseresultat")
        if all(r and r.values for r in (summa_int, summa_kost, ror_res)):
            expected = (summa_int.values[0] or 0) + (summa_kost.values[0] or 0)
            actual = ror_res.values[0] or 0
            if abs(expected - actual) > 1:  # SEK tolerance
                errors.append(
                    f"[guard 2] Rörelseresultat structural: intäkter+kostnader={expected:,} != row={actual:,}"
                )

    # 3) Balansräkning: tillgångar = eget kapital + skulder
    bal = data.tables.get("balansrakning_koncern")
    if bal:
        summa_tg = _table_row(bal, "Summa tillgångar")
        summa_sek = _table_row(bal, "Summa skulder och eget kapital")
        if summa_tg and summa_sek and summa_tg.values and summa_sek.values:
            for i, (tg, sek) in enumerate(zip(summa_tg.values, summa_sek.values)):
                if tg is None or sek is None:
                    continue
                if abs(tg - sek) > 1:
                    errors.append(f"[guard 3] Balans skev i kolumn {i}: tillgångar={tg:,} vs skulder+ek={sek:,}")

    # 4) Kassaflöde reconciliation
    cf = data.tables.get("kassaflode_koncern")
    if cf:
        per_kf = _table_row(cf, "Periodens kassaflöde")
        ib = _table_row(cf, "vid periodens början")
        ub = _table_row(cf, "vid periodens slut")
        if all(r and r.values for r in (per_kf, ib, ub)):
            for i, (pk, ib_v, ub_v) in enumerate(zip(per_kf.values, ib.values, ub.values)):
                if pk is None or ib_v is None or ub_v is None:
                    continue
                if abs(ib_v + pk - ub_v) > 1:
                    errors.append(
                        f"[guard 4a] Kassaflöde reconciliation col {i}: IB({ib_v:,}) + KF({pk:,}) != UB({ub_v:,})"
                    )
        # Check closing cash = balansräkning Likvida medel = kpis.likvida_medel_eom
        if bal and ub and ub.values and ub.values[0] is not None:
            lm_bal = _table_row(bal, "Likvida medel")
            if lm_bal and lm_bal.values and lm_bal.values[0] is not None:
                if abs(ub.values[0] - lm_bal.values[0]) > 1:
                    errors.append(
                        f"[guard 4b] Closing cash mismatch: kassaflöde UB={ub.values[0]:,} vs balansräkning likvida medel={lm_bal.values[0]:,}"
                    )
            kpi_lm = data.kpis["likvida_medel_eom"].current
            if kpi_lm is not None:
                kpi_lm_sek = kpi_lm * 1_000_000
                if abs(ub.values[0] - kpi_lm_sek) > 100_000:  # 0.1 MSEK rounding
                    warnings.append(
                        f"[guard 4c] Likvida medel rounding: kassaflöde={ub.values[0]:,} SEK vs KPI={kpi_lm_sek:,.0f} SEK"
                    )

    # 5) YoY % consistency (skip when current/prior are null — operational KPIs flagged TODO)
    for name, k in data.kpis.items():
        if k.yoy_pct is None or k.current is None or k.prior is None:
            continue
        if k.prior == 0:
            continue
        expected = round((k.current - k.prior) / abs(k.prior) * 100)
        if abs(expected - k.yoy_pct) > 1:
            warnings.append(f"[guard 5] YoY% mismatch on {name}: expected {expected}%, declared {k.yoy_pct}%")

    # 6) Period labels — at least one column in resultatrakning_koncern should
    # encode the current period's YYYYMM tokens, and the comparison period likewise.
    if not data.meta.period_short or not data.meta.period_short_compare:
        errors.append("[guard 6a] period_short or period_short_compare is empty")
    res_table = data.tables.get("resultatrakning_koncern")
    if res_table:
        cols_joined = " ".join(res_table.columns).replace("-", "")
        # Derive YYYYMM tokens from period_short like "jul-sep 2025" → 202507, 202509
        # We don't try to be exact — just check the year+adjacent month digits are present.
        import re as _re
        # Find any 4-digit year in period_short
        m = _re.search(r"(20\d{2})", data.meta.period_short)
        if m and m.group(1)[2:] not in cols_joined:
            errors.append(
                f"[guard 6b] Year '{m.group(1)}' from period_short '{data.meta.period_short}' "
                f"not found in resultatrakning_koncern columns {res_table.columns}"
            )
        mc = _re.search(r"(20\d{2})", data.meta.period_short_compare)
        if mc and mc.group(1)[2:] not in cols_joined:
            errors.append(
                f"[guard 6c] Year '{mc.group(1)}' from period_short_compare '{data.meta.period_short_compare}' "
                f"not found in resultatrakning_koncern columns {res_table.columns}"
            )

    # 7) Footer label everywhere — checked post-render against PDF; here just ensure non-empty
    if not data.meta.footer_label:
        errors.append("[guard 7] footer_label is empty")

    # 8) Date-on-two-places
    pub = data.meta.publication_date
    sign = data.governance.vd_signing_date
    if pub != sign and not allow_date_mismatch:
        errors.append(f"[guard 8] publication_date ({pub}) != vd_signing_date ({sign}); pass --allow-date-mismatch to override")

    # 10) Board roster non-empty + has ordförande; VD lives separately
    roles = [m.roll.lower() for m in data.governance.board]
    if len(data.governance.board) < 4:
        errors.append(f"[guard 10a] Board roster too small: {len(data.governance.board)} members")
    if not any("ordförande" in r for r in roles):
        errors.append("[guard 10b] Board missing Styrelseordförande")
    if not data.governance.vd_namn:
        errors.append("[guard 10c] governance.vd_namn missing")

    # 11) Kalendarium non-empty, no XXXX dates
    if not data.kalendarium:
        errors.append("[guard 11a] Kalendarium is empty")
    for ev in data.kalendarium:
        if "X" in ev.date or "?" in ev.date:
            errors.append(f"[guard 11b] Kalendarium event '{ev.event}' has placeholder date '{ev.date}'")

    # 12) kpi_tiles values should be derivable from kpis (catches manual-sync typos)
    tile_to_kpi = {
        "ARR": ("arr", "yoy_pct", "{:+.0f}%"),
        "NETTOOMSÄTTNING": ("nettoomsattning", "yoy_pct", "{:+.0f}%"),
        "BRUTTOMARGINAL": ("bruttomarginal_pct", "current", "{:.0f}%"),
        "EBITDA": ("ebitda_pct", "current", "{:.0f}%"),
        "SaaS40": ("saas40_pct", "current", "{:.0f}%"),
        "ABONNEMANGSKUNDER": ("aktiva_betalande_kunder", "yoy_pct", "{:+.0f}%"),
    }
    TBD_TOKENS = {"TBD", "TODO", "-", "", "XX"}  # XX = canonical draft-mode placeholder

    # Fill any tile still on the draft placeholder from the KPI it maps to. The tiles restate
    # figures that already exist; typing them by hand only creates a second place to be wrong.
    for tile in data.kpi_tiles:
        if tile.get("value", "") in TBD_TOKENS:
            m = tile_to_kpi.get(tile.get("label", ""))
            if m:
                kp = data.kpis.get(m[0])
                v = getattr(kp, m[1], None) if kp else None
                if v is not None:
                    tile["value"] = m[2].format(v)

    for tile in data.kpi_tiles:
        label = tile.get("label", "")
        declared = tile.get("value", "")
        mapping = tile_to_kpi.get(label)
        if mapping is None:
            continue
        kpi_key, field, fmt = mapping
        kp = data.kpis.get(kpi_key)
        if kp is None:
            warnings.append(f"[guard 12] kpi_tiles label '{label}' references missing KPI '{kpi_key}'")
            continue
        expected_val = getattr(kp, field)
        if expected_val is None:
            # Operational KPI is null → tile should be a TBD-marker, not a fabricated number
            if declared not in TBD_TOKENS:
                warnings.append(
                    f"[guard 12] kpi_tile '{label}' shows '{declared}' but underlying kpis['{kpi_key}'].{field} is null — expected TBD"
                )
            continue
        expected = fmt.format(expected_val)
        if declared != expected:
            errors.append(
                f"[guard 12] kpi_tile '{label}' declared '{declared}' but kpis['{kpi_key}'].{field} → '{expected}'"
            )

    if errors:
        raise ReconciliationError("\n".join(errors))
    return warnings


# ------------------------------------------------------ rendered-HTML guard

PLACEHOLDER_PATTERNS = [
    re.compile(r"XXXX", re.I),
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bFIXME\b", re.I),
    re.compile(r"\?\?\?"),
    re.compile(r"\{\{|\}\}"),  # leaked Jinja tokens
]

def scan_rendered_html(html: str, footer_label: str, publication_date: str) -> list[str]:
    errors: list[str] = []
    for pat in PLACEHOLDER_PATTERNS:
        m = pat.search(html)
        if m:
            errors.append(f"[guard 9] Placeholder token '{m.group()}' found in rendered HTML at position {m.start()}")
    # Footer-label-on-every-page: presence of string-set var. Check at least one occurrence.
    if footer_label not in html:
        errors.append(f"[guard 7] footer_label '{footer_label}' not present in rendered HTML")
    return errors


# ------------------------------------------------------- summerande rader

# Which rows in each financial table are totals. BDO's workbook carries no formatting we can
# read, so the rule lives here — keyed on the table name, because the same label means different
# things in different tables ("Periodens resultat" is a total in the income statement and an
# equity component in the parent balance sheet).
SUMMA_EXACT = {
    "resultatrakning": {
        "Summa intäkter", "Summa rörelsens kostnader", "Rörelseresultat",
        "Resultat efter finansiella poster", "Periodens resultat",
    },
    # "Kortfristiga skulder" is a total despite the label — BDO omits the "Summa" prefix there.
    "balansrakning": {"Kortfristiga skulder"},
    "kassaflode": {"Periodens kassaflöde", "Likvida medel vid periodens slut"},
    "forandring_eget_kapital": set(),
}
SUMMA_PREFIX = {
    "resultatrakning": (),
    "balansrakning": ("Summa ",),
    "kassaflode": ("Kassaflöde ",),
    "forandring_eget_kapital": ("Utgående eget kapital",),
}


def mark_summa_rows(data: DataModel) -> int:
    """Flag total rows so they render bold with a rule above, matching the pre-2025 reports.

    A row that already sets `summa` in data.json is left alone, so a report can override.
    """
    n = 0
    for tname, tab in data.tables.items():
        kind = next((k for k in SUMMA_EXACT if tname.startswith(k)), None)
        if kind is None:
            continue
        rows = list(tab.rows or [])
        for b in (tab.blocks or []):
            rows.extend(b.rows)
        for r in rows:
            if r.section_header or r.values is None or r.summa:
                continue
            if r.label in SUMMA_EXACT[kind] or r.label.startswith(SUMMA_PREFIX[kind]):
                r.summa = True
                r.bold = True
                n += 1
    return n


# --------------------------------------------------------------- main render

def render(data_path: Path, out_pdf: Path, debug: bool = False,
           allow_date_mismatch: bool = False, lang: str = "sv",
           text_overlay: Path | None = None, charts_dir: Path | None = None,
           allow_pending_charts: bool = False) -> None:
    global LANG, _STRINGS, _GLOSSARY
    LANG = lang
    _STRINGS = _i18n.Strings(_i18n.load_strings(), lang == "en") if lang == "en" else None
    _GLOSSARY = _i18n.Glossary(_i18n.load_glossary(), lang == "en") if lang == "en" else None
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    data = DataModel.model_validate(raw)
    _marked = mark_summa_rows(data)
    print(f"[summa] {_marked} summerande rader markerade")
    _derived = derive_kpis(data)
    if _derived:
        print(f"[derive] {len(_derived)} KPI-värden härledda ur tabellerna")
    if not getattr(data.meta, "kpi_band_jamforelse", None):
        _note = kpi_band_comparison(data)
        if _note:
            object.__setattr__(data.meta, "kpi_band_jamforelse", _note)
            print(f"[kpi-band] {_note}")

    print(f"[render] Validated {data_path}")
    print(f"[render] Report: {data.meta.report_type} {data.meta.period_short}")

    # Reconciliation guards (pre-render)
    warnings = run_guards(data, allow_date_mismatch=allow_date_mismatch)
    for w in warnings:
        print(f"[warn] {w}")
    print("[guards] All pre-render guards passed.")

    # ---- English overlay -------------------------------------------------------------
    # AFTER the guards (they match Swedish labels) and BEFORE the charts (the two-bar
    # fallback reads meta.period_short*). Both halves of that ordering are load-bearing.
    if lang == "en":
        overlay = _i18n.load_overlay(data_path, text_overlay)
        for w in _i18n.check_freshness(overlay, data_path):
            print(f"[warn] {w}")
        for note in _i18n.apply_overlay(data, overlay):
            print(f"[warn] {note}")
        _STRINGS.bind_notice(
            translation_date=overlay.get("_translation_date", data.meta.publication_date))
        print(f"[i18n] English overlay applied from "
              f"{text_overlay or data_path.resolve().parent / 'text.en.json'}")
    _i18n.check_assets(data, [])

    # Charts
    charts_dir = charts_dir or (out_pdf.parent / "charts")
    charts, extra_charts = build_placeholder_charts(data, charts_dir, data_path=data_path,
                                                    allow_pending=allow_pending_charts)
    print(f"[render] Rendered {len(charts)} charts to {charts_dir}")

    # Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["fmt_int"] = fmt_int
    env.globals["fmt_msek"] = fmt_msek
    env.globals["fmt_decimal"] = fmt_decimal
    env.globals["fmt_table_value"] = fmt_table_value
    env.globals["format_signing_date"] = format_signing_date
    env.globals["render_table"] = render_fin_table
    env.globals["bind_range_dash"] = bind_range_dash
    env.globals["render_balansrakning"] = render_balansrakning
    env.globals["render_forandring_ek"] = render_forandring_ek
    env.globals["inline_bold_prefix"] = inline_bold_prefix
    env.globals["fmt_change"] = fmt_change
    env.globals["lang"] = lang
    env.globals["t"] = (_STRINGS.t if _STRINGS else (lambda key, sv: sv))
    env.globals["ts"] = (_STRINGS.s if _STRINGS else (lambda key, **kw: ""))
    env.globals["notice"] = (_STRINGS.notice if _STRINGS else {})
    env.globals["fmt_pct"] = lambda x: f"{int(round(x))}" if x is not None else _TBD_PLACEHOLDER

    template = env.get_template("template.html")
    skill_dir = SKILL_DIR
    default_assets = {
        "wordmark_white": str(skill_dir / "assets" / "sonetel-wordmark-white.svg"),
        "wordmark_black": str(skill_dir / "assets" / "sonetel-wordmark-black.svg"),
        "icon": str(skill_dir / "assets" / "sonetel-icon.svg"),
        "icon_white": str(skill_dir / "assets" / "sonetel-icon-white.svg"),
    }
    assets = {**default_assets, **(data.assets or {})}

    html_str = template.render(
        meta=data.meta,
        kpis=data.kpis,
        kpis_kvartal=getattr(data, "kpis_kvartal", None),
        kpi_tiles=data.kpi_tiles,
        narrative=data.narrative,
        tables=data.tables,
        share_capital=data.share_capital,
        governance=data.governance,
        disclosures=data.disclosures,
        transaktioner_narstaende=data.transaktioner_narstaende,
        kalendarium=data.kalendarium,
        definitioner=data.definitioner or [],
        boilerplate=data.boilerplate,
        charts=charts,
        # Filename -> absolute path, so a narrative block can name its own chart with a
        # "graf" key in data.json and have it rendered inline next to the text that
        # discusses it. The Nyckeltal page keeps using the ordered `charts` list.
        chart_by_name={Path(c["path"]).name: c["path"] for c in charts + extra_charts},
        assets=assets,
    )

    if _GLOSSARY:
        _GLOSSARY.raise_on_misses()
    _leftover = _i18n.scan_placeholders(html_str)
    if _leftover:
        raise _i18n.TranslationError(
            "[i18n] unsubstituted placeholder(s) reached the rendered output: "
            + ", ".join(_leftover)
            + "\nPLACEHOLDER_PATTERNS only matches doubled braces, so these print silently.")

    # Post-render guards
    post_errors = scan_rendered_html(html_str, data.meta.footer_label, data.meta.publication_date)
    if post_errors:
        if debug:
            (out_pdf.parent / "debug_output.html").write_text(html_str, encoding="utf-8")
        raise ReconciliationError("\n".join(post_errors))
    print("[guards] All post-render guards passed.")

    if debug:
        debug_html = out_pdf.parent / "debug_output.html"
        debug_html.write_text(html_str, encoding="utf-8")
        print(f"[debug] Wrote {debug_html}")

    # WeasyPrint
    css_path = TEMPLATE_DIR / "style.css"
    sheets = [CSS(filename=str(css_path))]
    if lang == "en":
        # Appended AFTER style.css: equal specificity is resolved by order, so the English
        # sheet wins. It never touches `string-set`, which is why the Swedish footer defect
        # is not this CR's to fix and the Swedish output cannot change.
        en_css = TEMPLATE_DIR / "style.en.css"
        if not en_css.exists():
            raise _i18n.TranslationError(f"--lang en needs {en_css}")
        sheets.append(CSS(filename=str(en_css)))
    HTML(string=html_str, base_url=str(TEMPLATE_DIR)).write_pdf(
        str(out_pdf),
        stylesheets=sheets,
    )
    if _DROPPED_ZERO_ROWS:
        print(f"[nollrader] {len(_DROPPED_ZERO_ROWS)} rader utelämnade (noll i samtliga kolumner)")
        for _x in _DROPPED_ZERO_ROWS:
            print(f"           - {_x}")
    print(f"[render] Wrote PDF: {out_pdf} ({out_pdf.stat().st_size:,} bytes)")


def main():
    ap = argparse.ArgumentParser(description="Render Sonetel Kvartalsredogörelse from data.json to PDF.")
    ap.add_argument("data_path", type=Path, help="Path to data.json")
    ap.add_argument("out_pdf", type=Path, help="Output PDF path")
    ap.add_argument("--debug", action="store_true", help="Also write intermediate HTML")
    ap.add_argument("--lang", choices=["sv", "en"], default="sv",
                    help="Output language. 'en' renders the unofficial English translation.")
    ap.add_argument("--text-overlay", type=Path, default=None,
                    help="Path to the English prose overlay (default: text.en.json beside data.json)")
    ap.add_argument("--charts-dir", type=Path, default=None,
                    help="Where chart PNGs are WRITTEN. Never point this at a directory whose "
                         "contents must be preserved — every PNG is rewritten unconditionally.")
    ap.add_argument("--allow-date-mismatch", action="store_true",
                    help="Allow publication_date != vd_signing_date")
    ap.add_argument("--utkast-grafer", action="store_true",
                    help="DRAFT ONLY: render a quarterly chart whose period value is still XX with an "
                         "empty, labelled slot instead of failing guard 25. Never for a release.")
    args = ap.parse_args()

    args.out_pdf.parent.mkdir(parents=True, exist_ok=True)
    try:
        render(args.data_path, args.out_pdf, debug=args.debug,
               allow_date_mismatch=args.allow_date_mismatch, lang=args.lang,
               text_overlay=args.text_overlay, charts_dir=args.charts_dir,
               allow_pending_charts=args.utkast_grafer)
    except ReconciliationError as e:
        print(f"\n[FAIL] Reconciliation:\n{e}", file=sys.stderr)
        sys.exit(2)
    except _i18n.TranslationError as e:
        print(f"\n[FAIL] Translation:\n{e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
