import logging
import os
from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)

from mcp_obsidian.tools import (
    AppendContentToolHandler,
    BatchGetFileContentsToolHandler,
    ComplexSearchToolHandler,
    DeleteFileToolHandler,
    GetFileContentsToolHandler,
    ListFilesInDirToolHandler,
    ListFilesInVaultToolHandler,
    PatchContentToolHandler,
    PeriodicNotesToolHandler,
    PutContentToolHandler,
    RecentChangesToolHandler,
    RecentPeriodicNotesToolHandler,
    SearchToolHandler,
    ToolHandler,
)

load_dotenv()


# Load environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(
        f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}"
    )

app = Server("mcp-obsidian")

tool_handlers = {}


def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class


def get_tool_handler(name: str) -> ToolHandler | None:
    if name not in tool_handlers:
        return None

    return tool_handlers[name]


add_tool_handler(ListFilesInDirToolHandler())
add_tool_handler(ListFilesInVaultToolHandler())
add_tool_handler(GetFileContentsToolHandler())
add_tool_handler(SearchToolHandler())
add_tool_handler(PatchContentToolHandler())
add_tool_handler(AppendContentToolHandler())
add_tool_handler(PutContentToolHandler())
add_tool_handler(DeleteFileToolHandler())
add_tool_handler(ComplexSearchToolHandler())
add_tool_handler(BatchGetFileContentsToolHandler())
add_tool_handler(PeriodicNotesToolHandler())
add_tool_handler(RecentPeriodicNotesToolHandler())
add_tool_handler(RecentChangesToolHandler())


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available"""

    return [th.get_tool_description() for th in tool_handlers.values()]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""

    if not isinstance(arguments, dict):
        raise RuntimeError("arguments must be dictionary")

    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        return tool_handler.run_tool(arguments)
    except Exception as e:
        logger.error(str(e))
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
