# MelonMe — Guerrilla Monetization MCP

**Konzept v0.3.1 · 28. Oktober 2026**  
**Status:** Konzept v0.3.1 + Python-MCP v0.4.0; Live-Betrieb nicht verifiziert  
**Systemrolle:** schlankes, seitlich angedocktes Geschäftsmodell des bestehenden FruitStacks

> **MelonMe findet aktuelle Kaufabsichten, nutzt passende und tatsächlich erreichbare Angebote, antwortet dort, wo eine kommerzielle Beteiligung erlaubt ist, und lernt aus realem wirtschaftlichem Erfolg. Schnell, international, mit geringsten Betriebskosten.**
>
> **FruitStack denkt und organisiert. MelonMe führt dieses eine Geschäft aus.**

## Tatsächlich implementierter Stand (28.10.2026)

Das Repository enthält jetzt einen **installierbaren MCP-v2-stdio-Server** mit drei ausführbaren Funktionen: `find`, `execute`, `learn`. Der Code steht in [melonme/core.py](melonme/core.py) und [melonme/server.py](melonme/server.py). Die [Kurzanleitung](docs/QUICKSTART.md) dokumentiert Installation und Eingaben, die [Offline-Tests](tests/test_core.py) prüfen Kern- und Fehlerpfade.

**Implementiert:** Markt-/Sprachtrennung und sprachübergreifende Suchbegriffe; ein gebündelter HTTPS-Adapter zur **bestehenden** FruitStack-Angebotssuche; echte optionale Awin-Publisher-Programmabfrage, regionale Promotions und begrenzt durchsuchte Enhanced-Produktfeeds; Awin-Linkerzeugung und Transaktionslesung bei vorhandenen Credentials; Entwurfserstellung mit lokalisierter Werbekennzeichnung; Fallback auf vergleichbar geeignete Händlerangebote; optionale HTTPS-Bridge zu einem bestehenden Publisher; externe Antwort-ID als Veröffentlichungsbeleg; sowie provisionssichere Deduplizierung und getrennte Zahlungs-/Kostenaggregation. Ein Fehler bei einem Partner stoppt andere Gelegenheiten nicht.

**Nicht nachgewiesen:** bestehende Amazon- oder Awin-Zugangsdaten, tatsächliche FruitStack-Live-Verbindung, Beiträge in realen Foren oder Umsätze. Ein globales Crawling, ein Amazon-Creators-API-Adapter und adaptive Optimierung sind noch **nicht** implementiert. Die Unit-Tests verwenden bewusst Offline-Doubles statt vorgetäuschter Live-Ergebnisse.

Dieses Konzept beschreibt die gewünschte Weiterentwicklung; nicht alle nachfolgenden Fähigkeiten sind schon programmierte Funktionen.

## Update v0.3.0 — Suchabdeckung, Linkqualität und reale Attribution

Der MCP-Kern kann Kaufanfragen **einzeln gegen denselben Awin-Produktfeed** bewerten, ohne Anbieter durch zusammengefügte Suchbegriffe oder ein frühes Kataloglimit zu übersehen. Promotions erhalten begrenzte Pagination und zeigen Teilabdeckung an. Feed-Sprache und Käufermarkt werden nicht künstlich gleichgesetzt.

Die Ausführung verwendet einen schnellen Link-Builder-Pfad, respektiert das vom FruitStack tatsächlich besprochene Produkt und trennt **inhaltsbezogenen `fingerprint`** von der für Wiederholungsversuche stabilen **`publication_key`**. Die bei Awin tatsächlich erzeugte `clickref` wird zur Finanzzuordnung zurückgegeben.

`learn` kann über `attribution_map` bestätigte Provisionen und zuordenbare Kosten je Opportunity auswerten. Fehlende Referenzen werden nicht erfunden, Auszahlungen weiterhin separat ausgewiesen. Ein MCP-v2-Client testet die drei realen Tool-Aufrufe in der CI.

Siehe [Release v0.3.0](docs/RELEASE_0.3.md), [Ausführungsanleitung](docs/QUICKSTART.md) und [MCP-Protokolltests](tests/test_mcp_protocol.py).

## Update v0.4.0 – nur eine minimale Posting-Historie

`find` und `execute` prüfen nun vor kostspieligen Produkt- und Link-Aufrufen, ob dieselbe Forumsdiskussion bereits beantwortet wurde. Gespeichert werden ausschließlich **Thread-Hash, Zeitpunkt, externe Beitrags-ID und technische Kurzzeitfelder zur Doppelpost-Vermeidung**. Keine Forentexte, Profile, Kontakte oder KIGOR-artigen Quellendaten. Eine einzelne bereits beantwortete Diskussion wird zurückgestellt, andere Gelegenheiten laufen weiter.

Die Veröffentlichungskennung basiert auf der normalisierten Thread-Adresse und bleibt auch bei unterschiedlichen Such-IDs stabil. Das Zeitfenster ist konfigurierbar (Standard 180 Tage). Siehe [Minimal-Historie und Tests](docs/POST_HISTORY.md).

**Automatische Forenregistrierung existiert in MelonMe weiterhin nicht.** Weder Account-Erstellung noch Login sind implementiert. Auch die Publisher-Bridge ist noch nicht als reale FruitStack-Live-Verbindung nachgewiesen.

## 1. Auftrag: ein Guerilla-Geschäftsmodell, keine Affiliate-Plattform

MelonMe ist ein **Guerilla-Monetarisierungstool**: Es sucht proaktiv nach konkreten, zeitkritischen Gelegenheiten, die bereits im Netz entstehen, statt eigene Anzeigen zu kaufen, große Kampagnen zu planen oder zunächst Reichweite aufzubauen. Es arbeitet in den Sprachen der jeweiligen Diskussionen und prüft den tatsächlichen Zielmarkt getrennt von der Sprache.

Beispiel: In einem geeigneten Forum fragt jemand nach dem besten Staubsauger für Tierhaare oder nach Alternativen zu bestimmten Kopfhörern. MelonMe erkennt die Frage frühzeitig, ermittelt passende Produkte, zeigt auf Wunsch einen kurzen, brauchbaren Vergleich und kann zulässige, korrekt gekennzeichnete Angebote verlinken. Nicht die Anzahl der Beiträge, sondern der **reale Ertrag nach Kosten** entscheidet, was sich wiederholen lohnt.

**„Guerilla“ schließt nach der Geschäftsabsicht ausdrücklich unaufgeforderte kommerzielle Kontaktaufnahme ein — auch das, was Empfänger oder Plattformen als Spam einstufen.** Diese Absicht wird nicht als rein organische Kaufberatung umetikettiert. Das ist ein erheblicher wirtschaftlicher und plattformbezogener Risikofaktor (Sperrung, Entfernung, entfallende Provisionen), den MelonMe bei der Bewertung berücksichtigen muss. Für die technische Ausführung bleiben die Rechte der konkret angesprochenen Plattform und des Partnerprogramms maßgeblich; Täuschung, Fake-Accounts, fingierte Erfahrungen und Umgehung technischer Schutzmaßnahmen sind keine vorgesehenen Funktionen.

MelonMe deckt **genau dieses eine Geschäftsmodell** ab. Es ist keine neue zentrale FruitStack-Architektur, keine allgemeine Commerce-/Affiliate-SaaS, kein Werbemarktplatz, kein Adserver, kein Publisher-Portal und kein Buy-Side-Ads-Tool. Andere Geschäftsmodelle sind eigene Projekte.

## 2. Drei Funktionen — die ganze fachliche MCP-Oberfläche

### `melonme.find(context)` — Finden und entscheiden

- Erkennt **aktuelle** Kaufberatungsfragen aus zulässig zugänglichen Quellen, priorisiert konkrete Kaufabsicht, Gesprächsrelevanz und Zeitfenster.
- Erkennt Sprache und **Absatz-/Liefermarkt unabhängig voneinander**; nicht aus „Deutsch“ automatisch „Deutschland“ ableiten.
- Fragt vorhandene, tatsächlich zugängliche Angebotsquellen ab (z. B. bereits angebundene Amazon- oder Awin-Funktionen), ohne Vollständigkeit zu behaupten.
- Prüft *konkret*, ob ein Produkt für diesen Markt angeboten wird, ob ein gültiges vergütbares Angebot möglich ist und ob der Zielkanal die beabsichtigte kommerzielle Antwort erlaubt.
- Nutzt günstige Filter und vorhandene Erkenntnisse **vor** teuren Modell- oder Produktrecherchen.
- Liefert priorisierte, belegte Gelegenheiten oder einen klaren lokalen Grund, weshalb es sich jetzt nicht lohnt.

**Keine neue Partner-Registry als eigener Systemkern.** Vorhandene Zugangsdaten und FruitStack-Funktionen werden verwendet. Ein Teilzugang wird für seine **wirklich funktionierenden Fähigkeiten** genutzt; eine fehlende Teilfunktion sperrt nicht den gesamten Anbieter.

### `melonme.execute(opportunity)` — Nützliche Aktion ausführen

- Prüft nur die für **diese konkrete Aktion** notwendigen Rechte und technischen Voraussetzungen.
- Erstellt aus verifizierbaren Produktdaten eine ehrliche, kontextbezogene Antwort in der Sprache der Diskussion; drei Produkte sind ein **mögliches Format**, keine Pflicht.
- Vergleicht Eignung, Nachteile, Kompatibilität, Preis, Verfügbarkeit und gegebenenfalls Folgekosten. Provisionen dürfen fachlich ungeeignete Produkte nicht bevorzugen.
- Fügt vergütete Links **nur dann** ein, wenn der konkrete Affiliate-Zugang und die beabsichtigte Veröffentlichung diese Nutzung erlauben; kommerzielle Beziehungen werden deutlich gekennzeichnet.
- Veröffentlicht über eine nachweislich autorisierte Schnittstelle; wo eine Freigabe erforderlich oder die Erlaubnis ungeklärt ist, liefert es stattdessen einen verwendbaren Entwurf, **ohne** die Publikation zu erzwingen.
- Meldet die echte externe Antwort-ID bzw. einen belegten Ausführungsstatus; ein internes „Tool erfolgreich“ ist kein Beweis der Veröffentlichung.

**Kein allgemeiner Foren-Stopp.** Ist ein Forum ausdrücklich ungeeignet, wird nur **diese Aktion an diesem Ort** nicht veröffentlicht; andere legale Kanäle bleiben nutzbar. Kein systemweiter Abbruch wegen einer einzelnen Frage, Community oder Händleranbindung.

### `melonme.learn(results)` — Geld messen, Entscheidungen verbessern

- Übernimmt zulässig verfügbare Klick-/Transaktionsberichte sowie **bestätigte Provisionen, Stornos, Auszahlungen und tatsächlich verursachte Kosten**.
- Unterscheidet strikt Prognose, Klick, gemeldeten Kauf, freigegebene Provision und Geldzufluss. Unbekannte Attribution bleibt unbekannt.
- Erkennt, welche Kombinationen aus Thema, Sprache, Markt, Kanal, Angebot, Zeitpunkt und Antwortformat **nach Kosten** erfolgreich waren.
- Optimiert zunächst mit einfachen, nachvollziehbaren Regeln; komplexere Lernverfahren werden erst eingesetzt, wenn die Daten das rechtfertigen.
- **NO_ACTION** und der Abbruch einer teuren, wenig aussichtsreichen Recherche sind positive Entscheidungen, wenn sie Kosten sparen.

**Wirtschaftliches Ziel:** bestätigte Erlöse minus zurechenbare Kosten; tatsächlich ausgezahltes Geld wird separat ausgewiesen. Hohe Gewinne sind Ziel, keine erfundene Garantie.

## 3. AVCOS-Fehler nicht wiederholen

Bei AVCOS wurden Anbieter teilweise angebunden, aber ihre Funktionen wurden nicht konsequent real ausprobiert oder verwendet. Fehlende Informationen wurden als fehlende Berechtigung oder fehlendes Angebot interpretiert. Eigene pauschale Foren-Stopps und harte Fehlerbehandlung machten aus lokalen Schwierigkeiten globale Blockaden.

Daraus folgen für MelonMe **nur fünf operative Regeln**:

1. **Versuchen statt behaupten:** Ein Katalogeintrag ist kein funktionsfähiger Zugang. Ein teilweiser Zugang ist aber auch kein vollständiger Ausfall. Wo möglich: realen lesenden Capability-Call mit vorhandenem Konto ausführen und den tatsächlichen Rückgabewert nutzen.
2. **Sprache ≠ Land ≠ Marktplatz:** Produkt, Händler, Liefergebiet, Partnerfreigabe und Trackinglink beziehen sich auf einen **konkreten** Markt. Fehlende Daten nicht erraten.
3. **Lokaler Fehler bleibt lokal:** Kein Treffer bei einem Anbieter → einen anderen vorhandenen, zulässigen Anbieter prüfen. API-Fehler → begrenzt wiederholen oder vorhandene Alternativen nutzen. Verbot in einem Forum → nur dort nicht posten. **Keine unendlichen Retries, kein globaler STOP.**
4. **Unbekannt ≠ verboten ≠ erlaubt:** Unklare Voraussetzungen werden zielgerichtet geklärt. Solange die Veröffentlichung nicht positiv gedeckt ist, wird **nur dieser öffentliche Schreibvorgang** nicht ausgeführt; Recherche, andere Partner und andere Kanäle laufen weiter. Nachgewiesene Verbote werden respektiert, nicht umgangen.
5. **Externe Wirkung zählt:** Wirklich veröffentlichter Beitrag, tatsächlich bestätigte Provision und reale Auszahlung sind getrennte Belege. Keine simulierten Einnahmen oder interne Aktivitätsmetriken als Geschäftserfolg.

**Es gibt keine zusätzliche mehrstufige Partner-Workflow-Engine, kein schweres Zulassungsregister und keinen globalen „alles erst freischalten“-Zwang.** Wenn die konkrete Aktion mit einem vorhandenen Zugang zulässig und ausführbar ist, wird sie nicht durch künstliche Projektmeilensteine blockiert.

## 4. Schlanke Integration in FruitStack

MelonMe ist eine **fachliche MCP-Schnittstelle**, kein eigener Agentenapparat.

- **Intelligenz, Recherche, Orchestrierung, Modellauswahl, Credential-Sicherheit, Betriebsüberwachung und langfristiger Arbeitszustand** bleiben bei den dafür vorgesehenen FruitStack-Komponenten, soweit deren reale Schnittstellen geeignet und geprüft sind.
- MelonMe enthält nur die **drei fachlichen Operationen** und die kleinen Adapter für die konkret benötigten Angebots-, Publikations- und Ergebnisdaten.
- Keine zweite Modellverwaltung, kein eigener universeller Router, kein zweiter systemweiter Ledger, kein paralleler allgemeiner Scheduler und kein dupliziertes Agentenframework.
- Der Dienst muss mit wenigen Aufrufen nutzbar sein. Teure Recherche erfolgt nur, wenn die günstige Vorprüfung einen plausiblen Nutzen ergibt.
- Partnerdaten werden nicht in öffentliche Repositories oder Prompts geschrieben. Vorhandene Secrets bleiben in der zuständigen sicheren Infrastruktur.
- Externe Schreibaktionen müssen zielgenau autorisiert sein und doppelte Beiträge verhindern. Die Sicherheit ist **schmal und konkret**, nicht ein neu erfundenes Verwaltungsprogramm.

**Schnittstellenvertrag (konzeptionell):**
`find` liefert eine kompakte Opportunity mit Quellen-/Marktkontext, tatsächlich gefundenen Angeboten und bekannten Unsicherheiten.  
`execute` liefert `PUBLISHED`, `DRAFT_ONLY`, `NO_ACTION` oder einen **lokalen** Fehler mit überprüfbaren Belegen.  
`learn` liefert einen wirtschaftlichen Ergebnisstand und begründete Verbesserungen der nächsten Auswahl.

Das genaue Schema muss erst gegen die realen FruitStack-Contracts und verfügbaren Partnerfunktionen geprüft werden. Diese README behauptet **keine** bereits erfolgte Integration.

## 5. Guerilla-Betrieb: Tempo, Reichweite, Kosten

MelonMe priorisiert **schnell bearbeitbare, wirtschaftlich hochwertige Gelegenheiten** und bewertet ausdrücklich auch die Risiken unerwünschter kommerzieller Ansprache. Nicht jede Gelegenheit eignet sich für eine Veröffentlichung; wo diese nicht zulässig ist, bleibt Recherche oder Entwurf möglich.

- **Früh sein, aber nicht aufdringlich:** Aktuelle Fragen und echten Informationsbedarf erkennen; abgeschlossene Diskussionen nicht zwecks Werbung neu beleben.
- **Mehrsprachig, marktrichtig:** Eine Sprache kann mehrere Länder betreffen; Angebot, Währung, Lieferung, Partnerstatus und Link müssen wirklich passen.
- **Bestehendes zuerst:** Vorhandene Produktquellen, Partnerzugänge, geprüfte Fakten und FruitStack-Infrastruktur wiederverwenden.
- **Günstiger Erstfilter:** Keine langen Agentenketten für offensichtlich veraltete, wirtschaftlich unattraktive oder nicht nutzbare Gelegenheiten.
- **Zielgerichtete Alternativen:** Fällt eine konkrete Quelle aus, andere zulässige, real erreichbare Quellen prüfen, statt neue Gesamtarchitektur aufzubauen.
- **Qualität vor Affiliate-Bias:** Unbelegte Produktbehauptungen weglassen. Wo angebracht: kurze Einordnung statt aufwendiger Tabelle; keine manipulativ positiven Empfehlungen.
- **Messen statt aufblasen:** Nicht die Zahl der Foren, Publisher-Accounts, Modelle, MCP-Tools oder Posts ist ein Erfolg, sondern ein nachvollziehbarer positiver wirtschaftlicher Beitrag.

Es gibt keine im Voraus behaupteten Erfolgsquoten, zehnfach höheren Widget-Conversions oder fixen Margen einzelner Produktkategorien. Produktgruppen werden anhand realer Kosten und Provisionen verglichen, nicht per Architekturentscheidung vorgeschrieben.

## 6. Kleine Umsetzungsschritte ohne künstliche Blockaden

**Schritt A — Vorhandenes wirklich nutzen.** Tatsächliche FruitStack-Schnittstellen und bereits eingerichtete Amazon-/Awin-/sonstige Partnerzugänge **lesend testen**, Fähigkeiten pro Markt erfassen, reale Antwortwerte prüfen. Unklare, fehlende oder unzulässige Funktionen exakt benennen; parallel verwendbare Funktionen bleiben nutzbar.

**Schritt B — Drei MCP-Funktionen ausführbar machen.** Eine echte Gelegenheit erkennen, ein geeignetes Angebot korrekt recherchieren und einen fachlich geprüften Antwortentwurf erstellen. Mit Testdaten Fehlerfälle, lokale Ausweichpfade, Zeit-/Kostenlimits und `NO_ACTION` prüfen.

**Schritt C — Zulässige reale Aktion.** Wo konkrete Veröffentlichung und Affiliate-Nutzung gestattet sind, eine einzelne freigegebene Antwort ausspielen und den externen Zustand belegen. Andernfalls `DRAFT_ONLY` liefern und an anderen zulässigen Chancen weiterarbeiten. Kein globaler Forenstopp.

**Schritt D — Ergebnis messen und besser entscheiden.** Partnerdaten, bestätigte Provisionen, Kosten und tatsächliche Auszahlungen korrekt zuordnen; einfache wirtschaftliche Auswahlregeln mit realen Ergebnissen verbessern. Erst nach einem belegten Erlöskreislauf Aussagen zur Profitabilität treffen.

Schritte sind Entwicklungsarbeit, **keine globalen Freigabeschleusen** für bereits zugelassene Teilfähigkeiten.

## 7. Definition des Erfolgs

MelonMe ist technisch brauchbar, wenn FruitStack die drei Operationen zuverlässig aufrufen kann; Sprache und Markt korrekt getrennt werden; vorhandene Teilzugänge tatsächlich genutzt werden; ein lokaler Fehlschlag nicht die übrigen Chancen abbricht; kommerzielle Antworten nur in erlaubten Kontexten veröffentlicht werden; und Ausgaben, Ergebnisse und Unsicherheit nachvollziehbar sind.

MelonMe ist **wirtschaftlich erfolgreich**, wenn aus erlaubten realen Empfehlungen bestätigte Provisionen und schließlich Auszahlungen entstehen, die den zurechenbaren Aufwand übersteigen. Jede neue Entscheidung soll mit geringstmöglichen Kosten näher an dieses Ergebnis führen.

**Kernsatz:** *Schnell handeln, wo wir dürfen und tatsächlich können. Lokal ausweichen, wo etwas nicht funktioniert. Lernen, wo reales Geld verdient wird.*

---

**Abgrenzung des Stands:** v0.3.1 ist das Zielbild. Ergänzt wurde ein erster ausführbarer MCP-Kern, noch ohne Live-Partnernachweis, Host-Integration oder Zusage realer Einnahmen. Frühere Konzepte bleiben über Git-Historie nachvollziehbar.
