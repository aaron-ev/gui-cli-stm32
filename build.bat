::
:: Author: Aaron Escoboza
::
set executableName=GuiControl
set mainFileName=main
set mainPythonScript=%mainFileName%.py
set currentDir=%cd%
set appPath=%currentDir%\src\%mainPythonScript%
set imgPath=%currentDir%/img
set iconPath=%imgPath%/icon.ico

python -m PyInstaller --icon=%iconPath% --onefile -w --noconsole  --add-data="./img/*.png;img/" ^
--add-data="./img/*.ico;img/" %appPath%

if not %errorlevel%==0 (
    echo "Build failded, error code %errorlevel%"
    exit /b %errorlevel%
)

:: Copy executable to root folder and remnove not needed folders
copy %currentDir%\dist\*.exe %currentDir%
echo Y | rmdir /s %currentDir%\dist
echo Y | rmdir /s %currentDir%\build
del %currentDir%\*.spec

copy %currentDir%\%mainFileName%.exe %currentDir%\%executableName%.exe
del %currentDir%\%mainFileName%.exe

pause
