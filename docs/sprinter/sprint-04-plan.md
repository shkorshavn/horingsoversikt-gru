# Sprint 4 – Direktorater, prioritet 1: plan

Status: Plan til godkjenning · 25. oktober 2026 (oppdatert med Sveins svar kl. 16.54)

## Mål
Alle direktorater og etater med prioritet 1 overvåkes automatisk, eller er satt til
`aktiv: false` med en begrunnelse. Høringer som både etaten og regjeringen.no publiserer, vises
bare én gang.

## Akseptansekriterier (SPESIFIKASJON.md, avsnitt 8)
1. Alle prioritet 1-kilder i avsnitt 2 som ikke kom med i sprint 1, er lagt til eller satt til
   `aktiv: false` med begrunnelse.
2. Deduplisering mot regjeringen.no er testet med minst to konkrete eksempler.
3. Stikkprøver er gjennomført for hver ny kilde.

## Kildene

Tabellen bygger på kildekartleggingen fra sprint 0 (`docs/kildekartlegging.md`, avsnitt 3–7).
Før jeg skriver kode for en kilde, kontrollerer jeg at siden fortsatt ser slik ut og hva
robots.txt tillater. Kartleggingen er fra 29.9 og 16.10.

| # | Kilde | Metode | Hvordan høringene plukkes ut | Merknad |
|---|---|---|---|---|
| 1 | **Miljødirektoratet** | JSON-endepunktet høringssiden selv bruker | Alle åpne. Høringer med tema olje og gass tas ikke med (se spørsmål 3) | ~21 åpne i sprint 0 |
| 2 | **NVE – forskrifter og veiledere** | HTML | Alle som ikke er merket «(avsluttet)». Fristen hentes fra detaljsiden | robots.txt krever 20 s mellom kall |
| 3 | **NVE – konsesjonssaker** | JSON-endepunktet, `stadium=20` (på høring) | Samme geografiske filter som Vegvesenet (se spørsmål 1) | Vindkraft, vannkraft og kraftlinjer |
| 4 | **DSB** | RSS for å finne nye høringer, detaljsiden for fristen | Alle høringer. Samtykker til anlegg for farlig stoff bare med geografisk treff | 0 åpne i sprint 0 |
| 5 | **Helsedirektoratet** | HTML, seksjonen «Ute på høring» | Alle | Nasjonale faglige retningslinjer |
| 6 | **Bufdir** | HTML | Alle åpne | Fristen som tekstdato |
| 7 | **Digdir** | HTML | Alle åpne. Årstallet mangler i fristen og hentes fra detaljsiden | |
| 8 | **DiBK** | HTML | Alle åpne (TEK, SAK, universell utforming) | Sendes «på oppdrag fra KDD», så den kan også ligge på regjeringen.no |
| 9 | **Nye Veier (Innlandet)** | HTML-nyhetsstrøm | Søkeord (varsel om oppstart, offentlig ettersyn, planprogram, merknad …), testet mot alle 64 oppslag | Rv. 4 Hunndalen–Mjøsbrua |
| 10 | **Jernbanedirektoratet** | WordPress-API | Søkeord i tittel og tekst. Vag frist vises som tekst (se spørsmål 2) | 0–2 i året |
| 11 | **Bane NOR (Innlandet og Gjøvik)** | Sitemap + detaljsider | Prosjektene i Innlandet og søket «gjøvik», og ord som «regulering», «varsel» og «planprogram» | Fristen i fritekst |

**Allerede satt til `aktiv: false` med begrunnelse** (kontrolleres og står i rapporten):
Utdanningsdirektoratet (droppet av Svein 16.10, datakilden er sperret i robots.txt), IMDi
(ingen høringsside), NAV (ingen høringsside) og DFØ (ingen samlet høringsside).

Kildene får `kjoring: github`. Avviser en kilde GitHub slik regjeringen.no gjør, flytter jeg
den til PC-en (`kjoring: pc`) og sier fra.

## Deduplisering
Mange direktoratshøringer ligger også på regjeringen.no, for eksempel DiBK på oppdrag fra KDD og
Helsedirektoratet på oppdrag fra HOD. Plan:
- Høringer fra to kilder regnes som samme høring når den normaliserte tittelen er lik eller
  nesten lik (ord, ikke tegn), **og** fristen er lik.
- Da vises høringen én gang, med etaten som høringsinstans. På siden står «Også på
  regjeringen.no», og den har begge lenkene.
- Dedupliseringen gjøres i `bygg.py`, slik at den virker uansett hvilken maskin kildene ble
  hentet fra.
- Testes med minst to konkrete eksempler fra ekte data. Finnes det ikke to åpne par i dag, bruker
  jeg avsluttede par fra kildene som testdata, og sier det i rapporten.

## Prioritet per departement (forslag, se spørsmål 4)
Spesifikasjonen gir departementene ulik prioritet: KDD, KD, HOD, AID, DFD og FIN har 1, de
øvrige har 2. I dag har alle høringer fra regjeringen.no prioritet 1. Det gjør det nye flagget
«Foreslått prioritet» lite nyttig. Jeg foreslår å legge prioritet per departement inn i
`sources.yaml`, og per tema for Miljødirektoratet.

## Filer som berøres

| Fil | Endring |
|---|---|
| `horinger/kilder/miljodirektoratet.py`, `nve.py`, `dsb.py`, `helsedirektoratet.py`, `bufdir.py`, `digdir.py`, `dibk.py`, `nye_veier.py`, `jernbanedirektoratet.py`, `bane_nor.py` | Nye kildemoduler |
| `horinger/kilder/__init__.py` | Registrering |
| `horinger/sokeord.py` | Felles søkeordfilter for nyhetsstrømmene (Nye Veier, Jernbanedir., Bane NOR) |
| `horinger/dedup.py` (ny) og `horinger/bygg.py` | Deduplisering |
| `horinger/kilder/regjeringen.py` og `sources.yaml` | Prioritet per departement (hvis ja på spørsmål 4) |
| `sources.yaml` | `modul`, `aktiv: true` og merknader for de nye kildene |
| `side/app.js`, `side/stil.css` | «Også på regjeringen.no» med ekstra lenke |
| `tests/` + `tests/fixtures/` | Lagrede kopier av hver kildeside og tester per kilde, dedup og søkeord |
| `README.md` | Valget mellom etatens side og regjeringen.no per kilde, som spesifikasjonen krever |

## Testing og kvalitetssikring
- Hver kilde får tester mot en lagret kopi av siden: antall, felt, frist og årstall.
  Søkeordfiltrene testes også mot kjente falske treff, for eksempel Nye Veiers
  grunnundersøkelser og elfenbenslav.
- Testkjøring mot ekte data i GitHub. Antall per kilde, og forklaring på tall som 0 eller
  uventet mange.
- Stikkprøver: 5 høringer per ny kilde (eller alle, hvis færre), felt for felt mot kildens side.
  Har en kilde 0 åpne, kontrollerer jeg det mot siden og tester mot avsluttede høringer.
- Hele sjekklisten A–J og rapport, som før.

## Risikoer
1. **Kilder som avviser GitHub** (slik regjeringen.no gjør). Tiltak: flytte dem til PC-en.
2. **Frister i fritekst og uten årstall** (Digdir, Nye Veier, Bane NOR, Jernbanedir.) kan gi feil
   frist. Tiltak: dato fra detaljsiden, egne tester per format, og rapportere usikre tilfeller.
3. **Søkeordfiltre** i nyhetsstrømmene kan gi falske eller manglende treff. Tiltak: test mot alle
   oppslag i dag, og list hva som ble tatt med og ikke.
4. **Udokumenterte endepunkter** (Miljødir., NVE) kan endres. Tiltak: feil vises i statustabellen,
   og forrige data beholdes.
5. **NVE krever 20 sekunder mellom kall.** Kjøringen tar da noen minutter lenger. Ellers ingen
   konsekvens.
6. **Støy fra nasjonale lister** (Miljødir. enkeltbedrifter, NVE, DSB-samtykker). Tiltak:
   geografisk filter og temafilter, se spørsmålene.
7. **Feil dedup** kan slå sammen to ulike høringer. Tiltak: krav om lik frist i tillegg til
   tittel, og tester av par som ikke skal slås sammen.

## Spørsmål til Svein
1. **NVE-konsesjoner:** Skal de filtreres med samme geografi som Vegvesenets prosjekter
   (Gjøvikregionen og nabokommunene)? Alternativet er hele Innlandet. Forslag: samme geografi
   som Vegvesenet.
2. **Vage frister** (f.eks. Jernbanedirektoratets «midten av juni»): Er det greit at høringen
   vises med fristen som tekst, uten «dager igjen», og sorteres sist? Forslag: ja.
3. **Miljødirektoratet:** Skal høringer om olje og gass (petroleum) tas bort, slik vi gjorde med
   Sokkeldirektoratet og Havtil? Forslag: ja.
4. **Prioritet per departement:** Skal jeg legge inn spesifikasjonens prioritet (KDD, KD, HOD,
   AID, DFD og FIN høy, de andre middels) i denne sprinten, slik at flagget «Foreslått
   prioritet» skiller? Forslag: ja.

## Sveins svar 25.10.2026 kl. 16.54
1. NVE-konsesjoner: samme geografi som Vegvesenet. **OK.**
2. Vage frister vises som tekst, uten «dager igjen», og sorteres sist. **JA** (skrevet «AJ», tolket
   som ja).
3. Olje og gass tas bort fra Miljødirektoratet. **JA.**
4. Prioritet per departement: **JA, med mindre det er klart at høringen er av stor betydning for
   kommunene eller regionen.** Slik bygges det:
   - Departementene får prioriteten fra spesifikasjonen. KDD, KD, HOD, AID, DFD og FIN får høy.
     De andre får middels.
   - En høring fra et departement med middels prioritet løftes til **høy** når tittel eller
     ingress klart gjelder kommunene eller regionen. Det gjelder når teksten nevner kommuner,
     kommunale oppgaver, fylkeskommunen, plan- og bygningsloven, Innlandet eller en kommune i
     Gjøvikregionen eller nabokommunene. Ordlisten ligger i `sources.yaml` og kan justeres uten
     kodeendring.
   - Siden viser hvorfor en høring er løftet, for eksempel «Foreslått prioritet: høy (gjelder
     kommunene)».
   - Ordlisten er en enkel første versjon. En grundigere vurdering per høring kommer med
     regionflagget i sprint 6.
