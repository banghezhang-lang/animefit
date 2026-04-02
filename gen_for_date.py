"""
为 AnimeFit 生成指定日期的文章（强制 patch datetime.date）
用法: python gen_for_date.py --date 2026-03-31 --character 御坂美琴
"""
import sys
import io
import json
import shutil
from pathlib import Path
from datetime import date, datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / "generator"))

# ── 先 patch datetime.date 再 import content_pipeline ──
TARGET_DATE = None  # 由 main 设置

_original_date_class = date

class _PatchedDateMeta(type):
    """让 isinstance() 也能通过"""
    pass

class _PatchedDate(metaclass=_PatchedDateMeta):
    pass

# 关键：把全局 date 替换掉
import datetime as _dt_module

def _get_patched_date():
    class _RealDate(date):
        pass

    _RealDate.today = classmethod(lambda cls: TARGET_DATE)
    return _RealDate

# 直接替换 sys.modules 里的 datetime 类
_dt_module.date = _get_patched_date()

# 也替换 datetime 类
_orig_datetime = _dt_module.datetime

class _PatchedDatetime(_orig_datetime):
    pass

_dt_module.datetime = _PatchedDatetime

# 同时 patch content_pipeline 的 import
import generator.content_pipeline as _cp
_cp.date = _get_patched_date()
_cp.date.today = classmethod(lambda cls: TARGET_DATE)

# 强制重新加载
import importlib
importlib.reload(_cp)

from content_pipeline import generate_daily_content

from site_builder import render_article, render_homepage, save_content_json, slug_from_character, GRADIENTS, EMOJIS
from config import API_KEY, API_BASE, SITE_URL, OUTPUT_DIR, LANGUAGES


def generate_image_sf(prompt: str, slug: str) -> str | None:
    try:
        import requests
        from openai import OpenAI
        API_KEY_SF = 'sk-fwvzzktzkupnvbgedylylqgbjcjdevbcsoncucqtmsemkxcd'
        sf_client = OpenAI(api_key=API_KEY_SF, base_url="https://api.siliconflow.cn/v1")
        img_dir = Path(OUTPUT_DIR) / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        img_path = img_dir / f"{slug}.png"
        resp = sf_client.images.generate(
            model="Qwen/Qwen-Image",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        img_url = resp.data[0].url
        r = requests.get(img_url, timeout=60)
        with open(img_path, "wb") as f:
            f.write(r.content)
        print(f"  ✓ 图片已保存: {img_path.name} ({img_path.stat().st_size / 1024:.1f} KB)")
        return f"{SITE_URL}/images/{slug}.png"
    except Exception as e:
        print(f"  ⚠️ 图片失败: {e}")
        return None


def load_all_content() -> list:
    data_dir = Path(OUTPUT_DIR) / "data"
    all_content = []
    if data_dir.exists():
        for f in sorted(data_dir.glob("*.json")):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    all_content.append(json.load(fp))
            except Exception:
                pass
    return all_content


def run_for_date(target_date_str: str, character: str = None, style: str = None):
    global TARGET_DATE
    parts = target_date_str.split('-')
    TARGET_DATE = date(int(parts[0]), int(parts[1]), int(parts[2]))
    date_str = TARGET_DATE.strftime("%Y.%m.%d")
    iso_str = TARGET_DATE.isoformat()

    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 生成 {date_str} 内容...")
    if character:
        print(f"[指定角色: {character}]")
    print(f"{'='*60}\n")

    # 生成内容
    content = generate_daily_content(character=character, style=style)

    # 强制覆盖日期
    content["date"] = date_str
    content["date_iso"] = iso_str

    print(f"  角色: {content['character']}")
    print(f"  风格: {content['style']}")

    char_hash = hash(content["character"])
    content["gradient"] = GRADIENTS[char_hash % len(GRADIENTS)]
    content["emoji"] = EMOJIS[char_hash % len(EMOJIS)]

    slug = slug_from_character(content["character"], content["date"], content.get("slug_en"))
    print(f"  Slug: {slug}")

    # 图片
    print("\n生成图片...")
    img_url = generate_image_sf(content["image_prompt"], slug)
    content["image_url"] = img_url

    # 渲染文章
    print("\n渲染文章页面...")
    for lang in LANGUAGES:
        render_article(content, lang, SITE_URL, OUTPUT_DIR)
        print(f"  ✓ {lang}")

    # 保存 JSON
    save_content_json(content, OUTPUT_DIR)
    print(f"\n  ✓ JSON 已保存")

    # 重建首页
    print("\n重建首页...")
    all_content = load_all_content()
    all_content.sort(key=lambda x: x.get('date_iso', ''), reverse=True)
    for lang in LANGUAGES:
        render_homepage(all_content, lang, SITE_URL, OUTPUT_DIR)
        print(f"  ✓ {lang}")

    # 根目录重定向
    root_index = Path(OUTPUT_DIR) / "index.html"
    root_index.parent.mkdir(parents=True, exist_ok=True)
    root_index.write_text('<meta http-equiv="refresh" content="0;url=/zh/">', encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"✅ 完成！")
    print(f"  日期: {content['date']}")
    print(f"  角色: {content['character']}")
    print(f"  图片: {content['image_url']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="目标日期，如 2026-03-31")
    parser.add_argument("--character", type=str, default=None)
    parser.add_argument("--style", type=str, default=None)
    args = parser.parse_args()
    run_for_date(args.date, args.character, args.style)
