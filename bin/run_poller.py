#!/usr/bin/env python3
import os
import sys

# Ensure local src/ is on sys.path when running from repo root
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from mrlazy_bot.local_poller.main import main  # noqa: E402


if __name__ == "__main__":
    main()


