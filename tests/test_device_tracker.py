"""Test ZHA Device Tracker."""

import asyncio
import time
from unittest.mock import AsyncMock

import pytest
import zigpy.profiles.zha
from zigpy.zcl.clusters import general

from tests.common import (
    SIG_EP_INPUT,
    SIG_EP_OUTPUT,
    SIG_EP_PROFILE,
    SIG_EP_TYPE,
    create_mock_zigpy_device,
    get_entity,
    join_zigpy_device,
    send_attributes_report,
)
from zha.application import Platform
from zha.application.gateway import Gateway
from zha.application.platforms import WebSocketClientEntity
from zha.application.platforms.device_tracker import SourceType
from zha.application.registries import SMARTTHINGS_ARRIVAL_SENSOR_DEVICE_TYPE


@pytest.mark.parametrize(
    "zha_gateway",
    [
        "zha_gateway",
        "ws_gateways",
    ],
    indirect=True,
)
async def test_device_tracker(
    zha_gateway: Gateway,
) -> None:
    """Test ZHA device tracker platform."""
    zigpy_device_dt = create_mock_zigpy_device(
        zha_gateway,
        {
            1: {
                SIG_EP_INPUT: [
                    general.Basic.cluster_id,
                    general.PowerConfiguration.cluster_id,
                    general.Identify.cluster_id,
                    general.PollControl.cluster_id,
                    general.BinaryInput.cluster_id,
                ],
                SIG_EP_OUTPUT: [general.Identify.cluster_id, general.Ota.cluster_id],
                SIG_EP_TYPE: SMARTTHINGS_ARRIVAL_SENSOR_DEVICE_TYPE,
                SIG_EP_PROFILE: zigpy.profiles.zha.PROFILE_ID,
            }
        },
    )
    zha_device = await join_zigpy_device(zha_gateway, zigpy_device_dt)
    cluster = zigpy_device_dt.endpoints.get(1).power
    entity = get_entity(zha_device, platform=Platform.DEVICE_TRACKER)

    assert entity.state["connected"] is False

    # turn state flip
    await send_attributes_report(
        zha_gateway, cluster, {0x0000: 0, 0x0020: 23, 0x0021: 200, 0x0001: 2}
    )

    if isinstance(entity, WebSocketClientEntity):
        server_entity = get_entity(
            zha_gateway.ws_gateway.devices[zha_device.ieee],
            platform=Platform.DEVICE_TRACKER,
        )
        original_async_update = server_entity.async_update
        server_entity.async_update = AsyncMock(wraps=server_entity.async_update)
        async_update_mock = server_entity.async_update
    else:
        entity.async_update = AsyncMock(wraps=entity.async_update)
        async_update_mock = entity.async_update

    async_update_mock.reset_mock()
    zigpy_device_dt.last_seen = time.time() + 10
    await asyncio.sleep(48)
    await zha_gateway.async_block_till_done()
    assert async_update_mock.await_count == 1

    # this is because of the argspec stuff w/ WS calls... Look for a better solution
    if isinstance(entity, WebSocketClientEntity):
        server_entity.async_update = original_async_update

    assert entity.state["connected"] is True
    assert entity.is_connected is True
    assert entity.source_type == SourceType.ROUTER
    assert entity.battery_level == 100

    # knock it offline by setting last seen in the past
    zigpy_device_dt.last_seen = time.time() - 90
    await entity.async_update()
    await zha_gateway.async_block_till_done()
    assert entity.state["connected"] is False
    assert entity.is_connected is False

    # bring it back
    zigpy_device_dt.last_seen = time.time()
    await entity.async_update()
    await zha_gateway.async_block_till_done()
    assert entity.state["connected"] is True
    assert entity.is_connected is True

    # knock it offline by setting last seen None
    zigpy_device_dt.last_seen = None
    await entity.async_update()
    await zha_gateway.async_block_till_done()
    assert entity.state["connected"] is False
    assert entity.is_connected is False
