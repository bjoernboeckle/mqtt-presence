@echo off

IF "%1"=="build" (
    python scripts\pre_build.py
    python -m build
) ELSE IF "%1"=="clean" (
    del /Q /F mqtt_presence\version.py 2>nul
    rmdir /S /Q dist build mqtt_presence.egg-info 2>nul
) ELSE IF "%1"=="pylint" (
    python -m pylint mqtt_presence
) ELSE (
    echo "Usage: make.bat [build|clean]"
)
