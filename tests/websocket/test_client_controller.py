"""Test zha switch."""

import logging
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from zigpy.device import Device as ZigpyDevice
from zigpy.profiles import zha
from zigpy.types.named import EUI64
from zigpy.zcl.clusters import general

from tests.conftest import CombinedWebsocketGateways
from zha.application.discovery import Platform
from zha.application.gateway import (
    DeviceJoinedDeviceInfo,
    DevicePairingStatus,
    RawDeviceInitializedDeviceInfo,
    RawDeviceInitializedEvent,
    WebSocketServerGateway,
)
from zha.application.model import DeviceJoinedEvent, DeviceLeftEvent
from zha.application.platforms import WebSocketClientEntity
from zha.application.platforms.switch import WebSocketClientSwitchEntity
from zha.websocket.const import ControllerEvents
from zha.websocket.server.api.model import (
    ReadClusterAttributesResponse,
    WriteClusterAttributeResponse,
)
from zha.zigbee.device import Device, WebSocketClientDevice
from zha.zigbee.group import Group, GroupMemberReference, WebSocketClientGroup
from zha.zigbee.model import GroupInfo

from ..common import (
    SIG_EP_INPUT,
    SIG_EP_OUTPUT,
    SIG_EP_PROFILE,
    SIG_EP_TYPE,
    async_find_group_entity_id,
    create_mock_zigpy_device,
    find_entity,
    join_zigpy_device,
    update_attribute_cache,
)

ON = 1
OFF = 0
IEEE_GROUPABLE_DEVICE = "01:2d:6f:00:0a:90:69:e8"
IEEE_GROUPABLE_DEVICE2 = "02:2d:6f:00:0a:90:69:e8"
_LOGGER = logging.getLogger(__name__)


def zigpy_device_mock(
    zha_gateway: WebSocketServerGateway,
) -> ZigpyDevice:
    """Device tracker zigpy device."""
    endpoints = {
        1: {
            SIG_EP_INPUT: [general.Basic.cluster_id, general.OnOff.cluster_id],
            SIG_EP_OUTPUT: [],
            SIG_EP_TYPE: zha.DeviceType.ON_OFF_SWITCH,
            SIG_EP_PROFILE: zha.PROFILE_ID,
        }
    }
    return create_mock_zigpy_device(zha_gateway, endpoints)


async def device_switch_1_mock(
    zha_gateway: WebSocketServerGateway,
) -> Device:
    """Test zha switch platform."""

    zigpy_dev = create_mock_zigpy_device(
        zha_gateway,
        {
            1: {
                SIG_EP_INPUT: [general.OnOff.cluster_id, general.Groups.cluster_id],
                SIG_EP_OUTPUT: [],
                SIG_EP_TYPE: zha.DeviceType.ON_OFF_SWITCH,
                SIG_EP_PROFILE: zha.PROFILE_ID,
            }
        },
        ieee=IEEE_GROUPABLE_DEVICE,
    )
    zha_device = await join_zigpy_device(zha_gateway, zigpy_dev)
    ws_server_device = zha_gateway.ws_gateway.devices[zha_device.ieee]
    ws_server_device.update_available(available=True, on_network=zha_device.on_network)
    return zha_device


def get_group_entity(
    group_proxy: WebSocketClientGroup, entity_id: str
) -> Optional[WebSocketClientEntity]:
    """Get entity."""

    return group_proxy.group_entities.get(entity_id)


async def device_switch_2_mock(
    zha_gateway: WebSocketServerGateway,
) -> Device:
    """Test zha switch platform."""

    zigpy_dev = create_mock_zigpy_device(
        zha_gateway,
        {
            1: {
                SIG_EP_INPUT: [general.OnOff.cluster_id, general.Groups.cluster_id],
                SIG_EP_OUTPUT: [],
                SIG_EP_TYPE: zha.DeviceType.ON_OFF_SWITCH,
                SIG_EP_PROFILE: zha.PROFILE_ID,
            }
        },
        ieee=IEEE_GROUPABLE_DEVICE2,
    )
    zha_device = await join_zigpy_device(zha_gateway, zigpy_dev)
    ws_server_device = zha_gateway.ws_gateway.devices[zha_device.ieee]
    ws_server_device.update_available(available=True, on_network=zha_device.on_network)
    return zha_device


@pytest.mark.parametrize(
    "zha_gateway",
    [
        "ws_gateways",
    ],
    indirect=True,
)
async def test_ws_client_gateway_devices(
    zha_gateway: CombinedWebsocketGateways,
) -> None:
    """Test client ws_client_gateway device related functionality."""
    ws_client_gateway = zha_gateway.client_gateway
    zigpy_device = zigpy_device_mock(zha_gateway)
    zha_device = await join_zigpy_device(zha_gateway, zigpy_device)

    client_device: Optional[WebSocketClientDevice] = ws_client_gateway.devices.get(
        zha_device.ieee
    )
    assert client_device is not None

    entity = find_entity(client_device, Platform.SWITCH)
    assert entity is not None

    assert isinstance(entity, WebSocketClientSwitchEntity)

    assert entity.state["state"] is False

    await ws_client_gateway.load_devices()
    devices: dict[EUI64, WebSocketClientDevice] = ws_client_gateway.devices
    assert len(devices) == 2
    assert zha_device.ieee in devices

    # test client -> ws_server_gateway
    zha_gateway.application_controller.remove = AsyncMock(
        wraps=zha_gateway.application_controller.remove
    )
    await ws_client_gateway.devices_helper.remove_device(
        client_device._extended_device_info
    )
    assert zha_gateway.application_controller.remove.await_count == 1
    assert zha_gateway.application_controller.remove.await_args == call(
        client_device.ieee
    )

    # test zha_gateway -> client
    zha_gateway.ws_gateway.device_removed(zigpy_device)
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.devices) == 1

    # rejoin the device
    zha_device = await join_zigpy_device(zha_gateway, zigpy_device)
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.devices) == 2

    # test rejoining the same device
    zha_device = await join_zigpy_device(zha_gateway, zigpy_device)
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.devices) == 2

    # test client gateway device removal
    await ws_client_gateway.async_remove_device(zha_device.ieee)
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.devices) == 1

    # lets kill the network and then start it back up to make sure everything is still in working order
    await ws_client_gateway.network.stop_network()

    assert zha_gateway.application_controller is None

    await ws_client_gateway.network.start_network()

    assert zha_gateway.application_controller is not None

    # let's add it back
    zha_device = await join_zigpy_device(zha_gateway, zigpy_device)
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.devices) == 2

    # we removed and joined the device again so lets get the entity again
    client_device = ws_client_gateway.devices.get(zha_device.ieee)
    assert client_device is not None

    entity = find_entity(client_device, Platform.SWITCH)
    assert entity is not None

    # test device reconfigure
    ws_server_device = zha_gateway.ws_gateway.devices[zha_device.ieee]
    async_configure_mock = AsyncMock(wraps=ws_server_device.async_configure)
    ws_server_device.async_configure = async_configure_mock

    await ws_client_gateway.devices_helper.reconfigure_device(
        client_device._extended_device_info
    )
    await zha_gateway.async_block_till_done()
    assert async_configure_mock.call_count == 1
    assert async_configure_mock.await_count == 1
    assert async_configure_mock.call_args == call()

    # test read cluster attribute
    cluster = zigpy_device.endpoints.get(1).on_off
    assert cluster is not None
    cluster.PLUGGED_ATTR_READS = {general.OnOff.AttributeDefs.on_off.name: 1}
    update_attribute_cache(cluster)
    await ws_client_gateway.entities.refresh_state(entity.info_object)
    await zha_gateway.async_block_till_done()
    read_response: ReadClusterAttributesResponse = (
        await ws_client_gateway.devices_helper.read_cluster_attributes(
            client_device._extended_device_info,
            general.OnOff.cluster_id,
            "in",
            1,
            [general.OnOff.AttributeDefs.on_off.name],
        )
    )
    await zha_gateway.async_block_till_done()
    assert read_response is not None
    assert read_response.success is True
    assert len(read_response.succeeded) == 1
    assert len(read_response.failed) == 0
    assert read_response.succeeded[general.OnOff.AttributeDefs.on_off.name] == 1
    assert read_response.cluster.id == general.OnOff.cluster_id
    assert read_response.cluster.endpoint_id == 1
    assert (
        read_response.cluster.endpoint_attribute
        == general.OnOff.AttributeDefs.on_off.name
    )
    assert read_response.cluster.name == general.OnOff.name
    assert entity.state["state"] is True

    # test write cluster attribute
    write_response: WriteClusterAttributeResponse = (
        await ws_client_gateway.devices_helper.write_cluster_attribute(
            client_device._extended_device_info,
            general.OnOff.cluster_id,
            "in",
            1,
            general.OnOff.AttributeDefs.on_off.name,
            0,
        )
    )
    assert write_response is not None
    assert write_response.success is True
    assert write_response.cluster.id == general.OnOff.cluster_id
    assert write_response.cluster.endpoint_id == 1
    assert (
        write_response.cluster.endpoint_attribute
        == general.OnOff.AttributeDefs.on_off.name
    )
    assert write_response.cluster.name == general.OnOff.name

    await ws_client_gateway.entities.refresh_state(entity.info_object)
    await zha_gateway.async_block_till_done()
    assert entity.state["state"] is False

    # test ws_client_gateway events
    listener = MagicMock()

    # test device joined
    ws_client_gateway.on_event(ControllerEvents.DEVICE_JOINED, listener)
    device_joined_event = DeviceJoinedEvent(
        device_info=DeviceJoinedDeviceInfo(
            pairing_status=DevicePairingStatus.PAIRED,
            ieee=zigpy_device.ieee,
            nwk=zigpy_device.nwk,
        )
    )
    zha_gateway.ws_gateway.device_joined(zigpy_device)
    await zha_gateway.async_block_till_done()
    assert listener.call_count == 1
    assert listener.call_args == call(device_joined_event)

    # test device left
    listener.reset_mock()
    ws_client_gateway.on_event(ControllerEvents.DEVICE_LEFT, listener)
    zha_gateway.ws_gateway.device_left(zigpy_device)
    await zha_gateway.async_block_till_done()
    assert listener.call_count == 1
    assert listener.call_args == call(
        DeviceLeftEvent(
            ieee=zigpy_device.ieee,
            nwk=str(zigpy_device.nwk).lower(),
        )
    )

    # test raw  device initialized
    listener.reset_mock()
    ws_client_gateway.on_event(ControllerEvents.RAW_DEVICE_INITIALIZED, listener)
    zha_gateway.ws_gateway.raw_device_initialized(zigpy_device)
    await zha_gateway.async_block_till_done()
    assert listener.call_count == 1
    assert listener.call_args == call(
        RawDeviceInitializedEvent(
            device_info=RawDeviceInitializedDeviceInfo(
                pairing_status=DevicePairingStatus.INTERVIEW_COMPLETE,
                ieee=zigpy_device.ieee,
                nwk=zigpy_device.nwk,
                manufacturer=client_device.manufacturer,
                model=client_device.model,
                signature=client_device._extended_device_info.signature,
            ),
        )
    )

    # test topology scan
    zha_gateway.application_controller.topology.scan = AsyncMock()
    await ws_client_gateway.network.update_topology()
    assert zha_gateway.application_controller.topology.scan.await_count == 1

    # test permit join
    zha_gateway.application_controller.permit = AsyncMock()
    await ws_client_gateway.network.permit_joining(60)
    assert zha_gateway.application_controller.permit.await_count == 1
    assert zha_gateway.application_controller.permit.await_args == call(60, None)


@pytest.mark.parametrize(
    "zha_gateway",
    [
        "ws_gateways",
    ],
    indirect=True,
)
async def test_ws_client_gateway_groups(
    zha_gateway: CombinedWebsocketGateways,
) -> None:
    """Test client ws_client_gateway group related functionality."""
    ws_client_gateway = zha_gateway.client_gateway
    device_switch_1: Device = await device_switch_1_mock(zha_gateway)
    device_switch_2: Device = await device_switch_2_mock(zha_gateway)
    member_ieee_addresses = [device_switch_1.ieee, device_switch_2.ieee]
    members = [
        GroupMemberReference(ieee=device_switch_1.ieee, endpoint_id=1),
        GroupMemberReference(ieee=device_switch_2.ieee, endpoint_id=1),
    ]

    # test creating a group with 2 members
    zha_group: Group = await zha_gateway.async_create_zigpy_group("Test Group", members)
    await zha_gateway.async_block_till_done()

    assert zha_group is not None
    assert len(zha_group.members) == 2
    for member in zha_group.members:
        assert member.device.ieee in member_ieee_addresses
        assert member.group == zha_group
        assert member.endpoint_id == 1

    entity_id = async_find_group_entity_id(Platform.SWITCH, zha_group)
    assert entity_id is not None

    group_proxy: Optional[WebSocketClientGroup] = ws_client_gateway.groups.get(
        zha_group.group_id
    )
    assert group_proxy is not None

    entity: WebSocketClientSwitchEntity = get_group_entity(group_proxy, entity_id)  # type: ignore
    assert entity is not None

    assert isinstance(entity, WebSocketClientSwitchEntity)

    assert entity is not None

    await ws_client_gateway.load_groups()
    groups: dict[int, WebSocketClientGroup] = ws_client_gateway.groups
    # the application ws_client_gateway mock starts with a group already created
    assert len(groups) == 2
    assert zha_group.group_id in groups

    # test client -> zha_gateway
    await ws_client_gateway.groups_helper.remove_groups([group_proxy._group_info])
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.groups) == 1

    # test client create group
    client_device1: Optional[WebSocketClientDevice] = ws_client_gateway.devices.get(
        device_switch_1.ieee
    )
    assert client_device1 is not None

    entity1: WebSocketClientSwitchEntity = find_entity(client_device1, Platform.SWITCH)
    assert entity1 is not None

    client_device2: Optional[WebSocketClientDevice] = ws_client_gateway.devices.get(
        device_switch_2.ieee
    )
    assert client_device2 is not None

    entity2: WebSocketClientSwitchEntity = find_entity(client_device2, Platform.SWITCH)
    assert entity2 is not None

    response: GroupInfo = await ws_client_gateway.groups_helper.create_group(
        members=[
            GroupMemberReference(
                ieee=entity1.info_object.device_ieee,
                endpoint_id=entity1.info_object.endpoint_id,
            ),
            GroupMemberReference(
                ieee=entity2.info_object.device_ieee,
                endpoint_id=entity2.info_object.endpoint_id,
            ),
        ],
        name="Test Group Controller",
    )
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.groups) == 2
    assert response.group_id in ws_client_gateway.groups
    assert response.name == "Test Group Controller"
    assert client_device1.ieee in response.members_by_ieee
    assert client_device2.ieee in response.members_by_ieee

    group_from_ws_client_gateway = ws_client_gateway.get_group(response.group_id)
    assert group_from_ws_client_gateway is not None
    assert group_from_ws_client_gateway.group_id == response.group_id
    assert group_from_ws_client_gateway.name == response.name
    assert (
        group_from_ws_client_gateway.info_object.members_by_ieee
        == response.members_by_ieee
    )

    # test remove member from group from ws_client_gateway
    response = await ws_client_gateway.groups_helper.remove_group_members(
        response,
        [
            GroupMemberReference(
                ieee=entity2.info_object.device_ieee,
                endpoint_id=entity2.info_object.endpoint_id,
            )
        ],
    )
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.groups) == 2
    assert response.group_id in ws_client_gateway.groups
    assert response.name == "Test Group Controller"
    assert client_device1.ieee in response.members_by_ieee
    assert client_device2.ieee not in response.members_by_ieee

    # test add member to group from ws_client_gateway
    response = await ws_client_gateway.groups_helper.add_group_members(
        response,
        [
            GroupMemberReference(
                ieee=entity2.info_object.device_ieee,
                endpoint_id=entity2.info_object.endpoint_id,
            )
        ],
    )
    await zha_gateway.async_block_till_done()
    assert len(ws_client_gateway.groups) == 2
    assert response.group_id in ws_client_gateway.groups
    assert response.name == "Test Group Controller"
    assert client_device1.ieee in response.members_by_ieee
    assert client_device2.ieee in response.members_by_ieee
