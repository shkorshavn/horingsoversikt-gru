# Sprint 10 – Brukervennlighet på nettsiden

## Sammendrag
Alle de sju ønskene fra 28.10.2026 er levert:
- Filtrene har mindre skrift uten fet, og en ny deloverskrift: «Øvrige valg».
- Lenkene åpnes i ny fane.
- Utskriften er luftigere og tar med «KI: Hvorfor relevant».
- Prioritet vises uten tall.
- Verktøylinjen står i toppen.
- Søket tåler ulike skrivemåter og små skrivefeil.

Grensene for feiltoleransen i søket ble justert etter prøving mot de ekte høringene, se punkt 7.
Alle punktene i sjekklisten er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget
1. **Filtrene:**
   - Valgene har vanlig skriftvekt og 14 px skrift, mot 15 px før.
   - Årsaken til den fete skriften var en CSS-regel for feltoverskrifter som også traff
     valgene. Den er rettet.
   - Gruppeoverskriftene er halvfete som før.
   - Under arbeidet fant jeg at avkrysningsboksen krympet ved lange valg, for eksempel «Styring,
     digitalisering, juss og eiendom». Det er rettet og testet.
2. **Deloverskrift «Øvrige valg»** over de tre avkrysningsboksene: regionen er høringspart,
   mottatt av Gjøvik kommune og utløpt frist.
3. **Lenker i ny fane:**
   - Gjelder alle lenker til høringer og kilder: listen, «Også på», høringslisten, postlista og
     «Utelatte høringer».
   - Lenkene har `target="_blank"` og `rel="noopener"`.
   - Skjermlesere får beskjeden «Åpnes i ny fane» via `aria-describedby`.
4. **Utskriften:**
   - «KI: Hvorfor relevant» står på egen linje under sammendraget.
   - Fristen står i egen kolonne, og alt under tittelen har fast innrykk (som en tabulator).
   - Det er luft og en tynn strek mellom høringene.
   - Skriften er 8,5 pt, mot 7,5 pt før.
   - Eksempel med ekte data: `docs/sprinter/bilder/sprint-10-utskrift-eksempel.pdf`.
5. **Prioritet** vises som «Høy», «Middels» og «Lav» i filteret.
6. **Verktøylinjen i toppen:**
   - Antall, sortering, «Skriv ut», «Last ned som CSV» og fargeforklaringen står i et eget bånd
     nederst i toppen.
   - Båndet har samme kolonner som innholdet under, så verktøyene står rett over listen.
   - På PC står det alltid synlig, også når listen rulles.
   - På mobil brytes det over flere linjer.
   - Skjermbilde: `docs/sprinter/bilder/sprint-10-pc.png`.
7. **Søket:**
   - **Skrivemåte:** store og små bokstaver, punktum, bindestrek og mellomrom mellom bokstaver
     og tall regnes som like. «rv4», «Rv.4», «rv. 4», «rv 4», «RV-4» og «rv.  4» gir samme treff.
     Tall må stå alene, så «rv4» finner ikke «rv. 40».
   - **Små skrivefeil:**
     - Ord på 4–9 bokstaver tåler én skrivefeil, og ord på 10 eller flere tåler to.
     - En skrivefeil er en bokstav for mye, for lite, feil bokstav eller to bokstaver som har
       byttet plass.
     - De to første bokstavene må stemme.
     - Ord på 6 bokstaver eller mer sammenlignes også med starten av lengre ord, slik at
       «barnehave» finner «barnehageloven».
   - **Avvik fra planen:** planen sa to feil fra 8 bokstaver og sammenligning med starten av
     ord for alle lengder. Prøving mot de ekte dataene ga falske treff:
     - «barnehave» fant «barnevern».
     - «samer» fant «samarbeid».
     - «sitat» fant «Statens vegvesen».

     Grensene er derfor strammet inn, se tabellen under.

**Endrede filer:**
- `index.html`, `side/app.js`, `side/stil.css`
- `tests/test_nettside.py`
- `README.md`

**Nye filer:**
- `docs/sprinter/bilder/sprint-10-utskrift-eksempel.pdf`
- `docs/sprinter/bilder/sprint-10-pc.png`

## Søk mot de ekte dataene (127 høringer, 28.10.2026)
| Søk | Treff | Kommentar |
|---|---|---|
| barnehage / barnehave / barnehahgre | 5 / 5 / 5 | Like treff |
| skole / skloe | 23 / 8 | «skloe» finner ordet «skole», men ikke «skolene», «grunnskole» osv. (for kort til sammenligning med starten av ord) |
| kommune / kommnue | 53 / 44 | «kommnue» finner «kommune», «kommunene» osv., men ikke «kommunal» |
| energi / enrgi | 16 / 9 | Som over |
| klima / klmia | 16 / 16 | Like treff |
| jordbruk / jordbrk | 2 / 2 | Like treff |
| utdanning / utdaning | 17 / 16 | Nesten like |
| samarbeid / samrbeid | 19 / 19 | Like treff |
| helse / helsse | 36 / 26 | Som over |
| barnevern | 6 | Ikke lenger blandet med «barnehave» |
| samer | 10 | 9 med «samers» i teksten, og 1 med «saker» (én bokstav feil) |
| rv4 / rv. 4 | 0 / 0 | Ingen åpne høringer om rv. 4 i dag. Testet med testdata: alle seks skrivemåtene gir samme treff, og rv. 40 utelates |

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **423 bestått, 0 feilet, 0 hoppet over** (67,6 s). Nye: 6 for skrivemåter av vegnummer, 5 for skrivefeil, 3 mot falske treff («sitat», «fv33», «fv. 33»), korte ord, lenker i ny fane, verktøylinjen i toppen (står i ro ved rulling, over listen), filtrene (skriftvekt 400, «Øvrige valg», prioritet uten tall), utskrift med «Hvorfor relevant» og avkrysningsbokser som ikke krymper. Endret: to utskriftstester godtar flere sider (5 og 6 i stedet for 3 og 4) fordi luften er ønsket. Arbeidsflyten «Tester» kjøres ved push |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «96 files already formatted». `actionlint`: ingen funn. Skriptet sjekket for syntaks i Node |
| C. Ekte data | Bestått | Siden testet lokalt med de publiserte dataene på 1280 og 375 px (ingen vannrett rulling på mobil: scrollWidth 375). Søketabellen over er fra de ekte dataene. Ingen henting eller KI-kall i denne sprinten |
| D. Stikkprøver | Ikke relevant | Ingen kilder er endret |
| E. Tegn og datoer | Bestått | Søket bruker Unicode-klasser, så æ, ø og å behandles som bokstaver («gjøvik», «høring»). Utskriften viser æ, ø og å og norske datoer (PDF-eksempelet) |
| F. Feilhåndtering | Bestått | Søket tåler tomt søk, bare tegnsetting («...») og svært lange ord: avstandsberegningen avbryter tidlig når grensen er passert. Hurtigminnet for ordpar tømmes ved over 200 søkeord. Uendret feilhåndtering for datafilene |
| G. Kodegjennomgang | Bestått etter retting | Se under |
| H. Høflighet | Ikke relevant | Ingen nye kall til kildene |
| I. Dokumentasjon | Bestått | README: «Nettsiden» har søket (regler og grenser), lenker i ny fane, verktøylinjen og utskriften. «Status» har sprint 10 |
| J. Akseptansekriterier | Bestått | Se tabellen under |

## Akseptansekriterier
| Ønske (Svein 28.10.2026) | Oppfylt | Bevis |
|---|---|---|
| Mindre skrift uten fet i filtrene | Ja | `test_filtre_uten_fet_og_prioritet_uten_tall` (skriftvekt 400). Skjermbilde |
| Deloverskrift «Øvrige valg» | Ja | Samme test. Skjermbilde |
| Lenker åpnes i ny fane | Ja | `test_lenker_aapnes_i_ny_fane` (alle lenker i listen og under «Utelatte») |
| Begrunnelse i utskriften, og mer leservennlig (innrykk, luft) | Ja | `test_utskrift_har_hvorfor_relevant`, PDF-eksempelet |
| Prioritet uten tall | Ja | «Høy», «Middels» og «Lav» (testet) |
| Verktøylinjen flyttet opp i toppen | Ja | `test_verktoylinjen_staar_i_toppen`. Skjermbilde |
| Søk som tåler skrivemåter og skrivefeil (rv4, Rv.4, «rv.  4», barnehave, barnehahgre) | Ja | `test_sok_tåler_skrivemaater_for_vegnummer`, `test_sok_taaler_smaa_skrivefeil`, søketabellen over |

## G. Kodegjennomgang
Hele diffen er lest på nytt: `git diff 11fa302..92c72b0`, 7 filer, 324 nye og 68 fjernede linjer.

**Funnet og rettet:**
1. **Falske treff i søket.** Første versjon fant «Statens» ved søk på «sitat», fordi den
   sammenlignet med en kortere start av ordet. Strammet inn:
   - De to første bokstavene må stemme.
   - Sammenligning med starten av ord gjelder bare ord på 6 bokstaver eller mer.
   - To feil tillates først fra 10 bokstaver.
2. **Tall i søket.** «rv4» fant «rv. 40» via vanlig delstrengsøk. Tall må nå stå alene, med
   egen funksjon `inneholder()`.
3. **Navnekollisjon i `partblokk()`.** En lokal variabel `lenke` skygget den nye funksjonen
   `lenke()`. Variabelen er gitt nytt navn.
4. **Avkrysningsbokser krympet** ved lange valg (flex). Rettet med `flex: none`.

**Vurdert og beholdt:**
- Søketeksten bygges én gang per høring (`h._sok`).
- Avstand mellom ordpar regnes én gang per søkeord og ord.
- Grensene for feiltoleranse står i koden, ikke i `sources.yaml`, fordi de hører til
  nettsidens oppførsel. De er beskrevet i README.

## Kjente feil og begrensninger
1. **Søket kan fortsatt gi noen få falske treff med én bokstav feil**, for eksempel «samer»
   mot «saker». Alle ordene i søket må finnes, så flere ord gir færre slike treff.
2. **Korte ord med skrivefeil** (5 bokstaver eller færre) finner bare hele ord, ikke starten
   av sammensatte ord. «skloe» finner «skole», men ikke «grunnskole».
3. **Utskriften er lengre.** 67 høringer gir nå 11 sider. Det skyldes luften,
   innrykket og den større skriften du ba om. Vil du ha den tettere, kan luften justeres.

## Forslag til senere sprinter
- Vise «Viser også treff på lignende ord» når søket bare finner noe ved hjelp av feiltoleransen.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ (oppdater med Ctrl+F5), og se på
   verktøylinjen i toppen og filtrene med «Øvrige valg».
2. Søk på «barnehave», «barnehahgre» og et vegnummer med ulike skrivemåter.
3. Klikk på en høring og sjekk at den åpnes i ny fane.
4. Trykk «Skriv ut» og se på forhåndsvisningen, eller åpn
   `docs/sprinter/bilder/sprint-10-utskrift-eksempel.pdf`. Er luften passe?
