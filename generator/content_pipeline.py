"""
AnimeFit 内容生成流水线
按照 6 个步骤自动生成每日动漫时尚内容
"""

import json
import random
import re
from datetime import date
from openai import OpenAI
try:
    from config import (
        API_KEY, API_BASE, TEXT_MODEL,
        ANIME_CHARACTERS, FASHION_STYLES
    )
except ImportError:
    # 默认配置
    API_KEY = "sk-test"
    API_BASE = "https://api.deepseek.com/v1"
    TEXT_MODEL = "deepseek-chat"
    ANIME_CHARACTERS = ["御坂美琴（《某科学的超电磁炮》）"]
    FASHION_STYLES = ["电系帅气中性风"]


client = OpenAI(api_key=API_KEY, base_url=API_BASE)


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.8) -> str:
    """调用 LLM 生成文本"""
    resp = client.chat.completions.create(
        model=TEXT_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────
# Step 1: 生成主题
# ─────────────────────────────────────────────
def step1_generate_theme(character: str = None, style: str = None) -> dict:
    """
    输入：可选角色名、可选风格
    输出：包含角色、风格、主题描述的 dict
    """
    if not character:
        character = random.choice(ANIME_CHARACTERS)
    if not style:
        style = random.choice(FASHION_STYLES)

    system = "你是一名动漫与时尚双栖创作者，擅长为动漫角色设计时尚穿搭主题。"
    prompt = f"""
请为以下角色设计一个时尚穿搭主题：
- 角色：{character}
- 穿搭风格：{style}

要求：
1. 简述该角色的外形特征和性格气质（2-3句话）
2. 描述这套穿搭的核心搭配逻辑（3-4句话），融合角色特点和时尚风格
3. 输出为 JSON 格式：
{{
  "character": "角色名（带作品名）",
  "style": "穿搭风格",
  "character_desc": "角色特征描述",
  "outfit_desc": "穿搭描述",
  "theme_full": "完整主题内容（角色特征 + 穿搭描述 合并）"
}}
只输出 JSON，不要其他文字。
"""
    result = chat(system, prompt, temperature=0.9)
    # 提取 JSON
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"Step1 JSON 解析失败: {result}")


# ─────────────────────────────────────────────
# Step 2: 生成 AI 绘图 Prompt
# ─────────────────────────────────────────────
def step2_generate_image_prompt(theme: dict) -> str:
    """
    输入：Step1 主题 dict
    输出：英文 AI 绘图 prompt 字符串
    """
    system = "You are an expert AI art director specializing in anime fashion editorial photography. Create concise, precise image prompts."
    prompt = f"""
Based on the following anime character fashion theme, create a single English image generation prompt.

Theme: {theme['theme_full']}
Character: {theme['character']}
Style: {theme['style']}

Requirements:
- English only
- Under 100 words
- Include: character appearance, outfit details, color palette, art style, mood/atmosphere
- Art style should be: anime-meets-fashion-editorial, high quality illustration
- End with technical quality tags like: highly detailed, fashion magazine cover, vibrant colors

Output only the prompt text, nothing else.
"""
    return chat(system, prompt, temperature=0.7)


# ─────────────────────────────────────────────
# Step 3: 提炼一句话核心内容（三语）
# ─────────────────────────────────────────────
def step3_generate_tagline(theme: dict) -> dict:
    """
    输出：{"zh": "...", "en": "...", "ja": "..."}
    """
    system = "你是一名时尚杂志主编，善于提炼一句话金句。"
    prompt = f"""
请根据以下主题，提炼出一句话的核心内容，要求：
- 有文学感，像杂志封面金句
- 分别用中文、英文、日文输出
- 中文不超过20字，英文不超过15词，日文不超过25字

主题：{theme['theme_full']}
角色：{theme['character']}

输出 JSON 格式：
{{"zh": "中文金句", "en": "English tagline", "ja": "日本語タグライン"}}
只输出 JSON。
"""
    result = chat(system, prompt, temperature=0.85)
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"Step3 JSON 解析失败: {result}")


# ─────────────────────────────────────────────
# Step 4: 生成标签
# ─────────────────────────────────────────────
def step4_generate_tags(theme: dict) -> list:
    """
    输出：标签列表，5-10个
    """
    system = "你是一名内容标签专家，善于为文章提取精准标签。"
    prompt = f"""
请根据以下主题内容，提取5-10个标签词组：

主题：{theme['theme_full']}
角色：{theme['character']}
风格：{theme['style']}

规则：
- 选择重点核心词组作为标签
- 去除无意义、不适合做标签的词组
- 相似词只选一个
- 不选纯数字
- 标签用中文（角色名可保留日文/英文原名）
- 输出 JSON 数组：["标签1", "标签2", ...]
只输出 JSON 数组。
"""
    result = chat(system, prompt, temperature=0.5)
    match = re.search(r'\[.*\]', result, re.DOTALL)
    if match:
        tags = json.loads(match.group())
        return tags[:10]  # 最多10个
    raise ValueError(f"Step4 JSON 解析失败: {result}")


# ─────────────────────────────────────────────
# Step 5: 生成 SEO Description（三语）
# ─────────────────────────────────────────────
def step5_generate_description(theme: dict) -> dict:
    """
    输出：{"zh": "...", "en": "...", "ja": "..."}
    """
    system = "你是一名SEO专家，精通网页description优化，同时善于提炼内容精华。"
    prompt = f"""
请根据以下主题，写三语版本的 SEO meta description：

主题：{theme['theme_full']}
角色：{theme['character']}
风格：{theme['style']}

要求：
- 中文：120-150字，自然流畅，包含核心关键词
- 英文：150-160字符，SEO标准长度，包含角色名和风格关键词
- 日文：120-150字，自然，包含核心词

输出 JSON 格式：
{{"zh": "中文description", "en": "English description", "ja": "日本語description"}}
只输出 JSON。
"""
    result = chat(system, prompt, temperature=0.6)
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"Step5 JSON 解析失败: {result}")


# ─────────────────────────────────────────────
# Step 6: 扩写正文文章（三语）
# ─────────────────────────────────────────────
def step6_generate_article(theme: dict) -> dict:
    """
    输出：{"zh": "HTML正文", "en": "HTML正文", "ja": "HTML正文"}
    """
    articles = {}

    prompts = {
        "zh": f"""你是一名兼具动漫文化素养和时尚杂志审美的专栏作家。

请根据以下主题，写一篇可读性强的中文文章：
主题：{theme['theme_full']}
角色：{theme['character']}
穿搭风格：{theme['style']}

要求：
- 字数300-500字
- 以动漫杂志结合时尚杂志的视角写作
- 不脱离原文主题
- 结构：可以有小标题（H3）、引用块（blockquote）增加层次感
- 输出 HTML 格式（只用 <p>, <h3>, <blockquote>, <strong> 标签）
- 语言生动，有时尚感和文化深度
""",
        "en": f"""You are a bilingual columnist with deep knowledge of anime culture and fashion aesthetics.

Write an engaging English article based on this theme:
Theme: {theme['theme_full']}
Character: {theme['character']}
Fashion Style: {theme['style']}

Requirements:
- 300-500 words
- Angle: anime magazine meets fashion editorial
- Stay on theme
- Use H3 subheadings and blockquotes for structure
- Output HTML only (use only <p>, <h3>, <blockquote>, <strong> tags)
- Vivid, stylish, culturally insightful writing
""",
        "ja": f"""あなたはアニメ文化とファッション美学に精通したコラムニストです。

以下のテーマに基づいて、読みやすい日本語記事を書いてください：
テーマ：{theme['theme_full']}
キャラクター：{theme['character']}
ファッションスタイル：{theme['style']}

要件：
- 300〜500文字
- アニメ誌×ファッション誌の視点で執筆
- テーマから外れないこと
- H3見出しとblockquoteで構造を作る
- HTML形式で出力（<p>, <h3>, <blockquote>, <strong>タグのみ使用）
- 生き生きとした、スタイリッシュな文体
"""
    }

    system = "你是一名专业内容创作者。请严格按照要求输出 HTML 格式的文章内容，不要输出任何其他文字。"

    for lang, user_prompt in prompts.items():
        print(f"  → 生成 {lang} 正文...")
        articles[lang] = chat(system, user_prompt, temperature=0.85)

    return articles


# ─────────────────────────────────────────────
# 主流水线：一键生成全部内容
# ─────────────────────────────────────────────
def generate_daily_content(
    character: str = None,
    style: str = None,
    skip_image: bool = False
) -> dict:
    """
    执行完整的6步内容生成流水线
    返回完整的文章数据 dict，可直接用于渲染页面
    """
    today = date.today().strftime("%Y.%m.%d")
    print(f"\n[AnimeFit Generator] 开始生成 {today} 内容...")

    # Step 1
    print("Step 1: 生成主题...")
    theme = step1_generate_theme(character, style)
    print(f"  → 角色: {theme['character']}")
    print(f"  → 风格: {theme['style']}")

    # Step 2
    print("Step 2: 生成绘图 Prompt...")
    image_prompt = step2_generate_image_prompt(theme)
    print(f"  → {image_prompt[:80]}...")

    # Step 3
    print("Step 3: 生成金句标语...")
    tagline = step3_generate_tagline(theme)
    print(f"  → ZH: {tagline['zh']}")

    # Step 4
    print("Step 4: 生成标签...")
    tags = step4_generate_tags(theme)
    print(f"  → {tags}")

    # Step 5
    print("Step 5: 生成 SEO Description...")
    description = step5_generate_description(theme)
    print(f"  → {description['zh'][:50]}...")

    # Step 6
    print("Step 6: 扩写正文文章...")
    article_body = step6_generate_article(theme)

    # 组装结果
    result = {
        "date": today,
        "date_iso": date.today().isoformat(),
        "character": theme["character"],
        "style": theme["style"],
        "theme": theme,
        "image_prompt": image_prompt,
        "tagline": tagline,
        "tags": tags,
        "description": description,
        "article_body": article_body,
        "image_url": None,  # 后续步骤填充
    }

    print(f"\n✅ 内容生成完成！角色: {theme['character']} · 风格: {theme['style']}")
    return result


if __name__ == "__main__":
    # 测试运行
    content = generate_daily_content()
    print("\n── 生成结果预览 ──")
    print(json.dumps({
        "character": content["character"],
        "style": content["style"],
        "tagline_zh": content["tagline"]["zh"],
        "tags": content["tags"],
        "description_zh": content["description"]["zh"][:100],
        "image_prompt": content["image_prompt"][:100],
    }, ensure_ascii=False, indent=2))
