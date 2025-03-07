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
            "messages": [
                    {"role": m["role"], "content": m["content"], "type": m["type"]}
                    for m in messages if m['type'] == 'text'
                ],
            "stream": True,
        }

        response = requests.post(self.base_url, headers=headers, json=data, stream=True)

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}, 内容: {response.text}")

        # 处理流式输出
        is_first = True
        is_first_reasoning_token = True
        is_first_content_token = True
        has_reasoning_token = False
        for line in response.iter_lines():
            if line:
                # 解析每一行的JSON数据
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:]
                    if json_str == "[DONE]":
                        break

                    json_data = json.loads(json_str)

                    if is_first:
                        yield {"role": "assistant", "delta": "", "type": "text", "finish_reason": ""}
                        is_first = False

                    delta = json_data.get('choices', [{}])[0].get('delta', {})
                    content = delta.get('content', '')
                    reasoning_content = delta.get('reasoning_content', '')

                    if reasoning_content:
                        has_reasoning_token = True
                        if is_first_reasoning_token:
                            reasoning_content = "思维链过程: " + reasoning_content
                            is_first_reasoning_token = False
                        yield {"role": "assistant", "delta": reasoning_content, "type": "text", "finish_reason": ""}
                    
                    if content:
                        if is_first_content_token and has_reasoning_token:
                            content = "\n\n思维链结果: " + content
                            is_first_content_token = False
                        yield {"role": "assistant", "delta": content, "type": "text", "finish_reason": ""}

# 示例用法
if __name__ == "__main__":
    api_key = "your api key"
    model = "your model endpoint"
    client = DeepSeekLLMClient(api_key,model)

    messages = [{"role": "user", "content": "我要有研究推理模型与非推理模型区别的课题，怎么体现我的专业性"}]
    for chunk in client.chat_completions(messages):
        print(chunk)