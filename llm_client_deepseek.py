import requests
import json

class DeepSeekLLMClient:
    def __init__(self, api_key, model="deepseek-r1-250120"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def chat_completions(self, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        response = requests.post(self.base_url, headers=headers, json=data, stream=True)

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}, 内容: {response.text}")

        # 处理流式输出
        for line in response.iter_lines():
            if line:
                # 解析每一行的JSON数据
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_data = json.loads(decoded_line[6:])
                    delta = json_data.get('choices', [{}])[0].get('delta', {})
                    content = delta.get('content', '')

                    if 'end_of_message' in delta:
                        yield {"role": "assistant", "delta": "", "type": "", "finish_reason": "stop"}
                    else:
                        yield {"role": "assistant", "delta": content, "type": "text", "finish_reason": ""}

# 示例用法
if __name__ == "__main__":
    api_key = "36d865bc-90e1-4daf-82b6-767b3e0ddda5"
    model = "ep-20250306140353-knhhc"
    client = DeepSeekLLMClient(api_key,model)

    messages = [{"role": "user", "content": "我要有研究推理模型与非推理模型区别的课题，怎么体现我的专业性"}]
    for chunk in client.chat_completions(messages):
        print(chunk)