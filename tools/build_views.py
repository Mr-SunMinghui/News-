# -*- coding: utf-8 -*-
"""Event Afterwatch 视图构建器。

作用
----
把仓库里的档案内容渲染成三类离线单文件 HTML：
1. 根目录 `速览.html`            —— 事件总览（卡片 + 筛选 + 搜索）
2. `实践/events/<id>/速览.html`   —— 单事件速览（时间线 + 关键数据 + 侧栏导航）
3. `实践/events/<id>/档案.html`   —— 档案阅读器（把该事件全部 .md 渲染成网页，含来源快照）

内容来源与边界
--------------
- 事件页的正文（摘要、关键数据、时间线、后续关注、来源短链）**不重写、不新增事实**：
  首次运行时从已有页面抽取，落到 `tools/views/<event_id>.json` 作为内容源，之后只改版式不碰内容。
  抽取基线是 `.workbuddy/backup/2026-10-22-quickview/`（首次重构前的原页面副本），
  这样重复构建是幂等的，不会把生成物再当成素材。
- 状态/优先级/时间等元信息以 `event.yaml` 为准（它们比手写页面更新）。
- 阅读器内容直接来自磁盘上的 .md：改完 md 重跑本脚本即可刷新。

用法
----
    python tools/build_views.py             # 构建全部
    python tools/build_views.py --extract   # 强制从基线重新抽取内容 JSON
    python tools/build_views.py --only evt-20261017-france-unrest

依赖：markdown、beautifulsoup4、pyyaml（见 tools/README.md 的虚拟环境说明）。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aw_styles import BASE_CSS, EVENT_CSS, INDEX_CSS, READER_CSS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "实践" / "events"
VIEWS_DIR = Path(__file__).resolve().parent / "views"
BASELINE_DIR = ROOT / ".workbuddy" / "backup" / "2026-10-22-quickview"

STATUS_ZH = {
    "watching": "跟踪中",
    "developing": "持续发展",
    "quiet": "暂无进展",
    "closed_provisional": "阶段性结案",
    "reopened": "重新激活",
    "merged": "已并入他档",
    "archived": "已归档",
}
STATUS_CLASS = {
    "watching": "b-watching",
    "developing": "b-developing",
    "quiet": "b-quiet",
    "closed_provisional": "b-closed",
    "reopened": "b-reopened",
    "merged": "b-closed",
    "archived": "b-closed",
}
PRIORITY_ZH = {"high": "优先级 高", "medium": "优先级 中", "low": "优先级 低"}


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")


def parse_iso_date(s) -> str:
    s = str(s or "").strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else s


# --------------------------------------------------------------------------
# Markdown 渲染
# --------------------------------------------------------------------------
EVIDENCE_CLASS = {
    "corroborated": "b-corrob",
    "partially_verified": "b-partial",
    "unverified": "b-unver",
    "disputed": "b-disputed",
    "refuted": "b-refuted",
    "unknown": "b-unver",
    "accessible": "b-ok",
    "temporarily_unavailable": "b-partial",
    "not_found_observed": "b-unver",
    "redirected": "b-unver",
    "access_restricted": "b-partial",
}


def _md_engine() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
        output_format="html5",
    )


def _rewrite_links(frag: str, doc_id: str, known_ids: set[str]) -> str:
    """改写相对链接、处理表格单元格（日期不断行、状态上色）、外链开新窗口。"""
    soup = BeautifulSoup(frag, "html.parser")
    cur_dir = os.path.dirname(doc_id)

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http://", "https://")):
            a["target"] = "_blank"
            a["rel"] = "noopener noreferrer"
            continue
        if href.startswith("#") or href.startswith("mailto:"):
            continue
        raw = href.split("#")[0]
        if not raw.lower().endswith(".md"):
            continue
        target = os.path.normpath(os.path.join(cur_dir, raw)).replace("\\", "/")
        if target.startswith("./"):
            target = target[2:]
        if target.endswith(".md"):
            target = target[:-3]
        if target in known_ids:
            a["href"] = "#/" + target
            a["class"] = a.get("class", []) + ["doclink"]
        else:
            a["href"] = "#"
            a["title"] = "该文件未收录进阅读器：" + raw

    for td in soup.find_all("td"):
        t = td.get_text(strip=True)
        if not t:
            continue
        # 日期/编号这类"原子"内容不要被压成竖排
        if (re.match(r"\d{4}-\d{2}-\d{2}", t) and len(t) <= 12) or re.fullmatch(r"[SC]-\d{3}(-v\d)?", t):
            td["class"] = td.get("class", []) + ["nw"]
            continue
        if t in EVIDENCE_CLASS and not td.find(True):
            td.clear()
            sp = soup.new_tag("span")
            sp["class"] = ["badge", EVIDENCE_CLASS[t]]
            sp.string = t
            td.append(sp)
            continue
        _soften_cell(td, soup)

    return str(soup)


ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2})(T\d{2}:\d{2}(?::\d{2})?[+\-Z0-9:]*)")
ENUM_SPLIT = ("、", "，", "；")


def _soften_cell(td, soup) -> None:
    """在单元格里指定更自然的折行点，避免把日期/编号切成残字。

    - ISO 时间戳：只在日期与时间之间断
    - 顿号/分号：优先在标点之后断
    """
    for node in list(td.find_all(string=True)):
        raw = str(node)
        if not raw.strip() or not (ISO_RE.search(raw) or any(c in raw for c in ENUM_SPLIT)):
            continue
        text = html.escape(raw, quote=False)
        text = ISO_RE.sub(lambda m: f'{m.group(1)}<wbr><span class="nw2">{m.group(2)}</span>', text)
        for ch in ENUM_SPLIT:
            text = text.replace(ch, ch + "<wbr>")
        node.replace_with(BeautifulSoup(text, "html.parser"))


def _post_process(frag: str, doc_id: str, known_ids: set[str]) -> str:
    # 表格外层加滚动容器
    frag = re.sub(r"<table>", '<div class="tbl"><table>', frag)
    frag = re.sub(r"</table>", "</table></div>", frag)
    # 行内代码里的状态词 → 徽标
    def badge(m):
        word = m.group(1)
        cls = EVIDENCE_CLASS.get(word)
        if not cls:
            return m.group(0)
        return f'<span class="badge {cls}">{word}</span>'

    frag = re.sub(
        r"<code>(corroborated|partially_verified|unverified|disputed|refuted|unknown|"
        r"accessible|temporarily_unavailable|not_found_observed|redirected|access_restricted)</code>",
        badge,
        frag,
    )
    frag = _rewrite_links(frag, doc_id, known_ids)
    return frag


def render_md(text: str, doc_id: str, known_ids: set[str]) -> str:
    engine = _md_engine()
    frag = engine.convert(text)
    return _post_process(frag, doc_id, known_ids)


# --------------------------------------------------------------------------
# 从既有页面抽取内容（仅在内容 JSON 缺失或 --extract 时执行）
# --------------------------------------------------------------------------
def baseline_page(event_id: str, kind: str = "event") -> Path | None:
    if kind == "index":
        for cand in (BASELINE_DIR / "总览_速览.html", ROOT / "速览.html"):
            if cand.exists():
                return cand
    for cand in (BASELINE_DIR / f"{event_id}_速览.html", EVENTS_DIR / event_id / "速览.html"):
        if cand.exists():
            return cand
    return None


def _iter_after(heading, stop=("h2", "h3")):
    """按文档顺序遍历 heading 之后的元素，遇到下一个标题即停（可跨父容器）。"""
    for el in heading.next_elements:
        if getattr(el, "name", None) in stop:
            break
        yield el


def _block_links(soup, headings_re) -> list[tuple[str, str]]:
    """收集指定标题之后、下一个标题之前的所有链接。"""
    out: list[tuple[str, str]] = []
    for h in soup.find_all(["h2", "h3"]):
        if not headings_re.search(clean_text(h.get_text())):
            continue
        for el in _iter_after(h):
            if getattr(el, "name", None) == "a" and el.get("href"):
                out.append((clean_text(el.get_text()), el["href"]))
    return out


def extract_event(event_id: str) -> dict | None:
    page = baseline_page(event_id)
    if page is None:
        return None
    soup = BeautifulSoup(read_text(page), "html.parser")
    for t in soup(["style", "script", "footer"]):
        t.decompose()

    hero = soup.find("header") or soup.find("section")
    title = ""
    intro = ""
    if hero:
        h1 = hero.find("h1")
        if h1:
            title = "".join(str(c) for c in h1.contents).strip()
        for p in hero.find_all("p"):
            if len(clean_text(p.get_text())) >= 40:
                intro = "".join(str(c) for c in p.contents).strip()
                break

    metrics: list[dict] = []
    for box in soup.select(".metric, .stats > div, .numbers > div"):
        strong = box.find(["strong", "b", "em"])
        if not strong:
            continue
        value = clean_text(strong.get_text())
        label = clean_text(box.get_text(" ", strip=True))
        label = label.replace(value, "", 1).strip()
        if value:
            metrics.append({"v": value, "l": label})

    timeline: list[dict] = []
    for art in soup.find_all("article"):
        date = ""
        for sel in ("time", ".date", "b"):
            el = art.select_one(sel)
            if el:
                cand = clean_text(el.get_text())
                if cand and re.search(r"\d{2}", cand):
                    date = cand
                    el.extract()
                    break
        head = art.find(["h3", "h2"])
        head_html = ""
        if head:
            head_html = "".join(str(c) for c in head.contents).strip()
            head.extract()
        body = ""
        p = art.find("p")
        if p:
            body = "".join(str(c) for c in p.contents).strip()
            p.extract()
        tag_el = art.find(class_=re.compile(r"tag|badge|chip"))
        tag = clean_text(tag_el.get_text()) if tag_el else ""
        if tag_el:
            tag_el.extract()
        latest = "latest" in (art.get("class") or [])
        if body or head_html:
            timeline.append(
                {"date": date, "title": head_html, "body": body, "tag": tag, "latest": latest}
            )

    # “当前信息”这类段落区块
    info: list[dict] = []
    for h in soup.find_all(["h2", "h3"]):
        if "当前信息" not in clean_text(h.get_text()):
            continue
        paras: list[str] = []
        for el in _iter_after(h):
            if getattr(el, "name", None) == "p":
                frag = "".join(str(c) for c in el.contents).strip()
                if frag and frag not in paras:
                    paras.append(frag)
        if paras:
            info.append({"title": clean_text(h.get_text()), "paras": paras})

    watch = ""
    for pat in ("接下来关注", "后续关注"):
        for h in soup.find_all(["h2", "h3"]):
            if pat not in clean_text(h.get_text()):
                continue
            parts: list[str] = []
            for el in _iter_after(h):
                if getattr(el, "name", None) in ("p", "li"):
                    txt = clean_text(el.get_text(" ", strip=True))
                    if txt and txt not in parts:
                        parts.append(txt)
            if parts:
                watch = "；".join(parts)
                break
        if watch:
            break

    nav = [
        (t, h)
        for t, h in _block_links(soup, re.compile("档案导航|档案直达"))
        if not h.startswith("http")
    ]
    sources = [
        (t, h)
        for t, h in _block_links(soup, re.compile("主要来源|来源速链"))
        if h.startswith("http")
    ]
    end_note = ""
    for p in soup.find_all("p"):
        txt = clean_text(p.get_text())
        if txt.startswith("以上为速览摘要"):
            end_note = txt
            break

    return {
        "event_id": event_id,
        "title": title,
        "intro": intro,
        "metrics": metrics,
        "timeline": timeline,
        "info": info,
        "watch": watch,
        "nav": nav,
        "sources": sources,
        "end_note": end_note,
        "extracted_from": str(page),
    }


def load_view_json(event_id: str, force: bool = False) -> dict:
    p = VIEWS_DIR / f"{event_id}.json"
    if p.exists() and not force:
        return json.loads(read_text(p))
    data = extract_event(event_id)
    if data is None:
        data = {"event_id": event_id, "title": "", "intro": "", "metrics": [], "timeline": [],
                "info": [], "watch": "", "nav": [], "sources": [], "end_note": ""}
    write_text(p, json.dumps(data, ensure_ascii=False, indent=2))
    return data


# --------------------------------------------------------------------------
# 数据统计
# --------------------------------------------------------------------------
def count_claims(d: Path) -> int:
    f = d / "claims.md"
    if not f.exists():
        return 0
    return len(re.findall(r"^##\s+C-\d+", read_text(f), flags=re.M))


def count_sources(d: Path) -> int:
    f = d / "sources.md"
    if not f.exists():
        return 0
    return len(re.findall(r"^\|\s*S-\d+", read_text(f), flags=re.M))


def count_files(d: Path, sub: str, pattern: str) -> int:
    p = d / sub
    if not p.is_dir():
        return 0
    return len(list(p.glob(pattern)))


def load_yaml(d: Path) -> dict:
    f = d / "event.yaml"
    if not f.exists():
        return {}
    try:
        return yaml.safe_load(read_text(f)) or {}
    except yaml.YAMLError:
        return {}


# --------------------------------------------------------------------------
# 页面骨架
# --------------------------------------------------------------------------
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='9' fill='%231E5744'/%3E"
    "%3Cpath d='M10 23V9h11M10 16h8' stroke='%23D8E6C6' stroke-width='2.4' "
    "fill='none' stroke-linecap='round'/%3E%3C/svg%3E"
)

ICON_SEARCH = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'
)
ICON_BACK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>'
)
ICON_DOC = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>'
)
ICON_BOOK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 5.5v15"/></svg>'
)
ICON_MENU = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.1" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
)


def page_shell(title: str, css: str, body: str, script: str = "", body_class: str = "") -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{esc(title)}</title>
<link rel="icon" href="{FAVICON}">
<style>{BASE_CSS}{css}</style>
</head>
<body class="{body_class}">
{body}
{f"<script>{script}</script>" if script else ""}
</body>
</html>
"""


def topbar(left_html: str, right_html: str = "") -> str:
    return f"""<div class="topbar"><div class="wrap inner">
  {left_html}
  <div class="spacer"></div>
  {right_html}
</div></div>"""


def brand_home(href: str) -> str:
    return f"""<a class="brand" href="{esc(href)}">
    <span class="mark">EA</span>
    <span class="name">Event&nbsp;Afterwatch <span>/ 事件档案</span></span>
  </a>"""


# --------------------------------------------------------------------------
# 总览页
# --------------------------------------------------------------------------
def extract_index_cards() -> list[dict]:
    page = baseline_page("", "index")
    if page is None:
        return []
    soup = BeautifulSoup(read_text(page), "html.parser")
    cards = []
    for art in soup.select("article.event"):
        eyebrow = art.select_one(".event-top .eyebrow")
        status = art.select_one(".status")
        h3 = art.find("h3")
        p = art.find("p")
        foot = art.select_one(".event-foot")
        href = ""
        if foot and foot.find("a"):
            href = foot.find("a")["href"]
        first = ""
        if foot:
            span = foot.find("span")
            if span:
                first = clean_text(span.get_text())
        m = re.search(r"events/([^/]+)/", href)
        cards.append(
            {
                "id": m.group(1) if m else "",
                "place": clean_text(eyebrow.get_text()) if eyebrow else "",
                "status": clean_text(status.get_text()) if status else "",
                "title": clean_text(h3.get_text()) if h3 else "",
                "summary": clean_text(p.get_text()) if p else "",
                "first": first.replace("首次发现：", ""),
                "href": href,
            }
        )
    return cards


def render_index(events: list[dict]) -> str:
    cards = []
    for i, ev in enumerate(events, 1):
        st = ev["status_code"]
        cards.append(
            {
                "no": f"{i:02d}",
                "place": ev["place"],
                "status_code": st,
                "status_zh": ev["status_zh"],
                "status_cls": STATUS_CLASS.get(st, "b-quiet"),
                "pulse": "pulse" if st == "developing" else "",
                "title": ev["card_title"],
                "summary": ev["card_summary"],
                "first": ev["first_seen"],
                "claims": ev["n_claims"],
                "sources": ev["n_sources"],
                "href": f"{ev['rel_dir']}/速览.html",
                "read": f"{ev['rel_dir']}/档案.html",
                "search": clean_text(f"{ev['place']} {ev['card_title']} {ev['card_summary']}"),
                "group": st if st in ("developing", "watching") else "other",
            }
        )

    n_total = len(cards)
    n_dev = sum(1 for c in cards if c["status_code"] == "developing")
    n_watch = sum(1 for c in cards if c["status_code"] == "watching")
    n_other = n_total - n_dev - n_watch

    def chip(key: str, label: str, n: int, active: bool = False) -> str:
        if n == 0 and key != "all":
            return ""
        return (
            f'<button class="chip" data-filter="{key}" aria-pressed="{"true" if active else "false"}">'
            f"{label} {n}</button>"
        )

    chips_html = (
        chip("all", "全部", n_total, True)
        + chip("developing", "持续发展", n_dev)
        + chip("watching", "跟踪中", n_watch)
        + chip("other", "其他", n_other)
    )
    last_check = max((e["last_checked"] for e in events), default="")
    total_claims = sum(e["n_claims"] for e in events)
    total_sources = sum(e["n_sources"] for e in events)
    total_snaps = sum(e["n_snaps"] for e in events)

    bars = []
    for n, cls, lab in ((n_dev, "#C08A50", "持续发展"), (n_watch, "#3C7A62", "跟踪中"), (n_other, "#A9B2A4", "其他")):
        if n:
            bars.append(
                f'<i style="width:{(n / n_total) * 100:.2f}%;background:{cls}" title="{lab} {n}"></i>'
            )

    cards_html = "\n".join(
        f"""<article class="ev rise" data-group="{c['group']}" data-search="{esc(c['search'])}" style="animation-delay:{min(i*45,300)}ms">
  <span class="no">{c['no']}</span>
  <div class="head">
    <span class="place">{esc(c['place'])}</span>
    <span class="badge {c['status_cls']}"><i class="dot {c['pulse']}"></i>{esc(c['status_zh'])}</span>
  </div>
  <h3>{esc(c['title'])}</h3>
  <p>{esc(c['summary'])}</p>
  <div class="foot2">
    <span class="t">首次发现 {esc(c['first'])}</span>
    <span class="acts">
      <a class="btn btn-sm btn-ghost" href="{esc(c['read'])}">打开档案</a>
      <a class="btn btn-sm" href="{esc(c['href'])}">事件速览 <span class="arw">→</span></a>
    </span>
  </div>
</article>"""
        for i, c in enumerate(cards)
    )

    body = f"""
{topbar(brand_home('速览.html'), f'<a class="navlink" href="#list">{ICON_SEARCH}<span>跳转到列表</span></a>')}
<header class="hero"><div class="wrap">
  <div class="row">
    <div>
      <div class="eyebrow">Independent Event Tracking · 本地离线档案</div>
      <h1 class="display">事件速览</h1>
      <p class="lede">把每起追踪中事件的时间线、关键数据、主张证据与来源状态放在一处。页面全部离线自包含，档案正文在站内直接阅读，无需打开原始 Markdown。</p>
    </div>
    <aside class="legend" aria-label="状态图例">
      <div class="t">状态图例</div>
      <div class="r"><i style="background:#C08A50"></i>持续发展<em>{n_dev}</em></div>
      <div class="r"><i style="background:#3C7A62"></i>跟踪中<em>{n_watch}</em></div>
      <div class="r"><i style="background:#A9B2A4"></i>结案 / 归档<em>{n_other}</em></div>
    </aside>
  </div>
  <div class="stats">
    <div class="cell">
      <div class="n">{n_total}</div>
      <div class="k">追踪中事件</div>
      <div class="bar">{''.join(bars)}</div>
    </div>
    <div class="cell">
      <div class="n">{total_claims}<span style="font-size:.5em;color:var(--muted);letter-spacing:0"> 条</span></div>
      <div class="k">编号主张 · 已登记</div>
    </div>
    <div class="cell">
      <div class="n">{total_sources}<span style="font-size:.5em;color:var(--muted);letter-spacing:0"> 个</span></div>
      <div class="k">来源 · {total_snaps} 份本地快照</div>
    </div>
  </div>
  <div class="meta">
    <span class="badge">最近核查 {esc(last_check)}</span>
    <span class="badge">全部离线 · 无外部依赖</span>
    <span class="badge">时区 Asia/Shanghai</span>
  </div>
</div></header>

<main class="wrap" id="list">
  <div class="tools">
    <div class="chips" role="group" aria-label="按状态筛选">
      {chips_html}
    </div>
    <label class="search">{ICON_SEARCH}
      <input id="q" type="search" placeholder="搜索事件、地区或关键词" autocomplete="off" aria-label="搜索事件">
    </label>
  </div>
  <section class="grid" id="grid" aria-label="事件列表">
{cards_html}
    <div class="empty" id="empty" hidden>没有匹配的事件。换个关键词，或点「全部」。</div>
  </section>
</main>

<footer class="foot"><div class="wrap inner">
  <div>本地静态页面 · 构建于 {datetime.now().strftime('%Y-%m-%d %H:%M')} · 数据以 <code>event.yaml</code> 与各档案 <code>.md</code> 为准</div>
  <div>刷新视图：<code>python tools/build_views.py</code></div>
</div></footer>
"""

    script = """
(function(){
  const grid=document.getElementById('grid');
  const cards=[...grid.querySelectorAll('.ev')];
  const empty=document.getElementById('empty');
  const q=document.getElementById('q');
  const chips=[...document.querySelectorAll('.chip')];
  let filter='all';
  function apply(){
    const kw=q.value.trim().toLowerCase();
    let shown=0;
    cards.forEach(c=>{
      const okGroup = filter==='all'
        || (filter==='other' ? !['developing','watching'].includes(c.dataset.group) : c.dataset.group===filter);
      const okKw=!kw||c.dataset.search.toLowerCase().includes(kw);
      const show=okGroup&&okKw;
      c.hidden=!show;
      if(show) shown++;
    });
    empty.hidden=shown>0;
  }
  chips.forEach(b=>b.addEventListener('click',()=>{
    filter=b.dataset.filter;
    chips.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
    apply();
  }));
  q.addEventListener('input',apply);
})();
"""
    return page_shell("Event Afterwatch｜事件速览", INDEX_CSS, body, script)


# --------------------------------------------------------------------------
# 事件速览页
# --------------------------------------------------------------------------
def render_event(ev: dict, content: dict) -> str:
    status = ev["status_code"]
    status_cls = STATUS_CLASS.get(status, "b-quiet")
    chips_html = [
        f'<span class="badge {status_cls}"><i class="dot"></i>{esc(ev["status_zh"])}</span>',
        f'<span class="badge">{esc(PRIORITY_ZH.get(ev["priority"], "优先级 " + str(ev["priority"])))}</span>',
        f'<span class="badge">首次发现 {esc(ev["first_seen"])}</span>',
        f'<span class="badge">最近核查 {esc(ev["last_checked"])}</span>',
    ]
    if ev["location_short"]:
        chips_html.append(f'<span class="badge">{esc(ev["location_short"])}</span>')

    metrics = content.get("metrics") or []
    metrics_html = ""
    if metrics:
        items = "".join(
            f'<div class="m"><div class="v">{m["v"]}</div><div class="l">{m["l"]}</div></div>'
            for m in metrics
        )
        metrics_html = f'<div class="metrics rise">{items}</div>'

    info_html = ""
    for blk in content.get("info") or []:
        paras = "".join(f"<p>{p}</p>" for p in blk["paras"])
        info_html += f'<section class="block"><h2>{esc(blk["title"])}</h2><div class="prose">{paras}</div></section>'

    tl_items = []
    for it in content.get("timeline") or []:
        cls = "it latest" if it.get("latest") else "it"
        title = f'<h3>{it["title"]}</h3>' if it.get("title") else ""
        tag = f'<span class="tag">{esc(it["tag"])}</span>' if it.get("tag") else ""
        tl_items.append(
            f'<article class="{cls}"><time>{esc(it["date"])}</time>{title}<p>{it["body"]}</p>{tag}</article>'
        )
    timeline_html = f"""
<section class="block">
  <h2>事件时间线</h2>
  <div class="tl">{''.join(tl_items)}</div>
  {f'<p class="note">{esc(content["end_note"])}</p>' if content.get("end_note") else ''}
</section>"""

    core = [
        ("事实汇编", "事实汇编", "档"),
        ("timeline", "时间线", "时"),
        ("claims", "主张与证据", "主"),
        ("sources", "来源登记", "源"),
        ("status", "状态与待办", "态"),
        ("narrative", "叙事与用语观察", "叙"),
    ]
    nav_rows = []
    for slug, label, icon in core:
        f = ev["dir"] / f"{slug}.md"
        if not f.exists():
            continue
        nav_rows.append(
            f'<a class="link-row" href="档案.html#/{slug}"><span class="i">{icon}</span>'
            f'<span>{label}</span><span class="go">→</span></a>'
        )
    nav_rows.append(
        f'<a class="link-row" href="档案.html"><span class="i">全</span><span>打开完整档案</span>'
        f'<span class="go">→</span></a>'
    )

    watch_html = ""
    if content.get("watch"):
        watch_html = f"""<section class="panel watch"><h2>后续关注</h2><p>{esc(content['watch'])}</p></section>"""

    src_rows = "".join(
        f'<a class="src-row" href="{esc(href)}" target="_blank" rel="noopener noreferrer">'
        f"<span>{esc(label)}</span><span class=\"arw\">↗</span></a>"
        for label, href in (content.get("sources") or [])
    )
    src_html = f"""<section class="panel"><h2>主要来源</h2><div class="src-list">{src_rows}</div></section>""" if src_rows else ""

    body = f"""
{topbar(brand_home('../../速览.html'),
         f'<a class="navlink" href="../../速览.html">{ICON_BACK}<span>返回总览</span></a>'
         f'<a class="navlink" href="档案.html">{ICON_BOOK}<span>档案阅读器</span></a>')}

<header class="hd"><div class="wrap hd-row">
  <div>
    <div class="kicker">事件档案 · {esc(ev['id'])}</div>
    <h1>{content.get('title') or esc(ev['title'])}</h1>
    <p class="lede">{content.get('intro') or esc(ev['summary'])}</p>
    <div class="chips">{''.join(chips_html)}</div>
  </div>
  <aside class="index-card">
    <div class="t">档案索引</div>
    <div class="rows">
      <div class="row"><span>文档</span><b>{ev['n_docs']}</b></div>
      <div class="row"><span>来源快照</span><b>{ev['n_snaps']}</b></div>
      <div class="row"><span>巡检日志</span><b>{ev['n_logs']}</b></div>
    </div>
    <a class="go2" href="档案.html"><span>打开完整档案</span><span class="arw">→</span></a>
  </aside>
</div></header>

<main class="wrap">
  {metrics_html}
  <div class="layout">
    <div class="main-col">
      {info_html}
      {timeline_html}
    </div>
    <aside class="side">
      <section class="panel">
        <h2>档案导航</h2>
        <div class="links">{''.join(nav_rows)}</div>
        <p class="link-note">共 {ev['n_docs']} 篇文档 · {ev['n_snaps']} 份来源快照 · {ev['n_logs']} 篇巡检日志，均在站内阅读。</p>
      </section>
      {watch_html}
      {src_html}
    </aside>
  </div>
</main>

<footer class="foot"><div class="wrap inner">
  <div>状态 {esc(ev['status_code'])} · 优先级 {esc(str(ev['priority']))} · 本次构建 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
  <div>数字与结论以档案核查记录、来源与统计时点为准</div>
</div></footer>
"""
    return page_shell(f"{ev['title']}｜事件速览", EVENT_CSS, body)


# --------------------------------------------------------------------------
# 档案阅读器
# --------------------------------------------------------------------------
CORE_DOCS = [
    ("事实汇编", "事实汇编", "档案正文"),
    ("timeline", "时间线", None),
    ("claims", "主张与证据", None),
    ("sources", "来源登记", None),
    ("status", "状态与待办", None),
    ("narrative", "叙事与用语观察", None),
    ("event", "事件元数据（yaml）", None),
]


def doc_display_name(doc_id: str, fallback: str) -> str:
    """把时间戳式文件名换成更易读的显示名（不改磁盘文件名）。"""
    m = re.match(r"daily-logs/(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})", doc_id)
    if m:
        return f"{m.group(2)}-{m.group(3)} {m.group(4)}:{m.group(5)} 巡检"
    m = re.match(r"snapshots/(\d{4})-(\d{2})-(\d{2})-(.+)$", doc_id)
    if m:
        return f"{m.group(2)}-{m.group(3)} · {m.group(4)}"
    return fallback


def collect_docs(d: Path) -> tuple[list[dict], set[str]]:
    docs: list[dict] = []
    ids: set[str] = set()

    def add(doc_id: str, name: str, group: str, path: Path, kind: str):
        docs.append({"id": doc_id, "name": name, "group": group, "path": path, "kind": kind})
        ids.add(doc_id)

    for slug, label, sub in CORE_DOCS:
        f = d / f"{slug}.md"
        if f.exists():
            add(slug, label, "核心档案", f, "md")
    y = d / "event.yaml"
    if y.exists():
        add("event", "事件元数据（yaml）", "核心档案", y, "yaml")

    for sub, group in (("daily-logs", "巡检日志"), ("snapshots", "来源快照"), ("reports", "报道元数据"), ("diffs", "版本差异")):
        p = d / sub
        if not p.is_dir():
            continue
        for f in sorted(p.rglob("*.md")):
            rel = f.relative_to(d).with_suffix("").as_posix()
            add(rel, doc_display_name(rel, f.stem), group, f, "md")
        for f in sorted(p.rglob("*.diff")):
            rel = f.relative_to(d).with_suffix("").as_posix()
            add(rel, doc_display_name(rel, f.stem), group, f, "code")

    for f in sorted(d.glob("*.md")):
        if f.stem not in ids:
            add(f.stem, f.stem, "其他", f, "md")
    return docs, ids


def render_reader(ev: dict, docs: list[dict], ids: set[str]) -> str:
    groups: dict[str, list[dict]] = {}
    for doc in docs:
        groups.setdefault(doc["group"], []).append(doc)

    order = ["核心档案", "巡检日志", "来源快照", "报道元数据", "版本差异", "其他"]
    side_parts = []
    sections = []
    for gi, g in enumerate([g for g in order if g in groups]):
        items = groups[g]
        rows = []
        for doc in items:
            rows.append(
                f'<a class="doc" href="#/{esc(doc["id"])}" data-doc="{esc(doc["id"])}" '
                f'data-name="{esc(doc["name"].lower())}">'
                f'<span class="nm">{esc(doc["name"])}</span></a>'
            )
        side_parts.append(
            f'<div class="grp">{esc(g)} <span class="c">{len(items)}</span></div>' + "".join(rows)
        )

        for doc in items:
            if doc["kind"] == "yaml":
                raw = read_text(doc["path"])
                inner = f'<pre><code>{esc(raw)}</code></pre>'
                title = doc["name"]
                sub = doc["path"].name
            elif doc["kind"] == "code":
                raw = read_text(doc["path"])
                inner = f'<pre><code>{esc(raw)}</code></pre>'
                title = doc["name"]
                sub = doc["path"].relative_to(ev["dir"]).as_posix()
            else:
                raw = read_text(doc["path"])
                inner = f'<div class="md">{render_md(raw, doc["id"], ids)}</div>'
                title = doc["name"]
                sub = doc["path"].relative_to(ev["dir"]).as_posix()
            sections.append(
                f'<article class="doc-sec" data-doc="{esc(doc["id"])}" data-title="{esc(title)}" '
                f'data-sub="{esc(sub)}" hidden>{inner}</article>'
            )

    first = docs[0]["id"] if docs else ""
    body = f"""
<div class="scrim" id="scrim"></div>
<div class="shell">
  <aside class="side" id="side">
    <div class="head">
      <a class="back" href="速览.html">{ICON_BACK}<span>返回事件速览</span></a>
      <div class="t">{esc(ev['title'])}</div>
      <div class="k">{esc(ev['id'])} · {len(docs)} 篇文档</div>
    </div>
    <div class="srch"><input id="docq" type="search" placeholder="过滤文档名…" autocomplete="off" aria-label="过滤文档"></div>
    <nav class="docs" id="docs">{''.join(side_parts)}</nav>
  </aside>
  <div class="main">
    <div class="progress"><i id="bar"></i></div>
    <div class="bar">
      <button class="btn btn-ghost btn-sm tocbtn" id="menu" aria-label="打开文档列表">{ICON_MENU}</button>
      <div class="cur"><span id="curName">档案</span><span class="path" id="curPath"></span></div>
      <div class="sp"></div>
      <a class="navlink" href="速览.html">速览</a>
      <a class="navlink" href="../../速览.html">总览</a>
    </div>
    <div class="content" id="content">
      <div class="doc-body">
        {''.join(sections) if sections else '<div class="empty-note">该事件目录下暂无可阅读的文档。</div>'}
      </div>
    </div>
  </div>
</div>
"""
    script = f"""
(function(){{
  const first={json.dumps(first)};
  const ORIG_TITLE={json.dumps("档案 · " + ev['title'])};
  const secs=[...document.querySelectorAll('.doc-sec')];
  const links=[...document.querySelectorAll('.doc')];
  const content=document.getElementById('content');
  const curName=document.getElementById('curName');
  const curPath=document.getElementById('curPath');
  const bar=document.getElementById('bar');
  function show(id){{
    let hit=null;
    secs.forEach(s=>{{const on=s.dataset.doc===id;s.hidden=!on;if(on)hit=s;}});
    if(!hit){{ if(secs[0]){{secs[0].hidden=false;hit=secs[0];}} }}
    links.forEach(a=>a.classList.toggle('active',a.dataset.doc===(hit?hit.dataset.doc:'')));
    if(hit){{
      curName.textContent=hit.dataset.title||'';
      curPath.textContent=hit.dataset.sub||'';
      content.scrollTop=0;
      document.title=(hit.dataset.title||'档案')+'｜'+ORIG_TITLE;
      if(document.body.classList.contains('nav-open')) document.body.classList.remove('nav-open');
      markWideTables(hit);
    }}
  }}
  // 宽表在窄容器里需要横向滚动：补一条提示，避免误以为右侧没有内容
  function markWideTables(scope){{
    scope.querySelectorAll('.tbl').forEach(t=>{{
      const wide=t.scrollWidth-t.clientWidth>4;
      let hint=t.nextElementSibling;
      const isHint=hint&&hint.classList&&hint.classList.contains('tbl-hint');
      if(wide&&!isHint){{
        const d=document.createElement('p');
        d.className='tbl-hint';
        d.textContent='表格较宽，可左右滚动查看全部列 →';
        t.insertAdjacentElement('afterend',d);
      }}else if(!wide&&isHint){{
        hint.remove();
      }}
    }});
  }}
  function route(){{
    const h=decodeURIComponent(location.hash.replace(/^#\\/?/,''));
    show(h||first);
  }}
  window.addEventListener('hashchange',route);
  document.addEventListener('click',e=>{{
    const a=e.target.closest('.md a[href^="#/"]');
    if(a){{ /* 交给 hashchange */ }}
  }});
  const docq=document.getElementById('docq');
  docq.addEventListener('input',()=>{{
    const kw=docq.value.trim().toLowerCase();
    links.forEach(a=>{{a.style.display=!kw||a.dataset.name.includes(kw)?'':'none';}});
    document.querySelectorAll('.grp').forEach(g=>{{
      let n=g.nextElementSibling,any=false;
      while(n&&!n.classList.contains('grp')){{
        if(n.classList.contains('doc')&&n.style.display!=='none')any=true;
        n=n.nextElementSibling;
      }}
      g.style.display=any?'':'none';
    }});
  }});
  content.addEventListener('scroll',()=>{{
    const h=content.scrollHeight-content.clientHeight;
    bar.style.width=(h>0?Math.min(100,content.scrollTop/h*100):0)+'%';
  }});
  document.getElementById('menu').addEventListener('click',()=>document.body.classList.toggle('nav-open'));
  document.getElementById('scrim').addEventListener('click',()=>document.body.classList.remove('nav-open'));
  document.addEventListener('keydown',e=>{{
    if(e.key==='/'&&document.activeElement!==docq){{e.preventDefault();docq.focus();}}
    if(e.key==='Escape')document.body.classList.remove('nav-open');
  }});
  route();
}})();
"""
    return page_shell(f"档案 · {ev['title']}", READER_CSS, body, script)


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def build(only: str | None = None, force_extract: bool = False) -> int:
    if not EVENTS_DIR.is_dir():
        print("找不到实践/events 目录", file=sys.stderr)
        return 1

    built = []
    for d in sorted([p for p in EVENTS_DIR.iterdir() if p.is_dir()]):
        eid = d.name
        if only and eid != only:
            continue
        y = load_yaml(d)
        content = load_view_json(eid, force=force_extract)
        loc = str(y.get("location", "") or "")
        loc_short = loc.split("；")[0].split(";")[0][:28] if loc else ""
        docs, ids = collect_docs(d)
        ev = {
            "id": eid,
            "dir": d,
            "rel_dir": f"实践/events/{eid}",
            "title": y.get("title") or content.get("title") or eid,
            "summary": y.get("summary") or content.get("intro") or "",
            "status_code": str(y.get("status") or "developing"),
            "status_zh": STATUS_ZH.get(str(y.get("status") or ""), str(y.get("status") or "")),
            "priority": y.get("priority") or "",
            "first_seen": parse_iso_date(y.get("first_discovered_at")),
            "last_checked": parse_iso_date(y.get("last_checked_at")),
            "location_short": loc_short,
            "n_claims": count_claims(d),
            "n_sources": count_sources(d),
            "n_snaps": count_files(d, "snapshots", "*.md"),
            "n_logs": count_files(d, "daily-logs", "*.md"),
            "n_docs": len(docs),
        }
        write_text(d / "速览.html", render_event(ev, content))
        write_text(d / "档案.html", render_reader(ev, docs, ids))
        built.append(ev)
        print(f"  ✓ {eid}  速览.html / 档案.html  ({len(docs)} 篇文档)")

    if not only:
        idx_cards = extract_index_cards()
        pool = {e["id"]: e for e in built}
        order = [c["id"] for c in idx_cards if c["id"] in pool]
        events = [pool.pop(i) for i in order] + list(pool.values())
        card_by_id = {c["id"]: c for c in idx_cards if c["id"]}

        merged = []
        for e in events:
            card = card_by_id.get(e["id"]) or {}
            e = dict(e)
            e["place"] = card.get("place") or e["location_short"]
            e["card_title"] = card.get("title") or e["title"]
            e["card_summary"] = card.get("summary") or e["summary"]
            e["first_seen"] = card.get("first") or e["first_seen"]
            merged.append(e)
        write_text(ROOT / "速览.html", render_index(merged))
        print(f"  ✓ 速览.html（总览）  {len(merged)} 个事件")

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="构建 Event Afterwatch 视图页面")
    ap.add_argument("--only", help="只构建指定事件 ID")
    ap.add_argument("--extract", action="store_true", help="强制从基线页面重新抽取内容 JSON")
    args = ap.parse_args()
    VIEWS_DIR.mkdir(parents=True, exist_ok=True)
    print("构建视图…")
    return build(only=args.only, force_extract=args.extract)


if __name__ == "__main__":
    raise SystemExit(main())
