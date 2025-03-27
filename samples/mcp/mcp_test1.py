import asyncio
import shutil
from pathlib import Path
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
from openai.types.responses import ResponseTextDeltaEvent


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=[mcp_server],
    )

    # List the files it can read
    message = "test.txt 의 파일 내용을 확인해줘."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # List the files it can read
    message = "favorite_books.txt 의 파일 내용을 확인해주고 한국어로 번역해줘."
    print(f"Running: {message}")
    # 결과 받는 것을 실시간으로 출력
    result = Runner.run_streamed(agent, input=message)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


async def main():
    # 다운로드 폴더 (보통의 기본 이름은 'Downloads')
    downloads_path = str(Path.home().joinpath("Downloads")).replace("/", "\\")
    print(f'downloads_path: {downloads_path}')

    async with MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx.cmd",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", downloads_path],
            },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/{trace_id}\n")
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())
