@echo off
REM Batch file wrapper for refreeze.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0refreeze.ps1"
