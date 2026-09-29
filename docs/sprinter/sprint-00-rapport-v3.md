# Sprint 0 – Kartlegging av kilder (versjon 3)

## Endringer fra versjon 2
Svein pekte på https://www.jernbanedirektoratet.no/nyheter/ og Bane NORs prosjektsøk
(https://www.banenor.no/prosjekter/alle-prosjekter/?q=gj%C3%B8vik…). Begge kildene er endret
fra inaktiv til aktiv (kartleggingen, avsnitt 3.3 og 3.4).

- **Jernbanedirektoratet:** WordPress REST-API (`/wp-json/wp/v2/posts?search=…`), filtrert på
  høringsord. Volumet er lavt, og fristen er av og til vag («midten av juni»).
- **Bane NOR:** Prosjektlisten filtrert på Innlandet (`Fylker=14488`, 5 prosjekter) pluss
  søket på «gjøvik». Høringsoppslagene finnes via sitemapet og hentes fra detaljsiden
  (f.eks. «Starter reguleringsarbeid i Moelv»).
- **Oppdatert i kartleggingen:** sammendragstabellen, resultatlinjen (24 aktive, 14
  inaktive), datoformater, risiko 2 og spørsmål 7.
- **Sjekklisten** er kjørt på nytt for endringen, se C, D, E, G og H (merket v3).

## Endringer fra versjon 1 (v2)
Svein ba om at Nye Veier undersøkes via
https://www.nyeveier.no/strekninger/innlandet/oppdateringer-fra-innlandet/.
Siden gir en brukbar kilde, og **Nye Veier er endret fra inaktiv til aktiv** (kartleggingen,
avsnitt 3.1).

- **Metode:** HTML-liste med alle 64 oppdateringer fra Innlandet. Høringer plukkes ut med
  søkeord, og fristen hentes fra detaljsiden.
- **Oppdatert i kartleggingen:** sammendragstabellen, resultatlinjen, datoformater (avsnitt 10),
  risiko 2 og spørsmål 7.
- **Sjekklisten** er kjørt på nytt for endringen, se C, D, E, G og H under.

## Sammendrag
Alle 39 kildene i spesifikasjonen og Gjøvik kommunes postliste er undersøkt 29. september 2026.
Resultatet ligger i `docs/kildekartlegging.md`.

- **24 kilder** anbefales aktive, **14 anbefales inaktive** (ingen egen høringsside, eller bare
  egne høringssvar), og **1 (Udir)** må avklares fordi robots.txt sperrer datakilden.
- Ingen av de anbefalte kildene trenger Playwright. Miljødirektoratet, NVE og Gjøvik-postlista
  har JSON-endepunkter som sidene selv bruker, og Stortinget har et åpent API.
- For postlista anbefales ACOS-endepunktet «nye-innsyn». eInnsyn er uaktuelt fordi Gjøvik ikke
  publiserer der og API-et er sperret i robots.txt.

Sprinten anbefales godkjent, under forutsetning av at Svein svarer på de ni åpne spørsmålene i
kartleggingen (avsnitt 12). Svarene påvirker oppsettet av `sources.yaml` i sprint 1.

## Hva som er bygget
Sprinten har ingen produksjonskode, i tråd med planen.

- `docs/kildekartlegging.md` (ny): sammendragstabell, ett avsnitt per kilde, postlista,
  datoformater, risikoer og åpne spørsmål
- `docs/sprinter/sprint-00-plan.md` (ny): godkjent plan med Sveins avklaringer
- `docs/sprinter/sprint-00-rapport.md` (ny): versjon 1 av rapporten
- `docs/sprinter/sprint-00-rapport-v2.md` (ny): versjon 2 av rapporten
- `docs/sprinter/sprint-00-rapport-v3.md` (ny): denne rapporten
- `SPRINTSTATUS.md`: bare statuskolonnen for sprint 0

Hjelpeskript og nedlastede sider ligger i en midlertidig mappe utenfor repoet og er ikke
committet.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Ikke relevant | Sprinten har ingen kode, så det finnes ingenting å teste. `pytest` er ikke kjørt, og Python er heller ikke installert på PC-en (se risiko 9 i kartleggingen). |
| B. Kodekvalitet | Ikke relevant | Ingen kode, så `ruff` er ikke kjørt. |
| C. Ekte data | Bestått | Antall åpne høringer per kilde er telt mot kildene 29.09.2026, se kolonnen «Åpne høringer» i kartleggingen, avsnitt 1. Tall som ser unaturlige ut, er forklart der: 0 hos Nkom, DSB, DiBK og Arbeidstilsynet (ingen åpne i dag, siste frist oppgitt) og 21 hos Miljødirektoratet (mange utslippssaker innen olje og gass). **v2:** Nye Veier Innlandet har 64 oppdateringer, hvorav 10 med høringsord og 0 med åpen frist i dag (siste frist 3. juli 2026). **v3:** Jernbanedirektoratet har 0 åpne høringer (9 nyheter nevner «høring» siden 2021, og 1 er en reell høring). Bane NOR i Innlandet har 5 prosjekter og minst 3 planoppslag i sitemapet. Antall åpne er ikke fastslått, fordi årstallet i fristene ikke er lest ut. |
| D. Stikkprøver | Delvis | Etter godkjent plan er det kontrollert **én** konkret høring per aktiv kilde (tittel, frist, lenke), se tabellen under. Sjekklistens krav om fem høringer felt for felt gjelder parserne og gjennomføres fra sprint 1. |
| E. Tegn og datoer | Bestått | Datoformatene per kilde er dokumentert (kartleggingen, avsnitt 10). Æ, ø og å kom riktig ut i alle JSON-svar («Næringskomiteen», «Mjøsa», «Høyringar»). Regjeringen.no bruker HTML-entiteter (`&#xE6;`), som må dekodes. Stortingets frister kommer i UTC (21:59) og tilsvarer 23:59 norsk tid. **v2:** Nye Veier bruker HTML-entiteter (`Mj&#xF8;sbrua`) som dekodes riktig til «Mjøsbrua», og fristene står i fritekst i tre ulike former. Formatene er lagt inn i avsnitt 10. **v3:** Jernbanedirektoratets API gir æ, ø og å som `ø`-koder, som dekodes riktig til «færre» og «Østlandet». Bane NOR har frist med ukedag («Søndag 16. …»), og Jernbanedirektoratet har vage perioder. Begge er lagt inn i avsnitt 10. |
| F. Feilhåndtering | Ikke relevant | Ingen kjørende kode. Feilsvar som ble observert under kartleggingen, er likevel dokumentert: HTTP 500 fra innlandetfylke.no/horinger og datatilsynet.no/robots.txt, og 404 på mange gjettede adresser. |
| G. Kodegjennomgang | Bestått | Jeg gikk gjennom dokumentene på nytt og rettet to feil: en feil kryssreferanse (eInnsyn viste til 9.2 i stedet for 9.1) og et udokumentert tall for NVE-forskrifter («0–1», endret til «ikke fastslått»). Det finnes ingen hemmeligheter i filene. **v2:** Jeg leste `git diff` for kartleggingen (36 linjer lagt til, 13 fjernet). Jeg rettet en setning som havnet i feil rekkefølge i risiko 2, og fjernet en udokumentert påstand om at Nye Veier har tilsvarende sider for andre regioner. **v3:** Jeg leste `git diff` på nytt (66 linjer lagt til, 23 fjernet) og rettet en uheldig orddeling i spørsmål 7. Usikre påstander er merket «ikke verifisert» eller «ikke fastslått». |
| H. Høflighet | Bestått | robots.txt er hentet og vurdert for de 40 opprinnelige domenene og for underdomenene som ble funnet underveis (stortinget.no, hoering-publisering.udir.no, hoering.udir.no, api.einnsyn.no og anskaffelser.no). Alle kall brukte User-Agent `HoringsoversiktGRU/0.1 (+mailto:svein-havar@gjovikregionen.no)` og hadde pauser mellom kallene, 20 sekunder mot NVE (`Crawl-delay`). Sperrede områder er ikke brukt, bortsett fra ett kontrollkall mot Udir-API-et før robots.txt var lest (se «Kjente feil»). Samtykkevinduer er ikke godtatt. **v2:** nyeveier.no/robots.txt gir 404, altså ingen begrensninger. Det ble gjort 1 listekall og 4 detaljkall med pauser og samme User-Agent. **v3:** Jernbanedirektoratet har tom `Disallow`, så REST-API-et er tillatt, og det ble gjort 7 kall. Bane NOR har `Allow: /`, og det ble gjort 10 kall. Alle kall hadde pauser. |
| I. Dokumentasjon | Ikke relevant | README og `sources.yaml` opprettes i sprint 1. Kartleggingen er sprintens dokumentasjon. |
| J. Akseptansekriterier | Bestått | Se tabellen under. |

## Stikkprøver
Én høring per aktiv kilde er kontrollert mot kildens egen side 29.09.2026.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Stortinget | Representantforslag om en tydelig og forpliktende integreringskontrakt (KOMMFORV), skriftlig, frist 07.10.2026 | tittel, komité, frist, lenke (200) | Ingen | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005899 |
| Regjeringen.no | Høring – forslag til endringer i pengespillforskriften (KUD), frist 29.11.2026 | tittel, departement, frist, status | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-pengespillforskriften/id3171815/ |
| Regjeringen.no (høringsinstanser) | Felles rammeplaner for lærerutdanninger (KD) | liste over høringsinstanser på detaljsiden | Ingen | https://www.regjeringen.no/no/dokumenter/horing-av-forslag-til-forskrifter-om-felles-rammeplaner-for-larerutdanninger-og-felles-rammeplaner-for-samiske-larerutdanninger/id3172070/ |
| Nye Veier (v2) | Varsel om utvidet varslingsområde for E6-strekningen fra Elstad til Fryasletta, publisert 08.06.2026, frist «innen 3. juli 2026» | tittel, dato, frist på detaljside | Ingen | https://www.nyeveier.no/strekninger/innlandet/oppdateringer-fra-innlandet/varsel-om-utvidet-varslingsomraade-for-e6-strekningen-fra-elstad-til-fryasletta/ |
| Nye Veier (v2) | Reguleringsplan for E6 Moelv – Roterud, publisert 05.05.2025, frist for merknader 23.05.2025 | tittel, dato, frist, kopimottaker Gjøvik kommune | Ingen | https://www.nyeveier.no/strekninger/innlandet/oppdateringer-fra-innlandet/reguleringsplan-for-e6-moelv-roterud/ |
| Jernbanedirektoratet (v3) | Tre nye utredninger: – Vi løser ikke utfordringene uten jernbanen, 09.04.2026, høringsperiode «midten av april til midten av juni» | tittel, dato, høringsparter (fylkeskommunene), frist | Ingen; fristen er vag på kilden | https://www.jernbanedirektoratet.no/nyheter/tre-nye-utredninger-vi-loser-ikke-utfordringene-uten-jernbanen/ |
| Bane NOR (v3) | Starter reguleringsarbeid i Moelv (Moelv kryssingsspor, sak 202408564), `lastmod` 16.01.2026 | tittel, publisert, saksnummer, «Frist for innspill» | Ingen; årstallet for fristen er ikke lest ut | https://www.banenor.no/prosjekter/alle-prosjekter/kapasitetsokende-tiltak-pa-dovrebanen/starter-reguleringsarbeid-i-moelv/ |
| Vegvesen, regelverk | Høring – forslag til endringer i førerkortforskriften vedlegg 1, frist 01.01.2027 | tittel, frist, referanse, høringsinstanser (PDF) | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing--forslag-til-endringer-i-forerkortforskriften-vedlegg-1-26-80489-6/ |
| Vegvesen, prosjekter | E39 Grungen bru, merknadsfrist 02.11.2026 | tittel, publisert, frist | Ingen | https://www.vegvesen.no/vegprosjekter/hoeringer-vegprosjekter/ |
| Miljødirektoratet | Utvidelse av ETS2 (2026/6330), frist 01.10.2026 | tittel, nummer, frist, lenke | Ingen | https://www.miljodirektoratet.no/hoeringer/2026/juli-2026/utvidelse-av-ets2/ |
| NVE, konsesjon | Granåsen vindkraftverk (Trysil), frist 06.11.2026 | tittel, kommune, frist | Ingen | https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id=26175&type=A-1 (lenkeformat fra NVEs egen side, id 26175 ikke åpnet) |
| NVE, forskrift | Høring av forslag til revidert damsikkerhetsforskrift (avsluttet) | tittel, status | Ingen | https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/ |
| DSB | Endringer i kompetansekrav i brann- og redningsvesenforskriften (19.11.2025) | tittel, dato, samme oppføring i RSS og liste | Ingen | https://www.dsb.no/horinger/horinger/ |
| Landbruksdirektoratet | Forslag til ny forskrift om markedsregulering av epler og matpoteter, frist 12.10.2026 | tittel, frist, høringsinstanser (PDF) | Ingen | https://www.landbruksdirektoratet.no/nb/om-direktoratet/horinger/horing-forslag-til-ny-forskrift-om-markedsregulering-av-epler-og-matpoteter |
| Nkom | (ingen åpne) Høring statlige bredbåndsstøtteordninger 2026, periode 13.04–15.05.2026 | tittel, periode | Ingen | https://nkom.no/tidligere-horinger |
| Bufdir | Forslag til endring av forskrift om tilskudd til inkludering av barn og unge, frist 3. august 2026 | tittel, frist, status | Ingen | https://www.bufdir.no/om/hoeringer/ |
| Riksantikvaren | Foreslår å frede deler av Haldenkanalen, frist 30.09.2026 | tittel, frist i ingress | Ingen | https://riksantikvaren.no/siste-nytt/horinger-og-kunngjoringer/ |
| Nasjonalarkivet | Høring: ny arkivforskrift 2025 | tittel | Ingen (frist ikke kontrollert) | https://www.nasjonalarkivet.no/offentlig-forvaltning/regelverk-og-standarder/riksarkivarens-horinger/ |
| Helsedirektoratet | Retningslinje for mat, måltider og ernæring i helse- og omsorgstjenesten, frist 03.12.2026 | tittel, frist | Ingen | https://www.helsedirektoratet.no/horinger |
| DMP | Høring – forslag til endringer i grossistforskriften §§ 5 og 5a, frist 9. november 2026 | tittel, publisert, frist, referanse 26/33703, høringsliste (PDF) | Ingen | https://www.dmp.no/nyheter/horing---forslag-til-endringer-i-grossistforskriften--5-og-5a |
| Mattilsynet | Høring – forslag til ny forskrift om materialer og produkter i kontakt med drikkevann, frist 20.10.2026 | tittel, publisert, frist | Ingen | https://www.mattilsynet.no/hoeringer |
| Arbeidstilsynet | (ingen åpne) Hongkong-konvensjonen, frist 14. august 2026 | tittel, frist, antall svar | Ingen | https://www.arbeidstilsynet.no/regelverk/horinger/ |
| Digdir | Høyring av DCAT-AP-NO og innføring av HVD-DCAT-AP-NO, frist «1. oktober» (uten år) | tittel, frist | Ingen, men årstallet mangler på kilden | https://www.digdir.no/standarder/hoyringar/1502 |
| DiBK | (ingen åpne) Forslag til endringer i veiledningen til kapittel 2 i TEK, frist 16.06.2026 | tittel, frist, antall svar | Ingen | https://www.dibk.no/regelverk/horinger/hoyringar |
| Politidirektoratet | Høring – Nasjonal retningslinje for utgivelse av navn, frist 11. september 2026 (fritekst) | tittel, avsender, dato, frist | Ingen | https://www.politiet.no/om-politiet/dokumenter-strategier-og-horinger/dokumenter/?innholdstype=72&enhet=103 |
| Skatteetaten | Høring – Forslag til endringer på skatteregnskapsområdet (publ. 28.09.2026) | tittel, publisert, høringsinstanser på detaljsiden | Ingen (frist ikke lest ut) | https://www.skatteetaten.no/rettskilder/type/horinger/horing--forslag-til-endringer-pa-skatteregnskapsomradet/ |
| Innlandet fylkeskommune | Planprogram – regional plan for nettinfrastrukturen for energi, frist 11. november 2026 | tittel, frist | Ingen | https://innlandetfylke.no/politikk/horinger/ |
| Statsforvalteren i Innlandet | Oppstart av verneprosess – Frivillig vern av skog – Syv områder, frist 16. oktober kl. 23:59 | tittel, frist | Ingen, men årstallet mangler på kilden | https://www.statsforvalteren.no/innlandet/horinger/ |
| Gjøvik postliste | Dokument 2026/79694, «Krav om redegjørelse …», inngående, 24.09.2026 | tittel, type, dokument-ID, dato | Ingen | https://www.gjovik.kommune.no/politikk-planer-og-organisasjon/postliste-dokumenter-og-vedtak/sok-i-postliste/ |

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Alle aktive kilder i avsnitt 2 er undersøkt | Ja | 39 av 39 kilder har eget avsnitt i `docs/kildekartlegging.md` (avsnitt 2–8), og alle er oppført i sammendragstabellen |
| Per kilde: URL, metode, tilgjengelige felter, om høringsparter finnes, og om kilden er dekket av regjeringen.no | Ja, med forbehold | Alle aktive kilder har URL, metode og felter. Høringsparter er verifisert for regjeringen.no, Vegvesen, Landbruksdir., DMP, Skatteetaten og Arbeidstilsynet, og står som «ikke verifisert» der de ikke er kontrollert. Dekning på regjeringen.no er dokumentert med gjennomgang av 200 høringer; for inaktive kilder er den merket «antatt». |
| Postlista er undersøkt og anbefalt metode er begrunnet, inkludert robots.txt | Ja | Kartleggingen, avsnitt 9: alle tre alternativer er vurdert, robots.txt og noindex er vurdert, og anbefalingen er begrunnet |
| Kilder uten stabil høringsside er listet med forslag om `aktiv: false` | Ja | 14 kilder (v2: Nye Veier og v3: Jernbanedirektoratet og Bane NOR er flyttet til aktiv), se avsnitt 1 og begrunnelse per kilde |
| Risikoer og åpne spørsmål er listet | Ja | Kartleggingen, avsnitt 11 (9 risikoer) og 12 (9 spørsmål) |

## Kjente feil og begrensninger
- Før jeg hadde lest robots.txt for `hoering-publisering.udir.no`, gjorde jeg ett GET-kall mot
  API-et, med robots.txt-kallet i samme kommando. Det var bare ett kall, og Udir-kilden er ikke
  anbefalt brukt før Svein har avgjort saken.
- Stikkprøvene er én høring per kilde, ikke fem. Det er i tråd med godkjent plan, siden sprinten
  ikke har parsere.
- Høringsparter er ikke verifisert for Miljødir., Helsedir., Mattilsynet, Statsforvalteren,
  IFK, Digdir og Nasjonalarkivet.
- Frist er ikke lest ut for Skatteetaten og Nasjonalarkivet, og antall åpne høringer hos
  NVE-forskrifter og Nasjonalarkivet er ikke fastslått. Listene deres viser ikke frist.
- Søkeforespørselen (request body) mot Gjøvik-postlista er ikke kartlagt i detalj, fordi
  samtykkevinduet blokkerte søket i nettleseren. Svarformatet er dokumentert. Resten gjøres i
  sprint 7.
- Tallene er et øyeblikksbilde fra 29.09.2026.

## Forslag til senere sprinter
- **Sprint 1:** Stortinget-modulen bør spørre både nåværende og neste sesjon, og bruke fristen i
  stedet for `horing_status`.
- **Sprint 1:** Lag én felles, grundig testet datoparser for alle formatene i kartleggingens
  avsnitt 10, med regel for datoer uten årstall.
- **Sprint 4/5:** Legg inn filtre på fylke og tema for de nasjonale listene (NVE, Vegvesenets
  prosjekter, Miljødir. olje og gass, DSB-samtykker).
- **Sprint 6:** PDF-baserte høringslister (Vegvesen, Ldir, DMP, Arbeidstilsynet) krever
  PDF-uttrekk. Vurder `pypdf`, men Vegvesenet sperrer PDF i robots.txt.
- **Sprint 4:** Nye Veier-parseren trenger en søkeordliste som testes mot alle 64 oppføringer,
  slik at falske treff (f.eks. grunnundersøkelser) og manglende treff kan måles.
- **Sprint 4:** Bane NOR-parseren må kombinere prosjektlisten (Innlandet + søk på «gjøvik») med
  sitemapet, og filtrere bort oppslag som ikke er høringer (f.eks. «reguleringsplan godkjent»).

## Hva Svein bør sjekke selv
1. Les avsnitt 1 (sammendragstabellen) og avsnitt 12 (spørsmål) i `docs/kildekartlegging.md`,
   og svar på spørsmål 1–9. Svarene kan gjerne skrives i kommentarkolonnen i `SPRINTSTATUS.md`.
2. Kontroller Udir-sperren selv: https://hoering-publisering.udir.no/robots.txt
   (viser `Disallow: /`).
3. Åpne https://www.regjeringen.no/no/dokument/hoyringar/id1763/ og se at avsenderne er
   departementer, ikke direktorater.
4. Åpne https://www.udir.no/om-udir/hoyringar/ og vurder hvor viktig Udir er. Siden viser 12 åpne
   høringer, bl.a. om organisering av skoledagen for 1. og 2. trinn.
5. Se gjennom de 14 kildene foreslått inaktive (kartleggingen, avsnitt 1).
6. (v2) Les kartleggingens avsnitt 3.1 om Nye Veier, og bekreft at søkeordfiltrering av
   nyhetsstrømmen er en akseptabel metode.
7. (v3) Les kartleggingens avsnitt 3.3 og 3.4 om Jernbanedirektoratet og Bane NOR, og svar på
   spørsmål 7 om vage frister.
