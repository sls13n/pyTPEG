SET PYTHON="C:\Python311\python.exe"
SET HOMEDIR=d:\work\evaluation-kit
SET RESULTDIR=%HOMEDIR%\testresults\3

set PYTHONIOENCODING=utf8

rmdir /s /q %RESULTDIR%
mkdir %RESULTDIR%

forfiles /S /P sample_data /M *.tpeg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"
forfiles /S /P sample_data /M *.tpg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"

forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_text.py @PATH >%RESULTDIR%\@FILE.txt"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_EAW.py --output_dir="%RESULTDIR%" @PATH >%RESULTDIR%\@FILE.eaw"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_KML.py @PATH >%RESULTDIR%\@FILE.kml"

forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_SHN_to_WKT.py @PATH >%RESULTDIR%\@FILE.wkt"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_generalise_WKT.py --output_dir="%RESULTDIR%" @PATH >%RESULTDIR%\@FILE.genWKT"
