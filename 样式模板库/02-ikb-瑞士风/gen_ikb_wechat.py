# -*- coding: utf-8 -*-
"""
把 IKB 瑞士风网页版 HTML 转成公众号可发布的 inline-HTML。

处理链(针对公众号后台会 strip <style>/class 的约束):
  1. 展开 :root CSS 变量(公众号留不住 var(),premailer 也不解析)
  2. 手机优先合并:把 @media (max-width) 的规则并入基础样式作为默认值
     ——公众号阅读九成在手机,桌面增强被剥离也不影响
  3. premailer 把 CSS 全部内联进元素 style=""
     ——伪元素(::before/::after)与 @media 无法内联,残留在 <style> 里,
       公众号会剥掉(等于丢装饰,无伤结构);本地预览仍可见

用法(依赖 premailer,首次:pip3 install premailer;遇 externally-managed 用 venv,见仓库 README):
  python3 gen_ikb_wechat.py
"""
import re
from pathlib import Path
from premailer import transform

ROOT = Path(__file__).resolve().parent
SRC_HTML = ROOT / "real-program-details-ikb.html"   # 网页版源
SRC_CSS = ROOT / "assets/program-ikb.css"            # 对应样式
OUT = ROOT / "real-program-details-ikb-公众号版.html" # 公众号版产物


def expand_vars(css: str) -> str:
    """:root 变量多轮展开(支持变量嵌套引用)"""
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


def merge_mobile_first(css: str) -> str:
    """把首个 @media (max-width:...) 块的规则体并入基础样式末尾(后置覆盖),
    并删掉该 @media 块。"""
    m = re.search(r"@media[^{]*\{(.*?)\n\}", css, re.DOTALL)
    if not m:
        return css
    mobile_rules = m.group(1)
    base = css[: m.start()] + css[m.end():]
    return base + "\n/* ---- mobile-first merge(公众号默认按手机端渲染)---- */\n" + mobile_rules + "\n"


def main():
    html = SRC_HTML.read_text(encoding="utf-8")
    css = SRC_CSS.read_text(encoding="utf-8")

    css = expand_vars(css)
    css = merge_mobile_first(css)

    # 外链样式改内嵌,交给 premailer
    html = html.replace(
        '<link rel="stylesheet" href="assets/program-ikb.css">',
        "<style>\n" + css + "\n</style>",
    )

    out = transform(html, keep_style_tags=False, remove_classes=False, disable_validation=True)
    OUT.write_text(out, encoding="utf-8")

    # ---- 体检 ----
    var_left = len(re.findall(r"var\(--", out))
    style_tags = re.findall(r"<style[^>]*>(.*?)</style>", out, re.DOTALL)
    residue = sum(len(s) for s in style_tags)
    stripped = re.sub(r"<style.*?</style>", "", out, flags=re.DOTALL)
    stripped = re.sub(r'\sclass="[^"]*"', "", stripped)
    survived = len(re.findall(r'style="', stripped))

    print(f"OK 生成: {OUT.name}  ({OUT.stat().st_size / 1024:.1f} KB)")
    print(f"  var() 残留          : {var_left}  ({'PASS' if var_left == 0 else 'FAIL'})")
    print(f"  <style> 残留字符     : {residue}  (仅伪元素等无法内联项,公众号会剥掉,无伤结构)")
    print(f"  模拟后台剥离后 inline: {survived} 处样式生效")


if __name__ == "__main__":
    main()
