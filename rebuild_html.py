"""
直接重新生成所有 HTML（JSON 已是 ASCII slug，图片已重命名）
"""
import sys, io, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "generator"))
from site_builder import slug_from_character, render_article, render_homepage, save_content_json, GRADIENTS, EMOJIS
from config import SITE_URL, OUTPUT_DIR, LANGUAGES

output = Path(OUTPUT_DIR)
data_dir = output / "data"

# 加载所有 JSON
all_content = []
for f in sorted(data_dir.glob("*.json")):
    with open(f, "r", encoding="utf-8") as fp:
        c = json.load(fp)
    # 确保 image_url 用 ASCII 文件名
    slug = slug_from_character(c["character"], c["date"], c.get("slug_en"))
    c["image_url"] = f"{SITE_URL}/images/{slug}.png"
    # 分配视觉元素
    if not c.get("gradient"):
        char_hash = hash(c["character"])
        c["gradient"] = GRADIENTS[char_hash % len(GRADIENTS)]
        c["emoji"] = EMOJIS[char_hash % len(EMOJIS)]
    all_content.append(c)

print(f"找到 {len(all_content)} 篇文章")

# 重新生成文章页
print("\n生成文章页面...")
for c in all_content:
    for lang in LANGUAGES:
        render_article(c, lang, SITE_URL, OUTPUT_DIR)

# 重新生成首页
print("\n生成首页...")
for lang in LANGUAGES:
    render_homepage(all_content, lang, SITE_URL, OUTPUT_DIR)

# 根目录重定向
root_index = output / "index.html"
root_index.write_text('<meta http-equiv="refresh" content="0;url=/zh/">', encoding="utf-8")

# 保存更新后的 JSON（含 image_url）
for c in all_content:
    save_content_json(c, OUTPUT_DIR)

print("\n✅ 完成！HTML 已全部重新生成。")
