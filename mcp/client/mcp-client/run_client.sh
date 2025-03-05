#!/bin/bash

# Script to run the MCP client with proper environment setup

# Change to the script's directory
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your AWS credentials."
    echo "You can copy .env.sample and fill in the required values."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    uv venv .venv
    source .venv/bin/activate
    uv sync
else
    source .venv/bin/activate
fi

# Check AWS credentials
echo "Testing AWS credentials..."
python test_aws_credentials.py
CRED_STATUS=$?

if [ $CRED_STATUS -ne 0 ]; then
    echo ""
    echo "AWS credential test failed. Would you like to:"
    echo "1) Continue with mock responses (no real API calls)"
    echo "2) Exit and fix credentials"
    read -p "Enter choice [1/2]: " choice
    
    if [ "$choice" = "1" ]; then
        echo "Setting USE_MOCK_RESPONSE=true"
        export USE_MOCK_RESPONSE=true
    else
        echo "Exiting. Please fix your AWS credentials and try again."
        exit 1
    fi
fi

# Run the client with the specified server
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_server_module>"
    echo "Example: $0 ../../server/weather/weather.py"
    exit 1
fi

echo "Starting MCP client..."
uv run client.py "$1"