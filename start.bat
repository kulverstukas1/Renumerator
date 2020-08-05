@echo off
title Renumerator by Kulverstukas (9v.lt)

set /p filename="Enter filename: "
echo.

echo [!] Press q to quit
:loop
echo.
set /p pages="Enter pages to extract (format: N-N): "
if %pages%==q goto :eof
python renumerator.py %filename% %pages%
goto :loop

:eof