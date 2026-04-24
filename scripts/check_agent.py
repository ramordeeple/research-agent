import asyncio

from src.agent.agent import Agent
from src.core.logger import setup_logging
from src.llm.client import get_llm_provider
from src.tools.calculator import CalculatorTool
from src.tools.registry import ToolRegistry


async def main() -> None:
    setup_logging()

    registry = ToolRegistry()
    registry.register(CalculatorTool())

    agent = Agent(llm=get_llm_provider(), tools=registry)

    questions = [
        "Hello, how are you?",
        "What is 25 times 13?",
        "What is the capital of France?",
    ]

    for question in questions:
        print(f"\n{'=' * 60}")
        print(f"Q: {question}")
        print('=' * 60)

        result = await agent.run(question)

        print(f"A: {result.answer}")
        print(f"Stopped: {result.stopped_reason}, iterations: {result.iterations_used}")

        if result.steps:
            print("Steps:")
            for step in result.steps:
                print(f"  [{step.iteration}] action={step.action}, obs={step.observation[:80]}")


if __name__ == "__main__":
    asyncio.run(main())