from lms_communication.base_rpc_endpoint_handler import BaseRPCEndpointHandler
from lms_harmony.model import (
    OpenaiInputOutputPreprocessingRpcRenderChatToTextParameter,
    OpenaiInputOutputPreprocessingRpcRenderChatToTextReturns,
)
from lms_harmony.to_harmony_conversation import to_harmony_conversation
from openai_harmony import (
    Role,
)
from lms_harmony.encoding_cache import cached_get_harmony_encoding


class RenderChatToTextHandler(BaseRPCEndpointHandler):
    async def handle_request(
        self,
        parameter: OpenaiInputOutputPreprocessingRpcRenderChatToTextParameter,
    ):
        if parameter.encodingName != "HarmonyGptOss":
            raise ValueError("Invalid encodingName")

        encoding = cached_get_harmony_encoding(parameter.encodingName)
        conversation = to_harmony_conversation(parameter.chat)

        tokens = encoding.render_conversation_for_completion(
            conversation, Role.ASSISTANT
        )
        text = encoding.decode_utf8(tokens)

        return OpenaiInputOutputPreprocessingRpcRenderChatToTextReturns(text=text)
