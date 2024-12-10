#!/bin/bash

# Controlla gli argomenti
PYTHON_PATH=${1:-}
APP_PATH=${2:-}

if [[ -z "$PYTHON_PATH" ]]; then
    echo "Percorso di Python mancante. Avvio senza argomento Python."
    osascript -e "do shell script \"launchctl asuser $(id -u) '${APP_PATH}'\" with administrator privileges"
else
    echo "Avvio con Python: $PYTHON_PATH"
    osascript -e "do shell script \"launchctl asuser $(id -u) '${PYTHON_PATH}' '${APP_PATH}'\" with administrator privileges"
fi