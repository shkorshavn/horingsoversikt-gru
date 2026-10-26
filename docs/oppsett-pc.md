# Oppsett av GitHub og GRUs PC

Denne veiledningen gjør du én gang. Den tar omtrent 20 minutter. Del A gjøres i GitHub i
nettleseren, del B på PC-en som skal hente regjeringen.no.

Hvorfor PC-en trengs: Regjeringen.no stopper forespørsler fra GitHubs servere med en
robotsjekk (Cloudflare). Fra en vanlig PC i GRUs nett slipper programmet gjennom. Alle de andre
kildene hentes fra GitHub og er ikke avhengige av PC-en.

## Del A – Innstillinger i GitHub

Gå til https://github.com/shkorshavn/horingsoversikt-gru og velg **Settings**.

### A1. Slå på GitHub Pages
1. Velg **Pages** i menyen til venstre.
2. Under **Build and deployment**, velg **Source: GitHub Actions**.

Nettsiden får adressen https://shkorshavn.github.io/horingsoversikt-gru/ etter første
publisering.

### A2. Krev godkjenning for arbeidsflyter fra utenforstående
1. Velg **Actions → General**.
2. Under **Approval for running fork pull request workflows from contributors**, velg
   **Require approval for all external contributors**.
3. Trykk **Save**.

Ingen av arbeidsflytene i repoet reagerer på forslag fra andre (pull requests), men denne
innstillingen er en ekstra sperre.

## Del B – PC-en

Du trenger administratorrettigheter på PC-en til installasjonen. Selve jobbene kjører
etterpå uten administratorrettigheter.

### B1. Installer Git og Python
Åpne **Terminal** eller **PowerShell som administrator** (høyreklikk på Start → Terminal
(administrator)) og kjør:

```powershell
winget install --id Git.Git -e --scope machine
winget install --id Python.Python.3.12 -e --scope machine --override "/quiet InstallAllUsers=1 PrependPath=1"
```

Lukk vinduet, åpne et nytt og kontroller:

```powershell
git --version
python --version
```

Begge skal svare med et versjonsnummer. Python må være installert for alle brukere, fordi
GitHub-programmet kjører som en egen tjenestebruker.

### B2. Last ned GitHub-programmet (runner)
1. I GitHub: **Settings → Actions → Runners → New self-hosted runner**.
2. Velg **Windows** og **x64**.
3. Kjør kommandoene under **Download** i PowerShell som administrator. De lager mappen
   `C:\actions-runner` og pakker ut programmet der.

### B3. Koble programmet til repoet
Kjør kommandoen under **Configure** (den begynner med `./config.cmd --url ...` og inneholder
en kode som bare gjelder i én time – ikke del den med noen). Svar slik på spørsmålene:

| Spørsmål | Svar |
|---|---|
| Enter the name of the runner group | Trykk Enter (standard) |
| Enter the name of runner | `gru-pc` |
| Enter any additional labels | `gru-pc` |
| Enter name of work folder | Trykk Enter (`_work`) |
| Would you like to run the runner as service? | `Y` |
| User account to use for the service | Trykk Enter (`NT AUTHORITY\NETWORK SERVICE`) |

`NETWORK SERVICE` er en innebygd Windows-konto med begrensede rettigheter. Programmet får
dermed ikke tilgang til dine filer eller administratorrettigheter.

### B4. Kontroller
I GitHub: **Settings → Actions → Runners**. `gru-pc` skal stå med status **Idle** (grønn).
Når PC-en er av, står den som **Offline**. Det er som forventet.

### B5. Prøvekjøring
1. Gå til **Actions → Regjeringen.no (GRUs PC) → Run workflow → Run workflow**.
2. Jobben skal bli grønn i løpet av et par minutter.
3. Etterpå starter **Publiser** automatisk og oppdaterer nettsiden.

Si fra til Claude når dette er gjort. Da kontrollerer jeg resultatet.

## Hvordan det virker i det daglige

- Mandag kl. 10.00 henter GitHub de andre kildene, og PC-en henter regjeringen.no.
- Er PC-en av kl. 10, venter jobben i kø hos GitHub i inntil 24 timer og kjøres så snart PC-en
  og programmet er på igjen.
- Er regjeringen.no ikke hentet mandag, prøver PC-en igjen tirsdag–fredag kl. 10. Den hopper
  over forsøket hvis regjeringen.no er hentet de siste seks dagene.
- Står PC-en av hele uken, viser nettsiden høringene fra forrige vellykkede henting, og
  statustabellen viser når regjeringen.no sist ble hentet.

PC-en trenger ikke stå på hele tiden, og du trenger ikke være logget inn: programmet starter
som en Windows-tjeneste når PC-en slås på.

## Sikkerhet

- Jobben på PC-en startes bare av tidsplanen eller av noen med skrivetilgang til repoet
  (i dag bare deg). Ingen arbeidsflyt i repoet kjører på PC-en for forslag fra andre.
- Programmet kjører som `NETWORK SERVICE` og arbeider bare i `C:\actions-runner`.
- Jobben har lov til å skrive til repoet og starte publiseringen. Den har ingen andre
  rettigheter i GitHub og ingen hemmeligheter utover den kortvarige nøkkelen GitHub gir hver
  jobb.
- Handlinger fra andre (GitHub Actions) er låst til bestemte versjoner.

## Fjerne PC-en igjen

Åpne PowerShell som administrator og kjør:

```powershell
cd C:\actions-runner
.\config.cmd remove
```

Følg instruksjonen (GitHub viser en kode under **Settings → Actions → Runners → gru-pc →
Remove**). Slett deretter mappen `C:\actions-runner`.

## Feilsøking

| Problem | Løsning |
|---|---|
| `gru-pc` står som Offline selv om PC-en er på | Start tjenesten: Start → Tjenester → «GitHub Actions Runner (…)» → Start |
| Jobben feiler med «python is not recognized» | Python er ikke installert for alle brukere. Gjenta B1 og start PC-en på nytt |
| Jobben feiler i steget «Hent regjeringen.no» med feilkode 403 | Robotsjekken slipper heller ikke PC-en gjennom. Si fra til Claude |
| «Cannot start the service» eller `sc start` gir feil 1068 | Norsk Windows lagrer kontoen som «NT-MYNDIGHET\NETTVERKSTJENESTE», som ikke virker. I ledetekst som administrator: `sc config actions.runner.shkorshavn-horingsoversikt-gru.X9SHK obj= "NT AUTHORITY\NetworkService" password= ""` og deretter `sc start …` (løst slik 26.10.2026) |
| Runneren står som Idle, men jobbene blir stående i kø | Merkelappen `gru-pc` mangler. Legg den til under Settings → Actions → Runners → runneren → Labels |
| To `run.cmd`-vinduer gir «A session for this runner already exists» | Bare én kopi av runneren kan være koblet til. Lukk det ene vinduet, eller bruk tjenesten |
| Brannmur eller proxy i GRUs nett stopper programmet | Programmet må nå `github.com`, `*.actions.githubusercontent.com` og `www.regjeringen.no` på port 443 |
