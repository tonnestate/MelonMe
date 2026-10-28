"""Test real MCP v2 tool discovery and request dispatch, not just Python imports."""
import unittest

from mcp import Client

from melonme.server import mcp


class McpWireContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_process_mcp_client_calls_all_three_tools(self):
        async with Client(mcp) as client:
            registered = await client.list_tools()
            names = {tool.name for tool in registered.tools}
            self.assertEqual(names, {"find", "execute", "learn"})

            opportunity = {
                "id": "mcp-q-1", "text": "Sport Kopfhörer",
                "market": "AT", "language": "de",
                "offers": [{"title": "Sport Kopfhörer",
                            "market": "AT", "url": "https://shop.example/item"}],
            }
            queries = {
                "questions": [{"id": "mcp-q-1",
                               "text": "Sport Kopfhörer", "market": "AT"}],
                "offers": opportunity["offers"],
            }
            for name, arguments in (
                ("find", {"context": queries}),
                ("execute", {"opportunity": opportunity}),
                ("learn", {"results": {"costs": [{"currency": "EUR", "amount": "0.02"}]}}),
            ):
                result = await client.call_tool(name, arguments=arguments)
                self.assertFalse(result.is_error, f"{name}: {result.content}")
                self.assertTrue(result.content or result.structured_content)
