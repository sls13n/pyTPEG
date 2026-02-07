SET PYTHON="C:\Python311\python.exe"
SET HOMEDIR=d:\work\evaluation-kit
SET RESULTDIR=%HOMEDIR%\testresults\3

set PYTHONIOENCODING=utf8

rmdir /s /q %RESULTDIR%
mkdir %RESULTDIR%

forfiles /S /P sample_data /M *.tpeg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"
forfiles /S /P sample_data /M *.tpg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"
