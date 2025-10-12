#!/usr/bin/env python3
"""
NumPy 2.x Compatibility Fix Script

This script helps fix the NumPy compatibility issue where modules compiled with
NumPy 1.x cannot run with NumPy 2.x. The error occurs because OpenCV (cv2) and
other modules were compiled with NumPy 1.x but are trying to run with NumPy 2.3.3.

Usage:
    python fix_numpy_compatibility.py
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_numpy_version():
    """Check current NumPy version."""
    try:
        import numpy
        version = numpy.__version__
        print(f"📊 Current NumPy version: {version}")
        return version
    except ImportError:
        print("❌ NumPy not installed")
        return None

def fix_numpy_compatibility():
    """Fix NumPy compatibility by downgrading to 1.x."""
    print("🔧 Fixing NumPy 2.x compatibility issue...")
    
    # Check current version
    current_version = check_numpy_version()
    if current_version and current_version.startswith('1.'):
        print("✅ NumPy is already at 1.x version - no fix needed")
        return True
    
    # Uninstall current NumPy
    print("🗑️  Uninstalling current NumPy...")
    run_command("pip uninstall numpy -y", "Uninstalling NumPy")
    
    # Install compatible NumPy version
    print("📦 Installing NumPy 1.x compatible version...")
    result = run_command("pip install 'numpy>=1.26.4,<2.0'", "Installing NumPy 1.x")
    
    if result:
        # Verify installation
        new_version = check_numpy_version()
        if new_version and new_version.startswith('1.'):
            print("✅ NumPy compatibility fix completed successfully!")
            print(f"📊 New NumPy version: {new_version}")
            return True
        else:
            print("❌ NumPy compatibility fix failed")
            return False
    else:
        print("❌ Failed to install compatible NumPy version")
        return False

def reinstall_opencv():
    """Reinstall OpenCV to ensure compatibility with NumPy 1.x."""
    print("🔄 Reinstalling OpenCV for NumPy 1.x compatibility...")
    
    # Uninstall OpenCV
    run_command("pip uninstall opencv-python opencv-contrib-python -y", "Uninstalling OpenCV")
    
    # Install specific OpenCV version that's compatible with NumPy 1.x
    # Using --no-deps to prevent automatic NumPy 2.x installation
    run_command("pip install 'opencv-python==4.8.1.78' --no-deps", "Installing OpenCV 4.8.1.78")
    
    print("✅ OpenCV reinstallation completed")

def main():
    """Main function."""
    print("🚀 NumPy 2.x Compatibility Fix Tool")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment - consider using one")
    
    # Fix NumPy compatibility
    if fix_numpy_compatibility():
        # Reinstall OpenCV
        reinstall_opencv()
        
        print("\n🎉 All fixes completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your application")
        print("2. Test that the NumPy compatibility error is resolved")
        print("3. If issues persist, check other dependencies for NumPy 2.x compatibility")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()