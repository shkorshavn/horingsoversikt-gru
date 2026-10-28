# Sprint 11 – Verktøylinjen over filtrene: plan

Status: Godkjent · 28. oktober 2026 («plan godkjent» kl. 10.21)

## Bakgrunn
Svein 28.10.2026 kl. 10.17, med skjermbilde: «jeg ønsker at seksjonen med antall høringer,
sortering, utskrift og forklaring til fargene flyttes til venstre del av nettsiden – over
filtre».

## Hva som skal bygges
1. **Verktøylinjen flyttes fra båndet i toppen til venstre kolonne, over «Filtre».** Den
   omfatter:
   - antall høringer
   - sortering
   - «Skriv ut» og «Last ned som CSV»
   - fargeforklaringen.

   Båndet i toppen fjernes, slik at toppen blir lavere og listen får mer plass.
2. **Oppsett i den smale kolonnen (16 rem, ca. 256 px):**
   - Antallet står øverst.
   - «Sorter etter» står med nedtrekkslisten i full bredde under.
   - «Skriv ut» og «Last ned som CSV» står ved siden av hverandre.
   - Fargeforklaringen står med én farge per linje.
   - En tynn strek skiller verktøylinjen fra filtrene.
3. **Står fast på PC:** verktøylinjen ligger øverst i venstre kolonne og blir stående når
   filtrene rulles. Bare filtrene under ruller.
4. **Mobil:** verktøylinjen står over den sammenfoldbare «Filtre»-boksen, som i dag.
5. **Utskrift:** uendret. Utvalget, antallet og fargeforklaringen står øverst, uten knappene.

## Filer som berøres
| Fil | Endring |
|---|---|
| `index.html` | Verktøylinjen flyttes inn i venstre kolonne |
| `side/stil.css` | Kolonneoppsett, fast verktøylinje over filtrene som ruller, mobil og utskrift |
| `tests/test_nettside.py` | Testen for plassering endres (venstre kolonne, over filtrene, står i ro) |
| `README.md` | Avsnittet «Nettsiden» |

## Testing
- **Plassering:** verktøylinjen står i venstre kolonne over «Filtre» på 1280 px.
- **Rulling:** den står i ro når både filtrene og listen rulles.
- **Mobil:** ingen vannrett rulling på 375 px, og verktøylinjen står over filtrene.
- **Tilgjengelighet:** axe (WCAG) uten alvorlige funn. Tastaturrekkefølgen er verktøylinje,
  filtre og så listen.
- **Utskrift:** uendret, testet som før.
- **Sjekklisten A–J**, med skjermbilde med ekte data.

## Risikoer
- **Mindre plass til filtrene på lave skjermer.** Verktøylinjen tar ca. 230 px i høyden. På
  en laptop med lav skjerm (ca. 700 px synlig høyde) blir det ca. 400 px igjen til filtrene,
  og de ruller da i sitt eget område. Er det for lite, kan verktøylinjen rulle med filtrene i
  stedet. Se spørsmålet.

## Spørsmål til Svein
1. Skal verktøylinjen stå fast øverst mens filtrene ruller under (forslag), eller rulle bort
   sammen med filtrene?

## Sveins svar 28.10.2026 kl. 10.21
1. «verktøylinjen skal stå fast over filterne». Verktøylinjen står fast øverst i venstre
   kolonne, og filtrene ruller under.
