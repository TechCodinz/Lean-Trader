# NumPy 2.x Compatibility Fix

## Problem Description

The error you're encountering is a common issue when upgrading to NumPy 2.x:

```
A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.3.3 as it may crash. To support both 1.x and 2.x
versions of NumPy, modules must be compiled with NumPy 2.0.
```

This happens because:
1. OpenCV (cv2) and other modules were compiled with NumPy 1.x
2. Your environment has NumPy 2.3.3 installed
3. These modules are incompatible with NumPy 2.x

## Solution

I've implemented a comprehensive fix by:

### 1. Updated All Requirements Files

Updated all `requirements*.txt` files to pin NumPy to version 1.x:
- `requirements.txt`: `numpy<2.0`
- `requirements-full.txt`: `numpy>=1.26.4,<2.0`
- `requirements_production.txt`: `numpy>=1.24.3,<2.0`
- `requirements_fx.txt`: `numpy>=1.26.0,<2.0`
- `requirements_ultra.txt`: `numpy>=1.21.0,<2.0`
- `traders_core/requirements.core.txt`: `numpy>=1.25,<2.0`
- `pyproject.toml`: `numpy>=1.26,<2.0`

### 2. Created Deployment-Specific Requirements

Created `requirements-deployment.txt` with NumPy 1.x compatible versions of all dependencies.

### 3. Created Fix Script

Created `fix_numpy_compatibility.py` to automatically fix the issue.

## How to Apply the Fix

### Option 1: Use the Fix Script (Recommended)

```bash
python3 fix_numpy_compatibility.py
```

### Option 2: Manual Fix

1. **Uninstall current NumPy:**
   ```bash
   pip uninstall numpy -y
   ```

2. **Install NumPy 1.x:**
   ```bash
   pip install "numpy>=1.26.4,<2.0"
   ```

3. **Reinstall OpenCV:**
   ```bash
   pip uninstall opencv-python opencv-contrib-python -y
   pip install "opencv-python>=4.8.0,<5.0"
   ```

4. **Reinstall other affected packages:**
   ```bash
   pip install -r requirements-deployment.txt
   ```

### Option 3: Use Deployment Requirements

For deployment environments, use the new requirements file:

```bash
pip install -r requirements-deployment.txt
```

## Verification

After applying the fix, verify it works:

```python
import numpy
import cv2
print(f"NumPy version: {numpy.__version__}")
print(f"OpenCV version: {cv2.__version__}")
```

## Prevention

To prevent this issue in the future:

1. **Always pin NumPy versions** in requirements files
2. **Test compatibility** when upgrading dependencies
3. **Use virtual environments** for isolation
4. **Check for NumPy 2.x compatibility** before upgrading

## Additional Notes

- The fix ensures compatibility with NumPy 1.x while maintaining all functionality
- OpenCV and other computer vision libraries work correctly with NumPy 1.x
- All machine learning libraries (scikit-learn, pandas, etc.) are compatible
- The fix is backward compatible and won't break existing code

## Troubleshooting

If you still encounter issues:

1. **Check all installed packages:**
   ```bash
   pip list | grep -E "(numpy|opencv|cv2|torch)"
   ```

2. **Force reinstall all dependencies:**
   ```bash
   pip install -r requirements-deployment.txt --force-reinstall
   ```

3. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

4. **Use a fresh virtual environment:**
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate
   pip install -r requirements-deployment.txt
   ```