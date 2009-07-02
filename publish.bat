rmdir /S /Q dist
rmdir /S /Q build
setup.py py2exe -O 2 -b 1 -c
del "dist\w9xpopen.exe"