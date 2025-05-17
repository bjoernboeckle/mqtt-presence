@echo off
setlocal

IF "%1"=="build" (
    call :prebuild || goto :prebuild_failed
    call :run_pylint || goto :pylint_failed
    python -m build
) ELSE IF "%1"=="clean" (
    del /Q /F mqtt_presence\version.py 2>nul
    rmdir /S /Q dist build mqtt_presence.egg-info 2>nul
) ELSE IF "%1"=="pylint" (
    call :prebuild || goto :prebuild_failed
    call :run_pylint || goto :pylint_failed
) ELSE (
    echo Usage: make.bat [build|clean|pylint]
)



goto :eof

:prebuild
python scripts\pre_build.py
goto :eof


:prebuild_failed
echo ❌ Prebuild failed. Aborting.
exit /b 1


:run_pylint
echo Running pylint...
python -m pylint mqtt_presence
goto :eof

:pylint_failed
echo ❌ Pylint reported issues. Aborting.
exit /b 1