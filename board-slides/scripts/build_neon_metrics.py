#!/usr/bin/env python3
"""Deterministic generator for the board deck's WEBSITE TRAFFIC & CONVERSION slide,
pulled from the sonetel.com first-party analytics Neon DB (project sonetel-ab-testing).

Series written to financials-data/neon-metrics.json (trends_grid data_ref shape):
  - distinct_visitors   : distinct visitor cookies on the marketing site in month M, ROBOTS
                          EXCLUDED (robot rule AND no sign that JavaScript ran). Sign-in paths
                          excluded (returning customers use legacy app.sonetel.com).
  - opened_to_paid_pct  : of the PEOPLE who opened the signup page (page actually rendered:
                          `signup_started` trigger=page_load) with their first opening in month M,
                          the % who made a first payment at or after that opening.
  - opened_persons / paid_from_opened : the two integers behind that ratio.
  - paying_customers    : distinct payers (first payment, `purchase`) in month M.
  - lead_sources        : per-account first-touch UTM snapshot (portal_user_attributes).

DEFINITIONS come from sonetel.com docs/reports/2026-09-10-signup-conversion-clean-denominator.md
(Henrik: "Robots and fraud ... and duplicate attempts has to be excluded to get a proper picture").
Why not the obvious denominators -- SKILL.md §56 + its CORRECTION:
  * raw signup-page views (ab_page_views) are >50% junk: the header "Try free" link PREFETCHES
    /sign-up/ on every desktop page view and middleware logs each prefetch as a visit, plus
    headless robots (Linux Chrome, no country). Discarded.
  * the page_load event only fires when the page really renders and runs JavaScript, so robots
    and prefetches cannot fire it -- it is the right "opened" base once collapsed to people.
PEOPLE = union-find over a visitor's cookies linked by session_id (onsite events), phone number
(form_submit) and account_id (signup_completed). Removes 0.1-1.7%.
Fraud and duplicate-attempt exclusions (Henrik 2026-09-10: email-path blocks only; "already has an
account" counts as a duplicate) apply to the ATTEMPT-based rate, which is not built here -- it is
only measurable from 2026-07 (report §6-7).

Known biases: paid is a LOWER bound (~11-12% of payers can't be tied to a signup cookie; the
purchase webhook has no account_id); JS-running robots can't be seen; the latest month is ~98%
final (97.9% of payments land within 10 days). `purchase` is the legacy app.sonetel.com webhook,
being retired -- when it goes this numerator goes to zero (report §7.5). May 2026 is partial
(page_load tracking starts 2026-05-13): chart the rate from June.

Connection: reads $AB_DATABASE_URL, else AB_DATABASE_URL= from
  ~/Library/CloudStorage/Dropbox/Workspace/sonetel.com/.env.local  (READ-ONLY session).

Usage:
  python3 build_neon_metrics.py                 # print JSON to stdout
  python3 build_neon_metrics.py --write financials-data/neon-metrics.json
"""
import argparse, json, os, re, sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ENV_FILE = Path.home() / "Library/CloudStorage/Dropbox/Workspace/sonetel.com/.env.local"
START = "2026-05-01"          # first month with the page_load event (partial: from 2026-05-13)
PROBE = "claude-probe-%"      # rows written by the 2026-09-10 prefetch proof; always excluded

# Robot rule (report appendix A2), applied per visitor-month. A visitor-month is a robot if it
# matches a robot signature AND never produced a site event. Beacon page views are NOT proof of a
# person: the Aug-2026 robots are headless browsers that run JavaScript (13,806 of 14,343 beaconed).
# `recommended_country_resolved` is written server-side on any page request, so it doesn't count.
# Signature visitors who searched numbers / started signups are kept (they pay at a normal rate).
ROBOT_UA = (r"bot|crawl|spider|slurp|headless|facebookexternalhit|whatsapp|telegrambot|curl/|wget/|"
            r"python-requests|axios/|node-fetch|go-http-client|okhttp|scrapy|phantomjs")
TRAFFIC_SQL = f"""
WITH pv AS (
  SELECT to_char(timestamp,'YYYY-MM') m, visitor_id, count(*) n, count(DISTINCT page_url) np,
         bool_or(coalesce(user_agent,'') = ''
              OR user_agent ~* '{ROBOT_UA}'
              OR user_agent ~ 'Chromium/79|Chrome/79\\.'
              OR (user_agent LIKE '%X11; Linux x86_64%' AND user_agent LIKE '%Chrome/%' AND country IS NULL)) ua_robot,
         bool_or(source = 'beacon') beacon
  FROM ab_page_views
  WHERE timestamp >= '{START}' AND visitor_id IS NOT NULL AND visitor_id NOT LIKE '{PROBE}'
    AND page_url !~ '/(app|portal|dashboard|login|signin)'
  GROUP BY 1, 2),
 js AS (
  SELECT DISTINCT to_char(timestamp,'YYYY-MM') m, visitor_id FROM ab_conversions
  WHERE timestamp >= '{START}' AND source = 'onsite' AND visitor_id IS NOT NULL
    AND event_name <> 'recommended_country_resolved')
SELECT pv.m, count(*) raw,
       count(*) FILTER (WHERE NOT ((ua_robot OR n >= 300 OR np >= 50) AND js.visitor_id IS NULL)) clean
FROM pv LEFT JOIN js ON js.m = pv.m AND js.visitor_id = pv.visitor_id
GROUP BY 1 ORDER BY 1;"""

OPENED_SQL = f"""
SELECT visitor_id, min(timestamp) FROM ab_conversions
WHERE event_name = 'signup_started' AND properties->>'trigger' = 'page_load'   -- exact: drops scanner junk
  AND timestamp >= '{START}' AND visitor_id IS NOT NULL AND visitor_id NOT LIKE '{PROBE}'
GROUP BY 1;"""
EDGE_SQL = [  # (visitor, key) pairs that tie several cookies to one person
    f"""SELECT DISTINCT visitor_id, 's:' || (properties->>'session_id') FROM ab_conversions
        WHERE timestamp >= '{START}' AND visitor_id IS NOT NULL AND properties->>'session_id' IS NOT NULL""",
    """SELECT DISTINCT visitor_id, 'p:' || (properties->>'phone_number') FROM ab_conversions
       WHERE event_name = 'signup_started' AND properties->>'trigger' = 'form_submit'
         AND visitor_id IS NOT NULL AND properties->>'phone_number' IS NOT NULL""",
    """SELECT DISTINCT visitor_id, 'a:' || account_id::text FROM ab_conversions
       WHERE event_name = 'signup_completed' AND visitor_id IS NOT NULL AND account_id IS NOT NULL""",
]
PURCHASE_SQL = """SELECT visitor_id, timestamp FROM ab_conversions
                  WHERE event_name = 'purchase' AND visitor_id IS NOT NULL"""

# Where completed signups come from, per WEEK. UTM has been persisted to ab_conversions since
# CR-2026-07-01 (2026-07-02) and referrer_host since CR-2026-07-05, so the consistent window
# starts 2026-07-13 (§62). Untagged rows split into Organic search vs Direct by referrer_host —
# the old portal_user_attributes snapshot could not do that and lumped both into "Direct/SEO".
SRC_START = "2026-07-13"
SRC_BUCKETS = ["Google Ads", "Organic search", "AI search", "Direct", "Social", "Other"]
SOURCES_SQL = f"""
SELECT to_char(date_trunc('week', timestamp), 'YYYY-MM-DD') w,
  CASE
    WHEN lower(coalesce(properties->>'utm_source','')) IN ('chatgpt.com','openai','perplexity','copilot.com','gemini.google.com')
      OR lower(coalesce(properties->>'referrer_host','')) ~ 'chatgpt|openai|perplexity|copilot|gemini|claude\\.ai' THEN 'AI search'
    WHEN lower(coalesce(properties->>'utm_source','')) = 'google' THEN 'Google Ads'
    WHEN lower(coalesce(properties->>'utm_source','')) IN ('fb','ig','fb-sitelink','instagram','facebook') THEN 'Social'
    WHEN (properties->>'utm_source') IS NULL
      AND lower(coalesce(properties->>'referrer_host','')) ~ 'google|bing|duckduckgo|brave|yahoo|yandex|ecosia' THEN 'Organic search'
    WHEN (properties->>'utm_source') IS NULL AND coalesce(properties->>'referrer_host','') = '' THEN 'Direct'
    ELSE 'Other' END b,
  count(DISTINCT visitor_id) n
FROM ab_conversions
WHERE event_name = 'signup_completed' AND timestamp >= '{SRC_START}' AND timestamp < %s
GROUP BY 1, 2;"""

MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Lead-source snapshot (per-account first-touch UTM, portal_user_attributes).
# NOTE: only PAID/tagged traffic carries UTM — organic SEO is untagged and falls into
# the 'direct' bucket (can't be split from direct here; needs GA4). So label google as
# "Google Ads" (it is 100% cpc) and the untagged bucket as "Direct/SEO".
LEAD_SRC_SQL = """
SELECT lower(COALESCE(NULLIF(utm_source,''),'direct')) s, COUNT(*) n
FROM portal_user_attributes GROUP BY 1;"""
LEAD_SRC_WINDOW_SQL = "SELECT MIN(tagged_at)::date, MAX(tagged_at)::date, COUNT(*) FROM portal_user_attributes;"
SRC_LABEL = {"google": "Google Ads", "direct": "Direct/SEO", "chatgpt.com": "ChatGPT",
             "ig": "Instagram", "fb": "Facebook"}


def build_lead_sources(cur):
    cur.execute(LEAD_SRC_SQL)
    agg = {}
    total = 0
    for s, n in cur.fetchall():
        label = SRC_LABEL.get(s, "Other")
        agg[label] = agg.get(label, 0) + int(n)
        total += int(n)
    # keep named sources in a stable order, roll the rest into Other
    order = ["Google Ads", "Direct/SEO", "ChatGPT", "Instagram", "Facebook", "Other"]
    pts = [{"month": lbl, "value": round(100.0 * agg[lbl] / total, 1)}
           for lbl in order if agg.get(lbl)]
    cur.execute(LEAD_SRC_WINDOW_SQL)
    lo, hi, cnt = cur.fetchone()
    return pts, {"window": f"{lo}→{hi}", "signups": cnt}


def get_url():
    if os.environ.get("AB_DATABASE_URL"):
        return os.environ["AB_DATABASE_URL"]
    if ENV_FILE.exists():
        m = re.search(r'AB_DATABASE_URL=(\S+)', ENV_FILE.read_text())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    sys.exit("No AB_DATABASE_URL: set the env var or provide %s" % ENV_FILE)


def person_finder(cur):
    """Union-find over a visitor's cookies, linked by session_id, phone and account_id.
    Returns find(node) -> person root. Nodes are 'v:'+visitor_id plus the link keys."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for sql in EDGE_SQL:
        cur.execute(sql)
        for v, k in cur.fetchall():
            a, b = find("v:" + v), find(k)
            if a != b:
                parent[max(a, b)] = min(a, b)       # deterministic root choice
    return find


def build_paid_sources(cur, find):
    """Per week: NEW PAYING CUSTOMERS by the source of their signup. Payments carry no source of
    their own (the purchase webhook has no account_id and empty properties), so each payer person
    is traced back to the first of their signup events that carried a UTM or referrer. Payers with
    no such event are reported as 'Not traced' (6-9%/week) so the bars still total actual payers."""
    bucket = SOURCES_SQL.split("CASE", 1)[1].split("END b", 1)[0]
    cur.execute(f"""SELECT visitor_id, timestamp, CASE {bucket} END b FROM ab_conversions
                    WHERE event_name IN ('signup_completed','signup_started')
                      AND visitor_id IS NOT NULL AND timestamp >= '{SRC_START}'::date - 60""")
    src = {}
    for v, t, b in cur.fetchall():
        p = find("v:" + v)
        if b and (p not in src or t < src[p][0]):
            src[p] = (t, b)
    cur.execute(f"""SELECT visitor_id, min(timestamp) FROM ab_conversions
                    WHERE event_name = 'purchase' AND visitor_id IS NOT NULL
                      AND timestamp >= '{SRC_START}' GROUP BY 1""")
    out = defaultdict(lambda: defaultdict(int))
    seen = {}
    for v, t in cur.fetchall():                     # first payment per PERSON
        p = find("v:" + v)
        if p not in seen or t < seen[p]:
            seen[p] = t
    for p, t in seen.items():
        w = (t.date() - timedelta(days=t.weekday())).isoformat()
        out[w][src.get(p, (None, "Not traced"))[1]] += 1
    return out


def build_opened_to_paid(cur, find=None):
    """Per month: people who opened the signup page that month, and how many of them paid at or
    after their first opening that month. Months are counted independently (a person who opens
    in June and again in July counts in both — 0.5% of people), matching the report's §6 table.
    Returns {month: (persons, paid)}."""
    cur.execute(OPENED_SQL.replace("GROUP BY 1;", "GROUP BY 1, to_char(timestamp,'YYYY-MM');")
                .replace("SELECT visitor_id, min(timestamp)", "SELECT visitor_id, min(timestamp), to_char(timestamp,'YYYY-MM')"))
    opened = [(v, t, m) for v, t, m in cur.fetchall()]
    find = find or person_finder(cur)
    first_open = {}                                  # (person, month) -> first opening that month
    for v, t, m in opened:
        key = (find("v:" + v), m)
        if key not in first_open or t < first_open[key]:
            first_open[key] = t
    pays = defaultdict(list)                         # person -> payment timestamps
    cur.execute(PURCHASE_SQL)
    for v, t in cur.fetchall():
        pays[find("v:" + v)].append(t)
    out = defaultdict(lambda: [0, 0])
    for (p, m), t in first_open.items():
        out[m][0] += 1
        out[m][1] += any(pt >= t for pt in pays.get(p, ()))
    return {m: tuple(v) for m, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", default=None, help="path to write neon-metrics.json (else stdout)")
    args = ap.parse_args()
    try:
        import psycopg2
    except ImportError:
        sys.exit("psycopg2 not installed (pip install psycopg2-binary)")

    conn = psycopg2.connect(get_url())
    conn.set_session(readonly=True, autocommit=True)
    cur = conn.cursor()
    current = date.today().strftime("%Y-%m")

    cur.execute(TRAFFIC_SQL)
    traffic = [(m, int(raw), int(clean)) for m, raw, clean in cur.fetchall() if m != current]
    find = person_finder(cur)
    conv = build_opened_to_paid(cur, find)
    paid_src = build_paid_sources(cur, find)
    cur.execute(f"""SELECT to_char(timestamp,'YYYY-MM') m, count(DISTINCT visitor_id) FROM ab_conversions
                    WHERE event_name='purchase' AND timestamp >= '{START}' GROUP BY 1 ORDER BY 1""")
    payers = {m: int(n) for m, n in cur.fetchall() if m != current}
    # weekly signup sources: only complete ISO weeks (Mon-Sun)
    today = date.today()
    first_incomplete = today - timedelta(days=today.weekday())      # Monday of the current week
    cur.execute(SOURCES_SQL, (first_incomplete.isoformat(),))
    by_week = {}
    for w, b, n in cur.fetchall():
        by_week.setdefault(w, {})[b] = int(n)
    src_weeks = sorted(by_week)
    paid_weeks = [w for w in sorted(paid_src) if w < first_incomplete.isoformat()]
    lead_sources, lead_win = build_lead_sources(cur)
    conn.close()

    months = [m for m, _, _ in traffic]
    cmonths = [m for m in months if m in conv]
    out = {
        "period_label": f"{MON[int(months[0][5:])]}–{MON[int(months[-1][5:])]} {months[-1][:4]}"
        if months else "",
        "lead_source_window": lead_win,
        "series": {
            "distinct_visitors": [{"month": m, "value": c} for m, _, c in traffic],
            "distinct_visitors_raw": [{"month": m, "value": r} for m, r, _ in traffic],
            "opened_to_paid_pct": [{"month": m, "value": round(100.0 * conv[m][1] / conv[m][0], 2)}
                                   for m in cmonths],
            "opened_persons": [{"month": m, "value": conv[m][0]} for m in cmonths],
            "paid_from_opened": [{"month": m, "value": conv[m][1]} for m in cmonths],
            "paying_customers": [{"month": m, "value": payers.get(m)} for m in months],
            "lead_sources": lead_sources,
            **{f"src_{b.lower().replace(' ', '_')}":
               [{"month": w, "value": by_week[w].get(b, 0)} for w in src_weeks]
               for b in SRC_BUCKETS},
            "src_ai_share_pct": [{"month": w,
                                  "value": round(100.0 * by_week[w].get("AI search", 0)
                                                 / max(1, sum(by_week[w].values())), 1)}
                                 for w in src_weeks],
            **{f"paid_src_{b.lower().replace(' ', '_')}":
               [{"month": w, "value": paid_src[w].get(b, 0)} for w in paid_weeks]
               for b in SRC_BUCKETS + ["Not traced"]},
            "paid_src_ai_share_pct": [{"month": w,
                                       "value": round(100.0 * paid_src[w].get("AI search", 0)
                                                      / max(1, sum(paid_src[w].values())), 1)}
                                      for w in paid_weeks],
        },
        "_metadata": {
            "source": "sonetel.com Neon (sonetel-ab-testing): ab_page_views + ab_conversions",
            "definitions": "sonetel.com docs/reports/2026-09-10-signup-conversion-clean-denominator.md; board-slides SKILL.md §56 + CORRECTION",
            "distinct_visitors": "distinct visitor cookies per month on the marketing site, robots excluded (robot signature AND no site event). Sign-in paths excluded. Counts cookies (visits), not people. NOT COMPARABLE ACROSS 2026-06-10: the browser beacon switched on then and made cached pages visible (browser-only visitors 0 -> 37K Jun -> 90K Jul -> 99K Aug). Do not chart as a trend spanning June 2026 (SKILL.md §56 FINAL).",
            "opened_to_paid_pct": "people (cookies linked by session, phone, account) whose first signup_started page_load fell in month M -> % with a purchase at or after that opening. Lower bound: ~11-12% of payers can't be tied to a signup cookie.",
            "paying_customers": "distinct visitor_id with a purchase (first payment webhook) in month M.",
            "partial": "May 2026 is partial for the conversion rate (page_load tracking starts 2026-05-13) -- chart from June.",
            "finality": "97.9% of payments land within 10 days of signup; the latest complete month is ~98% final.",
        },
    }
    js = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        Path(args.write).write_text(js)
        last = cmonths[-1] if cmonths else None
        print(f"Wrote {args.write}: {len(months)} months ({months[0]}→{months[-1]}); "
              f"latest visitors {traffic[-1][2]:,} clean / {traffic[-1][1]:,} raw; "
              f"opened→paid {last}: {conv[last][1]:,}/{conv[last][0]:,}; payers {payers.get(months[-1])}.",
              file=sys.stderr)
    else:
        sys.stdout.write(js)


if __name__ == "__main__":
    main()
