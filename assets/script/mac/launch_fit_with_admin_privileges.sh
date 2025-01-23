#!/bin/bash

PYTHON_PATH=${1:-}
APP_PATH=${2:-}

# Log the initial value of APP_PATH to Console.app and console
logger "fit --- Initial APP_PATH: $APP_PATH"

if [[ -z "$PYTHON_PATH" ]]; then
    # Temporary destination directory
    DEST_DIR="/tmp/__FIT__"

    # Remove temporary destination directory
    rm -rf "$DEST_DIR"

    # Create the destination directory (if it doesn't exist)
    mkdir -p "$DEST_DIR"

    # Get the parent directory of the executable (Fit.app directory)
    FIT_APP_DIR=$(dirname "$(dirname "$(dirname "$APP_PATH")")")

    # Log the Fit.app directory
    logger "fit --- Fit.app directory: $FIT_APP_DIR"

    # Copy the entire Fit.app directory to the destination
    cp -Rf "$FIT_APP_DIR" "$DEST_DIR/"

    # Update APP_PATH to point to the new location of the executable
    APP_PATH="$DEST_DIR/$(basename "$FIT_APP_DIR")/Contents/MacOS/$(basename "$APP_PATH")"

    # Log the updated value of APP_PATH to Console.app and console
    logger "fit --- Updated APP_PATH: $APP_PATH"

    echo "Missing Python path. Starting without the Python argument."
    osascript -e "do shell script \"launchctl asuser $(id -u) '${APP_PATH}'\" with administrator privileges"
else
    logger "fit --- Starting with Python: $PYTHON_PATH"
    osascript -e "do shell script \"launchctl asuser $(id -u) '${PYTHON_PATH}' '${APP_PATH}'\" with administrator privileges"
fi