#!/bin/sh
cd `dirname $0`

VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"
ENV_ERROR="This module requires Python, pip, and virtualenv to be installed."

# Check if already installed the python packages
if [ -f .installed ]; then
    # We are already done!
    exit 0
fi
# Attempt to create a virtual environment, and if it fails, try to install python3-venv
if ! python3 -m venv $VENV_NAME; then
    echo "Failed to create virtualenv." >&2
    # Try to install python3-venv
    if command -v apt-get >/dev/null; then
        echo "$ENV_ERROR" >&2
        exit 1
    fi
    echo "Detected Debian/Ubuntu, attempting to install python3-venv automatically."
    SUDO="sudo"
    # Run apt-get update by default, but only if it's available
    echo "Updating package lists..."
    if ! $SUDO apt-get update; then
        echo "Failed to update package lists." >&2
        exit 1
    fi
    # Install python3-venv, and gracefully exit if it fails
    echo "Installing python3-venv..."
    if ! $SUDO apt-get install -y python3-venv; then
        echo "Failed to install python3-venv." >&2
        exit 1
    fi
    # Create the virtual environment, and gracefully exit if it fails
    if ! python3 -m venv $VENV_NAME; then
        echo "$ENV_ERROR" >&2
        exit 1
    fi
fi

echo "Virtualenv found/created. Installing Python packages..."
if ! $PYTHON -m pip install -r requirements.txt -q; then
    echo "Failed to install Python packages. Please try again." >&2
    exit 1
fi

touch .installed
echo "Python packages installed successfully."
