#!/usr/bin/env python3
"""Check that retained Cutie Collect HTML resolves every shared local art path."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parent
for version in range(57, 61):
    page = root / f'v{version}' / ('index.html' if version == 60 else f'index-v{version}.html')
    raw = page.read_bytes()
    html = raw.decode('utf-8')
    if 'cutie_collect_v54_assets/' in html or 'cutie_collect_v58_assets/' in html:
        raise SystemExit(f'v{version}: old asset directory remains')
    paths = set(re.findall(r'\.\./assets/(?:v54|v58)/[0-9a-f]{64}\.(?:png|webp|svg|jpg)', html))
    expected = 251 if version < 58 else 265
    if len(paths) != expected:
        raise SystemExit(f'v{version}: found {len(paths)} local images, expected {expected}')
    for relative in paths:
        if not (page.parent / relative).is_file():
            raise SystemExit(f'v{version}: missing {relative}')
    manifest = json.loads((page.parent / 'asset-manifest.json').read_text(encoding='utf-8'))
    if manifest['htmlSha256'] != hashlib.sha256(raw).hexdigest():
        raise SystemExit(f'v{version}: manifest HTML hash mismatch')
    print(f'v{version}: {len(paths)} image paths OK; HTML hash OK')

for version in (61, 62, 63, 64, 65):
    page = root / f'v{version}/index.html'
    raw = page.read_bytes()
    html = raw.decode('utf-8')
    paths = set(re.findall(r'\.\./assets/(?:runtime|legacy)/[A-Za-z0-9_@.:-]+\.(?:png|webp)', html))
    manifest = json.loads((page.parent / 'asset-manifest.json').read_text(encoding='utf-8'))
    expected = manifest['runtimeAssets'] + manifest['shellAssets']
    if len(paths) != expected:
        raise SystemExit(f'v{version}: found {len(paths)} shared images, expected {expected}')
    for relative in paths:
        if not (page.parent / relative).is_file():
            raise SystemExit(f'v{version}: missing {relative}')
    if manifest['htmlSha256'] != hashlib.sha256(raw).hexdigest():
        raise SystemExit(f'v{version}: manifest HTML hash mismatch')
    archive = page.parent / manifest['offlineZip']
    if not archive.is_file() or manifest['offlineZipSha256'] != hashlib.sha256(archive.read_bytes()).hexdigest():
        raise SystemExit(f'v{version}: offline ZIP missing or changed')
    print(f'v{version}: {len(paths)} shared image paths OK; HTML and offline ZIP hashes OK')
