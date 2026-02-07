# TPEG2 Evaluation Kit

## Installation
Installation is easy, just follow these steps.
### 1. Install the latest Python 3 distribution version
Download the installation package from https://www.python.org/downloads
The scripts were tested with Python **3.10.6** and **3.11.1**, in case you find any incompatiblity please open an issue!
### 2. Extract files to a suitable location
Clone this repo or download it in a zip package and extract the files.
## Running the scripts
The scripts themselves can be run as follows: 
```
python.exe <path_and_filename_of_script> <filename_of_content_to_read>
```
Try to run test commands in a command prompt, make sure to check these test scripts:
- Windows: `test3.bat`
- UNIX: `test3.sh`

For reference, there is a full script from the `test3.bat` file. **Before running the script, make sure to adjust directory paths in the first two lines.**
```
SET PYTHON=c:\PYTHON311\python.exe
SET HOMEDIR=d:\work\evaluation-kit
SET RESULTDIR=%HOMEDIR%\testresults\3

set PYTHONIOENCODING=utf8

rmdir /s /q %RESULTDIR%
mkdir %RESULTDIR%

forfiles /S /P sample_data /M *.tpeg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"
forfiles /S /P sample_data /M *.tpg /C "cmd.exe /C %PYTHON% %HOMEDIR%\TPEG\TPEG_parser.py @PATH >%RESULTDIR%\@FILE.result"

forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_text.py @PATH >%RESULTDIR%\@FILE.txt"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_EAW.py @PATH >%RESULTDIR%\@FILE.eaw"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_to_KML.py @PATH >%RESULTDIR%\@FILE.kml"

forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_SHN_to_WKT.py @PATH >%RESULTDIR%\@FILE.wkt"
forfiles /S /P sample_data /M *.cap /C "cmd.exe /C %PYTHON% %HOMEDIR%\CAP\CAP_generalise_WKT.py @PATH >%RESULTDIR%\@FILE.genWKT"
```
You will find this code block in test3.bat as well in the root folder.
## Short description of functionality
### TPEG_parser.py
This utility parsers TPEG binary frames with either TEC or EAW messages. Frames may be (zlib) compressed. Output is sent to the screen. The Location Referencing methods TMC, ETL, GLR and OLR (geographic locations only) are supported.
### CAP_to_text.py
This utility takes a CAP (xml) file, parses the input and sends the decoded output to the screen, in a format similar to the TPEG_parser.
### CAP_to_EAW.py
This utility converts CAP messages/files into a TPEG binary frame containing EAW messages. By default OLR location referencing is used, GLR is optional. SHN area codes and WKT geocodes are converted to polygons for this purpose.
### CAP_to_KML.py
This utility converts CAP messages/files into a KML file that can be shown with Google Earth. SHN area codes and WKT geocodes are converted to polygons.
### CAP_SHN_to_WKT.py
Utility to only convert SHN area codes into WKT geocodes in the CAP file.
### CAP_generalise_WKT.py
Utility to reduce the number of coordinates in WKT geocodes, such that they can made fit with TPEG2 EAW size recommendations (total number coordinates in an EAW message < 400). This utility is based on a simple DouglasPeucker algorithm, and is not foolproof. Resulting generalized shapes need to be checked. (This functionality is also available in CAP_to_EAW utility).
## Bugs and feature requests
1. Go to the [Issues page](https://gitlab-tisa.org/tpeg2/evaluation-kit/-/issues) and click on the "New issue" button.
2. Fill out the Title and Description fields.
* In case of a bug please specify
  * What content did you use (you can attach it as a file to the issue)?
  * What are the steps to reproduce the bug?
  * What is the expected result?
  * What is the result you got?
  * Describe the software environment (at least operating system name and version, Python version).
* In case of a feature request please write down your requirements as detailed as possible.
3. Click on the "Create issue" button.
