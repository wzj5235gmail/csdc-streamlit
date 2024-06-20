import streamlit as st
from chains import create_chain

conversational_rag_chain = create_chain()

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.username = ""

# with st.sidebar:
#     if st.session_state.logged_in:
#         st.header(f"Welcome, {st.session_state.username}!")
#     else:
#       st.header("登录")
#       username = st.text_input("用户名")
#       password = st.text_input("密码", type="password")
#       if st.button("登录"):
#           if username == "admin" and password == "password":
#               st.success("Logged in successfully!")
#               st.session_state.logged_in = True
#               st.session_state.username = username
#               st.rerun()
#           else:
#               st.error("Invalid username or password")

st.set_page_config(
    page_title="中国结算业务规则问答助手",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="centered",
    menu_items=None,
)

st.title("中国结算业务规则问答助手")
st.markdown("<br>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def res_generator(stream):
    for i in stream:
        if 'answer' in i:
            yield i['answer']

def send_message(msg, container):
    with container:
        with st.chat_message("user"):
            st.markdown(msg)
        st.session_state.messages.append({"role": "user", "content": msg})
        stream = conversational_rag_chain.stream(
            {"input": msg},
            {'configurable': {'session_id': 'admin'}}
        )
        with st.chat_message("assistant"):
            response = st.write_stream(res_generator(stream))
        st.session_state.messages.append({"role": "assistant", "content": response})

c = st.container()

# example_questions = [
#     "持有人名册包括哪些？",
#     "限售股解除限售的流程是怎样的？",
#     "什么是转托管？",
# ]

# i = 0
# for col in st.columns(len(example_questions)):
#     msg = example_questions[i]
#     col.button(
#         msg,
#         on_click=lambda: send_message(msg, c),
#         use_container_width=True,
#     )
#     i += 1

# cols = st.columns(len(example_questions))
# for i, col in enumerate(cols):
#     if col.button(example_questions[i]):
#         send_message(example_questions[i], c)
    # col.button(
    #     example_questions[i],
    #     on_click=lambda: send_message(example_questions[i], c),
    #     use_container_width=True,
    # )

# for question in example_questions:
#     if st.button(question):
#         send_message(question, c)

if user_question := st.chat_input("请简要描述问题"):
    send_message(user_question, c)