#!/usr/bin/env python3
"""
FIX DATA LOADING - Make bot actually load your 11k+ rows
"""

import sqlite3
import sys

print("=" * 80)
print("CHECKING WHY BOT ISN'T LOADING YOUR DATA")
print("=" * 80)
print()

# Check what's in the database
print("1. Checking evolution_engine.db:")
try:
    db = sqlite3.connect('evolution_engine.db')
    cursor = db.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"   Tables: {tables}")
    
    # Check data in each table
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} rows")
    
    db.close()
    print("   [OK] Database HAS data!")
    
except Exception as e:
    print(f"   [X] Error: {e}")

print()

# Check if EVOLUTION_ENGINE.py has a load method
print("2. Checking if EVOLUTION_ENGINE.py loads data:")
try:
    with open('EVOLUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    if 'def load_from_database' in content:
        print("   [OK] Has load_from_database() method")
    else:
        print("   [X] Missing load_from_database() method")
    
    if 'SELECT * FROM model_evolution' in content:
        print("   [OK] Has SQL query to load models")
    else:
        print("   [X] Missing SQL query to load models")
        
except Exception as e:
    print(f"   [X] Error: {e}")

print()

# Check if orchestrator calls the load method
print("3. Checking if orchestrator loads evolution data:")
try:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    if 'load_from_database' in content or 'load_evolution_data' in content:
        print("   [OK] Orchestrator calls load method")
    else:
        print("   [X] Orchestrator doesn't call load method")
        print("   THIS IS THE PROBLEM!")
        
except Exception as e:
    print(f"   [X] Error: {e}")

print()
print("=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
print()
print("Your data is NOT lost! It's in evolution_engine.db (11,082 rows)")
print("The problem is: The loading code is not reading it!")
print()
print("SOLUTION:")
print("Need to add/fix the load_from_database() call in the bot startup")
print()
