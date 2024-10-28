"""Types for the ZHA zigbee module."""

from __future__ import annotations

from typing import TypeVar

from zha.application.gateway import BaseGateway

GatewayType = TypeVar("GatewayType", bound=BaseGateway)
