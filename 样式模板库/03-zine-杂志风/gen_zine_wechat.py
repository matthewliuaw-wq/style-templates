# -*- coding: utf-8 -*-
"""
zine 版 → 公众号 HTML 版(inline 样式,可直接贴后台)

处理链(针对 1080px 定宽设计 → 公众号 ~677px 正文宽):
  1. 展开 :root CSS 变量(公众号留不住 var(),premailer 也不解析)
  2. 定宽改造:html,body{width:1080px} → 包一层 .zw 容器(max-width 677px 自适应)
  3. 全量等比缩放:所有 Npx 值 × 0.627(字号/间距/边框/阴影同步缩)
  4. premailer 全量内联进元素 style=""

用法(依赖 premailer,首次:pip3 install premailer;遇 externally-managed 用 venv,见仓库 README):
  python3 gen_zine_wechat.py
"""
import re
from pathlib import Path
from premailer import transform

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "研修班回顾-zine版.html"
OUT = ROOT / "研修班回顾-zine版-公众号版.html"
SCALE = 677 / 1080  # ≈ 0.627


def expand_vars(css: str) -> str:
    m = re.search(r":root\s*\{(.*?)\}", css, re.DOTALL)
    tokens = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)))
    for _ in range(5):
        new = css
        for name, val in tokens.items():
            new = new.replace(f"var({name})", val.strip())
        if new == css:
            break
        css = new
    return css


def main():
    html = SRC.read_text(encoding="utf-8")

    # 1. 变量展开:<style> 块 + 正文内联 style 一并展开
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    css = expand_vars(m.group(1))
    html = html.replace(m.group(0), "<style>\n" + css + "\n</style>")
    html = expand_vars(html)  # 内联 style="color:var(--navy)" 等

    # 2. 定宽 → 响应式容器:dots 纹理搬到容器上
    css = css.replace(
        "html,body{width:1080px;background-color:",
        "html,body{width:100%;background-color:")
    css = re.sub(r"html,body\{[^}]*\}", "html,body{margin:0;padding:0;}", css)
    css = css.replace("body{\n    font-family", ".zw{\n    max-width:677px;margin:0 auto;\n    font-family")
    # body 上的背景纹理与字色移到 .zw(原 body 规则保留残余安全)
    html = html.replace(m.group(0), "<style>\n" + css + "\n</style>")
    html = html.replace("<body>", '<<body>>').replace("</body>", "<</body>>")  # 防误伤,稍后还原
    html = html.replace("<<body>>", '<body>\n<div class="zw">').replace("<</body>>", "</div>\n</body>")

    # 3. 全量等比缩放(1080 设计稿 → 677 正文宽);先撤掉已改的 width:100%
    html = re.sub(r"(\d+(?:\.\d+)?)px",
                  lambda mm: "100%" if mm.group(0) == "100%px" else str(max(1, round(int(float(mm.group(1))) * SCALE))) + "px",
                  html)

    # 4. 内联
    out = transform(html, keep_style_tags=False, remove_classes=False, disable_validation=True)
    OUT.write_text(out, encoding="utf-8")

    var_left = len(re.findall(r"var\(--", out))
    stripped = re.sub(r"<style.*?</style>", "", out, flags=re.DOTALL)
    stripped = re.sub(r'\sclass="[^"]*"', "", stripped)
    survived = len(re.findall(r'style="', stripped))
    print(f"OK 生成: {OUT.name}  ({OUT.stat().st_size / 1024:.1f} KB)")
    print(f"  var() 残留: {var_left}  ({'PASS' if var_left == 0 else 'FAIL'})")
    print(f"  模拟后台剥离后 inline: {survived} 处样式生效")


if __name__ == "__main__":
    main()
