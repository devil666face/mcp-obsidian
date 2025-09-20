import asyncio

from mcp_obsidian import server


def main():
    asyncio.run(server.main())


__all__ = ["main", "server"]
