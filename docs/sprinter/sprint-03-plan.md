# Sprint 3 – Automatisering og publisering: plan

Status: Plan til godkjenning · 17. oktober 2026

## Mål
Høringsoversikten oppdateres automatisk hver mandag kl. 10.00 norsk tid og publiseres på
GitHub Pages. Regjeringen.no hentes fra Sveins PC, de øvrige kildene fra GitHub. Siden får
merket «Ny», arkiv for utløpte høringer og en advarsel hvis dataene er gamle.

## Avklaringer som ligger til grunn
- Kjøring mandag kl. 10.00 norsk tid (Svein 17.10.2026), ikke kl. 06 som i spesifikasjonen.
- Regjeringen.no hentes fra Sveins Windows-PC (self-hosted runner), fordi regjeringen.no avviser
  GitHub (Svein 16.10.2026). PC-en står bare på når den er i bruk.
- Repoet er offentlig, så GitHub Pages er gratis.

## Hvordan det henger sammen

```
Mandag kl. 10.00
│
├─ Arbeidsflyt «Ukentlig oppdatering» (GitHubs servere)
│    henter Stortinget, Vegvesenet, fylkeskommunen og Statsforvalteren
│    + siste lagrede resultat fra regjeringen.no
│    → data/horinger.json, data/status.json, data/arkiv.json → commit → GitHub Pages
│
└─ Arbeidsflyt «Regjeringen.no» (Sveins PC)
     henter regjeringen.no → data/kilder/regjeringen.json → commit
     → starter «Ukentlig oppdatering» på nytt, slik at siden får med regjeringen.no
```

**Hvis PC-en er av mandag kl. 10:** Jobben for regjeringen.no venter hos GitHub i inntil et
døgn og kjøres så snart PC-en slås på. Resten av siden oppdateres uansett fra GitHub. I tillegg
legges det inn nye forsøk tirsdag–fredag kl. 10, som bare kjører hvis regjeringen.no ikke er
hentet de siste seks dagene. Statusoversikten viser når regjeringen.no sist ble hentet, og
markerer den som utdatert hvis det er mer enn åtte dager siden.

## Hva som bygges

| Fil | Innhold |
|---|---|
| `.github/workflows/oppdatering.yml` | Ukentlig kjøring på GitHub (se under), og publisering til GitHub Pages |
| `.github/workflows/regjeringen.yml` | Henting av regjeringen.no på Sveins PC |
| `horinger/kjor.py` | Kan kjøre et utvalg kilder og lagre én kildes resultat for seg (`data/kilder/<kilde>.json`), og slå sammen med lagrede resultater fra andre kilder |
| `horinger/historikk.py` | «Første gang sett»-dato per høring, flytting av utløpte til arkivet |
| `data/arkiv.json` | Utløpte høringer, med datoen de gikk ut |
| `side/app.js`, `index.html`, `side/stil.css` | Merket «Ny», utløpte høringer fra arkivet, advarsel ved gamle data, tidspunkt per kilde i statusoversikten |
| `docs/oppsett-pc.md` | Trinnvis veiledning for å koble PC-en til GitHub |
| `README.md` | Drift: hvordan kjøringen virker, hva du gjør hvis noe stopper |

### Tidspunkt i norsk tid
GitHub bruker UTC og kjenner ikke sommertid. Arbeidsflyten startes derfor både kl. 08.00 og
09.00 UTC, og første steg sjekker klokka i Europe/Oslo. Bare kjøringen som faller på
kl. 10 norsk tid går videre: 08.00 UTC om sommeren og 09.00 UTC om vinteren. Dette testes
for datoer på begge sider av sommertidsskiftet.

### Merket «Ny»
Hver høring får datoen den første gang ble sett. Den regnes som ny i sju dager. Dette tåler at
oppdateringen kjører flere ganger samme uke (f.eks. når regjeringen.no kommer inn senere).

### Utløpte høringer og arkivet
Høringer flyttes til `data/arkiv.json` når fristen er passert. Bryteren «Vis høringer med
utløpt frist» viser høringer som gikk ut de siste 30 dagene (se spørsmål 1). Arkivet beholder
alt, slik at ingenting forsvinner.

### Advarsel ved gamle data
Er dataene eldre enn ti dager, viser siden en tydelig melding øverst, slik at det synes hvis den
ukentlige kjøringen har stoppet.

### Simulert kildefeil
Den manuelle kjøringen får et valg «Simuler feil i kilde», som gjør én kilde utilgjengelig i den
kjøringen. Det brukes til akseptansetesten og ellers ikke.

## Sikring av PC-en
GitHub fraråder å koble en egen maskin til et offentlig repo uten sikring, fordi forslag til
endringer fra andre (pull requests) i prinsippet kan kjøre kode på maskinen. Tiltakene:

1. Arbeidsflyten for PC-en startes **bare av tidsplanen eller av deg manuelt**, aldri av
   forslag fra andre.
2. Innstillingen **«Require approval for all external contributors»** slås på, slik at ingen
   arbeidsflyt fra utenforstående kjører uten din godkjenning.
3. PC-en får en egen merkelapp (`gru-pc`), og bare jobben for regjeringen.no bruker den.
4. Programmet fra GitHub installeres som en Windows-tjeneste som kjører med begrensede
   rettigheter (ikke som administrator), i en egen mappe.
5. Jobben på PC-en har bare rett til å skrive til repoet, ingenting annet.
6. Handlinger fra andre (GitHub Actions) låses til en bestemt versjon.

## Det du må gjøre selv
Jeg har ikke tilgang til repoets innstillinger herfra, så disse stegene gjør du i GitHub
(veiledning trinn for trinn kommer når jeg er der, ca. 20 minutter totalt):

1. Slå på GitHub Pages med kilde «GitHub Actions».
2. Slå på «Require approval for all external contributors».
3. Installere GitHub-programmet (runner) på PC-en og koble det til repoet. Krever at du kan
   installere programmer på PC-en (se spørsmål 3).

## Tester og kvalitetssikring
- Nye tester: tidspunktsjekken (sommer og vinter), «første gang sett» og «Ny», flytting til
  arkivet, sammenslåing av lagrede kilderesultater, advarsel ved gamle data, og nettsiden med
  «Ny», arkiv og utdatert kilde.
- Manuell kjøring i GitHub som oppdaterer data og publiserer siden, og en manuell kjøring på
  PC-en for regjeringen.no.
- Simulert kildefeil i en manuell kjøring, vist på den publiserte siden.
- Hele sjekklisten A–J, inkludert stikkprøver av regjeringen.no nå som den kan hentes.

## Risikoer
1. **PC-oppsettet** krever administratorrettigheter for å installere tjenesten. Svein har det
   (avklart 17.10).
2. **GitHub forsinker noen ganger planlagte kjøringer** med opptil en time. Tidspunktsjekken
   tåler dette ved å godta kjøringer mellom kl. 10.00 og 11.59.
3. **GitHub slår av planlagte kjøringer** i offentlige repoer etter 60 dager uten aktivitet. Den
   ukentlige commiten av data regnes som aktivitet, men jeg følger med på det i rapporten.
4. **Regjeringen.no fra PC-en er ikke testet** med programmet ennå, bare i nettleseren. Det
   testes i sprinten.

## Utenfor omfang
Postlista (sprint 7), som spesifikasjonen plasserer i samme kjøring, legges inn der.
Egendefinert adresse (f.eks. horinger.gjovikregionen.no) er ikke med.

## Avklart med Svein 17.10.2026
1. Bryteren for utløpte høringer viser de som gikk ut de siste 30 dagene.
2. Adressen https://shkorshavn.github.io/horingsoversikt-gru/ brukes inntil videre.
3. PC-en er GRUs egen og administreres av Svein. Han kan installere programmer selv.
4. Nye forsøk på regjeringen.no tirsdag–fredag kl. 10 de ukene PC-en ikke var på mandag.

Planen venter bare på godkjenning.
