"""
AnimeFit 本地部署脚本
支持手动推送到 GitHub Pages 或部署到 Netlify/Vercel
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_cmd(cmd: list[str], cwd: str = None, check: bool = True) -> str:
    """运行 shell 命令"""
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if check and result.returncode != 0:
        print(f"  ❌ 命令失败: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def deploy_to_github_pages(output_dir: str, repo_url: str = None):
    """
    部署到 GitHub Pages
    方案：将 output/ 目录推送到 gh-pages 分支
    """
    print("\n🚀 部署到 GitHub Pages...")
    
    output_path = Path(output_dir).resolve()
    if not output_path.exists():
        print(f"❌ 输出目录不存在: {output_path}")
        return False
    
    # 检查 git
    try:
        run_cmd(["git", "--version"])
    except:
        print("❌ 未安装 Git，请先安装: https://git-scm.com/download")
        return False
    
    # 获取仓库信息
    try:
        origin_url = run_cmd(["git", "remote", "get-url", "origin"])
        print(f"  📦 远程仓库: {origin_url}")
    except:
        if not repo_url:
            print("❌ 未配置 Git 远程仓库")
            print("   请先运行: git remote add origin <你的仓库地址>")
            return False
        origin_url = repo_url
        run_cmd(["git", "remote", "add", "origin", repo_url])
    
    # 创建临时目录用于部署
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        deploy_dir = Path(tmpdir) / "deploy"
        
        # 克隆 gh-pages 分支（如果不存在则创建）
        print("\n  📥 准备 gh-pages 分支...")
        try:
            run_cmd([
                "git", "clone", "--branch", "gh-pages",
                "--single-branch", origin_url, str(deploy_dir)
            ], check=False)
        except:
            # 分支不存在，初始化
            run_cmd(["git", "clone", origin_url, str(deploy_dir)])
            os.chdir(deploy_dir)
            run_cmd(["git", "checkout", "--orphan", "gh-pages"])
            run_cmd(["git", "rm", "-rf", "."])
            os.chdir(output_path.parent)
        
        # 清空旧文件并复制新文件
        print("  📝 复制新文件...")
        for item in deploy_dir.iterdir():
            if item.name != '.git':
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        for item in output_path.iterdir():
            dest = deploy_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        
        # 提交并推送
        print("  📤 推送到 GitHub...")
        os.chdir(deploy_dir)
        run_cmd(["git", "add", "."])
        run_cmd(["git", "commit", "-m", "Update site content"], check=False)
        run_cmd(["git", "push", "origin", "gh-pages"])
        
    print("\n✅ 部署完成！")
    print(f"   网站地址: https://<你的用户名>.github.io/<仓库名>/")
    return True


def deploy_to_netlify(output_dir: str, site_id: str = None):
    """
    部署到 Netlify
    需要安装 Netlify CLI: npm install -g netlify-cli
    """
    print("\n🚀 部署到 Netlify...")
    
    # 检查 netlify CLI
    try:
        run_cmd(["netlify", "--version"])
    except:
        print("❌ 未安装 Netlify CLI")
        print("   请运行: npm install -g netlify-cli")
        return False
    
    output_path = Path(output_dir).resolve()
    
    # 部署
    cmd = ["netlify", "deploy", "--dir", str(output_path), "--prod"]
    if site_id:
        cmd.extend(["--site", site_id])
    
    try:
        run_cmd(cmd)
        print("\n✅ Netlify 部署完成！")
        return True
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        return False


def deploy_to_vercel(output_dir: str):
    """
    部署到 Vercel
    需要安装 Vercel CLI: npm install -g vercel
    """
    print("\n🚀 部署到 Vercel...")
    
    # 检查 vercel CLI
    try:
        run_cmd(["vercel", "--version"])
    except:
        print("❌ 未安装 Vercel CLI")
        print("   请运行: npm install -g vercel")
        return False
    
    output_path = Path(output_dir).resolve()
    
    # 部署
    try:
        run_cmd(["vercel", "--prod", str(output_path)])
        print("\n✅ Vercel 部署完成！")
        return True
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        return False


def setup_git_repo(repo_url: str):
    """初始化 Git 仓库并配置远程"""
    print("\n🔧 初始化 Git 仓库...")
    
    # 检查是否已经是 git 仓库
    if Path(".git").exists():
        print("  ✅ 已经是 Git 仓库")
    else:
        run_cmd(["git", "init"])
        print("  ✅ Git 仓库初始化完成")
    
    # 配置远程仓库
    try:
        existing = run_cmd(["git", "remote", "get-url", "origin"])
        print(f"  ✅ 远程仓库已配置: {existing}")
    except:
        run_cmd(["git", "remote", "add", "origin", repo_url])
        print(f"  ✅ 远程仓库已添加: {repo_url}")
    
    # 创建 .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 生成的图片（可选，如果图片太大不想提交到 Git）
# output/images/

# 日志
*.log
"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        print("  ✅ .gitignore 已创建")


def main():
    parser = argparse.ArgumentParser(description="AnimeFit 部署工具")
    parser.add_argument(
        "platform",
        choices=["github", "netlify", "vercel", "setup"],
        help="部署平台"
    )
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="输出目录 (默认: ./output)"
    )
    parser.add_argument(
        "--repo", "-r",
        help="GitHub 仓库地址 (如: https://github.com/用户名/animefit.git)"
    )
    parser.add_argument(
        "--site-id",
        help="Netlify Site ID"
    )
    
    args = parser.parse_args()
    
    if args.platform == "setup":
        if not args.repo:
            print("❌ 请提供仓库地址: --repo https://github.com/用户名/仓库名.git")
            sys.exit(1)
        setup_git_repo(args.repo)
        print("\n✅ 仓库配置完成！")
        print("\n下一步:")
        print("  1. 提交代码: git add . && git commit -m 'Initial commit'")
        print("  2. 推送到 GitHub: git push -u origin main")
        print("  3. 在 GitHub 设置 Pages 源为 gh-pages 分支")
        
    elif args.platform == "github":
        deploy_to_github_pages(args.output, args.repo)
        
    elif args.platform == "netlify":
        deploy_to_netlify(args.output, args.site_id)
        
    elif args.platform == "vercel":
        deploy_to_vercel(args.output)


if __name__ == "__main__":
    main()
