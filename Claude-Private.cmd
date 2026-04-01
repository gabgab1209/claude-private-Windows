@echo off
setlocal

:: Claude Code - Private Edition (Windows)
:: No telemetry, no phone-home.
:: For alternative backends, use claude-code-router externally 
:: and set ANTHROPIC_BASE_URL as usual.

:: Telemetry kill switches
set CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
set DISABLE_TELEMETRY=1
set DISABLE_AUTOUPDATER=1
set CLAUDE_CODE_ENABLE_TELEMETRY=0
set OTEL_METRICS_EXPORTER=none
set OTEL_LOGS_EXPORTER=none
set OTEL_TRACES_EXPORTER=none

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

:: Run the patched executable with any arguments passed by the user
"%SCRIPT_DIR%claude-notelemetry.exe" %*

endlocal
