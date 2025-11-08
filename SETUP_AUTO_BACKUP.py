#!/usr/bin/env python3
"""🔧 SETUP AUTO-BACKUP SYSTEM
Configures automatic cloud backup for your bot's learned intelligence

Run this once to setup:
1. GitHub auto-push (every 100 cycles)
2. Local backups (keep last 10)
3. Auto-restore on startup
4. Protection against VPS failures
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_git_credentials():
    """Setup Git credentials for automatic pushing"""
    print("=" * 80)
    print("🔧 SETTING UP GIT CREDENTIALS FOR AUTO-PUSH")
    print("=" * 80)
    print()
    
    # Check if git is installed
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed. Please install git first:")
        print("   Ubuntu/Debian: sudo apt install git")
        print("   CentOS/RHEL: sudo yum install git")
        return False
    
    # Check if we're in a git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, check=True)
        print("✅ Git repository detected")
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository!")
        print("   Initialize git first: git init && git remote add origin <your-repo-url>")
        return False
    
    # Check git config
    try:
        result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        email = result.stdout.strip()
        
        if not email:
            print()
            print("⚠️  Git user.email not set")
            email = input("Enter your git email: ")
            subprocess.run(['git', 'config', 'user.email', email], check=True)
            print(f"✅ Set git email: {email}")
        else:
            print(f"✅ Git email: {email}")
        
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        name = result.stdout.strip()
        
        if not name:
            print()
            print("⚠️  Git user.name not set")
            name = input("Enter your git name: ")
            subprocess.run(['git', 'config', 'user.name', name], check=True)
            print(f"✅ Set git name: {name}")
        else:
            print(f"✅ Git name: {name}")
    
    except Exception as e:
        print(f"❌ Git config error: {e}")
        return False
    
    print()
    print("=" * 80)
    print("✅ GIT CREDENTIALS CONFIGURED")
    print("=" * 80)
    return True


def setup_gitignore():
    """Setup .gitignore to allow backup files"""
    print()
    print("🔧 Configuring .gitignore...")
    
    gitignore = Path('.gitignore')
    
    # Read existing
    existing_lines = []
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            existing_lines = f.read().splitlines()
    
    # Add backup directory to allowed files
    backup_rules = [
        '',
        '# Auto-backup files (ALLOWED)',
        '!backups/',
        '!backups/*.tar.gz',
        '!backups/*.json',
    ]
    
    # Check if rules already exist
    needs_update = any(rule not in existing_lines for rule in backup_rules if rule)
    
    if needs_update:
        with open(gitignore, 'a') as f:
            f.write('\n'.join(backup_rules) + '\n')
        print("✅ .gitignore updated to allow backup files")
    else:
        print("✅ .gitignore already configured")


def create_backup_directory():
    """Create backups directory"""
    print("🔧 Creating backup directory...")
    
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create README
    readme = backup_dir / 'README.md'
    if not readme.exists():
        with open(readme, 'w') as f:
            f.write("""# Automatic Backups

This directory contains automatic backups of the bot's learned intelligence.

## Files:
- `learned_data_cycle_N_TIMESTAMP.tar.gz` - Compressed backup (all databases)
- `learned_data_cycle_N_TIMESTAMP.json` - Backup metadata (stats, cycle count)

## Frequency:
- Auto-backup every 100 evolution cycles
- Keeps last 10 local backups
- Automatically pushes to GitHub

## Recovery:
If databases are lost, bot will auto-restore from latest backup on startup.

Manual restore:
```bash
cd backups
tar -xzf learned_data_cycle_N_TIMESTAMP.tar.gz
mv *.db ..
```

## Protection:
These backups protect against:
- VPS failures
- Accidental deletions
- Data corruption
- Migration to new VPS

Your learned intelligence is SAFE! 🛡️
""")
        print("✅ Created backups directory with README")
    else:
        print("✅ Backup directory exists")


def test_backup_system():
    """Test the backup system"""
    print()
    print("=" * 80)
    print("🧪 TESTING AUTO-BACKUP SYSTEM")
    print("=" * 80)
    print()
    
    try:
        from AUTOMATIC_CLOUD_BACKUP import AutomaticCloudBackup
        
        # Create test backup system (without GitHub push for testing)
        backup = AutomaticCloudBackup(
            backup_every_n_cycles=10,
            enable_github=False,
            enable_local=True
        )
        
        print("✅ Backup system imports successfully")
        
        # Check if databases exist
        db_files = backup.get_db_files()
        if db_files:
            print(f"✅ Found {len(db_files)} database files to backup:")
            for db_file in db_files:
                size_mb = db_file.stat().st_size / (1024 * 1024)
                print(f"   - {db_file.name} ({size_mb:.1f} MB)")
        else:
            print("⚠️  No database files found yet (bot hasn't run)")
        
        print()
        print("✅ Auto-backup system is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Backup system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print()
    print("=" * 80)
    print("🔄 AUTOMATIC CLOUD BACKUP SETUP")
    print("=" * 80)
    print()
    print("This will configure automatic backups of your bot's learned intelligence.")
    print("Backups will be created every 100 evolution cycles and pushed to GitHub.")
    print()
    print("This protects against:")
    print("  • VPS failures")
    print("  • Accidental deletions")
    print("  • Data corruption")
    print("  • Migration to new VPS")
    print()
    
    # Step 1: Setup Git
    if not setup_git_credentials():
        print()
        print("❌ Git setup failed. Please fix the issues above and try again.")
        return 1
    
    # Step 2: Setup .gitignore
    setup_gitignore()
    
    # Step 3: Create backup directory
    create_backup_directory()
    
    # Step 4: Test system
    if not test_backup_system():
        print()
        print("❌ Backup system test failed. Check errors above.")
        return 1
    
    print()
    print("=" * 80)
    print("✅ AUTO-BACKUP SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start your bot normally")
    print("2. Every 100 evolution cycles, it will auto-backup")
    print("3. Backups are saved to backups/ directory")
    print("4. Backups are pushed to GitHub automatically")
    print("5. On new VPS, bot will auto-restore from backups")
    print()
    print("Your learned data is now protected! 🛡️")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
