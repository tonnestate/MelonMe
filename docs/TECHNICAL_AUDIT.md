# MelonMe v0.2.0 — Technischer Befund und AVCOS-Regressionen

Stand: 28. Oktober 2026. Tatsächliche Änderungen auf `main`; keine Live-Partnerzugänge oder Umsätze behauptet.

## Gefundene Fehler und Korrekturen

| Befund | Korrektur |
| --- | --- |
| Awin-Transaktionsstatus wurde aus `status` statt `commissionStatus` gelesen. Echte Provisionen konnten übersehen werden. | Echtes Awin-Feld ausgewertet, genehmigt und ausgezahlt getrennt. |
| Die gleiche Awin-Transaktion konnte nach Validierung mehrfach oder mit falschem Zustand gezählt werden. | Deduplizierung per Anbieter/ID, aktueller Validierungszustand. |
| Es gab gar keine eigenständige Produktsuche. | Optional echter Enhanced-JSONL-Produktfeed und regionale Awin-Promotions. |
| Eine vorhandene FruitStack-Produktquelle konnte nicht direkt abgefragt werden. | Ein einziger authentifizierter Batch-Adapter, ohne zweiten Crawler. |
| HTTP-Produktlinks wurden verworfen, obwohl Awin sie offiziell unterstützt. | HTTP und HTTPS für Händler-URLs, ausschließlich HTTPS für API-Zugang und Token. |
| Ein fehlgeschlagener Link-Builder stoppte die Affiliate-Auswertung des besten Angebots. | Anbieterfehler lokal; vergleichbar geeignete Alternativen bleiben verwendbar. |
| Extern mitgelieferte Affiliate-URLs wurden ungeprüft als funktionsfähig markiert. | Verifizierter Host-Beleg oder erfolgreiche reale Link-Erzeugung nötig. |
| Ein unvollständig geladener Produktfeed konnte als vollständige Suche missverstanden werden. | `scanned_rows`, `partial`, `complete`; Trailer-Fehler werden erkannt. |
| Sprach- und Marktzuordnung war zu starr; kürzere Modellnamen fielen durchs Raster. | Getrennte Sprache/Markt-Werte und explizite mehrsprachige `search_terms`. |
| Erfolgreiche Partnerchecks standen im Feld `errors`. | Getrennte `provider_checks` und `errors`. |
| Bearer-Header konnten bei URL-Redirects weitergereicht werden. | Weiterleitungen bei API- und Feed-Aufrufen unterbunden. |

## Kleiner fachlicher Umfang

Es bleiben genau drei MCP-Tools: `find`, `execute`, `learn`. Produkt- und Accountdaten bleiben in vorhandenen FruitStack- und Partnerdiensten. Keine neue allgemeine Orchestrierung, kein eigener Scheduler oder Credential-Manager, kein globaler STOP bei einer lokalen Störung.

## Noch offen

- Echte Awin-Publisher-Credentials und Amazon-Creators-API-Zugriffe sind nicht mit einem realen Konto geprüft.
- Die FruitStack-Inventar- und Publisher-Bridge ist technisch vorbereitet, aber nicht an laufende Host-Endpunkte angeschlossen.
- Awin Enhanced Feeds sind je Abruf begrenzt; ein Teilschnitt beweist keine Nichtverfügbarkeit im Land.
- Automatische weltweite Community-Discovery und wirtschaftliche Selbstoptimierung auf Basis bestätigter Einnahmen sind noch nicht implementiert.
- Es liegen keine realen Beiträge, Transaktionen oder Auszahlungen vor. Offline-Regressionstests sind kein Live-Nachweis.

## Primärquellen

- https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-publisher
- https://success.awin.com/articles/en_US/Knowledge/Publisher-API-GET-transactions-list
- https://help.awin.com/apidocs/retail-publisher-productapidocumentation-1
- https://help.awin.com/apis/apidocs/promotions
- https://py.sdk.modelcontextprotocol.io/migration/
