# AnimeFit · 每日动漫时尚网站

每天自动生成一篇动漫女性角色时尚穿搭文章，支持中文/英文/日文三语，包含 AI 配图和 SEO 优化。

## 项目结构

```
anime_fashion_site/
├── index.html              ← 网站首页（可本地预览）
├── daily_job.py            ← 每日任务主程序
├── 启动生成器.bat           ← 一键启动
├── generator/
│   ├── config.py           ← 配置（API Key、角色库、风格库）
│   ├── content_pipeline.py ← 6步内容生成流水线
│   └── site_builder.py     ← 静态 HTML 渲染器
└── output/                 ← 生成的静态网站文件
    ├── zh/                 ← 中文文章页
    ├── en/                 ← 英文文章页
    ├── ja/                 ← 日文文章页
    ├── images/             ← AI 生成图片
    └── data/               ← JSON 数据文件
```

## 快速开始

### 1. 配置 API Key

编辑 `generator/config.py`：

```python
API_KEY = "sk-你的OpenAI API Key"
API_BASE = "https://api.openai.com/v1"  # 或第三方中转地址
```

### 2. 安装依赖

```bash
pip install openai schedule requests
```

### 3. 运行

**测试模式（不消耗 API）：**
```bash
python daily_job.py --dry-run
```

**立即生成今日内容：**
```bash
python daily_job.py --now
```

**指定角色和风格：**
```bash
python daily_job.py --now --character "凉宫春日" --style "Y2K复古校园风"
```

**启动每日定时调度（每天 08:00）：**
```bash
python daily_job.py --schedule
```

**或双击 `启动生成器.bat`**

---

## 内容生成流程（6步）

| 步骤 | 功能 | 输出 |
|------|------|------|
| Step 1 | 生成主题：角色 + 穿搭风格描述 | 主题 JSON |
| Step 2 | 生成 AI 绘图 Prompt（英文） | Prompt 字符串 |
| Step 3 | 提炼一句话金句（三语） | zh/en/ja 标语 |
| Step 4 | 提取文章标签（5-10个） | 标签数组 |
| Step 5 | 生成 SEO Description（三语） | zh/en/ja description |
| Step 6 | 扩写正文文章（三语，300-500字） | zh/en/ja HTML 正文 |

---

## 多语言策略

- **URL 结构**：`/zh/2026-03-31-路易丝/` · `/en/2026-03-31-路易丝/` · `/ja/2026-03-31-路易丝/`
- **hreflang**：自动注入 SEO 多语言标签
- **语言切换**：导航栏一键切换，不刷页面

---

## 自动部署

### 方案 1：GitHub Actions（推荐，全自动）

每天自动生成内容并部署，**无需开电脑**。

```powershell
# 1. 配置 API Key（编辑 generator/config.py）
# 2. 初始化仓库
python deploy.py setup --repo https://github.com/用户名/animefit.git

# 3. 提交代码
git add . && git commit -m "Initial" && git push

# 4. 在 GitHub 设置 Secrets（OPENAI_API_KEY）
# 5. 开启 GitHub Pages（Settings → Pages → GitHub Actions）
```

详见 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

### 方案 2：本地生成 + 手动部署

```powershell
# 生成今日内容
python daily_job.py --now

# 部署到 GitHub Pages
python daily_job.py --now --deploy

# 或部署到 Netlify
python daily_job.py --now --deploy --platform netlify
```

### 部署平台对比

| 平台 | 命令 | 费用 | 特点 |
|------|------|------|------|
| **GitHub Pages** | `--deploy --platform github` | 免费 | 全自动，国内访问尚可 |
| **Netlify** | `--deploy --platform netlify` | 免费 | 全球 CDN，速度快 |
| **Vercel** | `--deploy --platform vercel` | 免费 | 界面美观，功能丰富 |

---

## 角色库

`generator/config.py` 中的 `ANIME_CHARACTERS` 已预置 30 个知名角色，包括：
凉宫春日、路易丝、御坂美琴、中野三玖、辉夜大小姐、雷姆、约尔、春日望等。

可自由添加更多角色。

## 扩展方向

- [ ] 接入 Telegram Bot 推送每日通知
- [ ] 添加 RSS Feed 支持
- [ ] 集成 Cloudflare Images CDN
- [ ] 添加读者评论功能（Giscus）
- [ ] Pinterest 自动发布
