# Sprint 12 – Mjøsa og vann alltid med, flere departementer og nye kilder: plan

Status: Plan til godkjenning · 3. november 2026

## Bakgrunn
Svein 03.11.2026 kl. 20.40: høringer som gjelder Mjøsa, vannkvalitet, overvåking av innsjøer,
fartsgrenser eller regler for båttrafikk på innsjøer og elver, avrenning eller utslipp til
innsjøer, eller ammunisjon i Mjøsa, skal være med, også når de kommer fra statlige
virksomheter som ellers ikke anses som aktuelle. Svarene på spørsmål 1–5 står nederst.

## Hva som skal bygges
1. **Regelen «alltid med»** (`felles.relevans.alltid_med` i `sources.yaml`).
   - **Faste ord og uttrykk** i tittel, ingress eller detaljtekst gir treff. Eksempler:
     - Mjøsa og innsjø
     - vannforskriften, vannforvaltning og vannkvalitet
     - avrenning og utslipp til vann
     - fartsforskrift og fritidsbåt
     - drikkevann, vannverk og flom
     - vassdragsregulering
     - ammunisjon sammen med Mjøsa eller innsjø.

     Ordene velges slik at de ikke gir mange falske treff. «Utslipp» alene tas for eksempel
     ikke med.
   - **KI-instruksen** får temaene som alltid relevante, slik at KI-en også fanger høringer som
     ikke bruker ordene over.
   - **Høringer som treffer regelen:**
     - står alltid i listen
     - går foran KI-ens «ikke relevant», regelen om representantforslag (svar 1) og
       temafilteret hos Miljødirektoratet
     - får høy prioritet med begrunnelsen «gjelder Mjøsa og vann» (svar 5).
2. **Barne- og familiedepartementet og Energidepartementet tas inn igjen** på regjeringen.no
   (svar 3). Utenriksdepartementet holdes fortsatt utenfor. KI-en legger høringer som ikke er
   relevante under «Utelatte høringer». De nye høringene får KI-sammendrag og relevansvurdering
   ved neste ukentlige oppdatering.
3. **Nye kilder: Sjøfartsdirektoratet, Kystverket og Forsvarsbygg** (svar 2).
   - Hver kilde undersøkes: høringsside, robots.txt, struktur og frist.
   - Kilder som kan hentes, bygges med filter, slik at bare høringer som treffer «alltid med»
     (innlandsvann og Mjøsa) tas med. Andre høringer fra disse kildene tas ikke med.
   - Kilder uten høringsside eller med sperre i robots.txt settes som inaktive i
     `sources.yaml`, med begrunnelse.
4. **Prioriteringslisten** (`prioritet_loft`) får de samme ordene, slik at prioriteten blir
   riktig også før KI-en har vurdert høringen.

## Filer som berøres
| Fil | Endring |
|---|---|
| `sources.yaml` | `alltid_med` (ord og temaer), `ekskluder_departementer` (bare UD), nye kilder |
| `horinger/relevans.py` | Regelen og rekkefølgen: alltid med → alltid utelat → vern → KI. KI-instruksen med temaene |
| `horinger/prioritet.py`, `horinger/bygg.py` | Høy prioritet og begrunnelse for «alltid med» |
| `horinger/kilder/` | Moduler for de nye kildene som kan hentes, med filter |
| `tests/` | Regelen (ord, falske treff, rekkefølge), departementene, nye kilder med testdata |
| `README.md` | Avsnittet «Relevans for Gjøvikregionen» og listen over kilder |

## Testing
- **Regelen:**
  - Treff på ordene.
  - Ingen treff på vanlige høringer, for eksempel om klimakvoter eller CO2-utslipp.
  - Regelen går foran representantforslag, KI-ens «ikke relevant» og temafilteret.
  - Prioriteten blir «høy».
- **Kjøring mot ekte data:** antall høringer fra Barne- og familiedepartementet og
  Energidepartementet, og hvor mange av dem KI-en legger i listen og under «Utelatte
  høringer».
- **Nye kilder:**
  - Stikkprøver mot kildens egen side.
  - Bekreftelse på at høringer uten Mjøsa- eller vanntema ikke tas med.
  - Er det ingen aktuelle høringer nå, testes filteret med lagrede sider.
- **Sjekklisten A–J.**

## Risikoer
1. **Falske treff fra ordlisten**, for eksempel «flom» i en høring om noe annet. Tiltak: ordene
   prøves mot alle høringene i dag og i arkivet, og treffene listes i rapporten.
2. **Flere høringer i listen** fra de to departementene. Tiltak: KI-en sorterer, og det som
   ikke er relevant, ligger under «Utelatte høringer».
3. **De nye kildene har kanskje ingen høringsside som kan hentes.** Tiltak: de settes som
   inaktive med begrunnelse. Høringene deres publiseres ofte også på regjeringen.no, og fanges
   der av «alltid med».
4. **Kostnad:** noen ekstra KI-kall for nye høringer, trolig under 1 dollar.

## Sveins svar 03.11.2026 kl. 20.45
1. **«Alltid med» går foran regelen om representantforslag:** ja.
2. **Sjøfartsdirektoratet, Kystverket og Forsvarsbygg:** ja, med filter.
3. **Barne- og familiedepartementet og Energidepartementet tas inn igjen:** ja. UD holdes
   utenfor.
4. **Flere ord:** ja, som foreslått: drikkevann, vannverk, flom og vassdragsregulering.
5. **Høy prioritet for «alltid med»:** ja.
