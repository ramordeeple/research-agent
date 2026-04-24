import asyncio
import logging

from src.agent.parser import parse_llm_response
from src.agent.prompts import SYSTEM_PROMPT_TEMPLATE

from src.agent.schemas import (
    AgentResult,
    AgentStep,
    ParsedResponse,
    StepType,
    StoppedReason,
)

from src.core.constants import (
    AGENT_TEMPERATURE,
    MAX_AGENT_ITERATIONS,
    MAX_AGENT_TIMEOUT_SECONDS,
)

from src.llm.base import LLMProvider
from src.llm.schemas import Message
from src.tools.base import ToolError
from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class Agent:
    """ReAct-style agent that uses tools to answer user questions."""

    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry,
        max_iterations: int = MAX_AGENT_ITERATIONS,
        timeout_seconds: int = MAX_AGENT_TIMEOUT_SECONDS,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._max_iterations = max_iterations
        self._timeout_seconds = timeout_seconds

    async def run(self, user_message: str) -> AgentResult:
        """Run the ReAct loop with timeout protection."""
        try:
            return await asyncio.wait_for(
                self._run_loop(user_message),
                timeout=self._timeout_seconds,
            )
        except TimeoutError:
            logger.warning("Agent timed out after %ds", self._timeout_seconds)

            return AgentResult(
                answer="The request took too long to process. Please try a simpler question.",
                steps=[],
                iterations_used=0,
                stopped_reason=StoppedReason.TIMEOUT,
            )

    async def _run_loop(self, user_message: str) -> AgentResult:
        messages = self._build_initial_messages(user_message)
        steps: list[AgentStep] = []

        for iteration in range(1, self._max_iterations + 1):
            response = await self._llm.complete(messages, temperature=AGENT_TEMPERATURE)
            parsed = parse_llm_response(response)

            if parsed.step_type == StepType.FINAL_ANSWER:
                logger.info("Agent finished at iteration %d", iteration)
                return AgentResult(
                    answer=parsed.final_answer,
                    steps=steps,
                    iterations_used=iteration,
                    stopped_reason=StoppedReason.FINAL_ANSWER,
                )

            observation = self._handle_step(parsed)
            steps.append(self._build_step(iteration, parsed, observation))

            messages.append(Message.assistant(response))
            messages.append(Message.user(f"Observation: {observation}"))

        logger.warning("Agent reached max iterations (%d)", self._max_iterations)

        return AgentResult(
            answer="I reached the maximum number of reasoning steps without a complete answer.",
            steps=steps,
            iterations_used=self._max_iterations,
            stopped_reason=StoppedReason.MAX_ITERATIONS,
        )

    def _build_initial_messages(self, user_message: str) -> list[Message]:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            tools_description=self._tools.describe_all(),
        )

        return [
            Message.system(system_prompt),
            Message.user(user_message),
        ]

    def _handle_step(self, parsed: ParsedResponse) -> str:
        """Execute the tool or report the parse error. Returns the observation text."""
        if parsed.step_type == StepType.PARSE_ERROR:
            return f"Error: {parsed.error}"

        return self._execute_tool(parsed.action, parsed.action_input)

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        if not self._tools.has(tool_name):
            available = [t.name for t in self._tools.list_tools()]
            return f"Tool '{tool_name}' not found. Available: {available}"

        tool = self._tools.get(tool_name)

        try:
            input_data = tool.input_schema(**tool_input)
        except Exception as e:
            return f"Invalid input for {tool_name}: {e}"

        try:
            return tool.execute(input_data)
        except ToolError as e:
            return f"Tool {tool_name} failed: {e}"
        except Exception:
            logger.exception("Unexpected error in tool %s", tool_name)
            return f"Tool {tool_name} encountered an unexpected error"

    @staticmethod
    def _build_step(iteration: int, parsed: ParsedResponse, observation: str) -> AgentStep:
        return AgentStep(
            iteration=iteration,
            thought=parsed.thought,
            action=parsed.action,
            action_input=parsed.action_input,
            observation=observation,
        )