# 自体心理学督导技能 - 安装脚本 (Windows PowerShell)
$ErrorActionPreference = "Stop"

$SkillName = "self-psychology-supervision"
$TargetDir = Join-Path $env:USERPROFILE ".claude\skills\$SkillName"

Write-Host "=== 自体心理学督导技能 安装 ===" -ForegroundColor Cyan
Write-Host "目标目录: $TargetDir"

if (Test-Path $TargetDir) {
    Write-Host ""
    Write-Host "目标目录已存在。" -ForegroundColor Yellow
    $reply = Read-Host "是否覆盖？(y/N)"
    if ($reply -notmatch '^[Yy]$') {
        Write-Host "已取消。"
        exit 1
    }
    Remove-Item $TargetDir -Recurse -Force
}

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -Path (Join-Path $ScriptDir "*") -Destination $TargetDir -Recurse -Force

# 清理不需要的安装产物
Remove-Item (Join-Path $TargetDir "install.sh") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $TargetDir "install.ps1") -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "安装完成: $TargetDir" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：重启你的 Claude Code / 兼容客户端，然后直接说："
Write-Host "    督导一下这个案例" -ForegroundColor Cyan
