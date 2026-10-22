"""translate-retro-game scripts dir: $SKILL (the dir holding SKILL.md), else the newest installed plugin copy."""
import glob, os
from pathlib import Path

SCRIPTS = Path(os.environ['SKILL'], 'scripts') if os.environ.get('SKILL') else Path(max(
    glob.glob(os.path.expanduser('~/.claude/plugins/cache/retro-translation/translate-retro-game/*/skills/'
                                 'translate-retro-game/scripts')), key=os.path.getmtime))
