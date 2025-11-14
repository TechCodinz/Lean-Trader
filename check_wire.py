# Check how wire function is defined and called

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Find wire_execution_to_testnet
import re
matches = re.findall(r'def wire_execution_to_testnet\(self.*?\):', content)
if matches:
    print("✅ Wire function found:")
    for m in matches:
        print(f"   {m}")
else:
    print("❌ Wire function NOT found in EXECUTION_ORCHESTRATOR.py")

# Check what it sets
if 'self.testnet_exchange =' in content:
    print("✅ Sets self.testnet_exchange")
elif 'self.active_exchange =' in content:
    print("✅ Sets self.active_exchange")
else:
    print("❌ Doesn't set exchange properly!")

# Check what it expects
if 'def wire_execution_to_testnet(self, testnet_exchange)' in content:
    print("✅ Expects testnet_exchange parameter")
