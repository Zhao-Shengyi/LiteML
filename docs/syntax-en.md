# LiteML Syntax Reference v1.0

**LiteML** (Lightweight Markup Language) — An AI-era minimalist web development language.
Compiles to standard HTML / CSS / JavaScript / PHP.

---

## Table of Contents

1. [Basic Structure & Comments](#1-basic-structure--comments)
2. [Tags, Attributes & Text](#2-tags-attributes--text)
3. [Media & Shortcodes (Markdown-style)](#3-media--shortcodes-markdown-style)
4. [Long Text & Code Blocks](#4-long-text--code-blocks)
5. [Template Engine — PHP](#5-template-engine--php)
6. [LiteCSS — Declarative Layout Engine](#6-litecss--declarative-layout-engine)
7. [LiteJS — No-Code Interactions](#7-litejs--no-code-interactions)
8. [Behavior Attributes](#8-behavior-attributes)
9. [Eject Mechanism](#9-eject-mechanismeject)
10. [Escape Hatch — Raw HTML](#10-escape-hatch--raw-html)
11. [Dual Mode: PHP SSR & JS SPA](#11-dual-mode-php-ssr--js-spa)
12. [Complete Example](#12-complete-example)
13. [Appendix: Quick Reference](#13-appendix-quick-reference)

---

## 1. Basic Structure & Comments

### Document Type Declaration

Use the `!` prefix to declare the document type:

```lite
! html5
```

Compiles to:

```html
<!DOCTYPE html>
```

### Comments

Use the `!` prefix for comments (`@` prefix also works for backward compatibility):

```lite
! This is a comment
! TODO: Add footer
```

Compiles to:

```html
<!-- This is a comment -->
<!-- TODO: Add footer -->
```

### Nesting Rules

**Use 2-space indentation to represent parent-child relationships.** The compiler automatically generates closing tags. This is LiteML's most fundamental rule.

```lite
! html5
html[lang=en]
  head
    meta[charset=UTF-8]
  body
    h1 Hello LiteML
```

Compiles to:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Hello LiteML</h1>
</body>
</html>
```

---

## 2. Tags, Attributes & Text

Inspired by CSS selectors — writing attributes feels like writing styles.

### Basic Tags

```lite
div
p
span
```

### ID Attribute (`#`)

```lite
div#app          → <div id="app"></div>
input#username   → <input id="username">
```

### Class Attribute (`.`)

```lite
p.intro                    → <p class="intro"></p>
div.card.active            → <div class="card active"></div>
span.badge.warning         → <span class="badge warning"></span>
```

### Regular Attributes (`[]`)

```lite
input[type=text]                      → <input type="text">
a[href=/about][target=_blank]         → <a href="/about" target="_blank"></a>
img[src=logo.png][alt=Logo]           → <img src="logo.png" alt="Logo">
meta[charset=UTF-8]                   → <meta charset="UTF-8">
link[rel=stylesheet][href=style.css]  → <link rel="stylesheet" href="style.css">
```

Boolean attributes (valueless) — just write the attribute name:

```lite
input[required][disabled]   → <input required disabled>
button[disabled]            → <button disabled></button>
```

### Inline Text

A space after the tag name signals text content:

```lite
h1 Welcome to my site            → <h1>Welcome to my site</h1>
p This is a paragraph.           → <p>This is a paragraph.</p>
a[href=/] Back to home           → <a href="/">Back to home</a>
```

### Combined Usage

```lite
a.btn#submit[href=/api][target=_blank] Submit
```

Compiles to:

```html
<a class="btn" id="submit" href="/api" target="_blank">Submit</a>
```

---

## 3. Media & Shortcodes (Markdown-style)

Use `@` directives or Markdown-compatible syntax to quickly embed media.

### Images (Markdown Compatible)

```lite
![A cute cat](cat.jpg)
![Logo](https://example.com/logo.png)
```

Compiles to:

```html
<img src="cat.jpg" alt="A cute cat">
<img src="https://example.com/logo.png" alt="Logo">
```

### Audio

```lite
@ Single file
@audio(song.mp3 | controls)

@ Multi-format (auto-generates source tags)
@audio(song.mp3, song.ogg | controls, autoplay)
```

Compiles to:

```html
<audio src="song.mp3" controls></audio>

<audio controls autoplay>
  <source src="song.mp3" type="audio/mpeg">
  <source src="song.ogg" type="audio/ogg">
</audio>
```

### Video

```lite
@video(movie.mp4 | controls, width=100%)
```

Compiles to:

```html
<video src="movie.mp4" controls style="width:100%"></video>
```

### Web Embed (iframe)

```lite
@embed(https://bilibili.com/video/xxx | ratio=16:9)
```

Compiles to:

```html
<div class="embed-16-9">
  <iframe src="https://bilibili.com/video/xxx" frameborder="0" allowfullscreen></iframe>
</div>
```

### Icons

```lite
@icon(home)
@icon(user)
```

Compiles to:

```html
<i class="icon-home"></i>
<i class="icon-user"></i>
```

### External Resources

```lite
@css(style.css)
@js(app.js | defer)
```

Compiles to:

```html
<link rel="stylesheet" href="style.css">
<script src="app.js" defer></script>
```

### Syntax Explanation

General format for `@` directives:

```
@directive_name(core_parameters | additional_attributes)
```

- Before `|`: core parameters (file paths, URLs)
- After `|`: additional HTML attributes (comma-separated)

---

## 4. Long Text & Code Blocks

### Long Text Blocks (Triple Quotes `"""`)

Automatically wraps paragraphs in `<p>` tags. Blank lines separate paragraphs.

```lite
article
  h1 My First Blog
  """
  This is the first paragraph. LiteML will automatically
  wrap it in p tags for me.

  A blank line means a new paragraph.
  """
```

Compiles to:

```html
<article>
  <h1>My First Blog</h1>
  <p>This is the first paragraph. LiteML will automatically wrap it in p tags for me.</p>
  <p>A blank line means a new paragraph.</p>
</article>
```

### Code Block Isolation (Backticks ``` ```)

Use Markdown's ``` syntax to wrap JS/CSS code. The LiteML engine **preserves** internal indentation and syntax.

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

### Inline Style Blocks (`@css`)

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

Compiles to:

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

## 5. Template Engine — PHP

LiteML includes a Blade-like template syntax for elegantly handling backend data in HTML.

### Variable Output (Safe Escaping by Default)

```lite
p Welcome, {{ $user.name }}
p Current time: {{ $time }}
```

Compiles to:

```html
<p>Welcome, <?php echo htmlspecialchars($user['name']); ?></p>
<p>Current time: <?php echo htmlspecialchars($time); ?></p>
```

### Raw Output (Unescaped, for Rich Text)

```lite
div {!! $html_content !!}
```

Compiles to:

```html
<div><?php echo $html_content; ?></div>
```

### Conditions

```lite
@if($is_vip)
  span.badge VIP Member
@else
  span Regular User

@if($score >= 90)
  p.grade-a Excellent
@elseif($score >= 60)
  p.grade-b Pass
@else
  p.grade-c Fail
```

Compiles to:

```php
<?php if($is_vip): ?>
  <span class="badge">VIP Member</span>
<?php else: ?>
  <span>Regular User</span>
<?php endif; ?>

<?php if($score >= 90): ?>
  <p class="grade-a">Excellent</p>
<?php elseif($score >= 60): ?>
  <p class="grade-b">Pass</p>
<?php else: ?>
  <p class="grade-c">Fail</p>
<?php endif; ?>
```

### Loops

```lite
ul.user-list
  @foreach($users as $user)
    li
      strong {{ $user.name }}
      span ({{ $user.email }})
```

Compiles to:

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

### Pure PHP Logic Block

```lite
@php
  $total_price = 0;
  foreach ($cart as $item) {
      $total_price += $item['price'] * $item['qty'];
  }

h1 Total: {{ $total_price }}
```

### File Inclusion

```lite
@include(header.lite)
@include(footer.lite)
```

---

## 6. LiteCSS — Declarative Layout Engine

Use `@` directives to generate complex CSS automatically.

### Syntax Format

```
@directive_name(param1, param2=value)
```

Write the directive directly after the tag name:

```
element_tag@directive_name(params)
```

### Common Layout Directives

#### Flex Layout

```lite
div@flex(center, middle)
nav@flex(between, middle)
div@flex(start, stretch)
```

| Alignment Param | CSS Property | Values |
| :--- | :--- | :--- |
| 1st param = `align-items` | Vertical alignment | `start`, `center`, `end`, `stretch` |
| 2nd param = `justify-content` | Horizontal alignment | `start`, `center`, `end`, `between`, `around`, `evenly` |

Example compile `div@flex(center, middle)`:

```html
<div style="display: flex; align-items: center; justify-content: center;"></div>
```

#### Grid Layout

```lite
div@grid(cols=3, gap=20px)
div@grid(cols=4, gap=16px, mobile-cols=2)
div@grid(cols=12, gap=10px, tablet-cols=6, mobile-cols=1)
```

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `cols` | Number of columns | 3 |
| `gap` | Spacing | 16px |
| `mobile-cols` | Columns on mobile (≤768px) | 1 |
| `tablet-cols` | Columns on tablet (769-1024px) | Same as cols |
| `responsive` | Generate responsive code | true |

#### Waterfall / Masonry Layout

```lite
div@waterfall(cols=3, gap=20px)
div@waterfall(cols=4, gap=16px, mobile-cols=2)
```

Under the hood: CSS `column-count` + `break-inside: avoid`

Example compile:

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
  <!-- Child elements auto-arrange as waterfall -->
</div>
```

#### Positioning

```lite
div@position(fixed, top=10px, right=20px)
div@position(absolute, bottom=0, left=0, z-index=100)
```

#### Transitions

```lite
div@transition(all 0.3s ease)
button@transition(background 0.2s, transform 0.2s)
```

#### Responsive Hiding

```lite
p@hide(mobile)     ← Hidden on mobile
p@hide(tablet)     ← Hidden on tablet
p@hide(desktop)    ← Hidden on desktop
```

---

## 7. LiteJS — No-Code Interactions

Add interactive features via `@` directives **without writing a single line of JavaScript**.

### Modal Dialog

```lite
@ Trigger button
button.btn@modal(open=#my-dialog) Click to open

@ Dialog itself
dialog#my-dialog@modal
  h2 Notice
  p This is a LiteML modal
  form[method=dialog]
    button Close
```

Auto-generated behavior:
- Click button → `showModal()`
- Click backdrop → `close()`
- Focus trapping + ESC key support

### Carousel

```lite
@carousel(banner1.jpg, banner2.jpg, banner3.jpg | autoplay, interval=3000)
```

Auto-generates: arrows, dots, autoplay, pause/play controls.

### Tabs

```lite
@tabs(Home, About, Contact | panel1, panel2, panel3)
```

### Dark Mode Toggle

```lite
button@theme-toggle
```

Toggles `html[data-theme="dark"]` and persists preference via localStorage.

### Like Button

```lite
button@like(id={{ $photo.id }}) ❤️ {{ $photo.likes }}
```

Auto-handles local storage and animations.

### Data Fetching

```lite
@fetch(/api/posts, trigger=load, target=#post-list)
@fetch(/api/more, trigger=click, target=#load-more)
```

---

## 8. Behavior Attributes

Use `[*behavior_name]` syntax to add interactive behaviors directly on HTML attributes.

### Form Validation

```lite
form
  input[type=email][*required][*email]
  input[type=text][*required][*minlength=2]
  input[type=number][*required][*range=1,100]
  input[type=url][*url]
  textarea[*required][*maxlength=500]
  button[type=submit] Submit
```

| Behavior Attribute | Description |
| :--- | :--- |
| `[*required]` | Required validation |
| `[*email]` | Email format validation |
| `[*url]` | URL format validation |
| `[*minlength=N]` | Minimum length |
| `[*maxlength=N]` | Maximum length |
| `[*range=min,max]` | Numeric range |
| `[*pattern=regex]` | Regex validation |

Auto-behaviors: validate on blur, auto-add red border + hint on error, block form submission.

### Event Binding

```lite
button[onclick={alert('Hello World!')}] Click me
input[type=text][oninput={this.value = this.value.toUpperCase()}]
```

Use `{}` to wrap JS expressions. The compiler handles quote escaping automatically.

---

## 9. Eject Mechanism (Eject)

**This is LiteML's soul feature.** Built-in `@` directives are "black box" by default. Append `!` to "white-box expand" them into native code.

### Local Eject

```lite
@ Default mode: references external CDN
div@waterfall(cols=3, gap=20px)

@ Eject mode: generates native CSS inline
div@waterfall!(cols=3, gap=20px)
```

Eject compilation result:

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
  <!-- Content -->
</div>
```

### Modal Eject Example

```lite
button@modal!(open=#my-dialog) Open

dialog#my-dialog@modal!
  h2 Notice
  p Native JS-controlled modal
```

Eject compilation result:

```html
<button id="btn-open-my-dialog">Open</button>

<dialog id="my-dialog">
  <h2>Notice</h2>
  <p>Native JS-controlled modal</p>
  <form method="dialog"><button>Close</button></form>
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

### Global Eject (CLI)

```bash
# Eject entire project to pure native code, zero LiteML dependency
liteml build --eject
```

After execution:
- All `.lite` files → `.html` / `.php`
- Inline CSS extracted to `styles.css`
- Inline JS extracted to `app.js`
- All LiteML CDN references removed
- 100% pure standard web project

---

## 10. Escape Hatch — Raw HTML

LiteML allows mixing raw HTML without any escaping or special markers.

### Inline Mixing

Lines starting with `<` are automatically recognized as raw HTML and output as-is:

```lite
section.hero
  h1 Welcome
  p This paragraph is in LiteML

  <!-- Raw HTML below, output as-is -->
  <video src="demo.mp4" controls autoplay muted>
    <source src="demo.webm" type="video/webm">
    Your browser doesn't support video
  </video>

  p Back to LiteML
```

### Block-Level Mixing (`@raw`)

For embedding large sections of native HTML:

```lite
div.content
  @raw
    <div class="third-party-widget" data-api-key="xxx">
      <script src="https://cdn.widget.com/embed.js"></script>
      <noscript>Please enable JavaScript</noscript>
    </div>
```

### Rule Summary

| Scenario | Behavior |
| :--- | :--- |
| Line starts with `<` | Recognized as raw HTML, output as-is |
| Indentation inside raw HTML block | Doesn't participate in LiteML nesting parsing |
| Any content inside `@raw` block | Output as-is without parsing |
| Raw child elements inside LiteML tags | Allowed |
| `@` directives inside raw HTML | Not effective, output literally |

---

## 11. Dual Mode: PHP SSR & JS SPA

LiteML supports two compilation modes, switched via CLI parameter.

### PHP SSR Mode (Server-Side Template Engine)

Best for: WordPress themes, CMS development, traditional business websites.

```bash
liteml build --mode=php
```

- Supports `@if`, `@foreach`, `@include` server directives
- `{{ $var }}` compiles to `<?php echo htmlspecialchars($var); ?>`
- Outputs `.php` files + inline CSS/JS
- Zero build steps, deploy directly to PHP server

### JS SPA Mode (Declarative UI Description Layer)

Best for: AI website builders, front-end prototypes, interactive pages.

```bash
liteml build --mode=spa --target=react
liteml build --mode=spa --target=htmx
liteml build --mode=spa --target=alpine
```

- Forbids `@if`, `@foreach` server-side directives
- Supports `@fetch`, `@component` client directives
- Data via API or framework Props
- Outputs `.jsx` / `.vue` / `.html+htmx`

**Important**: Never mix both modes in the same `.lite` file.

---

## 12. Complete Example

### Personal Homepage (All Features Combined)

```lite
! html5
html[lang=en]
  head
    meta[charset=UTF-8]
    meta[name=viewport][content=width=device-width, initial-scale=1.0]
    title {{ $page_title }} - My Homepage
    @css(style.css)

  body
    @ Navigation bar
    header.nav@flex(between, middle)
      h1.logo MySite
      nav
        a[href=/] Home
        a.active[href=/about] About
        a[href=/blog] Blog
      button@theme-toggle 🌙

    @ Hero section
    main#hero
      h2 Welcome to LiteML
      """
      A minimalist markup language for beginners.
      No closing tags, no verbose attributes.
      """
      @audio(bgm.mp3 | controls, autoplay)

    @ Feature list with waterfall layout
    section.features@waterfall(cols=3, gap=20px, mobile-cols=1)
      @foreach($features as $feat)
        div.card
          @icon(check)
          h3 {{ $feat.title }}
          p {{ $feat.desc }}

    @ Contact form
    section.contact
      h3 Contact Us
      form
        input[type=text][placeholder=Name][*required]
        input[type=email][placeholder=Email][*required][*email]
        textarea[placeholder=Message][*required]
        button.btn[type=submit] Send

    @ Footer
    footer@flex(center, middle)
      p &copy; 2026 LiteML

    @js(app.js | defer)
```

### Equivalent Compiled Output

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?php echo htmlspecialchars($page_title); ?> - My Homepage</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Navigation bar -->
  <header class="nav" style="display: flex; align-items: center; justify-content: space-between;">
    <h1 class="logo">MySite</h1>
    <nav>
      <a href="/">Home</a>
      <a class="active" href="/about">About</a>
      <a href="/blog">Blog</a>
    </nav>
    <button onclick="document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'">🌙</button>
  </header>

  <!-- Hero section -->
  <main id="hero">
    <h2>Welcome to LiteML</h2>
    <p>A minimalist markup language for beginners. No closing tags, no verbose attributes.</p>
    <audio src="bgm.mp3" controls autoplay></audio>
  </main>

  <!-- Feature list -->
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

  <!-- Contact form -->
  <section class="contact">
    <h3>Contact Us</h3>
    <form>
      <input type="text" placeholder="Name" required>
      <input type="email" placeholder="Email" required>
      <textarea placeholder="Message" required></textarea>
      <button class="btn" type="submit">Send</button>
    </form>
  </section>

  <!-- Footer -->
  <footer style="display: flex; align-items: center; justify-content: center;">
    <p>&copy; 2026 LiteML</p>
  </footer>

  <script src="app.js" defer></script>
</body>
</html>
```

---

## 13. Appendix: Quick Reference

### Document & Meta

| Directive | Description | Example |
| :--- | :--- | :--- |
| `! html5` | DOCTYPE declaration | `! html5` |
| `! comment` | HTML comment | `! TODO` |

### Layout Directives (LiteCSS)

| Directive | Description | Example |
| :--- | :--- | :--- |
| `@flex(align, justify)` | Flexbox layout | `div@flex(center, between)` |
| `@grid(cols, gap)` | Responsive grid | `div@grid(cols=3, gap=20px)` |
| `@waterfall(cols, gap)` | Masonry layout | `div@waterfall(cols=3)` |
| `@position(type, top...)` | Positioning | `div@position(fixed, top=0)` |
| `@transition(props)` | Transition animation | `div@transition(all 0.3s)` |
| `@hide(device)` | Responsive hiding | `p@hide(mobile)` |

### Interaction Directives (LiteJS)

| Directive | Description | Example |
| :--- | :--- | :--- |
| `@modal(open=#id)` | Modal dialog | `button@modal(open=#dialog)` |
| `@carousel(imgs \| auto)` | Carousel | `@carousel(1.jpg, 2.jpg \| autoplay)` |
| `@tabs(labels \| panels)` | Tabs | `@tabs(Home, About \| p1, p2)` |
| `@theme-toggle` | Dark mode switch | `button@theme-toggle` |
| `@like(id)` | Like button | `button@like(id=123)` |
| `@fetch(url, trigger, target)` | Data fetching | `@fetch(/api/data \| trigger=load)` |

### Media Shortcodes

| Directive | Description | Example |
| :--- | :--- | :--- |
| `![alt](src)` | Image (Markdown) | `![cat](cat.jpg)` |
| `@audio(src \| attrs)` | Audio | `@audio(song.mp3 \| controls)` |
| `@video(src \| attrs)` | Video | `@video(movie.mp4 \| controls)` |
| `@embed(url \| ratio)` | iframe embed | `@embed(https://... \| ratio=16:9)` |
| `@icon(name)` | Icon | `@icon(home)` |
| `@css(src)` | External CSS | `@css(style.css)` |
| `@js(src \| attrs)` | External JS | `@js(app.js \| defer)` |

### PHP Template Directives

| Directive | Description | Example |
| :--- | :--- | :--- |
| `@if(cond)` | Condition | `@if($is_vip)` |
| `@elseif(cond)` | Else if | `@elseif($score > 60)` |
| `@else` | Else | `@else` |
| `@foreach($arr as $item)` | Loop | `@foreach($users as $u)` |
| `@while(cond)` | While loop | `@while($i < 10)` |
| `@include(path)` | File include | `@include(header.lite)` |
| `@php` | PHP code block | `@php $a = 1;` |
| `{{ $var }}` | Escaped output | `{{ $user.name }}` |
| `{!! $var !!}` | Raw output | `{!! $html !!}` |

### Behavior Attributes

| Attribute | Description | Example |
| :--- | :--- | :--- |
| `[*required]` | Required validation | `input[*required]` |
| `[*email]` | Email format | `input[type=email][*email]` |
| `[*url]` | URL format | `input[type=url][*url]` |
| `[*minlength=N]` | Min length | `input[*minlength=2]` |
| `[*maxlength=N]` | Max length | `textarea[*maxlength=500]` |
| `[*range=min,max]` | Number range | `input[type=number][*range=1,100]` |
| `[*pattern=regex]` | Regex validation | `input[*pattern=\d{11}]` |

### Code Eject

| Syntax | Description | Example |
| :--- | :--- | :--- |
| `directive!` | Local eject to native | `div@waterfall!` |
| `--eject` | Global project eject | `liteml build --eject` |

### Escape Hatch

| Syntax | Description | Example |
| :--- | :--- | :--- |
| Lines starting with `<` | Raw HTML line | `<video src="...">` |
| `@raw` | Raw HTML block | `@raw ...` |

---

> This document is LiteML v1.0's complete syntax reference.
> Updated as the language evolves.
