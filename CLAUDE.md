# Arbeidsregler for Claude Code – Høringsoversikt Gjøvikregionen

Denne filen leses automatisk ved start av hver økt. Reglene her går foran alt annet i prosjektet.

- Full spesifikasjon: `SPESIFIKASJON.md`
- Sprintstatus og godkjenninger: `SPRINTSTATUS.md`
- Sprintrapporter: `docs/sprinter/`
- Oppdragsgiver: Svein, daglig leder i Gjøvikregionen Utvikling (GRU)

All kommunikasjon, dokumentasjon og alt brukergrensesnitt skal være på norsk bokmål.

---

## 1. Sprintporten – absolutte regler

1. **Én sprint om gangen.** Du arbeider bare på sprinten som har status «Pågår» eller «Plan til godkjenning» i `SPRINTSTATUS.md`.

2. **Sjekk porten før du starter.** Før du gjør noe arbeid på en sprint, skal du lese `SPRINTSTATUS.md`. Hvis forrige sprint ikke har `JA` i kolonnen «Godkjent av Svein» med dato, skal du ikke starte. Svar i stedet: «Sprint N er ikke godkjent ennå. Jeg venter på godkjenning før jeg går videre.» og stopp.

3. **Du godkjenner aldri selv.** En sprint er godkjent bare når Svein har godkjent den på en av disse to måtene:
   - **I filen:** Svein skriver `JA` og dato i kolonnen «Godkjent av Svein» selv.
   - **I chatten:** Svein skriver en uttrykkelig godkjenning som nevner sprintnummeret og «JA», f.eks. «Sprint 1: JA 23.10.2026». Da fører du inn godkjenningen i `SPRINTSTATUS.md`: `JA` i kolonnen «Godkjent av Svein», datoen han oppga (eller dagens dato), status «Godkjent», og i kommentarkolonnen «Godkjent i chat» med tidspunktet for meldingen. Du committer straks, og siterer meldingen hans ordrett i commit-meldingen.

   Godkjenning i chatten gjelder bare når den kommer **etter** at rapporten for sprinten er levert. Generelle svar som «ser bra ut», «kjør på» eller «planen er godkjent» er ikke en godkjenning av sprinten. Er du i tvil om en melding er en godkjenning, spør. Du skal aldri føre inn en godkjenning ut fra antakelser, og aldri endre eller slette en godkjenning som allerede står i filen.

4. **Plan før kode.** Hver sprint starter med at du legger fram en plan: hva som skal bygges, hvilke filer som berøres, hvordan det skal testes og hvilke risikoer du ser. Sett status til «Plan til godkjenning» og vent på Sveins OK før du skriver kode.

5. **Hold deg innenfor sprinten.** Ikke bygg noe som hører til en senere sprint, selv om det virker raskt eller naturlig. Skriv heller forslaget under «Forslag til senere sprinter» i rapporten.

6. **Avslutt med full kvalitetssikring.** Når arbeidet er ferdig, kjører du hele sjekklisten i avsnitt 2, skriver rapport etter malen i avsnitt 3, setter status til «Til godkjenning», committer og **stopper**.

7. **Feil stopper ikke rapporten.** Finner du feil under kvalitetssikringen, retter du dem innenfor sprinten og kjører hele sjekklisten på nytt. Kan en feil ikke rettes, skal den stå tydelig i rapporten. Du skal aldri presentere en sprint som bestått når et punkt har feilet.

8. **Endringer etter rapport.** Ber Svein om endringer etter at rapporten er levert, gjør du dem, kjører hele sjekklisten på nytt og leverer en ny versjon av rapporten (`sprint-NN-rapport-v2.md` osv.).

9. **Når du er i tvil, spør.** Er noe i spesifikasjonen uklart eller i konflikt med det du finner i kildene, stopp og spør i stedet for å gjette.

---

## 2. Kvalitetssikring – sjekkliste for hver sprint

Alle punkter skal gjennomføres og dokumenteres med bevis (kommandoutskrift, tabell eller filreferanse). «Ikke relevant» er lov, men krever en begrunnelse på én setning.

**A. Automatiske tester**
Kjør hele testsuiten med `pytest -v`. Lim inn sammendraget (antall bestått, feilet, hoppet over) i rapporten. Ingen tester skal være hoppet over uten begrunnelse. Nye funksjoner i sprinten skal ha egne tester.

**B. Kodekvalitet**
Kjør `ruff check .` og `ruff format --check .`. Resultatet skal være uten feil eller advarsler. Offentlige funksjoner skal ha type hints og en kort docstring på norsk.

**C. Kjøring mot ekte data**
Kjør innhentingen mot de faktiske kildene for sprintens omfang. Rapporter antall høringer hentet per kilde, og forklar tall som ser unaturlige ut (0, eller mange flere enn forventet).

**D. Stikkprøver mot kildene**
For hver ny eller endret kilde: sammenlign minst 5 høringer (eller alle, hvis færre) felt for felt mot kildens egen nettside. Kontroller tittel, høringsinstans, høringsfrist, lenke og høringsparter. Før resultatet i en tabell med lenke til kildesiden. Ethvert avvik regnes som en feil som skal rettes.

**E. Tegn, datoer og tid**
Kontroller at æ, ø og å er korrekte i alle felt, i JSON-filene og på nettsiden. Datoer lagres i ISO 8601 og vises i norsk format (f.eks. 15. oktober 2026). Frister og «dager igjen» regnes i norsk tid (Europe/Oslo).

**F. Feilhåndtering**
Simuler at minst én kilde feiler (feil URL eller tidsavbrudd) og vis at resten av kjøringen fullføres, at feilen logges og at den vises i statusoversikten.

**G. Gjennomgang av egen kode**
Les hele diffen for sprinten på nytt (`git diff` mot forrige godkjente sprint) som om du var en kritisk kollega. Se etter hardkodede verdier som burde ligge i konfigurasjon, duplisert kode, død kode, manglende feilhåndtering, sårbar parsing og hemmeligheter i koden. Skriv hva du fant og hva du rettet.

**H. Høflighet mot kildene**
Bekreft at alle forespørsler bruker en tydelig User-Agent, har pauser mellom kall og respekterer robots.txt.

**I. Dokumentasjon**
README og kommentarer i `sources.yaml` skal være oppdatert med det som ble bygget i sprinten.

**J. Akseptansekriterier**
Gå gjennom hvert akseptansekriterium for sprinten i `SPESIFIKASJON.md`, avsnitt 8, og marker det som oppfylt eller ikke oppfylt, med bevis.

**Ærlighetskrav:** Det som ikke er testet, skal stå som ikke testet. Skriv aldri at tester er grønne eller at noe virker uten å vise utskriften som dokumenterer det.

---

## 3. Mal for sprintrapport

Lagres som `docs/sprinter/sprint-NN-rapport.md`.

```markdown
# Sprint NN – [navn]

## Sammendrag
Tre–fem setninger om hva som er levert, og om sprinten anbefales godkjent.

## Hva som er bygget
Kort beskrivelse og liste over nye eller endrede filer.

## Kvalitetssikring
| Punkt | Resultat | Bevis / kommentar |
|---|---|---|
| A. Tester | Bestått / Feilet | x bestått, y feilet |
| B. Kodekvalitet | | |
| C. Ekte data | | |
| D. Stikkprøver | | se tabell under |
| E. Tegn og datoer | | |
| F. Feilhåndtering | | |
| G. Kodegjennomgang | | |
| H. Høflighet | | |
| I. Dokumentasjon | | |
| J. Akseptansekriterier | | se tabell under |

## Stikkprøver
| Kilde | Høring | Felt kontrollert | Avvik | Lenke |
|---|---|---|---|---|

## Akseptansekriterier
| Kriterium | Oppfylt | Bevis |
|---|---|---|

## Kjente feil og begrensninger

## Forslag til senere sprinter

## Hva Svein bør sjekke selv
Konkrete ting å se på før godkjenning, med lenker eller kommandoer.
```
