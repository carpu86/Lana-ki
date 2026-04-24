import asyncio
import json
from typing import get_args


class BaseChannelEndpointHandler:
    """
    Base class for endpoint handlers.
    This class contains "send_to_client" that children should use to format and send messages to the client.

    The `to_client_packet_cls` is a union type that defines the possible message types that can be sent to the client.
    """

    def __init__(self, channel_id: int, websocket, to_client_packet_cls):
        self.channel_id = channel_id
        self.websocket = websocket
        self.to_client_packet_cls = to_client_packet_cls

    @staticmethod
    def _create_message(union_type, data_dict: dict):
        """
        Create a validated messaged of the specific type by checking every type in the union for a match.
        """
        union_args = get_args(union_type)
        if union_args:
            for cls in union_args:
                try:
                    return cls(**data_dict)
                except TypeError:
                    pass
            raise TypeError(f"No matching type found in {union_type}")
        else:
            # It's not a union type, call it directly
            return union_type(**data_dict)

    def send_to_client_sync(
        self, data_dict: dict, *, loop: asyncio.AbstractEventLoop | None = None
    ):
        """
        Schedule a task to send a message to the client.

        Specify the message type and the arguments for that message type. For example:
        self.send_to_client(dict(type="progress", progress=0.5))

        A Future object is returned, which the caller can ignore if they don't need to wait for the message to be sent
        """
        to_client_packet = self._create_message(self.to_client_packet_cls, data_dict)
        data = {
            "type": "channelSend",
            "channelId": self.channel_id,
            "message": to_client_packet.model_dump(mode="json"),
        }
        if loop is None:
            loop = asyncio.get_event_loop()

        return asyncio.run_coroutine_threadsafe(
            self.websocket.send(json.dumps(data)), loop
        )

    async def send_to_client(self, data_dict: dict):
        """
        Run the synchronous send_to_client_sync in an asyncio event loop, and return an awaitable Future
        """
        # We need to await here to avoid the caller needing to double-await
        return await asyncio.wrap_future(self.send_to_client_sync(data_dict))
