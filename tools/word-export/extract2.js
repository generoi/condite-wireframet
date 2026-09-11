/* Condite-wireframe → rakenteellinen tekstipuu.
   Otsikkovetoinen segmentointi: toimii riippumatta siitä käyttääkö sivu
   <section>- vai <div>-pohjaista markupia. Ajetaan sivun sisällä;
   tulos JSONina <pre id="EXTRACT">-elementtiin. */
(function () {
  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'IFRAME']);
  const norm = s => (s || '').replace(/ /g, ' ').replace(/\s+/g, ' ').trim();

  const INLINE = /^(SPAN|STRONG|EM|B|I|U|BR|SMALL|CODE|TIME|SUP|SUB|ABBR|MARK|S|DEL|INS|Q)$/;
  const CTA_SEL = '.btn,.button,.cta,[class*="btn"],[class*="cta"]';
  /* Sisäiset muistiinpanot: aina oma kohta, ettei note sulaudu aikajanan tekstiin. */
  const NOTE_SEL = '.note,.oc-note,.hero-note,[class*="note"],[class*="kysymys"],[role="note"]';

  /* Kromi — toistuvat sivupohjan osat. Poimitaan erikseen omiksi lohkoikseen. */
  const CHROME_SEL = [
    '.site-header', 'body > header', '.nav-wrap',
    '.crumbs-wrap', '.crumbs', 'nav[aria-label*="urupolku"]',
    '.site-footer', 'body > footer',
    '.demo-bar', '.view-switch', '.wf-note', '.skip-link', '.demo-inner'
  ].join(',');

  /* Demo-/wireframe-apuvälineet: eivät ole sivun sisältöä eivätkä kromia. */
  const DEMO_SEL = '.demo-bar,.view-switch,.wf-note,.skip-link,.demo-inner,.segmented,.seg-btns';

  function isHiddenSelf(el) {
    if (el.hasAttribute('hidden')) return true;
    const cs = getComputedStyle(el);
    return cs.display === 'none' || cs.visibility === 'hidden';
  }

  /* Teksti niin, että inline-lapset erotellaan välilyönnillä.
     Korjaa esim. vaiheistuksen "1Briiffi" → "1 Briiffi". */
  function textOf(el) {
    let out = '';
    for (const n of el.childNodes) {
      if (n.nodeType === 3) { out += n.nodeValue; continue; }
      if (n.nodeType !== 1) continue;
      if (SKIP_TAGS.has(n.tagName)) continue;
      out += ' ' + textOf(n) + ' ';
    }
    return out;
  }

  function roleOf(el) {
    const t = el.tagName;
    const c = ' ' + (typeof el.className === 'string' ? el.className : '') + ' ';
    if (/^H[1-6]$/.test(t)) return t.toLowerCase();
    if (t === 'LI') return 'li';
    if (t === 'BUTTON') return 'cta';
    if (t === 'A' && /\bbtn\b|button|\bcta\b/i.test(c)) return 'cta';
    if (t === 'TH') return 'th';
    if (t === 'TD') return 'td';
    if (t === 'LABEL') return 'label';
    if (t === 'SUMMARY') return 'summary';
    if (t === 'FIGCAPTION') return 'caption';
    if (t === 'BLOCKQUOTE') return 'quote';
    if (t === 'DT') return 'dt';
    if (t === 'DD') return 'dd';
    if (/(^| )ph( |$)|(^| )ph-[\d-]/.test(c) || /placeholder-media|media-ph/i.test(c)) return 'image';
    if (/eyebrow|kicker/i.test(c)) return 'eyebrow';
    if (/\blede\b|\blead\b|\bintro\b/i.test(c)) return 'lede';
    if (/\boc-note\b/.test(c)) return 'text';                       // org-kaavion kuvaus = sisältöä
    if (/(^| )note( |$)|hero-note|wf-note|kysymys|notice|\bhuom/i.test(c)) return 'note';
    if (/\bchip\b|\btag\b|\bbadge\b|\bpill\b/i.test(c)) return 'chip';
    if (t === 'P') return 'p';
    return 'text';
  }

  /* Onko lapsi lohkotasoinen? <a>/<label> lasketaan inlineksi vain jos siinä ei ole
     omaa lohkorakennetta (linkki leipätekstin sisällä) — kortti-<a> on lohko. */
  function hasBlockChild(el) {
    for (const ch of el.children) {
      if (SKIP_TAGS.has(ch.tagName)) continue;
      if (!norm(textOf(ch))) continue;
      if (!(ch instanceof HTMLElement)) return true;   // SVG ym.: käsitellään erikseen
      if (ch.matches && (ch.matches(CTA_SEL) || ch.matches(NOTE_SEL))) return true;
      if (INLINE.test(ch.tagName)) continue;
      if (/^(A|LABEL)$/.test(ch.tagName) && !hasBlockChild(ch)) continue;
      return true;
    }
    return false;
  }
  function isLeaf(el) { return !hasBlockChild(el); }

  /* Kerää tekstilehdet dokumenttijärjestyksessä. */
  function harvest(root, opts) {
    opts = opts || {};
    const items = [];
    (function walk(el) {
      for (const ch of el.children) {
        if (SKIP_TAGS.has(ch.tagName)) continue;
        if (ch.tagName === 'svg') {
          // Grafiikan saavutettava kuvaus + foreignObjecteissa oleva oikea copy
          const d = ch.querySelector('desc') || ch.querySelector('title');
          if (d && norm(d.textContent)) items.push({ role: 'image', text: norm(d.textContent), tag: 'svg-desc' });
          ch.querySelectorAll('foreignObject').forEach(fo => walk(fo));
          continue;
        }
        if (!(ch instanceof HTMLElement)) continue;          // muut ei-HTML-elementit
        if (!opts.keepDemo && ch.matches && ch.matches(DEMO_SEL)) continue;
        if (!opts.insideChrome && ch.matches && ch.matches(CHROME_SEL)) continue;
        const hidden = isHiddenSelf(ch);
        if (hidden && !opts.keepHidden) continue;            // vaihtoehtoiset tilat pois
        if (ch.tagName === 'SELECT') {
          const choices = Array.from(ch.options || []).map(o => norm(o.textContent)).filter(Boolean);
          if (choices.length) items.push({ role: 'select', text: choices.join(' · '), tag: 'select' });
          continue;
        }
        const txt = norm(textOf(ch));
        if (!txt) continue;
        if (isLeaf(ch)) items.push({ role: roleOf(ch), text: txt, tag: ch.tagName.toLowerCase() });
        else walk(ch);
      }
    })(root);
    return items;
  }

  /* ---- Sisältöjuuri: main, tai body ilman kromia ---- */
  const main = document.querySelector('main') || document.body;

  /* ---- Sisältö: kerää lehdet ja segmentoi otsikoista ---- */
  const flat = harvest(main, {});
  const sections = [];
  let cur = null;
  function newSection(title, level) {
    cur = { heading: title, level: level, items: [] };
    sections.push(cur);
  }
  for (const it of flat) {
    if (it.role === 'h1' || it.role === 'h2') {
      newSection(it.text, it.role === 'h1' ? 1 : 2);
      continue;
    }
    if (!cur) newSection(null, 0);   // ennen ensimmäistä otsikkoa (esim. eyebrow)
    cur.items.push(it);
  }
  /* eyebrow ennen otsikkoa kuuluu seuraavalle sektiolle — siirretään */
  for (let i = 0; i < sections.length - 1; i++) {
    const s = sections[i], nx = sections[i + 1];
    while (s.items.length && ['eyebrow'].includes(s.items[s.items.length - 1].role)) {
      nx.items.unshift(s.items.pop());
    }
  }

  /* ---- Kromi: navi (myös kiinni olevat alasvedot), murupolku, footer ---- */
  function chromeBlock(sel, name) {
    const el = document.querySelector(sel);
    if (!el) return null;
    const items = harvest(el, { insideChrome: true, keepHidden: true });
    return items.length ? { name: name, items: items } : null;
  }
  const chrome = [
    chromeBlock('.site-header, body > header, .nav-wrap', 'Päänavigaatio'),
    chromeBlock('.crumbs-wrap, .crumbs', 'Murupolku'),
    chromeBlock('.site-footer, body > footer', 'Footer')
  ].filter(Boolean);

  const result = {
    file: location.pathname.split('/').pop(),
    title: document.title,
    meta_desc: (document.querySelector('meta[name="description"]') || {}).content || null,
    sections: sections.filter(s => s.heading || s.items.length),
    chrome: chrome
  };

  const pre = document.createElement('pre');
  pre.id = 'EXTRACT';
  pre.textContent = JSON.stringify(result);
  document.documentElement.replaceChildren(document.createElement('head'), document.createElement('body'));
  document.body.appendChild(pre);
})();
