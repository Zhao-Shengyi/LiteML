#!/usr/bin/env python3
"""
LiteML CLI — 命令行编译器

用法:
    python core/cli.py build input.lite -o output.html
    python core/cli.py build input.lite --mode=php -o output.php
    python core/cli.py build src/ -o dist/
    python core/cli.py watch input.lite -o output.html
    python core/cli.py components list
    python core/cli.py components init 组件名
    python core/cli.py version
"""

import argparse
import os
import sys
import time

# 确保能找到 core 包（兼容从项目根直接运行 python core/cli.py）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import Mode, AssetMode
from core.compiler import LiteMLCompiler
from core.component import ComponentLoader


def main():
    parser = argparse.ArgumentParser(
        description='LiteML Compiler — 编译 .lite 文件为标准 HTML/PHP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python core/cli.py build index.lite -o index.html
  python core/cli.py build index.lite --mode=php -o index.php
  python core/cli.py build index.lite --css=inline --js=external -o dist/
  python core/cli.py build src/ -o dist/
  python core/cli.py watch index.lite -o output.html
  python core/cli.py components list
  python core/cli.py components init dark-mode-toggle
        """
    )

    sub = parser.add_subparsers(dest='command', help='子命令')

    # ── build ──
    bp = sub.add_parser('build', help='编译 .lite 文件')
    bp.add_argument('input', help='输入文件或目录')
    bp.add_argument('-o', '--output', help='输出路径')
    bp.add_argument('--mode', choices=['html', 'php'], default='html',
                    help='编译模式 (默认 html)')
    bp.add_argument('--css', choices=['inline', 'external'], default='inline',
                    help='CSS 输出策略: inline=内联嵌入, external=独立文件 (默认 inline)')
    bp.add_argument('--js', choices=['inline', 'external'], default='inline',
                    help='JS 输出策略: inline=内联嵌入, external=独立文件 (默认 inline)')
    bp.add_argument('--watch', action='store_true', help='监听变化')

    # ── watch ──
    wp = sub.add_parser('watch', help='监听并自动编译')
    wp.add_argument('input', help='输入文件')
    wp.add_argument('-o', '--output', required=True, help='输出文件')
    wp.add_argument('--mode', choices=['html', 'php'], default='html')
    wp.add_argument('--css', choices=['inline', 'external'], default='inline')
    wp.add_argument('--js', choices=['inline', 'external'], default='inline')

    # ── components ──
    cp = sub.add_parser('components', help='组件管理')
    cp.add_argument('action', choices=['list', 'init'], help='操作')
    cp.add_argument('name', nargs='?', help='组件名 (init 时需要)')

    # ── directives ──
    dp = sub.add_parser('directives', help='列出所有可用指令')
    dp.add_argument('action', choices=['list'], help='操作')

    # ── version ──
    sub.add_parser('version', help='显示版本')

    args = parser.parse_args()

    if not args.command or args.command == 'version':
        from core import __version__
        print(f'LiteML Compiler v{__version__}')
        print('https://github.com/Zhao-Shengyi/LiteML')
        return

    if args.command == 'build':
        _cmd_build(args)
    elif args.command == 'watch':
        _cmd_watch(args)
    elif args.command == 'components':
        _cmd_components(args)
    elif args.command == 'directives':
        _cmd_directives(args)


# ══════════════════════════════════════════════
# 命令实现
# ══════════════════════════════════════════════


def _cmd_build(args):
    """build 子命令"""
    mode = Mode.PHP if args.mode == 'php' else Mode.HTML
    css_mode = AssetMode.EXTERNAL if args.css == 'external' else AssetMode.INLINE
    js_mode = AssetMode.EXTERNAL if args.js == 'external' else AssetMode.INLINE

    # CSS/JS 策略：取更外部的那个（如果任一为 external，就启用 external）
    # 实际 compiler 用 asset_mode 统一控制，这里简单处理
    asset_mode = AssetMode.EXTERNAL if (css_mode == AssetMode.EXTERNAL or js_mode == AssetMode.EXTERNAL) else AssetMode.INLINE

    compiler = LiteMLCompiler(mode=mode, asset_mode=asset_mode)
    inp = args.input
    out = args.output or 'output.html'

    if os.path.isfile(inp):
        if not inp.endswith('.lite'):
            print(f'⚠️  跳过非 .lite 文件: {inp}')
            return
        compiler.compile_to_file(inp, out)

    elif os.path.isdir(inp):
        if not out or not os.path.isdir(out):
            os.makedirs(out, exist_ok=True)
        for root, dirs, files in os.walk(inp):
            for f in files:
                if f.endswith('.lite'):
                    src = os.path.join(root, f)
                    rel = os.path.relpath(src, inp)
                    ext = '.html' if mode == Mode.HTML else '.php'
                    dst = os.path.join(out, rel.replace('.lite', ext))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    compiler.compile_to_file(src, dst)

    if args.watch and os.path.isfile(inp):
        _start_watch(inp, out, mode, asset_mode)


def _cmd_watch(args):
    """watch 子命令"""
    mode = Mode.PHP if args.mode == 'php' else Mode.HTML
    css_mode = AssetMode.EXTERNAL if args.css == 'external' else AssetMode.INLINE
    js_mode = AssetMode.EXTERNAL if args.js == 'external' else AssetMode.INLINE
    asset_mode = AssetMode.EXTERNAL if (css_mode == AssetMode.EXTERNAL or js_mode == AssetMode.EXTERNAL) else AssetMode.INLINE
    _start_watch(args.input, args.output, mode, asset_mode)


def _start_watch(inp: str, out: str, mode: Mode, asset_mode: AssetMode):
    """启动文件监听"""
    print(f'📡 监听: {inp} → {out}')
    last = os.path.getmtime(inp)
    try:
        while True:
            time.sleep(1)
            mtime = os.path.getmtime(inp)
            if mtime != last:
                last = mtime
                compiler = LiteMLCompiler(mode=mode, asset_mode=asset_mode)
                compiler.compile_to_file(inp, out)
    except KeyboardInterrupt:
        print('\n👋 停止监听')


def _cmd_components(args):
    """components 子命令"""
    loader = ComponentLoader()
    if args.action == 'list':
        comps = loader.list_components()
        if comps:
            print('可用组件:')
            for c in comps:
                print(f'  • {c}')
        else:
            print('components/ 目录中没有组件。')
            print('使用 "python core/cli.py components init 组件名" 创建。')

    elif args.action == 'init':
        if not args.name:
            print('❌ 请指定组件名: python core/cli.py components init 组件名')
            return
        if loader.init_component(args.name):
            print(f'💡 编辑 components/{args.name}/ 下的文件来定义组件内容。')
        else:
            print(f'❌ 组件 {args.name} 已存在。')


def _cmd_directives(args):
    """directives 子命令"""
    from core.directive_loader import list_directives
    dirs = list_directives()
    if dirs:
        print(f'可用指令 ({len(dirs)}):')
        for d in dirs:
            print(f'  @{d}')
    else:
        print('没有已注册的指令。')


if __name__ == '__main__':
    main()
