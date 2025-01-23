#!/bin/bash

PYTHON_PATH=${1:-}
APP_PATH=${2:-}

if [[ -z "$PYTHON_PATH" ]]; then
    echo "Missing Python path. Starting without the Python argument."
    logger "fit: Missing Python path. Starting without the Python argument."
    osascript -e "do shell script \"launchctl asuser $(id -u) '${APP_PATH}'\" with administrator privileges"
else
    echo "Starting with Python: $PYTHON_PATH"
    osascript -e "do shell script \"launchctl asuser $(id -u) '${PYTHON_PATH}' '${APP_PATH}'\" with administrator privileges"
fi