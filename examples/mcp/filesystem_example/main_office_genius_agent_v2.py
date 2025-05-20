import asyncio
import logging
import os
import shutil
import sys
import warnings

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStdio, MCPServerSse
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

# 抑制 asyncio 在 Windows 下的 event loop 關閉錯誤警告
warnings.filterwarnings("ignore", category=ResourceWarning)

# 抑制 asyncio 相關的 critical logging
if hasattr(asyncio, 'windows_events'):
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# 使用 unraisablehook 忽略特定的未捕獲例外 (Python 3.8+)
def ignore_unraisable_hook(unraisable):
    if isinstance(unraisable.exc_value, (RuntimeError, ValueError)):
        return  # 忽略 event loop is closed 及 I/O operation on closed pipe
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = ignore_unraisable_hook


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


async def run(mcp_servers: list[MCPServer]):

    azure_open_ai_client = get_azure_open_ai_client()
    set_tracing_disabled(disabled=True)

    agent = Agent(
        name="AI 助理",
        instructions="You are a helpful AI assistant. Use the available tools to interact with the filesystem (e.g., read files, list directories), manage PowerPoint presentations (e.g., create presentations, add slides, save files), and create/edit Excel spreadsheets (e.g., create workbooks, read and write data, apply formulas) to assist the user with their requests. Respond to the user based on the information you gather or the actions you perform.",
        model=OpenAIChatCompletionsModel(model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"), 
                                         openai_client=azure_open_ai_client),
        mcp_servers=mcp_servers,
    )

    print("您好！我是 AI 助理，協助您生成 PPT 簡報和 Excel 資料表格。您可以隨時輸入「離開」或「退出」來結束我們的對話。")

    while True:
        try:
            user_input = input("\n您：")
            if user_input.lower() in ["離開", "退出", "exit", "quit"]:
                print("正在結束對話。")
                break

            if not user_input:
                continue

            print(f"\nAI 助理正在處理：{user_input}...")
            result = await Runner.run(starting_agent=agent, input=user_input)
            print(f"\nAI 助理：{result.final_output}")

        except KeyboardInterrupt:
            print("\n因使用者中斷而結束對話。")
            break
        except Exception as e:
            print(f"發生錯誤：{e}")
            # Optionally, decide if the loop should break or continue on other errors


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")

    # 檔案系統伺服器
    filesystem_server = MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    )

    # PowerPoint 伺服器
    ppt_server = MCPServerStdio(
        name="ppt",
        params={
            "command": "uvx",
            "args": ["--from", "office-powerpoint-mcp-server", "ppt_mcp_server"],
        },
    )

    # Excel 伺服器
    excel_server = MCPServerSse(
        name="excel-studio",
        params={
            "url": "http://localhost:8000/sse"
        }
    )

    async with filesystem_server, ppt_server, excel_server:
        await run([filesystem_server, ppt_server, excel_server])


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx 未安裝。請使用 `npm install -g npx` 進行安裝。")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程式中斷，已優雅結束。")
    except Exception as e:
        print(f"\n發生未預期錯誤：{e}")
    finally:
        # Windows asyncio bug workaround: 強制清理所有未完成的任務
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()
        except Exception:
            pass  # loop 可能已經被關閉，忽略這個錯誤
