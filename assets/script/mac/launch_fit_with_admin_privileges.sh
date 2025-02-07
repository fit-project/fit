#!/bin/bash

PYTHON_PATH=${1:-}
APP_PATH=${2:-}

# Log the initial value of APP_PATH to Console.app and console
logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info Initial APP_PATH: $APP_PATH"

if [[ -z "$PYTHON_PATH" ]]; then
    # Temporary destination directory
    DEST_DIR="/tmp/__FIT__"

    # Remove temporary destination directory
    rm -rf "$DEST_DIR"

    # Create the destination directory (if it doesn't exist)
    mkdir -p "$DEST_DIR"

    ORIGINAL_APP_PATH_AND_USER="$DEST_DIR/original_app_path_and_user"

    # Write APP_PATH and UID to the file and check if it succeeds
    echo "$APP_PATH"":""$(id -u)" > "$ORIGINAL_APP_PATH_AND_USER"
    if [ $? -ne 0 ]; then
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Error: Unable to write to file $ORIGINAL_APP_PATH_AND_USER."
        exit 1
    else
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info: add "$APP_PATH:$UID" on $ORIGINAL_APP_PATH_AND_USER"
    fi

    # Set the owner of the file
    chown "$(id -u)" "$ORIGINAL_APP_PATH_AND_USER"
    if [ $? -ne 0 ]; then
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Error: Unable to change the owner of file $ORIGINAL_APP_PATH_AND_USER."
        exit 1
    else
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info change the owner of file $ORIGINAL_APP_PATH_AND_USER"
    fi

    # Set the permissions of the file
    chmod 777 "$ORIGINAL_APP_PATH_AND_USER"
    if [ $? -ne 0 ]; then
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Error: Unable to change the permissions of file $ORIGINAL_APP_PATH_AND_USER."
        exit 1
    else
        logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info change the permissions of file $ORIGINAL_APP_PATH_AND_USER"
    fi

    # Get the parent directory of the executable (Fit.app directory)
    FIT_APP_DIR=$(dirname "$(dirname "$(dirname "$APP_PATH")")")

    # Log the Fit.app directory
    logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info Fit.app directory: $FIT_APP_DIR"

    # Copy the entire Fit.app directory to the destination
    cp -Rf "$FIT_APP_DIR" "$DEST_DIR/"


    APP_PATH="$DEST_DIR/$(basename "$FIT_APP_DIR")/Contents/MacOS/$(basename "$APP_PATH")"

    logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info Starting $APP_PATH with administrator privileges"
    osascript -e "do shell script \"launchctl asuser $(id -u) '${APP_PATH}'\" with administrator privileges"
else
    logger "FIT --- START FIT WITH ADMINISTRATION PRIVILEGES: Info Starting $PYTHON_PATH and $APP_PATH with administrator privileges"
    osascript -e "do shell script \"launchctl asuser $(id -u) '${PYTHON_PATH}' '${APP_PATH}'\" with administrator privileges"
fi