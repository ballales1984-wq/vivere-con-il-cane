#!/bin/bash
set -e

# Install system dependencies for pycairo
apt-get update
apt-get install -y libcairo2-dev pkg-config python3-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt || pip install --no-deps -r requirements.txt
