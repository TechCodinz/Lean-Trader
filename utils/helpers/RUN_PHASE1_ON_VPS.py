#!/usr/bin/env python3
import sys
import os

# Change base directory to VPS /root/bot
os.chdir('/root/bot')

# Import and run Phase 1
exec(open('PHASE1_FUNCTIONAL_INTENT_EXTRACTION.py').read().replace(
    r"c:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\Lean-Trader-continue-from-micro-fix",
    "/root/bot"
))
