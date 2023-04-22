from __future__ import annotations
from langchain.schema import BaseLanguageModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackManager
from .prompts import FORMAT_INSTRUCTIONS, SUFFIX
from langchain.agents.agent import Agent, AgentOutputParser
from typing import Any, Optional, Sequence
from langchain.tools import BaseTool
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


class ChatZeroShotAgent(ZeroShotAgent):
    """Agent for the MRKL chain with chat models."""

    @classmethod
    def chat_create_prompt(
        cls,
        tools: Sequence[BaseTool],
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
    ) -> PromptTemplate:
        """Create prompt in the style of the zero shot agent with a chat model.

        Args:
            tools: List of tools the agent will have access to, used to format the
                prompt.
            prefix: String to put before the list of tools.
            suffix: String to put after the list of tools.
            input_variables: List of input variables the final prompt will expect.

        Returns:
            A PromptTemplate with the template assembled from the pieces here.
        """
        tool_strings = "\n".join(
            [f"    {tool.name}: {tool.description}" for tool in tools]
        )
        tool_names = ", ".join([tool.name for tool in tools])
        format_instructions = format_instructions.format(
            tool_names=tool_names, tool_strings=tool_strings
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(suffix)
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            format_instructions
        )
        return ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        callback_manager: Optional[BaseCallbackManager] = None,
        output_parser: Optional[AgentOutputParser] = None,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        **kwargs: Any,
    ) -> Agent:
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)
        prompt = cls.chat_create_prompt(
            tools,
            suffix=suffix,
            format_instructions=format_instructions,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        _output_parser = output_parser or cls._get_default_output_parser()
        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=_output_parser,
            **kwargs,
        )
