@echo off
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting Print Queue server...
python app.py
pause
