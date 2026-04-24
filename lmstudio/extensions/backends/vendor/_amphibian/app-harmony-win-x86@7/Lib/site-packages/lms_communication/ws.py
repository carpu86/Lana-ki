import functools
from websockets.asyncio.server import serve
import asyncio
import logging
import os

from lms_communication.base_rpc_endpoint_handler import BaseRPCEndpointHandler
from lms_communication.events import handle_incoming_message
from lms_communication.base_channel_endpoint_handler import BaseChannelEndpointHandler


async def _init_orphan_detection(check_interval: float = 5.0):
    """Clean up this process when its parent dies"""
    initial_parent_pid = os.getppid()

    async def check_parent():
        while True:
            await asyncio.sleep(check_interval)
            current_parent_pid = os.getppid()

            if current_parent_pid != initial_parent_pid:
                print(
                    f"Parent process changed ({initial_parent_pid} -> {current_parent_pid}), shutting down..."
                )

                # use os._exit instead of sys.exit so that we skip normal exit processing and kill immediately
                os._exit(0)

    asyncio.create_task(check_parent())


async def _server_loop(
    websocket,
    *,
    channel_map,
    namespace,
    endpoint_handlers,
    model_module,
    cancellation_event,
):
    """
    Immediately create a new task for each incoming message from the websocket, so that we don't block the server loop.
    If an unhandled exception escapes, signal the main server to shut down.
    """
    try:
        async for data in websocket:
            asyncio.create_task(
                handle_incoming_message(
                    data=data,
                    channel_map=channel_map,
                    namespace=namespace,
                    endpoint_handlers=endpoint_handlers,
                    websocket=websocket,
                    model_module=model_module,
                )
            )
    except Exception as e:
        logging.error(f"Unhandled exception in server_loop: {e}", exc_info=True)
        cancellation_event.set()
        raise


async def main(
    *,
    namespace: str,
    endpoint_handlers: dict[str, BaseChannelEndpointHandler | BaseRPCEndpointHandler],
    model_module,
    ws_max_msg_size: int = 104857600,
):
    """
    Start a websocket server and run indefinitely.

    Args:
        namespace: Namespace for routing messages.
        endpoint_handlers: Mapping of endpoint name to its channel/RPC handler(s).
        model_module: Module passed to handlers for model/schema-specific logic.
        ws_max_msg_size: Max inbound message size in bytes (default 100 MiB).

    Prints SERVER_PORT:{port} on startup; each message is handled in its own task.
    Server will shutdown gracefully if an unhandled exception occurs in server_loop.
    """
    channel_map = {}
    cancellation_event = asyncio.Event()

    server_loop_with_bindings = functools.partial(
        _server_loop,
        channel_map=channel_map,
        namespace=namespace,
        endpoint_handlers=endpoint_handlers,
        model_module=model_module,
        cancellation_event=cancellation_event,
    )

    await _init_orphan_detection()
    async with serve(
        server_loop_with_bindings, "127.0.0.1", max_size=ws_max_msg_size
    ) as server:
        print(f"SERVER_PORT:{server.sockets[0].getsockname()[1]}", flush=True)

        # Create server task
        server_task = asyncio.create_task(server.serve_forever())

        # Create cancellation listener
        cancellation_task = asyncio.create_task(cancellation_event.wait())

        # Serve forever, but wake up if we receive a cancel event
        _, pending = await asyncio.wait(
            [server_task, cancellation_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel the serve_forever task
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        raise RuntimeError("Server task was cancelled. Exiting...")
