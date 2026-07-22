# LiteML 语法参考手册 v1.0

**LiteML**（轻量级标记语言）—— 一种面向 AI 时代的极简 Web 开发语言。编译目标：标准 HTML / CSS / JavaScript / PHP。

---

## 目录

1. [基础结构与注释](#1-基础结构与注释)
2. [标签、属性与文本](#2-标签属性与文本)
3. [多媒体与快捷宏](#3-多媒体与快捷宏)
4. [长文本与代码隔离](#4-长文本与代码隔离)
5. [模板引擎 —— PHP 动态数据](#5-模板引擎--php-动态数据)
6. [LiteCSS — 声明式布局引擎](#6-litecss--声明式布局引擎)
7. [LiteJS — 无代码交互组件](#7-litejs--无代码交互组件)
8. [行为属性系统](#8-行为属性系统)
9. [代码回退机制](#9-代码回退机制eject)
10. [逃生舱 —— 直接写原生 HTML](#10-逃生舱--直接写原生-html)
11. [双模式（PHP SSR 与 JS SPA）](#11-双模式php-ssr-与-js-spa)
12. [完整实战示例](#12-完整实战示例)
13. [附录：指令速查表](#13-附录指令速查表)

---

## 1. 基础结构与注释

### 文档声明

使用 `!` 前缀声明文档类型：

```lite
! html5
```

编译为：

```html
<!DOCTYPE html>
```

### 注释

使用 `!` 前缀写注释（`@` 前缀也兼容）：

```lite
! 这是一个注释
! TODO: 添加页脚
```

编译为：

```html
<!-- 这是一个注释 -->
<!-- TODO: 添加页脚 -->
```

### 嵌套规则

**使用 2 个空格缩进表示父子关系**，编译器自动生成闭合标签。这是 LiteML 最核心的规则。

```lite
! html5
html[lang=zh-CN]
  head
    meta[charset=UTF-8]
  body
    h1 Hello LiteML
```

编译为：

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

## 2. 标签、属性与文本

借鉴 CSS 选择器语法，让写属性像写样式一样直观。

### 基础标签

```lite
div
p
span
```

### ID 属性

```lite
div#app          → <div id="app"></div>
input#username   → <input id="username">
```

### Class 属性

```lite
p.intro                    → <p class="intro"></p>
div.card.active            → <div class="card active"></div>
span.badge.warning         → <span class="badge warning"></span>
```

### 常规属性

```lite
input[type=text]                      → <input type="text">
a[href=/about][target=_blank]         → <a href="/about" target="_blank"></a>
img[src=logo.png][alt=Logo]           → <img src="logo.png" alt="Logo">
meta[charset=UTF-8]                   → <meta charset="UTF-8">
link[rel=stylesheet][href=style.css]  → <link rel="stylesheet" href="style.css">
```

布尔属性（无值的属性）直接写属性名：

```lite
input[required][disabled]   → <input required disabled>
button[disabled]            → <button disabled></button>
```

### 内联文本

标签名后跟空格即为文本内容：

```lite
h1 欢迎来到我的网站    → <h1>欢迎来到我的网站</h1>
p 这是一段段落文字。    → <p>这是一段段落文字。</p>
a[href=/] 返回首页     → <a href="/">返回首页</a>
```

### 组合使用

```lite
a.btn#submit[href=/api][target=_blank] 提交
```

编译为：

```html
<a class="btn" id="submit" href="/api" target="_blank">提交</a>
```

---

## 3. 多媒体与快捷宏（Markdown 风格）

使用 `@` 指令或 Markdown 兼容语法快速引入多媒体资源。

### 图片（兼容 Markdown）

```lite
![一只可爱的猫](cat.jpg)
![Logo](https://example.com/logo.png)
```

编译为：

```html
<img src="cat.jpg" alt="一只可爱的猫">
<img src="https://example.com/logo.png" alt="Logo">
```

### 音频

```lite
@ 单文件音频
@audio(song.mp3 | controls)

@ 多格式音频（自动生成 source 标签）
@audio(song.mp3, song.ogg | controls, autoplay)
```

编译为：

```html
<audio src="song.mp3" controls></audio>

<audio controls autoplay>
  <source src="song.mp3" type="audio/mpeg">
  <source src="song.ogg" type="audio/ogg">
</audio>
```

### 视频

```lite
@video(movie.mp4 | controls, width=100%)
```

编译为：

```html
<video src="movie.mp4" controls style="width:100%"></video>
```

### 网页嵌入

```lite
@embed(https://bilibili.com/video/xxx | ratio=16:9)
```

编译为：

```html
<div class="embed-16-9">
  <iframe src="https://bilibili.com/video/xxx" frameborder="0" allowfullscreen></iframe>
</div>
```

### 图标

```lite
@icon(home)
@icon(user)
```

编译为：

```html
<i class="icon-home"></i>
<i class="icon-user"></i>
```

### 外部资源引用

```lite
@css(style.css)
@js(app.js | defer)
```

编译为：

```html
<link rel="stylesheet" href="style.css">
<script src="app.js" defer></script>
```

### 语法说明

`@` 指令的通用格式：

```
@指令名(核心参数 | 附加属性)
```

- `|` 前：核心参数（如文件路径、URL）
- `|` 后：附加的 HTML 属性（多个用逗号分隔）

---

## 4. 长文本与代码隔离

### 长文本块（三引号 `"""`）

自动将多行文本拆分为 `<p>` 标签，空行视为段落分隔：

```lite
article
  h1 我的第一篇博客
  """
  这是第一段，LiteML 会自动帮我包裹 p 标签。

  这里空了一行，编译器会自动识别为第二个 p 标签。
  """
```

编译为：

```html
<article>
  <h1>我的第一篇博客</h1>
  <p>这是第一段，LiteML 会自动帮我包裹 p 标签。</p>
  <p>这里空了一行，编译器会自动识别为第二个 p 标签。</p>
</article>
```

### 代码块隔离（反引号）

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

### 内联样式块（`@css`）

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

编译为：

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

## 5. 模板引擎 —— PHP 动态数据

LiteML 内置类似 Laravel Blade 的模板语法，支持在 HTML 中优雅地处理后端数据。

### 变量输出（默认安全转义）

```lite
p 欢迎, {{ $user.name }}
p 当前时间: {{ $time }}
```

编译为：

```html
<p>欢迎, <?php echo htmlspecialchars($user['name']); ?></p>
<p>当前时间: <?php echo htmlspecialchars($time); ?></p>
```

### 原样输出（富文本，不转义）

```lite
div {!! $html_content !!}
```

编译为：

```html
<div><?php echo $html_content; ?></div>
```

### 条件判断

```lite
@if($is_vip)
  span.badge VIP 会员
@else
  span 普通用户

@if($score >= 90)
  p.grade-a 优秀
@elseif($score >= 60)
  p.grade-b 及格
@else
  p.grade-c 不及格
```

编译为：

```php
<?php if($is_vip): ?>
  <span class="badge">VIP 会员</span>
<?php else: ?>
  <span>普通用户</span>
<?php endif; ?>

<?php if($score >= 90): ?>
  <p class="grade-a">优秀</p>
<?php elseif($score >= 60): ?>
  <p class="grade-b">及格</p>
<?php else: ?>
  <p class="grade-c">不及格</p>
<?php endif; ?>
```

### 循环遍历

```lite
ul.user-list
  @foreach($users as $user)
    li
      strong {{ $user.name }}
      span ({{ $user.email }})
```

编译为：

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

### 纯 PHP 逻辑块

```lite
@php
  $total_price = 0;
  foreach ($cart as $item) {
      $total_price += $item['price'] * $item['qty'];
  }

h1 总价: {{ $total_price }}
```

### 文件包含

```lite
@include(header.lite)
@include(footer.lite)
```

---

## 6. LiteCSS — 声明式布局引擎

使用 `@` 指令替代手写 CSS，自动生成样式。

### 语法格式

```
@指令名(参数1, 参数2=值)
```

指令直接写在标签名后：

```
元素标签@指令名(参数)
```

### 常用布局指令

#### Flex 布局

```lite
div@flex(center, middle)
nav@flex(between, middle)
div@flex(start, stretch)
```

| 对齐参数 | CSS 属性 | 可选值 |
| :--- | :--- | :--- |
| 1st param = `align-items` | 垂直对齐 | `start`, `center`, `end`, `stretch` |
| 2nd param = `justify-content` | 水平对齐 | `start`, `center`, `end`, `between`, `around`, `evenly` |

编译示例 `div@flex(center, middle)`：

```html
<div style="display: flex; align-items: center; justify-content: center;"></div>
```

#### 网格

```lite
div@grid(cols=3, gap=20px)
div@grid(cols=4, gap=16px, mobile-cols=2)
div@grid(cols=12, gap=10px, tablet-cols=6, mobile-cols=1)
```

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `cols` | 列数 | 3 |
| `gap` | 间距 | 16px |
| `mobile-cols` | 手机端列数 | 1 |
| `tablet-cols` | 平板端列数 | 同 cols |
| `responsive` | 生成响应式代码 | true |

#### 瀑布流

```lite
div@waterfall(cols=3, gap=20px)
div@waterfall(cols=4, gap=16px, mobile-cols=2)
```

底层使用 CSS `column-count` + `break-inside: avoid`

编译示例：

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
  <!-- 子元素自动排列为瀑布流 -->
</div>
```

#### 定位

```lite
div@position(fixed, top=10px, right=20px)
div@position(absolute, bottom=0, left=0, z-index=100)
```

#### 过渡动画

```lite
div@transition(all 0.3s ease)
button@transition(background 0.2s, transform 0.2s)
```

#### 响应式隐藏

```lite
p@hide(mobile)     ← 手机端隐藏
p@hide(tablet)     ← 平板端隐藏
p@hide(desktop)    ← 桌面端隐藏
```

---

## 7. LiteJS — 无代码交互组件

通过 `@` 指令实现交互功能，**无需编写一行 JavaScript**。

### 弹窗

```lite
@ 触发按钮
button.btn@modal(open=#my-dialog) 点击打开

@ 弹窗本体
dialog#my-dialog@modal
  h2 提示
  p 这是一个 LiteML 弹窗
  form[method=dialog]
    button 关闭
```

自动生成：
- 点击按钮弹出
- 点击遮罩层关闭
- 焦点锁定 + ESC 关闭

### 轮播图

```lite
@carousel(banner1.jpg, banner2.jpg, banner3.jpg | autoplay, interval=3000)
```

自动生成：左右箭头、底部小圆点、自动播放、暂停/播放控制。

### 选项卡

```lite
@tabs(首页, 关于, 联系 | panel1, panel2, panel3)
```

### 暗黑模式切换

```lite
button@theme-toggle
```

点击自动切换 `html[data-theme="dark"]`，并记住用户偏好。

### 点赞交互

```lite
button@like(id={{ $photo.id }}) ❤️ {{ $photo.likes }}
```

自动处理本地存储和动画效果。

### 数据获取

```lite
@fetch(/api/posts, trigger=load, target=#post-list)
@fetch(/api/more, trigger=click, target=#load-more)
```

---

## 8. 行为属性系统

使用 `[*行为名]` 语法在 HTML 属性上直接添加交互行为。

### 表单验证

```lite
form
  input[type=email][*required][*email]
  input[type=text][*required][*minlength=2]
  input[type=number][*required][*range=1,100]
  input[type=url][*url]
  textarea[*required][*maxlength=500]
  button[type=submit] 提交
```

| 行为属性 | 说明 |
| :--- | :--- |
| `[*required]` | 必填验证 |
| `[*email]` | 邮箱格式验证 |
| `[*url]` | URL 格式验证 |
| `[*minlength=N]` | 最小长度 |
| `[*maxlength=N]` | 最大长度 |
| `[*range=min,max]` | 数值范围 |
| `[*pattern=regex]` | 正则验证 |

自动行为：失焦时验证、错误时自动添加红色边框和提示文字、阻止表单提交。

### 事件绑定

```lite
button[onclick={alert('Hello World!')}] 点我
input[type=text][oninput={this.value = this.value.toUpperCase()}]
```

使用 `{}` 包裹 JS 表达式，编译器自动处理引号转义。

---

## 9. 代码回退机制（Eject）

**这是 LiteML 的灵魂特性**。内置的 `@` 指令默认是"黑盒"，加上 `!` 后缀即可"白盒展开"为原生代码。

### 局部回退

```lite
@ 默认模式：引用外部 CDN
div@waterfall(cols=3, gap=20px)

@ 回退模式：直接生成原生 CSS
div@waterfall!(cols=3, gap=20px)
```

回退编译结果：

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
  <!-- 内容 -->
</div>
```

### 弹窗回退示例

```lite
button@modal!(open=#my-dialog) 打开弹窗

dialog#my-dialog@modal!
  h2 提示
  p 这是原生 JS 控制的弹窗
```

回退编译结果：

```html
<button id="btn-open-my-dialog">打开弹窗</button>

<dialog id="my-dialog">
  <h2>提示</h2>
  <p>这是原生 JS 控制的弹窗</p>
  <form method="dialog"><button>关闭</button></form>
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

### 全局 Eject

```bash
# 将整个项目回退为纯原生代码，无任何 LiteML 依赖
liteml build --eject
```

执行后：
- 所有 `.lite` 文件 → `.html` / `.php`
- 内联 CSS 提取为 `styles.css`
- 内联 JS 提取为 `app.js`
- 删除所有 LiteML CDN 引用
- 生成纯净的标准前端项目

---

## 10. 逃生舱 —— 直接写原生 HTML

LiteML 允许混写原生 HTML，无需任何转义或特殊标记。

### 行内混写

以 `<` 开头的行自动识别为原生 HTML，原样输出：

```lite
section.hero
  h1 欢迎
  p 这是 LiteML 写的段落

  <!-- 以下是原生 HTML，编译器原样输出 -->
  <video src="demo.mp4" controls autoplay muted>
    <source src="demo.webm" type="video/webm">
    您的浏览器不支持 video 标签。
  </video>

  p 这里又回到 LiteML 了
```

### 块级混写（`@raw`）

嵌入大段原生 HTML 时使用：

```lite
div.content
  @raw
    <div class="third-party-widget" data-api-key="xxx">
      <script src="https://cdn.widget.com/embed.js"></script>
      <noscript>请启用 JavaScript</noscript>
    </div>
```

### 规则总结

| 场景 | 行为 |
| :--- | :--- |
| 行以 `<` 开头 | 识别为原生 HTML，原样输出 |
| 原生 HTML 块内缩进 | 不参与 LiteML 嵌套解析 |
| `@raw` 块内任何内容 | 全部原样输出，不解析 |
| LiteML 标签内嵌原生子元素 | 允许混合使用 |
| 原生 HTML 内使用 `@` 指令 | 不生效，原样输出 |

---

## 11. 双模式（PHP SSR 与 JS SPA）

LiteML 支持两种编译模式，通过 CLI 参数切换：

### PHP SSR 模式（服务端模板引擎）

适用于：WordPress 主题、CMS 开发、传统企业网站。

```bash
liteml build --mode=php
```

- 支持 `@if`、`@foreach`、`@include` 服务端指令
- `{{ $var }}` 编译为 `<?php echo htmlspecialchars($var); ?>`
- 输出 `.php` 文件 + 内联 CSS/JS
- 零构建步骤，直接部署

### JS SPA 模式（声明式 UI 描述层）

适用于：AI 建站工具、前端原型、交互式页面。

```bash
liteml build --mode=spa --target=react
liteml build --mode=spa --target=htmx
liteml build --mode=spa --target=alpine
```

- 禁止 `@if`、`@foreach` 服务端指令
- 支持 `@fetch`、`@component` 客户端指令
- 数据通过 API 或框架 Props
- 输出 `.jsx` / `.vue` / `.html+htmx`

**重要**：严禁在同一个 `.lite` 文件中混合两种模式。

---

## 12. 完整实战示例

### 个人主页（集成所有特性）

```lite
! html5
html[lang=zh-CN]
  head
    meta[charset=UTF-8]
    meta[name=viewport][content=width=device-width, initial-scale=1.0]
    title {{ $page_title }} - 我的主页
    @css(style.css)

  body
    @ 导航栏
    header.nav@flex(between, middle)
      h1.logo MySite
      nav
        a[href=/] 首页
        a.active[href=/about] 关于
        a[href=/blog] 博客
      button@theme-toggle 🌙

    @ 主体
    main#hero
      h2 欢迎来到 LiteML 的世界
      """
      这是一个为新手打造的极简标记语言。
      无需闭合标签，告别繁琐属性。
      """
      @audio(bgm.mp3 | controls, autoplay)

    @ 特性列表（瀑布流）
    section.features@waterfall(cols=3, gap=20px, mobile-cols=1)
      @foreach($features as $feat)
        div.card
          @icon(check)
          h3 {{ $feat.title }}
          p {{ $feat.desc }}

    @ 联系表单
    section.contact
      h3 联系我们
      form
        input[type=text][placeholder=姓名][*required]
        input[type=email][placeholder=邮箱][*required][*email]
        textarea[placeholder=留言][*required]
        button.btn[type=submit] 发送

    @ 页脚
    footer@flex(center, middle)
      p &copy; 2026 LiteML

    @js(app.js | defer)
```

### 等价的编译输出

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?php echo htmlspecialchars($page_title); ?> - 我的主页</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 导航栏 -->
  <header class="nav" style="display: flex; align-items: center; justify-content: space-between;">
    <h1 class="logo">MySite</h1>
    <nav>
      <a href="/">首页</a>
      <a class="active" href="/about">关于</a>
      <a href="/blog">博客</a>
    </nav>
    <button onclick="document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'">🌙</button>
  </header>

  <!-- 主体 -->
  <main id="hero">
    <h2>欢迎来到 LiteML 的世界</h2>
    <p>这是一个为新手打造的极简标记语言。无需闭合标签，告别繁琐属性。</p>
    <audio src="bgm.mp3" controls autoplay></audio>
  </main>

  <!-- 特性列表 -->
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

  <!-- 联系表单 -->
  <section class="contact">
    <h3>联系我们</h3>
    <form>
      <input type="text" placeholder="姓名" required>
      <input type="email" placeholder="邮箱" required>
      <textarea placeholder="留言" required></textarea>
      <button class="btn" type="submit">发送</button>
    </form>
  </section>

  <!-- 页脚 -->
  <footer style="display: flex; align-items: center; justify-content: center;">
    <p>&copy; 2026 LiteML</p>
  </footer>

  <script src="app.js" defer></script>
</body>
</html>
```

---

## 13. 附录：指令速查表

### 文档与元信息

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `! html5` | 文档声明 | `! html5` |
| `! comment` | 注释 | `! 待办` |

### 布局指令（LiteCSS）

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `@flex(align, justify)` | Flexbox 布局 | `div@flex(center, between)` |
| `@grid(cols, gap)` | 响应式网格 | `div@grid(cols=3, gap=20px)` |
| `@waterfall(cols, gap)` | 瀑布流 | `div@waterfall(cols=3)` |
| `@position(type, top...)` | 定位 | `div@position(fixed, top=0)` |
| `@transition(props)` | 过渡动画 | `div@transition(all 0.3s)` |
| `@hide(device)` | 响应式隐藏 | `p@hide(mobile)` |

### 交互指令（LiteJS）

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `@modal(open=#id)` | 模态弹窗 | `button@modal(open=#dialog)` |
| `@carousel(imgs \| auto)` | 轮播图 | `@carousel(1.jpg, 2.jpg \| autoplay)` |
| `@tabs(labels \| panels)` | 选项卡 | `@tabs(首页, 关于 \| p1, p2)` |
| `@theme-toggle` | 暗黑模式 | `button@theme-toggle` |
| `@like(id)` | 点赞 | `button@like(id=123)` |
| `@fetch(url, trigger, target)` | 数据获取 | `@fetch(/api/data \| trigger=load)` |

### 多媒体宏

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `![alt](src)` | 图片 | `![猫](cat.jpg)` |
| `@audio(src \| attrs)` | 音频 | `@audio(song.mp3 \| controls)` |
| `@video(src \| attrs)` | 视频 | `@video(movie.mp4 \| controls)` |
| `@embed(url \| ratio)` | 嵌入 | `@embed(https://... \| ratio=16:9)` |
| `@icon(name)` | 图标 | `@icon(home)` |
| `@css(src)` | 外部 CSS | `@css(style.css)` |
| `@js(src \| attrs)` | 外部 JS | `@js(app.js \| defer)` |

### PHP 模板指令

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `@if(cond)` | 条件判断 | `@if($is_vip)` |
| `@elseif(cond)` | 否则如果 | `@elseif($score > 60)` |
| `@else` | 否则 | `@else` |
| `@foreach($arr as $item)` | 循环 | `@foreach($users as $u)` |
| `@while(cond)` | While 循环 | `@while($i < 10)` |
| `@include(path)` | 文件包含 | `@include(header.lite)` |
| `@php` | PHP 代码块 | `@php $a = 1;` |
| `{{ $var }}` | 安全输出 | `{{ $user.name }}` |
| `{!! $var !!}` | 原样输出 | `{!! $html !!}` |

### 行为属性

| 属性 | 说明 | 示例 |
| :--- | :--- | :--- |
| `[*required]` | 必填验证 | `input[*required]` |
| `[*email]` | 邮箱格式 | `input[type=email][*email]` |
| `[*url]` | URL 格式 | `input[type=url][*url]` |
| `[*minlength=N]` | 最小长度 | `input[*minlength=2]` |
| `[*maxlength=N]` | 最大长度 | `textarea[*maxlength=500]` |
| `[*range=min,max]` | 数值范围 | `input[type=number][*range=1,100]` |
| `[*pattern=regex]` | 正则验证 | `input[*pattern=\d{11}]` |

### 代码回退

| 语法 | 说明 | 示例 |
| :--- | :--- | :--- |
| `directive!` | 局部回退 | `div@waterfall!` |
| `--eject` | 全局回退 | `liteml build --eject` |

### 逃生舱

| 语法 | 说明 | 示例 |
| :--- | :--- | :--- |
| 行以 `<` 开头 | 原生 HTML 行 | `<video src="...">` |
| `@raw` | 原生 HTML 块 | `@raw ...` |

---

> 本文档是 LiteML v1.0 的完整语法参考手册。
> 随着语言发展，会持续更新和补充。
