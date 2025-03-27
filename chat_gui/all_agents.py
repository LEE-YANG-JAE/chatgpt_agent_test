# all_agents.py

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

def create_merged_agent(handoff_agents):
    """
    여러 하위 에이전트(handoff_agents)를 handoffs로 등록한 MergedAgent를 생성.
    예: handoff_agents = [filesystem_agent, general_agent, ...]
    """
    return Agent(
        name="MergedAgent",
        instructions="""
만약에 파일 관련 처리를 해야 한다면 FilesystemAgent 를 사용하여 처리를 하자. 그 외에는 알아서 답변 잘하자.
""",
        handoffs=handoff_agents
    )

async def run_merged_agent(merged_agent, msg: str) -> str:
    """
    merged_agent를 통해 사용자 메시지를 처리하고 최종 응답 텍스트를 반환.
    """
    result = Runner.run_streamed(merged_agent, input=msg)
    response_text = ""
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            response_text += event.data.delta
    return response_text
