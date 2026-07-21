// 暗色模式切换
(function() {
  'use strict';

  const STORAGE_KEY = 'liteml-theme';

  // 初始化：读取本地存储或系统偏好
  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      document.documentElement.dataset.theme = saved;
      return;
    }
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = prefersDark ? 'dark' : 'light';
  }

  // 切换
  function toggleTheme() {
    const html = document.documentElement;
    const current = html.dataset.theme || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    html.dataset.theme = next;
    localStorage.setItem(STORAGE_KEY, next);
  }

  // 绑定按钮
  function initToggle() {
    const btn = document.getElementById('dark-mode-toggle');
    if (btn) {
      btn.addEventListener('click', toggleTheme);
    }
  }

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      document.documentElement.dataset.theme = e.matches ? 'dark' : 'light';
    }
  });

  initTheme();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToggle);
  } else {
    initToggle();
  }
})();
