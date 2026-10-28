"""MCP v2 stdio entry point for MelonMe.

FruitStack supplies questions, offers and its approved publisher bridge.
Never logs credentials, never claims an external publication without a receipt.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from mcp.server import MCPServer

from melonme import core
from melonme.post_history import PostHistory


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


def _inventory_bridge(payload: dict) -> dict:
    endpoint = os.environ.get("MELONME_INVENTORY_BRIDGE_URL", "")
    token = os.environ.get("MELONME_INVENTORY_BRIDGE_TOKEN", "")
    if not endpoint or not token:
        raise core.PartnerError("INVENTORY_BRIDGE_NOT_CONFIGURED")
    response = core._json_request(endpoint, token, payload)
    if not isinstance(response, dict):
        raise core.PartnerError("INVENTORY_RESPONSE_INVALID")
    return response


@lru_cache(maxsize=1)
def _post_history() -> PostHistory:
    # Only this tiny local record is retained: thread hash, time, receipt.
    return PostHistory.from_env()



@mcp.tool()
def find(context: dict[str, Any]) -> dict:
    """Rank purchase-intent questions against factual, market-specific product offers.

    FruitStack provides context.questions[] and context.offers[]. Optional
    probe_awin reads joined Awin programmes using credentials from environment.
    One failure does not stop other questions.
    """
    lookup = _inventory_bridge if os.environ.get("MELONME_INVENTORY_BRIDGE_URL") else None
    try:
        history = _post_history()
    except (ValueError, OSError) as exc:
        # A broken local history must not disable discovery worldwide.
        result = core.find(context, inventory_lookup=lookup)
        result.setdefault("errors", []).append({
            "provider": "post_history", "code": "POST_HISTORY_UNAVAILABLE",
            "error_type": type(exc).__name__})
        return result
    return core.find(context, inventory_lookup=lookup, post_history=history)


@mcp.tool()
def execute(opportunity: dict[str, Any]) -> dict:
    """Create a factual answer draft; optionally publish through FruitStack bridge.

    publish=true only uses an operator-configured HTTPS publisher bridge.
    No bridge -> DRAFT_ONLY. PUBLISHED requires external_id from the bridge.
    """
    connected = bool(os.environ.get("MELONME_PUBLISH_BRIDGE_URL") and
                     os.environ.get("MELONME_PUBLISH_BRIDGE_TOKEN"))
    publisher = _publisher_bridge if opportunity.get("publish") and connected else None
    try:
        history = _post_history() if publisher is not None else None
    except (ValueError, OSError) as exc:
        return {"status": "DRAFT_ONLY", "id": opportunity.get("id"),
                "reason": "POST_HISTORY_UNAVAILABLE", "error_type": type(exc).__name__}
    return core.execute(opportunity, publisher=publisher, post_history=history)


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
