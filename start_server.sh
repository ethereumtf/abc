#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Install dependencies
pip install -r requirements.txt

# Run the API server
python3 api.py
