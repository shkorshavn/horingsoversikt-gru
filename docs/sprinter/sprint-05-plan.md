# Sprint 5 – Direktorater, prioritet 2 og 3: plan

Status: Plan til godkjenning · 25. oktober 2026

## Mål
Alle etater med prioritet 2 og 3 overvåkes automatisk eller er satt til `aktiv: false` med
begrunnelse. Filtrene for tema og prioritet virker med alle kilder, og hele innhentingen tar
under 30 minutter. I tillegg gjøres to rettelser du la til sprint 5 den 25.10.

## Akseptansekriterier (SPESIFIKASJON.md, avsnitt 8)
1. Alle prioritet 2- og 3-kilder er lagt til eller satt til `aktiv: false` med begrunnelse.
2. Filtre for kategori og prioritet virker med alle kilder.
3. Stikkprøver er gjennomført for hver ny kilde.
4. Total kjøretid for innhentingen er målt og holder seg under 30 minutter.

## Kildene som bygges (9)

Bygger på kildekartleggingen fra sprint 0 (avsnitt 3–7). Før jeg skriver kode for en kilde,
kontrollerer jeg siden og robots.txt på nytt, slik som i sprint 4.

| Kilde | Pri | Metode | Utvalg | Merknad |
|---|---|---|---|---|
| Nkom | 2 | HTML + detaljside | Alle åpne. Fristen står i fritekst på detaljsiden | Bredbånd og digital infrastruktur |
| Landbruksdirektoratet | 2 | HTML | Seksjonen «På høring nå» | To datoformater («mandag 12. oktober 2026» og `2.9.2026`) |
| Riksantikvaren | 2 | HTML-nyhetsliste | Bare oppslag med frist. Egne uttalelser utelates. Fredningssaker bare med geografisk treff (se spørsmål 1) | Fristen i ingressen, f.eks. «30.september» uten mellomrom |
| Nasjonalarkivet (tidl. Arkivverket) | 2 | HTML + detaljside | Riksarkivarens høringer | 1–2 i året |
| DMP | 2 | HTML + detaljside | Høringer fra de siste 120 dagene, med fristen fra detaljsiden | Noen sendes på vegne av HOD og dedupliseres |
| Mattilsynet | 2 | HTML-tabell | Bare rader der tittelen begynner med «Høring»/«Høyring» | Bl.a. drikkevann, relevant for kommunale vannverk |
| Arbeidstilsynet | 2 | HTML | Alle åpne | |
| Politidirektoratet | 2 | HTML-dokumentkort | Kort med «på høring til <dato>». Flere dokumenter fra samme høring slås sammen | |
| Skatteetaten | 2 | JSON i HTML + detaljside | Høringer fra de siste 120 dagene, med fristen fra detaljsiden | Eiendomsskatt og folkeregister |

Alle får prioritet 2 (middels). De løftes til høy etter regelen fra sprint 4 når de gjelder
kommunene eller regionen. DSA er den eneste med prioritet 3, og den forblir inaktiv.

**Forblir `aktiv: false`, med begrunnelse** (kontrolleres og skrives i `sources.yaml` og README):

| Kilde | Begrunnelse fra kartleggingen |
|---|---|
| DSA | Mest petroleumstillatelser, lav relevans |
| Kulturdirektoratet | Ingen høringsside |
| FHI | Publiserer bare egne høringssvar |
| Statens helsetilsyn | Publiserer bare egne uttalelser |
| Kartverket | Ingen høringsside |
| UDI | Viser bare egne høringssvar |
| Innlandet politidistrikt | Sender ikke ut egne høringer |
| Datatilsynet | Publiserer bare egne uttalelser. Veiledere på høring kommer som nyheter |
| SSB | Ingen samlet liste |
| Konkurransetilsynet | Siste egne høring fra 2021 |
| Sivilombudet | Publiserer bare høringsuttalelser |

Fire av dem (Datatilsynet, SSB, Konkurransetilsynet og Sivilombudet) mangler begrunnelse i
`sources.yaml` i dag. Den føres inn.

## Rettelser fra sprint 4 (Svein 25.10.2026)
1. **Frist med bare måned og år** (NVE: «innen høringsfristen desember 2026»): Fristen hentes fra
   teksten og vises i listen som «Høringsfrist: desember 2026», ikke som «Frist ikke oppgitt».
   - I datafilen lagres måneden (`frist_maned: 2026-12`).
   - Fristboksen viser «des. 2026» og «Frist i desember».
   - Høringen sorteres som om fristen er siste dag i måneden, og havner sammen med de andre
     desemberfristene (se spørsmål 2).
   - Det samme gjelder alle kilder der fristen bare har måned og år.
2. **Ingressen kuttes ved et helt ord** og avsluttes med «…», ikke midt i et ord.

## Filtre og kjøretid
- **Filtrene:** Nye tester sjekker at nedtrekkslisten «Tema» har alle temaene fra
  `sources.yaml` som har åpne høringer, og at prioritetsfilteret skiller høy, middels og lav med
  ekte data.
- **Kjøretid:** Hver kilde måler allerede tiden sin (`sekunder` i `data/kilder/`). Jeg legger til
  total tid i loggen og i `status.json`, og måler en full kjøring i GitHub. NVE alene tar ca.
  2 minutter (20 s mellom kall). Forventet total er 5–8 minutter.

## Filer som berøres

| Fil | Endring |
|---|---|
| `horinger/kilder/nkom.py`, `landbruksdirektoratet.py`, `riksantikvaren.py`, `nasjonalarkivet.py`, `dmp.py`, `mattilsynet.py`, `arbeidstilsynet.py`, `politidirektoratet.py`, `skatteetaten.py` | Nye kildemoduler. Enkle lister legges i `enkle_lister.py` |
| `horinger/kilder/__init__.py`, `sources.yaml` | Registrering, `modul`, `aktiv: true`, merknader og begrunnelser |
| `horinger/datoer.py`, `horinger/modell.py`, `horinger/bygg.py`, `horinger/kilder/nve.py` | Frist med måned og år (`frist_maned`) |
| `horinger/kilder/base.py` | Ingress kuttes ved helt ord |
| `horinger/kjor.py`, `horinger/bygg.py` | Total kjøretid i logg og `status.json` |
| `side/app.js`, `side/stil.css` | Visning og sortering av måned-frister |
| `tests/` + `tests/fixtures/` | Tester og lagrede sider per kilde. Tester av filtre, måned-frist og ingress |
| `README.md` | Tabellen «Etatens side eller regjeringen.no» utvidet med de nye kildene |

## Testing og kvalitetssikring
- Hver kilde testes mot en lagret kopi av siden: antall, felt, frist og årstall. Datoformatene
  med og uten mellomrom («30.september») testes særskilt.
- Kjøring mot ekte data i GitHub, med antall per kilde og forklaring på 0 eller uventet mange.
- Stikkprøver: 5 høringer per ny kilde (eller alle, hvis færre), felt for felt mot kildens side.
  Kilder med 0 åpne kontrolleres mot siden.
- Hele sjekklisten A–J og rapport, som før.

## Risikoer
1. **Kilder som avviser GitHub.** Tiltak: flytte dem til PC-en (`kjoring: pc`) og si fra.
2. **Frister i fritekst** (Riksantikvaren, Nkom, Politiet, DMP) kan gi feil frist. Tiltak:
   strengere fristtolkning fra sprint 4 og egne tester per format.
3. **Politidirektoratets dokumentkort** er dokumenter, ikke høringer. Tiltak: slå sammen kort med
   samme høring og test med ekte eksempel.
4. **Mattilsynets tabell** har også rader som ikke er høringer. Tiltak: bare titler som begynner
   med «Høring», testet mot hele tabellen.
5. **Flere kall gir lengre kjøretid.** Tiltak: detaljsider bare for nye oppslag, og måling
   (kriterium 4).
6. **Mange flere høringer med middels prioritet** kan gjøre listen lang. Standardvisningen viser
   høy og middels, som i dag. Lav vises bare når du krysser av for den.

## Spørsmål til Svein
1. **Riksantikvaren:** Listen har også fredningssaker for enkeltbygg i hele landet. Skal de
   filtreres med samme geografi som Vegvesenet og NVE, mens regelverkshøringer tas med uansett?
   Forslag: ja.
2. **Frist med bare måned:** Er det greit at «desember 2026» sorteres som 31. desember, og at
   siden ikke viser «dager igjen» før det finnes en eksakt dato? Forslag: ja.
3. **DMP (legemidler):** De fleste høringene gjelder legemiddelregelverk og apotek. Skal DMP ha
   prioritet 2 som i spesifikasjonen, eller 3 (lav, skjult som standard)? Forslag: 3, med løft
   når høringen gjelder kommunene (f.eks. legemidler i sykehjem og hjemmetjeneste).
