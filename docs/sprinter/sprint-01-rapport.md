# Sprint 1 – Grunnmur og fem kjernekilder

Rapportdato: 16. oktober 2026

## Sammendrag
Grunnmuren er på plass: datamodell, felles datoparser, geografisk filter, HTTP-klient med
robots.txt og pauser, felles kildegrensesnitt, kjøreskript og `sources.yaml` med alle 39
kilder. Alle fem kildemodulene er bygget og testet (80 tester), og testkjøringen i GitHub
Actions henter 37 åpne høringer fra fire av kildene. **Regjeringen.no avviser GitHub Actions
med en robotsjekk (Cloudflare)**, så den kilden gir ingen data fra GitHub ennå. Modulen er
bygget og testet mot en kopi av siden, og virker når tilgangen er løst. To akseptansekriterier
er derfor bare delvis oppfylt. Jeg anbefaler at sprinten godkjennes **med forbehold** om at
tilgangen til regjeringen.no løses som en egen sak (se «Kjente feil»), men det er Sveins
vurdering.

## Hva som er bygget

| Fil | Innhold |
|---|---|
| `horinger/modell.py` | Datamodellen `Hoering` med stabil id ut fra lenken, datoer i ISO 8601 |
| `horinger/datoer.py` | Felles tolkning av `dd.mm.åååå`, norsk tekstdato med og uten år, fristsetninger i fritekst, Stortingets `/Date(ms)/` og ISO |
| `horinger/geografi.py` | Geografisk filter etter reglene avklart 16.10 (kommuner, rv. 4, E6 med Eidsvoll/Ullensaker/Lillestrøm). Ignorerer postadresser |
| `horinger/nett.py` | HTTP-klient: User-Agent, pause per nettsted, tidsavbrudd, egen robots.txt-tolkning med `*` og `$` |
| `horinger/kilder/base.py`, `__init__.py` | Felles grensesnitt og register over kildemoduler |
| `horinger/kilder/stortinget.py` | Nåværende og neste sesjon. Skriftlige høringer: innspillsfrist. Muntlige: fristen for å søke om å delta. Kontrollhøringer: høringstittel fra programmet når det finnes |
| `horinger/kilder/regjeringen.py` | Blar til to hele sider uten åpne høringer. Filtrerer bort ED, BFD og UD |
| `horinger/kilder/vegvesen.py` | Regelverkshøringer (alle) og vegprosjekthøringer (geografisk filtrert, detaljsiden hentes bare ved behov) |
| `horinger/kilder/innlandet_fk.py` | Frist fra ingressen, ellers fra detaljsiden |
| `horinger/kilder/statsforvalteren.py` | Frist uten år, året fra adressen |
| `horinger/kjor.py` | Kjører kildene, fanger feil per kilde, fjerner utløpte og doble, skriver `data/horinger.json` og `data/status.json` |
| `sources.yaml` | 39 kilder (5 aktive), felles innstillinger, ekskluderte departementer, geografi |
| `.github/workflows/testkjoring.yml` | Manuell testkjøring mot ekte data. Resultat og logg legges på grenen `testkjoring` |
| `verktoy/hent_raa.py` | Henter rå kopier av kildesidene til testdata |
| `tests/` | 80 tester og lagrede kopier av kildesidene (`tests/fixtures/`) |
| `README.md`, `pyproject.toml`, `requirements.txt`, `.gitignore` | Oppsett og dokumentasjon |

**Avvik fra planen:**
- Testkjøringen legger resultatet på grenen `testkjoring` i tillegg til vedlegg, fordi vedlegg og
  logger fra Actions ikke kan lastes ned fra utviklingsmiljøet. Hovedgrenen røres ikke.
- Testdata for regjeringen.no er et utvalg på seks listepunkter hentet i nettleser, fordi
  siden ikke kunne hentes fra GitHub Actions.

## Kvalitetssikring

| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **80 bestått, 0 feilet, 0 hoppet over** (lokalt og i Actions-kjøring 38922149253). Alle moduler har egne tester |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «35 files already formatted». Offentlige funksjoner har type hints og docstring på norsk |
| C. Ekte data | Delvis | Kjøring 38922149253 (16.10): Stortinget 64 hentet / 29 åpne, Statens vegvesen 448 / 5, Innlandet fk 2 / 2, Statsforvalteren 1 / 1, **regjeringen.no 0 (HTTP 403)**. Totalt 37 åpne, 21 kall. Forklaring på tallene: Vegvesenets regelverksliste har hele historikken (448), bare 5 er åpne. Ingen av de 7 vegprosjekthøringene gjaldt regionen (se G). Stortinget har mange skriftlige høringer om statsbudsjettet nå |
| D. Stikkprøver | Delvis | 18 høringer kontrollert felt for felt (tabell under). To avvik funnet og rettet. Ett avvik kan ikke rettes fordi dataene mangler i API-et (kontrollhøring). Regjeringen.no er kontrollert mot testdata, ikke mot en kjøring |
| E. Tegn og datoer | Bestått | `horinger.json` fra kjøringen: æ, ø og å korrekte, ingen feilkodede tegn (`Ã¸`, `\u00..`). Alle frister i ISO 8601 (`2026-11-11`). Stortingets tider regnes om til norsk tid (test: 21:59 UTC → 23:59). Frister og «i dag» regnes i Europe/Oslo. Visning i norsk format kommer med nettsiden i sprint 2 |
| F. Feilhåndtering | Bestått | Ekte feil i hver kjøring: regjeringen.no svarte 403, resten fullførte, feilen ble logget (`ERROR Regjeringen.no feilet: 403 …`) og står i `status.json` med `"status": "feil"`. Tidsavbrudd er simulert i `test_en_feil_stopper_ikke_resten` |
| G. Kodegjennomgang | Bestått | Hele diffen er lest (33 filer, +2 617/−130 uten testdata). Funnet og rettet: (1) Vegvesenets postadresse «2605 Lillehammer» ga falske geografiske treff på E6 i Trøndelag og rv. 41 i Telemark; postadresser fjernes nå før vurdering. (2) Første versjon av adressefilteret kunne fjerne «2026 Gjøvik»; krever nå komma foran postnummeret. (3) Setningsdeling kuttet ved «3. desember». (4) BOM i robots.txt hos Statsforvalteren. (5) Feil frist for muntlige stortingshøringer (se D). Ingen hemmeligheter i koden. Gjenværende hardkodede verdier (`MAKS_SIDER = 20`, regjeringen.no) er dokumentert i modulen |
| H. Høflighet | Bestått | Logg fra kjøringen: robots.txt hentet for alle fem nettsteder før første kall, 1,5 sekunder mellom kall til samme nettsted (f.eks. 15:13:46,337 → 47,837 → 49,338), User-Agent `HoringsoversiktGRU/0.1 (+mailto:…)`. Regjeringen.no svarte 403 også på robots.txt; etter standarden (RFC 9309) betyr 4xx ingen regler, men vi bruker uansett bare `?page=`, som kartleggingen fant tillatt |
| I. Dokumentasjon | Bestått | `README.md` (kjøring, tester, testkjøring, kilder, ny kilde, høflighet) og kommentarer i `sources.yaml` |
| J. Akseptansekriterier | Delvis | 3 av 5 oppfylt, 2 delvis (tabell under) |

## Stikkprøver

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Stortinget | 10005914 Justiskomiteen, ekstremistiske digitale nettverk | tittel, instans, frist 20.10 kl. 23:59, lenke | Ingen | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005914 |
| Stortinget | 10005983 Samferdselskomiteen, bompenger E39 | tittel, instans, frist 20.10 kl. 23:59, lenke | Ingen | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005983 |
| Stortinget | 10005964 KOMMFORV, statsbudsjettet | tittel, instans, frist 22.10 kl. 12:00, lenke | Ingen | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005964 |
| Stortinget | 10005977 Næringskomiteen, god handelsskikk (muntlig) | tittel, instans, frist, lenke | **Rettet:** frist var 28.10 (API-ets innspillsfrist), siden viser fristen for å søke 26.10 kl. 13:00 | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005977 |
| Stortinget | 10005957 Næringskomiteen, statsbudsjettet (muntlig) | frist | **Rettet:** sto som åpen til 18.10, men søknadsfristen var 12.10. Tas nå ikke med | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005957 |
| Stortinget | 10005976 Kontroll- og konstitusjonskomiteen | tittel, instans, frist, lenke | **Ikke rettet:** siden viser høringstittel «Oppfølging og kontroll av rammeavtaler …», vi viser sakstittelen. Høringstittelen finnes ikke i API-et før programmet publiseres; koden henter den da automatisk | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005976 |
| Vegvesen | Hest i trafikken | tittel, instans, frist 07.12.2026, lenke | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing-om-hest-i-trafikken---forslag-til-endringer-i-trafikkregler-og-forskrift-om-bruk-av-kjoretoy/ |
| Vegvesen | Personlige kjennemerker | tittel, instans, frist 15.12.2026, lenke | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing-om-personlige-kjennemerker-26-132234-8/ |
| Vegvesen | Førerkortforskriften vedlegg 1 | tittel, instans, frist 01.01.2027, lenke | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing--forslag-til-endringer-i-forerkortforskriften-vedlegg-1-26-80489-6/ |
| Vegvesen | Ny forvaltningslov | tittel, instans, frist 06.01.2027, lenke | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing-om-forskriftsendringer-knyttet-til-gjennomforing-av-ny-forvaltningslov/ |
| Vegvesen | Endring i vegtrafikkloven | tittel, instans, frist 09.01.2027, lenke | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing--endring-i-vegtrafikkloven-20-38820/ |
| Innlandet fk | Planprogram nettinfrastruktur | tittel, instans, frist 11.11.2026, lenke | Ingen | https://innlandetfylke.no/politikk/horinger/planprogram-pa-horing-regional-plan-for-nettinfrastrukturen-for-energi.81920.aspx |
| Innlandet fk | Fv. 213 Skog bru | tittel, instans, frist 13.11.2026, lenke | Ingen | https://innlandetfylke.no/politikk/horinger/oppstart-av-reguleringsplanarbeid-for-fv-213-skog-bru-i-ringsaker-kommune.82328.aspx |
| Statsforvalteren | Frivillig vern av skog – syv områder | tittel, instans, frist 16.10.2026, lenke | Ingen | https://www.statsforvalteren.no/nb/innlandet/horinger/2026/10/oppstart-av-verneprosess---frivillig-vern-av-skog---syv-omrader/ |
| Regjeringen.no (testdata) | Klagenemd i finanssektoren (FIN) | tittel, instans, frist 04.01.2027, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-om-pliktig-tilslutning-til-godkjent-klagenemd-i-finanssektoren/id3178382/ |
| Regjeringen.no (testdata) | Petroleumsskattelova (FIN, nynorsk) | tittel, instans, frist 30.11.2026, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/hoyring-teknisk-revisjon-av-forskriftene-til-petroleumsskattelova/id3178316/ |
| Regjeringen.no (testdata) | Smågruppeundervisning (KD) | tittel, instans, frist 07.01.2027, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-opplaringsloven-og-privatskolen-smagruppeundervisning-og-leksehjelp/id3170886/ |
| Regjeringen.no (testdata) | Nettleie og fjernvarme (ED, to stk.) | at de filtreres bort | Ingen | https://www.regjeringen.no/no/dokument/hoyringar/id1763/ |

Innlandet fylkeskommune og Statsforvalteren hadde bare to og én åpne høringer, så alle er
kontrollert. Vegvesenets prosjekthøringer: ingen av de sju gjaldt regionen, og alle sju er
kontrollert mot filteret (se G). Høringsparter er ikke kontrollert, fordi de hentes i sprint 6.

## Akseptansekriterier

| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Prosjektstruktur, felles datamodell, `sources.yaml` og felles grensesnitt for kildemoduler er på plass | Ja | `horinger/`, `sources.yaml`, `horinger/kilder/base.py` |
| Alle fem kildene gir høringer i `data/horinger.json` med feltene i avsnitt 3 (unntatt sammendrag og høringsparter) | **Delvis** | Fire kilder gir høringer med alle feltene. Regjeringen.no gir ingen fra GitHub Actions (HTTP 403). Publiseringsdato mangler i kilden for fylkeskommunen og i listen for Statsforvalteren og Vegvesenets regelverkshøringer |
| Stortingets sesjons-ID beregnes dynamisk og er testet for dato før og etter 1. oktober | Ja | `test_sesjon_for` (30.09.2026 → 2025-2026, 01.10.2026 → 2026-2027 m.fl.) og `test_spor_naa_og_neste_sesjon` |
| Stikkprøver viser null avvik i tittel, avsender, frist og lenke | **Delvis** | To avvik funnet og rettet. Ett gjenstår: tittelen på kontrollhøring 10005976, som ikke finnes i API-et |
| Hver kilde har minst én test | Ja | `test_stortinget.py` (13), `test_regjeringen.py` (4), `test_vegvesen.py` (5), `test_innlandet_fk.py` (2), `test_statsforvalteren.py` (3) |

## Kjente feil og begrensninger
1. **Regjeringen.no avviser GitHub Actions** (Cloudflare-robotsjekk, også på robots.txt). Jeg
   har ikke forsøkt å komme forbi sjekken. Alternativene er lagt fram for Svein: be DSS om
   tilgang, eller kjøre jobben fra en maskin hos GRU. Modulen er klar og testet mot testdata.
2. **Kontrollhøringer på Stortinget** kan vise sakstittelen i stedet for høringstittelen til
   programmet er publisert (gjelder 2 av 64 høringer nå).
3. **Publiseringsdato** mangler for fylkeskommunen (finnes ikke i kilden), og for
   Statsforvalteren og Vegvesenets regelverkshøringer (finnes bare på detaljsiden, som ikke
   hentes for å holde antall kall nede).
4. **Statsforvalteren:** Siden har filtre og paginering. Innhentingen leser bare første side
   med standardvisning. Det holder med dagens volum (1 høring), men er ikke testet med flere
   sider.
5. **Testdata for regjeringen.no** er et utvalg (6 punkter) hentet i nettleser, ikke en full
   side hentet av programmet.

## Forslag til senere sprinter
- **Egen sak, før sprint 3:** Løse tilgangen til regjeringen.no (DSS eller egen maskin). Uten
  dette mangler den viktigste kilden i den ukentlige kjøringen.
- **Sprint 3:** Den ukentlige workflowen kan bygges på testkjøringen. Grenen `testkjoring` kan
  da fjernes eller beholdes til feilsøking.
- **Sprint 4:** Geografifilteret og postadresseregelen kan gjenbrukes for NVE, Bane NOR og Nye
  Veier.
- **Sprint 6:** Detaljsidene til Statsforvalteren og Vegvesenet hentes uansett for
  høringsparter. Publiseringsdatoen kan hentes samtidig.

## Hva Svein bør sjekke selv
1. Se resultatet fra siste testkjøring:
   https://github.com/shkorshavn/horingsoversikt-gru/blob/testkjoring/ut/horinger.json
   og statusen per kilde:
   https://github.com/shkorshavn/horingsoversikt-gru/blob/testkjoring/ut/status.json
2. Velg et par høringer du kjenner, og se at frist og lenke stemmer.
3. Ta stilling til regjeringen.no (DSS eller egen maskin hos GRU), og om sprinten kan
   godkjennes med det som en egen sak.
4. Se gjennom geografilisten i `sources.yaml` (`felles.geografi`) en gang til nå som den er i
   bruk.
5. Godkjenn ved å skrive «Sprint 1: JA <dato>» her i chatten, eller be om endringer.
