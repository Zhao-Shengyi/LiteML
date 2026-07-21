/**
 * LiteML VS Code 扩展入口
 * =========================
 * 提供：语法高亮、诊断检查、编译命令
 */

const vscode = require('vscode');
const { lintDocument } = require('./linter');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

/** 诊断集合 —— 由 linter 填充 */
let diagnosticCollection;

/**
 * 激活扩展
 */
function activate(context) {
  // 创建诊断集合，附加到当前编辑器
  diagnosticCollection = vscode.languages.createDiagnosticCollection('liteml');
  context.subscriptions.push(diagnosticCollection);

  // ── 注册诊断提供器：文件变化时自动检查 ──
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('liteml')) {
        // 配置变了，重新检查所有打开的 .lite 文件
        vscode.workspace.textDocuments.forEach(doc => {
          if (doc.languageId === 'liteml') runLint(doc);
        });
      }
    })
  );

  // ── 注册文档保存事件（延迟 lint） ──
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      if (doc.languageId === 'liteml') {
        const config = vscode.workspace.getConfiguration('liteml');
        if (config.get('lintOnSave') !== false) {
          runLint(doc);
        }
      }
    })
  );

  // ── 打开文档时检查 ──
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => {
      if (doc.languageId === 'liteml') runLint(doc);
    })
  );

  // ── 编辑器激活时检查当前文档 ──
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(editor => {
      if (editor && editor.document.languageId === 'liteml') {
        runLint(editor.document);
      }
    })
  );

  // ── 对所有已打开的 .lite 文件执行初始检查 ──
  vscode.workspace.textDocuments.forEach(doc => {
    if (doc.languageId === 'liteml') runLint(doc);
  });

  // ── 注册编译命令 ──
  context.subscriptions.push(
    vscode.commands.registerCommand('liteml.compile', () => compileCurrentFile('html'))
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('liteml.compilePhp', () => compileCurrentFile('php'))
  );

  // ── 右键菜单：编译选中的文件 ──
  context.subscriptions.push(
    vscode.commands.registerCommand('liteml.compileFile', (uri) => {
      if (uri && uri.fsPath) {
        compileFile(uri.fsPath, 'html');
      }
    })
  );

  console.log('[LiteML] 扩展已激活');
}

/**
 * 对文档执行 lint 检查
 */
function runLint(doc) {
  try {
    const diagnostics = lintDocument(doc);
    // 将诊断结果关联到文件
    const diagList = diagnostics.map(d => {
      const range = new vscode.Range(d.line, 0, d.line, 1000);
      return new vscode.Diagnostic(range, d.message, d.severity || vscode.DiagnosticSeverity.Error);
    });
    diagnosticCollection.set(doc.uri, diagList);
  } catch (err) {
    console.error('[LiteML] Lint error:', err);
  }
}

/**
 * 编译当前文件
 */
function compileCurrentFile(mode) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('请先打开一个 .lite 文件');
    return;
  }

  const filePath = editor.document.uri.fsPath;
  compileFile(filePath, mode);
}

/**
 * 编译指定文件
 */
function compileFile(filePath, mode) {
  if (!fs.existsSync(filePath)) {
    vscode.window.showErrorMessage(`文件不存在: ${filePath}`);
    return;
  }

  // 查找编译器
  const projectRoot = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath || path.dirname(filePath);
  const configPath = vscode.workspace.getConfiguration('liteml').get('compilerPath');
  let compilerPath = configPath || '';

  if (!compilerPath) {
    const candidates = [
      path.join(projectRoot, 'liteml.py'),
      path.join(projectRoot, 'LiteML', 'liteml.py'),
      path.join(__dirname, '..', '..', 'LiteML', 'liteml.py')
    ];
    for (const c of candidates) {
      if (fs.existsSync(c)) { compilerPath = c; break; }
    }
  }

  if (!compilerPath || !fs.existsSync(compilerPath)) {
    vscode.window.showErrorMessage(
      '找不到 liteml.py 编译器。请在设置中配置 "liteml.compilerPath"，或确保编译器文件在项目目录中。'
    );
    return;
  }

  // 确定输出路径
  const ext = mode === 'php' ? '.php' : '.html';
  const outPath = filePath.replace(/\.lite$/i, ext);

  try {
    const modeFlag = mode === 'php' ? '--mode=php' : '';
    const cmd = `python3 "${compilerPath}" build "${filePath}" ${modeFlag} -o "${outPath}"`.trim();
    const result = execSync(cmd, { timeout: 10000, encoding: 'utf-8' });

    vscode.window.showInformationMessage(`✅ 编译完成: ${path.basename(outPath)}`);

    // 询问是否打开输出文件
    vscode.window.showInformationMessage(
      `编译成功 → ${outPath}`,
      '打开文件'
    ).then(selection => {
      if (selection === '打开文件') {
        vscode.workspace.openTextDocument(outPath).then(doc => {
          vscode.window.showTextDocument(doc);
        });
      }
    });

  } catch (err) {
    let msg = err.stderr || err.message || '未知错误';
    // 截取有用信息
    const lines = msg.split('\n').filter(l => l.trim());
    const shortMsg = lines.slice(0, 3).join(' | ');
    vscode.window.showErrorMessage(`❌ 编译失败: ${shortMsg}`);
  }
}

/**
 * 停用扩展
 */
function deactivate() {
  if (diagnosticCollection) {
    diagnosticCollection.clear();
    diagnosticCollection.dispose();
  }
  console.log('[LiteML] 扩展已停用');
}

module.exports = { activate, deactivate };
