#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageOps

CHARS = "@#S%?*+;:,. "

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=72)
    p.add_argument("--invert", action="store_true")
    args = p.parse_args()

    image = Image.open(args.source).convert("L")
    # Crop to the largest centered portrait region, then preserve the face.
    w, h = image.size
    # For a typical portrait photo, focus on the person and avoid most background.
    if h >= 1000 and w >= 700:
        image = image.crop((0, int(h * 0.43), int(w * 0.94), h))
    else:
        crop_w = min(w, int(h * 0.78))
        left = max(0, (w - crop_w) // 2)
        image = image.crop((left, 0, left + crop_w, h))
    ratio = image.height / image.width
    height = max(1, int(args.width * ratio * 0.48))
    image = image.resize((args.width, height), Image.Resampling.LANCZOS)
    if args.invert:
        image = ImageOps.invert(image)

    lines = []
    pix = image.load()
    for y in range(image.height):
        chars = []
        for x in range(image.width):
            value = pix[x, y]
            chars.append(CHARS[int(value / 256 * len(CHARS)) if int(value / 256 * len(CHARS)) < len(CHARS) else -1])
        lines.append("".join(chars).rstrip())

    max_len = max(len(line) for line in lines)
    font_size = 12
    text_nodes = []
    y0 = 16
    for i, line in enumerate(lines):
        text_nodes.append(f'<text x="0" y="{y0 + i * font_size}" xml:space="preserve">{line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{max_len * 7}" height="{(len(lines)+1)*font_size}" viewBox="0 0 {max_len * 7} {(len(lines)+1)*font_size}"><g font-family="monospace" font-size="{font_size}" fill="#c9d1d9">{"".join(text_nodes)}</g></svg>'''
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    main()
