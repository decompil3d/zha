"""Tests for the server and client."""

from __future__ import annotations

import pytest

from tests.conftest import CombinedWebsocketGateways
from zha.application.gateway import WebSocketClientGateway, WebSocketServerGateway
from zha.application.helpers import ZHAData
from zha.websocket.client.client import Client
from zha.websocket.client.helpers import ClientHelper


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

        async with WebSocketClientGateway(zha_data) as client_gateway:
            assert client_gateway.client.connected
            assert client_gateway.client._listen_task is not None

        assert not client_gateway.client.connected
        assert client_gateway.client._listen_task is None

    assert not gateway.is_serving
    assert gateway._ws_server is None


async def test_client_helper_disconnect(
    zha_data: ZHAData,
) -> None:
    """Tests client helper disconnect logic."""

    async with WebSocketServerGateway(zha_data) as gateway:
        assert gateway.is_serving
        assert gateway._ws_server is not None

        client = Client(f"ws://localhost:{zha_data.ws_server_config.port}")
        client_helper = ClientHelper(client)

        await client.connect()
        assert client.connected
        assert "connected" in repr(client)

        # The client does not begin listening immediately
        assert client._listen_task is None
        await client_helper.listen()
        assert client._listen_task is not None

        await client_helper.disconnect()
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
