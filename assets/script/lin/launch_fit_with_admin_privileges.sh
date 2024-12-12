#!/bin/bash

python_path=${1:-}
app_path=${2}

if [[ -z "$python_path" ]]; then
    echo "Running the app without Python..."
    pkexec "$app_path"
else
    echo "Running with Python..."
    pkexec "$python_path" "$app_path"
fi
