# LiteML

> 🚀 **想快速上手？** 下载项目根目录的 [`liteml-quickstart.zip`](liteml-quickstart.zip) 解压即用，内含编译器 + 完整教程 + 双代码对照示例。
>
> Want to get started quickly? Download [`liteml-quickstart.zip`](liteml-quickstart.zip) — includes the compiler, full tutorial, and dual-code example.

**Lightweight Markup Language / 轻量级标记语言**

A beginner-friendly web development language for the AI era, based on HTML. Compiles to standard HTML / CSS / JavaScript / PHP.

一款面向 AI 时代的新手友好型 Web 开发语言，基于 HTML 设计，编译为标准 HTML / CSS / JS / PHP。

---

## Core Philosophy / 核心理念

Use indentation instead of closing tags, use symbols instead of verbose attributes, 1:1 mapping to standard HTML.

**用缩进代替闭合标签，用符号代替繁琐属性，1:1 映射标准 HTML。**

```
LiteML is to HTML what TypeScript is to JavaScript.
LiteML 之于 HTML，就像 TypeScript 之于 JavaScript。
```

## Features / 特性

- **Indentation-based nesting / 缩进即嵌套** — No more closing tag errors / 再无闭合标签烦恼
- **CSS selector syntax / CSS 选择器语法** — `div#app.card[href=/]` style attributes / 风格化属性书写
- **Markdown-compatible media / Markdown 风格媒体** — `![alt](src)`, `@audio()`, `@video()`
- **Declarative layout / 声明式布局** — `@flex`, `@grid`, `@waterfall` for complex CSS / 一行指令搞定复杂 CSS
- **No-code interactions / 无代码交互** — `@modal`, `@carousel`, `[*required]` without writing JS / 无需手写 JS
- **PHP template engine / PHP 模板引擎** — `@if`, `@foreach`, `{{ $var }}` built-in / 内置模板语法
- **Component system / 组件系统** — `use` components written in native HTML/CSS/JS / 用原生代码写组件
- **CSS Templates / CSS 模板** — 12 themes via `@template(name)`, one line to style / 一行代码应用主题
- **Eject mechanism / 代码回退** — One-click revert to pure native code / 一键回退纯原生代码
- **Dual mode / 双模式** — PHP SSR & JS SPA / 服务端渲染与客户端交互
- **AI-optimized / AI 优化** — 50% less tokens, higher accuracy / 省 50% Token，更高准确率

## Quick Start / 快速开始

```bash
# 1. 解压快速入门包
unzip liteml-quickstart.zip
cd liteml-quickstart

# 2. 编译第一个页面
python3 core/cli.py build examples/intro.lite -o examples/intro.html

# 3. 打开 examples/intro.html 查看结果
# 4. 阅读 README.md 学习完整语法
```

或者直接使用项目源码：

```bash
git clone https://github.com/Zhao-Shengyi/LiteML.git
cd LiteML
python3 core/cli.py build 你的文件.lite -o 输出.html
```

## Documentation / 文档

| Document / 文档 | Description / 说明 |
| :--- | :--- |
| [SYNTAX.md](SYNTAX.md) | Full syntax reference / 完整语法参考手册 |
| [README.md](README.md) | This file / 本文件 |
| [`liteml-quickstart.zip`](liteml-quickstart.zip) | Quickstart pack: compiler + tutorial + examples / 快速入门包：编译器 + 教程 + 示例 |

## Project Structure / 项目结构

```
LiteML/
├── core/              ← 编译器核心
│   ├── cli.py         ←   命令行入口
│   ├── tui.py         ←   终端 UI 入口
│   ├── compiler.py    ←   编译引擎
│   ├── parser.py      ←   语法解析
│   ├── directives.py  ←   指令系统
│   ├── component.py   ←   组件加载
│   └── ...
├── components/        ← 组件仓库
│   └── dark-mode-toggle/
├── tests/             ← 测试文件
├── editors/vscode/    ← VS Code 扩展
├── prompts/           ← AI 提示词
├── liteml-quickstart.zip  ← 快速入门包
└── README.md / SYNTAX.md
```

## License / 许可证

MIT License — see [LICENSE](LICENSE)
