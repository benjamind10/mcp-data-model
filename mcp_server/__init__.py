(
    """
MCP Server Package

This package provides the Model Control Plane (MCP) server API helpers and
convenience exports. It exposes the FastAPI application (in `server`), the
broker functions used to gather tags and build prompts, and common data models
used across the package.

Example:
	from mcp_server import app, get_tags_from_server, OPCUATag

"""
)

from .server import app
from .broker import get_tags_from_server, generate_model_prompt
from .prompt_tools import generate_prompt_from_tags
from .models import OPCUATag, TagSample

__all__ = [
    "app",
    "get_tags_from_server",
    "generate_model_prompt",
    "generate_prompt_from_tags",
    "OPCUATag",
    "TagSample",
]

__version__ = "0.1.0"
__author__ = "Ben Duran"
