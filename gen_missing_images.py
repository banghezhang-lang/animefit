# -*- coding: utf-8 -*-
import requests, time, json
from pathlib import Path

API_KEY = 'sk-fwvzzktzkupnvbgedylylqgbjcjdevbcsoncucqtmsemkxcd'
API_URL = 'https://api.siliconflow.cn/v1/images/generations'

headers = {
    'Authorization': 'Bearer ' + API_KEY,
    'Content-Type': 'application/json'
}

prompts = [
    ('2026-03-31-91014e89',
     'Misaka Mikoto, anime girl with short brown hair, Tokiwadai school uniform with navy skirt, electric sparks around, cool androgynous fashion editorial, cyberpunk neon lighting, highly detailed, vibrant colors'),
    ('2026-04-01-91014e89',
     'Misaka Mikoto, anime girl with short spiky brown hair, Tokiwadai white blouse and navy pleated skirt, oversized electric blue blazer, fingerless tactical gloves, coin between fingers crackling with electricity, standing in neon-lit city street at dusk, cool androgynous fashion editorial, anime style, vibrant colors, 4k'),
]

img_dir = Path(r'c:/Users/Banghe.Zhang/WorkBuddy/Claw/anime_fashion_site/output/images')

for slug, prompt in prompts:
    print(f'Generating: {slug}')
    for attempt in range(5):
        try:
            payload = {
                'model': 'Qwen/Qwen-Image',
                'image_size': '1024x1024',
                'images': [{'prompt': prompt}]
            }
            r = requests.post(API_URL, headers=headers, json=payload, timeout=180)
            print(f'  Status: {r.status_code}')
            data = r.json()
            if r.status_code == 200 and 'images' in data and data['images']:
                img_url = data['images'][0]['url']
                img_data = requests.get(img_url, timeout=60).content
                out_path = img_dir / (slug + '.png')
                out_path.write_bytes(img_data)
                print(f'  Saved: {out_path.name} ({len(img_data)} bytes)')
                break
            else:
                print(f'  Error: {data}')
                time.sleep(10)
        except Exception as e:
            print(f'  Exception: {e}')
            time.sleep(15)
    else:
        print(f'  FAILED after 5 attempts: {slug}')

print('Done')
