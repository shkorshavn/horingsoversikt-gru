# Sprint 3 – Automatisering og publisering (v2)

**Endringer fra v1**, bestilt av Svein 25.10.2026 (commit 17e4785):
1. Stortinget og regjeringen er egne temaer. Temaet «Regjeringen og Stortinget» er delt i
   **«Stortinget»** og **«Regjeringen og departementene»**, både i filteret og på hver høring.
2. Hver høring har et flagg: **«Foreslått prioritet: høy / middels / lav»**. Flagget har egne farger:
   burgunder for høy, rosa for middels og omriss for lav. Det er ikke oransje, fordi oransje betyr kort
   frist. Filteret har nytt navn: «Foreslått prioritet».
3. Byggingen tar nå tema, avsender og prioritet fra gjeldende `sources.yaml`. Endringer der slår inn
   ved neste publisering, uten ny henting. Slik ble endring 1 synlig med en gang.

Hele sjekklisten er kjørt på nytt. Tall og bevis som er endret siden v1, er oppdatert under.

## Sammendrag
Høringsoversikten oppdateres nå automatisk hver mandag kl. 10 og publiseres på
https://shkorshavn.github.io/horingsoversikt-gru/. Regjeringen.no hentes fra GRUs PC og ga 52 høringer
ved første kjøring 23.10.2026. Siden viser nå 101 åpne høringer fra alle fem kildene. Den ukentlige
kjøringen gikk av seg selv mandag 19.10. En simulert kildefeil og en ekte nettverksfeil hos Vegvesenet
ble begge håndtert: resten av kjøringen fullførte, og siden viste feilen. Fire feil ble funnet og rettet
under arbeidet. Alle punktene i sjekklisten er bestått, og sprinten anbefales godkjent. To ting er ikke
observert i praksis ennå: en kjøring i vintertid (første er mandag 26.10) og en PC-kjøring som starter
av seg selv fra tidsplanen. Begge er dekket av tester.

## Hva som er bygget

**Innhenting og bygging**
- Hver kilde lagres i sin egen fil i `data/kilder/`. Feiler en kilde, beholdes høringene fra forrige
  vellykkede henting, og `sist_ok` viser når den var.
- `python -m horinger.kjor --maskin github|pc` henter bare kildene som hører til maskinen.
  Regjeringen.no har `kjoring: pc` i `sources.yaml`.
- `horinger/bygg.py` slår sammen kildefilene til `horinger.json`, `status.json`, `arkiv.json` og
  `historikk.json`. Høringer som er sett første gang de siste sju dagene, merkes «Ny». Utløpte
  høringer flyttes til arkivet, også når kilden har fjernet dem.
- `horinger/tidsjekk.py` slipper bare gjennom kjøringen som er kl. 10 norsk tid, både sommer og
  vinter. På PC-en hoppes ekstraforsøkene tirsdag–fredag over hvis regjeringen.no er hentet de siste
  seks dagene.

**Arbeidsflyter**
- *Ukentlig oppdatering* (GitHub): mandag 08.00 og 09.00 UTC, og manuelt med valget «simuler feil».
- *Regjeringen.no (GRUs PC)*: mandag–fredag 08.00 og 09.00 UTC, og manuelt.
- *Publiser*: bygger datafilene og publiserer på GitHub Pages. Startes av begge innhentingene og når
  nettsiden endres.

**Nettsiden**
- Merket «Ny» ved tittelen, og antall nye i overskriften over listen.
- Bryteren «Vis høringer med utløpt frist (siste 30 dager)». Arkivet lastes bare når bryteren slås på.
- Advarsel øverst når oversikten er eldre enn ti dager.
- Kildetabellen har fire kolonner: Kilde, Status, Sist hentet og Åpne høringer. Statusene er Hentet,
  Feil (med data fra forrige henting), Utdatert og Ikke hentet ennå. På mobil flyttes «Sist hentet»
  inn i statuskolonnen.

**Nye filer:** `horinger/bygg.py`, `horinger/lager.py`, `horinger/filer.py`, `horinger/tidsjekk.py`,
`verktoy/git_lagre.py`, `verktoy/start_publisering.py`, `.github/workflows/oppdatering.yml`,
`.github/workflows/regjeringen.yml`, `.github/workflows/publiser.yml`, `.github/actionlint.yaml`,
`.gitattributes`, `requirements-kjoring.txt`, `docs/oppsett-pc.md`, `tests/test_bygg.py`,
`tests/test_lager.py`, `tests/test_tidsjekk.py`, `data/kilder/*.json`, `data/arkiv.json`,
`data/historikk.json`.

**Endrede filer:** `horinger/kjor.py`, `horinger/nett.py`, `sources.yaml`, `requirements.txt`,
`index.html`, `side/app.js`, `side/stil.css`, `README.md`, `tests/test_kjor.py`, `tests/test_nett.py`,
`tests/test_nettside.py`.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v` (v2): **147 bestått, 0 feilet, 0 hoppet over** (23,9 s). 36 flere enn i sprint 2 (111): bygg 12, tidsjekk 8, lager 4, nettside 9, nett 1 og kjør 2 (4 nye, 2 utgåtte fjernet). Nye i v2: `test_foreslatt_prioritet_vises`, `test_tema_avsender_og_prioritet_fra_gjeldende_konfig` og `test_stortinget_og_regjeringen_er_egne_temaer` |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «51 files already formatted» (v2). `actionlint`: ingen funn. Offentlige funksjoner har type hints og docstring på norsk |
| C. Ekte data | Bestått | Kjøringer 23.10.2026: Stortinget 38, Regjeringen.no 52 (fra PC-en), Vegvesenet 7, Innlandet fylkeskommune 4, Statsforvalteren 0. Det gir 101 åpne høringer og 52 i arkivet. **v2:** ingen ny henting (ingen kilde er endret). Publiseringen 25.10 (40180083417) bygget på nytt: 100 åpne, 53 i arkivet. Én høring gikk ut 23.10. Temaer etter endringen: Regjeringen og departementene 52, Stortinget 37, Transport 7, Regionale ledd 4. Forklaring på tallene under tabellen |
| D. Stikkprøver | Bestått | 5 av 5 høringer fra regjeringen.no stemmer felt for felt. Se tabell under. v2 endrer ikke hentingen, så stikkprøvene gjelder fortsatt |
| E. Tegn og datoer | Bestått | v2: «Foreslått prioritet: høy» vises med ø i testen og på skjermbildene. æ, ø og å er riktige i JSON og på den publiserte siden («Høringer – Gjøvikregionen», «Høyring … petroleumsskattelova»). Alle filer skrives i UTF-8 med LF, også på Windows (`.gitattributes` og test). Tidspunkt lagres i ISO 8601 med tidssone, for eksempel `2026-10-23T11:33:35+02:00`. Siden viser «Oppdatert 23. oktober 2026 kl. 11.37». Tidssjekken er testet både sommer og vinter, også overgangen 25.10.2026 |
| F. Feilhåndtering | Bestått | **Simulert feil:** manuell kjøring 23.10 med «Innlandet fylkeskommune». De fire andre kildene ble hentet. Status ble «feil» med «SimulertFeil», og de 2 høringene fra 19.10 ble beholdt (commit c0f83fd). Ny kjøring uten simulering rettet det (439a911). **Ekte feil:** i samme kjøring var Vegvesenet utilgjengelig fra GitHub (Errno 101). Siden viste høringene fra 19.10 med feilforklaring |
| G. Kodegjennomgang | Bestått etter retting | 4 feil funnet og rettet. Se avsnittet under. v2-diffen (`git diff 923f67f..17e4785`, 9 filer) er lest. Prioritetsflagget fikk ny farge etter første skjermbilde, fordi oransje kunne forveksles med kort frist |
| H. Høflighet | Bestått | PC-en bruker samme kode som GitHub: samme User-Agent, 1,5 s pause per nettsted og sjekk av robots.txt før første kall. Regjeringen.no hentes én gang i uken. Ekstraforsøkene hoppes over når kilden er fersk. Cloudflare-sjekken er ikke omgått: PC-en er en vanlig maskin i GRUs nett. Hvis robots.txt ikke kan hentes, hentes ingenting fra nettstedet |
| I. Dokumentasjon | Bestått | README har nytt avsnitt «Slik oppdateres oversikten», og i v2 avsnitt om prioritetsflagget og de to temaene. `sources.yaml` har listen over temaer med «Stortinget» og «Regjeringen og departementene». `docs/oppsett-pc.md` beskriver GitHub og PC-en trinn for trinn. `sources.yaml` dokumenterer feltet `kjoring`. Arbeidsflytene er kommentert |
| J. Akseptansekriterier | 4 av 4 oppfylt | Se tabell under |

**Om tallene i C:**
- **Regjeringen.no 52:** alle høringer med status «På høring», minus Energidepartementet, BFD og UD.
  To høringer Gjøvik kommune har mottatt, og som ikke ble funnet i sprint 1, er nå med: AID
  (integreringsloven, frist 14.12.2026) og HOD (rekvirering av vaksiner, frist 23.12.2026).
- **Vegvesenet 7 åpne:** av 448 høringer i listene. Resten er utløpte regelverkshøringer helt tilbake
  til 2008, eller prosjekter utenfor området.
- **Statsforvalteren 0:** siden har ingen åpne høringer nå. Det er det samme som i sprint 1.
- **71 nye:** regjeringen.no ble hentet for første gang denne uken. Derfor er alle de 52 høringene
  derfra merket «Ny». Det retter seg fra neste uke.

### Funn i kodegjennomgangen (G)
Jeg leste diffen mot godkjent sprint 2 (`git diff 426551a..HEAD`, 33 filer, utenom data).

1. **Rettet – arkivet fylte seg med gamle høringer.** Vegvesenets regelverksliste går tilbake til 2008.
   Første bygging la 478 utløpte høringer i arkivet. Nå holdes høringer med frist mer enn 30 dager
   før oversikten startet, utenfor arkivet og historikken. Det er testet. Etter rettingen hadde
   arkivet 46 høringer og historikken 82. Nå er tallene 52 og 153 (19c67c7).
2. **Rettet – PowerShell var sperret på PC-en.** Første kjøring på PC-en feilet i «Installer
   avhengigheter», fordi Windows stopper PowerShell-skript (execution policy). Arbeidsflyten bruker
   nå `cmd`, så sikkerhetsinnstillingen på PC-en trenger ikke endres (258d0bc).
3. **Rettet – nettverksfeil ble vist som robots-sperre.** Da Vegvesenet ikke svarte, sto det
   «Nettstedet tillater ikke automatisk innhenting» på siden. Det var feil. Nettverksfeil ved henting
   av robots.txt er nå en egen feiltype, og siden viser «Fikk ikke kontakt med nettstedet». Det er
   testet (7506df5).
4. **Rettet – PC-jobbene avbrøt hverandre i køen.** Køen for arbeidsflyten var satt opp slik at en ny
   jobb erstattet en ventende jobb. Når PC-en var av, avbrøt 09.00-jobben 08.00-jobben. Om sommeren er
   08.00 UTC kl. 10 norsk tid, så regjeringen.no ville da aldri blitt hentet. Sett i kjøringene
   20.–22.10. Rettet ved å fjerne køgruppen. PC-en kjører uansett én jobb om gangen (0441e92).

Ellers ingen hemmeligheter i koden. Nøkkelen til publisering er den kortvarige `GITHUB_TOKEN` som
GitHub gir hver jobb. Inndata fra «simuler feil» går via miljøvariabel, ikke rett inn i kommandoen.
Disse verdiene står i koden og ikke i konfigurasjonen: «Ny» i 7 dager, «Utdatert» etter 8 dager, arkiv
i 30 dager på siden og advarsel etter 10 dager. De står som navngitte konstanter øverst i `bygg.py` og
`app.js`. Jeg har latt dem stå der, siden de henger sammen med teksten på siden.

## Stikkprøver
Kontrollert 23.10.2026 mot regjeringen.no i nettleseren. Høringsparter hentes ikke før sprint 6 og er
ikke kontrollert.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Regjeringen.no | Lotteritilsynets utredning om pengespill-lignende elementer i dataspill (KUD) | tittel, instans, frist 12.01.2027, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-av-lotteritilsynets-utredning-om-regulering-av-pengespill-lignende-elementer-i-dataspill/id3176704/ |
| Regjeringen.no | Særordning for fordrevne med kollektiv beskyttelse (AID) | tittel, instans, frist 05.11.2026, lenke | Ingen. Fristen er forlenget fra 30.10, og vi viser den nye | https://www.regjeringen.no/no/dokumenter/horing-forslag-til-en-sarordning-om-overgang-til-annen-oppholdsstatus-pa-grunnlag-av-arbeid-for-fordrevne-fra-ukraina-med-midlertidig-kollektiv-beskyttelse/id3172986/ |
| Regjeringen.no | NOU 2026: 10 Fellesskolen (KD) | tittel, instans, frist 21.12.2026, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-nou-2026-10-fellesskolen-barebjelken-i-framtidens-samfunn/id3171614/ |
| Regjeringen.no | Pliktig tilslutning til klagenemd i finanssektoren (FIN) | tittel, instans, frist 04.01.2027, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-om-pliktig-tilslutning-til-godkjent-klagenemd-i-finanssektoren/id3178382/ |
| Regjeringen.no | Regionale ruteflyginger i Nord-Norge (SD) | tittel, instans, frist 15.12.2026, lenke | Ingen | https://www.regjeringen.no/no/dokumenter/horing-ny-konkurranse-om-regionale-ruteflyginger-i-nord-norge-fra-1.-november-2028/id3172071/ |

Ingen andre kilder er endret i denne sprinten. Vegvesenet, Stortinget, fylkeskommunen og
Statsforvalteren ble kontrollert i sprint 1.

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Arbeidsflyt med ukentlig cron og `workflow_dispatch`, riktig norsk tid sommer og vinter | Ja | `oppdatering.yml` og `regjeringen.yml` har cron 08.00 og 09.00 UTC og `workflow_dispatch`. 8 tester av tidssjekken: sommer, vinter, overgangen 25./26.10, forsinket kjøring og manuell kjøring. **I praksis mandag 19.10 (sommertid):** jobben fra 08.00 UTC hentet kildene (kjøring 39274979554), og jobben fra 09.00 UTC hoppet over (39282983204, «Hent kildene: skipped»). Vintertid er ikke sett i praksis ennå. Første gang er 26.10 |
| Manuell kjøring i GitHub har oppdatert data og nettsiden på Pages | Ja | 23.10: *Regjeringen.no (GRUs PC)* (39932699470) og *Ukentlig oppdatering* ga «Data: … hentet» og «Data: oversikten bygget». *Publiser* ble grønn (39932779744 m.fl.). Den publiserte siden viser «Oppdatert 23. oktober 2026 kl. 11.37» og 101 høringer |
| Simulert kildefeil: resten fullføres og feilen vises på siden | Ja | Kjøring med «Innlandet fylkeskommune», se F. Status «feil», høringene fra 19.10 beholdt, de andre kildene hentet og publisert. Tabellen på siden viser Feil, forklaring og «Viser høringene fra …» (testet i `test_status_feil_med_tidligere_data`) |
| «Ny»-merking og flytting til `data/arkiv.json` virker og er testet | Ja | `test_bygg.py`: ny i sju dager, ikke ny ved første kjøring, utløpt flyttes til arkivet, fjernet fra kilden etter fristen flyttes til arkivet, forlenget frist tas ut av arkivet. På siden: `test_ny_merke`, `test_utlopte_kan_vises` og `test_arkiv_hentes_bare_ved_behov`. I praksis: 71 nye og 52 i arkivet 23.10 |

## Kjente feil og begrensninger
- **GitHub starter planlagte kjøringer for sent.** Mandag 19.10 startet jobben fra 08.00 UTC først
  kl. 17.06 norsk tid. Tidssjekken håndterer det, så hentingen ble riktig. Men oppdateringen kom
  sju timer etter planen. GitHub garanterer ikke tidspunktet for planlagte kjøringer.
- **PC-en må være på.** Er den av hele uken, viser siden høringene fra forrige henting av regjeringen.no.
  Statustabellen viser da «Utdatert» og «Sist hentet». En jobb som venter i kø hos GitHub, forsvinner
  etter 24 timer. Neste dags jobb tar over.
- **Første planlagte kjøring på PC-en er ikke sett ennå.** De manuelle kjøringene virker. Køproblemet
  i G4 er rettet, men rettingen er bare kontrollert med `actionlint`.
- **71 høringer er merket «Ny» denne uken.** Grunnen er at regjeringen.no ble hentet for første gang
  (se C).
- **Siden henter ikke selv.** Hentingen skjer bare i arbeidsflytene.
- **Data-commits.** Hver kjøring lager to til tre commits fra «github-actions[bot]» på `main`.
- **Alle høringer har foreslått prioritet «høy» i dag.** Prioriteten følger kilden, og alle fem
  aktive kilder har prioritet 1. Flagget skiller ikke mellom høringer før direktoratene med
  prioritet 2 og 3 kommer inn (sprint 4–5) og regionflagget kommer (sprint 6).
- **Temaet for regjeringen.no er avsenderen, ikke saksfeltet.** En skolehøring fra KD står under
  «Regjeringen og departementene», ikke under «Oppvekst». Regjeringen.no har egne temaer på hver
  høringsside (f.eks. «Skole og videregående opplæring»). Se forslag under.
- **v2 er ikke sett i nettleseren på den publiserte siden.** Chrome var ikke tilgjengelig herfra
  25.10. Publiseringen er grønn, og endringen er testet lokalt i Chromium på PC- og mobilbredde.
- **Fra før:** Kontrollhøring 10005976 hos Stortinget viser sakstittelen til programmet publiseres.
  Satoshi-skriften er ikke med.

## Forslag til senere sprinter
- Hente temaet fra hver høringsside på regjeringen.no og vise det i tillegg til avsenderen, slik at
  filteret «Tema» blir et saksfelt (sprint 6, sammen med høringspartene).
- La den foreslåtte prioriteten settes per høring, ikke bare per kilde, ut fra regionflagget og
  høringspartene (sprint 6).
- Flytte tidsplanen til et minutt utenom hel time, for eksempel 07.43 og 08.43 UTC. GitHub forsinker
  ofte kjøringer som starter på hel time.
- Et lite e-postvarsel når en kilde har feilet to uker på rad.
- Rydde data-commits: samle dem i én commit per kjøring.

## Hva Svein bør sjekke selv
0. **v2:** Åpne siden og se at hver høring har flagget «Foreslått prioritet: høy». Åpne
   nedtrekkslisten «Tema» og se at «Stortinget» og «Regjeringen og departementene» står hver for seg.
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ og se at regjeringen.no-høringene er med,
   og at «Ny» vises. Sjekk at tabellen «Kildene» nederst viser «Hentet» for alle fem kildene.
2. Slå på «Vis høringer med utløpt frist (siste 30 dager)» og se at utløpte høringer kommer med.
3. Mandag 26.10 etter kl. 10 (eller utpå dagen, se forsinkelsen over), med PC-en på: Under
   **Actions** skal *Ukentlig oppdatering* og *Regjeringen.no (GRUs PC)* være grønne, og siden skal
   vise «Oppdatert 26. oktober 2026». Det er første kjøring i vintertid.
4. Sjekk at runneren starter av seg selv: Start PC-en på nytt, og se at `gru-pc` står som **Idle**
   under Settings → Actions → Runners uten at du gjør noe. Står den som Offline, må programmet
   installeres som tjeneste (se `docs/oppsett-pc.md`, B3 og feilsøking).
