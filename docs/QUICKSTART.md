# MelonMe — ausführbarer erster Schnitt

## Start

Python 3.11+:

    python -m pip install -e .
    python -m melonme.server

MCP v2 über stdio. Genau drei Tools: find, execute, learn.
Ein bestehender FruitStack-MCP-Host kann den Prozess starten:

    {"mcpServers":{"melonme":{"command":"python","args":["-m","melonme.server"]}}}

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
ausgegeben. Der Entwurf enthält eine stabile SHA-256-Kennung.

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
