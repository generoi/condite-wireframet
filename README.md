# Condite.fi — wireframet

Kiillotetut HTML-wireframet Condite Oy:n verkkosivu-uudistuksesta (palvelumuotoiluvaihe).

**Selaa:** https://generoi.github.io/condite-wireframet/

## Mitä tämä on

- Itsenäisiä yhden tiedoston HTML-sivuja — ei build-vaihetta, ei riippuvuuksia.
- Vain suomi. Lomakkeet ja haku näytetään tiloineen, mutta eivät lähetä mitään.
- Jokainen sivu nojaa yhteiseen tokenikerrokseen; kanoninen lähde on
  [`condite_design_system.html`](condite_design_system.html).

## Huomiot

- Sivujen sisäiset navigaatiolinkit osoittavat tulevan sivuston osoitteisiin
  (esim. `/tuotteet/`) eivätkä avaudu tässä prototyypissä. Liiku sivujen välillä
  [hakemistosta](index.html).
- `noindex` + `robots.txt` — sivusto ei indeksoidu.

## Rakenne

| Ryhmä | Sivut |
|---|---|
| Etusivu | `condite_etusivu_wireframe.html` |
| Tuotteet ja brändit | tuotteet-hub, tuotelistaus/haku, tuotekortti v2 ja v3, brändihub, Xocofine |
| Toimialat | toimialat-hub, segmenttihubi (Leipomot) |
| Reseptit | reseptipankki, reseptisivu |
| Tuotekehitys | hub, Makupaja, räätälöintiprosessi, reseptikehitys, private label, referenssit |
| Yritys ja yhteys | Meistä, vastuullisuus, yhteys, laskutusohjeet |
| Kampanjat | kampanjaländäri |
| Systeemi | design system, vaiheistus-komponentti, Makupaja-infograafivariantit |

Toteutus: [Genero](https://genero.fi)
