#!/bin/bash

# Render Deployment Script
# Optimized for 8GB starter plan

echo "🚀 Deploying to Render with 8GB optimization..."

# Install dependencies
echo "📦 Installing lightweight dependencies..."
pip install -r requirements-render.txt

# Set environment variables
export STREAMLIT_SERVER_PORT=10000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start the Streamlit app
echo "🎯 Starting Streamlit dashboard..."
streamlit run streamlit_app.py --server.port=10000 --server.address=0.0.0.0