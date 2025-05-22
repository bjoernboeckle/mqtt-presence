@echo off
setlocal

IF "%1"=="build" (
    call :run_pylint || goto :pylint_failed
    poetry run pytest tests
    poetry build    
) ELSE IF "%1"=="clean" (
    rmdir /S /Q dist build mqtt_presence.egg-info 2>nul
) ELSE IF "%1"=="pylint" (
    call :run_pylint || goto :pylint_failed
) ELSE IF "%1"=="pytest" (
    call :run_pytest || goto :pytest_failed
) ELSE (
    echo "Usage: make.bat [build|clean|pylint]"
)



goto :eof



:run_pylint
echo Running pylint...
poetry run pylint mqtt_presence
goto :eof

:pylint_failed
echo ❌ pylint reported issues. Aborting.
exit /b 1



:run_pytest
echo Running pylint...
poetry run pytest tests
goto :eof

:pytest_failed
echo ❌ pytest reported issues. Aborting.
exit /b 1

	