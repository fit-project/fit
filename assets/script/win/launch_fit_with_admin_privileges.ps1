$python_path = $args[0]
$app_path = $args[1]

if (-not $python_path) {
    Write-Host "Running the app without Python..."
    Start-Process -FilePath $app_path -Verb RunAs
} else {
    Write-Host "Running with Python..."
    Start-Process -FilePath $python_path -ArgumentList $app_path -Verb RunAs
}