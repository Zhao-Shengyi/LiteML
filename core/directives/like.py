"""
@like 指令：点赞按钮
用法：button@like 👍 <span.like-count>0</span>
"""

from ..directive_loader import directive


@directive('like')
def handle_like(node, params: str, state: dict):
    """给按钮绑定点赞计数行为，注入 JS"""
    counter = state['id_counter']
    cls = f'eject-like-{counter}'
    state['id_counter'] = counter + 1

    node.classes.append(cls)
    state['ejected_scripts'].append(
        f'(function() {{\n'
        f'  document.querySelectorAll(".{cls}").forEach(function(btn) {{\n'
        f'    btn.addEventListener("click", function() {{\n'
        f'      var c = this.querySelector(".like-count");\n'
        f'      if (c) c.textContent = parseInt(c.textContent) + 1;\n'
        f'    }});\n'
        f'  }});\n'
        f'}})();'
    )
