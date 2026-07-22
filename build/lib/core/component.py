"""
LiteML 组件加载器

负责从 components/ 目录加载组件，支持两种形式：
1. 约定式：自动发现 template.html / style.css / script.js
2. 清单式：读取 component.json 明确指定文件路径
"""

import json
import os
from typing import Optional

from .models import ComponentInfo


class ComponentLoader:
    """组件加载器，搜索 components/ 目录下的组件"""

    def __init__(self, components_dir: str = 'components'):
        self.components_dir = components_dir

    def load(self, name: str) -> Optional[ComponentInfo]:
        """按名称加载组件，返回 ComponentInfo 或 None"""
        comp_dir = os.path.join(self.components_dir, name)
        if not os.path.isdir(comp_dir):
            return None

        info = ComponentInfo(name=name, dir_path=comp_dir)

        # 优先读取 component.json
        manifest_path = os.path.join(comp_dir, 'component.json')
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                files = manifest.get('files', {})
                info.template = self._read_file(comp_dir, files.get('template', 'template.html'))
                info.style = self._read_file(comp_dir, files.get('style', 'style.css'))
                info.script = self._read_file(comp_dir, files.get('script', 'script.js'))
                return info
            except (json.JSONDecodeError, IOError) as e:
                print(f'⚠️  组件 {name} 的 component.json 读取失败: {e}')
                # 降级到约定式

        # 约定式：自动检测常见文件名
        for tpl_file in ('template.html', 'template.htm', f'{name}.html'):
            info.template = self._read_file(comp_dir, tpl_file)
            if info.template:
                break

        info.style = self._read_file(comp_dir, 'style.css') or \
                     self._read_file(comp_dir, f'{name}.css')

        info.script = self._read_file(comp_dir, 'script.js') or \
                      self._read_file(comp_dir, f'{name}.js')

        return info

    def list_components(self) -> list:
        """列出 components/ 下所有可用组件"""
        if not os.path.isdir(self.components_dir):
            return []
        return sorted([
            d for d in os.listdir(self.components_dir)
            if os.path.isdir(os.path.join(self.components_dir, d))
        ])

    def init_component(self, name: str) -> bool:
        """在 components/ 下创建一个新组件的骨架文件"""
        comp_dir = os.path.join(self.components_dir, name)
        if os.path.exists(comp_dir):
            return False

        os.makedirs(comp_dir, exist_ok=True)

        # 创建 component.json
        manifest = {
            "name": name,
            "description": f"{name} 组件",
            "files": {
                "template": "template.html",
                "style": "style.css",
                "script": "script.js"
            }
        }
        with open(os.path.join(comp_dir, 'component.json'), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # 创建模板文件（空占位）
        for filename in ('template.html', 'style.css', 'script.js'):
            path = os.path.join(comp_dir, filename)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    if filename.endswith('.html'):
                        f.write(f'<!-- {name} 组件模板 -->\n')
                    elif filename.endswith('.css'):
                        f.write(f'/* {name} 样式 */\n')
                    else:
                        f.write(f'// {name} 脚本\n')

        print(f'✅ 组件 {name} 已创建: {comp_dir}')
        return True

    @staticmethod
    def _read_file(comp_dir: str, filename: str) -> str:
        """读取组件目录下的文件内容，不存在返回空字符串"""
        path = os.path.join(comp_dir, filename)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
