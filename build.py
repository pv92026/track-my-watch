#!/usr/bin/env python3
"""Build the static support site; publication requires real provider details."""
from pathlib import Path
from html import escape
import argparse
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true', help='Render a clearly marked local draft.')
args = parser.parse_args()
C = json.loads((ROOT / 'site-config.json').read_text())
missing = not C['provider_name'].strip() or len(C['provider_address_lines']) < 2 or any(not x.strip() for x in C['provider_address_lines'])
if missing and not args.preview:
    raise SystemExit('Nicht veröffentlicht: Anbietername und vollständige öffentliche Anschrift in site-config.json fehlen. Für eine lokale Vorschau: python3 build.py --preview')
OUT = ROOT / ('preview' if args.preview else 'dist')
OUT.mkdir(exist_ok=True)
(OUT / 'en').mkdir(exist_ok=True)
(OUT / 'assets').mkdir(exist_ok=True)
for asset in ['style.css', 'mark.svg']:
    shutil.copy2(ROOT / asset, OUT / 'assets' / asset)
EMAIL = escape(C['support_email'])
EMAIL_LINK = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'

def md_inline(text):
    text = escape(text)
    text = re.sub(r'\[([^\]]+)\]\((mailto:[^)]+)\)', r'<a href="\2">\1</a>', text)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def md_blocks(text):
    result = []
    for block in text.strip().split('\n\n'):
        lines = block.splitlines()
        if all(re.match(r'^\d+\. ', line) for line in lines):
            result.append('<ol>' + ''.join('<li>' + md_inline(re.sub(r'^\d+\. ', '', x)) + '</li>' for x in lines) + '</ol>')
        else:
            result.append('<p>' + md_inline(' '.join(lines)) + '</p>')
    return ''.join(result)

def provider(lang):
    if missing:
        return '<p class="provider-pending">' + ('Anbietername und öffentliche Anschrift werden vor der Veröffentlichung ergänzt.' if lang == 'de' else 'The provider’s name and public postal address will be added before publication.') + '</p>'
    return '<address><strong>' + escape(C['provider_name']) + '</strong><br>' + '<br>'.join(escape(x) for x in C['provider_address_lines']) + '</address>'

WORDS = {
 'de': {'support':'Support','privacy':'Datenschutz','legal':'Impressum','backup':'Backup-Verschlüsselung','skip':'Zum Inhalt','nav':'Hauptnavigation','lang':'Sprache','toc':'Auf dieser Seite','footer':'Deine Uhren. Gut organisiert.','back':'Zurück zum Support','date':'Stand: 24. September 2026','draft':'Vorschau · Vor der Veröffentlichung fehlen noch die öffentlichen Anbieterangaben.'},
 'en': {'support':'Support','privacy':'Privacy','legal':'Legal notice','backup':'Backup encryption','skip':'Skip to content','nav':'Main navigation','lang':'Language','toc':'On this page','footer':'Your watches, well organised.','back':'Back to support','date':'Updated: 24 September 2026','draft':'Preview · Public provider details must be added before publication.'}
}
FILES = {'support':'index.html','privacy':'privacy.html','legal':'legal.html','backup':'backup.html'}

def page(lang, key, title, description, body):
    w = WORDS[lang]
    rel = '../' if lang == 'en' else ''
    filename = FILES.get(key, '404.html')
    de_link = rel + filename
    en_link = filename if lang == 'en' else 'en/' + filename
    nav = ''.join(f'<a href="{FILES[k]}"' + (' aria-current="page"' if key == k else '') + f'>{w[k]}</a>' for k in ['support','privacy','legal'])
    langs = f'<a href="{de_link}" lang="de" hreflang="de"' + (' aria-current="page"' if lang=='de' else '') + '>DE</a>'
    langs += f'<a href="{en_link}" lang="en" hreflang="en"' + (' aria-current="page"' if lang=='en' else '') + '>EN</a>'
    note = '<div class="wrap preview-note" role="note">' + w['draft'] + '</div>' if args.preview else ''
    robots = '<meta name="robots" content="noindex,nofollow">' if args.preview or key=='notfound' else ''
    base = f'<base href="{escape(C["site_url"])}/{"en/" if lang=="en" else ""}">' if key=='notfound' and not args.preview else ''
    canonical = '' if args.preview else f'<link rel="canonical" href="{escape(C["site_url"])}/{"en/" if lang=="en" else ""}{filename}">'
    output = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#070707"><meta name="referrer" content="no-referrer"><title>{escape(title)} · Track my Watch</title><meta name="description" content="{escape(description)}">{robots}{canonical}{base}<link rel="icon" type="image/svg+xml" href="{rel}assets/mark.svg"><link rel="stylesheet" href="{rel}assets/style.css"></head>
<body><a class="skip" href="#main">{w['skip']}</a><header class="site-header wrap"><a class="brand" href="index.html"><img src="{rel}assets/mark.svg" width="42" height="42" alt=""><span>Track my Watch</span></a><div class="header-links"><nav class="main-nav" aria-label="{w['nav']}">{nav}</nav><nav class="languages" aria-label="{w['lang']}">{langs}</nav></div></header>{note}<main id="main" class="wrap">{body}</main><footer class="site-footer wrap"><div class="footer-brand"><strong>Track my Watch</strong><span>{w['footer']}</span></div><nav class="footer-links" aria-label="Footer">{nav}<a href="mailto:{EMAIL}">{'Kontakt' if lang=='de' else 'Contact'}</a></nav></footer></body></html>'''
    path = OUT / ('en' if lang == 'en' else '') / filename
    path.write_text(output, encoding='utf-8')

def support(lang):
    de = lang == 'de'
    sections = (ROOT / f'support-{lang}.md').read_text().split('\n## ')[1:]
    ids = ['storage','save-backup','restore-backup','password','details','photos','wear','watch-card']
    faqs = ''
    for id_, section in zip(ids, sections):
        question, answer = section.split('\n',1)
        faqs += f'<details class="faq" id="{id_}"><summary>{escape(question)}</summary><div class="answer">{md_blocks(answer)}</div></details>'
    if de:
        intro = '<span class="eyebrow">Hilfe & Kontakt</span><h1>Deine Sammlung.<br><span>Gut begleitet.</span></h1><p class="lead">Alles Wichtige zu Track my Watch – vom ersten Backup bis zum richtigen Blick auf deine Uhren.</p>'
        contact = f'<span class="eyebrow">Persönlicher Support</span><h2>Eine Frage offen?</h2><p>Schreib uns, wenn du Hilfe brauchst oder eine Idee für die App hast.</p><a class="button" href="mailto:{EMAIL}?subject=Track%20my%20Watch%20Support">Support kontaktieren <span aria-hidden="true">↗</span></a><span class="email-address">{EMAIL}</span>'
        principles = ['Lokal auf deinem Gerät','Ohne Benutzerkonto','Mit verschlüsseltem Backup']
        side = '<h2>Häufige Fragen</h2><p>Wähle ein Thema, um die Antwort zu öffnen.</p><a href="backup.html">So schützt die App dein Backup →</a><p class="fineprint" style="margin-top:26px">Bei Problemen helfen App-Version, iOS-Version, Gerätemodell und eine kurze Beschreibung. Bitte keine Passwörter oder privaten Backups senden.</p>'
    else:
        intro = '<span class="eyebrow">Help & contact</span><h1>Your collection.<br><span>In good company.</span></h1><p class="lead">Get to know Track my Watch — from your first backup to a closer look at your watches.</p>'
        contact = f'<span class="eyebrow">Personal support</span><h2>Still have a question?</h2><p>Get in touch if you need a hand or have an idea for the app.</p><a class="button" href="mailto:{EMAIL}?subject=Track%20my%20Watch%20Support">Contact support <span aria-hidden="true">↗</span></a><span class="email-address">{EMAIL}</span>'
        principles = ['Stored on your device','No account required','Encrypted backups']
        side = '<h2>Common questions</h2><p>Choose a topic to open the answer.</p><a href="backup.html">How the app protects your backup →</a><p class="fineprint" style="margin-top:26px">For help with a problem, include your app version, iOS version, device model and a brief description. Please do not send passwords or private backups.</p>'
    body = f'<section class="hero"><div>{intro}</div><aside class="contact-card">{contact}</aside></section><div class="principles">' + ''.join(f'<span>{x}</span>' for x in principles) + f'</div><section class="help-grid" aria-label="FAQ"><div class="help-sidebar">{side}</div><div>{faqs}</div></section>'
    page(lang,'support',WORDS[lang]['support'], 'Hilfe, Kontakt und Antworten zu Track my Watch.' if de else 'Help, contact and answers for Track my Watch.', body)

def article(lang, key, intro, sections):
    w = WORDS[lang]
    toc = f'<aside class="contents" aria-label="{w["toc"]}"><strong>{w["toc"]}</strong>' + ''.join(f'<a href="#{id_}">{escape(title)}</a>' for id_,title,_ in sections) + '</aside>'
    content = ''.join(f'<section id="{id_}"><h2>{escape(title)}</h2>{body}</section>' for id_,title,body in sections)
    body = f'<header class="article-head"><span class="eyebrow">Track my Watch</span><h1>{w[key]}</h1><p class="lead">{intro}</p><p class="meta">{w["date"]}</p></header><div class="article-layout">{toc}<div class="prose">{content}<a class="back-link" href="index.html">← {w["back"]}</a></div></div>'
    page(lang,key,w[key],intro,body)

def privacy(lang):
    if lang == 'de':
        sections = [
         ('contact','Verantwortlicher & Kontakt',provider(lang)+f'<p>Für Fragen zum Datenschutz: {EMAIL_LINK}.</p>'),
         ('app','Deine Sammlung in der App','<p>Track my Watch speichert Uhren, Kaufdaten, Seriennummern, Aufbewahrungsorte, Notizen, Fotos, Dokumente, Serviceeinträge, Ereignisse, Gangwerte und Tragezeiten lokal im App-Speicher deines Geräts. Die App benötigt kein Benutzerkonto und übermittelt deine Sammlung nicht an einen Server des Entwicklers. Sie enthält keine Werbung und keine eigenen Analyse- oder Trackingdienste.</p><p>Du bestimmst, welche Fotos und Dokumente du importierst. Erinnerungen werden nach deiner Erlaubnis lokal von iOS angezeigt. Die optionale App-Sperre nutzt die Geräteauthentifizierung; die App erhält deren Ergebnis, keine biometrischen Daten und keinen Gerätecode.</p><p>Sprache, Diskretionsmodus und Anzeigeoptionen werden in den lokalen App-Einstellungen gespeichert. Der Aufbewahrungsort einer Uhr ist deine manuelle Angabe; die App ermittelt keinen GPS-Standort.</p>'),
         ('sharing','Backups & Teilen','<p>Ein manuell erstelltes Backup enthält auch private Angaben, Fotos und Dokumente. Es wird mit deinem Passwort verschlüsselt. Du wählst den Speicherort selbst. Ein in iCloud Drive oder bei einem anderen Anbieter gespeichertes Backup ist eine separate Datei. Die App synchronisiert deine Sammlung nicht automatisch. iOS-Gerätesicherungen richten sich zusätzlich nach deinen Systemeinstellungen.</p><p>Beim Teilen einer Watch Card bestimmst du Empfänger und Ziel-App. Kaufpreis, Seriennummer, Aufbewahrungsort und private Notizen werden nicht als Felder übernommen. Prüfe Fotos und Freitext vor dem Teilen auf persönliche Inhalte.</p>'),
         ('website','Diese Website','<p>Die Website wird über GitHub Pages bereitgestellt. Beim Aufruf erhält GitHub technische Verbindungsdaten. GitHub bestätigt insbesondere die Protokollierung von IP-Adressen zu Sicherheitszwecken. Anbieter sind GitHub, Inc. bzw. GitHub B.V.</p><p>Für die Bereitstellung und Sicherheit der Website wird Art. 6 Abs. 1 lit. f DSGVO herangezogen. Das berechtigte Interesse ist ein zuverlässiges, sicheres Informationsangebot.</p><p>Diese Website verwendet keine eigenen Analysewerkzeuge, Werbetracker, Kontaktformulare, Cookies oder Browser-Speicher. Schriftarten werden vom Gerät geladen, Grafiken und Stylesheets vom selben Hosting. Externe Links werden erst beim Anklicken aufgerufen.</p><p>Informationen zu GitHubs Verarbeitung, Aufbewahrung und internationalen Übermittlungen: <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noreferrer">GitHub-Datenschutzhinweise</a>. GitHub nennt unter anderem Standardvertragsklauseln und das EU-US Data Privacy Framework als Übermittlungsmechanismen.</p>'),
         ('support','Support per E-Mail',f'<p>Wenn du an {EMAIL_LINK} schreibst, werden deine E-Mail-Adresse, der Nachrichteninhalt und freiwillig übermittelte Anhänge zur Bearbeitung deiner Anfrage verarbeitet. Die Angabe weiterer Informationen ist freiwillig; ohne eine erreichbare Kontaktadresse ist eine Antwort nicht möglich.</p><p>Der E-Mail-Dienst ist Gmail von Google; für Nutzer im EWR ist Google Ireland Limited der zuständige Anbieter. Dabei können Informationen auch außerhalb des EWR verarbeitet werden. Details zu Empfängern, Schutzmechanismen und Aufbewahrung findest du in <a href="https://policies.google.com/privacy?hl=de" rel="noreferrer">Googles Datenschutzerklärung</a> und den <a href="https://policies.google.com/privacy/frameworks?hl=de" rel="noreferrer">Hinweisen zu Datenübermittlungen</a>.</p><p>Grundlage ist Art. 6 Abs. 1 lit. f DSGVO, um Anfragen zu beantworten und Probleme zu beheben; bei einer vertragsbezogenen Anfrage Art. 6 Abs. 1 lit. b DSGVO. Korrespondenz wird aufbewahrt, solange sie zur Bearbeitung und nachvollziehbaren Klärung der Anfrage erforderlich ist. Danach wird sie gelöscht, sofern keine gesetzlichen Aufbewahrungspflichten oder erforderliche Rechtsansprüche entgegenstehen.</p><p>Bitte sende keine Passwörter, vollständigen Backups oder unnötigen privaten Angaben. Supportnachrichten werden nicht für Newsletter verwendet.</p>'),
         ('deletion','Daten löschen','<p>Du kannst Uhren samt zugehörigen App-Daten in der App löschen. Importierte Originaldateien sowie exportierte Backups und Watch Cards sind unabhängige Kopien und müssen am jeweiligen Speicherort gelöscht werden. Beim Löschen der App werden ihre lokalen Daten entfernt. Sichere die Sammlung vorher, wenn du sie behalten möchtest.</p><p>Der Entwickler hat keinen Fernzugriff auf deine lokale Sammlung. Für Supportdaten kannst du dich an die oben genannte E-Mail-Adresse wenden.</p>'),
         ('rights','Deine Rechte','<p>Unter den gesetzlichen Voraussetzungen bestehen Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung und Datenübertragbarkeit. Einer Verarbeitung auf Basis berechtigter Interessen kannst du aus Gründen deiner besonderen Situation widersprechen. Außerdem kannst du dich bei einer Datenschutzaufsichtsbehörde beschweren.</p><p>Es findet durch den Anbieter keine automatisierte Entscheidung mit rechtlicher oder ähnlich erheblicher Wirkung und kein Profiling statt.</p>')
        ]
        intro='Wie die App, diese Website und der Support mit deinen Angaben umgehen.'
    else:
        sections = [
         ('contact','Controller & contact',provider(lang)+f'<p>For privacy questions: {EMAIL_LINK}.</p>'),
         ('app','Your collection in the app','<p>Track my Watch stores watches, purchase details, serial numbers, storage locations, notes, photos, documents, service records, events, timekeeping measurements and wear sessions locally in the app’s storage on your device. No account is needed. The app does not send your collection to a developer-operated server. It contains no advertising and no analytics or tracking services of its own.</p><p>You choose which photos and documents to import. With your permission, iOS displays local reminders. The optional app lock uses device authentication; the app receives the result, not biometric data or your device passcode.</p><p>Language, discreet mode and display preferences are stored in local app settings. A watch’s storage location is entered manually; the app does not determine a GPS location.</p>'),
         ('sharing','Backups & sharing','<p>A manual backup includes private details, photos and documents. It is encrypted with your password. You choose where to save it. A backup saved to iCloud Drive or another provider is a separate file. The app does not automatically sync your collection. iOS device backups also depend on your system settings.</p><p>When sharing a Watch Card, you choose the recipient and destination app. Purchase price, serial number, storage location and private notes are excluded as fields. Check your photos and free text for personal content before sharing.</p>'),
         ('website','This website','<p>This website is hosted on GitHub Pages. GitHub receives technical connection data when you visit. GitHub specifically states that it logs IP addresses for security purposes. Its providers are GitHub, Inc. or GitHub B.V.</p><p>Article 6(1)(f) GDPR applies to providing and securing the website. The legitimate interest is a reliable, secure information service.</p><p>This website uses no analytics tools, advertising trackers, contact forms, cookies or browser storage of its own. Fonts come from your device; images and stylesheets use the same hosting. External links are accessed when clicked.</p><p>For GitHub’s processing, retention and international transfers, see the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noreferrer">GitHub Privacy Statement</a>. GitHub describes Standard Contractual Clauses and the EU-US Data Privacy Framework among its transfer mechanisms.</p>'),
         ('support','Email support',f'<p>If you email {EMAIL_LINK}, your address, message and any attachments you choose to send are processed to handle your request. Further information is voluntary; a reachable contact address is needed to reply.</p><p>Email is handled through Google’s Gmail service. Google Ireland Limited is the relevant provider for users in the EEA. Information may be processed outside the EEA. See <a href="https://policies.google.com/privacy?hl=en" rel="noreferrer">Google’s Privacy Policy</a> and its <a href="https://policies.google.com/privacy/frameworks?hl=en" rel="noreferrer">data transfer information</a> for recipients, safeguards and retention.</p><p>The basis is Article 6(1)(f) GDPR to answer questions and resolve problems, or Article 6(1)(b) for contract-related requests. Correspondence is retained for as long as needed to handle and clarify the request, then deleted unless legal retention duties or necessary legal claims require otherwise.</p><p>Please do not send passwords, complete backups or unnecessary private details. Support messages are not used for newsletters.</p>'),
         ('deletion','Deleting data','<p>You can delete watches and their associated app data in the app. Imported original files, exported backups and Watch Cards are independent copies and must be deleted where they are stored. Deleting the app removes its local data. Back up your collection first if you want to keep it.</p><p>The developer has no remote access to your local collection. For support data, contact the email address above.</p>'),
         ('rights','Your rights','<p>Subject to legal conditions, you have rights of access, correction, deletion, restriction and portability. You may object to processing based on legitimate interests for reasons relating to your particular situation. You can also complain to a data protection authority.</p><p>The provider does not conduct automated decision-making with legal or similarly significant effects, or profiling.</p>')
        ]
        intro='How the app, this website and support handle your information.'
    article(lang,'privacy',intro,sections)

def backup(lang):
    if lang == 'de':
        intro='Deine Sicherung ist mit deinem Passwort geschützt. Hier erfährst du, was das bedeutet.'
        sections=[
         ('contents','Was wird geschützt?','<p>Die App verschlüsselt den gesamten Inhalt der Sicherung: deine Sammlung einschließlich privater Angaben, Fotos und Dokumenten. Beim Öffnen prüft sie auch, ob der geschützte Inhalt verändert wurde.</p><p>Dateiname, Dateigröße und Informationen des gewählten Speicheranbieters bleiben außerhalb dieser Inhaltsverschlüsselung.</p>'),
         ('password','Dein Passwort','<p>Für eine neue Sicherung sind mindestens <strong>8 Zeichen</strong> nötig. Ein langes, einzigartiges Passwort schützt besser. Die App speichert das Passwort nicht dauerhaft. Bewahre es sicher und getrennt von der Datei auf.</p><div class="callout"><p><strong>Ein vergessenes Passwort lässt sich nicht zurücksetzen.</strong> Ist deine Sammlung noch in der App vorhanden, kannst du davon ein neues Backup mit einem neuen Passwort erstellen.</p></div>'),
         ('restore','Sichern & wiederherstellen','<p>Unter <strong>Einstellungen → Backup & Wiederherstellung</strong> gibst du dein Passwort zweimal ein, erstellst das Backup und speicherst es anschließend über die Dateien-App. Erst die Bestätigung nach dem Speichern bedeutet, dass die Datei gesichert wurde.</p><p>Zum Laden brauchst du die Datei und ihr ursprüngliches Passwort. Die Vorschau zeigt, welche Uhren ergänzt werden. Bereits vorhandene Uhrenkennungen werden übersprungen; die Wiederherstellung setzt bestehende Einträge nicht zurück.</p><p>Prüfe die Wiederherstellung auf einer separaten Testinstallation, bevor du dich allein auf eine Sicherung verlässt.</p>'),
         ('scope','Backup, App-Sperre & Diskretionsmodus','<p>Das Passwort schützt die exportierte Sicherungsdatei. Die App-Sperre regelt den Zugang zur App mit der Geräteauthentifizierung. Der Diskretionsmodus blendet Angaben nur aus; das vollständige Backup enthält weiterhin alle privaten Daten.</p><p>Eine Sicherung in iCloud Drive ist eine Datei und keine automatische Synchronisierung deiner Sammlung.</p>'),
         ('technology','Technik verständlich erklärt','<p>Die App verwendet <strong>AES-256-GCM</strong> zur Verschlüsselung. Aus deinem Passwort wird mit <strong>PBKDF2-HMAC-SHA-256</strong> und 600.000 Durchläufen ein Schlüssel abgeleitet. Zufallswerte sorgen dafür, dass neu erstellte Sicherungen unterschiedlich aussehen.</p><p>Die Umsetzung nutzt Apples CryptoKit und CommonCrypto. Das Dateiformat heißt TMWBACKUP1; die maximale Dateigröße beträgt 128 MiB.</p>')]
    else:
        intro='Your backup is protected by your password. Here is what that means.'
        sections=[
         ('contents','What is protected?','<p>The app encrypts the entire backup: your collection, private details, photos and documents. When you open it, the app also checks whether the protected contents have been altered.</p><p>The filename, file size and information held by your chosen storage provider remain outside this content encryption.</p>'),
         ('password','Your password','<p>A new backup requires at least <strong>8 characters</strong>. A long, unique password offers better protection. The app does not store it permanently. Keep it safe and separate from the file.</p><div class="callout"><p><strong>A forgotten password cannot be reset.</strong> If your collection is still in the app, you can create a new backup with a new password.</p></div>'),
         ('restore','Saving & restoring','<p>In <strong>Settings → Backup & Restore</strong>, enter your password twice, create the backup, then save it through the Files app. Only the confirmation after saving means the file has been saved.</p><p>To restore, you need the file and its original password. The preview shows which watches will be added. Existing watch IDs are skipped; restoration does not revert existing entries.</p><p>Verify restoration on a separate test installation before relying on a backup alone.</p>'),
         ('scope','Backups, app lock & discreet mode','<p>The password protects the exported backup file. The app lock controls access to the app using device authentication. Discreet mode only hides information on screen; a complete backup still contains all private data.</p><p>A backup in iCloud Drive is a file, not automatic collection sync.</p>'),
         ('technology','The technology, explained','<p>The app uses <strong>AES-256-GCM</strong> encryption. A key is derived from your password using <strong>PBKDF2-HMAC-SHA-256</strong> with 600,000 iterations. Random values make newly created backups look different.</p><p>The implementation uses Apple’s CryptoKit and CommonCrypto. The file format is TMWBACKUP1; the maximum file size is 128 MiB.</p>')]
    article(lang,'backup',intro,sections)

for lang in ['de','en']:
    support(lang)
    privacy(lang)
    backup(lang)
    article(lang,'legal','Angaben zum Anbieter von Track my Watch.' if lang=='de' else 'Provider information for Track my Watch.',[
        ('provider','Anbieter' if lang=='de' else 'Provider',provider(lang)),
        ('email','Kontakt' if lang=='de' else 'Contact',f'<p>{EMAIL_LINK}</p>')
    ])
(OUT/'.nojekyll').write_text('')
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if args.preview else 'User-agent: *\nAllow: /\n')
page('de','notfound','Seite nicht gefunden','Diese Seite wurde nicht gefunden.','<section class="notfound"><span class="eyebrow">404</span><h1>Diese Seite fehlt.</h1><p class="lead">Über die Startseite findest du Hilfe und Kontakt zu Track my Watch.</p><a class="button" href="index.html">Zum Support</a></section>')
page('en','notfound','Page not found','This page could not be found.','<section class="notfound"><span class="eyebrow">404</span><h1>This page is missing.</h1><p class="lead">Visit the support page for help and contact details.</p><a class="button" href="index.html">Go to support</a></section>')
print(f'Built {len(list(OUT.rglob("*.html")))} pages in {OUT.name}/')
