#!/bin/bash

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="${SCRIPT_DIR}/backend"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"

# Change to backend directory
cd "${BACKEND_DIR}"

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "🔧 Creating .env file from .env.example"
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration"
fi

# Initialize the database
echo "🚀 Initializing database..."
python "${BACKEND_DIR}/init_db.py"

# Start the FastAPI server
echo "🚀 Starting Orbyte API server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Server is running at http://localhost:8000"
echo "📚 API documentation is available at http://localhost:8000/api/docs"
