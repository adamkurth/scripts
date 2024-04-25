#!/bin/bash 
if [ $# -eq 0 ]; then 
    echo "No files provided for Albula."
    exit 1
fi

albula_command="albula"
$albula_command "$@"