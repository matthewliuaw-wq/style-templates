# -*- coding: utf-8 -*-
"""
出全页图 —— HTML/SVG 源 → 整页 PNG(不截断、不手猜高度)

原理:Chrome headless 用超高窗口(16000px)截图,再用 PIL 从底部向上找
最后一行有内容的像素,裁掉下方空白。背景色按左上角像素判定。

用法(需 Python3 + Pillow + Chrome,首次: pip3 install Pillow):
  python3 出全页图.py <源文件.html|.svg> [输出.png] [宽度,默认1080]

例:
  python3 出全页图.py 03-zine-杂志风/模板示例.html 新主题.png 1080
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

# Chrome 逐个探测:macOS 常规路径优先,退到 PATH 里的 chrome/chromium(Linux/Windows)
_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
]
CHROME = next((c for c in _CHROME_CANDIDATES if Path(c).exists()), None) \
    or shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
if not CHROME:
    sys.exit("找不到 Chrome/Chromium,请安装后重试(macOS 装Google Chrome,Linux 装 chromium)")
MAX_H = 16000  # Chrome 单窗高度上限附近,再高会被钳制


def render(src: Path, out: Path, width: int = 1080) -> None:
    tmp = out.with_suffix(".tmp.png")
    # 支持 "file.html?query" 写法:查询串拼在 URI 之后,不进文件名
    src_str = str(src)
    if "?" in src_str:
        path_part, query = src_str.split("?", 1)
        uri = Path(path_part).resolve().as_uri() + "?" + query
    else:
        uri = src.resolve().as_uri()
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--screenshot={tmp}", f"--window-size={width},{MAX_H}",
         "--virtual-time-budget=8000", uri],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    img = Image.open(tmp).convert("RGB")
    w, h = img.size
    # 背景取全图众数色(纸色占最大面积;不能用角落——封面可能是满版色块)
    small = img.resize((160, max(1, int(h * 160 / w))))
    colors = small.getcolors(160 * small.size[1])
    bg = max(colors, key=lambda c: c[0])[1]

    def row_has_content(y: int) -> bool:
        for x in range(2, w - 2, 8):
            p = img.getpixel((x, y))
            if abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 30:
                return True
        return False

    bottom = h - 1
    while bottom > 0 and not row_has_content(bottom):
        bottom -= 1
    if bottom >= h - 4:  # 页面比窗口还高,内容被截,提醒人工处理
        print(f"警告:内容高度可能超过 {MAX_H}px,请检查底部是否完整")
    img.crop((0, 0, w, min(h, bottom + 40))).save(out)
    tmp.unlink()
    print(f"OK {out}  ({w}x{min(h, bottom + 40)})")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".png")
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
    render(src, out, width)


if __name__ == "__main__":
    main()
