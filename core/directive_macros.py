"""
LiteML 宏指令处理器

负责 @audio, @video, @embed, @icon, @css(src), @js(src), @flex(独立使用)
这些"直接转成原生 HTML 标签"的宏指令。

⚠️ 标签附加指令（@grid, @modal, @theme-toggle 等）已拆分到 directives/ 目录下。
"""

import os
import re
from typing import List


def render_macro(content: str, prefix: str) -> List[str]:
    """处理独立使用的 @ 宏指令。
    @audio, @video, @embed, @css(src), @js(src), @flex, @icon 等。
    返回输出行列表。"""
    lines: List[str] = []

    # @css(src)
    m = re.match(r'@css\(([^)]+)\)$', content)
    if m:
        href = m.group(1).strip().strip('"\'')
        lines.append(f'{prefix}<link rel="stylesheet" href="{href}">')
        return lines

    # @js(src | attrs)
    m = re.match(r'@js\(([^)]+)\)$', content)
    if m:
        parts = [p.strip() for p in m.group(1).split('|')]
        src = parts[0].strip().strip('"\'')
        attrs = ''
        if len(parts) > 1:
            for a in parts[1].split(','):
                a = a.strip()
                if '=' in a:
                    k, v = a.split('=', 1)
                    attrs += f' {k.strip()}="{v.strip()}"'
                else:
                    attrs += f' {a}'
        lines.append(f'{prefix}<script src="{src}"{attrs}></script>')
        return lines

    # @audio
    m = re.match(r'@audio\(([^)]+)\)$', content)
    if m:
        args = m.group(1)
        parts = args.split('|')
        sources = [s.strip().strip('"\'') for s in parts[0].split(',')]
        attrs = ''
        if len(parts) > 1:
            for a in parts[1].split(','):
                a = a.strip()
                if '=' in a:
                    k, v = a.split('=', 1)
                    attrs += f' {k.strip()}="{v.strip()}"'
                else:
                    attrs += f' {a}'
        if len(sources) == 1:
            lines.append(f'{prefix}<audio src="{sources[0]}"{attrs}></audio>')
        else:
            srcs = ''.join(f'<source src="{s}">' for s in sources)
            lines.append(f'{prefix}<audio{attrs}>{srcs}</audio>')
        return lines

    # @video
    m = re.match(r'@video\(([^)]+)\)$', content)
    if m:
        args = m.group(1)
        parts = args.split('|')
        sources = [s.strip().strip('"\'') for s in parts[0].split(',')]
        attrs = ''
        if len(parts) > 1:
            for a in parts[1].split(','):
                a = a.strip()
                if '=' in a:
                    k, v = a.split('=', 1)
                    attrs += f' {k.strip()}="{v.strip()}"'
                else:
                    attrs += f' {a}'
        if len(sources) == 1:
            lines.append(f'{prefix}<video src="{sources[0]}"{attrs}></video>')
        else:
            srcs = ''.join(f'<source src="{s}">' for s in sources)
            lines.append(f'{prefix}<video{attrs}>{srcs}</video>')
        return lines

    # @embed(url | ratio=16:9)
    m = re.match(r'@embed\(([^)]+)\)$', content)
    if m:
        parts = [p.strip() for p in m.group(1).split('|')]
        url = parts[0].strip().strip('"\'')
        ratio = parts[1].strip().split('=')[1] if len(parts) > 1 and '=' in parts[1] else '16:9'
        pad = _ratio_to_padding(ratio)
        lines.append(f'{prefix}<div style="position:relative;padding-bottom:{pad};height:0;overflow:hidden;">')
        lines.append(f'{prefix}  <iframe src="{url}" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" frameborder="0" allowfullscreen></iframe>')
        lines.append(f'{prefix}</div>')
        return lines

    # @icon
    m = re.match(r'@icon\(([^)]+)\)$', content)
    if m:
        name = m.group(1).strip()
        lines.append(f'{prefix}<i class="icon-{name}"></i>')
        return lines

    # @flex(params) - 独立使用
    m = re.match(r'@flex\(([^)]*)\)$', content)
    if m:
        css = _parse_flex_params(m.group(1))
        lines.append(f'{prefix}<div style="{css}">')
        return lines

    # @template(name) — 引用 CSS 模板（从 templates/name/theme.css 读取）
    m = re.match(r'@template\(([^)]+)\)$', content)
    if m:
        name = m.group(1).strip().strip('"\'')
        template_path = os.path.join('templates', name, 'theme.css')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            lines.append(f'{prefix}<style>')
            for cl in css_content.split('\n'):
                lines.append(f'{prefix}{cl}')
            lines.append(f'{prefix}</style>')
        except FileNotFoundError:
            lines.append(f'{prefix}<!-- ⚠️ 模板 "{name}" 未找到 → templates/{name}/theme.css -->')
        return lines

    return lines


def render_behavior(name: str, value: str) -> str:
    """将 [*behavior] 转为 HTML 属性"""
    mapping = {
        'required': 'required',
        'email': 'type="email"',
        'url': 'type="url"',
    }
    if name in mapping:
        return mapping[name]
    if name == 'minlength':
        return f'minlength="{value}"'
    if name == 'maxlength':
        return f'maxlength="{value}"'
    if name == 'pattern':
        return f'pattern="{value}"'
    if name == 'range':
        parts = value.split(',')
        result = ''
        if len(parts) >= 1 and parts[0].strip():
            result += f'min="{parts[0].strip()}" '
        if len(parts) >= 2 and parts[1].strip():
            result += f'max="{parts[1].strip()}"'
        return result.strip()
    return ''


def _ratio_to_padding(ratio: str) -> str:
    """将 '16:9' 转为 CSS padding-bottom 百分比"""
    try:
        w, h = ratio.split(':')
        return f'{float(h) / float(w) * 100}%'
    except (ValueError, IndexError):
        return '56.25%'


def _parse_flex_params(params: str) -> str:
    """解析 @flex(align,justify) 参数为 CSS"""
    align_map = {'start': 'flex-start', 'end': 'flex-end',
                 'center': 'center', 'stretch': 'stretch'}
    justify_map = {'start': 'flex-start', 'end': 'flex-end',
                   'center': 'center', 'between': 'space-between',
                   'around': 'space-around', 'evenly': 'space-evenly'}
    parts = [p.strip() for p in params.split(',') if p.strip()]
    css = 'display: flex;'
    if len(parts) >= 1 and parts[0]:
        css += f' align-items: {align_map.get(parts[0], parts[0])};'
    if len(parts) >= 2 and parts[1]:
        css += f' justify-content: {justify_map.get(parts[1], parts[1])};'
    return css
