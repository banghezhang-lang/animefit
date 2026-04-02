# -*- coding: utf-8 -*-
import requests
from pathlib import Path

prompts = [
    ('2026-03-31-91014e89',
     'Misaka Mikoto anime girl Tokiwadai school uniform electric sparks cyberpunk fashion editorial vibrant'),
    ('2026-04-01-91014e89',
     'Misaka Mikoto anime girl Tokiwadai uniform electric blue blazer coin electricity fashion editorial vibrant'),
]

img_dir = Path(r'c:/Users/Banghe.Zhang/WorkBuddy/Claw/anime_fashion_site/output/images')

for slug, prompt in prompts:
    encoded = requests.utils.quote(prompt)
    url = f'https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed=42&nologo=true'
    print(f'Fetching: {slug}')
    try:
        r = requests.get(url, timeout=90)
        ct = r.headers.get('Content-Type', '?')
        print(f'  Status: {r.status_code}, Content-Type: {ct}')
        if r.status_code == 200 and 'image' in ct:
            out = img_dir / (slug + '.png')
            out.write_bytes(r.content)
            print(f'  Saved: {out.name} ({len(r.content)} bytes)')
        else:
            print(f'  Response snippet: {r.text[:200]}')
    except Exception as e:
        print(f'  Error: {e}')

print('Done')
