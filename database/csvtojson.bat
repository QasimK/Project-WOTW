@echo off

REM For converting __initial_data.csv outputted from Excel
REM to initial_data.json

:: %~dp0 Gives current directory with last \
set pyfile="%~dp0editdata.py"
:: echo %pyfile%

python2.lnk %pyfile% "%~dp0__initial_data.csv" "%~dp0__initial_data.json"

if %ERRORLEVEL% EQU 1 pause