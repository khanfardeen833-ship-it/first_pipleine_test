from dotenv import load_dotenv
load_dotenv()

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant. Be concise.",
        allowed_tools=[],
    )

    async for message in query(
        prompt="Say hello and tell me what 2+2 is.",
        options=options,
    ):
        print(message)


anyio.run(main)
