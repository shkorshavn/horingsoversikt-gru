# Sprint 10 – Brukervennlighet på nettsiden: plan

Status: Godkjent · 28. oktober 2026 (Sveins svar nederst, «plan godkjent» kl. 09.13)

## Bakgrunn
Ønsker fra Svein 28.10.2026 kl. 09.07, med skjermbilde av verktøylinjen over listen.

## Hva som skal bygges
1. **Filtrene får mindre skrift uten fet.**
   - Valgene (tema, avsender, prioritet og avkrysningsboksene) får vanlig vekt og noe mindre
     skrift.
   - Gruppeoverskriftene («Tema», «Avsender» osv.) blir stående halvfete, slik at det fortsatt
     er lett å se hvor en gruppe begynner. Si fra hvis også de skal være uten fet.
2. **Deloverskrift:** ønsket ditt ble kuttet etter «Lag en deloverskrift "». Se spørsmål 1.
3. **Lenker til høringene åpnes i ny fane**, slik at siden med filtrene blir stående.
   - Det gjelder lenker i listen, under «Utelatte høringer», i postlista og til andre kilder
     («Også publisert hos»).
   - Lenkene får `rel="noopener"`.
   - Skjermlesere får vite at lenken åpnes i ny fane. Teksten «(åpnes i ny fane)» er skjult for
     andre.
4. **Utskriften:**
   - «KI: Hvorfor relevant» tas med, på egen linje under sammendraget. Se spørsmål 2.
   - Mer luft: fast innrykk (som en tabulator) for alt under tittelen, slik at fristen står i en
     egen kolonne. En tom linje mellom høringene, og en tynn strek.
   - Skriften blir litt større (fra 7,5 til ca. 8,5 pt). Utskriften blir dermed noe lengre, og
     det er greit med flere sider.
5. **Foreslått prioritet uten tall:** filteret viser «Høy», «Middels» og «Lav», ikke
   «Høy (1)». Merket på hver høring er allerede uten tall, og forklaringen på utskriften blir
   også uten.
6. **Verktøylinjen flyttes opp i toppen** (seksjonen i skjermbildet):
   - Disse delene flyttes:
     - «Viser 68 høringer …»
     - «Sorter etter»
     - «Skriv ut» og «Last ned som CSV»
     - fargeforklaringen for fristene.
   - På PC legges de til høyre i toppen, under tittelen. Da står de alltid synlig, og listen
     begynner rett under toppen.
   - På mobil legges de under ingressen i toppen og brytes over flere linjer.
   - Utskriften er som før: utvalget og forklaringen øverst, uten knappene.
7. **Søket tåler små skrivefeil og ulike skrivemåter:**
   - **Skrivemåte:** store og små bokstaver, punktum, bindestrek og mellomrom mellom bokstaver
     og tall regnes som like. «rv4», «Rv.4», «rv. 4», «rv 4» og «RV-4» gir de samme treffene. Det
     gjelder også «fv. 33», «E6» osv.
   - **Små skrivefeil:**
     - Ord på 4–7 bokstaver tillater én feil.
     - Ord på 8 bokstaver eller flere tillater to feil.

     En feil er én bokstav for mye, for lite, feil bokstav eller to bokstaver som har byttet
     plass. Ordet sammenlignes også med starten av lengre ord, slik at «barnehave» og
     «barnehahgre» finner «barnehageloven».
   - **Tall** må stemme nøyaktig, slik at «rv4» ikke finner «rv. 40».
   - **Korte ord** (1–3 bokstaver) må stemme nøyaktig, for å unngå mange tilfeldige treff.
   - Søket gjelder både listen og «Utelatte høringer», som i dag.

## Filer som berøres
| Fil | Endring |
|---|---|
| `index.html` | Verktøylinjen flyttes inn i toppen, prioritetsvalg uten tall, ev. deloverskrift |
| `side/app.js` | Lenker i ny fane, søk med normalisering og feiltoleranse, relevans på utskrift |
| `side/stil.css` | Filtrenes skrift, toppen med verktøylinjen (PC og mobil), utskriftsoppsett |
| `tests/test_nettside.py` | Nye og endrede tester |
| `README.md` | Søk, lenker og utskrift |

## Testing
- **Søk:** rv4, Rv.4, «rv. 4», «rv 4» og RV-4 gir samme treff. Barnehave, barnehahgre og
  barnehage finner barnehageloven. Rv4 finner ikke rv. 40. Ord på 3 bokstaver må stemme
  nøyaktig.
- **Lenker:** alle lenker til høringer har `target="_blank"` og `rel="noopener"`.
- **Toppen:**
  - Verktøylinjen står i toppen på 1280 px.
  - Den rulles ikke bort sammen med listen.
  - Ingen vannrett rulling på 375 px.
  - axe (WCAG) uten alvorlige funn.
- **Utskrift:**
  - «Hvorfor relevant» er med, og knappene er skjult.
  - PDF-eksempel med ekte data legges ved rapporten, slik at du kan se luften og innrykket.
- **Filtrene:** valgene har vanlig skriftvekt, og prioritet vises uten tall.
- **Sjekklisten A–J.**

## Risikoer
1. **Feiltoleranse gir falske treff**, for eksempel at «samer» finner «sammen». Tiltak: korte ord
   og tall må stemme nøyaktig, og antall tillatte feil avhenger av ordlengden. Testet med
   eksemplene over og med søk på vanlige ord mot de ekte dataene.
2. **Toppen blir høy på små skjermer.** Tiltak: på mobil står verktøylinjen kompakt og brytes
   over flere linjer. Toppen står ikke fast på mobil.
3. **Lengre utskrift** på grunn av luft og større skrift. Det er ønsket, og PDF-eksempelet viser
   resultatet.

## Spørsmål til Svein
1. **Deloverskrift:** meldingen stoppet etter «Lag en deloverskrift "». Hva skal overskriften
   hete, og hvor skal den stå? Et forslag, hvis du mente filtrene: dele dem i «Søk og tema» og
   «Avgrens utvalget».
2. **«Begrunnelse» i utskriften:** jeg tolker det som «KI: Hvorfor relevant». Skal også
   foreslått prioritet med begrunnelse (f.eks. «høy (regionen er høringspart)») med? Den står
   der allerede i dag.

## Sveins svar 28.10.2026 kl. 09.11
1. **Deloverskrift:** «Øvrige valg». Tolkes som en deloverskrift i filtrene over de tre
   avkrysningsboksene: «Bare høringer der regionen er høringspart», «Bare høringer mottatt av
   Gjøvik kommune» og «Vis høringer med utløpt frist».
2. **Begrunnelse i utskriften:** «KI: Hvorfor relevant», slik den står på nettsiden.
