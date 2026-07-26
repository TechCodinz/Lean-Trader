
import os
import sys
import subprocess
import time
import platform
import logging

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [START_BOT] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot_launch.log")
    ]
)
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_environment():
    """Verify python version and dependencies"""
    logger.info(f">> LAUNCHING LEAN TRADER BOT (Unified Golden Version)")
    logger.info(f"   Root: {ROOT_DIR}")
    logger.info(f"   Python: {platform.python_version()}")
    
    # Check for .env
    if not os.path.exists(os.path.join(ROOT_DIR, ".env")):
        logger.warning(" .env file missing! Creating/checking for .env...")
        # (Optional: Logic to create .env if needed, but assuming it exists from stitch)
    
    # Verify critical files
    critical_files = [
        "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "INTELLIGENT_EXECUTION_ENGINE.py",
        "COMPLETE_PROFIT_SYSTEM.py",
        "EVOLUTION_ENGINE.py"
    ]
    
    missing = []
    for f in critical_files:
        if not os.path.exists(os.path.join(ROOT_DIR, f)):
            missing.append(f)
            
    if missing:
        logger.error(f"[X] CRITICAL ERROR: Missing files: {missing}")
        sys.exit(1)
        
    logger.info("[OK] Environment check passed.")

def run_sanitization():
    """Run the sanitization check before launch"""
    logger.info("🛡️ Running pre-flight sanitization check...")
    try:
        if os.path.exists(os.path.join(ROOT_DIR, "SANITIZE_AND_VERIFY.py")):
            cmd = [sys.executable, "SANITIZE_AND_VERIFY.py"]
            subprocess.check_call(cmd)
            logger.info("[OK] Pre-flight check complete.")
        else:
            logger.warning(" Sanitization script not found, skipping.")
    except Exception as e:
        logger.error(f"[X] Sanitization check failed: {e}")
        # We might want to abort or continue based on user preference
        # For now, we continue but warn heavily
        time.sleep(2)

def start_bot():
    """Launch the main orchestrator"""
    main_script = "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    cmd = [sys.executable, main_script]
    
    logger.info(f"🔥 STARTING ENGINE: {main_script}")
    logger.info("="*50)
    
    try:
        # Run the bot
        process = subprocess.Popen(
            cmd,
            cwd=ROOT_DIR,
            env=os.environ.copy()  # Pass current env vars
        )
        
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user.")
    except Exception as e:
        logger.error(f"[X] Bot crashed: {e}")
    finally:
        logger.info("Bot process ended.")

if __name__ == "__main__":
    check_environment()
    run_sanitization()
    
    # Optional: Loop restart logic could go here
    start_bot()
