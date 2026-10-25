# Sprint 5 – Direktorater, prioritet 2 og 3

## Sammendrag
Tolv nye kilder overvåkes nå. Ni av dem er etater med høringsliste: Nkom,
Landbruksdirektoratet, Riksantikvaren, Nasjonalarkivet, DMP, Mattilsynet, Arbeidstilsynet,
Politidirektoratet og Skatteetaten. De tre siste, SSB, Konkurransetilsynet og Innlandet
politidistrikt, har ingen høringsliste. De tas bare med når høringen gjelder kommunene eller
regionen, slik du ønsket. FHI, Helsetilsynet, Kartverket, UDI og Datatilsynet er undersøkt på nytt.
Ingen av dem har en kanal med utgående høringer, så de står fortsatt som inaktive, med begrunnelse.
Siden viser nå 133 åpne høringer fra 27 kilder. Hele innhentingen tar 3–4 minutter. Begge
rettelsene fra sprint 4 er gjort: «Høringsfrist: desember 2026», og ingress kuttet ved helt ord.
Alle punkter er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget

**Nye kilder** (`horinger/kilder/etater.py`, med en felles gang: liste → detaljside ved behov →
krav)

| Kilde | Pri | Metode | Utvalg |
|---|---|---|---|
| Nkom | 2 | Liste + detaljside | Alle. Fristen fra detaljsiden |
| Landbruksdirektoratet | 2 | Høringsside | «På høring nå» |
| Riksantikvaren | 2 | Nyhetsliste | Bare oppslag med frist. Fredning av enkeltsteder bare når det gjelder regionen eller kommunene |
| Nasjonalarkivet | 2 | Lenkeliste + detaljside | De 3 nyeste |
| DMP | 3 | Liste + detaljside | Siste 120 dager |
| Mattilsynet | 2 | Regelverkstabell | Alle unntatt «Bestilling til VKM» |
| Arbeidstilsynet | 2 | Høringsside | Pågående |
| Politidirektoratet | 2 | Dokumentliste | Kort med «på høring til <dato>». Dokumenter fra samme høring slås sammen |
| Skatteetaten | 2 | JSON i siden + detaljside | Siste 120 dager |
| Innlandet politidistrikt | 2 | Samme dokumentliste | Bare når aktuell for regionen eller kommunene |
| SSB | 2 | Én høringsside | Bare når fristen ikke er passert og høringen er aktuell |
| Konkurransetilsynet | 3 | Sitemap (samme modul som Bane NOR) | Bare når aktuell for regionen eller kommunene |

**Felles**
- `Kilde.aktuell_for_regionen` og `krav: aktuell_for_regionen` i `sources.yaml` følger samme
  regel som løftet til høy prioritet: kommunene, fylkeskommunen, plan- og bygningsloven,
  Innlandet eller et sted i regionen.
- **Frist med bare måned og år:** `finn_frist_maned` gjør «innen høringsfristen desember 2026»
  om til `frist` = 1. desember, `frist_maned` = «2026-12» og fristteksten «Høringsfrist:
  desember 2026». Byggingen arkiverer den først når måneden er over. Siden viser «des.
  2026 – Frist i desember» og sorterer den som den 1.
- **Ingress:** `kort_ingress` kutter ved helt ord med «…» for alle kilder. De fire stedene som
  kuttet midt i et ord, er fjernet.
- **Kjøretid:** Total tid står i loggen, og samlet tid per kilde i `status.json`
  (`kjoretid_sekunder`).
- Bane NOR-modulen kan nå brukes for flere etater (`sitemaps`, `instans`, `krav`).

**Endrede filer:** `sources.yaml`, `horinger/datoer.py`, `horinger/modell.py`,
`horinger/bygg.py`, `horinger/kjor.py`, `horinger/kilder/base.py`, `bane_nor.py`, `dsb.py`,
`jernbanedirektoratet.py`, `nve.py`, `horinger/kilder/__init__.py`, `side/app.js`,
`side/stil.css`, `README.md`.
**Nye tester:** `tests/test_sprint5_kilder.py`, pluss tillegg i `test_bygg.py`,
`test_dedup_prioritet.py` og `test_nettside.py`. 16 nye testkopier ligger i `tests/fixtures/`.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **226 bestått, 0 feilet, 0 hoppet over** (35,2 s). 28 nye siden sprint 4 (198). I GitHub Actions: 225 bestått før den siste regresjonstesten ble lagt til |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «71 files already formatted». `actionlint`: ingen funn. **Merk:** én for lang linje kom med i en commit (fanget i denne gjennomgangen og rettet i 34825f1) |
| C. Ekte data | Bestått | Ukentlig oppdatering 25.10 (40217720723): 27 kilder hentet, 0 feil, 133 åpne høringer. Tabell under |
| D. Stikkprøver | Bestått | 15 høringer kontrollert felt for felt, og 0-tallene kontrollert. Ingen avvik. Se tabell under |
| E. Tegn og datoer | Bestått | æ, ø og å er riktige, også nynorsk (Riksantikvaren: «høyringsfrist», «ynskjer»). Nye formater tolket og testet: «fredag 16. oktober 2026», «30.september 2026» uten mellomrom, «Publisert : 8. april 2026», «på høring til 11. september 2026» og månedsfrist «desember 2026». Frister lagres i ISO 8601 |
| F. Feilhåndtering | Bestått | Simulert feil i Mattilsynet 25.10 (commit 6165d01): status «feil», de 26 andre kildene ble hentet og publisert. Mattilsynet hadde ingen tidligere data, så tabellen viste «Høringene herfra mangler i listen». Ny kjøring rettet det (969a7ff). Datatilsynet: robots.txt gir 500, og da hentes ingenting (testet i sprint 4) |
| G. Kodegjennomgang | Bestått etter retting | 7 funn rettet. Se avsnittet under |
| H. Høflighet | Bestått | Samme User-Agent og pauser. robots.txt sjekket for alle nettstedene. Landbruksdirektoratet tillater bare `/nb` o.l., og siden ligger der. Datatilsynet hentes ikke, fordi robots.txt svarer med feil. Detaljsider bare for nye oppslag, høyst 10 per kilde (Nasjonalarkivet 3, Konkurransetilsynet 5). Hele kjøringen: 92 kall |
| I. Dokumentasjon | Bestått | README: tabellen per etat er utvidet med de 12 nye og de 5 som fortsatt er inaktive, pluss avsnitt om månedsfrist. `sources.yaml` har merknad for alle 20 etater med prioritet 2 og 3 |
| J. Akseptansekriterier | 4 av 4 oppfylt | Se tabell under |

**Antall per kilde (C), og tid:**

| Kilde | Åpne | Tid (s) | Forklaring |
|---|---|---|---|
| Mattilsynet | 9 | 4,0 | 216 rader med frist i tabellen. 9 har frist fram i tid |
| Skatteetaten | 4 | 9,9 | 5 fra de siste 120 dagene. Én hadde frist 05.10, utløpt. CO2-avgift for sjøfart har ingen frist på siden og vises som «Frist ikke oppgitt» |
| DMP | 2 | 9,8 | Grossistforskriften (9.11) og medisinsk utstyr (9.12). Prioritet 3 |
| Nkom | 1 | 3,5 | Lokale FM-sendernett, frist 13.11 |
| Arbeidstilsynet | 1 | 2,1 | Røntgenundersøkelse ved bergarbeid, frist 31.01.2027 |
| Landbruksdirektoratet | 0 | 2,3 | Eneste under «På høring nå» hadde frist 16.10, utløpt |
| Riksantikvaren | 0 | 2,5 | Siste frist var 30.09 (Haldenkanalen, ikke i regionen) |
| Nasjonalarkivet | 0 | 6,1 | Siste høringer hadde frist i november 2025 |
| Politidirektoratet | 0 | 7,3 | Siste høring hadde frist 11.09.2026 |
| Innlandet politidistrikt | 0 | 0,6 | Bare et høringssvar fra 2020 |
| SSB | 0 | 2,2 | Høringssiden viser en høring med frist 4. juni 2026 |
| Konkurransetilsynet | 0 | 3,4 | Siste høring (fusjonsretningslinjer) er eldre enn 120 dager og gjelder ikke kommunene |

**Kjøretid (kriterium 4):** Testkjøringen i GitHub brukte **204 sekunder** for alle 27 kilder
(loggen: «Hentet 27 kilder … 92 kall, 204 sekunder»). `status.json` viser 222 sekunder, som er
summen per kilde, inkludert regjeringen.no fra PC-en. NVE alene tar 100 s på grunn av kravet om
20 s mellom kall. Det er godt under grensen på 30 minutter.

### Funn i kodegjennomgangen (G)
Diffen mot godkjent sprint 4 (`git diff 631dc31..HEAD`, 21 filer utenom data og testkopier) er
lest.

1. **Rettet – «innenriks» ble lest som fristordet «innen».** Skatteetatens høring om CO2-avgift fikk
   en setning om «innenriks kvotepliktig sjøfart» som fristtekst. Ordet må nå stå alene. Det gjelder
   alle kilder som leser frist fra fritekst (regresjonstest lagt til).
2. **Rettet – Riksantikvaren ga dobbeltoppføringer** med tittelen «Les mer om …», fordi hver
   artikkel har to lenker. Nå leses tittel og lenke fra overskriften.
3. **Rettet – en høring for fylkeskommunene ble filtrert bort som fredningssak.** «Overføring av
   forvaltningsansvar for fredet eiendom … til fylkeskommunen» gjelder fylkeskommunene og skal være
   med. Fredningssaker tas nå med når de gjelder regionen **eller** kommunene og fylkeskommunen.
4. **Rettet – DMP-listen tok med menylenker** («Høringer», «Høringer om opptak på byttelisten»), og
   «Publisert: …» ble en del av tittelen.
5. **Rettet – Nasjonalarkivet ga 0 høringer** på grunn av feil utvalg av lenker.
6. **Rettet – SSB-sidens dato ble ikke lest** («Publisert : 8. april 2026», med mellomrom før
   kolon).
7. **Rettet – for lang linje** etter retting 1, som ble pushet uten ny ruff-kjøring. Rettet straks
   (34825f1). Det er samme svakhet som i sprint 4: kodesjekken kjøres ikke automatisk ved push. Se
   forslag.

Ingen hemmeligheter i koden. Søkeord, krav, geografi og prioritet ligger i `sources.yaml`.

## Stikkprøver
Kontrollert 25.10.2026 mot kildenes egne sider, hentet i GitHub Actions. Høringsparter hentes
ikke før sprint 6.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Mattilsynet | Offentlig kontroll – animalsk produksjon (levende muslinger) | tittel, frist 26.10.2026, lenke | Ingen | https://www.mattilsynet.no/hoeringer?bId=4003 |
| Mattilsynet | Dyrehelseforskrifter – listeføring og kategorisering | tittel, frist 17.11.2026, lenke | Ingen | https://www.mattilsynet.no/hoeringer?bId=4013 |
| Mattilsynet | Elektronisk sprøytejournal | tittel, frist 20.11.2026, lenke | Ingen | https://www.mattilsynet.no/hoeringer?bId=4000 |
| Mattilsynet | Animaliebiproduktforskriften – åtselsfugler | tittel, frist 25.11.2026, lenke | Ingen | https://www.mattilsynet.no/hoeringer?bId=3953 |
| Mattilsynet | Forskrift om honning | tittel, frist 26.11.2026, lenke | Ingen | https://www.mattilsynet.no/hoeringer?bId=3977 |
| Skatteetaten | Overgangsregler til innkrevingsloven | tittel, frist 11.11.2026, lenke | Ingen | https://www.skatteetaten.no/rettskilder/type/horinger/horing---endringer-i-overgangsregler-til-innkrevingsloven-mv/ |
| Skatteetaten | Skatteregnskapsområdet | tittel, frist 24.11.2026, lenke | Ingen | https://www.skatteetaten.no/rettskilder/type/horinger/horing--forslag-til-endringer-pa-skatteregnskapsomradet/ |
| Skatteetaten | Avgiftsfritak for sukker | tittel, frist 03.12.2026, lenke | Ingen | https://www.skatteetaten.no/rettskilder/type/horinger/horing---forslag-om-endringer-i-avgiftsfritaket-for-sukker-som-brukes-i-ervervsmessig-produksjon-av-andre-varer/ |
| Skatteetaten | CO2-avgift for kvotepliktig sjøfart | tittel, frist (ingen på siden), lenke | **Rettet:** fristteksten var en setning om «innenriks» (G1). Nå: «Frist ikke oppgitt» | https://www.skatteetaten.no/rettskilder/type/horinger/horing--endringer-i-co2-avgiften-for-kvotepliktig-sjofart/ |
| DMP | Grossistforskriften §§ 5 og 5a | tittel, frist 09.11.2026, lenke | Ingen | https://www.dmp.no/nyheter/horing---forslag-til-endringer-i-grossistforskriften--5-og-5a |
| DMP | Medisinsk utstyr – kvalitetsstyring | tittel, frist 09.12.2026, lenke | Ingen | https://www.dmp.no/nyheter/horing-om-endringer-i-forskrift-for-medisinsk-utstyr--kvalitetsstyring-og-samsvarsvurdering |
| Nkom | Lokale FM-sendernett | tittel, frist 13.11.2026, lenke | Ingen | https://nkom.no/hoeringer/horing-av-utlysningsvilkar-og-tildelingsregler-for-lokale-fm-sendernett |
| Arbeidstilsynet | Røntgenundersøkelse ved bergarbeid | tittel, frist 31.01.2027, lenke | Ingen | https://www.arbeidstilsynet.no/regelverk/horinger/horing/?hearingId=3884 |
| Politidirektoratet | Retningslinje for utgivelse av navn (3 dokumenter → 1 høring) | tittel, frist 11.09.2026 (utløpt), sammenslåing | Ingen | https://www.politiet.no/om-politiet/dokumenter-strategier-og-horinger/dokumenter/?innholdstype=72&enhet=103 |
| NVE (rettelse) | Økodesignforskriften | fristtekst «Høringsfrist: desember 2026», sortering, ingress | Ingen | https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/forslag-til-endringer-i-oekodesignforskriften-eksterne-stroemkilder-endring-av-hviletilstand-og-toerketromler-og-energimerkeforskriften-for-produkter-endring-av-toerketromler/ |
| Landbruksdir., Riksantikvaren, Nasjonalarkivet, Innlandet pd., SSB, Konkurransetilsynet | 0 åpne | Kontrollert mot sidene. Se tabellen under C | Ingen | Adressene står i `sources.yaml` |

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Alle prioritet 2- og 3-kilder er lagt til eller satt til `aktiv: false` med begrunnelse | Ja | 12 lagt til. 8 er inaktive med begrunnelse i `sources.yaml` og README: DSA, Kulturdirektoratet, FHI, Helsetilsynet, Kartverket, UDI, Datatilsynet og Sivilombudet. Fem av dem er undersøkt på nytt etter ditt ønske. Test: `test_alle_etater_i_avsnitt_2_har_oppforing` |
| Filtre for kategori og prioritet virker med alle kilder | Ja | `test_temafilter_har_alle_temaer` og `test_prioritetsfilter_skiller`. Med ekte data har temafilteret 8 temaer, og prioritetene fordeler seg på 92 høy, 39 middels og 2 lav (DMP) |
| Stikkprøver er gjennomført for hver ny kilde | Ja | Se tabellen over: 15 høringer felt for felt, og 0-tallene kontrollert |
| Total kjøretid er målt og under 30 minutter | Ja | 204 s i testkjøringen (3,4 min). `kjoretid_sekunder` i `status.json`: 222 s. Test: `test_kjoretid_i_status` |

## Kjente feil og begrensninger
- **Ingen av de «aktuelt for regionen»-kildene har truffet ennå.** SSB, Konkurransetilsynet og
  Innlandet politidistrikt ga 0. Regelen er testet, men ikke sett på ekte høringer.
- **Fem etater har ingen kanal med utgående høringer:** FHI, Helsetilsynet, Kartverket og UDI har
  bare egne svar. Datatilsynets robots.txt svarer ikke. Høringene på feltene deres sendes ut av
  departementene og er med via regjeringen.no.
- **Mattilsynet gir mange høringer om næringsmidler og dyrehelse**, som sjelden gjelder kommunene.
  De har prioritet 2 (middels). Vil du ha dem lavere, kan prioriteten justeres i `sources.yaml`.
- **Skatteetaten oppgir ikke alltid fristen på siden** (den står i høringsbrevet, som er PDF).
- **Løftet til høy prioritet har fortsatt ikke slått inn på ekte data** (se sprint 4).
- **Sorteringen «nyeste først» bruker datoen høringen først ble sett.** Alle de nye kildene ble sett
  første gang i dag, så de ligger øverst denne uken.

## Forslag til senere sprinter
- Kjøre tester og ruff automatisk ved hver push til `main` (G7, og G5 i sprint 4).
- Lese fristen i høringsbrevet (PDF) for Skatteetaten der siden ikke har den. Mange robots.txt
  tillater PDF, men ikke alle.
- Prøve Datatilsynet igjen i sprint 6 eller 7.

## Hva Svein bør sjekke selv
1. Åpne https://shkorshavn.github.io/horingsoversikt-gru/ og søk etter «økodesign». Fristboksen skal
   vise «des. 2026 – Frist i desember», teksten «Høringsfrist: desember 2026», og ingressen skal
   slutte med «…» etter et helt ord.
2. Under Avsender «Direktorater og etater»: Er Mattilsynet (9), Skatteetaten (4) og DMP (2)
   nyttige for regionen, eller skal prioriteten ned?
3. Kryss av for «Lav (3)» under «Foreslått prioritet». Da kommer de to DMP-høringene fram.
4. Er du enig i at FHI, Helsetilsynet, Kartverket, UDI og Datatilsynet står som inaktive, med
   begrunnelsene i README?
