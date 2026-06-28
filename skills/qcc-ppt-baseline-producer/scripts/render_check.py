#!/usr/bin/env python3
"""Render PPTX to PDF/PNG and create a montage for visual inspection."""
from __future__ import annotations
import argparse, subprocess, shutil, math
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pptx", type=Path)
    ap.add_argument("--out", type=Path, default=Path("output/render"))
    args=ap.parse_args()
    out=args.out; out.mkdir(parents=True, exist_ok=True)
    soffice=shutil.which("soffice") or shutil.which("libreoffice")
    pdftoppm=shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        raise SystemExit("LibreOffice 'soffice' and poppler 'pdftoppm' are required for render checks")
    run([soffice,"--headless","--convert-to","pdf","--outdir",str(out),str(args.pptx)])
    pdf=out/(args.pptx.stem+".pdf")
    if not pdf.exists():
        candidates=list(out.glob("*.pdf"))
        if not candidates: raise SystemExit("PDF not produced")
        pdf=candidates[0]
    prefix=out/"slide"
    run([pdftoppm,"-png",str(pdf),str(prefix)])
    imgs=sorted(out.glob("slide-*.png"))
    thumbs=[]
    for i,p in enumerate(imgs,1):
        im=Image.open(p).convert("RGB")
        im.thumbnail((320,180))
        canvas=Image.new("RGB",(340,220),"white")
        canvas.paste(im,((340-im.width)//2,10))
        d=ImageDraw.Draw(canvas); d.text((8,195),f"{i:02d}",fill=(80,80,80))
        thumbs.append(canvas)
    if thumbs:
        cols=4; rows=math.ceil(len(thumbs)/cols)
        montage=Image.new("RGB",(cols*340,rows*220),(240,240,240))
        for i,t in enumerate(thumbs): montage.paste(t,((i%cols)*340,(i//cols)*220))
        montage_path=out/"montage.png"; montage.save(montage_path)
        print("Montage:", montage_path)
    print("Rendered slides:", out)

if __name__ == "__main__":
    main()
