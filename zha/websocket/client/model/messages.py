"""Models that represent messages in zha."""

from pydantic import RootModel

from zha.websocket.server.api.model import Messages


class Message(RootModel):
    """Response model."""

    root: Messages
