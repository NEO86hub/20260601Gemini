import streamlit as st
import json
from google import genai
from google.genai import types

# =====================
# 頁面設定
# =====================
st.set_page_config(page_title="附中 AI 導覽員")
st.title("陽明交大附中 - xx導覽")

# =====================
# 讀取背景知識
# =====================
try:
    with open("tour.json", "r", encoding="utf-8") as f:
        context_data = json.load(f)
        context_text = json.dumps(context_data, ensure_ascii=False)

except FileNotFoundError:
    st.error("找不到 tour.json 檔案")
    st.stop()

except Exception as e:
    st.error(f"讀取 JSON 發生錯誤：{e}")
    st.stop()

# =====================
# 初始化 Gemini
# =====================
if "chat_session" not in st.session_state:

    try:
        api_key = st.secrets["GEMINI_API_KEY"]

    except KeyError:
        st.error("找不到 GEMINI_API_KEY")
        st.stop()

    client = genai.Client(api_key=api_key)

    system_instruction = f"""
你是陽明交大附中的導覽員「xx」。

請優先依照提供的資料回答問題。

如果資料中沒有相關資訊，
可以利用 Google Search 搜尋後再回答。

以下是學校資料：

{context_text}
"""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        tools=[
            types.Tool(
                google_search=types.GoogleSearch()
            )
        ]
    )

    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好，我是陽明交大附中的 AI 導覽員 xx，請問有什麼想了解的呢？"
        }
    ]

# =====================
# 顯示聊天紀錄
# =====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =====================
# 使用者輸入
# =====================
prompt = st.chat_input("請輸入問題")

if prompt:

    # 顯示使用者訊息
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Gemini 回覆
    with st.spinner("思考中..."):

        try:
            response = st.session_state.chat_session.send_message(prompt)

            response_text = response.text

            with st.chat_message("assistant"):
                st.write(response_text)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_text
                }
            )

        except Exception as e:
            st.error(f"發生錯誤：{e}")
