# AnimeFit 自动部署配置指南

> 手把手教你配置每日自动更新 + 自动部署的网站

---

## 📋 前置准备

1. **GitHub 账号**（免费注册：https://github.com/signup）
2. **OpenAI API Key**（或第三方兼容 API）
3. **Git**（Windows 下载：https://git-scm.com/download/win）

---

## 🚀 快速配置（3 步搞定）

### 第 1 步：创建 GitHub 仓库

1. 登录 GitHub → 点击右上角 `+` → `New repository`
2. 仓库名填 `animefit`（或你喜欢的名字）
3. 选择 `Public`（免费）
4. 勾选 `Add a README file`
5. 点击 `Create repository`

**复制仓库地址**（后面要用）：
```
https://github.com/你的用户名/animefit.git
```

---

### 第 2 步：配置 API Key

编辑 `generator/config.py`：

```python
API_KEY = "sk-你的OpenAI API Key"
API_BASE = "https://api.openai.com/v1"  # 或第三方地址
SITE_URL = "https://你的用户名.github.io/animefit"  # 替换为你的 GitHub Pages 地址
```

---

### 第 3 步：一键初始化

在项目目录打开 PowerShell，运行：

```powershell
# 1. 初始化 Git 仓库
python deploy.py setup --repo https://github.com/你的用户名/animefit.git

# 2. 提交代码
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## ⚙️ 开启 GitHub Actions 自动部署

### 3.1 配置 Secrets（API Key）

1. 打开 GitHub 仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下 Secret：

| 名称 | 值 |
|------|-----|
| `OPENAI_API_KEY` | 你的 OpenAI API Key |
| `OPENAI_API_BASE` | https://api.openai.com/v1（或第三方地址）|

### 3.2 开启 GitHub Pages

1. 仓库页面 → `Settings` → `Pages`
2. `Source` 选择 `GitHub Actions`
3. 保存

---

## ✅ 测试部署

### 方案 A：本地生成 + 推送（推荐首次测试）

```powershell
# 生成今日内容并推送到 GitHub
python daily_job.py --now --deploy
```

等待 1-2 分钟后，访问：
```
https://你的用户名.github.io/animefit/
```

### 方案 B：全自动云端生成（正式使用）

GitHub Actions 已配置为**每天 08:30 UTC（北京时间 16:30）**自动生成内容并部署。

**手动触发测试：**
1. 打开 GitHub 仓库
2. 点击 `Actions` 标签
3. 选择 `Deploy AnimeFit to GitHub Pages`
4. 点击 `Run workflow`

---

## 🔄 部署方式对比

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| **GitHub Actions（推荐）** | 自动运行 | 每天自动生成，无需开电脑 |
| **本地生成 + 推送** | `python daily_job.py --now --deploy` | 想立即看到效果 |
| **Netlify** | `python deploy.py netlify` | 需要更快的全球 CDN |
| **Vercel** | `python deploy.py vercel` | 喜欢 Vercel 的界面 |

---

## 🛠️ 常见问题

### Q: 部署后页面 404？

A: 检查以下几点：
1. GitHub Pages 设置中 Source 是否选择了 `GitHub Actions`
2. Actions 工作流是否成功运行（绿色勾）
3. 等待 2-3 分钟，GitHub Pages 有缓存延迟

### Q: 如何修改每天生成的时间？

A: 编辑 `.github/workflows/deploy.yml`：
```yaml
schedule:
  - cron: '30 8 * * *'  # UTC 时间 08:30 = 北京时间 16:30
```

### Q: 不想用 GitHub Pages，用别的平台？

A: 支持 Netlify 和 Vercel：

```powershell
# Netlify（需先安装 CLI: npm install -g netlify-cli）
python daily_job.py --now --deploy --platform netlify

# Vercel（需先安装 CLI: npm install -g vercel）
python daily_job.py --now --deploy --platform vercel
```

### Q: 生成的图片太大，GitHub 仓库会爆吗？

A: 建议开启 Git LFS（大文件存储）：
```powershell
git lfs install
git lfs track "output/images/*.jpg"
git add .gitattributes
git commit -m "Enable Git LFS for images"
```

---

## 📁 生成的文件结构

```
output/
├── index.html              # 首页（自动更新）
├── zh/
│   └── 2026-03-31-角色名/  # 中文文章页
│       └── index.html
├── en/
│   └── 2026-03-31-角色名/  # 英文文章页
├── ja/
│   └── 2026-03-31-角色名/  # 日文文章页
├── images/
│   └── 2026-03-31-角色名.jpg
└── data/
    └── posts.json          # 所有文章数据
```

---

## 🎉 完成！

配置完成后，你的网站将：

- ✅ **每天自动生成**新的动漫时尚内容
- ✅ **自动部署**到 GitHub Pages
- ✅ **零成本**运行（GitHub Pages 免费）
- ✅ **全球访问**（CDN 加速）

访问你的专属网站：`https://你的用户名.github.io/animefit/`
