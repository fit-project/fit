#!/bin/bash


if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path_to_dmg_file> [destination_folder]" >&2
  exit 1
fi


DMG_PATH="$1"
DEST_DIR="${2:-/Applications}"
MOUNT_DIR="/Volumes/InstallDMG"


if [ ! -f "$DMG_PATH" ]; then
  echo "Error: File $DMG_PATH not found." >&2
  exit 1
fi


if [ ! -d "$DEST_DIR" ]; then
  echo "Error: Destination directory $DEST_DIR does not exist." >&2
  exit 1
fi

echo "Mounting $DMG_PATH..."
hdiutil attach "$DMG_PATH" -nobrowse -mountpoint "$MOUNT_DIR" || {
  echo "Error: Failed to mount the DMG file." >&2
  exit 1
}


APP_PATH=$(find "$MOUNT_DIR" -type d -name "*.app" | head -n 1)

if [ -z "$APP_PATH" ]; then
  echo "Error: No application found inside the DMG." >&2
  hdiutil detach "$MOUNT_DIR"
  exit 1
fi


APP_NAME=$(basename "$APP_PATH")
TARGET_PATH="$DEST_DIR/$APP_NAME"

if [ -d "$TARGET_PATH" ]; then
  echo "Removing existing version of $APP_NAME in $DEST_DIR..."
  rm -rf "$TARGET_PATH" || {
    echo "Error: Failed to remove the old version." >&2
    hdiutil detach "$MOUNT_DIR"
    exit 1
  }
fi


echo "Copying $APP_PATH to $DEST_DIR..."
cp -R "$APP_PATH" "$DEST_DIR" || {
  echo "Error: Failed to copy the application." >&2
  hdiutil detach "$MOUNT_DIR"
  exit 1
}


echo "Unmounting the DMG..."
hdiutil detach "$MOUNT_DIR" || {
  echo "Error: Failed to unmount the DMG." >&2
  exit 1
}


echo "Launching $APP_NAME..."
open "$TARGET_PATH" || {
  echo "Error: Failed to launch the application." >&2
  exit 1
}

echo "Installation and launch completed successfully in $DEST_DIR!"
exit 0
