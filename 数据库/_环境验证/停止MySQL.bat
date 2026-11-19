@echo off
setlocal
set "MYSQL_ADMIN=F:\Scoop\apps\mysql\current\bin\mysqladmin.exe"
if not exist "%MYSQL_ADMIN%" (
    echo mysqladmin.exe not found: "%MYSQL_ADMIN%"
    pause
    exit /b 1
)
set "MYSQL_USER=root"
"%MYSQL_ADMIN%" --host=127.0.0.1 --port=3306 --user="%MYSQL_USER%" -p shutdown
if errorlevel 1 (
    echo MySQL was not shut down. Check the server and login information.
    pause
    exit /b 1
)
echo MySQL shut down cleanly.
pause
