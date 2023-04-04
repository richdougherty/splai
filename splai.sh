#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIR"
exec python3 "$SCRIPT_DIR/splai/cli/main.py" "$@"