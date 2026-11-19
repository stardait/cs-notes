@echo off
setlocal
set "MYSQL_START=F:\Scoop\persist\mysql\start-mysql.vbs"
if not exist "%MYSQL_START%" (
    echo MySQL start script not found: "%MYSQL_START%"
    pause
    exit /b 1
)
tasklist /FI "IMAGENAME eq mysqld.exe" /NH | findstr /I /C:"mysqld.exe" >nul
if not errorlevel 1 (
    echo A mysqld process is already running. Check 127.0.0.1:3306 in HeidiSQL.
    pause
    exit /b 0
)
cscript.exe //NoLogo "%MYSQL_START%"
if errorlevel 1 (
    echo MySQL startup script returned an error.
    pause
    exit /b 1
)
echo Startup requested. After a few seconds, connect to 127.0.0.1:3306 in HeidiSQL.
pause
