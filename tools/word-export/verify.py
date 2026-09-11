#!/usr/bin/env python3
"""Tarkista tuotetut Word-dokumentit — riippumattomasti textutililla (Applen
docx-parseri) ja vertaa sisältöä lähdepuuhun, ettei tekstiä ole kadonnut."""
import io, os, re, json, sys, subprocess, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'word-export')
sys.path.insert(0, HERE)
from render import PAGES

trees = json.load(io.open(os.path.join(HERE, 'trees.json'), encoding='utf-8'))
BRACKET = re.compile(r'\[[^\]]*\]')


def words(s):
    return len(re.findall(r'\S+', s))


def txt_of(path):
    return subprocess.run(['textutil', '-convert', 'txt', '-stdout', path],
                          capture_output=True, text=True).stdout


def slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')


fails, warns = [], []
print(f"{'dokumentti':40} {'sanat':>6} {'lähde':>6} {'kate%':>6}  tarkistukset")
print('-' * 92)

order = [(f, l) for f, l in PAGES if f in trees]
for i, (f, label) in enumerate(order, 1):
    tree = trees[f]
    name = f'{i:02d}_{slug(label)}.docx'
    path = os.path.join(OUT, name)
    if not os.path.exists(path):
        fails.append(f'{name}: tiedosto puuttuu')
        continue

    body = txt_of(path)
    if not body.strip():
        fails.append(f'{name}: textutil ei saanut sisältöä (tiedosto rikki?)')
        continue

    # lähdepuun sanamäärä (sisältö + kromi)
    src_words = 0
    for s in tree['sections']:
        src_words += words(s['heading'] or '')
        for it in s['items']:
            src_words += words(it['text'])
    for c in tree.get('chrome', []):
        src_words += words(c['name'])
        for it in c['items']:
            src_words += words(it['text'])

    doc_words = words(body)
    cover = 100.0 * doc_words / src_words if src_words else 0

    checks = []
    # 1) H1 mukana
    h1 = next((s['heading'] for s in tree['sections'] if s['level'] == 1 and s['heading']), None)
    if h1:
        probe = BRACKET.sub('', h1).strip() or h1
        key = probe[:28] if len(probe) > 8 else h1[:28]
        checks.append('H1' if key.strip('[] ') and key.strip('[] ')[:20] in body else 'H1?')
        if 'H1?' == checks[-1] and h1[:20] not in body:
            warns.append(f'{name}: H1 ei löytynyt tekstistä ({h1[:40]!r})')

    # 2) kromiosio
    if tree.get('chrome'):
        ok = 'Sivupohjan elementit' in body
        checks.append('kromi' if ok else 'KROMI PUUTTUU')
        if not ok:
            fails.append(f'{name}: kromiosio puuttuu')

    # 3) KYSYMYS ei leipätekstiin
    cut = body.find('Liite: avoimet kysymykset')
    head_part = body[:cut] if cut > -1 else body
    stray = len(re.findall(r'KYSYMYS', head_part))
    checks.append('kysymykset eroteltu' if stray == 0 else f'{stray} KYSYMYSTÄ LEIPÄTEKSTISSÄ')
    if stray:
        fails.append(f'{name}: {stray} KYSYMYS-notea jäi leipätekstiin')

    # 4) kattavuus
    if cover < 92:
        fails.append(f'{name}: vain {cover:.0f} % lähteen sanoista dokumentissa')
        checks.append('VAJAA')
    elif cover > 118:
        warns.append(f'{name}: {cover:.0f} % — dokumentissa selvästi enemmän tekstiä kuin lähteessä')

    print(f'{name:40} {doc_words:>6} {src_words:>6} {cover:>5.0f}%  ' + ', '.join(checks))

print('-' * 92)
if fails:
    print('\nVIRHEET:')
    for x in fails:
        print('  ✗', x)
if warns:
    print('\nHUOMIOT:')
    for x in warns:
        print('  !', x)
if not fails:
    print('\nKaikki tarkistukset läpi.' + (f' ({len(warns)} huomiota)' if warns else ''))
