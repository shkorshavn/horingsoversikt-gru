# Sprint 8 – KI-sammendrag og ferdigstilling: plan

Status: Plan til godkjenning · 27. oktober 2026

## Mål
Hver høring får et kort sammendrag i klarspråk (1–2 setninger) om hva den gjelder. Sammendraget
lages med Anthropic API og lagres, så hver høring bare oppsummeres én gang. Uten API-nøkkel
vises ingressen som i dag. Nettsiden deles i to deler som ruller hver for seg: filtrene til
venstre og listen til høyre (ditt ønske 27.10.2026). Til slutt kontrolleres hele løsningen
samlet, og README testes ved at oppsettet følges fra bunnen.

## Akseptansekriterier (SPESIFIKASJON.md, avsnitt 8)
1. Sammendrag lages med Anthropic API og caches per høring.
2. Uten API-nøkkel brukes ingressen, uten at kjøringen feiler.
3. Ti sammendrag er vurdert i rapporten mot originalteksten for korrekthet og klarspråk.
4. README er komplett og testet ved at oppsettet er fulgt fra bunnen.
5. Hele sjekklisten i `CLAUDE.md` er kjørt for hele løsningen samlet, ikke bare siste sprint.

Tillegg fra deg: venstre og høyre side ruller hver for seg.

## 1. Delt visning (ditt ønske)
- **På PC** (bredere enn 52 rem, ca. 830 px):
  - Filtrene står i en egen kolonne med full skjermhøyde og ruller for seg selv.
  - Listen til høyre ruller uavhengig av filtrene. Toppen med logo og tittel blir stående.
- **På mobil og nettbrett på høykant:** som i dag. Filtrene kan foldes sammen over listen, og
  hele siden ruller som én.
- **Utskrift:** som i dag, uten filtrene.
- **Tilgjengelighet:** tastaturnavigasjon og «Hopp til listen» virker fortsatt. Hvert område
  får en synlig fokusramme, og axe-testene kjøres som før.
- **Tester:** at filterkolonnen kan rulles uten at listen flytter seg, og omvendt, på 1280 × 800.
  At mobilvisningen er uendret.

## 2. KI-sammendrag (`horinger/sammendrag.py`, ny)
- **Grunnlag for sammendraget:**
  - Avsender, tittel og ingress.
  - Teksten fra detaljsiden (høringsbrevet), når vi allerede leser den for høringsparter. Den
    lagres bare i bufferen, ikke på nettsiden, og kuttes etter ca. 6 000 tegn (se spørsmål 2).
- **Instruks til modellen:**
  - Norsk bokmål og klarspråk, 1–2 setninger, høyst ca. 45 ord.
  - Si hva som foreslås, og hvem det gjelder.
  - Bare bruk opplysninger som står i teksten. Gi ingen vurdering og ingen frist, siden den
    vises for seg.
  - Gir teksten for lite å bygge på, svarer modellen «MANGLER». Da brukes ingressen.
- **Buffer:** `data/sammendrag.json`, nøkkel = høringens id, og en sjekksum av grunnlaget.
  - Bare nye høringer, eller høringer der teksten er endret, sendes til API-et.
  - Sammendrag for høringer som er borte fra både oversikten og arkivet, slettes.
- **Modell:** står i `sources.yaml` (`felles.sammendrag.modell`), se spørsmål 1.
  - Ett kall per høring, med lav `max_tokens`.
  - Pause mellom kall. Tidsavbrudd og feil per høring gir ingressen for den høringen, og
    kjøringen fortsetter.
- **Uten API-nøkkel:** steget hoppes over med en melding i loggen. Ingressen vises, og ingen
  feil oppstår.
- **Hvor det kjøres:** i arbeidsflyten «Publiser», før byggingen. Nøkkelen hentes fra GitHub
  Secret `ANTHROPIC_API_KEY` og står aldri i koden eller i loggen.
- **Kostnad:** ca. 150 åpne høringer første gang, med ca. 2 000 tokens inn og 100 tokens ut
  hver. Med Sonnet 5.5 ($2 inn / $10 ut per million tokens) blir det under 1 dollar første gang,
  og noen få kroner i uka etter det.
- **Nettsiden:**
  - Sammendraget erstatter ingressen i listen og er merket «KI-sammendrag» (se spørsmål 3).
  - CSV får både sammendrag og ingress.
  - Søket leter i begge.
- **Kriterium 3:** ti sammendrag, valgt på tvers av kildene, vurderes mot originalteksten for
  korrekthet (ingen feil eller påfunn) og klarspråk. Vurderingen står i en tabell i rapporten.

## 3. Ferdigstilling
- **README** gjennomgås og fullføres:
  - Oppsett, nye kilder og søkeord, API-nøkkel, PC-runneren, postlista og feilsøking.
  - Kriterium 4: oppsettet følges ordrett fra bunnen i en ny, tom mappe (klone, installere,
    teste, kjøre bygg). Avvik rettes i README.
- **Hele sjekklisten A–J for hele løsningen:**
  - Alle tester.
  - Ekte kjøring av alle 27 kilder og postlista.
  - Stikkprøver: to høringer per kilde med åpne høringer, og kontroll av kildene med 0 åpne.
  - Gjennomgang av all kode og robots.txt for alle domener.
  - Alle akseptansekriterier fra sprint 0–8 på nytt.
- **Opprydding:** død kode og utdaterte kommentarer fjernes. `SPESIFIKASJON.md` røres ikke.

## Filer som berøres

| Fil | Endring |
|---|---|
| `horinger/sammendrag.py` (ny) | Kall til API-et, buffer og reserve med ingressen |
| `horinger/kilder/base.py` | Lagrer grunnlagsteksten fra detaljsiden til bufferen |
| `horinger/bygg.py` | Legger sammendraget inn i høringene |
| `sources.yaml` | `felles.sammendrag` (modell, maks lengde, pause) |
| `.github/workflows/publiser.yml` | Sammendragssteget med `ANTHROPIC_API_KEY` |
| `requirements-kjoring.txt` | `anthropic` (offisiell Python-klient) |
| `index.html`, `side/stil.css`, `side/app.js` | Delt visning, sammendrag med merke |
| `tests/` | Sammendrag med falsk API, uten nøkkel, feil og buffer. Delt visning |
| `README.md` | Komplett, og testet fra bunnen |

## Risikoer
1. **Feil i sammendrag** (påfunn eller feil tall). Tiltak: streng instruks om bare å bruke
   teksten, kort lengde, «MANGLER» som reserve, merket «KI-sammendrag» og vurdering av ti
   sammendrag (kriterium 3).
2. **Kostnad.** Tiltak: buffer per høring, korte svar og en lav brukgrense i Anthropic-kontoen.
3. **API-feil eller utløpt nøkkel.** Tiltak: ingressen brukes, og kjøringen fortsetter.
   Statusen viser at sammendrag mangler.
4. **Delt visning på små skjermer.** Tiltak: gjelder bare på bred skjerm. Mobil og utskrift er
   som før og testes.

## Spørsmål til Svein
1. **Modell:** Spesifikasjonen sier `claude-sonnet-4-6`. Den er nå en eldre modell («legacy»),
   og skal ikke fases ut før tidligst 17.02.2027. Gjeldende Sonnet er `claude-sonnet-5-5`, som er
   nyere og billigere ($2/$10 mot $3/$15 per million tokens). Forslag: bruke
   `claude-sonnet-5-5`. Modellen står i `sources.yaml` og kan byttes uten kodeendring.
2. **Grunnlag:** Skal sammendraget bygge på høringsbrevet fra detaljsiden når vi har det, i
   tillegg til tittel og ingress? Det gir bedre sammendrag, men teksten sendes til Anthropic.
   Teksten er offentlig. Forslag: ja.
3. **Merking:** Skal sammendraget merkes «KI-sammendrag», med ingressen tilgjengelig ved klikk?
   Forslag: ja.
4. **API-nøkkel:** Du lager nøkkelen selv i Anthropic Console og legger den inn som GitHub Secret
   `ANTHROPIC_API_KEY`. Jeg skriver en trinnvis veiledning i README. Forslag: sett også en lav
   månedlig brukgrense, f.eks. 10 dollar. Er det greit?

## Sveins svar 27.10.2026 kl. 00.13
1. **Modell:** OK, `claude-sonnet-5-5`.
2. **Grunnlag:** Ja, høringsbrevet fra detaljsiden brukes når vi har det.
3. **Merking:** Ja, «KI-sammendrag», med ingressen tilgjengelig ved klikk.
4. **API-nøkkel og brukgrense:** OK. Tillegg: «oppdatering trenger kun gå en gang pr uke».
   Sammendragene lages derfor bare i den ukentlige oppdateringen. Det er publiseringen som
   startes av «Ukentlig oppdatering» og «Regjeringen.no (GRUs PC)». Når publiseringen startes av
   en kodeendring (push), lages ingen nye sammendrag. Da brukes de som er lagret.
