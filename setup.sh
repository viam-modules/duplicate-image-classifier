#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"
ENV_ERROR="This module requires Python, pip, and virtualenv to be installed."

if ! python3 -m venv $VENV_NAME; then
    echo "Failed to create virtualenv." >&2
    # If the virtualenv creation fails, we try to install python3-venv
    if command -v apt-get >/dev/null; then
        echo "Detected Debian/Ubuntu, attempting to install python3-venv automatically."
        SUDO="sudo"
        # If sudo is not available, we don't use it and use apt-get instead, making the script more portable
        if ! command -v $SUDO >/dev/null; then
            SUDO=""
        fi
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
    # If the system does not have apt-get, we exit with an error
    else
        echo "$ENV_ERROR" >&2
        exit 1
    fi
fi

echo "Virtualenv found/created. Installing Python packages..."
# Check if packages are already installed
if ! [ -f .installed ]; then
    if ! $PYTHON -m pip install -r requirements.txt -q; then
        echo "Failed to install Python packages. Please try again." >&2
        exit 1
    else
        touch .installed
        echo "Python packages installed successfully."
    fi
fi
