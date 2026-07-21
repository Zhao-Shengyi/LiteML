"""
@transition 指令：CSS 过渡动画
用法：div@transition(all 0.3s ease)
"""

from ..directive_loader import directive


@directive('transition')
def handle_transition(node, params: str, state: dict):
    """给节点加上 transition 样式"""
    node.attributes.append(('style', f'transition: {params.strip()}'))
