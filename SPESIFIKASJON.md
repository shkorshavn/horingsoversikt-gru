# Spesifikasjon: Høringsoversikt for Gjøvikregionen

Arbeidsregler, sprintport og kvalitetssikring står i `CLAUDE.md`. Status og godkjenninger står i `SPRINTSTATUS.md`.

## 1. Formål

Gjøvikregionen Utvikling (GRU) er et interkommunalt oppgavefellesskap eid av Gjøvik, Østre Toten, Vestre Toten, Søndre Land og Nordre Land, og sekretariat for Gjøvikregionen IPR. Verktøyet skal hver uke automatisk hente aktuelle høringer fra nasjonale og regionale myndigheter, slik at GRU og eierkommunene raskt ser hva de bør svare på, og hvilke høringer Gjøvik kommune allerede har mottatt.

## 2. Kilder

Undersøk hver kilde før du skriver kode. Bruk API, RSS eller strukturerte data framfor HTML-skraping. Bruk Playwright der innholdet lastes med JavaScript.

Alle kilder legges i `sources.yaml` med feltene `navn`, `kategori`, `prioritet` (1–3), `url`, `metode` og `aktiv`, slik at kilder kan legges til, fjernes eller nedprioriteres uten kodeendring.

Mange direktorater publiserer høringene sine også på regjeringen.no. Sjekk dette per etat. Hent fra regjeringen.no der det er dekkende, og fra etatens egen side der den har høringer som ikke finnes på regjeringen.no (typisk planhøringer, veiledere og faglige retningslinjer). Dokumenter valget per kilde i README. Dedupliser på tvers av kilder.

Prioritet: 1 = alltid relevant for kommunene i Gjøvikregionen, 2 = ofte relevant, 3 = av og til relevant.

### Regjeringen og Stortinget
- Stortingets fagkomiteer: komitéhøringer (muntlige og skriftlige) via Stortingets åpne data-API (data.stortinget.no). Sesjons-ID beregnes dynamisk, siden ny sesjon starter i oktober. (1)
- Alle departementer via regjeringen.no (https://www.regjeringen.no/no/dokument/hoyringar/), kun åpne høringer. Departementet vises som høringsinstans. Særlig: Kommunal- og distriktsdepartementet, Kunnskapsdepartementet, Helse- og omsorgsdepartementet, Arbeids- og inkluderingsdepartementet, Digitaliserings- og forvaltningsdepartementet og Finansdepartementet (1). Øvrige: Klima- og miljø-, Samferdsels-, Landbruks- og mat-, Justis- og beredskaps-, Kultur- og likestillings-, Nærings- og fiskeri- og Forsvarsdepartementet (2).

### Transport, samferdsel og infrastruktur
- Nye Veier AS: planoppstart, trasévalg og detaljregulering (1)
- Statens vegvesen: transportplaner, vegprosjekter, trafikksikkerhet og vegforskrifter (1)
- Jernbanedirektoratet (1)
- Bane NOR SF: jernbaneplaner, utbygging og arealbruk langs sporet (1)
- Nasjonal kommunikasjonsmyndighet (Nkom): bredbånd og digital infrastruktur (2)

### Miljø, klima, energi og beredskap
- Miljødirektoratet (1)
- NVE: flom- og skredsikring, konsesjoner for vind- og vannkraft og kraftlinjer (1)
- Direktoratet for samfunnssikkerhet og beredskap (DSB) (1)
- Landbruksdirektoratet (2)
- Direktoratet for strålevern og atomsikkerhet (DSA), blant annet radon (3)

### Oppvekst, utdanning, kultur og integrering
- Utdanningsdirektoratet (Udir) (1)
- Integrerings- og mangfoldsdirektoratet (IMDi) (1)
- Barne-, ungdoms- og familiedirektoratet (Bufdir) (1)
- Kulturdirektoratet (2)
- Riksantikvaren (2)
- Arkivverket (2)

### Helse, omsorg og velferd
- Helsedirektoratet, inkludert nasjonale faglige retningslinjer (1)
- Arbeids- og velferdsdirektoratet (NAV) (1)
- Direktoratet for medisinske produkter (DMP) (2)
- Folkehelseinstituttet (FHI) (2)
- Mattilsynet, blant annet drikkevann (2)
- Arbeidstilsynet (2)
- Statens helsetilsyn (2)

### Styring, digitalisering, juss og eiendom
- Digitaliseringsdirektoratet (Digdir) (1)
- Direktoratet for forvaltning og økonomistyring (DFØ), inkludert anskaffelsesregelverket (1)
- Direktoratet for byggkvalitet (DiBK): TEK, SAK og universell utforming (1)
- Kartverket (2)
- Utlendingsdirektoratet (UDI) (2)
- Politidirektoratet og Innlandet politidistrikt (2)
- Skatteetaten, inkludert folkeregister, skatteoppkreving og eiendomsskatt (2)
- Datatilsynet (2)
- Statistisk sentralbyrå (SSB), inkludert KOSTRA-rapportering (2)
- Konkurransetilsynet, blant annet offentlig støtte (3)
- Sivilombudet (3)

### Regionale ledd
- Innlandet fylkeskommune: høringer og offentlige ettersyn på innlandetfylke.no, inkludert regionale planer og planstrategier (1)
- Statsforvalteren i Innlandet: høringer på statsforvalteren.no/innlandet, inkludert regionale verneplaner (1)

### Kilder uten fast høringsside
Finnes det ikke en stabil høringsside, RSS eller et nyhetsarkiv som kan filtreres på «høring», settes kilden til `aktiv: false` med en kommentar om hvorfor. Inaktive kilder vises i en egen liste «Kilder som ikke overvåkes automatisk» nederst på nettsiden.

## 3. Felter per høring

- **Høringsinstans (avsender):** kort navn, f.eks. «Kommunal- og distriktsdepartementet».
- **Tittel:** høringens offisielle tittel.
- **Hva høringen gjelder:** sammendrag på 1–2 setninger i klarspråk (se sprint 8). Inntil sammendrag er på plass brukes ingressen.
- **Høringsparter:**
  - Kort kategorisering, f.eks. «Alle kommuner og fylkeskommuner», «Departementer og direktorater», «Organisasjoner».
  - Tydelig flagg hvis noen av disse er nevnt: Gjøvik, Østre Toten, Vestre Toten, Søndre Land, Nordre Land, Gjøvikregionen, «alle kommuner», «alle fylkeskommuner», KS, Innlandet fylkeskommune. Søkeordene ligger i konfigurasjonen.
  - Full liste kan utvides ved klikk.
  - Står det at høringen er åpen for alle, vises det.
- **Høringsfrist:** dato og antall dager igjen. For Stortinget: frist for påmelding og/eller skriftlig innspill.
- **Lenke** til høringen hos kilden.
- **Publiseringsdato** når den finnes.

## 4. Kobling mot Gjøvik kommunes postliste

En egen jobb skal hver uke sjekke Gjøvik kommunes postliste og markere hvilke høringer kommunen har mottatt høringsbrev eller varsel om.

### Datakilde
- Postlista: https://www.gjovik.kommune.no/politikk-planer-og-organisasjon/postliste-dokumenter-og-vedtak/sok-i-postliste/
- Siden kjører på ACOS-plattformen og laster innholdet med JavaScript. Undersøk i denne rekkefølgen og velg den første som fungerer stabilt:
  1. Om Gjøvik kommune publiserer postlista på eInnsyn (einnsyn.no), som har et åpent API.
  2. Om postlistemodulen har et underliggende JSON-endepunkt, RSS eller eksport som siden selv kaller (sjekk nettverkstrafikken).
  3. Skraping med Playwright.
- Siden er merket `noindex, nofollow`. Sjekk robots.txt, hold trafikken lav og rapporter til Svein hvis automatisk henting ikke ser ut til å være tillatt.

### Hva som hentes
- Inngående journalposter (dokumenttype I) de siste 14 dagene. Vinduet overlapper med forrige kjøring fordi journalposter ofte publiseres med forsinkelse.
- Filtrer på søkeord i tittel: «høring», «høringsbrev», «høringsnotat», «høringsinvitasjon», «varsel om oppstart», «offentlig ettersyn», «innspill», «konsultasjon». Søkeordene ligger i konfigurasjonen.
- Per treff: journaldato, avsender, tittel, saksnummer, journalpostnummer og lenke.

### Kobling
- Match mot `data/horinger.json` ut fra avsender (normaliserte navn, f.eks. «KDD» = «Kommunal- og distriktsdepartementet»), tittellikhet (fuzzy matching, f.eks. rapidfuzz) og eventuelle referansenumre.
- Sikre treff markeres automatisk. Treff under en konfigurerbar terskel markeres som «Mulig treff».
- Koblinger lagres i `data/postliste_treff.json`, slik at en markering blir stående etter at journalposten faller ut av 14-dagersvinduet.

### Visning
- Merke «Mottatt av Gjøvik kommune» med journaldato og lenke til journalposten.
- Filter: «Kun høringer mottatt av Gjøvik kommune».
- Egen seksjon «Høringsbrev i postlista uten treff i oversikten».
- Tidspunkt for siste sjekk av postlista og om den lyktes.

### Utvidelse
Modulen bygges slik at Østre Toten, Vestre Toten, Søndre Land og Nordre Land kan legges til i konfigurasjonen senere, med eget merke per kommune.

## 5. Nettsiden

- Statisk side på GitHub Pages: `index.html` som leser `data/horinger.json`.
- Norsk bokmål i hele grensesnittet.
- Sortert på frist, nærmeste først. Utløpte høringer skjules som standard, men kan vises med en bryter.
- Fargekoding etter frist: under 14 dager, 14–30 dager og over 30 dager.
- Filtre: kategori, kilde/nivå (Storting, regjering, direktorat, fylkeskommune, statsforvalter), prioritet (1 og 2 valgt som standard), «kun høringer der regionen er høringspart», «kun mottatt av Gjøvik kommune» og fritekstsøk.
- Merke «Ny» på høringer som er kommet siden forrige oppdatering.
- Tidspunkt for siste oppdatering og status per kilde, også inaktive kilder.
- Eksport til CSV.
- Rent og profesjonelt uttrykk, responsiv, WCAG 2.1 AA, ingen eksterne sporingsskript.

## 6. Automatisk oppdatering

- GitHub Actions-workflow hver mandag kl. 06:00 norsk tid. Cron i Actions er UTC, så ta høyde for sommertid. Manuell kjøring via `workflow_dispatch`.
- Rekkefølge: hent høringer → kjør postlistejobben → oppdater data → commit.
- En kilde som feiler skal ikke stoppe resten av kjøringen.
- Utløpte høringer flyttes til `data/arkiv.json`.

## 7. Teknisk

- Python med requests, BeautifulSoup og Playwright ved behov. Én modul per kilde med felles grensesnitt.
- UTF-8 gjennom hele kjeden.
- Tydelig User-Agent, pauser mellom forespørsler, respekt for robots.txt.
- pytest for tester, ruff for linting og formatering.
- Tester per kilde som verifiserer at parseren fortsatt finner høringer, slik at strukturendringer på nettsidene oppdages.
- Anthropic API-nøkkel som GitHub Secret `ANTHROPIC_API_KEY`. Aldri i koden.
- README på norsk: oppsett, hvordan legge til kilder og søkeord, og hvordan sette API-nøkkel.

## 8. Sprintplan med akseptansekriterier

Hver sprint følger reglene i `CLAUDE.md`: plan først, godkjenning av plan, bygging, full kvalitetssikring, rapport, og stopp til Svein har godkjent i `SPRINTSTATUS.md`.

### Sprint 0 – Kartlegging av kilder
Ingen produksjonskode. Leveranse: `docs/kildekartlegging.md`.
- [ ] Alle aktive kilder i avsnitt 2 er undersøkt.
- [ ] Per kilde: URL, metode (API/RSS/HTML/Playwright), tilgjengelige felter, om høringsparter finnes, og om kilden er dekket av regjeringen.no.
- [ ] Postlista er undersøkt og anbefalt metode er begrunnet (eInnsyn, endepunkt eller Playwright), inkludert vurdering av robots.txt.
- [ ] Kilder uten stabil høringsside er listet med forslag om `aktiv: false`.
- [ ] Risikoer og åpne spørsmål til Svein er listet.

### Sprint 1 – Grunnmur og fem kjernekilder
Kilder: regjeringen.no, Stortinget, Innlandet fylkeskommune, Statsforvalteren i Innlandet, Statens vegvesen.
- [ ] Prosjektstruktur, felles datamodell, `sources.yaml` og felles grensesnitt for kildemoduler er på plass.
- [ ] Alle fem kildene gir høringer i `data/horinger.json` med feltene i avsnitt 3 (unntatt sammendrag og høringsparter).
- [ ] Stortingets sesjons-ID beregnes dynamisk og er testet for dato før og etter 1. oktober.
- [ ] Stikkprøver viser null avvik i tittel, avsender, frist og lenke.
- [ ] Hver kilde har minst én test.

### Sprint 2 – Nettsiden
- [ ] `index.html` viser høringene fra sprint 1 med sortering, fargekoding, filtre, fritekstsøk og CSV-eksport.
- [ ] Siden fungerer i en mobil visning (375 px) og på PC, verifisert med skjermbilder i rapporten.
- [ ] Tilgjengelighet er sjekket med et automatisk verktøy (f.eks. axe via Playwright) uten alvorlige funn.
- [ ] Statusoversikten per kilde vises.
- [ ] Siden fungerer lokalt uten eksterne avhengigheter utover det som er dokumentert.

### Sprint 3 – Automatisering og publisering
- [ ] GitHub Actions-workflow med ukentlig cron og `workflow_dispatch` er satt opp, med riktig tidspunkt i norsk tid både sommer og vinter.
- [ ] En manuell kjøring i GitHub er fullført og har oppdatert data og nettsiden på GitHub Pages.
- [ ] En simulert kildefeil fører til at resten fullføres og feilen vises på siden.
- [ ] «Ny»-merking og flytting til `data/arkiv.json` virker og er testet.

### Sprint 4 – Direktorater, prioritet 1
- [ ] Alle prioritet 1-kilder i avsnitt 2 som ikke kom med i sprint 1 er lagt til eller satt til `aktiv: false` med begrunnelse.
- [ ] Deduplisering mot regjeringen.no er testet med minst to konkrete eksempler.
- [ ] Stikkprøver er gjennomført for hver ny kilde.

### Sprint 5 – Direktorater, prioritet 2 og 3
- [ ] Alle prioritet 2- og 3-kilder er lagt til eller satt til `aktiv: false` med begrunnelse.
- [ ] Filtre for kategori og prioritet virker med alle kilder.
- [ ] Stikkprøver er gjennomført for hver ny kilde.
- [ ] Total kjøretid for innhentingen er målt og holder seg under 30 minutter.

### Sprint 6 – Høringsparter og regionflagg
- [ ] Høringsparter hentes der kildene har dem, og kategoriseres.
- [ ] Regionflagget settes ut fra søkeordene i konfigurasjonen, inkludert «alle kommuner».
- [ ] Minst tre høringer der kommunene er kjent høringsinstans er verifisert med riktig flagg.
- [ ] Minst tre høringer uten regionen som høringspart er verifisert uten flagg (ingen falske treff).
- [ ] Full liste kan utvides på nettsiden.

### Sprint 7 – Gjøvik kommunes postliste
- [ ] Postlista hentes med metoden som ble godkjent i sprint 0.
- [ ] Filtrering på søkeord og 14-dagersvindu virker.
- [ ] Kobling mot høringene er testet med minst fem kjente høringsbrev fra postlista, med treffkvalitet dokumentert.
- [ ] Terskelen for «Mulig treff» er begrunnet ut fra testresultatene.
- [ ] Seksjonen for postlistetreff uten kobling vises.
- [ ] Hvis postlista feiler, fullføres resten av oppdateringen.

### Sprint 8 – KI-sammendrag og ferdigstilling
- [ ] Sammendrag lages med Anthropic API (`claude-sonnet-4-6`) og caches per høring.
- [ ] Uten API-nøkkel brukes ingressen, uten at kjøringen feiler.
- [ ] Ti sammendrag er vurdert i rapporten mot originalteksten for korrekthet og klarspråk.
- [ ] README er komplett og testet ved at oppsettet er fulgt fra bunnen.
- [ ] Hele sjekklisten i `CLAUDE.md` er kjørt for hele løsningen samlet, ikke bare siste sprint.
