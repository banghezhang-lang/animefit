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
        ANIME_CHARACTERS, FASHION_STYLES,
        LANGUAGES, LANG_INFO
    )
except ImportError:
    # 默认配置
    API_KEY = "sk-test"
    API_BASE = "https://api.deepseek.com/v1"
    TEXT_MODEL = "deepseek-chat"
    ANIME_CHARACTERS = ["御坂美琴（《某科学的超电磁炮》）"]
    FASHION_STYLES = ["电系帅气中性风"]
    LANGUAGES = ["zh", "en", "ja", "ar", "es", "fr", "de", "hi"]
    LANG_INFO = {
        "zh": {"name": "中文", "html_lang": "zh-CN", "text_dir": "ltr"},
        "en": {"name": "English", "html_lang": "en", "text_dir": "ltr"},
        "ja": {"name": "日本語", "html_lang": "ja", "text_dir": "ltr"},
        "ar": {"name": "العربية", "html_lang": "ar", "text_dir": "rtl"},
        "es": {"name": "Español", "html_lang": "es", "text_dir": "ltr"},
        "fr": {"name": "Français", "html_lang": "fr", "text_dir": "ltr"},
        "de": {"name": "Deutsch", "html_lang": "de", "text_dir": "ltr"},
        "hi": {"name": "हिन्दी", "html_lang": "hi", "text_dir": "ltr"},
    }


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
1. 简述该角色的外形特征和性格气质（2-3句话），包含发色、发型、眼睛颜色、体型等具体外貌描述
2. 描述这套穿搭的核心搭配逻辑（3-4句话），要具体说明服装单品、颜色、材质、配饰等可视化细节，融合角色特点和时尚风格
3. 输出为 JSON 格式：
{{
  "character": "角色名（带作品名）",
  "style": "穿搭风格",
  "slug_en": "character-name-in-english-kebab-case",
  "character_desc": "角色外貌特征描述（含发色、眼色等具体视觉细节）",
  "outfit_desc": "穿搭描述（含具体服装单品、颜色、材质、配饰等可视化细节）",
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
    输出：英文 AI 绘图 prompt 字符串（与文章主题强关联）
    """
    system = "You are an expert AI art director specializing in anime fashion editorial photography. Create concise, precise image prompts that visually represent the article's specific theme."
    prompt = f"""
Based on the following anime character fashion theme, create a single English image generation prompt.
The image must visually tell the SAME story as the article — not just show the character, but capture the specific outfit, scene, and mood described in the theme.

Theme: {theme['theme_full']}
Character: {theme['character']}
Style: {theme['style']}
Character description: {theme.get('character_desc', '')}
Outfit description: {theme.get('outfit_desc', '')}

Requirements:
- English only
- Under 120 words
- MUST include: specific outfit items/colors from the outfit_desc, the scene/setting that matches the article theme, character's pose and expression that reflects their personality
- Art style: anime-meets-fashion-editorial, high quality illustration
- The image should look like it could be the cover photo of the article
- End with: highly detailed, fashion magazine editorial, vibrant colors, 4k

Output only the prompt text, nothing else.
"""
    return chat(system, prompt, temperature=0.7)


# ─────────────────────────────────────────────
# Step 2b: 生成5张图片的 Prompt（不同角度/场景）
# ─────────────────────────────────────────────
def step2b_generate_multi_image_prompts(theme: dict, cover_prompt: str) -> list:
    """
    基于主题和封面 prompt，生成5个不同角度/场景的图片 prompt。
    返回列表长度 = 5，每个元素为英文 prompt 字符串。
    第0张是封面（cover_prompt），后4张为不同角度。
    """
    system = "You are an expert AI art director for anime fashion editorials. Create varied image prompts that tell a complete fashion story from multiple angles."
    prompt = f"""
The cover image prompt for this article is already created:
COVER: {cover_prompt}

Character: {theme['character']}
Style: {theme['style']}
Character description: {theme.get('character_desc', '')}
Outfit description: {theme.get('outfit_desc', '')}

Now create 4 MORE image prompts showing DIFFERENT angles/scenes for the same character and outfit.
Each must show the same character, same outfit, but from a different perspective or moment:
1. Close-up portrait: face and upper body, dramatic lighting, showing expression and accessories
2. Full-body shot: complete outfit visible, dynamic pose, showing shoes and full silhouette
3. Action/movement shot: character in motion, outfit in dynamic flow, energetic pose
4. Atmospheric/scene shot: character in background, emphasizing the environment and mood

Requirements for each prompt:
- English only, under 100 words each
- Keep the same character appearance, outfit colors/materials consistent with cover
- Vary composition, pose, and lighting
- End each with: highly detailed, fashion magazine editorial, vibrant colors, 4k

Output ONLY a JSON array of 4 strings (no numbering, no labels):
["prompt1", "prompt2", "prompt3", "prompt4"]
"""
    result = chat(system, prompt, temperature=0.75)
    match = re.search(r'\[.*\]', result, re.DOTALL)
    if match:
        extra_prompts = json.loads(match.group())
        # 封面在最前，共5张
        return [cover_prompt] + extra_prompts[:4]
    # 解析失败降级：5张都用封面 prompt（加角度后缀）
    angles = ["cover shot", "close-up portrait", "full-body shot", "action shot", "atmospheric shot"]
    base = cover_prompt.rstrip(", 4k").rstrip()
    return [f"{base}, {a}, highly detailed, fashion magazine editorial, vibrant colors, 4k" for a in angles]


# ─────────────────────────────────────────────
# Step 3: 提炼一句话核心内容（三语）
# ─────────────────────────────────────────────
def step3_generate_tagline(theme: dict) -> dict:
    """
    输出：{"zh": "...", "en": "...", "ja": "...", "ar": "...", "es": "...", "fr": "...", "de": "...", "hi": "..."}
    """
    system = "你是一名时尚杂志主编，善于提炼一句话金句。精通中文、英文、日文、阿拉伯文、西班牙文、法文、德文、印地文。"
    
    lang_names = {
        "zh": "中文", "en": "英文", "ja": "日文",
        "ar": "阿拉伯文", "es": "西班牙文", "fr": "法文", "de": "德文", "hi": "印地文"
    }
    lang_list = ", ".join(f'{k}({v})' for k, v in lang_names.items())
    
    prompt = f"""
请根据以下主题，提炼出一句话的核心内容，要求：
- 有文学感，像杂志封面金句
- 分别用 {lang_list} 输出
- 每种语言不超过20词
- 阿拉伯文从右到左书写

主题：{theme['theme_full']}
角色：{theme['character']}

输出 JSON 格式：
{{"zh": "中文金句", "en": "English tagline", "ja": "日本語タグライン", "ar": "العربية عبارة", "es": "Spanish tagline", "fr": "Phrase d'accroche française", "de": "Deutsche Schlagzeile", "hi": "हिंदी टैगलाइन"}}
只输出 JSON。
"""
    result = chat(system, prompt, temperature=0.85)
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        taglines = json.loads(match.group())
        # 确保所有语言都有值
        for lang in LANGUAGES:
            if lang not in taglines:
                taglines[lang] = taglines.get("en", "Anime Fashion Inspiration")
        return taglines
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
    输出：8语版本的 SEO meta description
    """
    lang_descs = {
        "zh": "中文：120-150字，自然流畅，包含核心关键词",
        "en": "English: 150-160 characters, SEO standard, include character name and style keywords",
        "ja": "日本語：120-150字、自然、キーワードを含む",
        "ar": "Arabic: 120-150 characters, SEO optimized, right-to-left",
        "es": "Spanish: 150-160 characters, SEO optimized",
        "fr": "French: 150-160 characters, SEO optimized",
        "de": "German: 150-160 characters, SEO optimized",
        "hi": "Hindi: 120-150 characters, SEO optimized",
    }
    lang_list = "\n".join(f"- {v}" for k, v in lang_descs.items())
    
    system = "你是一名SEO专家，精通网页description优化，同时善于提炼内容精华。精通中文、英文、日文、阿拉伯文、西班牙文、法文、德文、印地文。"
    prompt = f"""
请根据以下主题，写 8 语版本的 SEO meta description：

主题：{theme['theme_full']}
角色：{theme['character']}
风格：{theme['style']}

要求：
{lang_list}
- 阿拉伯文从右到左书写
- 每种语言要包含角色名和风格相关关键词

输出 JSON 格式：
{{"zh": "...", "en": "...", "ja": "...", "ar": "...", "es": "...", "fr": "...", "de": "...", "hi": "..."}}
只输出 JSON。
"""
    result = chat(system, prompt, temperature=0.6)
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        descriptions = json.loads(match.group())
        for lang in LANGUAGES:
            if lang not in descriptions:
                descriptions[lang] = descriptions.get("en", "Anime fashion inspiration daily")
        return descriptions
    raise ValueError(f"Step5 JSON 解析失败: {result}")


# ─────────────────────────────────────────────
# Step 6: 扩写正文文章（三语）
# ─────────────────────────────────────────────
def step6_generate_article(theme: dict) -> dict:
    """
    输出：8语版本的 HTML 正文文章
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
        "en": f"""You are a columnist with deep knowledge of anime culture and fashion aesthetics.

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
""",
        "ar": f"""أنت كاتب عمود متخصص في ثقافة الأنمي وعلم الجمال في الأزياء.

اكتب مقالاً جذاباً باللغة العربية بناءً على هذا الموضوع:
الموضوع: {theme['theme_full']}
الشخصية: {theme['character']}
نمط الأزياء: {theme['style']}

المتطلبات:
- 300-500 كلمة
- زاوية: مجلة أنمي تلتقي بمجلة أزياء
- الالتزام بالموضوع
- استخدم عناوين H3 واقتباسات blockquote
- الإخراج بتنسيق HTML فقط (استخدم فقط <p>, <h3>, <blockquote>, <strong>)
- الكتابة من اليمين إلى اليسار، حيوية وأنيقة
""",
        "es": f"""Eres un columnista experto en cultura anime y estética de la moda.

Escribe un artículo atractivo en español basado en este tema:
Tema: {theme['theme_full']}
Personaje: {theme['character']}
Estilo de moda: {theme['style']}

Requisitos:
- 300-500 palabras
- Enfoque: revista anime meets editorial de moda
- Mantente en el tema
- Usa subtítulos H3 y blockquotes para estructura
- Salida en formato HTML (solo <p>, <h3>, <blockquote>, <strong>)
- Escritura vívida, estilizada y culturalmente perspicaz
""",
        "fr": f"""Vous êtes un chroniqueur expert en culture anime et esthétique de la mode.

Rédigez un article captivant en français basé sur ce thème :
Thème : {theme['theme_full']}
Personnage : {theme['character']}
Style vestimentaire : {theme['style']}

Exigences :
- 300-500 mots
- Angle : magazine anime rencontre éditorial de mode
- Restez dans le thème
- Utilisez des sous-titres H3 et des citations en blockquote
- Sortie au format HTML uniquement (<p>, <h3>, <blockquote>, <strong>)
- Écriture vivante, stylée et culturellement perspicace
""",
        "de": f"""Sie sind ein Kolumnist mit tiefem Wissen über Anime-Kultur und Modeästhetik.

Schreiben Sie einen ansprechenden Artikel auf Deutsch basierend auf diesem Thema:
Thema: {theme['theme_full']}
Charakter: {theme['character']}
Modestil: {theme['style']}

Anforderungen:
- 300-500 Wörter
- Perspektive: Anime-Magazin trifft Mode-Editorial
- Bleiben Sie beim Thema
- Verwenden Sie H3-Überschriften und Blockquotes
- Ausgabe nur im HTML-Format (<p>, <h3>, <blockquote>, <strong>)
- Lebendige, stilvolle und kulturell tiefgründige Sprache
""",
        "hi": f"""आप एक कॉलमनिस्ट हैं जो एनीमे संस्कृति और फैशन एस्थेटिक्स में विशेषज्ञ हैं।

इस विषय पर आधारित एक आकर्षक हिंदी लेख लिखें:
विषय: {theme['theme_full']}
पात्र: {theme['character']}
फैशन स्टाइल: {theme['style']}

आवश्यकताएँ:
- 300-500 शब्द
- दृष्टिकोण: एनीमे मैगज़ीन मीट्स फैशन एडिटोरियल
- विषय से न भटकें
- H3 उपशीर्षक और blockquote का उपयोग करें
- HTML फॉर्मेट में आउटपुट (<p>, <h3>, <blockquote>, <strong> टैग्स)
- जीवंत, स्टाइलिश और सांस्कृतिक रूप से गहरा लेखन
"""
    }

    system = "你是一名专业内容创作者。请严格按照要求输出 HTML 格式的文章内容，不要输出任何其他文字。"

    for lang, user_prompt in prompts.items():
        print(f"  → 生成 {lang} 正文...")
        try:
            articles[lang] = chat(system, user_prompt, temperature=0.85)
        except Exception as e:
            print(f"  ⚠️ {lang} 正文生成失败: {e}")
            articles[lang] = articles.get("en", "<p>Content coming soon.</p>")

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

    # Step 2b
    print("Step 2b: 生成5张图片 Prompt（不同角度）...")
    image_prompts = step2b_generate_multi_image_prompts(theme, image_prompt)
    print(f"  → 共 {len(image_prompts)} 个 prompt")

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
        "image_prompt": image_prompt,       # 封面 prompt（向后兼容）
        "image_prompts": image_prompts,     # 5张图片 prompt 列表
        "tagline": tagline,
        "tags": tags,
        "description": description,
        "article_body": article_body,
        "image_url": None,                  # 封面图（向后兼容）
        "image_urls": [],                   # 5张图片 URL 列表（后续步骤填充）
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
