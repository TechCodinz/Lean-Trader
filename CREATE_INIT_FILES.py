
import os

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"

def create_init_files():
    print("🚀 Creating __init__.py files...")
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if "_BACKUP" in root or ".git" in root: continue
        
        init_path = os.path.join(root, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write(f"# Package: {os.path.basename(root)}\n")
            count += 1
            
    print(f"✅ Created {count} __init__.py files.")

if __name__ == "__main__":
    create_init_files()
