import subprocess
import os

# Paths to the scripts
scripts = [
    r"Code\player.py",
    r"Analysis\Improved_FD.py"
]

for script in scripts:
    print(f"\n>>> Running: {script}")
    subprocess.run(["python", script], check=True)