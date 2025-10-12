#!/bin/bash

# NumPy 2.x Compatibility Fix Deployment Script
# This script ensures NumPy 1.x compatibility for deployment environments

set -e  # Exit on any error

echo "🚀 Deploying with NumPy 2.x Compatibility Fix"
echo "=============================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Running in virtual environment: $VIRTUAL_ENV"
else
    echo "⚠️  Not in a virtual environment - consider using one"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Install/upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Uninstall problematic packages
echo "🗑️  Removing incompatible packages..."
python3 -m pip uninstall numpy opencv-python opencv-contrib-python -y || true

# Install NumPy 1.x first
echo "📊 Installing NumPy 1.x..."
python3 -m pip install "numpy>=1.26.4,<2.0"

# Install OpenCV with specific version (compatible with NumPy 1.x)
echo "👁️  Installing OpenCV compatible with NumPy 1.x..."
python3 -m pip install "opencv-python==4.8.1.78" --no-deps

# Install other dependencies from requirements
echo "📋 Installing other dependencies..."
if [ -f "requirements-deployment.txt" ]; then
    echo "Using requirements-deployment.txt..."
    python3 -m pip install -r requirements-deployment.txt
elif [ -f "requirements-full.txt" ]; then
    echo "Using requirements-full.txt..."
    python3 -m pip install -r requirements-full.txt
elif [ -f "requirements.txt" ]; then
    echo "Using requirements.txt..."
    python3 -m pip install -r requirements.txt
else
    echo "❌ No requirements file found!"
    exit 1
fi

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "
import numpy
import cv2
print(f'✅ NumPy version: {numpy.__version__}')
print(f'✅ OpenCV version: {cv2.__version__}')
print('✅ NumPy and OpenCV are compatible!')
"

# Test other common packages
echo "🧪 Testing other packages..."
python3 -c "
try:
    import pandas
    print(f'✅ Pandas version: {pandas.__version__}')
except ImportError:
    print('⚠️  Pandas not installed')

try:
    import sklearn
    print(f'✅ Scikit-learn version: {sklearn.__version__}')
except ImportError:
    print('⚠️  Scikit-learn not installed')

try:
    import torch
    print(f'✅ PyTorch version: {torch.__version__}')
except ImportError:
    print('⚠️  PyTorch not installed')
"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Summary:"
echo "- NumPy 1.x installed (compatible with OpenCV)"
echo "- OpenCV 4.8.1.78 installed (compatible with NumPy 1.x)"
echo "- Other dependencies installed from requirements"
echo ""
echo "✅ Your application should now work without NumPy 2.x compatibility errors!"