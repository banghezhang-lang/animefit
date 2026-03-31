"""
AnimeFit 网站配置文件
"""

# ── OpenAI / 兼容 API 配置 ──
# DeepSeek 配置（推荐，性价比高，国内访问稳定）
API_KEY = "sk-bd00d21119fd43239a7dc7f3bbb6e42d"  # DeepSeek API Key
API_BASE = "https://api.deepseek.com/v1" # DeepSeek API 地址
TEXT_MODEL = "deepseek-chat"             # DeepSeek 文本模型（V3）

# 图片生成配置（DeepSeek 不支持图片生成，需用其他服务）
# 方案1：使用 SiliconFlow 的免费 FLUX 模型
# IMAGE_API_KEY = "sk-xxxxxxxx"          # SiliconFlow API Key
# IMAGE_API_BASE = "https://api.siliconflow.cn/v1"
# IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

# 方案2：使用本地 Stable Diffusion（需自己搭建）
# IMAGE_API_BASE = "http://localhost:7860"
# IMAGE_MODEL = "local"

# 方案3：暂不生成图片（用占位图）
IMAGE_MODEL = None                       # 设为 None 则跳过图片生成
IMAGE_SIZE = "1024x1024"

# ── 网站配置 ──
SITE_TITLE = "AnimeFit · 每日动漫时尚"
SITE_URL = "https://your-site.com"       # 替换为实际域名
OUTPUT_DIR = "./output"                  # 静态文件输出目录
POSTS_PER_PAGE = 9                       # 首页展示文章数

# ── 内容语言 ──
LANGUAGES = ["zh", "en", "ja"]          # 支持语言列表

# ── 角色主题库（每日从此随机选取或按序轮换）──
ANIME_CHARACTERS = [
    "凉宫春日（《凉宫春日的忧郁》）",
    "路易丝（《零之使魔》）",
    "御坂美琴（《某科学的超电磁炮》）",
    "中野三玖（《五等分的花嫁》）",
    "天使（《天使的心跳》）",
    "小鸟游六花（《中二病也要谈恋爱》）",
    "雪之下雪乃（《我的青春恋爱物语果然有问题》）",
    "桐人（《刀剑神域》爱丽丝）",
    "爱丽丝·祖贝鲁克（《刀剑神域》）",
    "辉夜大小姐（《辉夜大小姐想让我告白》）",
    "四宫芽衣子（《辉夜大小姐》）",
    "雾岛丽奈（《吹响吧！上低音号》）",
    "长门有希（《凉宫春日》）",
    "依玛里（《我的英雄学院》耳郎京香）",
    "八百万百（《我的英雄学院》）",
    "战场ヶ原ひたぎ（《物语》系列）",
    "千与千寻的小千（《千与千寻》）",
    "菜月亚（《Re:从零开始的异世界生活》）",
    "雷姆（《Re:Zero》）",
    "艾米利亚（《Re:Zero》）",
    "托尔（《小林家的龙女仆》）",
    "酸素弱点（《Spy×Family》约尔·福杰）",
    "阿尼亚（《Spy×Family》）",
    "阿窦·弗雷加特（《Spy×Family》约尔）",
    "春日望（《孤独摇滚》）",
    "后藤一里（《孤独摇滚》）",
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
