import openai


prompt_template = '''# Tools

## python

When you send a message containing Python code to python, it will be executed in a
stateful Jupyter notebook environment. python will respond with the output of the execution or time out after 60.0
seconds. The drive at '/mnt/data' can be used to save and persist user files. Internet access for this session is disabled. Do not make external web requests or API calls as they will fail.

### 通信格式

我们通信的方式是通过以下固定的格式:

对于user, 可以使用以下的block类型

<|text|> 代表用户的问题
<|file|> 代表用户上传的文件路径
<|file_description|> 代表用户上传的文件的内容描述


你作为assistant, 可以使用以下的block类型

<|text|> 代表你返回的文本
<|code|> 代表你返回的代码(代码将会被执行)
<|execution|> 代表你返回的代码执行的结果。你不允许输出这个block,因为这个是代码执行的结果。只要你输出了 code block, 系统会自动生成一个 execution block。


1. 对于以上每个block,都必须对应一个<|endofblock|>。
2. 你在一轮对话中，可以输出多个block，但是每次你只能输出1个block。
3. 如果你输出了 <|endofmessage|>，代表你该轮返回的所有消息已经结束。接下来会由于用户来进行下一轮的通信。

#### 一个示例

以下是一轮对话的示例:

<|user|>
<|file|>/mnt/data/上证500.xlsx<|endofblock|>
<|file_description|>{\"fileName\": \"上证500.xlsx\", \"sheetNames\": [\"Sheet1\"], \"sheets\": [{\"sheetName\": \"Sheet1\", \"sheetType\": \"Worksheet\", \"rawUsedRange\": \"A1:G20\", \"usedRange\": \"A1:G20\", \"cells\": {\"A1\": \"日期\", \"B1\": \"收盘\", \"C1\": \"开盘\", \"D1\": \"高\", \"E1\": \"低\", \"F1\": \"交易量\", \"G1\": \"涨跌幅\", \"A2\": \"2024/5/27\", \"B2\": 5339.31, \"C2\": 5288.37, \"D2\": 5339.82, \"E2\": 5288.37, \"F2\": \"157.57K\", \"G2\": 0.0115, \"A3\": \"2024/5/24\", \"B3\": 5278.36, \"C3\": 5303.01, \"D3\": 5341.5, \"E3\": 5275.7, \"F3\": \"16.54B\", \"G3\": -0.0072, \"A4\": \"2024/5/23\", \"B4\": 5316.9, \"C4\": 5361.53, \"D4\": 5362.72, \"E4\": 5304.91, \"F4\": \"19.18B\", \"G4\": -0.0123, \"A5\": \"2024/5/22\", \"B5\": 5383.29, \"C5\": 5370.84, \"D5\": 5413.38, \"E5\": 5367.99, \"F5\": \"19.94B\", \"G5\": 0.0018, \"A6\": \"2024/5/21\", \"B6\": 5373.81, \"C6\": 5367.75, \"D6\": 5387.59, \"E6\": 5355.31, \"F6\": \"18.19B\", \"G6\": -0.0009, \"A7\": \"2024/5/21\", \"B7\": 5373.81, \"C7\": 5367.75, \"D7\": 5387.59, \"E7\": 5355.31, \"F7\": \"18.19B\", \"G7\": -0.0009, \"A8\": \"2024/5/20\", \"B8\": 5378.63, \"C8\": 5367.55, \"D8\": 5392.27, \"E8\": 5352.59, \"F8\": \"23.99B\", \"G8\": 0.0038, \"A9\": \"2024/5/17\", \"B9\": 5358.53, \"C9\": 5289.22, \"D9\": 5358.53, \"E9\": 5271.01, \"F9\": \"21.28B\", \"G9\": 0.0141, \"A10\": \"2024/5/16\", \"B10\": 5283.99, \"C10\": 5261.59, \"D10\": 5308.58, \"E10\": 5258.55, \"F10\": \"202.54K\", \"G10\": 0.0062, \"A11\": \"2024/5/15\", \"B11\": 5251.19, \"C11\": 5275.1, \"D11\": 5283.4, \"E11\": 5247.71, \"F11\": \"16.70B\", \"G11\": -0.0058, \"A12\": \"2024/5/14\", \"B12\": 5282.04, \"C12\": 5298.51, \"D12\": 5304.31, \"E12\": 5268.07, \"F12\": \"179.26K\", \"G12\": -0.0033, \"A13\": \"2024/5/13\", \"B13\": 5299.41, \"C13\": 5260.34, \"D13\": 5311.37, \"E13\": 5238.92, \"F13\": \"213.33K\", \"G13\": 0.0037, \"A14\": \"2024/5/10\", \"B14\": 5279.99, \"C14\": 5247.43, \"D14\": 5287.21, \"E14\": 5232.62, \"F14\": \"20.91B\", \"G14\": 0.0075, \"A15\": \"2024/5/9\", \"B15\": 5240.75, \"C15\": 5195.26, \"D15\": 5249.53, \"E15\": 5195.26, \"F15\": \"189.80K\", \"G15\": 0.0085, \"A16\": \"2024/5/8\", \"B16\": 5196.83, \"C16\": 5208.15, \"D16\": 5221.39, \"E16\": 5193.8, \"F16\": \"17.24B\", \"G16\": -0.0044, \"A17\": \"2024/5/7\", \"B17\": 5219.86, \"C17\": 5214.13, \"D17\": 5223.99, \"E17\": 5192.78, \"F17\": \"203.54K\", \"G17\": 0.0007, \"A18\": \"2024/5/6\", \"B18\": 5216.46, \"C18\": 5221.8, \"D18\": 5228.78, \"E18\": 5200.35, \"F18\": \"258.60K\", \"G18\": 0.0088, \"A19\": \"2024/4/30\", \"B19\": 5170.86, \"C19\": 5180.09, \"D19\": 5205.78, \"E19\": 5167.38, \"F19\": \"24.53B\", \"G19\": -0.0025, \"A20\": \"2024/4/29\", \"B20\": 5183.59, \"C20\": 5145.94, \"D20\": 5195.82, \"E20\": 5126.26, \"F20\": \"29.11B\", \"G20\": 0.0052}}], \"mode\": \"Complete information\", \"ActiveSheet\": \"Sheet1\", \"Selection\": \"C24\"}<|endofblock|>
<|text|>将交易价格画成箱线图，横轴是日期<|endofblock|>
<|endofmessage|>
<|assistant|>
<|code|>import pandas as pd\r\nimport matplotlib.pyplot as plt\r\nimport seaborn as sns\r\n\r\n# 读取Excel文件\r\nfile_path = '/mnt/data/上证500.xlsx'\r\ndf = pd.read_excel(file_path)\r\n\r\n# 检查数据的前几行以了解其结构\r\ndf.head()<|endofblock|>
<|execution|>\n          日期       收盘       开盘        高        低      交易量     涨跌幅\n0 2024-05-27  5339.31  5288.37  5339.82  5288.37  157.57K  0.0115\n1 2024-05-24  5278.36  5303.01  5341.50  5275.70   16.54B -0.0072\n2 2024-05-23  5316.90  5361.53  5362.72  5304.91   19.18B -0.0123\n3 2024-05-22  5383.29  5370.84  5413.38  5367.99   19.94B  0.0018\n4 2024-05-21  5373.81  5367.75  5387.59  5355.31   18.19B -0.0009\n<|endofblock|>
<|code|># 为了绘制箱线图，我们需要将数据转换成适合的格式\r\n# 箱线图通常用于显示一组数据的分布情况，因此我们需要将每天的交易价格（开盘、收盘、高、低）作为一组数据\r\n\r\n# 提取相关列\r\nprice_data = df[['日期', '开盘', '收盘', '高', '低']]\r\n\r\n# 将数据转换为长格式，以便于绘制箱线图\r\nprice_data_long = price_data.melt(id_vars=['日期'], var_name='交易类型', value_name='价格')\r\n\r\n# 绘制箱线图\r\nplt.figure(figsize=(12, 6))\r\nsns.boxplot(x='日期', y='价格', hue='交易类型', data=price_data_long)\r\nplt.xticks(rotation=45)\r\nplt.title('上证500交易价格箱线图')\r\nplt.xlabel('日期')\r\nplt.ylabel('价格')\r\nplt.legend(title='交易类型')\r\nplt.tight_layout()\r\n\r\n# 显示图表\r\nplt.show()<|endofblock|>
<|execution|>\n\n<<ImageDisplayed>><|endofblock|>
<|text|>将【开盘】,【收盘】,【高】,【低】四列数据转换为长格式，然后以【日期】为x轴，以转换后的价格数据为y轴，画出箱线图。<|endofblock|><|text|>已经根据提供的数据绘制了上证500的交易价格箱线图。图中展示了不同日期的开盘、收盘、最高和最低价格的分布情况。如果有任何其他需求或调整，请告知。<|endofblock|>
<|endofmessage|>




好了，你已经完全了解了上面的规则了，我们现在开始吧。


以下是一个对话的历史记录:

${chat_history}

接下来请你根据上面的规则，来完成接下来的对话。请直接返回一个block的信息，不要返回任何其他信息。
再次强调: 你的回复只能是以下三种形式:
1. <|code|>{code content here}<|endofblock|> 
2. <|text|>{text content here}<|endofblock|>
3. 单独只返回 <|endofmessage|>: 如果你想要结束这一轮对话，听取下用户的反馈，请单独只返回 <|endofmessage|>
'''


def format_chat_history(chat_history):
    result = []
    current_role = None

    for message in chat_history:
        # 当角色改变时，添加新的角色标记
        if message['role'] != current_role:
            if current_role is not None:
                result.append('<|endofmessage|>')
            result.append(f"<|{message['role']}|>")
            current_role = message['role']

        # 添加消息内容
        result.append(f"<|{message['type']}|>{message['content']}<|endofblock|>")

    # 添加最后一条消息的结束标记
    # if chat_history:
    #     result.append('<|endofmessage|>')

    # 连接所有部分
    return '\n'.join(result)

def render_prompt(messages: []) -> str:
    chat_history = format_chat_history(messages)

    from string import Template
    text = Template(prompt_template)
    return text.substitute(chat_history=chat_history)


def split_string(a, b):
    # 查找子串位置
    pos = a.find(b)

    if pos != -1:  # 如果找到了子串
        before = a[:pos]  # 子串之前的部分
        middle = b  # 子串本身
        after = a[pos + len(b):]  # 子串之后的部分
        return before, middle, after
    else:
        return None  # 如果没找到返回 None

def find_overlap(str1: str, str2: str) -> tuple[bool, str]:
    """
    判断两个字符串是否存在重合部分（str1的尾部和str2的头部）

    Args:
        str1: 第一个字符串
        str2: 第二个字符串

    Returns:
        tuple[bool, str]: (是否重合, 重合部分的字符串)
    """
    # 获取较短字符串的长度
    min_len = min(len(str1), len(str2))

    # 从最长可能的重合开始检查
    for i in range(min_len, 0, -1):
        if str1[-i:] == str2[:i]:
            return True, str1[-i:]

    return False, ""

def end_of_message_signal():
    print("received endofmessage")

    end_of_message_data = {
        "role": "assistant",
        "delta": "",
        "type": "",
        "finish_reason": "stop"
    }

    return end_of_message_data

def wrap_token(token: str):
    return f'<|{token}|>'

class OpenAILLMClient:
    def __init__(self, api_key, model="gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def chat_completions(
            self,
            messages: []):
        chat_prompt = render_prompt(messages)
        messages = [{"role": "user", "content": chat_prompt}]

        print(f'chat completion message: {messages}')

        # 使用流式输出
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            stream=True  # 启用流式输出
        )

        # 用于收集完整的响应
        full_response = ""
        response_buffer = ""

        # 逐个输出token
        start_token_type = ""
        start_token_types = ["text", "code", "endofmessage"]
        stop_token = wrap_token("endofblock")



        # step 1: detect block type
        for chunk in stream:
            if chunk.choices[0].delta.content is None:
                continue
            content = chunk.choices[0].delta.content
            full_response += content
            response_buffer += content

            # 检查是否以允许的块类型开始
            for allowed_type in start_token_types:
                if response_buffer.startswith(wrap_token(allowed_type)):
                    start_token_type = allowed_type
                    break

            if start_token_type != "":
                break

        if start_token_type == "":
            print(f'no valid start token found, full_response: {full_response}')
            return
        elif start_token_type == "endofmessage":
            yield end_of_message_signal()
            return
        else:
            print(f'received start_token_type: {start_token_type}')
            out = {
                "role": "assistant",
                "delta": "",
                "type": start_token_type,
                "finish_reason": ""
            }
            yield out

        # 移除块类型前缀
        response_buffer = response_buffer[len(wrap_token(start_token_type)):]


        # step 2: detect endofblock
        for chunk in stream:
            if chunk.choices[0].delta.content is None:
                continue
            content = chunk.choices[0].delta.content
            full_response += content
            response_buffer += content

            # condition 1: 是否完全包含endofblock
            result = split_string(response_buffer, stop_token)
            if result:
                before, middle, after = result
                print(f"前部分: '{before}'")
                print(f"匹配部分: '{middle}'")
                print(f"后部分: '{after}'")

                # 发送前半部份
                out = {
                    "role": "assistant",
                    "delta": before,
                    "type": start_token_type,
                    "finish_reason": ""
                }
                yield out

                # 截取后部分
                response_buffer = after

                break

            # condition 2: 尾部包含部分endofblock
            has_overlap, overlap = find_overlap(response_buffer, stop_token)
            if has_overlap:
                print(f"'{response_buffer}' 和 '{stop_token}' 重合，重合部分是 '{overlap}'")
                continue
            else:
                print(f"'{response_buffer}' 和 '{stop_token}' 没有重合")

            # condition 3: 完全不包含 enodofblock
            out = {
                "role": "assistant",
                "delta": response_buffer,
                "type": start_token_type,
                "finish_reason": ""
            }
            yield out

            response_buffer = ""

        # step 3: 检测 endofmessage
        for chunk in stream:
            if chunk.choices[0].delta.content is None:
                continue
            content = chunk.choices[0].delta.content
            full_response += content
            response_buffer += content

        endofmessage_token = wrap_token("endofmessage")
        if endofmessage_token in response_buffer:
            out = end_of_message_signal()
            # TODO: support last EndOfMessage
            # yield out
