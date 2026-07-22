"""
LiteML 数据结构定义
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Node:
    """单个标签行解析后的结构化数据"""
    tag: str = ''
    id_attr: str = ''
    classes: List[str] = field(default_factory=list)
    attributes: List[Tuple[str, str]] = field(default_factory=list)
    text: str = ''
    directives: List[str] = field(default_factory=list)
    behaviors: List[Tuple[str, str]] = field(default_factory=list)
    is_void: bool = False
    eject: bool = False


@dataclass
class ParsedLine:
    """解析后的单行数据结构"""
    indent: int = 0
    raw: str = ''           # 原始行内容
    content: str = ''       # 去除缩进后的内容
    line_type: str = ''     # 行类型标识

    # 不同类型携带的额外数据
    tag: str = ''           # 标签名 (tag 类型)
    node: Node = field(default_factory=Node)  # 完整标签节点 (tag 类型)


@dataclass
class ComponentInfo:
    """从 components/ 目录加载的组件信息"""
    name: str
    dir_path: str
    template: str = ''       # 模板 HTML 内容
    style: str = ''          # CSS 内容
    script: str = ''         # JS 内容
