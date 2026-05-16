#!/usr/bin/env python3
"""draft_vd_ordet.py — VD-ordet pipeline helper for Sonetel Kvartalsredogörelse.

Handles the deterministic parts of the iteration loop:
  - init-period: create the vd-ordet/ folder skeleton
  - extract-prompt: pull §10 system-prompt from the style guide into briefs/system-prompt.txt
  - draft: call openai_call.py with system + brief → drafts/vd-ordet-draft-vN.md
  - revise: call openai_call.py with system + previous draft + revision brief → drafts/vd-ordet-draft-v(N+1).md
  - log-score: append a row to critics/scores.jsonl
  - promote-final: copy drafts/vd-ordet-draft-vN.md to ../vd-ordet-final.md

The critic-agent loop (spawning Avanza retail + sell-side personas in parallel,
parsing scores) lives in Claude's PIPELINE.md workflow — that orchestration
needs Claude Code's Agent tool, not Python. This script handles only the
deterministic ops.

Usage:
  draft_vd_ordet.py init-period <period-folder>
  draft_vd_ordet.py extract-prompt <period-folder>
  draft_vd_ordet.py draft <period-folder> [--version 1]
  draft_vd_ordet.py revise <period-folder> <new-version>
  draft_vd_ordet.py log-score <period-folder> <iteration-json>
  draft_vd_ordet.py promote-final <period-folder> <version>

<period-folder> is the full path to the period's Kvartalsredogörelse folder,
e.g. /Users/henrik/.../2026/Quarter/Q1/Kvartalsredogörelse
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent  # ~/.claude/skills/kvartalsredogörelse
STYLE_GUIDE = SKILL_DIR / "vd-ordet-style-guide.md"
OPENAI_CALL = Path.home() / ".claude" / "scripts" / "openai_call.py"

SUBFOLDERS = ["briefs", "drafts", "critics", "pipeline"]


def vd_dir(period: Path) -> Path:
    """The VD-ordet working folder lives directly under the period (Kvartalsredogörelse) folder.
    Holds everything VD-ordet-related: transcript.txt + briefs/drafts/critics/pipeline + vd-ordet-final.md.
    Whole-report underlag (BDO, ledning) lives at the period root in separate folders."""
    return period / "vd-ordet"


def init_period(period: Path) -> None:
    vd = vd_dir(period)
    for sub in SUBFOLDERS:
        (vd / sub).mkdir(parents=True, exist_ok=True)
    print(f"[init] folder skeleton ready at {vd}")
    for sub in SUBFOLDERS:
        print(f"  - {sub}/")
    print(f"\nNext: drop transcript.txt into {vd}/, whole-report management material into {period.parent}/Underlag från ledning/, then `extract-prompt` and `draft`.")


def extract_prompt(period: Path) -> None:
    """Pull §10's verbatim system prompt from the style guide."""
    sg = STYLE_GUIDE.read_text(encoding="utf-8")
    # Section 10's content is the first ```...``` block after "## 10."
    m = re.search(r"## 10\.[^\n]*\n.*?\n```\n(.*?)\n```", sg, flags=re.DOTALL)
    if not m:
        sys.exit("[extract-prompt] could not locate §10 block in style guide")
    prompt = m.group(1)
    out = vd_dir(period) / "briefs" / "system-prompt.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    print(f"[extract-prompt] wrote {out} ({len(prompt.split())} words)")


def _call_openai(system_file: Path, user_file: Path, out_file: Path,
                 log_file: Path, max_tokens: int = 12000,
                 model: str = "gpt-5") -> None:
    if not OPENAI_CALL.exists():
        sys.exit(f"[draft] missing openai_call.py at {OPENAI_CALL}")
    cmd = [
        "python3", str(OPENAI_CALL),
        "--system-file", str(system_file),
        "--user-file", str(user_file),
        "--model", model,
        "--max-tokens", str(max_tokens),
    ]
    with out_file.open("w") as out, log_file.open("w") as log:
        r = subprocess.run(cmd, stdout=out, stderr=log)
    if r.returncode != 0:
        sys.exit(f"[draft] openai_call failed (rc={r.returncode}); see {log_file}")
    words = len(out_file.read_text().split())
    print(f"[draft] wrote {out_file} ({words} words)")
    print(f"[draft] log: {log_file}")


def draft(period: Path, version: int = 1) -> None:
    """Initial draft from brief-for-drafter.md."""
    vd = vd_dir(period)
    system_file = vd / "briefs" / "system-prompt.txt"
    brief = vd / "briefs" / "brief-for-drafter.md"
    if not system_file.exists():
        sys.exit(f"[draft] missing {system_file} — run `extract-prompt` first")
    if not brief.exists():
        sys.exit(f"[draft] missing {brief} — compose it from source/ first")
    out = vd / "drafts" / f"vd-ordet-draft-v{version}.md"
    log = vd / "pipeline" / f"draft-v{version}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    _call_openai(system_file, brief, out, log)


def revise(period: Path, new_version: int) -> None:
    """Revision draft from previous draft + revision-brief-vN.md.

    Assumes briefs/revision-brief-v<new_version>.md exists with the convergent
    revision instructions, and drafts/vd-ordet-draft-v<new_version-1>.md is
    the previous draft.

    Builds the user message as:
      revision-brief-vN.md
      \n---\n# SOURCE TEXT (vN-1)\n
      vd-ordet-draft-v(N-1).md content
    """
    vd = vd_dir(period)
    system_file = vd / "briefs" / "system-prompt.txt"
    rev_brief = vd / "briefs" / f"revision-brief-v{new_version}.md"
    prev_draft = vd / "drafts" / f"vd-ordet-draft-v{new_version - 1}.md"
    if not rev_brief.exists():
        sys.exit(f"[revise] missing {rev_brief} — compose revision brief first")
    if not prev_draft.exists():
        sys.exit(f"[revise] missing previous draft {prev_draft}")

    # Build combined user message in pipeline/
    user_msg = vd / "pipeline" / f"user-message-v{new_version}.md"
    user_msg.parent.mkdir(parents=True, exist_ok=True)
    user_msg.write_text(
        rev_brief.read_text()
        + f"\n\n---\n\n# SOURCE TEXT (v{new_version - 1} — APPLY THE EDITS ABOVE)\n\n"
        + prev_draft.read_text(),
        encoding="utf-8",
    )

    out = vd / "drafts" / f"vd-ordet-draft-v{new_version}.md"
    log = vd / "pipeline" / f"draft-v{new_version}.log"
    _call_openai(system_file, user_msg, out, log)


def log_score(period: Path, payload: str) -> None:
    """Append a JSON object (one line) to critics/scores.jsonl."""
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError as e:
        sys.exit(f"[log-score] invalid JSON: {e}")
    scores = vd_dir(period) / "critics" / "scores.jsonl"
    scores.parent.mkdir(parents=True, exist_ok=True)
    with scores.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"[log-score] appended to {scores}")


def promote_final(period: Path, version: int) -> None:
    """Copy a draft to vd-ordet/vd-ordet-final.md (the deliverable, inside the
    VD-ordet working folder so everything VD-ordet-related stays in one place)."""
    src = vd_dir(period) / "drafts" / f"vd-ordet-draft-v{version}.md"
    if not src.exists():
        sys.exit(f"[promote-final] missing {src}")
    dst = vd_dir(period) / "vd-ordet-final.md"
    shutil.copy2(src, dst)
    print(f"[promote-final] {src} -> {dst}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init-period")
    p.add_argument("period", type=Path)

    p = sub.add_parser("extract-prompt")
    p.add_argument("period", type=Path)

    p = sub.add_parser("draft")
    p.add_argument("period", type=Path)
    p.add_argument("--version", type=int, default=1)

    p = sub.add_parser("revise")
    p.add_argument("period", type=Path)
    p.add_argument("new_version", type=int)

    p = sub.add_parser("log-score")
    p.add_argument("period", type=Path)
    p.add_argument("payload", help="One-line JSON object to append to scores.jsonl")

    p = sub.add_parser("promote-final")
    p.add_argument("period", type=Path)
    p.add_argument("version", type=int)

    args = ap.parse_args()
    period = args.period.expanduser().resolve()
    if args.cmd == "init-period":
        init_period(period)
    elif args.cmd == "extract-prompt":
        extract_prompt(period)
    elif args.cmd == "draft":
        draft(period, args.version)
    elif args.cmd == "revise":
        revise(period, args.new_version)
    elif args.cmd == "log-score":
        log_score(period, args.payload)
    elif args.cmd == "promote-final":
        promote_final(period, args.version)


if __name__ == "__main__":
    main()
