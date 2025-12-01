import subprocess
import os

# Paths to the scripts
scripts = [
    r"Code\player.py",
    r"Models\Python_files\Model_2.py",
    r"Website\app.py"
]

for script in scripts:
    print(f"\n>>> Running: {script}")
    subprocess.run(["python", script], check=True)