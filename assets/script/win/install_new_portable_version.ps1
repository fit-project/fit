if ($args.Count -lt 1) {
    Write-Host "Usage: .\$($MyInvocation.MyCommand.Name) <path_to_zip_file> [destination_folder]" -ForegroundColor Red
    exit 1
}

$ZIP_PATH = $args[0]
$DEST_DIR = if ($args.Count -ge 2) { $args[1] } else { "C:\Program Files" }


if (-not (Test-Path -Path $ZIP_PATH)) {
    Write-Host "Error: File $ZIP_PATH not found." -ForegroundColor Red
    exit 1
}


if (-not (Test-Path -Path $DEST_DIR)) {
    Write-Host "Error: Destination directory $DEST_DIR does not exist." -ForegroundColor Red
    exit 1
}

Write-Host "Extracting $ZIP_PATH..."
try {
    Expand-Archive -Path $ZIP_PATH -DestinationPath $DEST_DIR -Force
} catch {
    Write-Host "Error: Failed to extract the ZIP file." -ForegroundColor Red
    exit 1
}

$APP_NAME = Get-ChildItem -Path $DEST_DIR -Recurse -Filter "*.exe" | Select-Object -First 1

Write-Host "Launching $APP_NAME..."
$exePath = Join-Path -Path $DEST_DIR -ChildPath "\$APP_NAME"
if (Test-Path -Path $exePath) {
    Start-Process -FilePath $exePath
} else {
    Write-Host "Error: Executable not found in $TARGET_PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Installation and launch completed successfully in $DEST_DIR!" -ForegroundColor Green
exit 0