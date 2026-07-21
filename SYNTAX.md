# LiteML Syntax Reference v1.0 / LiteML 语法参考手册 v1.0

**LiteML** (Lightweight Markup Language) — An AI-era minimalist web development language.
Compiles to standard HTML / CSS / JavaScript / PHP.

**LiteML**（轻量级标记语言）—— 一种面向 AI 时代的极简 Web 开发语言。
编译目标：标准 HTML / CSS / JavaScript / PHP。

---

## Table of Contents / 目录

1. [Basic Structure & Comments / 基础结构与注释](#1-basic-structure--comments-基础结构与注释)
2. [Tags, Attributes & Text / 标签、属性与文本](#2-tags-attributes--text-标签属性与文本)
3. [Media & Shortcodes / 多媒体与快捷宏](#3-media--shortcodes-多媒体与快捷宏markdown-风格)
4. [Long Text & Code Blocks / 长文本与代码隔离](#4-long-text--code-blocks-长文本与代码隔离)
5. [Template Engine — PHP / 模板引擎 —— PHP 动态数据](#5-template-engine--php-模板引擎--php-动态数据)
6. [LiteCSS — Declarative Layout / 声明式布局引擎](#6-litecss--declarative-layout-engine-声明式布局引擎)
7. [LiteJS — No-Code Interactions / 无代码交互组件](#7-litejs--no-code-interactions-无代码交互组件)
8. [Behavior Attributes / 行为属性系统](#8-behavior-attributes-行为属性系统)
9. [Eject Mechanism / 代码回退机制](#9-eject-mechanism-代码回退机制eject)
10. [Escape Hatch — Raw HTML / 逃生舱 —— 直接写原生 HTML](#10-escape-hatch--raw-html-逃生舱--直接写原生-html)
11. [Dual Mode: PHP SSR & JS SPA / 双模式](#11-dual-mode-php-ssr--js-spa-双模式php-ssr-与-js-spa)
12. [Complete Example / 完整实战示例](#12-complete-example-完整实战示例)
13. [Appendix: Quick Reference / 附录：指令速查表](#13-appendix-quick-reference-附录指令速查表)

---

## 1. Basic Structure & Comments / 基础结构与注释

### Document Type Declaration / 文档声明

Use the `!` prefix to declare the document type:

使用 `!` 前缀声明文档类型：

```lite
! html5
```

Compiles to / 编译为：

```html
<!DOCTYPE html>
```

### Comments / 注释

Use the `@` prefix for comments:

使用 `@` 前缀写注释：

```lite
@ This is a comment / 这是一个注释
@ TODO: Add footer / 添加页脚
```

Compiles to / 编译为：

```html
<!-- This is a comment / 这是一个注释 -->
<!-- TODO: Add footer / 添加页脚 -->
```

### Nesting Rules / 嵌套规则

**Use 2-space indentation to represent parent-child relationships.** The compiler automatically generates closing tags. This is LiteML's most fundamental rule.

**使用 2 个空格缩进表示父子关系**，编译器自动生成闭合标签。这是 LiteML 最核心的规则。

```lite
! html5
html[lang=zh-CN]
  head
    meta[charset=UTF-8]
  body
    h1 Hello LiteML
```

Compiles to / 编译为：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Hello LiteML</h1>
</body>
</html>
```

---

## 2. Tags, Attributes & Text / 标签、属性与文本

Inspired by CSS selectors — writing attributes feels like writing styles.

借鉴 CSS 选择器语法，让写属性像写样式一样直观。

### Basic Tags / 基础标签

```lite
div
p
span
```

### ID Attribute (`#`) / ID 属性

```lite
div#app          → <div id="app"></div>
input#username   → <input id="username">
```

### Class Attribute (`.`) / Class 属性

```lite
p.intro                    → <p class="intro"></p>
div.card.active            → <div class="card active"></div>
span.badge.warning         → <span class="badge warning"></span>
```

### Regular Attributes (`[]`) / 常规属性

```lite
input[type=text]                      → <input type="text">
a[href=/about][target=_blank]         → <a href="/about" target="_blank"></a>
img[src=logo.png][alt=Logo]           → <img src="logo.png" alt="Logo">
meta[charset=UTF-8]                   → <meta charset="UTF-8">
link[rel=stylesheet][href=style.css]  → <link rel="stylesheet" href="style.css">
```

Boolean attributes (valueless) — just write the attribute name:

布尔属性（无值的属性）直接写属性名：

```lite
input[required][disabled]   → <input required disabled>
button[disabled]            → <button disabled></button>
```

### Inline Text / 内联文本

A space after the tag name signals text content:

标签名后跟空格即为文本内容：

```lite
h1 Welcome to my site / 欢迎来到我的网站    → <h1>Welcome to my site / 欢迎来到我的网站</h1>
p This is a paragraph. / 这是一段段落文字。  → <p>This is a paragraph. / 这是一段段落文字。</p>
a[href=/] Back to home / 返回首页           → <a href="/">Back to home / 返回首页</a>
```

### Combined Usage / 组合使用

```lite
a.btn#submit[href=/api][target=_blank] Submit / 提交
```

Compiles to / 编译为：

```html
<a class="btn" id="submit" href="/api" target="_blank">Submit / 提交</a>
```

---

## 3. Media & Shortcodes / 多媒体与快捷宏（Markdown 风格）

Use `@` directives or Markdown-compatible syntax to quickly embed media.

使用 `@` 指令或 Markdown 兼容语法快速引入多媒体资源。

### Images (Markdown Compatible) / 图片（兼容 Markdown）

```lite
![A cute cat / 一只可爱的猫](cat.jpg)
![Logo](https://example.com/logo.png)
```

Compiles to / 编译为：

```html
<img src="cat.jpg" alt="A cute cat / 一只可爱的猫">
<img src="https://example.com/logo.png" alt="Logo">
```

### Audio / 音频

```lite
@ Single file / 单文件音频
@audio(song.mp3 | controls)

@ Multi-format / 多格式音频 (auto-generates source tags / 自动生成 source 标签)
@audio(song.mp3, song.ogg | controls, autoplay)
```

Compiles to / 编译为：

```html
<audio src="song.mp3" controls></audio>

<audio controls autoplay>
  <source src="song.mp3" type="audio/mpeg">
  <source src="song.ogg" type="audio/ogg">
</audio>
```

### Video / 视频

```lite
@video(movie.mp4 | controls, width=100%)
```

Compiles to / 编译为：

```html
<video src="movie.mp4" controls style="width:100%"></video>
```

### Web Embed (iframe) / 网页嵌入

```lite
@embed(https://bilibili.com/video/xxx | ratio=16:9)
```

Compiles to / 编译为：

```html
<div class="embed-16-9">
  <iframe src="https://bilibili.com/video/xxx" frameborder="0" allowfullscreen></iframe>
</div>
```

### Icons / 图标

```lite
@icon(home)
@icon(user)
```

Compiles to / 编译为：

```html
<i class="icon-home"></i>
<i class="icon-user"></i>
```

### External Resources / 外部资源引用

```lite
@css(style.css)
@js(app.js | defer)
```

Compiles to / 编译为：

```html
<link rel="stylesheet" href="style.css">
<script src="app.js" defer></script>
```

### Syntax Explanation / 语法说明

General format for `@` directives / `@` 指令的通用格式：

```
@directive_name(core_parameters | additional_attributes)
@指令名(核心参数 | 附加属性)
```

- Before `|`: core parameters (file paths, URLs) / 核心参数（如文件路径、URL）
- After `|`: additional HTML attributes (comma-separated) / 附加的 HTML 属性（多个用逗号分隔）

---

## 4. Long Text & Code Blocks / 长文本与代码隔离

### Long Text Blocks (Triple Quotes `"""`) / 长文本块（三引号）

Automatically wraps paragraphs in `<p>` tags. Blank lines separate paragraphs.

自动将多行文本拆分为 `<p>` 标签，空行视为段落分隔：

```lite
article
  h1 My First Blog / 我的第一篇博客
  """
  This is the first paragraph. LiteML will automatically
  wrap it in p tags for me.
  这是第一段，LiteML 会自动帮我包裹 p 标签。

  A blank line means a new paragraph.
  这里空了一行，编译器会自动识别为第二个 p 标签。
  """
```

Compiles to / 编译为：

```html
<article>
  <h1>My First Blog / 我的第一篇博客</h1>
  <p>This is the first paragraph. LiteML will automatically wrap it in p tags for me. 这是第一段，LiteML 会自动帮我包裹 p 标签。</p>
  <p>A blank line means a new paragraph. 这里空了一行，编译器会自动识别为第二个 p 标签。</p>
</article>
```

### Code Block Isolation (Backticks ``` ```) / 代码块隔离（反引号）

Use Markdown's ``` syntax to wrap JS/CSS code. The LiteML engine **preserves** internal indentation and syntax.

使用 Markdown 的 ``` 语法包裹 JS/CSS 等代码，LiteML 引擎**原样保留**内部缩进和语法：

```lite
script
  ```js
  document.addEventListener('click', () => {
      console.log('Hello!');
  });
  ```

@js
  ```js
  function likePost(id) {
    fetch('/api/like', { method: 'POST' });
  }
  ```
```

### Inline Style Blocks (`@css`) / 内联样式块

```lite
@css
  body {
    font-family: sans-serif;
    background: #f0f9ff;
  }
  .card {
    padding: 2rem;
    border-radius: 1rem;
  }
```

Compiles to / 编译为：

```html
<style>
  body {
    font-family: sans-serif;
    background: #f0f9ff;
  }
  .card {
    padding: 2rem;
    border-radius: 1rem;
  }
</style>
```

---

## 5. Template Engine — PHP / 模板引擎 —— PHP 动态数据

LiteML includes a Blade-like template syntax for elegantly handling backend data in HTML.

LiteML 内置类似 Laravel Blade 的模板语法，支持在 HTML 中优雅地处理后端数据。

### Variable Output (Safe Escaping by Default) / 变量输出（默认安全转义）

```lite
p Welcome, / 欢迎, {{ $user.name }}
p Current time: / 当前时间: {{ $time }}
```

Compiles to / 编译为：

```html
<p>Welcome, / 欢迎, <?php echo htmlspecialchars($user['name']); ?></p>
<p>Current time: / 当前时间: <?php echo htmlspecialchars($time); ?></p>
```

### Raw Output (Unescaped, for Rich Text) / 原样输出（富文本，不转义）

```lite
div {!! $html_content !!}
```

Compiles to / 编译为：

```html
<div><?php echo $html_content; ?></div>
```

### Conditions / 条件判断

```lite
@if($is_vip)
  span.badge VIP Member / VIP 会员
@else
  span Regular User / 普通用户

@if($score >= 90)
  p.grade-a Excellent / 优秀
@elseif($score >= 60)
  p.grade-b Pass / 及格
@else
  p.grade-c Fail / 不及格
```

Compiles to / 编译为：

```php
<?php if($is_vip): ?>
  <span class="badge">VIP Member / VIP 会员</span>
<?php else: ?>
  <span>Regular User / 普通用户</span>
<?php endif; ?>

<?php if($score >= 90): ?>
  <p class="grade-a">Excellent / 优秀</p>
<?php elseif($score >= 60): ?>
  <p class="grade-b">Pass / 及格</p>
<?php else: ?>
  <p class="grade-c">Fail / 不及格</p>
<?php endif; ?>
```

### Loops / 循环遍历

```lite
ul.user-list
  @foreach($users as $user)
    li
      strong {{ $user.name }}
      span ({{ $user.email }})
```

Compiles to / 编译为：

```php
<ul class="user-list">
  <?php foreach($users as $user): ?>
    <li>
      <strong><?php echo htmlspecialchars($user['name']); ?></strong>
      <span>(<?php echo htmlspecialchars($user['email']); ?>)</span>
    </li>
  <?php endforeach; ?>
</ul>
```

### Pure PHP Logic Block / 纯 PHP 逻辑块

```lite
@php
  $total_price = 0;
  foreach ($cart as $item) {
      $total_price += $item['price'] * $item['qty'];
  }

h1 Total: / 总价: {{ $total_price }}
```

### File Inclusion / 文件包含

```lite
@include(header.lite)
@include(footer.lite)
```

---

## 6. LiteCSS — Declarative Layout Engine / 声明式布局引擎

Use `@` directives to generate complex CSS automatically.

使用 `@` 指令替代手写 CSS，自动生成样式。

### Syntax Format / 语法格式

```
@directive_name(param1, param2=value)
@指令名(参数1, 参数2=值)
```

Write the directive directly after the tag name:

指令直接写在标签名后：

```lite
element_tag@directive_name(params)
元素标签@指令名(参数)
```

### Common Layout Directives / 常用布局指令

#### Flex Layout / Flex 布局

```lite
div@flex(center, middle)
nav@flex(between, middle)
div@flex(start, stretch)
```

| Alignment Param / 对齐参数 | CSS Property / 对应 CSS | Values / 可选值 |
| :--- | :--- | :--- |
| 1st param = `align-items` | Vertical / 垂直对齐 | `start`, `center`, `end`, `stretch` |
| 2nd param = `justify-content` | Horizontal / 水平对齐 | `start`, `center`, `end`, `between`, `around`, `evenly` |

Example compile `div@flex(center, middle)` / 编译示例：

```html
<div style="display: flex; align-items: center; justify-content: center;"></div>
```

#### Grid Layout / 网格

```lite
div@grid(cols=3, gap=20px)
div@grid(cols=4, gap=16px, mobile-cols=2)
div@grid(cols=12, gap=10px, tablet-cols=6, mobile-cols=1)
```

| Parameter / 参数 | Description / 说明 | Default / 默认值 |
| :--- | :--- | :--- |
| `cols` | Number of columns / 列数 | 3 |
| `gap` | Spacing / 间距 | 16px |
| `mobile-cols` | Columns on mobile (≤768px) / 手机端列数 | 1 |
| `tablet-cols` | Columns on tablet (769-1024px) / 平板端列数 | Same as cols / 同 cols |
| `responsive` | Generate responsive code / 生成响应式代码 | true |

#### Waterfall / Masonry Layout / 瀑布流

```lite
div@waterfall(cols=3, gap=20px)
div@waterfall(cols=4, gap=16px, mobile-cols=2)
```

Under the hood: CSS `column-count` + `break-inside: avoid` / 底层使用 CSS `column-count` + `break-inside: avoid`

Example compile / 编译示例：

```html
<style>
.waterfall-1 {
  column-count: 3;
  column-gap: 20px;
}
.waterfall-1 > * {
  break-inside: avoid;
  margin-bottom: 20px;
}
@media (max-width: 768px) {
  .waterfall-1 { column-count: 1; }
}
</style>
<div class="waterfall-1">
  <!-- Child elements auto-arrange as waterfall / 子元素自动排列为瀑布流 -->
</div>
```

#### Positioning / 定位

```lite
div@position(fixed, top=10px, right=20px)
div@position(absolute, bottom=0, left=0, z-index=100)
```

#### Transitions / 过渡动画

```lite
div@transition(all 0.3s ease)
button@transition(background 0.2s, transform 0.2s)
```

#### Responsive Hiding / 响应式隐藏

```lite
p@hide(mobile)     ← Hidden on mobile / 手机端隐藏
p@hide(tablet)     ← Hidden on tablet / 平板端隐藏
p@hide(desktop)    ← Hidden on desktop / 桌面端隐藏
```

---

## 7. LiteJS — No-Code Interactions / 无代码交互组件

Add interactive features via `@` directives **without writing a single line of JavaScript**.

通过 `@` 指令实现交互功能，**无需编写一行 JavaScript**。

### Modal Dialog / 弹窗

```lite
@ Trigger button / 触发按钮
button.btn@modal(open=#my-dialog) Click to open / 点击打开

@ Dialog itself / 弹窗本体
dialog#my-dialog@modal
  h2 Notice / 提示
  p This is a LiteML modal / 这是一个 LiteML 弹窗
  form[method=dialog]
    button Close / 关闭
```

Auto-generated behavior / 自动生成：
- Click button → `showModal()` / 点击按钮弹出
- Click backdrop → `close()` / 点击遮罩层关闭
- Focus trapping + ESC key support / 焦点锁定 + ESC 关闭

### Carousel / 轮播图

```lite
@carousel(banner1.jpg, banner2.jpg, banner3.jpg | autoplay, interval=3000)
```

Auto-generates: arrows, dots, autoplay, pause/play controls.
自动生成：左右箭头、底部小圆点、自动播放、暂停/播放控制。

### Tabs / 选项卡

```lite
@tabs(Home, About, Contact / 首页, 关于, 联系 | panel1, panel2, panel3)
```

### Dark Mode Toggle / 暗黑模式切换

```lite
button@theme-toggle
```

Toggles `html[data-theme="dark"]` and persists preference via localStorage.
点击自动切换 `html[data-theme="dark"]`，并记住用户偏好。

### Like Button / 点赞交互

```lite
button@like(id={{ $photo.id }}) ❤️ {{ $photo.likes }}
```

Auto-handles local storage and animations / 自动处理本地存储和动画效果。

### Data Fetching / 数据获取

```lite
@fetch(/api/posts, trigger=load, target=#post-list)
@fetch(/api/more, trigger=click, target=#load-more)
```

---

## 8. Behavior Attributes / 行为属性系统

Use `[*behavior_name]` syntax to add interactive behaviors directly on HTML attributes.

使用 `[*行为名]` 语法在 HTML 属性上直接添加交互行为。

### Form Validation / 表单验证

```lite
form
  input[type=email][*required][*email]
  input[type=text][*required][*minlength=2]
  input[type=number][*required][*range=1,100]
  input[type=url][*url]
  textarea[*required][*maxlength=500]
  button[type=submit] Submit / 提交
```

| Behavior Attribute / 行为属性 | Description / 说明 |
| :--- | :--- |
| `[*required]` | Required validation / 必填验证 |
| `[*email]` | Email format validation / 邮箱格式验证 |
| `[*url]` | URL format validation / URL 格式验证 |
| `[*minlength=N]` | Minimum length / 最小长度 |
| `[*maxlength=N]` | Maximum length / 最大长度 |
| `[*range=min,max]` | Numeric range / 数值范围 |
| `[*pattern=regex]` | Regex validation / 正则验证 |

Auto-behaviors: validate on blur, auto-add red border + hint on error, block form submission.
自动行为：失焦时验证、错误时自动添加红色边框和提示文字、阻止表单提交。

### Event Binding / 事件绑定

```lite
button[onclick={alert('Hello World!')}] Click me / 点我
input[type=text][oninput={this.value = this.value.toUpperCase()}]
```

Use `{}` to wrap JS expressions. The compiler handles quote escaping automatically.
使用 `{}` 包裹 JS 表达式，编译器自动处理引号转义。

---

## 9. Eject Mechanism / 代码回退机制（Eject）

**This is LiteML's soul feature.** Built-in `@` directives are "black box" by default. Append `!` to "white-box expand" them into native code.

**这是 LiteML 的灵魂特性**。内置的 `@` 指令默认是"黑盒"，加上 `!` 后缀即可"白盒展开"为原生代码。

### Local Eject / 局部回退

```lite
@ Default mode: references external CDN / 默认模式：引用外部 CDN
div@waterfall(cols=3, gap=20px)

@ Eject mode: generates native CSS inline / 回退模式：直接生成原生 CSS
div@waterfall!(cols=3, gap=20px)
```

Eject compilation result / 回退编译结果：

```html
<style>
.eject-waterfall-1 {
  column-count: 3;
  column-gap: 20px;
}
.eject-waterfall-1 > * {
  break-inside: avoid;
  margin-bottom: 20px;
}
@media (max-width: 768px) {
  .eject-waterfall-1 { column-count: 1; }
}
</style>
<div class="eject-waterfall-1">
  <!-- Content / 内容 -->
</div>
```

### Modal Eject Example / 弹窗回退示例

```lite
button@modal!(open=#my-dialog) Open / 打开弹窗

dialog#my-dialog@modal!
  h2 Notice / 提示
  p Native JS-controlled modal / 这是原生 JS 控制的弹窗
```

Eject compilation result / 回退编译结果：

```html
<button id="btn-open-my-dialog">Open / 打开弹窗</button>

<dialog id="my-dialog">
  <h2>Notice / 提示</h2>
  <p>Native JS-controlled modal / 这是原生 JS 控制的弹窗</p>
  <form method="dialog"><button>Close / 关闭</button></form>
</dialog>

<script>
(function() {
  const btn = document.getElementById('btn-open-my-dialog');
  const dialog = document.getElementById('my-dialog');
  btn.addEventListener('click', () => dialog.showModal());
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog.close();
  });
})();
</script>
```

### Global Eject (CLI) / 全局 Eject

```bash
# Eject entire project to pure native code, zero LiteML dependency
# 将整个项目回退为纯原生代码，无任何 LiteML 依赖
liteml build --eject
```

After execution / 执行后：
- All `.lite` files → `.html` / `.php` / 所有 `.lite` 文件
- Inline CSS extracted to `styles.css` / 内联 CSS 提取为
- Inline JS extracted to `app.js` / 内联 JS 提取为
- All LiteML CDN references removed / 删除所有 LiteML CDN 引用
- 100% pure standard web project / 生成纯净的标准前端项目

---

## 10. Escape Hatch — Raw HTML / 逃生舱 —— 直接写原生 HTML

LiteML allows mixing raw HTML without any escaping or special markers.

LiteML 允许混写原生 HTML，无需任何转义或特殊标记。

### Inline Mixing / 行内混写

Lines starting with `<` are automatically recognized as raw HTML and output as-is:

以 `<` 开头的行自动识别为原生 HTML，原样输出：

```lite
section.hero
  h1 Welcome / 欢迎
  p This paragraph is in LiteML / 这是 LiteML 写的段落

  <!-- Raw HTML below, output as-is / 以下是原生 HTML，编译器原样输出 -->
  <video src="demo.mp4" controls autoplay muted>
    <source src="demo.webm" type="video/webm">
    Your browser doesn't support video / 您的浏览器不支持 video 标签。
  </video>

  p Back to LiteML / 这里又回到 LiteML 了
```

### Block-Level Mixing (`@raw`) / 块级混写

For embedding large sections of native HTML / 嵌入大段原生 HTML 时使用：

```lite
div.content
  @raw
    <div class="third-party-widget" data-api-key="xxx">
      <script src="https://cdn.widget.com/embed.js"></script>
      <noscript>Please enable JavaScript / 请启用 JavaScript</noscript>
    </div>
```

### Rule Summary / 规则总结

| Scenario / 场景 | Behavior / 行为 |
| :--- | :--- |
| Line starts with `<` / 行以 `<` 开头 | Recognized as raw HTML, output as-is / 识别为原生 HTML，原样输出 |
| Indentation inside raw HTML block / 原生 HTML 块内缩进 | Doesn't participate in LiteML nesting parsing / 不参与 LiteML 嵌套解析 |
| Any content inside `@raw` block / `@raw` 块内任何内容 | Output as-is without parsing / 全部原样输出，不解析 |
| Raw child elements inside LiteML tags / LiteML 标签内嵌原生子元素 | Allowed / 允许混合使用 |
| `@` directives inside raw HTML / 原生 HTML 内使用 `@` 指令 | Not effective, output literally / 不生效，原样输出 |

---

## 11. Dual Mode: PHP SSR & JS SPA / 双模式（PHP SSR 与 JS SPA）

LiteML supports two compilation modes, switched via CLI parameter:

LiteML 支持两种编译模式，通过 CLI 参数切换：

### PHP SSR Mode (Server-Side Template Engine)

Best for: WordPress themes, CMS development, traditional business websites.
适用于：WordPress 主题、CMS 开发、传统企业网站。

```bash
liteml build --mode=php
```

- Supports `@if`, `@foreach`, `@include` server directives / 支持服务端指令
- `{{ $var }}` compiles to `<?php echo htmlspecialchars($var); ?>`
- Outputs `.php` files + inline CSS/JS / 输出 `.php` 文件
- Zero build steps, deploy directly to PHP server / 零构建步骤，直接部署

### JS SPA Mode (Declarative UI Description Layer)

Best for: AI website builders, front-end prototypes, interactive pages.
适用于：AI 建站工具、前端原型、交互式页面。

```bash
liteml build --mode=spa --target=react
liteml build --mode=spa --target=htmx
liteml build --mode=spa --target=alpine
```

- Forbids `@if`, `@foreach` server-side directives / 禁止服务端指令
- Supports `@fetch`, `@component` client directives / 支持客户端指令
- Data via API or framework Props / 数据通过 API 或框架 Props
- Outputs `.jsx` / `.vue` / `.html+htmx` / 输出对应格式

**Important**: Never mix both modes in the same `.lite` file.
**重要**：严禁在同一个 `.lite` 文件中混合两种模式。

---

## 12. Complete Example / 完整实战示例

### Personal Homepage (All Features Combined) / 个人主页（集成所有特性）

```lite
! html5
html[lang=zh-CN]
  head
    meta[charset=UTF-8]
    meta[name=viewport][content=width=device-width, initial-scale=1.0]
    title {{ $page_title }} - My Homepage / 我的主页
    @css(style.css)

  body
    @ Navigation bar / 导航栏
    header.nav@flex(between, middle)
      h1.logo MySite
      nav
        a[href=/] Home / 首页
        a.active[href=/about] About / 关于
        a[href=/blog] Blog / 博客
      button@theme-toggle 🌙

    @ Hero section / 主体
    main#hero
      h2 Welcome to LiteML / 欢迎来到 LiteML 的世界
      """
      A minimalist markup language for beginners.
      这是一个为新手打造的极简标记语言。
      No closing tags, no verbose attributes.
      无需闭合标签，告别繁琐属性。
      """
      @audio(bgm.mp3 | controls, autoplay)

    @ Feature list with waterfall layout / 特性列表（瀑布流）
    section.features@waterfall(cols=3, gap=20px, mobile-cols=1)
      @foreach($features as $feat)
        div.card
          @icon(check)
          h3 {{ $feat.title }}
          p {{ $feat.desc }}

    @ Contact form / 联系表单
    section.contact
      h3 Contact Us / 联系我们
      form
        input[type=text][placeholder=Name / 姓名][*required]
        input[type=email][placeholder=Email / 邮箱][*required][*email]
        textarea[placeholder=Message / 留言][*required]
        button.btn[type=submit] Send / 发送

    @ Footer / 页脚
    footer@flex(center, middle)
      p &copy; 2026 LiteML

    @js(app.js | defer)
```

### Equivalent Compiled Output / 等价的编译输出

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?php echo htmlspecialchars($page_title); ?> - My Homepage / 我的主页</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Navigation bar / 导航栏 -->
  <header class="nav" style="display: flex; align-items: center; justify-content: space-between;">
    <h1 class="logo">MySite</h1>
    <nav>
      <a href="/">Home / 首页</a>
      <a class="active" href="/about">About / 关于</a>
      <a href="/blog">Blog / 博客</a>
    </nav>
    <button onclick="document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'">🌙</button>
  </header>

  <!-- Hero section / 主体 -->
  <main id="hero">
    <h2>Welcome to LiteML / 欢迎来到 LiteML 的世界</h2>
    <p>A minimalist markup language for beginners. 这是一个为新手打造的极简标记语言。No closing tags, no verbose attributes. 无需闭合标签，告别繁琐属性。</p>
    <audio src="bgm.mp3" controls autoplay></audio>
  </main>

  <!-- Feature list / 特性列表 -->
  <section class="features" style="column-count: 3; column-gap: 20px;">
    <?php foreach($features as $feat): ?>
      <div class="card">
        <i class="icon-check"></i>
        <h3><?php echo htmlspecialchars($feat['title']); ?></h3>
        <p><?php echo htmlspecialchars($feat['desc']); ?></p>
      </div>
    <?php endforeach; ?>
  </section>
  <style>
    @media (max-width: 768px) {
      .features { column-count: 1; }
    }
  </style>

  <!-- Contact form / 联系表单 -->
  <section class="contact">
    <h3>Contact Us / 联系我们</h3>
    <form>
      <input type="text" placeholder="Name / 姓名" required>
      <input type="email" placeholder="Email / 邮箱" required>
      <textarea placeholder="Message / 留言" required></textarea>
      <button class="btn" type="submit">Send / 发送</button>
    </form>
  </section>

  <!-- Footer / 页脚 -->
  <footer style="display: flex; align-items: center; justify-content: center;">
    <p>&copy; 2026 LiteML</p>
  </footer>

  <script src="app.js" defer></script>
</body>
</html>
```

---

## 13. Appendix: Quick Reference / 附录：指令速查表

### Document & Meta / 文档与元信息

| Directive / 指令 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `! html5` | DOCTYPE declaration / 文档声明 | `! html5` |
| `@ comment` | HTML comment / 注释 | `@ TODO / 待办` |

### Layout Directives (LiteCSS) / 布局指令

| Directive / 指令 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `@flex(align, justify)` | Flexbox layout / Flexbox 布局 | `div@flex(center, between)` |
| `@grid(cols, gap)` | Responsive grid / 响应式网格 | `div@grid(cols=3, gap=20px)` |
| `@waterfall(cols, gap)` | Masonry layout / 瀑布流 | `div@waterfall(cols=3)` |
| `@position(type, top...)` | Positioning / 定位 | `div@position(fixed, top=0)` |
| `@transition(props)` | Transition animation / 过渡动画 | `div@transition(all 0.3s)` |
| `@hide(device)` | Responsive hiding / 响应式隐藏 | `p@hide(mobile)` |

### Interaction Directives (LiteJS) / 交互指令

| Directive / 指令 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `@modal(open=#id)` | Modal dialog / 模态弹窗 | `button@modal(open=#dialog)` |
| `@carousel(imgs \| auto)` | Carousel / 轮播图 | `@carousel(1.jpg, 2.jpg \| autoplay)` |
| `@tabs(labels \| panels)` | Tabs / 选项卡 | `@tabs(Home, About \| p1, p2)` |
| `@theme-toggle` | Dark mode switch / 暗黑模式 | `button@theme-toggle` |
| `@like(id)` | Like button / 点赞 | `button@like(id=123)` |
| `@fetch(url, trigger, target)` | Data fetching / 数据获取 | `@fetch(/api/data \| trigger=load)` |

### Media Shortcodes / 多媒体宏

| Directive / 指令 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `![alt](src)` | Image (Markdown) / 图片 | `![cat / 猫](cat.jpg)` |
| `@audio(src \| attrs)` | Audio / 音频 | `@audio(song.mp3 \| controls)` |
| `@video(src \| attrs)` | Video / 视频 | `@video(movie.mp4 \| controls)` |
| `@embed(url \| ratio)` | iframe embed / 嵌入 | `@embed(https://... \| ratio=16:9)` |
| `@icon(name)` | Icon / 图标 | `@icon(home)` |
| `@css(src)` | External CSS / 外部 CSS | `@css(style.css)` |
| `@js(src \| attrs)` | External JS / 外部 JS | `@js(app.js \| defer)` |

### PHP Template Directives / PHP 模板指令

| Directive / 指令 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `@if(cond)` | Condition / 条件判断 | `@if($is_vip)` |
| `@elseif(cond)` | Else if / 否则如果 | `@elseif($score > 60)` |
| `@else` | Else / 否则 | `@else` |
| `@foreach($arr as $item)` | Loop / 循环 | `@foreach($users as $u)` |
| `@while(cond)` | While loop | `@while($i < 10)` |
| `@include(path)` | File include / 文件包含 | `@include(header.lite)` |
| `@php` | PHP code block / PHP 代码块 | `@php $a = 1;` |
| `{{ $var }}` | Escaped output / 安全输出 | `{{ $user.name }}` |
| `{!! $var !!}` | Raw output / 原样输出 | `{!! $html !!}` |

### Behavior Attributes / 行为属性

| Attribute / 属性 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `[*required]` | Required validation / 必填验证 | `input[*required]` |
| `[*email]` | Email format / 邮箱格式 | `input[type=email][*email]` |
| `[*url]` | URL format / URL 格式 | `input[type=url][*url]` |
| `[*minlength=N]` | Min length / 最小长度 | `input[*minlength=2]` |
| `[*maxlength=N]` | Max length / 最大长度 | `textarea[*maxlength=500]` |
| `[*range=min,max]` | Number range / 数值范围 | `input[type=number][*range=1,100]` |
| `[*pattern=regex]` | Regex validation / 正则验证 | `input[*pattern=\d{11}]` |

### Code Eject / 代码回退

| Syntax / 语法 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| `directive!` | Local eject to native / 局部回退 | `div@waterfall!` |
| `--eject` | Global project eject / 全局回退 | `liteml build --eject` |

### Escape Hatch / 逃生舱

| Syntax / 语法 | Description / 说明 | Example / 示例 |
| :--- | :--- | :--- |
| Lines starting with `<` | Raw HTML line / 原生 HTML 行 | `<video src="...">` |
| `@raw` | Raw HTML block / 原生 HTML 块 | `@raw ...` |

---

> This document is LiteML v1.0's complete syntax reference.
> Updated as the language evolves.
>
> 本文档是 LiteML v1.0 的完整语法参考手册。
> 随着语言发展，会持续更新和补充。
