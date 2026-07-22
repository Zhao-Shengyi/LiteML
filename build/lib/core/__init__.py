"""
LiteML — 轻量级 HTML/PHP 模板语言编译器
"""

__version__ = '0.2.0'

from .compiler import LiteMLCompiler
from .constants import Mode, AssetMode
from .component import ComponentLoader

# 自动发现指令插件
from .directive_loader import discover as _discover
_discover()
