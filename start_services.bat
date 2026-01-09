@echo off
echo ================================================================
echo    FACE RECOGNITION WEB APPLICATION - Service Launcher
echo ================================================================
echo.
echo Khoi dong 3 services:
echo   1. Main Web App (port 5000)
echo   2. Face Recognition Service (port 5001) - env: face_recognition
echo   3. DeepFace Service (port 5002) - env: deepface_recognition
echo.
echo ================================================================
echo.

REM Khởi động Face Recognition Service trong môi trường riêng
echo [1/3] Khoi dong Face Recognition Service (port 5001)...
start "Face Recognition Service" cmd /c "conda activate face_recognition && python face_recognition_service.py"
timeout /t 3 /nobreak >nul

REM Khởi động DeepFace Service trong môi trường riêng  
echo [2/3] Khoi dong DeepFace Service (port 5002)...
start "DeepFace Service" cmd /c "conda activate deepface_recognition && python deepface_service.py"
timeout /t 3 /nobreak >nul

REM Khởi động Main Web App
echo [3/3] Khoi dong Main Web Application (port 5000)...
start "Main Web App" cmd /c "python app.py"

echo.
echo ================================================================
echo HOAN THANH! Tat ca services dang khoi dong...
echo.
echo Vui long cho 30-60 giay de cac services load models.
echo.
echo Cac cua so terminal:
echo   - Face Recognition Service (port 5001)
echo   - DeepFace Service (port 5002)  
echo   - Main Web App (port 5000)
echo.
echo Truy cap: http://localhost:5000
echo ================================================================
echo.
pause
