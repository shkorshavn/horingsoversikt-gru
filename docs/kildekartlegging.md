# Kildekartlegging – Høringsoversikt Gjøvikregionen

Sprint 0. Undersøkt 29. september 2026 av Claude Code.
Versjon 2: Nye Veier ble undersøkt på nytt via Innlandet-siden Svein anviste (avsnitt 3.1).
Versjon 3: Jernbanedirektoratet og Bane NOR ble undersøkt på nytt via sidene Svein anviste
(avsnitt 3.3 og 3.4).

Alle tall er et øyeblikksbilde fra undersøkelsesdagen. Alle kall er gjort med User-Agent
`HoringsoversiktGRU/0.1 (+mailto:svein-havar@gjovikregionen.no)`, med minst 0,3 sekunder mellom
kallene. Mot NVE ble det holdt 20 sekunder mellom kallene, slik NVEs robots.txt krever
(`Crawl-delay: 20`).

Forklaring på metodene:

- **API**: dokumentert eller udokumentert JSON-endepunkt.
- **JSON i HTML**: dataene ligger som JSON inne i selve HTML-siden.
- **HTML**: vanlig, ferdig generert HTML som kan parses med BeautifulSoup.
- **Playwright**: siden krever at JavaScript kjøres.

Ingen av de anbefalte kildene trenger Playwright.

---

## 1. Sammendrag

| # | Kilde | Pri | Anbefalt | Metode | Åpne høringer 29.09.26 | Dekket av regjeringen.no |
|---|---|---|---|---|---|---|
| 1 | Stortinget (komitéhøringer) | 1 | aktiv | API (data.stortinget.no) | 1 i sesjon 2025–26 + 7 i 2026–27 | Nei (egen kanal) |
| 2 | Regjeringen.no (alle departementer) | 1/2 | aktiv | HTML | 58 | – |
| 3 | Nye Veier AS (Innlandet) | 1 | aktiv | HTML + søkeordfilter | 0 (siste frist 03.07.26) | Nei |
| 4 | Statens vegvesen – regelverk | 1 | aktiv | HTML | 12 | Nei |
| 4b | Statens vegvesen – vegprosjekter | 1 | aktiv | HTML | 7 (hele landet) | Nei |
| 5 | Jernbanedirektoratet | 1 | aktiv | API (WordPress REST) + søkeordfilter | 0 | Delvis (via SD) |
| 6 | Bane NOR SF (Innlandet) | 1 | aktiv | Sitemap + HTML | ikke fastslått | Nei |
| 7 | Nkom | 2 | aktiv | HTML | 0 (siden er tom nå) | Nei |
| 8 | Miljødirektoratet | 1 | aktiv | API (JSON) | 21 | Nei |
| 9 | NVE – forskrifter/veiledere | 1 | aktiv | HTML | ikke fastslått (listen viser dato, ikke frist) | Nei |
| 9b | NVE – konsesjonssaker | 1 | aktiv | API (JSON) | 14 (2 i Innlandet) | Nei |
| 10 | DSB | 1 | aktiv | RSS + HTML | 0 | Nei |
| 11 | Landbruksdirektoratet | 2 | aktiv | HTML | 1 | Nei |
| 12 | DSA | 3 | **inaktiv** | – | – | Delvis (via HOD) |
| 13 | Udir | 1 | **avklares** (robots.txt) | – | 12 (sett i nettleser) | Nei |
| 14 | IMDi | 1 | **inaktiv** | – | – | Antatt (via AID) |
| 15 | Bufdir | 1 | aktiv | HTML | 0 | Nei |
| 16 | Kulturdirektoratet | 2 | **inaktiv** | – | – | Antatt (via KUD) |
| 17 | Riksantikvaren | 2 | aktiv | HTML | 1 | Nei |
| 18 | Arkivverket (nå **Nasjonalarkivet**) | 2 | aktiv | HTML | ikke fastslått | Nei |
| 19 | Helsedirektoratet | 1 | aktiv | HTML | 5 | Nei |
| 20 | NAV (Arbeids- og velferdsdir.) | 1 | **inaktiv** | – | – | Antatt (via AID) |
| 21 | DMP | 2 | aktiv | HTML | 13 publisert i 2026, frist på detaljside | Nei |
| 22 | FHI | 2 | **inaktiv** | – | – | Antatt (via HOD) |
| 23 | Mattilsynet | 2 | aktiv | HTML | 8 | Nei |
| 24 | Arbeidstilsynet | 2 | aktiv | HTML | 0 | Nei |
| 25 | Statens helsetilsyn | 2 | **inaktiv** | – | – | Antatt (via HOD) |
| 26 | Digdir | 1 | aktiv | HTML | 1 | Nei |
| 27 | DFØ | 1 | **inaktiv** | – | – | Antatt (via DFD/NFD) |
| 28 | DiBK | 1 | aktiv | HTML | 0 | Nei (sendes på oppdrag fra KDD) |
| 29 | Kartverket | 2 | **inaktiv** | – | – | Antatt (via KDD) |
| 30 | UDI | 2 | **inaktiv** | – | – | Antatt (via JD) |
| 31 | Politidirektoratet | 2 | aktiv | HTML | 0 (siste frist 11.09.26) | Delvis (via JD) |
| 32 | Innlandet politidistrikt | 2 | **inaktiv** | – | – | – |
| 33 | Skatteetaten | 2 | aktiv | JSON i HTML | ≥ 1 (frist på detaljside) | Delvis (via FIN) |
| 34 | Datatilsynet | 2 | **inaktiv** | – | – | – |
| 35 | SSB | 2 | **inaktiv** | – | – | Antatt (via FIN) |
| 36 | Konkurransetilsynet | 3 | **inaktiv** | – | – | – |
| 37 | Sivilombudet | 3 | **inaktiv** | – | – | – |
| 38 | Innlandet fylkeskommune | 1 | aktiv | HTML | 2 | Nei |
| 39 | Statsforvalteren i Innlandet | 1 | aktiv | HTML | 1 | Nei |
| – | Gjøvik kommunes postliste | – | aktiv (etter OK fra Svein) | API (ACOS «nye-innsyn», JSON) | – | – |

**Resultat:** 24 kilder anbefales aktive, 14 anbefales inaktive, og 1 (Udir) må avklares.
Nye Veier (v2), Jernbanedirektoratet og Bane NOR (v3) ble endret fra inaktiv til aktiv etter
tips fra Svein.
Statens vegvesen og NVE har to delkilder hver, med hver sin innhentingsmetode.

**Om «Dekket av regjeringen.no»:** Jeg gikk gjennom de 200 nyeste høringene på regjeringen.no
(side 1–10). Alle hadde et departement som avsender, og ingen hadde et direktorat. Høringer
som direktoratene sender ut selv, havner altså **ikke** på regjeringen.no. «Antatt (via X)»
betyr at etaten ikke har egne høringer, og at regelverksendringer på området trolig sendes ut
av departementet X. Det har jeg ikke kontrollert høring for høring.

---

## 2. Regjeringen og Stortinget

### 2.1 Stortinget – komitéhøringer
- **URL:** `https://data.stortinget.no/eksport/horinger?sesjonid=<ID>&format=json`
- **Metode:** Åpent API (JSON). robots.txt: `Allow: /`. Lenke til høringen:
  `https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h=<id>` (sjekket, gir 200).
  robots.txt for www.stortinget.no krever `Crawl-delay: 5`.
- **Felter:** `id`, `komite.navn`, `horing_sak_info_liste[].sak_tittel`/`sak_korttittel`,
  `skriftlig` (true = skriftlig høring), `innspillsfrist`, `anmodningsfrist_dato_tid`
  (frist for påmelding til muntlig høring), `start_dato`, `horing_status`
  (Planlagt/Aktiv/Avholdt/Avlyst), `horingstidspunkt_liste` (sted og tid).
- **Høringsparter:** Ingen liste. Komitéhøringer er åpne for alle.
- **Sesjons-ID:** Sesjonen 2025–2026 varer til 30.09.2026 kl. 23:59, og 2026–2027 starter
  01.10.2026. Det er bekreftet via `/eksport/sesjoner`. API-et gir også `innevaerende_sesjon`.
  **Viktig funn:** Neste sesjon (2026–2027) hadde allerede **8 høringer** med frister i
  oktober, *før* sesjonen har startet. Innhentingen må derfor spørre både nåværende og neste
  sesjon, i alle fall i september.
- **Datoer:** Formatet er `/Date(<ms>+0200)/`. Tomme verdier er `/Date(-62135596800000)/` (år 1).
  Fristen 23:59 norsk tid ligger som 21:59 UTC.
- **Fallgruve:** `horing_status` står fortsatt som «Aktiv» etter at fristen er ute (sett for
  flere høringer med frist 27.–28.09). Innhentingen må bruke fristen, ikke statusen.

### 2.2 Regjeringen.no – alle departementer
- **URL:** `https://www.regjeringen.no/no/dokument/hoyringar/id1763/?page=N` (20 per side).
- **Metode:** HTML. RSS finnes (`/Utilities/RSSEngine/`), men den er **sperret i robots.txt**.
  Det samme gjelder filterparametrene `?ownerid`, `?documenttype`, `?term`, `?type` m.fl.
  Bare `?page=` er tillatt. Filtrering på departement må derfor gjøres i vår egen kode.
- **Felter i listen:** tittel, lenke, publiseringsdato (`dd.MM.yyyy`), departement
  (`span.department`), ingress, «Høringsfrist: dd.MM.yyyy» og status («På høring», «Under
  behandling», «Ferdigbehandlet»).
- **Paginering:** Listen er sortert på publiseringsdato. Åpne høringer fantes til og med side 7
  (publisert 08.04.2026, frist 08.10.2026). Innhentingen bør bla til den finner to hele sider
  uten «På høring», og ikke kortere enn ca. 8 måneder tilbake.
- **Detaljside:** Har metadata (`DC.Creator` = departement, `DC.Date`, `ownerid`) og en
  **fullstendig liste over høringsinstanser** i HTML (bl.a. «KS», «Fylkeskommunene»). Den er
  godt egnet til regionflagget i sprint 6.
- **Åpne høringer 29.09.26:** 58. Fordeling: JD 10, AID 7, ED 6, HOD 5, BFD 5, SD 4, FIN 4,
  NFD 3, LMD 3, KDD 3, DFD 2, KLD 2, KD 2, KUD 1, FD 1.
- **Tegn:** Noen departementsnavn kommer HTML-kodet (`N&#xE6;rings-`) og må dekodes.
- **Ikke i spesifikasjonens liste:** **Energidepartementet** (6 åpne), **Barne- og
  familiedepartementet** (5 åpne) og Utenriksdepartementet. Se spørsmål 4.

---

## 3. Transport, samferdsel og infrastruktur

### 3.1 Nye Veier AS – aktiv (endret i v2, etter tips fra Svein)
- **URL:** `https://www.nyeveier.no/strekninger/innlandet/oppdateringer-fra-innlandet/`
- **Metode:** HTML (UIkit). Hver oppdatering er en `article.uk-news-card` med tittel og lenke
  (`h1 > a`), dato (`dd.MM.yyyy` i `span.uk-text-semibold`), ingress og prosjektmerke
  (`uk-label`, f.eks. «Rv. 4 Hunndalen - Mjøsbrua»). Siden bruker HTML-entiteter for æ, ø og å,
  som må dekodes.
- **Volum:** Alle 64 oppdateringer (juni 2024 – september 2026) ligger på én side, uten
  paginering.
- **Filtrering:** Siden er en nyhetsstrøm, ikke en høringsliste. Høringer må plukkes ut med
  søkeord i tittel og ingress. Søkeordene «høring», «offentlig ettersyn», «varsel om oppstart»,
  «varslingsområde», «planprogram», «reguleringsplan» og «merknad» ga 10 treff blant 64
  oppføringer. Minst 2 av treffene var falske (grunnundersøkelser, elfenbenslav), så søkeordene
  må justeres og testes i sprint 4.
- **Frist:** Bare i fritekst på detaljsiden, i ulike former: «Frist for merknader er
  23.05.2025», «innen 3. juli 2026» og «Frist for å levere innspill var 7. april» (uten år).
- **Høringsparter:** Noen ganger listet i teksten, f.eks. Miljødirektoratet, Statsforvalteren,
  NVE, Innlandet fylkeskommune og Lillehammer kommune for Gausadeltaet. Det finnes ingen fast
  struktur.
- **Relevans:** Svært høy. Rv. 4 Hunndalen–Mjøsbrua går gjennom Gjøvik. Varselet om E6
  Moelv–Roterud (2025) ba om kopi av merknader til postmottak@gjovik.kommune.no.
- **Åpne i dag:** 0. Siste frist var 3. juli 2026 (E6 Elstad–Fryasletta).
- **robots.txt:** gir 404, altså ingen begrensninger.
- **Andre regioner:** Bare Innlandet er relevant. Jeg har ikke undersøkt om det finnes
  tilsvarende sider for andre regioner. Planene kunngjøres i tillegg av vertskommunene.

### 3.2 Statens vegvesen – aktiv (to delkilder)
- **a) Regelverkshøringer:** `https://www.vegvesen.no/fag/publikasjoner/hoeringer/`. HTML med
  tittel, ingress, «Høringsfrist: dd.MM.yyyy» og «Referanse: 26-80489-6». Siden inneholder både
  aktive og tidligere høringer (446 frister), og 12 hadde frist fra 29.09 og framover.
  Detaljsiden har «Høringsinstanser» som **PDF-vedlegg**.
- **b) Vegprosjekter:** `https://www.vegvesen.no/vegprosjekter/hoeringer-vegprosjekter/`. HTML
  med prosjektnavn, «Publisert», «Merknadsfrist» og type (varsel om oppstart / offentlig
  ettersyn). Listen gjelder **hele landet** (7 åpne, ingen i Innlandet i dag). Se spørsmål 6.
- robots.txt sperrer `*.pdf`, `/globalassets/` og `/contentassets/`. Høringslister i PDF kan
  derfor ikke hentes automatisk.
- Noen høringer skjer «på vegne av Samferdselsdepartementet». Det kan gi duplikater mot
  regjeringen.no, som må fanges opp av dedupliseringen.

### 3.3 Jernbanedirektoratet – aktiv (endret i v3, etter tips fra Svein)
- **Utgangspunkt:** `https://www.jernbanedirektoratet.no/nyheter/` (WordPress). Siden har
  12 nyheter per side (`/nyheter/page/N/`), omtrent 160 nyheter totalt siden 2018. Det finnes
  ingen egen høringsside (`/horinger/` gir 404).
- **Metode:** WordPress sitt innebygde REST-API:
  `https://www.jernbanedirektoratet.no/wp-json/wp/v2/posts?search=<ord>&per_page=20&_fields=date,link,title,content`.
  Det gir JSON med dato (ISO), tittel, lenke og hele brødteksten, og er enklere og mer stabilt
  enn å parse HTML. robots.txt har tom `Disallow`, så API-et er tillatt. RSS (`/nyheter/feed/`)
  gir HTML og ikke en feed, så den kan ikke brukes.
- **Filtrering:** Nyhetene er stort sett ikke høringer. Søk på «høring» og «på høring» ga 9
  treff siden 2021, men de fleste bare *nevner* høringer (f.eks. Bane NORs ruteplanhøring).
  Et reelt eksempel er «Tre nye utredninger: – Vi løser ikke utfordringene uten jernbanen»
  (09.04.2026): tre utredninger på høring hos jernbanesektoren, **fylkeskommunene** og øvrige
  interessenter.
- **Frist:** Står i fritekst og kan være vag, f.eks. «Høringsperioden blir fra midten av april
  til midten av juni». Uten en eksakt dato kan det ikke regnes «dager igjen».
- **Høringsparter:** Noen ganger nevnt i teksten (se over).
- **Volum:** Lavt, anslagsvis 0–2 reelle høringer i året i nyhetene. Enkelte høringer
  (tilskuddsordning for langdistansebuss, lokførerskolens forskrift) ser ut til å bare ha vært
  publisert som PDF, ikke som nyhet. De fanges ikke opp (ikke verifisert).
- **Åpne i dag:** 0.

### 3.4 Bane NOR SF – aktiv (endret i v3, etter tips fra Svein)
- **Utgangspunkt:** Prosjektlisten
  `https://www.banenor.no/prosjekter/alle-prosjekter/?q=&Baner+%28A-%C3%85%29=&Fylker=14488&Categories=`
  (`Fylker=14488` = Innlandet). HTML med 5 prosjekter: Dobbeltspor gjennom Stange, Hamar
  stasjon, Kapasitetsøkende tiltak Dovrebanen, Oppgradering av Kongsvingerbanen og
  Togparkering Lillehammer.
- **Søk på «gjøvik»** (Sveins lenke) gir 3 prosjekter: Godstiltak Oslo–Bergen, Brynsbakken i
  Oslo og SPOT (vedlikehold). Ingen av dem har planarbeid i Gjøvikregionen i dag, og
  Gjøvikbane-prosjektene er registrert på Oslo og Akershus, ikke Innlandet. Søket bør likevel
  tas med, slik at nye Gjøvik-prosjekter fanges opp.
- **Høringsoppslag** ligger som undersider til hvert prosjekt, ikke i prosjektlisten.
  Prosjektsidene lenker ikke alltid til dem. Den sikreste måten å finne dem på er sitemapet
  `https://www.banenor.no/nb-no/sitemap.xml` (1 704 adresser med `lastmod`), filtrert på
  prosjektnavnene og ord som «regulering», «horing», «varsel», «planprogram» og «ettersyn».
  For Innlandet ga det bl.a.:
  - «Starter reguleringsarbeid i Moelv» (Moelv kryssingsspor, `lastmod` 16.01.2026)
  - «Oppstart av reguleringsarbeid på Dallerud»
  - «Otta stasjon – oppstart av reguleringsarbeid»
  - «Reguleringsplan godkjent i Hamar og Stange» (ikke høring, filtreres bort)
- **Felter på detaljsiden:** tittel, «Publisert: <dato>», saksnummer (f.eks. «Sak: 202408564»)
  og fristen i fritekst, f.eks. «Frist for innspill: 23. …» eller «Frist for å gi innspill:
  Søndag 16. …».
- **Høringsparter:** Ikke oppgitt. Varsel om oppstart går til berørte etter plan- og
  bygningsloven.
- **Åpne i dag:** ikke fastslått. De to oppslagene jeg åpnet, har frister som ser ut til å være
  utløpt, men årstallet er ikke lest ut.
- **robots.txt:** `Allow: /` for alle (bare `/sok/` er sperret, og bare for Googlebot).
- Reguleringsplanene kunngjøres i tillegg av vertskommunen (Ringsaker, Stange, Hamar, Sel m.fl.).

### 3.5 Nkom – aktiv
- `https://nkom.no/hoeringer` (Enonic, statisk HTML). Siden viste i dag «Denne siden har ingen
  undersider enda», altså ingen åpne høringer. Avsluttede høringer ligger på
  `https://nkom.no/tidligere-horinger`, med tekstlig periode (f.eks. «13. april til 15. mai 2026»).
- Frist og høringsparter må hentes fra detaljsiden, der fristen står i fritekst.

---

## 4. Miljø, klima, energi og beredskap

### 4.1 Miljødirektoratet – aktiv
- **URL:** `https://www.miljodirektoratet.no/hearingslistpage/gethearings?skip=0&searchTerm=&searchExpired=false`
- **Metode:** JSON-endepunktet som siden `/hoeringer/` selv kaller (funnet i nettverkstrafikken).
  Samme data ligger også som React-props i HTML-en. Paginering skjer med `skip` (20 per side).
- **Felter:** `title`, `hearingNumber` (f.eks. 2026/6107), `subjects` (tema), `deadline`
  (`dd.MM.yyyy`), `published`, `url`. Totalt antall står i `totalMatching`.
- **Åpne i dag:** 21. Mange gjelder olje og gass eller enkeltbedrifter. Temafeltet kan brukes
  til å nedprioritere dem.
- **Høringsparter:** Detaljsiden nevner høringsinstansene, men selve listen er ikke undersøkt
  (ikke verifisert).

### 4.2 NVE – aktiv (to delkilder)
- **a) Forskriftsendringer:** `https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/`,
  HTML med tittel og dato. Avsluttede er merket «(avsluttet)». Undersidene for veiledere og RME
  er lenket fra `https://www.nve.no/om-nve/hoeringer/`.
- **b) Konsesjonssaker:**
  `https://www.nve.no/umbraco/api/license/getall?caseType=00&county=00&filterText=&municipality=00&pageNumber=1&pageSize=100&progress=0&size=0&stadium=20&type=0`.
  JSON-endepunktet som siden selv bruker. `stadium=20` = «På høring», og `county=34` = Innlandet.
  - Felter: `SoknadId`, `Tittel`, `Tiltakshaver`, `Fylke`, `Kommune`, `Hoeringsfrist`
    (ISO uten tidssone, 23:59:59), `Type` og `Stadium`.
  - Lenke: `https://www.nve.no/konsesjon/konsesjonssaker/konsesjonssak?id=<SoknadId>&type=<Type>`
  - I dag var 14 saker på høring, 2 av dem i Innlandet (Granåsen og Borveggen vindkraftverk i
    Trysil, frist 06.11.2026). Høringspartene er ikke oppgitt.
- robots.txt: `Crawl-delay: 20`. Bruk minst 20 sekunder mellom kall.

### 4.3 DSB – aktiv
- **RSS:** `https://www.dsb.no/rss/rss-dsb---horinger/` gir tittel, lenke og pubDate.
  RSS-en inneholder også «Høringer – samtykker» (samtykke til anlegg for farlig stoff).
- **Liste:** `https://www.dsb.no/horinger/horinger/`, HTML med dato, tittel og
  «Høringsfrist: 18. desember 2024» (norsk tekstdato). Siste høring i listen er fra 19.11.2025,
  så det finnes ingen åpne høringer i dag.
- **Anbefaling:** Bruk RSS for å oppdage nye høringer, og hent fristen fra detaljsiden.

### 4.4 Landbruksdirektoratet – aktiv
- `https://www.landbruksdirektoratet.no/nb/om-direktoratet/horinger`, HTML med tre seksjoner:
  «På høring nå», «Under behandling» og «Avsluttede saker».
- Fristen står som «mandag 12. oktober 2026» i øverste seksjon og som `2.9.2026` i tabellene.
  Parseren må håndtere begge formatene.
- Detaljsiden har «Liste over høringsinstanser (PDF)».
- robots.txt tillater `/nb`.

### 4.5 DSA – inaktiv (forslag)
`https://www.dsa.no/horinger-og-tillatelser` blander tillatelser for petroleumsvirksomhet
(de fleste oppføringene) med sjeldne egne høringer (f.eks. solarier). Fristen står bare i
fritekst. Relevansen for kommunene er lav, og listen gir mye støy. **Forslag:** `aktiv: false`.
Endringer i regelverk om radon og stråling sendes normalt ut av HOD på regjeringen.no.

---

## 5. Oppvekst, utdanning, kultur og integrering

### 5.1 Udir – må avklares
- `https://www.udir.no/om-udir/hoyringar/` laster listen med JavaScript fra
  `https://hoering-publisering.udir.no/api`. API-et gir god JSON: `tittel`, `frist`,
  `publisert`, `status`, `url` (`https://hoering.udir.no/hoering/<id>`), `beskrivelse`,
  `emneknagger` og `vedlegg`.
- **robots.txt på `hoering-publisering.udir.no` og `hoering.udir.no` er `Disallow: /` for
  alle roboter.** Selve udir.no-siden er tillatt, men innholdet kommer fra det sperrede API-et.
- I nettleseren så jeg 12 åpne høringer, bl.a. «Høring om endringer i organisering av
  skoledagen for 1. og 2. trinn» (frist 16. november 2026). Det er svært relevant for kommunene.
- Se spørsmål 1.

### 5.2 IMDi – inaktiv
IMDi har ingen høringsside (`/om-imdi/horinger/` gir 404, og sitemapet har ingen treff).
Regelverk på integreringsfeltet sendes ut av AID på regjeringen.no. **Forslag:** `aktiv: false`.

### 5.3 Bufdir – aktiv
- `https://www.bufdir.no/om/hoeringer/`, HTML med seksjonene «Under behandling» og
  «Avsluttede høringer». Fristen står som tekstdato («3. august 2026»).
- Ingen åpne høringer i dag. Volumet er lavt, men høringene er relevante for kommunene
  (bl.a. barnevernsretningslinjer).

### 5.4 Kulturdirektoratet – inaktiv
Kulturdirektoratet har ingen høringsside. Sitemapet har bare én gammel høringsoppsummering
(2014). **Forslag:** `aktiv: false`.

### 5.5 Riksantikvaren – aktiv
- `https://riksantikvaren.no/siste-nytt/horinger-og-kunngjoringer/`, en nyhetsliste med tittel,
  ingress og «Publisert».
- Fristen står bare i ingressen, f.eks. «Høringsfrist er 30.september 2026». Parseren må
  lete fram datoen i fritekst.
- Listen inneholder også egne uttalelser (f.eks. om bygningsenergidirektivet). Disse bør
  filtreres bort, eller bare oppføringer med «frist» bør tas med.

### 5.6 Arkivverket / Nasjonalarkivet – aktiv
- Arkivverket heter nå **Nasjonalarkivet**, og arkivverket.no videresender til nasjonalarkivet.no.
- Egne høringer ligger på
  `https://www.nasjonalarkivet.no/offentlig-forvaltning/regelverk-og-standarder/riksarkivarens-horinger/`
  (WordPress, HTML). Siden er en enkel tittelliste uten frister, og fristen må hentes fra
  detaljsiden. Volumet er lavt (1–2 i året).

---

## 6. Helse, omsorg og velferd

### 6.1 Helsedirektoratet – aktiv
- `https://www.helsedirektoratet.no/horinger`, HTML med seksjonene «Ute på høring» (tittel +
  «Høringsfrist: dd.MM.yyyy») og «Under behandling». Høringer på nasjonale faglige
  retningslinjer og veiledere er med.
- 5 åpne høringer i dag, bl.a. «Retningslinje for mat, måltider og ernæring i helse- og
  omsorgstjenesten» (frist 03.12.2026).
- Høringsparter: ikke verifisert.

### 6.2 NAV – inaktiv
NAV har ingen høringsside (`/no/nav-og-samfunn/kontakt-nav/hoeringer` gir 404, og sitemapet har
ingen treff). **Forslag:** `aktiv: false`, siden AID sender ut regelverket på regjeringen.no.

### 6.3 DMP – aktiv
- `https://www.dmp.no/om-oss/horinger`, HTML-liste med tittel og «Publisert». Listen har ingen
  frist, så detaljsiden må hentes.
- Detaljsiden har fristen i fritekst («Frist for å gi høringssvar er 9. november 2026»),
  referansenummer og **Høringsliste (PDF)**. Noen høringer sendes «på vegne av HOD» og kan
  derfor finnes som duplikat på regjeringen.no.

### 6.4 FHI – inaktiv
FHI publiserer bare egne høringssvar (`/om/fhi/uttalelser/`) og har ingen liste over høringer
de sender ut selv. **Forslag:** `aktiv: false`.

### 6.5 Mattilsynet – aktiv
- `https://www.mattilsynet.no/hoeringer` videresender til «Regelverksutvikling». Siden har en
  HTML-tabell med «Publisert – Tittel – Høringsfrist» (`dd.MM.yyyy`) over 226
  regelverksprosesser. Tabellen tar også med rader som ikke er høringer, f.eks. «Bestilling til
  VKM …», så bare titler som begynner med «Høring»/«Høyring» skal tas med.
- 8 åpne høringer i dag, bl.a. «Høring – forslag til ny forskrift om materialer og produkter i
  kontakt med drikkevann» (frist 20.10.2026). Den er relevant for kommunale vannverk.
- Siden har JSON-LD.

### 6.6 Arbeidstilsynet – aktiv
- `https://www.arbeidstilsynet.no/regelverk/horinger/`, HTML med «Høringsfrist 14. august 2026»
  og antall svar. Ingen åpne høringer i dag.
- Siden sier selv: «En liste over høringsinstanser ligger lagt ved alle høringene» og «Alle kan
  gi innspill». Høringspartene er derfor tilgjengelige, men ligger i vedlegg.

### 6.7 Statens helsetilsyn – inaktiv
Helsetilsynet publiserer bare egne høringsuttalelser. **Forslag:** `aktiv: false`.

---

## 7. Styring, digitalisering, juss og eiendom

### 7.1 Digdir – aktiv
- `https://www.digdir.no/standarder/hoyringar/1502` (Drupal, HTML) har høringer om IT-standarder
  og referansekatalogen, med statusfilter.
- **Fallgruve:** Fristen står uten årstall («Høyringsfrist 1. oktober»). Årstallet må hentes fra
  detaljsiden eller utledes fra publiseringsdatoen.
- Digdir har også spredte høringer på andre undersider (f.eks. `/informasjonsforvaltning/`) som
  denne listen ikke fanger opp.

### 7.2 DFØ – inaktiv
DFØ har ingen samlet høringsside. Enkelte høringer om anskaffelseskriterier har ligget på
anskaffelser.no, men adressene jeg fant, gir nå 404. Anskaffelsesregelverket sendes ut av NFD
på regjeringen.no. **Forslag:** `aktiv: false`.

### 7.3 DiBK – aktiv
- `https://www.dibk.no/regelverk/horinger/hoyringar`, HTML med «Høringsfrist dd.MM.yyyy» og
  antall svar. Tekniske EØS-høringer ligger på `/regelverk/horinger/tekniske-horinger`.
- Ingen åpne høringer i dag (siste frist 16.06.2026). Høringene gjelder TEK og SAK og er svært
  relevante for kommunene. DiBK sender dem «på oppdrag fra KDD».

### 7.4 Kartverket – inaktiv
Kartverket har ingen høringsside. Høringer kommer som enkeltstående nyheter. **Forslag:**
`aktiv: false`.

### 7.5 UDI – inaktiv
`https://www.udi.no/om-udi/horinger-og-horingsuttalelser/` viser bare UDIs egne høringssvar
(39 stk.), ikke høringer UDI sender ut. **Forslag:** `aktiv: false`.

### 7.6 Politidirektoratet – aktiv
- `https://www.politiet.no/om-politiet/dokumenter-strategier-og-horinger/dokumenter/?innholdstype=72&enhet=103`
  gir ferdig generert HTML med dokumentkort: tittel, «Gjelder fra», **Avsender** og beskrivelse.
  `enhet=103` = Politidirektoratet og `enhet=203` = Innlandet politidistrikt.
- Hvert kort er et **dokument** (PDF), ikke en høring. Én høring kan derfor ha flere kort, og
  fristen står bare i fritekst («på høring til 11. september 2026»).
- Det finnes 4 dokumenter totalt. Siste høring (retningslinje for utgivelse av navn) hadde frist
  11.09.2026.
- robots.txt sperrer `/api/`, men ikke denne siden.

### 7.7 Innlandet politidistrikt – inaktiv
Med samme filter (`enhet=203`) er det bare ett dokument, et høringssvar fra 2020. Distriktet
sender ikke ut egne høringer. **Forslag:** `aktiv: false`. Kilden beholdes som egen, inaktiv
oppføring, slik Svein ønsker.

### 7.8 Skatteetaten – aktiv
- `https://www.skatteetaten.no/rettskilder/type/horinger/` har listen som JSON inne i HTML-en,
  med `title`, `url` og `properties.startPublish` (115 høringer totalt). Listen har ingen frist.
- Detaljsiden har fristen og en egen seksjon «Høringsinstanser» i HTML.

### 7.9 Datatilsynet – inaktiv
Datatilsynet publiserer bare egne høringsuttalelser. Egne veiledere på høring kommer som
nyheter. **Forslag:** `aktiv: false`. robots.txt ga HTTP 500 under undersøkelsen.

### 7.10 SSB – inaktiv
SSB har ingen samlet liste, bare enkeltsider under `/omssb/ssbs-virksomhet/`. Siste høring
hadde frist 4. juni 2026. KOSTRA-endringer varsles gjennom andre kanaler. **Forslag:**
`aktiv: false`.

### 7.11 Konkurransetilsynet – inaktiv
Siste egne høring var fra 2021. Siden «Høringer fra EU-kommisjonen» er ikke relevant for
kommunene. **Forslag:** `aktiv: false`.

### 7.12 Sivilombudet – inaktiv
Sivilombudet publiserer bare høringsuttalelser. **Forslag:** `aktiv: false`.

---

## 8. Regionale ledd

### 8.1 Innlandet fylkeskommune – aktiv
- `https://innlandetfylke.no/politikk/horinger/` (ACOS, HTML). Siden har «Høringer og offentlig
  ettersyn» med tittel, ingress og frist i fritekst («Høringsfrist er 11. november 2026», «Frist
  for innspill er 9. oktober 2026»).
- 2 åpne høringer i dag: planprogram for regional plan for nettinfrastruktur for energi, og
  offentlig ettersyn av fv. 255 Vigga bru i Gausdal.
- Avsluttede høringer ligger på `/politikk/horinger/avsluttede-horinger/`. Gjettet adresse
  `/horinger/` ga HTTP 500.
- robots.txt sperrer bl.a. `/innsyn` og `/artikkelRSS.aspx` (RSS), men ikke `/politikk/`.
- Innlandet fylkeskommune er registrert som enhet på eInnsyn, men eInnsyn kan ikke brukes
  (se 9.1).

### 8.2 Statsforvalteren i Innlandet – aktiv
- `https://www.statsforvalteren.no/innlandet/horinger/` (Episerver, HTML). Siden har filtrene
  «Kommende/Tidligere», tittel, tema og «Høringsfrist: 16. oktober kl. 23:59» **uten årstall**.
- 1 kommende høring i dag: «Oppstart av verneprosess – Frivillig vern av skog – Syv områder».
- Det finnes RSS for nyheter (`/nb/innlandet/nyheter/rss`), men ingen egen RSS for høringer.

---

## 9. Gjøvik kommunes postliste

### 9.1 Alternativ 1: eInnsyn
- Jeg fant ingen tegn til at Gjøvik kommune publiserer postlista si på eInnsyn. Kommunens
  arkivplan sier at postlista publiseres på kommunens egen nettside med tre dagers forsinkelse.
  Dokumenter fra Gjøvik finnes på eInnsyn bare som korrespondanse hos andre virksomheter
  (f.eks. Statsforvalteren).
- **I tillegg:** `https://api.einnsyn.no/robots.txt` er `Disallow: /`, og einnsyn.no sperrer
  `/api/` og `/sok`. eInnsyn er derfor ikke et alternativ.

### 9.2 Alternativ 2: underliggende endepunkt (anbefalt)
- Søkesiden er ACOS «nye-innsyn». Den kaller
  `POST https://www.gjovik.kommune.no/api/presentation/v2/nye-innsyn/overviewInit`, som
  returnerer JSON. Funnet i nettverkstrafikken i nettleseren.
- **Felter per treff:** `title`, `type` («Inngående dokument» / «Utgående dokument» /
  «Møteprotokoll»), `properties.dokumentID` (f.eks. `2026/79694`), `properties.dato`
  (`dd.MM.yyyy`), `properties.avsender`/`mottaker`, `identifier` og `parentIdentifier` (saken).
  Lenken bygges som `…/sok-i-postliste/#/details/<parentIdentifier>/<identifier>`.
- **Filtre:** Svaret inneholder `searchOptions` med fritekst (`titleSearchTerm`), periode
  (`FromDate`/`ToDate`), dokumenttype (egen ID for «Inngående dokument») og sakstype.
  Innhentingen kan derfor be om bare inngående dokumenter de siste 14 dagene, med søkeord.
- **Volum:** 197 623 poster totalt. Nyeste poster var datert 24.09, fem dager før
  undersøkelsesdagen. Det stemmer med «innen tre virkedager» og støtter 14-dagersvinduet.
- **robots.txt:** Sperrer `/innsyn`, `/Innsyn`, `/Innsyn5`, `/Innsyn6`, `/Data` m.m., men
  **ikke** `/api/presentation/` eller søkesiden.
- **`noindex, nofollow, nosnippet, noarchive`:** Siden har disse metataggene. De ber
  søkemotorer om ikke å indeksere eller arkivere siden, men forbyr ikke å lese den. Vi
  publiserer bare våre egne koblinger (tittel, dato og lenke), ikke kopier av postlista.
- **Personvern:** Postlista har navn på privatpersoner som avsendere og mottakere. Innhentingen
  bør bare lagre treff på høringssøkeordene. For avsendere som ikke er virksomheter, bør bare
  tittel og lenke lagres.
- Jeg har bare sett svaret fra `overviewInit`. Selve søkeforespørselen (request body) må
  kartlegges nøyaktig i sprint 7. Et samtykkevindu for informasjonskapsler blokkerte søket
  i nettleseren, og jeg godtok det ikke på vegne av Svein.

### 9.3 Alternativ 3: Playwright
Playwright er ikke nødvendig, fordi alternativ 2 gir strukturerte data direkte. Det holdes i
reserve hvis endepunktet endres.

**Anbefaling:** Alternativ 2, med 1–3 kall per ukentlige kjøring og pauser mellom kallene.
Bør godkjennes av Svein (spørsmål 2).

---

## 10. Datoformater som parseren må håndtere

| Format | Kilder |
|---|---|
| `dd.MM.yyyy` | regjeringen.no, Miljødir., Helsedir., Vegvesen, Mattilsynet, DiBK, Gjøvik postliste |
| `d.M.yyyy` | Landbruksdir. (tabeller) |
| Norsk tekstdato med år («9. november 2026», «mandag 12. oktober 2026») | DMP, Ldir, DSB, Bufdir, Arbeidstilsynet, IFK, Riksantikvaren |
| Norsk tekstdato **uten år** («1. oktober», «16. oktober kl. 23:59») | Digdir, Statsforvalteren |
| Fritekst i ingress eller brødtekst («Høringsfristen er 30.september 2026» – uten mellomrom, «innen 3. juli 2026», «Frist for å gi innspill: Søndag 16. …») | Riksantikvaren, IFK, Politiet, Nye Veier, Bane NOR |
| Vag periode uten dato («fra midten av april til midten av juni») | Jernbanedirektoratet |
| Kompakt `ddMMyyyy` i fritekst («Frist 01102026») | Politiet |
| ISO uten tidssone (`2026-11-06T23:59:59`) | NVE konsesjon |
| ISO med tid (`2026-09-28T12:25:04+00:00`) | Skatteetaten |
| `/Date(ms+0200)/`, tom = år 1 | Stortinget |

Alle kildene jeg har undersøkt, leverer UTF-8, og æ, ø og å kom riktig fram i API- og
JSON-svarene («Næringskomiteen», «Høring», «Høyringar», «Mjøsa»). Unntaket er HTML-kodede
entiteter på regjeringen.no, som må dekodes.

---

## 11. Risikoer

1. **Robots.txt sperrer to aktuelle API-er:** Udir (`hoering-publisering.udir.no`) og eInnsyn
   (`api.einnsyn.no`). Vi respekterer sperrene til Svein har bestemt noe annet.
2. **Frister i fritekst og uten årstall** (Riksantikvaren, Digdir, Statsforvalteren, Politiet,
   IFK, Nye Veier, Jernbanedirektoratet, Bane NOR). Det gir risiko for feil frist.
   Nye Veier, Jernbanedirektoratet og Bane NOR publiserer i tillegg høringer i nyhetsstrømmer
   eller som prosjektnyheter, der høringene må skilles fra andre nyheter med søkeord. Det gir
   risiko for både falske og manglende treff. Tiltak: egen, grundig testet datoparser, og å regne
   fristen som «neste forekomst etter publiseringsdato» når årstallet mangler.
3. **Høringslister i PDF** (Vegvesen, Ldir, DMP, Arbeidstilsynet). Regionflagget i sprint 6 kan
   bli ufullstendig for disse. Vegvesenet sperrer i tillegg `*.pdf` i robots.txt.
4. **Duplikater** når direktorater sender høringer «på vegne av» departementet (DMP/HOD,
   Vegvesen/SD, DiBK/KDD).
5. **Nasjonale lister med lokalt innhold** (NVE-konsesjoner, Vegvesenets prosjekthøringer,
   DSB-samtykker, Miljødirektoratets enkeltutslipp) gir mye støy uten filter på fylke eller tema.
6. **Stortinget:** Høringer i neste sesjon kommer før sesjonsstart, og statusfeltet henger etter.
7. **Strukturendringer:** Flere kilder bruker udokumenterte interne endepunkter (Miljødir., NVE,
   Gjøvik). Disse kan endres uten varsel. Tester per kilde (spesifikasjonen, avsnitt 7) fanger
   det opp.
8. **Oppføringer uten frist** (DMP, Skatteetaten, Nasjonalarkivet, Nkom) krever ett ekstra kall
   per høring. Det øker kjøretiden, men er godt innenfor 30-minuttersgrensen med det lave volumet.
9. **Utviklingsmiljøet:** Python er ikke installert på denne PC-en, og `git` finnes bare via
   GitHub Desktop, ikke i PATH. Begge trengs fra sprint 1.

## 12. Åpne spørsmål til Svein

1. **Udir:** robots.txt sperrer Udirs høringsdata helt. Hva ønsker du?
   - (a) `aktiv: false` inntil videre, og manuell lenke til udir.no/om-udir/hoyringar
   - (b) GRU spør Udir om tillatelse til å bruke API-et. Anbefalt, sammen med (a) i mellomtiden.
   - (c) Hente siden med Playwright likevel. Anbefales ikke, fordi det i praksis omgår sperren.
2. **Postlista:** Godtar du at vi bruker ACOS-endepunktet (alternativ 2) med svært lav trafikk
   og bare lagrer høringstreff? Vil du eventuelt varsle Gjøvik kommunes arkivtjeneste først?
3. **eInnsyn:** Enig i at eInnsyn ikke brukes på grunn av robots.txt?
4. **Departementer som ikke står i spesifikasjonen:** Energidepartementet, Barne- og
   familiedepartementet og Utenriksdepartementet. Forslag til prioritet: BFD 1 (barnevern,
   barnehage), ED 2 (kraft og nett, mye er nasjonalt) og UD 3.
5. **NVE-konsesjoner:** Bare Innlandet (`county=34`), eller hele landet?
   Forslag: bare Innlandet.
6. **Vegvesenets prosjekthøringer:** Hele landet eller bare Innlandet? Listen har ikke
   fylkesfelt, så filtrering krever at detaljsiden eller prosjektsiden hentes.
   Forslag: bare Innlandet.
7. **Kilder foreslått inaktive** (14 stk., se tabellen i avsnitt 1). Er du enig?
   Jernbanedirektoratet oppgir av og til bare en vag frist («midten av juni»). Er det greit at
   slike høringer vises uten «dager igjen»?
8. **Arkivverket** heter nå Nasjonalarkivet. Skal kilden hete det i `sources.yaml` og på
   nettsiden?
9. **Python og git:** Kan jeg installere Python 3.12 (f.eks. med `winget`) og Git for Windows på
   denne PC-en i starten av sprint 1, eller vil du gjøre det selv?
