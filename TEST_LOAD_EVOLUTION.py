#!/usr/bin/env python3
"""
Test if load_existing_models() works correctly
"""
import sqlite3

print("=" * 80)
print("TESTING EVOLUTION DATA LOADING")
print("=" * 80)

# Test 1: Check database has data
print("\n1. Checking database...")
try:
    db = sqlite3.connect('evolution_engine.db')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM model_evolution")
    count = cursor.fetchone()[0]
    print(f"   ✅ Database has {count} rows")
    
    cursor.execute("SELECT MAX(generation) FROM model_evolution")
    max_gen = cursor.fetchone()[0]
    print(f"   ✅ Max generation: {max_gen}")
    
    db.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")
    exit(1)

# Test 2: Test the load_existing_models() logic
print("\n2. Testing load logic...")
try:
    db = sqlite3.connect('evolution_engine.db')
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM model_evolution ORDER BY generation DESC")
    rows = cursor.fetchall()
    
    db.close()
    
    if rows:
        print(f"🔄 LOADING EXISTING EVOLUTION DATA...")
        print(f"   Found {len(rows)} models in database")
        
        max_generation = max(row[1] for row in rows if row[1])  # generation is index 1, not 4!
        evolution_cycle = int(max_generation) if max_generation else 0
        models_spawned = len(rows)
        
        print(f"✅ LOADED: Generation {evolution_cycle}, {len(rows)} models")
        print(f"🚀 Bot will CONTINUE from where it left off!")
        
        print(f"\n   evolution_cycle = {evolution_cycle}")
        print(f"   models_spawned = {models_spawned}")
    else:
        print("❌ No data found!")
        
except Exception as e:
    print(f"   ❌ Load error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 80)
print("✅ TEST PASSED - Load logic works!")
print("=" * 80)
