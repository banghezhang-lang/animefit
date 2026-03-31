@echo off
chcp 65001 >nul
title AnimeFit - 动漫时尚网站生成器

echo ============================================
echo    AnimeFit - 每日动漫时尚内容生成器
echo ============================================
echo.

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装，请先安装 Python 3.9+
    pause
    exit /b
)

REM 安装依赖
echo 检查依赖包...
pip install openai schedule requests -q
echo.

:menu
echo 选择运行模式：
echo   1. 立即生成今日内容（调用 API）
echo   2. 生成并部署到 GitHub Pages
echo   3. 测试模式（不调用 API，验证流程）
echo   4. 启动每日定时调度（每天 08:00 自动运行）
echo   5. 初始化 Git 仓库配置
echo   0. 退出
echo.
set /p choice="请输入选项："

if "%choice%"=="1" (
    echo.
    echo [启动] 生成今日内容...
    python daily_job.py --now
    echo.
    pause
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo [部署] 生成并部署...
    echo.
    echo 选择部署平台：
    echo   1. GitHub Pages
    echo   2. Netlify（推荐，国内更快）
    set /p deploy_choice="平台 (1/2):"
    if "%deploy_choice%"=="2" (
        python daily_job.py --now --deploy --platform netlify
    ) else (
        python daily_job.py --now --deploy --platform github
    )
    echo.
    pause
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo [测试] DRY RUN 模式...
    python daily_job.py --dry-run
    echo.
    pause
    goto menu
) else if "%choice%"=="4" (
    echo.
    echo [调度] 启动定时任务（每天 08:00 运行）...
    echo 按 Ctrl+C 停止调度器
echo.
    python daily_job.py --schedule
) else if "%choice%"=="5" (
    echo.
    echo [配置] 初始化 Git 仓库...
    echo.
    set /p repo_url="请输入 GitHub 仓库地址（如: https://github.com/用户名/animefit.git）:"
    python deploy.py setup --repo %repo_url%
    echo.
    echo 下一步操作：
    echo   1. git add . ^&^& git commit -m "Initial" ^&^& git push
echo   2. 在 GitHub 仓库设置 Secrets（OPENAI_API_KEY）
echo   3. 开启 GitHub Pages（Settings ^-^> Pages ^-^> GitHub Actions）
    echo.
    pause
    goto menu
) else if "%choice%"=="0" (
    echo 再见！
    exit /b
) else (
    echo 无效输入，请重新选择
    goto menu
)
