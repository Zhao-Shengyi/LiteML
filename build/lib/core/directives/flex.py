"""
@flex 指令：Flexbox 布局
用法：div@flex(align,justify) 或 div@flex(center,between)
"""

from ..directive_loader import directive

# 对齐方式映射
_ALIGN_MAP = {
    'start': 'flex-start', 'end': 'flex-end',
    'center': 'center', 'stretch': 'stretch',
}
_JUSTIFY_MAP = {
    'start': 'flex-start', 'end': 'flex-end',
    'center': 'center', 'between': 'space-between',
    'around': 'space-around', 'evenly': 'space-evenly',
}


@directive('flex')
def handle_flex(node, params: str, state: dict):
    """给节点加上 display:flex 样式"""
    parts = [p.strip() for p in params.split(',') if p.strip()]
    css = 'display: flex;'
    if len(parts) >= 1 and parts[0]:
        css += f' align-items: {_ALIGN_MAP.get(parts[0], parts[0])};'
    if len(parts) >= 2 and parts[1]:
        css += f' justify-content: {_JUSTIFY_MAP.get(parts[1], parts[1])};'
    node.attributes.append(('style', css))
