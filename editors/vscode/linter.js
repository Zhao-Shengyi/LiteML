/**
 * LiteML 诊断检查器
 * ===================
 * 功能：
 * 1. 调用 Python 编译器做完整检查（如果可用）
 * 2. 基本语法检查做后备
 */

const vscode = require('vscode');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 已知的 HTML 标签名集合 —— 用于检查标签拼写
 */
const KNOWN_TAGS = new Set([
  'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio',
  'b', 'base', 'bdi', 'bdo', 'blockquote', 'body', 'br', 'button',
  'canvas', 'caption', 'cite', 'code', 'col', 'colgroup',
  'data', 'datalist', 'dd', 'del', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt',
  'em', 'embed',
  'fieldset', 'figcaption', 'figure', 'footer', 'form',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html',
  'i', 'iframe', 'img', 'input', 'ins',
  'kbd',
  'label', 'legend', 'li', 'link',
  'main', 'map', 'mark', 'menu', 'meta', 'meter',
  'nav', 'noscript',
  'object', 'ol', 'optgroup', 'option', 'output',
  'p', 'picture', 'portal', 'pre', 'progress',
  'q',
  'rp', 'rt', 'ruby',
  's', 'samp', 'script', 'section', 'select', 'slot', 'small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup',
  'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track',
  'u', 'ul',
  'var', 'video',
  'wbr'
]);

/**
 * 已知的指令名集合（用于检查拼写）
 */
const KNOWN_DIRECTIVES = new Set([
  'if', 'elseif', 'else', 'endif',
  'foreach', 'endforeach',
  'while', 'endwhile',
  'for', 'endfor',
  'include', 'php', 'endphp',
  'raw', 'endraw',
  'flex', 'grid', 'waterfall', 'position', 'transition', 'hide',
  'modal', 'theme-toggle', 'like',
  'audio', 'video', 'embed', 'icon', 'css', 'js'
]);

/**
 * 自闭合标签
 */
const SELF_CLOSING_TAGS = new Set([
  'meta', 'input', 'img', 'br', 'hr', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'
]);

/**
 * PHP 控制流指令对
 */
const PHP_OPEN_CLOSE = {
  'if': ['elseif', 'else', 'endif'],
  'foreach': ['endforeach'],
  'while': ['endwhile'],
  'for': ['endfor'],
  'php': ['endphp'],
  'raw': ['endraw']
};

/**
 * 解析一行 LiteML，提取关键信息
 */
function parseLine(line, lineNum) {
  const trimmed = line.trimEnd();
  const indent = line.length - line.trimStart().length;

  if (trimmed === '') return null;

  const content = trimmed;

  return { indent, content, lineNum };
}

/**
 * 查找编译器路径
 */
function findCompiler(projectRoot) {
  // 从设置读取
  const configPath = vscode.workspace.getConfiguration('liteml').get('compilerPath');
  if (configPath && fs.existsSync(configPath)) return configPath;

  // 在项目目录查找
  const candidates = [
    path.join(projectRoot || '', 'liteml.py'),
    path.join(projectRoot || '', 'LiteML', 'liteml.py'),
    path.join(projectRoot || '', '..', 'LiteML', 'liteml.py')
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }

  return null;
}

/**
 * 使用 Python 编译器做完整诊断
 */
function checkWithCompiler(doc) {
  const diagnostics = [];
  const compilerPath = findCompiler(vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath);

  if (!compilerPath) return null; // 找不到编译器，回退到 JS 检查

  try {
    const source = doc.getText();
    const result = execSync(
      `python3 "${compilerPath}" check --stdin`,
      {
        input: source,
        encoding: 'utf-8',
        timeout: 5000
      }
    );
    // 编译成功，无错误
    return diagnostics;
  } catch (err) {
    // 解析 Python 编译器的错误输出
    if (err.stderr) {
      const errorLines = err.stderr.split('\n');
      for (const errLine of errorLines) {
        const match = errLine.match(/^Error\s+(?:at\s+)?line\s+(\d+):\s*(.+)$/i);
        if (match) {
          const line = parseInt(match[1]) - 1; // 转为 0-indexed
          const msg = match[2];
          diagnostics.push({
            line: Math.max(0, line),
            message: msg,
            severity: vscode.DiagnosticSeverity.Error
          });
        } else if (errLine.match(/^SyntaxError|^Error|^Traceback/)) {
          // 可能包含 Python 堆栈信息，尝试提取行号
          const tbMatch = errLine.match(/File\s+".*?",\s*line\s+(\d+)/);
          if (tbMatch) {
            // 这是 Python 内部错误，不直接报告给用户
          }
        }
      }
    }

    // 如果编译器返回非零但没解析到错误，说明是编译器内部错误
    if (diagnostics.length === 0) {
      if (err.stderr) {
        // 尝试把整个 stderr 作为错误信息
        const msg = err.stderr.split('\n').filter(l => l.trim())[0];
        if (msg) {
          diagnostics.push({
            line: 0,
            message: `编译器错误: ${msg}`,
            severity: vscode.DiagnosticSeverity.Error
          });
        }
      } else {
        diagnostics.push({
          line: 0,
          message: `编译器调用失败: ${err.message}`,
          severity: vscode.DiagnosticSeverity.Error
        });
      }
    }

    return diagnostics;
  }
}

/**
 * 基本的 JS 语法检查（后备方案）
 */
function checkBasic(doc) {
  const diagnostics = [];
  const text = doc.getText();
  const lines = text.split('\n');
  const parsedLines = [];

  // 第一遍：解析所有行
  for (let i = 0; i < lines.length; i++) {
    const parsed = parseLine(lines[i], i);
    if (parsed) parsedLines.push(parsed);
  }

  // 1. 检查缩进一致性（只允许空格，不允许 Tab）
  for (const pl of parsedLines) {
    const rawLine = lines[pl.lineNum];
    const leading = rawLine.match(/^(\s*)/)[1];
    if (leading.includes('\t')) {
      diagnostics.push({
        line: pl.lineNum,
        message: `第 ${pl.lineNum + 1} 行使用了 Tab 缩进。LiteML 要求只用空格缩进。`,
        severity: vscode.DiagnosticSeverity.Warning
      });
    }
    if (leading.length % 2 !== 0) {
      diagnostics.push({
        line: pl.lineNum,
        message: `缩进空格数（${leading.length}）不是 2 的倍数。LiteML 推荐 2 空格一级缩进。`,
        severity: vscode.DiagnosticSeverity.Warning
      });
    }
  }

  // 2. 检查突变缩进（跳过超过 2 级）
  for (let i = 1; i < parsedLines.length; i++) {
    const prev = parsedLines[i - 1];
    const curr = parsedLines[i];
    const diff = curr.indent - prev.indent;
    if (diff > 2) {
      // 缩进超过 2 级可能是遗漏了中间标签，但空行之后的缩进重置不报
      const prevContent = prev.content;
      // 如果上一行没有子标签（是文本内容行、注释、或自闭合标签），才警告
      if (!prevContent.startsWith('@ ') && !prevContent.startsWith('@raw') && !prevContent.startsWith('@php')) {
        diagnostics.push({
          line: curr.lineNum,
          message: `缩进跳级：从 ${prev.indent} 跳到 ${curr.indent}（差 ${diff}），可能遗漏了中间标签。`,
          severity: vscode.DiagnosticSeverity.Warning
        });
      }
    }
  }

  // 3. 检查未知标签
  const TAG_RE = /^[a-zA-Z_][\w-]*/;
  for (const pl of parsedLines) {
    const content = pl.content;
    // 跳过非标签行
    if (content.startsWith('@') || content.startsWith('<') || content.startsWith('!') || content.startsWith('"') || content.startsWith('`') || content.startsWith('|')) continue;

    const tagMatch = content.match(TAG_RE);
    if (tagMatch) {
      const tag = tagMatch[0].toLowerCase();
      if (!KNOWN_TAGS.has(tag) && !tag.includes('.') && !tag.includes('#')) {
        diagnostics.push({
          line: pl.lineNum,
          message: `未知标签 "${tag}"。请检查拼写，或者如果是自定义标签可以忽略此提示。`,
          severity: vscode.DiagnosticSeverity.Information
        });
      }
    }
  }

  // 4. 检查 @ 指令拼写
  const DIRECTIVE_RE = /^@([a-zA-Z][\w-]*)/;
  for (const pl of parsedLines) {
    const match = pl.content.match(DIRECTIVE_RE);
    if (match) {
      const directive = match[1];
      // 去掉 ! 后缀
      const bare = directive.replace(/!$/, '');
      if (!KNOWN_DIRECTIVES.has(bare)) {
        diagnostics.push({
          line: pl.lineNum,
          message: `未知指令 "@${bare}"。支持的指令：${[...KNOWN_DIRECTIVES].join(', ')}`,
          severity: vscode.DiagnosticSeverity.Error
        });
      }
    }
  }

  // 5. 检查 PHP 控制流配对
  const phpStack = [];
  const PHP_OPEN_RE = /^@(if|foreach|while|for|php|raw)(?:\s*\(|$)/;
  const PHP_CLOSE_RE = /^@(end(?:if|foreach|while|for|php|raw))/;
  const PHP_MID_RE = /^@(else|elseif(?:\s*\())?/;

  for (const pl of parsedLines) {
    const openMatch = pl.content.match(PHP_OPEN_RE);
    if (openMatch) {
      phpStack.push({ type: openMatch[1], line: pl.lineNum });
      continue;
    }

    const closeMatch = pl.content.match(PHP_CLOSE_RE);
    if (closeMatch) {
      const closeType = closeMatch[1]; // e.g., "endif", "endforeach"
      const openType = closeType.slice(3); // e.g., "if", "foreach"
      if (phpStack.length === 0) {
        diagnostics.push({
          line: pl.lineNum,
          message: `多余的 "@${closeType}"，没有对应的 "@${openType}"。`,
          severity: vscode.DiagnosticSeverity.Error
        });
      } else {
        const last = phpStack[phpStack.length - 1];
        // endforeach 匹配 foreach，endif 匹配 if 等
        const expectedClose = PHP_OPEN_CLOSE[last.type]?.[PHP_OPEN_CLOSE[last.type].length - 1] || `end${last.type}`;
        if (closeType !== expectedClose) {
          diagnostics.push({
            line: pl.lineNum,
            message: `闭合指令不匹配：预期 "@${expectedClose}" 来闭合第 ${last.line + 1} 行的 "@${last.type}"，但得到了 "@${closeType}"。`,
            severity: vscode.DiagnosticSeverity.Error
          });
        } else {
          phpStack.pop();
        }
      }
      continue;
    }

    // else/elseif 不改变栈深度，但检查是否有 @if 在栈顶
    const midMatch = pl.content.match(/^@(else|elseif)/);
    if (midMatch) {
      if (phpStack.length === 0 || phpStack[phpStack.length - 1].type !== 'if') {
        diagnostics.push({
          line: pl.lineNum,
          message: `"@${midMatch[1]}" 必须在 @if 块内使用。`,
          severity: vscode.DiagnosticSeverity.Error
        });
      }
    }
  }

  // 检查栈中剩余未闭合的指令
  for (const item of phpStack) {
    diagnostics.push({
      line: item.line,
      message: `"@${item.type}" 未闭合（缺少对应的闭合指令）。`,
      severity: vscode.DiagnosticSeverity.Error
    });
  }

  // 6. 检查 PHP 变量语法：应该用 . 而不是 ->
  const ARROW_RE = /\$\w+->\w+/;
  for (const pl of parsedLines) {
    if (pl.content.startsWith('@')) continue; // 指令行不检查
    const arrowMatch = pl.content.match(ARROW_RE);
    if (arrowMatch) {
      diagnostics.push({
        line: pl.lineNum,
        message: `LiteML 中 PHP 变量属性访问用 "." 而不是 "->"。建议：将 "${arrowMatch[0]}" 改为 "${arrowMatch[0].replace('->', '.')}"`,
        severity: vscode.DiagnosticSeverity.Warning
      });
    }
  }

  // 7. 检查未闭合的括号
  for (const pl of parsedLines) {
    const content = pl.content;
    let depth = 0;
    let inStr = false;
    for (let i = 0; i < content.length; i++) {
      const ch = content[i];
      if (ch === '"' && (i === 0 || content[i - 1] !== '\\')) inStr = !inStr;
      if (inStr) continue;
      if (ch === '(') depth++;
      if (ch === ')') depth--;
    }
    if (depth > 0) {
      diagnostics.push({
        line: pl.lineNum,
        message: `未闭合的括号 "("，缺少对应的 ")"。`,
        severity: vscode.DiagnosticSeverity.Error
      });
    }
    if (depth < 0) {
      diagnostics.push({
        line: pl.lineNum,
        message: `多余的 ")"，没有对应的 "("。`,
        severity: vscode.DiagnosticSeverity.Error
      });
    }
  }

  // 8. 检查 @audio/@video/@embed 的参数
  const ARG_RE = /^@(audio|video|embed|css|js|icon)\(/;
  for (const pl of parsedLines) {
    const argMatch = pl.content.match(ARG_RE);
    if (argMatch) {
      const inner = pl.content.slice(pl.content.indexOf('(') + 1, pl.content.lastIndexOf(')'));
      if (!inner.trim()) {
        diagnostics.push({
          line: pl.lineNum,
          message: `"@${argMatch[1]}" 缺少参数。例如：@${argMatch[1]}(src.mp3)`,
          severity: vscode.DiagnosticSeverity.Error
        });
      }
    }
  }

  return diagnostics;
}

/**
 * 对文档运行全部检查
 */
function lintDocument(doc) {
  if (doc.languageId !== 'liteml') return [];

  // 优先用 Python 编译器
  const compilerResult = checkWithCompiler(doc);
  if (compilerResult !== null) {
    return compilerResult;
  }

  // 回退到 JS 基本检查
  return checkBasic(doc);
}

module.exports = { lintDocument };
