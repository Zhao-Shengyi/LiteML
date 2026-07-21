"""
LiteML 编译核心

负责将 .lite 源码编译为 HTML/PHP。
使用 parser 进行行解析，使用 directives 处理指令。
"""

import os
import re
import time
from typing import List, Optional, Tuple

from .constants import VOID_ELEMENTS, PHP_CLOSE_MAP, Mode, AssetMode
from .models import Node
from .parser import (
    preprocess_blocks, decode_block, try_parse_code_block,
    classify_line, parse_tag_line,
    parse_include_path, parse_eject_component, parse_use_component,
)
from .directive_macros import render_macro, render_behavior
from .directive_loader import get_handler, discover as discover_directives
from .component import ComponentLoader

# 启动时自动发现所有指令插件
discover_directives()


class LiteMLCompiler:
    """
    LiteML 编译器核心
    将 .lite 源码编译为 HTML/PHP

    Args:
        mode: 编译模式（HTML / PHP）
        asset_mode: CSS/JS 输出策略（inline / external）
        components_dir: 组件目录路径
    """

    def __init__(
        self,
        mode: Mode = Mode.HTML,
        asset_mode: AssetMode = AssetMode.INLINE,
        components_dir: str = 'components',
    ):
        self.mode = mode
        self.asset_mode = asset_mode
        self.component_loader = ComponentLoader(components_dir)

        # 编译状态
        self.output_lines: List[str] = []
        self.indent_stack: List[Tuple[int, str]] = []
        self.id_counter: int = 0
        self.ejected_styles: List[str] = []
        self.ejected_scripts: List[str] = []

        # 外部文件模式收集的 CSS/JS
        self.external_styles: List[str] = []
        self.external_scripts: List[str] = []

    # ══════════════════════════════════════════
    # 编译入口
    # ══════════════════════════════════════════

    def compile(self, source: str) -> str:
        """接收 LiteML 源码字符串，返回编译后的 HTML/PHP"""
        lines = source.split('\n')
        self._reset_state()

        # 预处理：合并多行块
        blocks = preprocess_blocks(lines)

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

            line_type = classify_line(content)

            if line_type == 'doctype':
                self.output_lines.append('<!DOCTYPE html>')

            elif line_type == 'comment':
                pfx = self._prefix()
                self.output_lines.append(f'{pfx}<!-- {content[1:].strip()} -->')

            elif line_type == 'php_ctrl':
                self._handle_php_ctrl(content, indent)

            elif line_type == 'include':
                pfx = self._prefix()
                path = parse_include_path(content)
                self.output_lines.append(f'{pfx}{self._handle_include(path)}')

            elif line_type == 'php_block':
                self._collect_php_block(blocks, i + 1, indent)
                i = self._skip_block_lines(blocks, i + 1, indent)

            elif line_type == 'raw_block':
                self._collect_raw_block(blocks, i + 1, indent)
                i = self._skip_block_lines(blocks, i + 1, indent)

            elif line_type in ('style_block', 'script_block'):
                self._collect_asset_block(content, blocks, i + 1, indent)
                i = self._skip_block_lines(blocks, i + 1, indent)

            elif line_type == 'eject':
                comp = parse_eject_component(content)
                self._handle_eject(comp)

            elif line_type == 'text_block':
                text = content[3:-3] if content.endswith('"""') else content[3:]
                text = decode_block(text)
                self._emit_long_text(text)

            elif line_type == 'code_block':
                _, lang, code = try_parse_code_block(content)
                pfx = self._prefix()
                code = decode_block(code)
                if lang:
                    self.output_lines.append(f'{pfx}<pre><code class="language-{lang}">')
                else:
                    self.output_lines.append(f'{pfx}<pre><code>')
                for cl in code.split('\n'):
                    self.output_lines.append(f'{pfx}{cl}')
                self.output_lines.append(f'{pfx}</code></pre>')

            elif line_type == 'use_comp':
                comp_name = parse_use_component(content)
                self._handle_use_component(comp_name, indent)

            elif line_type == 'macro':
                pfx = self._prefix()
                lines_out = render_macro(content, pfx)
                self.output_lines.extend(lines_out)

            elif line_type == 'raw_html':
                self.output_lines.append(raw_line.rstrip())

            elif line_type == 'tag':
                self._process_tag_line(content, indent)

            else:
                # 兜底
                self.output_lines.append(raw_line.rstrip())

            i += 1

        # 关闭所有剩余标签
        self._close_all()

        # 组装最终输出
        return self._finalize_output()

    def _reset_state(self):
        """重置编译器状态，供每次 compile 调用"""
        self.output_lines = []
        self.indent_stack = []
        self.ejected_styles = []
        self.ejected_scripts = []
        self.external_styles = []
        self.external_scripts = []
        self.id_counter = 0

    # ══════════════════════════════════════════
    # 缩进与栈管理
    # ══════════════════════════════════════════

    def _prefix(self) -> str:
        return '  ' * len(self.indent_stack)

    def _close_to_indent(self, target_indent: int):
        while self.indent_stack and self.indent_stack[-1][0] >= target_indent:
            top_indent, top_tag = self.indent_stack[-1]
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

    def _handle_php_ctrl(self, content: str, indent: int):
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

        m = re.match(r'@(if|foreach|while|for)\((.+)\)$', content)
        if m:
            directive = m.group(1)
            condition = m.group(2)
            if self.indent_stack and self.indent_stack[-1][1] in ('@else', '@elseif'):
                self._close_to_indent(self.indent_stack[-1][0])
            pfx = self._prefix()
            self.output_lines.append(f'{pfx}<?php {directive}({condition}): ?>')
            self.indent_stack.append((indent, f'@{directive}'))

    # ══════════════════════════════════════════
    # 块收集
    # ══════════════════════════════════════════

    def _collect_php_block(self, blocks: List[str], start: int, indent: int):
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
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            self.output_lines.append(blocks[i].rstrip())
            i += 1

    def _collect_asset_block(self, directive: str, blocks: List[str],
                              start: int, indent: int):
        """收集 @css / @js 内联块内容"""
        pfx = self._prefix()
        lines = []
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            line = nxt
            is_code, lang, code = try_parse_code_block(line.strip())
            if is_code:
                line = decode_block(code)
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

    @staticmethod
    def _skip_block_lines(blocks: List[str], start: int, indent: int) -> int:
        """跳过块内容行，返回最后索引"""
        i = start
        while i < len(blocks):
            nxt = blocks[i]
            ni = len(nxt) - len(nxt.lstrip())
            if ni <= indent and nxt.strip():
                break
            i += 1
        return i - 1

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
    # @use 组件
    # ══════════════════════════════════════════

    def _handle_use_component(self, name: str, indent: int):
        """处理 @use 组件引用"""
        comp = self.component_loader.load(name)
        if not comp:
            pfx = self._prefix()
            self.output_lines.append(f'{pfx}<!-- 组件未找到: {name} -->')
            return

        pfx = self._prefix()

        # 输出模板
        if comp.template:
            for tpl_line in comp.template.split('\n'):
                self.output_lines.append(f'{pfx}{tpl_line}')

        # 收集 CSS
        if comp.style:
            if self.asset_mode == AssetMode.EXTERNAL:
                self.external_styles.append(comp.style)
            else:
                self.ejected_styles.append(comp.style)

        # 收集 JS
        if comp.script:
            if self.asset_mode == AssetMode.EXTERNAL:
                self.external_scripts.append(comp.script)
            else:
                self.ejected_scripts.append(comp.script)

    # ══════════════════════════════════════════
    # @eject
    # ══════════════════════════════════════════

    def _handle_eject(self, component: str):
        """处理 @eject (内置组件回退)"""
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
        paragraphs = re.split(r'\n\s*\n', text.strip())
        pfx = self._prefix()
        for para in paragraphs:
            para = ' '.join(para.split('\n')).strip()
            if para:
                if self.mode == Mode.PHP:
                    para = self._interpolate(para)
                self.output_lines.append(f'{pfx}<p>{para}</p>')

    # ══════════════════════════════════════════
    # PHP 插值
    # ══════════════════════════════════════════

    def _interpolate(self, text: str) -> str:
        text = re.sub(r'\{\{(.+?)\}\}', r'<?php echo htmlspecialchars(\1); ?>', text)
        text = re.sub(r'\{\!(.+?)\!\}', r'<?php echo \1; ?>', text)
        return text

    # ══════════════════════════════════════════
    # 标签处理
    # ══════════════════════════════════════════

    def _process_tag_line(self, content: str, indent: int):
        """解析并渲染一行标签"""
        node = parse_tag_line(content)
        if not node.tag:
            self.output_lines.append(f'{self._prefix()}{content}')
            return

        # 处理标签上的指令（通过 directive_loader 插件系统）
        if node.directives:
            state = {
                'id_counter': self.id_counter,
                'ejected_styles': self.ejected_styles,
                'ejected_scripts': self.ejected_scripts,
                'mode': self.mode,
            }
            for (dir_name, dir_params, eject) in node.directives:
                handler = get_handler(dir_name)
                if handler:
                    handler(node, dir_params, state)
                else:
                    # 未注册的指令 — 按原名输出（容错）
                    pass
            self.id_counter = state['id_counter']

        # PHP 插值处理
        if self.mode == Mode.PHP:
            node.text = self._interpolate(node.text)
            node.attributes = [
                (k, self._interpolate(v) if '{{' in v else v)
                for k, v in node.attributes
            ]

        self._render_node(node, indent)

    # ══════════════════════════════════════════
    # 节点渲染
    # ══════════════════════════════════════════

    def _render_node(self, node: Node, indent: int):
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
            attrs.append(render_behavior(k, v))

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

    # ══════════════════════════════════════════
    # 最终输出组装
    # ══════════════════════════════════════════

    def _finalize_output(self) -> str:
        result = '\n'.join(self.output_lines)

        # 注入 CSS
        if self.ejected_styles:
            css_block = '\n'.join(self.ejected_styles)
            result = re.sub(
                r'([ \t]*)</head>',
                lambda m: (m.group(1) + '<style>\n' + css_block + '\n'
                           + m.group(1) + '</style>\n' + m.group(1) + '</head>'),
                result
            )

        # 注入 JS（放在 </body> 前）
        if self.ejected_scripts:
            js_block = '\n'.join(self.ejected_scripts)
            script_tag = f'<script>\n{js_block}\n</script>'
            if '</body>' in result:
                result = result.replace('</body>', f'{script_tag}\n</body>')
            else:
                result += '\n' + script_tag

        return result

    # ══════════════════════════════════════════
    # 文件接口
    # ══════════════════════════════════════════

    def compile_file(self, input_path: str) -> str:
        with open(input_path, 'r', encoding='utf-8') as f:
            return self.compile(f.read())

    def compile_to_file(self, input_path: str, output_path: str):
        result = self.compile_file(input_path)
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'✅ 编译完成: {input_path} → {output_path}')

        # 外部文件模式：输出独立的 CSS/JS
        if self.asset_mode == AssetMode.EXTERNAL:
            self._write_external_assets(output_path)

    def _write_external_assets(self, output_path: str):
        """输出外部 CSS/JS 文件"""
        base = os.path.splitext(output_path)[0]

        if self.external_styles:
            css_path = base + '.components.css'
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(self.external_styles))
            print(f'  📄 组件样式: {css_path}')

        if self.external_scripts:
            js_path = base + '.components.js'
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(self.external_scripts))
            print(f'  📄 组件脚本: {js_path}')
