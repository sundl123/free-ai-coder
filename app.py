import streamlit as st
import uuid
import json
import base64
import os
import pandas as pd
from llm_client_openai import OpenAILLMClient
from llm_client_deepseek import DeepSeekLLMClient
from kernel_gateway_client import GatewayClient

MNT_DATA_DIR = "/mnt/data"

FILE_PROCESSED_KEY = "file_processed"
LLM_CLIENT_KEY = "llm_client"
SESSION_ID_KEY = "session_id"

KERNEL_CLIENT_KEY = "kernel_client"
SERVER_URL = "127.0.0.1:8889"
KERNEL_NAME = "python"
KERNEL_INIT_CODE = """

import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

"""

CODE_BLOCK_START = "```python\n"
CODE_BLOCK_END = "\n```"

AVATAR_MATERIAL_ICON_UPLOAD_FILE = ":material/upload_file:"
AVATAR_MATERIAL_ICON_CODE = ":material/code_blocks:"
AVATAR_MATERIAL_ICON_EXECUTION = ":material/screenshot_monitor:"
AVATAR_MATERIAL_ICON_IMAGE = ":material/image:"

OPENAI_MODELS = ["gpt-4-turbo-preview", "gpt-4-turbo"]
OPENAI_MODELS = ["gpt-4-turbo-preview", "gpt-4-turbo"]
MODEL_PROVIDER_KEY = "model_provider"
OPENAI_API_KEY_KEY = "openai_api_key"
OPENAI_MODEL_KEY = "openai_model"

def extract_delta_stream(stream):
    for value in stream:
        yield value["delta"]


def add_markdown_code_block_marker_to_stream(stream):
    is_first = True

    for value in stream:
        if is_first:
            yield CODE_BLOCK_START
            is_first = False
        yield value

    yield CODE_BLOCK_END

def remove_markdown_code_block_marker(text):
    if text.startswith(CODE_BLOCK_START):
        text = text[len(CODE_BLOCK_START):]
    if text.endswith(CODE_BLOCK_END):
        text = text[:-len(CODE_BLOCK_END)]
    return text

def add_markdown_code_block_marker(text):
    return CODE_BLOCK_START + text + CODE_BLOCK_END


def drain_stream(stream):
    for _ in stream:
        pass

def should_extract_file_summary(file_name):
    allowed_extensions = ['xls', 'xlsx', 'xlsm', 'csv']
    # 分割文件名和扩展名
    _, ext = os.path.splitext(file_name)
    # 检查扩展名是否在允许的列表中
    if ext[1:] in allowed_extensions:  # 移除点号
        return True
    return False

def init_session():
    # init session
    if SESSION_ID_KEY not in st.session_state:
        st.session_state[SESSION_ID_KEY] = str(uuid.uuid4())
    session_id = st.session_state[SESSION_ID_KEY]

    session_dir_path = os.path.join("data", session_id)
    os.makedirs(session_dir_path, exist_ok=True)

    print(f'session_id: {session_id}')
    return session_id, session_dir_path

def init_kernel_client():
    if KERNEL_CLIENT_KEY not in st.session_state:
        gateway_client = GatewayClient(host=SERVER_URL)
        kernel_client = gateway_client.start_kernel(KERNEL_NAME)
        init_result = kernel_client.execute(KERNEL_INIT_CODE)
        print(f'kernel_init_result: {json.dumps(init_result)}')
        st.session_state[KERNEL_CLIENT_KEY] = kernel_client
    kernel_client = st.session_state[KERNEL_CLIENT_KEY]
    return kernel_client

def setup_data_dir_manager(data_dir_path):
    files_in_data = os.listdir(data_dir_path)
    should_expand = (len(files_in_data) > 0)
    with st.expander("文件下载专区", expanded=should_expand):
        if files_in_data:
            st.write("当前可下载的文件：")
            cols = st.columns(3)  # 创建3列布局
            for idx, file in enumerate(files_in_data):
                file_path = os.path.join(data_dir_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        col = cols[idx % 3]  # 在3列中循环
                        col.download_button(
                            label=f"下载 {file}",
                            data=f.read(),
                            file_name=file,
                            mime="application/octet-stream"
                        )
        else:
            st.write("目前没有可下载的文件。")

        # 清理 data 目录
        if st.button("清理 data 目录"):
            for file in os.listdir(data_dir_path):
                file_path = os.path.join(data_dir_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            st.success("data 目录已清理")

def extract_file_summary(filename: str) -> str:
    READER_MAP = {
        '.csv': pd.read_csv,
        '.tsv': pd.read_csv,
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
        '.xml': pd.read_xml,
        '.json': pd.read_json,
        '.hdf': pd.read_hdf,
        '.hdf5': pd.read_hdf,
        '.feather': pd.read_feather,
        '.parquet': pd.read_parquet,
        '.pkl': pd.read_pickle,
        '.sql': pd.read_sql,
    }

    _, ext = os.path.splitext(filename)

    try:
        df = READER_MAP[ext.lower()](filename)
        return f'The file contains the following columns: {", ".join(df.columns)}'
    except KeyError:
        return ''  # unsupported file type
    except Exception:
        return ''  # file reading failed. - Don't want to know why.

def setup_sidebar_config_panel():
    with st.sidebar:
        st.header("模型设置")

        # 选择模型提供商
        model_provider = st.radio(
            "选择模型提供商",
            options=["OpenAI", "Claude", "商汤小浣熊", "DeepSeek"],  # 添加 DeepSeek 选项
            key=MODEL_PROVIDER_KEY
        )

        # OpenAI 特定设置
        if model_provider == "OpenAI":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                key=OPENAI_API_KEY_KEY,
                help="请输入您的 OpenAI API Key"
            )

            selected_model = st.selectbox(
                "选择模型",
                options=OPENAI_MODELS,
                key=OPENAI_MODEL_KEY
            )

            if not api_key:
                st.error("请输入 OpenAI API Key")

        # DeepSeek 特定设置
        elif model_provider == "DeepSeek":
            deepseek_api_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                key="deepseek_api_key",
                help="请输入您的 DeepSeek API Key"
            )

            selected_model = st.selectbox(
                "选择模型",
                options=OPENAI_MODELS,
                key=OPENAI_MODEL_KEY
            )

            if not deepseek_api_key:
                st.error("请输入 DeepSeek API Key")

        elif model_provider == "Claude":
            st.info("Claude模型接入即将推出，敬请期待！")
            st.stop()  # 阻止继续执行
        else:
            st.info("商汤小浣熊 Raccoon模型接入即将推出，敬请期待！")
            st.stop()  # 阻止继续执行

        # 添加确认按钮
        if st.button("确认设置"):
            if model_provider == "OpenAI" and not api_key:
                st.error("请先输入 OpenAI API Key")
            elif model_provider == "DeepSeek" and not deepseek_api_key:
                st.error("请先输入 DeepSeek API Key")
            else:
                # 重新初始化 LLM 客户端
                if LLM_CLIENT_KEY in st.session_state:
                    del st.session_state[LLM_CLIENT_KEY]

                if model_provider == "OpenAI":
                    st.session_state[LLM_CLIENT_KEY] = OpenAILLMClient(
                        api_key,
                        model=selected_model
                    )
                elif model_provider == "DeepSeek":
                    st.session_state[LLM_CLIENT_KEY] = DeepSeekLLMClient(
                        deepseek_api_key,
                    )
                else:
                    st.info("Currently Unsupported Model Provider")
                    st.stop()  # 阻止继续执行

                st.success("设置已更新！")

def render_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message['role'] == "user":
            if message['type'] == "text":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            elif message['type'] == "file":
                with st.chat_message("user", avatar=AVATAR_MATERIAL_ICON_UPLOAD_FILE):
                    st.markdown(f'User uploaded file: {os.path.basename(message["content"])}')
        elif message['role'] == "assistant":
            if message['type'] == "text":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
            elif message['type'] == "code":
                with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_CODE):
                    st.markdown(add_markdown_code_block_marker(message["content"]))
            elif message['type'] == "execution":
                with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_EXECUTION):
                    st.text(f'Execution result: \n{message["content"]}')
            elif message['type'] == "image":
                with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_IMAGE):
                    st.image(message["content"], caption=os.path.basename(message["content"]))

def set_up_file_uploader(session_dir_path:str):
    if FILE_PROCESSED_KEY not in st.session_state:
        uploaded_files = st.file_uploader(
            "Upload any file", accept_multiple_files=True
        )
        for uploaded_file in uploaded_files:
            st.session_state[FILE_PROCESSED_KEY] = True

            bytes_data = uploaded_file.read()

            file_path = os.path.join(session_dir_path, uploaded_file.name)
            with open(file_path, "wb") as file:
                file.write(bytes_data)

            summary = ""
            if should_extract_file_summary(file_path):
                summary = extract_file_summary(file_path)

            st.session_state.messages.append({"role": "user", 'type': 'file', "content": f'{MNT_DATA_DIR}/{uploaded_file.name}'})
            if summary != "":
                st.session_state.messages.append({"role": "user", 'type': 'file_description', "content": summary})

            with st.chat_message("user", avatar=AVATAR_MATERIAL_ICON_UPLOAD_FILE):
                st.markdown(f'User uploaded file: {uploaded_file.name}')

def set_up_user_input_box(session_dir_path:str, kernel_client):
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt, 'type': 'text'})
        with st.chat_message("user"):
            st.markdown(prompt)

        if LLM_CLIENT_KEY not in st.session_state:
            st.error("请在侧边栏完成设置并点击确认")
            st.stop()
        llm_client = st.session_state[LLM_CLIENT_KEY]

        for i in range(1, 33):
            stream = llm_client.chat_completions(
                messages=[
                    {"role": m["role"], "content": m["content"], "type": m["type"]}
                    for m in st.session_state.messages if m['type'] != 'image'
                ]
            )

            event = next(stream)
            if event["type"] == "text":
                with st.chat_message("assistant"):
                    response = st.write_stream(extract_delta_stream(stream))
                st.session_state.messages.append({"role": "assistant", "content": response, 'type': 'text'})
            elif event["type"] == "code":
                # display code
                with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_CODE):
                    response = st.write_stream(add_markdown_code_block_marker_to_stream(extract_delta_stream(stream)))
                response = remove_markdown_code_block_marker(response)
                st.session_state.messages.append({"role": "assistant", "content": response, 'type': 'code'})

                # execute code
                modified_code = response.replace(MNT_DATA_DIR, session_dir_path)
                print(f'execute code: {modified_code}')
                execution_result = kernel_client.execute(modified_code)
                response_results = execution_result[0]
                has_error = execution_result[1]
                print(f'execution result: {execution_result}')

                img_urls = []
                plain_text = ""

                for result in response_results:
                    if result["msg_type"] == "image/png":
                        binary_data = base64.b64decode(result["content"])

                        image_id = uuid.uuid4()
                        file_path = os.path.join(session_dir_path, f'{image_id}.png')

                        with open(file_path, "wb") as file:
                            file.write(binary_data)

                        img_urls.append(file_path)
                    else:
                        plain_text += " " + result["content"]

                if len(plain_text) > 3000:
                    plain_text = plain_text[:3000]

                plain_text = plain_text.replace(session_dir_path, MNT_DATA_DIR)

                if len(plain_text) > 0:
                    st.session_state.messages.append({"role": "assistant", "content": plain_text, 'type': 'execution'})

                for img_url in img_urls:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": img_url, 'type': 'image'})

                # display execution result
                with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_EXECUTION):
                    st.text(f'Execution result: \n{plain_text}')

                for img_url in img_urls:
                    with st.chat_message("assistant", avatar=AVATAR_MATERIAL_ICON_IMAGE):
                        st.image(img_url, caption=os.path.basename(img_url))
            elif event["finish_reason"] == "stop":
                drain_stream(stream)
                break

st.title("Free AI Coder")

setup_sidebar_config_panel()

_, session_dir_path = init_session()

kernel_client = init_kernel_client()

render_chat_history()

set_up_file_uploader(session_dir_path)

set_up_user_input_box(session_dir_path, kernel_client)

setup_data_dir_manager(session_dir_path)
