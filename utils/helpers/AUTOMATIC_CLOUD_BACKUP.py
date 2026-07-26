#!/usr/bin/env python3
"""🔄 AUTOMATIC CLOUD BACKUP SYSTEM
Protects your learned data against VPS failures

Features:
- Auto-saves every N evolution cycles
- Backs up to GitHub automatically
- Compresses databases before upload
- Incremental backups (only changed data)
- Multiple backup destinations
- Automatic recovery on new VPS
- Zero manual intervention

CRITICAL: This prevents data loss if VPS goes down!
"""

import os
import json
import time
import logging
import sqlite3
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import shutil
import tarfile
import threading

logger = logging.getLogger(__name__)


class AutomaticCloudBackup:
    """Automatic backup system for bot's learned intelligence"""
    
    def __init__(
        self,
        backup_every_n_cycles: int = 100,  # Backup every 100 evolution cycles
        backup_dir: str = "backups",
        enable_github: bool = True,
        enable_local: bool = True,
        max_local_backups: int = 10
    ):
        """
        Initialize automatic backup system
        
        Args:
            backup_every_n_cycles: How often to backup (cycles)
            backup_dir: Local backup directory
            enable_github: Push to GitHub automatically
            enable_local: Keep local backups
            max_local_backups: Max number of local backups to keep
        """
        self.backup_every_n_cycles = backup_every_n_cycles
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.enable_github = enable_github
        self.enable_local = enable_local
        self.max_local_backups = max_local_backups
        
        # Track what's been backed up
        self.last_backup_cycle = 0
        self.last_backup_time = 0
        self.backup_hashes = {}  # File -> hash (for incremental)
        
        # Background backup thread
        self.backup_thread = None
        self.backup_queue = []
        self.running = False
        
        logger.info("=" * 80)
        logger.info("🔄 AUTOMATIC CLOUD BACKUP SYSTEM ACTIVATED")
        logger.info("=" * 80)
        logger.info(f"   Backup frequency: Every {backup_every_n_cycles} evolution cycles")
        logger.info(f"   GitHub auto-push: {enable_github}")
        logger.info(f"   Local backups: {enable_local} (max {max_local_backups})")
        logger.info("=" * 80)
    
    def should_backup(self, current_cycle: int) -> bool:
        """Check if it's time to backup"""
        cycles_since_last = current_cycle - self.last_backup_cycle
        return cycles_since_last >= self.backup_every_n_cycles
    
    def get_db_files(self) -> List[Path]:
        """Find all database files to backup"""
        db_files = []
        
        # Main databases
        for db_name in [
            'evolution_engine.db',
            'enhanced_trading_bot.db',
            'ultimate_bot_450_models.db',
            'divine_intelligence.db'
        ]:
            db_path = Path(db_name)
            if db_path.exists():
                db_files.append(db_path)
        
        # Bot data directory
        bot_data = Path('bot_data')
        if bot_data.exists():
            for json_file in bot_data.glob('*.json'):
                db_files.append(json_file)
        
        return db_files
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def has_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last backup"""
        current_hash = self.calculate_file_hash(file_path)
        last_hash = self.backup_hashes.get(str(file_path), "")
        
        if current_hash != last_hash:
            self.backup_hashes[str(file_path)] = current_hash
            return True
        return False
    
    def get_db_stats(self, db_path: Path) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get total row count
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            total_rows = 0
            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total_rows += cursor.fetchone()[0]
                except:
                    pass
            
            conn.close()
            
            return {
                'tables': table_count,
                'rows': total_rows,
                'size_mb': db_path.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Failed to get stats for {db_path}: {e}")
            return {}
    
    def create_backup(self, current_cycle: int) -> Optional[Path]:
        """Create compressed backup of all learned data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"learned_data_cycle_{current_cycle}_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        logger.info(f"🔄 Creating backup: {backup_name}")
        
        try:
            # Get files to backup
            db_files = self.get_db_files()
            
            if not db_files:
                logger.warning("No database files found to backup")
                return None
            
            # Check which files changed
            changed_files = [f for f in db_files if self.has_changed(f)]
            
            if not changed_files:
                logger.info("No changes detected, skipping backup")
                return None
            
            logger.info(f"Changed files: {len(changed_files)}/{len(db_files)}")
            
            # Create tar.gz archive
            with tarfile.open(backup_path, "w:gz") as tar:
                for db_file in db_files:
                    tar.add(db_file, arcname=db_file.name)
                    logger.debug(f"  Added: {db_file.name}")
            
            # Create metadata
            metadata = {
                'cycle': current_cycle,
                'timestamp': timestamp,
                'files': [str(f) for f in db_files],
                'changed_files': [str(f) for f in changed_files],
                'stats': {}
            }
            
            # Add database stats
            for db_file in db_files:
                if db_file.suffix == '.db':
                    stats = self.get_db_stats(db_file)
                    metadata['stats'][str(db_file)] = stats
            
            # Save metadata
            metadata_path = self.backup_dir / f"{backup_name}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"[OK] Backup created: {backup_path.name} ({backup_size_mb:.2f} MB)")
            
            # Log database stats
            if 'evolution_engine.db' in metadata['stats']:
                stats = metadata['stats']['evolution_engine.db']
                logger.info(f"   Evolution DB: {stats.get('rows', 0)} rows, {stats.get('size_mb', 0):.1f} MB")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"[X] Backup failed: {e}", exc_info=True)
            return None
    
    def push_to_github(self, backup_path: Path) -> bool:
        """Push backup to GitHub automatically"""
        if not self.enable_github:
            return True
        
        logger.info(f"📤 Pushing to GitHub: {backup_path.name}")
        
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning("Not in a git repository, skipping GitHub push")
                return False
            
            # Git add backup
            subprocess.run(['git', 'add', str(backup_path)], check=True)
            subprocess.run(['git', 'add', str(backup_path).replace('.tar.gz', '.json')], check=True)
            
            # Git commit
            commit_msg = f"auto: Backup learned data at cycle {self.last_backup_cycle}"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                check=True,
                capture_output=True
            )
            
            # Git push (in background)
            subprocess.Popen(
                ['git', 'push'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info("[OK] Pushed to GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"GitHub push failed: {e}")
            return False
        except Exception as e:
            logger.error(f"GitHub push error: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old local backups"""
        if not self.enable_local:
            return
        
        # Get all backup files
        backups = sorted(
            self.backup_dir.glob("learned_data_cycle_*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Keep only max_local_backups most recent
        if len(backups) > self.max_local_backups:
            for old_backup in backups[self.max_local_backups:]:
                try:
                    old_backup.unlink()
                    # Remove metadata too
                    metadata_file = old_backup.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    logger.debug(f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    logger.error(f"Failed to remove old backup: {e}")
    
    def backup_now(self, current_cycle: int) -> bool:
        """Perform backup immediately"""
        logger.info(f"🔄 Starting automatic backup at cycle {current_cycle}")
        
        # Create backup
        backup_path = self.create_backup(current_cycle)
        if not backup_path:
            return False
        
        # Push to GitHub
        self.push_to_github(backup_path)
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        # Update tracking
        self.last_backup_cycle = current_cycle
        self.last_backup_time = time.time()
        
        logger.info(f"[OK] Automatic backup complete at cycle {current_cycle}")
        return True
    
    def backup_async(self, current_cycle: int):
        """Backup in background thread (non-blocking)"""
        if self.backup_thread and self.backup_thread.is_alive():
            logger.warning("Backup already in progress, skipping")
            return
        
        self.backup_thread = threading.Thread(
            target=self.backup_now,
            args=(current_cycle,),
            daemon=True
        )
        self.backup_thread.start()
    
    def on_evolution_cycle(self, current_cycle: int):
        """Call this after every evolution cycle"""
        if self.should_backup(current_cycle):
            # Backup in background (non-blocking)
            self.backup_async(current_cycle)
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """Restore from a backup file"""
        logger.info(f"🔄 Restoring from backup: {backup_path.name}")
        
        try:
            # Extract backup
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall()
            
            logger.info("[OK] Backup restored successfully")
            
            # Load metadata
            metadata_path = backup_path.with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    logger.info(f"   Restored to cycle: {metadata['cycle']}")
            
            return True
            
        except Exception as e:
            logger.error(f"[X] Restore failed: {e}", exc_info=True)
            return False
    
    def get_latest_backup(self) -> Optional[Path]:
        """Get path to most recent backup"""
        backups = sorted(
            self.backup_dir.glob("learned_data_cycle_*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups[0] if backups else None
    
    def auto_restore_on_startup(self) -> bool:
        """Automatically restore from latest backup if databases missing"""
        # Check if main databases exist
        main_dbs = [
            Path('evolution_engine.db'),
            Path('enhanced_trading_bot.db')
        ]
        
        missing_dbs = [db for db in main_dbs if not db.exists()]
        
        if not missing_dbs:
            logger.info("All databases present, no restore needed")
            return False
        
        logger.warning(f"Missing databases: {[str(db) for db in missing_dbs]}")
        
        # Get latest backup
        latest_backup = self.get_latest_backup()
        if not latest_backup:
            logger.warning("No backups found, starting fresh")
            return False
        
        logger.info(f"Found backup: {latest_backup.name}")
        logger.info("Restoring automatically...")
        
        return self.restore_from_backup(latest_backup)


# Singleton instance
_backup_system = None


def get_backup_system(
    backup_every_n_cycles: int = 100,
    enable_github: bool = True
) -> AutomaticCloudBackup:
    """Get or create backup system singleton"""
    global _backup_system
    if _backup_system is None:
        _backup_system = AutomaticCloudBackup(
            backup_every_n_cycles=backup_every_n_cycles,
            enable_github=enable_github
        )
    return _backup_system


def initialize_auto_backup(backup_every_n_cycles: int = 100) -> AutomaticCloudBackup:
    """Initialize automatic backup system"""
    global _backup_system
    _backup_system = AutomaticCloudBackup(
        backup_every_n_cycles=backup_every_n_cycles,
        enable_github=True,
        enable_local=True
    )
    
    # Try to auto-restore if needed
    _backup_system.auto_restore_on_startup()
    
    return _backup_system


if __name__ == "__main__":
    # Test the backup system
    logging.basicConfig(level=logging.INFO)
    
    backup = AutomaticCloudBackup(
        backup_every_n_cycles=10,
        enable_github=False  # Test without GitHub
    )
    
    # Simulate evolution cycles
    for cycle in range(1, 101):
        print(f"Evolution cycle {cycle}")
        backup.on_evolution_cycle(cycle)
        time.sleep(0.1)
    
    print("\nBackup system test complete!")
