# Sprint 0 – Kartlegging av kilder

## Sammendrag
Alle 39 kildene i spesifikasjonen og Gjøvik kommunes postliste er undersøkt 29. september 2026.
Resultatet ligger i `docs/kildekartlegging.md`.

- **21 kilder** anbefales aktive, **17 anbefales inaktive** (ingen egen høringsside, eller bare
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
- `docs/sprinter/sprint-00-rapport.md` (ny): denne rapporten
- `SPRINTSTATUS.md`: bare statuskolonnen for sprint 0

Hjelpeskript og nedlastede sider ligger i en midlertidig mappe utenfor repoet og er ikke
committet.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Ikke relevant | Sprinten har ingen kode, så det finnes ingenting å teste. `pytest` er ikke kjørt, og Python er heller ikke installert på PC-en (se risiko 9 i kartleggingen). |
| B. Kodekvalitet | Ikke relevant | Ingen kode, så `ruff` er ikke kjørt. |
| C. Ekte data | Bestått | Antall åpne høringer per kilde er telt mot kildene 29.09.2026, se kolonnen «Åpne høringer» i kartleggingen, avsnitt 1. Tall som ser unaturlige ut, er forklart der: 0 hos Nkom, DSB, DiBK og Arbeidstilsynet (ingen åpne i dag, siste frist oppgitt) og 21 hos Miljødirektoratet (mange utslippssaker innen olje og gass). |
| D. Stikkprøver | Delvis | Etter godkjent plan er det kontrollert **én** konkret høring per aktiv kilde (tittel, frist, lenke), se tabellen under. Sjekklistens krav om fem høringer felt for felt gjelder parserne og gjennomføres fra sprint 1. |
| E. Tegn og datoer | Bestått | Datoformatene per kilde er dokumentert (kartleggingen, avsnitt 10). Æ, ø og å kom riktig ut i alle JSON-svar («Næringskomiteen», «Mjøsa», «Høyringar»). Regjeringen.no bruker HTML-entiteter (`&#xE6;`), som må dekodes. Stortingets frister kommer i UTC (21:59) og tilsvarer 23:59 norsk tid. |
| F. Feilhåndtering | Ikke relevant | Ingen kjørende kode. Feilsvar som ble observert under kartleggingen, er likevel dokumentert: HTTP 500 fra innlandetfylke.no/horinger og datatilsynet.no/robots.txt, og 404 på mange gjettede adresser. |
| G. Kodegjennomgang | Bestått | Jeg gikk gjennom dokumentene på nytt og rettet to feil: en feil kryssreferanse (eInnsyn viste til 9.2 i stedet for 9.1) og et udokumentert tall for NVE-forskrifter («0–1», endret til «ikke fastslått»). Det finnes ingen hemmeligheter i filene. |
| H. Høflighet | Bestått | robots.txt er hentet og vurdert for de 40 opprinnelige domenene og for underdomenene som ble funnet underveis (stortinget.no, hoering-publisering.udir.no, hoering.udir.no, api.einnsyn.no og anskaffelser.no). Alle kall brukte User-Agent `HoringsoversiktGRU/0.1 (+mailto:svein-havar@gjovikregionen.no)` og hadde pauser mellom kallene, 20 sekunder mot NVE (`Crawl-delay`). Sperrede områder er ikke brukt, bortsett fra ett kontrollkall mot Udir-API-et før robots.txt var lest (se «Kjente feil»). Samtykkevinduer er ikke godtatt. |
| I. Dokumentasjon | Ikke relevant | README og `sources.yaml` opprettes i sprint 1. Kartleggingen er sprintens dokumentasjon. |
| J. Akseptansekriterier | Bestått | Se tabellen under. |

## Stikkprøver
Én høring per aktiv kilde er kontrollert mot kildens egen side 29.09.2026.

| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Stortinget | Representantforslag om en tydelig og forpliktende integreringskontrakt (KOMMFORV), skriftlig, frist 07.10.2026 | tittel, komité, frist, lenke (200) | Ingen | https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=10005899 |
| Regjeringen.no | Høring – forslag til endringer i pengespillforskriften (KUD), frist 29.11.2026 | tittel, departement, frist, status | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-pengespillforskriften/id3171815/ |
| Regjeringen.no (høringsinstanser) | Felles rammeplaner for lærerutdanninger (KD) | liste over høringsinstanser på detaljsiden | Ingen | https://www.regjeringen.no/no/dokumenter/horing-av-forslag-til-forskrifter-om-felles-rammeplaner-for-larerutdanninger-og-felles-rammeplaner-for-samiske-larerutdanninger/id3172070/ |
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
| Kilder uten stabil høringsside er listet med forslag om `aktiv: false` | Ja | 17 kilder, se avsnitt 1 og begrunnelse per kilde |
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
- **Senere:** Overvåk Nye Veier og Bane NOR per prosjekt i Innlandet via sitemap, hvis Svein
  ønsker det.

## Hva Svein bør sjekke selv
1. Les avsnitt 1 (sammendragstabellen) og avsnitt 12 (spørsmål) i `docs/kildekartlegging.md`,
   og svar på spørsmål 1–9. Svarene kan gjerne skrives i kommentarkolonnen i `SPRINTSTATUS.md`.
2. Kontroller Udir-sperren selv: https://hoering-publisering.udir.no/robots.txt
   (viser `Disallow: /`).
3. Åpne https://www.regjeringen.no/no/dokument/hoyringar/id1763/ og se at avsenderne er
   departementer, ikke direktorater.
4. Åpne https://www.udir.no/om-udir/hoyringar/ og vurder hvor viktig Udir er. Siden viser 12 åpne
   høringer, bl.a. om organisering av skoledagen for 1. og 2. trinn.
5. Se gjennom de 17 kildene foreslått inaktive, særlig Nye Veier, Jernbanedirektoratet og
   Bane NOR.
