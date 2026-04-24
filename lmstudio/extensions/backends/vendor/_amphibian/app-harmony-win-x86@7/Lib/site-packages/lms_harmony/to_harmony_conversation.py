from openai_harmony import (
    Author,
    Conversation,
    DeveloperContent,
    Message,
    Role,
    SystemContent,
    ToolDescription,
    ReasoningEffort,
)
from lms_harmony.model import (
    OpenaiAssistantCommentaryPreambleMessage,
    OpenaiAssistantFinalMessage,
    OpenaiAssistantReasoningMessage,
    OpenaiAssistantToolCallMessage,
    OpenaiChat,
    OpenaiReasoningEffort,
    OpenaiToolDefinition,
    OpenaiToolResultMessage,
    OpenaiUserMessage,
)
from datetime import datetime


def _get_current_date_yyyy_mm_dd():
    return datetime.now().strftime("%Y-%m-%d")


def _get_reasoning_effort(reasoning_effort: OpenaiReasoningEffort) -> ReasoningEffort:
    if reasoning_effort == OpenaiReasoningEffort.low:
        return ReasoningEffort.LOW
    elif reasoning_effort == OpenaiReasoningEffort.medium:
        return ReasoningEffort.MEDIUM
    elif reasoning_effort == OpenaiReasoningEffort.high:
        return ReasoningEffort.HIGH
    else:
        raise ValueError(f"Unknown reasoning effort: {reasoning_effort}")


def _get_system_content(chat: OpenaiChat) -> SystemContent:
    """
    Given the chat, construct the system content for the chat.
    """
    system_content = (
        SystemContent.new()
        # According to OpenAI, this will be removed.
        .with_model_identity(
            "You are ChatGPT, a large language model trained by OpenAI."
        )
        .with_reasoning_effort(_get_reasoning_effort(chat.reasoningEffort))
        .with_conversation_start_date(_get_current_date_yyyy_mm_dd())
    )
    return system_content


def _get_tool_description(tool_definition: OpenaiToolDefinition) -> ToolDescription:
    """
    Construct one tool description.
    """
    return ToolDescription.new(
        name=tool_definition.name,
        description=tool_definition.description,
        parameters=tool_definition.parametersJsonSchema,
    )


def _get_tool_descriptions(
    tool_definitions: list[OpenaiToolDefinition],
) -> list[ToolDescription]:
    """
    Given the chat, construct tool descriptions for the chat.
    """
    return [
        _get_tool_description(tool_definition) for tool_definition in tool_definitions
    ]


def _get_developer_content(chat: OpenaiChat) -> DeveloperContent | None:
    """
    Given the chat, construct the developer content.
    """
    if chat.developerInstructions == "" and len(chat.toolDefinitions) == 0:
        return None

    developer_content = DeveloperContent.new()

    if chat.developerInstructions != "":
        developer_content = developer_content.with_instructions(
            chat.developerInstructions
        )
    if len(chat.toolDefinitions) > 0:
        developer_content = developer_content.with_function_tools(
            _get_tool_descriptions(chat.toolDefinitions)
        )

    return developer_content


def _get_user_message(message: OpenaiUserMessage) -> Message:
    """
    Convert an OpenAI user message to a Harmony message.
    """
    harmony_message = Message.from_role_and_content(
        Role.USER,
        message.content,
    )
    return harmony_message


def _get_assistant_reasoning_message(
    message: OpenaiAssistantReasoningMessage,
) -> Message:
    """
    Convert an OpenAI assistant reasoning message to a Harmony message.
    """
    harmony_message = Message.from_role_and_content(
        Role.ASSISTANT,
        message.content,
    ).with_channel("analysis")
    return harmony_message


def _get_assistant_tool_call_message(
    message: OpenaiAssistantToolCallMessage,
) -> Message:
    """
    Convert an OpenAI assistant tool call message to a Harmony message.
    """
    harmony_message = (
        Message.from_role_and_content(
            Role.ASSISTANT,
            message.toolParameter,
        )
        .with_channel("commentary")
        .with_recipient(f"functions.{message.toolName}")
        .with_content_type("json")
    )
    return harmony_message


def _get_assistant_commentary_preamble_message(
    message: OpenaiAssistantCommentaryPreambleMessage,
) -> Message:
    """
    Convert an OpenAI assistant commentary preamble message to a Harmony message.
    """
    harmony_message = Message.from_role_and_content(
        Role.ASSISTANT,
        message.content,
    ).with_channel("commentary")
    return harmony_message


def _get_assistant_final_message(message: OpenaiAssistantFinalMessage) -> Message:
    """
    Convert an OpenAI assistant final message to a Harmony message.
    """
    harmony_message = Message.from_role_and_content(
        Role.ASSISTANT,
        message.content,
    ).with_channel("final")
    return harmony_message


def _get_tool_result_message(message: OpenaiToolResultMessage) -> Message:
    """
    Convert an OpenAI tool result message to a Harmony message.
    """
    harmony_message = (
        Message.from_author_and_content(
            Author.new(Role.TOOL, f"functions.{message.toolName}"),
            message.toolResult,
        )
        .with_recipient("assistant")
        .with_channel("commentary")
    )
    return harmony_message


def to_harmony_conversation(chat: OpenaiChat) -> Conversation:
    """
    Convert an OpenAI chat object to a Harmony conversation.
    """
    messages: list[Message] = []
    messages.append(
        Message.from_role_and_content(
            Role.SYSTEM,
            _get_system_content(chat),
        )
    )

    developer_content = _get_developer_content(chat)
    if developer_content is not None:
        messages.append(
            Message.from_role_and_content(
                Role.DEVELOPER,
                developer_content,
            )
        )

    for message in chat.messages:
        concrete_message = message.root
        if isinstance(concrete_message, OpenaiUserMessage):
            messages.append(_get_user_message(concrete_message))
        elif isinstance(concrete_message, OpenaiAssistantReasoningMessage):
            messages.append(_get_assistant_reasoning_message(concrete_message))
        elif isinstance(concrete_message, OpenaiAssistantToolCallMessage):
            messages.append(_get_assistant_tool_call_message(concrete_message))
        elif isinstance(concrete_message, OpenaiAssistantCommentaryPreambleMessage):
            messages.append(
                _get_assistant_commentary_preamble_message(concrete_message)
            )
        elif isinstance(concrete_message, OpenaiAssistantFinalMessage):
            messages.append(_get_assistant_final_message(concrete_message))
        elif isinstance(concrete_message, OpenaiToolResultMessage):
            messages.append(_get_tool_result_message(concrete_message))
        else:
            raise ValueError(f"Unknown message type: {type(concrete_message)}")

    conversation = Conversation.from_messages(messages)
    return conversation
