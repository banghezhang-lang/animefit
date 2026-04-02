"""
一次性迁移脚本：把所有含中文的文件/目录名改为 ASCII slug，并重新生成所有 HTML。
运行一次即可，完成后删除本脚本。
"""
import sys
import io

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "generator"))
from site_builder import slug_from_character, render_article, render_homepage, save_content_json, GRADIENTS, EMOJIS
from config import SITE_URL, OUTPUT_DIR, LANGUAGES

output = Path(OUTPUT_DIR)
data_dir = output / "data"
img_dir = output / "images"

# ── 1. 加载所有 JSON 内容 ──
all_content = []
for f in sorted(data_dir.glob("*.json")):
    with open(f, "r", encoding="utf-8") as fp:
        c = json.load(fp)
    all_content.append((f, c))

print(f"找到 {len(all_content)} 篇文章")

# ── 2. 给没有 slug_en 的文章补充 slug_en（基于 md5）──
for f, c in all_content:
    if not c.get("slug_en"):
        import hashlib
        char_hash = hashlib.md5(c["character"].encode('utf-8')).hexdigest()[:8]
        date_clean = c["date"].replace('.', '-')
        c["slug_en"] = char_hash
        print(f"  补充 slug_en: {c['character']} → {char_hash}")

# ── 3. 重命名 JSON 文件 ──
for f, c in all_content:
    new_slug = slug_from_character(c["character"], c["date"], c.get("slug_en"))
    new_path = data_dir / f"{new_slug}.json"
    if f != new_path:
        print(f"  JSON 重命名: {f.name} → {new_path.name}")
        # 先写入新文件（含更新后的 slug_en）
        with open(new_path, "w", encoding="utf-8") as fp:
            json.dump(c, fp, ensure_ascii=False, indent=2)
        # 删除旧文件（如果不同名）
        if f.exists() and f != new_path:
            f.unlink()
    else:
        # 同名，只更新内容（补充 slug_en）
        with open(new_path, "w", encoding="utf-8") as fp:
            json.dump(c, fp, ensure_ascii=False, indent=2)

# ── 4. 重命名图片文件 ──
for _, c in all_content:
    new_slug = slug_from_character(c["character"], c["date"], c.get("slug_en"))
    # 找对应图片（可能是中文名）
    char_hash_old = None
    old_image_url = c.get("image_url", "")
    if old_image_url and "/images/" in old_image_url:
        old_img_name = old_image_url.split("/images/")[-1]
        old_img_path = img_dir / old_img_name
        new_img_path = img_dir / f"{new_slug}.png"
        if old_img_path.exists() and old_img_path != new_img_path:
            print(f"  图片重命名: {old_img_path.name} → {new_img_path.name}")
            old_img_path.rename(new_img_path)
        # 更新 content 里的 image_url
        c["image_url"] = f"{SITE_URL}/images/{new_slug}.png"

# ── 5. 给每篇内容分配视觉元素 ──
contents = [c for _, c in all_content]
for c in contents:
    if not c.get("gradient"):
        char_hash = hash(c["character"])
        c["gradient"] = GRADIENTS[char_hash % len(GRADIENTS)]
        c["emoji"] = EMOJIS[char_hash % len(EMOJIS)]

# ── 6. 重新生成所有语言的文章页面 ──
print("\n重新生成文章页面...")
for c in contents:
    for lang in LANGUAGES:
        render_article(c, lang, SITE_URL, OUTPUT_DIR)

# ── 7. 重新生成首页 ──
print("\n重新生成首页...")
for lang in LANGUAGES:
    render_homepage(contents, lang, SITE_URL, OUTPUT_DIR)

# ── 8. 根目录重定向 ──
root_index = output / "index.html"
root_index.write_text('<meta http-equiv="refresh" content="0;url=/zh/">', encoding="utf-8")

# ── 9. 保存更新后的 JSON ──
for c in contents:
    save_content_json(c, OUTPUT_DIR)

print("\n✅ 迁移完成！所有文件已重命名为 ASCII slug，HTML 已重新生成。")
print("请检查 output/ 目录，然后提交推送。")
