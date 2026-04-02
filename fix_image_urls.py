"""修复所有 JSON 的 image_url（如果有对应图片文件）"""
import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / 'generator'))
from site_builder import slug_from_character
from config import SITE_URL

data_dir = BASE / 'output' / 'data'
img_dir = BASE / 'output' / 'images'

fixed = []
missing = []
for f in sorted(data_dir.glob('*.json')):
    with open(f, encoding='utf-8') as fp:
        c = json.load(fp)
    slug = slug_from_character(c['character'], c['date'], c.get('slug_en'))
    img_path = img_dir / (slug + '.png')
    new_url = f'{SITE_URL}/images/{slug}.png'
    if img_path.exists():
        old_url = c.get('image_url', '')
        c['image_url'] = new_url
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(c, fp, ensure_ascii=False, indent=2)
        if old_url != new_url:
            fixed.append(f'FIXED: {c["character"]} ({slug})')
    else:
        missing.append(f'MISSING IMAGE: {c["character"]} (slug={slug})')

for m in fixed:
    print(m)
for m in missing:
    print(m)
print(f'\nDone. Fixed={len(fixed)}, Missing={len(missing)}')
