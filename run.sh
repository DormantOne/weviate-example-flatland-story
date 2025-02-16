#!/bin/bash

echo "🚀 Starting Flatland Explorer..."

# 1. Activate virtual environment
source venv/bin/activate

set -a  # Automatically export all variables
source .env
set +a  # Stop automatically exporting

# 3. Start Weaviate if not running
echo "Starting Weaviate..."
docker compose up -d
sleep 5  # Give Weaviate time to start

# 4. Start the server
echo "Starting Flask application..."
python3 start_server.py