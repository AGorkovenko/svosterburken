# SV 1919 Osterburken e.V. – neue Website

Statische Website ohne Datenbank. Seiten werden mit einem kleinen Python-Skript gebaut.

    python3 build.py                    # baut public/ neu
    python3 -m http.server 4173 -d public   # lokal ansehen: http://localhost:4173

## Aufbau

| Pfad | Inhalt |
|---|---|
| `src/pages/*.html` | Inhalte der Seiten (Kopfzeilen: title, description, theme, nav, scripts) |
| `src/partials/` | Kopf- und Fußbereich für alle Seiten |
| `src/data/news.json` | Beiträge („Aktuelles“), aus der alten WordPress-Seite übernommen |
| `src/data/sponsors.json` | Sponsorenlogos |
| `build.py` | Vorstandschaft (Liste oben im Skript), Deko-Motive, Beitragskarten |
| `tools/make_forms.py` | erzeugt die drei Online-Formularseiten |
| `public/assets/js/data.js` | **alle Trainingszeiten** – Heute-Tafel, Wochenpläne, Team- und Gruppenkarten |
| `public/assets/js/forms.js` | füllt die Original-PDFs im Browser aus (pdf-lib), nichts wird übertragen |
| `public/assets/img/icons.svg` | kleine Vektor-Icons (Phosphor Icons, MIT) – Pfeile, Mail, Kalender … |
| `public/assets/img/iconsflat/` | farbige Flat-Icons als SVG (generiert mit OpenAI GPT Image 2.5 über OpenRouter, vektorisiert) |
| `src/icon-sheets/flat-*.png` + `tools/vectorize_icons.py` | Original-Sheets und Skript: zerschneiden, Farben einrasten, vektorisieren |
| `public/assets/img/svo-logo*.png` | Vereinslogo: Original-PNG (2000 px) und verkleinerte Fassungen |
| `public/assets/img/gen/` | KI-Illustrationen (keine Vereinsmitglieder) |

## Häufige Änderungen

- **Trainingszeit ändern:** `public/assets/js/data.js` bearbeiten – kein Build nötig.
- **Neuer Beitrag:** Eintrag in `src/data/news.json` ergänzen (slug, date, title, cats, image, excerpt, body), Bild nach `public/assets/img/news/` und Vorschaubild nach `news/thumb/`, dann `python3 build.py`.
- **Vorstandsfoto:** Foto nach `public/assets/img/vorstand/` legen und in `build.py` (`VORSTAND`) statt Platzhalter verwenden.

## Design System

- `public/design-system.html` – interne Referenzseite (nicht verlinkt, `noindex`): Farben, Schriften, Icons, Bausteine, Code-Beispiele
- `public/assets/design-tokens.json` – alle Tokens im W3C-Format für andere Produkte (App, Druck, Social Media)
- Abteilungsfarben über `data-theme` (`fussball`, `turnen`, `fitness`, `verein`) → `--accent`, `--accent-soft`, `--accent-ink`, `--on-accent`

## Icons in Seiten

- `{{icon:arrow}}` – kleines Vektor-Icon (Buttons, Listen)
- `{{art:ball}}` – farbiges Flat-Icon (SVG) (Karten, Kacheln, Kontakte); verfügbar: ball, child, music, glove, family, dance, volleyball, stretch, walk, fistball, dumbbell, medal, whistle, handshake, shield, clipboard, team, trophy, food, couple, heart, jersey, calendar, pin, mail

## Farben

Wappenblau `#1B3D8C`, Trikotblau `#2352D6`, Fußball Grün `#12A05A`, Turnen Orange `#FF6F3C`, Fitness Pink `#E23D7F`, „Heute/Läuft“ Gelb `#FFC933`.
