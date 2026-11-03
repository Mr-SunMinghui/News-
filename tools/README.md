# 视图构建工具

把仓库里的档案内容渲染成三类离线 HTML 页面，双击即可看，不依赖网络、CDN 或本地服务器。

## 生成物

| 文件 | 内容 |
|---|---|
| `速览.html`（根目录） | 全部事件总览：状态图例、统计条、卡片、按状态筛选、关键词搜索 |
| `实践/events/<id>/速览.html` | 单事件速览：关键数据、时间线、后续关注、来源速链、档案导航 |
| `实践/events/<id>/档案.html` | 档案阅读器：把该事件全部 `.md`（事实汇编、时间线、主张、来源、状态、叙事、巡检日志、来源快照）渲染成网页，左侧切换、站内跳转，表格与证据状态上色 |

## 怎么用

双击 `tools/build_views.bat`，或在仓库根目录执行：

```bat
python tools\build_views.py
```

常用参数：

```bat
python tools\build_views.py --only evt-20261017-france-unrest   :: 只重建一个事件
python tools\build_views.py --extract                           :: 从基线页面重新抽取内容 JSON
```

改完 `.md` 或 `event.yaml` 后重跑一次即可刷新页面；页面里的"构建时间"会跟着变，看到旧时间就说明还没重建。

## 依赖

脚本用到 `markdown`、`beautifulsoup4`、`pyyaml`，已装在隔离虚拟环境里：

```text
%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe
```

换机器时需要重建环境：

```bat
python -m venv 目标目录
目标目录\Scripts\pip install markdown pyyaml beautifulsoup4
```

## 内容从哪来（重要）

- **事件速览页的正文不写死在模板里**。摘要、关键数据、时间线、后续关注、来源短链来自 `tools/views/<event_id>.json`。
  首次运行从重构前的老页面抽取生成（基线副本在 `.workbuddy/backup/2026-10-22-quickview/`），之后构建只改版式、不碰内容，重复运行是幂等的。
- 要改某个事件速览的文字，改对应的 `tools/views/<event_id>.json`，再重建。新事件可从 `tools/views/_template.json` 复制一份起步。
- **状态、优先级、首次发现、最近核查以 `event.yaml` 为准**，因为 YAML 通常比手写页面更新。
- **档案阅读器的内容独取磁盘上的 `.md`**，不经过 JSON，所以 md 是唯一事实来源。

## 校验

```bat
python tools\verify_views.py
```

把重构前页面的正文切句，逐条检查是否仍出现在新页面里。导航、英文状态行、用「·」串起的来源行属于版式等价改写，单独放行并注明理由。全部输出 `OK` 才算没有丢内容。

## 已知边界

- 不联网、不抓取、不改写任何档案内容，只做渲染。
- 阅读器内 md 之间的相对链接会改写成站内跳转；指向未收录文件的链接会置灰并提示。
- 宽表在窄屏上需要左右滚动，页面会在表格下方自动加提示。
