# TODO — LiteML 开发规划

优先级：🔴 高 > 🟡 中 > 🟢 低
状态：⬜ 待办 / 🔄 进行中 / ✅ 已完成

---

## 🔴 编译器核心

### ⬜ 实现 `!markdown` 内联 Markdown & 外部引用

- `!markdown` → 将块内内容/外部 .md 文件转为 HTML
- 依赖 `mistune`（pip install mistune），可选安装
- 两种用法：
  ```lite
  ! markdown
    这里是 **Markdown** 内容
  ```
  ```lite
  ! markdown(./posts/hello.md)
  ```
- 输出直接对接 `@template`，无需额外机制

### ⬜ 重新实现 Markdown 图片语法 `![alt](src)`

- 旧版 `liteml.py` 中有实现，重构时丢失
- 当前替代方案：`img[src=url][alt=text]`
- 需在 parser 中添加预处理，将 `![alt](src)` 转为 tag 行

### ⬜ 清除冗余宏 `@audio` / `@video`

- `core/directive_macros.py` 中的 `@audio()` / `@video()` 功能可以用标准 tag 语法覆盖
- 考虑保留或标记废弃（deprecated），避免破坏现有代码

### ⬜ 修复 TextMate grammar `@endraw` / `@endphp`

- 解析器使用缩进检测结束，但语法高亮文件期望显式 `@endraw` / `@endphp`
- 不影响编译，只影响 VS Code 高亮范围

---

## 🟡 工程基建

### ⬜ CI/CD — GitHub Actions

- 每次推送自动运行：
  - Python 语法检查（`py_compile`）
  - 编译器全模式测试（HTML / PHP / watch）
  - 所有 .lite 测试文件编译验证
  - VS Code 扩展语法文件格式校验

### ⬜ 单元测试框架

- 引入 `pytest` 或 `unittest`
- 测试范围：
  - `parser.py` — 各类行解析、缩进、注释、doctype
  - `compiler.py` — 输出结构、属性、嵌套、指令、组件
  - `directive_loader.py` — 插件加载
  - `component.py` — 组件发现与合并
- 测试文件目录：`tests/`（目前已放 .lite 测试文件）

### ✅ 项目打包（pyproject.toml）

- `pyproject.toml` 已创建，setuptools 构建
- `liteml` CLI 命令可用（`liteml build` / `liteml version` 等）
- `pip install liteml` 可安装
- 拆掉了 `cli.py` / `tui.py` 中的无条件 `sys.path` hack

---

## 🟡 VS Code 扩展

### ⬜ 发布到 Marketplace

- 需要 `.vsix` 打包 + 微软市场发布流程
- 当前 `editors/vscode/` 已完整，可直接 `vsce package`
- 注意：语法高亮中 `@endraw` / `@endphp` 问题需先修或标注已知

### ⬜ 完善语法高亮

- `!markdown` 高亮（如果实现该功能）
- `@modal`, `@transition` 等新增指令的高亮颜色区分

---

## 🟢 组件 & 模板

### ⬜ 新增组件

- 反馈：rating, comment
- 布局：side-panel, split-view
- 导航：toc（目录生成），tab-bar（移动端）

### ⬜ 新增 CSS 模板

- 超过 12 个后考虑分类（文章类/展示类/工具类）
- `!markdown` 配套模板——专门用于 Markdown 渲染的文章页

### ⬜ 组件库文档与示例

- 每个组件增加 README 和预览截图
- 用 LiteML 构建组件展示页

---

## 🟢 网站

### ⬜ 更多页面

- 教程/入门指南页（`tutorial.lite`）
- 组件画廊页（`components.lite`）
- 模板预览页（`templates.lite`）
- API 参考页（`api.lite`）

### ⬜ SEO 与社交分享

- 完善 `<meta>` 标签
- Open Graph / Twitter Card
- Sitemap（如果页面超过 5 个）

---

## 🟢 文档

### ⬜ 更新快速入门包

- `liteml-quickstart.zip` 与最新仓库同步
- 补充 `!markdown` 教程（如果已实现）
- 补充新组件和模板示例

### ⬜ 补全英文文档

- `AGENTS.md` 的英文部分补全
- `README.md` 英文说明与中文完全对等
- `TODO.md` 双语（当前仅中文）

---

## 版本路线图

| 版本 | 主要目标 | 状态 |
|---|---|---|
| v0.1 | 核心编译器 + 基础语法 | ✅ 已完成 |
| v0.2 | 组件系统 + 12 模板 + 网站 | ✅ 已完成 |
| v0.3 | pip 发布 + `!markdown` + CI | 🎯 当前目标（pip 已完成） |
| v0.4 | 单元测试 + VS Code 发布 | 📋 规划中 |
| v0.5 | 项目打包 + 国际化文档 | 📋 规划中（npm 包裹器已创建） |
