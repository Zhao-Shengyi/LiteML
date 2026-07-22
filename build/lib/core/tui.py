"""
LiteML TUI — Textual 终端用户界面编译器

用法:
    python core/tui.py                    # 打开目录选择
    python core/tui.py 文件.lite          # 直接打开文件
    python core/tui.py 目录/              # 打开目录
"""

import os
import sys
from pathlib import Path
from typing import Optional

# pip 安装后模块在包中，不需要手动加路径
if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查 Textual 是否可用
try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import (
        Header, Footer, DirectoryTree, TextArea, Select, Label,
        Button, Static, TabbedContent, TabPane
    )
    from textual.binding import Binding
except ImportError:
    print('❌ TUI 模式需要安装 textual 库。')
    print('   运行: pip3 install textual')
    print('   或使用 CLI 模式: python3 core/cli.py build ...')
    sys.exit(1)

from core.constants import Mode, AssetMode
from core.compiler import LiteMLCompiler


class OutputPanel(Static):
    """显示编译结果的输出面板"""
    pass


class LiteMLTUI(App):
    """LiteML Textual 终端界面"""

    TITLE = 'LiteML Compiler'
    SUB_TITLE = '轻量级 HTML/PHP 模板编译器'
    CSS = """
    Screen {
        background: #1a1b26;
    }

    #main-container {
        height: 100%;
    }

    #sidebar {
        width: 30%;
        min-width: 30;
        max-width: 40;
        border-right: solid #3b4261;
        background: #1f2137;
    }

    #sidebar Label {
        padding: 1 2;
        text-style: bold;
        color: #a9b1d6;
        background: #24283b;
    }

    #editor-panel {
        width: 70%;
        height: 100%;
    }

    #controls {
        height: 5;
        padding: 0 1;
        background: #24283b;
        border-bottom: solid #3b4261;
    }

    #mode-select {
        width: 16;
    }

    #css-select, #js-select {
        width: 16;
    }

    #compile-btn {
        width: 20;
        background: #2ac3de;
        color: #1a1b26;
        text-style: bold;
    }

    #compile-btn:hover {
        background: #7dcfff;
    }

    TextArea {
        border: none;
    }

    TextArea:focus {
        border: none;
    }

    #output-panel {
        height: 40%;
        background: #1f2137;
        border-top: solid #3b4261;
        padding: 1;
    }

    #output-panel Label {
        text-style: bold;
        color: #73daca;
        margin-bottom: 1;
    }

    OutputPanel {
        height: 1fr;
        overflow-y: auto;
        color: #c0caf5;
    }

    .success {
        color: #9ece6a;
    }

    .error {
        color: #f7768e;
    }

    .info {
        color: #7aa2f7;
    }

    DirectoryTree {
        background: #1f2137;
    }

    DirectoryTree:focus {
        border: none;
    }

    DirectoryTree .tree--label {
        color: #c0caf5;
    }

    DirectoryTree .tree--highlight {
        background: #3b4261;
    }

    LoadingIndicator {
        height: 3;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding('ctrl+b', 'compile', '编译'),
        Binding('ctrl+s', 'save_and_compile', '保存并编译'),
        Binding('ctrl+q', 'quit', '退出'),
    ]

    def __init__(self, start_path: Optional[str] = None):
        super().__init__()
        self._start_path = start_path
        self._current_file: Optional[str] = None
        self._compiler: Optional[LiteMLCompiler] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id='main-container'):
            # 左侧文件树
            with Vertical(id='sidebar'):
                yield Label('📁 文件浏览器')
                start = self._start_path or os.getcwd()
                if os.path.isfile(start):
                    start = os.path.dirname(start)
                yield DirectoryTree(str(Path(start).resolve()))

            # 右侧编辑面板
            with Vertical(id='editor-panel'):
                # 顶部控制栏
                with Horizontal(id='controls'):
                    yield Label('模式:', id='mode-label')
                    yield Select(
                        [(m.value, m.value) for m in Mode],
                        prompt='模式',
                        value='html',
                        id='mode-select',
                    )
                    yield Label('CSS:', id='css-label')
                    yield Select(
                        [('内联 inline', 'inline'), ('外部 external', 'external')],
                        value='inline',
                        id='css-select',
                    )
                    yield Label('JS:', id='js-label')
                    yield Select(
                        [('内联 inline', 'inline'), ('外部 external', 'external')],
                        value='inline',
                        id='js-select',
                    )
                    yield Button('▶ 编译 (Ctrl+B)', id='compile-btn', variant='primary')

                # 编辑器区域
                with TabbedContent(initial='source'):
                    with TabPane('源码', id='source'):
                        yield TextArea('', id='source-editor', language=None)
                    with TabPane('编译结果', id='output-tab'):
                        yield TextArea('', id='result-editor', language='html', read_only=True)

                # 底部输出信息
                with Vertical(id='output-panel'):
                    yield Label('📋 日志')
                    yield OutputPanel('就绪。打开 .lite 文件开始编译。', id='status')
        yield Footer()

    def on_mount(self) -> None:
        """初始化"""
        editor = self.query_one('#source-editor', TextArea)
        editor.show_line_numbers = True

        result = self.query_one('#result-editor', TextArea)
        result.show_line_numbers = True

        # 如果指定了文件，直接打开
        if self._start_path and os.path.isfile(self._start_path):
            self._load_file(self._start_path)

    # ── 事件处理 ──

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """文件树中选中文件"""
        path = str(event.path)
        if path.endswith('.lite'):
            self._load_file(path)
        else:
            self._log(f'⚠️ 只支持 .lite 文件', 'error')

    @on(Button.Pressed, '#compile-btn')
    def _on_compile_click(self):
        self.action_compile()

    def action_compile(self):
        """执行编译"""
        if not self._current_file:
            self._log('❌ 请先打开一个 .lite 文件', 'error')
            return

        source = self.query_one('#source-editor', TextArea).text
        if not source.strip():
            self._log('❌ 源码为空', 'error')
            return

        mode_val = self.query_one('#mode-select', Select).value
        css_val = self.query_one('#css-select', Select).value
        js_val = self.query_one('#js-select', Select).value

        mode = Mode.PHP if mode_val == 'php' else Mode.HTML
        asset_mode = AssetMode.EXTERNAL if (css_val == 'external' or js_val == 'external') else AssetMode.INLINE

        self._compiler = LiteMLCompiler(mode=mode, asset_mode=asset_mode)

        try:
            result = self._compiler.compile(source)
            self.query_one('#result-editor', TextArea).text = result
            self._log(f'✅ 编译成功 ({len(result)} 字节)', 'success')
        except Exception as e:
            self._log(f'❌ 编译失败: {e}', 'error')

    def action_save_and_compile(self):
        """保存并编译（先保存源码到文件）"""
        if self._current_file:
            source = self.query_one('#source-editor', TextArea).text
            with open(self._current_file, 'w', encoding='utf-8') as f:
                f.write(source)
            self._log(f'💾 已保存: {os.path.basename(self._current_file)}', 'info')
        self.action_compile()

    # ── 内部方法 ──

    def _load_file(self, path: str):
        """加载 .lite 文件到编辑器"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._current_file = path
            editor = self.query_one('#source-editor', TextArea)
            editor.text = content
            editor.focus()
            self._log(f'📂 已打开: {os.path.basename(path)} ({len(content)} 字节)', 'info')
            # 自动编译
            self.action_compile()
        except Exception as e:
            self._log(f'❌ 无法打开文件: {e}', 'error')

    def _log(self, message: str, style: str = 'info'):
        """输出日志"""
        panel = self.query_one('#status', OutputPanel)
        panel.update(message)
        # 用 CSS 类控制颜色
        panel.classes = style


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    app = LiteMLTUI(start_path=path)
    app.run()


if __name__ == '__main__':
    main()
