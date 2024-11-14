"""Websocket application to run a zigpy Zigbee network."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

from zha.application.gateway import WebSocketServerGateway
from zha.application.model import (
    WebsocketClientConfiguration,
    WebsocketServerConfiguration,
    ZHAConfiguration,
    ZHAData,
)

_LOGGER = logging.getLogger(__name__)


async def main(config_path: str | None = None) -> None:
    """Run the websocket server."""
    if config_path is None:
        raise ValueError("config_path must be provided")
    else:
        _LOGGER.info("Loading configuration from %s", config_path)
        path = Path(config_path)
        raw_data = json.loads(path.read_text(encoding="utf-8"))
        zha_data = ZHAData(
            config=ZHAConfiguration.model_validate(raw_data["zha_config"]),
            ws_server_config=WebsocketServerConfiguration.model_validate(
                raw_data["ws_server_config"]
            ),
            ws_client_config=WebsocketClientConfiguration.model_validate(
                raw_data["ws_client_config"]
            ),
            zigpy_config=raw_data["zigpy_config"],
        )
    async with await WebSocketServerGateway.async_from_config(zha_data) as ws_gateway:
        await ws_gateway.async_initialize()
        await ws_gateway.async_initialize_devices_and_entities()
        await ws_gateway.wait_closed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the ZHAWS gateway")
    parser.add_argument(
        "--config", type=str, default=None, help="Path to the configuration file"
    )

    args = parser.parse_args()

    from colorlog import ColoredFormatter

    fmt = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
    colorfmt = f"%(log_color)s{fmt}%(reset)s"
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            colorfmt,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    )

    asyncio.run(main(args.config))
