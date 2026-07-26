import os
import re

def fix_orchestrator():
    file_path = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'
    print(f"🔧 Patcher: Scanning {file_path} for Telegram fixes...")
    
    with open(file_path, 'r') as f:
        content = f.read()

    # FIX 1: 'telegram' is not defined -> likely 'self.telegram' or 'self.premium_vip_telegram'
    # We look for where it might be used.
    # Pattern: "telegram.send_message" -> "self.telegram.send_message"
    
    new_content = content
    if "telegram.send_message" in content and "self.telegram.send_message" not in content:
        # Be careful not to replace if it's already correct in some local scope, but global error suggests it's not.
        # However, a blind replacment might be risky. 
        # Better approach: check for the specific block causing issues near line 4700.
        pass

    # Let's try to find the error handler and look backwards
    # "except Exception as e:\n            logger.error(f\"[X] VIP send failed: {e}\")"
    
    # We will look for usage of 'telegram' that isn't 'self.telegram'
    # Regex: whitespace + telegram\.
    
    # Actually, let's just create a safe wrapper class or method to inject.
    pass

    # Direct Patching for the known error area
    # Previous log showed: "VIP send failed: name 'telegram' is not defined"
    # This implies code like: telegram.send_message(...)
    # We will replace `telegram.send_message` with `if hasattr(self, 'telegram'): self.telegram.send_message`
    
    # Simple brute force replacement for the likely culprit
    chk = "telegram.send_message"
    fix = "if hasattr(self, 'telegram'): self.telegram.send_message"
    
    # Iterate lines to be safer
    lines = content.splitlines()
    fixed_lines = []
    changes = 0
    for line in lines:
        if chk in line and "self." not in line and "def " not in line:
            # Found a bare usage
            # Replace 'telegram.send_message' with 'self.telegram.send_message' if it looks like a call
            # But the error says 'telegram' is not defined. 
            # So replace 'telegram.' with 'self.telegram.'
            new_line = line.replace("telegram.", "self.telegram.")
            fixed_lines.append(new_line)
            changes += 1
            print(f"   Fixed line: {line.strip()} -> {new_line.strip()}")
        else:
            fixed_lines.append(line)
            
    if changes > 0:
        with open(file_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
        print(f"[OK] Applied {changes} Telegram keyword fixes.")
    else:
        print("  No bare 'telegram.' calls found. Maybe it's named 'bot' or inside a string?")


def fix_execution_engine():
    file_path = 'INTELLIGENT_EXECUTION_ENGINE.py'
    print(f"🔧 Patcher: Scanning {file_path} for Dust Filter...")
    
    with open(file_path, 'r') as f:
        lines = f.lines() if hasattr(f, 'lines') else f.read().splitlines()
        
    # We need to find 'def execute_trade' and inject validation logic right after arguments.
    # def execute_trade(self, symbol, signal, ...):
    
    new_lines = []
    injected = False
    
    for line in lines:
        new_lines.append(line)
        if "def execute_trade" in line and not injected:
            # Inject Dust Logic
            print("   Found execute_trade, injecting filter...")
            indent = "        " # Assumption
            # Try to determine indent from next line? No, let's assume standard 4 or 8.
            # Safe bet: use the same indentation as the def + 4 spaces
            leading_spaces = len(line) - len(line.lstrip())
            indent = " " * (leading_spaces + 4)
            
            check_logic = [
                f"",
                f"{indent}# 🛡️ DUST FILTER INJECTION (Auto-Fix)",
                f"{indent}try:",
                f"{indent}    # Extract simple price/qty for validation",
                f"{indent}    _p = float(entry_price) if 'entry_price' in locals() else 0",
                f"{indent}    _q = float(quantity) if 'quantity' in locals() else 0",
                f"{indent}    if _p * _q < 6.0 and _p * _q > 0:",
                f"{indent}        logger.warning(f'[X] SKIPPING DUST TRADE: Value ${{_p*_q:.2f}} < $6.0 Limit')",
                f"{indent}        return None",
                f"{indent}except: pass",
                f""
            ]
            new_lines.extend(check_logic)
            injected = True
            
    if injected:
        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))
        print("[OK] Injected dust filter into execute_trade.")
    else:
        print("[X] Could not find execute_trade function.")

if __name__ == "__main__":
    try:
        fix_orchestrator()
    except Exception as e:
        print(f"Orchestrator Patch Failed: {e}")
        
    try:
        fix_execution_engine()
    except Exception as e:
        print(f"Execution Patch Failed: {e}")
