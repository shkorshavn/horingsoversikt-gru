# Sprintstatus – Høringsoversikt Gjøvikregionen

**Kolonnen «Godkjent av Svein» viser Sveins godkjenning.** Svein fyller den ut selv, eller godkjenner i chatten med en uttrykkelig melding («Sprint N: JA <dato>»), som Claude da fører inn her med henvisning til meldingen. Claude godkjenner aldri selv, og starter ikke en ny sprint før forrige sprint har `JA` og dato her.

Gyldige statuser: Ikke startet · Plan til godkjenning · Pågår · Til godkjenning · Godkjent

| Sprint | Navn | Status | Godkjent av Svein | Dato | Kommentar |
|---|---|---|---|---|---|
| 0 | Kartlegging av kilder | Godkjent | JA | 16.10.2026 | Rapport v4: docs/sprinter/sprint-00-rapport-v4.md. Godkjent i chat 16.10.2026 kl. 15.13 |
| 1 | Grunnmur og fem kjernekilder | Godkjent | JA | 16.10.2026 | Rapport: docs/sprinter/sprint-01-rapport.md. Godkjent i chat 16.10.2026 kl. 17.20 |
| 2 | Nettsiden | Godkjent | JA | 17.10.2026 | Rapport: docs/sprinter/sprint-02-rapport.md. Godkjent i chat 17.10.2026 kl. 17.23 («dd» tolket som dags dato) |
| 3 | Automatisering og publisering | Godkjent | JA | 25.10.2026 | Godkjent i chat 25.10.2026 kl. 16.08 («dd» tolket som dags dato). Rapport v3: docs/sprinter/sprint-03-rapport-v3.md (endringer bestilt 25.10.2026 kl. 10.16 og 15.42). Plan: docs/sprinter/sprint-03-plan.md (plan godkjent av Svein i chat 17.10.2026 kl. 17.28). Beslutning 16.10.2026: ukentlig kjøring på maskin hos GRU (self-hosted runner), fordi regjeringen.no avviser GitHub Actions. 17.10.2026: Sveins Windows-PC (står bare på når den er i bruk), kjøring mandag kl. 10.00 |
| 4 | Direktorater, prioritet 1 | Plan til godkjenning | | | Plan: docs/sprinter/sprint-04-plan.md |
| 5 | Direktorater, prioritet 2 og 3 | Ikke startet | | | |
| 6 | Høringsparter og regionflagg | Ikke startet | | | |
| 7 | Gjøvik kommunes postliste | Ikke startet | | | |
| 8 | KI-sammendrag og ferdigstilling | Ikke startet | | | |

## Slik godkjenner du en sprint

1. Les rapporten i `docs/sprinter/sprint-NN-rapport.md`.
2. Gjør kontrollene under «Hva Svein bør sjekke selv».
3. Godkjenn på en av to måter:
   - **I chatten:** skriv f.eks. «Sprint 1: JA 23.10.2026». Claude fører det inn her og committer.
   - **I GitHub:** skriv `JA` og dato i sprintens rad, sett status til «Godkjent» og commit.
4. Ønsker du endringer i stedet, si det i chatten eller skriv dem i kommentarkolonnen, og be Claude rette dem.
5. Skriv «Start sprint N» til Claude når du vil gå videre.
