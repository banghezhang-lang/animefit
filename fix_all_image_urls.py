# -*- coding: utf-8 -*-
import json
from pathlib import Path
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(r'c:/Users/Banghe.Zhang/WorkBuddy/Claw/anime_fashion_site')
img_dir = BASE / 'output' / 'images'
data_dir = BASE / 'output' / 'data'
sys.path.insert(0, str(BASE / 'generator'))
from site_builder import slug_from_character
from config import SITE_URL

fixed = []
for f in sorted(data_dir.glob('*.json')):
    with open(f, encoding='utf-8') as fp:
        c = json.load(fp)
    slug = slug_from_character(c['character'], c['date'], c.get('slug_en'))
    img_path = img_dir / (slug + '.png')
    old_url = c.get('image_url', '')
    new_url = SITE_URL + '/images/' + slug + '.png'

    if img_path.exists():
        if old_url != new_url:
            c['image_url'] = new_url
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(c, fp, ensure_ascii=False, indent=2)
            fixed.append(c['character'] + ' (' + c['date'] + '): ' + str(old_url) + ' -> ' + new_url)
    else:
        print('NO IMAGE FILE:', c['character'], '(slug=' + slug + ')')

for msg in fixed:
    print('FIXED:', msg)
print('Total fixed:', len(fixed))
