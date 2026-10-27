# Sprint 8 – KI-sammendrag og ferdigstilling

## Sammendrag
Høringene har nå et kort sammendrag i klarspråk, laget med Anthropic API (`claude-sonnet-5-5`)
og merket «KI-sammendrag». Ingressen fra kilden ligger bak et klikk. Sammendragene lagres per
høring og lages bare i den ukentlige oppdateringen. Uten nøkkel, eller ved feil, vises
ingressen, og oppdateringen går som normalt.

Nettsiden er delt, slik du ønsket: på PC ruller filtrene og listen hver for seg.

README er fulgt fra bunnen i en tom mappe, og hele sjekklisten er kjørt for løsningen samlet.
Under ferdigstillingen fant og rettet jeg tre feil:
- Lagringen fra PC-en ville ha feilet ved neste mandagskjøring.
- Sammendrag ble kuttet før modellen rakk å svare.
- Sammendragene inneholdt to små påfunn.

Alle punktene er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget

**Delt visning** (`side/stil.css`, `index.html`)
- **På PC** (bredere enn 52 rem): toppen står fast, og filtrene og listen er hvert sitt
  rulleområde.
  - Rulling i listen flytter ikke filtrene, og omvendt.
  - «Hopp til høringene» flytter ikke toppen.
  - Skjulte tekster for skjermlesere holdes inne i rulleområdet, slik at selve siden aldri får
    noe å rulle.
- **Bunnteksten** står nå nederst i listen.
- **Mobil og utskrift** er som før.

**KI-sammendrag** (`horinger/sammendrag.py`, ny)
- **Grunnlag:** avsender, tittel, ingress og teksten fra høringssiden (`detaljtekst`, høyst
  6 000 tegn). Detaljteksten lagres når detaljsiden uansett leses for høringsparter, og
  publiseres ikke på nettsiden.
- **Instruks:**
  - Norsk bokmål og klarspråk, 1–2 setninger, høyst 45 ord.
  - Bare opplysninger fra teksten. Hvem høringen gjelder, nevnes bare når teksten sier det
    uttrykkelig.
  - Ingen frist og ingen vurdering.
  - Gir teksten for lite å bygge på, svarer modellen «MANGLER», og ingressen vises.
- **Buffer:** `data/sammendrag.json`, med versjon og sjekksum av grunnlaget.
  - Bare nye eller endrede høringer sendes til API-et.
  - Sammendrag for høringer som er borte, slettes.
- **Feil:** svar uten tekst (modellen tenker først, og tenkingen teller mot `maks_tokens`) regnes
  som feil og prøves igjen neste gang. Feil for én høring stopper ikke resten, og kommandoen
  avslutter alltid med 0.
- **Når:** steget «KI-sammendrag» i `publiser.yml` kjører bare når publiseringen er startet av
  den ukentlige oppdateringen eller PC-jobben (`workflow_dispatch`), ikke ved kodeendringer
  (ditt svar 27.10.2026).
- **Nøkkel:** GitHub Secret `ANTHROPIC_API_KEY`. Den står ikke i koden og skrives aldri til
  loggen (testet).
- **Nettsiden:**
  - Merket «KI-sammendrag» foran teksten, og «Vis ingressen fra kilden».
  - Søket leter også i sammendraget.
  - CSV har to nye kolonner: «KI-sammendrag» og «Ingress».

**Ferdigstilling**
- **README:**
  - Komplett oppsett fra bunnen (klone, venv, installere, teste, kjøre).
  - Nytt avsnitt om KI-sammendrag, med trinnvis oppsett av API-nøkkelen.
  - Datafilene er beskrevet.
- `docs/oppsett-pc.md` har feilsøking for tjenesten.

**Feil funnet og rettet:**
- **Lagring fra PC-en** (`verktoy/git_lagre.py`). Etter at runneren ble en Windows-tjeneste
  27.10, avviste git arbeidsmappen («dubious ownership»), og steget «Lagre resultatet» feilet to
  ganger. Det ville ha stoppet regjeringen.no ved mandagskjøringen. `safe.directory` settes nå
  per kommando, uten endringer på PC-en. Neste kjøring lagret som normalt.
- **Tidssone i en test** (`tests/test_statsforvalteren.py`). Testen sammenlignet norsk dato med
  maskinens dato, og feilet på GitHub (UTC) like etter midnatt. Den bruker nå `i_dag()`.

**Nye filer:**
- `horinger/sammendrag.py`
- `tests/test_sammendrag.py`
- `docs/sprinter/sprint-08-plan.md`

**Endrede filer:**
- `horinger/bygg.py`, `horinger/kilder/base.py`, `horinger/modell.py`
- `sources.yaml`, `requirements-kjoring.txt` (`anthropic`)
- `.github/workflows/publiser.yml`
- `index.html`, `side/app.js`, `side/stil.css`
- `README.md`, `docs/oppsett-pc.md`
- `verktoy/git_lagre.py`
- `tests/test_nettside.py`, `tests/test_statsforvalteren.py`

## Kvalitetssikring (hele løsningen)
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **373 bestått, 0 feilet, 0 hoppet over** (53,3 s). Dette er hele suiten for alle sprintene. Nye i sprint 8: 14 for sammendrag og 4 for nettsiden (delt visning og sammendrag). Arbeidsflyten «Tester» er grønn |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «89 files already formatted» |
| C. Ekte data | Bestått | Oppdatering 27.10. kl. 18.31: **28 kilder og postlista, alle «ok»**. 12 kilder er inaktive med begrunnelse. 127 åpne høringer, hentet på 361 s. 119 med KI-sammendrag, 53 med liste over høringsparter, 23 med regionflagg og 5 «Mottatt av Gjøvik kommune» |
| D. Stikkprøver | Bestått | 22 høringer (to per kilde med åpne høringer, 13 kilder) kontrollert mot kildens side. Se tabellen. 15 sammendrag kontrollert mot originalteksten (kriterium 3) |
| E. Tegn og datoer | Bestått | Æ, ø og å er riktige i alle JSON-filene (ingen `\u00..`-koder) og på siden. ISO 8601 i data, norsk format på siden. Dagens dato i Europe/Oslo. En test som brukte maskinens dato, er rettet |
| F. Feilhåndtering | Bestått | **Sammendrag:** uten nøkkel gikk publiseringen 26.–27.10 som normalt og viste ingressen. Testene dekker feil per høring, tomt svar og at nøkkelen ikke logges. **Postlista:** simulert feil (sprint 7). **PC-en:** feilen i lagringen ga rød status og stoppet ikke GitHub-kildene. Nå rettet |
| G. Kodegjennomgang | Bestått etter retting | `git diff 9654016..HEAD`: 18 filer og 810 nye linjer, se eget avsnitt. Hele kodebasen er sjekket for hemmeligheter: ingen |
| H. Høflighet | Bestått | Alle kall til kildene går gjennom `Nett`: User-Agent, minst 1,5 s pause (lenger der robots.txt krever det) og robots.txt før første kall. robots.txt med BOM tolkes riktig (sprint 6). Datatilsynet står fortsatt inaktiv (robots.txt svarer 500). Detaljsidene som nå lagres som grunnlag, ble allerede hentet for høringsparter. Ingen nye kall til kildene |
| I. Dokumentasjon | Bestått | README fulgt fra bunnen (kriterium 4). Kommentarer i `sources.yaml` for `felles.sammendrag` |
| J. Akseptansekriterier | Bestått | Sprint 8 i tabellen under. Sprint 0–7 er kontrollert på nytt i eget avsnitt |

## Stikkprøver (hele løsningen)
Sidene ble hentet på nytt 27.10 fra GitHub (utforsk-github) og fra PC-en (regjeringen.no). Felt
for felt ble sammenlignet automatisk og deretter lest: tittel på siden, frist i et av formatene
siden bruker, avsender på siden og lenke (svar 200).

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Regjeringen.no | Kystruten Bergen–Kirkenes (frist 28.10) | tittel, frist, instans, lenke | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-ny-ruteplan-for-kystruten-bergen-kirkenes/id3169361/) |
| Regjeringen.no | Varig tilrettelagt arbeid etter 67 år (30.10) | samme | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-om-ev.-deltakelse-i-arbeidsmarkedstiltaket-varig-tilrettelagt-arbeid-etter-fylte-67-ar/id3166867/) |
| Stortinget | Nasjonal strategi for … (27.10) | samme | Ingen | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/) |
| Stortinget | Rullerende … (27.10) | samme | Ingen | [Stortinget](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/) |
| Miljødirektoratet | Forbud mot fossil gass til oppvarming (27.10) | samme | Ingen | [side](https://www.miljodirektoratet.no/hoeringer/2026/juni-2026/forbud-mot-bruk-av-fossil-gass-til-oppvarming/) |
| Miljødirektoratet | Karbonpris ved import (06.11) | samme | Ingen | [liste](https://www.miljodirektoratet.no/hoeringer/) |
| DMP | Grossistforskriften (09.11) | samme | Ingen | [side](https://www.dmp.no/nyheter/horing---forslag-til-endringer-i-grossistforskriften--5-og-5a) |
| DMP | Medisinsk utstyr (09.12) | samme | Ingen | [side](https://www.dmp.no/nyheter/horing-om-endringer-i-forskrift-for-medisinsk-utstyr--kvalitetsstyring-og-samsvarsvurdering) |
| Skatteetaten | Overgangsregler til innkrevingsloven (11.11) | samme | Ingen | [liste](https://www.skatteetaten.no/rettskilder/type/horinger/) |
| Skatteetaten | Skatteregnskapsområdet (24.11) | samme | Ingen | [liste](https://www.skatteetaten.no/rettskilder/type/horinger/) |
| Innlandet fylkeskommune | Planprogram nettinfrastruktur (11.11) | samme | Ingen | [side](https://innlandetfylke.no/politikk/horinger/planprogram-pa-horing-regional-plan-for-nettinfrastrukturen-for-energi.81920.aspx) |
| Innlandet fylkeskommune | Fv. 213 Skog bru (13.11) | samme | Ingen | [side](https://innlandetfylke.no/politikk/horinger/oppstart-av-reguleringsplanarbeid-for-fv-213-skog-bru-i-ringsaker-kommune.82328.aspx) |
| Nkom | Lokale FM-sendernett (13.11) | samme | Ingen | [side](https://nkom.no/hoeringer/horing-av-utlysningsvilkar-og-tildelingsregler-for-lokale-fm-sendernett) |
| Mattilsynet | Dyrehelseforskrifter (17.11) | samme | Ingen | [liste](https://www.mattilsynet.no/hoeringer) |
| Mattilsynet | Næringsmiddelforskrifter (20.11) | samme | Ingen | [liste](https://www.mattilsynet.no/hoeringer) |
| DSB | Sivilforsvarsforskriften (27.11) | samme | Ingen | [side](https://www.dsb.no/horinger/horinger/endringer-i-sivilforsvarsforskriften/) |
| Statens vegvesen | Parkeringsforskriften (30.11) | samme | Ingen | [side](https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing-om-parkeringsforskriften-21-219359/) |
| Statens vegvesen | Hest i trafikken (07.12) | samme | Ingen | [liste](https://www.vegvesen.no/fag/publikasjoner/hoeringer/) |
| NVE | Økodesignforskriften («desember 2026») | samme | Ingen | [side](https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/) |
| Helsedirektoratet | Mat, måltider og ernæring (03.12) | samme | Ingen | [side](https://www.helsedirektoratet.no/horinger/retningslinje-for-mat-maltider-og-ernaering-i-helse-og-omsorgstjenesten) |
| Helsedirektoratet | Breddekompetanse (01.02.2027) | samme | Ingen | [side](https://www.helsedirektoratet.no/horinger/breddekompetanse-i-legenes-spesialistutdanning-innspillsrunde) |
| Arbeidstilsynet | Røntgenundersøkelse ved bergarbeid (31.01.2027) | samme | Ingen | [side](https://www.arbeidstilsynet.no/regelverk/horinger/horing/?hearingId=3884) |

Kildene med 0 åpne høringer er de samme som i sprint 5–7, for eksempel Bane NOR, Bufdir og SSB.
DiBK, Digdir, Landbruksdirektoratet, Nasjonalarkivet og Riksantikvaren har bare høringer med
utløpt frist. Konkurransetilsynet og Statsforvalteren har ingen åpne i dag.

## Vurdering av sammendrag (kriterium 3)
Hvert sammendrag er lest mot grunnlaget (ingressen og hele detaljteksten). Påstander som ikke
stod i utdraget, ble søkt opp i teksten. Første runde (instruksversjon 2) hadde to små påfunn.
Instruksen ble strammet inn (versjon 3), alle sammendrag ble laget på nytt, og vurderingen ble
gjentatt:

| # | Kilde | Høring | Korrekt | Klarspråk | Merknad |
|---|---|---|---|---|---|
| 1 | Regjeringen.no (FIN) | Valutasikring i verdipapirfond | Ja | Middels | Riktig, men fagspråk («andelsklasser», «basisvaluta»). Følger teksten |
| 2 | Regjeringen.no (JD) | Utlendingsloven § 34 | Ja | God | Fem til sju år, permanent opphold etter to i stedet for tre år, og asylsøknad i bero. Alt står i teksten |
| 3 | Regjeringen.no (HOD) | Spesialisthelsetjenester til samene | Ja | God | Utvalgets tre anbefalte elementer gjengitt riktig |
| 4 | Mattilsynet | Kondensert melk og melkepulver | Ja | God | Laktosereduksjon og merking riktig |
| 5 | Statens vegvesen | Parkeringsforskriften | Ja | God | Ren indeksregulering, § 36 femte ledd, hvert femte år |
| 6 | Arbeidstilsynet | Røntgenundersøkelse ved bergarbeid | Ja | God | Ordrett nær teksten |
| 7 | Miljødirektoratet | Klimakvoteforskriften | Ja | Middels | Riktig («krav til … revisor» = «hvem som kan revidere»). Fagtungt tema |
| 8 | NVE | Økodesignforskriften | Ja | God | «Tre EU-forordninger» stemmer (2025/2052, 2025/2262 og 2025/1353) |
| 9 | Nkom | Lokale FM-sendernett | Ja (v3) | God | **v2 hadde et påfunn:** «Gjelder lokalradioaktører, særlig mindre». Teksten ber om innspill *om* mindre aktører. v3 er riktig |
| 10 | Skatteetaten | Sukkeravgiften | Ja | God | Utvidet fritak for små bakerier og kafeer, og forenklinger |
| 11 | Innlandet fylkeskommune | Fv. 187 Ringgata | Ja (v3) | God | **v2 hadde et påfunn:** «Planen berører grunneiere langs vegen». v3 er riktig («kryss og krysningspunkter» står i teksten) |
| 12 | DSB | Sivilforsvarsforskriften | Nesten | God | «blir skattepliktige fra 1. januar 2027». Teksten sier at et *forslag* til endring i skatteloven innebærer det. Liten unøyaktighet, står som kjent begrensning |

**Resultat:**
- Av de ti første (1–10) er alle korrekte i versjon 3, og åtte har god klarspråk.
- To er korrekte, men fagtunge, fordi temaet er det.
- Påfunnene i versjon 2 (nr. 9 og 11) er rettet med den strengere instruksen.
- Nr. 12 viser at modellen av og til kan skrive et forslag som et vedtak.

**Lengde:** 8–45 ord, gjennomsnitt 31, ingen over grensen.

**«MANGLER»:** 8 av 127 viser ingressen. Det er 6 Stortinget-høringer der grunnlaget bare er
tittel og «Skriftlig høring» (riktig), og 2 på regjeringen.no der modellen var for forsiktig.

## Akseptansekriterier (sprint 8)
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| 1. Sammendrag lages med Anthropic API og caches per høring | Ja | 119 sammendrag i `data/sammendrag.json`, med sjekksum og versjon. Test `test_lager_og_bufrer_sammendrag`: andre kjøring gir 0 nye kall. Modell `claude-sonnet-5-5` (ditt svar 1, i stedet for `claude-sonnet-4-6` i spesifikasjonen) |
| 2. Uten API-nøkkel brukes ingressen, uten at kjøringen feiler | Ja | Ekte publisering uten nøkkel 26.–27.10 («Ingen API-nøkkel … vises med ingressen»). Testene `test_uten_nokkel_feiler_ikke` og `test_main_uten_nokkel_gir_0` |
| 3. Ti sammendrag vurdert mot originalteksten for korrekthet og klarspråk | Ja | Tabellen over (12 vurdert) |
| 4. README er komplett og testet ved at oppsettet er fulgt fra bunnen | Ja | Ny mappe: `git clone` → `python -m venv` → `pip install -r requirements.txt` → `npm install axe-core` → `pytest` (371 bestått da) → `ruff` → `python -m horinger.sammendrag` → `python -m horinger.bygg`. Alt virket. Unntak: `playwright install chromium` ble ikke kjørt, fordi Chromium allerede finnes på maskinen min |
| 5. Hele sjekklisten er kjørt for hele løsningen samlet | Ja | Tabellen «Kvalitetssikring (hele løsningen)» og avsnittet under |
| Tillegg: venstre og høyre side ruller hver for seg | Ja | Testene `test_filtre_og_liste_ruller_hver_for_seg`, `test_hopp_til_listen_flytter_ikke_toppen` og `test_mobil_ruller_som_en_side`. Tatt i bruk på nettsiden |

## Akseptansekriterier sprint 0–7, kontrollert på nytt 27.10.2026
| Sprint | Kontrollert nå | Status |
|---|---|---|
| 0 Kartlegging | Kildekartleggingen er fulgt. Metoder og inaktive kilder står i `sources.yaml` med begrunnelse | Oppfylt |
| 1 Grunnmur og fem kjernekilder | Stortinget, regjeringen.no, Statens vegvesen, Innlandet fylkeskommune og Statsforvalteren er «ok» i dag. Feltene i avsnitt 3 finnes i `horinger.json` | Oppfylt |
| 2 Nettsiden | Sortering på frist, fargekoder, filtre, CSV, statusoversikt, WCAG (axe) og mobil. Alle testene består | Oppfylt |
| 3 Automatisering og publisering | Ukentlig oppdatering og publisering virker. Mandagskjøringen 26.10 kom sent på grunn av forsinkelse hos GitHub, men gikk gjennom. Arkiv og «Ny» virker | Oppfylt |
| 4 Prioritet 1-direktorater | Kildene er «ok», deduplisering og prioritet er testet | Oppfylt |
| 5 Prioritet 2 og 3 | Kjøretid 361 s (krav: under 30 min). Filtrene virker med alle kilder | Oppfylt |
| 6 Høringsparter og regionflagg | 53 lister og 23 flagg. KS alene gir ikke flagg | Oppfylt |
| 7 Postlista | «ok» i dag. 5 merker og listen «uten treff» vises | Oppfylt |

## G. Kodegjennomgang
Jeg leste diffen mot godkjenningen av sprint 7 (`git diff 9654016..HEAD`) og søkte i hele
kodebasen etter hemmeligheter, testnøkler og `print(`.

**Funnet og rettet:**
- `maks_tokens` var 200. Med adaptiv tenking i Sonnet 5.5 kom det ofte ikke noe tekstsvar.
  Første runde ga 53 tomme sammendrag, som ble lagret som «MANGLER». Grensen er nå 2000, og
  tomme svar er en feil som prøves igjen.
- Påfunn i to sammendrag. Rettet med strengere instruks (versjon 3).
- `git_lagre.py` og testen med tidssone, se over.
- Absolutt plasserte skjulte elementer slapp ut av rulleområdet, slik at selve siden kunne
  rulles («Hopp til høringene» skjøv toppen bort). Rettet med `position: relative`.

**Vurdert og beholdt:**
- Modell, `maks_tokens`, pause og maks antall kall per kjøring står i `sources.yaml`.
- `anthropic` importeres bare når nøkkelen finnes.
- `TomtSvar` og `VERSJON` gjør at bufferen aldri lagrer et svar som er kuttet av.

## Kjente feil og begrensninger
1. **Sammendrag kan være unøyaktige.** Nr. 12 skriver et forslag som et vedtak. Sammendragene
   er merket «KI-sammendrag», og ingressen ligger ett klikk unna.
2. **Kostnad i testingen:** sammendragene ble laget tre ganger i dag (versjon 1–3, ca. 380
   kall). Det koster trolig noen få dollar, mer enn anslaget på under 1 dollar for én runde.
   Fremover lages bare nye høringer. Sjekk forbruket under **Usage** i Anthropic Console.
3. **API-nøkkelen utløper** etter perioden du valgte i Console. Da vises ingressen igjen. Lag
   en ny nøkkel og bytt den i GitHub (README, «Slik setter du API-nøkkelen»).
4. **8 høringer uten sammendrag** («MANGLER») viser ingressen. Det gjelder mest
   Stortinget-høringer der grunnlaget er for tynt.
5. **Delt visning** gjelder bare skjermer bredere enn ca. 830 px. Smalere skjermer ruller som
   én side, slik planen sa.

## Forslag til senere arbeid
- Hente teksten til Stortinget-høringene (saksdokumentet), slik at de også får sammendrag.
- Bruke Message Batches API for sammendragene. Det er halv pris, og tidspunktet spiller ingen
  rolle.
- De andre kommunenes postlister og Udir (forslagene fra sprint 7).

## Hva Svein bør sjekke selv
1. **Delt visning:** åpne https://shkorshavn.github.io/horingsoversikt-gru/ på PC-en. Rull i
   filtrene til venstre, og sjekk at listen står i ro. Gjør så det motsatte.
2. **Sammendrag:** les et par sammendrag, f.eks. utlendingsloven § 34 og sukkeravgiften, og
   klikk «Vis ingressen fra kilden». Er formen og lengden slik du vil ha den?
3. **Forbruk:** se på **Usage** i Anthropic Console, og bekreft at brukgrensen er satt.
4. **Status:** alle kildene, postlista og regjeringen.no står som OK i statusoversikten.
