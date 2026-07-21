"""
@hide 指令：响应式隐藏
用法：div@hide(mobile)  — 在手机端隐藏
     div@hide(tablet)  — 在平板端隐藏
     div@hide(desktop) — 在桌面端隐藏
"""

from ..directive_loader import directive

_MEDIA_MAP = {
    'mobile': '(max-width: 768px)',
    'tablet': '(min-width: 769px) and (max-width: 1024px)',
    'desktop': '(min-width: 1025px)',
}


@directive('hide')
def handle_hide(node, params: str, state: dict):
    """给节点加上响应式隐藏的 CSS"""
    device = params.strip()
    media = _MEDIA_MAP.get(device, device)

    counter = state['id_counter']
    cls = f'eject-hide-{counter}'
    state['id_counter'] = counter + 1

    node.classes.append(cls)
    state['ejected_styles'].append(
        f'@media {media} {{\n'
        f'  .{cls} {{ display: none !important; }}\n'
        f'}}'
    )
