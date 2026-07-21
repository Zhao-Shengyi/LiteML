# AGENTS.md — LiteML Compiler

## Language / 语言

When communicating with the human user, always use **Chinese (中文)**. Code comments should be in Chinese explaining *why* (not what). Commit messages should be in Chinese.

## Quick start

```bash
python3 core/cli.py build input.lite -o output.html
python3 core/cli.py build input.lite --mode=php -o output.php
python3 core/cli.py watch input.lite -o output.html
```

## Commands

| Action | Command |
|---|---|
| Build (single file) | `python3 core/cli.py build <file.lite> -o <output>` |
| Build (directory) | `python3 core/cli.py build src/ -o dist/` |
| PHP mode | add `--mode=php` |
| Asset mode | add `--css=inline\|external --js=inline\|external` (controls component style/script output) |
| Eject directives | add `--eject` (expands `@directive!` to native code) |
| Watch mode | `python3 core/cli.py watch <file.lite> -o <output>` |
| Components | `python3 core/cli.py components list\|init <name>` |
| Directives | `python3 core/cli.py directives list` |
| TUI | `python3 core/tui.py [file\|dir]` (requires `pip3 install textual`, v8.2.8) |
| Version | `python3 core/cli.py version` → "LiteML Compiler v0.2" (defined in `cli.py`; source of truth in `core/__init__.py`)

## Testing

No test framework. Manual validation:

```bash
python3 core/cli.py build tests/test.lite -o tests/test.html
# visually diff against expected output
```

Test fixtures: `tests/test_full.lite`, `test_php.lite`, `test_use.lite`.

## Architecture

- **Compiler core**: `core/` Python package (no `setup.py`/`pyproject.toml`/`requirements.txt` — pure scripts run from project root).
- **Entry points**: `core/cli.py` (argparse) and `core/tui.py` (Textual). Both use `sys.path.insert(0, ...)` hack — **always run from project root**.
- **Directives (plugins)**: `core/directives/*.py`, registered via `@directive` decorator.
  - To add a new directive: create `core/directives/xxx.py`, decorate a function with `@directive('name')`.
  - Signature: `handler(node, params: str, state: dict) -> None` — mutate `node` (add attributes/classes), append to `state['ejected_styles']` / `state['ejected_scripts']`, increment `state['id_counter']` if needed.
  - The `core/directive_loader.py` auto-discovers all files in `core/directives/` at import time.
- **Components**: `components/<name>/template.html` + `style.css` + `script.js` (or `component.json` manifest).
- **VS Code extension**: `editors/vscode/` — standalone npm package with pre-built `.vsix`.

## Gotchas

- **`"""` in docstrings**: Python triple-quote docstrings cannot contain `"""` (used in language examples). Use single-quote docstrings instead.
- **`sys.path` requirement**: `core/cli.py` and `core/tui.py` prepend parent dir to `sys.path`. Running from anywhere except project root will break imports.
- **No `check` subcommand**: VS Code extension originally called `check --stdin` — the compiler has no such command. Old workaround: temp file + `build`.
- **`.lite` indent rules**: 2-space indentation mandatory. Tabs and odd indent spaces warned by the linter.
- **`@css`/`@js` dual role**: With parens = external include (`@css(path)` → `<link>`); without parens + block = inline (`@css` ... `@endcss` → `<style>`).
- **`@raw`/`@php`**: No explicit closing tag — ends when indentation returns to parent level. TextMate grammar expects `@endraw`/`@endphp` but the parser uses indentation detection (grammar ≠ parser; this does NOT affect compilation, only syntax highlighting color range).
- **PHP `$user.name`**: Uses dot syntax, compiles to `$user['name']` array access, NOT `->` object syntax.
- **Python 3.9.6**: No `|` union type syntax (3.10+). `f"{x=}"` is fine (3.8+).
- **No CI/CD**: No GitHub Actions, no automated tests, no lint runner outside VS Code.

## Prompts (for LLMs using LiteML)

See `prompts/usage-prompt.md` and `prompts/decompile-prompt.md`. Full language reference in `SYNTAX.md` (1090 lines).
