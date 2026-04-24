from abc import ABC, abstractmethod


class BaseRPCEndpointHandler(ABC):
    """
    Base class for RPC endpoint handlers.

    The `to_result_cls` is a union type that defines the possible message types that can be sent to the client.
    """

    @abstractmethod
    async def handle_request(self, parameter):
        """
        Handle an incoming RPC request.
        """
        pass
