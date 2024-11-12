import streamlit as st
import os
import zipfile
import shutil

# 创建本地 data 目录
DATA_DIR = os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def save_uploaded_files(uploaded_files):
    for file in uploaded_files:
        file_path = os.path.join(DATA_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    return len(uploaded_files)


def zip_directory(directory):
    zip_path = os.path.join(DATA_DIR, "download.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                zipf.write(file_path, arcname)
    return zip_path


st.title("文件上传和下载应用")

# 文件上传
uploaded_files = st.file_uploader("选择要上传的文件", accept_multiple_files=True)
if uploaded_files:
    num_files = save_uploaded_files(uploaded_files)
    st.success(f"成功上传 {num_files} 个文件")

# 文件下载专区
with st.expander("文件下载专区", expanded=True):
    files_in_data = os.listdir(DATA_DIR)
    if files_in_data:
        st.write("当前可下载的文件：")
        cols = st.columns(3)  # 创建3列布局
        for idx, file in enumerate(files_in_data):
            file_path = os.path.join(DATA_DIR, file)
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
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    st.success("data 目录已清理")