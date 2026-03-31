"""
AnimeFit 每日定时任务
每天自动运行完整流程：生成内容 → 生成图片 → 渲染页面 → 部署
"""

import json
import os
import sys
import time
import schedule
import traceback
from datetime import datetime, date
from pathlib import Path

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 把 generator 目录加入 path
sys.path.insert(0, str(Path(__file__).parent / "generator"))

from content_pipeline import generate_daily_content
from site_builder import render_article, save_content_json, GRADIENTS, EMOJIS
from config import (
    API_KEY, API_BASE, TEXT_MODEL, IMAGE_MODEL, IMAGE_SIZE,
    SITE_URL, OUTPUT_DIR, LANGUAGES
)

try:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
except Exception:
    client = None


# ─────────────────────────────────────────────
# 图片生成
# ─────────────────────────────────────────────
def generate_image(prompt: str, slug: str) -> str | None:
    """调用 AI 生成图片，返回本地路径"""
    if not client:
        print("  ⚠️ OpenAI client 未初始化，跳过图片生成")
        return None
    
    # 检查是否配置了图片生成
    if IMAGE_MODEL is None:
        print("  ℹ️ 图片生成已禁用（IMAGE_MODEL = None）")
        return None

    try:
        print(f"  → 调用 {IMAGE_MODEL} 生成图片...")
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=IMAGE_SIZE,
            quality="hd",
            n=1,
        )
        img_url = resp.data[0].url

        # 下载图片到本地
        import requests
        img_dir = Path(OUTPUT_DIR) / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        img_path = img_dir / f"{slug}.jpg"

        r = requests.get(img_url, timeout=30)
        with open(img_path, "wb") as f:
            f.write(r.content)

        print(f"  ✓ 图片已保存: {img_path}")
        return f"{SITE_URL}/images/{slug}.jpg"

    except Exception as e:
        print(f"  ⚠️ 图片生成失败: {e}")
        return None


# ─────────────────────────────────────────────
# 自动部署
# ─────────────────────────────────────────────
def auto_deploy(output_dir: str, platform: str = "github"):
    """
    自动部署到指定平台
    platform: github | netlify | vercel
    """
    import subprocess
    from pathlib import Path
    
    output_path = Path(output_dir).resolve()
    
    if platform == "github":
        print("\n  📤 推送到 GitHub...")
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.stdout.strip():
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", f"Update content {date.today().isoformat()}"], check=True)
                subprocess.run(["git", "push"], check=True)
                print("  ✅ 代码已推送到 GitHub")
                print("  🌐 GitHub Actions 将自动部署网站")
            else:
                print("  ℹ️ 没有需要提交的更改")
                
        except Exception as e:
            print(f"  ⚠️ Git 推送失败: {e}")
            print("     请确保已配置 Git 远程仓库")
            
    elif platform == "netlify":
        print("\n  📤 部署到 Netlify...")
        try:
            subprocess.run(["netlify", "deploy", "--dir", str(output_path), "--prod"], check=True)
            print("  ✅ Netlify 部署完成")
        except Exception as e:
            print(f"  ⚠️ 部署失败: {e}")
            
    elif platform == "vercel":
        print("\n  📤 部署到 Vercel...")
        try:
            subprocess.run(["vercel", "--prod", str(output_path)], check=True)
            print("  ✅ Vercel 部署完成")
        except Exception as e:
            print(f"  ⚠️ 部署失败: {e}")


# ─────────────────────────────────────────────
# 每日任务主函数
# ─────────────────────────────────────────────
def run_daily_job(
    character: str = None, 
    style: str = None, 
    dry_run: bool = False,
    deploy: bool = False,
    deploy_platform: str = "github"
):
    """
    执行每日完整生成任务
    dry_run=True 时跳过 API 调用，用假数据测试流程
    deploy=True 时自动部署到指定平台
    """
    today = date.today().strftime("%Y.%m.%d")
    log_prefix = f"[{datetime.now().strftime('%H:%M:%S')}]"

    print(f"\n{'='*60}")
    print(f"{log_prefix} 🌸 AnimeFit 每日任务开始 — {today}")
    print(f"{'='*60}\n")

    try:
        # ── Step 1-6: 内容生成 ──
        if dry_run:
            print("⚡ DRY RUN 模式，使用示例数据")
            content = _get_mock_content()
        else:
            content = generate_daily_content(character=character, style=style)

        # 分配随机视觉元素
        char_hash = hash(content["character"])
        content["gradient"] = GRADIENTS[char_hash % len(GRADIENTS)]
        content["emoji"] = EMOJIS[char_hash % len(EMOJIS)]

        # 从 site_builder 导入 slug 函数
        from site_builder import slug_from_character
        slug = slug_from_character(content["character"], content["date"])

        # ── 图片生成 ──
        if not dry_run:
            img_url = generate_image(content["image_prompt"], slug)
            if img_url:
                content["image_url"] = img_url

        # ── 渲染多语言页面 ──
        print("\n渲染页面...")
        for lang in LANGUAGES:
            render_article(content, lang, SITE_URL, OUTPUT_DIR)

        # ── 保存 JSON 数据 ──
        save_content_json(content, OUTPUT_DIR)

        # ── 自动部署 ──
        if deploy and not dry_run:
            auto_deploy(OUTPUT_DIR, deploy_platform)

        print(f"\n{'='*60}")
        print(f"{log_prefix} ✅ 任务完成！")
        print(f"  角色: {content['character']}")
        print(f"  风格: {content['style']}")
        print(f"  标语: {content['tagline']['zh']}")
        print(f"{'='*60}\n")

        return content

    except Exception as e:
        print(f"\n{log_prefix} ❌ 任务失败: {e}")
        traceback.print_exc()
        return None


def _get_mock_content() -> dict:
    """DRY RUN 用的示例数据"""
    return {
        "date": date.today().strftime("%Y.%m.%d"),
        "date_iso": date.today().isoformat(),
        "character": "御坂美琴（《某科学的超电磁炮》）",
        "style": "电系帅气中性风",
        "theme": {"theme_full": "mock theme"},
        "image_prompt": "Misaka Mikoto, anime girl with short brown hair, school uniform with skirt, electric sparks, Tokiwadai school setting, cool androgynous fashion editorial, cyberpunk lighting, highly detailed",
        "tagline": {
            "zh": "「伏特最强的衣品担当」",
            "en": '"The strongest style icon in Academy City"',
            "ja": "「学園都市最強のファッションアイコン」"
        },
        "tags": ["御坂美琴", "超电磁炮", "中性风", "校服", "电系", "常盘台"],
        "description": {
            "zh": "探索御坂美琴的时尚密码，超电磁炮少女如何用中性帅气风格征服整个学园都市。",
            "en": "Discover Misaka Mikoto's fashion DNA—how the Railgun girl conquers Academy City with cool androgynous style.",
            "ja": "御坂美琴のファッションコードを探る——超電磁砲少女がクールなアンドロジナスでどのように学園都市を制覇するか。"
        },
        "article_body": {
            "zh": "<p>御坂美琴，这位学园都市的超能力第三位，她的穿搭哲学简单粗暴：<strong>能打就行，但要好看。</strong></p><h3>校服改造实验</h3><p>作为常盘台中学的学生，她的制服改造堪称教科书级别。</p><blockquote>「真正的力量不需要装饰，但对的颜色会让力量更有说服力。」</blockquote>",
            "en": "<p>Misaka Mikoto, Level 5 #3 of Academy City, her fashion philosophy is simple: <strong>functional, but make it fashion.</strong></p><h3>Uniform Reinvention</h3><p>As a Tokiwadai student, her uniform adaptation is textbook cool.</p><blockquote>\"True power needs no ornament—but the right palette makes power more persuasive.\"</blockquote>",
            "ja": "<p>御坂美琴、学園都市のレベル5第三位、彼女のファッション哲学はシンプル：<strong>機能的に、でもファッショナブルに。</strong></p><h3>制服の再発明</h3><p>常盤台中学の生徒として、彼女の制服アレンジは教科書級のクールさだ。</p><blockquote>「本物の力に装飾は要らない——でも正しいカラーパレットは力をより説得力あるものにする。」</blockquote>"
        },
        "image_url": None,
    }


# ─────────────────────────────────────────────
# 定时调度
# ─────────────────────────────────────────────
def start_scheduler():
    """启动定时任务，每天早上 8:00 自动运行"""
    print("🕐 AnimeFit 定时任务调度器启动")
    print("   每天 08:00 自动生成内容")
    print("   按 Ctrl+C 停止\n")

    # 每天早上 8:00 运行
    schedule.every().day.at("08:00").do(run_daily_job)

    # 测试：每隔5分钟运行一次（调试用，正式部署时注释掉）
    # schedule.every(5).minutes.do(run_daily_job)

    while True:
        schedule.run_pending()
        time.sleep(60)


# ─────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AnimeFit 内容生成器")
    parser.add_argument("--now", action="store_true", help="立即执行一次生成任务")
    parser.add_argument("--dry-run", action="store_true", help="测试模式（不调用 API）")
    parser.add_argument("--character", type=str, help="指定角色名")
    parser.add_argument("--style", type=str, help="指定穿搭风格")
    parser.add_argument("--schedule", action="store_true", help="启动定时调度")
    parser.add_argument("--deploy", action="store_true", help="生成后自动部署")
    parser.add_argument("--platform", default="github", choices=["github", "netlify", "vercel"],
                        help="部署平台 (默认: github)")
    args = parser.parse_args()

    if args.now or args.dry_run:
        run_daily_job(
            character=args.character,
            style=args.style,
            dry_run=args.dry_run,
            deploy=args.deploy,
            deploy_platform=args.platform
        )
    elif args.schedule:
        start_scheduler()
    else:
        # 默认：立即执行一次
        run_daily_job(deploy=args.deploy, deploy_platform=args.platform)
