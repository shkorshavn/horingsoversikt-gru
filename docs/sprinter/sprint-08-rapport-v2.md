# Sprint 8 – KI-sammendrag og ferdigstilling (rapport v2)

Versjon 2 bygger videre på [rapport v1](sprint-08-rapport.md). Den tar med endringene du ba om
27.10.2026 kl. 21.50. Alt som står i v1 gjelder fortsatt. Unntaket er punktene som er
oppdatert her.

## Sammendrag
Hver høring har fått en kort KI-begrunnelse for hvorfor den er relevant for Gjøvikregionen.
Den står under KI-sammendraget. KI-en vurderer også om høringen er relevant i det hele tatt.

Høringer som vurderes som ikke relevante, er flyttet ut av listen. De står i en sammenfoldet
seksjon, «Utelatte høringer», nederst. Hver har lenke og én linje om hvorfor den er utelatt.
Ingen høringer fjernes helt.

Resultatet fra den ekte kjøringen:
- 44 av 127 åpne høringer ble utelatt.
- Alle de fem høringene du nevnte, er utelatt.
- Høringer der regionen er høringspart, som Gjøvik kommune har mottatt, eller som kommer fra
  Innlandet fylkeskommune eller Statsforvalteren, utelates aldri.

Hele sjekklisten er kjørt på nytt, og alle punktene er bestått. Jeg anbefaler at sprinten
godkjennes.

## Hva som er bygget

**«Hvorfor relevant» og relevansvurdering** (`horinger/relevans.py`, ny)
- **Svar:** for hver høring gir modellen JSON: `{"relevant": true/false, "hvorfor": "..."}`.
  - En relevant høring får høyst 25 ord om hva i høringen som berører kommunene eller regionen.
  - En høring som ikke er relevant, får høyst 15 ord om hvorfor den er utelatt.
- **Grunnlag:** samme tekst som sammendraget (avsender, tittel, ingress og detaljtekst).
- **Instruksen inneholder:**
  - en beskrivelse av regionen (de fem kommunene, Mjøsa, industri, landbruk, NTNU i Gjøvik,
    sykehus, Gjøvikbanen og rv. 4)
  - en kriterieliste over hva som er relevant og hva som ikke er det
  - dine fem eksempler.

  Er modellen i tvil, regnes høringen som relevant. Den skal ikke legge til geografi som ikke
  står i teksten.
- **Innstillinger i `sources.yaml`** (`felles.relevans`): `region`, `ikke_relevant_eksempler`
  og `aldri_utelat_niva`. Du kan legge til flere eksempler selv. Instruksen inngår i
  sjekksummen, så da vurderes alle høringene på nytt ved neste ukentlige oppdatering.
- **Vern:** høringer med regionflagg, treff i postlista eller avsender fra fylkeskommunen eller
  Statsforvalteren utelates aldri. Seks høringer ble holdt i listen på denne måten.
- **Buffer og kostnad:** `data/relevans.json`, på samme måte som sammendragene. Modell og
  grenser er de samme som for sammendraget (`claude-sonnet-5-5`). Fremover vurderes bare nye
  eller endrede høringer.
- **Når:** i samme steg som sammendraget («KI-sammendrag og relevans» i `publiser.yml`), bare
  ved den ukentlige oppdateringen. Feiler det ene, går det andre som normalt. Uten vurdering står
  høringen i listen som før.

**Nettsiden** (`index.html`, `side/app.js`, `side/stil.css`)
- Linjen «KI: Hvorfor relevant …» står under sammendraget.
- **«Utelatte høringer (N)»** er sammenfoldet under listen. Hver linje har:
  - tittel med lenke
  - avsender og frist
  - «Utelatt: …» med begrunnelsen.
- Filtrene og søket gjelder også de utelatte. Seksjonen skjules når ingen passer.
- Antallet øverst («… åpne totalt») teller bare høringene i listen.
- CSV har den nye kolonnen «Hvorfor relevant (KI)». CSV og utskrift tar bare med hovedlisten.

**Omstrukturering:** den felles API-logikken i `horinger/sammendrag.py` er trukket ut i
`kall()`, `felter()` og `kjor_oppgave()`, slik at relevansvurderingen bruker samme buffer,
feilhåndtering og nøkkelhåndtering. Sammendragene er ikke laget på nytt.

**Nye filer:**
- `horinger/relevans.py`
- `tests/test_relevans.py`
- `docs/sprinter/sprint-08-rapport-v2.md`

**Endrede filer:**
- `horinger/sammendrag.py`, `horinger/bygg.py`
- `sources.yaml`
- `.github/workflows/publiser.yml`
- `index.html`, `side/app.js`, `side/stil.css`
- `tests/test_nettside.py`
- `README.md`

## Kvalitetssikring (hele løsningen, kjørt på nytt 27.10.2026 kl. 22.15)
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **392 bestått, 0 feilet, 0 hoppet over** (51,6 s). Nye: 15 i `test_relevans.py` og 4 i `test_nettside.py` (hvorfor-linjen, utelatte, ingen seksjon uten utelatte, ikke på utskrift). axe-testen kjøres nå med utelatte høringer og hvorfor-linjer (375 og 1280 px). Arbeidsflyten «Tester» er grønn |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «92 files already formatted». `actionlint`: ingen funn |
| C. Ekte data | Bestått | Publisering 27.10. kl. 22.11 (workflow_dispatch, run 40583741951): alle stegene «success». 127 av 127 åpne høringer er vurdert: **83 relevante og 44 utelatt**. 6 høringer er holdt i listen av vernet. Kildene er ikke hentet på nytt. Status fra v1 gjelder: 28 kilder og postlista er «ok» |
| D. Stikkprøver | Bestått | Ingen kilder er endret. Stikkprøvene fra v1 gjelder. Relevansvurderingen er kontrollert mot teksten, se egne tabeller |
| E. Tegn og datoer | Bestått | `data/relevans.json` har ingen `\u00`-koder. Æ, ø og å er riktige på siden (skjermbilde lokalt med ekte data). Fristene i «Utelatte høringer» vises i norsk format, f.eks. «Frist 28. oktober 2026» |
| F. Feilhåndtering | Bestått | Testene viser: ugyldig svar (ikke JSON, eller «relevant» ikke true/false) regnes som feil og prøves igjen. Uten nøkkel feiler ingenting. Et brudd i sammendragssteget stopper ikke relevanssteget. Høringer uten vurdering vises i listen. Nøkkelen skrives ikke til loggen |
| G. Kodegjennomgang | Bestått etter retting | `git diff 802a254..HEAD` (uten data): 11 filer, 595 nye og 40 fjernede linjer. Se avsnittet under |
| H. Høflighet | Bestått | Ingen nye kall til kildene. Relevansvurderingen bruker bare tekst som allerede er hentet |
| I. Dokumentasjon | Bestått | Nytt avsnitt i README: «Relevans for Gjøvikregionen» (justering, vern, buffer, visning). «Nettsiden» og «Status» er oppdatert. Kommentarer i `sources.yaml` for `felles.relevans` |
| J. Akseptansekriterier | Bestått | Kriteriene for sprint 8 fra v1 er uendret og oppfylt. Tilleggene fra deg står i tabellen under |

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| 1–5 (spesifikasjonen, sprint 8) | Ja | Se v1. Uendret |
| Tillegg 27.10 kl. 00.08: delt visning | Ja | Se v1 |
| Tillegg 27.10 kl. 21.50: «Hvorfor er høringen relevant for Gjøvikregionen eller kommunene?» | Ja | 75 av 83 relevante høringer har en begrunnelse. De 8 uten er 6 høringer som er holdt i listen av vernet (der passer ikke begrunnelsen for å utelate) og 2 med for tynt grunnlag. Skjermbilde: sukkeravgiften har «KI: Hvorfor relevant: Avgiftsfritaket for sukker utvides til å gjelde også små håndverksbakerier og kafeer, som finnes i alle kommunene …». Test `test_hvorfor_relevant_vises_under_sammendraget` |
| Tillegg 27.10 kl. 21.50: irrelevante høringer utelates, med oversikt og klikk til mer info | Ja | Dine fem eksempler er utelatt, se tabellen under. «Utelatte høringer (43)» vises med lenke og begrunnelse (43, ikke 44, fordi én har prioritet 3 og skjules av standardfilteret). Test `test_utelatte_hoeringer_er_samlet_nederst` |

## Dine eksempler
| Høring | Resultat | Begrunnelse fra KI-en |
|---|---|---|
| Ny ruteplan for kystruten Bergen–Kirkenes | Utelatt | «Gjelder bare rutetider for kystruten Bergen–Kirkenes.» |
| Lønnsvilkår på skip (tariffavtaler) | Utelatt | «Gjelder bare lønnsvilkår på skip, en næring som knapt finnes i regionen.» |
| Næringsmiddelforskrifter for Svalbard | Utelatt | «Gjelder bare at næringsmiddelforskrifter skal gjelde for Svalbard.» |
| CO2-kompensasjon for fiskeflåten | Utelatt | «Gjelder bare CO2-kompensasjon for fiskeflåten.» |
| Regionale ruteflyginger i Nord-Norge | Utelatt | «Gjelder bare regionale ruteflyginger (FOT-ruter) i Nord-Norge.» |

Disse fem står som eksempler i instruksen, så de er ingen ren test. Det som viser at KI-en har
forstått mønsteret, er de lignende høringene den også utelot:
- CO2-avgift for sjøfart
- havbruk (MTB)
- avfall fra skip i havner
- marine ressurser i Grunnloven
- petroleumsskatt (to høringer)
- havneanlegg i Strömstad.

## Kontroll av relevansvurderingen
**Utelatte høringer (44).** Jeg har lest alle. De fleste er klart utenfor regionen:
- Kysten, havet, Svalbard, Nord-Norge og Sverige.
- Smale finansregler: IRB-banker, verdipapirfond, folkefinansiering og oljefondets etiske
  rammeverk.
- Rene statlige saker: påtalemyndigheten, Etterretningstjenesten og utlendingsinternatet.
- Tekniske produktregler: juice, syltetøy, honning, kondensert melk, ladere og kjemikalielister.

**Grensetilfeller du bør se på** (disse kan være riktige å vise):

| Høring | KI-ens vurdering | Merknad |
|---|---|---|
| Klimakvoteforskriften (dokumentasjonskrav) | Utelatt | Kan angå kvotepliktig industri i regionen |
| Politiloven (innbringelse av barn) | Utelatt | Kan berøre barnevernet i kommunene |
| Eiendomsmegling (forenklinger) | Utelatt | Smalt, men gjelder boligmarkedet |
| Tidlig tilgang til legemidler for alvorlig syke | Utelatt | Gjelder sykehus, ikke kommunene |
| Samiske spesialisthelsetjenester | Utelatt | Gjelder samiske områder |
| Karbonfangst Kirkenær (Grue) | Utelatt | Innlandet, men utenfor regionen. Karbonfangst på Hamar er tatt med fordi utslippet går til Mjøsa |
| Personlige kjennemerker | Med | Svak begrunnelse («gjelder alle bilister») |
| E6 Sjoa–Otta (Nye Veier) | Med | Innlandet, men utenfor regionen |

**Stabilitet:** vurderingen ble kjørt to ganger, før og etter at instruksen ble strammet inn.
Tre grensetilfeller byttet side mellom kjøringene: eiendomsmegling, kjennemerker og E6
Sjoa–Otta. De klare tilfellene var stabile. Er du uenig i et grensetilfelle, kan du legge det
til i `ikke_relevant_eksempler`.

**«Hvorfor relevant»:** 15 begrunnelser er kontrollert mot teksten, og nøkkelordene er søkt
opp. Eksempler:
- Skatteregnskapet (landstotal)
- E6 Sjoa–Otta (rundkjøring ved rv. 15)
- Karbonfangst på Hamar (HIAS og Mjøsa)
- Sivilforsvaret (ulempe- og ledertillegg)
- Lootbokser (KS høringsinstans)
- Forsvarsindustri (Nammo høringsinstans)
- Kringkasting (Radio Toten)
- Sukkeravgiften.

12 av 15 er fullt dekket av teksten. Tre bruker allmennkunnskap som ikke står i teksten, men
som er riktig:
- at kommunene følger opp granulat på idrettsbaner
- at krematorier ofte er kommunale eller kirkelige
- «i stedet for kommunens egen skatt» i skatteregnskapssaken.

Lengde: høyst 27 ord, gjennomsnitt 18.

## G. Kodegjennomgang
**Funnet og rettet:**
- **Første kjøring, med instruksen før innstrammingen:**
  - Én begrunnelse hadde feil geografi: Strömstad «på Vestlandskysten av Østfold/Viken-siden».
  - Én trakk inn rv. 4 uten grunn (røntgen ved bergarbeid).
  - Snittet var 24 ord, og to begrunnelser var over 30.

  Instruksen er strammet inn: høyst 25 og 15 ord, ingen tillagt geografi, og regionens egne
  prosjekter nevnes bare når høringen gjelder dem direkte. Etter ny kjøring er feilene borte.
- **To høringer manglet vurdering** etter første kjøring (tidsavbrudd eller ugyldig svar). De
  ble vurdert ved neste kjøring, slik buffer og feilhåndtering skal gjøre.

**Vurdert og beholdt:**
- Logikken for API-kall er felles og ikke duplisert.
- Region, eksempler og vern står i konfigurasjon, ikke i koden.
- `vurder()` har ingen nettverkskall og er testet for alle vernetilfellene.
- JSON tolkes med en regex som tåler tekst rundt svaret, og alt annet gir feil og et nytt
  forsøk.

## Kjente feil og begrensninger
1. **Grensetilfeller kan bytte side** mellom kjøringer, fordi KI-en ikke er helt stabil. Nye
   høringer vurderes bare én gang, så det skjer bare når instruksen eller teksten endres.
2. **Begrunnelsene bruker av og til allmennkunnskap** som ikke står i høringen. Det har vært
   riktig i det jeg har kontrollert, og linjen er merket «KI».
3. **Ikke relevant er en vurdering, ikke en sannhet.** Seksjonen «Utelatte høringer» står
   derfor alltid på siden, og CSV og utskrift tar den ikke med.
4. **Ekstra kostnad i dag:** to fulle kjøringer, ca. 254 kall. Det koster trolig under 1 dollar.
5. Punktene 1–5 fra v1 gjelder fortsatt.

## Forslag til senere arbeid
- Mulighet for at du selv kan overstyre én høring (alltid med eller alltid utelatt) i
  `sources.yaml`.
- Eksempler på høringer som alltid er relevante, i tillegg til de som ikke er det.
- Forslagene fra v1: tekst til Stortinget-høringene, Message Batches API, flere postlister og
  Udir.

## Hva Svein bør sjekke selv
1. **Utelatte høringer:** åpne siden, rull til bunnen av listen og fold ut «Utelatte høringer».
   Er det noe der som burde stått i listen? Se særlig grensetilfellene over. Gi meg titlene, så
   legger jeg dem inn som eksempler, eller legg dem inn selv.
2. **«Hvorfor relevant»:** les noen begrunnelser, f.eks. for skatteregnskapet, fellesskolen og
   tilfluktsstedene. Er lengden og formen nyttig?
3. **Antallet:** øverst står nå «Viser 82 høringer (83 åpne totalt …)», som bare teller
   høringene i listen.
