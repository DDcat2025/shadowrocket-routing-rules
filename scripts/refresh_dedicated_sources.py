"""Pin the full Google include tree; stage all downloads before replacing it."""
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
from refresh_sources import get, api

ROOT = Path(__file__).resolve().parents[1]


def main():
    repo = 'v2fly/domain-list-community'
    commit = api(repo + '/commits/master')['sha']
    fetched = {}

    def fetch(name):
        if name in fetched:
            return
        assert name and all(c.isalnum() or c == '-' for c in name), name
        url = f'https://raw.githubusercontent.com/{repo}/{commit}/data/{name}'
        raw = get(url)
        fetched[name] = (raw, url)
        for line in raw.decode().splitlines():
            tokens = line.split('#', 1)[0].split()
            if tokens and tokens[0].startswith('include:'):
                assert len(tokens) == 1, ('Filtered include requires explicit handling', name, line)
                fetch(tokens[0].split(':', 1)[1])

    fetch('google')
    with tempfile.TemporaryDirectory(prefix='.dedicated-', dir=ROOT) as folder:
        stage = Path(folder)
        for name, (raw, _) in fetched.items():
            (stage / name).write_bytes(raw)
        dest = ROOT / 'data/sources/google-v2fly'
        previous = stage / 'previous'
        if dest.exists():
            dest.rename(previous)
        try:
            dest.mkdir()
            for name in fetched:
                shutil.move(str(stage / name), str(dest / name))
        except Exception:
            shutil.rmtree(dest)
            if previous.exists():
                previous.rename(dest)
            raise
    lock = {'repository': repo, 'commit': commit, 'root': 'google',
            'files': [{'path': 'google-v2fly/' + name, 'url': url,
                       'sha256': hashlib.sha256(raw).hexdigest()}
                      for name, (raw, url) in sorted(fetched.items())]}
    (ROOT / 'data/dedicated-source-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
    print(f'Pinned Google include tree: {len(fetched)} files at {commit[:12]}')


if __name__ == '__main__':
    main()
