"""
Shared module for common single-agent and multi-agent functionality.

This module provides base classes and helper functions that can be
reused across different agent features to minimize code duplication.
"""

from .base_single_agent_service import BaseSingleAgentService
from .route_helpers import (
    browse_records,
    delete_records,
    download_records_as_conversations,
    download_records_raw
)

__all__ = [
    'BaseSingleAgentService',
    'browse_records',
    'delete_records',
    'download_records_as_conversations',
    'download_records_raw',
]

