@echo off
chcp 936 >nul
cd /d "%~dp0.."
set "PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" tools\build_views.py %*
if errorlevel 1 (
  echo.
  echo [失败] 构建没有完成，请查看上面的报错。
) else (
  echo.
  echo [完成] 已重新生成 速览.html 与各事件的 档案.html。
)
pause
