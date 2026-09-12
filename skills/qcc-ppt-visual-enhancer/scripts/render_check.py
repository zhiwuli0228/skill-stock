#!/usr/bin/env python3
"""Render PPTX -> PDF -> PNG -> montage for the visual review gate.

PDF export order:
1. Microsoft PowerPoint COM automation (Windows);
2. LibreOffice `soffice` / `libreoffice` headless;

PNG rendering uses poppler `pdftoppm`; the montage uses Pillow when available.
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path


def export_pdf_powerpoint(pptx: Path, pdf: Path) -> bool:
    try:
        import win32com.client  # type: ignore
    except ImportError:
        return False
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        presentation = powerpoint.Presentations.Open(
            str(pptx), ReadOnly=True, Untitled=False, WithWindow=False
        )
        try:
            presentation.SaveAs(str(pdf), 32)  # ppSaveAsPDF
        finally:
            presentation.Close()
            powerpoint.Quit()
        return pdf.exists()
    except Exception as error:  # pragma: no cover - depends on the desktop
        print(f"PowerPoint export failed: {error}", file=sys.stderr)
        return False


def export_pdf_libreoffice(pptx: Path, outdir: Path) -> bool:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return False
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(pptx)],
        check=False,
    )
    return (outdir / (pptx.stem + ".pdf")).exists()


def build_montage(images: list[Path], target: Path, columns: int = 4) -> Path | None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    thumbs = []
    for index, path in enumerate(images, start=1):
        image = Image.open(path).convert("RGB")
        image.thumbnail((420, 236))
        canvas = Image.new("RGB", (440, 276), "white")
        canvas.paste(image, ((440 - image.width) // 2, 8))
        ImageDraw.Draw(canvas).text((10, 250), f"{index:02d}", fill=(90, 100, 110))
        thumbs.append(canvas)
    rows = math.ceil(len(thumbs) / columns)
    montage = Image.new("RGB", (columns * 440, rows * 276), (238, 242, 246))
    for index, thumb in enumerate(thumbs):
        montage.paste(thumb, ((index % columns) * 440, (index // columns) * 276))
    montage.save(target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a PPTX for visual review.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--out", type=Path, default=Path("render"))
    args = parser.parse_args()

    if not args.pptx.exists():
        print(f"PPTX not found: {args.pptx}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    pdf = args.out / (args.pptx.stem + ".pdf")

    if not export_pdf_powerpoint(args.pptx, pdf) and not export_pdf_libreoffice(args.pptx, args.out):
        print(
            "No PDF exporter available: install Microsoft PowerPoint or LibreOffice.",
            file=sys.stderr,
        )
        return 2
    if not pdf.exists():
        candidates = list(args.out.glob("*.pdf"))
        if not candidates:
            print("PDF export produced no file", file=sys.stderr)
            return 2
        pdf = candidates[0]

    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        print("poppler pdftoppm is required for PNG rendering", file=sys.stderr)
        return 2
    subprocess.run(
        [pdftoppm, "-png", "-r", "110", str(pdf), str(args.out / "slide")],
        check=True,
    )
    images = sorted(args.out.glob("slide-*.png"))
    montage = build_montage(images, args.out / "montage.png") if images else None
    print(f"pdf: {pdf}")
    print(f"slides: {len(images)}")
    if montage:
        print(f"montage: {montage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
