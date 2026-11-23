"""English-language support for the report pipeline.

The Swedish data.json is the ONLY data source. Nothing here rewrites it. Translation is a prose
overlay merged onto the validated model AFTER derive_kpis(), mark_summa_rows() and run_guards(),
plus a glossary applied at print time for table captions.

Why not translate data.json: render.py matches Swedish string literals in six places and five of
them fail SILENTLY -- derive_kpis()'s _find(), the _table_row() gates in guards 1/2/3/4a/4b/4c,
mark_summa_rows(), render_forandring_ek()'s summa test, and guard 12's kpi_tiles map. A translated
data.json produces no reconciliation at all, and nothing in the output shows it. See
CR-2026-08-25-engelsk-oversattning-halvarsrapport, Designval 1.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

I18N_DIR = Path(__file__).resolve().parent / "i18n"
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class TranslationError(RuntimeError):
    """A translation input is missing, stale or incomplete. Never rendered around."""


# --------------------------------------------------------------- loading

def load_glossary() -> dict:
    return json.loads((I18N_DIR / "glossary.en.json").read_text(encoding="utf-8"))


def load_strings() -> dict:
    return json.loads((I18N_DIR / "strings.en.json").read_text(encoding="utf-8"))


def load_overlay(data_path: Path, overlay_path: Path | None = None) -> dict:
    p = overlay_path or (data_path.resolve().parent / "text.en.json")
    if not p.exists():
        raise TranslationError(
            f"--lang en needs a prose overlay and none was found at {p}.\n"
            f"If the file exists but cannot be read, Dropbox may not have it locally: "
            f"brctl download '{p}'")
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------- freshness

def check_freshness(overlay: dict, data_path: Path) -> list[str]:
    """Warn when the overlay was translated from a different data.json.

    A whole-file hash fires on any byte change, including fields the overlay does not shadow, so
    this is a WARNING and not a hard stop -- the per-key structural checks below are the real gate.
    The overlay carries no figures by construction, so a stale overlay can only produce a stale
    phrasing, never a wrong number.
    """
    import hashlib
    recorded = overlay.get("_source_sha256")
    if not recorded:
        return ["[i18n] overlay carries no _source_sha256; provenance unknown"]
    actual = hashlib.sha256(data_path.read_bytes()).hexdigest()
    if actual != recorded:
        return [f"[i18n] overlay was translated from a different data.json "
                f"(recorded {recorded[:12]}, current {actual[:12]}) -- prose may be stale"]
    return []


# --------------------------------------------------------------- overlay merge

def _same_shape(sv, en, path: str) -> None:
    if isinstance(sv, list):
        if not isinstance(en, list) or len(sv) != len(en):
            raise TranslationError(
                f"[i18n] {path}: overlay has {len(en) if isinstance(en, list) else type(en).__name__}, "
                f"source has {len(sv)} items. Counts must match exactly.")


def _looks_like_a_path(value: str) -> bool:
    return value.startswith("/") or bool(re.search(r"\.(png|jpe?g|webp|svg|csv|json)$", value, re.I))


def apply_overlay(data, overlay: dict) -> list[str]:
    """Merge English prose onto the validated model, in place. Returns warnings.

    MUST be called after run_guards() and before build_placeholder_charts(): the guards match on
    Swedish labels, and the two-bar chart fallback reads meta.period_short*.
    """
    notes: list[str] = []

    def guard_value(v, path):
        if isinstance(v, str) and _looks_like_a_path(v):
            raise TranslationError(
                f"[i18n] {path} in the overlay looks like a file path or image name ({v!r}). "
                f"Machine-read fields are never translated -- translating a chart filename makes "
                f"the chart vanish silently.")

    meta = overlay.get("meta", {})
    for k, v in meta.items():
        guard_value(v, f"meta.{k}")
        if hasattr(data.meta, k):
            setattr(data.meta, k, v)

    nar = overlay.get("narrative", {})
    for k, v in nar.items():
        if k not in data.narrative:
            notes.append(f"[i18n] overlay narrative.{k} has no counterpart in data.json; ignored")
            continue
        _same_shape(data.narrative[k], v, f"narrative.{k}")
        if isinstance(v, list) and v and isinstance(v[0], dict):
            for i, blk in enumerate(v):
                for kk, vv in blk.items():
                    guard_value(vv, f"narrative.{k}[{i}].{kk}")
                    data.narrative[k][i][kk] = vv
        else:
            if isinstance(v, list):
                for i, s in enumerate(v):
                    guard_value(s, f"narrative.{k}[{i}]")
            else:
                guard_value(v, f"narrative.{k}")
            data.narrative[k] = v

    dis = overlay.get("disclosures", {})
    for k, v in dis.items():
        if k == "kontakt" and isinstance(v, dict):
            for kk, vv in v.items():
                data.disclosures["kontakt"][kk] = vv
            continue
        if k in data.disclosures:
            _same_shape(data.disclosures[k], v, f"disclosures.{k}")
            data.disclosures[k] = v

    if "definitioner" in overlay and data.definitioner is not None:
        _same_shape(data.definitioner, overlay["definitioner"], "definitioner")
        data.definitioner = overlay["definitioner"]

    for tile in data.kpi_tiles:
        lbl = tile.get("label", "")
        if lbl in overlay.get("kpi_tiles_labels", {}):
            tile["label"] = overlay["kpi_tiles_labels"][lbl]

    kal = overlay.get("kalendarium_events", {})
    for ev in data.kalendarium:
        if ev.event in kal:
            ev.event = kal[ev.event]

    sc = overlay.get("share_capital", {})
    for k in ("marknadsplats", "bemyndigande_text", "optionsprogram_text"):
        if k in sc:
            data.share_capital[k] = sc[k]
    for row in data.share_capital.get("sammanstallning", []):
        lbl = row.get("label", "")
        if lbl in sc.get("sammanstallning_labels", {}):
            row["label"] = sc["sammanstallning_labels"][lbl]

    gov = overlay.get("governance", {})
    if "vd_titel" in gov:
        data.governance.vd_titel = gov["vd_titel"]
    if "vd_signing_location" in gov:
        data.governance.vd_signing_location = gov["vd_signing_location"]
    roles = gov.get("board_roles", {})
    for m in data.governance.board:
        if m.roll in roles:
            m.roll = roles[m.roll]

    if "transaktioner_narstaende" in overlay:
        data.transaktioner_narstaende = overlay["transaktioner_narstaende"]
    for k, v in overlay.get("assets", {}).items():
        guard_value(v, f"assets.{k}") if not _looks_like_a_path(v) else None
        if data.assets is not None and k in data.assets:
            data.assets[k] = v

    return notes


# --------------------------------------------------------------- glossary

class Glossary:
    """Swedish -> English for table captions, applied at print time.

    Never applied to data.json. The Swedish label is the key that derive_kpis(), the guards and
    mark_summa_rows() match on, so it must survive untouched until the moment a cell is written.
    """

    def __init__(self, raw: dict, active: bool):
        self.active = active
        self.rows = raw.get("row_labels", {})
        self.cols = raw.get("column_headers", {})
        self.subs = raw.get("substrings", {})
        self.first_cell = raw.get("header_first_cell", {})
        self.misses: set[str] = set()

    def row(self, label: str) -> str:
        if not self.active or not label:
            return label
        masked = _DATE_RE.sub("{DATE}", label)
        hit = self.rows.get(masked)
        if hit is None:
            self.misses.add(label)
            return label
        dates = _DATE_RE.findall(label)
        for d in dates:
            hit = hit.replace("{DATE}", d, 1)
        return hit

    def column(self, header: str) -> str:
        if not self.active or not header:
            return header
        if header in self.cols:
            return self.cols[header]
        out = header
        for sv, en in self.subs.items():
            out = out.replace(sv, en)
        if out != header:
            return out
        # Bare ISO dates and date ranges are language-neutral and legitimately untranslated.
        if _DATE_RE.search(header) or not re.search(r"[A-Za-zÅÄÖåäö]", header):
            return header
        self.misses.add(header)
        return header

    def cell(self, text: str) -> str:
        return self.first_cell.get(text, text) if self.active else text

    def raise_on_misses(self) -> None:
        if self.active and self.misses:
            listing = "\n".join(f"  - {m}" for m in sorted(self.misses))
            raise TranslationError(
                f"[i18n] {len(self.misses)} caption(s) have no glossary entry. An untranslated "
                f"Swedish caption in an English report reads as authoritative:\n{listing}\n"
                f"Add them to i18n/glossary.en.json.")


# --------------------------------------------------------------- strings

class Strings:
    def __init__(self, raw: dict, active: bool):
        self.active = active
        self.labels = raw.get("labels", {})
        self.sentences = raw.get("sentences", {})
        self.charts = raw.get("chart_titles", {})
        self.months = raw.get("months_abbrev", {})
        self.notice = dict(raw.get("notice", {}))

    def bind_notice(self, **values) -> None:
        """Substitute the notice's own placeholders once, at render time.

        {translation_date} leaked verbatim into a rendered PDF on 2026-08-25: it is a single-brace
        placeholder, and PLACEHOLDER_PATTERNS only matches doubled braces. Any key left unbound is
        caught by scan_placeholders() below rather than printed.
        """
        for k, v in list(self.notice.items()):
            if isinstance(v, str):
                for name, val in values.items():
                    v = v.replace("{" + name + "}", str(val))
                self.notice[k] = v

    def t(self, key: str, sv_default: str) -> str:
        """Swedish falls through to the literal that never moved, so the Swedish PDF cannot change."""
        if not self.active:
            return sv_default
        if key not in self.labels:
            raise TranslationError(
                f"[i18n] strings.en.json has no label '{key}' (Swedish: {sv_default!r})")
        return self.labels[key]

    def s(self, key: str, **kw) -> str:
        if key not in self.sentences:
            raise TranslationError(f"[i18n] strings.en.json has no sentence '{key}'")
        try:
            return self.sentences[key].format(**kw)
        except KeyError as e:
            raise TranslationError(f"[i18n] sentence '{key}' expects placeholder {e}") from None

    def chart_title(self, filename: str, sv_title: str) -> str:
        if not self.active:
            return sv_title
        if filename not in self.charts:
            raise TranslationError(f"[i18n] no English title for chart '{filename}'")
        return self.charts[filename]

    def month_label(self, label: str) -> str:
        """'maj 26' -> 'may 26'. Quarterly labels ('Q3 24') are language-neutral and pass through."""
        if not self.active:
            return label
        m = re.match(r"^([a-zåäö]{3})(\s.*)?$", label.strip(), re.I)
        if not m:
            return label
        head = m.group(1).lower()
        return (self.months.get(head, head) + (m.group(2) or "")) if head in self.months else label


# --------------------------------------------------------------- assets

def check_assets(data, notes: list[str]) -> None:
    """Every image the report references must be readable BEFORE rendering starts.

    WeasyPrint logs a missing image at ERROR and leaves an empty box; by then the PDF exists and
    looks finished. A dehydrated Dropbox file reads as missing, which is how six charts shipped as
    placeholders on 2026-08-24.
    """
    missing: list[str] = []

    def check(p, where):
        if isinstance(p, str) and p and not p.startswith(("http:", "https:", "data:")):
            if _looks_like_a_path(p) and not Path(p).exists():
                missing.append(f"  - {where}: {p}")

    for k, v in (data.assets or {}).items():
        check(v, f"assets.{k}")
    for key in ("verksamhet_under_perioden", "verksamhet_efter_perioden"):
        for i, blk in enumerate(data.narrative.get(key) or []):
            if isinstance(blk, dict):
                for kk in ("bild", "bild_bred"):
                    check(blk.get(kk), f"narrative.{key}[{i}].{kk}")
    if missing:
        listing = "\n".join(missing)
        raise TranslationError(
            "[assets] referenced image file(s) not readable:\n" + listing +
            "\nIf they exist but will not open, Dropbox may not have them locally: brctl download <path>")


_LEFTOVER = re.compile(r"\{[a-z_][a-z0-9_]{1,28}\}", re.I)


def scan_placeholders(html: str) -> list[str]:
    """Single-brace placeholders that survived into the rendered output.

    render.py's PLACEHOLDER_PATTERNS matches `{{`/`}}` only, so `{translation_date}` passed every
    existing guard and printed into a rendered PDF on 2026-08-25. Verified against both languages:
    the Swedish report contains no legitimate single-brace token.
    """
    return sorted(set(_LEFTOVER.findall(html)))
