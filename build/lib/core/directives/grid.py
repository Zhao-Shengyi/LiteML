"""
@grid 指令：CSS Grid 网格布局
用法：div@grid(cols=3,gap=16px,mobile-cols=1)
"""

from ..directive_loader import directive


def _parse_grid_params(params: str) -> dict:
    r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
    for p in params.split(','):
        p = p.strip()
        if '=' in p:
            k, v = p.split('=', 1)
            r[k.strip()] = v.strip()
    return r


@directive('grid')
def handle_grid(node, params: str, state: dict):
    """给节点加上 CSS Grid 样式并注入响应式规则"""
    grid = _parse_grid_params(params)
    counter = state['id_counter']
    cls = f'eject-grid-{counter}'
    state['id_counter'] = counter + 1

    node.classes.append(cls)
    state['ejected_styles'].append(
        f'.{cls} {{\n'
        f'  display: grid;\n'
        f'  grid-template-columns: repeat({grid["cols"]}, 1fr);\n'
        f'  gap: {grid["gap"]};\n'
        f'}}\n'
        f'@media (max-width: 768px) {{\n'
        f'  .{cls} {{\n'
        f'    grid-template-columns: repeat({grid["mobile-cols"]}, 1fr);\n'
        f'  }}\n'
        f'}}'
    )
