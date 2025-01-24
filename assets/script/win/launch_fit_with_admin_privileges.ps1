param(
    [string]$PythonPath,
    [string]$AppPath
)

# Check if the parameters are provided
if (-not $AppPath) {
    Write-Host "Error: The app path was not provided." -ForegroundColor Red
    exit 1
}

if ($PythonPath -and -not (Test-Path $PythonPath)) {
    Write-Host "Error: The Python path is not valid." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $AppPath)) {
    Write-Host "Error: The app path is not valid." -ForegroundColor Red
    exit 1
}

try {
    # Check if Python is specified
    if (-not $PythonPath) {
        Write-Host "Starting the app without Python..."
        Start-Process -FilePath $AppPath -Verb RunAs
    } else {
        Write-Host "Starting the app with Python..."
        Start-Process -FilePath $PythonPath -ArgumentList $AppPath -Verb RunAs
    }
} catch {
    Write-Host "Error: Operation canceled or not executed correctly." -ForegroundColor Red
    exit 1
}

Write-Host "The operation completed successfully." -ForegroundColor Green