# Sprint 6 – Høringsparter og regionflagg: plan

Status: Plan til godkjenning · 26. oktober 2026

## Mål
For hver høring vises hvem den er sendt til (høringsparter), kort kategorisert. Et tydelig flagg
viser om regionen er høringspart: Gjøvik, Østre Toten, Vestre Toten, Søndre Land, Nordre Land,
Gjøvikregionen, «alle kommuner», «alle fylkeskommuner», KS eller Innlandet fylkeskommune. Du kan
filtrere på «Bare høringer der regionen er høringspart», og hele listen kan foldes ut.

## Akseptansekriterier (SPESIFIKASJON.md, avsnitt 8)
1. Høringsparter hentes der kildene har dem, og kategoriseres.
2. Regionflagget settes ut fra søkeordene i konfigurasjonen, inkludert «alle kommuner».
3. Minst tre høringer der kommunene er kjent høringsinstans, er verifisert med riktig flagg.
4. Minst tre høringer uten regionen som høringspart er verifisert uten flagg (ingen falske treff).
5. Full liste kan utvides på nettsiden.

## Hvor høringspartene står

Bygger på kartleggingen fra sprint 0 og det jeg så i sprint 4 og 5. Jeg kontrollerer hver kilde
og robots.txt før jeg skriver kode.

| Kilde | Hvor | Plan |
|---|---|---|
| **Regjeringen.no** (52 åpne) | Detaljsiden har avsnittet «Høringsinstanser», ofte som liste på siden, ellers som PDF | Hentes fra PC-en, som i dag. Det gir ca. 52 ekstra kall i uken. Detaljsidene caches, så bare nye høringer hentes på nytt |
| Skatteetaten | Avsnitt «Høringsinstanser» i HTML | Leses fra detaljsiden, som allerede hentes |
| Helsedirektoratet, Arbeidstilsynet, Nkom m.fl. | Tekst som «offentlig høring, alle er velkomne» | Vises som «Åpen for alle» |
| Stortinget | Komitéhøringer er åpne for alle som melder seg | Vises som «Åpen for alle» |
| Landbruksdir., DMP, SSB, Arbeidstilsynet, Miljødir. | Høringsliste som PDF | Leses der robots.txt tillater det (se spørsmål 1) |
| Statens vegvesen | Høringsliste som PDF, men robots.txt sperrer `*.pdf` | **Ikke mulig.** Vises som «Høringsparter ikke tilgjengelig» |
| Fylkeskommunen, Statsforvalteren, Nye Veier, Bane NOR | Planvarsler etter plan- og bygningsloven, sendt til berørte | Ofte i teksten. Leses der det står, ellers «ikke oppgitt» |

## Kategorisering og regionflagg
- **Kategorier** (flere kan gjelde én høring): «Alle kommuner», «Alle fylkeskommuner»,
  «Departementer og direktorater», «Statsforvaltere», «Organisasjoner» og «Åpen for alle». Ordene
  som avgjør kategorien, står i `sources.yaml`.
- **Regionflagg:** settes når listen nevner et søkeord fra `sources.yaml` (`regionflagg.sokeord`).
  Utgangspunktet er spesifikasjonens liste: de fem kommunene, Gjøvikregionen, «alle kommuner», «alle
  fylkeskommuner», KS og Innlandet fylkeskommune. Grunnen lagres, f.eks. «Alle kommuner» eller
  «Gjøvik kommune».
- **Falske treff unngås:** Søkeordene må stå i listen over høringsparter, ikke ellers i teksten. «KS»
  må stå som eget ord (ikke i «KS2» eller «Statens vegvesen KS»), og «Gjøvik» må ikke treffe «Gjøvik
  tingrett» eller «Sykehuset Innlandet, Gjøvik» (se spørsmål 2).
- **Prioritet:** Har en høring regionflagg, løftes den til høy med grunnen «regionen er
  høringspart». Det er det løftet vi manglet ekte treff på i sprint 4 og 5.

## Nettsiden
- Flagget vises ved tittelen, f.eks. «Regionen er høringspart: alle kommuner».
- Kort kategorisering under ingressen, f.eks. «Høringsparter: Alle kommuner, Organisasjoner (148)».
- Lenken «Vis alle høringsparter (148)» folder ut hele listen. Den er tilgjengelig med tastatur
  og skjermleser (`<details>`).
- Nytt filter «Bare høringer der regionen er høringspart», som spesifikasjonen ber om.
- Utskrift og CSV: kategori og flagg tas med. Den fulle listen tas ikke med i utskriften, så antall
  sider holder seg nede.

## Filer som berøres

| Fil | Endring |
|---|---|
| `horinger/horingsparter.py` (ny) | Tolking av lister (HTML og PDF), kategorisering og regionflagg |
| `horinger/kilder/regjeringen.py` | Henter detaljsiden for høringsinstanser, med cache |
| `horinger/kilder/etater.py`, `stortinget.py` og andre | Høringsparter fra detaljsider de allerede henter, og «Åpen for alle» |
| `horinger/modell.py`, `horinger/bygg.py`, `horinger/prioritet.py` | Nye felt (`horingsparter`, `partkategorier`, `regionflagg`), og løft ved flagg |
| `sources.yaml` | `regionflagg.sokeord`, kategoriord, og PDF per kilde |
| `side/app.js`, `side/stil.css`, `index.html` | Flagg, kategori, utfoldbar liste og nytt filter |
| `requirements-kjoring.txt` | `pypdf` (hvis ja på spørsmål 1) |
| `tests/` + `tests/fixtures/` | Ekte høringslister fra regjeringen.no og etatene, med og uten regionen |

## Testing og kvalitetssikring
- **Kriterium 3:** Minst tre ekte høringer der kommunene er høringsinstans, f.eks. KDD-høringer
  sendt til «alle kommuner» og høringen om fylkeskommunale tannhelsetjenester (HOD). Flagget
  kontrolleres mot listen på regjeringen.no.
- **Kriterium 4:** Minst tre ekte høringer uten regionen, f.eks. kystruten Bergen–Kirkenes (SD),
  pengespill (KUD) og forsvarsindustri (FD). Kontrolleres for falske treff.
- Tester av «KS», «Gjøvik» o.l. mot ord som ikke skal treffe.
- Hele sjekklisten A–J og rapport, som før.

## Risikoer
1. **Regjeringen.no fra PC-en:** 52 flere kall. Cloudflare kan reagere på flere kall. Tiltak: pause
   som i dag, cache, og bare nye høringer.
2. **robots.txt på regjeringen.no:** I sprint 1 så jeg at bare `?page=` er tillatt av
   spørreparametre. Detaljsidene har ingen parametre, men jeg kontrollerer på nytt. Er de sperret,
   kan høringspartene ikke hentes fra regjeringen.no, og det sier jeg fra om.
3. **Lister i PDF** varierer i form. Noen er skannede bilder og kan ikke leses. Tiltak: tester per
   kilde, og «ikke tilgjengelig» når det ikke går.
4. **Falske treff i regionflagget** (f.eks. «KS», «Gjøvik» i adresser). Tiltak: søk bare i
   høringslisten, hele ord, og egne negative tester.
5. **Kjøretiden øker**, mest på PC-en. Forventet under 5 minutter totalt.

## Spørsmål til Svein
1. **PDF-lister:** Mange etater legger høringslisten bare i PDF. Skal jeg lese PDF-ene der robots.txt
   tillater det? Det gir mer komplett flagg, men flere kall og en ny avhengighet (`pypdf`). Forslag:
   ja.
2. **Søkeord for regionflagget:** Spesifikasjonen har de fem kommunene, Gjøvikregionen, «alle
   kommuner», «alle fylkeskommuner», KS og Innlandet fylkeskommune. Skal også Gjøvikregionen IPR,
   Statsforvalteren i Innlandet eller nabokommunene gi flagg? Forslag: legge til «Gjøvikregionen
   IPR» og «regionråd/interkommunale politiske råd», men ikke Statsforvalteren og nabokommunene.
3. **Tema fra regjeringen.no:** Når detaljsidene uansett hentes, kan vi også lese regjeringen.no
   sitt tema (f.eks. «Skole og videregående opplæring»). Da blir Tema-filteret et saksfelt for de 52
   departementshøringene. Skal det med i denne sprinten? Forslag: ja, som eget felt «Saksfelt»,
   mens dagens Tema beholdes.
4. **Automatiske tester ved push:** I sprint 4 og 5 slapp to feil gjennom fordi tester og kodesjekk
   ikke kjører automatisk når koden lastes opp. Skal jeg legge inn det i denne sprinten (én liten
   arbeidsflyt)? Forslag: ja.
