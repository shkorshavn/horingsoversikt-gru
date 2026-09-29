# Sprint 0 – Kartlegging av kilder: plan

Status: Plan til godkjenning (29. september 2026)

## Mål
Undersøke alle kildene i `SPESIFIKASJON.md` avsnitt 2 og Gjøvik kommunes postliste, og anbefale en innhentingsmetode per kilde. Sprinten gir ingen produksjonskode. Leveransen er `docs/kildekartlegging.md` og sprintrapporten.

## Hva som skal gjøres

### 1. Kildene (39 oppføringer)
- Regjeringen og Stortinget: regjeringen.no og data.stortinget.no (2)
- Transport: Nye Veier, Statens vegvesen, Jernbanedirektoratet, Bane NOR, Nkom (5)
- Miljø og beredskap: Miljødirektoratet, NVE, DSB, Landbruksdirektoratet, DSA (5)
- Oppvekst og kultur: Udir, IMDi, Bufdir, Kulturdirektoratet, Riksantikvaren, Arkivverket (6)
- Helse og velferd: Helsedirektoratet, NAV, DMP, FHI, Mattilsynet, Arbeidstilsynet, Helsetilsynet (7)
- Styring og digitalisering: Digdir, DFØ, DiBK, Kartverket, UDI, Politidirektoratet, Innlandet politidistrikt, Skatteetaten, Datatilsynet, SSB, Konkurransetilsynet, Sivilombudet (12)
- Regionale ledd: Innlandet fylkeskommune, Statsforvalteren i Innlandet (2)

For hver kilde skal kartleggingen svare på dette:
1. **URL** til høringssiden, eventuelt også RSS eller API.
2. **Metode** i prioritert rekkefølge: API, deretter RSS, deretter strukturerte data (JSON-LD eller innebygd JSON), deretter statisk HTML, og til slutt Playwright. Jeg kontrollerer om innholdet ligger i HTML-kilden eller lastes med JavaScript.
3. **Tilgjengelige felter:** tittel, høringsinstans, frist, publiseringsdato, ingress, lenke og referansenummer.
4. **Høringsparter:** om de finnes, og i hvilken form (liste på siden, PDF eller ingenting).
5. **Dekning på regjeringen.no:** Jeg sammenligner de åpne høringene på etatens egen side med regjeringen.no, der jeg kan filtrere på etaten, og konkluderer med om regjeringen.no dekker kilden helt, delvis eller ikke.
6. **robots.txt:** om høringssiden er tillatt å hente.
7. **Anbefaling:** `aktiv: true/false`, metode og begrunnelse.

Stortinget: Jeg bekrefter hvilke endepunkter som gir komitéhøringer (f.eks. `horinger` og `horingsprogram`), hvordan sesjons-ID er bygget opp, og at ny sesjon starter i oktober. Det passer å teste nå, fordi sesjonsskiftet kommer rett etter sprinten.

### 2. Gjøvik kommunes postliste
Jeg følger rekkefølgen i avsnitt 4:
1. eInnsyn: om Gjøvik kommune publiserer der, hvor ofte, og om API-et gir dokumenttype, avsender og journaldato.
2. ACOS-siden: Jeg åpner postlista i nettleseren og leser nettverkstrafikken for å finne JSON-endepunkter, RSS eller eksport.
3. Playwright som siste utvei.

Jeg leser også robots.txt og vurderer `noindex, nofollow`-merkingen. Anbefalingen begrunnes. Hvis automatisk henting ikke ser ut til å være tillatt, rapporterer jeg det til deg i stedet for å anbefale skraping.

### 3. Kilder uten stabil høringsside
Disse listes med forslag om `aktiv: false` og en kort begrunnelse, klart til å overføres til `sources.yaml` i sprint 1.

### 4. Risikoer og åpne spørsmål
Samles i et eget avsnitt i kartleggingen.

## Filer som berøres
- `docs/kildekartlegging.md` (ny): hovedleveransen, med en sammendragstabell og ett avsnitt per kilde
- `docs/sprinter/sprint-00-plan.md` (denne filen)
- `docs/sprinter/sprint-00-rapport.md` (ny): rapport etter malen i `CLAUDE.md`
- `SPRINTSTATUS.md`: bare statuskolonnen

Eventuelle små hjelpeskript for å undersøke kildene legges i en midlertidig mappe utenfor repoet og committes ikke. Er et skript nyttig som bevis, gjengis det i kartleggingen.

## Slik testes og dokumenteres arbeidet
Siden sprinten ikke har produksjonskode, gjelder sjekklisten slik:

| Punkt | Hvordan |
|---|---|
| A. Tester | Ikke relevant: ingen kode. Begrunnes i rapporten. |
| B. Kodekvalitet | Ikke relevant, av samme grunn. |
| C. Ekte data | Per kilde føres antall åpne høringer funnet manuelt på undersøkelsesdagen. Tallet brukes som referanse i sprint 1 og 4–5. |
| D. Stikkprøver | For hver aktiv kilde noteres minst én konkret høring med tittel, frist og lenke som bevis på at feltene finnes. |
| E. Tegn og datoer | Jeg noterer datoformatet hver kilde bruker og kontrollerer at æøå kommer riktig ut i API- og RSS-svar. |
| F. Feilhåndtering | Ikke relevant: ingen kjørende kode. |
| G. Kodegjennomgang | Jeg går gjennom diffen for dokumentene og ser etter feil og mangler. |
| H. Høflighet | Robots.txt sjekkes og dokumenteres per kilde. Undersøkelsen gjøres med få, manuelle kall. |
| I. Dokumentasjon | Kartleggingen er selve dokumentasjonen. README og `sources.yaml` lages i sprint 1. |
| J. Akseptansekriterier | De fem kriteriene for sprint 0 gås gjennom med bevis. |

## Risikoer
- **Mange kilder har ingen egen høringsside.** Flere mindre etater (f.eks. Sivilombudet, Konkurransetilsynet og DSA) publiserer trolig høringer bare via regjeringen.no eller i nyhetsarkivet. Det gir mange `aktiv: false`, og det er et forventet resultat.
- **Felles publiseringsplattformer.** Mange etater bruker samme løsning (f.eks. Episerver/Optimizely). Det er en fordel, fordi én parser da kan dekke flere kilder. Jeg noterer plattform per kilde.
- **Postlista kan være vanskelig.** ACOS med JavaScript og `noindex` kan gjøre automatisk henting teknisk eller formelt uklar. Det er den største usikkerheten i prosjektet.
- **Bot-beskyttelse.** Noen sider kan ha Cloudflare eller lignende. Jeg omgår ikke slik beskyttelse, men markerer kilden og foreslår et alternativ.
- **Øyeblikksbilde.** Kartleggingen viser situasjonen i dag. Kilder med få høringer kan tilfeldigvis ha null åpne høringer akkurat nå. Da ser jeg på arkiverte høringer for å vurdere strukturen.
- **Omfang.** 39 kilder og postlista er mye for én sprint. Jeg prioriterer grundig undersøkelse av prioritet 1-kildene og postlista, og gjør en enklere undersøkelse av prioritet 3-kildene.

## Avklaringer fra Svein (29. september 2026)
1. **User-Agent:** Kontaktadressen er `svein-havar@gjovikregionen.no`, f.eks. `HoringsoversiktGRU/0.1 (+mailto:svein-havar@gjovikregionen.no)`. Tas i bruk fra sprint 1.
2. **Politiet:** Politidirektoratet og Innlandet politidistrikt kartlegges som **to separate kilder**, slik at nasjonal informasjon og informasjon fra politidistriktet holdes adskilt. Det gir 39 kilder i alt.
3. **Modell i sprint 8:** Modellvalget endres ikke nå. I sprint 8 vurderes det på nytt, og den mest hensiktsmessige tilgjengelige Claude-modellen velges.
