from lms_communication.base_rpc_endpoint_handler import BaseRPCEndpointHandler
from lms_harmony.model import (
    OpenaiInputOutputPreprocessingRpcGetStopTokensParameter,
    OpenaiInputOutputPreprocessingRpcGetStopTokensReturns,
)
from lms_harmony.encoding_cache import cached_get_harmony_encoding


class GetStopTokensHandler(BaseRPCEndpointHandler):
    async def handle_request(
        self,
        parameter: OpenaiInputOutputPreprocessingRpcGetStopTokensParameter,
    ):
        encoding = cached_get_harmony_encoding(parameter.encodingName)
        stop_tokens = encoding.stop_tokens_for_assistant_actions()

        return OpenaiInputOutputPreprocessingRpcGetStopTokensReturns(
            stopTokens=stop_tokens
        )
