# Høringsoversikt for Gjøvikregionen

Henter aktuelle høringer fra Stortinget, regjeringen.no, direktorater, Innlandet
fylkeskommune og Statsforvalteren i Innlandet, slik at Gjøvikregionen Utvikling (GRU) og
eierkommunene ser hva de bør svare på.

Prosjektet bygges i sprinter. Se `SPESIFIKASJON.md`, `SPRINTSTATUS.md` og rapportene i
`docs/sprinter/`. Kildene er kartlagt i `docs/kildekartlegging.md`.

## Status
Sprint 1: Grunnmur og fem kjernekilder.

| Kilde | Status |
|---|---|
| Stortinget | Virker |
| Statens vegvesen (regelverk og vegprosjekter) | Virker |
| Innlandet fylkeskommune | Virker |
| Statsforvalteren i Innlandet | Virker |
| Regjeringen.no | Bygget, men regjeringen.no avviser GitHub Actions (robotsjekk). Se sprintrapport 1 |

Sprint 2: nettsiden er bygget. Publisering, ukentlig kjøring og flere kilder kommer i senere sprinter.

## Nettsiden

Siden består av `index.html` og mappen `side/` (stil, skript, logo), og leser
`data/horinger.json` og `data/status.json`. Den har ingen eksterne avhengigheter og ingen
sporing. Farger og logo er hentet fra Gjøvikregionens designsystem.

For å se siden lokalt må den åpnes via en webserver, fordi nettleseren ikke lar en lokal fil
lese JSON:

```bash
python -m http.server 8000
```

og gå til http://localhost:8000.

Filtrene lagres i adressen (f.eks. `?q=barnehage&niva=Regjeringen`), slik at en filtrert
visning kan deles som lenke. Dagens dato og «dager igjen» regnes i norsk tid.

`data/` inneholder foreløpig resultatet fra en testkjøring. Fra sprint 3 oppdateres filene av
den ukentlige kjøringen.

## Kjøre lokalt

Krever Python 3.11 eller nyere.

```bash
pip install -r requirements.txt
python -m horinger.kjor                        # alle aktive kilder
python -m horinger.kjor --kilder Stortinget    # bare utvalgte kilder
```

Resultatet skrives til `data/horinger.json` (åpne høringer, sortert på frist) og
`data/status.json` (status per kilde). Datoer lagres i ISO 8601, og frister regnes i
norsk tid.

## Tester og kodekvalitet

```bash
pytest -v
ruff check .
ruff format --check .
```

Testene bruker lagrede kopier av kildesidene i `tests/fixtures/`. Kopiene kan fornyes
med `python verktoy/hent_raa.py --ut raa/`.

Testene av nettsiden (`tests/test_nettside.py`) kjører siden i Chromium og sjekker
tilgjengelighet med axe-core. De krever:

```bash
python -m playwright install chromium
npm install --no-save axe-core@4.10.2   # eller sett AXE_STI til axe.min.js
```

## Testkjøring i GitHub Actions

Workflowen **Testkjøring** (`.github/workflows/testkjoring.yml`) startes manuelt under
Actions. Den kjører tester og innhenting mot ekte data, og legger resultat og logg på
grenen `testkjoring`. Hovedgrenen `main` endres ikke.

## Kilder og innstillinger

Alle kilder står i `sources.yaml`. En kilde hentes når den har `aktiv: true` og en
`modul` som finnes i `horinger/kilder/`. Der står også:

- `felles.user_agent`, `pause_sekunder` og `tidsavbrudd_sekunder` for alle kall
- `felles.ekskluder_departementer`: departementer på regjeringen.no som ikke tas med
- `felles.geografi`: kommunene og vegene som avgjør om en vegprosjekthøring er relevant

### Legge til en kilde

1. Lag `horinger/kilder/<navn>.py` med en klasse som arver `Kilde` og har metoden
   `hent()`, som returnerer en liste med `Hoering`.
2. Registrer klassen i `horinger/kilder/__init__.py`.
3. Sett `modul: <navn>` og `aktiv: true` i `sources.yaml`.
4. Lagre en kopi av kildesiden i `tests/fixtures/` og skriv tester i `tests/`.

## Høflighet mot kildene

Alle kall bruker User-Agent fra `sources.yaml`, venter minst 1,5 sekunder mellom kall til
samme nettsted (lenger hvis robots.txt krever det), og sjekker robots.txt før første kall.
Sperrede adresser hentes ikke.
