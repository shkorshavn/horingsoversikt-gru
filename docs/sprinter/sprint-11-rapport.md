# Sprint 11 – Verktøylinjen over filtrene

## Sammendrag
Antall høringer, sortering, «Skriv ut», «Last ned som CSV» og fargeforklaringen er flyttet fra
båndet i toppen til venstre kolonne, over «Filtre».

På PC står verktøylinjen fast mens filtrene ruller under, slik du ønsket. Toppen er blitt
lavere, så listen får mer plass. På mobil står verktøylinjen over «Filtre»-boksen.

Endringen er publisert, og «Tester» og «Publiser» er grønne på GitHub. Alle punktene i
sjekklisten er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget
- **`index.html`:**
  - Verktøylinjen er flyttet til en ny venstre kolonne (`.venstre`) over `<aside class="filtre">`.
  - Båndet i toppen er fjernet.
  - Tastaturrekkefølgen er nå verktøylinje, filtre og liste.
- **`side/stil.css`:**
  - **Oppsett i den smale kolonnen:**
    - Antallet står øverst.
    - «Sorter etter» står med nedtrekkslisten i full bredde.
    - Knappene står ved siden av hverandre med litt mindre skrift, slik at «Last ned som CSV»
      får plass på én linje.
    - Fargeforklaringen står med én farge per linje.
    - En tynn strek skiller verktøylinjen fra filtrene.
  - **PC:** venstre kolonne er en fleksibel kolonne med verktøylinjen fast øverst, og filtrene
    er rulleområdet under.
  - **Utskrift:** antallet og fargeforklaringen står øverst på én linje, som før.
- **`tests/test_nettside.py`:**
  - To nye tester: verktøylinjen står fast over filtrene på PC, og over filtrene på mobil.
  - Testen fra sprint 10 for verktøylinjen i toppen er erstattet.
  - Testen for at filtrene og listen ruller hver for seg legger musen lenger ned, under
    verktøylinjen.
- **`README.md`:** avsnittet «Nettsiden» og «Status».
- **Skjermbilder:** `docs/sprinter/bilder/sprint-11-pc.png` og `sprint-11-mobil.png`.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **424 bestått, 0 feilet, 0 hoppet over** (67,0 s). På GitHub: «Tester» success (run 40664111181, dc4df92) |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: ingen endringer. `actionlint`: ingen funn |
| C. Ekte data | Bestått | Siden kontrollert lokalt med de publiserte dataene på 1280 × 900, 1366 × 700 (laptop) og 375 × 800 (mobil). Ingen vannrett rulling. «Publiser» success (run 40664111092) |
| D. Stikkprøver | Ikke relevant | Ingen kilder er endret |
| E. Tegn og datoer | Bestått | Æ, ø og å og «Oppdatert 28. oktober 2026 kl. 09.22» vises riktig (skjermbildene) |
| F. Feilhåndtering | Bestått | Uendret. Testene for manglende datafiler (høringer, status, arkiv) består, og knappene deaktiveres som før når data mangler |
| G. Kodegjennomgang | Bestått | `git diff` for sprinten: 6 filer, 115 nye og 94 fjernede linjer. CSS for båndet i toppen er fjernet helt (ingen død kode igjen, sjekket med søk på `verktoy-band` og `verktoy-indre`). Ingen endringer i JavaScript, siden elementene har samme id |
| H. Høflighet | Ikke relevant | Ingen kall til kildene |
| I. Dokumentasjon | Bestått | README («Nettsiden», «Status») |
| J. Akseptansekriterier | Bestått | Se tabellen under |

## Akseptansekriterier
| Kriterium (plan og Sveins svar) | Oppfylt | Bevis |
|---|---|---|
| Antall, sortering, utskrift, CSV og fargeforklaring står i venstre del, over filtrene | Ja | `test_verktoylinjen_staar_fast_over_filtrene` (alle fem står i `.venstre`, ikke i toppen, over «Filtre» og til venstre for listen). Skjermbilde |
| Verktøylinjen står fast over filtrene (svar kl. 10.21) | Ja | Samme test: knappen står på samme sted når filtrene og listen rulles, og selve siden ruller ikke |
| Mobil: over filtrene, uten vannrett rulling | Ja | `test_verktoylinjen_over_filtrene_paa_mobil`. Skjermbilde |
| Utskriften er uendret | Ja | Utskriftstestene består (sidetall, innhold, ingen knapper) |
| Tilgjengelighet | Ja | axe uten alvorlige funn på 375 og 1280 px |

## Kjente feil og begrensninger
- **Lite plass til filtrene på lave skjermer.** Verktøylinjen tar ca. 275 px i høyden. På en
  laptop med 700 px synlig høyde blir det ca. 220 px igjen til filtrene. De ruller i sitt eget
  område, men viser færre valg om gangen. På en vanlig PC-skjerm (900 px) er det ca. 420 px.
- **Bredden kan avvike litt.** Verktøylinjen er noen få piksler bredere enn søkefeltet under,
  fordi filterområdet har plass til rullefelt.

## Forslag til senere sprinter
- Ingen nye.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ (Ctrl+F5) og rull i filtrene og i
   listen. Verktøylinjen skal stå i ro.
2. Sjekk siden på laptopen eller med nettleservinduet gjort lavere. Er plassen til filtrene
   god nok?
