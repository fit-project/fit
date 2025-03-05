if ($args.Count -lt 1) {
    Write-Host "Usage: .\$($MyInvocation.MyCommand.Name) <path_to_zip_file>" -ForegroundColor Red
    exit 1
}

$ZIP_PATH = $args[0]

if (-not (Test-Path -Path $ZIP_PATH)) {
    Write-Host "Error: File $ZIP_PATH not found." -ForegroundColor Red
    exit 1
}

$DEST_DIR = Join-Path -Path (Split-Path -Path $ZIP_PATH -Parent) -ChildPath ([System.IO.Path]::GetFileNameWithoutExtension($ZIP_PATH))

if (-not (Test-Path -Path $DEST_DIR)) {
    New-Item -ItemType Directory -Path $DEST_DIR | Out-Null
}

Write-Host "Extracting $ZIP_PATH to $DEST_DIR..."
Start-Sleep -Seconds 2

try {
    Expand-Archive -Path $ZIP_PATH -DestinationPath $DEST_DIR -Force
} catch {
    Write-Host "Error: Failed to extract the ZIP file." -ForegroundColor Red
    exit 1
}

$APP_NAME = Get-ChildItem -Path $DEST_DIR -Recurse -Filter "*.exe" | Select-Object -First 1

if ($null -eq $APP_NAME) {
    Write-Host "Error: No executable found in $DEST_DIR." -ForegroundColor Red
    exit 1
}

Write-Host "Launching $APP_NAME..."
Start-Sleep -Seconds 2

$exePath = $APP_NAME.FullName
if (Test-Path -Path $exePath) {
    Start-Process -FilePath $exePath
} else {
    Write-Host "Error: Executable not found at $exePath." -ForegroundColor Red
    exit 1
}

Write-Host "Launch $exePath" -ForegroundColor Green

Write-Host "Waiting for 10 seconds before exit..."
Start-Sleep -Seconds 10