# 开发记忆

## 2026-07-22 CSS 模板系统：12 款主题 + @template 宏

### 做了什么
- 创建 `templates/` 目录，内置 12 款 CSS 模板：
  - minimal / modern / dark / glass / neumorph / retro
  - corporate / blog / landing / card / gradient / terminal
- 每款模板包含：`theme.css`（完整样式）+ `example.lite` + `example.html`
- 添加 `@template(name)` 宏，读取 `templates/name/theme.css` 并内联为 `<style>` 块
- 添加 `templates list` CLI 子命令
- 模板使用 CSS 变量，用户可覆盖自定义

### 注意
- `@template(name)` 读取路径为 `templates/name/theme.css`（相对于工作目录）
- 模板 CSS 内联注入 `<head>`，适合独立页面；如需外链可用 `@css(templates/xxx/theme.css)`

## 2026-07-22 语法清理：注释改用 !，组件引用去 @

### 做了什么
- 注释前缀从 `@` 改为 `!`：
  - `! 这是注释` → `<!-- 这是注释 -->`
  - `@ 注释` 仍向后兼容
  - `! html5` 仅第一行视为 doctype，其余行视为普通注释
- 组件引用去掉 `@`：
  - `use dark-mode-toggle` → 加载组件
  - `@use dark-mode-toggle` 仍向后兼容
- 更新了 `classify_line` 新增行号参数，确保 `! html5` 只在第一行生效
- 修复了 `.class` 和 `#id` 简写（无标签名时默认 div）：
  - `classify_line` 中 `.` 和 `#` 开头的行归为 tag 类型
  - `parse_tag_line` 中无标签名时检查是否以 `.`/`#` 开头，默认 tag 为 `div`
- 更新了 `parser.py`、`compiler.py`、VS Code grammar、SYNTAX.md、test 文件、prompt 文件

### 动机
- `@` 同时用于注释和指令（`@flex`、`@modal`...）容易混淆
- 新约定：`!` 管文件级（doctype + 注释），`@` 管指令，`use` 管组件引用

### 需要注意
- `! html5` 只在文件第一行生效；非第一行当作普通注释
- `@use xxx` 和 `@ 注释` 均向后兼容，但建议改新语法

## 2026-07-21 重构：模块拆分 + 组件系统 + TUI

### 做了什么
- 将单文件 `liteml.py`（1046 行）拆分为 `core/` 包：7 个模块各司其职
  - `constants.py` — 常量（VOID_ELEMENTS, Mode, AssetMode）
  - `models.py` — 数据结构（Node, ParsedLine, ComponentInfo）
  - `parser.py` — .lite 语法解析、行类型分类、预处理
  - `directives.py` — 内置指令渲染（宏、布局、行为）
  - `component.py` — 组件加载器（约定式 + component.json）
  - `compiler.py` — 编译核心（组装全部流程）
  - `cli.py` — 命令行入口（argparse）
  - `tui.py` — 终端 UI（Textual）
- 删除了根目录的 `liteml.py`（不再需要入口文件）
- 实现了 `@use` 组件系统
  - 约定式发现：`components/组件名/template.html` + `style.css` + `script.js`
  - 清单式：`component.json` 明确指定文件
  - 组件 CSS/JS 支持内联（inline）和外部文件（external）两种模式
  - 添加了 `components init` / `components list` 子命令
- 添加了 `--css` / `--js` 编译选项，控制组件样式脚本输出策略
- 创建了示例组件 `dark-mode-toggle/`
- 更新了 VS Code 扩展的编译器路径，支持 `core/cli.py`
- 重写了 VS Code 扩展的编译器检查逻辑（临时文件 + build 命令替代不存在的 check 命令）

### 遇到的问题
1. **Python docstring 中的 `"""` 导致 SyntaxError**
   - **原因**：docstring 里写 `"""..."""` 做示例，Python 误解析为字符串结束
   - **解决**：把所有含 triple-quote 的 docstring 改成用单引号描述

2. **`from core.xxx import ...` 在直接运行 core/cli.py 时找不到包**
   - **原因**：Python 把 `core/cli.py` 当作 `__main__` 执行时，`core` 不是包
   - **解决**：在 cli.py 和 tui.py 开头加了 `sys.path.insert(0, ...)` 确保能找到包

3. **VS Code 扩展的 `check --stdin` 调用失败**
   - **原因**：编译器没有 `check` 子命令
   - **解决**：改为写入临时文件 + `build` 命令验证，并修复了 JS 检查被编译器短路的问题

### 需要注意
- 所有 `.py` 文件的 docstring 中不能出现 `"""`（Python 语法限制）
- `core/cli.py` 和 `core/tui.py` 是从项目根直接运行的入口，开头需要调整 `sys.path`
- 组件目录默认在项目根下的 `components/`，可通过 `ComponentLoader(components_dir)` 自定义
- Textual TUI 需要 `pip install textual`，已安装 v8.2.8
