@echo off
echo Starting Underwriting Dashboard with fixes applied...
echo.

:: Run the fixed dashboard Python script
python run_fixed_dashboard.py

:: If there was an error, pause so the user can see it
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error running dashboard. See message above.
    pause
)
