# 全球政要与官方动态实时看板

本项目为您提供了一套完整的**零成本、自动更新、自动翻译**的全球政要动态看板方案。支持 **GitHub Pages** 与 **Cloudflare** 双重部署方式。

## 方案一：部署到 GitHub Pages (推荐，最简单)

1. 在 GitHub 上创建一个新的公开仓库（例如命名为 `world-leaders-live`）。
2. 将本仓库中的 `update.py` 和 `.github/workflows/update.yml` 上传到仓库中。
3. 在 GitHub 仓库的 **Settings -> Pages** 中：
   - **Source** 选择 `GitHub Actions`。
4. 在 **Settings -> Actions -> General** 中：
   - 将 **Workflow permissions** 改为 **Read and write permissions**（允许 Action 自动提交更新的网页）。
5. 提交后，GitHub Actions 会每 2 小时自动运行一次，抓取全球政要动态、自动翻译成中文并更新网页！
6. 访问地址：`https://你的用户名.github.io/仓库名/`

## 方案二：部署到 Cloudflare Workers

1. 登录 Cloudflare 创建一个 Worker。
2. 将 `worker.js` 代码复制进去。
3. 在 KV 中创建一个名为 `LEADERS_KV` 的存储空间并绑定。
4. 设置 Cron 触发器（如每小时执行一次）。
