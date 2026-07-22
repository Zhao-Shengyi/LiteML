"""
LiteML 语法解析器

职责：
1. 预处理多行块（长文本、代码块）
2. 行类型分类（doctype, tag, directive, PHP控制流等）
3. 标签行解析（tag#id.class[attr] 语法）
"""

import re
from typing import List, Tuple

from .models import Node, ParsedLine
from .constants import VOID_ELEMENTS


# ──────────────────────────────────────────────
# 预处理：将多行块合并为单行标记
# ──────────────────────────────────────────────

def preprocess_blocks(lines: List[str]) -> List[str]:
    """
    Merge long text ('''...''') and code blocks (```...```) into single-line markers,
    将长文本和代码块合并为单行标记，避免被逐行解析。
    块内换行用 \\x00 编码，后续解码。
    """
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 长文本块
        if stripped.startswith('"""'):
            indent = len(line) - len(line.lstrip())
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('"""'):
                block.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # 跳过结束 """
            encoded = ' ' * indent + '"""' + _encode_block('\n'.join(block)) + '"""'
            result.append(encoded)
            continue

        # 代码块
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
            encoded = ' ' * indent + '``' + lang + '`' + _encode_block('\n'.join(block)) + '````'
            result.append(encoded)
            continue

        result.append(line)
        i += 1

    return result


def _encode_block(text: str) -> str:
    """将块内换行编码为 \x00"""
    return text.replace('\n', '\x00')


def decode_block(text: str) -> str:
    """解码块内的换行符"""
    return text.replace('\x00', '\n')


def try_parse_code_block(content: str) -> Tuple[bool, str, str]:
    """尝试解析编码后的代码块标记。返回 (is_match, lang, encoded_content)"""
    m = re.match(r'^``(.+?)`(.+)````$', content)
    if m:
        return True, m.group(1).strip(), m.group(2)
    return False, '', ''


# ──────────────────────────────────────────────
# 行类型分类
# ──────────────────────────────────────────────

# PHP 控制流指令集合
PHP_DIRECTIVES = {'@if', '@elseif', '@else', '@foreach', '@while', '@for'}


def classify_line(content: str, line_number: int = 0) -> str:
    """识别行类型，返回类型标识字符串。
    类型列表（按优先级）：
      empty        — 空行
      doctype      — ! html5 (仅第 1 行)
      comment      — ! 或 @ 开头（后跟空格）
      php_ctrl     — @if/@foreach 等
      include      — @include(...)
      php_block    — @php
      raw_block    — @raw
      css_block    — @css (内联块)
      js_block     — @js (内联块)
      eject        — @eject(...)
      text_block   — '''...''' (长文本块)
      code_block   - ```...``` (代码块)
      macro        — @xxx(...) 宏指令
      use_comp     — use xxx 或 @use xxx 组件引用
      raw_html     — < 开头的原生 HTML
      tag          — 普通标签行
    """
    if not content:
        return 'empty'

    # ! html5 — 仅第一行视为 doctype
    if content == '! html5' and line_number == 0:
        return 'doctype'

    # ! 开头的注释（不在第一行时）
    if content.startswith('! '):
        return 'comment'

    # @ 开头的注释（向后兼容）
    if content.startswith('@ ') or content.startswith('@\t'):
        return 'comment'

    if _is_php_ctrl(content):
        return 'php_ctrl'

    if content.startswith('@include('):
        return 'include'

    if content == '@php':
        return 'php_block'

    if content == '@raw':
        return 'raw_block'

    if content in ('@css', '@js'):
        return 'style_block' if content == '@css' else 'script_block'

    if content.startswith('@eject('):
        return 'eject'

    if content.startswith('"""'):
        return 'text_block'

    is_code, _, _ = try_parse_code_block(content)
    if is_code:
        return 'code_block'

    if content.startswith('use ') or content.startswith('@use '):
        return 'use_comp'

    if content.startswith('@') and not content.startswith('@@'):
        return 'macro'

    if content.startswith('<'):
        return 'raw_html'

    # 普通标签行：标签名或 .class / #id 简写（省略标签名时默认为 div）
    if re.match(r'^[a-zA-Z.#]', content):
        return 'tag'

    # 兜底：作为原始内容输出
    return 'raw_html'


def _is_php_ctrl(content: str) -> bool:
    for d in PHP_DIRECTIVES:
        if content.startswith(d):
            return True
    return False


# ──────────────────────────────────────────────
# 标签行解析
# ──────────────────────────────────────────────

def parse_tag_line(content: str) -> Node:
    """
    解析一行标签语法：
      tag#id.class1.class2[attr=val][*behavior] text
      tag@directive(params)[attr=val] text
      tag@directive! ...    ← 回退模式
    返回 Node 结构体。
    """
    node = Node()
    remaining = content

    # 提取标签名
    m = re.match(r'^([a-zA-Z][\w-]*)', remaining)
    if not m:
        # 没有显式标签名，但以 . 或 # 开头 → 默认为 div
        if remaining.startswith(('.', '#')):
            node.tag = 'div'
        else:
            return node
    else:
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
        # 指令数据暂存到 node.directives，后续由编译器调用 apply_directive
        node.directives = [(dir_name, dir_params, node.eject)]

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
                # 去掉值两端的引号（单引号或双引号）
                v = v.strip().strip('"\'')
                node.attributes.append((k.strip(), v.strip()))
            else:
                node.attributes.append((attr_content.strip(), ''))

    # 剩余文本
    node.text = remaining.strip()

    return node


def parse_include_path(content: str) -> str:
    """从 @include(path) 中提取路径"""
    m = re.match(r'@include\(([^)]+)\)', content)
    if m:
        return m.group(1).strip().strip('"\'')
    return ''


def parse_eject_component(content: str) -> str:
    """从 @eject(name) 中提取组件名"""
    m = re.match(r'@eject\(([^)]+)\)', content)
    if m:
        return m.group(1).strip()
    return ''


def parse_use_component(content: str) -> str:
    """从 use xxx 或 @use xxx 中提取组件名"""
    if content.startswith('@use '):
        # 向后兼容: @use component
        return content[5:].strip()
    # 新语法: use component
    return content[4:].strip()
