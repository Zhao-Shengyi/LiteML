"""
LiteML 内置指令处理器

负责处理 @ 开头的各类指令（宏、布局、行为等），
纯函数风格，不持有编译器状态。
"""

import re
from typing import List, Tuple

from .models import Node


# ──────────────────────────────────────────────
# 宏指令：独立使用，非标签附加
# ──────────────────────────────────────────────

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

    # @flex(params) — 单独使用
    m = re.match(r'@flex\(([^)]*)\)$', content)
    if m:
        css = _parse_flex_params(m.group(1))
        lines.append(f'{prefix}<div style="{css}">')
        return lines

    return lines


# ──────────────────────────────────────────────
# 标签指令：附加在标签上的 @directive
# ──────────────────────────────────────────────

def apply_directive(node: Node, dir_name: str, params: str,
                    id_counter: int,
                    ejected_styles: List[str],
                    ejected_scripts: List[str]) -> int:
    """对节点应用指令（如 @flex, @grid, @modal 等）。
    返回新的 id_counter（可能自增过）。"""
    counter = id_counter

    if dir_name == 'flex':
        css = _parse_flex_params(params)
        node.attributes.append(('style', css))

    elif dir_name == 'grid':
        grid = _parse_grid_params(params)
        cls = f'eject-grid-{counter}'
        counter += 1
        node.classes.append(cls)
        ejected_styles.append(
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

    elif dir_name == 'waterfall':
        wf = _parse_waterfall_params(params)
        cls = f'eject-waterfall-{counter}'
        counter += 1
        node.classes.append(cls)
        ejected_styles.append(
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

    elif dir_name == 'modal':
        modal_id = ''
        if params.startswith('open='):
            modal_id = params.split('=', 1)[1].strip().strip('"\'')
        if modal_id:
            btn_id = f'btn-modal-{counter}'
            counter += 1
            node.attributes.append(('id', btn_id))
            ejected_scripts.append(
                f'(function() {{\n'
                f'  document.getElementById("{btn_id}").addEventListener("click", function() {{\n'
                f'    document.querySelector("{modal_id}").showModal();\n'
                f'  }});\n'
                f'  document.querySelector("{modal_id}").addEventListener("click", function(e) {{\n'
                f'    if (e.target === this) this.close();\n'
                f'  }});\n'
                f'}})();'
            )

    elif dir_name == 'theme-toggle':
        # 暗色模式切换按钮 — 一行内联 JS 搞定
        node.attributes.append(('onclick',
            "var t=document.documentElement.dataset;"
            "t.theme=t.theme==='dark'?'light':'dark';"
            "localStorage.setItem('theme',t.theme);"
        ))

    elif dir_name == 'position':
        parts = [p.strip() for p in params.split(',') if p.strip()]
        css = ''
        for p in parts:
            if '=' in p:
                css += f' {p.replace("=", ": ")};'
            else:
                css += f' position: {p};'
        node.attributes.append(('style', css.strip()))

    elif dir_name == 'transition':
        node.attributes.append(('style', f'transition: {params.strip()}'))

    elif dir_name == 'hide':
        device = params.strip()
        media_map = {
            'mobile': '(max-width: 768px)',
            'tablet': '(min-width: 769px) and (max-width: 1024px)',
            'desktop': '(min-width: 1025px)',
        }
        media = media_map.get(device, device)
        cls = f'eject-hide-{counter}'
        counter += 1
        node.classes.append(cls)
        ejected_styles.append(
            f'@media {media} {{\n'
            f'  .{cls} {{ display: none !important; }}\n'
            f'}}'
        )

    elif dir_name == 'like':
        cls = f'eject-like-{counter}'
        counter += 1
        node.classes.append(cls)
        ejected_scripts.append(
            f'(function() {{\n'
            f'  document.querySelectorAll(".{cls}").forEach(function(btn) {{\n'
            f'    btn.addEventListener("click", function() {{\n'
            f'      var c = this.querySelector(".like-count");\n'
            f'      if (c) c.textContent = parseInt(c.textContent) + 1;\n'
            f'    }});\n'
            f'  }});\n'
            f'}})();'
        )

    return counter


# ──────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────

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


def _parse_grid_params(params: str) -> dict:
    """解析 @grid(cols=3,gap=16px,mobile-cols=1)"""
    r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
    for p in params.split(','):
        p = p.strip()
        if '=' in p:
            k, v = p.split('=', 1)
            r[k.strip()] = v.strip()
    return r


def _parse_waterfall_params(params: str) -> dict:
    """解析 @waterfall(cols=3,gap=16px,mobile-cols=1)"""
    r = {'cols': '3', 'gap': '16px', 'mobile-cols': '1'}
    for p in params.split(','):
        p = p.strip()
        if '=' in p:
            k, v = p.split('=', 1)
            r[k.strip()] = v.strip()
    return r


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
