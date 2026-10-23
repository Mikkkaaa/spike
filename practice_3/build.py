#!/usr/bin/env python3
"""Собирает dist/ для публикации.

Исходники лендинга лежат в src/. Бренд-материалы (логотипы, шрифты, токены) не
дублируются: они берутся из shared/brand/ при сборке и попадают только в dist/
(его можно удалять и пересобирать).
"""
import os
import re
import shutil
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
BRAND_DIR = ROOT.parent / "shared" / "brand"
SRC, DIST = ROOT / "src", ROOT / "dist"

FONTS = ["Inter-Regular", "Inter-Medium", "Inter-SemiBold", "Inter-Bold",
         "JetBrainsMono-Regular", "JetBrainsMono-Medium"]
LOGOS = ["spike-icon.svg", "spike-logo-horizontal-dark-bg.svg"]
# латиница, кириллица, пунктуация, ₽ № ± ≈ − стрелки
UNICODES = [*range(0x20, 0x7F), *range(0xA0, 0x100), *range(0x400, 0x4FF),
            *range(0x2010, 0x2028), 0x2030, 0x2039, 0x203A, 0x20BD, 0x2116,
            0x2212, 0x2248, *range(0x2190, 0x2194)]


def subset_font(src: Path, dst: Path) -> None:
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    font = TTFont(src)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = "woff"
    font.save(dst)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "fonts").mkdir(parents=True)
    (DIST / "logo").mkdir()

    for f in SRC.iterdir():
        if f.is_file():
            shutil.copy2(f, DIST / f.name)

    # tokens.css вливается в style.css: на один блокирующий запрос меньше.
    tokens = (BRAND_DIR / "tokens.css").read_text(encoding="utf-8")
    css = DIST / "style.css"
    css.write_text(tokens + "\n" + css.read_text(encoding="utf-8"), encoding="utf-8")

    html = (DIST / "index.html").read_text(encoding="utf-8")
    link = '<link rel="stylesheet" href="tokens.css">\n'
    assert link in html, "в index.html не найдена ссылка на tokens.css"
    html = html.replace(link, "")

    # Абсолютные адреса (canonical, og:image) известны только после публикации:
    # SITE_URL=https://логин.github.io/репозиторий/practice_3/ python3 build.py
    site = os.environ.get("SITE_URL", "").strip()
    block = re.compile(r"<!--site:start-->.*?<!--site:end-->\n", re.S)
    if site:
        site = site.rstrip("/") + "/"
        html = html.replace("<!--site:start-->\n", "").replace("<!--site:end-->\n", "").replace("%SITE_URL%", site)
    else:
        html = block.sub("", html)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    for name in LOGOS:
        shutil.copy2(BRAND_DIR / "logo" / name, DIST / "logo" / name)
    for name in FONTS:
        subset_font(BRAND_DIR / "fonts" / f"{name}.ttf", DIST / "fonts" / f"{name}.woff")

    total = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file())
    print(f"dist/ готов: {sum(1 for _ in DIST.rglob('*') if _.is_file())} файлов, {total/1024:.0f} КБ")


if __name__ == "__main__":
    main()
