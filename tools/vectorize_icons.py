#!/usr/bin/env python3
"""Macht aus den generierten Flat-Icon-Sheets einzelne SVG-Icons.
    python3 tools/vectorize_icons.py src/icon-sheets/flat-1.png src/icon-sheets/flat-2.png
Schritte: Zelle ausschneiden → weißen Hintergrund entfernen → Farben auf die Vereinspalette
einrasten → mit vtracer vektorisieren. Braucht: pip install pillow vtracer"""
import re
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import vtracer

OUT = Path(__file__).resolve().parent.parent / 'public/assets/img/iconsflat'
SHEETS = [
    (4, ['ball', 'child', 'music', 'glove', 'family', 'dance', 'volleyball', 'stretch',
         'walk', 'fistball', 'dumbbell', 'medal', 'whistle', 'handshake', 'shield', 'clipboard']),
    (3, ['team', 'trophy', 'food', 'couple', 'heart', 'jersey', 'calendar', 'pin', 'mail']),
]
PALETTE = ['#1D54DA', '#1A4396', '#3E74E5', '#C2D2F7', '#E3EBFC', '#FDCA69', '#FEC43C',
           '#E2437F', '#FC6A3F', '#22A463', '#FFFFFF']
PAL = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PALETTE]


def nearest(p):
    return min(PAL, key=lambda c: (c[0] - p[0]) ** 2 * .3 + (c[1] - p[1]) ** 2 * .59 + (c[2] - p[2]) ** 2 * .11)


def prepare(cell):
    rgb = cell.convert('RGB')
    r, g, b = rgb.split()
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    hi = ImageChops.lighter(ImageChops.lighter(r, g), b)
    white = ImageChops.multiply(lo.point(lambda v: 255 if v > 236 else 0),
                                ImageChops.subtract(hi, lo).point(lambda v: 255 if v < 16 else 0))
    w, h = white.size
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if white.getpixel(p) == 255:
            ImageDraw.floodfill(white, p, 128)
    obj = white.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    bbox = obj.getbbox()
    rgb, obj = rgb.crop(bbox), obj.crop(bbox)
    # Farben einrasten (Cache pro Farbe)
    cache = {}
    data = [cache.setdefault(p, nearest(p)) for p in rgb.getdata()]
    snapped = Image.new('RGB', rgb.size); snapped.putdata(data)
    snapped = snapped.filter(ImageFilter.ModeFilter(5))            # Kantenrauschen entfernen
    out = snapped.convert('RGBA'); out.putalpha(obj)
    side = int(max(out.size) * 1.06)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(out, ((side - out.width) // 2, (side - out.height) // 2), out)
    return sq


def to_svg(img, name):
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / 'in.png', Path(tmp) / 'out.svg'
        img.save(src)
        vtracer.convert_image_to_svg_py(str(src), str(dst), colormode='color', hierarchical='stacked', mode='spline',
                                        filter_speckle=10, color_precision=8, layer_difference=10,
                                        corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1)
        svg = dst.read_text()
    w, h = img.size
    svg = re.sub(r'<\?xml.*?\?>\s*|<!--.*?-->\s*', '', svg, flags=re.S)
    svg = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">', svg, count=1)
    (OUT / f'{name}.svg').write_text(svg)
    return len(svg)


def main(paths):
    OUT.mkdir(parents=True, exist_ok=True)
    for path, (n, names) in zip(paths, SHEETS):
        sheet = Image.open(path)
        cw, ch = sheet.width / n, sheet.height / n
        for i, name in enumerate(names):
            row, col = divmod(i, n)
            cell = sheet.crop((round(col * cw), round(row * ch), round((col + 1) * cw), round((row + 1) * ch)))
            print(name, to_svg(prepare(cell), name) // 1024, 'KB')


if __name__ == '__main__':
    main(sys.argv[1:])
