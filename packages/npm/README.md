# LiteML Compiler — JS Wrapper

[LiteML](https://github.com/Zhao-Shengyi/LiteML) 是个轻量级 HTML/PHP 模板语言编译器。这个包通过 Node.js 调用 Python CLI 来编译 `.lite` 文件。

## 安装

```bash
npm install liteml
```

需要 Python 3 环境，且 LiteML CLI 可用：

```bash
# 方式 1：全局安装
pip install liteml

# 方式 2：项目根目录直接使用
git clone https://github.com/Zhao-Shengyi/LiteML.git
cd LiteML
```

## 使用

### JS API

```js
const { compile, compileFile } = require('liteml')

// 编译源代码字符串
compile('! html5\nhtml\n  body\n    p 你好世界', { mode: 'html' })
  .then(html => console.log(html))
  .catch(err => console.error(err))

// 编译文件
compileFile('input.lite', 'output.html', { mode: 'html', css: 'inline', js: 'inline' })
  .then(({ input, output }) => console.log(`✅ ${input} → ${output}`))

// 列出可用组件
const { listComponents, listDirectives, listTemplates } = require('liteml')

listComponents().then(console.log)
listDirectives().then(console.log)
listTemplates().then(list => list.forEach(t => console.log(`  @template(${t.name}) — ${t.description}`)))
```

### CLI

```bash
npx liteml build input.lite -o output.html
npx liteml build input.lite --mode=php -o output.php
npx liteml components list
npx liteml directives list
npx liteml templates list
```

## API

| 函数 | 参数 | 返回 |
|---|---|---|
| `compile(source, options?)` | 源码字符串，可传 `mode`/`css`/`js` | `Promise<string>` |
| `compileFile(input, output, options?)` | 输入/输出路径 | `Promise<{input, output}>` |
| `listComponents()` | — | `Promise<string[]>` |
| `listDirectives()` | — | `Promise<string[]>` |
| `listTemplates()` | — | `Promise<{name, description}[]>` |

---

# LiteML Compiler — JS Wrapper

A Node.js wrapper for the [LiteML](https://github.com/Zhao-Shengyi/LiteML) compiler. Compiles `.lite` files to HTML/PHP via the Python CLI.

## Install

```bash
npm install liteml
```

Requires Python 3 and the LiteML CLI:

```bash
# Option 1: global pip install
pip install liteml

# Option 2: use from project root
git clone https://github.com/Zhao-Shengyi/LiteML.git
cd LiteML
```

## Usage

### JS API

```js
const { compile, compileFile } = require('liteml')

compile('! html5\nhtml\n  body\n    p Hello World', { mode: 'html' })
  .then(html => console.log(html))

compileFile('input.lite', 'output.html', { mode: 'html' })
  .then(({ input, output }) => console.log(`✅ ${input} → ${output}`))
```

### CLI

```bash
npx liteml build input.lite -o output.html
npx liteml build input.lite --mode=php -o output.php
```

## License

MIT
