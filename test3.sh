export PYTHON=python3   # Should be a path to Python3.6 or Python 3.10, e.g. /usr/local/Cellar/python@3.10/3.10.10_1/bin/python3.10
export PYTHONIOENCODING=utf8

export HOME_DIR=$(pwd)
export SAMPLE_DATA_DIR=$HOME_DIR/sample_data
export RESULT_DIR=$HOME_DIR/testresults/3


printf "Removing old test results...\n"
rm -rf $RESULT_DIR
mkdir -p $RESULT_DIR
printf "Removing old test results...  - Done\n"

printf "Creating new test results...\n"

printf "    - .tpeg->.result... "
find $SAMPLE_DATA_DIR -name '*.tpeg' -type f -exec bash -c '$PYTHON $HOME_DIR/TPEG/TPEG_parser.py {} > "$RESULT_DIR/$(basename {} .tpeg).result"' \;
printf " - Done\n"
printf "    - .tpg->.result... "
find $SAMPLE_DATA_DIR -name '*.tpg' -type f -exec bash -c '$PYTHON $HOME_DIR/TPEG/TPEG_parser.py {} > "$RESULT_DIR/$(basename {} .tpg).result"' \;
printf " - Done\n"

printf "    - .cap->.txt... "
find $SAMPLE_DATA_DIR -name '*.cap' -type f -exec bash -c '$PYTHON $HOME_DIR/CAP/CAP_to_text.py {} > "$RESULT_DIR/$(basename {} .cap).txt"' \;
printf " - Done\n"

printf "    - .cap->.eaw... "
find $SAMPLE_DATA_DIR -name '*.cap' -type f -exec bash -c '$PYTHON $HOME_DIR/CAP/CAP_to_EAW.py {} > "$RESULT_DIR/$(basename {} .cap).eaw"' \;
printf " - Done\n"

printf "    - .cap->.kml... "
find $SAMPLE_DATA_DIR -name '*.cap' -type f -exec bash -c '$PYTHON $HOME_DIR/CAP/CAP_to_KML.py {} > "$RESULT_DIR/$(basename {} .cap).kml"' \;
printf " - Done\n"

printf "    - .cap->.wkt... "
find $SAMPLE_DATA_DIR -name '*.cap' -type f -exec bash -c '$PYTHON $HOME_DIR/CAP/CAP_SHN_to_WKT.py {} > "$RESULT_DIR/$(basename {} .cap).wkt"' \;
printf " - Done\n"

printf "    - .cap->.genWKT... "
find $SAMPLE_DATA_DIR -name '*.cap' -type f -exec bash -c '$PYTHON $HOME_DIR/CAP/CAP_generalise_WKT.py {} > "$RESULT_DIR/$(basename {} .cap).genWKT"' \;
printf " - Done\n"

printf "Creating new test results...  - Done\n"
printf "Please check newly generated files in $RESULT_DIR\n"