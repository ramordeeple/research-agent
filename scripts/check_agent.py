import asyncio

from src.core.logger import setup_logging
from src.services.agent_service import get_agent


async def main() -> None:
    setup_logging()
    agent = get_agent()

    questions = [
        "Hello, how are you?",
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
