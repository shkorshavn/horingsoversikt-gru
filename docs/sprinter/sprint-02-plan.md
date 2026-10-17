# Sprint 2 – Nettsiden: plan

Status: Plan til godkjenning · 17. oktober 2026

## Mål
En statisk nettside som viser høringene fra `data/horinger.json` og statusen fra
`data/status.json`, med sortering, fargekoding etter frist, filtre, fritekstsøk og
CSV-eksport. Siden skal fungere på mobil og PC og oppfylle WCAG 2.1 AA. Publisering på
GitHub Pages og automatisk oppdatering hører til sprint 3.

## Hva som bygges

### Filer
| Fil | Innhold |
|---|---|
| `index.html` | Selve siden, med tilgjengelig struktur (overskrifter, landemerker, skjemaetiketter) |
| `side/stil.css` | Utseende, responsivt fra 320 px og opp, lys og mørk modus |
| `side/app.js` | Leser JSON-filene, filtrerer, sorterer, tegner listen og lager CSV. Ren JavaScript, ingen rammeverk |
| `data/horinger.json`, `data/status.json` | Resultatet fra siste testkjøring (16.10), slik at siden har ekte innhold å vise. Erstattes av den ukentlige kjøringen i sprint 3 |
| `sources.yaml`, `horinger/` | Nytt felt `niva` per kilde (Storting, Regjering, Direktorat, Fylkeskommune, Statsforvalter), som tas med i JSON-filen for filteret «kilde/nivå». Ingen andre endringer i innhentingen |

Siden har **ingen eksterne avhengigheter**: ingen skrifter, skript eller stilark fra andre
nettsteder, og ingen sporing. Alt ligger i repoet.

### Funksjoner
- **Liste** sortert på frist, nærmeste først. Hver høring viser tittel (lenke til kilden),
  høringsinstans, frist i norsk format («11. november 2026»), «dager igjen», kategori og en
  kort ingress.
- **Fargekoding etter frist:** under 14 dager, 14–30 dager og over 30 dager. Fargen står
  aldri alene: hver høring har også tekst («5 dager igjen») og en tydelig etikett, slik at
  siden fungerer for fargeblinde og i utskrift.
- **Filtre:** kategori, kilde/nivå, prioritet (1 og 2 valgt som standard) og fritekstsøk i
  tittel, instans og ingress. Antall treff vises og leses opp for skjermlesere.
- **Bryter for utløpte høringer**, av som standard.
- **Statusoversikt per kilde:** siste oppdatering, antall høringer og status (ok, feil med
  feilmelding, ikke overvåket), også for inaktive kilder.
- **CSV-eksport** av det som vises med gjeldende filtre: semikolon som skilletegn og UTF-8
  med BOM, slik at æ, ø og å blir riktige når filen åpnes i norsk Excel.
- **Valgte filtre huskes i adressen** (f.eks. `?kategori=…&q=…`), slik at en filtrert
  visning kan deles som lenke.
- Datoer og «dager igjen» regnes i norsk tid.

### Visuelt uttrykk
Bygger på Gjøvikregionens designsystem (https://www.gjovikregionen.no/test/design-system),
hentet 17.10.2026:

| Bruk | Farge (designsystemet) | Kode |
|---|---|---|
| Overskrifter, tekst, lenker, knapper og logo | Skogsgrønn 700 | `#05423b` |
| Sekundær tekst | Skogsgrønn 300 | `#366f68` |
| Bakgrunn, skillelinjer | Beige 500 | `#fefaf0` |
| Fremheving, valgte filtre | Turkis 700 / 300 | `#baf2e3` / `#dbfff5` |
| Frist under 14 dager, feil | Oransje 700 / 100, med burgunder tekst | `#ff6e3d` / `#ffbba5`, `#540024` |
| Frist 14–30 dager | Rosa 300 | `#f8cee1` |
| Frist over 30 dager, ok-status | Grønn 700 / 100 | `#b5de75` / `#e2f6c2` |

- **Logo:** Gjøvikregionen-logoen (SVG) fra designsystemet, i skogsgrønn.
- **Skrift:** Designsystemet bruker Satoshi. Den lastes fra Gjøvikregionens eget nettsted, og
  jeg kan ikke hente skriftfilene herfra. Siden bruker derfor systemets skrift, med Satoshi
  først i listen, slik at den brukes der den er installert. Skriften kan legges inn i repoet
  senere hvis du ønsker det.
- Alle fargekombinasjoner kontrolleres mot kontrastkravet i WCAG 2.1 AA før bruk. De lyse
  fristfargene brukes som bakgrunn bak mørk tekst, ikke som tekstfarge.
- Merk: Designsystemet ligger under `/test/` på nettstedet og kan bli endret. Fargene samles
  i variabler øverst i stilarket, slik at de er enkle å oppdatere.

## Utenfor omfang (senere sprinter)
Spesifikasjonen nevner tre ting for nettsiden som avhenger av data som ikke finnes ennå. De
bygges i sprinten der dataene kommer, etter regel 5 i `CLAUDE.md`:

| Funksjon | Sprint | Hvorfor ikke nå |
|---|---|---|
| Merke «Ny» siden forrige oppdatering | 3 | Krever sammenligning med forrige kjøring |
| Utløpte høringer i listen | 3 | Bryteren bygges nå, men innhentingen fjerner utløpte høringer. Arkivet kommer i sprint 3 |
| Filter «regionen er høringspart» | 6 | Høringsparter hentes i sprint 6 |
| Filter «mottatt av Gjøvik kommune» | 7 | Postlista kobles i sprint 7 |

Publisering på GitHub Pages skjer i sprint 3.

## Tester og kvalitetssikring
- **Automatiske tester av siden** (`tests/test_nettside.py`) med Playwright i Chromium, mot en
  lokal webserver og egne testdata: sortering, hvert filter, fritekstsøk, bryteren for
  utløpte, fargeklasser ved 13, 14, 30 og 31 dager igjen, statusoversikten, CSV-innhold
  (tegn og skilletegn), filtre i adressen og visning uten data eller med feil i
  `status.json`.
- **Tilgjengelighet:** axe-core kjøres mot siden i testene, i både mobil- og PC-bredde.
  Kravet er null alvorlige («serious» og «critical») funn. I tillegg kontrollerer jeg
  tastaturnavigering og fokusmarkering manuelt.
- **Skjermbilder** ved 375 px og 1280 px, lagt ved i rapporten.
- Playwright og axe-core installeres i utviklingsmiljøet og i testkjøringen, og
  dokumenteres i README. De brukes bare i testene, ikke på selve siden.
- Hele sjekklisten A–J i `CLAUDE.md`. Punkt C og D gjelder her visningen: at siden viser det
  som står i JSON-filen, kontrollert mot fem høringer.

## Risikoer
1. **Playwright i Chromium** må fungere både her og i GitHub Actions. Chromium er
   forhåndsinstallert her. Faller det, bruker jeg en enklere testform og sier det i
   rapporten.
2. **Siden må åpnes via en webserver**, ikke ved å dobbeltklikke på filen, fordi nettlesere
   ikke lar en lokal fil lese JSON. README forklarer hvordan (`python -m http.server`). På
   GitHub Pages er dette ikke noe problem.
3. **Kontrast i fristfargene** kan være vanskelig å få innenfor AA, særlig gult. Fargene
   velges og kontrolleres mot kravet før bruk.

## Avklart med Svein 17.10.2026
1. «Ny»-merke og utløpte høringer bygges i sprint 3, filtrene for høringsparter og postlista i
   sprint 6 og 7.
2. Logo og farger hentes fra Gjøvikregionens designsystem (se «Visuelt uttrykk»).
3. Tittel: «Høringer – Gjøvikregionen».

Planen venter bare på godkjenning.
