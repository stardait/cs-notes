@echo off
title 启动 MySQL
set MYSQLD=F:\Scoop\apps\mysql\current\bin\mysqld.exe
set MYINI=F:\Scoop\persist\mysql\my.ini
echo ========================================
echo   启动 MySQL
echo ========================================
echo.
tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
if %errorlevel%==0 goto running
if not exist "%MYSQLD%" goto nofile
echo [启动中] 正在启动 mysqld ...
start "" /B "%MYSQLD%" --defaults-file="%MYINI%"
timeout /t 10 /nobreak >nul
tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
if %errorlevel%==0 goto ok
echo [失败] 启动失败，看日志 F:\Scoop\persist\mysql\data
goto end

:running
echo [已运行] MySQL 本来就在跑，不用重复启动。
goto info

:nofile
echo [错误] 找不到 mysqld.exe
echo 请先安装：scoop install mysql
goto end

:ok
echo [成功] MySQL 已启动
echo.
:info
echo   连接信息：
echo     地址 127.0.0.1
echo     端口 3306
echo     用户 root
echo     密码 Root@2026
echo.
echo   停止请双击：停止MySQL.bat

:end
echo.
pause
