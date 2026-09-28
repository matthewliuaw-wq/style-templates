#!/usr/bin/env python3
"""
scan.py —— 「文件夹知识库」可视化页面的数据生产线。

用法：
    python3 build/scan.py            # 扫描知识库文件夹，把真实数据注入 index.html

它做的事：
    1. 数一遍知识库文件夹：文章数（按月）、图片数、视频数
    2. 对每一篇策展文章，从该文件夹的 _source-meta.json 里取出原文链接
    3. 把以上数据写成 JSON，注入 index.html 的 <!--KB:DATA--> 标记块

页面是母版（本文件所在的 index.html），文件夹是要素表——
改了文件夹之后重跑一次这个脚本，页面的数字与链接随之更新。
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"
# 个人文章库根目录:默认 ~/Documents/网页文章,他人复用时用环境变量 KB_DIR 指向自己的库
KB = Path(os.environ.get("KB_DIR", "~/Documents/网页文章")).expanduser()

# ---------------------------------------------------------------- 策展层 ----
# 六层关系的语义策展（人的判断）。dir 是知识库里的文件夹名；
# title/note 是给读者看的说明。url 由脚本从 _source-meta.json 自动补全。

CURATION = [
    {
        "id": "origin",
        "line": "血缘线",
        "en": "ORIGIN",
        "color": "#C48A84",
        "summary": "演示材料的原文母本就在库里——同一条 X 帖，讲义由它改写而来。",
        "articles": [
            {
                "dir": "260811-GPT-Image-2-City-Poster-Prompt-SimplyAnnisa",
                "title": "城市旅行海报 city DNA 框架",
                "author": "SimplyAnnisa",
                "note": "2026-08-10 发布，次日入库存档。今天演示用的《城市旅行海报 Prompt 范本》正是从这一篇翻译改写而来——讲义把原文的“日式文具美学”改成了“精致文具美学”，这本身就是一次“照模板改”。",
            },
        ],
    },
    {
        "id": "siblings",
        "line": "范本线",
        "en": "SIBLING TEMPLATES",
        "color": "#7FA8BC",
        "summary": "九篇同类城市题材范本，恰好排成一条“要素表复杂度阶梯”——从单变量到十一个变量槽。",
        "articles": [
            {
                "dir": "260713-旅行海报Prompt-luciaAI",
                "title": "奢华复古旅行海报",
                "author": "luciaAI",
                "note": "五段式、单变量 [LOCATION]——最简的“母版＋要素表”入门范本。",
            },
            {
                "dir": "260731-Premium-Travel-Posters-GPT-Prompt-simeon-sanai",
                "title": "中世纪现代风旅行海报",
                "author": "simeon_sanai",
                "note": "十维度结构化提示词：三层构图、枚举式禁色、九条反向词——母版即视觉需求规格书。",
            },
            {
                "dir": "260821-CityPoster-VanishingPoint-MrLarus",
                "title": "灭点构图城市海报",
                "author": "MrLarus",
                "note": "一城一主色一符号（东京红×樱花、纽约钴蓝×出租车）。原文未贴全提示词——正好当“从成品反推”的练习题。",
            },
            {
                "dir": "260821-粉彩剪纸旅行海报模板Prompt-Goodmanprotocol",
                "title": "粉彩剪纸分层旅行海报",
                "author": "Goodmanprotocol",
                "note": "全篇数字化约束：45–60% 地标高度、2–6 纸层、6–8 色——要素表量化的典范。",
            },
            {
                "dir": "260821-城市微缩纸艺明信片Prompt-NoorAI",
                "title": "微缩纸艺城市明信片",
                "author": "NoorAI",
                "note": "十一个变量槽的现成要素表，填表即可换城量产——阶段三“照模板改”的最好底稿。",
            },
            {
                "dir": "260821-四城地标旅行海报Prompt-Goodmanprotocol",
                "title": "四城地标上下对分海报",
                "author": "Goodmanprotocol",
                "note": "上下 50/50，同一地标摄影与图形化双表达——色盘从城市推导，即 city DNA 的写法化。",
            },
            {
                "dir": "260821-水彩墨线旅行海报猜城市Prompt-Goodmanprotocol",
                "title": "水彩墨线“猜城市”海报",
                "author": "Goodmanprotocol",
                "note": "IDENTITY LOCK 锁定三至五个剪影迥异的地标。“猜城市”可直接做课堂游戏——能被认出来，才算 DNA 提取成功。",
            },
            {
                "dir": "260811-Travel-Picturebook-Prompt-Goodmanprotocol",
                "title": "1950 年代旅行绘本",
                "author": "Goodmanprotocol",
                "note": "六百词、八分区，教 AI“画得不完美”——给歪以叙事理由，控制犯错的方向。",
            },
            {
                "dir": "260821-等距国家立体模型提示词-TechieBySA",
                "title": "等距国家立体模型",
                "author": "TechieBySA",
                "note": "按国家真实国土轮廓切块——city DNA 从城市放大到国家的尺度版本。",
            },
        ],
    },
    {
        "id": "method",
        "line": "方法线",
        "en": "THREE PATHS",
        "color": "#7FA186",
        "summary": "提示词三条路，每一条都能在库里找到真人走通的实证。",
        "articles": [
            {
                "dir": "260811-Image-Prompt-Details-Adam",
                "title": "写真级提示词的物理细节法",
                "author": "Adam",
                "note": "路①自己写：把姿态、面部、服饰、手部、镜头写成具体物理细节——自己写提示词的内功。",
            },
            {
                "dir": "260821-热门生图Prompt复测-naberkayra",
                "title": "热门提示词复测",
                "author": "kayra",
                "note": "路①的进阶——复测：同一位作者、同一个提示词，前一天 81.5 万浏览，第二天续帖只有 1 条回复。",
            },
            {
                "dir": "260821-插画提示词效果验证-GjcJov",
                "title": "插画提示词效果验证",
                "author": "GjcJov",
                "note": "路①的验证生态：评论区就是免费众测报告——晒图复现、失败图暴露边界、变体二创。",
            },
            {
                "dir": "260731-文字类提示词设计指南-AdrianPunk115",
                "title": "中文字体设计提示词指南",
                "author": "AdrianPunk115",
                "note": "路②照模板改：文字＋字体＋笔画＋材质＋气质的五段公式，二十一类八十四个方案——一本模板词典。",
            },
            {
                "dir": "260821-Prompt-Tweak-Showcase-Brad",
                "title": "提示词微调展示",
                "author": "Brad",
                "note": "路②的礼仪样本：拿社群里别人的旅照提示词“稍作改写后出图”，回帖致谢——“改一处”与“全抄”的对照组。",
            },
            {
                "dir": "260821-GPT2美学提示词VOL06-丙烯平涂-xiaoxiaodong01",
                "title": "美学提示词 VOL 系列连载",
                "author": "xiaoxiaodong01",
                "note": "路②的活体展示：同一底盘句式，每期只换一种视觉语言，库里有其中十四期——下方风格墙即出自它们。",
            },
            {
                "dir": "260821-抖音爆款短片推导-leaf_sanren",
                "title": "抖音爆款是可以推导的",
                "author": "leaf_sanren",
                "note": "路③从成品反推：万粉小号断更三周，一条反推爆款的 30 秒短片冲到 10 万播放，推特同法 14 万＋11 万观看（当时仅 1500 粉），并换来商单。",
            },
            {
                "dir": "260705-Codex-Hyperframes拆解抖音爆款-Serena",
                "title": "把爆款逆向成十二步工作流",
                "author": "Serena",
                "note": "路③连着走的教科书：先拆一条对标爆款，固化成十二步工作流，再批量生成 N 条——反推、攒模板、照着改，一气呵成。",
            },
        ],
    },
    {
        "id": "industry",
        "line": "产业线",
        "en": "INDUSTRY",
        "color": "#C2A36B",
        "summary": "“图片生产线”不是教学假设——服装电商行业正在用同一种结构砍成本。",
        "articles": [
            {
                "dir": "260821-WorkBuddy笔Codex手主图产线-Shenmeili1213",
                "title": "电商主图产线",
                "author": "Shenmeili1213",
                "note": "原话是“有产线就出一批，替代有灵感出一张”。行业数据：Zalando 视觉成本约降九成、时间压缩 95% 以上；ASOS 一场活动多出 1600 多张素材、省约 9 个拍摄日。",
            },
            {
                "dir": "260731-批量提案-GPT-Image2-产品海报-derek_wall90176",
                "title": "一张产品图，一次八张提案",
                "author": "derek_wall90176",
                "note": "设计决策从线性试错变成并行比选：固定产品识别点，只换场景、风格、比例。",
            },
            {
                "dir": "260821-SkildArt电商视觉生产链-GeekCatX",
                "title": "白底图长成整套素材",
                "author": "GeekCatX",
                "note": "一张白底图沿“场景图→多尺寸→营销视频→口播”长成整套素材，画布保留生成分支——换装回分支改，不推倒重来。",
            },
            {
                "dir": "260804-TudouFlow-AI视频流水线-iluciddreaming",
                "title": "TudouFlow 个人视频流水线",
                "author": "iluciddreaming",
                "note": "个人创作者的产线化自白：“我缺的不是更快的工具，是一条生产线。”",
            },
        ],
    },
    {
        "id": "svg",
        "line": "工程线",
        "en": "DETERMINISTIC",
        "color": "#3D5A78",
        "summary": "“结构清楚走 SVG”这条判断，有工程界的同款实践背书。",
        "articles": [
            {
                "dir": "260808-HTML-SVG确定性视频Skill-heizolshao",
                "title": "HTML/SVG 确定性视频",
                "author": "heizolshao",
                "note": "把分野说清楚了：AI 生成是概率性的，HTML/SVG 是确定性的——像素可控、改一处全局生效。",
            },
            {
                "dir": "260705-Claude-Code用HTML替代Markdown-Thariq",
                "title": "用 HTML 替代 Markdown",
                "author": "Thariq",
                "note": "Claude Code 团队成员的内部实践：智能体输出几乎全面改用 HTML——信息密度、交互、流程图表达都更好。",
            },
        ],
    },
    {
        "id": "mirror",
        "line": "镜像线",
        "en": "THE MIRROR",
        "color": "#9B7E9E",
        "summary": "知识库本身就是一条生产线——结构与图片生产线完全同构。",
        "articles": [
            {
                "dir": "README.md",
                "title": "知识库 README（策展目录）",
                "author": "本库",
                "note": "三百多篇文章按主题专题编目：Loops 到 Graph 的八篇进阶链、Skills 工程化五篇——一份自己写的“内容体系初稿”。",
                "local": True,
            },
            {
                "dir": "关于工程化.md",
                "title": "关于工程化",
                "author": "本库",
                "note": "批量化与复杂性的分辨：横向重复带来线性收益，纵向分层移动能力边界——“母版批量＝效率，SVG 分层＝能力”的理论出处。",
                "local": True,
            },
            {
                "dir": "知识库升级规划.md",
                "title": "知识库升级规划",
                "author": "本库",
                "note": "为五百篇规模预建的三层索引规划——产线要跑得久，就得在规模到来之前把结构立好。",
                "local": True,
            },
        ],
    },
]


# ---------------------------------------------------------------- 扫描层 ----

def month_of(dirname: str) -> str | None:
    m = re.match(r"^(\d{2})(\d{2})", dirname)
    if not m:
        return None
    yy, mm = m.group(1), m.group(2)
    return f"20{yy}-{mm}"


def day_of(dirname: str) -> str:
    m = re.match(r"^(\d{6})", dirname)
    return f"20{m.group(1)[:2]}-{m.group(1)[2:4]}-{m.group(1)[4:6]}" if m else ""


def scan_totals():
    months: dict[str, int] = {}
    for d in KB.iterdir():
        if d.is_dir() and re.match(r"^\d{6}-", d.name):
            mm = month_of(d.name)
            if mm:
                months[mm] = months.get(mm, 0) + 1
    images = sum(
        1
        for p in KB.rglob("*")
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    )
    videos = sum(1 for p in KB.rglob("*") if p.suffix.lower() in {".mp4", ".mov", ".webm"})
    by_month = [{"month": k, "count": v} for k, v in sorted(months.items())]
    cum, run = [], 0
    for m in by_month:
        run += m["count"]
        cum.append(run)
    return {
        "articles": sum(months.values()),
        "images": images,
        "videos": videos,
        "by_month": by_month,
        "cumulative": cum,
    }


def enrich(article: dict) -> dict:
    """从 _source-meta.json 补原文链接与入库日期。"""
    a = dict(article)
    meta = KB / a["dir"] / "_source-meta.json"
    if meta.exists():
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
            a.setdefault("url", m.get("source_url", ""))
            a["fetched_chars"] = m.get("source_text_chars")
            a["fetched_imgs"] = m.get("source_img_count")
        except json.JSONDecodeError:
            pass
    a.setdefault("url", "")
    if not a.get("local"):
        a["date"] = day_of(a["dir"])
    return a


def build_payload() -> dict:
    layers = []
    for layer in CURATION:
        layers.append(
            {
                "id": layer["id"],
                "line": layer["line"],
                "en": layer["en"],
                "color": layer["color"],
                "summary": layer["summary"],
                "articles": [enrich(a) for a in layer["articles"]],
            }
        )
    return {
        "generated": date.today().isoformat(),
        "kb_root": KB.name,
        "totals": scan_totals(),
        "layers": layers,
    }


MARK_OPEN, MARK_CLOSE = "<!--KB:DATA-->", "<!--/KB:DATA-->"


def inject(payload: dict) -> None:
    html = PAGE.read_text(encoding="utf-8")
    block = (
        f"{MARK_OPEN}\n<script type=\"application/json\" id=\"kb-data\">"
        f"{json.dumps(payload, ensure_ascii=False, indent=1)}"
        f"</script>\n{MARK_CLOSE}"
    )
    if MARK_OPEN not in html:
        sys.exit("index.html 里找不到 <!--KB:DATA--> 标记，中止。")
    html = re.sub(
        re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE),
        lambda _: block,
        html,
        flags=re.S,
    )
    PAGE.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    data = build_payload()
    inject(data)
    t = data["totals"]
    print(
        f"已注入 {PAGE.name}：{t['articles']} 篇 / {t['images']} 图 / "
        f"{t['videos']} 视频，{sum(len(l['articles']) for l in data['layers'])} 篇策展入图。"
    )
