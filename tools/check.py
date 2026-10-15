"""One-command check (pre-commit runs this): pytest over tests/ plus the text lint when script exists.
python -X utf8 tools/check.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', '-x', str(ROOT / 'tests')], cwd=ROOT)
if r.returncode:
    sys.exit(r.returncode)
lint = ROOT / 'tools' / 'lint.py'
if lint.exists():
    r = subprocess.run([sys.executable, '-X', 'utf8', str(lint)], cwd=ROOT)
    sys.exit(r.returncode)
