#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
steps=[
 [sys.executable,'scripts/make_ascii_portrait_source.py','--source','assets/profile.jpg','--out','assets/ascii-portrait.svg'],
 [sys.executable,'scripts/make_ascii_svg.py'],
 [sys.executable,'scripts/make_wordmark_svg.py'],
 [sys.executable,'scripts/make_tech_stack_svg.py'],
 [sys.executable,'scripts/make_language_stats_svg.py'],
 [sys.executable,'scripts/render_contributions.py'],
]
for cmd in steps: subprocess.run(cmd,cwd=ROOT,check=True)
print('Profile assets generated successfully.')
