#!/usr/bin/env python3
"""Compatibility wrapper for local source-tree usage."""
from pathlib import Path
import sys

_src = Path(__file__).resolve().parent / "src"
if _src.exists():
    sys.path.insert(0, str(_src))

from github_actions_deprecation_preflight.cli import *
from github_actions_deprecation_preflight.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
