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
I handle filesystem operations. 
If the user says "read test.txt", I will call fs.read_file(['test.txt']).
""",
        mcp_servers=[mcp_server]
    )
