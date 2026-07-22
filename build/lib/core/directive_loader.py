"""
LiteML 指令插件注册器

指令格式：每个指令是一个独立的 .py 文件，用 @directive(name) 装饰器注册。
注册器启动时自动扫描 directives/ 目录发现所有插件。
"""

import os
import importlib
import sys
from typing import Callable, Dict, List

# 全局指令注册表
_registry: Dict[str, Callable] = {}


def directive(name: str):
    """装饰器：将函数注册为名为 name 的指令处理器"""
    def decorator(func: Callable):
        _registry[name] = func
        return func
    return decorator


def get_handler(name: str):
    """通过指令名获取处理器"""
    return _registry.get(name)


def get_all_handlers() -> Dict[str, Callable]:
    """获取所有已注册的指令处理器"""
    return dict(_registry)


def list_directives() -> List[str]:
    """列出所有注册的指令名"""
    return sorted(_registry.keys())


def discover():
    """自动扫描 directives/ 目录，加载所有指令插件"""
    dir_path = os.path.dirname(os.path.abspath(__file__))
    directives_dir = os.path.join(dir_path, 'directives')

    if not os.path.isdir(directives_dir):
        return

    for f in sorted(os.listdir(directives_dir)):
        if f.endswith('.py') and not f.startswith('_'):
            module_name = f'core.directives.{f[:-3]}'
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f'⚠️  指令插件加载失败: {module_name} — {e}')
