#!/usr/bin/env python3
"""Upload and verify named assets on the synchromora draft release.

Authentication is read only from $GITHUB_TOKEN or --token-file, never written
into the repository. Existing named assets are not deleted or replaced. A failed
or changed upload must receive a new revision name.
"""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys

import requests

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'edits/release.json').read_text())
BASE = 'https://api.github.com/repos/' + CONFIG['repository']


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def client(token_file):
    token = os.environ.get('GITHUB_TOKEN')
    if not token and token_file:
        token = Path(token_file).read_text().strip()
    if not token:
        raise SystemExit('Set GITHUB_TOKEN or pass a private --token-file outside the repo')
    s = requests.Session()
    s.headers.update({'Authorization': 'Bearer ' + token,
                      'Accept': 'application/vnd.github+json',
                      'X-GitHub-Api-Version': '2022-11-28',
                      'User-Agent': 'synchromora-clips'})
    return s


def get_release(s):
    r = s.get(f"{BASE}/releases/{CONFIG['release_id']}", timeout=45)
    r.raise_for_status(); info = r.json()
    if info['tag_name'] != CONFIG['tag']:
        raise RuntimeError('Release id/tag mismatch; refusing to modify a different release')
    return info


def upload(s, path: Path, name: str):
    if not path.is_file():
        raise FileNotFoundError(path)
    info = get_release(s)
    digest = sha256_file(path)
    existing = next((a for a in info['assets'] if a['name'] == name), None)
    if existing:
        remote_digest = existing.get('digest')
        if existing['size'] == path.stat().st_size and remote_digest == 'sha256:' + digest:
            print('ALREADY UPLOADED', name, digest, flush=True)
            return existing
        raise RuntimeError(f'Asset {name!r} exists with a different or unverifiable hash. Use a new revision name; no overwrite.')
    url = info['upload_url'].split('{')[0]
    typ = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    print('UPLOADING', name, path.stat().st_size, 'bytes', flush=True)
    with path.open('rb') as f:
        r = s.post(url, params={'name': name}, headers={'Content-Type': typ}, data=f, timeout=(30, 1200))
    if r.status_code not in (200, 201):
        raise RuntimeError(f'Upload {name}: HTTP {r.status_code}: {r.text[:300]}')
    asset = r.json()
    if asset.get('state') != 'uploaded' or asset.get('size') != path.stat().st_size:
        raise RuntimeError(f'Upload {name} did not finish with expected size')
    if asset.get('digest') and asset['digest'] != 'sha256:' + digest:
        raise RuntimeError(f'Upload {name} has a different server digest')
    print('UPLOADED', name, 'id', asset['id'], 'sha256', digest, flush=True)
    return asset


def verify(s, name: str, expected: str):
    info = get_release(s)
    a = next((x for x in info['assets'] if x['name'] == name), None)
    if not a:
        raise RuntimeError('No asset named ' + name)
    # The binary media-type endpoint is also available for unpublished drafts.
    r = s.get(a['url'], headers={'Accept': 'application/octet-stream'}, stream=True, timeout=(30, 600))
    r.raise_for_status()
    if 'json' in r.headers.get('Content-Type', ''):
        raise RuntimeError('GitHub returned metadata instead of the binary')
    h = hashlib.sha256(); n = 0
    for chunk in r.iter_content(1024 * 1024):
        if chunk:
            h.update(chunk); n += len(chunk)
    got = h.hexdigest()
    if got != expected or n != a['size']:
        raise RuntimeError(f'Download verification failed for {name}: {n} bytes sha256 {got}')
    print('VERIFIED', name, n, got, flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--token-file', help='private local token file; never committed')
    sub = p.add_subparsers(dest='command', required=True)
    up = sub.add_parser('upload'); up.add_argument('path', type=Path); up.add_argument('--name')
    ls = sub.add_parser('list')
    v = sub.add_parser('verify'); v.add_argument('name'); v.add_argument('sha256')
    pub = sub.add_parser('publish'); pub.add_argument('--body-file', type=Path, required=True)
    pub.add_argument('--name', required=True); pub.add_argument('--partial', action='store_true')
    args = p.parse_args(); s = client(args.token_file)
    if args.command == 'upload':
        upload(s, args.path, args.name or args.path.name)
    elif args.command == 'list':
        x = get_release(s)
        print('release', x['tag_name'], 'draft', x['draft'], 'prerelease', x['prerelease'])
        for a in x['assets']:
            print(a['name'], a['size'], a.get('digest'))
    elif args.command == 'verify':
        verify(s, args.name, args.sha256)
    elif args.command == 'publish':
        x = get_release(s)
        if not x['draft']:
            raise RuntimeError('Release is already published; do not silently change a published release')
        body = args.body_file.read_text(encoding='utf-8')
        r = s.patch(f"{BASE}/releases/{CONFIG['release_id']}",
                    json={'name': args.name, 'body': body, 'draft': False, 'prerelease': args.partial}, timeout=60)
        r.raise_for_status(); out = r.json()
        print('PUBLISHED', out['html_url'], 'partial', out['prerelease'])

if __name__ == '__main__':
    main()
