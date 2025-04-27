import asyncio
import os
import shutil

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI


def get_azure_open_ai_client():
    """
    Creates and returns Azure OpenAI client instance.
    
    Returns:
        AsyncAzureOpenAI: Configured Azure OpenAI client
    """
    load_dotenv()
    
    return AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


async def run(mcp_server: MCPServer):

    azure_open_ai_client = get_azure_open_ai_client()
    set_tracing_disabled(disabled=True)

    agent = Agent(
        name="Assistant",
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        model=OpenAIChatCompletionsModel(model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"), 
                                         openai_client=azure_open_ai_client),
        mcp_servers=[mcp_server],
    )

    # List the files it can read
    message = "Read the files in `sample_files` folder, and list them."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask about books
    message = "What is my #1 favorite book?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask a question that reads then reasons.
    message = "Look at my favorite songs. Suggest one new song that I might like."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")

    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())
