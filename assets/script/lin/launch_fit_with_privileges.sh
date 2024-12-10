#!/bin/bash

python_path=${1:-}
app_path=${2}

if [[ -z "$python_path" ]]; then
    echo "Esecuzione dell'app senza Python..."
    pkexec "$app_path"
else
    echo "Esecuzione con Python..."
    pkexec "$python_path" "$app_path"
fi
