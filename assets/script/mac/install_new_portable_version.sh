#!/bin/bash


if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path_to_dmg_file> [destination_folder]" >&2
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Usage: $0 <path_to_dmg_file> [destination_folder]"
  exit 1
fi


DMG_PATH="$1"
DEST_DIR="${2:-/Applications}"
MOUNT_DIR="/Volumes/InstallDMG"


if [ ! -f "$DMG_PATH" ]; then
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: File $DMG_PATH not found."
  exit 1
fi


if [ ! -d "$DEST_DIR" ]; then
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Destination directory $DEST_DIR does not exist."
  exit 1
fi

logger "FIT --- INSTALL NEW PORTABLE VERSION: Mounting $DMG_PATH..."
hdiutil attach "$DMG_PATH" -nobrowse -mountpoint "$MOUNT_DIR" || {
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Failed to mount the DMG file."
  exit 1
}


APP_PATH=$(find "$MOUNT_DIR" -type d -name "*.app" | head -n 1)
logger "FIT --- INSTALL NEW PORTABLE VERSION: Info APP_PATH: $APP_PATH"

if [ -z "$APP_PATH" ]; then
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: No application found inside the DMG."
  hdiutil detach "$MOUNT_DIR"
  exit 1
fi

APP_NAME=$(basename "$APP_PATH")
TARGET_PATH="$DEST_DIR/$APP_NAME"
logger "FIT --- INSTALL NEW PORTABLE VERSION: Info TARGET_PATH: $TARGET_PATH"

if [ -d "$TARGET_PATH" ]; then
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Info Removing existing version of $APP_NAME in $DEST_DIR..."
  rm -rf "$TARGET_PATH" || {
    logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Failed to remove the old version."
    hdiutil detach "$MOUNT_DIR"
    exit 1
  }
fi


logger  "FIT --- INSTALL NEW PORTABLE VERSION: Info Copying $APP_PATH to $DEST_DIR..."

cp -R "$APP_PATH" "$DEST_DIR" || {
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Failed to copy the application."
  hdiutil detach "$MOUNT_DIR"
  exit 1
}


logger "FIT --- INSTALL NEW PORTABLE VERSION: Info Unmounting the DMG..."
hdiutil detach "$MOUNT_DIR" || {
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Failed to unmount the DMG."
  exit 1
}

logger "FIT --- INSTALL NEW PORTABLE VERSION: Info Launching $APP_NAME..."
open "$TARGET_PATH" || {
  logger "FIT --- INSTALL NEW PORTABLE VERSION: Error: Failed to launch the application."
  exit 1
}

logger "FIT --- INSTALL NEW PORTABLE VERSION: Info Installation and launch completed successfully in $DEST_DIR!"
exit 0
