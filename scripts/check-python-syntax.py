#!/usr/bin/env python3
"""Parse tracked Python sources without importing them or writing bytecode."""
import ast
from pathlib import Path
import subprocess

paths = subprocess.check_output(["git", "ls-files", "-z", "*.py"]).decode("utf-8").split("\0")
for name in paths:
    if name:
        ast.parse(Path(name).read_text(encoding="utf-8-sig"), filename=name)
print("Tracked Python syntax: PASS")
