"""Models that represent messages in zhawss."""

from typing import Annotated

from pydantic import RootModel
from pydantic.fields import Field

from zha.websocket.server.api.model import CommandResponses, Events


class Message(RootModel):
    """Response model."""

    root: Annotated[
        CommandResponses | Events,
        Field(discriminator="message_type"),
    ]
