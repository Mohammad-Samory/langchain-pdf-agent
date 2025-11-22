@echo off
REM Batch file wrapper for boot.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0boot.ps1"
