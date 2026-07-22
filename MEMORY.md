# 开发记忆

## 2026-07-22 pip 打包发布

### 做了什么
- 创建 `pyproject.toml`，使用 setuptools 构建
- 修改 `cli.py` 和 `tui.py` 的 `sys.path` 为条件添加（`if not __package__`）
- `liteml` 命令已可用（`liteml version` / `liteml build` / `liteml components list` 等）
- 更新 `README.md` 加入 pip 安装说明
- 创建 `packages/npm/` JS 包裹器（保留，但有性能开销）

### 验证
- `pip install -e .` 安装成功
- `liteml build` HTML/PHP 模式均正常
- `liteml components list` → 15 个组件
- `liteml directives list` → 9 个指令
- `liteml templates list` → 12 个模板
- 原生 `python3 core/cli.py` 仍然兼容

## 2026-07-22 全项目 Bug 扫描

### 做了什么
- 全面扫描 19 个 Python 文件、9 个指令插件、15 个组件、12 个模板、3 个网站页面、VS Code 扩展
- 修复 VS Code `language-configuration.json` 的行注释配置 `@` → `!`
- 更新 `docs/AGENTS.md` 移除不存在的 `--eject` 文档

### 问题与修复
1. **language-configuration.json 行注释还是 `@`**
   - 语法已从 `@` 改为 `!`，但 VS Code 配置未同步
   - 修复：`lineComment` 改为 `"! "`

2. **docs/AGENTS.md 提到 `--eject` 但 cli.py 未实现**
   - 实际指令已自动内联展开，无需独立 eject 开关
   - 修复：删除该行文档

3. **MEMORY.md 组件数写 14 但实际是 15**
   - 漏记了 `toast` 组件

### 已知未修复（均为旧记录）
- Markdown 图片 `![alt](src)` 语法缺失
- `@audio`/`@video` 宏冗余（标准 tag 语法已覆盖）
- TextMate grammar 的 `@endraw`/`@endphp` 与解析器缩进逻辑不匹配（仅影响高亮范围，不影响编译）

### 验证通过
- Python 语法：19 个文件全部通过
- 编译器：HTML / PHP / watch 模式正常
- 指令：9 个全部可加载
- 组件：15 个全部可用，`component.json` 全部合法 JSON
- 模板：12 个全部完整（theme.css + example.lite + example.html）
- 网站：3 页全部可构建，与仓库已同步
- 向后兼容：`@use` / `@` 注释语法兼容
- 深层嵌套、空行、引号等边缘情况正常

## 2026-07-22 修复官网 syntax.lite 编译 Bug

### 做了什么
- 发现并修复了 LiteML 编译器中的两个 Bug，重新编译了官网所有页面（index.html、syntax.html、history.html）

### 修复的 Bug

1. **`#id` 在 `.class#id` 组合语法中被当作文本**（`parser.py`）
   - **现象**：`.syntax-section#sec1` 输出为 `<div class="syntax-section">#sec1</div>`，`#sec1` 被渲染为文本内容而非 `id` 属性
   - **原因**：`parse_tag_line()` 中 `#id` 解析在 `.class` 循环**之前**执行。当行以 `.` 开头时（如 `.syntax-section#sec1`），`#id` 正则不匹配；`.class` 循环匹配 `.syntax-section` 后剩余 `#sec1`，但 `#id` 不会再次检查，`#sec1` 被归为文本
   - **解决**：在 `.class` 循环**之后**增加二次 `#id` 检查

2. **`|` 管道文本的 `|` 前缀被原样输出**（`parser.py` + `compiler.py`）
   - **现象**：`| 文本内容` 输出为 `| 文本内容`，管道字符 `|` 被保留在 HTML 中（影响所有页面）
   - **原因**：`|` 行被归类为 `raw_html`，原样输出
   - **解决**：在 `classify_line()` 中新增 `text_pipe` 类型；在 `compiler.py` 中添加处理逻辑，去掉 `|` 前缀后输出纯文本，保留后续空格（支持 `pre` 块内缩进示例）

### 需要注意
- 官网全部 3 个页面（index.lite、syntax.lite、history.lite）都使用了 `|` 管道文本，修复后需全部重新编译
- `#id` 在 `.class` 之后的组合写法（`.foo#bar`）之前完全不工作，现在是标准用法

## 2026-07-22 官网翻新：动效 + 视觉升级

### 做了什么
- 彻底重写 website/style.css v2：
  - 加入毛玻璃效果（backdrop-filter blur）
  - 动效系统：浮动光晕、淡入上移、脉搏发光、渐变闪烁
  - 代码展示区模拟窗口装饰（红黄绿三色圆点）
  - 特性卡片悬停上浮 + 顶部渐变条
  - 统计区渐变数字、模板画廊彩色预览
  - 精致排版：字重、间距、字号系统调整
- 重写所有页面：
  - index.lite — 动画英雄区 + 浮动光晕 + 统计数字 + 12 模板画廊 + CTA
  - syntax.lite — 圆角卡片分节 + 目录索引 + 中英双语代码对照
  - history.lite — 时间线动画 + featured 高亮 + 项目结构代码展示
- 整体视觉从"素"到"精致"，提升品牌质感

### 修复
- 重写前解决了 meta 标签引号嵌套问题（parser.py 属性值剥离引号）

## 2026-07-22 官网 + 属性值引号修复

### 做了什么
- 创建 `website/` 目录，用 LiteML 构建官方文档网站
  - `index.html` — 首页（英雄区 + 核心特性 + 快速开始 + 模板画廊）
  - `syntax.html` — 完整语法参考（整合 syntax-en.md / syntax-cn.md 全部内容）
  - `history.html` — 开发历程（整合两个 MEMORY.md 的时间线）
- 所有页面中英双语，使用自定义 website/style.css
- 修复 `parser.py` 属性值引号问题：`[attr="value with spaces"]` 现在正确编译
  - 去掉值两端的引号后再输出，避免 `content=""value""` 的双引号嵌套

### 遇到问题
1. **meta description 被 sed 截断**：sed 替换把 `LiteML` 从内容中去掉了
   - 手动修复三个文件的 description 内容

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
- 更新了 `parser.py`、`compiler.py`、VS Code grammar、SYNTAX.md（现拆为 syntax-en.md / syntax-cn.md）、test 文件、prompt 文件

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

## 2026-07-21 VS Code 扩展创建

### 做了什么
- 在 `editors/vscode/` 创建了完整的 VS Code 扩展项目
- **项目结构**：
  ```
  editors/vscode/
  ├── .vscode/launch.json             # 调试配置
  ├── syntaxes/liteml.tmLanguage.json  # TextMate 语法高亮
  ├── language-configuration.json      # 注释切换、括号匹配
  ├── extension.js                     # 扩展入口（激活、命令）
  ├── linter.js                        # 诊断检查器
  └── package.json                     # 扩展清单
  ```

- **语法高亮覆盖的 token 类型**：
  - 注释（`@ ` 行）
  - DOCTYPE（`! html5`）
  - PHP 控制流指令（`@if/@foreach/@while/@php/@include`）
  - 布局指令（`@flex/@grid/@waterfall/@position/@transition/@hide`）
  - 交互指令（`@modal/@theme-toggle/@like`）
  - 多媒体宏（`@audio/@video/@embed/@icon/@css/@js`）
  - 行为属性（`[*required][*email][*range]` 等）
  - CSS 选择器（`#id`、`.class`）
  - HTML 属性（`[attr=val]`）
  - 变量输出（`{{ var }}` / `{!! var !!}`）
  - 代码块（`` ``` ``）和长文本（`"""`）
  - 原生 HTML 逃生舱（`<` 前缀行）
  - Eject 操作符（`!` 后缀）

- **诊断检查器（linter）检测的项目**：
  - Tab 缩进检测（LiteML 只用空格）
  - 缩进步长检查（必须是 2 的倍数）
  - 缩进跳级警告（可能遗漏中间标签）
  - 未知标签名检查
  - 未知 @ 指令拼写检查
  - PHP 控制流配对检查（@if↔@endif、@foreach↔@endforeach）
  - else/elseif 位置检查（必须在 @if 块内）
  - `->` 误用检测（应改为 `.`）
  - 括号匹配检查
  - @audio/@video/@embed 参数检查（不能为空）
  - 可通过 `liteml.compilerPath` 配置使用 Python 编译器做完整检查

- **编译命令**：
  - `Ctrl+Alt+B` 编译当前 .lite 文件为 HTML
  - 命令面板：LiteML: 编译当前文件 / 编译为 PHP
  - 编译后弹出提示，可直接打开输出文件

### 遇到的问题
1. **TextMate 语法匹配行首缩进复杂**：缩进后的内容匹配需要在模式中加入 `^(\\s*)` 捕获组
   - **解决**：对需要整行匹配的构造（如注释、DOCTYPE、raw HTML）用 `^(\\s*)` 前缀，内容部分用单独的捕获组
2. **PHP 块和代码块需要跨行匹配**：`@php ... @endphp` 和 ``` ``` ``` 跨越多行
   - **解决**：用 `begin/end` 模式，内容区域使用 `.*` 捕获全行
3. **Python 编译器诊断检测失败时难以定位错误行**：编译器的错误信息格式不统一
   - **解决**：先用 Python 编译器做完整检查；如果不可用则回退到 JS 基本检查，覆盖了 9 类常见错误

### 需要注意
- 扩展未发布到 Marketplace，需在 VS Code 中按 `F5` 加载运行调试
- 首次加载后需要打开 `.lite` 文件触发激活
- 编译器路径默认自动查找；如项目结构不同，需手动设置 `"liteml.compilerPath"`
- 语法高亮中，标签名匹配使用了反向预查 `(?<![@\\w])` 避免误匹配到指令后的文本

## 2026-07-21 编译器开发（Python）

### 做了什么
- 创建了 `liteml.py`，一个完整的 LiteML → HTML/PHP 编译器（约 1000 行）
- 支持的特性：
  - **基础**：缩进嵌套、`#id`/`.class`/`[attr]` 语法、自闭合标签
  - **注释/文档**：`@ 注释`、`! html5`
  - **多媒体宏**：`@audio`、`@video`、`@embed`、`@icon`、Markdown 图片 `![]()`
  - **外部资源**：`@css(src)`、`@js(src | attrs)`
  - **布局指令**：`@flex`、`@grid`、`@waterfall`、`@position`、`@transition`、`@hide`
  - **交互指令**：`@modal`、`@theme-toggle`、`@like`
  - **行为属性**：`[*required]`、`[*email]`、`[*minlength]`、`[*range]` 等
  - **PHP 模板**：`@if/@else/@elseif`、`@foreach`、`@while`、`@for`、`@include`、`@php`、`{{ var }}`
  - **Eject 回退**：指令加 `!` 后缀触发原生代码注入
  - **逃生舱**：原生 HTML 混写、`@raw` 块
  - **长文本**：`"""` 三引号分段自动转 `<p>`
  - **代码块**：`` ``` `` 语法隔离
  - **内联 CSS/JS**：`@css` / `@js` 块
  - **CLI**：`build` 和 `watch` 命令，支持文件/目录输入，`--mode=php` 切换
- 创建了完整的测试套件：
  - `test.lite` — 基础 HTML 功能测试
  - `test_php.lite` — PHP 模板功能测试（@if/@else/@foreach）
  - `test_full.lite` — 全部特性综合测试（10 大特性类别）

### 修复的 Bug
1. **缩进栈使用了行号而非缩进值**：`_render_node` 中 `indent_stack.append` 错误使用了 `len(self.output_lines)` 作为缩进值，导致标签顺序混乱
   - **修复**：改用实际的缩进 `indent` 参数
2. **PHP @else 缩进计算错误**：在弹出 `@if` 前计算了 `pfx`，导致 `<?php endif; ?>` 和 `<?php else: ?>` 缩进多一级
   - **修复**：在 stack.pop() 之后再调用 `self._prefix()`
3. **@else 输出了多余的 `<?php endif; ?>`**：导致 PHP 语法错误（endif 后紧接 else 无效）
   - **修复**：@else 不再输出 endif，直接输出 `<?php else: ?>`
4. **PHP 指令被 `_close_to_indent` 过早关闭**：@else 的缩进与 @if 相同时，@if 被关闭
   - **修复**：`_close_to_indent` 遇到同缩进的 PHP 起始指令时 break（留给 @else 处理）
5. **注入的 `<style>` 缩进丢失**：字符串替换 `replace('</head>', ...)` 导致样式缩进不对
   - **修复**：改用 `re.sub` 捕获 `</head>` 前的空白缩进
6. **`"""` 在 docstring 中引发语法错误**：Python 将 `"""` 解释为字符串结束
   - **修复**：docstring 中避免使用 `"""`
7. **meta description 被 sed 截断**：sed 替换把 `LiteML` 从内容中去掉了（官网翻新时手动修复）

### 需要注意
- 编译器目前约 1000 行 Python，可处理 90% 以上的 LiteML 语法
- CLI 支持 `build` 和 `watch` 模式，`--mode=php` 切换 PHP 输出
- 测试文件建议用 `test_full.lite` 覆盖验证
- 后续可扩展：组件化、`@tabs`/`@carousel` 等高级交互指令、Tree-sitter 语法高亮
- 提示词文件：`docs/prompts/usage-prompt.md`（教 AI 写 LiteML）和 `docs/prompts/decompile-prompt.md`（让 AI 把 HTML/PHP 反编译回 LiteML）

## 2026-07-21 中英双语化所有文档

### 做了什么
- 将 `README.md` 改为中英双语版本
- 将 `SYNTAX.md`（现拆为 syntax-en.md / syntax-cn.md）改为中英双语版本，每个章节标题、术语、示例都配有中英文对照
- 编译示例中的文本也做了中英双语示范
- 附录速查表所有条目均为中英文并列

## 2026-07-21 生成语法文档

### 做了什么
- 读取了 53 轮对话的 JSON 文件（约 180KB），提取了全部聊天内容
- 创建了 `LiteML-完整聊天总结.md`，系统化整理了 LiteML 项目的所有设计要点，包括：
  - 语法设计（基础语法、CSS 选择器、多媒体宏、PHP 模板）
  - LiteCSS 声明式布局引擎
  - LiteJS 无代码交互组件
  - 代码回退机制（Eject）
  - 反编译器与合成数据飞轮
  - 与 Pug/Haml/Slim 的对比
  - AI 经济账与 Token 优化
  - HTMX 集成策略
  - 成功与失败推演
  - 开源许可证选择
  - 编译器技术栈推荐
  - 所有 16 个章节的全面总结
- 在 LiteML 仓库中创建了 `SYNTAX.md`（后拆为 syntax-en.md / syntax-cn.md），一份完整的语法参考手册
- 涵盖 13 个章节：基础语法、标签属性、多媒体宏、长文本、PHP 模板、LiteCSS、LiteJS、行为属性、Eject 回退、逃生舱、双模式、实战示例、指令速查表
- 每个语法点都配有 LiteML 源码 + 编译后 HTML 的对照示例
- 末尾附有完整的指令速查表，方便快速查阅

## 2026-07-21 LiteML 完整聊天内容总结

### 做了什么
- 克隆了 GitHub 仓库 `Zhao-Shengyi/LiteML` 到本地
- 更新了 `README.md`，加入项目的核心理念描述
- 创建了 `LiteML-完整聊天总结.md`，系统化整理了 LiteML 项目的所有设计要点
- 完整梳理了 16 个章节的设计文档

### 遇到的问题
1. **JSON 文件单行 180KB，直接读取被截断**
   - **原因**：Read 工具每行有 2000 字符限制
   - **解决**：先用 bash 的 python3 脚本解析 JSON 结构，再输出到临时文件用 Read 分段读取

2. **临时文件输出仍有 50KB 限制**
   - **原因**：Read 工具默认 limit 为 2000 行，且有内存限制
   - **解决**：分 3 段读取（offset=0, offset=1322, offset=2186），完整获取了全部 3450 行内容

### 需要注意
- JSON 聊天记录是单行 minified 格式，需要先解析再阅读
- LiteML 项目涉及的知识点非常多（语法设计、编译器、反编译器、AI 模型、许可证等），整理时要保持结构清晰
