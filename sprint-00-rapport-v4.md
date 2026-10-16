# Sprint 0 – Kartlegging av kilder (versjon 4)

Rapportdato: 16. oktober 2026

## Endringer fra versjon 3
Svein satte sprint 0 tilbake til «Ikke startet» 16.10 og ba om en ny gjennomgang. Kartleggingen
fra 29. september (v3) er beholdt som grunnlag. Versjon 4 legger til en kontroll per 16.10 og
nye funn, samlet i kartleggingens **avsnitt 13**. Avsnitt 1–12 er ikke skrevet om, men har
korte henvisninger («v4: …») der funnene er endret.

- **Gjøvik-postlista:** Selve søkeforespørselen er kartlagt (endepunkt `overview`, request body
  og filter for inngående dokumenter). Dette var en kjent mangel i v3. (13.3)
- **Kryssjekk av postlista mot kildene:** 11 inngående høringsbrev til Gjøvik er sjekket. Seks
  er funnet i kildene, to departementshøringer ble *ikke* funnet blant de 40 nyeste på
  regjeringen.no, og resten er uavklart eller faller utenfor kildelistene. (13.4)
- **Stortinget:** Alle 11 planlagte budsjetthøringer hadde påmeldingsfrist som var utløpt da
  kontrollen ble gjort. Det gir nytt spørsmål om daglig kjøring. (13.1, spørsmål 10)
- **Oppdaterte tall** for hovedkildene og sju direktorater per 16.10. (13.1–13.2)
- **To nye risikoer** (12 og 13) og **to nye spørsmål** (10 og 11).
- **Sjekklisten** er kjørt på nytt for endringene. Punktene merket «v4» under er nye.

## Sammendrag
Grunnlaget fra v3 står: 39 kilder er undersøkt, 24 anbefales aktive, 14 inaktive og Udir må
avklares. Versjon 4 lukker den viktigste kjente mangelen i v3 (søkeforespørselen mot
postlista) og viser at postlista er et godt kontrollverktøy: den fant seks sikre samsvar, men
også departementshøringer som ikke dukket opp der de var forventet. Sprinten anbefales godkjent,
under forutsetning av at Svein svarer på spørsmålene i kartleggingens avsnitt 12, nå 11 i alt.

## Hva som er bygget
Ingen produksjonskode, i tråd med planen.

- `docs/kildekartlegging.md` (endret): ny versjonslinje, avsnitt 13, henvisninger i 9.2, 3.5 og
  risiko 6, og spørsmål 10–11
- `docs/sprinter/sprint-00-rapport-v4.md` (ny): denne rapporten
- `SPRINTSTATUS.md`: bare statuskolonnen og kommentaren for sprint 0

Ikke endret: `CLAUDE.md`, `SPESIFIKASJON.md`, `sprint-00-plan.md` og rapportene v1–v3.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Ikke relevant | Ingen kode i sprinten. |
| B. Kodekvalitet | Ikke relevant | Ingen kode, så `ruff` er ikke kjørt. |
| C. Ekte data | Bestått | v3: se kartleggingen avsnitt 1. **v4:** Telt mot kildene 16.10: Stortinget 11 planlagte (alle med utløpt påmeldingsfrist, forklart i 13.1), regjeringen.no 35 «På høring» på side 1–2, Vegvesenet 5 åpne (12 den 29.09, forklart av utløpte frister), fylket 2, Statsforvalteren 1, Helsedir. 2, Landbruksdir. 2 i «På høring nå» (1 utløpt), Nkom 1, Bufdir 0, DiBK 0. Postlista: 848 inngående treff på «høring». |
| D. Stikkprøver | Delvis | v3: én høring per aktiv kilde. **v4:** 11 høringsbrev fra postlista er sjekket mot kildene (tabell under og 13.4). Fem høringer per kilde felt for felt gjennomføres fra sprint 1, som i v3. |
| E. Tegn og datoer | Bestått | v3: avsnitt 10. **v4:** Postlista returnerer UTF-8 med korrekte æ, ø og å i titler og avsendere. Datoformat `dd.MM.yyyy`, som i 10. Ny observasjon: avsendernavn har uensartede store bokstaver og er avkortet (13.3). Kartleggingen er kontrollert for feilkodede tegn (utskrift under). |
| F. Feilhåndtering | Ikke relevant | Ingen kode. **v4:** Observerte feil er dokumentert: Vegvesen.no og miljodirektoratet.no (gammel adresse) avviste WebFetch, og flere gjettede adresser ga 404 (risiko 12). |
| G. Gjennomgang | Bestått | **v4:** Jeg leste `git diff` for kartleggingen (utskrift under) og rettet fire feil før commit: feil antall «På høring»/«Under behandling» på regjeringen.no (33/7 → 35/5), feil antall kall mot postlista («fire» → omtrent 15), Skatteetatens høring som var merket «ikke kontrollert» selv om v3 hadde funnet den, og antall samsvar (fire → seks). |
| H. Høflighet | Delvis | v3: robots.txt lest for alle domener, egen User-Agent og pauser. **v4:** Kontrollen 16.10 ble gjort med WebFetch og i Sveins Chrome, ikke med prosjektets User-Agent. robots.txt ble lest på nytt bare for gjovik.kommune.no (`/api/` er fortsatt ikke sperret). Omtrent 15 kall mot postlisteendepunktet, med pause i skriptene. Ingen sperrede områder brukt, og ingen samtykker godtatt. Udir-listen ble bare vist i nettleseren via udir.no, som v3 vurderte som tillatt. |
| I. Dokumentasjon | Ikke relevant | README og `sources.yaml` opprettes i sprint 1. |
| J. Akseptansekriterier | Bestått | Se tabellen under. |

Kontroll av tegn og omfang (16.10):

```
$ git diff --stat -- docs/kildekartlegging.md
 docs/kildekartlegging.md | 130 ++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 128 insertions(+), 2 deletions(-)
$ grep -c 'Ã' docs/kildekartlegging.md
0
```

## Stikkprøver (v4: postlista mot kildene)

| Postliste | Kilde | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| 01.10, Innlandet fk, planprogram nettinfrastruktur | Fylkets høringsliste | tittel, avsender, frist | Ingen | https://innlandetfylke.no/politikk/horinger/planprogram-pa-horing-regional-plan-for-nettinfrastrukturen-for-energi.81920.aspx |
| 09.10, Statens vegvesen, endring i vegtrafikkloven | Vegvesenets liste, 20-38820 | tittel, avsender, publisert, frist | Ingen | https://www.vegvesen.no/fag/publikasjoner/hoeringer/horing--endring-i-vegtrafikkloven-20-38820/ |
| 07.10, KD, smågruppeundervisning og leksehjelp | Regjeringen.no | tittel, avsender, publisert, frist | Ingen | https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-opplaringsloven-og-privatskolen-smagruppeundervisning-og-leksehjelp/id3170886/ |
| 01.10, KD, gudstjenester og seremonier | Regjeringen.no | tittel, avsender, publisert, frist | Ingen | https://www.regjeringen.no/no/dokumenter/horing-av-forslag-om-a-presisere-i-opplaringsloven-at-skolene-kan-tilby-elever-a-vare-med-pa-gudstjenester-og-andre-seremonier-knyttet-til-religion-og-livssyn/id3173070/ |
| 21.09, Udir, organisering av skoledagen | Udirs liste | tittel, avsender, frist | Ingen (Udir er «må avklares») | https://www.udir.no/om-udir/hoyringar/ |
| 13.10, Skatteetaten, skatteregnskapsområdet | Skatteetatens liste | tittel, avsender | Ingen (fra stikkprøven i v3) | https://www.skatteetaten.no/rettskilder/type/horinger/horing--forslag-til-endringer-pa-skatteregnskapsomradet/ |
| 08.10, AID, integreringsloven | Regjeringen.no | tittel, avsender | **Ikke funnet** blant de 40 nyeste | https://www.regjeringen.no/no/dokument/hoyringar/id1763/ |
| 24.09, HOD, rekvirering for sykepleiere og farmasøyter | Regjeringen.no | tittel, avsender | **Ikke funnet** blant de 40 nyeste | https://www.regjeringen.no/no/dokument/hoyringar/id1763/ |

De to som ikke ble funnet, er ikke feil i kartleggingen, men et funn om kildene. De er
forklart i 13.4 og ligger til grunn for spørsmål 11.

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|
| Alle aktive kilder i avsnitt 2 er undersøkt | Ja | Uendret fra v3: 39 av 39 kilder har eget avsnitt. |
| Per kilde: URL, metode, felter, høringsparter og dekning på regjeringen.no | Ja, med forbehold | Uendret fra v3. **v4:** Kryssjekken (13.4) viser at «Antatt (via X)» for inaktive kilder er usikkert, se spørsmål 11. |
| Postlista er undersøkt og metode begrunnet, inkl. robots.txt | Ja | v3: avsnitt 9. **v4:** Søkeforespørselen er kartlagt (13.3), og robots.txt er kontrollert på nytt. |
| Kilder uten stabil høringsside er listet med forslag om `aktiv: false` | Ja | Uendret fra v3: 14 kilder. |
| Risikoer og åpne spørsmål er listet | Ja | Avsnitt 11 (nå 13 risikoer, inkl. 13.5) og 12 (nå 11 spørsmål). |

## Kjente feil og begrensninger
Fra v3, fortsatt gjeldende:
- Ett kontrollkall mot Udir-API-et før robots.txt var lest (29.09).
- Stikkprøvene er én høring per kilde, ikke fem.
- Høringsparter er ikke verifisert for Miljødir., Helsedir., Mattilsynet, Statsforvalteren,
  IFK, Digdir og Nasjonalarkivet.
- Frist er ikke lest ut for Nasjonalarkivet, og antall åpne er ikke fastslått for
  NVE-forskrifter og Nasjonalarkivet.

Nye i v4:
- **Kontrollen 16.10 er ikke fullstendig.** Bare hovedkildene og sju direktorater er sjekket på
  nytt. Tallene for de øvrige er fra 29.09.
- **Datofilteret i postlista** virket ikke slik jeg prøvde det (13.3). Det er ikke kritisk.
- **Vegvesenets høring om vekter og dimensjoner** (mottatt av Gjøvik 02.10) er ikke avklart.
- **De to departementshøringene som ikke ble funnet** (13.4) er ikke undersøkt videre enn de 40
  nyeste oppføringene.
- **Kontrollen er gjort med andre verktøy enn i v3** (WebFetch og Sveins nettleser), uten
  prosjektets User-Agent. Den sier derfor ikke noe sikkert om hvordan kildene svarer på
  automatisk henting fra en server.
- Den mangelen v3 hadde om postlistens søkeforespørsel er **lukket**.

## Forslag til senere sprinter
Forslagene fra v3 gjelder fortsatt. I tillegg:
- **Sprint 1:** Test henting av alle fem hovedkildene fra GitHub Actions så tidlig som mulig,
  før parserne bygges ferdig (risiko 12).
- **Sprint 1/3:** Hvis Svein svarer ja på spørsmål 10, endres workflowen til daglig kjøring.
  Spesifikasjonen avsnitt 6 må da oppdateres.
- **Alle parsere:** Avgjør om en høring er åpen ut fra fristen, ikke ut fra hvilken seksjon den
  står i (risiko 13).
- **Sprint 7:** Bruk de seks samsvarene i 13.4 som testtilfeller. Legg inn filter for innkomne
  høringssvar og normalisering av avkortede avsendernavn. Finn riktig form på datofilteret.

## Hva Svein bør sjekke selv
1. Les kartleggingens **avsnitt 13** (nytt) og svar på **spørsmål 10 og 11** i avsnitt 12, i
   tillegg til spørsmål 1–9 fra v3.
2. Åpne [Gjøviks postliste](https://www.gjovik.kommune.no/politikk-planer-og-organisasjon/postliste-dokumenter-og-vedtak/sok-i-postliste/),
   søk på «høring», og se at treffene stemmer med utvalget i 13.4.
3. Søk på regjeringen.no etter «integreringsloven» og «rekvirere». Finner du høringene fra AID
   og HOD som Gjøvik har mottatt? Svaret avgjør hvor viktig postlisten er som kontroll.
4. Åpne [Stortingets høringer](https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/horing/)
   og vurder om daglig oppdatering trengs (spørsmål 10).
5. Når du er fornøyd: skriv `JA` og dato i raden for sprint 0 i `SPRINTSTATUS.md`.
