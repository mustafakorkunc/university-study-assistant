import os
for root, dirs, files in os.walk("."):
    if ".git" in root or "venv" in root or ".pytest_cache" in root or "__pycache__" in root: continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "modules.adaptive_learning" in content:
                content = content.replace("modules.adaptive_learning", "modules.adaptive_learning")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed {path}")

