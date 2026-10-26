# Sprint 6 – Høringsparter og regionflagg

## Sammendrag
For hver høring vises nå hvem den er sendt til, så langt kilden oppgir det. Listen er kort
kategorisert, og hele listen kan foldes ut. Er regionen høringspart, står det et tydelig flagg
under tittelen. Det gjelder de fem kommunene, Ringsaker, Lillehammer, Gjøvikregionen (IPR),
regionråd, «alle kommuner», «alle fylkeskommuner», KS og Innlandet fylkeskommune. Høringen
løftes da til høy prioritet. Det nye filteret «Bare høringer der regionen er høringspart»
virker. Regjeringen.no har også fått saksfelt.

Med ekte data har 54 av 133 åpne høringer en liste. 42 høringer har regionflagg, 40 av dem fra
regjeringen.no. Ruff og testene kjører nå ved hver push.

Alle punktene i sjekklisten er bestått. Underveis fant og rettet jeg en alvorlig feil i
tolkingen av robots.txt (se H). Ett forhold bør du ta stilling til før godkjenning: KS står på
nesten alle departementenes høringslister. 18 høringer har derfor flagg bare fordi KS er
høringspart (se «Kjente feil og begrensninger»). Jeg anbefaler at sprinten godkjennes, med
svaret ditt på KS-spørsmålet.

## Hva som er bygget

**Høringsparter** (`horinger/horingsparter.py`, ny)
- Listen leses fra detaljsiden. Programmet ser etter overskrifter som «Høringsinstanser»,
  «Høringsliste» eller «Mottakerliste», og listen slutter ved neste avsnitt («Kontakt»,
  «Høringsbrev» o.l.). Gruppeoverskrifter og innledninger hoppes over.
- Står listen i en PDF, leses den med `pypdf`, men bare der robots.txt tillater det.
  Adresser, postnummer og poststed fjernes, og navn som er brutt over to linjer, slås sammen.
- Uten liste lagres en merknad med høringen:
  - «Åpen for alle»: siden sier at alle kan svare.
  - «Ikke tilgjengelig»: listen finnes, men er sperret i robots.txt. Lenken vises.
  - «Ikke oppgitt»: siden har ingen liste.
- Listen lagres med høringen i `data/kilder/` og brukes om igjen ved neste kjøring. Bare nye
  høringer koster dermed ekstra kall. Endres tolkingen, får den et nytt versjonsnummer
  (`DETALJ_VERSJON`), og da leses alle åpne høringer på nytt.
- Kategorier og regionflagg beregnes ved byggingen ut fra `felles.horingsparter` i
  `sources.yaml`. Endringer i ordlistene slår dermed inn uten ny henting.

**Regionflagg**
- Hver høringspart vurderes for seg, og bare listen brukes, ikke teksten ellers.
- «Gjøvik kommune» gir flagg. Det gjør verken «Gjøvik tingrett», «Sykehuset Innlandet, Gjøvik»
  eller en postadresse i Lillehammer.
- «Kommunene i Troms» gir ikke flagg, men «alle kommuner i Innlandet» gjør det. KS Bedrift
  utelates.
- Nynorske former («Kommunane», «Fylkeskommunane») gir også flagg.
- Har høringen flagg, løftes prioriteten til høy med grunnen «regionen er høringspart»
  (`horinger/prioritet.py`).
- Ved deduplisering hentes listen fra den andre versjonen når versjonen som vises, mangler den
  (`horinger/dedup.py`).

**Regjeringen.no.** Høringsinstanser og saksfelt hentes fra detaljsidene på GRUs PC
(`Regjeringen.detaljfelt`). Den første kjøringen hentet 53 detaljsider på 136 sekunder. Senere
kjøringer henter bare nye høringer.

**Nettsiden** (`side/app.js`, `side/stil.css`, `index.html`)
- «Regionen er høringspart: …» står under tittelen.
- Under ingressen vises «Høringsparter: Alle kommuner, Organisasjoner (42), Andre (40)», eller
  merknaden.
- «Vis alle høringsparter (107)» folder ut hele listen. Det er et `<details>`-element, som
  virker med tastatur og skjermleser.
- Saksfelt vises i detaljlinjen.
- Søket leter også i høringspartene og saksfeltet.
- Nytt filter: «Bare høringer der regionen er høringspart» (`?regionpart=1`).
- CSV har tre nye kolonner: «Regionen er høringspart», «Høringsparter» (kategorier) og
  «Saksfelt».
- Utskriften tar med flagg og kategorier, men ikke hele listen.

**Tester ved push.** Den nye arbeidsflyten `.github/workflows/tester.yml` kjører ruff og pytest ved
hver push til `main`.

**Utforsking fra PC-en.** Arbeidsflyten `.github/workflows/utforsk-pc.yml` og
`verktoy/lagre_gren.py` henter rå sider fra regjeringen.no via GRUs PC og legger dem på grenen
`utforsk-pc`. Arbeidsflyten startes bare manuelt.

**Nye filer:** `horinger/horingsparter.py`, `tests/test_horingsparter.py`,
`tests/fixtures/horingsparter/` (19 ekte sider og PDF-er), `tests/fixtures/regjeringen_robots.txt`,
`.github/workflows/tester.yml`, `.github/workflows/utforsk-pc.yml`, `verktoy/lagre_gren.py`.

**Endrede filer:** `horinger/kilder/base.py`, `horinger/kilder/regjeringen.py`, `horinger/kjor.py`,
`horinger/bygg.py`, `horinger/dedup.py`, `horinger/prioritet.py`, `horinger/modell.py`,
`horinger/nett.py`, `sources.yaml`, `requirements-kjoring.txt` (pypdf), `side/app.js`,
`side/stil.css`, `index.html`, `README.md`, `tests/test_nett.py`, `tests/test_nettside.py`.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **305 bestått, 0 feilet, 0 hoppet over** (42,7 s). 77 tester er nye: 66 i `test_horingsparter.py`, 9 i `test_nettside.py` og 2 i `test_nett.py`. Arbeidsflyten «Tester» er grønn på commit bcb60c5 |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «77 files already formatted». Offentlige funksjoner har type hints og docstring på norsk |
| C. Ekte data | Bestått | Kjøringen 26.10. kl. 21.23–21.29: 27 kilder, alle «ok», og 133 åpne høringer. Samlet kjøretid er 425 s, hvorav regjeringen.no tok 136 s. 54 høringer har liste. Av de 79 uten liste er 42 «Åpen for alle», 26 «Ikke oppgitt» og 11 «Ikke tilgjengelig». Se tabellen under |
| D. Stikkprøver | Bestått etter retting | 22 høringer fra 8 kilder er kontrollert, se tabellen. To avvik ble funnet og rettet: «proLAR» ble slått sammen med linjen over (regjeringen.no), og «DNV AS» falt ut av en PDF-liste (DMP) |
| E. Tegn og datoer | Bestått | Æ, ø og å er riktige i JSON (ikke `\u00..`-koder) og på siden («Høringsparter», «Åpen for alle», «Nordre Land kommune»). Datoformatene er uendret fra sprint 5. Frist og «dager igjen» regnes i Europe/Oslo |
| F. Feilhåndtering | Bestått | Tester: én høring som feiler (tidsavbrudd), stopper ikke resten, og prøves igjen neste gang. En PDF som er sperret i robots.txt, gir «Ikke tilgjengelig» med lenke. Ekte kjøring 26.10. kl. 13.02: Bane NOR fikk tidsavbrudd, og resten fullførte. Feilen er logget og står i `status.json` som «feil» (vist i statusoversikten, testet siden sprint 3) |
| G. Kodegjennomgang | Bestått etter retting | `git diff 6a1e202..HEAD` (godkjenningen av sprint 5): 23 filer og 1693 nye linjer, se eget avsnitt |
| H. Høflighet | Bestått etter retting | User-Agent og pause er som før. Alle detaljsider og PDF-er går gjennom robots-sjekken. **Feil funnet og rettet:** robots.txt med BOM ble lest feil (se eget avsnitt) |
| I. Dokumentasjon | Bestått | README har nytt avsnitt «Høringsparter og regionflagg», og avsnittene Nettsiden, Tester, Kilder og Høflighet er oppdatert. `sources.yaml` forklarer reglene og har `horingsparter` per kilde, med begrunnelse der listen er sperret |
| J. Akseptansekriterier | Bestått | Se tabellen under |

### C. Ekte data per kilde (26.10.2026 kl. 21.29)

| Kilde | Åpne | Liste over høringsparter |
|---|---|---|
| Regjeringen.no | 52 | 50 med liste, 2 «Åpen for alle» uten liste. 35 har saksfelt. 40 har regionflagg |
| Stortinget | 38 | «Åpen for alle» (fast merknad: alle kan melde seg på komitéhøringer) |
| Miljødirektoratet | 11 | 1 «Ikke tilgjengelig» (vedleggstjenesten er sperret i robots.txt), 10 «Ikke oppgitt» |
| Mattilsynet | 9 | «Ikke oppgitt». Høringene går via hoering.no, og siden har ingen liste |
| Statens vegvesen | 7 | 6 «Ikke tilgjengelig» (robots.txt sperrer `*.pdf`), 1 «Åpen for alle» |
| Skatteetaten | 4 | «Ikke tilgjengelig» (robots.txt sperrer `/contentassets`) |
| Innlandet fylkeskommune | 4 | «Ikke oppgitt» (planvarsler uten liste) |
| Helsedirektoratet | 2 | Liste på siden (65 og 12) og «Åpen for alle» |
| DMP | 2 | Liste i PDF (86 og 46) |
| Nkom, NVE, DSB, Arbeidstilsynet | 1 hver | Arbeidstilsynet: «Åpen for alle». De andre: «Ikke oppgitt» |
| 15 andre kilder | 0 | Ingen åpne høringer i dag (som i sprint 5) |

0 åpne er forventet for de 15 kildene: tallene er de samme som i sprint 5. Landbruksdirektoratet,
DiBK og Digdir har høringer, men alle har utløpt frist. Utløpte høringer slås ikke opp.

## Stikkprøver
Høringspartene er kontrollert mot kildens side eller PDF. For regjeringen.no er listen lest
uavhengig fra «Høringsinstanser»-boksen og sammenlignet linje for linje. Tittel, instans, frist
og lenke for regjeringen.no er kontrollert mot `DC.Title`, `DC.Creator`, «Høringsfrist:» og
`og:url` på siden. For etatene er disse feltene uendret siden sprint 4 og 5.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Regjeringen.no | Fylkeskommunale tannhelsetjenester (HOD) | tittel, instans, frist 19.01.2027, 362/362 parter, saksfelt (ingen), flagg Alle kommuner/Alle fylkeskommuner/KS | Første versjon ga 361: «proLAR» ble slått sammen med linjen over. **Rettet** | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-ny-lov-om-fylkeskommunale-tannhelsetjenester-mv/id3178971/) |
| Regjeringen.no | Forskrift om tilfluktssteder (JD) | tittel, instans, frist 30.10.2026, 107/107, saksfelt «Samfunnssikkerhet og beredskap», flagg Alle kommuner/Alle fylkeskommuner/KS | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forskrift-om-tilfluktssteder/id3166695/) |
| Regjeringen.no | Saksbehandlings- og klageregler i opplæringsloven (KD) | tittel, instans, frist 07.01.2027, 111/111, saksfelt «Skole og videregående opplæring», flagg (nynorsk «Kommunane», «Fylkeskommunane») | Først uten flagg for nynorsk. **Rettet** | [side](https://www.regjeringen.no/no/dokumenter/horing-av-forslag-til-endringer-i-enkelte-saksbehandlings-og-klageregler-i-opplaringsloven-og-opplaringsforskriften-mv/id3173894/) |
| Regjeringen.no | Smågruppeundervisning og leksehjelp (KD) | tittel, instans, frist 07.01.2027, 110/110, flagg | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-opplaringsloven-og-privatskolen-smagruppeundervisning-og-leksehjelp/id3170886/) |
| Regjeringen.no | Ordningen Arktis 2030 (KDD) | tittel, instans, frist 01.12.2026, 110/110 | Ingen avvik fra siden, men siden viser samme liste som KDs høringer (se begrensninger) | [side](https://www.regjeringen.no/no/dokumenter/horing-horing-om-endring-i-forskrift-om-ordningen-arktis-2030/id3176630/) |
| Regjeringen.no | Pengespillforskriften (KUD) | tittel, instans, frist 29.11.2026, 150/150, saksfelt «Lotteri og pengespill», **ingen flagg** | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-pengespillforskriften/id3171815/) |
| Regjeringen.no | Tilskuddsordning for forsvarsindustri (FD) | tittel, instans, frist 01.12.2026, 22/22, saksfelt «Forsvar», «Forsvarsindustri», **ingen flagg** | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-av-forslag-til-forskriftsfestet-tilskuddordning-for-okt-produksjonskapasitet-i-norsk-forsvarsindustri/id3178998/) |
| Regjeringen.no | Strategi for besøkssentre for natur (KLD) | tittel, instans, frist 31.12.2026, «Åpen høring» → «Åpen for alle», saksfelt «Naturmangfold», **ingen flagg** | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-strategi-for-besokssentre-for-natur-2027-2037/id3173330/) |
| Regjeringen.no | Kystruten Bergen–Kirkenes (SD) | tittel, instans, frist 28.10.2026, 123/123, saksfelt «Kollektivtransport». Helgeland regionråd, Fjordane IPR o.l. gir ikke flagg | Ingen. Flagg «KS», fordi KS står i listen (se begrensninger) | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-ny-ruteplan-for-kystruten-bergen-kirkenes/id3169361/) |
| Helsedirektoratet | Retningslinje for mat, måltider og ernæring | 65/65 parter (gruppeoverskrifter utelatt), «Åpen for alle», flagg Alle kommuner/KS | Ingen | [side](https://www.helsedirektoratet.no/horinger/retningslinje-for-mat-maltider-og-ernaering-i-helse-og-omsorgstjenesten) |
| Helsedirektoratet | Breddekompetanse i legenes spesialistutdanning | 12/12 parter, ingen flagg | Første versjon tok med «Referansegruppens medlemmer, herunder …» og kontaktpersonen. **Rettet** | [side](https://www.helsedirektoratet.no/horinger/breddekompetanse-i-legenes-spesialistutdanning-innspillsrunde) |
| DMP | Forskrift for medisinsk utstyr | PDF: 90 linjer, fire navn brutt over to linjer → 86 parter, flagg KS | «DNV AS» falt ut (tatt for et poststed). **Rettet** | [side](https://www.dmp.no/nyheter/horing-om-endringer-i-forskrift-for-medisinsk-utstyr--kvalitetsstyring-og-samsvarsvurdering) |
| DMP | Grossistforskriften §§ 5 og 5a | PDF: 47 linjer, én dobbel → 46, ingen flagg | Ingen | [side](https://www.dmp.no/nyheter/horing---forslag-til-endringer-i-grossistforskriften--5-og-5a) |
| Skatteetaten | Alle 4 åpne | «Ikke tilgjengelig» med lenke. Loggen viser «sperret i robots.txt» for alle fire PDF-ene | Ingen (etter rettingen i H) | [liste](https://www.skatteetaten.no/rettskilder/type/horinger/) |
| Statens vegvesen | 6 regelverkshøringer | «Ikke tilgjengelig» med lenke til PDF-en. Loggen viser at alle seks er sperret | Ingen | [liste](https://www.vegvesen.no/fag/publikasjoner/hoeringer/) |
| Statens vegvesen | Parkeringsforskriften | «Åpen for alle» (dokumentet heter «Offentlig høring …») | Ingen | [side](https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing-om-parkeringsforskriften-21-219359/) |
| Arbeidstilsynet | Røntgenundersøkelse ved bergarbeid | «Åpen for alle». Siden har ingen liste, og listesiden sier «Alle kan gi innspill» | Ingen | [side](https://www.arbeidstilsynet.no/regelverk/horinger/horing/?hearingId=3884) |
| Landbruksdirektoratet | Omregningsfaktor for roesnitter (utløpt) | PDF: 11/11 parter, adresser fjernet, adressen i Moelv gir ikke flagg | Ingen | [side](https://www.landbruksdirektoratet.no/nb/om-direktoratet/horinger/horing-forslag-til-omregningsfaktor-for-lettmelasserte-roesnitter-i-forskrift-om-omregningsfaktorer-for-ravarer) |

Mattilsynet, Miljødirektoratet («Ikke oppgitt»), NVE, DSB og Nkom er kontrollert på 1–2 sider
hver: ingen av dem har en liste på siden.

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| 1. Høringsparter hentes der kildene har dem, og kategoriseres | Ja | 54 åpne høringer har liste (regjeringen.no 50, Helsedirektoratet 2 og DMP 2). Kategoriene vises på siden og i CSV. Der listen ikke kan leses, sier merknaden hvorfor |
| 2. Regionflagget settes ut fra søkeordene i konfigurasjonen, inkludert «alle kommuner» | Ja | `felles.horingsparter.regionflagg` i `sources.yaml`. 20 tester med treff (også nynorsk) |
| 3. Minst tre høringer med kommunene som kjent høringsinstans, verifisert med riktig flagg | Ja | Tannhelsetjenester (HOD), tilfluktssteder (JD), opplæringsloven saksbehandling (KD) og Helsedirektoratets mat og måltider. Alle er kontrollert mot siden og ligger som tester med ekte sider |
| 4. Minst tre høringer uten regionen, verifisert uten flagg | Ja | Pengespill (KUD, 150 parter), forsvarsindustri (FD, 22), besøkssentre (KLD, åpen), Helsedirektoratets breddekompetanse (12) og DMPs grossistforskrift (46). Kystruten var tenkt som negativt eksempel, men KS står i listen, så den har flagg (se under). 14 tester av ord som ikke skal treffe |
| 5. Full liste kan utvides på nettsiden | Ja | «Vis alle høringsparter (N)» med `<details>`. Testen åpner den med tastaturet (Enter). Axe-testene er grønne |

## G. Kodegjennomgang
Jeg leste hele diffen mot godkjenningen av sprint 5 (`git diff 6a1e202..HEAD`).

**Funnet og rettet:**
- Sider limt inn fra Word mangler overskrifter som avgrenser listen. Listen stopper nå ved løpende
  tekst eller ved «Kontakt», «Høringsbrev» o.l.
- Linjer ble slått sammen også på nettsider («proLAR»). Nå skjer det bare i PDF.
- Store bokstaver ble tolket som poststed, også for «DNV AS». Firmanavn unntas nå.
- Lagrede lister ble brukt om igjen selv når tolkingen var endret. To planlagte kjøringer
  fra i dag ettermiddag (forsinket av GitHub) hadde lagret lister uten saksfelt. Løst med
  `DETALJ_VERSJON`.
- Navnet på en kommune alene gav flagg, og det kan være poststedet i en adresse. Nå gir bare
  «X kommune» flagg.
- En utdatert kommentar i `Regel` er rettet.

**Vurdert og beholdt:**
- Ordlistene for kategorier og flagg ligger i `sources.yaml`, ikke i koden. Høyst 60
  detaljsider per kilde og kjøring (`maks_per_kjoring`).
- Ingen hemmeligheter i koden. `GITHUB_TOKEN` hentes fra miljøet i `lagre_gren.py`.
- Lenker til lister brukes bare når de begynner med http(s) (`app.js`).

## H. Robots.txt med BOM (feil funnet og rettet)
Skatteetatens robots.txt begynner med et byte order mark (BOM), og svaret oppgir ikke tegnsett.
`requests` leste da filen som ISO-8859-1, og første linje ble «ï»¿User-agent: *». Regelen for
alle roboter ble ikke gjenkjent, og sperren for `/contentassets` ble ikke fulgt.

**Konsekvens:** To testkjøringer i dag (kl. 13.02 og 13.27) hentet de fire høringslistene i PDF
fra Skatteetaten. Det ble 8 kall til sperrede adresser. Den samme feilen gjorde at Stortingets
`Crawl-delay: 5` på www.stortinget.no ikke ble fulgt. Det gjaldt én utforskingsside i dag. Selve
innhentingen bruker data.stortinget.no.

**Retting:** robots.txt leses nå alltid som UTF-8 uten BOM (`robots_tekst` i `horinger/nett.py`),
og to tester dekker det. Den første rettingen (commit 68e89c4) var ikke nok, fordi teksten
allerede var feil dekodet. Den andre rettingen (2451048) er bekreftet i testkjøringen
kl. 13.47, der loggen viser «høringslisten er sperret i robots.txt» for alle fire. De hentede
listene er ikke lagret i `main`. Skatteetaten står som «Ikke tilgjengelig».

## Kjente feil og begrensninger
1. **KS står på nesten alle departementenes lister.** På regjeringen.no har 40 av 52 åpne
   høringer flagg. 17 av dem (18 med DMP) har flagg bare fordi KS står i listen, f.eks. kystruten, boliglån og
   eiendomsmegling. Slik du ba om, følger flagget regelen «KS gir flagg», men flagget skiller
   dermed dårligere. **Spørsmål til deg:** Skal KS alene fortsatt gi flagg og høy prioritet? To
   alternativer er å vise KS som en svakere merknad («KS er høringspart») uten løft, eller å
   kreve kommunene, fylkeskommunene, regionen eller Innlandet fylkeskommune for flagg. Endringen
   er én linje i `sources.yaml`.
2. **Listene som ikke kan leses:** Statens vegvesen (6), Skatteetaten (4) og Miljødirektoratet (1)
   har listene i PDF som robots.txt sperrer. De vises som «Ikke tilgjengelig», med lenke.
3. **Kilder uten liste på siden:** Mattilsynet, NVE, DSB, Nkom, Innlandet fylkeskommune og de fleste
   av Miljødirektoratets høringer vises som «Ikke oppgitt». DiBK, Mattilsynet, DSB og
   Arbeidstilsynet har egne høringsløsninger der listen kanskje står. De er ikke undersøkt.
4. **Arktis 2030 (KDD)** viser på regjeringen.no samme liste som KDs opplæringshøringer, med
   «Kommunane» og KS. Vi viser det som står på siden.
5. **Utskrift:** høringer med høringsparter får én linje mer. 60 slike høringer tar fire
   A4-sider. Uten høringsparter er det tre, som før (begge er testet).
6. **Saksfelt** vises og kan søkes i, men har ikke eget filter. Bare regjeringen.no har saksfelt.

## Forslag til senere sprinter
- Filter på saksfelt.
- Lese listene i DiBKs høringsløsning (hoering.dibk.no) og på hoering.no for Mattilsynet,
  Arbeidstilsynet og DSB, der robots.txt tillater det.
- Vise hvor mange høringer hver kommune i regionen står som høringspart i (per måned).

## Hva Svein bør sjekke selv
1. **Nettsiden med filteret:** https://shkorshavn.github.io/horingsoversikt-gru/?regionpart=1
   - Viser listen 42 høringer?
   - Åpne «Vis alle høringsparter» på «Høring av forskrift om tilfluktssteder», og sjekk at
     listen stemmer med
     [regjeringen.no](https://www.regjeringen.no/no/dokumenter/horing-forskrift-om-tilfluktssteder/id3166695/).
2. **En høring uten flagg:** søk etter «pengespill». Den skal ha 150 høringsparter og ikke noe
   flagg.
3. **KS-spørsmålet:** søk etter «kystruten». Den har flagget «Regionen er høringspart: KS». Er det
   slik du vil ha det (punkt 1 under begrensninger)?
4. **Utskrift:** krysse av for filteret og trykke «Skriv ut». Flagg og kategorier skal være med,
   men ikke hele listene.
5. **Tester ved push:** under Actions → «Tester» skal siste kjøring være grønn.
