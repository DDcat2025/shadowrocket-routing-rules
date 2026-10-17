"""Behavior checks for cross-repository priority, domain precision and exports."""
from __future__ import annotations
from pathlib import Path
import json
import ipaddress
from build_rules import ROOT, Scope, external, read_rules, read_ip_rules, module


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
        (provider('Gemini'),'GEMINI'),
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
    'GEMINI':['gemini.google.com','app.gemini.google.com','gemini.google',
              'aistudio.google.com','ai.google.dev','generativelanguage.googleapis.com',
              'bard.google.com','makersuite.google.com',
              'alkalimakersuite-pa.clients6.google.com','proactivebackend-pa.googleapis.com',
              'robinfrontend-pa.googleapis.com','accounts.google.com','oauth2.googleapis.com',
              'www.googleapis.com','apis.google.com','fonts.googleapis.com','fonts.gstatic.com',
              'www.gstatic.com','gemini.gstatic.com','lh3.googleusercontent.com',
              'lh4.googleusercontent.com','ogads-pa.clients6.google.com',
              'waa-pa.clients6.google.com','www.googletagmanager.com'],
    'ADOBE':['firefly.adobe.com','firefly.adobe.io','firefly-ps.adobe.io','firefly-ae.adobe.io',
             'firefly-cme-training.adobe.io','mds-cdn.infra.adobesensei.io',
             'pre-signed-firefly-prod.s3.amazonaws.com','stock.adobe.com','contributor.stock.adobe.com',
             'as1.ftcdn.net','www.behance.net'],
    'DIRECT':['account.adobe.com','ims-na1.adobelogin.com','creativecloud.com','fonts.adobe.com',
              'cc-api-storage.adobe.io','helpx.adobe.com','scene7.com','www.qq.com','weixin.qq.com',
              'www.taobao.com','www.jd.com','jimeng.jianying.com','douyin.com','doubao.com','feishu.cn',
              'vjshi.com','www.vjshi.com','mp4.vjshi.com','future-service.vjshi.com',
              'vjshi.soboten.com','vjshi-data-online-upload.oss-cn-shanghai.aliyuncs.com',
              'vjshi-personal-picture-online.oss-cn-hangzhou.aliyuncs.com',
              'vjshi-photos-preview-not-enabled-prod.oss-cn-shanghai.aliyuncs.com',
              'stock.xinpianchang.com','video.699pic.com','www.vcg.com','www.hellorf.com',
              'stock.tuchong.com','static-prod.ituchong.com','huaban.com','hbimg.huabanimg.com',
              'www.gaoding.com','cdn.dancf.com','gd-filems.dancf.com','static.chuangkit.com',
              'ibaotu.com','www.58pic.com','www.zcool.com.cn'],
    'PINTEREST':['www.pinterest.com','i.pinimg.com','pin.it'],
    'PROXY':['www.google.com','www.youtube.com','www.netflix.com','discord.com','replicate.delivery',
             'runway.com','krea.ai','ideogram.ai','linear.app','notadobe.com',
             'browserleaks.com','www.browserleaks.com','probe.browserleaks.net','probe.browserleaks.org',
             'firefly.adobe.io.example.invalid','openai.com.example.invalid','x.com.example.invalid'],
}
expectations['CLAUDE'] += [
    'anthropic.com.cdn.cloudflare.net', 'anthropic.auth0.com', 'anthropic-com.ghost.io',
    'static.intercomassets.com',
]
# Existing OpenAI rules intentionally precede Claude for these shared hosts.
# Membership in Claude remains useful for clients that subscribe to it alone.
expectations['OPENAI'] += [
    'api-iam.intercom.io', 'widget.intercom.io', 'downloads.intercomcdn.com', 'js.intercomcdn.com',
]
checks = 0
gemini = provider('Gemini')
assert not any(kind == 'DOMAIN-KEYWORD' for kind, _ in gemini)
negative_gemini_hosts = [
    'www.google.com','www.youtube.com','drive.google.com',
    'maps.googleapis.com','storage.googleapis.com',
    'colab.research.google.com','developerprofiles-pa.googleapis.com',
    'cloudcode-pa.googleapis.com','generativelanguage.example.org',
    'notgemini.google.com','gemini.google.com.example.org','aistudio.google.com.example.org',
    'accounts.google.com.example.org','robinfrontend-pa.googleapis.com.example.org',
    'evilgoogleusercontent.com','lh3.googleusercontent.com.example.org','evilgstatic.com',
    'www.gstatic.com.example.org','unrelated.clients6.google.com',
]
for host in negative_gemini_hosts:
    assert not any(match(host, r) for r in gemini), ('Gemini provider too broad', host)
creative = read_rules(ROOT / 'data/custom/domestic-creative.list')
# Platform supplements must not capture lookalikes, other tenants or shared roots.
negative_creative_hosts = [
    'evilvjshi.com','vjshi.com.example.invalid','other.soboten.com','soboten.com',
    'aliyuncs.com','oss-cn-shanghai.aliyuncs.com','oss-cn-hangzhou.aliyuncs.com',
    'other-bucket.oss-cn-shanghai.aliyuncs.com','other-bucket.oss-cn-hangzhou.aliyuncs.com',
    'vjshi-data-online-upload.oss-cn-shanghai.aliyuncs.com.example.invalid',
    'dancf.com','unrelated.dancf.com','cdn.dancf.com.example.invalid',
    'huabanimg.com','unrelated.huabanimg.com','ituchong.com','unrelated.ituchong.com',
    'www.googletagmanager.com','firefly.adobe.com','chatgpt.com','claude.ai',
]
for host in negative_creative_hosts:
    assert not any(match(host, r) for r in creative), ('Creative supplement too broad', host)
diagnostics = read_rules(ROOT / 'data/custom/network-diagnostics.list')
for host in ['evilbrowserleaks.com', 'browserleaks.com.example.org',
             'probe.browserleaks.net.example.org', 'browserleaks.org.example.org']:
    assert not any(match(host, r) for r in diagnostics), ('Diagnostics supplement too broad', host)
for name in ['International', 'InternationalPriority']:
    assert diagnostics <= provider(name), ('Diagnostics missing from', name)
for domestic in ['ChinaDirect','ChinaDirectFull']:
    assert creative <= provider(domestic), ('Creative supplement missing from', domestic)
    for host in ['browserleaks.com', 'www.browserleaks.com', 'probe.browserleaks.net', 'probe.browserleaks.org']:
        assert not any(match(host, r) for r in provider(domestic)), ('Diagnostics must not route DIRECT', domestic, host)
    ordered = base + [(provider(domestic),'DIRECT'),(provider('International'),'PROXY')]
    for expected, hosts in expectations.items():
        for host in hosts:
            actual = next((policy for rules,policy in ordered if any(match(host,r) for r in rules)), 'PROXY')
            assert actual == expected, (domestic,host,expected,actual)
            checks += 1
    # Clients that have not added the optional provider retain the old proxy path.
    legacy_ordered = [(rules, policy) for rules, policy in ordered if policy != 'GEMINI']
    legacy_shared = {'fonts.googleapis.com': 'CLAUDE', 'fonts.gstatic.com': 'CLAUDE'}
    for host in expectations['GEMINI']:
        actual = next((policy for rules, policy in legacy_ordered if any(match(host, r) for r in rules)), 'PROXY')
        assert actual == legacy_shared.get(host, 'PROXY'), ('Gemini legacy routing changed', domestic, host, actual)
    # Explicit Adobe entries must be absent even if a shared parent CDN remains.
    protected = Scope(adobe | adobe_direct | external('adobe-shadowrocket-rules','AdobeStockLegacy') | {('DOMAIN-KEYWORD','adobe')})
    for name in [domestic,'International','InternationalPriority']:
        assert not any(protected.contains(r) for r in provider(name)), ('Adobe mixed into',name)
# Rule-set / domain-set(+keyword) / Mihomo exports must retain exact-match semantics.
for name in json.loads((ROOT/'docs/counts.json').read_text()):
    if name == 'Claude_IP':
        continue  # Separate typed IP provider has no DOMAIN-SET representation.
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
print(f'PASS: {checks} routing scenarios, {len(negative_creative_hosts)} creative and {len(negative_gemini_hosts)} Gemini boundary cases, Gemini legacy routing, Adobe isolation, exact/suffix/keyword semantics, client parity and Anthropic alias')

# Every non-shared Adobe community entry must be owned by the dedicated Adobe repository.
owned = Scope(adobe | adobe_direct | external('adobe-shadowrocket-rules','AdobeStockLegacy'))
for rule in module('Adobe'):
    if rule[0] == 'DOMAIN-KEYWORD' or rule[1] in {'newrelic.com','demandbase.com','bam.nr-data.net'}:
        continue
    assert owned.contains(rule), ('New Adobe source entry needs explicit classification', rule)
print('PASS: Adobe source migration coverage')

# IP fallback is only the officially documented API ingress space. Broader
# outbound/registration ranges must not silently take unrelated traffic.
ip_rules = read_ip_rules(ROOT / 'rule/Shadowrocket/Claude_IP/Claude_IP.list')
assert ip_rules == {('IP-CIDR', '160.79.104.0/23'), ('IP-CIDR6', '2607:6bc0::/48')}
ip_export = (ROOT / 'rule/Mihomo/Claude_IP/Claude_IP.yaml').read_text().splitlines()
ip_lines = [line.strip()[2:] for line in ip_export if line.strip().startswith('- ')]
assert set(ip_lines) == {','.join(rule) + ',no-resolve' for rule in ip_rules}
ip_networks = [ipaddress.ip_network(value) for _, value in ip_rules]
for address, expected in [
    ('160.79.104.0', True), ('160.79.104.10', True), ('160.79.105.255', True),
    ('160.79.103.255', False), ('160.79.106.0', False), ('160.79.111.255', False),
    ('2607:6bc0::', True), ('2607:6bc0:0:ffff:ffff:ffff:ffff:ffff', True),
    ('2607:6bc0:1::', False), ('2607:6bc1::', False),
]:
    ip = ipaddress.ip_address(address)
    assert any(ip in network for network in ip_networks if ip.version == network.version) == expected, address
for provider_name in ['Claude_Core', 'Claude_Dependencies', 'Claude']:
    values = provider(provider_name)
    assert not any(kind == 'DOMAIN-KEYWORD' for kind, _ in values), provider_name
    for broad in ['sentry.io', 'statsigapi.net', 'datadoghq.com', 'intercom.io',
                  'intercomcdn.com', 'intercomassets.com', 'auth0.com', 'ghost.io', 'cloudflare.net']:
        assert ('DOMAIN-SUFFIX', broad) not in values, (provider_name, broad)
assert {('DOMAIN', host) for host in [
    'api-iam.intercom.io', 'widget.intercom.io', 'downloads.intercomcdn.com',
    'js.intercomcdn.com', 'static.intercomassets.com',
]} <= provider('Claude_Dependencies')
for host in ['other.auth0.com', 'other.ghost.io', 'other.cdn.cloudflare.net',
             'anthropic.auth0.com.example.org', 'anthropic-com.ghost.io.example.org']:
    assert not any(match(host, rule) for rule in provider('Claude_Core')), host
print('PASS: Claude ingress IP boundaries, no-resolve export parity and shared-domain precision')
