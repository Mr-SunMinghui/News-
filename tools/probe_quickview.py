# -*- coding: utf-8 -*-
"""探查旧速览.html 的 DOM 结构，为重建提取器做依据。只读，不修改任何文件。"""
import glob
import re
from bs4 import BeautifulSoup


def txt(node):
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True))


for f in sorted(glob.glob("实践/events/*/速览.html")):
    print("#" * 70)
    print(f)
    soup = BeautifulSoup(open(f, encoding="utf-8").read(), "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    print("h1:", txt(soup.h1) if soup.h1 else None)
    print("h2 顺序:", [txt(h) for h in soup.find_all("h2")])
    print("h3 顺序:", [txt(h) for h in soup.find_all("h3")])
    arts = soup.find_all("article")
    print("article 数:", len(arts))
    if arts:
        print("  article[0]:", str(arts[0])[:300].replace("\n", " "))
    stats = soup.select(".stats div")
    print("stats 数:", len(stats))
    for s in stats[:4]:
        print("   stat:", txt(s)[:80])
    links = soup.find_all("a")
    print("链接:", [(txt(a)[:26], a.get("href", "")[:60]) for a in links])
    for sel in [".chips", ".meta", ".pill", ".chip", ".badge"]:
        els = soup.select(sel)
        if els:
            print(f"  {sel}:", [txt(e)[:90] for e in els])
