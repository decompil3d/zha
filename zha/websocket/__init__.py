"""Websocket module for Zigbee Home Automation."""

from __future__ import annotations

from zha.exceptions import ZHAException


class ZHAWebSocketException(ZHAException):
    """Exception raised by websocket errors."""
