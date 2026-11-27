#!/usr/bin/env python3
"""Atomically apply the reviewed four-line live printer.cfg Z offset edit."""

import hashlib
import os
import shutil
import stat
from pathlib import Path


ROOT = Path('/home/voron/printer_data/config').resolve()
TARGET = ROOT / 'printer.cfg'
STAGED = ROOT / 'printer.cfg.codex-pf2-z-20261127.tmp'
BACKUP = ROOT / 'printer-20261127-pre-pf2-z-offsets.cfg'
OLD_SHA256 = 'a7813e58a7dd711dd9930068e8d7fa61fc2c9aceb6092db09993ea9c05596aa8'
NEW_SHA256 = '3b27bf87626b64f654477d14a51a38e310ce3890d0beef1e53f5c4aae7462273'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if TARGET.resolve() != ROOT / 'printer.cfg' or STAGED.resolve() != ROOT / STAGED.name:
    raise SystemExit('Unexpected config target or staged path')
if BACKUP.exists():
    raise SystemExit('Remote backup already exists; refusing to overwrite it')
if digest(TARGET) != OLD_SHA256:
    raise SystemExit('Live printer.cfg changed since review; refusing to apply')
if digest(STAGED) != NEW_SHA256:
    raise SystemExit('Staged printer.cfg hash differs from reviewed candidate')

STAGED.chmod(stat.S_IMODE(TARGET.stat().st_mode))
shutil.copy2(TARGET, BACKUP)
if digest(BACKUP) != OLD_SHA256:
    raise SystemExit('Remote backup failed verification')
os.replace(STAGED, TARGET)
if digest(TARGET) != NEW_SHA256:
    raise SystemExit('Applied printer.cfg failed verification')
print(f'Applied four Z offset lines; backup={BACKUP}; sha256={NEW_SHA256}')
