# main.py

import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
import asyncio
import threading
from agents.mcp import MCPServerStdio

# 우리가 만든 모듈들
from chat_gui.filesystem_agent import create_filesystem_agent
from chat_gui.all_agents import create_merged_agent, run_merged_agent

loop = asyncio.new_event_loop()
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MergedAgent + FilesystemAgent Demo")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=60, height=15)
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.tag_configure("left", justify='left')
        self.chat_area.tag_configure("right", justify='right')

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)
        send_button = tk.Button(input_frame, text="전송", command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=(5,0))

        # 아직 merged_agent가 없으므로 None
        self.merged_agent = None

        # 앱 시작 시 MCP 서버, FilesystemAgent, MergedAgent 순으로 초기화
        asyncio.run_coroutine_threadsafe(self.initialize_agents(), loop)

    async def initialize_agents(self):
        # 1) MCP 서버 초기화
        print("[ChatApp] Initializing MCP server...")
        downloads_path = str(Path.home().joinpath("Downloads"))
        mcp_server_ctx = MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx.cmd",  # Windows면 "npx.cmd"가 필요할 수도 있음
                "args": ["-y", "@modelcontextprotocol/server-filesystem", downloads_path],
            },
        )
        mcp_server = await mcp_server_ctx.__aenter__()
        print("[ChatApp] MCP server initialized:", mcp_server)

        # 2) 파일시스템 에이전트 생성
        filesystem_agent = create_filesystem_agent(mcp_server)
        print("[ChatApp] FilesystemAgent created.")

        # 3) MergedAgent 생성 (handoffs에 filesystem_agent 등록)
        self.merged_agent = create_merged_agent([filesystem_agent])
        print("[ChatApp] MergedAgent created with filesystem handoff.")

        # 채팅창에 초기화 메시지 표시
        self.root.after(0, self._append_message, "[System] MCP + FilesystemAgent + MergedAgent initialized.", "left")

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self._append_message(f"사용자: {user_text}", "right")
        self.entry.delete(0, tk.END)

        asyncio.run_coroutine_threadsafe(self.handle_response(user_text), loop)

    async def handle_response(self, msg):
        # MergedAgent가 준비되기 전이면 대기
        while self.merged_agent is None:
            await asyncio.sleep(0.1)

        # MergedAgent를 통해 메시지를 처리
        response_text = await run_merged_agent(self.merged_agent, msg)
        self.root.after(0, self._append_message, f"봇: {response_text}", "left")

    def _append_message(self, message, align="left"):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n", align)
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
