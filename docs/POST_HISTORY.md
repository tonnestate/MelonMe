# MelonMe – minimale Posting-Historie (v0.4.0)

## Zweck

MelonMe soll eine Diskussion nicht wiederholt beantworten, nur weil sie in
mehreren Suchläufen, über unterschiedliche Quellen oder mit anderen IDs auftaucht.
**Keine KIGOR-artige Quellen- oder Personen-Datenbank.**

Die lokale Datei `~/.melonme/posting.sqlite3` speichert in genau einer Tabelle:

- `target_key`: SHA-256 aus Kanal und normalisierter Thread-Adresse
- `state`: PENDING, POSTED oder UNCERTAIN
- `posted_at`: tatsächlicher Zeitpunkt des extern bestätigten Posts (UTC)
- `external_id`: Beleg-ID aus der Antwort des bestehenden Publishers
- `attempted_at`, `token`: technische Kurzzeitfelder gegen parallele Doppelposts

**Nicht gespeichert:** Thread-Text, Nutzername, Profil, E-Mail, Produktempfehlung,
Affiliate-Link oder vollständige Diskussionsadresse. Die URL wird nur
für die Berechnung des Hashes verwendet.

## Ablauf – nur im bestehenden `find` / `execute`

1. `find` prüft die Thread-Adresse vor dem Produktabruf. Bereits beantwortete
   Diskussionen erscheinen in `posted[]` mit `last_posted_at` und `external_id`.
   Die übrigen Fragen werden normal bearbeitet.
2. `execute` prüft denselben Thread noch einmal vor der Linkgenerierung.
3. Direkt vor dem externen POST wird atomar ein kurzer lokaler Eintrag reserviert.
   So können zwei parallele lokale Worker den gleichen Thread nicht gleichzeitig beantworten.
4. Erst nach echter externer Beitrags-ID wird `POSTED` mit dem Zeitpunkt
   eingetragen. Der vorhandene Publisher erhält als `idempotency_key`
   eine stabile Thread-Kennung, nicht den wechselnden Text-Hash.
5. Bei einem Timeout oder einer unklaren externen Antwort heißt der Status
   für diesen einzelnen Thread `PUBLISH_UNCERTAIN`: Das System behauptet
   keinen erfolgreichen Beitrag und vermeidet unkontrollierte Duplikate.
   Andere Threads laufen weiter. Die externe Bridge muss bei einer
   späteren Wiederholung dieselbe Idempotenzkennung beachten.

Unterschiedliche Such-IDs für dieselbe Diskussion, wechselnde `utm_*`-,
`page`- oder `start`-Parameter und Discourse-Paginierungsnummern
ändern die Thread-Kennung nicht. Echte Thread-IDs in Query-Parametern
bleiben erhalten.

## Wiederholungsfenster

Standardmäßig liegt das Fenster für **bestätigte** Beiträge bei **180 Tagen**.
Der technische Wert ist über die Host-Umgebung einstellbar:

    MELONME_POST_HISTORY_DB=/persistent/path/posting.sqlite3
    MELONME_REPOST_DAYS=180

Nach diesem Fenster darf dieselbe Diskussion erneut geprüft werden.
Der ältere Zeitpunkt war bis zu einer neuen erfolgreichen Veröffentlichung
gespeichert. Das ist ein **lokaler Duplikatschutz**, kein globaler Foren-Stopp,
kein neuer Workflow und keine Aussage über die Regeln eines Forums.

## Realer Registrierungsstand

**MelonMe besitzt keine automatische Registrierung für Foren.**
`melonme/server.py` enthält nur `find`, `execute`, `learn` und
HTTP-Bridges für Produktangebote und Veröffentlichung. Es gibt dort
keinen Account-Creator, Login- oder Session-Verwalter. Die Veröffentlichung
funktioniert nur, wenn der **bestehende** FruitStack-Publisher eine
tatsächlich nutzbare Schnittstelle bereitstellt. Eine solche Live-Integration
wurde nicht nachgewiesen.

## Grenzen

Diese SQLite-Datei schützt eine gemeinsame lokale Laufzeit. Mehrere Hosts
benötigen zusätzlich eine **gemeinsame** idempotente Publisher-Bridge;
eine pro Host getrennte lokale Datenbank genügt dann nicht.
Bei fehlender Historie läuft `find` mit einem Fehlerhinweis weiter;
nur ein konkret beabsichtigter Post wird ohne verlässliche Duplikatprüfung
nicht blind als erfolgreich behandelt.

## Nachweise

- `tests/test_post_history.py`: Persistenz, normalisierte URLs, konkurrierende
  Reservierungen, lokale Fehlerschranken, Vorprüfung vor Anbieteraufrufen.
- `tests/test_mcp_protocol.py`: dieselben drei MCP-Tools bleiben verfügbar.
