# Sprint 1 – Grunnmur og fem kjernekilder: plan

Status: Plan til godkjenning · 16. oktober 2026

## Mål
Bygge grunnmuren (prosjektstruktur, datamodell, `sources.yaml`, felles grensesnitt for
kildemoduler) og innhenting fra de fem kjernekildene, slik at `data/horinger.json` fylles med
ekte høringer. Ingen nettside, ingen planlagt kjøring og ingen KI-sammendrag – det hører til
senere sprinter.

## Avklaringer som ligger til grunn
Fra Svein 16.10.2026:
- Udir droppes (`aktiv: false`).
- Energidepartementet, Barne- og familiedepartementet og Utenriksdepartementet droppes. Siden
  regjeringen.no-listen inneholder alle departementer, filtreres disse tre bort i koden via en
  liste i `sources.yaml` (`ekskluder_departementer`), slik at de lett kan tas inn igjen.
- Kjøring skjer ukentlig (settes opp i sprint 3).
- Testing mot ekte data skjer via GitHub Actions, fordi miljøet mitt ikke når kildene.

## Hva som bygges

### Felles grunnmur
| Fil | Innhold |
|---|---|
| `pyproject.toml`, `requirements.txt` | Avhengigheter (requests, beautifulsoup4, pyyaml), oppsett for ruff og pytest |
| `sources.yaml` | Alle 39 kilder fra kartleggingen med `navn`, `kategori`, `prioritet`, `url`, `metode`, `aktiv`. Bare de fem kjernekildene er `aktiv: true` i denne sprinten; de øvrige aktiveres i sprint 4 og 5. Felles innstillinger: User-Agent, pause mellom kall, tidsavbrudd, `ekskluder_departementer` |
| `horinger/modell.py` | Datamodellen `Hoering`: `id` (stabil, ut fra lenken), `kilde`, `kategori`, `prioritet`, `instans`, `tittel`, `ingress`, `frist` (ISO-dato), `frist_tekst` (slik kilden skrev den), `publisert` (ISO-dato eller tom), `lenke`, `hentet` |
| `horinger/datoer.py` | Én felles datoparser for formatene i kartleggingen avsnitt 10 som kjernekildene bruker: `dd.MM.yyyy`, norsk tekstdato med og uten år, fritekst («Høringsfrist er 11. november 2026»), Stortingets `/Date(ms+0200)/` og ISO. Datoer uten år får «neste forekomst etter publiseringsdato» |
| `horinger/nett.py` | Felles HTTP-klient: User-Agent fra `sources.yaml`, pause mellom kall per domene, tidsavbrudd, kontroll mot robots.txt før første kall til et domene |
| `horinger/kilder/base.py` | Felles grensesnitt: hver kilde er en klasse med `hent() -> list[Hoering]` |
| `horinger/kjor.py` | Kjører alle aktive kilder, fanger feil per kilde, skriver `data/horinger.json` og `data/status.json` (antall, tidspunkt, feilmelding per kilde) |
| `README.md` | Kort innledning på norsk: hva prosjektet er, hvordan man kjører det, og hvordan en kilde legges til |

### De fem kildene
| Kilde | Metode | Viktige valg |
|---|---|---|
| Stortinget | JSON-API (`/eksport/horinger?format=json`) | Sesjons-ID beregnes ut fra dato (ny sesjon 1. oktober). Spør **både nåværende og neste sesjon**, fordi høringer for neste sesjon publiseres før sesjonsstart. Åpen/lukket avgjøres av fristen, ikke `horing_status`. Bruker `innspillsfrist` for skriftlige høringer og `anmodningsfrist_dato_tid` (påmelding) for muntlige |
| Regjeringen.no | HTML, bare `?page=N` (resten er sperret i robots.txt) | Blar til to hele sider uten «På høring». Alle feltene hentes fra listen, så detaljsidene trengs ikke i denne sprinten (høringsinstanser hentes i sprint 6). Dekoder HTML-entiteter. ED, BFD og UD filtreres bort |
| Statens vegvesen | HTML, én side | **Bare regelverkshøringene** (`/fag/publikasjoner/hoeringer/`). Se spørsmål 1 |
| Innlandet fylkeskommune | HTML | Frist hentes fra fritekst i ingressen. Publiseringsdato finnes ikke i kilden og blir stående tom |
| Statsforvalteren i Innlandet | HTML | Frist står uten år. Året hentes fra publiseringsdatoen (detaljsiden) eller adressen (`/2026/10/…`) |

### Tester
| Fil | Hva testes |
|---|---|
| `tests/test_datoer.py` | Alle datoformatene over, inkludert årsskifte for datoer uten år og tomme Stortinget-datoer |
| `tests/test_stortinget.py` | Sesjons-ID før og etter 1. oktober (f.eks. 30.09.2026 → 2025-2026, 01.10.2026 → 2026-2027), og tolkning av et lagret API-svar |
| `tests/test_regjeringen.py`, `test_vegvesen.py`, `test_innlandet_fk.py`, `test_statsforvalteren.py` | Tolkning av lagrede kopier av kildesidene, og at listen ikke er tom (fanger strukturendringer) |
| `tests/test_kjor.py` | At én kilde som feiler ikke stopper de andre, og at feilen havner i `status.json` |

De lagrede kildesidene (`tests/fixtures/`) hentes én gang via GitHub Actions, siden miljøet mitt
ikke når kildene.

### Testkjøring i GitHub Actions
`.github/workflows/testkjoring.yml`: en workflow som **bare kan startes manuelt**. Den kjører
testene og innhentingen mot ekte data, og lagrer `horinger.json`, `status.json` og de rå
kildesidene som nedlastbare vedlegg til kjøringen. Den committer ingenting og har ingen
tidsplan. Den ukentlige, automatiske kjøringen bygges i sprint 3. Se spørsmål 2.

## Arbeidsrekkefølge
1. Grunnmur: modell, datoparser med tester, HTTP-klient, `sources.yaml`, `kjor.py`.
2. Testkjøringsworkflow som henter de rå kildesidene. Dette tester samtidig risiko 12 (om
   kildene avviser GitHub Actions).
3. De fem kildemodulene, én om gangen, med tester mot de lagrede sidene.
4. Full testkjøring mot ekte data i Actions.
5. Kvalitetssikring etter sjekklisten og rapport.

## Kvalitetssikring
Hele sjekklisten A–J kjøres:
- **A/B:** `pytest -v`, `ruff check .` og `ruff format --check .` her og i Actions.
- **C:** Antall høringer per kilde fra testkjøringen i Actions.
- **D:** Minst fem høringer per kilde (eller alle, hvis færre) kontrolleres felt for felt mot
  kildens nettside: tittel, instans, frist og lenke. Høringsparter kontrolleres ikke, fordi de
  hentes først i sprint 6.
- **E:** Æ, ø og å i JSON, datoer i ISO 8601, frister regnet i Europe/Oslo.
- **F:** Simulert feil (feil URL og tidsavbrudd) i test og i én testkjøring.
- **G:** Gjennomgang av hele diffen.
- **H:** User-Agent, pauser og robots.txt dokumentert fra koden og loggen.
- **I:** README og kommentarer i `sources.yaml`.
- **J:** De fem akseptansekriteriene.

## Risikoer
1. **Kildene avviser GitHub Actions** (særlig vegvesen.no og regjeringen.no). Testes i steg 2.
   Hvis det skjer, stopper jeg og legger fram alternativer før jeg går videre.
2. **Frister i fritekst og uten år** (fylket, Statsforvalteren). Kan gi feil frist. Dekkes av
   egne tester og av stikkprøvene.
3. **Antall kall mot regjeringen.no:** 8–10 listesider per kjøring, med pause mellom. Akseptabelt.
4. **Stikkprøver på sider som avviser WebFetch:** gjøres i nettleseren din ved behov.

## Utenfor omfang
Nettside (sprint 2), planlagt kjøring, commit av data og GitHub Pages (sprint 3), øvrige
direktorater (sprint 4–5), høringsparter og regionflagg (sprint 6), postlista (sprint 7),
KI-sammendrag (sprint 8).

## Spørsmål til Svein før start
1. **Statens vegvesen:** Kilden har to deler: regelverkshøringer og høringer i vegprosjekter.
   Prosjekthøringene gjelder hele landet og må filtreres på Innlandet via detaljsidene
   (spørsmål 6 i kartleggingen). Forslag: bare regelverkshøringene i sprint 1, og
   prosjekthøringene, filtrert på Innlandet, i sprint 4. Greit?
2. **Testkjøringsworkflowen** er en liten forskuttering fra sprint 3, men trengs for å teste mot
   ekte data. Greit at den lages nå, så lenge den bare kan startes manuelt?
3. **User-Agent:** Skal den fortsatt inneholde svein-havar@gjovikregionen.no, eller en generell
   adresse som post@gjovikregionen.no? (Repoet er offentlig.)
