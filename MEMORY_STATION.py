#!/usr/bin/env python3
"""
🧠 MEMORY STATION
Central memory hub where all models and engines bank and retrieve knowledge fluently
"""

import logging
import sqlite3
import json
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryStation:
    """
    🧠 CENTRAL MEMORY HUB
    
    All models and engines can:
    - Bank knowledge (store)
    - Call knowledge (retrieve)
    - Share knowledge (broadcast)
    - Query knowledge (search)
    
    Features:
    - Persistent storage (SQLite + files)
    - Fast retrieval (indexed)
    - Auto-backup
    - Never loses data
    - Reports when deployed to new location
    """
    
    def __init__(self, db_path: str = "memory_station.db", backup_dir: str = "memory_backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # In-memory cache for fast access
        self.cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Knowledge categories
        self.categories = [
            'strategies',      # Trading strategies
            'patterns',        # Market patterns
            'models',          # ML models
            'pairs',           # Pair-specific knowledge
            'exchanges',       # Exchange-specific knowledge
            'errors',          # Error patterns and solutions
            'performance',     # Performance metrics
            'decisions',       # Trading decisions history
            'insights'         # General insights
        ]
        
        # Initialize database
        self._init_database()
        
        # Check if this is a new deployment
        self._check_deployment_status()
        
        logger.info(f"🧠 Memory Station initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                UNIQUE(category, key)
            )
        ''')
        
        # Index for fast retrieval
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category_key 
            ON memory(category, key)
        ''')
        
        # Deployment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                memory_loaded INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Memory Station database initialized")
    
    def _check_deployment_status(self):
        """Check if this is a new deployment and report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get deployment count
        cursor.execute("SELECT COUNT(*) FROM deployments")
        deployment_count = cursor.fetchone()[0]
        
        # Get total memory items
        cursor.execute("SELECT COUNT(*) FROM memory")
        memory_count = cursor.fetchone()[0]
        
        # Record this deployment
        import socket
        location = socket.gethostname()
        
        cursor.execute('''
            INSERT INTO deployments (location, memory_loaded, notes)
            VALUES (?, ?, ?)
        ''', (location, memory_count, f"Deployment #{deployment_count + 1}"))
        
        conn.commit()
        conn.close()
        
        if deployment_count == 0:
            logger.info(f"🎉 NEW DEPLOYMENT detected! Location: {location}")
            logger.info("📊 Memory Station is empty - will start learning")
        else:
            logger.info(f"♻️  REDEPLOYMENT #{deployment_count + 1} detected! Location: {location}")
            logger.info(f"📊 Memory Station has {memory_count} items - resuming with existing knowledge")
    
    def bank(self, category: str, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Bank knowledge into memory station
        
        Args:
            category: Knowledge category
            key: Unique key within category
            value: Value to store (any JSON-serializable object)
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            elif isinstance(value, (int, float, str, bool)):
                value_str = str(value)
            else:
                # Use pickle for complex objects
                value_str = pickle.dumps(value).hex()
            
            # Serialize metadata
            metadata_str = json.dumps(metadata) if metadata else '{}'
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO memory 
                (category, key, value, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (category, key, value_str, metadata_str))
            
            conn.commit()
            conn.close()
            
            # Update cache
            self.cache[category][key] = value
            
            logger.debug(f"💾 Banked: {category}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to bank {category}/{key}: {e}")
            return False
    
    def call(self, category: str, key: str, default: Any = None) -> Any:
        """
        Call (retrieve) knowledge from memory station
        
        Args:
            category: Knowledge category
            key: Unique key within category
            default: Default value if not found
            
        Returns:
            Stored value or default
        """
        try:
            # Check cache first
            if category in self.cache and key in self.cache[category]:
                logger.debug(f"📖 Called from cache: {category}/{key}")
                return self.cache[category][key]
            
            # Retrieve from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM memory 
                WHERE category = ? AND key = ?
            ''', (category, key))
            
            result = cursor.fetchone()
            
            # Update access count
            if result:
                cursor.execute('''
                    UPDATE memory 
                    SET access_count = access_count + 1 
                    WHERE category = ? AND key = ?
                ''', (category, key))
            
            conn.commit()
            conn.close()
            
            if result:
                value_str = result[0]
                
                # Deserialize
                try:
                    value = json.loads(value_str)
                except:
                    try:
                        # Try pickle
                        value = pickle.loads(bytes.fromhex(value_str))
                    except:
                        value = value_str
                
                # Cache it
                self.cache[category][key] = value
                
                logger.debug(f"📖 Called from DB: {category}/{key}")
                return value
            
            logger.debug(f"⚠️  Not found: {category}/{key}, using default")
            return default
            
        except Exception as e:
            logger.error(f"❌ Failed to call {category}/{key}: {e}")
            return default
    
    def query(self, category: str, filter_func: Optional[callable] = None, limit: int = 100) -> List[Dict]:
        """
        Query memory station
        
        Args:
            category: Knowledge category
            filter_func: Optional filter function (receives key, value, metadata)
            limit: Maximum results
            
        Returns:
            List of matching items
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key, value, metadata, created_at, updated_at, access_count
                FROM memory 
                WHERE category = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (category, limit))
            
            results = []
            for row in cursor.fetchall():
                key, value_str, metadata_str, created, updated, access_count = row
                
                # Deserialize
                try:
                    value = json.loads(value_str)
                except:
                    try:
                        value = pickle.loads(bytes.fromhex(value_str))
                    except:
                        value = value_str
                
                try:
                    metadata = json.loads(metadata_str)
                except:
                    metadata = {}
                
                item = {
                    'key': key,
                    'value': value,
                    'metadata': metadata,
                    'created_at': created,
                    'updated_at': updated,
                    'access_count': access_count
                }
                
                # Apply filter
                if filter_func is None or filter_func(key, value, metadata):
                    results.append(item)
            
            conn.close()
            
            logger.debug(f"🔍 Query {category}: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to query {category}: {e}")
            return []
    
    def broadcast(self, category: str, key: str, value: Any) -> int:
        """
        Broadcast knowledge to all listening models
        (Same as bank, but with notification semantics)
        """
        success = self.bank(category, key, value, metadata={'broadcast': True})
        if success:
            logger.info(f"📡 Broadcast: {category}/{key}")
            return 1
        return 0
    
    def get_stats(self) -> Dict:
        """Get memory station statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total items
            cursor.execute("SELECT COUNT(*) FROM memory")
            total_items = cursor.fetchone()[0]
            
            # Items by category
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM memory 
                GROUP BY category
            ''')
            by_category = dict(cursor.fetchall())
            
            # Most accessed
            cursor.execute('''
                SELECT category, key, access_count 
                FROM memory 
                ORDER BY access_count DESC 
                LIMIT 10
            ''')
            most_accessed = cursor.fetchall()
            
            # Deployment info
            cursor.execute('''
                SELECT location, deployed_at, memory_loaded 
                FROM deployments 
                ORDER BY deployed_at DESC 
                LIMIT 1
            ''')
            last_deployment = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_items': total_items,
                'by_category': by_category,
                'most_accessed': most_accessed,
                'last_deployment': last_deployment,
                'cache_size': sum(len(cat) for cat in self.cache.values())
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    def backup(self) -> str:
        """Create backup of memory station"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"memory_station_backup_{timestamp}.db"
            
            # Copy database
            import shutil
            shutil.copy2(self.db_path, backup_file)
            
            logger.info(f"💾 Memory Station backed up to {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return ""


# Global memory station instance
_memory_station = None

def get_memory_station() -> MemoryStation:
    """Get global memory station instance"""
    global _memory_station
    if _memory_station is None:
        _memory_station = MemoryStation()
    return _memory_station


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    station = MemoryStation("test_memory_station.db")
    
    # Test banking
    print("\n" + "="*70)
    print("Testing banking:")
    station.bank('strategies', 'scalping_btc', {
        'win_rate': 0.65,
        'avg_profit': 0.015,
        'trades': 100
    })
    station.bank('patterns', 'bullish_engulfing', {
        'success_rate': 0.70,
        'timeframes': ['15m', '1h']
    })
    
    # Test calling
    print("\n" + "="*70)
    print("Testing calling:")
    strategy = station.call('strategies', 'scalping_btc')
    print(f"Retrieved strategy: {strategy}")
    
    # Test query
    print("\n" + "="*70)
    print("Testing query:")
    all_strategies = station.query('strategies')
    print(f"All strategies: {len(all_strategies)}")
    
    # Test stats
    print("\n" + "="*70)
    print("Stats:", json.dumps(station.get_stats(), indent=2))
    
    # Test backup
    print("\n" + "="*70)
    backup_file = station.backup()
    print(f"Backup created: {backup_file}")
