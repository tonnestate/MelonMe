# MelonMe — ausführbarer erster Schnitt

## Start

Python 3.11+:

    python -m pip install -e .
    python -m melonme.server

MCP v2 über stdio. Genau drei Tools: find, execute, learn.
Ein bestehender FruitStack-MCP-Host kann den Prozess starten:

    {"mcpServers":{"melonme":{"command":"python","args":["-m","melonme.server"]}}}


**v0.3.0:** Siehe [Release-Anleitung](RELEASE_0.3.md) zu mehrseitigen
Awin-Promotions, getrennt bewerteten Käuferfragen im selben Feed,
sprachunabhängigen Absatzmärkten und provisionsgenauer Zuordnung
über `attribution_map` und `by_opportunity`. Die CI testet jetzt auch
die echten MCP-v2-Aufrufe aller drei Tools.

## find(context)

Der Host liefert echte Fragen und konkrete Angebote (keine erfundenen Katalogdaten).
Sprache und Absatzmarkt sind getrennte Werte.

    {
      "questions": [{
        "id": "q-101", "source_url": "https://community.example/q/101",
        "channel": "forum", "text": "Suche Sport Kopfhörer",
        "language": "de", "market": "AT"
      }],
      "offers": [{
        "title": "Sport Kopfhörer", "market": "AT",
        "provider": "host", "url": "https://shop.example/sport",
        "price": "49.99", "currency": "EUR",
        "verified_facts": ["Bluetooth"]
      }],
      "probe_awin": false
    }

Wenn probe_awin=true und AWIN_PUBLISHER_ID sowie AWIN_API_TOKEN gesetzt sind,
liest MelonMe über die echte Awin-API die beigetretenen Partnerprogramme
pro Zielmarkt. Die tatsächliche Anzahl wird ausgegeben; Programme sind
keine Produktangebote. Bei 401, 403, 429 oder fehlender Konfiguration
bleiben die gefundenen Angebote und anderen Gelegenheiten verfügbar.

## execute(opportunity)

Der Host liefert eine Opportunity mit gültigem Markt und Offer.
Die Option answer_text enthält eine vom FruitStack formulierte Antwort.
Ohne diesen Text erstellt MelonMe einen knappen sachlichen Entwurf
aus verifizierten Produktdaten. Ohne publish=true wird nur DRAFT_ONLY
ausgegeben. Der Entwurf liefert einen Inhalts-`fingerprint` und eine für denselben Zielbeitrag stabile `publication_key`; nur letztere ist der externe `idempotency_key`. Ein erfolgreicher Awin Link Builder liefert zusätzlich `clickref` für die spätere Zuordnung.

Zum Veröffentlichen ist die vorhandene, berechtigte FruitStack-Bridge
anzuschließen, nicht ein neuer Publikationsagent:

    MELONME_PUBLISH_BRIDGE_URL=https://publisher.example/api/publish
    MELONME_PUBLISH_BRIDGE_TOKEN=<secret from host secret store>

Die Bridge akzeptiert HTTPS POST mit den Feldern id, channel, source_url,
text und idempotency_key. Erfolgreiche Veröffentlichung meldet eine
tatsächliche externe Beleg-ID:

    {"external_id":"actual-post-id","url":"https://forum.example/p/123"}

Ohne externe ID behauptet MelonMe keinen veröffentlichten Beitrag.
Die Bridge ist für die tatsächlichen Kanalberechtigungen und die
Vermeidung doppelter Posts bei Wiederholung zuständig.

Bei einem Awin-Angebot mit provider=awin, advertiser_id, URL und
passendem Markt prüft MelonMe nach Möglichkeit das beigetretene Programm
und erzeugt den realen Trackinglink per Awin Link Builder.
Funktioniert das nicht, wird nur dieser Link-Versuch zurückgestellt.

## learn(results)

Übergeben werden echte Transaktionen, belegte Auszahlungen und Kosten.

    {
      "transactions":[
        {"id":"tx-42","provider":"awin","status":"approved",
         "currency":"EUR","commission":"12.50"}
      ],
      "payouts":[
        {"payment_id":"bank-42","currency":"EUR","amount":"10.00"}
      ],
      "costs":[{"currency":"EUR","amount":"3.20"}]
    }

APPROVED bedeutet NICHT PAID. Auszahlung nur aus einem separaten
Payment-Beleg. Währungen werden getrennt ausgewiesen; keine
Wechselkurse geraten. Mit sync_awin=true, start und end im Format
YYYY-MM-DDTHH:MM:SS und einem maximalen Zeitfenster von 31 Tagen
werden echte Awin-Publisher-Transaktionen gelesen.

## Testen

    python -m unittest discover -s tests -v

Tests sind offline und benötigen keine Tokens, Konten oder LLMs.
CI prüft außerdem den MCP-Import.

## Was noch nicht vorhanden ist

Das Repository hat bislang KEINE nachweislich aktive Live-Verbindung
zu den privaten FruitStack-Komponenten, zu tatsächlichen Amazon-
Creators-API-Credentials oder zu einem Publisher-Konto.
Die Amazon-Creators-API ist der offizielle Nachfolger der früheren PA-API 5.
Ein Produkt-Suchadapter für Amazon und proaktive globale Quellensuche
werden hier nicht als bereits implementiert behauptet. Der Host kann
bereits vorhandene Quellen/Angebote in find einspeisen.

API-Referenzen:
- https://help.awin.com/apidocs/get-program-information
- https://help.awin.com/apidocs/generatelink
- https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-publisher
- https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation


## v0.2: Bestehende FruitStack-Produktsuche direkt verbinden

Setze die URL und das Zugriffstoken der **bereits vorhandenen** Suchfunktion:

    MELONME_INVENTORY_BRIDGE_URL=https://fruitstack.example/api/search-offers
    MELONME_INVENTORY_BRIDGE_TOKEN=<token from existing secret store>

Wenn die URL gesetzt ist, sendet find einen gebündelten HTTPS-POST mit
questions (id, text, market, language, search_terms) und
limit_per_question=10. Die Host-Funktion muss liefern:

    {"offers":[
      {"title":"Bose Sport Kopfhörer","market":"AT",
       "url":"https://shop.example/p1","provider":"host",
       "price":"89.90","currency":"EUR",
       "affiliate_url":"https://affiliate.example/r",
       "affiliate_verified":true}
    ]}

affiliate_verified=true bedeutet: Der **Host** hat diesen Link
tatsächlich validiert. Ohne solche Angabe wird ein mitgelieferter
Affiliate-Link nicht als geprüft bezeichnet. Wenn der Host nicht antwortet,
läuft find mit anderen vorhandenen Quellen weiter.

Die Frage kann search_terms als explizite sprachübergreifende Suchbegriffe
enthalten, z.B. eine englische Frage und die deutschen Produktausdrücke.
MelonMe unterstellt weder Sprache=Land noch übersetzt es Produktangaben
auf Verdacht.

## v0.2: Live-Awin-Produktfeeds und Aktionen

Eine vorhandene Awin Publisher API-Kennung lässt sich lesend
auf folgende Weise benutzen:

    {
      "questions":[{"id":"q1","text":"Sport Kopfhörer",
                    "market":"AT","language":"de"}],
      "offers":[],
      "awin_promotions":true,
      "awin_feeds":[{
        "advertiser_id":1234,"locale":"de_AT",
        "market":"AT","max_rows":5000
      }]
    }

awin_promotions ruft die echte Awin Offers API für die konkreten
Zielmärkte auf. Ein Aktionsangebot ist nicht dasselbe wie ein konkretes
Katalogprodukt.

awin_feeds ruft die echte **Enhanced Google JSONL Product Feed API** ab,
jedoch nur für explizit angegebene Advertiser + Locale. Ein Feed kann
Millionen Produkte enthalten; maximal max_rows werden je Aufruf gescannt
(standardmäßig 5.000). Das Ergebnis enthält inventory_checks mit
scanned_rows, complete und partial. **partial=true bedeutet: nicht
vollständig durchsucht. Ein fehlender Treffer belegt dann nichts über den
restlichen Feed.** Die Ausführung ist außerdem auf maximal zwei Feeds pro
find-Aufruf begrenzt.

Awin begrenzt Feed-Aufrufe auf **höchstens fünf pro Minute**; es darf
nicht parallel derselbe Advertiser-Feed abgefragt werden. Publisher-API-
Aufrufe können zusätzliche Limits haben. FruitStack muss daher den
bestehenden gemeinsamen Scheduler/Cache respektieren. MelonMe führt
keinen eigenen allgemeinen Scheduler ein.

Ein Tracking-Link wird nur nach einem erfolgreich ausgeführten Link
Builder oder einer Host-verifizierten URL als tracked ausgewiesen.
Zustandslose Fehler werden beim jeweiligen Anbieter gemeldet, nicht
zum globalen STOP umgedeutet.

## v0.2: Finanzkorrekturen

Die Awin-Transaktionsantwort verwendet commissionStatus und
commissionAmount.amount/currency. Die Auswertung dedupliziert
wiederholte IDs und bevorzugt spätere Validierungen bzw. genehmigte
statt unverarbeitete Snapshots. approved ist **kein** Zahlungseingang;
Zahlungsbelege bleiben ein separater Eingang.

## Noch nicht nachgewiesen

Es gab bisher keinen authentifizierten Live-Awin-Aufruf mit dem realen
Publisherkonto, keinen Abruf einer echten Amazon-Creators-API und keine
verifizierte Verbindung zu einem laufenden FruitStack-Host. Die
Produktfeed-Tests verwenden dokumentationsnahe Offline-Datensätze.

Zusätzliche offizielle Awin-Quellen:
- https://help.awin.com/apidocs/retail-publisher-productapidocumentation-1
- https://help.awin.com/apis/apidocs/promotions
- https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-publisher
