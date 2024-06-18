import dotenv
import os
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.llms import Tongyi, QianfanLLMEndpoint, BaichuanLLM
import streamlit as st

dotenv.load_dotenv()

MAX_MSG_IN_HISTORY = int(os.getenv("MAX_MSG_IN_HISTORY"))

chat_histories = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

def create_chain():
    # llm = QianfanLLMEndpoint(model="ERNIE-4.0-8K-Preview",)
    # llm = QianfanLLMEndpoint(model="ERNIE-Speed-8K")
    llm = QianfanLLMEndpoint()
    # llm = Tongyi(model_name="qwen-turbo")
    # llm = BaichuanLLM()
    vectors_path = os.path.join(os.getcwd(), "app/vectors")
    vectorstore = FAISS.load_local(vectors_path, QianfanEmbeddingsEndpoint(model="bge_large_zh", endpoint="bge_large_zh"), allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    qa_system_prompt = """
        你是一个回答中国结算深圳分公司业务指南相关问题的助手。\
        请使用以下检索到的上下文来回答问题。\
        如果你不知道答案，或者遇到与上下文无关的问题，就直接说“根据已知内容无法回答，请修改问题。”。\
        如果问题范围模糊，难以回答，不要随便回答，要求用户澄清问题。\
        使用序号要点，并保持答案简洁。\
        {context}"""
        # 回答字数不要超过50字。\
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain