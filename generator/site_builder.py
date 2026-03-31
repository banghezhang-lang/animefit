"""
AnimeFit 静态网站生成器
将内容数据渲染成 HTML 页面，实现多语言静态化
"""

import json
import os
import shutil
from datetime import date, datetime
from pathlib import Path

# ── HTML 模板引擎（使用内联模板，无需额外依赖）──

ARTICLE_TEMPLATE = '''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:type" content="article">
  <title>{page_title} · AnimeFit</title>
  <link rel="canonical" href="{canonical_url}">
  <link rel="alternate" hreflang="zh" href="{url_zh}">
  <link rel="alternate" hreflang="en" href="{url_en}">
  <link rel="alternate" hreflang="ja" href="{url_ja}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&family=Playfair+Display:ital,wght@0,700;1,400&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --pink: #ff6eb4; --purple: #9b5de5; --cyan: #00f5d4;
      --dark: #0d0d1a; --card-bg: #16162a; --text: #e8e8f0;
      --muted: #888899; --border: rgba(255,255,255,0.08);
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: var(--dark); color: var(--text); font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; }}
    body::before {{
      content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: radial-gradient(ellipse at 20% 20%, rgba(155,93,229,0.12) 0%, transparent 50%),
                  radial-gradient(ellipse at 80% 80%, rgba(255,110,180,0.08) 0%, transparent 50%);
      pointer-events: none; z-index: 0;
    }}
    nav {{
      position: sticky; top: 0; z-index: 100;
      backdrop-filter: blur(20px); background: rgba(13,13,26,0.85);
      border-bottom: 1px solid var(--border);
      padding: 0 5vw; height: 64px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .logo {{
      font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700;
      background: linear-gradient(135deg, var(--pink), var(--purple));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
      text-decoration: none;
    }}
    .lang-links {{ display: flex; gap: 8px; }}
    .lang-link {{
      border: 1px solid var(--border); color: var(--muted); padding: 4px 12px;
      border-radius: 20px; font-size: 0.78rem; text-decoration: none; transition: all 0.2s;
    }}
    .lang-link.active, .lang-link:hover {{ border-color: var(--pink); color: var(--pink); background: rgba(255,110,180,0.08); }}
    main {{ position: relative; z-index: 1; max-width: 760px; margin: 0 auto; padding: 60px 5vw 80px; }}
    .back-link {{
      display: inline-flex; align-items: center; gap: 8px; color: var(--muted);
      text-decoration: none; font-size: 0.85rem; margin-bottom: 40px; transition: color 0.2s;
    }}
    .back-link:hover {{ color: var(--text); }}
    .hero-img {{
      width: 100%; height: 420px;
      background: {img_gradient};
      border-radius: 16px; display: flex; align-items: center; justify-content: center;
      font-size: 8rem; margin-bottom: 40px; position: relative; overflow: hidden;
    }}
    .hero-img::after {{
      content: ''; position: absolute; inset: 0;
      background: radial-gradient(ellipse at center, transparent 40%, rgba(13,13,26,0.5));
    }}
    .hero-img .emoji {{ position: relative; z-index: 1; animation: float 5s ease-in-out infinite; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-12px); }} }}
    .meta {{ display: flex; gap: 12px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }}
    .meta .a-date {{ font-size: 0.75rem; color: var(--cyan); letter-spacing: 1.5px; }}
    .meta .category {{
      background: rgba(155,93,229,0.15); border: 1px solid rgba(155,93,229,0.3);
      color: #c4a0ff; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem;
    }}
    h1 {{ font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 4vw, 2.8rem); line-height: 1.3; margin-bottom: 12px; }}
    .tagline {{ font-size: 1rem; color: var(--purple); font-style: italic; margin-bottom: 20px; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 32px; }}
    .tag {{
      background: rgba(255,255,255,0.06); border: 1px solid var(--border);
      color: var(--muted); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem;
    }}
    .prompt-box {{
      background: rgba(0,245,212,0.05); border: 1px solid rgba(0,245,212,0.2);
      border-radius: 12px; padding: 20px 24px; margin: 28px 0;
    }}
    .prompt-label {{ font-size: 0.7rem; letter-spacing: 2px; color: var(--cyan); margin-bottom: 10px; text-transform: uppercase; }}
    .prompt-text {{ font-family: 'Space Grotesk', monospace; font-size: 0.85rem; color: #a0f0e0; line-height: 1.6; }}
    .article-img {{
      width: 100%; border-radius: 12px; margin: 28px 0; display: block;
      border: 1px solid var(--border);
    }}
    .article-body {{ font-size: 0.95rem; line-height: 1.9; color: #c8c8d8; }}
    .article-body p {{ margin-bottom: 20px; }}
    .article-body h3 {{ font-family: 'Playfair Display', serif; font-size: 1.3rem; color: var(--text); margin: 32px 0 16px; }}
    .article-body blockquote {{ border-left: 3px solid var(--pink); padding-left: 20px; color: var(--muted); font-style: italic; margin: 24px 0; }}
    footer {{ position: relative; z-index: 1; border-top: 1px solid var(--border); padding: 32px 5vw; text-align: center; color: var(--muted); font-size: 0.8rem; }}
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--dark); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(155,93,229,0.4); border-radius: 3px; }}
  </style>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{og_title}",
    "description": "{description}",
    "datePublished": "{date_iso}",
    "author": {{"@type": "Organization", "name": "AnimeFit"}},
    "publisher": {{"@type": "Organization", "name": "AnimeFit", "logo": {{"@type": "ImageObject", "url": "{site_url}/logo.png"}}}},
    "image": "{image_url}"
  }}
  </script>
</head>
<body>
<nav>
  <a class="logo" href="/{lang}/">AnimeFit</a>
  <div class="lang-links">
    <a class="lang-link {zh_active}" href="{url_zh}">中文</a>
    <a class="lang-link {en_active}" href="{url_en}">EN</a>
    <a class="lang-link {ja_active}" href="{url_ja}">日本語</a>
  </div>
</nav>
<main>
  <a class="back-link" href="/{lang}/">{back_text}</a>
  <div class="hero-img" style="background: {img_gradient}">
    <span class="emoji">{emoji}</span>
  </div>
  <div class="meta">
    <span class="a-date">{date_display}</span>
    <span class="category">ANIME FASHION</span>
  </div>
  <h1>{title}</h1>
  <p class="tagline">{tagline}</p>
  <div class="tags">{tags_html}</div>
  <div class="prompt-box">
    <div class="prompt-label">✦ AI Image Prompt</div>
    <div class="prompt-text">{image_prompt}</div>
  </div>
  {image_html}
  <div class="article-body">
    {article_body}
  </div>
</main>
<footer>
  <p style="font-family:'Playfair Display',serif; font-size:1.1rem; margin-bottom:8px; background:linear-gradient(135deg,#ff6eb4,#9b5de5); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">AnimeFit</p>
  <p>{footer_text}</p>
  <p style="margin-top:10px; opacity:0.4; font-size:0.72rem;">© {year} AnimeFit · Powered by AI</p>
</footer>
</body>
</html>'''

# 语言相关文本
LANG_TEXTS = {
    "zh": {
        "back": "← 返回首页",
        "footer": "每日自动生成 · AI 驱动内容 · 多语言发布",
        "html_lang": "zh-CN",
    },
    "en": {
        "back": "← Back to Home",
        "footer": "Auto-generated daily · AI-powered content · Multilingual",
        "html_lang": "en",
    },
    "ja": {
        "back": "← ホームへ戻る",
        "footer": "毎日自動生成 · AIコンテンツ · 多言語対応",
        "html_lang": "ja",
    }
}

# 随机颜色渐变（根据角色特色选择）
GRADIENTS = [
    "linear-gradient(135deg, #2d0a3e, #4a1175, #0d2040)",
    "linear-gradient(135deg, #0d1a3a, #0a2a5e, #1a0040)",
    "linear-gradient(135deg, #0a2a1e, #0d3d28, #1a3a0a)",
    "linear-gradient(135deg, #3a0a0a, #5e0a1a, #2d0040)",
    "linear-gradient(135deg, #1a1a0a, #3d3a0d, #2a1a40)",
    "linear-gradient(135deg, #0a2a3a, #0d3d4a, #1a0a40)",
]

EMOJIS = ["🌸", "⚡", "🎀", "🍀", "✨", "🌙", "🔮", "💫", "🦋", "🌺"]


def slug_from_character(character: str, date_str: str) -> str:
    """生成 URL slug"""
    import re
    # 提取括号前的名字
    name = re.sub(r'[（(《》）)、，。,.·\s]', '-', character)
    name = re.sub(r'-+', '-', name).strip('-').lower()
    date_clean = date_str.replace('.', '-')
    return f"{date_clean}-{name[:30]}"


def render_article(content: dict, lang: str, site_url: str, output_dir: str):
    """渲染单个语言版本的文章页面"""
    slug = slug_from_character(content["character"], content["date"])
    
    url_zh = f"{site_url}/zh/{slug}/"
    url_en = f"{site_url}/en/{slug}/"
    url_ja = f"{site_url}/ja/{slug}/"
    
    texts = LANG_TEXTS[lang]
    
    # 组装 tags HTML
    tags_html = "".join(f'<span class="tag">#{t}</span>' for t in content["tags"])
    
    # 处理图片
    image_url = content.get("image_url") or f"{site_url}/images/{slug}.jpg"
    image_html = ""
    if content.get("image_url"):
        image_html = f'<img class="article-img" src="{content["image_url"]}" alt="{content["character"]}" loading="lazy">'
    
    gradient = content.get("gradient", GRADIENTS[hash(content["character"]) % len(GRADIENTS)])
    emoji = content.get("emoji", EMOJIS[hash(content["character"]) % len(EMOJIS)])
    
    html = ARTICLE_TEMPLATE.format(
        html_lang=texts["html_lang"],
        description=content["description"][lang],
        og_title=f"{content['character']} · {content['style']}",
        image_url=image_url,
        page_title=f"{content['character']} · {content['style']}",
        canonical_url=f"{site_url}/{lang}/{slug}/",
        url_zh=url_zh, url_en=url_en, url_ja=url_ja,
        site_url=site_url, date_iso=content["date_iso"],
        lang=lang,
        zh_active="active" if lang == "zh" else "",
        en_active="active" if lang == "en" else "",
        ja_active="active" if lang == "ja" else "",
        back_text=texts["back"],
        img_gradient=gradient,
        emoji=emoji,
        date_display=content["date"],
        title=content["character"] + " · " + content["style"],
        tagline=content["tagline"][lang],
        tags_html=tags_html,
        image_prompt=content["image_prompt"],
        image_html=image_html,
        article_body=content["article_body"][lang],
        footer_text=texts["footer"],
        year=datetime.now().year,
    )
    
    # 写入文件
    out_path = Path(output_dir) / lang / slug / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  ✓ 输出: {out_path}")
    return slug


def render_homepage(all_content: list, lang: str, site_url: str, output_dir: str):
    """渲染某语言的首页"""
    texts = LANG_TEXTS[lang]
    lang_titles = {"zh": "每日动漫时尚", "en": "Daily Anime Fashion", "ja": "毎日アニメファッション"}
    lang_catchphrases = {
        "zh": "AI 驱动的动漫角色穿搭灵感，每日更新",
        "en": "AI-powered anime character fashion inspiration, updated daily",
        "ja": "AI搭えのアニメキャラクターファッション、毎日更新"
    }
    lang_readmores = {"zh": "阅读全文", "en": "Read More", "ja": "続きを読む"}

    # 组装文章卡片
    cards = ""
    for c in reversed(all_content[-20:]):  # 最新 20 篇
        slug = slug_from_character(c["character"], c["date"])
        gradient = c.get("gradient", GRADIENTS[hash(c["character"]) % len(GRADIENTS)])
        emoji = c.get("emoji", EMOJIS[hash(c["character"]) % len(EMOJIS)])
        cards += f'''
    <a class="card" href="/{lang}/{slug}/">
      <div class="card-img" style="background:{gradient}"><span class="card-emoji">{emoji}</span></div>
      <div class="card-body">
        <div class="card-date">{c["date"]}</div>
        <div class="card-title">{c["character"]}</div>
        <div class="card-style">{c["style"]}</div>
        <div class="card-tagline">{c["tagline"][lang]}</div>
      </div>
    </a>'''

    html = f'''<!DOCTYPE html>
<html lang="{texts["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{lang_catchphrases[lang]}">
  <title>{lang_titles[lang]} · AnimeFit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&family=Playfair+Display:ital,wght@0,700;1,400&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --pink:#ff6eb4;--purple:#9b5de5;--cyan:#00f5d4;--dark:#0d0d1a;--card-bg:#16162a;--text:#e8e8f0;--muted:#888899;--border:rgba(255,255,255,0.08); }}
    * {{ margin:0;padding:0;box-sizing:border-box; }}
    body {{ background:var(--dark);color:var(--text);font-family:'Space Grotesk','Noto Sans SC',sans-serif; }}
    body::before {{ content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 20% 20%,rgba(155,93,229,0.12) 0%,transparent 50%),radial-gradient(ellipse at 80% 80%,rgba(255,110,180,0.08) 0%,transparent 50%);pointer-events:none;z-index:0; }}
    nav {{ position:sticky;top:0;z-index:100;backdrop-filter:blur(20px);background:rgba(13,13,26,0.85);border-bottom:1px solid var(--border);padding:0 5vw;height:64px;display:flex;align-items:center;justify-content:space-between; }}
    .logo {{ font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,var(--pink),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none; }}
    .lang-links {{ display:flex;gap:8px; }}
    .lang-link {{ border:1px solid var(--border);color:var(--muted);padding:4px 12px;border-radius:20px;font-size:0.78rem;text-decoration:none;transition:all 0.2s; }}
    .lang-link.active,.lang-link:hover {{ border-color:var(--pink);color:var(--pink);background:rgba(255,110,180,0.08); }}
    .hero {{ position:relative;z-index:1;text-align:center;padding:80px 5vw 40px; }}
    .hero h1 {{ font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.5rem);background:linear-gradient(135deg,var(--pink),var(--purple),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:12px; }}
    .hero p {{ color:var(--muted);font-size:1.05rem;max-width:500px;margin:0 auto; }}
    .grid {{ position:relative;z-index:1;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;max-width:1100px;margin:40px auto;padding:0 5vw 80px; }}
    .card {{ background:var(--card-bg);border:1px solid var(--border);border-radius:16px;overflow:hidden;text-decoration:none;color:var(--text);transition:transform 0.3s,box-shadow 0.3s; }}
    .card:hover {{ transform:translateY(-4px);box-shadow:0 12px 40px rgba(155,93,229,0.15); }}
    .card-img {{ height:200px;display:flex;align-items:center;justify-content:center;font-size:4rem; }}
    .card-body {{ padding:20px; }}
    .card-date {{ font-size:0.72rem;color:var(--cyan);letter-spacing:1.5px;margin-bottom:6px; }}
    .card-title {{ font-size:1.05rem;font-weight:700;margin-bottom:4px; }}
    .card-style {{ font-size:0.8rem;color:var(--purple);margin-bottom:8px; }}
    .card-tagline {{ font-size:0.82rem;color:var(--muted);line-height:1.5; }}
    .empty {{ position:relative;z-index:1;text-align:center;padding:80px 5vw;color:var(--muted); }}
    footer {{ position:relative;z-index:1;border-top:1px solid var(--border);padding:32px 5vw;text-align:center;color:var(--muted);font-size:0.8rem; }}
  </style>
</head>
<body>
<nav>
  <a class="logo" href="/">AnimeFit</a>
  <div class="lang-links">
    <a class="lang-link {"active" if lang=="zh" else ""}" href="/zh/">中文</a>
    <a class="lang-link {"active" if lang=="en" else ""}" href="/en/">EN</a>
    <a class="lang-link {"active" if lang=="ja" else ""}" href="/ja/">日本語</a>
  </div>
</nav>
<div class="hero">
  <h1>AnimeFit</h1>
  <p>{lang_catchphrases[lang]}</p>
</div>
{"<div class='grid'>" + cards + "</div>" if all_content else "<div class='empty'><p>🚧 Coming soon...</p></div>"}
<footer>
  <p style="font-family:'Playfair Display',serif;font-size:1.1rem;margin-bottom:8px;background:linear-gradient(135deg,#ff6eb4,#9b5de5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">AnimeFit</p>
  <p>{texts["footer"]}</p>
  <p style="margin-top:10px;opacity:0.4;font-size:0.72rem;">© {datetime.now().year} AnimeFit · Powered by AI</p>
</footer>
</body>
</html>'''

    out_path = Path(output_dir) / lang / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  ✓ 首页输出: {out_path}")


def save_content_json(content: dict, output_dir: str):
    """保存内容数据到 JSON（供前端动态加载或备份）"""
    data_dir = Path(output_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    slug = slug_from_character(content["character"], content["date"])
    json_path = data_dir / f"{slug}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON 数据: {json_path}")
