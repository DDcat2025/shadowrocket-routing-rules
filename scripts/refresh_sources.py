"""Refresh public rule snapshots transactionally; do not change live client settings."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import urllib.request
from build_rules import ROOT, read_rules


def get(url):
    headers = {'User-Agent': 'DDcat2025-routing-rules'}
    token = os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = 'Bearer ' + token
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as response:
                data = response.read()
            if not data: raise ValueError('Empty response: ' + url)
            return data
        except Exception as error:
            last = error
            if attempt < 2: time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f'Failed to fetch {url}: {last}')


def api(path): return json.loads(get('https://api.github.com/repos/' + path))


def main():
    groups = json.loads((ROOT / 'data/groups.json').read_text())
    services = {n for names in groups.values() for n in names}
    black_repo = 'blackmatrix7/ios_rule_script'
    black = api(black_repo + '/commits/master')['sha']
    directories = api(black_repo + '/contents/rule?ref=' + black)
    tree_sha = next(d['sha'] for d in directories if d['name'] == 'Shadowrocket')
    tree = api(black_repo + '/git/trees/' + tree_sha + '?recursive=1')
    if tree.get('truncated'): raise ValueError('Truncated Shadowrocket source index')
    indexed = {f['path']: f for f in tree['tree'] if f['type'] == 'blob'}
    jobs = []
    for name in sorted(services):
        primary = f'{name}/{name}.list'
        if primary not in indexed: raise ValueError('Missing module: ' + primary)
        for rel in [primary, f'{name}/{name}_Domain.list']:
            if rel in indexed:
                jobs.append(('blackmatrix/' + rel,
                    f'https://raw.githubusercontent.com/{black_repo}/{black}/rule/Shadowrocket/{rel}', indexed[rel]['sha']))
    v_repo = 'v2fly/domain-list-community'; v_commit = api(v_repo + '/commits/master')['sha']
    for name in ['anthropic', 'twitter', 'xai']:
        jobs.append(('v2fly/' + name, f'https://raw.githubusercontent.com/{v_repo}/{v_commit}/data/{name}', None))
    external = json.loads((ROOT / 'data/external-files.json').read_text())
    commits = {}
    for item in external.values():
        repo = item['repo']
        if repo not in commits: commits[repo] = api(repo + '/commits/main')['sha']
    for relative, item in sorted(external.items()):
        repo = item['repo']; commit = commits[repo]
        jobs.append(('external/' + relative, f'https://raw.githubusercontent.com/{repo}/{commit}/{item["path"]}', None))
    lock = {'blackmatrix_commit': black, 'v2fly_commit': v_commit, 'external_commits': commits, 'files': []}
    with tempfile.TemporaryDirectory(prefix='.refresh-', dir=ROOT) as temp:
        staging = Path(temp)
        def fetch(job):
            rel, url, blob_sha = job
            data = get(url)
            if blob_sha:
                actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                if actual != blob_sha: raise ValueError('Blob mismatch: ' + rel)
            target = staging / rel; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
            if target.suffix == '.list': read_rules(target)
            else:
                # v2fly includes/regex additions need explicit conversion, never silent omission.
                for raw in data.decode('utf-8').splitlines():
                    token = raw.split('#', 1)[0].strip().split()
                    if token and ':' in token[0] and not token[0].startswith(('full:', 'domain:')):
                        raise ValueError('Unsupported v2fly token: ' + token[0])
            return {'path': rel, 'url': url, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            for result in pool.map(fetch, jobs): lock['files'].append(result)
        if len(lock['files']) != len(jobs): raise ValueError('Incomplete fetch')
        # All network and parser checks finish before replacing the snapshot directory.
        destination = ROOT / 'data/sources'
        backup = staging / 'previous'
        destination.rename(backup)
        destination.mkdir()
        try:
            for category in ['blackmatrix', 'v2fly', 'external']:
                shutil.move(str(staging / category), str(destination / category))
            (ROOT / 'data/source-lock.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n')
        except Exception:
            shutil.rmtree(destination); backup.rename(destination); raise
    print(f'Refreshed {len(jobs)} files at blackmatrix {black[:12]}, v2fly {v_commit[:12]}')


if __name__ == '__main__': main()
