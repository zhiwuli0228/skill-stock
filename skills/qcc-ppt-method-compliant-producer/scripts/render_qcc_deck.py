#!/usr/bin/env python3
"""Render a deck to PDF / per-page PNG / montage for visual acceptance review.

PPTX → PDF uses PowerPoint COM (Windows); PDF → PNG uses poppler's
``pdftoppm``; the montage uses Pillow. Any missing piece is reported with the
manual fallback instead of failing silently.

    python scripts/render_qcc_deck.py qcc-workspace/output/qcc-review-ready.pptx \
      --outdir qcc-workspace

Outputs land in ``<outdir>/render/`` (``qcc-review-ready.pdf``, ``slide-XX.png``,
``montage.png``).
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path


def export_pdf(pptx: Path, outdir: Path) -> Path:
    try:
        import win32com.client  # pywin32
    except ImportError as error:
        raise SystemExit(
            "渲染需要 pywin32（pip install pywin32）与已安装的 PowerPoint；"
            f"也可以手动把 {pptx.name} 另存为 PDF。原始错误：{error}"
        ) from error
    outdir.mkdir(parents=True, exist_ok=True)
    pdf = outdir / (pptx.stem + ".pdf")
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    presentation = None
    try:
        presentation = powerpoint.Presentations.Open(
            str(pptx), ReadOnly=True, Untitled=False, WithWindow=False
        )
        presentation.SaveAs(str(pdf), 32)  # ppSaveAsPDF
    finally:
        if presentation is not None:
            presentation.Close()
        powerpoint.Quit()
    if not pdf.exists():
        raise SystemExit(f"PDF 未生成：{pdf}")
    return pdf


def render_png(pdf: Path, render_dir: Path, dpi: int = 110) -> list[Path]:
    render_dir.mkdir(parents=True, exist_ok=True)
    tool = shutil.which("pdftoppm")
    if tool is None:
        raise SystemExit(
            "渲染 PNG 需要 poppler 的 pdftoppm；已生成 PDF，可手动导出图片。"
        )
    subprocess.run(
        [tool, "-png", "-r", str(dpi), str(pdf), str(render_dir / "slide")],
        check=True,
    )
    return sorted(render_dir.glob("slide-*.png"))


def build_montage(images: list[Path], out_path: Path, columns: int = 4) -> Path:
    from PIL import Image, ImageDraw

    thumbs = []
    for index, path in enumerate(images, start=1):
        image = Image.open(path).convert("RGB")
        image.thumbnail((420, 236))
        canvas = Image.new("RGB", (440, 276), "white")
        canvas.paste(image, ((440 - image.width) // 2, 8))
        draw = ImageDraw.Draw(canvas)
        draw.text((10, 250), f"{index:02d}", fill=(90, 100, 110))
        thumbs.append(canvas)
    rows = math.ceil(len(thumbs) / columns)
    montage = Image.new("RGB", (columns * 440, rows * 276), (238, 242, 246))
    for index, thumb in enumerate(thumbs):
        montage.paste(thumb, ((index % columns) * 440, (index // columns) * 276))
    montage.save(out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a QCC deck to PDF / PNG / montage.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--outdir", type=Path, required=True,
                        help="渲染根目录（结果写入 <outdir>/render/）")
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()
    if not args.pptx.exists():
        print(f"PPTX 不存在：{args.pptx}", file=sys.stderr)
        return 2

    render_dir = args.outdir / "render"
    pdf = export_pdf(args.pptx, render_dir)
    images = render_png(pdf, render_dir, args.dpi)
    montage = build_montage(images, render_dir / "montage.png")
    print(f"pdf: {pdf}")
    print(f"slides: {len(images)}")
    print(f"montage: {montage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
