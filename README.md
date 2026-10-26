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
| Regjeringen.no | Hentes fra GRUs PC, fordi regjeringen.no avviser GitHub Actions (robotsjekk) |

Sprint 2: nettsiden er bygget.
Sprint 3: ukentlig kjøring mandag kl. 10, publisering på
https://shkorshavn.github.io/horingsoversikt-gru/, merket «Ny» og arkiv for utløpte høringer.
Sprint 4: direktorater og etater med prioritet 1, deduplisering og prioritet per departement.
Sprint 5: etater med prioritet 2 og 3, frist med bare måned og år, og måling av kjøretid.
Sprint 6: høringsparter, regionflagg («Regionen er høringspart») og tester ved hver push.
Sprint 7: Gjøvik kommunes postliste: «Mottatt av Gjøvik kommune» og høringsbrev uten treff.
Sprint 8: KI-sammendrag, delt visning (filtrene og listen ruller hver for seg) og ferdigstilling.

## Etatens side eller regjeringen.no

Spesifikasjonen ber om at valget dokumenteres per etat. Alle etatene under hentes fra egen
side, fordi høringene der i hovedsak **ikke** ligger på regjeringen.no (kontrollert 25.10.2026:
ingen av etatenes åpne høringer fantes blant de 52 på regjeringen.no). Når samme høring likevel
finnes begge steder, vises den én gang, med etaten som høringsinstans og lenken «Også på
regjeringen.no» (`horinger/dedup.py`).

| Etat | Hentes fra | Hvorfor |
|---|---|---|
| Miljødirektoratet | Egen høringsliste (JSON) | Forskrifter og tillatelser sendes ut av direktoratet selv. Olje og gass utelates |
| NVE | Egen side (forskrifter) og konsesjonsdatabasen | Konsesjonssaker finnes bare hos NVE. Konsesjoner filtreres på geografi |
| DSB | Egen RSS og detaljsider | Forskrifter og samtykkehøringer sendes ut av DSB |
| Helsedirektoratet | Egen høringsliste | Faglige retningslinjer og veiledere finnes ikke på regjeringen.no |
| Bufdir | Egen høringsliste | Retningslinjer og tilskuddsforskrifter fra Bufdir |
| Digdir | Egen høringsliste for standarder | IT-standarder og Referansekatalogen |
| DiBK | Egen høringsliste | TEK og SAK sendes ut av DiBK på oppdrag fra KDD |
| Nye Veier | Oppdateringer fra Innlandet | Planvarsler etter plan- og bygningsloven, ikke på regjeringen.no |
| Jernbanedirektoratet | Nyheter (WordPress-API) | Ingen høringsside. Utredninger på høring omtales i nyhetene |
| Bane NOR | Sitemap og prosjektsider | Planvarsler etter plan- og bygningsloven, ikke på regjeringen.no |
| Nkom | Egen høringsliste + detaljside | Frekvenser og digital infrastruktur |
| Landbruksdirektoratet | Egen høringsside («På høring nå») | Forskrifter og satser på landbruksfeltet |
| Riksantikvaren | Egen nyhetsliste | Fredningssaker og forskrifter. Fredning av enkeltsteder bare når det gjelder regionen |
| Nasjonalarkivet | Egen høringsside | Riksarkivarens forskrifter |
| DMP | Egen høringsliste + detaljside | Legemiddel- og utstyrsforskrifter. Prioritet 3 |
| Mattilsynet | Egen regelverkstabell | Bl.a. drikkevann og næringsmidler |
| Arbeidstilsynet | Egen høringsside | Arbeidsmiljøforskrifter |
| Politidirektoratet | Politiets dokumentliste | Retningslinjer fra POD |
| Skatteetaten | Egen høringsliste (JSON i siden) + detaljside | Bl.a. særavgifter og innkreving |
| SSB, Konkurransetilsynet, Innlandet politidistrikt | Egen side/sitemap/dokumentliste | Ingen fast høringsliste. Tas bare med når høringen gjelder kommunene eller regionen (Svein 25.10.2026) |
| FHI, Helsetilsynet, Kartverket, UDI, Datatilsynet | Ikke overvåket (`aktiv: false`) | Undersøkt på nytt 25.10.2026: publiserer bare egne høringssvar, har ingen høringssider (Kartverket), eller robots.txt svarer ikke (Datatilsynet). Høringene på feltene sendes av departementene og er med via regjeringen.no |
| DSA, Kulturdirektoratet, Sivilombudet | Ikke overvåket (`aktiv: false`) | Mest petroleumstillatelser (DSA), ingen høringsside, eller bare egne uttalelser |
| Udir, IMDi, NAV, DFØ | Ikke overvåket (`aktiv: false`) | Udir: datakilden er sperret i robots.txt (droppet av Svein 16.10.2026). IMDi og NAV: ingen høringsside, regelverket sendes ut av AID. DFØ: ingen samlet høringsside, regelverket sendes ut av NFD |

## Foreslått prioritet

Hver høring får foreslått prioritet høy, middels eller lav (`horinger/prioritet.py`):
utgangspunktet er kildens `prioritet`. På regjeringen.no har KDD, KD, HOD, AID, DFD og FIN høy,
og de andre departementene middels (`prioritet_instans`). En høring med middels eller lav
prioritet løftes til høy når tittel eller ingress nevner kommunene, fylkeskommunen, plan- og
bygningsloven, Innlandet eller et sted i regionen (`felles.prioritet_loft` og `geografi`).
Siden viser da grunnen, for eksempel «Foreslått prioritet: høy (gjelder kommunene)».

Er regionen høringspart (se under), løftes høringen til høy med grunnen «regionen er
høringspart».

## Høringsparter og regionflagg

Mange kilder lister hvem høringen er sendt til. Listen leses fra detaljsiden («Høringsinstanser»
o.l.), eller fra PDF-en det lenkes til, der robots.txt tillater det (`horinger/horingsparter.py`).
Hva som leses per kilde, står i `horingsparter` for kilden i `sources.yaml`:

- `detalj: true`: detaljsiden leses for åpne høringer.
- `pdf: true`: står listen i en PDF, leses den med `pypdf`.
- `merknad`: fast merknad når kilden ikke har lister, f.eks. «Åpen for alle» (Stortinget).

Listen lagres med høringen i `data/kilder/`, og brukes om igjen ved neste kjøring, så bare nye
høringer koster ekstra kall. Uten liste vises en merknad: «Åpen for alle» (alle kan svare),
«Ikke tilgjengelig» (listen finnes, men kan ikke leses, f.eks. sperret i robots.txt, med lenke)
eller «Ikke oppgitt».

**Regionflagg:** settes når en høringspart i listen er Gjøvik, Østre Toten, Vestre Toten,
Søndre Land, Nordre Land, Ringsaker eller Lillehammer kommune, Gjøvikregionen (IPR), regionrådene,
«alle kommuner», «alle fylkeskommuner», KS eller Innlandet fylkeskommune
(`felles.horingsparter.regionflagg`). Statsforvalteren gir ikke flagg, og KS gir ikke flagg
alene (`ikke_alene`), fordi KS står på nesten alle departementenes lister. Hver part vurderes for
seg, og bare listen brukes, ikke teksten ellers. Derfor gir verken «Gjøvik tingrett», «Sykehuset
Innlandet, Gjøvik» eller en postadresse i Lillehammer flagg.

**Kategorier:** partene telles i kategoriene i `felles.horingsparter.kategorier`, f.eks.
«Alle kommuner, Departementer og direktorater (17), Organisasjoner (12), Andre (17)».
Kategorier og flagg beregnes ved byggingen, så endringer i ordlistene slår inn uten ny henting.

## KI-sammendrag

Hver høring kan få et sammendrag på 1–2 setninger i klarspråk, laget med Anthropic API
(`horinger/sammendrag.py`, modell i `felles.sammendrag.modell`, nå `claude-sonnet-5-5`).

- **Grunnlag:** avsender, tittel, ingress og teksten fra høringssiden når den er lest
  (`detaljtekst`, høyst 6 000 tegn). Detaljteksten publiseres ikke.
- **Instruks:** bare opplysninger fra teksten, ingen frist og ingen vurdering. Er teksten for
  tynn, svarer modellen «MANGLER», og ingressen brukes.
- **Buffer:** `data/sammendrag.json`. Hver høring oppsummeres bare én gang, og på nytt bare hvis
  grunnlaget endres.
- **Når:** bare når publiseringen startes av den ukentlige oppdateringen eller PC-jobben for
  regjeringen.no, ikke ved kodeendringer.
- **På siden:** sammendraget vises merket «KI-sammendrag», og ingressen fra kilden ligger bak
  «Vis ingressen fra kilden». CSV har begge.
- **Uten nøkkel**, eller hvis API-et feiler, vises ingressen, og resten av oppdateringen går som
  normalt.

### Slik setter du API-nøkkelen

1. Gå til Anthropic Console (https://console.anthropic.com, kan sende deg videre til
   platform.claude.com) og logg inn med GRUs konto.
2. Under **Billing**: legg inn betaling, og sett en månedlig brukgrense (f.eks. 10 dollar).
   Forventet forbruk er under 1 dollar første gang og noen få kroner i uka etter det.
3. Under **API keys**: klikk **Create key**, gi den navnet `horingsoversikt-gru`, og kopier
   nøkkelen (begynner med `sk-ant-`). Den vises bare én gang.
4. I GitHub: repoet → **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret**. Navn: `ANTHROPIC_API_KEY`. Lim inn nøkkelen og lagre.
5. Nøkkelen skal aldri stå i koden, i `sources.yaml` eller i chatten. Lekker den, sletter du den
   i Anthropic Console og lager en ny.
6. Neste ukentlige oppdatering lager sammendragene. Vil du ikke vente: Actions → **Ukentlig
   oppdatering** → **Run workflow**.

## Gjøvik kommunes postliste

Den ukentlige oppdateringen sjekker også Gjøvik kommunes postliste (`horinger/postliste.py`).
Den bruker det samme endepunktet som postlistesiden selv
(`/api/presentation/v2/nye-innsyn/overview`). Postlistesiden hentes først, fordi endepunktet
krever informasjonskapslene derfra.

- **Utvalg:** inngående dokumenter de siste 14 dagene med et søkeord i tittelen
  (`felles.postliste.sokeord`). Titler som begynner med f.eks. «Høringssvar», «Høringsuttalelse»
  eller «Innspill», er svar til kommunen og tas ikke med (`utelat_ord`).
- **Personvern:** bare treff lagres. Avsender lagres bare når navnet ser ut som en virksomhet
  (`virksomhet_ord`). Ellers står det «Avsender ikke vist».
- **Kobling** (`horinger/kobling.py`): tittellikhet med rapidfuzz, avsender (forkortelser i
  `avsender_alias`, avkortede navn håndteres) og referansenumre. Poengsum 85 eller mer gir merket
  «Mottatt av Gjøvik kommune». 70–85 gir «Mulig treff». Tersklene er begrunnet i
  sprintrapport 7.
- **Lagring:** `data/postliste_treff.json`. Et merke blir stående etter at journalposten har
  falt ut av 14-dagersvinduet. Høringsbrev uten treff vises i 60 dager i seksjonen
  «Høringsbrev i postlista uten treff i oversikten».
- **Feil:** feiler postlista, fullføres resten. Forrige treff beholdes, og statusoversikten
  viser feilen.
- **Flere kommuner:** legg til en oppføring under `postlister:` i `sources.yaml`, med eget
  `dokumenttype_inngaaende` fra kommunens postliste (ACOS «nye-innsyn»).

## Slik oppdateres oversikten

```
Mandag kl. 10 (norsk tid)
├─ «Ukentlig oppdatering» (GitHub)  henter Stortinget, Vegvesenet, fylkeskommunen,
│                                   Statsforvalteren og direktoratene → data/kilder/
├─ «Regjeringen.no (GRUs PC)»       henter regjeringen.no → data/kilder/
│                                   (nye forsøk tirsdag–fredag hvis PC-en var av)
└─ «Publiser» (startes av begge)    bygger data/horinger.json, status.json og arkiv.json,
                                    og publiserer nettsiden på GitHub Pages
```

- Hver kilde har sin egen fil i `data/kilder/`. Feiler en kilde, beholdes høringene fra
  forrige vellykkede henting, og `sist_ok` viser når det var.
- `data/historikk.json` husker når hver høring ble sett første gang. Høringer som er sett
  første gang de siste sju dagene, merkes «Ny».
- Høringer med utløpt frist flyttes til `data/arkiv.json`.
- GitHub bruker UTC. Arbeidsflytene startes både 08.00 og 09.00 UTC, og `horinger.tidsjekk`
  slipper bare gjennom den som er kl. 10 norsk tid (sommer- og vintertid).
- Oppsett av GitHub Pages og PC-en: `docs/oppsett-pc.md`.

Alle arbeidsflytene kan også startes manuelt under **Actions → (arbeidsflyt) → Run workflow**.
«Ukentlig oppdatering» og «Regjeringen.no (GRUs PC)» har feltet «simuler feil», der du kan
skrive navnet på en kilde som skal late som den feiler. Det brukes bare til å teste
feilhåndteringen. Kjør arbeidsflyten på nytt uten feltet etterpå.

## Nettsiden

Siden består av `index.html` og mappen `side/` (stil, skript, logo), og leser
`data/horinger.json` og `data/status.json`, og `data/arkiv.json` når brukeren vil se utløpte
høringer (de siste 30 dagene). Den har ingen eksterne avhengigheter og ingen
sporing. Farger og logo er hentet fra Gjøvikregionens designsystem.

For å se siden lokalt må den åpnes via en webserver, fordi nettleseren ikke lar en lokal fil
lese JSON:

```bash
python -m http.server 8000
```

og gå til http://localhost:8000.

Filtrene lagres i adressen (f.eks. `?q=barnehage&niva=Regjeringen`), slik at en filtrert
visning kan deles som lenke. Dagens dato og «dager igjen» regnes i norsk tid.

Er oversikten ikke oppdatert på mer enn ti dager, viser siden en advarsel øverst.

Frist med bare måned og år («innen høringsfristen desember 2026») vises som «Høringsfrist:
desember 2026». Den sorteres som den 1. i måneden, men står som åpen ut måneden.

Hver høring har et flagg med foreslått prioritet (høy, middels eller lav), se «Foreslått
prioritet». Stortinget og regjeringen er egne temaer.

Er regionen høringspart, står «Regionen er høringspart: …» under tittelen. Under ingressen står
kategoriene for høringspartene, og «Vis alle høringsparter» folder ut hele listen. Filteret
«Bare høringer der regionen er høringspart» viser bare høringer med flagg (`?regionpart=1`).
Søket leter også i høringspartene. CSV og utskrift tar med flagg og kategorier, men ikke hele
listen.

Har Gjøvik kommune mottatt høringen, står «Mottatt av Gjøvik kommune 20. oktober 2026» med lenke
til journalposten (stiplet «Mulig treff …» når koblingen er usikker). Filteret «Bare høringer
mottatt av Gjøvik kommune» (`?mottatt=1`) viser bare sikre treff. Under listen står
høringsbrevene i postlista som ikke er koblet til noen høring, og statusoversikten viser når
postlista sist ble sjekket.

Listen kan sorteres etter frist (standard), nyeste først, foreslått prioritet, høringsinstans
eller tema. Valget lagres i adressen (`?sort=avsender`). Knappen «Skriv ut» skriver ut samme
utvalg og rekkefølge som på skjermen, i farger og med liten skrift og tette rader, med en linje
øverst som beskriver utvalget. Eksempel: `docs/sprinter/bilder/sprint-03-utskrift-eksempel.pdf`.

## Kjøre lokalt

Krever Python 3.11 eller nyere.

```bash
pip install -r requirements.txt
python -m horinger.kjor                        # alle aktive kilder, og bygg
python -m horinger.kjor --kilder Stortinget    # bare utvalgte kilder
python -m horinger.kjor --maskin github --bare-kilder   # som arbeidsflyten på GitHub
python -m horinger.bygg                        # bare bygg datafilene på nytt
```

Innhentingen skriver ett resultat per kilde til `data/kilder/`. Byggingen lager
`data/horinger.json` (åpne høringer, sortert på frist), `data/status.json` (status per kilde),
`data/arkiv.json` (utløpte høringer) og `data/historikk.json` (når hver høring ble sett
første gang). Datoer lagres i ISO 8601, og frister regnes i norsk tid. Filene skrives alltid
med LF som linjeskift, også på Windows.

`requirements-kjoring.txt` har det som trengs for å hente og bygge. `requirements.txt` har i
tillegg verktøyene for testing.

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

Arbeidsflyten **Tester** (`.github/workflows/tester.yml`) kjører ruff og hele testsuiten ved
hver push til `main`. Feiler den, blir kjøringen rød under Actions.

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
- `felles.horingsparter`: regionflagg og kategorier for høringsparter
- `kjoring` per kilde: `github` (standard) eller `pc` (hentes på GRUs PC)
- `horingsparter` per kilde: om detaljside og PDF leses for høringsparter

### Legge til en kilde

1. Lag `horinger/kilder/<navn>.py` med en klasse som arver `Kilde` og har metoden
   `hent()`, som returnerer en liste med `Hoering`.
2. Registrer klassen i `horinger/kilder/__init__.py`.
3. Sett `modul: <navn>` og `aktiv: true` i `sources.yaml`.
4. Lagre en kopi av kildesiden i `tests/fixtures/` og skriv tester i `tests/`.

## Høflighet mot kildene

Alle kall bruker User-Agent fra `sources.yaml`, venter minst 1,5 sekunder mellom kall til
samme nettsted (lenger hvis robots.txt krever det), og sjekker robots.txt før første kall.
Sperrede adresser hentes ikke. Det gjelder også PDF-er med høringsparter: Statens vegvesen
sperrer `*.pdf`, Skatteetaten `/contentassets` og Miljødirektoratet sin vedleggstjeneste
(`hss.miljodirektoratet.no`). For dem vises lenke til listen i stedet.
