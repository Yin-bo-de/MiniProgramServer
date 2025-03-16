#!/bin/bash
PROJECT_DIR=$1
VENV_NAME=".venv"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project_directory>"
    exit 1
fi

cd "$PROJECT_DIR" || exit
python3 -m venv "$VENV_NAME"
echo "Virtual environment created at $PROJECT_DIR/$VENV_NAME"
source .venv/bin/activate # 进入虚拟环境