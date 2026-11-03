# Sprint 12 – Mjøsa og vann alltid med, flere departementer og nye kilder

## Sammendrag
Høringer om Mjøsa og vann står nå alltid i listen og får høy prioritet med begrunnelsen
«gjelder Mjøsa og vann». Det gjelder også når de kommer fra virksomheter som ellers ikke anses
som aktuelle, og når de er representantforslag. Regelen bruker både en ordliste i
`sources.yaml` og KI-instruksen.

Energidepartementet og Barne- og familiedepartementet er tatt inn igjen. Alle de 5 høringene
de har i dag, ble vurdert som relevante. Kystverket er ny kilde, med filter for Mjøsa og vann.
Sjøfartsdirektoratet, Forsvarsbygg, Vannportalen og Folkehelseinstituttet er undersøkt og
settes som inaktive, med begrunnelse.

Under kontrollen fant og rettet jeg tre feil:
- Ordet «Mjøsa» traff firmanavnet «Mjøsanlegget» i en liste over høringsparter.
- Ord som «drikkevann» og «flom» ga falske treff i lange tekster.
- Et KI-svar ble avvist ved tolking.

Alle punktene i sjekklisten er bestått, og jeg anbefaler at sprinten godkjennes.

## Hva som er bygget
1. **«Alltid med»** (`horinger/tema.py`, ny, og `felles.relevans.alltid_med` i `sources.yaml`).
   - **`ord`** treffer i tittel, ingress og teksten fra høringssiden:
     - Mjøsa, Mjøsas, Vorma, Gudbrandsdalslågen, Hunnselva og Lenaelva
     - innsjø*, vannforskrift*, vannforvaltning*, vannområde* og vannregion*
     - ammunisjon* + Mjøsa, ammunisjon* + innsjø* og dumpet ammunisjon*
     - vassdragsregulering*, reguleringskonsesjon* og manøvreringsreglement*.
   - **`ord_tittel`** treffer bare i tittel og ingress. Dette er vanlige ord som ga falske treff
     i lange tekster:
     - vannkvalitet*, vannmiljø*, overvåking* + vassdrag* og avrenning*
     - utslipp til vann/vassdrag/innsjø
     - fartsforskrift*, fartsgrense* + innsjø*/vassdrag*/båt*, båttrafikk*, fritidsbåt*,
       småbåt* og vannscooter*
     - drikkevann*, vannverk*, vannforsyning* og flom*.
   - **Syntaks:** * betyr at ordet kan fortsette («innsjø*» treffer «innsjøer»). Uten * må hele
     ordet stemme. « + » krever at alle delene står i teksten.
   - **Rekkefølge i relevansvurderingen** (`horinger/relevans.py`): «alltid med» går først, så
     fast regel (representantforslag, svar 1), så vern, og til slutt KI-en.
     Representantforslag om Mjøsa sendes likevel til KI-en, slik at de får «Hvorfor relevant».
   - **KI-instruksen** har temaene som «ALLTID relevante, uansett avsender». Alle høringene ble
     vurdert på nytt med den nye instruksen.
   - **Prioritet** (`horinger/prioritet.py`): høy prioritet med grunnen «gjelder Mjøsa og vann»
     (svar 5), også når kildens prioritet allerede er høy.
   - **Kildenes egne filtre slipper slike høringer gjennom:**
     - ekskluderte departementer (regjeringen.no)
     - utelatte temaer (Miljødirektoratet)
     - geografi (DSB samtykkehøringer, NVE konsesjoner og Vegvesenets prosjekter)
     - `krav: aktuell_for_regionen` (Politiet, Konkurransetilsynet og Bane NOR).
2. **Departementene** (svar 3): `ekskluder_departementer` har nå bare Utenriksdepartementet.
3. **Nye kilder** (svar 2 og tillegget kl. 20.49):

| Kilde | Resultat | Begrunnelse |
|---|---|---|
| Kystverket | **Aktiv** (modul `kystverket`) | Høringsside med alle 38 høringer på én side og frist på detaljsiden. robots.txt har bare sitemap. Bare høringer som treffer «alltid med» eller nevner et sted i geografien, tas med. I dag: 0, fordi den ene aktive høringen gjelder avgiftssatser for 2027 |
| Sjøfartsdirektoratet | Inaktiv | robots.txt er «Disallow: /», så hele nettstedet er sperret. /regelverk/horinger/ gir 404 |
| Forsvarsbygg | Inaktiv | Ingen høringsside, og ingen høringssider i sitemapet. Sakene høres av Miljødirektoratet, Statsforvalteren og kommunene, og fanges der av «alltid med» |
| Vannportalen | Inaktiv | Siden er en JavaScript-app uten innhold i HTML-en, og sitemapet gir den samme tomme siden. Vannforvaltningsplanene høres av fylkeskommunen (vannregionmyndighet) og Statsforvalteren, som overvåkes |
| Folkehelseinstituttet | Inaktiv (som før) | Sender ikke ut egne høringer (undersøkt 25.10). Drikkevannsforskriften høres av Mattilsynet og Helse- og omsorgsdepartementet |

4. **Mer robust tolking av KI-svar.** Første JSON-objekt med «relevant» brukes, selv om det
   står tekst eller klammer rundt. I tillegg vises feil i KI-svar som merknader på kjøringen i
   GitHub, siden loggene ikke kan leses herfra.

**Nye filer:**
- `horinger/tema.py`
- `tests/test_mjosa_vann.py`
- `tests/fixtures/kystverket/` (listen og tre detaljsider)
- `docs/sprinter/sprint-12-plan.md`, `docs/sprinter/sprint-12-rapport.md`

**Endrede filer:**
- `sources.yaml`
- `horinger/relevans.py`, `horinger/prioritet.py`, `horinger/bygg.py`, `horinger/sammendrag.py`
- `horinger/kilder/`: `base.py`, `etater.py`, `__init__.py`, `regjeringen.py`,
  `miljodirektoratet.py`, `dsb.py`, `nve.py`, `vegvesen.py`
- `tests/test_regjeringen.py`, `tests/test_sammendrag.py`
- `README.md`

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått | `pytest -v`: **460 bestått, 0 feilet, 0 hoppet over** (64,3 s). 37 nye i `test_mjosa_vann.py` (ordene og falske treff, rekkefølgen, KI-instruksen, prioritet, filtrene i regjeringen.no, Miljødirektoratet, NVE og `aktuell_for_regionen`, Kystverket mot lagrede sider, nye kilder i `sources.yaml`, tolking av KI-svar) og 1 i `test_sammendrag.py`. «Tester» er grønn på GitHub |
| B. Kodekvalitet | Bestått | `ruff check .`: «All checks passed!». `ruff format --check .`: «102 files already formatted». `actionlint`: ingen funn |
| C. Ekte data | Bestått | Ukentlig oppdatering og regjeringen.no (GRUs PC) 03.11. kl. 21.0x: begge «success». Status: **29 kilder «ok»**, 15 ikke overvåket, kjøretid 253 s. Regjeringen.no: 59 åpne (54 dagen før), inkludert 4 fra Energidepartementet og 1 fra Barne- og familiedepartementet. Kystverket: «ok», 0 høringer (ingen om Mjøsa eller vann). Publisering med KI: 132 åpne, **80 i listen og 52 utelatt** (12 av dem er representantforslag) |
| D. Stikkprøver | Bestått | Alle 5 nye høringer fra departementene er hentet på nytt fra PC-en og sammenlignet. Tittel, frist og instans stemte for alle. Høringspartene stemte med siden (to navn med hardt mellomrom i kilden er normalisert riktig). Én liste kommer fra PDF-vedlegg, som før. Kystverket: den ene aktive høringen er kontrollert mot siden, og den skal ikke være med. Se tabellen under |
| E. Tegn og datoer | Bestått | Æ, ø og å er riktige i «Mjøsa», «gjelder Mjøsa og vann» og i JSON-filene (ingen `\u00`-koder). Kystverkets publiseringsdato regnes om fra UTC til norsk tid |
| F. Feilhåndtering | Bestått | En kilde som feiler, stopper ikke resten (`test_en_feil_stopper_ikke_resten` og `test_simulert_feil` gjelder også Kystverket). Ugyldig KI-svar gir feil og nytt forsøk neste gang, og vises som merknad i GitHub (testet). Uten vurdering står høringen i listen |
| G. Kodegjennomgang | Bestått etter retting | `git diff 4727f1a..HEAD` uten data og testdata: 20 filer, 682 nye og 33 fjernede linjer. Se under |
| H. Høflighet | Bestått | Kystverket: robots.txt kontrollert (ingen sperrer), samme User-Agent og pause. Sjøfartsdirektoratet respekteres som sperret, selv om robots.txt mangler linjen «User-agent», siden hensikten er tydelig. Undersøkelsen ble gjort med de vanlige verktøyene, som sjekker robots.txt |
| I. Dokumentasjon | Bestått | README («Relevans for Gjøvikregionen», «Status», «Kilder og innstillinger») og kommentarer i `sources.yaml` (ordlisten, syntaksen, departementene og de fem nye kildene med begrunnelse) |
| J. Akseptansekriterier | Bestått | Se tabellen under |

## Stikkprøver
| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|
| Regjeringen.no (ED) | Tariffer og rapporteringsplikt, energileddet i nettleien | tittel, frist (04.12.2026), instans, parter (129) | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-om-forslag-til-endring-i-forskrift-om-tariffer-og-rapporteringsplikt-for-omsetningskonsesjonarer-adgang-til-a-begrense-storrelsen-pa-energileddet-i-nettleien/id3177359/) |
| Regjeringen.no (ED) | Prisregulering av fjernvarme | tittel, frist (08.12.2026), instans, parter (262) | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-av-forslag-til-endringer-i-energiloven-og-energilovforskriften-om-prisregulering-av-fjernvarme-med-mer/id3176605/) |
| Regjeringen.no (BFD) | Utvidet barnetrygd | tittel, frist (11.12.2026), instans, parter (96, fra PDF) | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-om-endringer-i-vilkarene-for-utvidet-barnetrygd-fjerning-av-muligheten-for-dobbelt-mottak/id3173109/) |
| Regjeringen.no (ED) | Flaskehalsinntekter | tittel, frist (11.12.2026), instans, parter (112) | Ingen | [side](https://www.regjeringen.no/no/dokumenter/ny-side/id3179022/) |
| Regjeringen.no (ED) | Opprinnelsesgarantier | tittel, frist (18.01.2027), instans, parter (259) | Ingen | [side](https://www.regjeringen.no/no/dokumenter/horing-forslag-til-ny-forskrift-om-opprinnelsesgarantier/id3179002/) |
| Kystverket | Nye avgiftssatser for 2027 (eneste aktive) | tittel, publisert 15.10.2026, frist 24.11.2026 (detaljside), utelatt fordi den ikke gjelder Mjøsa eller vann | Ingen | [liste](https://www.kystverket.no/regelverk/horinger/) |

## Ordlisten prøvd mot alle høringene (907, åpne og arkiv)
| Treff | Høring | Riktig? |
|---|---|---|
| Mjøsa (detaljtekst) | Karbonfangstanlegg på Trehørningen, Hamar (Miljødirektoratet): kondensat via HIAS til Mjøsa | Ja |
| drikkevann* | PFAS-grenseverdi i drikkevannsforskriften (Mattilsynet) | Ja |
| drikkevann* | Materialer i kontakt med drikkevann (Mattilsynet) | Ja |
| avrenning* | Overtredelsesgebyr for avrenning (Statens vegvesen) | Ja |
| flom* | Organisatoriske sikringstiltak for flom, stormflo og skred (DiBK) | Ja |

**Falske treff som er fjernet underveis:**
- «drikkevann» på høringssiden om næringsmiddelforskrifter for Svalbard, som du ville ha
  utelatt.
- «flom» i planteksten for fv. 33 Skreia–Bilitt.
- «utslipp til vann» i en tillatelse for en fabrikk utenfor regionen.
- «fartsforskrift» i Kystverkets fartsgrenser på sjøen.
- «Mjøsa» i firmanavnet «Mjøsanlegget» i en liste over høringsparter (opprinnelsesgarantier).

## Endringer i relevansvurderingen etter ny instruks
De 117 høringene som fantes både før og etter, ble vurdert på nytt. 10 byttet side:
- **Inn i listen (5):**
  - karbonfangst i Kirkenær
  - eiendomsmegling
  - overgangsregler til innkrevingsloven
  - honning
  - politiloven (innbringelse av barn)
- **Ut (5):**
  - grossistforskriften (beredskapslagring)
  - førerkort med syn på ett øye
  - klagenemd i finanssektoren
  - gebyrer for Norsk akkreditering
  - sivilforsvarsforskriften

Dette er de samme grensetilfellene som i sprint 8. KI-en er ikke helt stabil på dem.

## Akseptansekriterier
| Kriterium (plan og Sveins svar) | Oppfylt | Bevis |
|---|---|---|
| Høringer om Mjøsa, vannkvalitet, overvåking av innsjøer, fart og båttrafikk, utslipp og avrenning, og ammunisjon i Mjøsa er alltid med | Ja | `test_alltid_med_ordene` (20 tilfeller), KI-instruksen (`test_ki_instruksen_har_temaene`), ekte data (karbonfangst Hamar) |
| Også fra virksomheter som ellers ikke anses som aktuelle | Ja | Filtrene i regjeringen.no, Miljødirektoratet, NVE og `aktuell_for_regionen` slipper slike høringer gjennom (4 tester). Kystverket er ny kilde |
| 1. Går foran regelen om representantforslag | Ja | `test_alltid_med_gaar_foran_representantforslag_og_ki` |
| 2. Nye kilder undersøkt, med filter | Ja | Tabellen over. Kystverket aktiv med filter (`test_kystverket_tar_bare_med_mjosa_og_regionen`), fire satt som inaktive med begrunnelse |
| 3. Energidepartementet og Barne- og familiedepartementet tatt inn igjen, Utenriksdepartementet utenfor | Ja | `test_departementene_er_tatt_inn_igjen`. 5 nye høringer i dag, alle vurdert som relevante |
| 4. Drikkevann, vannverk, flom og vassdragsregulering | Ja | I ordlisten og KI-instruksen (testet) |
| 5. Høy prioritet med begrunnelse | Ja | `test_hoy_prioritet_med_grunn`. Ekte data: «Foreslått prioritet: høy (gjelder Mjøsa og vann)» |

## G. Kodegjennomgang
**Funnet og rettet:**
1. **Falske treff fra ordlisten.** Ordene ble delt i `ord` og `ord_tittel` etter prøving mot
   alle høringene.
2. **«Mjøsa» traff «Mjøsanlegget».** Ord uten * må nå stå som hele ord. Fant det i ekte data
   etter første kjøring, og testen er lagt til.
3. **Et KI-svar ble avvist to ganger** (opprinnelsesgarantier). Tolkingen leter nå etter første
   gyldige JSON-objekt. Etter rettingen ble høringen vurdert som normalt. Årsaken kunne ikke
   leses i loggene, så KI-feil vises nå som merknader på kjøringen.
4. **Representantforslag om Mjøsa ville ikke fått «Hvorfor relevant»**, fordi den faste regelen
   hoppet over KI-kallet. Rettet og testet.

**Vurdert og beholdt:**
- Ordene og grunnteksten står i `sources.yaml`.
- `tema.py` har ingen avhengigheter, så kildene, prioriteten og relevansen bruker samme regel
  uten sirkulære importer.
- Treffet lagres i `alltid_med` mens teksten fra høringssiden finnes i byggingen. Selve teksten
  publiseres fortsatt ikke.

## Kjente feil og begrensninger
1. **Ordlisten fanger bare det den kjenner.** En høring om Mjøsa som verken nevner ordene eller
   blir fanget av KI-en, kan fortsatt bli utelatt. Den ligger da under «Utelatte høringer». Nye
   ord kan legges inn i `sources.yaml`.
2. **Kommunenes egne regler**, for eksempel lokale fartsforskrifter for Mjøsa, overvåkes ikke.
   Bare Gjøviks postliste leses. Dette er foreslått som en senere sprint.
3. **Sjøfartsdirektoratet og Vannportalen kan ikke hentes.** Høringene deres fanges bare når de
   også publiseres hos en kilde vi overvåker.
4. **KI-en er ikke helt stabil på grensetilfeller.** 10 av 117 byttet side med ny instruks.
5. **Kostnad:** to fulle relevansvurderinger og et nytt forsøk i dag (ca. 260 kall), trolig
   under 1 dollar.

## Forslag til senere sprinter
- Postlistene til Mjøsa-kommunene (Hamar, Ringsaker, Stange, Lillehammer, Østre Toten) for
  lokale forskrifter og saker om Mjøsa.
- Arbeidsflyten «Publiser» bruker `ubuntu-latest`, som GitHub flytter til Ubuntu 26. «Tester»
  er allerede låst til 24.04. «Publiser» bør låses på samme måte.

## Hva Svein bør sjekke selv
1. **Mjøsa-merket:** søk på «Mjøsa» på https://shkorshavn.github.io/horingsoversikt-gru/.
   Karbonfangstanlegget på Trehørningen skal stå med «Foreslått prioritet: høy (gjelder Mjøsa
   og vann)».
2. **De nye høringene:** se på høringene fra Energidepartementet og Barne- og
   familiedepartementet. Er det riktig at de står i listen?
3. **Ordlisten:** se gjennom `felles.relevans.alltid_med` i `sources.yaml`. Mangler det ord, for
   eksempel navn på andre innsjøer eller elver i regionen, som Randsfjorden eller Einavatnet?
