#!/bin/bash


if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path_to_gz_file> [destination_folder]" >&2
  exit 1
fi

GZ_PATH="$1"
DEST_DIR="${2:-/opt}"
TEMP_DIR="/tmp/InstallApp"

if [ ! -f "$GZ_PATH" ]; then
  echo "Error: File $GZ_PATH not found." >&2
  exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
  echo "Error: Destination directory $DEST_DIR does not exist." >&2
  exit 1
fi


mkdir -p "$TEMP_DIR"

echo "Extracting $GZ_PATH..."
gzip -d "$GZ_PATH" || {
  echo "Error: Failed to extract the .gz file." >&2
  exit 1
}


EXTRACTED_FILE="${GZ_PATH%.gz}"


if [ ! -f "$EXTRACTED_FILE" ]; then
  echo "Error: Extraction failed, no file found at $EXTRACTED_FILE" >&2
  exit 1
fi


echo "Copying $EXTRACTED_FILE to $DEST_DIR..."
cp "$EXTRACTED_FILE" "$DEST_DIR" || {
  echo "Error: Failed to copy the extracted file." >&2
  exit 1
}


echo "Cleaning up temporary files..."
rm -f "$EXTRACTED_FILE"

echo "Launching $EXTRACTED_FILE..."
"$DEST_DIR/$(basename "$EXTRACTED_FILE")" || {
  echo "Error: Failed to launch the application." >&2
  exit 1
}

echo "Installation and launch completed successfully in $DEST_DIR!"
exit 0