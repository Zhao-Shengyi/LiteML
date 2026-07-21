"""
LiteML 编译常量
"""

from enum import Enum
from typing import Set


# ── 自闭合标签（Void Elements） ──
VOID_ELEMENTS: Set[str] = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}

# ── PHP 指令 → 闭合关键字 ──
PHP_CLOSE_MAP: dict = {
    '@if': 'endif',
    '@elseif': 'endif',
    '@else': 'endif',
    '@foreach': 'endforeach',
    '@while': 'endwhile',
    '@for': 'endfor',
}


class Mode(Enum):
    """编译模式"""
    HTML = 'html'
    PHP = 'php'


class AssetMode(Enum):
    """CSS/JS 输出策略"""
    INLINE = 'inline'       # 内联到 HTML 中 (默认)
    EXTERNAL = 'external'   # 输出到独立文件
