# -*- coding: utf-8 -*-
"""Event Afterwatch 视觉系统（单人本地档案站）。

设计取向：自然有机 · 档案纸感 · 编辑排版。
- 主色沿用仓库既有绿系（#235C48 一带），不引入新品牌色
- 标题用衬线（宋体系）承接"档案/文献"气质，正文用黑体保证屏读清晰
- 所有尺寸走 4pt/8pt 网格，圆角与阴影各只有两档
说明：本文件只是常量，被 build_views.py 内联进生成的单文件 HTML（离线可用，无 CDN 依赖）。
"""

BASE_CSS = r"""
:root{
  --paper:#F1F0E8; --surface:#FFFDF6; --surface-2:#F7F5EC; --surface-3:#EFEEE4;
  --ink:#1A211C; --ink-2:#333D36; --muted:#6C7A71; --muted-2:#8B968D;
  --line:#DCDED2; --line-2:#C7CDBE;
  --brand:#1E5744; --brand-d:#153F31; --brand-l:#3C7A62;
  --lime:#D8E6C6; --lime-2:#E8F0DC;
  --amber:#A9612F; --amber-bg:#FBEFDF; --amber-line:#EFD8BC;
  --red:#9E4136; --red-bg:#F8E4E0;
  --serif:"Source Han Serif SC","Songti SC","STSong","Noto Serif SC",SimSun,Georgia,serif;
  --sans:"Aptos","Segoe UI","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  --mono:"Cascadia Mono","SFMono-Regular",Consolas,"Liberation Mono",monospace;
  --r-1:12px; --r-2:18px; --r-3:26px;
  --sh-1:0 1px 2px rgba(26,33,28,.05), 0 8px 22px rgba(26,33,28,.055);
  --sh-2:0 2px 6px rgba(26,33,28,.07), 0 22px 48px rgba(26,33,28,.11);
  --ease:cubic-bezier(.2,0,0,1);
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font:400 16px/1.72 var(--sans);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
body::before{
  content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(940px 520px at 88% -10%, rgba(216,230,198,.80), transparent 62%),
    radial-gradient(820px 460px at -8% 2%, rgba(213,224,207,.55), transparent 58%);
}
body::after{
  content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;
  background-image:
    linear-gradient(to right, rgba(26,33,28,.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(26,33,28,.05) 1px, transparent 1px);
  background-size:72px 72px;
  -webkit-mask-image:linear-gradient(to bottom, rgba(0,0,0,.6), transparent 42%);
  mask-image:linear-gradient(to bottom, rgba(0,0,0,.6), transparent 42%);
}
a{color:inherit}
img{max-width:100%}
.wrap{width:min(1180px,calc(100% - 40px));margin-inline:auto;position:relative;z-index:1}
.wrap-narrow{width:min(900px,calc(100% - 40px))}

/* ---------- 顶栏 ---------- */
.topbar{
  position:sticky;top:0;z-index:60;
  background:rgba(241,240,232,.86);
  -webkit-backdrop-filter:saturate(1.3) blur(14px);backdrop-filter:saturate(1.3) blur(14px);
  border-bottom:1px solid var(--line);
}
.topbar .inner{display:flex;align-items:center;gap:18px;min-height:64px}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none;flex-shrink:0}
.brand .mark{
  width:26px;height:26px;border-radius:9px;background:var(--brand);
  display:grid;place-items:center;color:#EDF3E6;font:700 12px/1 var(--sans);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.16);
}
.brand .name{
  font:700 12.5px/1 var(--sans);letter-spacing:.20em;text-transform:uppercase;color:var(--ink);
}
.brand .name span{color:var(--muted-2);font-weight:600}
.topbar .spacer{flex:1}
.navlink{
  display:inline-flex;align-items:center;gap:7px;height:36px;padding:0 12px;border-radius:10px;
  font:600 13px/1 var(--sans);color:var(--ink-2);text-decoration:none;
  transition:background .16s var(--ease),color .16s var(--ease);
}
.navlink:hover{background:rgba(255,255,255,.72);color:var(--brand)}
.navlink svg{opacity:.72}

/* ---------- 版式基元 ---------- */
.eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  font:700 11.5px/1.4 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--brand);
}
.kicker{
  font:600 12px/1.5 var(--mono);letter-spacing:.06em;color:var(--muted);
}
h1,h2,h3,h4{font-family:var(--serif);font-weight:600;letter-spacing:-.012em}
.display{
  font-family:var(--serif);font-weight:600;
  font-size:clamp(2.5rem,6.4vw,4.5rem);line-height:1.04;letter-spacing:-.035em;
  margin:.35rem 0 0;
}
.lede{color:var(--ink-2);font-size:clamp(1rem,1.35vw,1.09rem);line-height:1.78;max-width:62ch}
.muted{color:var(--muted)}
.hr{height:1px;background:var(--line);border:0;margin:0}

/* ---------- 按钮 ---------- */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  height:40px;padding:0 17px;border-radius:var(--r-1);border:1px solid transparent;
  background:var(--brand);color:#F6F8F1;text-decoration:none;
  font:600 13.5px/1 var(--sans);letter-spacing:.01em;cursor:pointer;white-space:nowrap;
  transition:background .16s var(--ease),transform .16s var(--ease),box-shadow .16s var(--ease),color .16s var(--ease),border-color .16s var(--ease);
  box-shadow:0 1px 0 rgba(255,255,255,.10) inset, 0 6px 16px rgba(30,87,68,.16);
}
.btn:hover{background:var(--brand-d);transform:translateY(-1px);box-shadow:0 1px 0 rgba(255,255,255,.10) inset,0 10px 22px rgba(30,87,68,.22)}
.btn:active{transform:translateY(0) scale(.985)}
.btn-ghost{
  background:rgba(255,255,255,.55);border-color:var(--line-2);color:var(--ink-2);box-shadow:none;
}
.btn-ghost:hover{background:var(--surface);border-color:var(--brand);color:var(--brand);box-shadow:var(--sh-1)}
.btn-sm{height:34px;padding:0 13px;font-size:12.5px;border-radius:10px}
.btn .arw{transition:transform .2s var(--ease)}
.btn:hover .arw{transform:translateX(3px)}
:where(a,button,input,summary):focus-visible{
  outline:2px solid var(--brand);outline-offset:3px;border-radius:6px;
}

/* ---------- 徽标 ---------- */
.badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:3px 9px;border-radius:999px;border:1px solid var(--line);
  background:var(--surface-2);color:var(--muted);
  font:600 11.5px/1.7 var(--sans);letter-spacing:.02em;white-space:nowrap;
}
.badge .dot{width:6px;height:6px;border-radius:50%;background:currentColor;opacity:.85}
.b-developing{background:var(--amber-bg);border-color:var(--amber-line);color:#8A4E1F}
.b-watching{background:var(--lime-2);border-color:#CFE0BA;color:#2C5B3C}
.b-quiet{background:#EDEEE7;border-color:var(--line);color:#6A7268}
.b-closed{background:#E9EAE3;border-color:var(--line-2);color:#4C554D}
.b-reopened{background:var(--red-bg);border-color:#EACBC4;color:#8E3A2C}
.b-corrob{background:#E4EFD8;border-color:#CFE0BA;color:#2C5B3C}
.b-partial{background:var(--amber-bg);border-color:var(--amber-line);color:#8A5A22}
.b-unver{background:#EFEFE8;border-color:var(--line);color:#5F675C}
.b-disputed{background:var(--red-bg);border-color:#EACBC4;color:#8E3A2C}
.b-refuted{background:#F1DEDA;border-color:#DFC0BA;color:#7E2F22}
.b-ok{background:#E4EFD8;border-color:#CFE0BA;color:#2C5B3C}
.pulse{position:relative}
.pulse::after{
  content:"";position:absolute;inset:-4px;border-radius:50%;
  border:1px solid currentColor;opacity:0;animation:pulse 2.6s var(--ease) infinite;
}
@keyframes pulse{0%{transform:scale(.7);opacity:.5}70%{transform:scale(1.9);opacity:0}100%{opacity:0}}

/* ---------- 卡片 ---------- */
.card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-2);
  box-shadow:var(--sh-1);position:relative;
}
.card-pad{padding:26px}

/* ---------- 进场动画 ---------- */
.rise{animation:rise .58s var(--ease) both}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.001s !important;animation-iteration-count:1 !important;transition-duration:.001s !important}
  html{scroll-behavior:auto}
}

/* ---------- 页脚 ---------- */
.foot{
  margin-top:64px;padding:26px 0 40px;border-top:1px solid var(--line);
  color:var(--muted);font-size:12.5px;line-height:1.8;position:relative;z-index:1;
}
.foot .inner{display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:space-between;align-items:flex-start}
.foot code{font-family:var(--mono);font-size:12px;background:var(--surface-3);padding:1px 6px;border-radius:5px}
"""

INDEX_CSS = r"""
.hero{padding:64px 0 34px}
.hero .row{display:flex;align-items:flex-end;justify-content:space-between;gap:40px;flex-wrap:wrap}
.hero .lede{margin:18px 0 0}
.hero .meta{margin-top:26px;display:flex;flex-wrap:wrap;gap:8px}
.hero .meta .badge{background:rgba(255,255,255,.7)}

.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:34px;border-top:1px solid var(--line-2);border-bottom:1px solid var(--line-2)}
.stats .cell{padding:18px 22px 16px 0;display:flex;flex-direction:column;min-height:106px}
.stats .cell + .cell{border-left:1px solid var(--line);padding-left:22px}
.stats .n{font-family:var(--serif);font-size:clamp(1.9rem,3.4vw,2.6rem);line-height:1;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stats .k{margin-top:8px;font-size:12px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase;font-weight:600}
.stats .bar{display:flex;height:5px;border-radius:99px;overflow:hidden;margin-top:auto;background:var(--surface-3)}
.stats .bar i{display:block;height:100%}

.legend{
  display:grid;gap:10px;padding:20px 22px;border:1px solid var(--line);
  border-radius:var(--r-2);background:rgba(255,255,255,.55);width:min(268px,100%);
}
.legend .t{font:700 10.5px/1.6 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted-2);margin-bottom:2px}
.legend .r{display:flex;align-items:center;gap:9px;font-size:12.5px;color:var(--ink-2);line-height:1.5}
.legend .r i{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.legend .r em{margin-left:auto;font:500 11px/1 var(--mono);font-style:normal;color:var(--muted-2)}

.tools{
  display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  padding:22px 0 18px;
}
.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip{
  border:1px solid var(--line-2);background:rgba(255,255,255,.6);color:var(--ink-2);
  border-radius:999px;height:32px;padding:0 14px;display:inline-flex;align-items:center;
  font:600 12.5px/1 var(--sans);cursor:pointer;transition:all .16s var(--ease);
}
.chip:hover{border-color:var(--brand);color:var(--brand);background:var(--surface)}
.chip[aria-pressed="true"]{background:var(--brand);border-color:var(--brand);color:#F6F8F1}
.search{margin-left:auto;position:relative;display:flex;align-items:center}
.search svg{position:absolute;left:13px;opacity:.5;pointer-events:none}
.search input{
  height:38px;width:min(280px,60vw);padding:0 14px 0 36px;border-radius:11px;
  border:1px solid var(--line-2);background:rgba(255,255,255,.72);
  font:400 13.5px/1 var(--sans);color:var(--ink);transition:box-shadow .16s var(--ease),border-color .16s var(--ease);
}
.search input::placeholder{color:var(--muted-2)}
.search input:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 3px rgba(30,87,68,.12);background:#fff}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,352px),1fr));gap:20px;padding-bottom:10px}
.ev{
  display:flex;flex-direction:column;gap:0;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-3);
  padding:26px 26px 22px;box-shadow:var(--sh-1);position:relative;overflow:hidden;
  transition:transform .22s var(--ease),box-shadow .22s var(--ease),border-color .22s var(--ease);
}
.ev::before{
  content:"";position:absolute;left:0;top:26px;bottom:26px;width:3px;border-radius:0 3px 3px 0;
  background:var(--brand);opacity:.0;transition:opacity .22s var(--ease);
}
.ev:hover{transform:translateY(-3px);box-shadow:var(--sh-2);border-color:#BFCDBB}
.ev:hover::before{opacity:1}
.ev .no{
  position:absolute;right:18px;top:8px;font-family:var(--serif);font-size:64px;line-height:1;
  color:var(--ink);opacity:.055;font-weight:600;pointer-events:none;letter-spacing:-.04em;
}
.ev .head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;min-height:26px}
.ev .place{font:700 11px/1.5 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--brand)}
.ev .sep{width:14px;height:1px;background:var(--line-2)}
.ev h3{
  font-size:1.32rem;line-height:1.4;margin:16px 0 0;letter-spacing:-.015em;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;
}
.ev p{
  color:var(--muted);font-size:14px;line-height:1.72;margin:11px 0 0;
  display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;
}
.ev .foot2{
  margin-top:auto;padding-top:16px;border-top:1px solid var(--line);
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
}
.ev .foot2 .t{font:500 11.5px/1.6 var(--mono);color:var(--muted-2);letter-spacing:-.01em}
.ev .acts{display:flex;gap:7px;margin-left:auto}
.empty{
  grid-column:1/-1;text-align:center;padding:64px 20px;color:var(--muted);
  border:1px dashed var(--line-2);border-radius:var(--r-3);background:rgba(255,255,255,.4);
}
@media(max-width:760px){
  .stats{grid-template-columns:1fr}
  .stats .cell{padding:16px 0;min-height:0}
  .stats .cell + .cell{border-left:0;border-top:1px solid var(--line);padding-left:0}
  .stats .bar{margin-top:12px}
  .search{margin-left:0;width:100%}
  .search input{width:100%}
  .ev{padding:22px 20px 18px}
  .ev .no{font-size:52px}
}
@media(max-width:600px){
  .topbar .inner{gap:10px;min-height:56px}
  .brand{gap:8px}
  .brand .mark{width:23px;height:23px;border-radius:8px;font-size:11px}
  .brand .name{font-size:11px;letter-spacing:.10em}
  .brand .name span{display:none}
  .navlink{padding:0 8px}
  .navlink span{display:none}
  .hero{padding:34px 0 24px}
  .hero .row{gap:24px}
  .legend{width:100%}
}
"""

EVENT_CSS = r"""
.backline{padding:20px 0 0}
.hd{padding:26px 0 30px}
.hd .hd-row{display:grid;grid-template-columns:minmax(0,1fr) 252px;gap:44px;align-items:end}
.hd .kicker{margin-bottom:10px}
.hd h1{font-size:clamp(1.9rem,3.7vw,3rem);line-height:1.18;margin:0;letter-spacing:-.028em;max-width:19em;text-wrap:balance}
.hd .lede{margin-top:16px}
.hd .chips{margin-top:22px;display:flex;flex-wrap:wrap;gap:8px}
.hd .chips .badge{background:rgba(255,255,255,.75)}
.index-card{
  border:1px solid var(--line);border-radius:var(--r-2);background:rgba(255,255,255,.62);
  padding:18px 20px 16px;box-shadow:var(--sh-1);
}
.index-card .t{font:700 10.5px/1.6 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted-2)}
.index-card .rows{margin:12px 0 14px;display:grid;gap:0}
.index-card .row{
  display:flex;align-items:baseline;justify-content:space-between;gap:10px;
  font-size:12.5px;color:var(--muted);padding:7px 0;border-bottom:1px dashed var(--line);
}
.index-card .row:last-child{border-bottom:0}
.index-card .row b{font-family:var(--serif);font-size:15.5px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.index-card .go2{
  display:flex;align-items:center;justify-content:space-between;gap:8px;
  height:36px;border-radius:9px;background:var(--brand);color:#F6F8F1;text-decoration:none;
  padding:0 13px;font:600 12.5px/1 var(--sans);transition:background .16s var(--ease);
}
.index-card .go2:hover{background:var(--brand-d)}
.index-card .go2 .arw{transition:transform .2s var(--ease)}
.index-card .go2:hover .arw{transform:translateX(3px)}

.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:6px 0 30px}
.metrics .m{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-2);
  padding:18px 20px;box-shadow:var(--sh-1);
}
.metrics .v{font-family:var(--serif);font-size:clamp(1.5rem,2.4vw,2rem);line-height:1.05;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.metrics .l{margin-top:8px;font-size:12.5px;line-height:1.6;color:var(--muted)}

.layout{display:grid;grid-template-columns:minmax(0,1fr) 316px;gap:26px;align-items:start;padding-bottom:20px}
.main-col{min-width:0}
.side{position:sticky;top:84px;display:grid;gap:16px}

.block{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-3);box-shadow:var(--sh-1);padding:26px 28px}
.block + .block{margin-top:18px}
.block > h2{
  display:flex;align-items:center;gap:10px;
  font-size:1.16rem;margin:0 0 18px;letter-spacing:-.01em;
}
.block > h2::before{content:"";width:3px;height:17px;border-radius:2px;background:var(--brand);flex-shrink:0}
.block .prose p{margin:0 0 12px;color:var(--ink-2);font-size:15px;line-height:1.82}
.block .prose p:last-child{margin-bottom:0}
.block .prose b{color:var(--ink);font-weight:700}
.note{font-size:12.5px;color:var(--muted);margin:18px 0 0;padding-top:14px;border-top:1px dashed var(--line-2)}

.tl{position:relative;margin:2px 0 0;padding-left:26px}
.tl::before{content:"";position:absolute;left:5px;top:8px;bottom:8px;width:1px;background:linear-gradient(to bottom,var(--line-2),var(--line) 60%,transparent)}
.tl .it{position:relative;padding:0 0 22px}
.tl .it:last-child{padding-bottom:0}
.tl .it::before{
  content:"";position:absolute;left:-25px;top:6px;width:11px;height:11px;border-radius:50%;
  background:var(--surface);border:2px solid var(--brand-l);box-shadow:0 0 0 3px var(--paper);
}
.tl .it.latest::before{background:var(--amber);border-color:var(--amber);box-shadow:0 0 0 3px #FBEFDF}
.tl time{
  display:inline-block;font:600 11.5px/1.6 var(--mono);letter-spacing:-.01em;color:var(--brand);
  background:var(--lime-2);border:1px solid #D5E3C1;border-radius:6px;padding:1px 7px;
}
.tl h3{font-family:var(--sans);font-size:14.5px;font-weight:700;line-height:1.6;margin:9px 0 4px;color:var(--ink);letter-spacing:0}
.tl p{margin:0;font-size:14px;line-height:1.78;color:var(--ink-2)}
.tl .tag{
  display:inline-block;margin-top:9px;font:600 11px/1.7 var(--sans);letter-spacing:.02em;
  color:var(--amber);background:var(--amber-bg);border:1px solid var(--amber-line);border-radius:5px;padding:0 7px;
}

.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-2);padding:20px;box-shadow:var(--sh-1)}
.panel > h2,.panel > h3{
  font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin:0 0 13px;display:flex;align-items:center;gap:8px;
}
.panel > h3{border:0}
.links{display:grid;gap:2px}
.link-row{
  display:flex;align-items:center;gap:9px;padding:8px 10px;margin:0 -10px;border-radius:9px;
  text-decoration:none;color:var(--ink-2);font-size:13.5px;line-height:1.5;
  transition:background .14s var(--ease),color .14s var(--ease);
}
.link-row:hover{background:var(--lime-2);color:var(--brand-d)}
.link-row .i{
  width:22px;height:22px;flex-shrink:0;border-radius:6px;background:var(--surface-3);
  display:grid;place-items:center;font:600 10.5px/1 var(--mono);color:var(--muted);
}
.link-row:hover .i{background:var(--brand);color:#F2F6EC}
.link-row .go{margin-left:auto;opacity:.75;font-size:11px;color:var(--brand-l)}
.link-row:hover .go{opacity:.9}
.link-note{margin:12px 0 0;font-size:11.5px;color:var(--muted-2);line-height:1.7}
.watch p{margin:0;font-size:13.5px;line-height:1.82;color:var(--ink-2)}
.watch{border-left:3px solid var(--amber);border-radius:var(--r-1)}
.src-list{display:grid;gap:1px}
.src-row{
  display:flex;gap:9px;align-items:baseline;padding:7px 0;text-decoration:none;
  font-size:13px;line-height:1.55;color:var(--ink-2);border-bottom:1px dashed var(--line);
}
.src-row:last-child{border-bottom:0;padding-bottom:0}
.src-row:hover{color:var(--brand)}
.src-row .arw{margin-left:auto;opacity:.4;flex-shrink:0}
.src-row:hover .arw{opacity:1;transform:translate(1px,-1px)}

@media(max-width:940px){
  .layout{grid-template-columns:1fr}
  .side{position:static;grid-row:1}
  .hd h1{max-width:none}
  .hd .hd-row{grid-template-columns:1fr;gap:22px;align-items:start}
  .index-card{display:none}
}
@media(max-width:600px){
  .block{padding:20px 18px;border-radius:var(--r-2)}
  .hd{padding-top:14px}
}
"""

READER_CSS = r"""
html,body{height:100%}
body{overflow:hidden}
.shell{display:grid;grid-template-columns:296px minmax(0,1fr);height:100vh;position:relative;z-index:1}

.side{
  background:rgba(247,245,236,.92);border-right:1px solid var(--line);
  display:flex;flex-direction:column;min-height:0;
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
}
.side .head{padding:18px 18px 12px;border-bottom:1px solid var(--line)}
.side .head .back{
  display:inline-flex;align-items:center;gap:7px;font:600 12px/1 var(--sans);color:var(--muted);
  text-decoration:none;margin-bottom:12px;
}
.side .head .back:hover{color:var(--brand)}
.side .head .t{font-family:var(--serif);font-size:15px;line-height:1.42;letter-spacing:-.01em;color:var(--ink)}
.side .head .k{margin-top:6px;font:500 10.5px/1.6 var(--mono);color:var(--muted-2);word-break:break-all}
.side .srch{padding:12px 18px;border-bottom:1px solid var(--line)}
.side .srch input{
  width:100%;height:34px;border-radius:9px;border:1px solid var(--line-2);
  background:var(--surface);padding:0 11px;font:400 12.5px/1 var(--sans);color:var(--ink);
}
.side .srch input:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 3px rgba(30,87,68,.10)}
.docs{flex:1;overflow-y:auto;padding:8px 10px 26px;scrollbar-width:thin}
.grp{margin:12px 0 4px;padding:0 8px;font:700 10px/1.6 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted-2)}
.grp .c{font-weight:600;color:var(--muted-2);opacity:.8;letter-spacing:0;text-transform:none}
.doc{
  display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:8px;text-decoration:none;
  color:var(--ink-2);font-size:13px;line-height:1.45;transition:background .13s var(--ease),color .13s var(--ease);
}
.doc:hover{background:#fff;color:var(--brand-d)}
.doc.active{background:var(--brand);color:#F4F8EE;box-shadow:0 6px 16px rgba(30,87,68,.18)}
.doc .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.doc .n{margin-left:auto;font:500 10.5px/1 var(--mono);opacity:.55}

.main{min-width:0;display:flex;flex-direction:column;min-height:0;position:relative}
.main .bar{
  display:flex;align-items:center;gap:12px;min-height:56px;padding:0 26px;
  border-bottom:1px solid var(--line);background:rgba(241,240,232,.9);
  -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
}
.main .bar .cur{font:600 13px/1.4 var(--sans);color:var(--ink-2);display:flex;align-items:center;gap:9px;min-width:0}
.main .bar .cur .path{font:500 11px/1.4 var(--mono);color:var(--muted-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.main .bar .sp{flex:1}
.main .bar .tocbtn{display:none}
.progress{position:absolute;left:0;right:0;top:0;height:2px;background:transparent;z-index:5}
.progress i{display:block;height:100%;width:0;background:var(--brand);transition:width .1s linear}

.content{flex:1;overflow-y:auto;padding:0;scroll-behavior:smooth}
.doc-body{width:auto;margin:0;padding:32px 44px 96px}
.crumb{
  display:flex;align-items:center;gap:8px;font:600 11px/1.4 var(--sans);
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted-2);margin-bottom:10px;
}
.crumb b{color:var(--brand);font-weight:700}

/* ---- Markdown 排版 ---- */
.md{font-size:15.5px;line-height:1.86;color:var(--ink-2)}
.md > *{max-width:900px}
.md > .tbl{max-width:min(100%,1120px)}
.md > :first-child{margin-top:0}
.md h1{
  font-family:var(--serif);font-size:clamp(1.75rem,3vw,2.35rem);line-height:1.24;letter-spacing:-.028em;
  color:var(--ink);margin:0 0 22px;padding-bottom:16px;border-bottom:1px solid var(--line);
}
.md h2{
  font-family:var(--serif);font-size:1.24rem;line-height:1.45;letter-spacing:-.012em;color:var(--ink);
  margin:38px 0 14px;padding-left:14px;border-left:3px solid var(--brand);
}
.md h3{font-family:var(--sans);font-size:1.02rem;font-weight:700;color:var(--ink);margin:24px 0 9px;letter-spacing:0}
.md h4{font-family:var(--sans);font-size:.94rem;font-weight:700;color:var(--ink-2);margin:18px 0 7px}
.md p{margin:0 0 14px}
.md ul,.md ol{margin:0 0 14px;padding-left:1.35em}
.md li{margin:4px 0}
.md li > ul,.md li > ol{margin:5px 0 2px}
.md li::marker{color:var(--brand-l)}
.md strong{color:var(--ink);font-weight:700}
.md em{color:var(--ink)}
.md a{color:var(--brand);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:2.5px;text-decoration-color:rgba(30,87,68,.32);transition:background .14s var(--ease)}
.md a:hover{background:var(--lime-2);text-decoration-color:var(--brand)}
.md hr{border:0;height:1px;background:var(--line-2);margin:28px 0}
.md blockquote{
  margin:16px 0;padding:12px 18px;border-left:3px solid var(--line-2);
  background:var(--surface-2);border-radius:0 var(--r-1) var(--r-1) 0;color:var(--ink-2);
}
.md blockquote p:last-child{margin-bottom:0}
.md code{
  font-family:var(--mono);font-size:.855em;background:var(--surface-3);color:#3A4A3E;
  padding:1.5px 6px;border-radius:5px;box-decoration-break:clone;-webkit-box-decoration-break:clone;
}
.md pre{
  background:#20261F;color:#E6EADD;border-radius:var(--r-1);padding:16px 18px;overflow-x:auto;
  font-size:12.5px;line-height:1.7;margin:16px 0;
}
.md pre code{background:none;color:inherit;padding:0;font-size:inherit}
.md .tbl{
  margin:18px 0;border:1px solid var(--line);border-radius:var(--r-1);overflow:auto;
  max-height:none;background:var(--surface);scrollbar-width:thin;
}
.md .tbl::-webkit-scrollbar{height:9px}
.md .tbl::-webkit-scrollbar-track{background:var(--surface-2)}
.md .tbl::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:99px;border:2px solid var(--surface)}
.md .tbl::-webkit-scrollbar-thumb:hover{background:var(--muted-2)}
.md table{
  border-collapse:separate;border-spacing:0;
  width:100%;font-size:12.5px;line-height:1.6;
}
.md thead th{
  position:sticky;top:0;background:var(--surface-3);z-index:3;
  font:700 11.5px/1.5 var(--sans);letter-spacing:.04em;color:var(--ink);
  text-align:left;padding:8px 10px;border-bottom:1px solid var(--line-2);white-space:nowrap;
}
.md tbody td{
  padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;
  color:var(--ink-2);min-width:84px;
}
.md td.nw{white-space:nowrap}
.md .nw2{white-space:nowrap}
.md th:first-child,.md td:first-child{position:sticky;left:0;z-index:2;background:var(--surface)}
.md thead th:first-child{z-index:4}
.md tbody tr:nth-child(even) td{background:#FAF8F0}
.md tbody tr:nth-child(even) td:first-child{background:#FAF8F0}
.md tbody tr:last-child td{border-bottom:0}
.md tbody tr:hover td{background:var(--lime-2)}
.md td:first-child{font-variant-numeric:tabular-nums}
.md td .badge{font-size:10.5px;padding:1px 7px;line-height:1.7}
.tbl-hint{
  display:flex;align-items:center;gap:6px;margin:-8px 0 18px;
  font:500 11.5px/1.6 var(--sans);color:var(--muted-2);letter-spacing:.01em;
}
.md .anchor{margin-left:-14px;opacity:0;color:var(--muted-2);font-size:.7em;text-decoration:none;transition:opacity .15s}
.md h2:hover .anchor,.md h3:hover .anchor{opacity:1}

.empty-note{color:var(--muted);font-size:13.5px;padding:60px 0;text-align:center}
@media(max-width:900px){
  .shell{grid-template-columns:1fr}
  .side{
    position:fixed;inset:0 auto 0 0;width:288px;z-index:70;transform:translateX(-102%);
    transition:transform .26s var(--ease);box-shadow:0 0 0 1px var(--line),24px 0 60px rgba(26,33,28,.18);
  }
  body.nav-open .side{transform:none}
  .scrim{position:fixed;inset:0;background:rgba(26,33,28,.28);z-index:65;opacity:0;pointer-events:none;transition:opacity .22s}
  body.nav-open .scrim{opacity:1;pointer-events:auto}
  .main .bar{padding:0 14px}
  .main .bar .tocbtn{display:inline-flex}
  .doc-body{width:calc(100% - 32px);padding:22px 0 80px;margin-inline:auto}
  .md > *{max-width:100%}
}
"""
