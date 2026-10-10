import os
import re

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    new_content = re.sub(r'ResPilot', 'ResPilot', content)
    new_content = re.sub(r'respilot', 'respilot', new_content)
    new_content = re.sub(r'RESPILOT', 'RESPILOT', new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

if __name__ == "__main__":
    for root, dirs, files in os.walk('.'):
        if any(skip in root for skip in ['.git', 'venv', '__pycache__', '.venv', 'env', '.pytest_cache']):
            continue
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.env')):
                replace_in_file(os.path.join(root, file))
