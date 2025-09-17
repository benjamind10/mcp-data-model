"""
OPC UA Client Module

This module provides a reusable client class for connecting to and interacting with
multiple OPC UA servers. It enables reading values, browsing nodes, and integration
into the MCP server architecture.
"""

from .client import MCPClient

__all__ = ["MCPClient"]
__version__ = "0.1.0"
__author__ = "Ben Duran"
