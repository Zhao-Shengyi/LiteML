"""
@position 指令：CSS 定位
用法：div@position(fixed,top=0,left=0)
"""

from ..directive_loader import directive


@directive('position')
def handle_position(node, params: str, state: dict):
    """给节点加上 position 定位样式"""
    parts = [p.strip() for p in params.split(',') if p.strip()]
    css = ''
    for p in parts:
        if '=' in p:
            css += f' {p.replace("=", ": ")};'
        else:
            css += f' position: {p};'
    node.attributes.append(('style', css.strip()))
