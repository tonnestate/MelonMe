# MelonMe — selbstlernendes Vermittlungsgeschäftsmodell im FruitStack

**Konzept:** v0.2 · **Datum:** 28.10.2026 · **Status:** fachliches Zielbild, keine implementierte Funktion behauptet  
**Repository:** [tonnestate/MelonMe](https://github.com/tonnestate/MelonMe) · **Anbindung:** seitlich an den bestehenden FruitStack über geprüfte Schnittstellen

> **MelonMe ist genau ein Geschäftsmodell — kein neues Betriebssystem.** Das System findet vorhandene, aktuelle Kaufberatungsfragen, erstellt bei Bedarf nachprüfbar hilfreiche Produkt- und Angebotsvergleiche, vermittelt ausschließlich auf erlaubten Kanälen mit aktiv freigegebenen Partnerzugängen und lernt aus **tatsächlich nachgewiesenen wirtschaftlichen Ergebnissen**. Es kauft keine Werbung ein, ersetzt keine FruitStack-Komponente und wird nicht zur universellen Affiliate-Plattform ausgebaut.

## 1. Ziel, Geschäftsmodell und Systemgrenze

### 1.1 Wirtschaftlicher Zweck

Menschen fragen in unterschiedlichen Sprachen beispielsweise „Welcher Staubsauger eignet sich für Tierhaare?“, „Welche Kopfhörer sind eine sinnvolle Alternative?“ oder „Welche Lösung erfüllt meine konkreten Anforderungen?“. MelonMe erkennt aussichtsreiche, aktuelle Fragen in **zulässig nutzbaren Quellen**, ermittelt fachlich geeignete Produkte und verfasst passende, ehrliche Antworten. Wo sowohl Community- als auch Partnerbedingungen es erlauben, kann die Antwort vergütete Angebote enthalten. Die eigentliche Leistung ist die Beratung am vorhandenen Bedarf; die Provision ist eine mögliche Folge.

**Fachliche Wertschöpfungskette:** `DEMAND → QUALIFY → ELIGIBILITY → RESEARCH → COMPARE → AUTHORIZED_PUBLISH → ATTRIBUTION → COMMISSION → LEARN`.

MelonMe entwickelt **nicht** neue, unabhängige Geschäftsmodelle, sondern optimiert ausschließlich diese Vermittlungsform: Welche Art vorhandener Anfrage lohnt die Bearbeitung, welche fachlich geeignete Empfehlung hilft, wo ist ihre Veröffentlichung zulässig, und wie sieht das tatsächliche Ergebnis aus?

### 1.2 Verbindliche Nichtziele

- Keine neue zentrale Commerce-, Affiliate-, Revenue-, Werbe- oder Marketing-Infrastruktur für den gesamten FruitStack.
- Keine zentrale Orchestrierung oder zweite allgemeine KI-/Modell-, Gedächtnis-, Governance-, Projekt-, Kosten- oder Lernplattform.
- Keine TonnEstate-spezifische Werbefunktion, keine Advertising-Agentur, keine eigenen Paid-Ads-Kampagnen.
- Kein unaufgeforderter Massenspam, keine automatischen Beiträge auf nicht freigegebenen Plattformen, keine gefälschten Erfahrungen, Bewertungen oder Identitäten.
- Kein eigenständiges SaaS-/White-Label-Geschäft, kein AdCP-/Prebid-Werbemarktplatz und kein Aufbau einer eigenen Community als automatische Projekterweiterung.
- Keine unbewiesene Annahme, dass ein vorhandener Affiliate-MCP bereits einen autorisierten, monetarisierbaren Vertriebskanal darstellt.

Eigene oder partnerschaftliche Veröffentlichungsflächen sind **mögliche zulässige Kanäle** innerhalb einer ausdrücklich beschlossenen Strategie, kein impliziter Auftrag, Websites, Newsletter oder Portale zu bauen.

### 1.3 Seitlicher FruitStack-Vertrag

FruitStack bleibt Herr über Rollen, Aufträge, Modelle, Budgets, Ausführung, Sicherheitsgrenzen und kanonische Arbeitsnachweise. MelonMe nimmt einen begrenzten Auftrag entgegen, liefert fachlich nachvollziehbare Zustände, externe Belege und wirtschaftliche Ergebnisse zurück und nutzt vorhandene Dienste, soweit ihre Verträge **tatsächlich** geprüft wurden.

Aus den dokumentierten Aufgaben der bestehenden Repositories ergeben sich mögliche Wiederverwendungsfelder: CherryMe für quellenbasierte Verifikation, PlumMe für kostenbewusste Modellversorgung, PeachMe für Sitzungs-/Ausführungskontrollen, MangoMe für dauerhafte Arbeit und Evidenz, OrangeMe für Projektanbindung und AppleMe für Assurance. **Keine dieser Schnittstellen wird hier als bereits erfolgreich mit MelonMe integriert dargestellt.**

Insbesondere darf MelonMe **keinen** zweiten allgemeinen Router, Ledger, Claim-Store oder Agenten-Harness etablieren. Fachliche Partner- und Transaktionsbelege gehören in eine schmale, mit dem bestehenden System kompatible Projektion; eine zweite Autorität für FruitStack-Projektzustände ist ausgeschlossen. Dieses öffentliche Dokument enthält bewusst keine privaten Implementierungsdetails anderer FruitStack-Repositories.

## 2. Zentrale AVCOS-Lehre: Partnerzugänge sind ein echtes Betriebsproblem

Bei AVCOS waren Affiliate-/Partnerzugänge nur teilweise organisiert: Bewerbungen, Freischaltungen, Zugangsdaten, Programme, erlaubte Kanäle und Reporting waren teils unklar oder schlecht dokumentiert. Eine Integration auf dem Papier ist damit wirtschaftlich wertlos. MelonMe darf diesen Fehler **nicht wiederholen**.

### 2.1 Eine kleine fachliche Partner-/Capability-Registry — keine neue Plattform

Pro **konkreter Kombination** aus Partnerprogramm, Advertiser, Land, Affiliate-Konto, genehmigter Publisher-Eigenschaft beziehungsweise Domain, erlaubtem Kanal und Provisionsmodell sind folgende Nachweise nötig:

| Feld | Verbindliche Bedeutung |
| --- | --- |
| `PARTNER_ID`, `PROGRAM_ID`, `MARKET` | Eindeutige Partner-, Programm- und Länderzuordnung |
| `APPLICATION_STATUS` | Beantragung, Prüfung, Ablehnung, Freigabe und letzter nachgewiesener Stand |
| `CONTRACTUALLY_PERMITTED` | Explizit erlaubte Publikationsorte, Inhalte, KI-Nutzung und Affiliate-Link-Formate |
| `API_AVAILABILITY` | Welche Recherche-, Link-, Reporting- und Transaktionsschnittstellen sind **real** verfügbar? |
| `CREDENTIAL_REF` | Nur eine sichere Referenz auf vorhandene Credentials, niemals Klartext im Repository oder Agentenprompt |
| `ACCOUNT_PERMISSIONS` | Tatsächlich freigeschaltete Rechte; ein gültiges Login bedeutet nicht automatisch Programmfreigabe |
| `COMMISSION_MODEL` | Provisionsart, Qualifizierung, Storno-/Auszahlungsregeln, Länder-/Produktbeschränkungen |
| `ATTRIBUTION` | Erlaubte Sub-IDs, Trackingfenster, Last-Click-/Code-Regeln, verwendbare Reports |
| `HEALTH` | Letzter authentifizierter Probeabruf, Fehlerklassifikation, Zeitstempel, Nachweis |
| `EVIDENCE` | Vertrag/Programmbedingungen, Genehmigungsnachricht, konkrete Quelle, Version und Gültigkeitsdatum |

Reine Katalogeinträge, ein öffentliches GitHub-Repository, eine dokumentierte API oder ein gespeicherter Schlüssel beweisen **keine** operative Nutzbarkeit.

**Nachweisleiter:** `DEFINED ≠ AVAILABLE ≠ AUTHORIZED ≠ VERIFIED ≠ PROFITABLE`.

### 2.2 Verbindlicher Zugangslifecycle

`DISCOVERED → APPLICATION_REQUIRED → APPLICATION_SUBMITTED → PENDING_APPROVAL → APPROVED → CREDENTIAL_AVAILABLE → VERIFIED_OPERATIONAL`

Aus jedem Stadium können abweichende Zustände entstehen: `WAITING_FOR_CREDENTIAL`, `LEGAL_REVIEW_REQUIRED`, `ACCESS_FAILED`, `REJECTED`, `SUSPENDED`, `EXPIRED`, `REVOKED`.

Die Zustände werden anhand **externer Belege** gesetzt, nicht aus KI-Vermutungen. `APPROVED` ist ohne nutzbaren Zugang noch **nicht** `VERIFIED_OPERATIONAL`. Ein erfolgreicher API-Aufruf ist ohne Freigabe des konkreten Werbekanals noch **nicht** publikationsfähig. Partner- und Werbekanalberechtigung müssen getrennt nachgewiesen werden.

### 2.3 Umgang mit unvollständigen oder gescheiterten Zugängen

- Die KI darf Zulassungsanforderungen, Vertragsklauseln, Bewerbungsformulare und Dokumentationslücken recherchieren sowie einen vollständigen **Antragsentwurf** vorbereiten.
- Kontoeröffnung, Identitätsprüfung, Vertragsannahme und die Offenlegung erforderlicher geschäftlicher Angaben unterliegen den tatsächlichen Berechtigungen und gegebenenfalls menschlicher Freigabe. Keine erfundenen Firmen-, Domain- oder Traffic-Angaben.
- Fehlende Secrets führen zu **WAITING_FOR_CREDENTIAL**, fehlende Programmgenehmigung zu einem gesonderten Freigabestatus; technische Fehler erhalten nachvollziehbare Ursachen und begrenzte Wiederholungsversuche.
- Nach einem Fehlschlag: **Diagnose → fehlende Nachweise beschaffen → regulär erneut prüfen → gegebenenfalls anderen rechtmäßigen Partner suchen**. Kein stillschweigendes Umschalten auf nicht genehmigte Accounts, andere Identitäten, unerlaubte Kanäle oder Trackingumgehungen.
- Der fehlgeschlagene **Mechanismus** wird vorläufig blockiert, nicht das gesamte Geschäftsmodell verworfen.
- Vor jeder realen Veröffentlichung wird geprüft, ob der spezifische Partnerzugang noch aktiv, vertragskonform und für den Zielkanal freigegeben ist.
- Zugänge werden mit Fristen und Zuständigkeit dokumentiert; niemand muss den Zustand aus verstreuten Chats, Screenshots oder E-Mails erraten.

Dies ist die minimale, geschäftsnotwendige Zugangsverwaltung von **MelonMe**, keine allgemeine FruitStack- oder Affiliate-Account-Plattform.

## 3. Zulässigkeit: Doppeltes Gate vor jeder kommerziellen Aktion

Jeder externe Vorgang benötigt zwei voneinander unabhängige positive Ergebnisse:

**Distribution Gate:** Darf MelonMe in der konkreten Community mit diesem Konto, dieser Art von KI-Unterstützung, dieser Kennzeichnung und dieser Beitragsform tätig werden?

**Monetization Gate:** Ist das konkrete Partnerprogramm für das Land, den Publisher, die Domain, die Inhaltsart und diesen Trackinglink **nachweislich** genehmigt, aktiv und abrechenbar?

Daneben gelten Datennutzungsrechte, Urheberrecht, Datenschutz, plattform- und länderspezifische Werbungsvorschriften sowie lokale Moderationsvorgaben.

Beide Gates verwenden `ALLOW / DENY / UNKNOWN`, Beleg, Prüfdatum, Ablaufdatum und klaren Grund. `UNKNOWN` ist eine **Recherche- oder Klärungsaufgabe**, keine pauschale endgültige Verurteilung. Für externe Veröffentlichung gilt aber immer **fail closed**: nur ein belegtes `ALLOW` erlaubt die betroffene Aktion. Eine hohe erwartete Provision darf die Regel nicht überstimmen.

Wenn Partnerlinks nicht erlaubt sind, kann eine **nicht monetarisierte** sachliche Antwort nur dann als separate Handlung betrachtet werden, wenn **diese Handlung** ausdrücklich zulässig, hilfreich und autorisiert ist. Beiträge werden nicht als verdeckte Werbung getarnt.

## 4. Der begrenzte End-to-End-Prozess

### 4.1 Opportunity Discovery — proaktiv, nicht blind

MelonMe erkennt aktuelle, relevante Kaufberatungsfragen in legal nutzbaren Quellen und Sprachen. Erfasst werden mindestens Thread-/Quellen-ID, Zeitpunkt, Sprache, relevanter Bedarf, Diskussionsstand und Nachweis der Datennutzbarkeit. Deduplikation verhindert dieselbe Bearbeitung mehrfach. Alte abgeschlossene Threads sind keine automatisch geeigneten Veröffentlichungsziele.

**Günstig zuerst:** Regeln, Aktualität, Kaufabsicht und potenzieller Nutzen werden vor tiefem Produktscraping oder teuren Modellketten geprüft. Keine erfundene Quote wie „nur 3–5 %“: Die tatsächliche geeignete Teilmenge wird gemessen.

### 4.2 Qualified Opportunity — erste wirtschaftliche Bewertung

MelonMe prüft, ob ein möglicher legaler Kanal, ein nutzbarer Partner und ausreichend belastbare Produktinformationen überhaupt existieren. Die Bearbeitung kann in `NO_ACTION`, `RESEARCH_MORE`, `WAITING_FOR_PERMISSION`, `WAITING_FOR_CREDENTIAL` oder `READY_TO_DRAFT` enden.

Ein fehlender Zugang ist ein **konkreter Blocker**, nicht eine Aufforderung, dennoch eine „monetarisierte“ Antwort zu simulieren.

### 4.3 Independent Product Intelligence

MelonMe prüft Produkte unabhängig von der Provisionshöhe auf Eignung, echte Unterschiede, Kompatibilität, relevante Nachteile, längerfristige Kosten und Herkunft der Daten. Produktidentitäten und Händlerangebote werden getrennt; dieselbe Ware bei drei Shops ist **nicht** automatisch ein Vergleich dreier Produkte.

Preis, Währung, Verfügbarkeit, Versandland und Abrufzeitpunkt müssen aus legitim nutzbaren, ausreichend aktuellen Quellen stammen. Es gibt keine erfundenen Echtzeitpreise. Jede publizierte technische Behauptung benötigt einen nachprüfbaren Beleg; Unbelegtes wird weggelassen oder ausdrücklich als unbekannt markiert. Weder gekaufte Tests noch eigene Nutzung werden vorgetäuscht.

Es gibt **keine feste Anzahl** zu empfehlender Produkte. Vergütung wird erst nach nachgewiesener fachlicher Eignung berücksichtigt.

### 4.4 Answer & Review

Die Antwort behandelt die konkrete Frage in ihrer Sprache, mit passenden Trade-offs und verständlicher Werbekennzeichnung. Die Form kann ein kurzer Vergleich, eine klar begründete Empfehlung, eine Rückfrage oder — wo zulässig und sinnvoll — eine Antwort ohne Link sein.

Vor jeder Veröffentlichung: Faktenprüfung, Linkprüfung, Antwortnützlichkeit, Plattform- und Partnerrecht, Aktualität, Offenlegung und konkrete Aktionsfreigabe. Initial ist eine menschliche Einzelgenehmigung erforderlich. Spätere eng begrenzte Autopublikation ist nur nach gesondert belegter Betreiberberechtigung und definierter Freigabe möglich.

### 4.5 Publish & Verify

Nur berechtigte Schreibschnittstellen; kein Umgehen von Moderation, CAPTCHA, Limits oder Plattformverboten. Aufträge nutzen Ziel-ID, Entwurfs-Hash, Freigabe, Idempotency Key und externe Antwort-ID. Erfolg bedeutet erst **extern nachgewiesene** Veröffentlichung, nicht nur ein erfolgreiches internes Tool-Ergebnis. Entfernte Beiträge, Änderungsbedarf und Beschwerden werden als Qualitätsereignisse erfasst.

### 4.6 Reconcile & Learn

Erfasst werden nur rechtmäßig verfügbare Impressionen/Klicks, Partnertransaktionen, offene Provisionen, bestätigte Provisionen, Stornos und **tatsächliche Auszahlungen** sowie verursachte Kosten. Unbekannte Attribution bleibt `UNKNOWN`; verzögerte Transaktionen werden nicht zu voreilig negativem Training.

MelonMe optimiert **nur seine eigenen fachlichen Entscheidungen**. Es darf nicht das übergreifende Modell- oder Agentenmanagement des FruitStacks übernehmen.

## 5. Wirtschaftliche Steuerung ohne Scheingewinne

**Operative Kennzahlen:** geprüfte Gelegenheiten, erteilte Publikationsrechte, aktive Partnerzugänge, autorisierte Veröffentlichungen, nicht publizierte Fälle, bestätigte Provisionsereignisse, Auszahlungen, abgebrochene Vorgänge und tatsächlich zugerechnete Kosten.

**Bestätigter Deckungsbeitrag:** bestätigte provisionsfähige Erlöse abzüglich zurechenbarer variabler Kosten; Stornos werden später nachvollziehbar korrigiert.  
**Realisierter Zahlungszufluss:** ausgezahlte Provisionen abzüglich bezahlter zuordenbarer Kosten, mit offener zeitlicher Abgrenzung.  
**Erwartungswert:** nur als unsichere Schätzung für künftige Entscheidungen gekennzeichnet, niemals als gebuchter Umsatz.

Kosten umfassen unter anderem Suche, Produktdaten, Modelle, Prüfschritte, APIs, Freigaben und Betrieb. Vertiefende Recherchen erhalten harte Budgets. Wenn das prognostizierte Erlöspotenzial die zusätzlichen Kosten nicht plausibel deckt, ist `NO_ACTION` eine erfolgreiche Sparentscheidung.

Hohe Preise, SaaS- oder B2B-Produkte sind keine bevorzugten Vertikale per Beschluss. MelonMe darf sie als Varianten **innerhalb desselben Vermittlungsmodells** vergleichen. Conversion, Provisionsfreigabe, Stornos, Auszahlungsdauer und Vollkosten entscheiden. Wiederkehrende Provisionen zählen nur, wenn tatsächlich vertraglich zugesagt.

**Trennung der Stufen:** `DISCOVERED ≠ ELIGIBLE ≠ PUBLISHED ≠ CLICKED ≠ COMMISSION_APPROVED ≠ PAID`. Weder eine simulierte Conversion noch ein bloßer Klick dürfen als wirtschaftlicher Erfolg bilanziert werden.

## 6. Lernen: messbare Entscheidungen unter festen Grenzen

MelonMe soll eigenständig herausfinden, welche Kombinationen aus Bedarf, Sprache, Kanal, Aktualität, Produktkategorie und Antwortformat nach Kosten wirtschaftlich lohnen. Die Regelprüfung ist **kein optimierbarer Reward**, sondern eine unveränderliche Zulässigkeitsbedingung.

1. **Shadow Mode:** zulässige Datenquellen prüfen, Chancen entdecken, hypothetische Antworten/Recherchekosten messen, keine externen Posts und kein vorgetäuschter Conversion-Nachweis.
2. **Kontrollierte reale Versuche:** nur aktive Partner, genehmigte Communities, verifizierte externe Antwort-IDs und begrenzte Kosten.
3. **Reconciliation:** verfügbare Partnerergebnisse einschließlich Verzögerung, Storno, unbekannter Attribution und tatsächlicher Auszahlung.
4. **Adaptive Auswahl:** zunächst nachvollziehbare Heuristiken, später Contextual Bandits nur mit ausreichend Daten, protokollierten Entscheidungswahrscheinlichkeiten und seriöser Evaluation.
5. **Skalierung:** erst bei belegter legaler Handlungsfähigkeit, nachgewiesenen Einnahmen und aussagekräftigen Kosten-/Qualitätsdaten.

Die KI darf weder wegen eines gesperrten Partners die Rechte umgehen noch anhand einzelner zufälliger Verkäufe andere Märkte vorschnell ausschließen. Nicht einmal eine große Shadow-Mode-Stichprobe beweist ohne reale Ausspielung echte Conversion-Raten.

## 7. Technische Schnittstelle — klein und austauschbar

### 7.1 Fachliche MCP-Oberfläche (Vorschlag, nicht implementiert)

| Operation | Fachlicher Zweck |
| --- | --- |
| `discover` | Geeignete aktuelle Kaufberatungsgelegenheiten aus erlaubten Quellen erkennen |
| `qualify` | Aktualität, Bedarf, grobe Wirtschaftlichkeit und vorhandene Berechtigungen prüfen |
| `partner_access_status` | Tatsächlichen Freischaltungs-, Credential-, Vertrags- und API-Zustand nachweisen |
| `research_products` | Geeignete Produkte, aktuelle Angebote und Quellen ermitteln |
| `prepare_answer` | Fachlich begründeten, transparenten Entwurf erstellen |
| `check_publication` | Distributions- und Monetarisierungs-Gates für die konkrete Aktion erneut prüfen |
| `publish_approved` | Ausschließlich freigegebenen, überprüften Beitrag über den erlaubten Adapter senden |
| `reconcile_commissions` | Partnerbelege, Stornos, Provisionen und Auszahlungen abgleichen |
| `evaluate_outcomes` | Nettoertrag, Qualitätsrisiken und Lernsignale auswerten |
| `stop` | Neue Veröffentlichungen sofort blockieren |

MCP ist eine **Schnittstelle**, kein zweites Denk- oder Orchestrierungssystem. Verantwortlichkeiten, Schnittstellenversionen, Berechtigungen und tatsächliche Host-Kompatibilität sind vor Implementierung in den betreffenden FruitStack-Repositories zu prüfen.

### 7.2 Daten- und Fehlerzustände

Jede Gelegenheit besitzt eine fachliche ID, Quellreferenz, aktuelle Zulässigkeitsbelege, Produktquellen, unveränderliche Entwurfsversion, Freigabe, Veröffentlichungsreferenz, verknüpfbare Partner-Trackingkennung (sofern erlaubt) und spätere ökonomische Ereignisse.

Eine externe Wirkung ist erst nach Rücklese-/Partnerbeleg **VERIFIED**. Scheitert ein Aufruf, lautet der Zustand nicht automatisch Erfolg oder vollständiger Geschäftsabbruch, sondern beispielsweise `EXTERNAL_OUTCOME_UNKNOWN`, `WAITING_FOR_CREDENTIAL`, `POLICY_DENIED` oder `PARTNER_REPORT_DELAYED`. Reconciliation muss idempotent sein.

## 8. Donoren: Wiederverwendung nur für konkrete Lücken

**Grundsatz:** Kein fremdes Framework wird zur Hauptarchitektur von MelonMe. Donoren werden einzeln gegen Aufgaben, Reife, Lizenz, Betriebskosten, Datennutzungsrechte und vorhandene FruitStack-Funktionen geprüft.

| Donor/Quelle | Höchstens vorgesehener Zweck | Voraussetzung |
| --- | --- | --- |
| eBay Partner Network / eBay APIs | Angebote und nachweisbare Partner-/Transaktionsdaten | Individuell zugelassener Publisher, Kanal, Markt und Tracking |
| Sovrn Commerce MCP | Potenziell Produkt-, Link- und Transaktionszugang | Tatsächlicher Account, Freigabe, Bedingungen und belastbarer Probeabruf |
| impact.com MCP | Partnerprogramm-/Reportingzugang | Verfügbarer Account, passende Rolle und explizit zugelassene Nutzung |
| Awin/andere Partnerprogramme | Weitere geeignete Partner, soweit real nutzbar | Freischaltung, erlaubte Quellen und Provisionsmessung |
| Discourse API / erlaubte Foren-APIs | Autorisierte Discovery und Veröffentlichung | **Instanz-/Community-spezifische** ausdrückliche Rechte |
| RSSHub / SearXNG | Preiswerte Suche in erlaubten Quellen | Datennutzung und Lizenz-/Betriebsprüfung; keine automatischen Publikationsrechte |
| PriceBuddy/Produktdatenanbieter | Nur konkret benötigte Produkt-/Preisprüfung | Datenrecht, Verfügbarkeit, Lizenz und Datenqualität |
| Contextual-Bandit-Bibliotheken | Spätere, fachlich begrenzte Optimierung | Genügend belastbare Ergebnisse; kein neues systemweites Lernframework |

Adspirer, Claude Ads, Prebid, Revive, White-Label-Affiliate-SaaS, allgemeine Revenue-Plattformen und universelle Agentenframeworks sind **nicht Bestandteil des kritischen Pfads**. Ihre Existenz ist kein Grund, MelonMes Scope auszuweiten.

**Donor-Nachweis:** Herkunft, genaue Version/Commit, Lizenz, Sicherheits- und Wartungsstatus, tatsächlich getestete Funktion, Abhängigkeiten und letzte erfolgreiche Integration. Vorher ist ein Donor nur ein **Kandidat**, keine vorhandene Funktion.

## 9. Governance, Sicherheit und Veröffentlichung

- **Default deny** bei fehlenden oder ungeklärten Plattform- und Partnerrechten. Unklare Regeln werden aktiv recherchiert, nicht geraten.
- Kein Account-Farming, keine gekauften/vorgealterten Konten, keine Identitätsumgehung und kein Missbrauch von Affiliate-Attribution, Coupons, Cookies oder Multi-Accounts.
- Nur wahrheitsgemäße Kontodaten und notwendige Einwilligungen; niemals falsche eigene Produkterfahrungen oder fingierte unabhängige Empfehlungen.
- Werbung beziehungsweise Provisionen sind deutlich in der Sprache der Antwort und gemäß den lokalen Vorschriften zu kennzeichnen.
- Kein verstecktes Tracking. Datenschutz, Urheberrechte, Regeln des Forums und Programmbedingungen gelten nebeneinander.
- Menschliche Freigabe vor den ersten externen Veröffentlichungen; spätere eng begrenzte Autonomie nur nach separater Autorisierung.
- Verbindliche Ausgabenobergrenzen und Stop-Funktion. Ein entzogenes Programmrecht, geänderter Forenstatus oder fehlendes Tracking kann die betroffene Aktion sofort deaktivieren.
- Für kritische Produktbehauptungen und Partnerrechte ist überprüfbare Evidenz erforderlich; KI-Urteile allein reichen nicht.

## 10. Entwicklungs- und Evidenzstufen

### M0 — Grenzen und reale Zugänge nachweisen

**Ergebnis:** nachgeprüfte FruitStack-Schnittstellen; Donor-Kandidatenmatrix; mindestens ein konkret untersuchter zulässiger Veröffentlichungskanal und mindestens ein konkret untersuchtes Affiliate-Programm mit dokumentiertem Zugangsstatus. Noch nicht freigegebene Accounts sind als solche ausgewiesen; keine erfundenen Berechtigungen. Definiert sind Kostenbudget, Erfolgskriterien und Zuordnungsweg von Partnerereignissen.

**Abnahme:** jede geplante externe Operation ist einer belegten technischen, vertraglichen und fachlichen Voraussetzung zugeordnet. **Ein bloßer Partnerkatalogeintrag reicht nicht.**

### M1 — Shadow Mode mit echten Opportunitäten

**Ergebnis:** real zulässig gesammelte Fragen werden dedupliziert, klassifiziert und intern zu sachlich geprüften Vergleichen verarbeitet. Kosten, Blocker, Fehler und benötigte Freigaben werden gemessen. Keine echte Veröffentlichung, keine fingierte Provision. Anzahl der Fälle anhand von Varianz und Untersuchungsziel festlegen; keine willkürliche Stichprobenzahl als Profitabilitätsbeweis.

**Abnahme:** vollständiger Prüfpfad, überprüfbare Kosten und explizite `NO_ACTION`-, `WAITING_FOR_CREDENTIAL`- und `POLICY_DENIED`-Resultate.

### M2 — Erste autorisierte externe Veröffentlichung

**Voraussetzung:** konkret nachgewiesene Publikations- und Partnerrechte sowie eine freigegebene Antwort. Eigene Testflächen belegen allein Technik, nicht externe Nachfrage.

**Abnahme:** tatsächliche externe Antwort-ID, Beleg der Anzeige und Kennzeichnung, keine Doppelveröffentlichung, sofortige Stop-Funktion.

### M3 — Erster nachgewiesener Provisionskreislauf

**Ergebnis:** Partnerreport wird zu einer autorisierten MelonMe-Aktion abgeglichen; Provision, eventuelle Stornos und tatsächlicher Zahlungseingang werden unterschieden.

**Abnahme:** ein vollständig nachweisbarer Ablauf bis zur **bestätigten** Provision und nach Auszahlung zum Zahlungsabgleich. Bei Null-Umsatz oder unbekanntem Partnerstatus wird genau das berichtet.

### M4 — Belastbare Wirtschaftlichkeit und selbstlernende Auswahl

**Ergebnis:** MelonMe nutzt echte Ergebnisdaten, hält Kostenlimits ein und lernt innerhalb der fachlichen Grenzen. Statistisch unzureichende Resultate werden nicht als profitable Strategie ausgegeben.

**Abnahme:** reproduzierbare Auswertung von Kosten, Qualität, Programmlaufzeiten, Verzögerungen, Erträgen und NO_ACTION-Entscheidungen.

### M5 — Geprüfte Übertragbarkeit

Weitere Sprachen, Produktbereiche und **ausdrücklich zugelassene** Communities werden als zusätzliche Instanzen **desselben** Geschäftsmodells freigegeben. Kein Ausbau zur plattformweiten Affiliate- oder AdTech-Architektur.

**Abnahme:** unabhängige Berechtigungen und Budgets je Kanal/Partner; nachgewiesener externer Ergebnisabgleich und isolierbare Abschaltung.

## 11. Projektentscheidungen, offene Belege und Definition of Done

### Fest entschieden

1. **MelonMe** ist ein eigenständiges, seitlich angedocktes Geschäftsmodell innerhalb des bestehenden FruitStacks.
2. Es erkennt aktuelle Kaufabsichten, hilft fachlich, vermittelt unter expliziten Rechten und lernt aus verifizierten Ergebnissen.
3. Plattform- **und** Partnerrechte sind getrennte harte Gates.
4. Tatsächlich organisierte und getestete Affiliate-Zugänge sind eine **Voraussetzung**, keine nachträgliche Verwaltungsaufgabe.
5. Kein zweiter allgemeiner FruitStack-Kern, keine Scope-Ausweitung durch Donor-Suche.
6. Externes Ergebnis, genehmigte Provision und Auszahlung sind unterschiedliche Zustände; Prognosen werden nicht als Gewinne ausgegeben.
7. Eine KI darf Research/Antragsvorbereitung unterstützen, aber Rechte, Verträge, Accounts oder Provisionsereignisse nicht erfinden.

### Noch offen und nachzuweisen

- Welche konkret implementierten FruitStack-APIs stehen MelonMe tatsächlich zur Verfügung?
- Welche Affiliate-Accounts und Programme sind schon **wirklich** freigeschaltet, welcher Zugriff fehlt und wer kann ihn rechtmäßig herstellen?
- Welche publizierenden Communities erlauben kommerzielle KI-Unterstützung und Links tatsächlich?
- Welche gültigen Produktdaten und Affiliate-Reports sind für genau diese Kombinationen verfügbar?
- Welche Mindeststichproben und Beobachtungsfenster sind je Partner für sinnvolle Kosten-/Ertragsaussagen nötig?

### Definition of Done

MelonMe ist erst **wirtschaftlich nachgewiesen**, wenn ein klar autorisierter externer Beratungsvorgang mit überprüfbar geeigneten Angeboten, genehmigtem Partnerzugang, korrekt gekennzeichneter Veröffentlichung, nachvollziehbarer Partnertransaktion und korrekt abgeglichenem wirtschaftlichen Ergebnis stattgefunden hat. Echte Auszahlung wird separat nachgewiesen; **Profitabilität** erst anhand tatsächlicher zurechenbarer Kosten und hinreichender Beobachtung behauptet.

Ein erfolgreiches GitHub-Commit, eine bestandene Offline-Demo, ein veröffentlichter Text oder ein registrierter Affiliate-Account erfüllen diese Definition nicht allein.

## 12. Quellen und Gültigkeitsgrenzen

Die folgenden Links sind technische beziehungsweise regelbezogene **Startpunkte für die individuelle Prüfung**, keine Garantie, dass MelonMe eine Plattform dort kommerziell nutzen darf:

- [Model Context Protocol](https://modelcontextprotocol.io/specification/)
- [Discourse API](https://docs.discourse.org/)
- [eBay Developer – Browse API](https://developer.ebay.com/api-docs/buy/static/api-browse.html)
- [Amazon PartnerNet – Programmregeln](https://partnernet.amazon.de/help/operating/policies)
- [Reddit – Spam-Richtlinie](https://support.reddithelp.com/hc/de/articles/360043504051-Spam)
- [Reddit – Data API Terms](https://redditinc.com/de-de/policies/data-api-terms)
- [EU-Kommission – Influencer Legal Hub](https://commission.europa.eu/topics/consumers/consumer-rights-and-complaints/influencer-legal-hub_en)
- [Vowpal Wabbit – Contextual Bandits](https://vowpalwabbit.org/tutorials/contextual_bandits.html)

### Änderungsbilanz v0.1 → v0.2

- Systemgrenze gegenüber FruitStack und AVCOS-Lehren ausdrücklich festgeschrieben.
- **Partnerzugang, Antragsstatus, Credential-Verfügbarkeit, konkrete Rechte und Live-Verifikation** zum eigenständigen fachlichen Gate erhoben.
- `WAITING_FOR_CREDENTIAL`, fehlende Partnerfreigabe und tatsächliche technische Fehler getrennt; Diagnose/Rework statt voreiligem Geschäftsabbruch.
- Klare Trennung von Discovery, Distributionserlaubnis, Partnererlaubnis, externem Ergebnis, Provision und Auszahlung.
- Proaktive, aber kostenbegrenzte Opportunitätssuche und echte unabhängige Produktverifikation aufgenommen.
- M0/M1/M2/M3-Abnahmekriterien so formuliert, dass interne KI-Aktivität **nicht** als realer Geschäftserfolg ausgegeben werden kann.
- B2B-/White-Label-, Publisher- und generische Affiliate-Plattform-Ideen ausdrücklich aus dem MelonMe-Scope herausgehalten.
- Donoren auf austauschbare, konkret erforderliche Fachadapter begrenzt; FruitStack-Funktionen werden nicht doppelt entwickelt.

**Dieses Dokument ist ein Konzept und keine Zusicherung bereits vorhandener Partnerverträge, Accounts, APIs, Berechtigungen, Agentenintegrationen oder Umsätze.**
