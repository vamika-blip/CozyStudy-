#!/bin/bash
# CozyStudy Launcher Script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if command -v python3 &>/dev/null; then
    python3 main.py
elif command -v /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 &>/dev/null; then
    /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 main.py
else
    echo "Python 3 is required to run CozyStudy."
fi
