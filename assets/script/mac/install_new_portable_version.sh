#!/bin/bash


if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path_to_dmg_file> [destination_folder]" >&2
  logger "fit --- Usage: $0 <path_to_dmg_file> [destination_folder]"
  exit 1
fi


DMG_PATH="$1"
DEST_DIR="${2:-/Applications}"
MOUNT_DIR="/Volumes/InstallDMG"


if [ ! -f "$DMG_PATH" ]; then
  echo "Error: File $DMG_PATH not found." >&2
  logger "fit --- Error: File $DMG_PATH not found."
  exit 1
fi


if [ ! -d "$DEST_DIR" ]; then
  echo "Error: Destination directory $DEST_DIR does not exist." >&2
  logger "fit --- Error: Destination directory $DEST_DIR does not exist."
  exit 1
fi

echo "Mounting $DMG_PATH..."
hdiutil attach "$DMG_PATH" -nobrowse -mountpoint "$MOUNT_DIR" || {
  echo "Error: Failed to mount the DMG file." >&2
  logger "fit --- Error: Failed to mount the DMG file."
  exit 1
}


APP_PATH=$(find "$MOUNT_DIR" -type d -name "*.app" | head -n 1)

if [ -z "$APP_PATH" ]; then
  echo "Error: No application found inside the DMG." >&2
  logger "fit --- Error: No application found inside the DMG."
  hdiutil detach "$MOUNT_DIR"
  exit 1
fi


APP_NAME=$(basename "$APP_PATH")
TARGET_PATH="$DEST_DIR/$APP_NAME"

if [ -d "$TARGET_PATH" ]; then
  echo "Removing existing version of $APP_NAME in $DEST_DIR..."
  rm -rf "$TARGET_PATH" || {
    echo "Error: Failed to remove the old version." >&2
    logger "fit --- Error: Failed to remove the old version."
    hdiutil detach "$MOUNT_DIR"
    exit 1
  }
fi


echo "Copying $APP_PATH to $DEST_DIR..."
cp -R "$APP_PATH" "$DEST_DIR" || {
  echo "Error: Failed to copy the application." >&2
  logger "fit --- Error: Failed to copy the application."
  hdiutil detach "$MOUNT_DIR"
  exit 1
}


echo "Unmounting the DMG..."
hdiutil detach "$MOUNT_DIR" || {
  echo "Error: Failed to unmount the DMG." >&2
  logger "fit --- Error: Failed to unmount the DMG."
  exit 1
}


echo "Launching $APP_NAME..."
open "$TARGET_PATH" || {
  echo "Error: Failed to launch the application." >&2
  logger "fit --- Error: Failed to launch the application."
  exit 1
}

echo "Installation and launch completed successfully in $DEST_DIR!"
logger "fit --- Installation and launch completed successfully in $DEST_DIR!"
exit 0
