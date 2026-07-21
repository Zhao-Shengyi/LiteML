"""
@theme-toggle 指令：暗色模式切换
用法：button@theme-toggle  (无需参数)
"""

from ..directive_loader import directive


@directive('theme-toggle')
def handle_theme_toggle(node, params: str, state: dict):
    """给按钮添加一键切换暗色模式的内联 JS"""
    node.attributes.append(('onclick',
        "var t=document.documentElement.dataset;"
        "t.theme=t.theme==='dark'?'light':'dark';"
        "localStorage.setItem('theme',t.theme);"
    ))
