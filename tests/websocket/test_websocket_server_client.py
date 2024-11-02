"""Tests for the server and client."""

from __future__ import annotations

import pytest

from tests.conftest import CombinedWebsocketGateways
from zha.application.gateway import WebSocketServerGateway
from zha.application.helpers import ZHAData
from zha.application.websocket_api import StopServerCommand
from zha.websocket.client.client import Client


async def test_server_client_connect_disconnect(
    zha_data: ZHAData,
) -> None:
    """Tests basic connect/disconnect logic."""

    async with WebSocketServerGateway(zha_data) as gateway:
        assert gateway.is_serving
        assert gateway._ws_server is not None

        async with Client(f"ws://localhost:{zha_data.ws_server_config.port}") as client:
            assert client.connected
            assert "connected" in repr(client)

            # The client does not begin listening immediately
            assert client._listen_task is None
            await client.listen()
            assert client._listen_task is not None

        # The listen task is automatically stopped when we disconnect
        assert client._listen_task is None
        assert "not connected" in repr(client)
        assert not client.connected

    assert not gateway.is_serving
    assert gateway._ws_server is None


@pytest.mark.parametrize(
    "zha_gateway",
    [
        "ws_gateways",
    ],
    indirect=True,
)
async def test_client_message_id_uniqueness(
    zha_gateway: CombinedWebsocketGateways,
) -> None:
    """Tests that client message IDs are unique."""
    ids = [zha_gateway.client_gateway.client.new_message_id() for _ in range(1000)]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "zha_gateway",
    [
        "ws_gateways",
    ],
    indirect=True,
)
async def test_client_stop_server(
    zha_gateway: CombinedWebsocketGateways,
) -> None:
    """Tests that the client can stop the server."""
    controller = zha_gateway.client_gateway
    gateway = zha_gateway.ws_gateway

    assert gateway.is_serving
    await controller.client.async_send_command_no_wait(StopServerCommand())
    await controller.disconnect()
    await gateway.wait_closed()
    assert not gateway.is_serving
