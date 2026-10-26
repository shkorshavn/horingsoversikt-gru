# Sprint 7 – Gjøvik kommunes postliste: plan

Status: Godkjent · 26. oktober 2026 (Sveins svar nederst)

## Mål
Hver uke sjekkes Gjøvik kommunes postliste for inngående høringsbrev. Høringer som kommunen har
mottatt, får merket «Mottatt av Gjøvik kommune» med journaldato og lenke til journalposten.
Høringsbrev i postlista som ikke finnes i oversikten, vises i en egen seksjon. Dermed ser du
også hullene i kildedekningen.

## Akseptansekriterier (SPESIFIKASJON.md, avsnitt 8)
1. Postlista hentes med metoden som ble godkjent i sprint 0.
2. Filtrering på søkeord og 14-dagersvindu virker.
3. Koblingen mot høringene er testet med minst fem kjente høringsbrev fra postlista, med
   treffkvaliteten dokumentert.
4. Terskelen for «Mulig treff» er begrunnet ut fra testresultatene.
5. Seksjonen for postlistetreff uten kobling vises.
6. Feiler postlista, fullføres resten av oppdateringen.

## Metode (godkjent i sprint 0)
- **Kilde:** ACOS «nye-innsyn»-endepunktet som postlistesiden selv bruker:
  `POST https://www.gjovik.kommune.no/api/presentation/v2/nye-innsyn/overview`. Det gir JSON
  med tittel, dokumenttype, dokument-ID (f.eks. `2026/79694`), journaldato, avsender og lenke
  (kildekartleggingen, avsnitt 9.2 og 13.3).
- **eInnsyn** er ikke brukt: Gjøvik publiserer ikke der, og robots.txt sperrer API-et.
  **Playwright** holdes i reserve hvis endepunktet endres.
- **Før jeg skriver kode:** Jeg leser robots.txt på nytt (i sprint 0 var `/api/` ikke sperret),
  og kontrollerer at endepunktet svarer fra GitHub. Blir GitHub avvist, slik regjeringen.no
  gjør, flyttes postlista til PC-en på samme måte som regjeringen.no. Er `/api/` sperret nå,
  stopper jeg og sier fra.

## Hva som hentes
- **Bare inngående dokumenter** (dokumenttypefilteret virker, sprint 0).
- **Søk per søkeord**, sortert nyeste først. Innhentingen blar til den møter journalposter
  eldre enn 14 dager. Datofilteret i API-et virket ikke i sprint 0. Jeg prøver å finne riktig
  form, men trenger det ikke.
- **Søkeordene** står i `sources.yaml`: «høring», «høringsbrev», «høringsnotat»,
  «høringsinvitasjon», «varsel om oppstart», «offentlig ettersyn», «innspill» og
  «konsultasjon». Jeg sjekker om søket på «høring» også treffer «høringsbrev». Gjør det det,
  trengs færre kall.
- **Støy filtreres bort** med `utelat_ord` i konfigurasjonen. Det gjelder høringssvar til
  kommunens egne planer: «Høringsuttalelse», «Høringssvar», «Svar på høring» og «Innspill til
  varsel om oppstart» (sett i sprint 0).
- **Høflighet:** Forventet 8–20 kall per uke, med pause mellom kallene, egen User-Agent og
  robots.txt som før.
- **Personvern:** Bare treff på høringsordene lagres. Avsendernavnet lagres bare når det ser ut
  som en virksomhet (kommune, departement, direktorat, AS, forening o.l.) eller når det er
  koblet til en høring. Ellers lagres bare tittel, dato og lenke (se spørsmål 2).

## Kobling mot høringene (`horinger/kobling.py`, ny)
Hver journalpost får en poengsum mot hver åpne høring (og arkivet de siste 60 dagene):
- **Avsender:** normalisert navn. Store og små bokstaver ignoreres, avkortede navn håndteres
  («Arbeids- Og Inkluderingsdepart» = Arbeids- og inkluderingsdepartementet), og det finnes en
  liste med forkortelser (KDD, KD, HOD …) i konfigurasjonen.
- **Tittel:** likhet med `rapidfuzz` etter at «Høring –», «Høyring av» o.l. er tatt bort.
- **Referansenummer:** når begge har ett (Vegvesenets `20-38820`, regjeringen.no sin «Vår ref.»),
  er samsvar et sterkt treff.

Treffene får to nivåer, med terskler i `sources.yaml`:
- **«Mottatt av Gjøvik kommune»:** sikre treff.
- **«Mulig treff»:** under terskelen for sikre treff, men over terskelen for mulige. Vises med
  et svakere merke.

Terskelene settes ut fra testene med ekte høringsbrev (kriterium 4).

Koblingene lagres i `data/postliste_treff.json`. En markering står derfor også etter at
journalposten har falt ut av 14-dagersvinduet. Journalposter uten treff lagres der også, til
seksjonen «uten treff».

## Nettsiden
- **Merke** på høringen: «Mottatt av Gjøvik kommune 12. oktober 2026», med lenke til
  journalposten. «Mulig treff» vises med et lysere merke.
- **Nytt filter:** «Bare høringer mottatt av Gjøvik kommune».
- **Ny seksjon** «Høringsbrev i postlista uten treff i oversikten»: dato, avsender, tittel og
  lenke, nyeste først.
- **Status:** tidspunkt for siste sjekk av postlista og om den lyktes, i statusoversikten.
- **CSV og utskrift** tar med merket.

## Utvidelse til de andre kommunene
`sources.yaml` får en liste `postlister:` med én oppføring per kommune (navn, adresse, aktiv).
Bare Gjøvik er aktiv nå. Østre Toten, Vestre Toten, Søndre Land og Nordre Land kan legges til
senere med eget merke, hvis de bruker samme ACOS-modul. Det sjekker jeg ikke i denne sprinten.

## Kjøring
- **Rekkefølge** i den ukentlige oppdateringen, slik spesifikasjonen sier: hent høringer → hent
  postlista → bygg (kobling og datafiler) → commit.
- **Feiler postlista**, kjøres resten likevel. Forrige `postliste_treff.json` beholdes, og
  statusen viser feilen.

## Filer som berøres

| Fil | Endring |
|---|---|
| `horinger/postliste.py` (ny) | Henting fra ACOS-endepunktet, filtrering og personvern |
| `horinger/kobling.py` (ny) | Normalisering av avsender, tittellikhet, referansenumre og terskler |
| `horinger/kjor.py`, `horinger/bygg.py` | Postlista som eget steg. Koblingen og `postliste_treff.json` i byggingen |
| `sources.yaml` | `postlister:` (Gjøvik), søkeord, `utelat_ord`, forkortelser og terskler |
| `.github/workflows/oppdatering.yml` | Postlista i den ukentlige kjøringen (eller i PC-jobben, se over) |
| `side/app.js`, `side/stil.css`, `index.html` | Merke, filter, seksjonen «uten treff» og status |
| `requirements-kjoring.txt` | `rapidfuzz` |
| `tests/` + `tests/fixtures/` | Ekte svar fra endepunktet, kobling med ekte høringsbrev og feilhåndtering |
| `README.md` | Nytt avsnitt om postlista |

## Testing og kvalitetssikring
- **Kriterium 3:** minst fem ekte høringsbrev fra postlista med kjent fasit. Utgangspunktet er
  de seks samsvarene fra sprint 0: fylkets planprogram for nettinfrastruktur, Vegvesenets
  vegtrafikklov, de to KD-høringene, Skatteetaten og Udir. Pluss nye fra de siste 14 dagene.
  For hver: poengsum, nivå og om koblingen er riktig. Feilkoblinger og bomtreff telles.
- **Kriterium 4:** terskelen velges der testene gir null feilkoblinger blant sikre treff, og
  begrunnes med tabellen.
- **Kriterium 6:** simulert feil i postlista (feil adresse og tidsavbrudd) viser at resten
  fullføres.
- **Stikkprøver** (D): fem journalposter felt for felt mot postlistesiden.
- Hele sjekklisten A–J og rapport, som før.

## Risikoer
1. **Endepunktet kan endres** (ACOS-oppdateringer). Tiltak: tydelig feil i statusen, og
   Playwright i reserve.
2. **GitHub kan bli avvist** av kommunens nettsted. Tiltak: kjøre postlista fra PC-en.
3. **Avsendernavn er avkortet og uensartet.** Tiltak: normalisering og forkortelseslista, testet
   med ekte navn.
4. **Feilkoblinger** når to høringer fra samme departement har lignende titler. Tiltak:
   referansenummer når det finnes, høy terskel for sikre treff, og «Mulig treff» for resten.
5. **Forsinkelse:** journalposter publiseres med ca. tre dagers forsinkelse. 14-dagersvinduet
   tar høyde for det.
6. **Personvern:** postlista har privatpersoner som avsendere. Tiltak: bare høringstreff
   lagres, og avsendernavn bare for virksomheter.

## Spørsmål til Svein
1. **Varsle kommunen?** I sprint 0 spurte jeg om du vil varsle Gjøvik kommunes arkivtjeneste før
   vi henter fra postlista. Trafikken blir 8–20 kall i uka. Forslag: et kort varsel er
   høflig, men ikke nødvendig. Vil du sende det, kan jeg skrive et utkast.
2. **Avsendere som er privatpersoner:** Er det greit at avsender bare lagres når det er en
   virksomhet, og at slike journalposter ellers vises med bare tittel, dato og lenke? Forslag:
   ja.
3. **Seksjonen «uten treff»:** Hvor langt tilbake skal den vise? Forslag: 60 dager, med de
   nyeste først.
4. **«Mulig treff»:** Skal mulige treff vises på siden med et lysere merke, eller bare i
   rapporten til du har sett kvaliteten? Forslag: vises på siden, tydelig merket som
   «Mulig treff».

## Sveins svar 26.10.2026 kl. 22.45
1. **Varsle kommunen:** Nei. Vi varsler ikke arkivtjenesten.
2. **Privatpersoner som avsendere:** Ja. Avsender lagres bare når det er en virksomhet, og ellers
   bare tittel, dato og lenke.
3. **Seksjonen «uten treff»:** OK, 60 dager.
4. **«Mulig treff»:** Ja. Vises på siden med et lysere merke.

Planen er godkjent («plan godkjent»).
