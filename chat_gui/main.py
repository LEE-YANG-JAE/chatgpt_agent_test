# main.py
import tkinter as tk
from tkinter import scrolledtext
import asyncio
import threading

from chat_gui.all_agents import initialize_agents, run_merged_agent

# 별도의 asyncio 이벤트 루프 생성 및 실행
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

        self.merged_agent = None  # 초기에는 None

        # 앱 시작 시 all_agents.initialize_agents() 호출하여 에이전트 초기화
        asyncio.run_coroutine_threadsafe(self.initialize_agents(), loop)

    async def initialize_agents(self):
        self.merged_agent = await initialize_agents()
        self.root.after(0, self._append_message, "[System] MCP + FilesystemAgent + MergedAgent initialized.", "left")

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self._append_message(f"사용자: {user_text}", "right")
        self.entry.delete(0, tk.END)
        asyncio.run_coroutine_threadsafe(self.handle_response(user_text), loop)

    async def handle_response(self, msg):
        while self.merged_agent is None:
            await asyncio.sleep(0.1)
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
