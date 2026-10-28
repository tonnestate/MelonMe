"""MCP v2 stdio entry point for MelonMe.

FruitStack supplies questions, offers and its approved publisher bridge.
Never logs credentials, never claims an external publication without a receipt.
"""
from __future__ import annotations

import os
from typing import Any

from mcp.server import MCPServer

from melonme import core


mcp = MCPServer("MelonMe")


def _publisher_bridge(payload: dict) -> dict:
    endpoint = os.environ.get("MELONME_PUBLISH_BRIDGE_URL", "")
    token = os.environ.get("MELONME_PUBLISH_BRIDGE_TOKEN", "")
    if not endpoint or not token:
        raise core.PartnerError("PUBLISH_BRIDGE_NOT_CONFIGURED")
    receipt = core._json_request(endpoint, token, payload)
    if not isinstance(receipt, dict):
        raise core.PartnerError("INVALID_PUBLISH_RECEIPT")
    return receipt


@mcp.tool()
def find(context: dict[str, Any]) -> dict:
    """Rank purchase-intent questions against factual, market-specific product offers.

    FruitStack provides context.questions[] and context.offers[]. Optional
    probe_awin reads joined Awin programmes using credentials from environment.
    One failure does not stop other questions.
    """
    return core.find(context)


@mcp.tool()
def execute(opportunity: dict[str, Any]) -> dict:
    """Create a factual answer draft; optionally publish through FruitStack bridge.

    publish=true only uses an operator-configured HTTPS publisher bridge.
    No bridge -> DRAFT_ONLY. PUBLISHED requires external_id from the bridge.
    """
    publisher = _publisher_bridge if opportunity.get("publish") else None
    return core.execute(opportunity, publisher=publisher)


@mcp.tool()
def learn(results: dict[str, Any]) -> dict:
    """Summarize real commissions, payouts and costs, without assuming revenue.

    Optionally reads actual Awin transactions when sync_awin=true and
    start/end are supplied in yyyy-MM-ddTHH:mm:ss format.
    """
    return core.learn(results)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
