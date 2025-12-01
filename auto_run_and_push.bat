@echo off
echo ===========================
echo Running all Python scripts
echo ===========================
python run_all.py

IF %ERRORLEVEL% NEQ 0 (
    echo Script execution failed. Aborting Git push.
    pause
    exit /b %ERRORLEVEL%
)

echo ===========================
echo Committing changes to Git
echo ===========================
git add .

REM Optional: use timestamp to avoid duplicate commit messages
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (set TODAY=%%a-%%b-%%c)
for /f "tokens=1-2 delims=: " %%h in ("%time%") do (set NOW=%%h-%%i)

git commit -m "Automated update on %TODAY% %NOW%"

echo ===========================
echo Pushing to GitHub
echo ===========================
git push

echo Done!
pause
