"""Builds docs/index.html from data/summit-johannesburg-2026/sessions.jsonl.

Run from the repo root: python tools/build_dashboard.py
Re-run after pulling fresh session data to regenerate the GitHub Pages site.
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "data" / "summit-johannesburg-2026" / "sessions.jsonl"
OUT = REPO_ROOT / "docs" / "index.html"


def ns_short(ns):
    return ns.split("#")[-1]


def extract_sessions():
    out = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            item = d["item"]
            af = item.get("additionalFields", {})
            title_full = af.get("title", "")
            m = re.match(r"^(.*)\|\s*([A-Z]+\d+[A-Z]?)\s*$", title_full)
            if m:
                title, code = m.group(1).strip(), m.group(2).strip()
            else:
                title, code = title_full.strip(), ""

            badge_raw = af.get("badge", "")
            level = ""
            try:
                badge = json.loads(badge_raw)
                level = (badge.get("value") or [""])[0]
            except Exception:
                pass

            tags_by_ns = {}
            for t in d.get("tags", []):
                ns = ns_short(t["tagNamespaceId"])
                tags_by_ns.setdefault(ns, []).append(t["name"])

            speakers = ""
            body = af.get("body", "")
            if body.lower().startswith("speakers:"):
                speakers = body.split(":", 1)[1].strip()

            out.append({
                "id": item["id"],
                "title": title,
                "code": code,
                "type": af.get("heading", ""),
                "level": level,
                "time": af.get("time", ""),
                "duration": af.get("durationText", ""),
                "location": af.get("location", ""),
                "speakers": speakers,
                "abstract": af.get("bodyBack", ""),
                "ctaLink": af.get("ctaLink", ""),
                "roles": tags_by_ns.get("local-tags-event-content-role", []),
                "areas": tags_by_ns.get("local-tags-event-content-area-of-interest", []),
                "topics": tags_by_ns.get("local-tags-event-content-event-topic", []),
                "industries": tags_by_ns.get("local-tags-event-content-industry", []),
                "features": tags_by_ns.get("aws-session-feature", []),
                "products": tags_by_ns.get("aws-aws-products-and-services", []),
            })

    out.sort(key=lambda s: (s["time"], s["title"]))
    return out


DATA = extract_sessions()
DATA_JSON = json.dumps(DATA, ensure_ascii=False)

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AWS Summit Johannesburg 2026 — Session Explorer</title>
<style>
.viz-root {
  color-scheme: light;
  --surface-1:      #fcfcfb;
  --page:           #f9f9f7;
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --text-muted:     #898781;
  --grid:           #e1e0d9;
  --axis:           #c3c2b7;
  --border:         rgba(11,11,11,0.10);
  --series-1:       #2a78d6;
  --series-2:       #eb6834;
  --ord-100:        #86b6ef;
  --ord-200:        #5598e7;
  --ord-300:        #2a78d6;
  --ord-400:        #184f95;
  --critical:       #d03b3b;
  --good:           #0ca30c;
  --chip-bg:        #f0efec;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-1:      #1a1a19;
    --page:           #0d0d0d;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:     #898781;
    --grid:           #2c2c2a;
    --axis:           #383835;
    --border:         rgba(255,255,255,0.10);
    --series-1:       #3987e5;
    --series-2:       #d95926;
    --ord-100:        #184f95;
    --ord-200:        #256abf;
    --ord-300:        #6da7ec;
    --ord-400:        #b7d3f6;
    --critical:       #e66767;
    --good:           #0ca30c;
    --chip-bg:        #242422;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-1:      #1a1a19;
  --page:           #0d0d0d;
  --text-primary:   #ffffff;
  --text-secondary: #c3c2b7;
  --text-muted:     #898781;
  --grid:           #2c2c2a;
  --axis:           #383835;
  --border:         rgba(255,255,255,0.10);
  --series-1:       #3987e5;
  --series-2:       #d95926;
  --ord-100:        #184f95;
  --ord-200:        #256abf;
  --ord-300:        #6da7ec;
  --ord-400:        #b7d3f6;
  --critical:       #e66767;
  --good:           #0ca30c;
  --chip-bg:        #242422;
}

* { box-sizing: border-box; }
body { margin: 0; }
.viz-root {
  background: var(--page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 20px 24px 64px;
  max-width: 1180px;
  margin: 0 auto;
}
h1 { font-size: 22px; margin: 0 0 2px; }
h2 { font-size: 15px; margin: 0 0 12px; color: var(--text-primary); }
.subtitle { color: var(--text-secondary); font-size: 13.5px; margin: 0 0 20px; }
.card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}
.stat-tile { padding: 14px 16px; }
.stat-value { font-size: 26px; font-weight: 600; line-height: 1.1; }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 18px;
  padding: 10px 12px;
}
.filter-row input, .filter-row select {
  font: inherit;
  font-size: 13px;
  padding: 6px 9px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--page);
  color: var(--text-primary);
}
.filter-row input[type="text"] { flex: 1 1 200px; min-width: 160px; }
.filter-count { font-size: 12.5px; color: var(--text-muted); margin-left: auto; white-space: nowrap; }
.filter-reset {
  font-size: 12.5px; color: var(--series-1); background: none; border: none; cursor: pointer; padding: 4px 6px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}
@media (max-width: 720px) { .charts-grid { grid-template-columns: 1fr; } }

.chart-head { display: flex; align-items: baseline; justify-content: space-between; }
.table-toggle {
  font-size: 11.5px; color: var(--text-secondary); background: none; border: 1px solid var(--border);
  border-radius: 5px; padding: 2px 7px; cursor: pointer;
}
.table-toggle:hover { color: var(--text-primary); }

.hbar-row { display: flex; align-items: center; gap: 8px; margin: 5px 0; }
.hbar-label { flex: 0 0 150px; font-size: 12px; color: var(--text-secondary); text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hbar-track { flex: 1; position: relative; height: 14px; }
.hbar-fill { position: absolute; top: 3px; height: 8px; border-radius: 4px; }
.hbar-value { font-size: 11.5px; color: var(--text-muted); flex: 0 0 22px; }

.legend { display: flex; gap: 14px; font-size: 11.5px; color: var(--text-secondary); margin-top: 8px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-swatch { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }

table.mini { width: 100%; border-collapse: collapse; font-size: 12px; }
table.mini td, table.mini th { padding: 3px 6px; text-align: left; border-bottom: 1px solid var(--grid); }
table.mini th { color: var(--text-muted); font-weight: 500; }

.section { margin-bottom: 20px; }

.agenda-card { border-left: 3px solid var(--series-1); }
.agenda-empty { color: var(--text-muted); font-size: 13px; }
.agenda-item { display: flex; gap: 10px; align-items: baseline; padding: 5px 0; font-size: 13px; border-bottom: 1px solid var(--grid); }
.agenda-item:last-child { border-bottom: none; }
.agenda-time { font-variant-numeric: tabular-nums; color: var(--text-secondary); flex: 0 0 50px; }
.agenda-title { flex: 1; }
.agenda-clash { color: var(--critical); font-size: 11.5px; font-weight: 600; }

.timeline-slot { margin-bottom: 10px; }
.timeline-time { font-size: 12.5px; font-weight: 600; color: var(--text-secondary); margin-bottom: 5px; font-variant-numeric: tabular-nums; }
.timeline-count { font-weight: 400; color: var(--text-muted); }
.session-chips { display: flex; flex-wrap: wrap; gap: 6px; }

.chip {
  background: var(--chip-bg);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 6px 9px;
  font-size: 12.5px;
  max-width: 320px;
}
.chip-title { font-weight: 500; }
.chip-meta { color: var(--text-muted); font-size: 11px; margin-top: 2px; }
.star-btn { background: none; border: none; cursor: pointer; font-size: 14px; line-height: 1; padding: 0 2px; color: var(--text-muted); }
.star-btn.starred { color: var(--ord-400); }

.session-list { display: flex; flex-direction: column; gap: 6px; }
.session-row { border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; background: var(--surface-1); }
.session-row summary { cursor: pointer; list-style: none; display: flex; gap: 10px; align-items: baseline; }
.session-row summary::-webkit-details-marker { display: none; }
.sr-time { flex: 0 0 46px; font-size: 12px; color: var(--text-secondary); font-variant-numeric: tabular-nums; }
.sr-title { flex: 1; font-size: 13.5px; font-weight: 500; }
.sr-code { color: var(--text-muted); font-weight: 400; }
.badge { font-size: 10.5px; padding: 1px 6px; border-radius: 10px; color: #fff; white-space: nowrap; }
.sr-detail { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--grid); font-size: 13px; color: var(--text-secondary); }
.sr-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.tag { font-size: 10.5px; background: var(--chip-bg); border-radius: 8px; padding: 1px 7px; color: var(--text-secondary); }
.sr-loc { color: var(--text-muted); font-size: 11.5px; margin-left: 4px; }
a.cta { color: var(--series-1); font-size: 12px; }

.insights-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }
@media (max-width: 720px) { .insights-cols { grid-template-columns: 1fr; } }
.insights-sub { margin-top: 12px; }
.insights-sub:first-child { margin-top: 0; }
.insights-subhead { font-size: 10.5px; font-weight: 600; color: var(--text-muted); margin: 0 0 6px; text-transform: uppercase; letter-spacing: 0.03em; }

.fact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px 12px;
}
.fact-tile { border-left: 3px solid var(--series-1); padding-left: 8px; }
.fact-value { font-size: 16px; font-weight: 600; line-height: 1.2; }
.fact-caption { font-size: 11px; color: var(--text-secondary); margin-top: 2px; line-height: 1.3; }

.gauge-value { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.gauge-track { position: relative; height: 10px; border-radius: 5px; background: var(--chip-bg); overflow: hidden; margin: 0 0 6px; }
.gauge-fill { position: absolute; inset: 0 auto 0 0; border-radius: 5px; background: var(--series-1); transition: width 0.4s ease; }
.gauge-caption { font-size: 11px; color: var(--text-secondary); }

.cloud-wrap { display: flex; flex-wrap: wrap; align-items: baseline; gap: 3px 8px; padding: 2px 0; }
.cloud-word { line-height: 1; }

.pairs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 6px; }
.pair-card { background: var(--chip-bg); border: 1px solid var(--border); border-radius: 7px; padding: 5px 9px; }
.pair-terms { display: flex; gap: 5px; align-items: center; font-size: 11.5px; font-weight: 500; }
.pair-terms span { color: var(--series-1); }
.pair-terms span.meta { color: var(--text-muted); font-size: 10.5px; font-weight: 400; }
.pair-connect { color: var(--text-secondary); }

.topicmap-wrap { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
.topicmap-svg-col { flex: 1 1 320px; min-width: 260px; }
.topicmap-detail { flex: 1 1 220px; min-width: 200px; background: var(--chip-bg); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; }
.topicmap-detail-empty { color: var(--text-muted); font-size: 12.5px; }
.tm-current-title { font-weight: 600; color: var(--text-primary); font-size: 13px; margin-bottom: 2px; }
.tm-current-meta { color: var(--text-muted); font-size: 11.5px; margin-bottom: 10px; }
.tm-label { font-size: 10.5px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 4px; }
.tm-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.tm-tag { font-size: 10.5px; background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px; padding: 2px 7px; color: var(--text-secondary); }
.tm-neighbor { padding: 5px 0; border-top: 1px solid var(--grid); }
.tm-neighbor-title { font-size: 12.5px; color: var(--text-primary); }
.tm-neighbor-meta { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.tab-btn {
  background: none; border: none; font: inherit; font-size: 13.5px; padding: 8px 4px 9px;
  color: var(--text-secondary); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-btn.active { color: var(--text-primary); border-bottom-color: var(--series-1); font-weight: 600; }

.level-100 { border-left: 3px solid var(--ord-100); }
.level-200 { border-left: 3px solid var(--ord-200); }
.level-300 { border-left: 3px solid var(--ord-300); }
.level-400 { border-left: 3px solid var(--ord-400); }
</style>
</head>
<body>
<div class="viz-root" id="root">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
    <div>
      <h1>AWS Summit Johannesburg 2026 — Session Explorer</h1>
      <p class="subtitle">17 July 2026 · Johannesburg Expo Centre, Nasrec · all times CAT (UTC+2)</p>
    </div>
    <button class="table-toggle" id="theme-toggle" style="flex:0 0 auto;">🌙 Dark</button>
  </div>

  <div class="stats-row" id="stats"></div>

  <div class="section card">
    <h2>The agenda, decoded <span style="font-weight:400;color:var(--text-muted)">— a few inferences pulled from all 93 sessions</span></h2>
    <div class="insights-cols">
      <div class="insights-col">
        <div class="fact-grid" id="fun-facts"></div>
        <div class="insights-sub">
          <h3 class="insights-subhead">Agentic AI hype-o-meter</h3>
          <div class="gauge-value" id="gauge-value"></div>
          <div class="gauge-track"><div class="gauge-fill" id="gauge-fill"></div></div>
          <div class="gauge-caption" id="gauge-caption"></div>
        </div>
      </div>
      <div class="insights-col">
        <div class="insights-sub">
          <h3 class="insights-subhead">Buzzword cloud <span style="font-weight:400;text-transform:none;letter-spacing:normal">— most-repeated words</span></h3>
          <div class="cloud-wrap" id="cloud"></div>
        </div>
        <div class="insights-sub">
          <h3 class="insights-subhead">Emerging topics <span style="font-weight:400;text-transform:none;letter-spacing:normal">— less common but potent</span></h3>
          <div class="pairs-grid" id="emerging"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="section card">
    <div class="chart-head"><h2>Topic map <span style="font-weight:400;color:var(--text-muted)">— sessions positioned by shared tags; closer dots share more themes</span></h2><button class="table-toggle" data-target="chart-topicmap">Table</button></div>
    <div id="chart-topicmap"></div>
  </div>

  <div class="card filter-row">
    <input type="text" id="f-search" placeholder="Search title, speaker, abstract, tags, products…">
    <select id="f-level"><option value="">All levels</option></select>
    <select id="f-type"><option value="">All session types</option></select>
    <select id="f-area"><option value="">All areas of interest</option></select>
    <span class="filter-count" id="f-count"></span>
    <button class="filter-reset" id="f-reset">Reset filters</button>
  </div>

  <div class="section card agenda-card">
    <h2>My Agenda <span style="font-weight:400;color:var(--text-muted)">— star sessions below to build your day</span></h2>
    <div id="agenda"></div>
  </div>

  <div class="section">
    <div class="charts-grid">
      <div class="card">
        <div class="chart-head"><h2>Sessions by level</h2><button class="table-toggle" data-target="chart-level">Table</button></div>
        <div id="chart-level"></div>
      </div>
      <div class="card">
        <div class="chart-head"><h2>Sessions by format</h2><button class="table-toggle" data-target="chart-type">Table</button></div>
        <div id="chart-type"></div>
      </div>
      <div class="card">
        <div class="chart-head"><h2>Top areas of interest</h2><button class="table-toggle" data-target="chart-area">Table</button></div>
        <div id="chart-area"></div>
      </div>
      <div class="card">
        <div class="chart-head"><h2>Most-mentioned AWS products</h2><button class="table-toggle" data-target="chart-product">Table</button></div>
        <div id="chart-product"></div>
      </div>
    </div>
  </div>

  <div class="section card">
    <div class="tabs">
      <button class="tab-btn active" data-tab="list">All sessions <span id="sl-count" style="font-weight:400"></span></button>
      <button class="tab-btn" data-tab="timeline">Schedule at a glance</button>
    </div>
    <div id="tab-list"><div class="session-list" id="session-list"></div></div>
    <div id="tab-timeline" style="display:none"><div id="timeline"></div></div>
  </div>
</div>

<script>
const SESSIONS = __DATA_JSON__;

const LEVEL_COLOR = { "100": "var(--ord-100)", "200": "var(--ord-200)", "300": "var(--ord-300)", "400": "var(--ord-400)" };
const LEVEL_ORDER = ["100", "200", "300", "400"];

function parseLevel(raw) {
  if (!raw) return { code: "", label: "Unspecified" };
  const parts = raw.split(/[–-]/);
  return { code: parts[0].trim(), label: (parts[1] || "").trim() || raw.trim() };
}
function toMinutes(hhmm) {
  const [h, m] = hhmm.slice(0, 5).split(":").map(Number);
  return h * 60 + m;
}
function durationMinutes(text) {
  const m = /(\d+)/.exec(text || "");
  return m ? parseInt(m[1], 10) : 0;
}
function fmtTime(mins) {
  const h = Math.floor(mins / 60), m = mins % 60;
  return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
}

const rows = SESSIONS.map(s => {
  const lvl = parseLevel(s.level);
  const start = toMinutes(s.time);
  const dur = durationMinutes(s.duration);
  return { ...s, levelCode: lvl.code, levelLabel: lvl.label, start, dur, end: start + dur, timeLabel: fmtTime(start) };
});

// ---- Fun facts, hype meter, buzzword cloud, emerging terms & clusters: computed once from the full unfiltered agenda ----
const STOPWORDS = new Set(("this that with from your have will into their about across through these those where "
  + "which while when what how session sessions aws amazon summit using learn learns learned discover discovers "
  + "explore explores join joins attend during including between after before more most also such some many best "
  + "real world need needs help build builds building built news teams team today future just like well take takes "
  + "you your yours youll youre weve well were was were will would could should does doing dive dives look looks "
  + "into onto over under only than then them they were work works working ways way part parts each every both "
  + "share shares shared come comes gain gains hear hands full end come along right here there").split(/\s+/));

function tokenize(text) {
  return (text || "").toLowerCase().replace(/[^a-z0-9\s-]/g, " ").split(/\s+/)
    .filter(w => w.length > 3 && !STOPWORDS.has(w));
}
function titleCase(s) {
  return s.replace(/[-_]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}
function shortProduct(name) {
  const m = /\(([^)]+)\)\s*$/.exec(name);
  return m ? m[1] : name;
}

const AI_RE = /\b(ai|agent|agentic|genai|llm|bedrock)\b/i;
function mentionsAI(r) {
  return AI_RE.test(r.title) || AI_RE.test(r.abstract) || (r.areas || []).some(a => /gen-ai/i.test(a))
    || (r.products || []).some(p => /bedrock|sagemaker|amazon q/i.test(p));
}

function renderFunFacts() {
  const totalMin = rows.reduce((a, r) => a + r.dur, 0);
  const aiCount = rows.filter(mentionsAI).length;
  const slotCounts = countBy(rows, r => r.timeLabel);
  const [busiestSlot, busiestN] = [...slotCounts.entries()].sort((a, b) => b[1] - a[1])[0];
  const typeCounts = countBy(rows, r => r.type);
  const [rarestType, rarestN] = [...typeCounts.entries()].sort((a, b) => a[1] - b[1])[0];
  const laptopCount = rows.filter(r => (r.features || []).some(f => /laptop/i.test(f))).length;
  const mysteryCount = rows.filter(r => !r.speakers).length;

  const facts = [
    [`${totalMin >= 60 ? Math.floor(totalMin / 60) + "h " : ""}${totalMin % 60}m`,
      "of content if you tried to attend every single session back to back — good luck with that."],
    [`${busiestSlot} · ${busiestN} sessions`,
      "the single busiest time slot of the day. Pick your battles."],
    [`${rarestN} × ${rarestType}`,
      "the rarest session format at the whole summit — blink and it's over."],
    [`${laptopCount} sessions`,
      "want you to bring a laptop. Charge it tonight, not at the one free power outlet."],
    [`${mysteryCount} sessions`,
      "don't name a speaker in the data — mystery presenters, or AWS keeping it a surprise."],
    [`${uniqueSorted(rows.map(r => r.location)).length} venues`,
      "in play across the day — floor plan open in another tab is not optional."],
  ];
  document.getElementById("fun-facts").innerHTML = facts.map(([v, c]) =>
    `<div class="fact-tile"><div class="fact-value">${v}</div><div class="fact-caption">${c}</div></div>`
  ).join("");

  const pct = Math.round(aiCount / rows.length * 100);
  document.getElementById("gauge-value").textContent = pct + "%";
  document.getElementById("gauge-fill").style.width = pct + "%";
  document.getElementById("gauge-caption").textContent =
    `${aiCount} of ${rows.length} sessions mention AI, agents, or Bedrock by name — allergic to hype? that leaves ${rows.length - aiCount} sessions to hide in.`;
}

function renderCloud() {
  const freq = new Map();
  rows.forEach(r => tokenize(r.title + " " + r.abstract).forEach(w => freq.set(w, (freq.get(w) || 0) + 1)));
  const top = [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 28);
  const maxF = top[0][1], minF = top[top.length - 1][1];
  const scaled = top.map(([w, f], i) => ({
    w, f, i,
    size: 10.5 + (maxF === minF ? 4 : (f - minF) / (maxF - minF) * 14),
  }));
  // shuffle deterministically for an organic layout, seeded by word so it's stable across renders
  scaled.sort((a, b) => (a.w.charCodeAt(0) + a.w.length) - (b.w.charCodeAt(0) + b.w.length));
  document.getElementById("cloud").innerHTML = scaled.map(({ w, f, i, size }) => {
    const emphasize = i < 3;
    const color = emphasize ? "var(--series-1)" : "var(--text-secondary)";
    const weight = emphasize ? 700 : 400;
    return `<span class="cloud-word" style="font-size:${size.toFixed(0)}px;color:${color};font-weight:${weight}" title="${w}: ${f} mentions">${w}</span>`;
  }).join("");
}

function renderEmerging() {
  const freq = new Map();
  rows.forEach(r => tokenize(r.title + " " + r.abstract).forEach(w => freq.set(w, (freq.get(w) || 0) + 1)));
  const topWords = new Set([...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 32).map(([w]) => w));

  // Find words with 2–4 mentions, excluding top 32
  const emerging = [...freq.entries()]
    .filter(([w, f]) => !topWords.has(w) && f >= 2 && f <= 4)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([w, f]) => ({ w: titleCase(w), f }));

  document.getElementById("emerging").innerHTML = emerging.map(({ w, f }) =>
    `<div class="pair-card"><div class="pair-terms"><span>${w}</span><span class="meta">${f}×</span></div></div>`
  ).join("");
}

// Topic map: a 2D PCA projection of each session's tag vector (areas + topics + products) —
// a lightweight stand-in for a full semantic embedding, computed instantly with no dependencies.
function buildTagVocab() {
  const counts = countBy(rows, r => [...(r.areas || []), ...(r.topics || []), ...(r.products || []).map(shortProduct)]);
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 30).map(([t]) => t);
}
function sessionVector(r, vocab) {
  const tags = new Set([...(r.areas || []), ...(r.topics || []), ...(r.products || []).map(shortProduct)]);
  return vocab.map(t => (tags.has(t) ? 1 : 0));
}
function pca2(vectors) {
  const n = vectors.length, d = vectors[0].length;
  const mean = new Array(d).fill(0);
  vectors.forEach(v => v.forEach((x, i) => { mean[i] += x; }));
  for (let i = 0; i < d; i++) mean[i] /= n;
  const centered = vectors.map(v => v.map((x, i) => x - mean[i]));

  const cov = Array.from({ length: d }, () => new Array(d).fill(0));
  centered.forEach(v => {
    for (let i = 0; i < d; i++) {
      if (!v[i]) continue;
      for (let j = 0; j < d; j++) cov[i][j] += v[i] * v[j];
    }
  });
  for (let i = 0; i < d; i++) for (let j = 0; j < d; j++) cov[i][j] /= n;

  const matVec = (m, v) => m.map(row => row.reduce((s, x, i) => s + x * v[i], 0));
  const norm = v => Math.sqrt(v.reduce((s, x) => s + x * x, 0)) || 1;
  function topEigen(mat) {
    let v = Array.from({ length: d }, (_, i) => (i % 2 === 0 ? 1 : -1));
    for (let k = 0; k < 60; k++) {
      v = matVec(mat, v);
      const nrm = norm(v);
      v = v.map(x => x / nrm);
    }
    const mv = matVec(mat, v);
    const val = v.reduce((s, x, i) => s + x * mv[i], 0);
    return { vec: v, val };
  }
  const e1 = topEigen(cov);
  const cov2 = cov.map((row, i) => row.map((x, j) => x - e1.val * e1.vec[i] * e1.vec[j]));
  const e2 = topEigen(cov2);

  return centered.map(v => [
    v.reduce((s, x, i) => s + x * e1.vec[i], 0),
    v.reduce((s, x, i) => s + x * e2.vec[i], 0),
  ]);
}

function renderTopicMap() {
  const el = document.getElementById("chart-topicmap");
  const vocab = buildTagVocab();
  if (vocab.length < 2) { el.innerHTML = "<p style='color:var(--text-muted);font-size:13px'>Not enough tag data to map.</p>"; return; }
  const vectors = rows.map(r => sessionVector(r, vocab));

  if (chartState.topicmap === "table") {
    const sims = [];
    for (let i = 0; i < rows.length; i++) {
      for (let j = i + 1; j < rows.length; j++) {
        let shared = 0;
        for (let k = 0; k < vocab.length; k++) if (vectors[i][k] && vectors[j][k]) shared++;
        if (shared >= 3) sims.push([`${rows[i].title} ↔ ${rows[j].title}`, shared]);
      }
    }
    sims.sort((a, b) => b[1] - a[1]);
    el.innerHTML = tableTwin(sims.slice(0, 15), ["Session pair", "Shared tags"]);
    return;
  }

  const coords = pca2(vectors);
  const xs = coords.map(c => c[0]), ys = coords.map(c => c[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const W = 480, H = 280, PAD = 18;
  const sx = x => PAD + (maxX === minX ? 0.5 : (x - minX) / (maxX - minX)) * (W - 2 * PAD);
  const sy = y => PAD + (maxY === minY ? 0.5 : (y - minY) / (maxY - minY)) * (H - 2 * PAD);

  const dots = rows.map((r, i) => {
    const cx = sx(coords[i][0]).toFixed(1), cy = sy(coords[i][1]).toFixed(1);
    const color = LEVEL_COLOR[r.levelCode] || "var(--text-muted)";
    const title = `${r.title} (${r.code}) — Level ${r.levelCode || "unspecified"}`;
    return `<circle cx="${cx}" cy="${cy}" r="5" fill="${color}" fill-opacity="0.85" stroke="var(--surface-1)" stroke-width="1.2"><title>${title}</title></circle>`;
  }).join("");

  const legend = LEVEL_ORDER.filter(c => rows.some(r => r.levelCode === c)).map(c =>
    `<span class="legend-item"><span class="legend-swatch" style="background:${LEVEL_COLOR[c]}"></span>${c}</span>`
  ).join("");

  el.innerHTML = `
    <div class="topicmap-wrap">
      <div class="topicmap-svg-col">
        <svg id="topicmap-svg" viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;max-width:520px;display:block;cursor:crosshair">${dots}</svg>
        <div class="legend">${legend}</div>
      </div>
      <div class="topicmap-detail" id="topicmap-detail">
        <div class="topicmap-detail-empty">Move the mouse over the map to see nearby sessions.</div>
      </div>
    </div>`;

  const svgEl = document.getElementById("topicmap-svg");
  const panel = document.getElementById("topicmap-detail");
  let highlighted = -1;

  function setHighlight(idx) {
    if (highlighted >= 0 && svgEl.children[highlighted]) {
      svgEl.children[highlighted].setAttribute("r", "5");
      svgEl.children[highlighted].setAttribute("stroke-width", "1.2");
    }
    if (idx >= 0 && svgEl.children[idx]) {
      svgEl.children[idx].setAttribute("r", "8");
      svgEl.children[idx].setAttribute("stroke-width", "2");
    }
    highlighted = idx;
  }

  function showNeighbors(i) {
    const target = rows[i];
    const nearby = rows
      .map((r, j) => (j === i ? null : { j, d2: (coords[j][0] - coords[i][0]) ** 2 + (coords[j][1] - coords[i][1]) ** 2 }))
      .filter(Boolean)
      .sort((a, b) => a.d2 - b.d2)
      .slice(0, 6);

    // What ties this cluster together: the hovered session's own tags, ranked by how many
    // of its nearest neighbors also carry them.
    const sharedTags = vocab
      .map((t, k) => ({ t, k }))
      .filter(({ k }) => vectors[i][k])
      .map(({ t, k }) => ({ t, count: nearby.filter(({ j }) => vectors[j][k]).length }))
      .filter(({ count }) => count > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, 4);

    panel.innerHTML = `
      <div class="tm-current-title">${target.title}</div>
      <div class="tm-current-meta">${target.code} · ${target.timeLabel} · Level ${target.levelCode || "—"}</div>
      ${sharedTags.length ? `
        <div class="tm-label">Shared themes</div>
        <div class="tm-tags">${sharedTags.map(({ t }) => `<span class="tm-tag">${t}</span>`).join("")}</div>
      ` : ""}
      <div class="tm-label">Nearby sessions</div>
      ${nearby.map(({ j }) => `
        <div class="tm-neighbor">
          <div class="tm-neighbor-title">${rows[j].title}</div>
          <div class="tm-neighbor-meta">${rows[j].code} · ${rows[j].timeLabel} · Level ${rows[j].levelCode || "—"}</div>
        </div>`).join("")}`;
  }

  svgEl.addEventListener("mousemove", e => {
    const rect = svgEl.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (W / rect.width);
    const my = (e.clientY - rect.top) * (H / rect.height);
    let best = -1, bestD = Infinity;
    rows.forEach((r, i) => {
      const dx = sx(coords[i][0]) - mx, dy = sy(coords[i][1]) - my;
      const d = dx * dx + dy * dy;
      if (d < bestD) { bestD = d; best = i; }
    });
    if (best === -1 || best === highlighted) return;
    setHighlight(best);
    showNeighbors(best);
  });
  svgEl.addEventListener("mouseleave", () => {
    setHighlight(-1);
    panel.innerHTML = `<div class="topicmap-detail-empty">Move the mouse over the map to see nearby sessions.</div>`;
  });
}

renderFunFacts();
renderCloud();
renderEmerging();

let STAR = new Set();
try { STAR = new Set(JSON.parse(localStorage.getItem("jhb-summit-starred") || "[]")); } catch (e) {}
function saveStars() { try { localStorage.setItem("jhb-summit-starred", JSON.stringify([...STAR])); } catch (e) {} }
function toggleStar(id) { STAR.has(id) ? STAR.delete(id) : STAR.add(id); saveStars(); render(); }

const state = { search: "", level: "", type: "", area: "" };

function populateSelect(sel, values, current) {
  const existing = sel.querySelector("option").outerHTML;
  sel.innerHTML = existing;
  values.forEach(v => {
    const o = document.createElement("option");
    o.value = v; o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
}

function uniqueSorted(arr) { return [...new Set(arr)].sort(); }

function countBy(list, fn) {
  const m = new Map();
  list.forEach(item => {
    const v = fn(item);
    const vals = Array.isArray(v) ? v : [v];
    vals.forEach(x => { if (x) m.set(x, (m.get(x) || 0) + 1); });
  });
  return m;
}

function hbarChart(container, pairs, opts) {
  opts = opts || {};
  const max = Math.max(...pairs.map(p => p[1]), 1);
  container.innerHTML = "";
  pairs.forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "hbar-row";
    const color = opts.colorFor ? opts.colorFor(label) : "var(--series-1)";
    row.innerHTML = `
      <div class="hbar-label" title="${label}">${label}</div>
      <div class="hbar-track">
        <div class="hbar-fill" style="width:${(value / max * 100).toFixed(1)}%;background:${color}" title="${label}: ${value}"></div>
      </div>
      <div class="hbar-value">${value}</div>`;
    container.appendChild(row);
  });
}

function tableTwin(pairs, headers) {
  const rowsHtml = pairs.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join("");
  return `<table class="mini"><thead><tr><th>${headers[0]}</th><th>${headers[1]}</th></tr></thead><tbody>${rowsHtml}</tbody></table>`;
}

const chartState = { level: "chart", type: "chart", area: "chart", product: "chart", topicmap: "chart" };

function renderCharts(filtered) {
  const byLevel = countBy(filtered, r => r.levelCode || "?");
  const levelPairs = LEVEL_ORDER.filter(c => byLevel.has(c)).map(c => {
    const label = (rows.find(r => r.levelCode === c) || {}).levelLabel || c;
    return [c + " · " + label, byLevel.get(c)];
  });
  const levelEl = document.getElementById("chart-level");
  if (chartState.level === "chart") {
    hbarChart(levelEl, levelPairs, { colorFor: (label) => LEVEL_COLOR[label.split(" ")[0]] || "var(--series-1)" });
  } else {
    levelEl.innerHTML = tableTwin(levelPairs, ["Level", "Sessions"]);
  }

  const byType = countBy(filtered, r => r.type || "Unspecified");
  const typePairs = [...byType.entries()].sort((a, b) => b[1] - a[1]);
  const typeEl = document.getElementById("chart-type");
  typeEl.innerHTML = "";
  if (chartState.type === "chart") hbarChart(typeEl, typePairs);
  else typeEl.innerHTML = tableTwin(typePairs, ["Format", "Sessions"]);

  const byArea = countBy(filtered, r => r.areas);
  const areaPairs = [...byArea.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
  const areaEl = document.getElementById("chart-area");
  if (chartState.area === "chart") hbarChart(areaEl, areaPairs);
  else areaEl.innerHTML = tableTwin(areaPairs, ["Area of interest", "Sessions"]);

  const byProduct = countBy(filtered, r => r.products);
  const productPairs = [...byProduct.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
  const productEl = document.getElementById("chart-product");
  if (chartState.product === "chart") hbarChart(productEl, productPairs);
  else productEl.innerHTML = tableTwin(productPairs, ["Product/service", "Mentions"]);
}

document.querySelectorAll(".table-toggle[data-target]").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.target.replace("chart-", "");
    chartState[key] = chartState[key] === "chart" ? "table" : "chart";
    btn.textContent = chartState[key] === "chart" ? "Table" : "Chart";
    render();
  });
});

function renderStats(filtered) {
  const workshops = filtered.filter(r => r.type === "Workshop").length;
  const handsOn = filtered.filter(r => (r.features || []).some(f => /hands-on/i.test(f))).length;
  const locations = uniqueSorted(filtered.map(r => r.location)).length;
  const stats = [
    [filtered.length, "Sessions"],
    [workshops, "Workshops"],
    [handsOn, "Hands-on sessions"],
    [locations, "Venues in use"],
    [STAR.size, "Starred by you"],
  ];
  document.getElementById("stats").innerHTML = stats.map(([v, l]) =>
    `<div class="card stat-tile"><div class="stat-value">${v}</div><div class="stat-label">${l}</div></div>`
  ).join("");
}

function renderAgenda() {
  const starred = rows.filter(r => STAR.has(r.id)).sort((a, b) => a.start - b.start);
  const el = document.getElementById("agenda");
  if (!starred.length) {
    el.innerHTML = `<div class="agenda-empty">No sessions starred yet — click ☆ next to any session in the schedule or list below.</div>`;
    return;
  }
  el.innerHTML = starred.map((r, i) => {
    const prev = starred[i - 1];
    const clash = prev && r.start < prev.end;
    return `<div class="agenda-item">
      <span class="agenda-time">${r.timeLabel}</span>
      <span class="agenda-title">${r.title} <span style="color:var(--text-muted)">${r.code}</span></span>
      ${clash ? '<span class="agenda-clash">⚠ overlaps previous</span>' : ""}
    </div>`;
  }).join("");
}

function renderTimeline(filtered) {
  const bySlot = new Map();
  filtered.forEach(r => {
    if (!bySlot.has(r.timeLabel)) bySlot.set(r.timeLabel, []);
    bySlot.get(r.timeLabel).push(r);
  });
  const slots = [...bySlot.keys()].sort();
  document.getElementById("timeline").innerHTML = slots.map(slot => {
    const items = bySlot.get(slot).sort((a, b) => a.title.localeCompare(b.title));
    const chips = items.map(r => `
      <div class="chip">
        <button class="star-btn ${STAR.has(r.id) ? "starred" : ""}" data-star="${r.id}">${STAR.has(r.id) ? "★" : "☆"}</button>
        <span class="chip-title">${r.title}</span>
        <div class="chip-meta">${r.code} · ${r.type} · ${r.location.split(",")[0]}</div>
      </div>`).join("");
    return `<div class="timeline-slot">
      <div class="timeline-time">${slot} <span class="timeline-count">— ${items.length} running</span></div>
      <div class="session-chips">${chips}</div>
    </div>`;
  }).join("");
}

function renderList(filtered) {
  document.getElementById("sl-count").textContent = `(${filtered.length})`;
  const sorted = [...filtered].sort((a, b) => a.start - b.start);
  document.getElementById("session-list").innerHTML = sorted.map(r => `
    <details class="session-row level-${r.levelCode || '?'}">
      <summary>
        <button class="star-btn ${STAR.has(r.id) ? "starred" : ""}" data-star="${r.id}">${STAR.has(r.id) ? "★" : "☆"}</button>
        <span class="sr-time">${r.timeLabel}</span>
        <span class="sr-title">${r.title} <span class="sr-code">${r.code}</span></span>
        <span class="badge" style="background:${LEVEL_COLOR[r.levelCode] || "var(--text-muted)"}">${r.levelCode || "—"}</span>
      </summary>
      <div class="sr-detail">
        <div>${r.type} · ${r.duration} · ${r.location}${r.speakers ? " · " + r.speakers : ""}</div>
        <p>${r.abstract || ""}</p>
        <div class="sr-tags">${(r.areas || []).map(a => `<span class="tag">${a}</span>`).join("")}${(r.products || []).slice(0, 6).map(p => `<span class="tag">${p}</span>`).join("")}</div>
        ${r.ctaLink ? `<a class="cta" href="${r.ctaLink}" target="_blank" rel="noopener">Register / details ↗</a>` : ""}
      </div>
    </details>
  `).join("");
}

function attachStarHandlers(root) {
  root.querySelectorAll("[data-star]").forEach(btn => {
    btn.addEventListener("click", (e) => { e.preventDefault(); toggleStar(btn.dataset.star); });
  });
}

function applyFilters() {
  const q = state.search.trim().toLowerCase();
  return rows.filter(r => {
    if (state.level && r.levelCode !== state.level) return false;
    if (state.type && r.type !== state.type) return false;
    if (state.area && !(r.areas || []).includes(state.area)) return false;
    if (q) {
      const hay = [
        r.title, r.abstract, r.speakers, r.code, r.type, r.location, r.levelLabel,
        ...(r.areas || []), ...(r.topics || []), ...(r.industries || []),
        ...(r.features || []), ...(r.products || []), ...(r.roles || []),
      ].join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function render() {
  const filtered = applyFilters();
  document.getElementById("f-count").textContent = `${filtered.length} of ${rows.length} sessions`;
  renderStats(filtered);
  renderAgenda();
  renderCharts(filtered);
  renderTopicMap();
  renderTimeline(filtered);
  renderList(filtered);
  attachStarHandlers(document.getElementById("root"));
}

populateSelect(document.getElementById("f-level"), LEVEL_ORDER.filter(c => rows.some(r => r.levelCode === c)));
populateSelect(document.getElementById("f-type"), uniqueSorted(rows.map(r => r.type)));
populateSelect(document.getElementById("f-area"), uniqueSorted(rows.flatMap(r => r.areas || [])));

document.getElementById("f-search").addEventListener("input", e => { state.search = e.target.value; render(); });
document.getElementById("f-level").addEventListener("change", e => { state.level = e.target.value; render(); });
document.getElementById("f-type").addEventListener("change", e => { state.type = e.target.value; render(); });
document.getElementById("f-area").addEventListener("change", e => { state.area = e.target.value; render(); });
document.getElementById("f-reset").addEventListener("click", () => {
  state.search = ""; state.level = ""; state.type = ""; state.area = "";
  document.getElementById("f-search").value = "";
  document.getElementById("f-level").value = "";
  document.getElementById("f-type").value = "";
  document.getElementById("f-area").value = "";
  render();
});

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b === btn));
    document.getElementById("tab-list").style.display = btn.dataset.tab === "list" ? "" : "none";
    document.getElementById("tab-timeline").style.display = btn.dataset.tab === "timeline" ? "" : "none";
  });
});

const THEME_KEY = "jhb-summit-theme";
function effectiveTheme() {
  let stored = null;
  try { stored = localStorage.getItem(THEME_KEY); } catch (e) {}
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function updateThemeBtn() {
  document.getElementById("theme-toggle").textContent = effectiveTheme() === "dark" ? "☀️ Light" : "🌙 Dark";
}
(function initTheme() {
  let stored = null;
  try { stored = localStorage.getItem(THEME_KEY); } catch (e) {}
  if (stored === "light" || stored === "dark") document.documentElement.setAttribute("data-theme", stored);
  updateThemeBtn();
})();
document.getElementById("theme-toggle").addEventListener("click", () => {
  const next = effectiveTheme() === "dark" ? "light" : "dark";
  try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
  document.documentElement.setAttribute("data-theme", next);
  updateThemeBtn();
});

render();
</script>
</body>
</html>
"""

HTML = HTML.replace("__DATA_JSON__", DATA_JSON)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("wrote", OUT, len(HTML), "bytes")
