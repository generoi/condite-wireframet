#!/usr/bin/env python3
"""Renderöi Condite-wireframet headless-Chromella, ajaa extract2.js:n sivun
sisällä ja tallentaa rakenteellisen tekstipuun JSONiksi."""
import io, os, re, json, html, subprocess, sys

SRC = '/Users/olli.rimpilainen/Claude/Condite/wireframet'
HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PROBE_DIR = os.path.join(HERE, 'probes')

# 21 pääsivua, esitysjärjestyksessä (IA:n mukaan)
PAGES = [
    ('condite_etusivu_wireframe.html',                 'Etusivu'),
    ('condite_tuotteet_wireframe.html',                'Tuotteet (hub)'),
    ('condite_tuotelistaus_feelia_wireframe.html',     'Tuotteet ja haku (listaus)'),
    ('condite_tuotekortti_v3_wireframe.html',          'Tuotekortti'),
    ('condite_brandihub_wireframe.html',               'Brändit (hub)'),
    ('condite_omabrandi_xocofine_wireframe.html',      'Oma brändi — Xocofine'),
    ('condite_toimialat_wireframe.html',               'Toimialat (hub)'),
    ('condite_segmenttihubi_leipomot_wireframe.html',  'Segmenttihubi — Leipomot'),
    ('condite_reseptipankki_wireframe.html',           'Reseptipankki'),
    ('condite_reseptisivu_wireframe.html',             'Reseptisivu'),
    ('condite_tuotekehitys_wireframe.html',            'Tuotekehitys (hub)'),
    ('condite_makupaja_wireframe.html',                'Makupaja'),
    ('condite_raatalointiprosessi_wireframe.html',     'Räätälöintiprosessi'),
    ('condite_reseptikehitys_wireframe.html',          'Resepti- ja sovelluskehitys'),
    ('condite_private_label_wireframe.html',           'Private label'),
    ('condite_referenssit_wireframe.html',             'Referenssit'),
    ('condite_yritys_wireframe.html',                  'Meistä'),
    ('condite_vastuullisuus_wireframe.html',           'Vastuullisuus ja toimitusketju'),
    ('condite_yhteys_wireframe.html',                  'Yhteys'),
    ('condite_laskutusohjeet_wireframe.html',          'Laskutusohjeet'),
    ('condite_kampanja_wireframe.html',                'Kampanjaländäri'),
]


def render(fname):
    """Injektoi extractor sivuun, renderöi, palauta JSON-puu."""
    ext = io.open(os.path.join(HERE, 'extract2.js'), encoding='utf-8').read()
    s = io.open(os.path.join(SRC, fname), encoding='utf-8').read()
    if '</body>' not in s:
        raise RuntimeError('ei </body>-tagia')
    s = s.replace('</body>', '<script>setTimeout(function(){try{' + ext
                  + '}catch(e){document.title="EXTRACT_ERROR: "+e.message;}},120);</script>\n</body>', 1)
    os.makedirs(PROBE_DIR, exist_ok=True)
    probe = os.path.join(PROBE_DIR, fname)
    io.open(probe, 'w', encoding='utf-8').write(s)

    out = subprocess.run(
        [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
         '--virtual-time-budget=12000', '--dump-dom', 'file://' + probe],
        capture_output=True, text=True, timeout=180).stdout

    if 'EXTRACT_ERROR' in out:
        m = re.search(r'EXTRACT_ERROR: ([^<]*)', out)
        raise RuntimeError('extractor kaatui: ' + (m.group(1) if m else '?'))
    m = re.search(r'<pre id="EXTRACT">(.*?)</pre>', out, re.S)
    if not m:
        raise RuntimeError('EXTRACT-elementtiä ei löytynyt (renderöinti kesken?)')
    return json.loads(html.unescape(m.group(1)))


if __name__ == '__main__':
    only = sys.argv[1:] or None
    trees = {}
    for fname, label in PAGES:
        if only and not any(o in fname for o in only):
            continue
        try:
            t = render(fname)
            t['label'] = label
            t['file'] = fname
            trees[fname] = t
            nsec = len(t['sections'])
            nitem = sum(len(s['items']) for s in t['sections'])
            nword = sum(len(i['text'].split()) for s in t['sections'] for i in s['items']) \
                + sum(len((s['heading'] or '').split()) for s in t['sections'])
            print(f'ok   {label:34} {nsec:>3} sektiota {nitem:>4} kohtaa {nword:>5} sanaa')
        except Exception as e:
            print(f'FAIL {label:34} {e}')
    path = os.path.join(HERE, 'trees.json')
    json.dump(trees, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n→', path, f'({len(trees)} sivua)')
