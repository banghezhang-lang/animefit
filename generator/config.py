"""
AnimeFit 网站配置文件
"""

# ── OpenAI / 兼容 API 配置 ──
# DeepSeek 配置（推荐，性价比高，国内访问稳定）
API_KEY = "sk-bd00d21119fd43239a7dc7f3bbb6e42d"  # DeepSeek API Key
API_BASE = "https://api.deepseek.com/v1"  # DeepSeek API 地址
TEXT_MODEL = "deepseek-chat"  # DeepSeek 文本模型（V3）

# ── 图片生成配置 ──
# SiliconFlow 方案（国内可访问，注册送免费额度 https://cloud.siliconflow.cn）
IMAGE_PROVIDER = "siliconflow"  # "pollinations" | "siliconflow" | "none"
POLLINATIONS_MODEL = "flux"  # flux | turbo

# SiliconFlow 配置
SILICONFLOW_API_KEY = "sk-fwvzzktzkupnvbgedylylqgbjcjdevbcsoncucqtmsemkxcd"
SILICONFLOW_API_BASE = "https://api.siliconflow.cn/v1"
SILICONFLOW_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

IMAGE_SIZE = "1024x1024"

# ── 网站配置 ──
SITE_TITLE = "AnimeFit · 每日动漫时尚"
SITE_URL = "https://jolly-puffpuff-cb278b.netlify.app"  # 实际域名
OUTPUT_DIR = "./output"  # 静态文件输出目录
POSTS_PER_PAGE = 9  # 首页展示文章数

# ── 内容语言（8种）──
LANGUAGES = ["zh", "en", "ja", "ar", "es", "fr", "de", "hi"]

# 语言名称和元信息
LANG_INFO = {
    "zh": {"name": "中文", "name_native": "中文", "html_lang": "zh-CN", "flag": "🇨🇳", "text_dir": "ltr"},
    "en": {"name": "English", "name_native": "English", "html_lang": "en", "flag": "🇺🇸", "text_dir": "ltr"},
    "ja": {"name": "日本語", "name_native": "日本語", "html_lang": "ja", "flag": "🇯🇵", "text_dir": "ltr"},
    "ar": {"name": "العربية", "name_native": "العربية", "html_lang": "ar", "flag": "🇸🇦", "text_dir": "rtl"},
    "es": {"name": "Español", "name_native": "Español", "html_lang": "es", "flag": "🇪🇸", "text_dir": "ltr"},
    "fr": {"name": "Français", "name_native": "Français", "html_lang": "fr", "flag": "🇫🇷", "text_dir": "ltr"},
    "de": {"name": "Deutsch", "name_native": "Deutsch", "html_lang": "de", "flag": "🇩🇪", "text_dir": "ltr"},
    "hi": {"name": "हिन्दी", "name_native": "हिन्दी", "html_lang": "hi", "flag": "🇮🇳", "text_dir": "ltr"},
}

# ── 角色主题库（每日从此随机选取或按序轮换）──
ANIME_CHARACTERS = [
    "凉宫春日（《凉宫春日的忧郁》）",
    "路易丝（《零之使魔》）",
    "御坂美琴（《某科学的超电磁炮》）",
    "中野三玖（《五等分的花嫁》）",
    "天使（《天使的心跳》）",
    "小鸟游六花（《中二病也要谈恋爱》）",
    "雪之下雪乃（《我的青春恋爱物语果然有问题》）",
    "桐人（《刀剑神域》）",
    "爱丽丝·祖贝鲁克（《刀剑神域》）",
    "辉夜大小姐（《辉夜大小姐想让我告白》）",
    "四宫芽衣子（《辉夜大小姐》）",
    "雾岛丽奈（《吹响吧！上低音号》）",
    "长门有希（《凉宫春日》）",
    "八百万百（《我的英雄学院》）",
    "战场ヶ原ひたぎ（《物语》系列）",
    "千与千寻的小千（《千与千寻》）",
    "雷姆（《Re:Zero》）",
    "艾米利亚（《Re:Zero》）",
    "托尔（《小林家的龙女仆》）",
    "约尔·福杰（《Spy×Family》）",
    "阿尼亚（《Spy×Family》）",
    "后藤一里（《孤独摇滚》）",
    "春日望（《孤独摇滚》）",
    "星野爱（《我推的孩子》）",
    "有马加奈（《我推的孩子》）",
    "虎杖祢豆子（《鬼灭之刃》）",
    "甘露寺蜜璃（《鬼灭之刃》）",
]

# ── 穿搭风格库（随机搭配主题）──
FASHION_STYLES = [
    "甜辣风（Sweet Spicy）",
    "Y2K复古校园风",
    "暗黑学院风（Dark Academia）",
    "仙女核（Fairycore）",
    "赛博朋克街头风",
    "莫兰迪系简约风",
    "法式优雅风",
    "Cottagecore田园风",
    "Grunge摇滚少女风",
    "和洋折衷风",
    "商务辣妹（Office Siren）",
    "芭比粉浪漫风",
    "中性帅气风（Androgynous）",
    "Vintage复古古着风",
    "户外机能风（Gorpcore）",
    "Coquette蝴蝶结少女风",
    "极简主义（Quiet Luxury）",
    "日系病娇少女风",
    "西装改造混搭风",
    "街头潮牌（Streetwear）",
]
