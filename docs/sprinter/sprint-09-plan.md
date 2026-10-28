# Sprint 9 – Faste regler for utelatte høringer: plan

Status: Plan til godkjenning · 28. oktober 2026

## Bakgrunn
Svein 28.10.2026 kl. 07.49: «Høring av alle Representantforslag skal legges i seksjonen
utelatte høringer». I dag står 16 representantforslag fra Stortinget blant de åpne høringene.
KI-en har utelatt 2 av dem, og 14 står i listen.

## Hva som skal bygges
1. **Faste regler** i `sources.yaml` (`felles.relevans.alltid_utelat`). Hver regel har:
   - ord titlen begynner med (store og små bokstaver spiller ingen rolle)
   - teksten som vises etter «Utelatt:».

   Første regel:
   ```yaml
   alltid_utelat:
     - tittel_starter_med: Representantforslag
       grunn: Representantforslag fra stortingsrepresentanter.
   ```
   Du kan selv legge til flere regler senere, f.eks. for grunnlovsforslag.
2. **Regelen går foran KI-en.** Høringer som treffer en regel, sendes ikke til KI-en for
   relevansvurdering. Det sparer kall. KI-sammendraget lages som før.
3. **Regelen går også foran vernet**, fordi du skrev «alle». Det gjelder selv om regionen er
   høringspart eller Gjøvik kommune har mottatt brevet. Representantforslag har i dag ingen slike
   merker.
4. **På nettsiden** vises de under «Utelatte høringer» med «Utelatt: Representantforslag fra
   stortingsrepresentanter.» Ellers er alt som før.

## Filer som berøres
| Fil | Endring |
|---|---|
| `sources.yaml` | `felles.relevans.alltid_utelat` med kommentar |
| `horinger/relevans.py` | Regelen i `vurder()`, og ingen API-kall for høringer som treffer en regel |
| `tests/test_relevans.py` | Regel treffer og treffer ikke, går foran vern og KI, og ingen API-kall |
| `README.md` | Avsnittet «Relevans for Gjøvikregionen» |

## Testing
- **Enhetstester** for regelen, nevnt over.
- **Hele sjekklisten A–J.**
- **Ekte bygging:** alle 16 representantforslag skal havne under «Utelatte høringer», og ingen
  andre høringer skal flytte seg. Dette gjøres med en lokal bygging og en publisering, uten nye
  KI-kall for andre høringer.

## Risikoer
- **For bred regel.** Bare titler som *begynner* med «Representantforslag», treffes. I dag gjør
  alle 16 det, og ingen andre titler inneholder ordet.
- **Viktige representantforslag skjules.** Eksempler er datasenterstrategi, solenergi og
  stemmerett ved kommunevalg. De er likevel ett klikk unna under «Utelatte høringer», og søket
  finner dem fortsatt.

## Spørsmål til Svein
1. **Vern:** skal regelen gjelde også når regionen er høringspart eller Gjøvik kommune har
   mottatt brevet? Forslag: ja, siden du skrev «alle».
2. **Grunnlovsforslag:** skal de behandles på samme måte? I dag står 6 åpne, og KI-en har
   utelatt 5. Forslag: nei, ikke nå. Regelen kan legges til i `sources.yaml` når som helst.
