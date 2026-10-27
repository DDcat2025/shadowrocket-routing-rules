"""Deterministic domain providers and a separate verified API IP provider."""
from __future__ import annotations
import argparse
import hashlib
import ipaddress
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'}
NON_DOMAIN = {'IP-CIDR', 'IP-CIDR6', 'IP-ASN', 'USER-AGENT', 'URL-REGEX'}
GENERATED: dict[Path, str] = {}


def read_rules(path: Path) -> set[tuple[str, str]]:
    out = set()
    for no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line: continue
        if path.name.endswith('_Domain.list'):
            kind, value = ('DOMAIN-SUFFIX', line[1:]) if line.startswith('.') else ('DOMAIN', line)
        else:
            fields = [x.strip() for x in line.split(',')]
            if fields[0] in NON_DOMAIN: continue
            if fields[0] not in SUPPORTED or len(fields) != 2:
                raise ValueError(f'{path}:{no}: unsupported rule {line}')
            kind, value = fields
        value = value.lower()
        if not value or any(c in value for c in ' ,/*\t\r\n'):
            raise ValueError(f'{path}:{no}: invalid value {value}')
        out.add((kind, value))
    return out


def read_ip_rules(path: Path) -> set[tuple[str, str]]:
    out = set()
    for no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        fields = [value.strip() for value in line.split(',')]
        if len(fields) != 3 or fields[0] not in {'IP-CIDR', 'IP-CIDR6'} or fields[2] != 'no-resolve':
            raise ValueError(f'{path}:{no}: invalid IP rule')
        network = ipaddress.ip_network(fields[1], strict=True)
        if network.version != (4 if fields[0] == 'IP-CIDR' else 6):
            raise ValueError(f'{path}:{no}: IP family does not match rule type')
        out.add((fields[0], str(network)))
    if not out:
        raise ValueError(f'Empty IP provider: {path}')
    return out


def module(name: str) -> set[tuple[str, str]]:
    directory = ROOT / 'data/sources/blackmatrix' / name
    result = read_rules(directory / (name + '.list'))
    companion = directory / (name + '_Domain.list')
    if companion.exists(): result |= read_rules(companion)
    if not result: raise ValueError(f'Empty domain module: {name}')
    return result


def v2fly(name: str) -> set[tuple[str, str]]:
    result = set()
    for raw in (ROOT / 'data/sources/v2fly' / name).read_text().splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line: continue
        token = line.split()[0]
        if ':' in token:
            prefix, token = token.split(':', 1)
            if prefix not in {'full', 'domain'}: raise ValueError(f'Unsupported v2fly {name}: {line}')
            kind = 'DOMAIN' if prefix == 'full' else 'DOMAIN-SUFFIX'
        else: kind = 'DOMAIN-SUFFIX'
        result.add((kind, token.lower()))
    if not result: raise ValueError(f'Empty v2fly {name}')
    return result


def external(repo: str, name: str) -> set[tuple[str, str]]:
    return read_rules(ROOT / 'data/sources/external' / repo / (name + '.list'))


def google_family():
    """Expand every pinned include; reject unknown syntax and audit redundant regex."""
    rules, seen, redundant_regex = set(), set(), []
    allowed_regex_parents = {'google-play': {'googlevideo.com', 'xn--ngstr-lra8j.com'}}

    def visit(name):
        if name in seen:
            return
        seen.add(name)
        for line in (ROOT / 'data/sources/google-v2fly' / name).read_text().splitlines():
            tokens = line.split('#', 1)[0].split()
            if not tokens:
                continue
            token = tokens[0]
            if token.startswith('include:'):
                assert len(tokens) == 1, ('Unsupported filtered include', line)
                visit(token.split(':', 1)[1])
            elif token.startswith('regexp:'):
                # Both current Play regexes are strict subdomains of suffix rules
                # already present in the same Google/YouTube source tree.
                parent = next((p for p in allowed_regex_parents.get(name, set())
                               if token.endswith(p.replace('.', r'\.') + '$')), None)
                assert parent, ('New regex requires review', name, token)
                redundant_regex.append({'source': name, 'regex': token, 'covered_suffix': parent})
            else:
                kind = 'DOMAIN-SUFFIX'
                if ':' in token:
                    prefix, token = token.split(':', 1)
                    assert prefix in {'full', 'domain'}, (name, line)
                    kind = 'DOMAIN' if prefix == 'full' else 'DOMAIN-SUFFIX'
                rules.add((kind, token.lower()))

    visit('google')
    for item in redundant_regex:
        assert ('DOMAIN-SUFFIX', item['covered_suffix']) in rules
    queue('docs/google-source-expansion.json', [json.dumps(
        {'files': sorted(seen), 'redundant_regex': redundant_regex}, ensure_ascii=False, indent=2)])
    return rules


class Scope:
    """Recognize explicit protected names, descendants and existing keyword rules.

    A shared parent such as amazonaws.com is NOT removed just because an Adobe
    exact bucket is protected. Ordered specific rules handle those cases.
    """
    def __init__(self, rules):
        self.suffix = {v for k, v in rules if k == 'DOMAIN-SUFFIX'}
        self.full = {v for k, v in rules if k == 'DOMAIN'}
        self.keyword = {v for k, v in rules if k == 'DOMAIN-KEYWORD'}

    def contains(self, rule):
        kind, value = rule
        if kind == 'DOMAIN-KEYWORD': return value in self.keyword
        if value in self.full: return True
        labels = value.split('.')
        if any('.'.join(labels[i:]) in self.suffix for i in range(len(labels))): return True
        return any(word in value for word in self.keyword)


def queue(path, lines):
    GENERATED[ROOT / path] = '\n'.join(lines) + '\n'


def output(name, rules, companion=True):
    ordered = sorted(rules)
    digest = hashlib.sha256('\n'.join(','.join(r) for r in ordered).encode()).hexdigest()
    header = [f'# NAME: {name}', '# AUTHOR: DDcat2025',
              '# REPO: https://github.com/DDcat2025/shadowrocket-routing-rules',
              '# SOURCE: data/source-lock.json; official manual supplements in data/custom',
              f'# RULES-SHA256: {digest}', f'# TOTAL: {len(ordered)}']
    if name in {'Instagram', 'Facebook', 'Google'}:
        release = json.loads((ROOT / 'data/release.json').read_text())
        header[2:2] = [f'# VERSION: {release["version"]}', f'# UPDATED: {release["date"]}']
        header.insert(-2, '# DEDICATED-SOURCES: data/dedicated-source-lock.json; data/custom/*-dedicated.list')
    if name == 'Grok':
        release = json.loads((ROOT / 'data/grok-release.json').read_text())
        header[2:2] = [f'# VERSION: {release["version"]}', f'# UPDATED: {release["date"]}']
        header.insert(-2, '# OFFICIAL-SUPPLEMENTS: data/custom/grok-dedicated.list; docs/grok.md')
    lines = [','.join(r) + (',no-resolve' if r[0] in {'IP-CIDR', 'IP-CIDR6'} else '') for r in ordered]
    queue(f'rule/Shadowrocket/{name}/{name}.list', header + lines)
    queue(f'rule/Mihomo/{name}/{name}.yaml', header + ['payload:'] + ['  - ' + r for r in lines])
    if companion:
        # DOMAIN-SET cannot express a keyword. Publish the keyword companion separately.
        suffix = {v for k, v in ordered if k == 'DOMAIN-SUFFIX'}
        exact = {v for k, v in ordered if k == 'DOMAIN'} - suffix
        domains = ['.' + v for v in sorted(suffix)] + sorted(exact)
        keywords = ['DOMAIN-KEYWORD,' + v for k, v in ordered if k == 'DOMAIN-KEYWORD']
        queue(f'rule/Shadowrocket/{name}/{name}_Domain.list',
              header[:-1] + [f'# TOTAL: {len(domains)}', '# Requires the _Keyword.list companion for equivalent coverage.'] + domains)
        queue(f'rule/Shadowrocket/{name}/{name}_Keyword.list',
              header[:-1] + [f'# TOTAL: {len(keywords)}'] + keywords)


def build():
    groups = json.loads((ROOT / 'data/groups.json').read_text())
    adobe_repo = 'adobe-shadowrocket-rules'
    adobe = set().union(*(external(adobe_repo, n) for n in ['AdobeProxy', 'AdobeDirect', 'AdobeStockLegacy']))
    # Remove the broad Adobe keyword from generic pools without publishing it as a catch-all Adobe rule.
    adobe_scope = Scope(adobe | {('DOMAIN-KEYWORD', 'adobe')})
    claude_core = module('Claude') | module('Anthropic') | v2fly('anthropic') | read_rules(ROOT / 'data/custom/claude-core.list')
    dependencies = read_rules(ROOT / 'data/custom/claude-dependencies.list')
    claude = claude_core | dependencies
    claude_ip = read_ip_rules(ROOT / 'data/custom/claude-ip.list')
    # Opt-in unified Gemini provider, including explicitly documented shared
    # dependencies. Clients without this provider keep the existing routing.
    gemini = (read_rules(ROOT / 'data/custom/gemini-core.list')
              | read_rules(ROOT / 'data/custom/gemini-shared.list'))
    instagram = read_rules(ROOT / 'data/custom/instagram-dedicated.list')
    facebook = read_rules(ROOT / 'data/custom/facebook-dedicated.list')
    google_modules = ['Google', 'GoogleSearch', 'GoogleDrive', 'GoogleVoice',
                      'GoogleEarth', 'YouTube', 'YouTubeMusic']
    google = google_family() | gemini | set().union(*(module(n) for n in google_modules))
    # Dedicated providers avoid broad keyword false positives. Generic legacy
    # providers remain compatible with clients that have not added these groups.
    google = {r for r in google if r[0] != 'DOMAIN-KEYWORD'}
    x = module('Twitter') | v2fly('twitter') | v2fly('xai')
    # Keep X backward-compatible while offering an opt-in independent Grok group.
    grok = v2fly('xai') | read_rules(ROOT / 'data/custom/grok-dedicated.list')
    openai_owned = {('DOMAIN-SUFFIX', h) for h in ['openai.com','chatgpt.com','chat.com','chatgpt.site','sora.com','oaistatic.com','oaistatsig.com','oaiusercontent.com','openaimerge.com']}
    dedicated_scope = Scope(openai_owned | claude_core | x | grok)
    own_direct = (external('tencent-shadowrocket-rules', 'Tencent')
                  | external('douyin-bytedance-shadowrocket-rules', 'ByteDanceCN')
                  | read_rules(ROOT / 'data/custom/domestic-creative.list'))
    source_direct = module('China') | own_direct
    source_full = module('ChinaMax') | own_direct
    diagnostics = read_rules(ROOT / 'data/custom/network-diagnostics.list')
    diagnostics_scope = Scope(diagnostics)
    excluded = []

    def filter_pool(pool, category):
        result = set()
        for rule in pool:
            reason = 'Adobe' if adobe_scope.contains(rule) else 'OpenAI/Claude/X' if dedicated_scope.contains(rule) else None
            if reason is None and category in {'ChinaDirect', 'ChinaDirectFull'} and diagnostics_scope.contains(rule):
                reason = 'NetworkDiagnostics'
            if reason: excluded.append({'category': category, 'rule': ','.join(rule), 'assigned_to': reason})
            else: result.add(rule)
        return result

    china = filter_pool(source_direct, 'ChinaDirect')
    china_full = filter_pool(source_full, 'ChinaDirectFull')
    other_names = [n for category, names in groups.items() if category != '基础' for n in names if n != 'Adobe']
    source_international = set().union(*(module(n) for n in other_names))
    source_international |= read_rules(ROOT / 'data/custom/international.list')
    source_international |= diagnostics
    international = filter_pool(source_international, 'International')
    # Explicit overseas modules are small enough to place before generic domestic classification.
    priority_names = ['Google','GoogleSearch','GoogleDrive','GoogleVoice','Gemini','BardAI','Bing','Copilot',
        'YouTube','YouTubeMusic','GitHub','GitLab','Telegram','Discord','Facebook','Instagram','Threads',
        'Whatsapp','Reddit','LinkedIn','Pinterest','TikTok','Netflix','Disney','HBO','Hulu','Spotify',
        'Notion','Figma','Dropbox','Slack','Protonmail','Wikipedia','Wikimedia','Twitch','Vimeo']
    priority_pool = set().union(*(module(n) for n in priority_names)) | read_rules(ROOT / 'data/custom/international.list')
    priority_pool |= diagnostics
    priority = filter_pool(priority_pool, 'InternationalPriority')
    names = {'ChinaDirect': china, 'ChinaDirectFull': china_full, 'Claude': claude,
             'Claude_Core': claude_core, 'Claude_Dependencies': dependencies, 'Anthropic': claude,
             'Claude_IP': claude_ip, 'X': x, 'Grok': grok, 'Gemini': gemini,
             'Instagram': instagram, 'Facebook': facebook, 'Google': google,
             'International': international, 'InternationalPriority': priority}
    for name, rules in names.items(): output(name, rules, companion=name != 'Claude_IP')
    # No complete .conf: these are composable rule providers without nodes or credentials.
    counts = {name: {'total': len(rules), **dict(sorted(Counter(k for k, _ in rules).items()))} for name, rules in names.items()}
    queue('docs/counts.json', [json.dumps(counts, ensure_ascii=False, indent=2)])
    queue('docs/规则规模.md', ['# 生成规则规模', '', '| 集合 | 匹配条件 |', '|---|---:|']
          + [f'| {name} | {stat["total"]:,} |' for name, stat in counts.items()]
          + ['', '统计的是匹配条件，不是独立网站数量。可选集合之间有交集，不应直接相加。'])
    audit = {'excluded': sorted(excluded, key=lambda r: (r['category'], r['rule'])),
             'adobe_reference_rules': len(adobe),
             'note': 'Explicit Adobe conditions are removed; shared provider parent domains may remain and require the documented order.'}
    queue('docs/exclusions.json', [json.dumps(audit, ensure_ascii=False, indent=2)])
    return names


def main():
    p = argparse.ArgumentParser(); p.add_argument('--check', action='store_true'); args = p.parse_args()
    names = build(); changed = []
    for path, content in GENERATED.items():
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding='utf-8')
    if args.check and changed: raise SystemExit('Generated files differ: ' + ', '.join(changed))
    print(json.dumps({name: len(rules) for name, rules in names.items()}, ensure_ascii=False))


if __name__ == '__main__': main()
