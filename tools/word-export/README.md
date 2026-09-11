# Word-export — wireframejen tekstit Word-dokumenteiksi

Putki, joka poimii wireframe-sivujen tekstit rakenteellisesti ja tuottaa
yhden Word-dokumentin per sivu (juokseva lukudokumentti).

## Miksi näin

`PAGE`-config on osassa sivuja IIFE:n sisällä (`var PAGE`), eikä tekstiä voi
lukea staattisesti. Siksi sivu **renderöidään** headless-Chromella ja
extractor ajetaan **sivun sisällä** valmiiseen DOMiin.

Segmentointi on **otsikkovetoinen** (H1/H2-rajat `<main>`:in sisällä), koska
sivut käyttävät sekä `<section>`- että `<div>`-pohjaista markupia.

## Ajo

```bash
python3 -m venv .venv && .venv/bin/pip install python-docx
python3 render.py                    # → trees.json  (kaikki 21 sivua)
python3 render.py makupaja yritys    # → vain nimensuodatetut sivut
.venv/bin/python docgen.py ../../word-export
python3 verify.py ../../word-export  # riippumaton tarkistus textutililla
```

Sivulista ja esitysjärjestys: `PAGES` tiedostossa `render.py`.

## Tulkinnat jotka on koodattu sisään

- **Placeholderit** (`[H2: …]`, `[Luonnos: …]`) tulevat mukaan keltaisella
  korostuksella — Condite näkee mikä on vielä kirjoittamatta.
- **KYSYMYS-notet** menevät dokumentin loppuliitteeseen, eivät leipätekstiin.
  Ohjaus tehdään **tekstin** perusteella (sisältääkö sanan "kysymys"), ei
  luokkanimen — `oc-note` on sisältöä, `div.note` on muistiinpano.
- Myös copyn **sisällä** olevat `[KYSYMYS 9: …]` irrotetaan liitteeseen.
- **Vaiheistus** on SVG + `foreignObject`. Laatikot ovat vuorotellen viivan
  ylä- ja alapuolella, joten DOM-järjestys on 1,3,5,2,4,6 → `regroup_steps`
  järjestää ne numeron mukaan.
- **Kromi** (navi, murupolku, footer) tulee joka dokumenttiin omaan osioonsa.
  Navin kiinni olevat alasvedot otetaan mukaan (rakennetta, ei "tilaa").
- **Vaihtoehtoiset tilat** (lomakkeen kiitos-tila, tyhjä hakutulos, lukitut
  lohkot) jätetään pois.
- Chromen `--virtual-time-budget` on 12 s. Alle 8 s ei riitä raskaimmille
  sivuille — extraktio ehtii kesken ja `EXTRACT`-elementti puuttuu.

## Tulos

`word-export/` on **gitignoroitu** — dokumentit sisältävät sisäisiä
KYSYMYS-muistiinpanoja eivätkä kuulu julkiseen repoon.
