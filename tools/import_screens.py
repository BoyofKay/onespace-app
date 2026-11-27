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


# Small real pieces of screens for the "Sound familiar?" answers: (source, top, bottom) as
# fractions of the screen height. Tune after a robot run if a layout moves.
CROPS = {
    'lists': ('lists', 0.36, 0.57),
    'places': ('places', 0.165, 0.37),
    'clocks': ('today', 0.17, 0.43),
    'options': ('decision', 0.235, 0.56),
    'counter': ('counters', 0.085, 0.36),
    'trip': ('trip', 0.07, 0.34),
}
SKIP = {'checkins', 'experiences', 'appearance', 'video_done'}  # empty or with debug overflow marks


def crops():
    for lang in ('en', 'ar'):
        for name, (source, top, bottom) in CROPS.items():
            f = ROOT / 'assets' / 'app' / lang / f'{source}.webp'
            if not f.exists():
                continue
            im = Image.open(f)
            out = ROOT / 'assets' / 'app' / lang / 'snip'
            out.mkdir(parents=True, exist_ok=True)
            im.crop((0, round(im.height * top), im.width, round(im.height * bottom))).save(out / f'{name}.webp', 'WEBP', quality=88, method=6)


def main(src: Path):
    shots = sorted((src / 'screenshots').glob('*.png'))
    for png in shots:
        parts = png.stem.split('_', 2)
        if len(parts) < 3:
            continue
        group, lang, name = parts
        if name in SKIP:
            continue
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
        # Poster: a frame from the middle of the clip (the start is often the same screen).
        import subprocess
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)],
                                   capture_output=True, text=True).stdout.strip() or 1)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{dur * 0.72:.2f}', '-i', str(mp4), '-frames:v', '1', '-q:v', '4',
                        str(vdir / mp4.with_suffix('.jpg').name)], check=True)
    # D110: chapter times for the tutorial videos (seconds where each caption starts).
    for marks in sorted((src / 'videos').glob('*.chapters.json')) if (src / 'videos').exists() else []:
        (vdir / marks.name).write_bytes(marks.read_bytes())
    crops()
    print(f'imported {len(shots)} screens and {len(vids)} clips')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
