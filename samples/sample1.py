from agents import Agent, Runner, set_default_openai_key
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

agents = Agent(
    name="Agents",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
)


async def main():
    # 한번에 결과가 모두 출력
    result = await Runner.run(agents, "who was the first president of the united states?")
    print(result.final_output)

    # 결과 받는 것을 실시간으로 출력
    result = Runner.run_streamed(agents, input="what is life")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


'''

https://openai.github.io/openai-agents-python/quickstart/
https://openai.github.io/openai-agents-python/streaming/

'''
if __name__ == "__main__":
    asyncio.run(main())
