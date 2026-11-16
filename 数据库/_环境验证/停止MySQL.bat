@echo off
title 停止 MySQL
echo ========================================
echo   停止 MySQL
echo ========================================
echo.
tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
if not %errorlevel%==0 goto notrunning
echo [停止中] 正在关闭 mysqld ...
taskkill /F /IM mysqld.exe >nul 2>&1
timeout /t 3 /nobreak >nul
tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
if %errorlevel%==0 goto failed
echo [成功] MySQL 已停止
goto end

:notrunning
echo [已停止] MySQL 本来就没在跑。
goto end

:failed
echo [失败] 还在运行，请用任务管理器结束 mysqld.exe

:end
echo.
pause
