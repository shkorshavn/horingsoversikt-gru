# Sprint 7 – Gjøvik kommunes postliste

## Sammendrag
Den ukentlige oppdateringen sjekker nå Gjøvik kommunes postliste for inngående høringsbrev de
siste 14 dagene, og kobler dem mot høringene i oversikten. På nettsiden får høringer kommunen
har mottatt, merket «Mottatt av Gjøvik kommune 20. oktober 2026», med lenke til journalposten.
Det finnes også et filter for disse. Høringsbrev uten treff vises i en egen seksjon under
listen.

Koblingen er testet med 48 ekte høringsbrev fra postlista (august–oktober 2026). Alle 23 brev
som har en høring i oversikten, ble koblet riktig, og ingen av de 24 andre fikk et feil treff.
Feiler postlista, fullføres resten av oppdateringen, og forrige treff beholdes. Det er testet med
en simulert feil i den ekte arbeidsflyten.

Alle punktene i sjekklisten er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget

**Henting** (`horinger/postliste.py`, ny)
- Henter fra samme endepunkt som postlistesiden selv bruker
  (`POST /api/presentation/v2/nye-innsyn/overview`), godkjent i sprint 0.
- Søker per søkeord og bare i inngående dokumenter. Resultatet er sortert nyeste først, og
  innhentingen blar til den når journalposter eldre enn 14 dager.
- **To funn underveis:**
  - Endepunktet avbryter svaret hvis forespørselen mangler hodene `Origin` og `Referer`.
  - Det avbryter også uten informasjonskapslene som postlistesiden setter.

  Postlistesiden hentes derfor først, og forespørselen sendes med de samme hodene som
  nettleseren sender. Ingen sperre i robots.txt omgås: `/api/presentation/` og postlistesiden er
  ikke sperret (robots.txt lest 26.10.2026).
- **Utvalg:** tittelen må ha et søkeord. Titler som begynner med «Høringssvar»,
  «Høringsuttalelse», «Svar på forespørsel om høringsuttalelse», «Innspill», «Merknad» o.l., også
  etter «Kopi -», er svar til kommunen og tas ikke med. Søkeord og utelatte ord står i
  `sources.yaml`.
- **Personvern** (ditt svar 2): bare treff lagres. Avsender lagres bare når navnet ser ut som en
  virksomhet (kommune, departement, AS, forbund o.l.). Ellers vises «Avsender ikke vist».
- **Feil:** fanges og lagres som status. Forrige journalposter beholdes
  (`data/kilder/gjovik-kommunes-postliste.json`).

**Kobling** (`horinger/kobling.py`, ny)
- **Tittellikhet:** `rapidfuzz` (token_sort og token_set) etter at «Høring –», «Høyring av» o.l.
  er tatt bort.
- **Avsender:** +5 poeng når avsenderen er den samme, −15 når den er en annen. Avkortede navn
  («Arbeids- Og Inkluderingsdepart») og forkortelser (`avsender_alias`) håndteres.
- **Referansenummer:** samme saksnummer gir 100.
- **Terskler:**
  - **85 gir «sikker»** («Mottatt av Gjøvik kommune»).
  - **70 gir «mulig»** («Mulig treff», ditt svar 4).
- **Kandidater:** åpne høringer og høringer med utløpt frist de siste 60 dagene.
- **Lagring:** koblingene lagres i `data/postliste_treff.json`.
  - Et sikkert treff holdes fast så lenge høringen finnes. Merket blir derfor stående etter
    14-dagersvinduet.
  - Brev uten treff vises i 60 dager (ditt svar 3).

**Kjøring:** `horinger/kjor.py` henter postlistene etter kildene (spesifikasjonen, avsnitt 6),
og `horinger/bygg.py` kobler. Postlista kjøres fra GitHub, fordi endepunktet svarer derfra. Nye
`postlister:` i `sources.yaml` med `kjoring` og `aktiv` gjør det enkelt å legge til de fire
andre kommunene senere.

**Nettsiden** (`index.html`, `side/app.js`, `side/stil.css`)
- **Merket under tittelen:** «Mottatt av Gjøvik kommune 20. oktober 2026», som lenke til
  journalposten. Usikre treff vises stiplet: «Mulig treff i Gjøvik kommunes postliste …».
- **Filter:** «Bare høringer mottatt av Gjøvik kommune» (`?mottatt=1`). Det viser bare sikre
  treff.
- **Ny seksjon:** «Høringsbrev i postlista uten treff i oversikten», med dato, avsender, tittel
  og lenke.
- **Statusoversikten:** egen rad med antall brev og en linje om når postlista sist ble sjekket.
  Ved feil vises når den sist lyktes.
- **CSV:** ny kolonne «Mottatt av Gjøvik kommune». Utskriften tar med merket.
- **Publisering:** `publiser.yml` legger `postliste_treff.json` ut sammen med siden.

**Utforsking.** Den nye arbeidsflyten `utforsk-github.yml` og verktøyet `verktoy/utforsk_api.py`
kjører POST-forespørsler med samme høflighetsregler som innhentingen. `utforsk-pc.yml` kan nå
det samme fra PC-en.

**Nye filer:**
- `horinger/postliste.py`
- `horinger/kobling.py`
- `tests/test_postliste.py`
- `tests/test_kobling.py`
- `tests/fixtures/postliste/` (ekte API-svar, 48 journalposter og høringene 26.10)
- `.github/workflows/utforsk-github.yml`
- `verktoy/utforsk_api.py`

**Endrede filer:**
- `horinger/kjor.py`, `horinger/bygg.py`
- `sources.yaml`, `requirements-kjoring.txt` (rapidfuzz)
- `index.html`, `side/app.js`, `side/stil.css`
- `.github/workflows/publiser.yml`, `.github/workflows/utforsk-pc.yml`
- `README.md`, `tests/test_nettside.py`

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **355 bestått, 0 feilet, 0 hoppet over** (45,2 s). 50 nye tester: 44 i `test_postliste.py` og `test_kobling.py`, og 6 i `test_nettside.py`. «Tester» er grønn på 3d80eca |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «85 files already formatted». Type hints og docstring på norsk |
| C. Ekte data | Bestått | Ukentlig oppdatering 26.10. kl. 23.33: 28 kilder «ok», inkludert postlista. **6 inngående høringsbrev** (13.–21.10), hentet med 7 kall på 12,3 s. 5 koblet sikkert og 1 uten treff (Sametinget). Samlet kjøretid 356 s. 6 er et naturlig tall: et søk på 70 dager ga 48 brev, altså 4–5 i uka |
| D. Stikkprøver | Bestått | Alle 6 journalposter er kontrollert felt for felt mot rådata fra endepunktet, se tabellen. Koblingen er kontrollert mot fasit for 48 brev |
| E. Tegn og datoer | Bestått | Æ, ø og å er riktige i JSON og på siden («Nærings- Og Fiskeridepartementet», «Samediggi Sametinget»). Journaldato lagres som ISO og vises som «20. oktober 2026». Vinduet regnes fra dagens dato i Europe/Oslo |
| F. Feilhåndtering | Bestått | Ekte arbeidsflyt med `simuler_feil=Gjøvik kommunes postliste` (26.10. kl. 23.29): de 27 andre kildene «ok», postlista «feil». De 5 merkene ble stående. Siden viste «…ble sist sjekket 26. oktober 2026 kl. 23.29, men sjekken feilet (sist vellykket 26. oktober 2026 kl. 23.24)». Testene dekker tidsavbrudd og simulert feil |
| G. Kodegjennomgang | Bestått etter retting | `git diff 9823d8d..HEAD`: 19 filer og 1416 nye linjer, se eget avsnitt |
| H. Høflighet | Bestått | User-Agent og pause som før. robots.txt sjekkes før første kall: `/api/presentation/` og postlistesiden er ikke sperret. Ukentlig trafikk er 7–8 kall. Utforskingen og testene i dag ga om lag 55 kall til endepunktet, fordelt over to timer |
| I. Dokumentasjon | Bestått | README har nytt avsnitt «Gjøvik kommunes postliste», og Status og Nettsiden er oppdatert. `sources.yaml` har kommentarer til `felles.postliste` og `postlister` |
| J. Akseptansekriterier | Bestått | Se tabellen under |

## Stikkprøver
Journalpostene ble lest uavhengig fra rådata hentet med `utforsk-github` og sammenlignet med det
som er lagret. Lenkeformatet (`#/details/<sak>/<dokument>`) er det samme som postlistesiden selv
brukte i nettleseren i sprint 0. Jeg har ikke åpnet lenkene her, så det bør du gjøre (se under).

| Postliste | Journalpost | Felt kontrollert | Avvik | Kobling |
|---|---|---|---|---|
| Gjøvik | 2026/86288, 21.10, Kunnskapsdepartementet: saksbehandlings- og klageregler i opplæringsloven | tittel, dato, dok.-ID, avsender, lenke | Ingen | Sikker (100) → regjeringen.no, riktig |
| Gjøvik | 2026/86270, 21.10, Nærings- og fiskeridep.: Europakommisjonens anskaffelsesforordning | samme | Ingen | Sikker (100), riktig |
| Gjøvik | 2026/85652, 20.10, Helse- og omsorgsdep.: fylkeskommunale tannhelsetjenester | samme | Ingen | Sikker (100), riktig |
| Gjøvik | 2026/85572, 19.10, Statens vegvesen: indeksregulering i parkeringsforskriften | samme | Ingen | Sikker (95) → «Høring om parkeringsforskriften (21-219359)», riktig |
| Gjøvik | 2026/84341, 14.10, Sametinget: behov for samisk tilbud i Sør-Norge valgkrets | samme | Ingen | Uten treff (33). Riktig: Sametinget er ikke en kilde |
| Gjøvik | 2026/84085, 13.10, Skatteetaten: skatteregnskapsområdet | samme | Ingen | Sikker (100), riktig |

Ett brev ble fjernet av filteret: «Innspill og spørsmål om Sørbyen – styringsdokument
2027–2030». Det er et innspill til kommunen, ikke et høringsbrev. Svar og kopier av høringssvar
til kommunens egne planer ble også tatt bort (sett i rådata).

## Koblingskvalitet og terskler (kriterium 3 og 4)
Søk på «høring» i inngående dokumenter for 06.08–21.10.2026 ga 48 brev med en virksomhet som
avsender. Fasiten ble satt for hånd ut fra tittel, avsender og dato:

| Gruppe | Antall | Resultat |
|---|---|---|
| Brev med riktig høring i oversikten | 23 | **23 koblet riktig, alle «sikker»** (poengsum 87,3–100) |
| Brev uten høring i oversikten | 24 | **0 treff** (høyeste poengsum 63,8) |
| Uavklart | 1 | «Revisjon av regelverket om vekter og dimensjoner» (Vegvesenet, 02.10) fikk 65 mot høringen om ny forskrift om vekter og dimensjoner, men den hadde frist 30.09. Kan være samme sak. Ingen kobling |

**De 23 riktige** fordeler seg på regjeringen.no (16), Statens vegvesen (3), Innlandet
fylkeskommune (2, både varselet om oppstart og planprogrammet for nettinfrastruktur),
Helsedirektoratet (1), Miljødirektoratet (1) og Skatteetaten (1). Fem av dem er de samme som
sprint 0 fant: fylkets planprogram, Vegvesenets vegtrafikklov, de to KD-høringene og
Skatteetaten.

**De 24 uten treff** er blant annet:
- Sametinget, NVEs detaljplan for dam Beritknappen og Oslo universitetssykehus (traumeplan).
- Statsforvalterens tiltaksplan for skog og Vestre Totens dispensasjonssak.
- Utdanningsdirektoratet (4).
- Vegvesenets skiltplaner og høringsbrev om trafikkregulerende skilt.
- Høringer fra Barne- og familiedepartementet og Mattilsynet som ikke er i oversikten.

**Tersklene:**
- **Sikker = 85.** Laveste riktige er 87,3 (hest i trafikken).
- **Mulig = 70.** Høyeste feil er 63,8 (eForvaltningsforskriften mot kringkastingsforskriften).
- Med 85 og 70 ble det null feilkoblinger og null bom blant de 23. Marginen er minst 2 poeng
  over sikker-terskelen og over 6 poeng under mulig-terskelen. Begge marginene testes i
  `test_tersklene_har_god_margin`.
- Ingen brev landet mellom 70 og 85, så «Mulig treff» er ikke sett i ekte data ennå. Det er
  testet med justerte terskler.

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| 1. Postlista hentes med metoden som ble godkjent i sprint 0 | Ja | ACOS-endepunktet (alternativ 2 i kildekartleggingen, sprint 0 godkjent 16.10). Ekte kjøring: 6 brev, status «ok» |
| 2. Filtrering på søkeord og 14-dagersvindu virker | Ja | Ekte kjøring 26.10: eldste brev 13.10 (vindu fra 12.10). Testene `test_14_dagers_vindu`, `test_blar_ikke_forbi_vinduet` og `test_er_svar` |
| 3. Koblingen testet med minst fem kjente høringsbrev, med treffkvalitet dokumentert | Ja | 23 kjente brev, alle riktige, i tabellen over. Ligger som tester med ekte data |
| 4. Terskelen for «Mulig treff» er begrunnet ut fra testresultatene | Ja | 70: over 6 poeng over høyeste feil (63,8). Se avsnittet over |
| 5. Seksjonen for postlistetreff uten kobling vises | Ja | «Høringsbrev i postlista uten treff i oversikten» med Sametinget i ekte data. Testene `test_seksjon_uten_treff` og `test_seksjonen_skjules_uten_data` |
| 6. Hvis postlista feiler, fullføres resten av oppdateringen | Ja | Simulert feil i ekte arbeidsflyt (F) og tester |

## G. Kodegjennomgang
Jeg leste hele diffen mot godkjenningen av sprint 6 (`git diff 9823d8d..HEAD`).

**Funnet og rettet:**
- **«Innspill …» fra privatpersoner kom med.** «Innspill» er nå et utelatt ord i starten av
  tittelen.
- **Utelatte ord traff hvor som helst i tittelen.** Ordene ble først sjekket i hele tittelen,
  slik at «Høring – … frist for høringssvar» ville falt bort. Nå teller de bare i starten.
- **Treff i departementsnavn manglet.** Virksomhetsordene var bare hele ord, slik at
  «Omsorgsdepartementet» ikke traff. Nå kan lange ord stå inne i sammensatte ord, mens korte
  (AS, KS, lag) må stå alene.
- **Kriminformasjonsforskriften fikk bare 61.** Parenteser ble fjernet fra titler, så navnet
  falt bort. Nå beholdes de, og høringen får 95.
- **Statusen viste «0 brev» ved feil.** Nå viser den antall beholdte brev.
- **Postlista hentet ingenting fra GitHub.** Svaret ble avbrutt uten informasjonskapsler. Nå
  hentes postlistesiden først.

**Vurdert og beholdt:**
- Terskler, søkeord, alias og virksomhetsord ligger i `sources.yaml`.
- Dokumenttypens ID for «Inngående dokument» står også der, ikke i koden.
- Lenker brukes bare når de begynner med http(s).
- Ingen hemmeligheter i koden.

## Kjente feil og begrensninger
1. **Endepunktet er ikke dokumentert av kommunen.**
   - Det krever de samme hodene og informasjonskapslene som postlistesiden sender.
   - Endrer ACOS dette, feiler postlista. Det vises da i statusen, og forrige treff blir stående.
2. **«Mulig treff» er ikke sett i ekte data ennå.** Ingen brev landet mellom 70 og 85.
   Tersklene bør vurderes på nytt når det har gått noen uker.
3. **Seksjonen «uten treff» viser bare brev fra og med i dag.** Den fylles opp mot 60 dager over
   tid. Historiske brev (48 fra august–oktober) er bare brukt i testene.
4. **Søkeordet «innspill» gir lite.** Titler som begynner med «Innspill», er innspill til
   kommunen, og de utelates. «Innspill» treffer derfor bare titler der ordet står senere.
5. **Filteret «Bare mottatt» viser bare sikre treff, ikke «Mulig treff».**
6. **Mange brev uten treff kommer fra kilder vi ikke overvåker:** Udir (inaktiv), Sametinget,
   Oslo universitetssykehus, og NVEs detaljplaner for dammer. Seksjonen viser dermed hullene, slik
   spesifikasjonen ønsker.

## Forslag til senere sprinter
- De fire andre kommunene: sjekk om de bruker ACOS «nye-innsyn», og legg dem inn under
  `postlister:`.
- Vurder Udir på nytt: Udir sender høringer direkte til kommunene. Fire av brevene uten treff er
  fra Udir.
- Vis «Mulig treff» i filteret som eget valg hvis det blir mange av dem.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/?mottatt=1. Viser listen fem høringer
   med merket «Mottatt av Gjøvik kommune»?
2. Klikk på merket «Mottatt av Gjøvik kommune 20. oktober 2026» på
   tannhelsetjenester-høringen. Åpner lenken journalposten 2026/85652 i postlista?
3. Under listen: står Sametingets høringsbrev i «Høringsbrev i postlista uten treff i
   oversikten»?
4. I statusoversikten: står «Gjøvik kommunes postliste» som OK, med «6 brev»?
