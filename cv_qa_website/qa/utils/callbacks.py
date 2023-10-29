from typing import Any

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult


class ThoughtsCallbackHandler(BaseCallbackHandler):

    """Callback Handler."""

    def __init__(self, color: str | None = None) -> None:
        """Initialize callback handler."""
        self.color = color
        self.thoughts = ""

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""

    def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        """Do nothing."""

    def on_chain_start(
        self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs: Any
    ) -> None:
        class_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
        self.thoughts += f"<strong>> Entering new {class_name} chain...</strong>\n"

    def on_chain_end(self, outputs: dict[str, Any], **kwargs: Any) -> None:
        self.thoughts += "\n<strong>> Finished chain.</strong>"

    def on_chain_error(
        self, error: Exception | KeyboardInterrupt, **kwargs: Any
    ) -> None:
        """Do nothing."""

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Do nothing."""

    def on_agent_action(
        self, action: AgentAction, color: str | None = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        self.thoughts += action.log + "\n"

    def on_tool_end(
        self,
        output: str,
        color: str | None = None,
        observation_prefix: str | None = None,
        llm_prefix: str | None = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        if observation_prefix is not None:
            self.thoughts += f"\n{observation_prefix}"
        self.thoughts += output + "\n"
        if llm_prefix is not None:
            self.thoughts += f"\n{llm_prefix}"

    def on_tool_error(
        self, error: Exception | KeyboardInterrupt, **kwargs: Any
    ) -> None:
        """Do nothing."""

    def on_text(
        self,
        text: str,
        color: str | None = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        self.thoughts += text + "\n"

    def on_agent_finish(
        self, finish: AgentFinish, color: str | None = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        self.thoughts += finish.log + "\n"
