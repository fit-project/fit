@echo off
set python_path=%1
set app_path=%2

if "%python_path%"=="" (
    echo Esecuzione solo dell'app senza Python...
    runas /user:Administrator "%app_path%"
) else (
    echo Esecuzione con Python...
    runas /user:Administrator "%python_path% %app_path%"
)