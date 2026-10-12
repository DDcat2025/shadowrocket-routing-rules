"""Behavior checks for cross-repository priority, domain precision and exports."""
from __future__ import annotations
from pathlib import Path
import json
from build_rules import ROOT, Scope, external, read_rules, module


def provider(name): return read_rules(ROOT / f'rule/Shadowrocket/{name}/{name}.list')
def match(host, rule):
    kind, value = rule
    if kind == 'DOMAIN': return host == value
    if kind == 'DOMAIN-SUFFIX': return host == value or host.endswith('.' + value)
    if kind == 'DOMAIN-KEYWORD': return value in host
    raise AssertionError(rule)

adobe = external('adobe-shadowrocket-rules', 'AdobeProxy')
adobe_direct = external('adobe-shadowrocket-rules', 'AdobeDirect')
openai = external('openai-shadowrocket-rules', 'OpenAI_Precise')
pinterest = external('pinterest-shadowrocket-rules', 'Pinterest')
base = [(adobe,'ADOBE'),(adobe_direct,'DIRECT'),(openai,'OPENAI'),
        (provider('Claude'),'CLAUDE'),(provider('X'),'X'),(pinterest,'PINTEREST'),
        (provider('InternationalPriority'),'PROXY')]
expectations = {
    'OPENAI':['api.openai.com','auth.openai.com','chatgpt.com','ws.chatgpt.com','sora.com',
              'files.oaiusercontent.com','cdn.workos.com','setup.workos.com','challenges.cloudflare.com',
              'o207216.ingest.sentry.io','register.appattest.apple.com','turn.livekit.cloud'],
    'CLAUDE':['claude.com','claude.ai','api.anthropic.com','downloads.claude.ai','platform.claude.com',
              'assets-proxy.anthropic.com','bridge.claudeusercontent.com','abc.frame.claudeusercontent.com',
              'preview.livepreview.claude.app','tool.claudemcpcontent.com','claudemcpclient.com',
              'claude.dev','clau.de','registry.npmjs.org'],
    'X':['x.com','api.x.com','twitter.com','pbs.twimg.com','video.twimg.com','t.co','twitter.map.fastly.net','grok.com','api.x.ai'],
    'ADOBE':['firefly.adobe.com','firefly.adobe.io','firefly-ps.adobe.io','firefly-ae.adobe.io',
             'firefly-cme-training.adobe.io','mds-cdn.infra.adobesensei.io',
             'pre-signed-firefly-prod.s3.amazonaws.com','stock.adobe.com','contributor.stock.adobe.com',
             'as1.ftcdn.net','www.behance.net'],
    'DIRECT':['account.adobe.com','ims-na1.adobelogin.com','creativecloud.com','fonts.adobe.com',
              'cc-api-storage.adobe.io','helpx.adobe.com','scene7.com','www.qq.com','weixin.qq.com',
              'www.taobao.com','www.jd.com','jimeng.jianying.com','douyin.com','doubao.com','feishu.cn'],
    'PINTEREST':['www.pinterest.com','i.pinimg.com','pin.it'],
    'PROXY':['www.google.com','www.youtube.com','www.netflix.com','discord.com','replicate.delivery',
             'runway.com','krea.ai','ideogram.ai','linear.app','notadobe.com',
             'firefly.adobe.io.example.invalid','openai.com.example.invalid','x.com.example.invalid'],
}
checks = 0
for domestic in ['ChinaDirect','ChinaDirectFull']:
    ordered = base + [(provider(domestic),'DIRECT'),(provider('International'),'PROXY')]
    for expected, hosts in expectations.items():
        for host in hosts:
            actual = next((policy for rules,policy in ordered if any(match(host,r) for r in rules)), 'PROXY')
            assert actual == expected, (domestic,host,expected,actual)
            checks += 1
    # Explicit Adobe entries must be absent even if a shared parent CDN remains.
    protected = Scope(adobe | adobe_direct | external('adobe-shadowrocket-rules','AdobeStockLegacy') | {('DOMAIN-KEYWORD','adobe')})
    for name in [domestic,'International','InternationalPriority']:
        assert not any(protected.contains(r) for r in provider(name)), ('Adobe mixed into',name)
# Rule-set / domain-set(+keyword) / Mihomo exports must retain exact-match semantics.
for name in json.loads((ROOT/'docs/counts.json').read_text()):
    rules = provider(name)
    directory = ROOT/'rule/Shadowrocket'/name
    combined = read_rules(directory/(name+'_Domain.list')) | read_rules(directory/(name+'_Keyword.list'))
    # Same-name full entries can be redundant beneath an identical suffix.
    suffix = {v for k,v in rules if k=='DOMAIN-SUFFIX'}
    expected = {r for r in rules if r[0]!='DOMAIN' or r[1] not in suffix}
    assert combined == expected, ('Domain Set parity',name)
    yaml = (ROOT/f'rule/Mihomo/{name}/{name}.yaml').read_text().splitlines()
    yaml_rules = {tuple(line.strip()[2:].split(',',1)) for line in yaml if line.strip().startswith('- ')}
    assert yaml_rules == rules, ('Mihomo parity',name)
assert provider('Anthropic') == provider('Claude')
# Isolation must respect boundaries, rather than removing a shared parent such as AWS.
sc = Scope({('DOMAIN-SUFFIX','adobe.com'),('DOMAIN','adobe-specific.s3.amazonaws.com')})
assert sc.contains(('DOMAIN','firefly.adobe.com'))
assert not sc.contains(('DOMAIN','adobe.com.example.org'))
assert not sc.contains(('DOMAIN-SUFFIX','amazonaws.com'))
assert not sc.contains(('DOMAIN-SUFFIX','s3.amazonaws.com'))
print(f'PASS: {checks} routing scenarios, Adobe isolation, exact/suffix/keyword semantics, client parity and Anthropic alias')

# Every non-shared Adobe community entry must be owned by the dedicated Adobe repository.
owned = Scope(adobe | adobe_direct | external('adobe-shadowrocket-rules','AdobeStockLegacy'))
for rule in module('Adobe'):
    if rule[0] == 'DOMAIN-KEYWORD' or rule[1] in {'newrelic.com','demandbase.com','bam.nr-data.net'}:
        continue
    assert owned.contains(rule), ('New Adobe source entry needs explicit classification', rule)
print('PASS: Adobe source migration coverage')
