# Raven Translate Native 官网

Raven Translate Native 的独立官方介绍网站。沿用原应用仓库中的静态官网，包含产品首页、更新日志、中英文切换及明暗主题。

- 本仓库维护官网，并通过公开 Releases 分发安装包。
- App 源码继续保留在私有应用仓库；安装包同步到本仓库，供官网访客直接下载。

## 目录

- `website/index.html`：产品介绍与下载入口。
- `website/changelog.html`、`website/changelog.js`：更新日志页面与条目。
- `website/i18n.js`：中英文文案。
- `website/main.js`：主题、语言与动效。
- `website/assets/`：品牌图片。
- `.github/workflows/pages.yml`：GitHub Pages 自动部署。

## 本地预览

在仓库根目录执行：

```sh
python3 -m http.server 8000 --directory website
```

然后访问 http://localhost:8000 。无需安装依赖或构建。

## GitHub Pages

在仓库 Settings → Pages 中将 Source 设置为 GitHub Actions。推送到 `main` 且官网或部署配置发生变化时会自动发布，也可手动运行 Deploy website。

部署只上传 `website/`，不会发布仓库文档或 Git 元数据。所有站内资源使用相对路径，可运行于仓库子路径。以 Pages 设置中显示的最终地址为准。

## 维护

当前下载版本记录在 `website/release.json`，安装包由本仓库的[公开 Releases](https://github.com/lhjZY/raven-translate-native-site/releases) 托管，适用于 Apple Silicon（arm64）、macOS 26+。现有包使用临时签名，未做 Apple 公证，网站下载区保留对应说明。

App 仓库的 **Sync website release** 工作流负责同步 DMG、验证公开下载并提交官网版本更新。首次使用需添加 `WEBSITE_RELEASE_TOKEN`，完整步骤见[发布自动化](docs/release-automation.md)。以后先上传 DMG 到 App Release 草稿，再发布即可。

官网使用固定版本的附件直链，预览版不依赖 `/releases/latest`。自动维护：

- `website/index.html` 的导航、首屏和底部下载链接，以及 Release 说明链接。
- `website/changelog.html` 的导航下载链接。
- `website/i18n.js` 及首页回退文案中的版本标识。
- `website/release.json` 的版本、预览标记、附件名和 SHA-256。

系统要求、签名说明和 `website/changelog.js` 的产品更新内容仍需按实际发布情况维护。自动化不会推断安装包已完成 Apple 公证。

验证自动化：`python3 -m unittest discover -s tests -v`。部署前仍需在 GitHub 上配置 Secret 并执行一次手动验证。

导航字标 `website/assets/raven-wordmark.png` 直接复用 App 的 `RavenWordmark.png`，通过 CSS 遮罩适配明暗主题。
