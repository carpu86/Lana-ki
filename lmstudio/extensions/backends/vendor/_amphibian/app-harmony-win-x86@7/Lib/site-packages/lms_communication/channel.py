import asyncio


class Channel:
    """
    Handle incoming Channel messages. The wire format for channel messages is defined in lmstudio.js/lms-communication/Transport.ts.

    This class should not contain any endpoint-specific logic. Instead, it should delegate to the appropriate handler based on the endpoint.

    A new instance of this class should be created per `channelCreate` message, and `handle_request` should be called with
    the channelCreate parameters. Followup `channelSend` messages should call `on_client_message`.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        channel_id: int,
        namespace: str,
        endpoint_handlers: dict,
        websocket,
        model_module,
    ):
        # Anything that could throw should be done in the `handle_request` method
        self.channel_id = channel_id
        self.namespace = namespace
        self.endpoint_handlers = endpoint_handlers
        self.websocket = websocket
        self.model_module = model_module
        self.abort_signal = asyncio.Event()
        self.abort_traceback = None

        # Find the data models
        endpoint = endpoint[0].upper() + endpoint[1:]
        self.endpoint = endpoint
        endpoint_preamble = f"{self.namespace}Channel{self.endpoint}"
        self.channel_creation_param_cls = self.model_module.__dict__[
            f"{endpoint_preamble}CreationParameter"
        ]
        self.channel_client_packet_cls = self.model_module.__dict__[
            f"{endpoint_preamble}ToClientPacket"
        ]
        self.channel_server_packet_cls = self.model_module.__dict__[
            f"{endpoint_preamble}ToServerPacket"
        ]

        # Find the appropriate handler
        self.channel_handler = self.endpoint_handlers[self.endpoint](
            self.channel_id,
            self.websocket,
            self.channel_client_packet_cls,
        )

    async def handle_request(self, creation_param):
        """
        Validate an incoming `channelCreate` message, parse it, and pass it to the handler
        """
        creation_param = self.channel_creation_param_cls(**creation_param)
        await self.channel_handler.handle_request(creation_param)

    async def on_client_message(self, data):
        """
        Validate an incoming `channelSend` message, parse it, and pass it to the handler
        """
        parsed_msg = self.channel_server_packet_cls(**data["message"])
        await self.channel_handler.on_client_message(parsed_msg)

    def set_abort_with_traceback(self, traceback_str):
        """
        Set the abort signal and store the traceback string for later retrieval
        """
        self.abort_traceback = traceback_str
        self.abort_signal.set()
