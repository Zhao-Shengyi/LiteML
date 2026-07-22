#!/usr/bin/env node
const path = require('path')
const { spawn, execFileSync } = require('child_process')

const PROJECT_ROOT = path.resolve(__dirname, '..', '..')
const args = process.argv.slice(2)

let cmd = 'python3'
let cmdArgs = [path.join(PROJECT_ROOT, 'core', 'cli.py'), ...args]

try {
  execFileSync('liteml', ['version'], { stdio: 'pipe', timeout: 3000 })
  cmd = 'liteml'
  cmdArgs = [...args]
} catch (_) {
  try {
    execFileSync('python3', ['-m', 'liteml', 'version'], { stdio: 'pipe', timeout: 3000 })
    cmd = 'python3'
    cmdArgs = ['-m', 'liteml', ...args]
  } catch (_2) {}
}

const child = spawn(cmd, cmdArgs, { stdio: 'inherit' })
child.on('exit', (code) => process.exit(code))
