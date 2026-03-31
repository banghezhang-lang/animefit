# AnimeFit Netlify 部署指南

> Netlify 国内访问速度比 GitHub Pages 快 3-5 倍，推荐！

---

## 🚀 快速配置（5 分钟搞定）

### 第 1 步：注册 Netlify

1. 访问 https://www.netlify.com/
2. 点击 `Sign up` → 选择 `GitHub` 登录（推荐）
3. 授权 Netlify 访问你的 GitHub 仓库

---

### 第 2 步：创建站点

**方式 A：通过 Git 部署（推荐，全自动）**

1. Netlify 控制台 → `Add new site` → `Import an existing project`
2. 选择 `GitHub` → 授权 → 选择你的 `animefit` 仓库
3. 构建设置：
   - **Build command**: `python daily_job.py --now`
   - **Publish directory**: `output`
4. 点击 `Deploy site`

**方式 B：手动部署（测试用）**

```powershell
# 1. 安装 Netlify CLI
npm install -g netlify-cli

# 2. 登录
netlify login

# 3. 初始化站点
netlify init

# 4. 部署
python daily_job.py --now
netlify deploy --dir=output --prod
```

---

### 第 3 步：配置环境变量

在 Netlify 控制台：
1. 进入你的站点 → `Site settings` → `Environment variables`
2. 添加以下变量：

| 变量名 | 值 |
|--------|-----|
| `OPENAI_API_KEY` | 你的 OpenAI API Key |
| `OPENAI_API_BASE` | https://api.openai.com/v1 |

---

### 第 4 步：配置自动部署（GitHub Actions）

**获取 Netlify 凭证：**

1. **Personal Access Token**：
   - Netlify 控制台 → `User settings` → `Applications` → `Personal access tokens`
   - 点击 `New access token`，复制 Token

2. **Site ID**：
   - 站点 `Site settings` → `General` → `Site details`
   - 复制 `Site ID`

**在 GitHub 仓库配置 Secrets：**

1. 打开 GitHub 仓库 → `Settings` → `Secrets and variables` → `Actions`
2. 添加以下 Secrets：

| 名称 | 值 |
|------|-----|
| `NETLIFY_AUTH_TOKEN` | 刚才复制的 Personal Access Token |
| `NETLIFY_SITE_ID` | 刚才复制的 Site ID |
| `OPENAI_API_KEY` | 你的 OpenAI API Key |
| `OPENAI_API_BASE` | https://api.openai.com/v1 |

---

### 第 5 步：启用工作流

1. GitHub 仓库 → `Actions` 标签
2. 点击 `Deploy AnimeFit to Netlify`
3. 点击 `Enable workflow`
4. 点击 `Run workflow` 测试

---

## 🔄 部署方式对比

| 方式 | 命令/操作 | 特点 |
|------|-----------|------|
| **GitHub Actions + Netlify** | 自动运行 | 全自动，每天定时生成，无需开电脑 |
| **Netlify Git 集成** | 推送到 GitHub 自动部署 | 代码更新时自动部署 |
| **本地 CLI 部署** | `netlify deploy --prod` | 即时部署，适合测试 |

---

## 🌐 绑定自定义域名（可选）

1. Netlify 控制台 → `Domain settings`
2. 点击 `Add custom domain`
3. 输入你的域名（如 `animefit.yourdomain.com`）
4. 按提示配置 DNS 解析

---

## 🛠️ 常见问题

### Q: 部署失败，提示 "Build command failed"？

A: 检查以下几点：
1. 环境变量 `OPENAI_API_KEY` 是否配置
2. Python 版本是否为 3.9+
3. 查看 Netlify 部署日志获取详细错误

### Q: 如何查看部署日志？

A: 
- **Netlify 控制台**: 站点 → `Deploys` → 点击具体部署查看日志
- **GitHub Actions**: 仓库 → `Actions` → 点击工作流运行记录

### Q: 国内访问还是慢？

A: 开启 Netlify Edge Network：
1. 站点 → `Site settings` → `Build & deploy` → `Edge handlers`
2. 或者考虑使用 **Cloudflare Pages**（国内更快）

### Q: 图片加载慢？

A: 已配置 `netlify.toml` 图片缓存一年：
```toml
[[headers]]
  for = "/images/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

---

## 📊 Netlify vs GitHub Pages 对比

| 特性 | Netlify | GitHub Pages |
|------|---------|--------------|
| **国内速度** | ⭐⭐⭐⭐ 快 | ⭐⭐ 较慢 |
| **全球 CDN** | ✅ 有 | ⚠️ 有限 |
| **自动 HTTPS** | ✅ 有 | ✅ 有 |
| **自定义域名** | ✅ 免费 | ✅ 免费 |
| **构建时间** | 300 分钟/月 免费 | 2000 分钟/月 |
| **带宽** | 100GB/月 免费 | 100GB/月 |

---

## ✅ 完成！

配置完成后，你的网站将：

- ✅ **全球 CDN 加速**，国内访问飞快
- ✅ **每天自动生成**新内容
- ✅ **自动 HTTPS**，安全可靠
- ✅ **零成本**运行（免费额度足够）

访问你的站点：`https://你的站点名.netlify.app/`
