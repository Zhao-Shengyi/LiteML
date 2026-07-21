"""
@modal 指令：对话框按钮
用法：button@modal(open=#myDialog)
"""

from ..directive_loader import directive


@directive('modal')
def handle_modal(node, params: str, state: dict):
    """给按钮绑定打开 <dialog> 的行为，注入 JS"""
    modal_id = ''
    if params.startswith('open='):
        modal_id = params.split('=', 1)[1].strip().strip('"\'')
    if not modal_id:
        return

    counter = state['id_counter']
    btn_id = f'btn-modal-{counter}'
    state['id_counter'] = counter + 1

    node.attributes.append(('id', btn_id))
    state['ejected_scripts'].append(
        f'(function() {{\n'
        f'  document.getElementById("{btn_id}").addEventListener("click", function() {{\n'
        f'    document.querySelector("{modal_id}").showModal();\n'
        f'  }});\n'
        f'  document.querySelector("{modal_id}").addEventListener("click", function(e) {{\n'
        f'    if (e.target === this) this.close();\n'
        f'  }});\n'
        f'}})();'
    )
