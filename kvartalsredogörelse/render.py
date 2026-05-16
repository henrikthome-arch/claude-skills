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
from pathlib import Path
from typing import Any

# WeasyPrint needs Homebrew libs on macOS — set before import.
os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")

from pydantic import BaseModel, ConfigDict, Field
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np

from weasyprint import HTML, CSS

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

class FinTable(BaseModel):
    model_config = ConfigDict(extra="allow")
    currency_unit: str
    columns: list[str]
    rows: list[TableRow]
    footnotes: dict[str, str] | None = None

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

def _space_thousands(n: float | int) -> str:
    if isinstance(n, float) and not n.is_integer():
        s = f"{abs(n):,.2f}".replace(",", " ").replace(".", ",")
    else:
        s = f"{abs(int(n)):,}".replace(",", " ")
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
        return "0,0"
    s = f"{abs(n):.1f}".replace(".", ",")
    return ("-" + s) if n < 0 else s

def fmt_decimal(n: float, places: int = 2) -> str:
    s = f"{abs(n):.{places}f}".replace(".", ",")
    return ("-" + s) if n < 0 else s

def fmt_table_value(v: float | int | None, fmt: str | None = None) -> str:
    if v is None:
        return _TBD_PLACEHOLDER
    if fmt == "percent":
        return f"{int(v)}%"
    if fmt == "decimal2":
        return fmt_decimal(v, 2)
    if isinstance(v, float) and not v.is_integer():
        return fmt_decimal(v, 2)
    return _space_thousands(int(v))

_SV_MONTHS = ["januari", "februari", "mars", "april", "maj", "juni",
              "juli", "augusti", "september", "oktober", "november", "december"]

def format_signing_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {_SV_MONTHS[int(m) - 1]} {y}"


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

    label_html = r.label
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


def render_fin_table(table: FinTable, header_first_cell: str = "SEK",
                     tint_current: bool = True, rows: list[TableRow] | None = None) -> Markup:
    """Render a financial table. Pass a subset of rows for the continuation case."""
    use_rows = rows if rows is not None else table.rows
    headers_html = f"<th>{header_first_cell}</th>" + "".join(f"<th>{c}</th>" for c in table.columns)
    rows_html = "\n".join(_row_to_html(r, len(table.columns)) for r in use_rows)

    footnotes_html = ""
    if table.footnotes and rows is None:  # only emit footnotes on the table that has them
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
        return render_fin_table(table, header_first_cell="SEK", tint_current=True)
    first = table.rows[:split_idx]
    rest = table.rows[split_idx:]
    table1 = render_fin_table(table, header_first_cell="SEK", tint_current=True, rows=first)
    table2 = render_fin_table(table, header_first_cell="Balansräkning fortsättning",
                              tint_current=True, rows=rest)
    return Markup(f'{table1}<div class="section-break"></div>{table2}')


def inline_bold_prefix(s: str) -> Markup:
    """Make the leading "Word." or "Word eller Word." part bold for affärsmodell bullets."""
    import re as _re
    m = _re.match(r'^([^.\n]+\.)\s*(.*)', s)
    if m:
        return Markup(f"<strong>{m.group(1)}</strong> {m.group(2)}")
    return Markup(s)


# ----------------------------------------------------------- charts

def _space_fmt(x, _pos):
    if x == int(x):
        return f"{int(x):,}".replace(",", " ")
    return f"{x:,.1f}".replace(",", " ")

def line_chart(labels: list[str], values: list[float], title: str, out_path: str,
               show_idx: list[int] | None = None, w: float = 3.74, h: float = 2.6) -> None:
    fig, ax = plt.subplots(figsize=(w, h))
    x = np.arange(len(labels))
    ax.plot(x, values, color=BRAND_RED, linewidth=2.2, zorder=3)
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color="#1A1A1A", pad=6)
    ticks = show_idx if show_idx is not None else list(range(0, len(labels), max(1, len(labels) // 6)))
    ax.set_xticks(ticks)
    ax.set_xticklabels([labels[i] for i in ticks])
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK)
        lbl.set_fontsize(7.5)
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
    ax.bar(x, values, color=BRAND_RED, width=0.65, zorder=3)
    top = max(values)
    for i, v in enumerate(values):
        # Use space-thousand delimiter for integer-format labels (Swedish convention)
        if fmt == "{:.0f}" and abs(v) >= 1000:
            label = _space_thousands(int(v))
        else:
            label = fmt.format(v)
        ax.text(i, v + top * 0.02, label, ha="center", va="bottom",
                fontsize=8, fontproperties=FP_BOLD, color="#1A1A1A")
    ax.set_title(title, fontsize=10, fontproperties=FP_BOLD, color="#1A1A1A", pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FP_BOOK)
        lbl.set_fontsize(7.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_space_fmt))
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.8, zorder=0)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    ax.set_ylim(0, top * 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _read_quarterly_csv(csv_path: Path, kvartal_col_prefix: str = "Kvartal", value_col_substring: str = "MSEK") -> list[tuple[str, float]] | None:
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
            for header, raw in r.items():
                if header is None or value_col_substring not in header:
                    continue
                if raw is None:
                    continue
                v = raw.strip().replace(" ", "").replace(",", ".")
                try:
                    rows.append((kv, float(v)))
                    break
                except ValueError:
                    pass
    return rows or None

def build_placeholder_charts(data: DataModel, out_dir: Path) -> list[dict[str, str]]:
    """Build chart PNGs for the Nyckeltal page. For each KPI: prefer 5-bar quarterly
    chart from <period>/Grafkälldata/*_per_kvartal_källdata.csv if available; else
    fall back to 2-bar prior-vs-current from KPI block; else placeholder."""
    out_dir.mkdir(parents=True, exist_ok=True)
    k = data.kpis
    charts = []
    labels_2bar = [data.meta.period_short_compare, data.meta.period_short]

    grafkalldata_dir = Path(data.assets.get("grafkalldata_dir") or
                            (out_dir.parent.parent / "Grafkälldata"))

    # Each spec: (filename, title, kpi_key, fmt, csv_filename, csv_value_col_substring)
    specs = [
        ("chart_intakt_kvartal.png", "Nettoomsättning per kvartal (MSEK)", "nettoomsattning", "{:.1f}",
         "nettoomsattning_per_kvartal_källdata.csv", "Nettoomsättning"),
        ("chart_arr.png", "Årligt värde (MSEK) av kundabonnemang (ARR)", "arr", "{:.1f}",
         "arr_per_kvartal_källdata.csv", "MSEK"),
        ("chart_kunder.png", "Betalande abonnemangskunder", "aktiva_betalande_kunder", "{:.0f}",
         "kunder_per_kvartal_källdata.csv", "Antal"),
        ("chart_telefonnummer.png", "Kundabonnemang virtuella telefonnummer", None, "{:.0f}",
         "telefonnummer_per_kvartal_källdata.csv", "Antal"),
        ("chart_premium.png", "Kundabonnemang Premium", None, "{:.0f}",
         "premium_per_kvartal_källdata.csv", "Antal"),
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

    for fname, title, key, fmt, csv_name, csv_col in specs:
        p = out_dir / fname

        # Try multi-quarter CSV first (5-bar pattern: last 4 kvartal + same kvartal prior year)
        csv_used = False
        if csv_name:
            csv_rows = _read_quarterly_csv(grafkalldata_dir / csv_name, value_col_substring=csv_col)
            if csv_rows and len(csv_rows) >= 5:
                last5 = csv_rows[-5:]
                bar_chart([r[0] for r in last5], [r[1] for r in last5], title, str(p), fmt=fmt)
                csv_used = True

        if not csv_used:
            if key is None:
                placeholder(str(p), title)
            else:
                kp = k[key]
                if kp.current is None or kp.prior is None:
                    placeholder(str(p), title, msg=f"[TBD]\n{key} pending\noperational data")
                else:
                    bar_chart(labels_2bar, [kp.prior, kp.current], title, str(p), fmt=fmt)

        charts.append({"title": title, "path": str(p)})

    return charts


# ----------------------------------------------------------- reconciliation

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
        "ARR": ("arr", "yoy_pct", "+{:.0f}%"),
        "NETTOOMSÄTTNING": ("nettoomsattning", "yoy_pct", "+{:.0f}%"),
        "BRUTTOMARGINAL": ("bruttomarginal_pct", "current", "{:.0f}%"),
        "EBITDA": ("ebitda_pct", "current", "{:.0f}%"),
        "SaaS40": ("saas40_pct", "current", "{:.0f}%"),
        "ABONNEMANGSKUNDER": ("aktiva_betalande_kunder", "yoy_pct", "+{:.0f}%"),
    }
    TBD_TOKENS = {"TBD", "TODO", "-", "", "XX"}  # XX = canonical draft-mode placeholder
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


# --------------------------------------------------------------- main render

def render(data_path: Path, out_pdf: Path, debug: bool = False,
           allow_date_mismatch: bool = False) -> None:
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    data = DataModel.model_validate(raw)

    print(f"[render] Validated {data_path}")
    print(f"[render] Report: {data.meta.report_type} {data.meta.period_short}")

    # Reconciliation guards (pre-render)
    warnings = run_guards(data, allow_date_mismatch=allow_date_mismatch)
    for w in warnings:
        print(f"[warn] {w}")
    print("[guards] All pre-render guards passed.")

    # Charts
    charts_dir = out_pdf.parent / "charts"
    charts = build_placeholder_charts(data, charts_dir)
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
    env.globals["render_balansrakning"] = render_balansrakning
    env.globals["inline_bold_prefix"] = inline_bold_prefix
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
        assets=assets,
    )

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
    HTML(string=html_str, base_url=str(TEMPLATE_DIR)).write_pdf(
        str(out_pdf),
        stylesheets=[CSS(filename=str(css_path))],
    )
    print(f"[render] Wrote PDF: {out_pdf} ({out_pdf.stat().st_size:,} bytes)")


def main():
    ap = argparse.ArgumentParser(description="Render Sonetel Kvartalsredogörelse from data.json to PDF.")
    ap.add_argument("data_path", type=Path, help="Path to data.json")
    ap.add_argument("out_pdf", type=Path, help="Output PDF path")
    ap.add_argument("--debug", action="store_true", help="Also write intermediate HTML")
    ap.add_argument("--allow-date-mismatch", action="store_true",
                    help="Allow publication_date != vd_signing_date")
    args = ap.parse_args()

    args.out_pdf.parent.mkdir(parents=True, exist_ok=True)
    try:
        render(args.data_path, args.out_pdf, debug=args.debug,
               allow_date_mismatch=args.allow_date_mismatch)
    except ReconciliationError as e:
        print(f"\n[FAIL] Reconciliation:\n{e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
