#!/usr/bin/env python3
"""Import real app screenshots made by the OneSpace screenshot robot.

The robot (OneSpace repo, .github/workflows/screenshots.yml) signs in as the
fictional demo couple and pushes PNGs to the private repo's `app-screens`
branch. This copies them here as light WebP files:

    python3 tools/import_screens.py /path/to/OneSpace-app-screens-checkout

core_en_today.png            -> assets/app/en/today.webp
together_ar_love.png         -> assets/app/ar/together/love.webp
themes_en_today_softRose.png -> assets/app/en/themes/today_softRose.webp
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
WIDTH = 720


def main(src: Path):
    shots = sorted((src / 'screenshots').glob('*.png'))
    for png in shots:
        parts = png.stem.split('_', 2)
        if len(parts) < 3:
            continue
        group, lang, name = parts
        folder = ROOT / 'assets' / 'app' / lang / ('' if group == 'core' else group)
        folder.mkdir(parents=True, exist_ok=True)
        im = Image.open(png).convert('RGB')
        h = round(im.height * WIDTH / im.width)
        im.resize((WIDTH, h), Image.LANCZOS).save(folder / f'{name}.webp', 'WEBP', quality=86, method=6)
    vids = sorted((src / 'videos').glob('*.mp4')) if (src / 'videos').exists() else []
    vdir = ROOT / 'assets' / 'app' / 'video'
    for mp4 in vids:
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / mp4.name).write_bytes(mp4.read_bytes())
        jpg = mp4.with_suffix('.jpg')
        if jpg.exists():
            (vdir / jpg.name).write_bytes(jpg.read_bytes())
    print(f'imported {len(shots)} screens and {len(vids)} clips')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
