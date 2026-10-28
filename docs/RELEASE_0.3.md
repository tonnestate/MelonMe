# MelonMe v0.3.0 — nachgewiesene Softwareverbesserungen

**Stand:** 28. Oktober 2026. Drei MCP-Tools bleiben unverändert: `find`, `execute`, `learn`.

## Verbesserungen an tatsächlichen Fehlern

1. **Recall:** Mehrere Kaufanfragen werden getrennt gegen denselben Awin-Feed bewertet; der Feed muss nicht pro Anfrage neu geladen werden. Ein zusammengeklebter Suchtext unterdrückt keine Treffer mehr.
2. **Partner-Abdeckung:** Neue Angebote aus FruitStack, Awin-Produktfeeds und Promotions werden nicht mehr von einem früheren 2.000-Einträge-Limit abgeschnitten. Awin-Promotions verwenden eine begrenzte Pagination, deren Teilabdeckung sichtbar ist.
3. **Sprache und Absatzmarkt:** Ein Feed mit `locale=de_DE` kann für eine deutschsprachige Anfrage aus Österreich untersucht werden. Die Ausgabe kennzeichnet, dass Feed-Locale keine Lieferbarkeitszusage darstellt.
4. **Keine ungültigen Produkte:** Auch die in Awins Dokumentation verwendete Schreibweise `out_ouf_stock` wird als nicht verfügbar erkannt. `preorder` oder `backorder` werden nicht pauschal als fehlender Anbieter behandelt.
5. **Schnellere Linkauswahl:** Nach dem ersten passenden Tracking-Erfolg entfallen weitere Link-Builder-Aufrufe. Ein vom FruitStack verfasster Text wird einem tatsächlich erwähnten oder über `answer_offer_id` bezeichneten Produkt zugeordnet.
6. **Idempotenz:** `fingerprint` kennzeichnet den konkreten Text. `publication_key` kennzeichnet stabil die Veröffentlichungszielstelle (Opportunity, Kanal und Quell-URL). Die Publisher-Bridge erhält nur die letztere als `idempotency_key`.
7. **Nachvollziehbare Attribution:** Ein erfolgreich beim Awin-Linkbuilder gesetztes `clickref` wird an FruitStack zurückgegeben. `learn` akzeptiert `attribution_map` und summiert reale genehmigte Provisionen gegen zugeordnete Kosten pro Opportunity.
8. **Finanzwahrheit:** `by_clickref`, `by_opportunity` und `unattributed_transactions` unterscheiden nachgewiesene Zuordnungen von unbekannten. `approved` bleibt von `paid` getrennt; mehrfache Payout-IDs werden pro Anbieter und Währung dedupliziert.
9. **Fehlerisolation:** Fehlerhafte Feed-Eingaben, unzulässige Datumstypen oder ein kaputter Awin-Konfigurationswert beenden die übrige Opportunity-Suche und Finanzverarbeitung nicht.
10. **MCP-Protokoll:** Ein echter MCP-v2-Client führt nun Discovery und Aufrufe aller drei Tools im automatisierten Test aus, statt lediglich Python-Imports zu prüfen.

## Kurzes Host-Beispiel

Nach `execute` die Relation zwischen zurückgeliefertem `clickref` und der Opportunity-ID im **vorhandenen FruitStack-Ledger** festhalten. Beispielhaft liefert `execute`:

```json
{"status":"DRAFT_ONLY","id":"q-44","clickref":"0123456789abcdef01234567","publication_key":"<sha256>","fingerprint":"<sha256>"}
```

Ein späterer `learn`-Aufruf verwendet echte Awin-Transaktionen sowie genau diese vom Host gespeicherte Beziehung:

```json
{
  "transactions": [{"id": 42, "commissionStatus": "approved", "commissionAmount": {"amount": "7.00", "currency": "EUR"}, "clickRefs": {"clickRef": "0123456789abcdef01234567"}}],
  "attribution_map": {"0123456789abcdef01234567": "q-44"},
  "costs": [{"id": "cost-1", "opportunity_id": "q-44", "currency": "EUR", "amount": "2.00"}]
}
```

Das Ergebnis ist eine **belegte** Zuordnung von 7 EUR genehmigter Provision und 2 EUR Kosten. Es ist keine Aussage über tatsächlich ausgezahltes Geld.

## Genaue Grenze

Die Unit- und MCP-Protokolltests verwenden Offline- bzw. in-process-Adapter. Noch nicht nachgewiesen sind reale Zugangsdaten, eine tatsächliche Host-Bridge zum laufenden FruitStack, Amazon-Creators-API-Zugriffe, öffentliche Veröffentlichungen oder Geldzuflüsse. Es wurden keine fremden Konten, Anträge, Rechte oder Verkäufe erfunden.

API-Referenzen:
- https://help.awin.com/apis/apidocs/promotions
- https://help.awin.com/apidocs/retail-publisher-productapidocumentation-1
- https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-publisher
- https://py.sdk.modelcontextprotocol.io/whats-new/
