"""
完整重建脚本：修复 image_url + 重新生成所有 HTML
"""
import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / 'generator'))

from site_builder import slug_from_character, render_article, render_homepage, GRADIENTS, EMOJIS
from config import SITE_URL, OUTPUT_DIR, LANGUAGES

output = BASE / 'output'
data_dir = output / 'data'
img_dir = output / 'images'

# 加载所有 JSON
all_content = []
for f in sorted(data_dir.glob('*.json')):
    with open(f, encoding='utf-8') as fp:
        c = json.load(fp)
    # 计算 ASCII slug
    slug = slug_from_character(c['character'], c['date'], c.get('slug_en'))
    # 修复 image_url（图片文件已重命名为 ASCII）
    expected_img = img_dir / (slug + '.png')
    if expected_img.exists():
        c['image_url'] = f'{SITE_URL}/images/{slug}.png'
    # 分配视觉元素
    if not c.get('gradient'):
        ch = hash(c['character'])
        c['gradient'] = GRADIENTS[ch % len(GRADIENTS)]
        c['emoji'] = EMOJIS[ch % len(EMOJIS)]
    # 保存更新的 JSON
    with open(f, 'w', encoding='utf-8') as fp:
        json.dump(c, fp, ensure_ascii=False, indent=2)
    all_content.append(c)
    print(f"  loaded: {c['character']} | slug: {slug} | image: {c.get('image_url','NONE')}")

print(f"\n找到 {len(all_content)} 篇文章\n")

# 重新生成所有文章页
print("生成文章页面...")
for c in all_content:
    for lang in LANGUAGES:
        render_article(c, lang, SITE_URL, str(output))
print("文章页面生成完毕")

# 重新生成首页
print("\n生成首页...")
for lang in LANGUAGES:
    render_homepage(all_content, lang, SITE_URL, str(output))
    print(f"  homepage: {lang}")

# 根目录重定向
redirect_html = '<meta http-equiv="refresh" content="0;url=/zh/">'
(output / 'index.html').write_text(redirect_html, encoding='utf-8')

print('\n[OK] 完成！所有 HTML 已重新生成，image_url 已修复。')
