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
from site_builder import render_article, render_homepage, save_content_json, GRADIENTS, EMOJIS
from config import (
    API_KEY, API_BASE, TEXT_MODEL, IMAGE_PROVIDER, IMAGE_SIZE,
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
    """调用 AI 生成图片，返回图片 URL（Pollinations.ai 免费方案）"""
    try:
        from config import IMAGE_PROVIDER

        if IMAGE_PROVIDER == "pollinations":
            # Pollinations.ai：完全免费，无需 API Key
            # 直接通过 URL 生成，返回的 URL 就是图片地址
            from urllib.parse import quote
            encoded_prompt = quote(prompt)
            img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
            print(f"  ✓ Pollinations 图片 URL: {img_url[:80]}...")
            return img_url

        elif IMAGE_PROVIDER == "siliconflow":
            # SiliconFlow 备选方案
            from config import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE, SILICONFLOW_IMAGE_MODEL
            if not SILICONFLOW_API_KEY:
                print("  ⚠️ SiliconFlow API Key 未配置，跳过图片生成")
                return None
            sf_client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url=SILICONFLOW_API_BASE)
            resp = sf_client.images.generate(
                model=SILICONFLOW_IMAGE_MODEL,
                prompt=prompt,
                size=IMAGE_SIZE,
                n=1,
            )
            img_url = resp.data[0].url
            # 下载到本地
            import requests
            img_dir = Path(OUTPUT_DIR) / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            img_path = img_dir / f"{slug}.jpg"
            r = requests.get(img_url, timeout=30)
            with open(img_path, "wb") as f:
                f.write(r.content)
            print(f"  ✓ SiliconFlow 图片已保存: {img_path}")
            return f"{SITE_URL}/images/{slug}.jpg"

        else:
            print("  ℹ️ 图片生成已禁用（IMAGE_PROVIDER = none）")
            return None

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
            try:
                content = generate_daily_content(character=character, style=style)
            except Exception as api_err:
                print(f"  ⚠️ API 调用失败: {api_err}")
                print("  ⚡ 自动降级为 DRY RUN 模式")
                content = _get_mock_content()

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

        # ── 渲染多语言首页 ──
        print("\n渲染首页...")
        all_content = _load_all_content()
        all_content.append(content)
        for lang in LANGUAGES:
            render_homepage(all_content, lang, SITE_URL, OUTPUT_DIR)

        # ── 生成根目录重定向（默认跳转中文首页）──
        root_index = Path(OUTPUT_DIR) / "index.html"
        root_index.parent.mkdir(parents=True, exist_ok=True)
        root_index.write_text(
            '<meta http-equiv="refresh" content="0;url=/zh/">',
            encoding="utf-8"
        )
        print(f"  ✓ 根目录重定向: {root_index}")

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


def _load_all_content() -> list:
    """加载已有的 JSON 内容数据（用于首页聚合展示）"""
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


def _get_mock_content() -> dict:
    """DRY RUN 用的示例数据"""
    return {
        "date": date.today().strftime("%Y.%m.%d"),
        "date_iso": date.today().isoformat(),
        "character": "御坂美琴（《某科学的超电磁炮》）",
        "style": "电系帅气中性风",
        "theme": {"theme_full": "mock theme"},
        "image_prompt": "Misaka Mikoto, anime girl with short spiky brown hair and copper-brown eyes, wearing Tokiwadai white blouse with navy pleated skirt, adding a deconstructed oversized blazer in electric blue, fingerless tactical gloves, coin held between fingers crackling with electricity, standing in Academy City arcade-lit street at dusk, cool androgynous fashion editorial pose, anime-meets-fashion-editorial, highly detailed, fashion magazine editorial, vibrant colors, 4k",
        "tagline": {
            "zh": "「伏特最强的衣品担当」",
            "en": '"The strongest style icon in Academy City"',
            "ja": "「学園都市最強のファッションアイコン」",
            "ar": "\"أيقونة الأناقة الأقوى في مدينة الأكاديمية\"",
            "es": '"La ícona de estilo más fuerte de Academy City"',
            "fr": "\"L'icône de style la plus forte d'Academy City\"",
            "de": '"Das stärkste Stil-Ikon in Academy City"',
            "hi": '"अकादमी सिटी की सबसे शक्तिशाली स्टाइल आइकन"',
        },
        "tags": ["御坂美琴", "超电磁炮", "中性风", "校服", "电系", "常盘台"],
        "description": {
            "zh": "探索御坂美琴的时尚密码，超电磁炮少女如何用中性帅气风格征服整个学园都市。",
            "en": "Discover Misaka Mikoto's fashion DNA—how the Railgun girl conquers Academy City with cool androgynous style.",
            "ja": "御坂美琴のファッションコードを探る——超電磁砲少女がクールなアンドロジナスでどのように学園都市を制覇するか。",
            "ar": "اكتشف رموز أزياء ميساكا ميكونتو — كيف فتاة الريلغان تكتسح مدينة الأكاديمية بأناقة أندروجينية رائعة.",
            "es": "Descubre el código de moda de Misaka Mikoto — cómo la chica Railgun conquista Academy City con estilo andrógino genial.",
            "fr": "Découvrez le code mode de Misaka Mikoto — comment la fille Railgun conquiert Academy City avec un style androgyne cool.",
            "de": "Entdecke Misaka Mikotos Mode-DNA — wie das Railgun-Mädchen Academy City mit coolem androgynem Stil erobert.",
            "hi": "मिसाका मिकोटो का फैशन कोड खोजें — रेलगन लड़की कैसे कूल एंड्रोजिनस स्टाइल से अकादमी सिटी जीतती है।",
        },
        "article_body": {
            "zh": "<p>御坂美琴，这位学园都市的超能力第三位，她的穿搭哲学简单粗暴：<strong>能打就行，但要好看。</strong></p><h3>校服改造实验</h3><p>作为常盘台中学的学生，她的制服改造堪称教科书级别。</p><blockquote>「真正的力量不需要装饰，但对的颜色会让力量更有说服力。」</blockquote>",
            "en": "<p>Misaka Mikoto, Level 5 #3 of Academy City, her fashion philosophy is simple: <strong>functional, but make it fashion.</strong></p><h3>Uniform Reinvention</h3><p>As a Tokiwadai student, her uniform adaptation is textbook cool.</p><blockquote>\"True power needs no ornament—but the right palette makes power more persuasive.\"</blockquote>",
            "ja": "<p>御坂美琴、学園都市のレベル5第三位、彼女のファッション哲学はシンプル：<strong>機能的に、でもファッショナブルに。</strong></p><h3>制服の再発明</h3><p>常盤台中学の生徒として、彼女の制服アレンジは教科書級のクールさだ。</p><blockquote>「本物の力に装飾は要らない——でも正しいカラーパレットは力をより説得力あるものにする。」</blockquote>",
            "ar": "<p>ميساكا ميكونتو، المستوى 5 رقم 3 في مدينة الأكاديمية، فلسفتها في الأزياء بسيطة: <strong>عملية، لكن بشكل أنيق.</strong></p><h3>إعادة اختراع الزي المدرسي</h3><p>كطالبة في توكيواداي، تعديلاتها على الزي المدرسي تُعد مثالاً على البرود.</p><blockquote>\"القوة الحقيقية لا تحتاج زخرفة—لكن الألوان الصحيحة تجعل القوة أكثر إقناعاً.\"</blockquote>",
            "es": "<p>Misaka Mikoto, Nivel 5 #3 de Academy City, su filosofía de moda es simple: <strong>funcional, pero con estilo.</strong></p><h3>Reinvención del Uniforme</h3><p>Como estudiante de Tokiwadai, su adaptación del uniforme es clásicamente genial.</p><blockquote>\"El verdadero poder no necesita adornos—pero la paleta correcta hace el poder más persuasivo.\"</blockquote>",
            "fr": "<p>Misaka Mikoto, Niveau 5 #3 d'Academy City, sa philosophie mode est simple : <strong>fonctionnelle, mais avec style.</strong></p><h3>Reinvention de l'Uniforme</h3><p>En tant qu'etudiante a Tokiwadai, son adaptation de l'uniforme est un classique du cool.</p><blockquote>\"Le vrai pouvoir n'a pas besoin d'ornements — mais la bonne palette rend le pouvoir plus persuasif.\"</blockquote>",
            "de": "<p>Misaka Mikoto, Level 5 #3 von Academy City, ihre Mode-Philosophie ist einfach: <strong>funktional, aber fashionable.</strong></p><h3>Uniform-Neuerfindung</h3><p>Als Tokiwadai-Schulerin ist ihre Uniform-Anpassung lehrbuchmassig cool.</p><blockquote>\"Echte Kraft braucht keinen Schmuck — aber die richtige Palette macht Kraft ueberzeugender.\"</blockquote>",
            "hi": "<p>मिसाका मिकोटो, अकादमी सिटी की लेवल 5 #3, उनका फैशन दर्शन सरल है: <strong>कार्यात्मक, लेकिन स्टाइलिश.</strong></p><h3>यूनिफॉर्म का पुनर्आविष्कार</h3><p>तोकिवादई की छात्रा के रूप में, उनका यूनिफॉर्म अनुकूलन क्लासिक रूप से कूल है।</p><blockquote>\"सच्ची ताकत को सजावट की ज़रूरत नहीं—लेकिन सही पैलेट ताकत को अधिक प्रभावशाली बनाती है।\"</blockquote>",
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
