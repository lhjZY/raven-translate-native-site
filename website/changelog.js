// 更新日志条目：新版本加在数组最前面。
// date 为空表示尚未发布；版本号与 App 仓库打包脚本的 CFBundleShortVersionString 保持一致。
const RAVEN_CHANGELOG = [
  {
    version: "0.2.3",
    date: "",
    items: {
      zh: [
        "翻译：新增拆句，逐句对照原文与译文，每句可单独朗读。",
        "翻译：语言固定为中英互译，自动判断方向。",
        "朗读：可选英式或美式英语音色；OK、API 429 这类短文本也使用所选音色。",
        "学习：在翻译或检查结果上点 ♡ 把句子加入词汇本，并在学习窗口中复习。",
        "移除长难句分析，句子结构改为在词汇本详情中生成。",
        "设置：移除“登录时启动”，不再管理系统登录项。",
        "外观：新的 App 图标与菜单栏标记，取自字标中停在树枝上的渡鸦。",
      ],
      en: [
        "Translate: new sentence split shows each source sentence beside its translation, and each can be read aloud.",
        "Translate: the language pair is now fixed to Chinese and English, with automatic direction detection.",
        "Read aloud: choose a British or American English voice; short text such as OK or API 429 uses it too.",
        "Learn: tap ♡ on a translation or check result to save the sentence to your notebook, then review it in the Learn window.",
        "Sentence analysis is removed; sentence structure is now generated from notebook details.",
        "Settings: Launch at Login is removed, and the app no longer manages login items.",
        "Appearance: a new app icon and menu bar mark, drawn from the raven perched on the wordmark's branch.",
      ],
    },
  },
  {
    version: "0.2.2",
    date: "2026-10-17",
    items: {
      zh: [
        "预览发布：提供 Apple Silicon（arm64）、macOS 26+ 的 DMG；使用临时签名，未做 Apple 公证。",
        "窗口：固定后保持置顶，切换到其他应用或打开设置时不再隐藏；取消固定后恢复失焦隐藏。",
        "外观：弹窗左上角改用 Raven 手写字标、树枝与渡鸦的一体透明 Logo，自动适配浅色和深色主题。",
        "布局：缩小标题栏 Logo，与右侧按钮组垂直居中，并校准左右可见边距。",
      ],
      en: [
        "Preview release: DMG for Apple Silicon (arm64), macOS 26+, with an ad-hoc signature and no Apple notarization.",
        "Window: pinning keeps the window on top when switching apps or opening settings; unpinning restores hiding on focus loss.",
        "Appearance: a transparent Raven script wordmark with a branch and perched raven replaces the separate header icon and title, adapting to light and dark themes.",
        "Layout: a smaller header logo is vertically centered with the action buttons, with balanced visible margins on both sides.",
      ],
    },
  },
  {
    version: "0.2.1",
    date: "",
    items: {
      zh: [
        "检查：补充原意后请求失败或被中断，切换模式再回来点“重试”，仍会按你的补充重新检查，不再丢失已补充的内容。",
        "检查：AI 没有给出回译时照常显示修改结果，不再整次报错。",
        "外观：窗口宽度按钮改用“加宽 / 收窄”图标，悬停提示随状态变化。",
      ],
      en: [
        "Check: if a refinement fails or is interrupted, Retry after switching modes still re-checks with your clarification instead of discarding it.",
        "Check: when the AI returns no back-translation, the correction is still shown instead of an error.",
        "Appearance: the window width button now shows widen and narrow icons, with a tooltip that matches.",
      ],
    },
  },
  {
    version: "0.2.0",
    date: "",
    items: {
      zh: [
        "选区：⌘1 可读取任意应用中选中的文本；Chrome、Electron 应用、PDF 等不提供选区的应用会自动模拟复制读取，完成后恢复原剪贴板。",
        "检查：结果直接显示修改后的文本，修改过的词以绿色背景标出。",
        "检查：新增回译，在修改结果下方给出中文意思，方便确认 AI 是否理解了你的原意。",
        "检查：意思不对时可用中文补充原意，AI 以补充为准重新修改；可多轮补充，等待时保留上一轮结果，失败可重试。",
        "检查：接受修改会把结果写入原文，可撤销；接受后仍可继续补充检查。",
        "外观：窗口的液态玻璃跟随系统设置中的 Liquid Glass 透明度。",
        "外观：开启系统“减少透明度”后自动改用不透明背景，深色与浅色均适配。",
        "布局：拉高窗口时，多出的高度全部分给译文区。",
        "设置：新增“登录时启动”，状态与系统设置中的登录项同步。",
      ],
      en: [
        "Selection: ⌘1 reads selected text in any app; apps that don’t expose their selection, such as Chrome, Electron apps and PDFs, are read by copying, and your clipboard is restored afterwards.",
        "Check: results show the corrected text, with changed words highlighted in green.",
        "Check: a back-translation under the correction shows what it means, so you can confirm the AI understood you.",
        "Check: if the meaning is off, describe what you meant and the AI revises accordingly; clarify over several rounds, keep the previous result while waiting, and retry on failure.",
        "Check: accepting writes the correction into your source text, with undo; you can keep refining after accepting.",
        "Appearance: the window’s Liquid Glass follows the transparency set in System Settings.",
        "Appearance: with Reduce Transparency on, the window switches to an opaque background in both light and dark modes.",
        "Layout: when you make the window taller, the extra space goes to the translation.",
        "Settings: new Launch at Login option, kept in sync with Login Items in System Settings.",
      ],
    },
  },
  {
    version: "0.1.0",
    date: "",
    items: {
      zh: [
        "翻译：Google、微软翻译免费可用；DeepSeek 与自定义 OpenAI 兼容服务提供 AI 翻译，自动判断互译方向。",
        "检查：英文语法检查，逐词聚焦等待，返回纠正文本与修改说明，可接受或撤销修改。",
        "分析：长难句译文与主干，原文成分高亮，并单独讲解难点。",
        "全局快捷键：⌘1 / ⌘2 翻译选区与剪贴板，⇧⌘G / ⇧⌘I 检查与分析选区，均可在设置中修改。",
        "原文与结果可分别复制、朗读，支持语速设置。",
        "中文 / 英文界面，深色 / 浅色 / 跟随系统主题。",
        "API Key 仅保存在本机；输入与结果只保留在内存，没有历史与云同步。",
      ],
      en: [
        "Translate: Google and Microsoft Translator for free; DeepSeek and custom OpenAI-compatible services for AI translation, with automatic direction detection.",
        "Check: English grammar checking with a word-by-word focus while waiting, corrections with explanations, and accept or undo.",
        "Analyze: translation and core structure of long sentences, highlighted sentence parts, and explanations of tricky spots.",
        "Global shortcuts: ⌘1 / ⌘2 translate selection and clipboard, ⇧⌘G / ⇧⌘I check and analyze selection — all customizable in Settings.",
        "Copy or read aloud source and result separately, with adjustable speech rate.",
        "Chinese and English interface; dark, light, or system theme.",
        "API keys stay on this Mac; input and results live in memory only, with no history or cloud sync.",
      ],
    },
  },
];

(() => {
  const list = document.getElementById("changelog-list");
  const strings = window.RAVEN_I18N;

  const render = (lang) => {
    list.textContent = "";
    for (const entry of RAVEN_CHANGELOG) {
      const article = document.createElement("article");
      article.className = "release";
      article.id = `v${entry.version}`;

      const head = document.createElement("header");
      head.className = "release-head";
      const title = document.createElement("h2");
      title.textContent = entry.version;
      const when = entry.date ? document.createElement("time") : document.createElement("span");
      when.className = "release-date";
      if (entry.date) {
        when.dateTime = entry.date;
        when.textContent = entry.date;
      } else {
        when.textContent = strings[lang]["changelog.unreleased"];
      }
      head.append(title, when);

      const items = document.createElement("ul");
      for (const text of entry.items[lang]) {
        const li = document.createElement("li");
        li.textContent = text;
        items.append(li);
      }
      article.append(head, items);
      list.append(article);
    }
  };

  document.addEventListener("raven:lang", (event) => render(event.detail.lang));
})();
