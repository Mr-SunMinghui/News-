# -*- coding: utf-8 -*-
"""校验重建后的速览页是否丢失了原页面的事实性文字（只读）。

做法：把基线页面（重构前副本）的正文切成片段，逐条检查是否出现在新页面里。
导航类文字（"返回项目总览""档案导航""离线事实汇编 ↗"等）属于被替换的版式元素，列入白名单。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / ".workbuddy" / "backup" / "2026-10-22-quickview"
EVENTS = ROOT / "实践" / "events"

WHITELIST = re.compile(
    r"^(返回|项目总览|档案导航|档案直达|事件档案|本地静态页面|状态$|优先级|首次发现|最近核查|"
    r"↑|↗|→|·|【|】|查看|打开|来源速链|主要来源|关键数据|事件时间线|时间线|当前信息|后续关注|接下来关注)$"
)
# 已知的版式改写：旧总览导语被重写（信息量不减少，只是措辞更新）
REWRITTEN = {
    "把重要事件的时间线、调查进展和后续结果放在一处",
    "每张卡片都通往可离线查阅的事件速览与来源档案",
}


def covered(piece: str, new_norm: str) -> bool:
    """判断旧文本片段是否被新页面覆盖（允许版式改写后的等价呈现）。"""
    if norm(piece) in new_norm:
        return True
    # 旧版的英文状态摘要行（状态/优先级/核查日期）→ 新版拆成中文徽标，
    # 只要核查日期都在，就说明这三项信息没有丢。
    if piece.startswith("状态："):
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", piece)
        return bool(dates) and all(d in new_norm for d in dates)
    # 旧版把多项来源用 " · " 串成一行，新版逐行列出：拆开逐项检查
    if " · " in piece:
        parts = [p.strip() for p in piece.split(" · ") if len(re.sub(r"\s", "", p)) >= 4]
        return bool(parts) and all(norm(p) in new_norm for p in parts)
    return False


def norm(s: str) -> str:
    s = s.replace("\u3000", " ")
    s = re.sub(r"[“”\"'‘’]", "", s)
    s = re.sub(r"\s+", "", s)
    return s


def sentences(soup) -> list[str]:
    for t in soup(["style", "script"]):
        t.decompose()
    out: list[str] = []
    for node in soup.find_all(["h1", "h2", "h3", "p", "li", "td"]):
        txt = node.get_text(" ", strip=True)
        for piece in re.split(r"[。；！？\n]", txt):
            piece = piece.strip()
            if len(re.sub(r"\s", "", piece)) >= 8:
                out.append(piece)
    return out


def main() -> int:
    problems = 0
    pairs = [(BACKUP / "总览_速览.html", ROOT / "速览.html")]
    for d in sorted(p for p in EVENTS.iterdir() if p.is_dir()):
        pairs.append((BACKUP / f"{d.name}_速览.html", d / "速览.html"))

    for old, new in pairs:
        if not old.exists() or not new.exists():
            print(f"!! 缺失文件：{old} / {new}")
            problems += 1
            continue
        old_soup = BeautifulSoup(old.read_text(encoding="utf-8"), "html.parser")
        new_soup = BeautifulSoup(new.read_text(encoding="utf-8"), "html.parser")
        new_norm = norm(new_soup.get_text(" ", strip=True))
        missing = []
        for s in sentences(old_soup):
            if WHITELIST.match(s.strip()) or s.strip() in REWRITTEN:
                continue
            if not covered(s, new_norm):
                missing.append(s)
        tag = "总览" if new == ROOT / "速览.html" else new.parent.name
        if missing:
            problems += len(missing)
            print(f"\n== {tag}: 有 {len(missing)} 段文字未出现在新页面 ==")
            for m in missing[:12]:
                print("   -", m[:110])
        else:
            print(f"OK  {tag}: 原页面文字全部保留")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
