# Raven Translate Native 官网

Raven Translate Native 的独立官方介绍网站。沿用原应用仓库中的静态官网，包含产品首页、更新日志、中英文切换及明暗主题。

- 应用源码与发行版本：https://github.com/lhjZY/Raven-t
- 本仓库只维护官网，应用源码与安装包仍由应用仓库维护。

## 目录

- `website/index.html`：产品介绍与下载入口。
- `website/changelog.html`、`website/changelog.js`：更新日志页面与条目。
- `website/i18n.js`：中英文文案。
- `website/main.js`：主题、语言、动效与下载配置。
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

发布应用新版本时，同步 `website/changelog.js` 与首页版本信息。目前首页下载入口保持原站的“即将发布”状态，未配置安装包地址。提供正式安装包后，更新 `website/index.html` 中 `#download-link` 的地址及对应双语文案。

本次从 `Raven-t` 的 `website/` 复制，不迁移应用仓库历史；原目录保留，便于核对与回退。确认新官网上线后，再单独清理旧官网和部署任务。
