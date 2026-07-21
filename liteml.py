#!/usr/bin/env python3
"""
LiteML Compiler v0.1 (原型版)
编译 .lite 文件为标准 HTML / PHP

Usage:
    python liteml.py build input.lite -o output.html
    python liteml.py build input.lite --mode=php -o output.php
    python liteml.py watch input.lite -o output.html
"""

import re
import sys
import os
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# ──────────────────────────────────────────────
# 自闭合标签（Void Elements）
# ──────────────────────────────────────────────
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}

# PHP 指令对应的闭合关键字
PHP_CLOSE_MAP = {
    '@if': 'endif',
    '@elseif': 'endif',
    '@else': 'endif',
    '@foreach': 'endforeach',
    '@while': 'endwhile',
    '@for': 'endfor',
}

# ──────────────────────────────────────────────
# 编译模式
# ──────────────────────────────────────────────
class Mode(Enum):
    HTML = 'html'
    PHP = 'php'

# ──────────────────────────────────────────────
# AST 节点
# ──────────────────────────────────────────────
@dataclass
class Node:
    """单个解析节点的数据结构"""
    tag: str = ''
    id_attr: str = ''
    classes: List[str] = field(default_factory=list)
    attributes: List[Tuple[str, str]] = field(default_factory=list)
    text: str = ''
    directives: List[str] = field(default_factory=list)
    behaviors: List[Tuple[str, str]] = field(default_factory=list)
    is_void: bool = False
    eject: bool = False

# ──────────────────────────────────────────────
# LiteML 编译器
# ──────────────────────────────────────────────
class LiteMLCompiler:
    """
    LiteML 编译器核心
    将 .lite 源码编译为 HTML/PHP
    """

    def __init__(self, mode: Mode = Mode.HTML):
        self.mode = mode
        self.output_lines: List[str] = []
        # 栈元素: (indent_level, tag_or_directive)
        self.indent_stack: List[Tuple[int, str]] = []
        self.id_counter: int = 0
        self.ejected_styles: List[str] = []
        self.ejected_scripts: List[str] = []

    # ══════════════════════════════════════════
    # 编译入口
    # ══════════════════════════════════════════

    def compile(self, source: str) -> str:
        """接收 LiteML 源码字符串，返回编译后的 HTML/PHP"""
        lines = source.split('\n')
        self.output_lines = []
        self.indent_stack = []
        self.ejected_styles = []
        self.ejected_scripts = []
        self.id_counter = 0

        # 预处理：合并多行块（长文本/代码块）为单行标记
        blocks = self._preprocess_blocks(lines)

        i = 0
        while i < len(blocks):
            raw_line = blocks[i]
            indent = len(raw_line) - len(raw_line.lstrip())
            content = raw_line.strip()

            if not content:
                i += 1
                continue

            # 根据缩进关闭已打开的标签
            self._close_to_indent(indent)

            # ── 按优先级匹配行类型 ──

            # 1) 原生 HTML 逃生舱
            if content.startswith('<'):
                self.output_lines.append(raw_line.rstrip())
                i += 1
                continue

            # 1.5) Markdown 图片 ![alt](src)
            md_img = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', content)
            if md_img:
                pfx = self._prefix()
                alt = md_img.group(1)
                src = md_img.group(2).strip().strip('"\'')
                self.output_lines.append(f'{pfx}<img src="{src}" alt="{alt}">')
                i += 1
                continue

            # 2) DOCTYPE
            if content == '! html5':
                self.output_lines.append('<!DOCTYPE html>')
                i += 1
                continue

            # 3) 注释
            if content.startswith('@ ') or content.startswith('@\t'):
                pfx = self._prefix()
                self.output_lines.append(f'{pfx}<!-- {content[1:].strip()} -->')
                i += 1
                continue

            # 4) PHP 控制流指令 (@if, @elseif, @else, @foreach, @while, @for)
            if self._is_php_ctrl(content):
                self._handle_php_ctrl(content, indent)
                i += 1
                continue

            # 5) @include
            if content.startswith('@include('):
                m = re.match(r'@include\(([^)]+)\)', content)
                if m:
                    pfx = self._prefix()
                    inc = self._handle_include(m.group(1).strip().strip('"\''))
                    self.output_lines.append(f'{pfx}{inc}')
                i += 1
                continue

            # 6) @php 纯 PHP 块
            if content == '@php':
                self._collect_php_block(blocks, i + 1, indent)
                # 跳过已消费的行
                while i + 1 < len(blocks):
                    nxt = blocks[i + 1]
                    ni = len(nxt) - len(nxt.lstrip())
                    if ni > indent and nxt.strip():
                        i += 1
                    else:
                        break
                i += 1
                continue

            # 7) @raw 原生块
            if content == '@raw':
                self._collect_raw_block(blocks, i + 1, indent)
                while i + 1 < len(blocks):
                    nxt = blocks[i + 1]
                    ni = len(nxt) - len(nxt.lstrip())
                    if ni > indent and nxt.strip():
                        i += 1
                    else:
                        break
                i += 1
                continue

            # 8) @eject 显式导出
            if content.startswith('@eject('):
                m = re.match(r'@eject\(([^)]+)\)', content)
                if m:
                    self._eject_component(m.group(1).strip())
                i += 1
                continue

            # 9) 解码后的长文本块
            if content.startswith('"""'):
                text_block = content[3:-3] if content.endswith('"""') else content[3:]
                text_block = self._decode_block(text_block)
                self._emit_long_text(text_block)
                i += 1
                continue

            # 10) 解码后的代码块
            is_code_block, lang, code = self._try_parse_code_block(content)
            if is_code_block:
                pfx = self._prefix()
                code = self._decode_block(code)
                if lang:
                    self.output_lines.append(f'{pfx}<pre><code class="language-{lang}">')
                else:
                    self.output_lines.append(f'{pfx}<pre><code>')
                for cl in code.split('\n'):
                    self.output_lines.append(f'{pfx}{cl}')
                self.output_lines.append(f'{pfx}</code></pre>')
                i += 1
                continue

            # 11) @css / @js 内联块
            if content in ('@css', '@js'):
                self._collect_script_block(content, blocks, i + 1, indent)
                while i + 1 < len(blocks):
                    nxt = blocks[i + 1]
                    ni = len(nxt) - len(nxt.lstrip())
                    if ni > indent and nxt.strip():
                        i += 1
                    else:
                        break
                i += 1
                continue

            # 12) @ 宏指令 ( @audio, @flex, @waterfall 等 )
            if content.startswith('@') and not content.startswith('@@'):
                self._handle_macro(content)
                i += 1
                continue

            # 13) 普通标签行
            self._process_tag_line(content, indent)
            i += 1

        # 关闭所有剩余的标签
        self._close_all()
        result = '\n'.join(self.output_lines)

        # 注入收集到的 CSS
        if self.ejected_styles:
            css_block = '\n'.join(self.ejected_styles)
            result = re.sub(
                r'([ \t]*)</head>',
                lambda m: m.group(1) + '<style>\n' + css_block + '\n' + m.group(1) + '</style>\n' + m.group(1) + '</head>',
                result
            )

        # 注入收集到的 JS（放在 </body> 前）
        if self.ejected_scripts:
            js_block = '\n'.join(self.ejected_scripts)
            script_tag = f'<script>\n{js_block}\n</script>'
            if '</body>' in result:
                result = result.replace('</body>', f'{script_tag}\n</body>')
            else:
                result += '\n' + script_tag

        return result

    # ══════════════════════════════════════════
    # 预处理
    # ══════════════════════════════════════════

    def _preprocess_blocks(self, lines: List[str]) -> List[str]:
        """
        Merge long text and code blocks into single-line markers.
        将长文本和代码块合并为单行标记，避免块内内容被逐行解析。
        """
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith('"""'):
                indent = len(line) - len(line.lstrip())
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('"""'):
                    block.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1  # 跳过结束 """
                encoded = ' ' * indent + '"""' + self._encode_block('\n'.join(block)) + '"""'
                result.append(encoded)
                continue

            if stripped.startswith('```'):
                lang = stripped[3:].strip()
                indent = len(line) - len(line.lstrip())
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    block.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1  # 跳过结束 ```
                # 格式: `` lang ` encoded_data ````
                encoded = ' ' * indent + '``' + lang + '`' + self._encode_block('\n'.join(block)) + '````'
                result.append(encoded)
                continue

            result.append(line)
            i += 1

        return result

    @staticmethod
    def _encode_block(text: str) -> str:
        return text.replace('\n', '\x00')

    @staticmethod
    def _decode_block(text: str) -> str:
        return text.replace('\x00', '\n')

    @staticmethod
    def _try_parse_code_block(content: str) -> Tuple[bool, str, str]:
        """尝试解析编码后的代码块标记。返回 (is_match, lang, encoded_content)"""
        m = re.match(r'^``(.+?)`(.+)````$', content)
        if m:
            return True, m.group(1).strip(), m.group(2)
        return False, '', ''

    # ══════════════════════════════════════════
    # 缩进与栈管理
    # ══════════════════════════════════════════

    def _prefix(self) -> str:
        """当前缩进前缀（空格数 = 栈深度 * 2）"""
        return '  ' * len(self.indent_stack)

    def _close_to_indent(self, target_indent: int):
        """关闭缩进 >= target_indent 的栈元素。
        对 PHP 指令（@if/@foreach 等），仅当 target_indent 严格更低时才关闭
        —— 同缩进的 @else/@elseif 需要先处理。"""
        while self.indent_stack and self.indent_stack[-1][0] >= target_indent:
            top_indent, top_tag = self.indent_stack[-1]
            # PHP 起始指令 (@if/@foreach) 在同级不关闭，留给 @else
            if top_indent == target_indent and top_tag in PHP_CLOSE_MAP:
                break
            self.indent_stack.pop()
            pfx = '  ' * len(self.indent_stack)
            if top_tag in PHP_CLOSE_MAP:
                self.output_lines.append(f'{pfx}<?php {PHP_CLOSE_MAP[top_tag]}; ?>')
            elif top_tag == '@else':
                self.output_lines.append(f'{pfx}<?php endif; ?>')
            elif top_tag not in VOID_ELEMENTS:
                self.output_lines.append(f'{pfx}</{top_tag}>')

    def _close_all(self):
        """关闭所有剩余栈元素"""
        while self.indent_stack:
            _, tag = self.indent_stack.pop()
            pfx = '  ' * len(self.indent_stack)
            if tag in PHP_CLOSE_MAP:
                self.output_lines.append(f'{pfx}<?php {PHP_CLOSE_MAP[tag]}; ?>')
            elif tag == '@else':
                self.output_lines.append(f'{pfx}<?php endif; ?>')
            elif tag not in VOID_ELEMENTS:
                self.output_lines.append(f'{pfx}</{tag}>')

    # ══════════════════════════════════════════
    # PHP 控制流
    # ══════════════════════════════════════════

    PHP_DIRECTIVES = {'@if', '@elseif', '@else', '@foreach', '@while', '@for'}

    def _is_php_ctrl(self, content: str) -> bool:
        for d in self.PHP_DIRECTIVES:
            if content.startswith(d):
                return True
        return False

    def _handle_php_ctrl(self, content: str, indent: int):
        """处理 PHP 控制流指令，同时管理缩进栈"""

        # @else 特殊处理：替换栈顶的 @if 为 @else，输出 <?php else: ?>
        if content == '@else':
            if self.indent_stack and self.indent_stack[-1][1] == '@if':
                self.indent_stack.pop()
                pfx = self._prefix()
                self.output_lines.append(f'{pfx}<?php else: ?>')
                self.indent_stack.append((indent, '@else'))
            return

        if content == '@elseif':
            m = re.match(r'@elseif\((.+)\)$', content)
            if m and self.indent_stack and self.indent_stack[-1][1] == '@if':
                self.indent_stack.pop()
                pfx = self._prefix()
                self.output_lines.append(f'{pfx}<?php elseif({m.group(1)}): ?>')
                self.indent_stack.append((indent, '@elseif'))
            return

        # @if(cond), @foreach(...), @while(...), @for(...)
        m = re.match(r'@(if|foreach|while|for)\((.+)\)$', content)
        if m:
            directive = m.group(1)
            condition = m.group(2)
            # 如果栈顶有 @else/@elseif，先关闭
            if self.indent_stack and self.indent_stack[-1][1] in ('@else', '@elseif'):
                top_tag = self.indent_stack[-1][1]
                self._close_to_indent(self.indent_stack[-1][0])

            pfx = self._prefix()
            self.output_lines.append(f'{pfx}<?php {directive}({condition}): ?>')
            self.indent_stack.append((indent, f'@{directive}'))

    # ══════════════════════════════════════════
    # 块收集
    # ══════════════════════════════════════════

    def _collect_php_block(self, blocks: List[str], start: int, indent: int):
        """收集 @php ... 块"""
        pfx = self._prefix()
        lines = []
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            lines.append(blocks[i].rstrip())
            i += 1
        self.output_lines.append(f'{pfx}<?php')
        for line in lines:
            self.output_lines.append(line)
        self.output_lines.append(f'{pfx}?>')

    def _collect_raw_block(self, blocks: List[str], start: int, indent: int):
        """收集 @raw ... 块"""
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            self.output_lines.append(blocks[i].rstrip())
            i += 1

    def _collect_script_block(self, directive: str, blocks: List[str],
                              start: int, indent: int):
        """收集 @css / @js 内联块"""
        pfx = self._prefix()
        lines = []
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            # 解码可能存在的编码内容
            line = nxt
            is_code, lang, code = self._try_parse_code_block(line.strip())
            if is_code:
                line = self._decode_block(code)
            lines.append(line)
            i += 1

        raw = '\n'.join(lines).strip()
        if directive == '@css':
            self.output_lines.append(f'{pfx}<style>')
            for line in raw.split('\n'):
                self.output_lines.append(pfx + line)
            self.output_lines.append(f'{pfx}</style>')
        else:  # @js
            self.output_lines.append(f'{pfx}<script>')
            for line in raw.split('\n'):
                self.output_lines.append(pfx + line)
            self.output_lines.append(f'{pfx}</script>')

    # ══════════════════════════════════════════
    # @宏指令
    # ══════════════════════════════════════════

    def _handle_macro(self, content: str):
        """处理 @audio, @video, @css(src), @js(src) 等宏"""
        pfx = self._prefix()

        # @css(src)
        m = re.match(r'@css\(([^)]+)\)$', content)
        if m:
            href = m.group(1).strip().strip('"\'')
            self.output_lines.append(f'{pfx}<link rel="stylesheet" href="{href}">')
            return

        # @js(src | attrs)
        m = re.match(r'@js\(([^)]+)\)$', content)
        if m:
            parts = [p.strip() for p in m.group(1).split('|')]
            src = parts[0].strip().strip('"\'')
            attrs = ''
            if len(parts) > 1:
                for a in parts[1].split(','):
                    a = a.strip()
                    if '=' in a:
                        k, v = a.split('=', 1)
                        attrs += f' {k.strip()}="{v.strip()}"'
                    else:
                        attrs += f' {a}'
            self.output_lines.append(f'{pfx}<script src="{src}"{attrs}></script>')
            return

        # @audio
        m = re.match(r'@audio\(([^)]+)\)$', content)
        if m:
            args = m.group(1)
            parts = args.split('|')
            sources = [s.strip().strip('"\'') for s in parts[0].split(',')]
            attrs = ''
            if len(parts) > 1:
                for a in parts[1].split(','):
                    a = a.strip()
                    if '=' in a:
                        k, v = a.split('=', 1)
                        attrs += f' {k.strip()}="{v.strip()}"'
                    else:
                        attrs += f' {a}'
            if len(sources) == 1:
                self.output_lines.append(f'{pfx}<audio src="{sources[0]}"{attrs}></audio>')
            else:
                srcs = ''.join(f'<source src="{s}">' for s in sources)
                self.output_lines.append(f'{pfx}<audio{attrs}>{srcs}</audio>')
            return

        # @video
        m = re.match(r'@video\(([^)]+)\)$', content)
        if m:
            args = m.group(1)
            parts = args.split('|')
            sources = [s.strip().strip('"\'') for s in parts[0].split(',')]
            attrs = ''
            if len(parts) > 1:
                for a in parts[1].split(','):
                    a = a.strip()
                    if '=' in a:
                        k, v = a.split('=', 1)
                        attrs += f' {k.strip()}="{v.strip()}"'
                    else:
                        attrs += f' {a}'
            if len(sources) == 1:
                self.output_lines.append(f'{pfx}<video src="{sources[0]}"{attrs}></video>')
            else:
                srcs = ''.join(f'<source src="{s}">' for s in sources)
                self.output_lines.append(f'{pfx}<video{attrs}>{srcs}</video>')
            return

        # @embed
        m = re.match(r'@embed\(([^)]+)\)$', content)
        if m:
            parts = [p.strip() for p in m.group(1).split('|')]
            url = parts[0].strip().strip('"\'')
            ratio = parts[1].strip().split('=')[1] if len(parts) > 1 and '=' in parts[1] else '16:9'
            pad = self._ratio_to_padding(ratio)
            self.output_lines.append(f'{pfx}<div style="position:relative;padding-bottom:{pad};height:0;overflow:hidden;">')
            self.output_lines.append(f'{pfx}  <iframe src="{url}" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" frameborder="0" allowfullscreen></iframe>')
            self.output_lines.append(f'{pfx}</div>')
            return

        # @icon
        m = re.match(r'@icon\(([^)]+)\)$', content)
        if m:
            name = m.group(1).strip()
            self.output_lines.append(f'{pfx}<i class="icon-{name}"></i>')
            return

        # @flex(params) — 独立使用
        m = re.match(r'@flex\(([^)]*)\)$', content)
        if m:
            css = self._parse_flex_params(m.group(1))
            self.output_lines.append(f'{pfx}<div style="{css}">')
            return

    @staticmethod
    def _ratio_to_padding(ratio: str) -> str:
        try:
            w, h = ratio.split(':')
            return f'{float(h) / float(w) * 100}%'
        except (ValueError, IndexError):
            return '56.25%'

    @staticmethod
    def _parse_flex_params(params: str) -> str:
        align_map = {'start': 'flex-start', 'end': 'flex-end',
                     'center': 'center', 'stretch': 'stretch'}
        justify_map = {'start': 'flex-start', 'end': 'flex-end',
                       'center': 'center', 'between': 'space-between',
                       'around': 'space-around', 'evenly': 'space-evenly'}
        parts = [p.strip() for p in params.split(',') if p.strip()]
        css = 'display: flex;'
        if len(parts) >= 1 and parts[0]:
            css += f' align-items: {align_map.get(parts[0], parts[0])};'
        if len(parts) >= 2 and parts[1]:
            css += f' justify-content: {justify_map.get(parts[1], parts[1])};'
        return css

    # ══════════════════════════════════════════
    # @include
    # ══════════════════════════════════════════

    def _handle_include(self, path: str) -> str:
        if self.mode == Mode.PHP:
            return f'<?php include "{path}"; ?>'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f'<!-- Include not found: {path} -->'

    # ══════════════════════════════════════════
    # Eject / 回退
    # ══════════════════════════════════════════

    def _eject_component(self, component: str):
        pfx = self._prefix()
        if component == 'modal':
            self.output_lines.append(f'{pfx}<!-- Ejected Modal Component -->')
            self.ejected_styles.append(
                'dialog::backdrop { background: rgba(0,0,0,0.5); }\n'
                'dialog { border: none; border-radius: 8px; padding: 2rem; }'
            )

    # ══════════════════════════════════════════
    # 长文本
    # ══════════════════════════════════════════

    def _emit_long_text(self, text: str):
        """将长文本按空行分段，每段输出 <p> 标签"""
        paragraphs = re.split(r'\n\s*\n', text.strip())
        pfx = self._prefix()
        for para in paragraphs:
            para = ' '.join(para.split('\n')).strip()
            if para:
                if self.mode == Mode.PHP:
                    para = self._interpolate(para)
                self.output_lines.append(f'{pfx}<p>{para}</p>')

    # ══════════════════════════════════════════
    # PHP 插值处理
    # ══════════════════════════════════════════

    def _interpolate(self, text: str) -> str:
        """处理 {{ }} 和 {!! !!} 模板插值"""
        text = re.sub(r'\{\{(.+?)\}\}', r'<?php echo htmlspecialchars(\1); ?>', text)
        text = re.sub(r'\{\!(.+?)\!\}', r'<?php echo \1; ?>', text)
        return text

    # ══════════════════════════════════════════
    # 核心标签解析
    # ══════════════════════════════════════════

    def _process_tag_line(self, content: str, indent: int):
        """
        解析一行标签，格式：
          tag#id.class1.class2[attr=val][*behavior] text
          tag@directive(params)[attr=val] text
          tag@directive! ...   ← 回退模式
        """
        node = Node()
        remaining = content

        # 提取标签名
        m = re.match(r'^([a-zA-Z][\w-]*)', remaining)
        if not m:
            self.output_lines.append(f'{self._prefix()}{content}')
            return
        node.tag = m.group(1)
        remaining = remaining[m.end():]
        node.is_void = node.tag in VOID_ELEMENTS

        # #id
        m = re.match(r'#([\w-]+)', remaining)
        if m:
            node.id_attr = m.group(1)
            remaining = remaining[m.end():]

        # .class1.class2
        while True:
            m = re.match(r'\.([\w-]+)', remaining)
            if m:
                node.classes.append(m.group(1))
                remaining = remaining[m.end():]
            else:
                break

        # @directive(params) 或 @directive!(params)
        m = re.match(r'@([a-zA-Z][\w-]*)(!)?(?:\(([^)]*)\))?', remaining)
        if m:
            dir_name = m.group(1)
            node.eject = m.group(2) == '!'
            dir_params = m.group(3) or ''
            node.directives.append(dir_name)
            remaining = remaining[m.end():]
            self._apply_directive(node, dir_name, dir_params)

        # [attr=val] 和 [*behavior]
        while True:
            m = re.match(r'\[([^\]]+)\]', remaining)
            if not m:
                break
            attr_content = m.group(1)
            remaining = remaining[m.end():]

            if attr_content.startswith('*'):
                # 行为属性 [*name=val]
                behavior = attr_content[1:]
                if '=' in behavior:
                    k, v = behavior.split('=', 1)
                    node.behaviors.append((k.strip(), v.strip()))
                else:
                    node.behaviors.append((behavior.strip(), ''))
            else:
                # 常规属性 [attr=val] 或 [attr]
                if '=' in attr_content:
                    k, v = attr_content.split('=', 1)
                    node.attributes.append((k.strip(), v.strip()))
                else:
                    node.attributes.append((attr_content.strip(), ''))

        # 剩余文本
        node.text = remaining.strip()

        # PHP 插值处理
        if self.mode == Mode.PHP:
            node.text = self._interpolate(node.text)
            # 属性值中的插值
            node.attributes = [
                (k, self._interpolate(v) if '{{' in v else v)
                for k, v in node.attributes
            ]

        self._render_node(node, indent)

    # ══════════════════════════════════════════
    # 指令应用
    # ══════════════════════════════════════════

    def _apply_directive(self, node: Node, dir_name: str, params: str):
        if dir_name == 'flex':
            css = self._parse_flex_params(params)
            node.attributes.append(('style', css))

        elif dir_name == 'grid':
            grid = self._parse_grid_params(params)
            cls = f'eject-grid-{self.id_counter}'
            self.id_counter += 1
            node.classes.append(cls)
            self.ejected_styles.append(
                f'.{cls} {{\n'
                f'  display: grid;\n'
                f'  grid-template-columns: repeat({grid["cols"]}, 1fr);\n'
                f'  gap: {grid["gap"]};\n'
                f'}}\n'
                f'@media (max-width: 768px) {{\n'
                f'  .{cls} {{\n'
                f'    grid-template-columns: repeat({grid["mobile-cols"]}, 1fr);\n'
                f'  }}\n'
                f'}}'
            )

        elif dir_name == 'waterfall':
            wf = self._parse_waterfall_params(params)
            cls = f'eject-waterfall-{self.id_counter}'
            self.id_counter += 1
            node.classes.append(cls)
            self.ejected_styles.append(
                f'.{cls} {{\n'
                f'  column-count: {wf["cols"]};\n'
                f'  column-gap: {wf["gap"]};\n'
                f'}}\n'
                f'.{cls} > * {{\n'
                f'  break-inside: avoid;\n'
                f'  margin-bottom: {wf["gap"]};\n'
                f'}}\n'
                f'@media (max-width: 768px) {{\n'
                f'  .{cls} {{\n'
                f'    column-count: {wf["mobile-cols"]};\n'
                f'  }}\n'
                f'}}'
            )

        elif dir_name == 'modal':
            modal_id = ''
            if params.startswith('open='):
                modal_id = params.split('=', 1)[1].strip().strip('"\'')
            if modal_id:
                btn_id = f'btn-modal-{self.id_counter}'
                self.id_counter += 1
                node.attributes.append(('id', btn_id))
                self.ejected_scripts.append(
                    f'(function() {{\n'
                    f'  document.getElementById("{btn_id}").addEventListener("click", function() {{\n'
                    f'    document.querySelector("{modal_id}").showModal();\n'
                    f'  }});\n'
                    f'  document.querySelector("{modal_id}").addEventListener("click", function(e) {{\n'
                    f'    if (e.target === this) this.close();\n'
                    f'  }});\n'
                    f'}})();'
                )

        elif dir_name == 'theme-toggle':
            node.attributes.append(('onclick',
                "var t=document.documentElement.dataset;"
                "t.theme=t.theme==='dark'?'light':'dark';"
                "localStorage.setItem('theme',t.theme);"
            ))

        elif dir_name == 'position':
            parts = [p.strip() for p in params.split(',') if p.strip()]
            css = ''
            for p in parts:
                if '=' in p:
                    css += f' {p.replace("=", ": ")};'
                else:
                    css += f' position: {p};'
            node.attributes.append(('style', css.strip()))

        elif dir_name == 'transition':
            node.attributes.append(('style', f'transition: {params.strip()}'))

        elif dir_name == 'hide':
            device = params.strip()
            media_map = {
                'mobile': '(max-width: 768px)',
                'tablet': '(min-width: 769px) and (max-width: 1024px)',
                'desktop': '(min-width: 1025px)',
            }
            media = media_map.get(device, device)
            cls = f'eject-hide-{self.id_counter}'
            self.id_counter += 1
            node.classes.append(cls)
            self.ejected_styles.append(
                f'@media {media} {{\n'
                f'  .{cls} {{ display: none !important; }}\n'
                f'}}'
            )

        elif dir_name == 'like':
            cls = f'eject-like-{self.id_counter}'
            self.id_counter += 1
            node.classes.append(cls)
            self.ejected_scripts.append(
                f'(function() {{\n'
                f'  document.querySelectorAll(".{cls}").forEach(function(btn) {{\n'
                f'    btn.addEventListener("click", function() {{\n'
                f'      var c = this.querySelector(".like-count");\n'
                f'      if (c) c.textContent = parseInt(c.textContent) + 1;\n'
                f'    }});\n'
                f'  }});\n'
                f'}})();'
            )

    @staticmethod
    def _parse_grid_params(params: str) -> dict:
        r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
        for p in params.split(','):
            p = p.strip()
            if '=' in p:
                k, v = p.split('=', 1)
                r[k.strip()] = v.strip()
        return r

    @staticmethod
    def _parse_waterfall_params(params: str) -> dict:
        r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
        for p in params.split(','):
            p = p.strip()
            if '=' in p:
                k, v = p.split('=', 1)
                r[k.strip()] = v.strip()
        return r

    # ══════════════════════════════════════════
    # 节点渲染
    # ══════════════════════════════════════════

    def _render_node(self, node: Node, indent: int):
        """将解析后的节点输出为 HTML"""
        pfx = self._prefix()
        attrs = []

        if node.id_attr:
            attrs.append(f'id="{node.id_attr}"')
        if node.classes:
            attrs.append(f'class="{" ".join(node.classes)}"')
        for k, v in node.attributes:
            if not v:
                attrs.append(k)
            else:
                attrs.append(f'{k}="{v}"')
        for k, v in node.behaviors:
            attrs.append(self._render_behavior(k, v))

        attr_str = ' ' + ' '.join(attrs) if attrs else ''
        tag = f'<{node.tag}{attr_str}>'

        if node.is_void:
            self.output_lines.append(f'{pfx}{tag}')
            return

        if node.text:
            self.output_lines.append(f'{pfx}{tag}{node.text}</{node.tag}>')
        else:
            self.output_lines.append(f'{pfx}{tag}')
            self.indent_stack.append((indent, node.tag))

    @staticmethod
    def _render_behavior(name: str, value: str) -> str:
        mapping = {
            'required': 'required',
            'email': 'type="email"',
            'url': 'type="url"',
        }
        if name in mapping:
            return mapping[name]
        if name == 'minlength':
            return f'minlength="{value}"'
        if name == 'maxlength':
            return f'maxlength="{value}"'
        if name == 'pattern':
            return f'pattern="{value}"'
        if name == 'range':
            parts = value.split(',')
            result = ''
            if len(parts) >= 1 and parts[0].strip():
                result += f'min="{parts[0].strip()}" '
            if len(parts) >= 2 and parts[1].strip():
                result += f'max="{parts[1].strip()}"'
            return result.strip()
        return ''

    # ══════════════════════════════════════════
    # 文件接口
    # ══════════════════════════════════════════

    def compile_file(self, input_path: str) -> str:
        with open(input_path, 'r', encoding='utf-8') as f:
            return self.compile(f.read())

    def compile_to_file(self, input_path: str, output_path: str):
        result = self.compile_file(input_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'✅ 编译完成: {input_path} → {output_path}')


# ══════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='LiteML Compiler — 编译 .lite 文件为标准 HTML/PHP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python liteml.py build index.lite -o index.html
  python liteml.py build index.lite --mode=php -o index.php
  python liteml.py build src/ -o dist/
  python liteml.py watch index.lite -o output.html
        """
    )

    sub = parser.add_subparsers(dest='command', help='子命令')

    # build
    bp = sub.add_parser('build', help='编译 .lite 文件')
    bp.add_argument('input', help='输入文件或目录')
    bp.add_argument('-o', '--output', help='输出路径')
    bp.add_argument('--mode', choices=['html', 'php', 'spa'], default='html')
    bp.add_argument('--target', choices=['react', 'htmx', 'alpine', 'vanilla'], default='vanilla')
    bp.add_argument('--eject', action='store_true', help='全局回退为原生代码')
    bp.add_argument('--watch', action='store_true', help='监听变化')

    # watch
    wp = sub.add_parser('watch', help='监听并自动编译')
    wp.add_argument('input', help='输入文件')
    wp.add_argument('-o', '--output', required=True, help='输出文件')
    wp.add_argument('--mode', choices=['html', 'php', 'spa'], default='html')

    sub.add_parser('version', help='显示版本')

    args = parser.parse_args()

    if args.command == 'version' or not args.command:
        print('LiteML Compiler v0.1')
        print('https://github.com/Zhao-Shengyi/LiteML')
        return

    if args.command == 'build':
        mode = Mode.PHP if args.mode == 'php' else Mode.HTML
        compiler = LiteMLCompiler(mode=mode)
        inp = args.input
        out = args.output or 'output.html'

        if os.path.isfile(inp):
            if not inp.endswith('.lite'):
                print(f'⚠️  跳过: {inp}')
                return
            compiler.compile_to_file(inp, out)

        elif os.path.isdir(inp):
            if not out or not os.path.isdir(out):
                os.makedirs(out, exist_ok=True)
            for root, dirs, files in os.walk(inp):
                for f in files:
                    if f.endswith('.lite'):
                        src = os.path.join(root, f)
                        rel = os.path.relpath(src, inp)
                        dst = os.path.join(out, rel.replace('.lite', '.html' if mode == Mode.HTML else '.php'))
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        compiler.compile_to_file(src, dst)

        if args.watch and os.path.isfile(inp):
            print(f'📡 监听: {inp}')
            last = os.path.getmtime(inp)
            try:
                while True:
                    time.sleep(1)
                    m = os.path.getmtime(inp)
                    if m != last:
                        last = m
                        compiler.compile_to_file(inp, out)
            except KeyboardInterrupt:
                print('\n👋 停止监听')

    elif args.command == 'watch':
        mode = Mode.PHP if args.mode == 'php' else Mode.HTML
        compiler = LiteMLCompiler(mode=mode)
        print(f'📡 监听: {args.input} → {args.output}')
        last = os.path.getmtime(args.input)
        try:
            while True:
                time.sleep(1)
                m = os.path.getmtime(args.input)
                if m != last:
                    last = m
                    compiler.compile_to_file(args.input, args.output)
        except KeyboardInterrupt:
            print('\n👋 停止监听')


if __name__ == '__main__':
    main()
