const { execFile } = require('child_process')
const path = require('path')
const fs = require('fs')
const os = require('os')

const PROJECT_ROOT = path.resolve(__dirname, '..', '..')
const DEFAULT_TIMEOUT = 30000

let _cliCache = null

function detectPythonCli() {
  if (_cliCache) return _cliCache
  const candidates = [
    { cmd: 'liteml', args: [] },
    { cmd: 'python3', args: [path.join(PROJECT_ROOT, 'core', 'cli.py')] },
    { cmd: 'python3', args: ['-m', 'liteml'] },
  ]
  for (const c of candidates) {
    try {
      require('child_process').execFileSync(c.cmd, [...c.args, 'version'], {
        stdio: 'pipe',
        timeout: 5000,
        encoding: 'utf-8',
      })
      _cliCache = c
      return c
    } catch (_) {}
  }
  throw new Error(
    '找不到 LiteML Python CLI。请确保已安装 liteml（pip install liteml）或处于项目根目录。'
  )
}

function runCli(args, options = {}) {
  const cli = detectPythonCli()
  const timeout = options.timeout || DEFAULT_TIMEOUT

  return new Promise((resolve, reject) => {
    const child = execFile(
      cli.cmd,
      [...cli.args, ...args],
      { timeout, encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 },
      (err, stdout, stderr) => {
        if (err) {
          if (err.killed) {
            reject(new Error('编译超时（超过 ' + (timeout / 1000) + ' 秒）'))
          } else {
            const msg = stderr.trim() || err.message || '未知错误'
            reject(new Error('LiteML 编译失败: ' + msg))
          }
          return
        }
        resolve(stdout)
      }
    )
  })
}

function compile(source, options = {}) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'liteml-'))
  const inputFile = path.join(tmpDir, 'input.lite')
  const outputFile = path.join(tmpDir, 'output.' + (options.mode === 'php' ? 'php' : 'html'))

  fs.writeFileSync(inputFile, source, 'utf-8')

  const args = ['build', inputFile, '-o', outputFile]
  if (options.mode) args.push('--mode', options.mode)
  if (options.css) args.push('--css', options.css)
  if (options.js) args.push('--js', options.js)

  return runCli(args, options)
    .then(() => {
      const result = fs.readFileSync(outputFile, 'utf-8')
      cleanup(tmpDir)
      return result
    })
    .catch((err) => {
      cleanup(tmpDir)
      throw err
    })
}

function cleanup(dir) {
  try {
    fs.rmSync(dir, { recursive: true, force: true })
  } catch (_) {}
}

function compileFile(inputPath, outputPath, options = {}) {
  const resolvedInput = path.resolve(inputPath)
  const resolvedOutput = path.resolve(outputPath)

  const args = ['build', resolvedInput, '-o', resolvedOutput]
  if (options.mode) args.push('--mode', options.mode)
  if (options.css) args.push('--css', options.css)
  if (options.js) args.push('--js', options.js)

  return runCli(args, options).then(() => ({
    input: resolvedInput,
    output: resolvedOutput,
  }))
}

function listComponents() {
  return runCli(['components', 'list']).then((stdout) => {
    const lines = stdout.split('\n').filter(Boolean)
    const names = []
    for (const line of lines) {
      const m = line.match(/•\s*(.+)/)
      if (m) names.push(m[1].trim())
    }
    return names
  })
}

function listDirectives() {
  return runCli(['directives', 'list']).then((stdout) => {
    const lines = stdout.split('\n').filter(Boolean)
    const names = []
    for (const line of lines) {
      const m = line.match(/@(\S+)/)
      if (m) names.push(m[1].trim())
    }
    return names
  })
}

function listTemplates() {
  return runCli(['templates', 'list']).then((stdout) => {
    const lines = stdout.split('\n').filter(Boolean)
    const results = []
    for (const line of lines) {
      const m = line.match(/•\s*@template\((\w+)\)\s*—\s*(.+)/)
      if (m) {
        results.push({ name: m[1], description: m[2].trim() })
      }
    }
    return results
  })
}

module.exports = { compile, compileFile, listComponents, listDirectives, listTemplates }
