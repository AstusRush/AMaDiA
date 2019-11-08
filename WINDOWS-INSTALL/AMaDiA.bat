cd "C:\Users\%USERNAME%\AMaDiA"
git pull
call "C:\Users\%USERNAME%\Anaconda3\Scripts\activate.bat"
"C:\Users\%USERNAME%\Anaconda3\python.exe" "C:\Users\%USERNAME%\AMaDiA\AMaDiA.py"
if NOT ["%errorlevel%"]==["0"] pause
