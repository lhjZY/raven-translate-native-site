# App Release → 公开下载 → 官网更新

App 仓库 `lhjZY/Raven-t` 保持私有；公开仓库 `lhjZY/raven-translate-native-site` 分发 DMG。App 中的 **Sync website release** 工作流在发布 Release 时运行，也可手动指定已发布的标签重跑。

## 一次性配置令牌

1. 打开 <https://github.com/settings/personal-access-tokens/new>，创建 **Fine-grained personal access token**。
2. Token name 填 `raven-website-release`，Resource owner 选 `lhjZY`，设置有效期（例如 90 天，过期前更换）。
3. Repository access 选 **Only select repositories**，只勾选 `raven-translate-native-site`。
4. Repository permissions 只增加 **Contents: Read and write**。Metadata 的只读权限由 GitHub 自动提供。不需要 App 仓库访问权限，也不需要 Workflows、Actions、Administration 权限。
5. 生成并复制令牌，打开 App 仓库的 <https://github.com/lhjZY/Raven-t/settings/secrets/actions>。
6. 点击 **New repository secret**，Name 必须是 `WEBSITE_RELEASE_TOKEN`，Secret 填令牌，保存。

令牌只放在 App 仓库 Actions Secret，不写入代码，不发送到聊天。App 自身附件通过只读的 `GITHUB_TOKEN` 读取。令牌到期后创建同权限的新令牌，并更新同名 Secret。

## 第一次验证

打开 <https://github.com/lhjZY/Raven-t/actions/workflows/sync-website-release.yml> → **Run workflow** → 分支 `main` → tag 输入 `v0.2.2` → Run workflow。

已有同名附件会先下载比对；内容一致时不会重复上传。当前官网已经是 0.2.2，第一次验证通常不产生新提交。查看任务日志中的 `Verified public release`，确认任务成功。未来版本有变更时，官网仓库还会出现 `Update website download for v…` 提交和 **Deploy website** 部署任务。

## 以后发布

1. 在 App 仓库创建 Release 草稿，标签使用 `v0.2.3` 或 `v0.3.0-beta.1` 等 SemVer 格式。
2. **先上传完整 DMG，再点击 Publish release**。文件名必须与标签一致：`Raven-Translate-0.2.3-arm64.dmg`；带后缀标签则为 `Raven-Translate-0.3.0-beta.1-arm64.dmg`。
3. 预览版本勾选 **Pre-release**；带预发布后缀的标签必须勾选。无后缀标签也支持预览标记，例如当前的 `v0.2.2`。
4. 自动化读取源附件，校验大小及可用的 GitHub SHA-256，在官网仓库创建草稿、上传和校验附件，然后公开发布。
5. 无需登录地下载公开附件并再次校验成功后，才更新四个下载按钮、Release 说明链接、中英文版本标识和 `website/release.json`，提交推送触发现有 Pages 部署。

源 Release 的私有正文和 App 源码不会复制。公开说明自动生成安装包名称、系统要求和 SHA-256；产品更新日志仍由维护者编写，不自动生成或翻译。

## 约束与失败处理

- 当前分发契约是 **arm64 / macOS 26+**；自动化不构建、不重新签名、不执行公证。增加 Intel / Universal 包、调整最低系统版本或完成公证时，需一起修改同步脚本和官网安装提示，不能只换 DMG。
- 先发布、后上传 DMG 时首次任务会失败；上传完成后手动重跑。不会无期限等待或发布空附件。
- 同标签、同内容可重跑；同标签、不同内容拒绝覆盖，请发布新版本。已发布附件不会被自动删除。
- 老版本可以补同步，但不会覆盖官网较新的入口；同版本预览转正式可更新标记，正式版不会降回预览。更高版本的预览版也会成为官网入口，与当前预览分发策略一致。
- 上传或公开下载失败时，官网保持原版本；任务有 15 分钟上限，下载重试有次数限制。新创建的草稿可能保留，重跑会继续校验、完成。
- 官网页面结构变化导致替换数量不符时停止更新，防止只改一部分链接。
- 不强制推送。同步期间有人修改官网时，推送可能失败；重跑即可基于最新主分支重新检查。
- GitHub 同一并发组最多保留一个运行中和一个等待任务；短时间连续发布多个版本时，较早的等待任务可能被替换，可手动补同步该版本。
- 如果以后使用 App 的 `GITHUB_TOKEN` 在 Actions 中创建 Release，该事件不会再自动触发本工作流；构建流程须在上传完毕后显式调用 `workflow_dispatch`，或把同步作为后续步骤。人工发布不受影响。
- 官网规则若禁止令牌直接推送 `main`，需调整为允许该发布流程，或改为 PR 流程；不要通过强制推送绕过规则。

## 验证与回滚

本地运行 `python3 -m unittest discover -s tests -v`。测试覆盖版本比较、重复运行、同版本冲突、缺附件、上传后的公开访问失败、私有正文隔离，以及中英文和全部静态链接同步。模拟测试不等于真实跨仓库认证已验证；配置 Secret 后执行上面的手动验证。

停用：在 App Actions 页面禁用 **Sync website release**。回滚官网入口：撤销相应 `Update website download…` 提交并推送，Pages 会重新部署；公开 Release 保留便于追溯。

## 设计依据

使用 App 仓库发布事件触发，避免让公开仓库持有读取私有源码的凭证。同步脚本维护在官网仓库 `scripts/`，App 工作流只检出其可信 `main`，源仓库令牌仅有只读权限。只有上传和匿名下载校验都成功才改官网；`website/release.json` 记录当前已验证版本，作为防回退依据。

跨仓库写入使用仅限官网的细粒度令牌；它提交的推送会触发 Pages。官网默认 `GITHUB_TOKEN` 提交则不会自动触发另一个 push 工作流，因此这里不使用它。

官方参考：[发布事件](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#release)、[令牌权限](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)、[工作流触发限制](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。
