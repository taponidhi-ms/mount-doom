"""
Shared module for common single-agent and multi-agent functionality.

This module provides base classes and factory functions that can be
reused across different agent use cases to minimize code duplication.
"""

from .base_single_agent_service import BaseSingleAgentService
from .base_routes import create_single_agent_routes

__all__ = [
    'BaseSingleAgentService',
    'create_single_agent_routes',
]
