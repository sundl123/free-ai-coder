import openai
from datetime import datetime
import json
import os
import sys


class ChatBot:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.chat_history = []
        self.model = "gpt-4-turbo-preview"

    def save_chat_history(self, filename="chat_history.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, ensure_ascii=False, indent=2)

    def load_chat_history(self, filename="chat_history.json"):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)

    def chat(self, user_input):
        # 添加用户输入到历史记录
        self.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        try:
            messages = [{"role": msg["role"], "content": msg["content"]}
                        for msg in self.chat_history if "role" in msg]

            # 使用流式输出
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                stream=True  # 启用流式输出
            )

            # 用于收集完整的响应
            full_response = ""

            # 逐个输出token
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # 实时打印内容，不换行
                    print(content, end='', flush=True)

            # 最后打印一个换行
            print()

            # 添加完整的助手回复到历史记录
            self.chat_history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return full_response

        except Exception as e:
            print(f"发生错误: {str(e)}")
            return f"抱歉，发生了错误: {str(e)}"


def main():
    # 从环境变量获取 API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return

    chatbot = ChatBot(api_key)
    chatbot.load_chat_history()

    print("欢迎使用 ChatBot！输入 'quit' 退出对话。")

    while True:
        user_input = input("\n你: ")
        if user_input.lower() == 'quit':
            break

        print("\nChatBot: ", end='', flush=True)  # 预先打印提示符
        response = chatbot.chat(user_input)
        chatbot.save_chat_history()


if __name__ == "__main__":
    main()