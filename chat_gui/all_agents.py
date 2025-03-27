# all_agents.py
from pathlib import Path
from agents.mcp import MCPServerStdio
from chat_gui.filesystem_agent import create_filesystem_agent
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent


def create_merged_agent(handoff_agents):
    """
    하위 에이전트(handoff_agents)를 handoffs로 등록한 MergedAgent를 생성합니다.
    """
    return Agent(
        name="MergedAgent",
        instructions="""
    만약에 파일 관련 처리를 해야 한다면 FilesystemAgent 를 사용하여 처리를 하자. 그 외에는 알아서 답변 잘하자.
""",
        handoffs=handoff_agents
    )


async def initialize_agents():
    """
    MCP 서버를 초기화하고, FilesystemAgent와 MergedAgent를 생성하여 최종적으로 merged_agent를 반환합니다.
    """
    # MCP 서버 초기화
    downloads_path = str(Path.home().joinpath("Downloads"))
    mcp_server_ctx = MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx.cmd",  # Windows 환경이면 npx.cmd, 다른 플랫폼이면 "npx"로 조정
            "args": ["-y", "@modelcontextprotocol/server-filesystem", downloads_path],
        },
    )
    mcp_server = await mcp_server_ctx.__aenter__()
    print("[all_agents.py] MCP server initialized:", mcp_server)

    # FilesystemAgent 생성 (MCP 서버 연결 전달)
    filesystem_agent = create_filesystem_agent(mcp_server)
    print("[all_agents.py] FilesystemAgent created.")

    # MergedAgent 생성, handoffs에 FilesystemAgent 등록
    merged_agent = create_merged_agent([filesystem_agent])
    print("[all_agents.py] MergedAgent created with filesystem handoff.")

    # 필요하다면 mcp_server_ctx를 반환해 종료시 활용할 수 있음
    return merged_agent


async def run_merged_agent(merged_agent, msg: str) -> str:
    """
    MergedAgent를 통해 사용자 메시지를 처리하고 최종 응답 텍스트를 반환합니다.
    """
    result = Runner.run_streamed(merged_agent, input=msg)
    response_text = ""
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            response_text += event.data.delta
    return response_text
