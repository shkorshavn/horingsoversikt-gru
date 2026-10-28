# Sprint 9 – Faste regler for utelatte høringer

## Sammendrag
Alle høringer der tittelen begynner med «Representantforslag», legges nå under «Utelatte
høringer» med begrunnelsen «Representantforslag fra stortingsrepresentanter.».

Regelen står i `sources.yaml`. Den går foran både KI-vurderingen og vernet, slik du svarte.
Slike høringer sendes ikke til KI-en for relevansvurdering, men får KI-sammendrag som før.

Etter publiseringen 28.10. kl. 08.45 står alle 13 åpne representantforslag under «Utelatte
høringer», og ingen står i listen. Ingen andre høringer har flyttet seg.

Alle punktene i sjekklisten er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget
- **`sources.yaml`:** ny liste `felles.relevans.alltid_utelat` med kommentar. Hver regel har
  `tittel_starter_med` og `grunn`. Den første regelen gjelder «Representantforslag».
- **`horinger/relevans.py`:**
  - `fast_regel()` finner første regel som treffer. Store og små bokstaver spiller ingen rolle,
    og mellomrom først i tittelen ignoreres.
  - `vurder()` bruker regelen før KI-svaret og før vernet.
  - Høringer som treffer en regel, sendes ikke til API-et, og et eldre KI-svar for dem slettes
    fra `data/relevans.json`.
- **`horinger/sammendrag.py`:** generell `hopp_over()` i felles API-løkke og telleren «regel».
  Sammendraget bruker den ikke, så KI-sammendrag lages som før.
- **Tester:** 11 nye i `tests/test_relevans.py`. `tests/test_sammendrag.py` er tilpasset den
  nye telleren.
- **README:** avsnittet «Relevans for Gjøvikregionen» forklarer de faste reglene og hvordan du
  legger til en ny. «Status» er oppdatert.

**Endrede filer:**
- `sources.yaml`
- `horinger/relevans.py`, `horinger/sammendrag.py`
- `tests/test_relevans.py`, `tests/test_sammendrag.py`
- `README.md`
- `SPRINTSTATUS.md`
- `docs/sprinter/sprint-09-plan.md`, `docs/sprinter/sprint-09-rapport.md`

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **403 bestått, 0 feilet, 0 hoppet over** (56,6 s). Nye: 6 for regeltreff (treffer, treffer ikke, «representantforslag» midt i tittelen, grunnlovsforslag, tom tittel), 3 for at regelen går foran KI og vern (uten merke, med regionflagg, med postliste), 1 for ingen API-kall og sletting av gammelt svar, og 1 for at sammendraget lages som før. Arbeidsflyten «Tester» er grønn for b67e0d7 |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «94 files already formatted». `actionlint`: ingen funn |
| C. Ekte data | Bestått | Publiser (push, run 40652083668): «success», data 28.10.2026 kl. 08.45. 123 åpne høringer: 68 i listen og 55 utelatt. Alle 13 åpne representantforslag er utelatt, og ingen andre titler inneholder ordet. Lokal bygging før og etter endringen på samme data: bare representantforslag endret status (12 fra listen til utelatt, ett var allerede utelatt av KI-en). 4 representantforslag fra 27.10 har utløpt frist og står i arkivet. Ingen kilder er hentet på nytt, og ingen KI-kall er gjort |
| D. Stikkprøver | Bestått | Ingen kilder er endret. Alle 13 representantforslag er kontrollert, se tabellen under. Tittel, frist og lenke stemmer med dataene fra Stortinget-kilden, som ble kontrollert i v1 |
| E. Tegn og datoer | Bestått | «Utelatt: Representantforslag fra stortingsrepresentanter.» og fristen «12. november 2026» vises riktig (skjermbilde `docs/sprinter/bilder/sprint-09-rep.png`). Ingen `\u00`-koder i dataene |
| F. Feilhåndtering | Bestått | En regel uten `grunn` gir «Utelatt etter fast regel.». En regel uten `tittel_starter_med` treffer ingenting (tom streng ignoreres). Uten `alltid_utelat` er alt som før. Feilhåndteringen for API-et er uendret |
| G. Kodegjennomgang | Bestått | `git diff 0a7742d..HEAD` (uten data): 8 filer, 174 nye og 5 fjernede linjer. Se under |
| H. Høflighet | Ikke relevant | Ingen nye kall til kildene og ingen endringer i hentingen |
| I. Dokumentasjon | Bestått | README («Relevans for Gjøvikregionen», «Status») og kommentarer i `sources.yaml` |
| J. Akseptansekriterier | Bestått | Se tabellen under |

## Stikkprøver: representantforslag 28.10.2026
| Høring | Frist | I listen | Under «Utelatte» | Lenke |
|---|---|---|---|---|
| Kriminelle aktører i barnevernet (Martinussen m.fl.) | 28.10 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005985) |
| Oppfølging av overlevende og etterlatte etter katastrofer | 28.10 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005989) |
| Digital suverenitet og digital helseinfrastruktur | 28.10 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005988) |
| Vigselsrett for stortingsrepresentanter | 28.10 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005972) |
| Digitale lotterier for frivillige organisasjoner | 28.10 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005973) |
| Raskere og skånsom utbygging av solenergi | 02.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005939) |
| Forby jakt på ekorn | 02.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005991) |
| Forby reklame for fossil energi | 02.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005992) |
| Pluggbare solceller og batterier | 02.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005990) |
| Stanse opptrappingsplanen for CO2-avgiften | 02.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005993) |
| Trygt og sikkert institusjonsbarnevern | 04.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005999) |
| Forby koranskoler med overnatting | 04.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10006004) |
| Stemmerett ved kommune- og fylkestingsvalg | 12.11 | Nei | Ja | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005994) |

Kontrollert i nettleseren med de publiserte dataene: 0 representantforslag i listen, og 13 under
«Utelatte høringer» (54 utelatte i alt med standardfilteret).

## Akseptansekriterier
| Kriterium (fra planen og Sveins svar) | Oppfylt | Bevis |
|---|---|---|
| Alle representantforslag legges under «Utelatte høringer» | Ja | 13 av 13 (tabellen over). Testen `test_fast_regel_gir_ingen_api_kall_og_fjerner_gammelt_svar` dekker byggingen |
| Regelen gjelder også når regionen er høringspart eller Gjøvik kommune har mottatt brevet (svar 1) | Ja | `test_fast_regel_gaar_foran_ki_og_vern` med regionflagg og postliste |
| Grunnlovsforslag behandles ikke av regelen (svar 2) | Ja | `test_fast_regel[Grunnlovsforslag om endring i § 96-False]`. Grunnlovsforslagene vurderes fortsatt av KI-en |
| Ingen KI-kall for relevans for representantforslag, men sammendrag som før | Ja | `test_fast_regel_gir_ingen_api_kall…` og `test_sammendrag_lages_fortsatt_for_representantforslag` |
| Regelen kan endres uten kodeendring | Ja | `felles.relevans.alltid_utelat` i `sources.yaml`, beskrevet i README |
| Ingen andre høringer flytter seg | Ja | Sammenligning før og etter på samme data: bare representantforslag endret status |

## G. Kodegjennomgang
- **Hardkoding:** ingen. Regelordet og begrunnelsen står i `sources.yaml`.
- **Kanttilfeller:**
  - Treffet er forankret til starten av tittelen. «Innstilling om representantforslag …»
    treffes derfor ikke (testet).
  - Tomme regler ignoreres.
- **Bufferen:** `hopp_over()` sletter et eldre KI-svar for høringen, slik at det ikke blir
  liggende igjen hvis regelen senere fjernes. Da vurderes høringen på nytt ved neste ukentlige
  oppdatering.
- **Ikke funnet:** død kode eller hemmeligheter.

## Kjente feil og begrensninger
- Viktige representantforslag skjules også, for eksempel stemmerett ved kommunevalg og
  datasenterstrategi. De er ett klikk unna under «Utelatte høringer», og søket finner dem.
- Regelen ser bare på starten av tittelen. Skriver Stortinget en dag tittelen annerledes, må
  regelen justeres.

## Forslag til senere sprinter
- Regler som alltid tar med en høring (det motsatte av `alltid_utelat`), og regler for enkelte
  høringer.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ og sjekk at ingen representantforslag
   står i listen.
2. Fold ut «Utelatte høringer» og sjekk at representantforslagene står der med «Utelatt:
   Representantforslag fra stortingsrepresentanter.».
