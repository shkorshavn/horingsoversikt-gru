# Sprint 4 – Direktorater, prioritet 1

## Sammendrag
Ti nye kilder med prioritet 1 overvåkes nå automatisk: Miljødirektoratet, NVE, DSB,
Helsedirektoratet, Bufdir, Digdir, DiBK, Nye Veier, Jernbanedirektoratet og Bane NOR. Udir, IMDi,
NAV og DFØ står fortsatt som ikke overvåket, med begrunnelse. Siden viser nå 116 åpne høringer,
mot 100 før sprinten. Departementene har fått ulik foreslått prioritet: 24 av 52 høringer på
regjeringen.no har nå middels prioritet. Dedupliseringen er bygget og testet, men **i dagens data
fantes ingen høring både hos en etat og på regjeringen.no**. De to eksemplene i testene er derfor
laget ut fra ekte titler, ikke ekte par (se J). Alle andre punkter er bestått. Jeg anbefaler at
sprinten godkjennes, hvis du godtar forbeholdet om dedupliseringen.

## Hva som er bygget

**Nye kilder** (`horinger/kilder/`)

| Kilde | Fil | Metode |
|---|---|---|
| Miljødirektoratet | `miljodirektoratet.py` | JSON-endepunktet høringssiden bruker. Olje og gass utelates (`utelat_tema`) |
| NVE | `nve.py` | Forskriftsendringer: liste + detaljside for fristen. Konsesjonssaker: JSON, samme geografi som Vegvesenet. 20 s mellom kall |
| DSB | `dsb.py` | RSS + detaljside. Samtykkehøringer (farlig stoff) bare med geografisk treff |
| Helsedirektoratet, Bufdir, DiBK | `enkle_lister.py` | HTML-lister med «Høringsfrist» |
| Digdir | `digdir.py` | HTML. Mangler fristen årstall, hentes år og status fra detaljsiden |
| Nye Veier | `nye_veier.py` | Nyhetsstrøm for Innlandet. Søkeord og krav om frist på detaljsiden |
| Jernbanedirektoratet | `jernbanedirektoratet.py` | WordPress-API. Søkeord. Vag frist vises som tekst |
| Bane NOR | `bane_nor.py` | Sitemap → nye sider med søkeord → frist og geografi |

**Felles**
- `horinger/dedup.py`: Samme høring fra to kilder vises én gang. Etatens versjon beholdes, med
  «Også på regjeringen.no» og lenke.
- `horinger/prioritet.py`: Foreslått prioritet per høring. Grunnlaget er kildens prioritet,
  prioritet per departement (`prioritet_instans`) og løft til høy når høringen gjelder kommunene
  eller regionen. Siden viser grunnen.
- `horinger/sokeord.py`: Søkeordfilter for nyhetsstrømmene. Ordene står i `sources.yaml`.
- `horinger/datoer.py`: `frist_etter_ord`, `setning_med_frist` og `fristtekst` for detaljsider,
  der første dato på siden sjelden er fristen.
- `horinger/geografi.py`: Tettsteder i tillegg til kommuner (`geografi.steder`, f.eks. Moelv,
  Raufoss og Dokka).
- `horinger/nett.py`: UTF-8 når serveren ikke oppgir tegnsett (se G).
- `side/app.js`: Grunn for prioritet («høy (gjelder kommunene)») og «Også på …».
- `.github/workflows/testkjoring.yml`: Fast Ubuntu 24.04, låste versjoner av handlingene, og
  egne adresser til utforsking.

**Endrede filer:** `sources.yaml`, `horinger/bygg.py`, `horinger/kilder/__init__.py`,
`horinger/kilder/base.py`, `README.md`, `verktoy/hent_raa.py`.
**Nye tester:** `tests/test_sprint4_kilder.py` og `tests/test_dedup_prioritet.py`, pluss tillegg i
`test_bygg.py`, `test_geografi.py`, `test_nett.py` og `test_nettside.py`. 23 nye testkopier ligger i
`tests/fixtures/`.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **198 bestått, 0 feilet, 0 hoppet over** (31,3 s). 45 nye siden sprint 3 (153). I GitHub Actions: 198 bestått (testkjøring 25.10) |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «67 files already formatted». `actionlint`: ingen funn. Nye offentlige funksjoner har type hints og docstring på norsk |
| C. Ekte data | Bestått | Ukentlig oppdatering 25.10 (40211893556): se tabellen under. 116 åpne høringer publisert |
| D. Stikkprøver | Bestått | 9 høringer kontrollert felt for felt, og 0-tallene kontrollert mot kildene. Ingen avvik. Se tabell under |
| E. Tegn og datoer | Bestått | æ, ø og å er riktige i alle nye kilder, også nynorsk («Høyringsfrist», «Laga»). Datoformatene `dd.MM.yyyy`, «3. desember 2026», «12.november 2023» (uten mellomrom), ISO uten tidssone (NVE) og RSS-dato (DSB) er tolket og testet. Frister lagres i ISO 8601 |
| F. Feilhåndtering | Bestått | Simulert feil i Miljødirektoratet 25.10 (commit 17d588c): status «feil» med «SimulertFeil», de 11 høringene fra forrige henting ble beholdt, og de andre 14 kildene ble hentet og publisert. Ny kjøring rettet det (d19dc5e). Regjeringen.no feilet med 403 i testkjøringene i GitHub, og resten fullførte |
| G. Kodegjennomgang | Bestått etter retting | 6 funn rettet. Se avsnittet under |
| H. Høflighet | Bestått | Samme User-Agent og pause som før. robots.txt sjekkes for alle 10 nye nettsteder. Ingen nye sider er sperret. NVE: 20 s mellom kall, slik `Crawl-delay: 20` krever (loggen viser kl. 16:22:19 → 16:22:39 → 16:22:59). Hele kjøringen bruker 54 kall. Detaljsider hentes bare for nye oppslag (≤ 120 dager), og Bane NOR høyst 15 sider |
| I. Dokumentasjon | Bestått | README har nye avsnitt: «Etatens side eller regjeringen.no» (valget per etat, som spesifikasjonen krever) og «Foreslått prioritet». `sources.yaml` har merknad, søkeord og filtre per kilde, og kommentarer om prioritet og tettsteder |
| J. Akseptansekriterier | 2 av 3 oppfylt, 1 med forbehold | Se tabell under |

**Antall per kilde (C):**

| Kilde | Hentet | Åpne på siden | Forklaring |
|---|---|---|---|
| Miljødirektoratet | 11 | 11 | 18 åpne hos kilden, minus 7 om olje og gass |
| NVE | 3 | 1 | 2 forskriftshøringer med utløpt frist. 1 åpen med vag frist («desember 2026»). 0 konsesjoner i området (13 i landet, 2 i Trysil) |
| DSB | 1 | 1 | «Endringer i sivilforsvarsforskriften». Ingen samtykkehøringer i området |
| Helsedirektoratet | 2 | 2 | De to under «Ute på høring» |
| Bufdir | 0 | 0 | Ingen åpne. Den eneste høringen har frist 3. august 2026 og er under behandling |
| Digdir | 6 | 0 | 6 med frist 2017–2020. 3 uten årstall er «Ferdig behandla». Ingen åpne |
| DiBK | 28 | 0 | Alle avsluttet. Siste frist var 16.06.2026 |
| Nye Veier | 0 | 0 | Ingen oppslag med søkeord og frist de siste 120 dagene. Siste frist var 3. juli 2026 |
| Jernbanedirektoratet | 0 | 0 | Siste høring i nyhetene var 9. april 2026, eldre enn 120 dager |
| Bane NOR | 0 | 0 | 4 sider åpnet. Sørli (Stange) hadde frist 13.08.2026, utløpt. De andre ligger utenfor området |

### Funn i kodegjennomgangen (G)
Diffen mot godkjent sprint 3 (`git diff 67c8f74..HEAD`, 31 filer utenom data og testkopier) er
lest.

1. **Rettet – feil tegnsett ga 0 høringer hos Helsedirektoratet.** Serveren oppgir ikke tegnsett.
   Da tolket requests siden som ISO-8859-1, og «Ute på høring» ble ikke funnet. Nå brukes UTF-8 når
   tegnsettet mangler (test i `test_nett.py`). Neste kjøring ga 2 høringer.
2. **Rettet – Bane NOR i Moelv ble ikke regnet som i området.** Siden nevner Moelv, ikke Ringsaker.
   Geografien har nå også tettsteder (`geografi.steder`). Det gjelder Vegvesenet og NVE også.
3. **Rettet – falske treff hos Jernbanedirektoratet.** Artikler om stopp på Steinberg og Svingen
   traff på «høringsfrist» i omtale av Bane NORs ruteplanprosess. Søkeordene er strammet inn, og
   «tentativ ruteplan» utelukker.
4. **Rettet – vag frist hos NVE ga feil utdrag.** Setningen med fristen ble kuttet midt i en
   punktliste. Nå vises et utsnitt rundt fristordet, og datoer som «15. mars» deler ikke
   setningen.
5. **Rettet – testkjøringen i GitHub feilet på to måter.** `ubuntu-latest` gikk over til Ubuntu 26
   fra 19.10, og Playwright 1.56 lot seg ikke installere der. Arbeidsflyten bruker nå Ubuntu 24.04.
   I tillegg var kildetabellen 3 px for bred på mobil med skriften GitHub bruker (DejaVu Sans).
   Den feilen kom fra sprint 3, men ble ikke fanget fordi testkjøringen ikke ble kjørt etter de
   siste endringene i sprint 3. Rettet med orddeling i tabellen.
6. **Rettet – samme grense på 120 dager stod fire steder.** Den er nå én konstant i `base.py`.

Ingen hemmeligheter i koden. Søkeord, utelatte temaer, geografi og prioritet ligger i
`sources.yaml`. Ugyldige lenker (`javascript:`) i «Også på» filtreres bort, og det er testet.

## Stikkprøver
Kontrollert 25.10.2026 mot kildenes egne sider, hentet i GitHub Actions. Høringsparter hentes
ikke før sprint 6 og er ikke kontrollert.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Miljødirektoratet | Foreslår endring i biocidforskriften | tittel, instans, frist 25.10.2026, lenke | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/september-2026/foreslar-endring-i-biocidforskriften/ |
| Miljødirektoratet | CBAM-forskriften | tittel, frist 06.11.2026, lenke | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/september-2026/horing-av-forslag-til-forskrift-om-justering-av-karbonpris-ved-innforing-av-varer-til-eos-cbam-forskriften/ |
| Miljødirektoratet | Espoo – havneanlegg i Strömstad | tittel, frist 10.11.2026, lenke | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/september-2026/espoo---horing-av-soknad-om-a-etablere-havneanlegg-i-stromstad-kommune-sverige/ |
| Miljødirektoratet | Carbon Centric, Solør Bioenergi Kirkenær | tittel, frist 24.11.2026, lenke, tema «Innlandet» | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/oktober-2026/carbon-centric-soker-om-tillatelse-til-karbonfangstanlegg-ved-solor-bioenergi-kirkenar/ |
| Miljødirektoratet | Forurensningsforskriften kap. 10, krematorier | tittel, frist 31.12.2026, lenke | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/september-2026/horing-av-forslag-til-endringer-i-forurensningsforskriften-kapittel-10.-utslipp-fra-krematorier |
| Helsedirektoratet | Retningslinje for mat, måltider og ernæring | tittel, instans, frist 03.12.2026, lenke | Ingen | https://www.helsedirektoratet.no/horinger/retningslinje-for-mat-maltider-og-ernaering-i-helse-og-omsorgstjenesten |
| Helsedirektoratet | Breddekompetanse i legenes spesialistutdanning | tittel, frist 01.02.2027, lenke | Ingen | https://www.helsedirektoratet.no/horinger/breddekompetanse-i-legenes-spesialistutdanning-innspillsrunde |
| DSB | Endringer i sivilforsvarsforskriften | tittel, instans, frist 27.11.2026, lenke | Ingen | https://www.dsb.no/horinger/horinger/endringer-i-sivilforsvarsforskriften/ |
| NVE | Økodesignforskriften (eksterne strømkilder, tørketromler) | tittel, frist (vag: «innen høringsfristen desember 2026»), lenke | Ingen. Siden har ingen eksakt dato | https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/forslag-til-endringer-i-oekodesignforskriften-eksterne-stroemkilder-endring-av-hviletilstand-og-toerketromler-og-energimerkeforskriften-for-produkter-endring-av-toerketromler/ |
| Bufdir, DiBK, Digdir, Nye Veier, Jernbanedir., Bane NOR, NVE-konsesjoner | 0 åpne | Kontrollert mot listene. Se forklaringene i tabellen under C | Ingen | Adressene står i `sources.yaml` |

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Alle prioritet 1-kilder i avsnitt 2 som ikke kom med i sprint 1, er lagt til eller satt til `aktiv: false` med begrunnelse | Ja | 10 lagt til (tabellen over). Udir, IMDi, NAV og DFØ har `aktiv: false` med begrunnelse i `sources.yaml` og README. Stortinget, regjeringen.no, Vegvesenet, fylkeskommunen og Statsforvalteren kom med i sprint 1. Test: `test_alle_kilder_har_gyldig_niva` og `test_stortinget_og_regjeringen_er_egne_temaer` |
| Deduplisering mot regjeringen.no er testet med minst to konkrete eksempler | **Med forbehold** | `test_eksempel_1_dibk_og_regjeringen` og `test_eksempel_2_miljodirektoratet_og_regjeringen`, pluss fire tester av tilfeller som *ikke* skal slås sammen, og én test gjennom hele byggingen. **Forbehold:** Eksemplene bruker ekte titler fra DiBK og Miljødirektoratet, men versjonen på regjeringen.no er laget av meg, fordi det ikke fantes ekte par. Jeg sammenlignet alle åpne høringer fra de nye kildene med de 52 på regjeringen.no 25.10: ingen par, og ingen titler med likhet over 30 %. Jeg søkte også etter avsluttede par, uten funn |
| Stikkprøver er gjennomført for hver ny kilde | Ja | Se tabellen over. 9 høringer felt for felt, og 0-tallene kontrollert for de sju kildene uten åpne høringer i dag |

## Kjente feil og begrensninger
- **Dedupliseringen har ikke truffet et ekte par ennå** (se J). Den slår seg på først når en
  høring faktisk ligger begge steder.
- **Løftet til høy prioritet har ikke slått inn på ekte data.** Ingressene på regjeringen.no er
  korte (én setning) og nevner sjelden kommunene, selv når høringen gjelder dem. Eksempel:
  «Høring av forskrift om tilfluktssteder». Testene viser at regelen virker. En bedre vurdering
  krever høringspartene (om kommunene står på listen), og det kommer i sprint 6.
- **Alle etatene har prioritet 1**, så foreslått prioritet skiller bare mellom departementene
  ennå. Etater med prioritet 2 og 3 kommer i sprint 5.
- **Miljødirektoratet viser også tillatelser til enkeltbedrifter i andre deler av landet** og i
  Sverige (Espoo). Bare olje og gass er tatt bort, slik du bestemte.
- **Nyhetsbaserte kilder** (Nye Veier, Jernbanedir., Bane NOR) kan gå glipp av høringer som ikke
  bruker søkeordene, eller som ikke har frist på siden. Bane NOR ser bare på sider endret de siste
  120 dagene.
- **NVE-høringen med vag frist** vises uten «dager igjen» og sorteres sist (ditt svar 25.10). Den
  forsvinner 90 dager etter publisering hvis NVE ikke legger inn en dato.
- **Udokumenterte endepunkter** (Miljødir., NVE-konsesjoner) kan endres uten varsel. Feil vises i
  statustabellen, og forrige data beholdes.

## Forslag til senere sprinter
- Kjøre testene automatisk ved hver endring på `main`, ikke bare i testkjøringen. Da ville
  mobilfeilen fra sprint 3 (G5) blitt fanget straks.
- Hente høringsinstansene fra regjeringen.no (sprint 6). Da kan «gjelder kommunene» bygge på om
  kommunene faktisk er høringsparter.
- Temaet fra Miljødirektoratet (`subjects`) kan brukes til lavere prioritet for enkeltbedrifter
  utenfor regionen.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ og velg Avsender «Direktorater og
   etater». Der skal Miljødirektoratet, Helsedirektoratet, DSB og NVE være med.
2. Kryss av bare for «Middels» under «Foreslått prioritet». Da vises de 24 høringene fra
   departementer med middels prioritet (bl.a. JD, SD, NFD, KUD og FD). Er fordelingen riktig?
3. Se på NVE-høringen om økodesign nederst i listen: fristen står som tekst («desember 2026»).
4. Ta stilling til forbeholdet om dedupliseringen (J): Godtar du testene slik de er, eller vil du
   at jeg venter på et ekte par?
5. Mandag 26.10: Når kjøringen er grønn under Actions, skal kildetabellen vise «Hentet» for alle
   15 kildene.
