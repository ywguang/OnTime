# OnTime 打包脚本
# 使用方法：在 PowerShell 中运行 .\build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OnTime 打包工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 PyInstaller 是否安装
Write-Host "[1/3] 检查 PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = pyinstaller --version 2>&1
    Write-Host "✓ PyInstaller 已安装: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ PyInstaller 未安装" -ForegroundColor Red
    Write-Host "正在安装 PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ 安装失败，请手动运行: pip install pyinstaller" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ PyInstaller 安装成功" -ForegroundColor Green
}

Write-Host ""

# 清理旧的构建文件
Write-Host "[2/3] 清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "  已删除 build 目录" -ForegroundColor Gray
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "  已删除 dist 目录" -ForegroundColor Gray
}
Write-Host "✓ 清理完成" -ForegroundColor Green

Write-Host ""

# 开始打包
Write-Host "[3/3] 开始打包..." -ForegroundColor Yellow
Write-Host ""
pyinstaller OnTime.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ 打包成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "可执行文件位置: dist\OnTime.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步操作：" -ForegroundColor Yellow
    Write-Host "  1. 测试运行: .\dist\OnTime.exe" -ForegroundColor White
    Write-Host "  2. 将整个 dist 文件夹分发给用户" -ForegroundColor White
    Write-Host "  3. 用户可以在 exe 同目录下创建 user_config.json 配置" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ 打包失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查上方的错误信息" -ForegroundColor Yellow
    exit 1
}
