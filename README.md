# Track my Watch — Supportwebsite

Deutsch und Englisch, Schwarz/Gold, statische Seiten ohne JavaScript, Fremdschriften, Formulare oder eigene Cookies/Analyse.

## Stand

Support, Backup-Erklärung, Datenschutzerklärung und Impressum wurden am 29.10.2026 mit den freigegebenen öffentlichen Anbieterangaben über GitHub Pages veröffentlicht. Alle acht Inhaltsseiten wurden auf Deutsch und Englisch live geprüft, einschließlich Anbieteranschrift, Kontaktadresse, Navigation und Sprachumschaltung. Die Kontaktadresse ist `trackmywatch.support@gmail.com`.

Erfolgreicher Veröffentlichungsablauf: https://github.com/pv92026/track-my-watch/actions/runs/40889148335 (Quellstand `c24e019eb984a89501a00857f1cccb6c679a0606`).

Die Inhalte beschreiben App-Version 1.0 einschließlich der kompakten Tragezeit-Historie aus Build 30. Build 32 ergänzt die direkten Website-Links in den Einstellungen. Es gibt keine automatische iCloud-Synchronisierung. Das Backup ergänzt fehlende Uhren und überschreibt vorhandene Kennungen nicht.

## Vorschau und Veröffentlichung

- `python3 build.py --preview` erstellt eine deutlich markierte Vorschau in `preview/`.
- `python3 build.py` erstellt ausschließlich bei ausgefülltem Anbietername und Anschrift die veröffentlichbaren Dateien in `dist/`.
- Die freigegebenen Angaben in `site-config.json` werden auf Impressum und Datenschutzseite übernommen; auch das Stand-Datum stammt aus dieser Datei. Keine nicht zur Veröffentlichung bestimmten persönlichen Daten eintragen.
- In GitHub Settings → Pages als Quelle **GitHub Actions** wählen.
- Nach Inhaltsänderungen den Workflow **Publish support website** manuell ausführen. Es gibt keine automatische Veröffentlichung bei einem Commit.
- Danach HTTPS-Erreichbarkeit aller Seiten auf der von GitHub bestätigten Adresse prüfen.

Veröffentlichte App-Store-Links:

- DE Support: `https://pv92026.github.io/track-my-watch/`
- DE Datenschutz: `https://pv92026.github.io/track-my-watch/privacy.html`
- EN Support: `https://pv92026.github.io/track-my-watch/en/index.html`
- EN Datenschutz: `https://pv92026.github.io/track-my-watch/en/privacy.html`

Die Quellen liegen in `build.py`, `support-de.md`, `support-en.md`, `style.css`, `mark.svg` und `site-config.json`. Es werden nur die Dateien in `dist/` ausgeliefert, keine Projektunterlagen oder App-Quelltexte. Python-Standardbibliothek genügt.

## Datenschutzgrundlagen

Anbieterangaben und die beschriebene tatsächliche Supportabwicklung müssen weiterhin zusammenpassen. Der Text ist auf die vorhandene lokale App, GitHub Pages und den gewählten Gmail-Kontakt abgestimmt; er ist keine unabhängige rechtliche Prüfung. Supportkorrespondenz wird entsprechend der veröffentlichten Zweck- und Aufbewahrungsbeschreibung behandelt. Die Website enthält keine zugesagten Support-Reaktionszeiten.

Primärquellen, geprüft am 24.09.2026:

- GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- GitHub-Datenschutzhinweise: https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement
- Google-Datenschutzhinweise: https://policies.google.com/privacy?hl=de
- Google-Datenübermittlungen: https://policies.google.com/privacy/frameworks?hl=de
- DSGVO: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Anbieterangaben: https://www.die-medienanstalten.de/aufgaben/aufsicht/impressumspflicht/
- GitHub-Pages-Workflow: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
