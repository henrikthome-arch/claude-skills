#!/usr/bin/env python3
"""
extract_bdo.py — read BDO's period workbook into data.json tables, deterministically.

Per CR-2026-08-19. The workbook is a template copied forward for a decade, so it contains
stale sheets, stale columns inside current sheets, and stale rows below current statements.
Nothing here selects a sheet, column or row by position or by loose name: sheets come from an
explicit allowlist, columns are located by searching the header row for an expected period
token or date, and rows stop at a declared terminator.

Usage:
    python3 extract_bdo.py <workbook.xls> --period-end 2026-06-30 \
        --out <period>/tables.json [--provenance <period>/bdo-provenance.json]

Exits 2 on any verification failure. Fix the data or the map — never loosen a check.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import xlrd
except ImportError:
    sys.exit("xlrd is required: pip3 install --user xlrd")


# --------------------------------------------------------------------------- stale detection

# Labels that must never appear in an extracted table. These sit *below* the current
# statements in KKF/KF 260630 and carry 2015/16 figures in the current columns, so neither
# sheet-name nor column checks reach them. See CR-2026-08-19 §Problem Statement.
STALE_LABEL_RE = re.compile(
    r"\b\d{2}/\d{2}\s+\d+\s*mån"          # "Intäkter 15/16 6 mån"
    r"|per den 31 december uppgick"
    r"|^soliditet$",
    re.IGNORECASE,
)

# Sheets whose names are prefixes of current sheets, or which carry old template data.
# Listed so a future maintainer sees why the allowlist below is explicit.
KNOWN_STALE_SHEETS = {
    "Resultaträkning", "Balansräkning", "Kassaflöde",
    "Totalresultat och förändring EK", "Finansiella utv i sammandrag",
    "RR", "BR", "KF",
}


def _fail(msg: str) -> None:
    sys.exit(f"[extract_bdo] {msg}")


# --------------------------------------------------------------------------- period tokens

def period_tokens(period_end: _dt.date) -> dict[str, str]:
    """Derive the BDO header tokens for the agreed column set.

    Column order leads with the half-year, matching the precedent report and the render
    guards, which read values[0] against the half-year KPI block.
    """
    y, py = period_end.year, period_end.year - 1
    q_start_m = period_end.month - 2
    return {
        "h1_current": f"{y}01-{y}{period_end.month:02d}",
        "h1_prior": f"{py}01-{py}{period_end.month:02d}",
        "q_current": f"{y}{q_start_m:02d}-{y}{period_end.month:02d}",
        "q_prior": f"{py}{q_start_m:02d}-{py}{period_end.month:02d}",
    }


# --------------------------------------------------------------------------- sheet map

def build_map(period_end: _dt.date, derived_fy_token: str | None) -> dict:
    """Explicit per-sheet extraction map.

    Rev 1 of the CR tried to derive this. The workbook refutes derivation: four distinct
    column layouts and two structural shapes. An explicit map is simpler and honest.
    """
    t = period_tokens(period_end)
    tok = period_end.strftime("%y%m%d")
    y, py = period_end.year, period_end.year - 1
    pe = period_end.strftime("%m-%d")
    q_start = f"{period_end.month - 2:02d}-01"
    ytd_cur, ytd_pri = f"{y}-01-01 – {y}-{pe}", f"{py}-01-01 – {py}-{pe}"

    # Report column order: YTD current, YTD prior, Q current, Q prior, derived 12-month.
    # Labels are derived from period_end (hardcoded to 2026-06-30 until 2026-11-17).
    rr_kf_columns = [
        (ytd_cur, t["h1_current"]),
        (ytd_pri, t["h1_prior"]),
        (f"{y}-{q_start} – {y}-{pe}", t["q_current"]),
        (f"{py}-{q_start} – {py}-{pe}", t["q_prior"]),
    ]
    if derived_fy_token:
        rr_kf_columns.append((f"{py}-01-01 – {py}-12-31 (härledd)", derived_fy_token))

    bs_dates = [
        (f"{y}-{pe}", period_end),
        (f"{py}-{pe}", period_end.replace(year=py)),
        (f"{py}-12-31", _dt.date(py, 12, 31)),
    ]
    ek_blocks = [
        (ytd_cur, f"{y}-01-01", f"{y}-{pe}"),
        (ytd_pri, f"{py}-01-01", f"{py}-{pe}"),
        (f"{py}-01-01 – {py}-12-31", f"{py}-01-01", f"{py}-12-31"),
    ]

    return {
        "resultatrakning_koncern": dict(
            sheet=f"KRR {tok}", mode="A", header_row=2,
            columns=rr_kf_columns, first_row=3, stop_after=None,
        ),
        "resultatrakning_moderbolag": dict(
            sheet=f"RR {tok}", mode="A", header_row=2,
            columns=rr_kf_columns, first_row=3, stop_after=None,
        ),
        "kassaflode_koncern": dict(
            sheet=f"KKF {tok}", mode="A", header_row=2,
            columns=rr_kf_columns, first_row=3,
            stop_after="Likvida medel vid periodens slut",
        ),
        "kassaflode_moderbolag": dict(
            sheet=f"KF {tok}", mode="A", header_row=2,
            columns=rr_kf_columns, first_row=3,
            stop_after="Likvida medel vid periodens slut",
        ),
        "balansrakning_koncern": dict(
            sheet=f"KBR {tok}", mode="B", header_row=2,
            columns=bs_dates, first_row=3,
            stop_after="Summa skulder och eget kapital",
        ),
        "balansrakning_moderbolag": dict(
            sheet=f"BR {tok}", mode="B", header_row=2,
            columns=bs_dates, first_row=3,
            stop_after="Summa skulder och eget kapital",
        ),
        "forandring_eget_kapital_koncern": dict(
            sheet="Koncern Förändring i eget kap", mode="C",
            blocks=ek_blocks,
        ),
        "forandring_eget_kapital_moderbolag": dict(
            sheet="Förändring i eget kapital", mode="C",
            blocks=ek_blocks,
        ),
    }


# --------------------------------------------------------------------------- cell helpers

def _label(sheet, row: int) -> str:
    return str(sheet.cell_value(row, 0)).strip()


def _num(sheet, row: int, col: int):
    """Return a SEK amount, or None for a blank cell. Rounds, never truncates.

    Whole amounts come back as ints. Genuinely fractional values — resultat per aktie is the
    only one in these statements — keep two decimals, because rounding −0,02 kr to an integer
    prints it as 0 and silently wrongs a figure First North 4.4.6(e) requires.
    """
    v = sheet.cell_value(row, col)
    if v == "" or v is None or isinstance(v, str):
        return None
    f = float(v)
    if abs(f - round(f)) < 1e-9:
        return int(round(f))
    return round(f, 2)


def _as_date(sheet, wb, row: int, col: int):
    """Decode a header cell that may be a date-typed cell or a raw serial."""
    ct = sheet.cell_type(row, col)
    v = sheet.cell_value(row, col)
    if ct == xlrd.XL_CELL_DATE:
        y, m, d, *_ = xlrd.xldate_as_tuple(v, wb.datemode)
        return _dt.date(y, m, d)
    if ct == xlrd.XL_CELL_NUMBER and 30000 < float(v) < 60000:
        y, m, d, *_ = xlrd.xldate_as_tuple(float(v), wb.datemode)
        return _dt.date(y, m, d)
    return None


# --------------------------------------------------------------------------- modes

def _resolve_data_column(sheet, header_col: int, first_row: int, last_row: int) -> int:
    """Mode B: headers and data are not always in the same column.

    `BR 260630` carries its headers at columns 4/6/8 while the data sits at 4/7/9. Rather
    than trusting the header index, take the header column if it holds data, else the next
    column that does. Anything further away is a map error, not a quirk — fail instead.
    """
    for cand in (header_col, header_col + 1):
        hits = sum(
            1 for r in range(first_row, last_row + 1)
            if _label(sheet, r) and _num(sheet, r, cand) is not None
        )
        if hits >= 3:
            return cand
    _fail(f"{sheet.name}: no data column found at or beside header column {header_col}")


def _extract_columnar(wb, sheet, spec: dict, mode: str) -> tuple[list, list, dict]:
    hrow = spec["header_row"]
    first = spec["first_row"]

    # Row terminator. Stale rows sit below the statement in the *current* columns, so a
    # column-level check cannot see them (CR-2026-08-19).
    last = sheet.nrows - 1
    if spec.get("stop_after"):
        target = spec["stop_after"].casefold()
        for r in range(first, sheet.nrows):
            if _label(sheet, r).casefold() == target:
                last = r
                break
        else:
            _fail(f"{sheet.name}: terminator row {spec['stop_after']!r} not found")

    resolved, prov_cols = [], []
    for label, wanted in spec["columns"]:
        found = None
        for c in range(1, sheet.ncols):
            if mode == "A":
                cell = sheet.cell_value(hrow, c)
                if isinstance(cell, str) and cell.strip() == wanted:
                    found = c
                    break
            else:
                if _as_date(sheet, wb, hrow, c) == wanted:
                    found = c
                    break
        if found is None:
            _fail(f"{sheet.name}: no column with header {wanted!r} on row {hrow}")
        data_col = found if mode == "A" else _resolve_data_column(sheet, found, first, last)
        resolved.append(data_col)
        prov_cols.append({"label": label, "matched_header": str(wanted),
                          "header_col": found, "data_col": data_col})

    raw = []
    for r in range(first, last + 1):
        lab = _label(sheet, r)
        if not lab:
            continue
        if STALE_LABEL_RE.search(lab):
            _fail(f"{sheet.name} r{r}: stale row {lab!r} inside the extracted range — "
                  f"the terminator is wrong")
        raw.append((lab, [_num(sheet, r, c) for c in resolved]))

    # BDO wraps long labels over two spreadsheet rows — "Avskrivningar av materiella" /
    # "och immateriella tillgångar" — with the figures on the second. A continuation is a
    # label starting lower-case, which a section header never does in Swedish. Merge them,
    # otherwise the first half renders as an empty row of XX.
    rows = []
    for lab, values in raw:
        if rows and lab[:1].islower() and all(v is None for v in rows[-1]["values"] or [None]):
            rows[-1]["label"] = f"{rows[-1]['label']} {lab}"
            rows[-1]["values"] = values
            rows[-1].pop("section_header", None)
            continue
        entry = {"label": lab, "values": values}
        if all(v is None for v in values):
            # `section_header` is the field render.py reads; anything else renders the row as
            # data with empty cells, i.e. a line of XX.
            entry["section_header"] = True
        rows.append(entry)

    return [c[0] for c in spec["columns"]], rows, {"columns": prov_cols, "last_row": last}


ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _extract_blocks(sheet, spec: dict) -> tuple[list, list, dict]:
    """Mode C: förändring i eget kapital.

    The sheet name carries no period token and the two equity sheets do not share a row
    layout, so blocks are anchored on the ISO dates inside the IB/UB row labels. Columns are
    equity components, not periods.
    """
    # A start date can occur more than once — "Ingående eget kapital 2025-01-01" opens both
    # the full-year 2025 block and the H1 2025 block. Collect every occurrence and pair each
    # closing balance with the nearest *preceding* opening balance that matches.
    ib: list[tuple[int, str]] = []
    ub: list[tuple[int, str]] = []
    for r in range(sheet.nrows):
        lab = _label(sheet, r)
        m = ISO_RE.search(lab)
        if not m:
            continue
        low = lab.casefold()
        if low.startswith("ingående eget kapital"):
            ib.append((r, m.group(1)))
        elif low.startswith("utgående eget kapital"):
            ub.append((r, m.group(1)))

    def _pair(start_iso: str, end_iso: str):
        best = None
        for ur, ud in ub:
            if ud != end_iso:
                continue
            opens = [ir for ir, idt in ib if idt == start_iso and ir < ur]
            if not opens:
                continue
            ir = max(opens)
            if best is None or (ur - ir) < (best[1] - best[0]):
                best = (ir, ur)
        return best

    # Columns are equity components, ending in a "Summa" column whose position differs per
    # sheet (koncern c5, moderbolag c6). Read them from the header row rather than sweeping
    # for numeric columns — a sweep picks up neighbouring values and, because both sheets
    # happen to hold 62 957 874 in a non-total column, fails identically and silently.
    pairs = {}
    for label, start_iso, end_iso in spec["blocks"]:
        p = _pair(start_iso, end_iso)
        if p is None:
            _fail(f"{sheet.name}: no block anchored {start_iso} → {end_iso}")
        pairs[label] = p

    # The header row is the one immediately above the *current* blocks. Taking the first
    # 'Aktiekapital' in the sheet lands in the stale 2015–2017 block, whose columns differ.
    first_block_row = min(r0 for r0, _ in pairs.values())
    hdr_row = None
    for r in range(first_block_row - 1, -1, -1):
        if str(sheet.cell_value(r, 1)).strip().casefold() == "aktiekapital":
            hdr_row = r
            break
    if hdr_row is None:
        _fail(f"{sheet.name}: no component header row above row {first_block_row}")

    comp_labels, summa_col = [], None
    for c in range(1, sheet.ncols):
        lab = str(sheet.cell_value(hdr_row, c)).strip()
        if not lab:
            continue
        comp_labels.append(lab)
        if lab.casefold() == "summa":
            summa_col = c
            break
    if summa_col is None:
        _fail(f"{sheet.name}: no 'Summa' column on header row {hdr_row}")
    cols = list(range(1, summa_col + 1))
    if len(comp_labels) != len(cols):
        _fail(f"{sheet.name}: {len(comp_labels)} component headers on row {hdr_row} but "
              f"{len(cols)} columns up to 'Summa' — header row and data are misaligned")

    blocks, prov = [], []
    for label, start_iso, end_iso in spec["blocks"]:
        r0, r1 = pairs[label]
        if not (0 < r1 - r0 < 20):
            _fail(f"{sheet.name}: implausible block {start_iso}→{end_iso} rows {r0}–{r1}")
        rows = [{"label": _label(sheet, r),
                 "values": [_num(sheet, r, c) for c in cols]}
                for r in range(r0, r1 + 1) if _label(sheet, r)]
        blocks.append({"period": label, "rows": rows})
        prov.append({"period": label, "ib_row": r0, "ub_row": r1, "cols": cols})

    return comp_labels, blocks, {"blocks": prov, "header_row": hdr_row,
                                 "summa_col": summa_col}


# --------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("workbook")
    ap.add_argument("--period-end", required=True)
    ap.add_argument("--derived-fy-token", default=None,
                    help="Header token for the derived 12-month column, e.g. 202501-202512. "
                         "Explicit because it is an artefact of the extended fiscal year, "
                         "not something that can be derived from the period end.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--provenance", default=None)
    args = ap.parse_args()

    path = Path(args.workbook)
    if path.suffix.lower() != ".xls":
        _fail(f"{path.name}: xlrd reads .xls only. A corrected workbook in .xlsx needs the "
              f"openpyxl path (CR-2026-08-19); it is not implemented yet — do not guess.")

    period_end = _dt.date.fromisoformat(args.period_end)
    wb = xlrd.open_workbook(str(path))
    sheet_names = set(wb.sheet_names())
    smap = build_map(period_end, args.derived_fy_token)

    tables, provenance = {}, {}
    for name, spec in smap.items():
        sn = spec["sheet"]
        if sn in KNOWN_STALE_SHEETS:
            _fail(f"map error: {sn!r} is a known stale sheet")
        if sn not in sheet_names:
            _fail(f"sheet {sn!r} not in workbook")
        sheet = wb.sheet_by_name(sn)

        if spec["mode"] == "C":
            cols, payload, prov = _extract_blocks(sheet, spec)
            tables[name] = {"columns": cols, "blocks": payload}
        else:
            cols, payload, prov = _extract_columnar(wb, sheet, spec, spec["mode"])
            tables[name] = {"columns": cols, "rows": payload}
        provenance[name] = {"sheet": sn, "mode": spec["mode"], **prov}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"tables": tables}, ensure_ascii=False,
                              indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.provenance:
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        Path(args.provenance).write_text(json.dumps({
            "source_file": path.name,
            "source_sha256": sha,
            "xlrd_version": xlrd.__version__,
            "period_end": args.period_end,
            "derived_fy_token": args.derived_fy_token,
            "sheet_count": len(sheet_names),
            "tables": provenance,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"[extract_bdo] {len(tables)} tables → {out}")
    for n, t in sorted(tables.items()):
        n_rows = len(t.get("rows") or [])
        n_blocks = len(t.get("blocks") or [])
        print(f"    {n:42s} {n_rows or n_blocks:3d} {'rows' if n_rows else 'blocks'}")


if __name__ == "__main__":
    main()
