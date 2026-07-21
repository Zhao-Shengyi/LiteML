"""
@waterfall 指令：瀑布流 / Masonry 布局
用法：div@waterfall(cols=4,gap=12px,mobile-cols=1)
"""

from ..directive_loader import directive


def _parse_waterfall_params(params: str) -> dict:
    r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
    for p in params.split(','):
        p = p.strip()
        if '=' in p:
            k, v = p.split('=', 1)
            r[k.strip()] = v.strip()
    return r


@directive('waterfall')
def handle_waterfall(node, params: str, state: dict):
    """给节点加上瀑布流 CSS (column-count) 并注入响应式规则"""
    wf = _parse_waterfall_params(params)
    counter = state['id_counter']
    cls = f'eject-waterfall-{counter}'
    state['id_counter'] = counter + 1

    node.classes.append(cls)
    state['ejected_styles'].append(
        f'.{cls} {{\n'
        f'  column-count: {wf["cols"]};\n'
        f'  column-gap: {wf["gap"]};\n'
        f'}}\n'
        f'.{cls} > * {{\n'
        f'  break-inside: avoid;\n'
        f'  margin-bottom: {wf["gap"]};\n'
        f'}}\n'
        f'@media (max-width: 768px) {{\n'
        f'  .{cls} {{\n'
        f'    column-count: {wf["mobile-cols"]};\n'
        f'  }}\n'
        f'}}'
    )
