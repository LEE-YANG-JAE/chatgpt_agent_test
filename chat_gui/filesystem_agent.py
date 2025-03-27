# filesystem_agent.py

from agents import Agent

def create_filesystem_agent(mcp_server):
    """
    외부에서 초기화된 MCP 서버(mcp_server)를 받아서,
    파일시스템 전용 에이전트를 생성해 반환합니다.
    """
    return Agent(
        name="FilesystemAgent",
        instructions="""
Use the tools to read the filesystem and answer questions based on those files.
""",
        mcp_servers=[mcp_server]
    )
