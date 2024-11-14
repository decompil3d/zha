"""Client implementation for the zha.client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import pprint
from types import TracebackType
from typing import Any

from aiohttp import ClientSession, ClientWebSocketResponse, client_exceptions
from aiohttp.http_websocket import WSMsgType
from async_timeout import timeout
from pydantic_core import ValidationError

from zha.const import COMMAND, MESSAGE_TYPE, MessageTypes
from zha.event import EventBase
from zha.websocket import ZHAWebSocketException
from zha.websocket.client.model.messages import Message
from zha.websocket.const import (
    ERROR_CODE,
    MESSAGE_ID,
    SUCCESS,
    ZIGBEE_ERROR,
    ZIGBEE_ERROR_CODE,
    ZIGBEE_ERROR_MESSAGE,
)
from zha.websocket.server.api.model import WebSocketCommand, WebSocketCommandResponse

SIZE_PARSE_JSON_EXECUTOR = 8192
_LOGGER = logging.getLogger(__package__)


class Client(EventBase):
    """Class to manage the IoT connection."""

    def __init__(
        self,
        ws_server_url: str,
        *args: Any,
        aiohttp_session: ClientSession | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Client class."""
        super().__init__(*args, **kwargs)
        self.ws_server_url = ws_server_url

        # Create a session if none is provided
        if aiohttp_session is None:
            self.aiohttp_session = ClientSession()
            self._close_aiohttp_session: bool = True
        else:
            self.aiohttp_session = aiohttp_session
            self._close_aiohttp_session = False

        # The WebSocket client
        self._client: ClientWebSocketResponse | None = None
        self._loop = asyncio.get_running_loop()
        self._result_futures: dict[int, asyncio.Future] = {}
        self._listen_task: asyncio.Task | None = None
        self._tasks: set[asyncio.Task] = set()

        self._message_id = 0

    def __repr__(self) -> str:
        """Return the representation."""
        prefix = "" if self.connected else "not "
        return f"{type(self).__name__}(ws_server_url={self.ws_server_url!r}, {prefix}connected)"

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self._client is not None and not self._client.closed

    def new_message_id(self) -> int:
        """Create a new message ID.

        XXX: JSON doesn't define limits for integers but JavaScript itself internally
        uses double precision floats for numbers (including in `JSON.parse`), setting
        a hard limit of `Number.MAX_SAFE_INTEGER == 2^53 - 1`.  We can be more
        conservative and just restrict it to the maximum value of a 32-bit signed int.
        """
        self._message_id = (self._message_id + 1) % 0x80000000
        return self._message_id

    async def async_send_command(
        self,
        command: WebSocketCommand,
    ) -> WebSocketCommandResponse:
        """Send a command and get a response."""
        future: asyncio.Future[WebSocketCommandResponse] = self._loop.create_future()
        message_id = command.message_id = self.new_message_id()
        self._result_futures[message_id] = future

        try:
            async with timeout(20):
                await self._send_json_message(
                    command.model_dump_json(exclude_none=True)
                )
                return await future
        except TimeoutError:
            _LOGGER.exception("Timeout waiting for response")
            return WebSocketCommandResponse.model_validate(
                {MESSAGE_ID: message_id, SUCCESS: False, COMMAND: command.command}
            )
        finally:
            self._result_futures.pop(message_id)

    async def async_send_command_no_wait(self, command: WebSocketCommand) -> None:
        """Send a command without waiting for the response."""
        command.message_id = self.new_message_id()
        task = asyncio.create_task(
            self._send_json_message(command.model_dump_json(exclude_none=True)),
            name=f"async_send_command_no_wait:{command.command}",
        )
        self._tasks.add(task)
        task.add_done_callback(self._tasks.remove)

    async def connect(self) -> None:
        """Connect to the websocket server."""

        _LOGGER.debug("Trying to connect")
        try:
            self._client = await self.aiohttp_session.ws_connect(
                self.ws_server_url,
                heartbeat=55,
                compress=15,
                max_msg_size=0,
            )
        except client_exceptions.ClientError as err:
            _LOGGER.exception("Error connecting to server", exc_info=err)
            raise ZHAWebSocketException from err

    async def listen_loop(self) -> None:
        """Listen to the websocket."""
        assert self._client is not None
        while not self._client.closed:
            data = await self._receive_json_or_raise()
            self._handle_incoming_message(data)

    async def listen(self) -> None:
        """Start listening to the websocket."""
        if not self.connected:
            raise ZHAWebSocketException("Not connected when start listening")

        assert self._client

        assert self._listen_task is None
        self._listen_task = asyncio.create_task(self.listen_loop())

    async def disconnect(self) -> None:
        """Disconnect the client."""
        _LOGGER.debug("Closing client connection")

        if self._listen_task is not None:
            self._listen_task.cancel()

            with contextlib.suppress(asyncio.CancelledError):
                await self._listen_task

            self._listen_task = None

        if self._client is not None:
            await self._client.close()

        if self._close_aiohttp_session:
            await self.aiohttp_session.close()

        _LOGGER.debug("Listen completed. Cleaning up")

        for future in self._result_futures.values():
            future.cancel()

        self._result_futures.clear()

    async def _receive_json_or_raise(self) -> dict:
        """Receive json or raise."""
        assert self._client
        msg = await self._client.receive()

        if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
            raise ZHAWebSocketException(f"Connection was closed: {msg}")

        if msg.type == WSMsgType.ERROR:
            raise ZHAWebSocketException(f"WS message type was ERROR: {msg}")

        if msg.type != WSMsgType.TEXT:
            raise ZHAWebSocketException(f"Received non-Text message: {msg}")

        try:
            if len(msg.data) > SIZE_PARSE_JSON_EXECUTOR:
                data: dict = await self._loop.run_in_executor(None, msg.json)
            else:
                data = msg.json()
        except ValueError as err:
            raise ZHAWebSocketException(f"Received invalid JSON: {msg}") from err

        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("Received message:\n%s\n", pprint.pformat(msg))

        return data

    def _handle_incoming_message(self, msg: dict) -> None:
        """Handle incoming message.

        Run all async tasks in a wrapper to log appropriately.
        """

        try:
            message = Message.model_validate(msg).root
        except ValidationError as err:
            _LOGGER.exception("Error parsing message: %s", msg, exc_info=err)
            if msg[MESSAGE_TYPE] == MessageTypes.RESULT:
                future = self._result_futures.get(msg[MESSAGE_ID])
                if future is not None:
                    future.set_exception(ZHAWebSocketException(err))
                    return
            return

        if message.message_type == MessageTypes.RESULT:
            future = self._result_futures.get(message.message_id)

            if future is None:
                _LOGGER.debug(
                    "Unable to handle result message because future for message: {message} is None"
                )
                return

            if message.success:
                future.set_result(message)
                return

            if msg[ERROR_CODE] != ZIGBEE_ERROR:
                error = ZHAWebSocketException(msg[MESSAGE_ID], msg[ERROR_CODE])
            else:
                error = ZHAWebSocketException(
                    msg[MESSAGE_ID],
                    msg[ZIGBEE_ERROR_CODE],
                    msg[ZIGBEE_ERROR_MESSAGE],
                )

            future.set_exception(error)
            return

        if message.message_type != MessageTypes.EVENT:
            # Can't handle
            _LOGGER.debug(
                "Received message with unknown type '%s': %s",
                msg[MESSAGE_TYPE],
                msg,
            )
            return

        try:
            self.emit(message.event_type, message)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Error handling event", exc_info=err)
            raise ZHAWebSocketException from err

    async def _send_json_message(self, message: str) -> None:
        """Send a message.

        Raises NotConnected if client not connected.
        """
        if not self.connected:
            raise ZHAWebSocketException("Sending message failed: no active connection.")

        _LOGGER.debug("Publishing message:\n%s\n", pprint.pformat(message))

        assert self._client
        assert MESSAGE_ID in message

        await self._client.send_str(message)

    async def __aenter__(self) -> Client:
        """Connect to the websocket."""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Exception, exc_value: str, traceback: TracebackType
    ) -> None:
        """Disconnect from the websocket."""
        await self.disconnect()
