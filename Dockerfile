# 使用官方的Python镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制requirements.txt到工作目录
COPY requirements.txt .

# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用程序代码到工作目录
COPY . .

# 暴露FastAPI默认端口
EXPOSE 8501

# 运行FastAPI应用
CMD ["streamlit", "run", "app/webui.py"]
