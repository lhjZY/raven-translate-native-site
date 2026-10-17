// 全站语言与明暗主题切换，以及首页首屏的「真聚焦」动效。
// 动效节奏沿用原生 App（docs/workspace-motion.md）：每词停留约 650ms、移动 350ms。
(() => {
  const dict = window.RAVEN_I18N;
  const LANG_KEY = "raven-site-lang";
  // 与 index.html / changelog.html 头部的首帧主题脚本共用此键。
  const THEME_KEY = "raven-site-theme";
  const HOLD_MS = 650;
  const MOVE_MS = 350;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  // 偏好只是便利项：隐私模式下存储可能不可用，读写失败时回退到系统或浏览器设置。
  const readPref = (key) => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  };
  const storePref = (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      // 忽略：仅影响下次访问的默认值。
    }
  };

  const initialLang = () => {
    const stored = readPref(LANG_KEY);
    if (stored && dict[stored]) return stored;
    return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
  };

  // ---- 真聚焦 ----
  const line = document.getElementById("focus-line");
  let words = [];
  let frame = null;
  let index = 0;
  let timer = 0;

  const placeFrame = () => {
    const word = words[index];
    if (!word || !frame) return;
    words.forEach((w, i) => w.classList.toggle("is-active", i === index));
    frame.style.width = `${word.offsetWidth}px`;
    frame.style.height = `${word.offsetHeight}px`;
    frame.style.transform = `translate(${word.offsetLeft}px, ${word.offsetTop}px)`;
  };

  const stop = () => {
    window.clearTimeout(timer);
    timer = 0;
  };

  const tick = () => {
    index = (index + 1) % words.length;
    placeFrame();
    timer = window.setTimeout(tick, HOLD_MS + MOVE_MS);
  };

  const start = () => {
    stop();
    if (reducedMotion.matches || document.hidden || words.length < 2) return;
    timer = window.setTimeout(tick, HOLD_MS + MOVE_MS);
  };

  // 仅首页有焦点句；其他页面（如更新日志）跳过动效。
  const buildFocus = (parts) => {
    stop();
    if (!line || !parts) return;
    line.textContent = "";
    line.setAttribute("aria-label", parts.join(" "));
    words = parts.map((text) => {
      const span = document.createElement("span");
      span.className = "focus-word";
      span.textContent = text;
      span.setAttribute("aria-hidden", "true");
      line.append(span, " ");
      return span;
    });
    frame = document.createElement("span");
    frame.className = "focus-frame";
    frame.setAttribute("aria-hidden", "true");
    for (const corner of ["tl", "tr", "bl", "br"]) {
      const c = document.createElement("i");
      c.className = `corner corner-${corner}`;
      frame.append(c);
    }
    line.append(frame);
    // 减少动态效果时静止聚焦在中间的关键词。
    index = reducedMotion.matches ? Math.min(1, words.length - 1) : 0;
    line.classList.add("is-ready");
    placeFrame();
    start();
  };

  // ---- 主题 ----
  // 未手动选择时跟随系统；一旦点击即固定为所选主题。
  const root = document.documentElement;
  const themeButton = document.getElementById("theme-toggle");
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
  const storedTheme = readPref(THEME_KEY);
  let themeChosen = storedTheme === "light" || storedTheme === "dark";

  const setTheme = (theme) => {
    root.dataset.theme = theme;
    themeButton.setAttribute(
      "aria-label",
      dict[lang][theme === "dark" ? "theme.toLight" : "theme.toDark"],
    );
  };

  themeButton.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    themeChosen = true;
    storePref(THEME_KEY, next);
    setTheme(next);
  });

  systemDark.addEventListener("change", () => {
    if (!themeChosen) setTheme(systemDark.matches ? "dark" : "light");
  });

  // ---- 语言 ----
  let lang = initialLang();

  const apply = (next) => {
    lang = next;
    const strings = dict[lang];
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    for (const el of document.querySelectorAll("[data-i18n]")) {
      const value = strings[el.dataset.i18n];
      if (typeof value === "string") el.textContent = value;
    }
    for (const el of document.querySelectorAll("[data-i18n-attr]")) {
      const [attr, key] = el.dataset.i18nAttr.split(":");
      if (typeof strings[key] === "string") el.setAttribute(attr, strings[key]);
    }
    setTheme(root.dataset.theme ?? (systemDark.matches ? "dark" : "light"));
    buildFocus(strings[line?.dataset.focusKey]);
    // 页面专属内容（如更新日志条目）监听此事件自行渲染。
    document.dispatchEvent(new CustomEvent("raven:lang", { detail: { lang } }));
  };

  document.getElementById("lang-toggle").addEventListener("click", () => {
    const next = lang === "zh" ? "en" : "zh";
    storePref(LANG_KEY, next);
    apply(next);
  });

  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  reducedMotion.addEventListener("change", () => buildFocus(dict[lang][line?.dataset.focusKey]));

  let resizeRaf = 0;
  window.addEventListener("resize", () => {
    window.cancelAnimationFrame(resizeRaf);
    resizeRaf = window.requestAnimationFrame(placeFrame);
  });

  apply(lang);
  // 字体加载完成后字宽会变化，重新对齐焦点框。
  document.fonts?.ready.then(placeFrame);
})();
