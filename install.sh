#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # For Unix/MacOS
# OR use: .\venv\Scripts\activate  # For Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

